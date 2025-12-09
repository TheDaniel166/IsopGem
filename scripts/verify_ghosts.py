
import sqlite3
import os

DB_PATH = os.path.join("data", "isopgem.db")

def check_ghosts():
    if not os.path.exists(DB_PATH):
        print("No DB found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'mindmap%'")
    rows = cursor.fetchall()
    
    if rows:
        print(f"GHOSTS FOUND: {rows}")
    else:
        print("No Mindscape tables found.")
    
    conn.close()

if __name__ == "__main__":
    check_ghosts()
