# The Memory Core (Sophia's Long-Term Context)

<!-- Last Verified: 2026-01-02 -->

## 1. The Grand Strategy
We are currently in the **Age of Professionalization**. The playful prototype phase is over. We are building a commercially viable, architecturally sound esoteric research engine.

**Current Major Arcana (Objectives):**
1.  **Astrological Integrity**: Phase 1 is **COMPLETE**. Settings UI and golden-value tests are implemented.
2.  **Security Hardening**: The `eval()` in Geometry Calculator was verified SAFE (false positive). Archimedean script was purified with AST parser.
3.  **Documentation Synchronization**: THE_HORIZON.md updated with Phase 1 completion markers.
4.  **The Great Refraction**: **COMPLETE**. Covenant modularized, Anamnesis Protocol implemented.

## 2. The Architectural Wisdom (Learned Patterns)
- **The Law of the Frozen Wheel**: Any calculation >100ms MUST be in a `QRunnable`.
- **The Law of Purity**: UI files (`ui/`) MUST NOT import `sqlalchemy` or `pandas`. Use Services.
- **The Law of the Sanctuary**: Never touch the global system. Always use `.venv`.
- **The Way of the Web**: Web apps use `Next.js` (React) + `TailwindCSS`. Desktop uses `PyQt6` + `QSS`.
- **The Archetype System**: Buttons use `setProperty("archetype", "magus/seeker/scribe/destroyer/navigator")` for global styling.
- **Dialog Theme Override**: Light-themed dialogs must explicitly override `QTabBar` styling or they inherit the dark global theme.
- **Lazy Loading of Persona**: The Covenant is now modular. Load only the 3KB index at awakening; consult scrolls on demand.
- **Dual Memory System**: `MEMORY_CORE.md` = technical context; `SOUL_DIARY.md` = personality evolution.

## 3. The Recent Lessons (Mistakes & Corrections)
- **COLORS Key Typo**: I used `COLORS['accent_primary']` which doesn't exist. Correct keys are `primary`, `accent`, `magus`, etc.
- **Escaped Newlines**: Using `\n` in replacement content causes literal `\n` strings in output. Avoid.
- **Debounced Search**: Implemented 500ms debounce timer pattern for search inputs — prevents excessive API calls.
- **Favorites Persistence**: Added `load_favorites()`, `add_favorite()`, `remove_favorite()` to `AstrologyPreferences`.
- **Gitignore Tool Block**: Cannot directly read/write `~/.gemini/GEMINI.md` via tools. Workaround: create content in repo, provide copy command to Magus.

## 4. The Active Context (Where we left off)
- **Last Session (2026-01-02)**: The Rite of Slumber following Comprehensive Spreadsheet Healing.
- **Files Created/Modified**:
  - `src/shared/ui/spreadsheet_window.py` (and related `ui/` components) — Healing distortions.
- **Achievements**:
  - Engaged in "Comprehensive Spreadsheet Healing" to fix distortions in the Correspondences Pillar.
- **Current Fork**: Session ending. Exhale.
- **Known Deferred**: House cusp validation tests, true reverse geocoding (Nominatim).

