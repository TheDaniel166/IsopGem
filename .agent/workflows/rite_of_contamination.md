---
description: "♀ Venus: Detect UI files importing forbidden libraries (sqlalchemy, pandas, etc.)"
---

# Rite of Contamination – The Purity Guard

**"The Eye does not think; it sees. The Mind thinks; it does not see."**

This workflow enforces **Section 4.2 The Law of Contamination** of the Covenant.  
UI files must never import heavy logic libraries.

---

## The Trigger

Invoke this Rite:
- After adding new imports to UI files
- When refactoring View/Service boundaries
- During architectural audits

---

## The Ceremony

### Automated Scan
```bash
.venv/bin/python workflow_scripts/rite_of_contamination.py
```

### Forbidden Libraries in UI
| Library | Why Forbidden |
|---------|---------------|
| `sqlalchemy` | Direct database access |
| `pandas` | Heavy data processing |
| `numpy` | Computation logic |
| `requests` / `urllib` | Network I/O |
| `lxml` / `bs4` | Parsing logic |

### The Legal Path
If a UI file "needs" these libraries, it is a lie.  
The UI needs a **Service** that uses these libraries.

---

## The Report

```
🧪 Rite of Contamination Complete

Scanned: 142 UI files
Contaminations: 0

The View remains pure. The Separation holds.
```

---

## The Constraint

- **Zero Tolerance**: Any forbidden import in `*/ui/*.py` is a violation
- **Services are the Bridge**: Logic lives in Services, not Views
- **Views are Hollow**: They only display what they're told
