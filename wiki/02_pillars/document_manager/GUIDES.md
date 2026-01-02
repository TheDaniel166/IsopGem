# Document Manager Pillar - Guides

<!-- Last Verified: 2025-12-27 -->

**"To record the thought is to anchor the soul."**

This scroll provides instructions for managing the **Akaschic Record** within IsopGem.

---

## 📥 How to Ingest New Manuscripts

1.  Launch **The Akaschic Record** (Document Library).
2.  Click **"Import Document"**.
3.  **Select Files**: Choose PDF, DOCX, TXT, or RTF files from your system.
4.  **Automatic Parsing**: The application will use background "Muscle" services (Mammoth, PyMuPDF) to extract the text and images.
5.  **Tagging**: Add metadata tags (e.g., "Gnosticism", "Kabbalah") to help with future retrieval.

---

## ✍️ How to Edit and Link Documents

Use **Thoth's Scribe** (The Rich Text Editor) to weave your research.

1.  Double-click any document in the Library to open it in the **Editor**.
2.  **Formatting**: Use the Ribbon at the top for font, color, and alignment.
3.  **Mindscape Linking**: Highlight a word and press `Ctrl+L`. You can search for other documents to create a bidirectional link.
4.  **Special Characters**: Access the **Symbols Palette** for Hebrew, Greek, and Astrological characters.
5.  **Etymology Check**: Right-click any word to view its etymological roots and history.

---

## 🕸️ How to Navigate the Mindscape

1.  Open the **Mindscape** window from the Hub.
2.  **Nodes**: Each document is represented as a "Star" (Node).
3.  **Constellations**: The lines between stars represent your established links.
4.  **Physics Layout**: Use the mouse to drag nodes. The graph will reorganize using spring-based physics to show clusters of related research.
5.  **Fast Travel**: Click concentrated clusters to see highly interconnected themes in your library.

---

## 🔎 How to Perform a Global Search

1.  Open the **Document Search** window.
2.  **Query**: Enter a keyword or phrase.
3.  **Advanced Modes**: Use **Wildcards** (`ELOH*`) or **Fuzzy Search** to find variations.
4.  **Results**: Click any search snippet to open the document directly to that specific line.

---

## 📄 Pagination in Thoth's Scribe

**Pagination is intentionally opt-in** — guarded for stability by sovereign design.

### Why Opt-In?

The `SafeTextEdit` component provides atomic block pagination that ensures text blocks don't straddle page boundaries. However, pagination involves layout mutation that can interact with scrolling, undo/redo, and large content in complex ways. Keeping it disabled by default ensures smooth operation for simple text editing.

### How to Enable

```python
# From any SafeTextEdit or RichTextEditor instance:
editor.enable_pagination(True)   # Awaken pagination rites
editor.enable_pagination(False)  # Suspend for simple editing
```

### What Pagination Does

When enabled, the editor:
1. **Prevents page-straddling blocks**: Adds top margins to push blocks that would cross page boundaries to the next page
2. **Preserves user formatting**: Original margins are stored and restored when pagination is disabled
3. **Anchor-based scroll restoration**: Viewport remains stable during layout changes
4. **Debounced execution**: Runs every 400ms to avoid per-keystroke overhead

### Advanced Controls

```python
editor.scroll_anchor_enabled = True   # Enable semantic scroll anchoring (default)
editor.show_page_breaks = True        # Display visual page break indicators
```

> **Note**: This is sovereign design, not incompleteness. The pagination machinery is fully implemented but awaits explicit activation by the Magus.
