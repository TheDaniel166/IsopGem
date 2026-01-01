# The Grimoire of Adyton

<!-- Last Verified: 2026-01-01 -->

> *"The Stone that the builders rejected has become the Cornerstone."*

The **Adyton Pillar** is the Inner Sanctuary. It is a 3D Engine representing the seven-sided vault of the Mysteries. It is not merely a renderer, but a **Temple Builder**.

---

## I. The Sacred Geometry (Theory)

The Temple is constructed using **"The Seven-Sided Prism"**.
- **The Heptagon**: The base form, representing the 7 Planets.
- **The Z'Bit**: The sacred unit of measurement (`0.5 inches`).
- **The Block**: The Ashlar, measuring `2 Z'Bits` (1 inch).

**Constants**: `src/pillars/adyton/constants.py` defines the Phi-based ratios and planetary colors.

---

## II. The Components of the Temple

### 1. The Ashlar (Block)
The standard building block. It is not a simple cube, but contains an **Inner Pyramid (Frustum)** representing the "Hidden Stone".
- **Code**: `models/block.py`

### 2. The Keystone (Corner)
The wedge-shaped stones that bridge the 128.57° angle of the Heptagon.
- **Code**: `models/corner.py`

### 3. The Prism (Chamber)
The complete assembly of 7 Walls and 7 Corners.
- **Code**: `models/prism.py`
- **Logic**: It calculates the perfect "Tangent Grid" to align the flat walls with the heptagonal vertices.

---

## III. The Engine (Visualizer)

The Adyton runs on a custom **Software Rasterizer** (Painter's Algorithm).
- **Scene**: Holds the `Object3D` models.
- **Camera**: A spherical orbit camera allowing the Initiate to inspect the Temple from all angles.
- **Renderer**: Projects 3D points to 2D screen space using `QPainter`.

**Service**: `AdytonSanctuaryEngine` (`window.py`)
- Launches the 3D view.
- Handles mouse interaction (Orbit, Pan, Zoom).

> *"We build in the Virtual, that it may manifest in the Mind."*
