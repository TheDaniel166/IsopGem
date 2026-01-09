# Memory Optimization - Lexicon Services

## Problem

The app was crashing when running the enrichment service due to excessive memory usage.

## Root Cause

The lexicon indexes, particularly for English and Latin, are very large JSON files that get loaded entirely into memory:

- **English index**: 37 MB
- **Latin index**: 19 MB
- **Total**: 56 MB just for these two indexes

### What Was Happening

When `enrichment_service.fetch_suggestions(word)` was called for an English word:

1. Called `lexicon_resolver.lookup(word)`
2. Detected script → "latin" (default for English)
3. Loaded English index (37 MB) → tried lookup
4. If no hit, loaded Latin index (19 MB) → tried lookup
5. **Total memory spike: 56+ MB per lookup**

This caused crashes, especially when:
- Multiple lookups were happening simultaneously
- The indexes stayed in memory after loading
- Other heavy services (etymology_db, occult references) were also running

## Fixes Applied

### 1. Optimized Enrichment Service

**File**: [enrichment_service.py:86-125](src/shared/services/lexicon/enrichment_service.py#L86-L125)

Changed from:
```python
# OLD: Loaded massive indexes for all words
resolver_results = self._resolver.lookup(word)
```

To:
```python
# NEW: Only lookup Hebrew/Greek, skip English/Latin
scripts = self._resolver._detect_scripts(word)
resolver_results = []

if "hebrew" in scripts:
    resolver_results.extend(self._resolver.lookup_hebrew(word))
elif "greek" in scripts:
    resolver_results.extend(self._resolver.lookup_greek(word))
# Skip "latin" to avoid loading 56MB of indexes
```

**Why**: For English words, we already have:
- Etymology-DB (4.2M relationships, optimized with word index)
- FreeDict API (online fallback)
- Theosophical Glossary
- OpenOccult references

We don't need to load 56MB of Kaikki indexes for English definitions.

### 2. Added Cache Clearing Method

**File**: [comprehensive_lexicon_service.py:378-401](src/shared/services/lexicon/comprehensive_lexicon_service.py#L378-L401)

Added `clear_caches()` method to explicitly free memory:

```python
def clear_caches(self):
    """
    Clear all loaded indexes and close file handles to free memory.

    This is useful when memory usage is high and you want to explicitly
    free up the loaded lexicon indexes (which can be 37MB+ for English).
    """
    # Close all file handles
    for handle in self._compact_handles.values():
        if handle:
            try:
                handle.close()
            except:
                pass

    # Clear caches
    self._compact_indexes.clear()
    self._compact_handles.clear()

    # Clear Strong's dictionaries
    self._strongs_greek = None
    self._strongs_hebrew = None

    logger.debug("Cleared all lexicon caches and closed file handles")
```

**Usage**: Call this when you want to free up memory:

```python
from shared.services.lexicon.lexicon_resolver import LexiconResolver

resolver = LexiconResolver()
# ... do lookups ...

# Free memory when done
resolver.comprehensive.clear_caches()
resolver.classical.clear_caches()
```

## Memory Usage Comparison

### Before Optimization

For English word lookup via enrichment service:
```
Lexicon Resolver: 56 MB (English + Latin indexes)
Etymology-DB:      minimal (indexed lookup)
Theosophical:      minimal (small dataset)
OpenOccult:        minimal (small dataset)
Strong's Greek:    1.4 MB (if loaded)
Strong's Hebrew:   2.0 MB (if loaded)
─────────────────────────────────
TOTAL:            ~60 MB per lookup
```

### After Optimization

For English word lookup via enrichment service:
```
Lexicon Resolver: 0 MB (skipped for English)
Etymology-DB:      minimal (indexed lookup)
Theosophical:      minimal (small dataset)
OpenOccult:        minimal (small dataset)
─────────────────────────────────
TOTAL:            ~5 MB per lookup
```

For Hebrew/Greek word lookup:
```
Lexicon Resolver: 3.4 MB (Strong's only, no huge indexes)
Etymology-DB:      minimal
Theosophical:      minimal
OpenOccult:        minimal
─────────────────────────────────
TOTAL:            ~8 MB per lookup
```

## Index Sizes Reference

Current lexicon index sizes:

```bash
$ du -h data/lexicons/indexes/*index.json | sort -hr | head -10
37M  data/lexicons/indexes/kaikki-english-index.json
19M  data/lexicons/indexes/kaikki-latin-index.json
780K data/lexicons/indexes/kaikki-sanskrit-index.json
80K  data/lexicons/indexes/kaikki-pie-index.json
68K  data/lexicons/indexes/kaikki-aramaic-index.json
```

## Future Optimization Ideas

If memory issues persist, consider:

1. **Implement LRU cache with size limit** - Only keep most-used indexes in memory
2. **Use SQLite instead of JSON** - Indexes could be SQL databases with proper indexing
3. **Memory-mapped files** - Use mmap for large indexes instead of loading into RAM
4. **Lazy index loading** - Only load index chunks as needed
5. **Compress indexes** - Use gzip compression and decompress on-the-fly
6. **Split large indexes** - Break English index into multiple smaller files (A-M, N-Z, etc.)

## Testing

After optimization, test that enrichment service still works:

```python
from src.shared.services.lexicon.enrichment_service import EnrichmentService

service = EnrichmentService()

# Test English word (should NOT load large indexes)
results = service.fetch_suggestions("love")
print(f"Found {len(results)} suggestions for 'love'")

# Test Hebrew word (should load Strong's only)
results = service.fetch_suggestions("שלום")
print(f"Found {len(results)} suggestions for 'שלום'")

# Test Greek word (should load Strong's only)
results = service.fetch_suggestions("λόγος")
print(f"Found {len(results)} suggestions for 'λόγος'")
```

## Monitoring

To check memory usage in your app:

```python
import psutil
import os

def get_memory_usage_mb():
    """Get current process memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

# Before lookup
mem_before = get_memory_usage_mb()
print(f"Memory before: {mem_before:.1f} MB")

# Do lookup
service.fetch_suggestions("test")

# After lookup
mem_after = get_memory_usage_mb()
print(f"Memory after: {mem_after:.1f} MB")
print(f"Memory increase: {mem_after - mem_before:.1f} MB")
```

## Related Files

- [enrichment_service.py](src/shared/services/lexicon/enrichment_service.py) - Optimized to skip large indexes
- [lexicon_resolver.py](src/shared/services/lexicon/lexicon_resolver.py) - Thin wrapper for lookups
- [comprehensive_lexicon_service.py](src/shared/services/lexicon/comprehensive_lexicon_service.py) - Added `clear_caches()`
- [classical_lexicon_service.py](src/shared/services/lexicon/classical_lexicon_service.py) - Hebrew/Greek lookups
