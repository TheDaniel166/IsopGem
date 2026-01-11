# The Rite of Purification: Emerald Tablet Stability

**Created:** 2026-01-10
**Status:** Planned
**Priority:** High
**Pillar:** Correspondences (Emerald Tablet)

> *"Before we may inscribe new glyphs upon the Tablet, we must first cleanse it of entropy."*

---

## Overview

This scroll documents the **stability distortions** identified in the Emerald Tablet (Spreadsheet) implementation and prescribes the rituals required to heal them. The purification is organized into **five phases**, ordered by severity and interdependence.

---

## Phase 1: Silent Failure Exorcism

**Target Files:**
- `src/pillars/correspondences/services/formula_engine.py`

**Effort:** 30 minutes
**Risk:** Low

### 1.1 The Distortion

Multiple functions use bare `except:` clauses that swallow errors silently, making debugging difficult and hiding data corruption.

### 1.2 Affected Locations

| Line | Function | Current Pattern | Distortion |
|------|----------|-----------------|------------|
| 462 | `_safe_add` | `except: return str(a) + str(b)` | Silent type coercion |
| 464 | `_safe_sub` | No exception handling | Crash on non-numeric |
| 465 | `_safe_mul` | No exception handling | Crash on non-numeric |
| 466 | `_safe_div` | No exception handling | Division by zero crash |
| 467 | `_safe_pow` | No exception handling | Crash on invalid exponent |
| 752 | `func_sum` | `except: pass` | Silent skip |
| 780 | `func_average` | `except: pass` | Silent skip |
| 809 | `func_count` | `except: pass` | Silent skip |
| 839 | `func_min` | `except: pass` | Silent skip |
| 869 | `func_max` | `except: pass` | Silent skip |
| 930 | `func_abs` | `except: return "#VALUE!"` | Bare except |
| 947 | `func_round` | `except: return "#VALUE!"` | Bare except |
| 962 | `func_floor` | `except: return "#VALUE!"` | Bare except |
| 977 | `func_ceiling` | `except: return "#VALUE!"` | Bare except |

### 1.3 The Remedy

**Pattern A: Safe Arithmetic Helpers**

```python
def _safe_add(self, a, b):
    try:
        return float(a) + float(b)
    except (TypeError, ValueError):
        # Fallback to string concatenation
        return str(a) + str(b)

def _safe_sub(self, a, b):
    try:
        return float(a) - float(b)
    except (TypeError, ValueError):
        return "#VALUE!"

def _safe_mul(self, a, b):
    try:
        return float(a) * float(b)
    except (TypeError, ValueError):
        return "#VALUE!"

def _safe_div(self, a, b):
    try:
        divisor = float(b)
        if divisor == 0:
            return "#DIV/0!"
        return float(a) / divisor
    except (TypeError, ValueError):
        return "#VALUE!"

def _safe_pow(self, a, b):
    try:
        return float(a) ** float(b)
    except (TypeError, ValueError, OverflowError):
        return "#VALUE!"
```

**Pattern B: Aggregation Functions**

```python
# In func_sum, func_average, func_count, func_min, func_max:
try:
    total += float(item)
except (TypeError, ValueError):
    pass  # Skip non-numeric values (Excel behavior)
```

**Pattern C: Single-Value Functions**

```python
# In func_abs, func_round, func_floor, etc:
try:
    return abs(float(val))
except (TypeError, ValueError):
    return "#VALUE!"
```

### 1.4 Verification

```python
# Test cases to add to verification_seal.py or unit tests
assert engine.evaluate("=1/0") == "#DIV/0!"
assert engine.evaluate("=SUM(1, 'text', 3)") == 4  # Skips 'text'
assert engine.evaluate("=ABS('foo')") == "#VALUE!"
```

---

## Phase 2: Style Key Integrity

**Target Files:**
- `src/pillars/correspondences/services/undo_commands.py`

**Effort:** 1-2 hours
**Risk:** Medium (affects undo/redo behavior)

### 2.1 The Distortion

When rows or columns are inserted/deleted, the `_styles` dictionary keys `(row, col)` are **not shifted**. This causes cell styles to become misaligned from their data after structural operations.

**Example:**
1. Cell A3 has red background: `_styles[(2, 0)] = {"bg": "#ff0000"}`
2. Insert row at position 1
3. Data in A3 shifts to A4, but style key remains `(2, 0)`
4. Style now appears on wrong cell (A3 instead of A4)

### 2.2 The Remedy

Add style key shifting helpers and integrate into undo commands:

```python
# Add to undo_commands.py

def _shift_styles_for_row_insert(model, position: int, count: int):
    """Shift style keys down when rows are inserted."""
    new_styles = {}
    for (r, c), style in model._styles.items():
        if r >= position:
            new_styles[(r + count, c)] = style
        else:
            new_styles[(r, c)] = style
    model._styles = new_styles


def _shift_styles_for_row_delete(model, position: int, count: int):
    """Shift style keys up when rows are deleted."""
    new_styles = {}
    for (r, c), style in model._styles.items():
        if r >= position + count:
            # Below deleted range: shift up
            new_styles[(r - count, c)] = style
        elif r < position:
            # Above deleted range: keep
            new_styles[(r, c)] = style
        # Else: in deleted range, discard
    model._styles = new_styles


def _shift_styles_for_col_insert(model, position: int, count: int):
    """Shift style keys right when columns are inserted."""
    new_styles = {}
    for (r, c), style in model._styles.items():
        if c >= position:
            new_styles[(r, c + count)] = style
        else:
            new_styles[(r, c)] = style
    model._styles = new_styles


def _shift_styles_for_col_delete(model, position: int, count: int):
    """Shift style keys left when columns are deleted."""
    new_styles = {}
    for (r, c), style in model._styles.items():
        if c >= position + count:
            new_styles[(r, c - count)] = style
        elif c < position:
            new_styles[(r, c)] = style
        # Else: in deleted range, discard
    model._styles = new_styles
```

