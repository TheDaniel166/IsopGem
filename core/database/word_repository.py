import sqlite3
from datetime import datetime
import threading
import queue
import logging

class WordRepository:
    def __init__(self):
        self._init_logging()
        self.conn = self._create_connection()
        self._setup_database()
        self.batch_queue = queue.Queue()
        self._start_batch_worker()

    def _init_logging(self):
        logging.basicConfig(
            filename='database.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _create_connection(self):
        """Create connection with optimized settings"""
        conn = sqlite3.connect('isopgem.db', check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
        conn.execute("PRAGMA synchronous=NORMAL")  # Better performance
        conn.execute("PRAGMA cache_size=-2000")  # 2MB cache
        conn.execute("PRAGMA temp_store=MEMORY")  # Store temp tables in memory
        return conn

    def _setup_database(self):
        """Setup database with all necessary tables and indexes"""
        cursor = self.conn.cursor()
        
        # First, check if saved_words exists and get its structure
        cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='saved_words'")
        old_table_exists = cursor.fetchone() is not None

        cursor.executescript('''
            -- First create categories table
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                color TEXT NOT NULL,
                parent_id INTEGER,
                date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name)
            );
        ''')

        if old_table_exists:
            # Backup existing data with explicit columns
            cursor.executescript('''
                CREATE TEMP TABLE saved_words_backup(
                    id INTEGER PRIMARY KEY,
                    text TEXT,
                    cipher_type TEXT,
                    value INTEGER
                );
                
                INSERT INTO saved_words_backup(id, text, cipher_type, value)
                SELECT id, text, cipher_type, value FROM saved_words;
                
                DROP TABLE saved_words;
            ''')

        # Create new saved_words table
        cursor.executescript('''
            CREATE TABLE saved_words (
                id INTEGER PRIMARY KEY,
                text TEXT NOT NULL,
                cipher_type TEXT NOT NULL,
                value INTEGER NOT NULL,
                category_id INTEGER,
                date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_modified DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(text, cipher_type),
                FOREIGN KEY(category_id) REFERENCES categories(id)
            );
        ''')

        if old_table_exists:
            # Restore data with new columns set to defaults
            cursor.executescript('''
                INSERT INTO saved_words (
                    id, text, cipher_type, value, 
                    category_id, date_added, last_modified
                )
                SELECT 
                    id, text, cipher_type, value,
                    NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                FROM saved_words_backup;
                
                DROP TABLE saved_words_backup;
            ''')

        # Create other tables and indexes
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS calculation_history (
                id INTEGER PRIMARY KEY,
                text TEXT NOT NULL,
                cipher_type TEXT NOT NULL,
                value INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_notes TEXT
            );

            -- Indexes for better query performance
            CREATE INDEX IF NOT EXISTS idx_saved_words_value 
                ON saved_words(value);
            CREATE INDEX IF NOT EXISTS idx_saved_words_text 
                ON saved_words(text COLLATE NOCASE);
            CREATE INDEX IF NOT EXISTS idx_saved_words_cipher 
                ON saved_words(cipher_type);
            CREATE INDEX IF NOT EXISTS idx_saved_words_category 
                ON saved_words(category_id);
            CREATE INDEX IF NOT EXISTS idx_history_timestamp 
                ON calculation_history(timestamp);
            
            -- Triggers for automatic updates
            CREATE TRIGGER IF NOT EXISTS update_word_timestamp 
            AFTER UPDATE ON saved_words
            BEGIN
                UPDATE saved_words 
                SET last_modified = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END;
        ''')
        
        self.conn.commit()

    def _start_batch_worker(self):
        """Start background worker for batch operations"""
        def worker():
            while True:
                try:
                    batch = self.batch_queue.get(timeout=5)
                    if batch is None:
                        break
                    self._execute_batch(batch)
                except queue.Empty:
                    continue
                except Exception as e:
                    logging.error(f"Batch worker error: {e}")

        self.worker_thread = threading.Thread(target=worker, daemon=True)
        self.worker_thread.start()

    def _execute_batch(self, batch):
        """Execute a batch of operations"""
        cursor = self.conn.cursor()
        try:
            cursor.executemany(batch['query'], batch['params'])
            self.conn.commit()
        except Exception as e:
            logging.error(f"Batch execution error: {e}")
            self.conn.rollback()

    def get_saved_words(self, offset=0, limit=100, sort_by='text', sort_order='ASC'):
        """Get saved words with pagination and sorting"""
        valid_sorts = {
            'text': 'text COLLATE NOCASE',
            'value': 'value',
            'date': 'date_added',
            'cipher': 'cipher_type'
        }
        sort_column = valid_sorts.get(sort_by, 'text COLLATE NOCASE')
        
        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT text, cipher_type, value 
            FROM saved_words
            ORDER BY {sort_column} {sort_order}
            LIMIT ? OFFSET ?
        """, (limit, offset))
        return cursor.fetchall()

    def find_duplicates(self):
        """Find duplicate texts/phrases (case-insensitive)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            WITH DuplicateTexts AS (
                SELECT LOWER(text) as lower_text
                FROM saved_words
                GROUP BY LOWER(text)
                HAVING COUNT(*) > 1
            )
            SELECT 
                sw.text,
                sw.cipher_type,
                sw.value
            FROM DuplicateTexts dt
            JOIN saved_words sw ON LOWER(sw.text) = dt.lower_text
            ORDER BY LOWER(sw.text), sw.cipher_type
        """)
        
        # Organize results by text
        duplicates = {}
        for text, cipher_type, value in cursor.fetchall():
            if text.lower() not in duplicates:
                duplicates[text.lower()] = []
            duplicates[text.lower()].append((text, cipher_type, value))
        
        return duplicates

    def cleanup_old_history(self, days=30):
        """Clean up old history entries"""
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM calculation_history
            WHERE timestamp < datetime('now', '-? days')
        """, (days,))
        self.conn.commit()

    def get_statistics(self):
        """Get database statistics"""
        cursor = self.conn.cursor()
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM saved_words")
        stats['total_words'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT value) FROM saved_words")
        stats['unique_values'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT cipher_type) FROM saved_words")
        stats['cipher_types'] = cursor.fetchone()[0]
        
        return stats

    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'batch_queue'):
            self.batch_queue.put(None)
        if hasattr(self, 'worker_thread'):
            self.worker_thread.join(timeout=1)
        if hasattr(self, 'conn'):
            self.conn.close()

    def save_word(self, text, cipher_type, value):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO saved_words (text, cipher_type, value)
                VALUES (?, ?, ?)
            ''', (text, cipher_type, value))
            self.conn.commit()
            return True
        except sqlite3.Error:
            return False

    def find_by_value(self, value, cipher_type):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT text, cipher_type FROM saved_words 
            WHERE value = ? AND cipher_type = ?
        ''', (value, cipher_type))
        return cursor.fetchall()

    def find_by_value_global(self, value):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT text, cipher_type FROM saved_words 
            WHERE value = ?
        ''', (value,))
        return cursor.fetchall()

    def get_history(self, limit=50):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT text, cipher_type, value, timestamp 
            FROM calculation_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

    def add_to_history(self, text, cipher_type, value):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO calculation_history (text, cipher_type, value)
            VALUES (?, ?, ?)
        ''', (text, cipher_type, value))
        self.conn.commit()

    def word_exists(self, text, cipher_type):
        """Check if word exists with the same text and cipher type"""
        query = "SELECT COUNT(*) FROM saved_words WHERE text = ? AND cipher_type = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (text, cipher_type))
        count = cursor.fetchone()[0]
        return count > 0

    def delete_word(self, text, cipher_type):
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM saved_words 
            WHERE text = ? AND cipher_type = ?
        """, (text, cipher_type))
        self.conn.commit()

    def add_category(self, name, color):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO categories (name, color)
            VALUES (?, ?)
        """, (name, color))
        self.conn.commit()

    def search_words(self, search_text):
        """Search words by text, value, or cipher type"""
        cursor = self.conn.cursor()
        search_pattern = f"%{search_text}%"
        
        cursor.execute("""
            SELECT text, cipher_type, value 
            FROM saved_words 
            WHERE LOWER(text) LIKE LOWER(?) 
               OR LOWER(cipher_type) LIKE LOWER(?)
               OR CAST(value AS TEXT) LIKE ?
            ORDER BY text COLLATE NOCASE
        """, (search_pattern, search_pattern, search_pattern))
        
        return cursor.fetchall()
