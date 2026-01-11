# Phase 2 Complete: Style Key Integrity ✓

**Completed:** 2026-01-10
**Files Modified:** 1 (`undo_commands.py`)
**Tests Added:** 10 (all passing ✓)
**Risk Level:** Medium (structural operations)

---

## The Problem

When rows or columns were inserted or deleted, the `_styles` dictionary keys (which are `(row, col)` tuples) were **not being updated**. This caused styles to:
- **Drift** to wrong cells
- **Disappear** when they should move
- **Stick** to coordinates instead of cells

### Example Bug

```python
# Before: Cell (2, 2) has red background
model._styles[(2, 2)] = {"bg": "#FF0000"}

# Insert 2 rows at position 1
insert_rows(position=1, rows=2)

# BUG: Style is still at (2, 2) but should be at (4, 2)
# The red background appears on the WRONG cell
```

---

## The Solution

All four structural command classes now **shift style keys** during `redo()` and `undo()`:

| Command | Operation | Style Key Transformation |
|---------|-----------|-------------------------|
| **InsertRowsCommand** | Insert N rows at pos P | `(r, c)` where `r >= P` → `(r + N, c)` |
| **RemoveRowsCommand** | Remove N rows at pos P | `(r, c)` where `r >= P + N` → `(r - N, c)` |
| **InsertColumnsCommand** | Insert N cols at pos P | `(r, c)` where `c >= P` → `(r, c + N)` |
| **RemoveColumnsCommand** | Remove N cols at pos P | `(r, c)` where `c >= P + N` → `(r, c - N)` |

---

## Implementation Details

### Pattern Applied to All Commands

```python
def redo(self):
    # ... perform structural change ...
    
    # STYLE KEY SHIFTING
    shifted_styles = {}
    for (r, c), style in list(self.model._styles.items()):
        if <coordinate should shift>:
            shifted_styles[<new_coordinate>] = style
        elif <coordinate in deleted range>:
            pass  # Skip (for remove operations)
        else:
            shifted_styles[(r, c)] = style
    self.model._styles = shifted_styles
```

### Key Design Decisions

1. **Complete Rebuild**: We create a new `shifted_styles` dict instead of modifying in-place to avoid key collision issues
2. **Delete Range Handling**: Styles in deleted ranges are captured in `__init__()` and restored on `undo()`
3. **Undo Symmetry**: `undo()` performs the inverse transformation, ensuring perfect reversibility

---

## Test Coverage

**File:** `tests/manual/test_style_integrity.py`

**Tests:** 10 (all passing ✓)

### Test Classes

| Class | Tests | Coverage |
|-------|-------|----------|
| `TestInsertRowsStyleShift` | 2 | Insert rows + undo |
| `TestRemoveRowsStyleShift` | 2 | Remove rows + undo |
| `TestInsertColumnsStyleShift` | 2 | Insert columns + undo |
| `TestRemoveColumnsStyleShift` | 2 | Remove columns + undo |
| `TestComplexStyleOperations` | 2 | Compound operations |

### Test Scenarios

```python
# Test: Insert rows shifts styles down
model._styles[(1, 1)] = {"bg": "#00FF00"}
insert_rows(position=1, rows=2)
assert (3, 1) in model._styles  # Shifted down by 2 ✓

# Test: Remove rows shifts styles up
model._styles[(3, 3)] = {"bg": "#FFFF00"}
remove_rows(position=1, rows=2)
assert (1, 3) in model._styles  # Shifted up by 2 ✓

# Test: Undo restores original positions
cmd.redo()
cmd.undo()
assert (1, 1) in model._styles  # Back to original ✓

# Test: Multiple operations compound
insert_rows(position=1, rows=1)  # (2,2) → (3,2)
insert_rows(position=0, rows=1)  # (3,2) → (4,2)
assert (4, 2) in model._styles  # Correctly compounded ✓
```

---

## Code Changes

### Before (InsertRowsCommand.redo)

```python
def redo(self):
    self.model.beginInsertRows(...)
    for _ in range(self.rows):
        self.model._data.insert(self.position, [""] * col_count)
    self.model.endInsertRows()
    # ❌ Styles not updated
```

