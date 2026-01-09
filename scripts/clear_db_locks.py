#!/usr/bin/env python3
"""Clean up database lock files."""
from pathlib import Path

db_dir = Path.home() / ".isopgem"
lock_files = [
    db_dir / "holy_key.db-shm",
    db_dir / "holy_key.db-wal"
]

for lock_file in lock_files:
    if lock_file.exists():
        lock_file.unlink()
        print(f"✓ Removed {lock_file.name}")
    else:
        print(f"  {lock_file.name} not found")

print("\nDatabase locks cleared. Restart the app.")
