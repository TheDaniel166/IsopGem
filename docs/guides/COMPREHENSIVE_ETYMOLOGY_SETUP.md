# Comprehensive Etymology System Setup

This guide explains how to download and configure the comprehensive multi-language etymology system for IsopGem.

## Overview

The system supports **50+ languages** organized into 6 categories:

1. **Core Ancient** (7 languages): English, Latin, Ancient Greek, Hebrew, Sanskrit, PIE, Aramaic
2. **Medieval Bridge** (8 languages): Old English, Middle English, Old French, Gothic, Old Norse, etc.
3. **Ancient Semitic** (6 languages): Akkadian, Syriac, Phoenician, Ugaritic, Ancient Hebrew, Coptic
4. **Ancient Indo-European** (6 languages): Avestan, Old Persian, Pali, Prakrit, Tocharian, Hittite
5. **Modern Major** (10 languages): French, German, Spanish, Italian, Portuguese, Russian, Greek, Arabic, Chinese, Japanese
6. **Other Ancient** (5 languages): Sumerian, Egyptian, Classical Syriac, Middle Persian, Elamite

## Quick Start

### 1. Download Dictionaries

Run the comprehensive downloader script:

```bash
# Download all tiers interactively (prompts for each tier)
python scripts/download_kaikki_comprehensive.py

# Download all tiers automatically (no prompts)
python scripts/download_kaikki_comprehensive.py --auto

# Download specific tier only
python scripts/download_kaikki_comprehensive.py --tier=core_ancient
python scripts/download_kaikki_comprehensive.py --tier=medieval_bridge
```

**Estimated sizes:**
- Core Ancient: ~3.5 GB (already have most)
- Medieval Bridge: ~100 MB
- Ancient Semitic: ~35 MB
- Ancient Indo-European: ~40 MB
- Modern Major: ~4 GB
- Other Ancient: ~25 MB

**Total: ~8 GB for complete system**

### 2. Build Indexes

After downloading dictionaries, build compact indexes for fast lookup:

```bash
python scripts/build_kaikki_indexes.py
```

This creates:
- `data/lexicons/indexes/kaikki-<language>-mini.jsonl` - Compact data
- `data/lexicons/indexes/kaikki-<language>-index.json` - Fast lookup index

Indexing takes ~10-30 minutes for the complete set.

### 3. Verify Installation

Check which languages are available:

```python
from src.shared.services.lexicon.comprehensive_lexicon_service import ComprehensiveLexiconService

service = ComprehensiveLexiconService()
stats = service.get_stats()

print(f"Configured: {stats['total_configured']} languages")
print(f"Available: {stats['total_available']} languages")
print(f"Available languages: {', '.join(stats['available_languages'])}")
```

## Usage Examples

### Basic Word Lookup

```python
from src.shared.services.lexicon.comprehensive_lexicon_service import ComprehensiveLexiconService

service = ComprehensiveLexiconService()

# Look up a word in Old English
results = service.lookup("word", "Old English")
for entry in results:
    print(f"{entry.word} - {entry.definition}")

# Look up across multiple languages
results = service.lookup_multi_language("love", ["Latin", "Old French", "Old English"])
for language, entries in results.items():
    print(f"\n{language}:")
    for entry in entries:
        print(f"  {entry.word}: {entry.definition}")

# Look up all languages in a category
results = service.lookup_by_category("god", "ancient_semitic")
for language, entries in results.items():
    print(f"\n{language}:")
    for entry in entries:
        print(f"  {entry.word}: {entry.definition}")
```

### Integration with Etymology Service

The `EtymologyService` automatically uses all available languages:

```python
from src.shared.services.document_manager.etymology_service import get_etymology_service

service = get_etymology_service()

# The service will now search across ALL available offline lexicons
result = service.get_word_origin("king")

print(f"Source: {result['source']}")
print(f"Origin: {result['origin']}")
```

## Architecture

### Data Flow

```
User Query
    ↓
EtymologyService (auto-detects script: Hebrew/Greek/Latin)
    ↓
ComprehensiveLexiconService (queries all configured languages)
    ↓
[For each language]
    ↓
Load compact index (word → byte offset)
    ↓
Seek to offset in mini.jsonl
    ↓
Return entry with definition + etymology
```

### File Structure

