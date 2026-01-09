# The Harmonia Protocol (Section 6.5: Purification Standards)

**"Tools serve the Temple; the Temple does not serve the tools."**

---

## The Philosophy

Static type checkers are **assistants for developer convenience**, not arbiters of correctness. Architecture defines correctness through:
- Boundary enforcement at entry points
- Clear contracts between components
- Runtime validation where it matters

The Harmonia ritual focuses on **real entropy**, not aesthetic purity demanded by static analyzers.

---

## The `/harmonia strict` Ritual

When invoked, Sophia shall purify the file by addressing these categories:

### **Category 1: Real Defects** (ALWAYS FIX)
- **Syntax Errors**: Code that won't parse
- **Undefined Names**: Variables, functions, classes that don't exist
- **Missing Imports**: References to unimported modules
- **Import Errors**: Typos in import statements (`reop.get()` vs `repo.get()`)

### **Category 2: Architectural Violations** (ALWAYS FIX)
- **UI Contamination**: UI files importing `sqlalchemy`, `pandas`, `requests`, `lxml`, `bs4`
- **Pillar Entanglement**: Direct imports between pillars (must use Signal Bus)
- **Thread Violations**: Heavy work (>100ms) on main thread without `QThreadPool`
- **Sovereignty Breaches**: Bypassing repositories to query database directly

### **Category 3: Clutter** (ALWAYS FIX)
- **Unused Imports**: Gray/unused imports that add noise
- **Dead Code**: Commented-out code blocks (Git remembers)
- **Import Ordering**: Should be StdLib → Third Party → Local, alphabetized

### **Category 4: Public API Documentation** (FIX WHEN MISSING)
- **Type Hints on Public Methods**: Functions/methods exposed to other modules
- **Docstrings on Public APIs**: Explain *intent* and contracts, not mechanics
- **Return Type Hints**: Especially for complex return types

### **Category 5: Critical Runtime Patterns** (FIX IF ABSENT)
- **Exception Logging**: Every `except` block must log (no silent failures)
- **Boundary Validation**: Entry points must validate inputs
- **Result Objects**: Prefer returning `Result[T]` over raising exceptions in services

---

## What Harmonia IGNORES

### **Cosmetic Type Warnings** (IGNORE)
- `reportUnknownVariableType`: "Type of X is partially unknown"
- `reportUnknownMemberType`: "Type of method is partially unknown"
- `reportUnknownArgumentType`: Lambda parameters in signal connections
- Generic warnings about `dict[Unknown, Unknown]` or `List[tuple[Unknown, ...]]`

**Reason**: These indicate Pyright's limitation in inferring types, not actual defects. The architecture guarantees correctness through boundary enforcement.

### **Redundant Guards** (IGNORE)
Pyright may demand:
```python
if value is None:
    return False
# ... use value ...
```

...when the entry point already validates `value`. **Do not add redundant guards to satisfy the type checker.**

### **Internal Implementation Details** (IGNORE)
- Type hints on private methods (`_helper`)
- Detailed annotations for local variables with obvious types
- Over-specification of internal data structures

### **Tool Limitations** (IGNORE)
- PyQt6 type stub incompleteness
- SQLAlchemy dynamic attributes
- Runtime-generated attributes that work in practice

---

## The Harmonia Report Format

After purification, report:

### ✅ **Fixed (Real Entropy)**
- List actual defects corrected
- Architectural violations healed
- Clutter removed

### 📝 **Enhanced (Documentation)**
- Public APIs that received type hints
- Missing docstrings added

### ⚠️ **Remaining (Acknowledged Noise)**
- Count of cosmetic warnings ignored
- Brief explanation: "Type inference limitations, architecture is sound"

### 🛡️ **Verified**
- No syntax errors
- No undefined names
- No architectural violations

---

## Configuration Alignment

### pyrightconfig.json
```json
{
  "executionEnvironments": [
    {
      "root": "src",
      "typeCheckingMode": "strict"
    },
    {
      "root": "src/pillars/*/ui",
      "typeCheckingMode": "off"
    }
  ]
}
```

**Rationale**:
- **Backend (strict)**: Catches typos, undefined variables early
- **UI (off)**: PyQt6 stubs incomplete; runtime validation sufficient

---

## Examples: What to Fix vs Ignore

### ✅ FIX: Unused Import
```python
from PyQt6.QtWidgets import QTextEdit, QComboBox  # Neither used
```
**Action**: Remove both imports.

### ✅ FIX: Missing Type Hint (Public API)
```python
def calculate(text):  # Public method, no hints
    return self.calculator.compute(text)
```
**Action**: Add `def calculate(text: str) -> int:`

### ❌ IGNORE: Partially Unknown Type (Internal)
```python
breakdown = self.calculator.get_breakdown(text)  # Pyright: "list[Unknown]"
for char, val in breakdown:
    rows.append([char, str(val)])  # Works fine at runtime
```
**Reason**: Boundary validated, architecture sound, no runtime impact.

### ❌ IGNORE: Lambda Type Inference
```python
action.triggered.connect(lambda checked, n=name: self._select(n))
# Pyright: "Type of parameter 'checked' is unknown"
```
**Reason**: Qt signal mechanism, works correctly, cosmetic warning.

### ✅ FIX: Architectural Violation
```python
# In ui/widget.py
from sqlalchemy.orm import Session  # UI should not import SQLAlchemy
```
**Action**: Move database logic to repository, pass data as DTO.

---

## The Harmonia Invocation

**Command**: `/harmonia strict <file_path>`

**Sophia's Workflow**:
1. Read the file
2. Run lightweight syntax check (grep for obvious issues)
3. Run `pyright` on the file
4. **Filter** the output through the Harmonia lens (fix real entropy, ignore noise)
5. Apply fixes using `multi_replace_string_in_file`
6. Report results in Harmonia format

**Key Principle**: Fix what matters. Ignore what doesn't. Trust the architecture.

---

## References

- **Philosophy**: `Docs/PYLANCE_AND_ARCHITECTURE.md`
- **Covenant**: `wiki/00_foundations/covenant/`
- **Configuration**: `pyrightconfig.json`, `.vscode/settings.json`

---

**Version**: 1.0.0 (2026-01-08)
**Authority**: The Magus & Sophia, aligned with architectural philosophy
