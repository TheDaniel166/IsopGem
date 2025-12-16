import sqlite3
import os

DB_PATH = "data/isopgem.db"

def migrate_mindscape():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    print(f"Migrating Mindscape Schema in {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Helpers
    def column_exists(table, col):
        try:
            cursor.execute(f"SELECT {col} FROM {table} LIMIT 1")
            return True
        except sqlite3.OperationalError:
            return False

    def add_column(table, col, type_def):
        if not column_exists(table, col):
            print(f"Adding {col} to {table}...")
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {type_def}")
                print(f"  Success: Added {col}")
            except Exception as e:
                print(f"  Error adding {col}: {e}")
        else:
            print(f"Skipping {col} (already exists in {table})")

    # MindNodes Migration
    add_column("mind_nodes", "content", "TEXT")
    add_column("mind_nodes", "tags", "TEXT")
    add_column("mind_nodes", "appearance", "TEXT")
    add_column("mind_nodes", "metadata_payload", "TEXT")
    add_column("mind_nodes", "document_id", "INTEGER")

    # MindEdges Migration
    add_column("mind_edges", "appearance", "TEXT")

    conn.commit()
    conn.close()
    print("Migration Complete.")

if __name__ == "__main__":
    migrate_mindscape()
