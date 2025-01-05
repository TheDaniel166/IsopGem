import sqlite3

class WordRepository:
    def __init__(self):
        self.conn = sqlite3.connect('isopgem.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_words (
                id INTEGER PRIMARY KEY,
                text TEXT NOT NULL,
                cipher_type TEXT NOT NULL,
                value INTEGER NOT NULL,
                UNIQUE(text, cipher_type)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calculation_history (
                id INTEGER PRIMARY KEY,
                text TEXT NOT NULL,
                cipher_type TEXT NOT NULL,
                value INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

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

    def get_saved_words(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT text, cipher_type, value 
            FROM saved_words 
            ORDER BY text
        ''')
        return cursor.fetchall()
