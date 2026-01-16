#!/usr/bin/env python3
"""Quick test of etymology CSV streaming query."""

from src.shared.services.lexicon.etymology_db_service import EtymologyDbService
import time

def test_query():
    service = EtymologyDbService()
    
    # Test common word
    print("Testing etymology query for 'love'...")
    start = time.time()
    results = service.get_etymologies('love', max_results=5)
    elapsed = time.time() - start
    
    print(f"Found {len(results)} results in {elapsed:.3f} seconds")
    
    for rel in results:
        print(f"  - {rel.to_display()}")
    
    if results:
        print("✓ Query successful!")
    else:
        print("⚠ No results (CSV may not exist or word not found)")
    
    # Show stats
    stats = service.get_stats()
    print(f"\nDataset info:")
    for key, val in stats.items():
        print(f"  {key}: {val}")

if __name__ == '__main__':
    test_query()
