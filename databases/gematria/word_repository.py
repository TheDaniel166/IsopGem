"""
Word Repository for Gematria calculations
Handles storage and retrieval of words, phrases, and their gematria values
"""
import sqlite3
from datetime import datetime
import threading
import queue
import logging
import os

class WordRepository:
    # Define a class variable for the database path
    DATABASE_PATH = os.path.join('databases', 'gematria', 'gematria.db')
    
    def __init__(self, db_path=None):
        """Initialize the word repository"""
        # Always use the class-defined database path unless explicitly overridden
        if db_path is None:
            db_path = WordRepository.DATABASE_PATH
            
        self.db_path = db_path
        print(f"Word Repository Database path: {os.path.abspath(db_path)}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Migrate data from old databases if needed
        self._migrate_from_old_databases()
        
        # Connect with foreign keys enabled
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # Create tables if they don't exist
        self._create_tables()
        
        # Add sample data if the database is empty
        self._add_sample_data_if_empty()
        
        self.batch_queue = queue.Queue()
        self._start_batch_worker()

    def _init_logging(self):
        logging.basicConfig(
            filename='database.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='saved_words';")
        saved_words_exists = cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='phrase_categories';")
        categories_exists = cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='phrase_tags';")
        tags_exists = cursor.fetchone() is not None
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='calculation_history';")
        history_exists = cursor.fetchone() is not None
        
        print(f"Tables exist: saved_words={saved_words_exists}, categories={categories_exists}, tags={tags_exists}, history={history_exists}")
        
        # Create saved_words table if it doesn't exist
        if not saved_words_exists:
            print("Creating saved_words table")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS saved_words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    value INTEGER NOT NULL,
                    cipher_type TEXT NOT NULL,
                    notes TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(text, cipher_type)
                )
            ''')
        
        # Create phrase_categories table if it doesn't exist
        if not categories_exists:
            print("Creating phrase_categories table")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS phrase_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    color TEXT NOT NULL,
                    description TEXT
                )
            ''')
        
        # Create phrase_tags table if it doesn't exist
        if not tags_exists:
            print("Creating phrase_tags table")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS phrase_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phrase_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    FOREIGN KEY (phrase_id) REFERENCES saved_words(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES phrase_categories(id) ON DELETE CASCADE,
                    UNIQUE(phrase_id, category_id)
                )
            ''')
        
        # Create calculation history table
        if not history_exists:
            print("Creating calculation_history table")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS calculation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    value INTEGER NOT NULL,
                    cipher_type TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        
        # Create indices for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_text ON saved_words(text)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_value ON saved_words(value)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cipher ON saved_words(cipher_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_timestamp ON calculation_history(timestamp)')
        
        # Add indices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_category_name ON phrase_categories(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_phrase_tags ON phrase_tags(phrase_id, category_id)')
        
        # Check if columns exist and add them if they don't
        try:
            cursor.execute("SELECT tags, notes FROM saved_words LIMIT 1")
        except sqlite3.OperationalError:
            # Add missing columns
            try:
                cursor.execute("ALTER TABLE saved_words ADD COLUMN tags TEXT")
                cursor.execute("ALTER TABLE saved_words ADD COLUMN notes TEXT")
                print("Added tags and notes columns to saved_words table")
            except sqlite3.OperationalError as e:
                print(f"Error adding columns: {e}")
        
        self.conn.commit()

    def _add_sample_data_if_empty(self):
        """Add sample data if the database is empty"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM saved_words")
            count = cursor.fetchone()[0]
            
            print(f"Database has {count} saved words")
            
            # Debug: Print all tables in the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"Database tables: {tables}")
            
            # Debug: Print sample of data
            if count > 0:
                cursor.execute("SELECT text, value, cipher_type FROM saved_words LIMIT 5")
                sample_data = cursor.fetchall()
                print(f"Sample data: {sample_data}")
            
            if count == 0:
                print("Database is empty, adding sample data")
                self._add_sample_data()
                return True
            return False
        except Exception as e:
            print(f"Error checking if database is empty: {e}")
            # If there's an error, try to add sample data anyway
            try:
                self._add_sample_data()
                return True
            except Exception as e2:
                print(f"Error adding sample data: {e2}")
                return False

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

    def save_word(self, text, value, cipher_type, notes=""):
        """Save a word to the database"""
        cursor = self.conn.cursor()
        
        try:
            # Convert value to integer if it's a string
            if isinstance(value, str):
                try:
                    value = int(value)
                except ValueError:
                    # Keep as string if conversion fails
                    pass
                
            cursor.execute('''
                INSERT INTO saved_words (text, value, cipher_type, notes, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
            ''', (text, value, cipher_type, notes))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error saving word: {e}")
            return False

    def word_exists(self, text, cipher_type):
        """Check if word exists with the same text and cipher type"""
        query = "SELECT COUNT(*) FROM saved_words WHERE text = ? AND cipher_type = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (text, cipher_type))
        count = cursor.fetchone()[0]
        return count > 0

    def delete_word(self, text, cipher_type):
        """Delete a word from the database"""
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM saved_words 
            WHERE text = ? AND cipher_type = ?
        """, (text, cipher_type))
        self.conn.commit()

    def get_saved_words(self, offset=0, limit=100, sort_by='text', sort_order='ASC'):
        """Get saved words with pagination and sorting"""
        valid_sorts = {
            'text': 'text COLLATE NOCASE',
            'value': 'value',
            'date': 'created_at',
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

    def add_to_history(self, text, cipher_type, value):
        """Add a calculation to history"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO calculation_history (text, cipher_type, value)
            VALUES (?, ?, ?)
        ''', (text, cipher_type, value))
        self.conn.commit()

    def get_history(self, limit=50):
        """Get calculation history"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT text, cipher_type, value, timestamp 
            FROM calculation_history 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        return cursor.fetchall()

    def cleanup_old_history(self, days=30):
        """Clean up old history entries"""
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM calculation_history
            WHERE timestamp < datetime('now', '-? days')
        """, (days,))
        self.conn.commit()

    def find_by_value(self, value, cipher_type):
        """Find phrases with specific value in given cipher"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT text, value, cipher_type, category 
            FROM saved_words 
            WHERE value = ? AND cipher_type = ?
            ORDER BY text
        ''', (value, cipher_type))
        return cursor.fetchall()

    def find_by_value_global(self, value):
        """Find phrases with specific value in any cipher"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT text, value, cipher_type, category 
            FROM saved_words 
            WHERE value = ?
            ORDER BY text
        ''', (value,))
        return cursor.fetchall()

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

    def add_category(self, name, color="#808080", description=None):
        """Add a new category"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO phrase_categories (name, color, description)
                VALUES (?, ?, ?)
            ''', (name, color, description))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def assign_category(self, text, cipher_type, category_name):
        """Assign a category to a phrase"""
        try:
            cursor = self.conn.cursor()
            
            # Get phrase ID
            cursor.execute('''
                SELECT id FROM saved_words 
                WHERE text = ? AND cipher_type = ?
            ''', (text, cipher_type))
            phrase_id = cursor.fetchone()
            
            if not phrase_id:
                return False
                
            # Get category ID
            cursor.execute('SELECT id FROM phrase_categories WHERE name = ?', (category_name,))
            category_id = cursor.fetchone()
            
            if not category_id:
                return False
                
            # Add tag
            cursor.execute('''
                INSERT OR IGNORE INTO phrase_tags (phrase_id, category_id)
                VALUES (?, ?)
            ''', (phrase_id[0], category_id[0]))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error assigning category: {e}")
            return False

    def get_phrase_categories(self, text, cipher_type):
        """Get all categories assigned to a phrase"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                SELECT pc.name, pc.color
                FROM phrase_categories pc
                JOIN phrase_tags pt ON pc.id = pt.category_id
                JOIN saved_words sw ON pt.phrase_id = sw.id
                WHERE sw.text = ? AND sw.cipher_type = ?
            ''', (text, cipher_type))
            
            return cursor.fetchall()
        except Exception as e:
            print(f"Error getting phrase categories: {e}")
            return []

    def get_categories(self):
        """Get all categories"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                SELECT id, name, color, description
                FROM phrase_categories
                ORDER BY name
            ''')
            
            categories = []
            for row in cursor.fetchall():
                categories.append({
                    'id': row[0],
                    'name': row[1],
                    'color': row[2],
                    'description': row[3]
                })
                
            return categories
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []

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

    def get_phrase_tags(self, text, cipher_type):
        """Get tags for a phrase"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT tags FROM saved_words 
            WHERE text = ? AND cipher_type = ?
        ''', (text, cipher_type))
        result = cursor.fetchone()
        if result and result[0]:
            return result[0].split(',')
        return []

    def get_phrase_notes(self, text, cipher_type):
        """Get notes for a phrase"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT notes FROM saved_words 
            WHERE text = ? AND cipher_type = ?
        ''', (text, cipher_type))
        result = cursor.fetchone()
        return result[0] if result and result[0] else ""

    def advanced_search(self, criteria):
        """Advanced search with multiple filters"""
        cursor = self.conn.cursor()
        
        query = '''
            SELECT text, value, cipher_type 
            FROM saved_words 
            WHERE 1=1
        '''
        params = []
        
        # Text search - search in both text and value fields
        if criteria.get('text'):
            search_text = criteria['text']
            # Try to convert to integer for value comparison
            try:
                search_value = int(search_text)
                # Search in both text and value fields
                query += " AND (LOWER(text) LIKE LOWER(?) OR value = ?)"
                params.extend([f"%{search_text}%", search_value])
            except ValueError:
                # Not a number, just search in text
                query += " AND LOWER(text) LIKE LOWER(?)"
                params.append(f"%{search_text}%")
            
        # Cipher filter
        if criteria.get('cipher'):
            query += " AND LOWER(cipher_type) = LOWER(?)"
            params.append(criteria['cipher'])
            
        # Value range
        if criteria.get('value_range'):
            min_val, max_val = criteria['value_range']
            query += " AND CAST(value AS INTEGER) BETWEEN ? AND ?"
            params.extend([min_val, max_val])
            
        # Date range
        if criteria.get('date_range'):
            date_range = criteria['date_range']
            if date_range == "Today":
                query += " AND DATE(created_at) = DATE('now')"
            elif date_range == "This week":
                query += " AND created_at >= datetime('now', '-7 days')"
            elif date_range == "This month":
                query += " AND created_at >= datetime('now', '-30 days')"
            elif date_range == "This year":
                query += " AND created_at >= datetime('now', '-365 days')"
                
        # Category filter
        if criteria.get('category'):
            query += ''' 
                AND id IN (
                    SELECT phrase_id FROM phrase_tags 
                    JOIN phrase_categories ON phrase_tags.category_id = phrase_categories.id
                    WHERE LOWER(phrase_categories.name) = LOWER(?)
                )
            '''
            params.append(criteria['category'])
            
        # Tags filter
        if criteria.get('tags') and len(criteria['tags']) > 0:
            tag_conditions = []
            for tag in criteria['tags']:
                tag_conditions.append("LOWER(tags) LIKE LOWER(?)")
                params.append(f"%{tag}%")
            query += f" AND ({' OR '.join(tag_conditions)})"
            
        query += " ORDER BY text COLLATE NOCASE LIMIT 100"
        
        print(f"SQL Query: {query}")
        print(f"SQL Params: {params}")
        
        try:
            cursor.execute(query, params)
            results = cursor.fetchall()
            print(f"Query returned {len(results)} results")
            
            # If no results with filters, try a simpler query
            if not results and not any(criteria.values()):
                simple_query = '''
                    SELECT text, value, cipher_type 
                    FROM saved_words 
                    ORDER BY text COLLATE NOCASE
                    LIMIT 100
                '''
                print(f"Trying simple query: {simple_query}")
                cursor.execute(simple_query)
                results = cursor.fetchall()
                print(f"Simple query returned {len(results)} results")
                
            return results
        except Exception as e:
            import traceback
            print(f"Error in advanced search: {e}")
            print(traceback.format_exc())
            # Return empty list on error
            return []

    def get_all_words(self):
        """Get all saved words"""
        cursor = self.conn.cursor()
        try:
            query = '''
                SELECT text, value, cipher_type 
                FROM saved_words 
                ORDER BY text COLLATE NOCASE
                LIMIT 100
            '''
            print(f"Get all words query: {query}")
            cursor.execute(query)
            results = cursor.fetchall()
            print(f"Get all words returned {len(results)} results: {results}")
            
            # If no results, add sample data and try again
            if not results:
                print("No results found, adding sample data")
                self._add_sample_data()
                cursor.execute(query)
                results = cursor.fetchall()
                print(f"After adding sample data, get_all_words returned {len(results)} results")
                
            return results
        except Exception as e:
            import traceback
            print(f"Error getting all words: {e}")
            print(traceback.format_exc())
            return []
            
    def _add_sample_data(self):
        """Add sample data to the database"""
        cursor = self.conn.cursor()
        
        # Sample categories
        categories = [
            ('Important', '#FF5733', 'Words with special significance'),
            ('Biblical', '#33FF57', 'Words from biblical texts'),
            ('Personal', '#3357FF', 'Words with personal meaning'),
            ('Numeric', '#FF33A8', 'Words with significant numeric values')
        ]
        
        # Add categories
        for name, color, description in categories:
            try:
                cursor.execute(
                    "INSERT OR IGNORE INTO phrase_categories (name, color, description) VALUES (?, ?, ?)",
                    (name, color, description)
                )
            except Exception as e:
                print(f"Error adding category {name}: {e}")
        
        # Sample words with specific values for testing
        sample_words = [
            ('Jesus', 74, 'English Ordinal', 'Biblical'),
            ('Christ', 77, 'English Ordinal', 'Biblical'),
            ('Gematria', 98, 'English Ordinal', 'Important'),
            ('Isopsephy', 137, 'English Ordinal', 'Important'),
            ('Love', 54, 'English Ordinal', 'Personal'),
            ('Peace', 50, 'English Ordinal', 'Personal'),
            ('Seventy Five', 75, 'TQ English', 'Numeric'),  # Value 75 for testing
            ('Ninety Six', 96, 'TQ English', 'Numeric'),    # Value 96 for testing
            ('Test 75', 75, 'English Ordinal', 'Numeric'),  # Another 75 value
            ('Test 96', 96, 'English Ordinal', 'Numeric')   # Another 96 value
        ]
        
        # Add sample words
        for text, value, cipher_type, category in sample_words:
            try:
                # Add the word
                cursor.execute(
                    "INSERT OR IGNORE INTO saved_words (text, value, cipher_type) VALUES (?, ?, ?)",
                    (text, value, cipher_type)
                )
                
                # Get the word ID and category ID
                cursor.execute("SELECT id FROM saved_words WHERE text = ? AND cipher_type = ?", (text, cipher_type))
                word_id = cursor.fetchone()[0]
                
                cursor.execute("SELECT id FROM phrase_categories WHERE name = ?", (category,))
                category_result = cursor.fetchone()
                
                if category_result:
                    category_id = category_result[0]
                    # Add the tag
                    cursor.execute(
                        "INSERT OR IGNORE INTO phrase_tags (phrase_id, category_id) VALUES (?, ?)",
                        (word_id, category_id)
                    )
            except Exception as e:
                print(f"Error adding sample word {text}: {e}")
        
        self.conn.commit()
        print("Sample data added successfully")

    def get_category_color(self, category_name):
        """Get color for a category"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT color FROM phrase_categories 
            WHERE name = ?
        ''', (category_name,))
        result = cursor.fetchone()
        return result[0] if result else "#808080"

    def update_category(self, old_name, new_name, new_color):
        """Update a category"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE phrase_categories 
                SET name = ?, color = ? 
                WHERE name = ?
            ''', (new_name, new_color, old_name))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating category: {e}")
            return False

    def remove_category(self, text, cipher_type, category_name):
        """Remove a category from a phrase"""
        try:
            cursor = self.conn.cursor()
            
            # Get phrase ID
            cursor.execute('''
                SELECT id FROM saved_words 
                WHERE text = ? AND cipher_type = ?
            ''', (text, cipher_type))
            phrase_id = cursor.fetchone()
            
            if not phrase_id:
                return False
                
            # Get category ID
            cursor.execute('SELECT id FROM phrase_categories WHERE name = ?', (category_name,))
            category_id = cursor.fetchone()
            
            if not category_id:
                return False
                
            # Remove tag
            cursor.execute('''
                DELETE FROM phrase_tags 
                WHERE phrase_id = ? AND category_id = ?
            ''', (phrase_id[0], category_id[0]))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error removing category: {e}")
            return False

    def add_word(self, text, value, cipher_type, tags=None, notes=None):
        """Add a new word with optional tags and notes"""
        try:
            cursor = self.conn.cursor()
            
            # Check if word already exists
            cursor.execute('''
                SELECT id FROM saved_words 
                WHERE text = ? AND cipher_type = ?
            ''', (text, cipher_type))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing word
                cursor.execute('''
                    UPDATE saved_words 
                    SET value = ?, tags = ?, notes = ? 
                    WHERE text = ? AND cipher_type = ?
                ''', (value, ','.join(tags) if tags else None, notes, text, cipher_type))
            else:
                # Insert new word
                cursor.execute('''
                    INSERT INTO saved_words (text, value, cipher_type, tags, notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (text, value, cipher_type, ','.join(tags) if tags else None, notes))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding word: {e}")
            return False

    def _migrate_from_old_databases(self):
        """Migrate data from all old databases to the new unified database"""
        # List of potential old database paths
        old_db_paths = [
            os.path.join('databases', 'gematria', 'words.db'),
            os.path.join('databases', 'gematria', 'saved_words.db')
        ]
        
        # Don't migrate if the target database already exists
        if os.path.exists(self.db_path) and os.path.getsize(self.db_path) > 0:
            print(f"Unified database {self.db_path} already exists, skipping migration")
            return
            
        # Check each old database and migrate data if needed
        for old_db_path in old_db_paths:
            if os.path.exists(old_db_path) and os.path.abspath(old_db_path) != os.path.abspath(self.db_path):
                print(f"Found old database at {old_db_path}, attempting migration")
                try:
                    # Connect to old database
                    old_conn = sqlite3.connect(old_db_path)
                    old_cursor = old_conn.cursor()
                    
                    # Check if old database has saved_words table
                    old_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='saved_words'")
                    if old_cursor.fetchone() is None:
                        print(f"Old database {old_db_path} does not have saved_words table, skipping")
                        old_conn.close()
                        continue
                        
                    # Check if old database has data
                    old_cursor.execute("SELECT COUNT(*) FROM saved_words")
                    old_count = old_cursor.fetchone()[0]
                    
                    if old_count == 0:
                        print(f"Old database {old_db_path} is empty, skipping")
                        old_conn.close()
                        continue
                        
                    # Connect to new database
                    new_conn = sqlite3.connect(self.db_path)
                    new_cursor = new_conn.cursor()
                    
                    # Create tables in new database
                    new_cursor.execute('''
                        CREATE TABLE IF NOT EXISTS saved_words (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            text TEXT NOT NULL,
                            value INTEGER NOT NULL,
                            cipher_type TEXT NOT NULL,
                            notes TEXT,
                            tags TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(text, cipher_type)
                        )
                    ''')
                    
                    # Copy data from old to new
                    print(f"Migrating {old_count} records from {old_db_path} to {self.db_path}")
                    
                    # Get column names from old database
                    old_cursor.execute("PRAGMA table_info(saved_words)")
                    columns = [col[1] for col in old_cursor.fetchall()]
                    
                    # Build query based on available columns
                    select_columns = []
                    for col in ['text', 'value', 'cipher_type', 'notes', 'tags', 'created_at']:
                        if col in columns:
                            select_columns.append(col)
                        else:
                            select_columns.append("NULL AS " + col)
                    
                    query = f"SELECT {', '.join(select_columns)} FROM saved_words"
                    old_cursor.execute(query)
                    rows = old_cursor.fetchall()
                    
                    # Insert into new database
                    for row in rows:
                        try:
                            # Only use columns that exist in both databases
                            available_cols = []
                            values = []
                            for i, col in enumerate(select_columns):
                                if "NULL AS" not in col:
                                    available_cols.append(col)
                                    values.append(row[i])
                            
                            placeholders = ", ".join(["?" for _ in available_cols])
                            insert_query = f"INSERT OR IGNORE INTO saved_words ({', '.join(available_cols)}) VALUES ({placeholders})"
                            new_cursor.execute(insert_query, values)
                        except Exception as e:
                            print(f"Error migrating row {row}: {e}")
                    
                    new_conn.commit()
                    
                    # Verify migration
                    new_cursor.execute("SELECT COUNT(*) FROM saved_words")
                    final_count = new_cursor.fetchone()[0]
                    print(f"Migration from {old_db_path} complete. New database now has {final_count} records")
                    
                    # Close connections
                    old_conn.close()
                    new_conn.close()
                    
                except Exception as e:
                    import traceback
                    print(f"Error during migration from {old_db_path}: {e}")
                    print(traceback.format_exc())

    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'batch_queue'):
            self.batch_queue.put(None)
        if hasattr(self, 'worker_thread'):
            self.worker_thread.join(timeout=1)
        if hasattr(self, 'conn'):
            self.conn.close()
