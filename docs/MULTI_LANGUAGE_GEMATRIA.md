# Multi-Language Gematria System

## Overview

The gematria system now supports **automatic language detection** and **per-language cipher configuration**. This solves the problem of mixed-language documents where forcing a single cipher (like TQ) produces incorrect values for Hebrew, Greek, and other languages.

## The Problem (Before)

Previously, the system was hardcoded to use TQ (English cipher) for all text:

```
Document: "The word λόγος (logos) means דָּבָר (davar)"
Issue: All words calculated using English TQ cipher
Result:
  - "λόγος" → English TQ value (incorrect!)
  - "דָּבָר" → English TQ value (incorrect!)
  - Only English words get correct values
```

## The Solution (After)

Now the system:
1. **Detects language** per word using Unicode character ranges
2. **Looks up user preference** for which cipher to use for that language
3. **Calculates using appropriate cipher**

```
Document: "The word λόγος (logos) means דָּבָר (davar)"
Process: Auto-detect + per-language ciphers
Result:
  - "The" → English TQ (user preference)
  - "word" → English TQ
  - "λόγος" → Greek Standard (user preference)
  - "logos" → English TQ
  - "means" → English TQ
  - "דָּבָר" → Hebrew Standard (user preference)
  - "davar" → English TQ
```

## Architecture

### 1. Language Detection Service

**File:** `src/shared/services/gematria/language_detector.py`

Detects language based on Unicode character ranges:

```python
from shared.services.gematria.language_detector import Language, LanguageDetector

# Detect word language
word = "λόγος"
lang = LanguageDetector.detect_word_language(word)
# → Language.GREEK

# Detect text language (for passages)
text = "The Hebrew word שָׁלוֹם means peace"
lang = LanguageDetector.detect_text_language(text)
# → Language.ENGLISH (majority language)

# Check if mixed language
is_mixed = LanguageDetector.is_mixed_language(text)
# → True (contains Hebrew and English)

# Get language statistics
stats = LanguageDetector.get_language_stats(text)
# → {Language.ENGLISH: 25, Language.HEBREW: 4}
```

**Supported Languages:**
- **Hebrew** (U+0590–U+05FF, U+FB1D–U+FB4F)
- **Greek** (U+0370–U+03FF, U+1F00–U+1FFF)
- **English** (A-Z, a-z)
- **Latin** (U+0100–U+024F)
- **Arabic** (U+0600–U+06FF, U+0750–U+077F, U+08A0–U+08FF)

### 2. Cipher Preference Manager

**File:** `src/shared/services/gematria/cipher_preferences.py`

Stores user preferences for which cipher to use per language:

```python
from shared.services.gematria.cipher_preferences import get_cipher_preferences, Language

prefs = get_cipher_preferences()

# Get preferred cipher for a language
cipher_name = prefs.get_cipher(Language.GREEK)
# → "Greek (Standard)"

# Set preferred cipher
prefs.set_cipher(Language.HEBREW, "Hebrew (Sofit)")

# Get all preferences
all_prefs = prefs.get_all_preferences()
# → {"Hebrew": "Hebrew (Sofit)", "Greek": "Greek (Standard)", ...}

# Reset to defaults
prefs.reset_to_defaults()
```

**Default Ciphers:**
- **Hebrew** → "Hebrew (Standard)"
- **Greek** → "Greek (Standard)"
- **English** → "English TQ"
- **Latin** → "English TQ"
- **Arabic** → "English TQ" (fallback until Arabic cipher added)
- **Unknown** → "English TQ"

**Storage:**
Preferences are saved to `~/.config/isopgem/cipher_preferences.json`

### 3. Multi-Language Calculator

**File:** `src/shared/services/gematria/multi_language_calculator.py`

Orchestrates language detection + cipher selection + calculation:

