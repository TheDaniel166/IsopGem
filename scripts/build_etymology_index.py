#!/usr/bin/env python3
"""
Build a word index for the etymology CSV to enable fast lookups.

Creates: data/etymology_db/word_index.json
Format: {"word": {"start_row": N, "count": M}, ...}

This allows direct navigation to word locations instead of scanning 4.2M rows.
"""
import gzip
import csv
import json
import logging
from pathlib import Path
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def build_index():
    """Build word index from etymology CSV."""
    csv_path = Path(__file__).parent.parent / "data" / "etymology_db" / "etymology.csv.gz"
    index_path = csv_path.parent / "word_index.json"
    
    if not csv_path.exists():
        logger.error(f"❌ Etymology CSV not found: {csv_path}")
        return
    
    logger.info("Building etymology word index...")
    logger.info(f"  Source: {csv_path}")
    logger.info(f"  Target: {index_path}")
    logger.info("")
    
    # Map word -> first row where it appears
    word_positions = {}
    word_counts = defaultdict(int)
    
    with gzip.open(csv_path, 'rt', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=1):
            lang = row.get('lang', '')
            term = row.get('term', '').lower()
            
            # Only index English terms
            if lang == 'English' and term:
                # Track first occurrence
                if term not in word_positions:
                    word_positions[term] = row_num
                word_counts[term] += 1
            
            # Progress indicator
            if row_num % 500_000 == 0:
                logger.info(f"  Processed {row_num:,} rows, indexed {len(word_positions):,} unique English words...")
    
    # Build final index structure
    index = {
        word: {
            "start_row": word_positions[word],
            "count": word_counts[word]
        }
        for word in word_positions
    }
    
    logger.info(f"")
    logger.info(f"✓ Indexed {len(index):,} unique English words")
    logger.info(f"  Total relationships: {sum(word_counts.values()):,}")
    logger.info(f"  Average per word: {sum(word_counts.values()) / len(index):.1f}")
    
    # Save index
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, separators=(',', ':'))
    
    size_mb = index_path.stat().st_size / (1024 * 1024)
    logger.info(f"  Index size: {size_mb:.1f} MB")
    logger.info(f"")
    logger.info(f"✓ Index saved: {index_path}")

if __name__ == '__main__':
    build_index()
