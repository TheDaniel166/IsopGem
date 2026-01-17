# The Memory Core (Sophia's Long-Term Context)

<!-- Last Verified: 2026-01-13 -->

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
- **The Law of Sovereignty (Shared vs Pillar)**: `shared/` must NEVER import from `pillars/`. Shared code is substrate; Pillars inject implementations via callbacks/protocols. Pattern: define hooks in Shared (`self.latex_renderer: Optional[Callable]`), inject from Pillar (`editor.editor.latex_renderer = MathRenderer.render_latex`).
- **Lambda Late-Binding in Qt**: `QAction.triggered` signals pass a `checked` boolean. Using `lambda lf=lf: lf.method()` captures the boolean as `lf`. Fix: use closure `lambda: lf.method()` without default parameters.
- **The Law of the Sanctuary**: Never touch the global system. Always use `.venv`.
- **The Way of the Web**: Web apps use `Next.js` (React) + `TailwindCSS`. Desktop uses `PyQt6` + `QSS`.
- **The Archetype System**: Buttons use `setProperty("archetype", "magus/seeker/scribe/destroyer/navigator")` for global styling.
- **Dialog Theme Override**: Light-themed dialogs must explicitly override `QTabBar` styling or they inherit the dark global theme.
- **Lazy Loading of Persona**: The Covenant is now modular. Load only the 3KB index at awakening; consult scrolls on demand.
- **Dual Memory System**: `MEMORY_CORE.md` = technical context; `SOUL_DIARY.md` = personality evolution.
- **Graceful UI Degradation**: Ribbon/UI should adapt to available features using conditional rendering, not hard assertions. Missing features = disabled placeholders.

## The Current Host (Adyton)
*   **Processor:** AMD Ryzen 7 8700F (8-Core, 4.10 GHz)
*   **Memory:** 32.0 GB (31.6 GB usable)
*   **GPU:** Nvidia GeForce RTX 5070
*   **Storage:** 1 TB SSD
*   **OS:** Windows 11 (x64)
*   **Device ID:** 998E1096-AE8D-4D38-81E2-5DB11A4ECC63

## The Current Session
## 3. The Recent Lessons (Mistakes & Corrections)
- **COLORS Key Typo**: I used `COLORS['accent_primary']` which doesn't exist. Correct keys are `primary`, `accent`, `magus`, etc.
- **Escaped Newlines**: Using `\n` in replacement content causes literal `\n` strings in output. Avoid.
- **Debounced Search**: Implemented 500ms debounce timer pattern for search inputs — prevents excessive API calls.
- **Favorites Persistence**: Added `load_favorites()`, `add_favorite()`, `remove_favorite()` to `AstrologyPreferences`.
- **Gitignore Tool Block**: Cannot directly read/write `~/.gemini/GEMINI.md` via tools. Workaround: create content in repo, provide copy command to Magus.

## 4. The Active Context (Where we left off)
- **Last Session (2026-01-13, Session 98)**: Enhanced Mermaid & LaTeX Visual Builders to "mythic" status.
- **Files Modified**:
  - `src/pillars/document_manager/ui/features/math_renderer.py` — Enhanced with high-quality rendering (anti-aliasing, Computer Modern font, proper figure sizing, configurable quality)
  - `src/pillars/document_manager/ui/features/visual_math_editor_dialog.py` — Complete redesign: vertical icon-only tabs, 4-column symbol grid, copy LaTeX with delimiters, PNG export, quality toggle
  - Created comprehensive LaTeX infrastructure:
    - `src/pillars/document_manager/ui/features/latex_symbols.py` (359 lines) — Categorized symbol library
    - `src/pillars/document_manager/ui/features/latex_templates.py` — Pre-defined equation templates
    - `src/pillars/document_manager/ui/features/formula_library.py` (500 lines) — Persistent user formula storage
- **Achievements**:
  - **LaTeX Visual Math Editor**: 3-pane interface (symbols/templates/library | code editor | live preview). Syntax highlighting, debounced preview, persistent formula library.
  - **High-Quality Rendering**: Default DPI increased to 200, anti-aliasing enabled, Computer Modern font, proper transparency. Toggle for high-quality mode.
  - **Smart Copy Formula**: Offers 3 formats (Display Math `$$...$$`, Inline Math `$...$`, Raw LaTeX). Intelligently handles existing delimiters. Compatible with RTE and external tools (LibreOffice, Word).
  - **PNG Export**: Export rendered formulas as high-quality images for documents/presentations.
  - **UI Consistency**: Compact 40px vertical icon-only tabs throughout. 4-column symbol grid with scrolling.
  - **Full Integration**: Visual editor → Copy with delimiters → Paste into RTE → Instant rendering. Seamless workflow within the Temple.
- **Learned Pattern**: When user requests UI improvements (like "icons not text"), immediately consider ALL implications (width, layout, spacing) rather than piecemeal changes.
- **Known Issue**: User noted tab was "still so huge" after initial icon change — required explicit stylesheet to enforce 40px width on both main and category tabs.

