# Multi-Language Gematria - Quick Start

## What Was Fixed

The multi-language gematria system is now fully implemented and working! The main issue was a **mismatch between calculator names and default preferences**.

### The Problem
- Greek calculator is named: `"Greek (Isopsephy)"`
- Default preference was: `"Greek (Standard)"` ❌
- Result: No calculator found for Greek words

### The Fix
Updated cipher preferences to match actual calculator names:
- Greek: `"Greek (Isopsephy)"` ✅
- Hebrew: `"Hebrew (Standard)"` ✅
- English: `"English (TQ)"` ✅

## Testing the System

Run the test script to verify everything works:

```bash
python3 scripts/test_multi_language_gematria.py
```

Expected output:
```
✓ Αγγελικος → Greek (Greek word from screenshot)
   Value:  342 using Greek (Isopsephy)

✓ λόγος → Greek (Greek word - logos)
   Value:  373 using Greek (Isopsephy)

✓ שָׁלוֹם → Hebrew (Hebrew word - shalom)
   Value:  376 using Hebrew (Standard)
```

## Using in the UI

### 1. Restart the Application

**IMPORTANT:** You must restart the Exegesis window to pick up the new code:

```bash
# Close the existing Exegesis window
# Re-launch from your main menu or:
python3 -m src.main  # Or however you normally launch it
```

### 2. Open a Document with Greek Text

1. Launch Exegesis window
2. Select a document (like "603 Liber Spectaculi")
3. Enable "Holy Scansion" checkbox
4. Enable "Interlinear" checkbox

### 3. Verify Language Detection

You should now see:
- **Greek words** (Αγγελικος, Αραχνη, etc.) calculated with Greek (Isopsephy)
- **English words** calculated with English (TQ)
- **Debug logs** showing language detection (if logging enabled)

Example logs:
```
Multi-lang calc: 'Αγγελικος' → 342 (Greek, Greek (Isopsephy))
Multi-lang calc: 'The' → 25 (English, English (TQ))
```

## How It Works

### Automatic Language Detection

```
Word: Αγγελικος
  ↓
Detect Unicode range (U+0370–U+03FF = Greek)
  ↓
Language: Greek
  ↓
Look up preference: "Greek (Isopsephy)"
  ↓
Calculate: Α(1) + γ(3) + γ(3) + ε(5) + λ(30) + ι(10) + κ(20) + ο(70) + ς(200)
  ↓
Value: 342 ✓
```

### Mixed-Language Documents

The system handles documents with multiple languages:

```
Text: "The word λόγος means דָּבָר"

Per-Word Calculation:
  The   → English (TQ)     = 25
  word  → English (TQ)     = 55
  λόγος → Greek (Isopsephy) = 373
  means → English (TQ)     = 78
  דָּבָר → Hebrew (Standard) = 206

Total: 737
```

## Troubleshooting

### Greek Words Showing 0 Value

**Symptom:** Greek words in interlinear view show value = 0

**Causes:**
1. Application not restarted
2. Multi-lang calculator not initialized
3. Old preference file with wrong cipher names

**Solution:**
```bash
# 1. Delete old preferences (if exists)
rm ~/.config/isopgem/cipher_preferences.json

# 2. Restart application
# Close and relaunch

# 3. Check logs for errors
# Look for: "No calculator found for word" warnings
```

### Words Not Detected as Greek

**Symptom:** Greek letters detected as English

**Cause:** Text might be transliterated (e.g., "logos" instead of "λόγος")

**Solution:**
- This is correct! Transliterated text IS English
- Only actual Greek letters (Unicode U+0370–U+03FF) are detected as Greek

### Calculator Name Mismatch

**Symptom:** Preferences show "Greek (Standard)" but no calculator found

**Solution:**
The system now has **automatic fallback** - it will find any Greek calculator even if the exact name doesn't match. But for best results, use the correct names:

```python
from shared.services.gematria.cipher_preferences import set_language_cipher, Language

# Set to exact calculator name
set_language_cipher(Language.GREEK, "Greek (Isopsephy)")
```

## Customizing Cipher Preferences

### Via Code

```python
from shared.services.gematria.cipher_preferences import get_cipher_preferences
from shared.services.gematria.language_detector import Language

prefs = get_cipher_preferences()

# Use different Greek cipher
prefs.set_cipher(Language.GREEK, "Greek (Ordinal)")

# Use Hebrew Sofit instead of Standard
prefs.set_cipher(Language.HEBREW, "Hebrew (Sofit)")

# Preferences automatically saved to ~/.config/isopgem/cipher_preferences.json
```

### Available Ciphers

**Greek:**
- Greek (Isopsephy) ← Default
- Greek (Ordinal)
- Greek (Small Value)
- Greek (Kolel)
- Greek (Square)
- Greek (Cube)
- Greek (Triangular)

**Hebrew:**
- Hebrew (Standard) ← Default
- Hebrew (Sofit)
- Hebrew (Ordinal)
- Hebrew (Small Value)
- Hebrew (AtBash)
- Hebrew (Albam)
- Hebrew (Kolel)
- Hebrew (Square)
- Hebrew (Cube)
- Hebrew (Triangular)

**English:**
- English (TQ) ← Default
- English (Ordinal)
- English (Reverse Ordinal)
- English (Reduced)
- TQ (Reduced)
- TQ (Square)
- TQ (Triangular)

## Summary

✅ **Language detection working** - Automatically detects Hebrew, Greek, English
✅ **Cipher preferences fixed** - Matches actual calculator names
✅ **Fallback mechanism** - Finds calculators even with name mismatches
✅ **Mixed-language support** - Handles multilingual documents correctly
✅ **Logging added** - Debug output shows language detection in action

**Next Steps:**
1. Restart your Exegesis window
2. Open a document with Greek text
3. Enable Holy Scansion + Interlinear
4. See Greek words calculated correctly! 🏛️

For more details, see [MULTI_LANGUAGE_GEMATRIA.md](MULTI_LANGUAGE_GEMATRIA.md)
