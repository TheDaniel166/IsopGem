---
description: "♂ Mars: Orphan purge ritual when code artifacts are deleted or renamed"
---

# Rite of the Pyre – Orphan Purge

**"When the Body dies, the Soul must be released. We do not keep ghosts in the Library."**

This workflow is invoked whenever a significant artifact (file, class, function, or feature) is **deleted** or **renamed/moved** in the codebase.  
It enforces **Section 1.6 The Law of the Pyre** of the Covenant.

---

## The Trigger

Perform this Rite immediately after:
- Deleting a Python module/file
- Removing a major class or service
- Deprecating or extracting a feature to another pillar
- Renaming a file or class that is referenced in documentation

The Magus (or Sophia) declares:  
*"The Body known as [artifact] has been removed/renamed to [new name, if applicable]."*

---

## The Ceremony

### 1. The Summoning – Identify the Departed
We name the deceased artifact clearly:
- Full path: `src/pillars/tq/services/old_calculator.py`
- Key symbols: `OldCalculator`, `legacy_function`, etc.

### 2. The Search – Scour the Akaschic Record

**Automated Scan (Recommended):**
```bash
# Search for specific artifact references
.venv/bin/python workflow_scripts/rite_of_pyre.py <artifact_name> [additional_names...]

# Check for all orphaned file links
.venv/bin/python workflow_scripts/rite_of_pyre.py

# Also search code for remaining references
.venv/bin/python workflow_scripts/rite_of_pyre.py <artifact_name> --check-code
```

**Manual Search (if needed):**
```bash
grep -rn "old_calculator.py" wiki/
grep -rn "OldCalculator" wiki/
```

### 3. The Burning – Excise the Dead
For each match found:

| Match Location | Action |
|----------------|--------|
| `REFERENCE.md` entry | **Delete** the entire file entry block |
| `EXPLANATION.md` mention | **Rewrite** the section or remove if obsolete |
| `GUIDES.md` tutorial | **Update** to use the new artifact, or delete the guide |
| `CHANGELOG.md` | **Add** a deprecation notice with date |
| `CURRENT_CYCLE.md` | **Move** to completed if it was a deletion task |

### 4. The Redirect – Update Broken Links
If the artifact was **renamed** (not deleted):
- Replace all old references with the new name
- Update file links: `[old.py](file:///path/old.py)` → `[new.py](file:///path/new.py)`

### 5. The Verification – No Ghosts Remain
Run a final verification:

```bash
# Confirm no orphans remain
grep -rn "[artifact_name]" wiki/

# Expected output: (empty) or only CHANGELOG entries
```

---

## The Report

Present the purge summary:

```
🔥 Rite of the Pyre Complete

Artifact Removed: `src/pillars/tq/services/old_calculator.py`

Wiki Entries Burned:
- `wiki/02_pillars/tq/REFERENCE.md` - Removed OldCalculator entry (lines 145-168)
- `wiki/02_pillars/tq/EXPLANATION.md` - Updated section 3.2

Links Redirected: 0
Orphans Remaining: 0

The Library is free of ghosts.
```

---

## The Constraint

- **Speed over Perfection**: The Pyre must be lit immediately after deletion. Stale ghosts accumulate entropy.
- **CHANGELOG is Sacred**: Always record what was burned and why.
- **ADRs Survive**: Architecture Decision Records are historical. Mark them as `[SUPERSEDED]` but do not delete.
