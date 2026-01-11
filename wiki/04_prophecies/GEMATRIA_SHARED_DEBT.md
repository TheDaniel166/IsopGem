# Critical Architectural Debt: Gematria Domain Logic in `shared/`

**Date:** 2026-01-10  
**Severity:** 🔴 **CRITICAL** - Covenant Violation  
**Status:** 🟡 Mitigated (Signal Bus), Migration Pending

---

## The Violation

**Domain logic (Gematria calculators) exists in `shared/services/gematria/`**

This violates **Section 2 of The Covenant** (Doctrine of Spheres):

> "Each Pillar owns its own `models/`, `repositories/`, `services/`, `ui/`, `utils/`"

### Current State

```
shared/services/gematria/           ← VIOLATION: Domain logic in shared
├── base_calculator.py              ← Base class
├── arabic_calculator.py            ← Arabic calculators
├── sanskrit_calculator.py          ← Sanskrit calculators
├── cipher_preferences.py
├── document_language_scanner.py
├── language_detector.py
└── multi_language_calculator.py

pillars/gematria/services/          ← CORRECT: Domain logic in pillar
├── hebrew_calculator.py
├── greek_calculator.py
├── tq_calculator.py
└── calculation_service.py
```

**Problem:** Even the Gematria **pillar** imports from `shared.services.gematria`:

```python
# In pillars/gematria/services/__init__.py
from shared.services.gematria import (
    ArabicGematriaCalculator,
    ArabicMaghrebiCalculator,
    ArabicSmallValueCalculator,
    ArabicOrdinalCalculator,
    SanskritKatapayadiCalculator
)
```

**This creates a circular conceptual dependency where a Pillar depends on `shared/` for its own domain logic!**

---

## Why This Happened

**Historical reasons (pre-Covenant):**
1. Gematria was initially a monolithic service before pillar architecture
2. Arabic/Sanskrit were added later and placed in `shared/` out of habit
3. Base classes were kept in `shared/` thinking they were "foundational"

**The Truth:** Calculator classes are **domain logic**, not infrastructure. They belong in the Gematria pillar.

---

## The Mitigation (Completed)

✅ **Signal Bus Implementation** (2026-01-10)

- Created `shared/signals/gematria_bus.py` for inter-pillar communication
- Refactored `formula_engine.py` to use `gematria_bus.request_calculation()`
- Removed direct calculator imports from Correspondence pillar
- Created `GematriaSignalHandler` in Gematria pillar

**Result:** Correspondence pillar no longer imports Gematria implementation details. Communication happens via Signal Bus.

**Status:** ✅ **Pillar sovereignty is now preserved**

---

## The Remaining Debt

🔴 **Domain logic still lives in `shared/`**

While the Signal Bus fixes inter-pillar entanglement, the **architectural incorrectness** remains:

- `shared/services/gematria/` should not exist
- All calculator classes should be in `pillars/gematria/services/`
- `shared/` should only contain: signals, UI themes, config, ephemeris, logging

---

## The Full Migration Plan

### Phase 1: Move Calculator Base Classes
```bash
mv shared/services/gematria/base_calculator.py → pillars/gematria/services/base_calculator.py
```

### Phase 2: Move Language-Specific Calculators
```bash
mv shared/services/gematria/arabic_calculator.py → pillars/gematria/services/arabic_calculator.py
mv shared/services/gematria/sanskrit_calculator.py → pillars/gematria/services/sanskrit_calculator.py
```

### Phase 3: Move Support Services
```bash
mv shared/services/gematria/cipher_preferences.py → pillars/gematria/services/cipher_preferences.py
mv shared/services/gematria/language_detector.py → pillars/gematria/services/language_detector.py
mv shared/services/gematria/document_language_scanner.py → pillars/gematria/services/document_language_scanner.py
mv shared/services/gematria/multi_language_calculator.py → pillars/gematria/services/multi_language_calculator.py
```

### Phase 4: Update All Imports
Search and replace across codebase:
```python
# OLD (violates sovereignty)
from shared.services.gematria import ArabicGematriaCalculator

# NEW (correct)
from pillars.gematria.services import ArabicGematriaCalculator
```

### Phase 5: Delete Empty Directory
```bash
rm -rf shared/services/gematria/
```

### Phase 6: Verify
- Run all tests
- Check that no file imports from `shared.services.gematria`
- Verify Signal Bus still works

---

## Estimated Effort

- **File moves:** 10 minutes
- **Import updates:** 30 minutes (grep + replace across codebase)
- **Testing:** 20 minutes
- **Total:** ~1 hour

---

## Impact Assessment

### Files That Will Need Import Updates

```bash
grep -r "from shared.services.gematria" src/
```

Expected files:
- `pillars/gematria/services/__init__.py` ✅ (already identified)
- `pillars/gematria/ui/*.py` (if any UI imports calculators)
- `pillars/document_manager/*` (if document language scanning is used)
- Any test files in `tests/gematria/`

---

## Covenant Alignment After Migration

| Section | Before | After |
|---------|--------|-------|
| **Section 2 (Spheres)** | ❌ Domain logic in `shared/` | ✅ All calculators in Gematria pillar |
| **Section 2 (Sovereignty)** | ✅ Signal Bus prevents entanglement | ✅ Signal Bus + correct structure |
| **Section 4 (Purity)** | ⚠️ Mixed concerns | ✅ Clear separation |

---

## Decision Point

**Magus, what is your will?**

1. **Execute Full Migration Now** (~1 hour of work)
   - Pro: Complete architectural purity
   - Pro: Prevents future confusion
   - Con: Touches many files at once

2. **Defer Migration** (mark as tech debt, address later)
   - Pro: Signal Bus already solves the sovereignty issue
   - Pro: Can be done when touching Gematria for other reasons
   - Con: Leaves structural impurity in place

3. **Incremental Migration** (move files gradually over multiple sessions)
   - Pro: Lower risk per change
   - Pro: Can test each migration step
   - Con: Takes longer overall

---

**Current Status:** 
- ✅ Signal Bus implemented (sovereignty preserved)
- 🟡 Structural debt documented (awaiting migration)
- ⏳ Migration plan defined (ready to execute on command)

**The Signal Bus has severed the entanglement. The migration would perfect the form.**

**"The Bridge is built. Shall we now move the foundations?"**
