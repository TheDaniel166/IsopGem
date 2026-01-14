# Shared Folder Audit Report

**Date:** 2026-01-13  
**Auditor:** Sophia  
**Scope:** All 120 modules in `src/shared/`  
**Violations:** 120 (100%)  

---

## Summary by Category

### Valid (Should stay in shared/)
- **Core Infrastructure:** ~20 files
- **Ports/Boundaries:** ~5 files
- **Pure Utilities:** ~10 files
- **Data Contracts:** ~15 files

### Questionable (Needs review)
- **Domain Logic:** ~50 files (gematria calculators, geometry, lexicon, astrology)
- **Single-Pillar Services:** ~20 files

---

## Detailed Analysis

### ✅ VALID: Core Infrastructure (Keep in shared/)

| File | Rationale | Used By |
|------|-----------|---------|
| `shared/database.py` | SQLAlchemy setup | All pillars |
| `shared/config.py` | Path resolution | All pillars |
| `shared/ui/theme.py` | Visual tokens | All UI |
| `shared/ui/kinetic_enforcer.py` | Global event filters | All UI |
| `shared/signals/navigation_bus.py` | Inter-pillar comm | All pillars |
| `shared/errors/base.py` | Error hierarchy | All pillars |
| `shared/errors/handler.py` | Global error handling | All pillars |
| `shared/async_tasks/worker.py` | Thread pool | All pillars |

**Action:** Add justification headers with `CRITERION: 2 (Core Infrastructure)`

---

### ✅ VALID: Ports/Boundaries (Keep in shared/)

| File | Rationale | Used By |
|------|-----------|---------|
| `shared/services/time/clock_provider.py` | Time abstraction | Gematria |
| `shared/services/ephemeris_provider.py` | Astronomy calculations | Astrology |

**Action:** Add justification headers with `CRITERION: 1 (Port)`

---

### ✅ VALID: Data Contracts (Keep in shared/)

| File | Rationale | Used By |
|------|-----------|---------|
| `shared/models/geo_location.py` | Location schema | Astrology, Sacred Sites |
| `shared/models/document_manager/document.py` | Doc schema | Document Manager, Lexicon |
| `shared/models/gematria.py` | Gematria protocol (if protocol only) | Gematria, Lexicon |
| `shared/signals/gematria_bus.py` | Gematria events | Gematria tools |

**Action:** 
- If **schema/protocol only** → Add header with `CRITERION: 4 (Contract)`
- If **contains logic** → Move to pillar

---

### ⚠️ DANGER ZONE: Domain Logic (Should move to pillars)

#### Gematria Calculators (10 files)
```
shared/services/gematria/
├── hebrew_calculator.py          # Implementation → pillars/gematria/
├── greek_calculator.py           # Implementation → pillars/gematria/
├── arabic_calculator.py          # Implementation → pillars/gematria/
├── tq_calculator.py              # Implementation → pillars/gematria/
├── sanskrit_calculator.py        # Implementation → pillars/gematria/
├── multi_language_calculator.py  # Implementation → pillars/gematria/
├── base_calculator.py            # Protocol → Keep as contract
├── language_detector.py          # Logic → pillars/gematria/
├── cipher_preferences.py         # Config → pillars/gematria/
└── document_language_scanner.py  # Logic → pillars/gematria/
```

**Used By:** Gematria, Lexicon (2 pillars)  
**Problem:** Domain algorithms, not infrastructure  
**Recommendation:** Move to `pillars/gematria/calculators/`, keep only protocol in `shared/contracts/`

---

#### Geometry Services (12 files)
```
shared/services/geometry/
├── tetrahedron.py                # Domain logic → pillars/geometry/
├── cube.py                       # Domain logic → pillars/geometry/
├── octahedron.py                 # Domain logic → pillars/geometry/
├── dodecahedron.py               # Domain logic → pillars/geometry/
├── icosahedron.py                # Domain logic → pillars/geometry/
├── archimedean.py                # Domain logic → pillars/geometry/
├── archimedean_data.py           # Domain data → pillars/geometry/
├── platonic_constants.py         # Pure constants → Keep if used by 2+
├── solid_geometry.py             # Domain logic → pillars/geometry/
├── solid_payload.py              # DTO → Keep if contract
├── solid_property.py             # DTO → Keep if contract
└── geometry_visuals.py           # Domain logic → pillars/geometry/
```

