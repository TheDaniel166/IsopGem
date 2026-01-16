import os
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from shared.config import get_config  # noqa: E402

DB_PATH = str(get_config().paths.main_db)

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
    add_column(cursor, "documents", "section_id", "INTEGER")
    add_column(cursor, "documents", "layout_json", "TEXT")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_documents_section_id ON documents(section_id)")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_schema()
