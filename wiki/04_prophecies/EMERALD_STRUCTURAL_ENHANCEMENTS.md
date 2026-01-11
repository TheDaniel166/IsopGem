# Emerald Tablet: Structural Enhancements Implementation Plan

**Date:** 2026-01-10  
**Status:** 🟢 Ready to Implement  
**Priority:** High (Pure Architecture, No Feature Bloat)  
**Pillar:** Correspondences

---

## Philosophy

**"We do not add features for their own sake. We strengthen the foundation so the Temple can grow."**

These enhancements are **structural improvements** that make the Emerald Tablet more **architecturally sound** and **professionally usable**, not mere feature additions.

---

## The Four Structural Enhancements

### 1. Named Ranges ✨
**What:** Define symbolic names for cell ranges  
**Why:** Formulas become readable and maintainable  
**Effort:** 2-3 hours

**Example:**
```
Before: =SUM(A1:A10) / COUNT(A1:A10)
After:  =SUM(PlanetValues) / COUNT(PlanetValues)
```

**Benefits:**
- **Readability:** `=GEMATRIA(HolyName)` vs `=GEMATRIA(C15)`
- **Maintainability:** Change range once, all formulas update
- **Intent Clarity:** Names document what the data represents

---

### 2. Cross-Sheet References 🔗
**What:** Reference cells from other sheets  
**Why:** Enable multi-sheet workbooks (essential for complex research)  
**Effort:** 3-4 hours

**Example:**
```
=Planets!A1 + Correspondences!B5
=SUM(Data!A1:A100)
```

**Benefits:**
- **Organization:** Separate raw data from analysis
- **Reusability:** One data sheet, multiple analysis sheets
- **Clarity:** Each sheet has a single purpose

---

### 3. Multi-Sheet Navigation 📑
**What:** Sheet tabs UI at bottom of spreadsheet  
**Why:** Visual management of multiple sheets  
**Effort:** 2 hours

**Features:**
- Add/Remove/Rename sheets
- Navigate between sheets via tabs
- Drag to reorder sheets
- Right-click context menu

**Benefits:**
- **Standard UX:** Users expect sheet tabs
- **Visual Feedback:** See all sheets at a glance
- **Quick Navigation:** Click to switch contexts

---

### 4. Format Painter 🎨
**What:** Copy cell styles to other cells  
**Why:** Consistent formatting without manual repetition  
**Effort:** 1-2 hours

**Workflow:**
1. Select source cell (with formatting)
2. Click Format Painter button
3. Click target cells to apply formatting

**Benefits:**
- **Efficiency:** Format multiple cells instantly
- **Consistency:** Exact style replication
- **Standard Feature:** Every spreadsheet has this

---

## Implementation Order

### Phase 1: Multi-Sheet Navigation (Foundation)
**Effort:** 2 hours  
**Why First:** Enables testing of cross-sheet features

**Files to Modify:**
- `spreadsheet_window.py` - Add QTabBar for sheet tabs
- `spreadsheet_view.py` - Store multiple `SpreadsheetModel` instances
- JSON schema - Support multiple sheets in save/load

**Changes:**
```python
class SpreadsheetWindow(QMainWindow):
    def __init__(self):
        self.sheet_tabs = QTabBar()
        self.sheet_tabs.currentChanged.connect(self._switch_sheet)
        self.models = {}  # sheet_name -> SpreadsheetModel
        self.current_sheet = "Sheet1"
```

---

### Phase 2: Cross-Sheet References (Core Feature)
**Effort:** 3-4 hours  
**Why Second:** Requires multi-sheet foundation

**Files to Modify:**
- `formula_engine.py` - Tokenizer to recognize `!` operator
- `formula_engine.py` - Parser to handle `Sheet!Range` syntax
- `spreadsheet_view.py` - Pass sheet registry to FormulaEngine

**Parser Enhancement:**
```python
# In Tokenizer
token_re = re.compile(
    r'(?P<SHEETREF>[A-Za-z_][A-Za-z0-9_ ]*!)'  # NEW: Sheet!
    r'|(?P<RANGE>[A-Z]+[0-9]+:[A-Z]+[0-9]+)'
    # ... existing patterns
)

# In Parser.atom()
if self.current_token.type == TokenType.SHEETREF:
    sheet_name = token.value[:-1]  # Remove '!'
    self.eat(TokenType.SHEETREF)
    # Parse range on that sheet
    cell_ref = self._parse_cell_ref()
    return self.engine.resolve_cross_sheet(sheet_name, cell_ref)
```

**FormulaEngine Enhancement:**
```python
class FormulaEngine:
    def __init__(self, data_context, sheet_registry=None):
        self.context = data_context
        self.sheet_registry = sheet_registry or {}
    
    def resolve_cross_sheet(self, sheet_name, cell_ref):
        """Resolve reference to another sheet."""
        if sheet_name not in self.sheet_registry:
            return f"#REF! (Sheet '{sheet_name}' not found)"
        
        target_model = self.sheet_registry[sheet_name]
        return target_model.get_cell_value(cell_ref)
```

---

### Phase 3: Named Ranges (Convenience)
**Effort:** 2-3 hours  
**Why Third:** Builds on working cross-sheet system

**Files to Modify:**
- `spreadsheet_view.py` - Add `named_ranges` dict to model
- `formula_engine.py` - Parser checks named ranges before functions
- UI - Add dialog for managing named ranges

