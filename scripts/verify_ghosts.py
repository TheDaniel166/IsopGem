
import os
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from shared.config import get_config  # noqa: E402

DB_PATH = str(get_config().paths.main_db)

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