```python
from shared.services.gematria.multi_language_calculator import MultiLanguageCalculator

# Create calculator with all available ciphers
multi_calc = MultiLanguageCalculator(calculators_list)

# Calculate single-language text
value = multi_calc.calculate("λόγος")
# → Uses Greek Standard cipher (based on preferences)

# Calculate mixed-language text (word-by-word detection)
value = multi_calc.calculate("The word λόγος means דָּבָר")
# → Calculates each word with appropriate cipher and sums

# Get breakdown with language info
breakdown = multi_calc.get_word_breakdown("The word λόγος")
# → [("The", 33, "English", "English TQ"),
#     ("word", 60, "English", "English TQ"),
#     ("λόγος", 373, "Greek", "Greek (Standard)")]

# Get language statistics
stats = multi_calc.get_language_stats("The word λόγος means דָּבָר")
# → {"English": {char_count: 14, cipher: "English TQ", percentage: 70%},
#     "Greek": {char_count: 5, cipher: "Greek (Standard)", percentage: 25%},
#     "Hebrew": {char_count: 4, cipher: "Hebrew (Standard)", percentage: 5%}}

# Update preference on-the-fly
multi_calc.set_preference(Language.GREEK, "Greek (Ordinal)")
```

## UI Integration

### Interlinear View (Exegesis)

The interlinear view now uses the multi-language calculator automatically:

**Before:**
```
Word: λόγος
TQ Value: [English TQ calculation - wrong!]
```

**After:**
```
Word: λόγος
Value: 373 (Greek Standard - auto-detected)
Language: Greek 🏛️
Cipher: Greek (Standard)
```

Each word label now shows:
- The word itself
- Gematria value (using language-appropriate cipher)
- Optionally: detected language and cipher used

**Implementation:**
- `InterlinearVerseWidget` now accepts `multi_lang_calculator` parameter
- `_get_word_data()` detects language per word
- Uses appropriate calculator from preferences
- Stores language and cipher info in word data

### Word Details Dialog

When clicking a word in interlinear view:

```
┌────────────────────────────────────┐
│ λόγος                              │
│ Value: 373 | 🏛️ Language: Greek   │
│ Cipher: Greek (Standard)           │
└────────────────────────────────────┘

Etymology Chain
  From Ancient Greek: λόγος

Definitions
  [Greek lexicon definitions...]
```

The dialog now shows which cipher was used for the calculation.

## Configuration & Preferences

### Default Behavior

Out of the box, the system uses sensible defaults:
- Hebrew words → Hebrew (Standard) cipher
- Greek words → Greek (Standard) cipher
- English/Latin words → English TQ cipher

### Changing Cipher Preferences

**Programmatically:**
```python
from shared.services.gematria.cipher_preferences import set_language_cipher
from shared.services.gematria.language_detector import Language

# Use Hebrew Sofit instead of Standard
set_language_cipher(Language.HEBREW, "Hebrew (Sofit)")

# Use Greek Ordinal instead of Standard
set_language_cipher(Language.GREEK, "Greek (Ordinal)")
```

**Via UI (Future):**
A cipher preference dialog will allow users to:
1. See current cipher for each language
2. Select from available ciphers
3. Save preferences
4. Reset to defaults

### Available Ciphers Per Language

**Hebrew:**
- Hebrew (Standard) - Traditional gematria
- Hebrew (Sofit) - Final letter values (500-900)
- Hebrew (Ordinal) - Sequential 1-22
- Hebrew (Small Value) - Reduced to single digits
- Hebrew (AtBash) - Reverse substitution
- Hebrew (Albam) - Pair matching
- Hebrew (Kolel) - Standard + 1
- Hebrew (Square) - Letter values squared
- Hebrew (Cube) - Letter values cubed
- Hebrew (Triangular) - Triangular numbers
- Hebrew (Full Value) - Including letter names

**Greek:**
- Greek (Standard) - Isopsephy values
- Greek (Ordinal) - Sequential 1-24
- Greek (Small Value) - Reduced digits
- Greek (Kolel) - Standard + 1
- Greek (Square) - Squared values
- Greek (Cube) - Cubed values
- Greek (Triangular) - Triangular numbers
- Greek (Full Value) - Including letter names

