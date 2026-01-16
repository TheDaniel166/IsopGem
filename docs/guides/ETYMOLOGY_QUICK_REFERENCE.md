# Etymology System - Quick Reference

## Command Cheat Sheet

### Download Dictionaries

```bash
# Interactive (prompts for each tier)
python scripts/download_kaikki_comprehensive.py

# Automatic (download all)
python scripts/download_kaikki_comprehensive.py --auto

# Specific tier
python scripts/download_kaikki_comprehensive.py --tier=core_ancient
python scripts/download_kaikki_comprehensive.py --tier=medieval_bridge
python scripts/download_kaikki_comprehensive.py --tier=ancient_semitic
```

### Build Indexes

```bash
# Build all indexes
python scripts/build_kaikki_indexes.py

# Downloads + indexes (legacy Strong's)
python scripts/download_lexicons.py
```

### Download Etymology Graph

```bash
python scripts/download_etymology_db.py
python scripts/build_etymology_index.py
```

## Language Categories

### Tier 1: Core Ancient (7 languages)
- English, Latin, Ancient Greek, Hebrew, Sanskrit, Proto-Indo-European, Aramaic
- **Size:** ~3.5 GB
- **Use case:** Essential for all etymology work

### Tier 2: Medieval Bridge (8 languages)
- Old English, Middle English, Old French, Gothic, Old Norse, Old High German, Old Irish, Old Church Slavonic
- **Size:** ~100 MB
- **Use case:** English/Germanic/Romance etymology chains

### Tier 3: Ancient Semitic (6 languages)
- Akkadian, Syriac, Phoenician, Ugaritic, Ancient Hebrew, Coptic
- **Size:** ~35 MB
- **Use case:** Hebrew Bible, ancient Near East

### Tier 4: Ancient Indo-European (6 languages)
- Avestan, Old Persian, Pali, Prakrit, Tocharian, Hittite
- **Size:** ~40 MB
- **Use case:** Comparative Indo-European linguistics

### Tier 5: Modern Major (10 languages)
- French, German, Spanish, Italian, Portuguese, Russian, Modern Greek, Arabic, Chinese, Japanese
- **Size:** ~4 GB
- **Use case:** Modern language coverage

### Tier 6: Other Ancient (5 languages)
- Sumerian, Egyptian, Classical Syriac, Middle Persian, Elamite
- **Size:** ~25 MB
- **Use case:** Ancient civilizations

## Python API

### Basic Lookup

```python
from src.shared.services.lexicon.comprehensive_lexicon_service import ComprehensiveLexiconService

service = ComprehensiveLexiconService()

# Single language
results = service.lookup("love", "Latin")

# Multiple languages
results = service.lookup_multi_language("king", ["Old English", "Gothic", "Old Norse"])

# By category
results = service.lookup_by_category("god", "ancient_semitic")

# Check available
available = service.get_available_languages()
```

### Etymology Service (Auto-routing)

```python
from src.shared.services.document_manager.etymology_service import get_etymology_service

service = get_etymology_service()

# Auto-detects Hebrew script
result = service.get_word_origin("שָׁלוֹם")

# Auto-detects Greek script
result = service.get_word_origin("λόγος")

# Latin/English - queries all offline sources
result = service.get_word_origin("love")
```

### Etymology Graph

```python
from src.shared.services.lexicon.etymology_db_service import EtymologyDbService

service = EtymologyDbService()

# Get relationships
relations = service.get_etymologies("love", lang="English", max_results=10)

for rel in relations:
    print(rel.to_display())
# Output: From Old English 'lufu' (inherited from)
```

## File Locations

```
data/
├── lexicons/
│   ├── kaikki.org-dictionary-*.jsonl     # Full dictionaries (GB)
│   ├── strongs_greek.json                # Strong's Greek (1.4 MB)
│   ├── strongs_hebrew.json               # Strong's Hebrew (2.0 MB)
│   └── indexes/
│       ├── kaikki-*-mini.jsonl           # Compact data (MB)
│       └── kaikki-*-index.json           # Word indexes (MB)
└── etymology_db/
    ├── etymology.csv.gz                  # 4.2M relationships (500 MB)
    └── word_index.json                   # Fast lookup index
```

## Supported Languages (50+)

### ✅ Already Downloaded (7)
English, Latin, Ancient Greek, Hebrew, Sanskrit, Proto-Indo-European, Aramaic

### 📥 Available to Download (43)

**Medieval/Bridge:**
Old English, Middle English, Old French, Gothic, Old Norse, Old High German, Old Irish, Old Church Slavonic

**Ancient Semitic:**
Akkadian, Syriac, Phoenician, Ugaritic, Ancient Hebrew, Coptic

**Ancient IE:**
Avestan, Old Persian, Pali, Prakrit, Tocharian, Hittite

**Modern:**
French, German, Spanish, Italian, Portuguese, Russian, Modern Greek, Arabic, Chinese, Japanese

**Other Ancient:**
Sumerian, Egyptian, Classical Syriac, Middle Persian, Elamite

## Common Workflows

### 1. English Word Etymology

```bash
# Download core + medieval
python scripts/download_kaikki_comprehensive.py --tier=core_ancient
python scripts/download_kaikki_comprehensive.py --tier=medieval_bridge

# Build indexes
python scripts/build_kaikki_indexes.py
```

Provides: English → Old English → Germanic → PIE chains

### 2. Biblical Text Analysis

```bash
# Download Semitic languages
python scripts/download_kaikki_comprehensive.py --tier=core_ancient
python scripts/download_kaikki_comprehensive.py --tier=ancient_semitic

# Download Strong's
python scripts/download_lexicons.py
```

Provides: Hebrew, Aramaic, Ancient Hebrew, Syriac, Coptic + Strong's concordance

### 3. Complete Coverage

```bash
# Download everything
python scripts/download_kaikki_comprehensive.py --auto

# Build all indexes
python scripts/build_kaikki_indexes.py

# Download etymology graph
python scripts/download_etymology_db.py
python scripts/build_etymology_index.py
```

Provides: Full 50+ language coverage (~10 GB)

## Performance Tips

1. **Indexes are essential** - Build them after downloading
2. **Category queries** - Faster than individual lookups
3. **Etymology graph** - Use for words missing in Kaikki
4. **Strong's fallback** - Automatic for Hebrew/Greek
5. **Cache results** - Service caches are already LRU

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Dictionary not found" | Language not available at Kaikki.org |
| Slow lookups | Build indexes with `build_kaikki_indexes.py` |
| Out of space | Download only needed tiers |
| No results | Check if language data was downloaded |
| Index build hangs | Normal for large dicts (English ~10 min) |

## Data Sources & Licenses

- **Kaikki.org**: CC BY-SA 4.0 + GFDL (monthly updates)
- **Strong's**: Public Domain (14k entries)
- **Etymology-DB**: CC BY-SA 4.0 (4.2M relationships)
- **Perseus LSJ**: CC BY-SA 3.0 (116k Greek entries)

## Next Steps

1. ✅ Download tiers you need
2. ✅ Build indexes
3. ✅ Test with `service.get_available_languages()`
4. ✅ Use in your etymology research!

For detailed documentation, see: [COMPREHENSIVE_ETYMOLOGY_SETUP.md](COMPREHENSIVE_ETYMOLOGY_SETUP.md)
