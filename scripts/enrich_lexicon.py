#!/usr/bin/env python3
"""
The Rite of Enrichment
----------------------
A script to automatically populate the Holy Key Lexicon with:
1. Etymologies (via 'ety' library)
2. Definitions (via Free Dictionary API)

This script respects the "Sovereignty" of the Holy Key by only 
enriching keys that have NO existing definitions.

Usage:
  python3 scripts/enrich_lexicon.py
"""
import sys
import os
import time
import requests
import ety
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from pillars.tq_lexicon.services.holy_key_service import HolyKeyService

def fetch_definitions(word):
    """Fetch definitions from Free Dictionary API."""
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                # Extract first meaning
                # We could get more, but let's stick to the primary one for now
                meanings = data[0].get('meanings', [])
                defs = []
                for m in meanings:
                    part_of_speech = m.get('partOfSpeech', 'unknown')
                    for d in m.get('definitions', [])[:1]: # Take top def per POS
                        defs.append(f"({part_of_speech}) {d.get('definition')}")
                return defs
    except Exception as e:
        print(f"  [!] API Error for '{word}': {e}")
    return []

def get_etymology(word):
    """Fetch etymology using local 'ety' library."""
    try:
        origins = ety.origins(word)
        if origins:
            # Format nicely: "word (lang) < root (lang)"
            return [str(o) for o in origins]
    except Exception as e:
        print(f"  [!] Etymology Error for '{word}': {e}")
    return []

def main():
    service = HolyKeyService()
    
    print("=== The Rite of Enrichment ===")
    
    # Get target keys
    targets = service.get_undefined_keys()
    total = len(targets)
    print(f"Found {total} keys requiring enrichment.")
    
    if total == 0:
        print("Nothing to do.")
        return

    processed = 0
    enriched = 0
    
    for key_id, word in targets:
        processed += 1
        print(f"[{processed}/{total}] Enriching '{word}'...")
        
        has_update = False
        
        # 1. Etymology
        etyms = get_etymology(word)
        if etyms:
            content = "Recursive Origins: " + "; ".join(etyms[:3]) # Limit to 3 branches
            service.db.add_definition(key_id, "Etymology", content, source="ety-python")
            print(f"  + Added Etymology")
            has_update = True
            
        # 2. Definitions
        # Add slight delay to be nice to API
        time.sleep(0.5) 
        defs = fetch_definitions(word)
        for d in defs:
            service.db.add_definition(key_id, "Standard", d, source="FreeDict API")
            print(f"  + Added Definition: {d[:30]}...")
            has_update = True
            
        if has_update:
            enriched += 1
            
    print("-" * 30)
    print(f"Rite Complete.")
    print(f"Processed: {processed}")
    print(f"Enriched: {enriched}")

if __name__ == "__main__":
    main()