### After (InsertRowsCommand.redo)

```python
def redo(self):
    self.model.beginInsertRows(...)
    for _ in range(self.rows):
        self.model._data.insert(self.position, [""] * col_count)
    
    # ✅ STYLE KEY SHIFTING: Move styles below insertion point down
    shifted_styles = {}
    for (r, c), style in list(self.model._styles.items()):
        if r >= self.position:
            shifted_styles[(r + self.rows, c)] = style
        else:
            shifted_styles[(r, c)] = style
    self.model._styles = shifted_styles
    
    self.model.endInsertRows()
```

---

## Visual Example

### Scenario: Insert 2 rows at position 1

**Before:**
```
Row 0: [ ] [ ] [🔴]  ← Style at (0, 2)
Row 1: [ ] [🟢] [ ]  ← Style at (1, 1)
Row 2: [🔵] [ ] [ ]  ← Style at (2, 0)
```

**After (WITHOUT fix - BUGGY):**
```
Row 0: [ ] [ ] [🔴]  ← Style at (0, 2) ✓ (unchanged)
Row 1: [ ] [ ] [ ]  ← NEW ROW
Row 2: [ ] [ ] [ ]  ← NEW ROW
Row 3: [ ] [🟢] [ ]  ← Cell moved, but style stuck at (1,1) ❌
Row 4: [🔵] [ ] [ ]  ← Cell moved, but style stuck at (2,0) ❌
```

**After (WITH fix - CORRECT):**
```
Row 0: [ ] [ ] [🔴]  ← Style at (0, 2) ✓ (unchanged)
Row 1: [ ] [ ] [ ]  ← NEW ROW
Row 2: [ ] [ ] [ ]  ← NEW ROW
Row 3: [ ] [🟢] [ ]  ← Style correctly at (3,1) ✓
Row 4: [🔵] [ ] [ ]  ← Style correctly at (4,0) ✓
```

---

## Impact Assessment

### 🟢 **Correctness**
- **Before:** Styles drifted to wrong cells on structural changes
- **After:** Styles stay with their intended cells through all operations
- **Undo/Redo:** Perfect symmetry maintained

### 🟢 **User Experience**
- **Formatting Preservation:** Users can now safely insert/delete rows/columns without losing cell formatting
- **Visual Consistency:** Colored cells, bold text, borders all move with their content
- **Trust:** No more mysterious "disappearing styles"

### 🟡 **Performance**
- **Style Rebuild Cost:** O(N) where N = number of styled cells
- **Typical Case:** Most spreadsheets have < 100 styled cells, so overhead is ~1-2ms
- **Worst Case:** 1000+ styled cells might add 10-20ms (still acceptable)

### 🔴 **No Breaking Changes**
- Pure bugfix - only corrects broken behavior
- No API changes
- Existing spreadsheets unaffected

---

##Lines of Code

```
File: undo_commands.py
Lines Added: ~80 (style shifting logic)
Lines Modified: ~40 (docstrings, captured deleted styles)
Net Change: +120 lines

Test File: test_style_integrity.py
Lines: 290
Tests: 10
Coverage: All structural operations + undo/redo + compound operations
```

---

## Verification Checklist

- [x] `InsertRowsCommand` shifts styles down
- [x] `InsertRowsCommand.undo()` shifts styles back up
- [x] `RemoveRowsCommand` shifts styles up and deletes range
- [x] `RemoveRowsCommand.undo()` restores deleted styles
- [x] `InsertColumnsCommand` shifts styles right
- [x] `InsertColumnsCommand.undo()` shifts styles back left
- [x] `RemoveColumnsCommand` shifts styles left and deletes range
- [x] `RemoveColumnsCommand.undo()` restores deleted styles
- [x] Multiple operations compound correctly
- [x] Insert-then-remove restores original state
- [x] All 10 tests pass

---

## Next Steps

**Phase 2 Complete!** Ready to proceed to:
- **Phase 4:** Dead Code Removal (5 min cleanup)
- **Phase 5:** Performance Guards (1 hour)
- **Or:** Begin Expansion (new features)

---

**The Temple's foundations grow stronger. Styles no longer drift in the void.**