**English:**
- English TQ - Trigrammaton Qabalah
- English (Ordinal) - A=1, B=2, ...
- English (Reverse Ordinal) - Z=1, Y=2, ...
- English (Reduced) - Reduced to single digits
- TQ (Reduced) - TQ reduced
- TQ (Square) - TQ squared
- TQ (Triangular) - TQ triangular

## Mixed-Language Documents

The system handles mixed-language documents correctly:

### Example: Theological Text

```markdown
Document: "The Greek word ἀγάπη (agape) and Hebrew אַהֲבָה (ahava) both mean love"

Per-Word Calculation:
  "The" → English TQ → 33
  "Greek" → English TQ → 45
  "word" → English TQ → 60
  "ἀγάπη" → Greek Standard → 93
  "agape" → English TQ → 27
  "and" → English TQ → 19
  "Hebrew" → English TQ → 64
  "אַהֲבָה" → Hebrew Standard → 13
  "ahava" → English TQ → 14
  "both" → English TQ → 44
  "mean" → English TQ → 33
  "love" → English TQ → 54

Total Document Value: 499 (sum of all words with appropriate ciphers)
```

### Language Statistics

For the above document:
```
English: 82% of characters (12 words) - English TQ
Greek: 10% of characters (1 word) - Greek Standard
Hebrew: 8% of characters (1 word) - Hebrew Standard
```

## Benefits

### 1. Accuracy
- Hebrew words get Hebrew values
- Greek words get Greek values
- No more incorrect English calculations for foreign scripts

### 2. Flexibility
- Users can choose their preferred cipher per language
- Different schools of thought can use different systems
- Easy to switch between methods (Standard vs. Ordinal vs. Sofit)

### 3. Automatic
- No manual language tagging required
- Unicode-based detection is fast and reliable
- Works seamlessly with existing workflows

### 4. Mixed-Language Support
- Correctly handles multilingual theological texts
- Each word calculated with appropriate cipher
- Language statistics show document composition

## Technical Details

### Unicode Detection

The system uses Unicode character ranges to identify scripts:

```python
# Hebrew character detection
if '\u0590' <= char <= '\u05ff':  # Hebrew block
    language = Language.HEBREW

# Greek character detection
if ('\u0370' <= char <= '\u03ff') or ('\u1f00' <= char <= '\u1fff'):
    language = Language.GREEK

# English (ASCII letters)
if 'A' <= char <= 'Z' or 'a' <= char <= 'z':
    language = Language.ENGLISH
```

### Tokenization

Word extraction is Unicode-aware:

```python
# Before (ASCII-only)
words = re.findall(r"[a-zA-Z]+", text)

# After (Unicode-aware)
words = re.findall(r"\w+", text, re.UNICODE)
```

This correctly extracts Hebrew (עִבְרִית), Greek (Ελληνικά), and other scripts.

### Mixed-Language Calculation

For mixed-language text, the calculator:
1. Tokenizes into words (Unicode-aware)
2. Detects language per word
3. Looks up preferred cipher for that language
4. Calculates with appropriate calculator
5. Sums all values

```python
def calculate_mixed_language(self, text: str) -> int:
    words = re.findall(r'\w+', text, re.UNICODE)
    total = 0
    for word in words:
        calc = self.get_calculator_for_word(word)
        if calc:
            total += calc.calculate(word)
    return total
```

## Future Enhancements

### 1. Cipher Preference UI

Add a settings dialog:
```
┌─────────────────────────────────────┐
│ Cipher Preferences                  │
├─────────────────────────────────────┤
│ Hebrew:  [Hebrew (Standard)    ▼]   │
│ Greek:   [Greek (Standard)     ▼]   │
│ English: [English TQ           ▼]   │
│ Latin:   [English TQ           ▼]   │
│                                     │
│          [Reset to Defaults]        │
│          [Save]  [Cancel]           │
└─────────────────────────────────────┘
```

### 2. Per-Document Cipher Override