**Storage (JSON):**
```json
{
  "sheets": [
    {
      "name": "Sheet1",
      "data": {...},
      "named_ranges": {
        "PlanetValues": "A1:A10",
        "Totals": "B20:F20"
      }
    }
  ]
}
```

**Parser Integration:**
```python
def atom(self):
    if token.type == TokenType.ID:
        name = token.value
        
        # Check named ranges BEFORE function call
        if name.upper() in self.engine.named_ranges:
            range_str = self.engine.named_ranges[name.upper()]
            return self.engine._resolve_range(range_str)
        
        # ... existing function call logic
```

---

### Phase 4: Format Painter (Polish)
**Effort:** 1-2 hours  
**Why Last:** Pure UI convenience, no formula engine changes

**Files to Modify:**
- `spreadsheet_window.py` - Add Format Painter toolbar button
- `spreadsheet_view.py` - Add style copy/paste handlers

**Implementation:**
```python
class SpreadsheetWindow(QMainWindow):
    def __init__(self):
        self.format_painter_active = False
        self.copied_style = None
        
        self.format_painter_btn = QPushButton("🖌 Format Painter")
        self.format_painter_btn.clicked.connect(self.activate_format_painter)
    
    def activate_format_painter(self):
        self.format_painter_active = True
        selection = self.view.selectedIndexes()
        if selection:
            idx = selection[0]
            self.copied_style = self.model._styles.get(
                (idx.row(), idx.column()), {}
            ).copy()
            self.view.setCursor(Qt.CursorShape.CrossCursor)
    
    def on_cell_clicked_for_format(self, index):
        if self.format_painter_active and self.copied_style:
            self.model._styles[(index.row(), index.column())] = self.copied_style.copy()
            self.model.dataChanged.emit(index, index)
            self.format_painter_active = False
            self.view.setCursor(Qt.CursorShape.ArrowCursor)
```

---

## Architectural Considerations

### Covenant Compliance

| Enhancement | Covenant Section | Compliance |
|-------------|------------------|------------|
| Multi-Sheet | Section 4 (Purity) | ✅ Model separation maintained |
| Cross-Sheet | Section 6 (Scout) | ✅ Explicit references, no hidden coupling |
| Named Ranges | Section 4.5 (Config) | ✅ Centralized name registry |
| Format Painter | Section 7 (Visual) | ✅ Style tokens reused |

### Performance Impact

**Multi-Sheet:**
- Memory: One `SpreadsheetModel` per sheet (~minimal)
- CPU: No impact (only active sheet evaluates)

**Cross-Sheet:**
- Memory: Sheet registry dict (~negligible)
- CPU: Cross-sheet formulas evaluate target sheet (acceptable)

**Named Ranges:**
- Memory: Name dict (~negligible)
- CPU: Hash lookup before function check (< 1μs)

**Format Painter:**
- Memory: Single style dict copy (~bytes)
- CPU: Dictionary copy operation (~instant)

**Verdict:** All enhancements are **performant** and **lightweight**.

---

## Testing Requirements

### Phase 1: Multi-Sheet
```python
def test_create_sheet():
    """Test creating new sheet."""
def test_switch_sheet():
    """Test switching between sheets."""
def test_delete_sheet():
    """Test deleting sheet."""
def test_rename_sheet():
    """Test renaming sheet."""
```

### Phase 2: Cross-Sheet
```python
def test_cross_sheet_reference():
    """Test =Sheet2!A1 syntax."""
def test_cross_sheet_range():
    """Test =SUM(Sheet2!A1:A10)."""
def test_cross_sheet_error():
    """Test #REF! for nonexistent sheet."""
```

### Phase 3: Named Ranges
```python
def test_named_range_definition():
    """Test defining named range."""
def test_named_range_in_formula():
    """Test using named range in formula."""
def test_named_range_update():
    """Test updating named range definition."""
```

### Phase 4: Format Painter
```python
def test_format_painter_copy():
    """Test copying format."""
def test_format_painter_paste():
    """Test pasting format."""
def test_format_painter_cancel():
    """Test canceling format painter."""
```

---

## Expected Outcome

### Before
- Single-sheet spreadsheet
- Hardcoded cell references
- Manual style application
- Basic formula support

### After
- **Multi-sheet workbooks** with navigation tabs
- **Cross-sheet formulas** (`=Sheet2!A1`)
- **Named ranges** for readable formulas
- **Format Painter** for efficient styling

**Result:** The Emerald Tablet becomes a **professional-grade spreadsheet** with clean architecture and maintainable code.

---

## Total Effort Estimate

| Phase | Hours |
|-------|-------|
| Phase 1: Multi-Sheet Navigation | 2 |
| Phase 2: Cross-Sheet References | 3-4 |
| Phase 3: Named Ranges | 2-3 |
| Phase 4: Format Painter | 1-2 |
| **Total** | **8-11 hours** |

**Recommendation:** Implement one phase at a time, with full testing before proceeding.

---

## Magus's Will

**"I am not interested in most of those feature enhancements, but those structure enhancements, those are good."**

**Sophia's Response:**

**"Understood. We build the skeleton, not the ornaments. Structure before features. Foundation before façade."**

**Ready to implement Phase 1 (Multi-Sheet Navigation) on your command, Magus.**