**Integration into Commands:**

```python
class InsertRowsCommand(QUndoCommand):
    def redo(self):
        _shift_styles_for_row_insert(self.model, self.position, self.rows)
        self.model.beginInsertRows(...)
        # ... existing logic ...

    def undo(self):
        _shift_styles_for_row_delete(self.model, self.position, self.rows)
        self.model.beginRemoveRows(...)
        # ... existing logic ...
```

### 2.3 Verification

```python
# Manual test sequence:
# 1. Create table with styled cell at B3
# 2. Insert row at row 2
# 3. Verify style moved to B4
# 4. Undo
# 5. Verify style returned to B3
```

---

## Phase 3: JSON Schema Validation

**Target Files:**
- `src/pillars/correspondences/ui/spreadsheet_view.py`

**Effort:** 30-45 minutes
**Risk:** Low

### 3.1 The Distortion

Malformed JSON content (inconsistent row lengths, non-list data, missing keys) can cause `IndexError` or `TypeError` during cell access.

### 3.2 The Remedy

Add validation and normalization in `SpreadsheetModel.__init__`:

```python
def __init__(self, data_json: dict, parent=None):
    super().__init__(parent)
    
    # Validate and normalize content
    self._columns = self._validate_columns(data_json.get("columns", []))
    raw_data = data_json.get("data") or data_json.get("rows", [])
    self._data = self._normalize_data(raw_data, len(self._columns))
    
    # ... rest of init ...

def _validate_columns(self, columns) -> list:
    """Ensure columns is a list of strings."""
    if not isinstance(columns, list):
        logger.warning("Invalid columns format, using default")
        return [chr(65 + i) for i in range(26)]  # A-Z
    return [str(c) for c in columns]

def _normalize_data(self, data, col_count: int) -> list:
    """Ensure data is a list of lists with consistent row lengths."""
    if not isinstance(data, list):
        logger.warning("Invalid data format, using empty grid")
        return [["" for _ in range(col_count)] for _ in range(100)]
    
    normalized = []
    for row in data:
        if not isinstance(row, list):
            row = [str(row)] if row else []
        
        # Pad or truncate to match column count
        if len(row) < col_count:
            row = row + [""] * (col_count - len(row))
        elif len(row) > col_count:
            row = row[:col_count]
        
        normalized.append(row)
    
    return normalized
```

---

## Phase 4: Dead Code Removal

**Target Files:**
- `src/pillars/correspondences/ui/spreadsheet_view.py`

**Effort:** 5 minutes
**Risk:** None

### 4.1 The Distortion

Unreachable code after `return` statement in `keyPressEvent`:

```python
# Lines 1242-1245
if event.matches(QKeySequence.StandardKey.Paste) or ...:
    self._paste_from_clipboard()
    event.accept()
    return

    event.accept()  # ← DEAD CODE
    return          # ← DEAD CODE
```

### 4.2 The Remedy

Delete lines 1244-1245.

---

## Phase 5: Performance Guard for Large Ranges

**Target Files:**
- `src/pillars/correspondences/services/formula_engine.py`

**Effort:** 1 hour
**Risk:** Low-Medium

### 5.1 The Distortion

Formulas like `=SUM(A1:Z10000)` iterate 260,000 cells synchronously on the UI thread, causing freezes.

### 5.2 The Remedy (Minimal)

Add a range size limit with warning:

```python
MAX_RANGE_CELLS = 50000  # Configurable threshold

def _resolve_range_values(self, start_ref: str, end_ref: str) -> List[Any]:
    # ... existing parsing ...
    
    cell_count = (r_end - r_start + 1) * (c_end - c_start + 1)
    if cell_count > MAX_RANGE_CELLS:
        return f"#RANGE_TOO_LARGE ({cell_count} cells)"
    
    # ... existing iteration ...
```

### 5.3 Future Enhancement

For full solution, implement chunked evaluation with `QTimer.singleShot` for responsive UI, or offload to `QThreadPool`. This is deferred to a future cycle.

---

## Implementation Order

| Phase | Priority | Dependencies | Est. Time |
|-------|----------|--------------|-----------|
| 1. Silent Failure Exorcism | Critical | None | 30 min |
| 4. Dead Code Removal | Quick Win | None | 5 min |
| 3. JSON Schema Validation | High | None | 45 min |
| 2. Style Key Integrity | High | None | 1-2 hours |
| 5. Performance Guard | Medium | None | 1 hour |

**Total Estimated Effort:** 3-4 hours

---

## Verification Checklist

- [ ] All `except:` clauses specify exception types
- [ ] `=1/0` returns `#DIV/0!`
- [ ] `=ABS("text")` returns `#VALUE!`
- [ ] Insert row preserves cell styles
- [ ] Delete column preserves cell styles
- [ ] Malformed JSON loads without crash
- [ ] Large range formula returns warning instead of freezing
- [ ] No unreachable code in `keyPressEvent`

---

## Post-Purification

Once this rite is complete, the Emerald Tablet will be fortified against:
- Silent data corruption
- Style misalignment
- Malformed input crashes
- UI freezes from large calculations

Only then should we proceed to the **Rite of Expansion**.