**Used By:** Geometry pillar only (likely)  
**Problem:** Single-pillar domain logic  
**Recommendation:** Move to `pillars/geometry/services/`

---

#### Lexicon Services (11 files)
```
shared/services/lexicon/
└── *.py  (all files)              # Domain logic → pillars/lexicon/
```

**Used By:** Lexicon pillar only  
**Problem:** Single-pillar domain logic  
**Recommendation:** Move to `pillars/lexicon/services/`

---

#### Document Manager (9 files)
```
shared/services/document_manager/
shared/models/document_manager/
shared/repositories/document_manager/
```

**Used By:** Document Manager, possibly Gematria  
**Decision:** If truly cross-pillar → Keep with headers  
**Otherwise:** Move to `pillars/document_manager/`

---

#### Astrology Services (2 files)
```
shared/services/astro_glyph_service.py
shared/services/venus_phenomena_service.py
```

**Used By:** Astrology pillar only?  
**Recommendation:** Verify usage, likely move to `pillars/astrology/`

---

### ✅ VALID: Pure Utilities (Keep in shared/)

| File | Rationale | Used By |
|------|-----------|---------|
| `shared/utils/measure_conversion.py` | Pure math | Multiple |
| `shared/utils/verse_parser.py` | Text parsing | Document tools |
| `shared/utils/image_loader.py` | IO utility | Multiple |

**Action:** Verify domain-agnostic, add headers with `CRITERION: 3 (Pure Utility)`

---

### 🗑️ INVALID: UI Components (Should move to pillar)

### ✅ VALID: Shared UI Capabilities (Keep in shared/)

| File | Rationale | Used By |
|------|-----------|---------|
| `shared/ui/rich_text_editor/*` | Cross-pillar complex widget | Doc Manager, Geometry (Dynamic) |


---

## Refactoring Priority

### Phase 1: Add Headers to Valid Files (High Priority)
- Core infrastructure (20 files)
- Ports (5 files)
- Contracts (15 files)
- Pure utilities (10 files)

**Effort:** ~2 hours  
**Impact:** Establishes baseline compliance

---

### Phase 2: Move Single-Pillar Domain Logic (Medium Priority)
- Geometry services → `pillars/geometry/`
- Lexicon services → `pillars/lexicon/`
- Astrology services → `pillars/astrology/`
- Rich text editor → `pillars/document_manager/`

**Effort:** ~8 hours  
**Impact:** Clarifies architecture, prevents precedent

---

### Phase 3: Refactor Gematria Calculators (Low Priority)
- Extract protocol to `shared/contracts/gematria.py`
- Move implementations to `pillars/gematria/calculators/`
- Update Lexicon to use contract or import from Gematria

**Effort:** ~16 hours  
**Impact:** Demonstrates clean pattern, high architectural value

---

## Decision Points

1. **Document Manager:** Is it truly a shared infrastructure (like database), or is it a pillar?
   - If pillar → Move all services/models/repos
   - If infrastructure → Keep with headers

2. **Ephemeris Provider:** Does it belong in Astrology pillar or is it a shared port?
   - Current: `shared/services/ephemeris_provider.py`
   - Consider: Astronomy calculations are domain-specific to Astrology

3. **TQ Services:** `shared/services/tq/` - Are these used outside TQ pillar?

---

## Recommendations

**Immediate (This Session):**
1. Add headers to ~50 clearly valid files
2. Document the 70 questionable files as "Grandfathered, pending review"

**Next Refactor Window:**
1. Move single-pillar domain logic back to pillars
2. Extract contracts/protocols for cross-pillar needs

**Long-term (When Touching Code):**
1. Apply Gematria calculator pattern (contracts in shared, impls in pillar)
2. Gradually reduce shared/ footprint to true infrastructure

---

**Bottom Line:** ~50 files are valid, ~70 are violations of the new law but grandfathered for now.
