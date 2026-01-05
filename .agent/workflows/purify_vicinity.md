---
description: "♃ Jupiter: Post-task code purification ritual to eliminate entropy in modified files"
---

# The Rite of Purification (Vicinity Sweep)

**"The Scout leaves the campsite cleaner than they found it."**

This workflow is invoked **after completing any code modification task**. It enforces Section 6 of the Covenant: The Ritual of the Scout.

---

## The Trigger

After any code change is complete and verified, before declaring the task "Done," perform this Rite on all files that were touched during the task.

---

## The Four Acts of Purification

For each modified file, perform these cleansings:

### 1. The Pruning (Unused Imports)
- Scan the import block at the top of the file.
- Remove any imports that are not referenced in the code body.
- Reorder imports: `Standard Library` → `Third Party` → `Local Pillars`.

### 2. The Illumination (Type Hints)
- Identify any function parameters or return values missing type hints.
- Add type annotations where they are absent.
- Example: `def calculate(value):` → `def calculate(value: int) -> float:`

### 3. The Inscription (Docstrings)
- Ensure every public function and class has a docstring.
- Docstrings must explain **Intent**, not just mechanics.
- Bad: `"""Calculates the value."""`
- Good: `"""Applies the Amun Ratio to derive the harmonic frequency."""`

### 4. The Exorcism (Dead Code)
- Identify any commented-out code blocks (`# old_code = ...`).
- Delete them. We have Git for history.
- Identify any `TODO` or `FIXME` comments that are now obsolete and remove them.

---

## Automated Scan (The Sentinel's Lens)

Before manual review, invoke the **Scout Script**:

```bash
# Single file
python3 scripts/covenant_scripts/scout.py src/path/to/file.py

# Multiple files
python3 scripts/covenant_scripts/scout.py file1.py file2.py

# Entire codebase (Recursive Scan)
python3 scripts/covenant_scripts/scout.py --scan
```

The script checks for:
- **Missing Docstrings** (Module, Class, Function)
- **Potential Dead Code** (commented out code, FIXMEs)
- **Syntax Errors**

Review the output and apply fixes as needed.

## The Presentation

After performing the Four Acts, present a summary to the Magus:

```
🧹 Rite of Purification Complete

Files Cleansed:
- `src/pillars/document_manager/ui/mindscape_page.py`
  - Removed 2 unused imports
  - Added type hints to 3 functions
  - Deleted 5 lines of dead code

- `src/pillars/document_manager/services/notebook_service.py`
  - Added docstring to `adopt_document`

Apply these cleanups? (Awaiting consent)
```

---

## The Constraint

- **Incidental, not Structural**: This workflow cleanses *within* the touched files. It does not trigger large-scale refactors.
- **Consent Required**: Present the diff. Do not apply without explicit approval.
- **Scope Limit**: If a file was only viewed (not edited), it is outside the Rite's purview unless the Magus requests otherwise.
