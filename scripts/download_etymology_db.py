#!/usr/bin/env python3
"""
Download the etymology-db dataset.

Source: https://github.com/droher/etymology-db
Dataset: 4.2M+ etymological relationships from Wiktionary (2023-12-05)
License: Apache 2.0 / CC-BY-SA 3.0

MANUAL DOWNLOAD REQUIRED (OneDrive links require browser authentication):
1. Visit: https://github.com/droher/etymology-db
2. Click the "Gzipped CSV" link in the README
3. OneDrive will prompt you to download
4. Save the file to: data/etymology_db/etymology.csv.gz
5. Expected size: ~100 MB compressed, 4.2M rows

The dataset contains:
- term_id: hash of term + language
- lang: language code (e.g., 'English', 'Latin')
- term: the word itself
- reltype: relationship type (inherited_from, borrowed_from, etc.)
- related_term_id, related_lang, related_term: the etymological source
- position, group_tag, parent_tag, parent_position: for complex relationships
"""
import sys
from pathlib import Path

ETYMOLOGY_DIR = Path(__file__).parent.parent / "data" / "etymology_db"
ETYMOLOGY_FILE = ETYMOLOGY_DIR / "etymology.csv.gz"
MINIMUM_SIZE_MB = 50  # If smaller than this, likely incomplete download

def check_dataset():
    """Check if dataset exists and is complete."""
    if not ETYMOLOGY_FILE.exists():
        print("✗ Etymology dataset not found")
        print(f"\nDownload required:")
        print(f"1. Visit: https://github.com/droher/etymology-db")
        print(f"2. Click 'Gzipped CSV' in README")
        print(f"3. Save to: {ETYMOLOGY_FILE}")
        print(f"\nExpected size: ~100 MB")
        return False
    
    size_mb = ETYMOLOGY_FILE.stat().st_size / (1024 * 1024)
    
    if size_mb < MINIMUM_SIZE_MB:
        print(f"⚠ Etymology dataset incomplete: {size_mb:.1f} MB")
        print(f"   Expected: ~100 MB")
        print(f"\nPlease re-download from:")
        print(f"   https://github.com/droher/etymology-db")
        return False
    
    print(f"✓ Etymology dataset found: {ETYMOLOGY_FILE}")
    print(f"  Size: {size_mb:.1f} MB")
    print(f"  Estimated rows: ~4.2 million")
    return True

if __name__ == "__main__":
    if not check_dataset():
        sys.exit(1)
