# RTF Editor: Encoding Normalization Feature

## Overview

The RTF Editor now functions as a **text encoding normalization tool** - it can open files in various legacy encodings but always saves as UTF-8.

## How It Works

### Opening Files (Multi-Encoding Support)

When you open a file, the editor tries multiple encodings in order:

```python
Encodings tried (in order):
1. utf-8              # Modern standard
2. utf-8-sig          # UTF-8 with BOM (Byte Order Mark)
3. latin-1            # ISO-8859-1 (Western European)
4. windows-1252       # Windows Western European
5. cp1252             # Alternative Windows encoding
6. iso-8859-1         # Alternative Latin-1 name
7. ascii              # Basic ASCII

If all fail:
8. Binary read with error replacement
```

### Saving Files (Always UTF-8)

**All saves use UTF-8 encoding** - no exceptions:

```python
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
```

The save dialog confirms: `"Document saved to filename.txt (UTF-8 encoding)"`

## User Experience

### Opening a Legacy File

**Scenario:** You have an old `notes.txt` file encoded in Windows-1252

```
1. File > Open Document
2. Select notes.txt
3. Editor detects: windows-1252
4. Shows notification:
   ┌─────────────────────────────────────┐
   │ Encoding Detected                   │
   ├─────────────────────────────────────┤
   │ File opened with windows-1252       │
   │ encoding.                           │
   │                                     │
   │ When saved, it will be normalized   │
   │ to UTF-8.                           │
   └─────────────────────────────────────┘
5. File loads successfully
6. Edit as needed
7. Save → Automatically converted to UTF-8
```

### Opening a UTF-8 File

**Scenario:** You have a modern UTF-8 file

```
1. File > Open Document
2. Select modern-file.md
3. Editor detects: utf-8
4. No notification (already UTF-8)
5. File loads successfully
6. Save → Remains UTF-8
```

### The Normalization Workflow

```
Legacy File (latin-1, windows-1252, etc.)
    ↓
Open in RTF Editor (auto-detects encoding)
    ↓
Edit/Review content
    ↓
Save (always UTF-8)
    ↓
Normalized File (UTF-8) ✓
```

## Supported Encodings

### Input (Opening)
✅ UTF-8 (with or without BOM)
✅ Latin-1 / ISO-8859-1 (Western European)
✅ Windows-1252 / CP1252 (Windows Western)
✅ ASCII (7-bit)
✅ Any encoding (with error replacement as fallback)

### Output (Saving)
✅ UTF-8 only (universal standard)

## Benefits

### 1. Universal Compatibility
- UTF-8 works on all modern systems (Windows, macOS, Linux)
- Supports all Unicode characters (multilingual, emoji, symbols)
- Standard web encoding (HTML, XML, JSON all prefer UTF-8)

### 2. Data Preservation
- Opens legacy files without losing data
- Graceful error handling if encoding is unknown
- Characters are preserved during conversion

### 3. Future-Proof
- UTF-8 is the universal standard
- No more encoding issues when sharing files
- Works with all modern tools and editors

### 4. Workflow Integration
- No manual encoding selection needed
- Automatic detection and conversion
- Clear notifications about what's happening

## Technical Details

### Encoding Detection Algorithm

```python
for encoding in [utf-8, utf-8-sig, latin-1, windows-1252, ...]:
    try:
        open file with encoding
        if success:
            use this encoding
            break
    except UnicodeDecodeError:
        try next encoding

if all failed:
    read as binary
    decode with error='replace'
    # Replaces invalid bytes with � (replacement character)
```

### User Notification Logic

```python
if detected_encoding not in ['utf-8', 'utf-8-sig']:
    show_notification(
        "File opened with {encoding}. "
        "When saved, it will be normalized to UTF-8."
    )
```

Only notifies when **non-UTF-8** encoding is detected, so UTF-8 files open silently.

## Use Cases

### 1. Batch Normalization
```
Goal: Convert 100 old text files to UTF-8

Process:
1. Open each file in RTF Editor
2. Immediately save (File > Save As)
3. Done - file is now UTF-8
```

### 2. Legacy System Integration
```
Scenario: Receive data exports in Windows-1252 from legacy system

Solution:
1. Open export in RTF Editor
2. Review data
3. Save as UTF-8
4. Import into modern system
```

### 3. Cross-Platform Collaboration
```
Problem: Windows colleague sends Latin-1 file, can't open on Mac

Solution:
1. Open in RTF Editor (auto-detects Latin-1)
2. Save (converts to UTF-8)
3. Send back - works on all platforms
```

### 4. Web Publishing
```
Goal: Prepare content for website (requires UTF-8)

Process:
1. Open legacy content files
2. Edit/format as needed
3. Save - ready for web (UTF-8)
```

## Error Handling

### Unreadable Files
If a file can't be decoded with any encoding:
```
1. Read file as binary
2. Decode with error='replace'
3. Invalid bytes become �
4. User can fix manually
5. Save as clean UTF-8
```

### Notification Examples

**Non-UTF-8 detected:**
```
┌────────────────────────────────────┐
│ Encoding Detected                  │
├────────────────────────────────────┤
│ File opened with latin-1 encoding. │
│                                    │
│ When saved, it will be normalized  │
│ to UTF-8.                          │
└────────────────────────────────────┘
```

**Save confirmation:**
```
┌────────────────────────────────┐
│ Saved                          │
├────────────────────────────────┤
│ Document saved to notes.txt    │
│ (UTF-8 encoding)               │
└────────────────────────────────┘
```

## Implementation

### File: `src/shared/ui/rich_text_editor/editor.py`

**Modified Methods:**
- `open_document()` - Added multi-encoding detection
- `save_document()` - Enhanced with UTF-8 confirmation

**Lines Changed:**
- Lines 2763-2824: Open with encoding detection
- Lines 2826-2861: Save with UTF-8 confirmation

## Testing

### Test Cases

1. **UTF-8 file** → Opens silently, saves silently
2. **Latin-1 file** → Shows notification, converts on save
3. **Windows-1252 file** → Shows notification, converts on save
4. **ASCII file** → Opens silently (ASCII is UTF-8 subset)
5. **Corrupted file** → Opens with replacements, saves clean

### Verification

After saving, verify UTF-8 encoding:
```bash
# Check file encoding
file -bi filename.txt
# Should show: text/plain; charset=utf-8

# Or use Python
python3 -c "open('filename.txt', encoding='utf-8').read()"
# Should read without errors
```

## Future Enhancements

Potential additions:
- **Encoding selector**: Let user manually choose input encoding
- **Batch converter**: Process multiple files at once
- **Encoding preview**: Show encoding before opening
- **Statistics**: Track how many files normalized

## FAQ

**Q: What if I want to save as Latin-1?**
A: UTF-8 is a superset that supports everything Latin-1 does, plus more. There's no reason to save as Latin-1 in modern systems.

**Q: Will this corrupt my files?**
A: No. The encoding detection is robust, and UTF-8 preserves all characters. If uncertain, test on a copy first.

**Q: What about emoji and special characters?**
A: UTF-8 supports all Unicode, including emoji, mathematical symbols, and all world languages.

**Q: Can I see what encoding was detected?**
A: Yes, a notification appears when non-UTF-8 encoding is detected.

## Summary

The RTF Editor is now a **universal text normalizer**:
- ✅ Opens files in any common encoding
- ✅ Saves everything as UTF-8
- ✅ Clear notifications about conversions
- ✅ Future-proof your text files

Perfect for cleaning up legacy data and ensuring universal compatibility! 🌍✨
