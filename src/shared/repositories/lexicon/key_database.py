import sqlite3
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class KeyEntry:
    id: int
    word: str
    tq_value: int
    is_active: bool
    frequency: int = 0  # Total occurrences across all texts

@dataclass
class Definition:
    id: int
    key_id: int
    type: str  # 'Etymology', 'Standard', 'Alchemical', 'Occult', 'Mythological'
    content: str
    source: str

@dataclass
class WordOccurrence:
    """A single occurrence of a word in a specific verse of a holy book."""
    id: int
    key_id: int
    document_id: int      # References documents.id in isopgem.db
    document_title: str   # Cached for display without cross-DB join
    verse_id: Optional[int]  # References document_verses.id (nullable for prose)
    verse_number: Optional[int]  # Cached verse number
    word_position: int    # Position of word within the verse
    original_form: str    # Original form as found (preserves case)
    context_snippet: str  # KWIC snippet

class KeyDatabase:
    """
    Manages the SQLite database for the Holy Book Key system.
    Enforces the 'Stable ID' and 'Opt-out Curation' philosophies.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default to a safe user location or project asset
            # Using home directory to preserve across project wipes/updates if needed
            # But adapting to project structure:
            base_dir = Path.home() / ".isopgem"
            base_dir.mkdir(exist_ok=True)
            self.db_path = base_dir / "holy_key.db"
        else:
            self.db_path = Path(db_path)
            
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30.0)  # 30 second timeout
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize the database schema."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Enable WAL mode once for better concurrency (only affects this database file)
        try:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=30000")  # 30 second timeout for locks
        except sqlite3.OperationalError:
            pass  # Already in WAL mode or locked temporarily
        
        # 1. Master Key Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_key (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT UNIQUE NOT NULL,
                tq_value INTEGER NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. Definitions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (key_id) REFERENCES master_key (id) ON DELETE CASCADE
            )
        """)
        
        # 3. Legacy Occurrences Table (deprecated, kept for migration)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS occurrences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id INTEGER NOT NULL,
                doc_path TEXT NOT NULL,
                line_number INTEGER,
                context_snippet TEXT,
                FOREIGN KEY (key_id) REFERENCES master_key (id) ON DELETE CASCADE
            )
        """)
        
        # 4. Word Occurrences Table (New Concordance - verse-linked)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS word_occurrences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id INTEGER NOT NULL,
                document_id INTEGER NOT NULL,
                document_title TEXT NOT NULL,
                verse_id INTEGER,
                verse_number INTEGER,
                word_position INTEGER NOT NULL DEFAULT 0,
                original_form TEXT NOT NULL,
                context_snippet TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (key_id) REFERENCES master_key (id) ON DELETE CASCADE,
                UNIQUE(key_id, document_id, verse_id, word_position)
            )
        """)
        
        # Index for fast lookups by document/verse
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_word_occurrences_document 
            ON word_occurrences(document_id, verse_number)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_word_occurrences_key 
            ON word_occurrences(key_id)
        """)
        
        # 5. Ignored Words (Opt-out list)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ignored_words (
                word TEXT PRIMARY KEY
            )
        """)
        
        # 6. Etymology Database (from etymology-db project)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS etymologies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                term_id TEXT NOT NULL,
                lang TEXT NOT NULL,
                term TEXT NOT NULL,
                reltype TEXT NOT NULL,
                related_term_id TEXT,
                related_lang TEXT,
                related_term TEXT,
                position INTEGER DEFAULT 0,
                group_tag TEXT,
                parent_tag TEXT,
                parent_position INTEGER,
                loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indices for etymology queries (English word lookups)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_etymologies_term 
            ON etymologies(term, lang)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS ix_etymologies_reltype 
            ON etymologies(term, reltype)
        """)
        
        # 7. Ensure master_key has frequency column (migration)
        try:
            cursor.execute("ALTER TABLE master_key ADD COLUMN frequency INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        conn.commit()
        conn.close()

    def reset_database(self):
        """
        DANGEROUS: Drops all tables and re-initializes.
        Used for rebuilding the lexicon from scratch.
        """
        import gc
        
        # Force garbage collection to close lingering connections
        gc.collect()
        
        conn = self._get_conn()
        cursor = conn.cursor()
        
        try:
            tables = ['word_occurrences', 'occurrences', 'definitions', 'master_key', 'ignored_words', 'etymologies']
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            
            conn.commit()
        except sqlite3.OperationalError as e:
            conn.rollback()
            raise Exception(f"Database is locked. Close all windows using the lexicon and try again. ({e})")
        finally:
            conn.close()
        
        # Re-init
        self._init_db()

    # --- Master Key Operations ---

    def add_word(self, word: str, tq_value: int) -> int:
        """
        Add a new word to the Holy Key. 
        Returns the new Key ID.
        Raises sqlite3.IntegrityError if word exists.
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO master_key (word, tq_value) VALUES (?, ?)",
                (word.lower(), tq_value)
            )
            new_id = cursor.lastrowid
            conn.commit()
            return new_id
        except sqlite3.IntegrityError:
            # If it exists, return the existing ID
            cursor.execute("SELECT id FROM master_key WHERE word = ?", (word.lower(),))
            result = cursor.fetchone()
            if result:
                return result['id']
            raise
        finally:
            conn.close()

    def get_word_by_id(self, key_id: int) -> Optional[KeyEntry]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM master_key WHERE id = ?", (key_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return KeyEntry(
                id=row['id'],
                word=row['word'],
                tq_value=row['tq_value'],
                is_active=bool(row['is_active']),
                frequency=row['frequency'] if 'frequency' in row.keys() else 0
            )
        return None

    def get_id_by_word(self, word: str) -> Optional[int]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM master_key WHERE word = ?", (word.lower(),))
        row = cursor.fetchone()
        conn.close()
        return row['id'] if row else None
    
    def update_tq_value(self, key_id: int, tq_value: int) -> bool:
        """Update the TQ value for an existing word."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE master_key SET tq_value = ? WHERE id = ?",
            (tq_value, key_id)
        )
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated
        
    def search_keys(
        self, 
        query: str, 
        page: int = 1, 
        page_size: int = 50,
        sort_by: str = 'word',
        descending: bool = False
    ) -> Tuple[List[KeyEntry], int]:
        """Search keys with pagination and sorting.
        
        Args:
            query: Search term (partial match on word)
            page: Page number (1-indexed)
            page_size: Results per page
            sort_by: Column to sort by ('word', 'tq_value', 'frequency', 'id')
            descending: Sort direction
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        param = f"%{query.lower()}%"
        offset = (page - 1) * page_size
        
        # 1. Get Total Count
        cursor.execute("SELECT COUNT(*) FROM master_key WHERE word LIKE ? AND is_active = 1", (param,))
        total_count = cursor.fetchone()[0]
        
        # 2. Build sort clause
        sort_col_map = {
            'word': 'word',
            'tq_value': 'tq_value',
            'frequency': 'frequency',
            'id': 'id'
        }
        sort_col = sort_col_map.get(sort_by, 'word')
        direction = 'DESC' if descending else 'ASC'
        
        # 3. Get Page Results
        cursor.execute(
            f"SELECT * FROM master_key WHERE word LIKE ? AND is_active = 1 ORDER BY {sort_col} {direction} LIMIT ? OFFSET ?", 
            (param, page_size, offset)
        )
        rows = cursor.fetchall()
        conn.close()
        
        results = [
            KeyEntry(
                id=row['id'], 
                word=row['word'], 
                tq_value=row['tq_value'], 
                is_active=bool(row['is_active']),
                frequency=row['frequency'] if 'frequency' in row.keys() else 0
            )
            for row in rows
        ]
        return results, total_count
        
    # --- Definition Operations ---

    def add_definition(self, key_id: int, def_type: str, content: str, source: str = "Magus") -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO definitions (key_id, type, content, source) VALUES (?, ?, ?, ?)",
            (key_id, def_type, content, source)
        )
        new_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return new_id

    def get_definitions(self, key_id: int) -> List[Definition]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM definitions WHERE key_id = ?", (key_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            Definition(
                id=row['id'],
                key_id=row['key_id'],
                type=row['type'],
                content=row['content'],
                source=row['source']
            )
            for row in rows
        ]

    # --- Occurrence operations (Concordance) ---

    def add_occurrence(self, key_id: int, doc_path: str, line: int = 0, context: str = ""):
        conn = self._get_conn()
        cursor = conn.cursor()
        # Avoid duplicates for same file/key
        cursor.execute(
            "SELECT id FROM occurrences WHERE key_id = ? AND doc_path = ?",
            (key_id, doc_path)
        )
        if cursor.fetchone():
            return # Already recorded source for this key
            
        cursor.execute(
            "INSERT INTO occurrences (key_id, doc_path, line_number, context_snippet) VALUES (?, ?, ?, ?)",
            (key_id, doc_path, line, context)
        )
        conn.commit()
        conn.close()

    def get_occurrences(self, key_id: int) -> List[str]:
        """Return list of distinct doc_paths (Sources) for a key."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT doc_path FROM occurrences WHERE key_id = ? ORDER BY doc_path",
            (key_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        return [row['doc_path'] for row in rows]

    # --- Ignored Words (Curation) ---

    def ignore_word(self, word: str):
        """Add word to ignore list (Opt-out)."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO ignored_words (word) VALUES (?)", (word.lower(),))
        conn.commit()
        conn.close()

    def is_ignored(self, word: str) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM ignored_words WHERE word = ?", (word.lower(),))
        result = cursor.fetchone()
        conn.close()
        return result is not None
        
    def get_all_ignored(self) -> List[str]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT word FROM ignored_words ORDER BY word")
        rows = cursor.fetchall()
        conn.close()
        return [row['word'] for row in rows]

    # --- Word Occurrence Operations (New Concordance) ---

    def add_word_occurrence(
        self,
        key_id: int,
        document_id: int,
        document_title: str,
        verse_id: Optional[int],
        verse_number: Optional[int],
        word_position: int,
        original_form: str,
        context_snippet: str = ""
    ) -> Optional[int]:
        """
        Add a word occurrence linked to a specific verse.
        Returns the occurrence ID, or None if duplicate.
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO word_occurrences 
                   (key_id, document_id, document_title, verse_id, verse_number, 
                    word_position, original_form, context_snippet)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (key_id, document_id, document_title, verse_id, verse_number,
                 word_position, original_form, context_snippet)
            )
            new_id = cursor.lastrowid
            
            # Update frequency count on master_key
            cursor.execute(
                "UPDATE master_key SET frequency = frequency + 1 WHERE id = ?",
                (key_id,)
            )
            
            conn.commit()
            return new_id
        except sqlite3.IntegrityError:
            # Duplicate occurrence
            return None
        finally:
            conn.close()

    def get_word_occurrences(self, key_id: int) -> List[WordOccurrence]:
        """
        Get all occurrences of a word across all documents.
        Returns list sorted by document, then verse number.
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM word_occurrences 
               WHERE key_id = ? 
               ORDER BY document_title, verse_number, word_position""",
            (key_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            WordOccurrence(
                id=row['id'],
                key_id=row['key_id'],
                document_id=row['document_id'],
                document_title=row['document_title'],
                verse_id=row['verse_id'],
                verse_number=row['verse_number'],
                word_position=row['word_position'],
                original_form=row['original_form'],
                context_snippet=row['context_snippet'] or ""
            )
            for row in rows
        ]

    def get_occurrences_by_document(self, document_id: int) -> List[WordOccurrence]:
        """
        Get all indexed word occurrences for a specific document.
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM word_occurrences 
               WHERE document_id = ? 
               ORDER BY verse_number, word_position""",
            (document_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return [
            WordOccurrence(
                id=row['id'],
                key_id=row['key_id'],
                document_id=row['document_id'],
                document_title=row['document_title'],
                verse_id=row['verse_id'],
                verse_number=row['verse_number'],
                word_position=row['word_position'],
                original_form=row['original_form'],
                context_snippet=row['context_snippet'] or ""
            )
            for row in rows
        ]

    def get_occurrence_count_by_document(self, key_id: int) -> Dict[str, int]:
        """
        Get occurrence counts grouped by document title.
        Returns dict: {document_title: count}
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT document_title, COUNT(*) as count 
               FROM word_occurrences 
               WHERE key_id = ? 
               GROUP BY document_title
               ORDER BY count DESC""",
            (key_id,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        return {row['document_title']: row['count'] for row in rows}

    def clear_document_occurrences(self, document_id: int) -> int:
        """
        Remove all word occurrences for a document (before re-indexing).
        Returns number of deleted rows.
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # First, decrement frequency counts
        cursor.execute(
            """SELECT key_id, COUNT(*) as count 
               FROM word_occurrences 
               WHERE document_id = ? 
               GROUP BY key_id""",
            (document_id,)
        )
        for row in cursor.fetchall():
            cursor.execute(
                "UPDATE master_key SET frequency = MAX(0, frequency - ?) WHERE id = ?",
                (row['count'], row['key_id'])
            )
        
        # Delete occurrences
        cursor.execute(
            "DELETE FROM word_occurrences WHERE document_id = ?",
            (document_id,)
        )
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted

    def is_document_indexed(self, document_id: int) -> bool:
        """Check if a document has been indexed to the concordance."""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM word_occurrences WHERE document_id = ? LIMIT 1",
            (document_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def get_concordance_stats(self) -> Dict[str, any]:
        """Return concordance statistics including document list."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM master_key WHERE is_active = 1")
        total_keys = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM word_occurrences")
        total_occurrences = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT document_id) FROM word_occurrences")
        indexed_documents = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM definitions")
        total_definitions = cursor.fetchone()[0]
        
        # Get indexed words count (keys with at least one occurrence)
        cursor.execute(
            "SELECT COUNT(DISTINCT key_id) FROM word_occurrences"
        )
        total_indexed_words = cursor.fetchone()[0]
        
        # Get list of indexed documents
        cursor.execute(
            """SELECT DISTINCT document_id, document_title 
               FROM word_occurrences 
               ORDER BY document_title"""
        )
        documents = [(row['document_id'], row['document_title']) for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "total_keys": total_keys,
            "total_occurrences": total_occurrences,
            "indexed_documents": indexed_documents,
            "total_definitions": total_definitions,
            "total_indexed_words": total_indexed_words,
            "documents": documents
        }
    
    def get_concordance_words(
        self, 
        document_id: Optional[int] = None,
        sort_by: str = 'frequency',
        descending: bool = True,
        limit: int = 2000
    ) -> List[Tuple[str, int, int, int]]:
        """
        Get words for concordance display with frequency and TQ value.
        
        Args:
            document_id: Filter to specific document (None = all)
            sort_by: 'frequency', 'tq_value', or 'word'
            descending: Sort direction
            limit: Max results
            
        Returns:
            List of (word, frequency, tq_value, key_id) tuples
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Build query based on whether we're filtering by document
        if document_id:
            query = """
                SELECT mk.word, COUNT(wo.id) as freq, mk.tq_value, mk.id as key_id
                FROM master_key mk
                JOIN word_occurrences wo ON mk.id = wo.key_id
                WHERE wo.document_id = ? AND mk.is_active = 1
                GROUP BY mk.id
            """
            params = [document_id]
        else:
            query = """
                SELECT mk.word, mk.frequency as freq, mk.tq_value, mk.id as key_id
                FROM master_key mk
                WHERE mk.is_active = 1 AND mk.frequency > 0
            """
            params = []
        
        # Add sort
        sort_col = {
            'frequency': 'freq',
            'tq_value': 'mk.tq_value',
            'word': 'mk.word'
        }.get(sort_by, 'freq')
        
        direction = 'DESC' if descending else 'ASC'
        query += f" ORDER BY {sort_col} {direction}"
        
        # Add limit
        query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [(row['word'], row['freq'], row['tq_value'], row['key_id']) for row in rows]