```
data/lexicons/
├── kaikki.org-dictionary-English.jsonl          (2.7 GB - full)
├── kaikki.org-dictionary-Latin.jsonl            (1 GB - full)
├── kaikki.org-dictionary-OldEnglish.jsonl       (20 MB - full)
├── ...
└── indexes/
    ├── kaikki-english-mini.jsonl                (273 MB - compact)
    ├── kaikki-english-index.json                (word → offset)
    ├── kaikki-latin-mini.jsonl                  (156 MB - compact)
    ├── kaikki-latin-index.json
    └── ...
```

**Memory efficiency:**
- Full dictionaries: Multi-GB, slow to scan
- Compact indexes: ~10-20% of original size
- Instant lookup via byte offset
- Only loads one entry at a time (minimal RAM)

## Adding New Languages

To add a new language:

### 1. Add to Configuration

Edit `src/shared/services/lexicon/language_config.py`:

```python
LanguageConfig("Mycenaean Greek", "mycenaean-greek", "ancient_ie", "linear-b", priority=36),
```

### 2. Add to Download Script

Edit `scripts/download_kaikki_comprehensive.py`:

```python
"ancient_ie": [
    # ... existing languages ...
    ("MycenaeanGreek", "Mycenaean Greek", "~3MB", "Bronze Age Greek"),
],
```

### 3. Add to Index Builder

Edit `scripts/build_kaikki_indexes.py`:

```python
{"name": "Mycenaean Greek", "slug": "mycenaean-greek", "source": "kaikki.org-dictionary-MycenaeanGreek.jsonl"},
```

### 4. Download and Index

```bash
python scripts/download_kaikki_comprehensive.py --tier=ancient_ie
python scripts/build_kaikki_indexes.py
```

That's it! The language is now automatically available throughout the system.

## Performance

### Lookup Speed

With compact indexes:
- **Cold start** (first query): ~50-200ms (loads index)
- **Warm queries**: ~1-5ms per language
- **Multi-language query** (10 languages): ~10-50ms total

### Memory Usage

- Base service: ~5 MB
- Per loaded index: ~1-50 MB (depending on language size)
- File handles: Minimal (kept open for reuse)
- Total for active use: ~100-500 MB

### Disk Space

- Full system: ~8 GB (dictionaries) + ~2 GB (indexes) = **~10 GB total**
- Minimum viable (core ancient only): ~4 GB
- Medieval + Ancient only: ~5 GB

## Data Sources

All dictionaries sourced from:
- **Kaikki.org** (https://kaikki.org/dictionary/)
  - Extracted from Wiktionary
  - License: CC BY-SA 4.0 + GFDL
  - Updated monthly
  - Machine-readable JSONL format

- **Strong's Dictionaries** (Hebrew & Greek)
  - Public domain
  - ~14,000 entries (5.5k Greek + 8.6k Hebrew)

- **Etymology-DB Graph** (4.2M relationships)
  - https://github.com/droher/etymology-db
  - Structured Wiktionary etymology data
  - 31 relationship types

## Troubleshooting

### "Dictionary not found" warnings

If you see warnings during indexing:
```
Old English: source not found at data/lexicons/kaikki.org-dictionary-OldEnglish.jsonl
```

This means the dictionary wasn't downloaded (not available at Kaikki.org or failed to download).

**Solution:** Check if the language is available at https://kaikki.org/dictionary/

### Index building is slow

For very large dictionaries (English, Latin, Spanish), indexing can take 5-10 minutes per language.

**Solution:** Run in background or only index languages you need.

### Out of disk space

**Solution:** Download only specific tiers:
```bash
# Essential only
python scripts/download_kaikki_comprehensive.py --tier=core_ancient

# Add medieval languages
python scripts/download_kaikki_comprehensive.py --tier=medieval_bridge
```

## Future Enhancements

Potential additions:
- **Phoenician Dictionary**: More comprehensive than Kaikki
- **Hittite Cuneiform**: Specialized academic lexicons
- **Ugaritic**: Ras Shamra texts
- **Egyptian Hieroglyphic**: Budge's dictionary
- **Interlinear linking**: Click etymology terms to explore further
- **Phonetic reconstruction**: PIE sound changes visualization

## License

- IsopGem Code: MIT License
- Kaikki.org Data: CC BY-SA 4.0 + GFDL
- Strong's Dictionaries: Public Domain
- Etymology-DB: CC BY-SA 4.0