Allow setting cipher per document (overrides global preference):
```python
# Use Greek Ordinal just for this document
document.set_cipher_override(Language.GREEK, "Greek (Ordinal)")
```

### 3. Language Hints

Allow users to manually tag text sections:
```markdown
<lang=Hebrew>אֱלֹהִים</lang>
<lang=Greek>θεός</lang>
```

### 4. Additional Languages

Expand detection to:
- **Aramaic** (U+0700–U+074F)
- **Syriac** (overlaps with Aramaic)
- **Arabic** (already detected, needs cipher)
- **Sanskrit** (Devanagari U+0900–U+097F)
- **Coptic** (U+2C80–U+2CFF)

### 5. Verse Totals by Language

Show language breakdown for verse totals:
```
Verse 1: Total = 1234
  - Hebrew: 500 (40%)
  - Greek: 450 (36%)
  - English: 284 (24%)
```

## Migration from TQ-Only System

Existing documents automatically benefit from the new system:

**Before:**
All calculations used TQ (hardcoded in InterlinearVerseWidget)

**After:**
- Interlinear view uses MultiLanguageCalculator
- English words continue using TQ (default preference)
- Hebrew/Greek words now use appropriate ciphers
- No data migration needed - preferences start with sensible defaults

## API Reference

### LanguageDetector

```python
# Detect language of a word
lang = LanguageDetector.detect_word_language("λόγος")

# Detect language of text passage
lang = LanguageDetector.detect_text_language("The word λόγος")

# Check if mixed language
is_mixed = LanguageDetector.is_mixed_language(text, threshold=0.1)

# Get character counts per language
stats = LanguageDetector.get_language_stats(text)

# Convenience functions
is_hebrew("שָׁלוֹם")  # → True
is_greek("λόγος")    # → True
is_english("word")   # → True
```

### CipherPreferences

```python
# Get global preferences instance
prefs = get_cipher_preferences()

# Get cipher for language
cipher_name = prefs.get_cipher(Language.GREEK)

# Set cipher for language
prefs.set_cipher(Language.HEBREW, "Hebrew (Sofit)")

# Get all preferences
all_prefs = prefs.get_all_preferences()

# Reset to defaults
prefs.reset_to_defaults()

# Get available ciphers for a language
available = prefs.get_available_ciphers_for_language(Language.GREEK)

# Convenience functions
set_language_cipher(Language.GREEK, "Greek (Ordinal)")
get_language_cipher(Language.GREEK)
```

### MultiLanguageCalculator

```python
# Create calculator
multi_calc = MultiLanguageCalculator(calculators_list)

# Calculate (auto-detect language)
value = multi_calc.calculate("λόγος")

# Calculate mixed-language text
value = multi_calc.calculate_mixed_language(text)

# Get calculator for specific language
calc = multi_calc.get_calculator_for_language(Language.HEBREW)

# Get calculator for text (auto-detect)
calc = multi_calc.get_calculator_for_text("שָׁלוֹם")

# Get calculator for word
calc = multi_calc.get_calculator_for_word("λόγος")

# Get breakdown with language info
breakdown = multi_calc.get_breakdown(text)  # → [(char, value, language), ...]

# Get word-level breakdown
word_breakdown = multi_calc.get_word_breakdown(text)
# → [(word, value, language, cipher_name), ...]

# Get language statistics
stats = multi_calc.get_language_stats(text)

# Update preference
multi_calc.set_preference(Language.GREEK, "Greek (Ordinal)")
```

## Summary

The multi-language gematria system provides:

✅ **Automatic language detection** via Unicode ranges
✅ **Per-language cipher preferences** (user-configurable)
✅ **Mixed-language document support** (per-word calculation)
✅ **Accurate calculations** for Hebrew, Greek, English, and more
✅ **Backward compatible** (defaults to sensible ciphers)
✅ **Persistent preferences** (saved to user config)
✅ **Full API** for programmatic use
✅ **UI integration** in Exegesis interlinear view

Now you can work with multilingual theological texts and get correct gematria values for each language! 🕎🏛️🔤
