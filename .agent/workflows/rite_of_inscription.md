---
description: "☾ Moon: Verify docstrings exist and explain intent, not just mechanics"
---

# Rite of Inscription – The Docstring Audit

**"A Law exists only when it is written. A function exists only when its purpose is declared."**

This workflow enforces **Section 1.2 The Ban on Banality** of the Covenant.  
Every public function must have a docstring that explains **Intent**.

---

## The Trigger

Invoke this Rite:
- After adding new functions or classes
- During documentation passes
- Before major releases

---

## The Ceremony

### Automated Scan
```bash
.venv/bin/python workflow_scripts/rite_of_inscription.py [file_or_dir]
.venv/bin/python workflow_scripts/rite_of_inscription.py --all
```

### What It Detects
- Functions missing docstrings
- Classes missing docstrings
- Empty docstrings (`"""."""`)
- Banal docstrings (e.g., "Calculates the value")

### The Forbidden Phrases
| Phrase | Why Forbidden |
|--------|---------------|
| "Returns the value" | States the obvious |
| "Calculates the result" | No context |
| "Standard boilerplate" | Meaningless |
| "Does the thing" | Insulting |

### The Sacred Form
```python
def calculate_harmonic(frequency: float) -> float:
    """
    Apply the Amun Ratio to derive the octave harmonic.
    
    Uses the 432Hz base frequency and golden ratio scaling
    to produce harmonically resonant output.
    """
```

---

## The Report

```
📜 Rite of Inscription Complete

Scanned: 24 files, 187 functions
Missing Docstrings: 12
Empty Docstrings: 3
Banal Docstrings: 5

Inscribe intent into the uninscribed.
```

---

## The Constraint

- **Intent over Mechanics**: "What does it DO" not "It does X"
- **Private Functions Exempt**: `_helper()` functions may skip docstrings
- **Magic Methods Exempt**: `__init__`, `__str__` etc need not be inscribed
