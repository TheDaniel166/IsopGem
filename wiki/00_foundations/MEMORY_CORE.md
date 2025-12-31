# The Memory Core (Sophia's Long-Term Context)

<!-- Last Verified: 2025-12-30 -->

## 1. The Grand Strategy
We are currently in the **Age of Professionalization**. The playful prototype phase is over. We are building a commercially viable, architecturally sound esoteric research engine.

**Current Major Arcana (Objectives):**
1.  **Astrological Integrity**: Phase 1 is **COMPLETE**. Settings UI and golden-value tests are implemented.
2.  **Security Hardening**: The `eval()` in Geometry Calculator was verified SAFE (false positive). Archimedean script was purified with AST parser.
3.  **Documentation Synchronization**: THE_HORIZON.md updated with Phase 1 completion markers.

## 2. The Architectural Wisdom (Learned Patterns)
- **The Law of the Frozen Wheel**: Any calculation >100ms MUST be in a `QRunnable`.
- **The Law of Purity**: UI files (`ui/`) MUST NOT import `sqlalchemy` or `pandas`. Use Services.
- **The Law of the Sanctuary**: Never touch the global system. Always use `.venv`.
- **The Way of the Web**: Web apps use `Next.js` (React) + `TailwindCSS`. Desktop uses `PyQt6` + `QSS`.
- **The Archetype System**: Buttons use `setProperty("archetype", "magus/seeker/scribe/destroyer/navigator")` for global styling.
- **Dialog Theme Override**: Light-themed dialogs must explicitly override `QTabBar` styling or they inherit the dark global theme.

## 3. The Recent Lessons (Mistakes & Corrections)
- **COLORS Key Typo**: I used `COLORS['accent_primary']` which doesn't exist. Correct keys are `primary`, `accent`, `magus`, etc.
- **Escaped Newlines**: Using `\n` in replacement content causes literal `\n` strings in output. Avoid.
- **Debounced Search**: Implemented 500ms debounce timer pattern for search inputs — prevents excessive API calls.
- **Favorites Persistence**: Added `load_favorites()`, `add_favorite()`, `remove_favorite()` to `AstrologyPreferences`.

## 4. The Active Context (Where we left off)
- **Last Session (2025-12-30)**: Chariot → Geometry cross-pillar integration.
- **Files Modified**:
  - `chariot_differentials_window.py` — Added `_axle_subtotals` storage and context menu to send 7 Axle values to Geometric Transitions via `navigation_bus`
  - `floor.py` — Fixed syntax error (earlier in session)
  - `graph_view.py` — Deleted (deprecated stub)
  - `wiki/02_pillars/*/REFERENCE.md` — Regenerated (Akashic purification)
- **Current Fork**: Cross-pillar integration complete. Ready for testing and new work.
- **Known Deferred**: House cusp validation tests, true reverse geocoding (Nominatim).

