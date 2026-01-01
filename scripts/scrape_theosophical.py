#!/usr/bin/env python3
"""
Scrape the Theosophical Glossary and save to local cache.

Usage:
    python scripts/scrape_theosophical.py
    
This will fetch all ~70 section pages and save entries to:
    data/openoccult/theosophical.json
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pillars.tq_lexicon.services.theosophical_glossary_service import TheosophicalGlossaryService


def main():
    print("=" * 60)
    print("Theosophical Glossary Scraper")
    print("=" * 60)
    print()
    
    service = TheosophicalGlossaryService()
    
    def progress(current, total, message):
        pct = int(current / total * 100) if total > 0 else 0
        print(f"  [{pct:3d}%] {message}")
    
    print("Starting scrape...")
    print("This will make ~70 HTTP requests with rate limiting.")
    print()
    
    count = service.scrape_all(progress_callback=progress)
    
    print()
    print(f"Complete! Scraped {count} entries.")
    print(f"Cache saved to: {service.cache_path}")
    
    # Test lookup
    print()
    print("Testing lookups:")
    for term in ["karma", "sephiroth", "akasha", "manas"]:
        results = service.lookup(term)
        if results:
            print(f"  ✓ '{term}' → {len(results)} entries found")
        else:
            print(f"  ✗ '{term}' → not found")


if __name__ == "__main__":
    main()
