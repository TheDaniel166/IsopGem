import sqlite3
import os

DB_PATH = "src/data/isopgem.db"  # Correct path relative to project root

def add_column(cursor, table, column, type_def):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}")
        print(f"Added column {column} to {table}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"Column {column} already exists in {table}")
        else:
            print(f"Error adding {column}: {e}")

def update_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found. It will be created by the app.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    add_column(cursor, "documents", "tags", "TEXT")
    add_column(cursor, "documents", "author", "TEXT")
    add_column(cursor, "documents", "collection", "TEXT")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_schema()
