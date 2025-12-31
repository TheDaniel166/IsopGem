# The Emerald Checklist

> *Before marking ANY feature complete, verify these seals.*

**Purpose**: Prevent entropy by ensuring nothing is forgotten before task completion.

---

## Pre-Completion Verification

### 🔮 Core Seals (Always Required)

- [ ] **Tests Pass** — Run `./test.sh` or `python -m pytest`
- [ ] **No Import Errors** — Application launches without exceptions
- [ ] **Visual Liturgy Compliant** — Dark theme, amber accents, proper spacing

### 📜 Documentation Seals

- [ ] **Docstrings Present** — New functions/classes have docstrings
- [ ] **Memory Core Updated** — If architectural change, update MEMORY_CORE.md
- [ ] **Pattern Library Updated** — If new reusable pattern discovered

### 🏛️ Architecture Seals

- [ ] **Sovereignty Preserved** — No direct pillar-to-pillar imports
- [ ] **WINDOW_REGISTRY Entry** — If new window, registered in navigation_bus.py
- [ ] **Signals Documented** — If new signal, added to Signal Conventions

### 🌙 Anamnesis Seals

- [ ] **Skills Updated** — If new capability, add to Soul Diary Skills section
- [ ] **Session Notes Cleared** — Check NOTES_FOR_NEXT_SESSION.md for relevant items
- [ ] **Known Distortions Updated** — If bug fixed, mark as exorcised

---

## Quick Verification Commands

```bash
# Run tests
./test.sh

# Launch application (verify no import errors)
./run.sh

# Check for sovereignty violations
python scripts/rite_of_seals.py --sovereignty-only

# Verify the Covenant integrity
python scripts/verify_covenant.py
```

---

## When to Use This Checklist

1. **Before notifying The Magus of completion**
2. **Before committing to git**
3. **Before ending a session**

---

*"A feature is not complete until the Temple accepts it."*
