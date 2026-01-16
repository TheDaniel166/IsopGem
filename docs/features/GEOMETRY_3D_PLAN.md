# Geometry 3D Engine Blueprint

## Goals
- Introduce a dedicated, reusable 3D rendering widget for geometry solids.
- Keep the 3D stack modular so other pillars can feed solids without duplicating logic.
- Provide orthographic, wireframe-first visuals with a path toward shaded faces later.
- Support robust calculations (surface area, volume, radii, special metrics) alongside visualization.

## High-Level Architecture
```
Geometry Hub → Solid Shape Service → SolidPayload Adapter → Geometry3DWindow
                                               ↓                    ↓
                                    SolidMathEngine         Geometry3DView (widget)
```

### Core Modules
1. **`Geometry3DView` (PyQt widget)**
   - Backed by `QWidget` + `QPainter` or `QOpenGLWidget` (start with software painter for simplicity).
   - Maintains camera state (orthographic projection, rotation quaternion/Euler, pan, zoom).
   - Renders wireframe primitives (vertices, edges, optional faces) with configurable colors.
   - Handles interaction (mouse drag rotate, shift+drag pan, wheel zoom).

2. **`SolidPayload` dataclass**
   - Mirrors 2D `GeometryScenePayload` philosophy.
   - Fields: `vertices: List[Vec3]`, `edges: List[Tuple[int, int]]`, `faces: List[List[int]]`, `bounds`, `labels`, `metadata` (surface area, volume, etc.).
   - Serves as the contract between math services and the widget.

3. **Solid Math Services**
   - Each solid (e.g., `TetrahedronShape`) computes geometric properties + canonical vertex positions.
   - Provide conversion helper `to_solid_payload()` that normalizes orientation/scale for the viewer.
   - Keep calculations in plain Python so they can be unit-tested without PyQt.

4. **Adapter / Window Layer**
   - `Geometry3DWindow` orchestrates UI (toolbar for orthographic axis snaps, reset view, measurement overlays).
   - Accepts a `SolidPayload`, feeds it to `Geometry3DView`, and bridges to metrics panel.

## Rendering Strategy
- **Orthographic Projection:** maintain view matrix (rotation) + projection matrix (scale/zoom). Since it’s orthographic, projection can be simple scale/translate from world to screen.
- **Wireframe First:** draw edges with z-sorting for clarity; optional face fill via painter path.
- **Axes Overlay:** mini triad showing world X/Y/Z to orient users.
- **Future-proofing:** keep renderer abstracted so we can swap to `QOpenGLWidget` (hardware) without changing payloads.

## Interaction Model
- **Rotate:** left-drag, storing yaw/pitch; clamp pitch to avoid gimbal issues.
- **Pan:** middle-drag or left-drag + modifier.
- **Zoom:** wheel scales orthographic size.
- **Snaps:** optional buttons to reset to isometric, top, front, side views.

## Data Flow Example (Tetrahedron)
1. UI requests `TetrahedronShape`.
2. Service validates inputs, computes vertices centered at origin (edge length L).
3. Service builds `SolidPayload` (include edges list, triangular faces, metrics like area, volume, inradius, circumradius).
4. `Geometry3DWindow` receives payload, updates `Geometry3DView`.
5. Widget renders wireframe; metrics panel shows derived values.

## Next Implementation Steps
1. Scaffold `geometry3d` package under `src/pillars/geometry/ui/`:
   - `view3d.py` for the widget.
   - `window3d.py` for hosting UI.
   - `solid_payload.py` for shared dataclasses.
2. Implement math service for tetrahedron under `services/solids/` (or extend existing module).
3. Add integration hook in Geometry Hub to launch the 3D window with a sample tetrahedron.

This blueprint keeps computation, payload definition, and rendering decoupled, ensuring DRY principles across future solids.
