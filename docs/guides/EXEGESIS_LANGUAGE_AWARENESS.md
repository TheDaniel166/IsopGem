# Exegesis Language Awareness

## Feature: Automatic Language Detection

The Exegesis/Interlinear view now automatically detects what language each word is and queries the appropriate lexicons.

## How It Works

### Detection Logic

When you click a word in the interlinear view:

```python
# Auto-detect from Unicode character ranges
if character in Hebrew range (U+0590–U+05FF):
    → "Hebrew" 🕎
elif character in Greek range (U+0370–U+03FF or U+1F00–U+1FFF):
    → "Ancient Greek" 🏛️
else:
    → "English" 🔤 (default)
```

### Query Flow with Language Awareness

```
Word Clicked: "λόγος"
    ↓
Auto-detect: Ancient Greek 🏛️
    ↓
Query Etymology-DB with language="Ancient Greek"
    ↓
Query Classical Greek Lexicons (Strong's + Kaikki)
    ↓
Display results with language badge
```

## Visual Changes

### Before (No Language Awareness)
```
┌─────────────────────────────────┐
│ λόγος                           │
│ TQ Value: 373                   │
└─────────────────────────────────┘
```
Assumed all words were English → wrong etymology chains

### After (With Language Awareness)
```
┌─────────────────────────────────┐
│ λόγος                           │
│ TQ Value: 373 | 🏛️ Language: Ancient Greek │
└─────────────────────────────────┘
```
Queries correct lexicons → accurate etymology chains

## Benefits

### 1. Accurate Etymology Chains
- **Hebrew words** → Query Hebrew etymology-DB + Strong's Hebrew
- **Greek words** → Query Greek etymology-DB + Strong's Greek + Classical lexicons
- **English words** → Query English etymology-DB + comprehensive lexicons

### 2. Correct Lexicon Routing
```
Before: Click Hebrew "שלום" → queries English etymology-DB → no results
After:  Click Hebrew "שלום" → queries Hebrew etymology-DB → full results!
```

### 3. Cross-Language Study
Now you can:
- Click Hebrew word → See Semitic roots
- Click Greek word → See Hellenic etymology
- Click English word → See Germanic/Romance/PIE chains
- Click Latin word (in etymology chain) → See Italic etymology

### 4. Visual Clarity
The language badge tells you immediately:
- 🕎 **Hebrew** - Semitic branch
- 🏛️ **Ancient Greek** - Hellenic branch
- 🔤 **English** - Default/Germanic

## Examples

### Example 1: Hebrew Word
```
User clicks: "אֱלֹהִים" (Elohim)
↓
Detected: Hebrew 🕎
↓
Etymology-DB queries: Hebrew relationships
Strong's queries: Hebrew lexicon (H430)
↓
Results: Semitic roots, Biblical usage, theological definitions
```

### Example 2: Greek Word
```
User clicks: "ἀγάπη" (agape)
↓
Detected: Ancient Greek 🏛️
↓
Etymology-DB queries: Greek relationships
Strong's queries: Greek lexicon (G26)
Kaikki queries: Classical Greek (77K senses)
↓
Results: Classical usage, NT theology, PIE connections
```

### Example 3: English Word
```
User clicks: "love"
↓
Detected: English 🔤
↓
Etymology-DB queries: English relationships
→ Finds: Old English "lufu"
→ Finds: Proto-Germanic "*lubō"
→ Finds: PIE "*lewbʰ-"
↓
Results: Complete Germanic → PIE etymology chain
```

## Technical Implementation

### Auto-Detection Code
```python
# In _on_word_clicked()
detected_lang = "English"  # Default
lang_icon = "🔤"

for char in word:
    if '\u0590' <= char <= '\u05ff':  # Hebrew
        detected_lang = "Hebrew"
        lang_icon = "🕎"
        break
    elif ('\u0370' <= char <= '\u03ff') or ('\u1f00' <= char <= '\u1fff'):  # Greek
        detected_lang = "Ancient Greek"
        lang_icon = "🏛️"
        break
```

### Etymology Query
```python
# Query with detected language (not hardcoded "English")
etym_relations = etym_service.get_etymologies(
    word.lower(),
    detected_lang,  # ← Language-aware!
    max_results=15
)
```

### Nested Exploration
```python
# When clicking etymology links, language is preserved
def handle_link(url):
    if url.startswith('etymology:'):
        parts = url[10:].split('|')
        word = parts[0]
        language = parts[1] if len(parts) > 1 else detected_lang
        # ← Language flows through the chain
        self._explore_etymology(word, language, chain)
```

## User Experience Improvements

### Clear Visual Feedback
- **Language badge** in header tells you what the system detected
- **Consistent throughout** - language flows through nested exploration
- **Icon coding** - 🕎 Hebrew, 🏛️ Greek, 🔤 English

### Accurate Results
- No more "no etymology found" for Hebrew/Greek words
- Correct lexicon queries based on actual language
- Proper etymology chains per language family

### Seamless Navigation
- Click Greek word → Greek chain
- Click English word in Greek etymology → English chain
- Language context preserved throughout exploration

## Future Enhancements

When more dictionaries are downloaded, add detection for:
- **Latin**: Check for Latin-only characters
- **Aramaic**: Aramaic script detection (U+0700–U+074F)
- **Syriac**: Syriac script (overlap with Aramaic)
- **Arabic**: Arabic script (U+0600–U+06FF)
- **Sanskrit**: Devanagari script (U+0900–U+097F)

## Testing

To test language awareness:

1. **Hebrew word**: Click any Hebrew word in interlinear view
   - Should show 🕎 Hebrew badge
   - Should query Hebrew etymology-DB
   - Should show Strong's Hebrew results

2. **Greek word**: Click any Greek word
   - Should show 🏛️ Ancient Greek badge
   - Should query Greek etymology-DB
   - Should show Strong's Greek + Classical results

3. **English word**: Click any English word
   - Should show 🔤 English badge
   - Should query English etymology-DB
   - Should show complete Germanic → PIE chain

## Impact on Apokalypsis

The focused, language-aware exploration enables deeper **Apokalypsis** (unveiling):

- **Hebrew roots** unveil Semitic theological concepts
- **Greek philosophy** unveils Hellenic thought patterns
- **English evolution** unveils cultural transmission
- **Cross-language links** unveil universal concepts

Each language becomes a lens through which divine patterns are revealed! 🌟
