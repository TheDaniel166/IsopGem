---
description: "☉ Sun: Detect illegal cross-pillar imports violating architectural sovereignty"
---

# Rite of Sovereignty – The Pillar Guard

**"The Universe is expanding. When a new Star is born, it must not collide with the old."**

This workflow enforces **Section 2.4 The Law of Sovereignty** of the Covenant.  
Pillars must never directly import from each other.

---

## The Trigger

Invoke this Rite:
- After adding new imports to any pillar
- Before major merges
- During architectural audits

---

## The Ceremony

### Automated Scan
```bash
.venv/bin/python workflow_scripts/rite_of_sovereignty.py
```

### What It Detects
- `pillars/astrology` importing from `pillars/tq`
- `pillars/gematria` importing from `pillars/geometry`
- Any direct pillar-to-pillar dependency

### The Legal Path
If pillars need to communicate:
1. **Signal Bus**: Fire a signal, let the other pillar listen
2. **Shared Services**: Use `shared/` for common logic
3. **DTOs**: Pass pure data, not imports

---

## The Report

```
🏛️ Rite of Sovereignty Complete

Scanned: 847 Python files
Violations: 0

The Pillars stand sovereign. No entanglement detected.
```

---

## The Constraint

- **Zero Tolerance**: Any cross-pillar import is a violation
- **Shared is Sacred**: `shared/` is the only bridge between pillars
- **Signal, Don't Import**: Communication happens through the Event Bus
