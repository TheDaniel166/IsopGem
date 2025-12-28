---
description: "☿ Mercury: Run the 7 Planetary Trials verification on a feature or module"
---

# Rite of the Seven Seals – The Planetary Trials

**"As the Seven Spheres govern the Heavens, so shall they judge the Code."**

This workflow enforces **Section 3 The Law of the Seal** of the Covenant.  
A feature is not Complete until the Seven Seals are broken.

---

## The Seven Planets

| Planet | Trial | What It Tests |
|--------|-------|---------------|
| ♄ Saturn | Structure | Circular imports, type hints, `__init__.py` files |
| ♃ Jupiter | Load | Performance under 10,000 rows, O(n²) detection |
| ♂ Mars | Conflict | Error handling, edge cases, `None` attacks |
| ☉ Sun | Truth | Happy path - does it actually work? |
| ♀ Venus | Harmony | API contracts, DTO shapes, type matches |
| ☿ Mercury | Communication | Signals firing, logging output |
| ☾ Moon | Memory | State persistence, save/reload integrity |

---

## The Ceremony

### Full Rite (All Trials)
```bash
.venv/bin/python workflow_scripts/verification_seal.py
```

### Specific Rite (Uncomment in script)
Edit `workflow_scripts/verification_seal.py` and enable the specific `Rite*` class.

### Available Rites
- `RiteOfGematria` - Cipher calculation logic
- `RiteOfGeometry` - Shape calculations, persistence
- `RiteOfAdytonEngine` - 3D rendering pipeline
- `RiteOfEmeraldTablet` - Spreadsheet model and formulas
- `RiteOfFormulaHelper` - Formula validation and search

---

## The Report

```
========================================
THE VERIFICATION SEAL
========================================

--- BEGINNING RITE: GEOMETRY CORE ---
[*] Testing Geometry Pillar...
[+] THE SEAL HOLDS: Circle Calculation (Radius -> Area) verified.
[+] THE SEAL HOLDS: Circle Bidirectional (Area -> Diameter) verified.
[+] THE SEAL HOLDS: Shape Serialization verified.
[+] THE SEAL HOLDS: Geometry Core completed in 12.34ms

The Seals are Broken. The Feature is Born.
```

---

## The Constraint

- **Headless Only**: Logic must be verified without UI
- **Speed Matters**: Each trial should complete in < 100ms
- **Isolation**: Each Rite tests ONE pillar in isolation
