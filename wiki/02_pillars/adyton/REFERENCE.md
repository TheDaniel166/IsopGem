# Adyton Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the components of the Inner Sanctuary (Adyton), mapping its bone (models), muscle (services), and skin (UI).

---

**File:** `src/pillars/adyton/ui/adyton_hub.py`

**Role:** `[Skin]` (UI/View)

**Purpose:** The diplomatic entry point for the Sanctuary. It organizes the "Chamber of the Seven Adepts" and provides navigation to the 3D Engine, OpenGL viewports, and specific Planetary Walls.

**The Input (Ingests):**
* `WindowManager` (Object)

**The Output (Emits):**
* None (Orchestrates window spawning)

**Dependencies (It Needs):**
* `shared.ui.WindowManager`
* `pillars.adyton.ui.engine.window.AdytonSanctuaryEngine`
* `pillars.adyton.ui.engine.opengl_viewport.AdytonGLViewport`
* `pillars.adyton.ui.engine.wall_window.AdytonWallWindow`
* `pillars.adyton.services.kamea_loader_service.KameaLoaderService`

**Consumers (Who Needs It):**
* `src/main.py` (IsopGemMainWindow)

**Key Interactions:**
* **Downstream:** Commands the `WindowManager` to launch specialized sanctuary windows.
* **Upstream:** None.

---

**File:** `src/pillars/adyton/services/kamea_loader_service.py`

**Role:** `[Muscle]` (Service)

**Purpose:** Implements the extraction logic for the Kamea of Maut. It parses raw ternary ditrunes from CSV foundations into structured coordinate models, determines Octant IDs, and maps planetary walls to the Zodiacal Heptagon.

**The Input (Ingests):**
* `project_root` (str)
* `Docs/kamea/kamea_maut_ternary - Sheet1.csv` (Raw Data)
* `Docs/adyton_walls/zodiacal_heptagon.csv` (Wall Map)

**The Output (Emits):**
* `Dict[Tuple[int, int], KameaCell]` (The Grid Object)
* `Dict[int, int]` (Value-to-Wall mapping)

**Dependencies (It Needs):**
* `pillars.adyton.models.kamea_cell.KameaCell`

**Consumers (Who Needs It):**
* `src/pillars/adyton/ui/adyton_hub.py`
* `src/pillars/adyton/ui/watchtower_view.py`

**Key Interactions:**
* **Downstream:** Feeds structured `KameaCell` models to the view layer for rendering.
* **Upstream:** Returns data directly; does not fire signals.

---

**File:** `src/pillars/adyton/models/kamea_cell.py`

**Role:** `[Bone]` (Model)

**Purpose:** A crystallized data structure representing a single unit in the Sanctuary. It holds Cartesian coordinates, ternary ditrunes, decimal translations, and Enochian Element markers.

**The Input (Ingests):**
* Primitive types (`int`, `str`)

**The Output (Emits):**
* Immutable `KameaCell` Objects.

**Dependencies (It Needs):**
* `dataclasses.dataclass`

**Consumers (Who Needs It):**
* `src/pillars/adyton/services/kamea_loader_service.py`
* `src/pillars/adyton/ui/watchtower_view.py`
* `src/pillars/adyton/ui/kamea_pyramid_cell.py`

**Key Interactions:**
* **Downstream:** Pure state; no logic triggers.
* **Upstream:** None.
