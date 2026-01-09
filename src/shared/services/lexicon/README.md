# Lexicon Services Architecture

This directory contains the lexicon lookup services used throughout Isopgem.

## Service Hierarchy

```
┌─────────────────────────────────────────────────────────┐
│              etymology_service.py                       │
│  (Document Manager - RTF Editor Etymology Feature)     │
│  • Handles UI formatting (HTML output)                  │
│  • Aggregates results from multiple sources             │
│  • Includes web fallbacks (Sefaria, Wiktionary scraping)│
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ uses
                   ▼
┌─────────────────────────────────────────────────────────┐
│            lexicon_resolver.py                          │
│  (Thin wrapper for unified interface)                  │
│  • Simple delegation to underlying services             │
│  • No business logic or formatting                      │
│  • Clean API for etymology_service                      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ delegates to
                   ▼
      ┌────────────────────────────┐
      │                            │
      ▼                            ▼
┌──────────────────┐    ┌─────────────────────────┐
│ comprehensive_   │    │ classical_lexicon_      │
│ lexicon_service  │    │ service.py              │
│                  │    │                         │
│ • Kaikki compact │    │ • Wraps comprehensive   │
│   data           │    │ • Adds Strong's lookups │
│ • Fast lookups   │    │ • Handles variants      │
│ • All languages  │    │ • Hebrew/Greek focused  │
└──────────────────┘    └─────────────────────────┘
```

## Key Services

### 1. `comprehensive_lexicon_service.py`
- **Purpose**: Low-level access to Kaikki compact lexicon data
- **Data Source**: Pre-processed Wiktionary data from kaikki.org
- **Languages**: Hebrew, Greek, Latin, English, Sanskrit, Aramaic, Proto-Indo-European, and more
- **Output**: `LexiconEntry` objects (word, definition, etymology, transliteration, morphology, source)

### 2. `classical_lexicon_service.py`
- **Purpose**: Enhanced lookups for Hebrew and Greek with Strong's numbers
- **Wraps**: `ComprehensiveLexiconService`
- **Additions**:
  - Strong's Hebrew/Greek lexicons
  - Perseus Classical Greek dictionary
  - Unicode normalization and accent removal
  - Variant generation for better matching
- **Output**: `LexiconEntry` objects

### 3. `lexicon_resolver.py`
- **Purpose**: Thin wrapper providing unified API
- **Role**: Simple delegation layer - no duplication
- **Output**: `LexiconEntry` objects from underlying services
- **Used By**: `etymology_service.py`

### 4. `etymology_service.py` (Document Manager)
- **Purpose**: Full-featured etymology lookup for RTF editor
- **Features**:
  - Script detection (Hebrew, Greek, Latin)
  - HTML formatting for UI display
  - Web fallbacks (Sefaria API, Wiktionary scraping)
  - Etymology graph integration
  - ety-python library integration
- **Output**: Formatted HTML for `ResearchDialog`
- **Uses**: `LexiconResolver` for offline lexicon lookups

## Why This Architecture?

### Before (The Problem)
- `etymology_service.py` directly used `ClassicalLexiconService`
- Creating `LexiconResolver` duplicated all the logic
- `LexiconResolver` had its own `LexiconResult` dataclass
- Nothing was using `LexiconResolver`
- Confusion about which service to use

### After (The Solution)
- `LexiconResolver` is a thin wrapper (no duplication)
- `etymology_service.py` uses `LexiconResolver` for cleaner interface
- All services return `LexiconEntry` objects (consistent data structure)
- Clear separation of concerns:
  - **Data access**: comprehensive/classical services
  - **Unified API**: lexicon_resolver
  - **UI presentation**: etymology_service

## Data Flow Example: Hebrew Word Lookup

```
User clicks "Word Origin" on שלום
         │
         ▼
etymology_service._lookup_hebrew_lexicon("שלום")
         │
         ▼
lexicon_resolver.lookup_hebrew("שלום")
         │
         ▼
classical_lexicon_service.lookup_hebrew("שלום")
         │
         ├─▶ comprehensive_lexicon_service.lookup("שלום", "Hebrew")
         │   └─▶ Returns Kaikki entries
         │
         └─▶ strong's_hebrew lookup
             └─▶ Returns Strong's entries
         │
         ▼
Returns List[LexiconEntry]
         │
         ▼
etymology_service._format_entries(...)
         │
         ▼
Returns HTML formatted result
         │
         ▼
ResearchDialog.show_result(html)
```

## Adding New Lexicon Sources

To add a new lexicon source:

1. Add data loading in `comprehensive_lexicon_service.py` OR
2. Add specialized logic in `classical_lexicon_service.py`
3. Optionally add convenience method in `lexicon_resolver.py`
4. Use in `etymology_service.py` via resolver

## Testing

```bash
# Test the resolver
python -m pytest tests/services/lexicon/test_lexicon_resolver.py

# Test etymology service
python -m pytest tests/services/document_manager/test_etymology_service.py
```

## Memory Management

**⚠️ IMPORTANT**: Large lexicon indexes (English: 37MB, Latin: 19MB) are lazy-loaded and stay in memory.

### Optimization Strategy

The enrichment service skips loading large English/Latin indexes because:
- They consume 56MB+ of memory
- We have better English sources (Etymology-DB, FreeDict API)
- Only Hebrew/Greek lookups need the compact lexicons

### Clearing Caches

If memory usage is high, clear the caches:

```python
from shared.services.lexicon.lexicon_resolver import LexiconResolver

resolver = LexiconResolver()
# ... do lookups ...

# Free memory
resolver.comprehensive.clear_caches()
resolver.classical.clear_caches()
```

See [MEMORY_OPTIMIZATION.md](../../../docs/MEMORY_OPTIMIZATION.md) for details.

## Notes

- The resolver is intentionally thin - it doesn't do any processing
- All formatting happens in etymology_service for UI display
- Classical service handles Hebrew/Greek variants (accents, nikud, etc.)
- Comprehensive service is the fastest for simple lookups
- Etymology service adds web fallbacks when offline sources fail
- **Memory-conscious**: Enrichment service only loads Hebrew/Greek indexes, not English/Latin
