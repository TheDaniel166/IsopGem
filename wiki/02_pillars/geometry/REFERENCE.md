# Geometry Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the Sacred Geometry pillar, mapping the transition from 2D plane logic to 3D solid manifolds.

---

**File:** `src/pillars/geometry/ui/geometry_hub.py`

**Role:** `[Skin]` (UI/View)

**Purpose:** The central navigator for the "Catalyst Array." It organizes geometry tools into 2D (Triangles, Polygons), 3D (Platonic Solids, Antiprisms), and "Esoteric Wisdom" categories.

**The Input (Ingests):**
* `WindowManager` (Object)

**The Output (Emits):**
* None (Orchestrates tool spawning)

**Dependencies (It Needs):**
* `shared.ui.WindowManager`
* `pillars.geometry.ui.ShapePickerDialog`
* `pillars.geometry.ui.geometry3d.window3d.Geometry3DWindow`

**Consumers (Who Needs It):**
* `src/main.py` (IsopGemMainWindow)

**Key Interactions:**
* **Downstream:** Injects shape factories into calculator windows.
* **Upstream:** None.

---

**File:** `src/pillars/geometry/services/solid_geometry.py`

**Role:** `[Muscle]` (Service)

**Purpose:** A library of mathematical utilities for 3D manifold computation. It provides vector arithmetic (dot, cross, normalize), surface area math, volume integrations, and face normal calculations.

**The Input (Ingests):**
* `Vec3` (Float Tuple), `Face` (Int Sequence)

**The Output (Emits):**
* `float` (Area, Volume), `Vec3` (Normal, Centroid)

**Dependencies (It Needs):**
* `math`

**Consumers (Who Needs It):**
* `src/pillars/geometry/ui/geometry3d/` (Multiple Viewports)
* `src/pillars/geometry/services/solid_property.py`

**Key Interactions:**
* **Downstream:** Pure mathematical utility functions.
* **Upstream:** None.

---

**File:** `src/pillars/geometry/shared/solid_payload.py`

**Role:** `[Bone]` (Model)

**Purpose:** The standardized transport object for 3D mesh data. It carries vertices, faces, and normals across the boundary from Service to 3D Viewport.

**The Input (Ingests):**
* Geometry primitives.

**The Output (Emits):**
* `SolidPayload` DTOs.

**Dependencies (It Needs):**
* `dataclasses.dataclass`

**Consumers (Who Needs It):**
* `src/pillars/geometry/services/` (Solid builders)
* `src/pillars/geometry/ui/geometry3d/` (OpenGL renderers)

**Key Interactions:**
* **Downstream:** Serves as the immutable skeleton for 3D rendering packets.
* **Upstream:** None.
