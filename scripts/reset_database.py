#!/usr/bin/env python3
import shutil
import os
from pathlib import Path

def reset_database():
    """
    Deletes the Whoosh index directory to reset the database.
    """
    # Default path as defined in CalculationRepository
    home = Path.home()
    db_path = home / '.isopgem' / 'calculations'
    
    print(f"Targeting database at: {db_path}")
    
    if db_path.exists():
        try:
            shutil.rmtree(db_path)
            print("Database successfully deleted.")
        except Exception as e:
            print(f"Error deleting database: {e}")
    else:
        print("Database directory does not exist. Nothing to delete.")

if __name__ == "__main__":
    confirmation = input("Are you sure you want to delete the entire database? This cannot be undone. (y/N): ")
    if confirmation.lower() == 'y':
        reset_database()
    else:
        print("Operation cancelled.")
