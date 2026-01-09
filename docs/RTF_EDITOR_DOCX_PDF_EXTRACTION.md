# RTF Editor: DOCX/PDF Plain Text Extraction

## Overview

The RTF Editor can now **extract clean plain text** from DOCX and PDF files, removing all formatting and HTML markup. Perfect for text normalization workflows!

## How It Works

### Opening DOCX/PDF Files

```
File > Open Document
    ↓
Select file type filter:
- "All Supported" (includes .docx, .pdf)
- "Word Document (*.docx)"
- "PDF Document (*.pdf)"
    ↓
Select DOCX or PDF file
    ↓
Plain text automatically extracted
    ↓
Loaded into editor (no formatting/HTML)
    ↓
Save as clean UTF-8 text
```

### What Gets Extracted

**DOCX Files:**
- ✅ All paragraph text
- ✅ Proper spacing between paragraphs
- ❌ Bold, italic, underline (removed)
- ❌ Colors, fonts, sizes (removed)
- ❌ Images, tables, shapes (removed)
- ❌ Headers, footers (removed)

**PDF Files:**
- ✅ All readable text from all pages
- ✅ Page breaks preserved as double newlines
- ❌ Images, graphics (removed)
- ❌ Formatting, fonts, colors (removed)
- ❌ Embedded objects (removed)

**Result:** Pure, clean, UTF-8 text!

## User Experience

### Opening a DOCX File

```
1. File > Open Document
2. Filter: "Word Document (*.docx)"
3. Select: report.docx
4. Notification appears:
   ┌─────────────────────────────────────┐
   │ DOCX Imported                       │
   ├─────────────────────────────────────┤
   │ Plain text extracted from           │
   │ report.docx                         │
   │                                     │
   │ (Formatting removed - save as       │
   │  UTF-8 text)                        │
   └─────────────────────────────────────┘
5. Clean text appears in editor
6. File > Save Document > report.txt
7. Saved as UTF-8 plain text
```

### Opening a PDF File

```
1. File > Open Document
2. Filter: "PDF Document (*.pdf)"
3. Select: article.pdf
4. Notification appears:
   ┌─────────────────────────────────────┐
   │ PDF Imported                        │
   ├─────────────────────────────────────┤
   │ Plain text extracted from           │
   │ article.pdf                         │
   │                                     │
   │ (Formatting removed - save as       │
   │  UTF-8 text)                        │
   └─────────────────────────────────────┘
5. Clean text from all pages appears
6. File > Save Document > article.txt
7. Saved as UTF-8 plain text
```

## Complete Workflow

### DOCX/PDF → Clean UTF-8 Text

```
Input: formatted_document.docx (with styling, images, tables)
    ↓
Open in RTF Editor
    ↓
Extracts: plain text paragraphs only
    ↓
Save As: clean_text.txt
    ↓
Output: UTF-8 plain text (no formatting, universally compatible)
```

### Combined with Encoding Normalization

```
Input: legacy.docx (created in old Word with legacy encoding references)
    ↓
Open in RTF Editor (extracts text, removes all legacy formatting)
    ↓
Save: normalized.txt
    ↓
Output: Modern UTF-8 plain text, completely normalized
```

## Use Cases

### 1. Document Text Extraction
```
Goal: Extract just the text from a Word document

Process:
1. Open document.docx
2. Text extracted automatically
3. Save as .txt
4. Use plain text in other applications
```

### 2. PDF Text Mining
```
Goal: Get searchable text from PDF

Process:
1. Open research_paper.pdf
2. All pages extracted to plain text
3. Save as .txt
4. Process with text analysis tools
```

### 3. Format Cleanup
```
Problem: Need text without messy formatting

Solution:
1. Open formatted_mess.docx
2. All formatting stripped
3. Save as clean .txt
4. Clean slate for re-formatting
```

### 4. Legacy Document Migration
```
Scenario: Migrate old .doc files to modern plain text

Workflow:
1. Open old_document.docx
2. Extract text (removes legacy formatting)
3. Save as UTF-8 text
4. Import into modern system
```

### 5. Bulk Text Extraction
```
Task: Extract text from 50 PDF reports

Process:
For each PDF:
  1. Open in RTF Editor
  2. Text extracted
  3. Save as .txt
  4. Next file
```

## Technical Details

### DOCX Extraction

Uses `python-docx` library:

```python
import docx
doc = docx.Document(file_path)
paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
plain_text = '\n\n'.join(paragraphs)
```

