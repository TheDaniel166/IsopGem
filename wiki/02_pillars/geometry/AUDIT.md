# Geometry Pillar: Calculators & Visualizers Audit

**"We trace Form so the Magus may see Number."**

## Scope
This audit covers the interactive calculators and visualizers within the Geometry pillar: the hub launcher, polygonal/centered/star figurate viewers, the 3D figurate viewer, and the shared canvas/view stack (Scene/View/Interaction) that underpins them.

## Strengths (The Harmonies)
- **Rich launcher surface:** [src/pillars/geometry/ui/geometry_hub.py](src/pillars/geometry/ui/geometry_hub.py) presents a clear tool grid with category routing, lowering navigation entropy.
- **Reusable rendering core:** [src/pillars/geometry/ui/geometry_view.py](src/pillars/geometry/ui/geometry_view.py) and [src/pillars/geometry/ui/geometry_scene.py](src/pillars/geometry/ui/geometry_scene.py) centralize zoom/pan, labeling, measurement preview, and snapping; UI windows share this spine instead of duplicating logic.
- **Figurate depth:** [src/pillars/geometry/services/polygonal_numbers.py](src/pillars/geometry/services/polygonal_numbers.py) and [src/pillars/geometry/services/figurate_3d.py](src/pillars/geometry/services/figurate_3d.py) offer broad coverage (polygonal, centered, star numbers; tetrahedral/pyramidal/octahedral/cubic, centered variants, stellated forms) with clean closed-form formulas.
- **Interaction affordances:** Polygonal/Star/3D viewers ([src/pillars/geometry/ui/polygonal_number_window.py](src/pillars/geometry/ui/polygonal_number_window.py), [src/pillars/geometry/ui/experimental_star_window.py](src/pillars/geometry/ui/experimental_star_window.py), [src/pillars/geometry/ui/figurate_3d_window.py](src/pillars/geometry/ui/figurate_3d_window.py)) share group management and connection drawing, enabling exploratory “connect-the-dots” flows.
- **DTO separation:** Geometry services emit lightweight primitives/payloads; UI classes convert them to Qt items, preserving the Doctrine of Purity.

## Weaknesses (Sources of Entropy)
- **Debug noise & duplicate signals:** `print` debugging and a duplicated `measurementChanged` declaration linger in [src/pillars/geometry/ui/geometry_scene.py](src/pillars/geometry/ui/geometry_scene.py), cluttering the event flow and risking signal misuse; logging is absent.
- **State proliferation in monolith:** [src/pillars/geometry/ui/advanced_scientific_calculator_window.py](src/pillars/geometry/ui/advanced_scientific_calculator_window.py) is a 3k+ line monolith combining expression parsing, unit conversion, persistence, and UI, making it difficult to test, extend, or reuse portions inside other calculators.
- **Interaction feedback gaps:** Measurements and selections lack visual breadcrumbs (no hover distances, no undo for connections, limited snap feedback). Rubber-band selection exists, but there is no status bar summary or history of measurements.
- **Performance risk at scale:** High-index figurate renders execute on the UI thread; no progressive rendering or background workers. Large point clouds (star numbers or centered polygons) can stall the main loop and freeze the wheel.
- **Inconsistent theming & axes/grid controls:** The viewers expose label toggles, but axes/grid toggles are inconsistent (e.g., 3D figurate hides axes, star/polygonal keep defaults), producing mismatched visual language.
- **Limited export/sharing surface:** Current viewers do not expose exports (SVG/PNG/JSON payload), nor a sharable permalink/state bundle.

## Immediate Purifications (Low-Risk)
- Replace `print` statements with structured logging and remove duplicate signal declarations in [src/pillars/geometry/ui/geometry_scene.py](src/pillars/geometry/ui/geometry_scene.py); align with The Chronicle.
- Factor measurement state (font/color/area toggle) into a small dataclass and pass through payload or interaction manager to reduce implicit globals.
- Normalize axes/grid/label toggles across Polygonal, Star, and 3D viewers for a consistent Visual Liturgy baseline.
- Add bounds-guard rails to prevent zero-size `fitInView` edge cases (already partially present) and clamp zoom to sane ranges in [src/pillars/geometry/ui/geometry_view.py](src/pillars/geometry/ui/geometry_view.py).

## Structural Refactors (Medium Effort)
- **Calculator modularization:** Split the advanced calculator into submodules (expression engine, unit converter, persistence, UI shell). Expose the conversion engine as a service so geometry tools can reuse it without pulling the entire window.
- **Interaction service:** Extract connection/group state and history into a headless service usable by all viewers; add undo/redo and bounded history to contain entropy.
- **Rendering workers:** Introduce background generation for dense figurate sets (>= few thousand dots) with progress signals; stream payloads in batches to keep the main thread responsive.
- **Test harness:** Add headless seal tests for polygonal/star point generators and 3D figurate projections (value checks, point counts, symmetry invariants) to guard against regressions in formula changes.

## Feature Enhancements (New Stars to Forge)
1. **Net Explorer:** From any solid payload, generate and visualize unfolded nets (multiple candidate layouts) with export to SVG/PDF; pair with dual-solid overlay from [src/pillars/geometry/services/geometry_visuals.py](src/pillars/geometry/services/geometry_visuals.py).
2. **Golden Ratio Analyzer:** Rapid probe for phi relationships in arbitrary shapes—measure edge ratios, highlight near-phi segments, and annotate in-scene.
3. **Measurement Journal:** Persist named measurements and connection graphs; render a right-rail “Akaschic log” with perimeter/area snapshots and deltas between takes.
4. **Parametric Animations:** Animate growth of polygonal/centered/star numbers over time (layer-by-layer), exportable as GIF/MP4; hook into the interaction manager for live drawing during playback.
5. **Data Export Surface:** One-click export of current payload as SVG (2D) or GLB/OBJ (3D), plus JSON for DOT coordinates and connection sets; include a lightweight share code for rehydration.
6. **Adaptive Theming:** A pillar-wide theme selector that propagates to scene/view/controls, ensuring consistent backgrounds, axes, and label palettes across all geometry tools.

## Verification Notes (Rite of the Seven)
- **Saturn:** Add lint/type checks to the geometry UI layer; verify no UI imports seep into services and no duplicate signal wiring remains.
- **Jupiter/Mars:** Stress-test high `n` polygonal and star renders with background workers and ensure UI remains responsive; add graceful cancellation.
- **Sun/Venus:** Unit-test closed-form figurate values against known sequences; validate DTO shapes consumed by scenes/views.
- **Mercury:** Replace `print` debugging with logger emissions; ensure selection/drawing/measurement signals produce structured events for telemetry.
- **Moon:** Persist interaction histories and saved measurement journals to confirm state survives reloads.

## Recommended Sequencing
1. Purify the scene/view logging and signal definitions; standardize toggles and zoom guard rails.
2. Modularize the advanced calculator and extract the conversion engine as a reusable service.
3. Add background generation plus progress UI for dense figurate sets and star numbers.
4. Layer in exports (SVG/JSON for 2D; GLB/OBJ for 3D) and the measurement journal.
5. Build Net Explorer and phi analyzer atop the stabilized scene/view stack.
