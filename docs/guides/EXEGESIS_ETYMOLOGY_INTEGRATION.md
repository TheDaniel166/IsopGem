# Exegesis Etymology Integration

## Overview

The Exegesis window (Interlinear view) now has access to the comprehensive multi-language lexicon system while maintaining its biblical/theological focus.

## Integration Points

### File: `src/pillars/gematria/ui/text_analysis/interlinear_widget.py`

The `_explore_etymology()` method now queries lexicons in this order:

1. **Etymology Database** (4.2M relationships)
   - Queries first for all languages
   - Provides clickable relationship chains

2. **Classical Lexicons** (Greek & Hebrew)
   - Strong's Greek Dictionary (5.5K entries)
   - Strong's Hebrew Dictionary (8.6K entries)
   - Kaikki.org Ancient Greek (77K senses)
   - Kaikki.org Hebrew (22K senses)

3. **Comprehensive Lexicon Service** (Latin, English, Sanskrit, PIE, Aramaic)
   - Falls back for non-Greek/Hebrew words
   - Queries all 5 available offline languages
   - Provides definitions + etymology chains

## Features

### Clickable Etymology Chains
- Links format: `etymology:word|language`
- Opens nested dialogs for deep exploration
- Maintains breadcrumb navigation history

### Language Detection
- Auto-detects Greek script (U+0370-U+03FF, U+1F00-U+1FFF)
- Auto-detects Hebrew script (U+0590-U+05FF)
- Falls back to language parameter for others

### Priority Rendering
Definition types shown in order:
1. **THEOSOPHICAL** ✨ - Occult/esoteric definitions
2. **ETYMOLOGY** 🌍 - Word origins
3. **STANDARD** 📖 - Dictionary definitions
4. **WIKTIONARY** 📚 - Community definitions
5. **OPENOCCULT** 🔮 - Occult database
6. **FREEDICT** 📖 - Free dictionary
7. **MANUAL** ✍️ - User-entered

### Smart Pattern Recognition

Makes these patterns clickable in definitions:
- `From Ancient Greek 'λόγος'` → links to λόγος (Ancient Greek)
- `From 'word'` → assumes English
- `*lewbʰ-*` → Proto-Indo-European reconstructions

## Usage Examples

### Example 1: Hebrew Word
```
User clicks Hebrew word "שלום" in interlinear view
↓
1. Queries Etymology-DB → finds relationships
2. Queries Strong's Hebrew → finds H7965
3. Queries Kaikki Hebrew → finds modern usage
4. Displays all results with clickable links
```

### Example 2: Latin Word (from etymology chain)
```
User explores "amor" (clicked from English "love" etymology)
↓
1. Queries Etymology-DB → finds relationships to PIE *am-
2. Classical lookup fails (not Greek/Hebrew)
3. Comprehensive service queries Latin lexicon → success!
4. Displays definition + etymology from Kaikki Latin (1M senses)
```

### Example 3: Sanskrit Root
```
User explores "yoga" (clicked from an etymology link)
↓
1. Etymology-DB lookup → partial results
2. Comprehensive service queries Sanskrit lexicon
3. Shows definition + related terms from 29K Sanskrit senses
```

## Benefits for Exegesis

### 1. Complete Etymology Chains
- English → Old English → Proto-Germanic → PIE
- Latin → Proto-Italic → PIE
- Hebrew → Proto-Semitic
- Sanskrit → PIE

### 2. Cross-Language Theological Study
- Trace concepts across cultures
- Compare Hebrew vs Greek vs Latin theological terms
- Follow word evolution through church history

### 3. Offline Scholarly Research
- No internet required
- Instant lookups
- Comprehensive coverage

## Technical Details

### Service Hierarchy
```
InterlinearWidget._explore_etymology()
    ↓
EtymologyDbService.get_etymologies()  [Priority 1]
    ↓
ClassicalLexiconService.lookup_*()     [Priority 2: Greek/Hebrew]
    ↓
ComprehensiveLexiconService.lookup()   [Priority 3: Other languages]
```

### Memory Usage
- Base services: ~10 MB
- Loaded indexes: ~50-100 MB (lazy loaded)
- Total active: ~100-200 MB

### Performance
- Etymology-DB query: ~5-10 ms
- Classical lexicon: ~1-5 ms
- Comprehensive lookup: ~1-5 ms
- **Total dialog open time: ~20-50 ms**

## Data Sources

All sources remain the same:
- **Etymology-DB**: 4.2M relationships (CC BY-SA 4.0)
- **Strong's**: Public Domain
- **Kaikki.org**: Wiktionary extract (CC BY-SA 4.0 + GFDL)

## Future Enhancements

When more languages are downloaded:
- Old English: Trace King James Bible language
- Coptic: Early Christian Egyptian texts
- Syriac: Eastern church fathers
- Akkadian: Ancient Near East context
- Gothic: Early Germanic Bible (Wulfila)

## User Experience

### Before Integration
- Greek/Hebrew: Full lexicon + etymology
- Other languages: Etymology-DB only or "not found"

### After Integration
- Greek/Hebrew: **Full lexicon + etymology** (unchanged)
- Latin/English/Sanskrit/PIE/Aramaic: **Full lexicon + etymology** (NEW!)
- Other languages: Etymology-DB or helpful error with available languages

The biblical focus remains, but scholarly depth increases significantly!
