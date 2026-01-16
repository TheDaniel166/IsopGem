# Etymology System - Final Configuration

## ✅ Verified Languages Available at Kaikki.org

### Tier 1: Core Ancient (7 languages) - **Already Downloaded**
- English (1.7M senses) ✓
- Latin (1M senses) ✓
- Ancient Greek (77K senses) ✓
- Hebrew (22K senses) ✓
- Sanskrit (29K senses) ✓
- Proto-Indo-European (2.4K senses) ✓
- Aramaic (3K senses) ✓

### Tier 2: Medieval/Bridge (8 languages) - **Downloading Now**
- Old English (86K senses)
- Middle English (63K senses)
- Old French (11K senses)
- Gothic (25K senses)
- Old Norse (15K senses)
- Old High German (4K senses)
- Old Irish (8K senses)
- Old Church Slavonic (6K senses)

### Tier 3: Ancient Semitic (4 languages) - **Downloading Now**
- Akkadian (2K senses)
- Classical Syriac (8K senses)
- Ugaritic (1K senses)
- Coptic (4K senses)

### Tier 4: Ancient Indo-European (6 languages) - **Downloading Now**
- Old Persian (619 senses)
- Pali (13K senses)
- Prakrit (3K senses)
- Tocharian A (555 senses)
- Tocharian B (3K senses)
- Mycenaean Greek (605 senses)

### Tier 5: Modern Major (10 languages) - **Downloading Now**
- French (454K senses)
- German (621K senses)
- Spanish (859K senses)
- Italian (716K senses)
- Portuguese (502K senses)
- Russian (489K senses)
- Modern Greek (112K senses)
- Arabic (98K senses)
- Chinese (377K senses)
- Japanese (226K senses)

### Tier 6: Other Ancient & Reconstructed (5 languages) - **Downloading Now**
- Sumerian (3K senses)
- Egyptian (8K senses)
- Proto-Germanic (8K senses)
- Proto-Slavic (7K senses)
- Proto-Celtic (2K senses)

## Total: 40 Languages

**Estimated Total Size:** ~8-9 GB (within your 12 GB limit)

## What Was Built

### Scripts
1. **`scripts/download_kaikki_comprehensive.py`** - Downloads all verified dictionaries
2. **`scripts/build_kaikki_indexes.py`** - Builds fast lookup indexes (updated with all languages)

### Services
1. **`src/shared/services/lexicon/language_config.py`** - Centralized language configuration
2. **`src/shared/services/lexicon/comprehensive_lexicon_service.py`** - Dynamic multi-language lookup service
3. **`src/shared/services/document_manager/etymology_service.py`** - Main etymology service (already exists)

### Documentation
1. **`docs/COMPREHENSIVE_ETYMOLOGY_SETUP.md`** - Complete setup guide
2. **`docs/ETYMOLOGY_QUICK_REFERENCE.md`** - Command cheat sheet

## Next Steps

Once the download completes:

```bash
# Build indexes for fast lookup
/home/burkettdaniel927/projects/isopgem/.venv/bin/python scripts/build_kaikki_indexes.py

# Check what's available
/home/burkettdaniel927/projects/isopgem/.venv/bin/python -c "
from src.shared.services.lexicon.comprehensive_lexicon_service import ComprehensiveLexiconService
service = ComprehensiveLexiconService()
stats = service.get_stats()
print(f'Available: {stats[\"total_available\"]} languages')
print('Languages:', ', '.join(stats['available_languages']))
"
```

## Key Features

✅ **40 languages** spanning 3000+ years of linguistic history
✅ **Offline-first** - No internet needed after download
✅ **Fast lookups** - Compact indexes for instant results
✅ **Memory efficient** - Only loads what's needed
✅ **Automatic routing** - Script detection (Hebrew/Greek/Latin)
✅ **Etymology chains** - Trace words from modern → ancient → PIE
✅ **Comprehensive coverage** - 5+ million word senses total

## Language Coverage Highlights

### Complete Etymology Chains
- **English → Old English → Proto-Germanic → PIE**
- **French → Old French → Latin → PIE**
- **Spanish/Italian/Portuguese → Latin → PIE**
- **Russian → Proto-Slavic → PIE**
- **Greek → Ancient Greek → Mycenaean Greek → PIE**

### Ancient Near East
- Hebrew, Aramaic, Classical Syriac, Akkadian, Ugaritic, Coptic, Egyptian, Sumerian

### Comparative Indo-European
- PIE, Proto-Germanic, Proto-Slavic, Proto-Celtic
- Old Persian, Pali, Prakrit
- Tocharian A & B (extinct IE branch)
- Mycenaean Greek (Bronze Age)

### Modern World Languages
- Romance: French, Spanish, Italian, Portuguese
- Germanic: German
- Slavic: Russian
- Hellenic: Modern Greek
- Semitic: Arabic
- Asian: Chinese, Japanese

## Usage Examples

### Basic Lookup
```python
from src.shared.services.lexicon.comprehensive_lexicon_service import ComprehensiveLexiconService

service = ComprehensiveLexiconService()
results = service.lookup("lufu", "Old English")
# Returns: love, affection
```

### Multi-Language Search
```python
# Trace a word across languages
languages = ["English", "Old English", "Proto-Germanic", "Proto-Indo-European"]
results = service.lookup_multi_language("love", languages)

for lang, entries in results.items():
    for entry in entries:
        print(f"{lang}: {entry.word} - {entry.definition}")
```

### Category Search
```python
# Search all ancient Semitic languages
results = service.lookup_by_category("god", "ancient_semitic")
```

## Data Sources

- **Kaikki.org** (https://kaikki.org/dictionary/) - CC BY-SA 4.0 + GFDL
- **Strong's Dictionaries** - Public Domain
- **Etymology-DB** - CC BY-SA 4.0 (4.2M relationships)
- **Perseus LSJ** - CC BY-SA 3.0 (116K Greek entries)

All open source, all offline-capable!