**Features:**
- Extracts all paragraph text
- Preserves paragraph breaks (double newline)
- Skips empty paragraphs
- No tables, no images, no formatting

### PDF Extraction

Uses `pypdf` library:

```python
import pypdf
reader = pypdf.PdfReader(file_path)
text_parts = []
for page in reader.pages:
    text = page.extract_text()
    if text.strip():
        text_parts.append(text.strip())
plain_text = '\n\n'.join(text_parts)
```

**Features:**
- Extracts text from all pages
- Page breaks = double newline
- Skips empty pages
- No images, no graphics

### Error Handling

**Missing Libraries:**
If `python-docx` or `pypdf` not installed:

```
┌──────────────────────────────────┐
│ Missing Library                  │
├──────────────────────────────────┤
│ python-docx library not          │
│ installed.                       │
│                                  │
│ Install with:                    │
│ pip install python-docx          │
└──────────────────────────────────┘
```

**Corrupted Files:**
If file can't be read:
```
┌──────────────────────────────────┐
│ Error                            │
├──────────────────────────────────┤
│ Could not extract text from      │
│ DOCX/PDF file                    │
└──────────────────────────────────┘
```

## File Type Support

### Now Supported (Open)
✅ Markdown (*.md)
✅ HTML (*.html, *.htm)
✅ Text (*.txt) - with multi-encoding support
✅ **Word Documents (*.docx)** ← NEW!
✅ **PDF Documents (*.pdf)** ← NEW!

### Supported (Save)
✅ Markdown (*.md)
✅ HTML (*.html)
✅ Text (*.txt) - always UTF-8

## Dependencies

Already in `requirements.txt`:
```
python-docx>=1.1.0
pypdf>=3.17.0
```

Install if needed:
```bash
pip install python-docx pypdf
```

## Limitations

### DOCX Extraction
- ❌ **No tables** - table content not extracted
- ❌ **No images** - images ignored
- ❌ **No headers/footers** - only body paragraphs
- ❌ **No formatting** - bold, italic, colors removed
- ✅ **Just text** - clean paragraph text only

### PDF Extraction
- ❌ **No images** - graphics ignored
- ❌ **No scanned text** - requires OCR (not included)
- ❌ **Layout may differ** - PDF layout to linear text
- ❌ **Some PDFs** - complex PDFs may not extract well
- ✅ **Text-based PDFs** - works great for normal PDFs

### Solutions
- **Tables:** Consider copying manually if needed
- **Scanned PDFs:** Use OCR tool first (Tesseract, Adobe)
- **Complex layouts:** May need manual cleanup after extraction

## Best Practices

### 1. Check Extracted Text
Always review extracted text before saving - some complex documents may need manual cleanup.

### 2. Use for Simple Documents
Works best with straightforward documents (articles, reports, essays).

### 3. Name Files Clearly
```
report.docx → report_extracted.txt
article.pdf → article_text.txt
```

### 4. Preserve Originals
Keep original DOCX/PDF files - extraction is lossy (formatting removed).

### 5. Batch Processing
For many files, open → extract → save → repeat.

## Examples

### Example 1: Extract Research Paper

**Input:** `research_paper.pdf` (20 pages, formatted)

**Process:**
1. File > Open Document
2. Select research_paper.pdf
3. Text from all 20 pages extracted
4. File > Save Document
5. Save as research_paper_text.txt

**Output:** Clean UTF-8 text, ready for analysis

### Example 2: Clean Up Word Document

**Input:** `messy_formatting.docx` (lots of fonts, colors, styles)

**Process:**
1. Open messy_formatting.docx
2. All formatting stripped
3. Save as clean_version.txt

**Output:** Plain text, ready to re-format cleanly

### Example 3: PDF to Markdown

**Input:** `article.pdf`

**Process:**
1. Open article.pdf (extracts as plain text)
2. Manually add markdown formatting (# headers, **bold**, etc.)
3. Save as article.md

**Output:** Markdown version of PDF article

## Summary

The RTF Editor is now a **universal text extractor**:

✅ Opens DOCX/PDF files
✅ Extracts clean plain text
✅ Removes all formatting/HTML
✅ Saves as UTF-8
✅ Perfect for text normalization

Combined with encoding normalization:
```
Legacy/Complex Document → RTF Editor → Clean UTF-8 Text
```

Your one-stop shop for text extraction and normalization! 📄→📝✨
