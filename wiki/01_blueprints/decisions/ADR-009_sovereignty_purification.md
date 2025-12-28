# ADR-009: The Great Purification - Resolving Sovereignty Violations

**Status**: Proposed  
**Date**: 2024-12-28  
**Context**: Rite of the Sun detected 58 cross-pillar import violations

---

## Context

The Temple has accumulated architectural debt over the course of rapid feature development. The **Rite of the Sun** (sovereignty audit) revealed **58 violations** of Section 2.4 of the Covenant—the Law of Sovereignty.

### Violation Categories

| Category | Count | Examples |
|----------|-------|----------|
| **UI Navigation** | ~30 | Windows importing other pillar windows for "Send to X" features |
| **Shared Logic** | ~15 | Services importing calculators/utilities from other pillars |
| **Geometry Coupling** | ~8 | TQ pillar importing Platonic solid services |
| **Document Bridge** | ~5 | Multiple pillars importing document repository/editor |

### Root Causes

1. **Legitimate Feature Needs**: Windows genuinely need to open other windows
2. **Missing Shared Layer**: Utilities like `verse_parser` belong in `shared/`
3. **Copy Avoidance**: Geometry solids are complex; copying would create maintenance burden
4. **Convenience Over Architecture**: Quick imports instead of Signal Bus patterns

---

## Decision

We will restore sovereignty through a **three-pronged strategy**:

### 1. Navigation via Signal Bus (UI violations)

Instead of:
```python
from pillars.tq.ui.quadset_analysis_window import QuadsetAnalysisWindow
# ...
self.window_manager.open_window("quadset", QuadsetAnalysisWindow)
```

We use:
```python
from shared.signals import navigation_bus
# ...
navigation_bus.request_window.emit("quadset_analysis", {"initial_value": 42})
```

The WindowManager listens and performs the actual import lazily.

### 2. Relocate Shared Logic (Service violations)

| Current Location | New Location | Reason |
|-----------------|--------------|--------|
| `pillars/gematria/services/*.py` (calculators) | `shared/services/gematria/` | Used by correspondences |
| `pillars/geometry/services/*_solid.py` | `shared/services/geometry/solids/` | Used by TQ |
| `pillars/gematria/utils/verse_parser.py` | `shared/utils/verse_parser.py` | Used by document_manager |
| `pillars/document_manager/repositories/document_repository.py` | Keep, but create signal interface | Used by gematria |

### 3. Shared UI Components

Windows used by multiple pillars become shared:
- `SavedCalculationsWindow` → `shared/ui/saved_calculations_window.py`

---

## Consequences

### Positive
- ✅ Zero cross-pillar imports (Rite of the Sun passes)
- ✅ Pillars can be developed/tested in isolation
- ✅ New pillars can participate via Signal Bus

### Negative
- ⚠️ Larger `shared/` directory
- ⚠️ Some refactoring effort (~2-4 hours)
- ⚠️ Circular dependency risk if `shared/` grows too large

### Mitigations
- Keep `shared/` organized by domain: `shared/services/gematria/`, `shared/services/geometry/`
- Document all shared components in `wiki/00_foundations/SHARED_MANIFEST.md`
- Sentinel script verifies `shared/` never imports from `pillars/`

---

## Implementation Order

1. **Phase 1**: Create Signal-based navigation system
2. **Phase 2**: Relocate geometry solids to `shared/`
3. **Phase 3**: Relocate gematria calculators to `shared/`
4. **Phase 4**: Refactor all UI imports to use navigation signals
5. **Phase 5**: Run Rite of the Sun, verify 0 violations

---

## Verification

```bash
# After each phase
.venv/bin/python workflow_scripts/rite_of_sovereignty.py

# Expected final output
🏛️ Rite of Sovereignty Complete
Scanned: 331 files
Violations: 0
The Pillars stand sovereign. No entanglement detected.
```
