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

@dataclass
class Definition:
    id: int
    key_id: int
    type: str  # 'Etymology', 'Standard', 'Alchemical', 'Occult', 'Mythological'
    content: str
    source: str

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
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize the database schema."""
        conn = self._get_conn()
        cursor = conn.cursor()
        
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
        
        # 3. Occurrences Table (Concordance)
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
        
        # 4. Ignored Words (Opt-out list)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ignored_words (
                word TEXT PRIMARY KEY
            )
        """)
        
        conn.commit()
        conn.close()

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
                is_active=bool(row['is_active'])
            )
        return None

    def get_id_by_word(self, word: str) -> Optional[int]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM master_key WHERE word = ?", (word.lower(),))
        row = cursor.fetchone()
        conn.close()
        return row['id'] if row else None
        
    def search_keys(self, query: str) -> List[KeyEntry]:
        conn = self._get_conn()
        cursor = conn.cursor()
        # Simple wildcard search
        param = f"%{query.lower()}%"
        cursor.execute("SELECT * FROM master_key WHERE word LIKE ? AND is_active = 1 ORDER BY word LIMIT 50", (param,))
        rows = cursor.fetchall()
        conn.close()
        
        return [
            KeyEntry(id=row['id'], word=row['word'], tq_value=row['tq_value'], is_active=bool(row['is_active']))
            for row in rows
        ]
        
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
