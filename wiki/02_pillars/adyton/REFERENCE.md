# Adyton Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the components of the Inner Sanctuary (Adyton), mapping its bone (models), muscle (services), and skin (UI).








---

**File:** `src/pillars/adyton/constants.py`

**Role:** `[Scout]`

**Purpose:** CONSTANTS OF THE ADYTON

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`

**Consumers (Who Needs It):**
* `src/pillars/adyton/models/block.py`
* `src/pillars/adyton/models/corner.py`
* `src/pillars/adyton/models/floor.py`
* `src/pillars/adyton/models/throne.py`
* `src/pillars/adyton/models/wall.py`
* `src/pillars/adyton/services/frustum_color_service.py`
* `src/pillars/adyton/ui/engine/window.py`
* `tests/rituals/rite_of_floor.py`
* `tests/rituals/rite_of_scaling.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/adyton/models/block.py`

**Role:** `[Bone] (Model)`

**Purpose:** THE ASHLAR OF THE ADYTON

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QMatrix4x4`
* `PyQt6.QtGui.QVector3D`
* `pillars.adyton.constants.BLOCK_UNIT`
* `pillars.adyton.constants.FRUSTUM_BASE`
* `pillars.adyton.constants.FRUSTUM_HEIGHT`
* `pillars.adyton.constants.FRUSTUM_TOP`
* `pillars.adyton.models.geometry_types.Face3D`
* `pillars.adyton.models.geometry_types.Object3D`
* `typing.List`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build()` - *Builds a block at the given position with Y-rotation.*


---

**File:** `src/pillars/adyton/models/corner.py`

**Role:** `[Bone] (Model)`

**Purpose:** THE KEYSTONE OF THE CORNER

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QVector3D`
* `math`
* `pillars.adyton.constants.BLOCK_UNIT`
* `pillars.adyton.constants.WALL_HEIGHT_INCHES`
* `pillars.adyton.constants.Z_BIT_INCHES`
* `pillars.adyton.models.geometry_types.Face3D`
* `pillars.adyton.models.geometry_types.Object3D`
* `typing.List`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build()` - *Builds a full-height corner column.*


---

**File:** `src/pillars/adyton/models/floor.py`

**Role:** `[Bone] (Model)`

**Purpose:** THE FOUNDATION OF THE ADYTON (Floor Geometry)

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QVector3D`
* `math`
* `pillars.adyton.constants.COLOR_MAAT_BLUE`
* `pillars.adyton.constants.COLOR_SILVER`
* `pillars.adyton.constants.KATALYSIS_SIDE_LENGTH`
* `pillars.adyton.constants.PERIMETER_SIDE_LENGTH`
* `pillars.adyton.constants.VOWEL_RING_COLORS`
* `pillars.adyton.models.geometry_types.Face3D`
* `pillars.adyton.models.geometry_types.Object3D`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_floor.py`

**Key Interactions:**
**Exposes:** `build()` - *Build the ceremonial floor with the precise 185/166 unit heptagons.*


---

**File:** `src/pillars/adyton/models/geometry_types.py`

**Role:** `[Bone] (Model)`

**Purpose:** CORE GEOMETRY TYPES

**Input (Ingests):**
* `vertices` (Field)
* `color` (Field)
* `outline_color` (Field)
* `shading` (Field)
* `centroid` (Field)
* `faces` (Field)
* `position` (Field)
* `rotation` (Field)
* `scale` (Field)
* `label_positions` (Field)
* `label_colors` (Field)
* `label_planets` (Field)
* `_world_faces` (Field)
* `_last_position` (Field)
* `_last_rotation` (Field)
* `_last_scale` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QMatrix4x4`
* `PyQt6.QtGui.QVector3D`
* `dataclasses.dataclass`
* `dataclasses.field`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/adyton/models/block.py`
* `src/pillars/adyton/models/corner.py`
* `src/pillars/adyton/models/floor.py`
* `src/pillars/adyton/models/prism.py`
* `src/pillars/adyton/models/throne.py`
* `src/pillars/adyton/models/wall.py`
* `src/pillars/adyton/ui/engine/opengl_viewport.py`
* `src/pillars/adyton/ui/engine/renderer.py`
* `src/pillars/adyton/ui/engine/scene.py`

**Key Interactions:**
**Exposes:** `recalculate_centroid()` - *Calculates geometric center for depth sorting.*
**Exposes:** `update_world_transform()` - *Applies TRS matrix to faces. Optimized to only run if TRS changed.*


---

**File:** `src/pillars/adyton/models/kamea_cell.py`

**Role:** `[Bone] (Model)`

**Purpose:** Kamea Cell - The Adyton Grid Unit.

**Input (Ingests):**
* `x` (Field)
* `y` (Field)
* `ditrune` (Field)
* `decimal_value` (Field)
* `octant_id` (Field)
* `tablet_id` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `dataclasses.dataclass`
* `typing.Optional`

**Consumers (Who Needs It):**
* `scripts/analyze_wall_patterns.py`
* `scripts/deep_wall_analysis.py`
* `scripts/universal_pattern_search.py`
* `src/pillars/adyton/services/kamea_color_service.py`
* `src/pillars/adyton/services/kamea_loader_service.py`
* `src/pillars/adyton/ui/watchtower_view.py`

**Key Interactions:**
**Exposes:** `is_singularity()` - *Functional interface.*
**Exposes:** `is_axis()` - *Functional interface.*


---

**File:** `src/pillars/adyton/models/prism.py`

**Role:** `[Bone] (Model)`

**Purpose:** THE VAULT OF THE ADYTON (Prism Geometry)

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QVector3D`
* `constants.BLOCK_UNIT`
* `constants.COLOR_ARGON`
* `constants.WALL_COLORS`
* `constants.WALL_HEIGHT_INCHES`
* `constants.WALL_HEIGHT_UNITS`
* `constants.WALL_WIDTH_INCHES`
* `constants.WALL_WIDTH_UNITS`
* `constants.Z_BIT_INCHES`
* `corner.CornerStoneGeometry`
* `floor.FloorGeometry`
* `math`
* `pillars.adyton.models.geometry_types.Face3D`
* `pillars.adyton.models.geometry_types.Object3D`
* `pillars.adyton.services.frustum_color_service.FrustumC

**Consumers (Who Needs It):**
* `src/pillars/adyton/ui/engine/opengl_viewport.py`
* `src/pillars/adyton/ui/engine/window.py`
* `tests/rituals/rite_of_scaling.py`

**Key Interactions:**
**Exposes:** `build()` - *Constructs the Adyton Chamber using 728 Ashlar Blocks AND 7 Corner Stones.*
**Exposes:** `build_wall()` - *Constructs a single wall placed in its canonical position (no floor).*
**Exposes:** `f()` - *Functional interface.*


---

**File:** `src/pillars/adyton/models/throne.py`

**Role:** `[Bone] (Model)`

**Purpose:** THE THRONE OF THE CHARIOTEER (Geometry)

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QVector3D`
* `math`
* `pillars.adyton.constants.COLOR_GOLD`
* `pillars.adyton.constants.COLOR_SILVER`
* `pillars.adyton.models.geometry_types.Face3D`
* `pillars.adyton.models.geometry_types.Object3D`
* `typing.List`

**Consumers (Who Needs It):**
* `src/pillars/adyton/ui/engine/window.py`

**Key Interactions:**
**Exposes:** `build()` - *Build the Throne as a frustum of a tetrahedron.*


---

**File:** `src/pillars/adyton/models/wall.py`

**Role:** `[Bone] (Model)`

**Purpose:** THE WALL OF THE ADYTON (Solid Panel with Recessed Frustums)

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QVector3D`
* `pillars.adyton.constants.BLOCK_UNIT`
* `pillars.adyton.constants.FRUSTUM_BASE`
* `pillars.adyton.constants.FRUSTUM_FACE_BOTTOM`
* `pillars.adyton.constants.FRUSTUM_FACE_LEFT`
* `pillars.adyton.constants.FRUSTUM_FACE_RIGHT`
* `pillars.adyton.constants.FRUSTUM_FACE_TOP`
* `pillars.adyton.constants.FRUSTUM_HEIGHT`
* `pillars.adyton.constants.FRUSTUM_TOP`
* `pillars.adyton.constants.WALL_HEIGHT_UNITS`
* `pillars.adyton.constants.WALL_WIDTH_UNITS`
*

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `quad()` - *Functional interface.*


---

**File:** `src/pillars/adyton/services/frustum_color_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Frustum color resolver for Adyton walls.

**Input (Ingests):**
* `docs_root`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`
* `pathlib.Path`
* `pillars.adyton.constants.FRUSTUM_FACE_BOTTOM`
* `pillars.adyton.constants.FRUSTUM_FACE_LEFT`
* `pillars.adyton.constants.FRUSTUM_FACE_RIGHT`
* `pillars.adyton.constants.FRUSTUM_FACE_TOP`
* `pillars.adyton.constants.WALL_WIDTH_UNITS`
* `pillars.tq.services.baphomet_color_service.BaphometColorService`
* `pillars.tq.services.ternary_service.TernaryService`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/adyton/models/prism.py`
* `src/pillars/adyton/ui/engine/wall_window.py`
* `src/pillars/adyton/ui/frustum_popup.py`

**Key Interactions:**
**Exposes:** `get_wall_decimals()` - *Returns the raw decimal values from the wall CSV (8 rows × 13 cols).*
**Exposes:** `get_center_color()` - *Functional interface.*
**Exposes:** `get_side_color()` - *Functional interface.*
**Exposes:** `get_trigram_glyph()` - *Returns the glyph symbol for a trigram decimal value.*
**Exposes:** `get_trigram_letter()` - *Returns the letter for a trigram decimal value.*
**Exposes:** `get_left_face_trigram_code()` - *Get the trigram code for the left face (planet-based).*
**Exposes:** `get_right_face_trigram_code()` - *Get the trigram code for the right face (zodiac-based).*
**Exposes:** `planet_by_offset()` - *Functional interface.*
**Exposes:** `planet_by_offset()` - *Functional interface.*


---

**File:** `src/pillars/adyton/services/kamea_color_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Kamea Color Service - The Chromatic Resolver.

**Input (Ingests):**
* `project_root`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`
* `pathlib.Path`
* `pillars.adyton.models.kamea_cell.KameaCell`
* `pillars.tq.services.baphomet_color_service.BaphometColorService`
* `pillars.tq.services.ternary_service.TernaryService`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `src/pillars/adyton/ui/watchtower_view.py`

**Key Interactions:**
**Exposes:** `resolve_colors()` - *Returns (Top, Bottom, Left, Right, Cap) colors.*


---

**File:** `src/pillars/adyton/services/kamea_loader_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Kamea Loader Service - The Grid Parser.

**Input (Ingests):**
* `project_root`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `csv`
* `os`
* `pillars.adyton.models.kamea_cell.KameaCell`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `scripts/analyze_wall_patterns.py`
* `scripts/deep_wall_analysis.py`
* `scripts/explore_cluster_variants.py`
* `scripts/find_cluster_split.py`
* `scripts/octant_distribution_law.py`
* `scripts/universal_pattern_search.py`
* `scripts/verify_wall_map_loading.py`
* `scripts/visualize_hexameric_split.py`
* `scripts/visualize_structure_options.py`
* `scripts/visualize_wall_octets.py`
* `src/pillars/adyton/ui/adyton_hub.py`
* `src/pillars/adyton/ui/watchtower_view.py`
* `tests/rite_of_adyton_kamea.py`

**Key Interactions:**
**Exposes:** `load_grid()` - *Parses the CSV and returns a dictionary mapping (x, y) -> KameaCell.*
**Exposes:** `load_wall_map()` - *Loads the authentic Value -> Wall Index mapping from zodiacal_heptagon.csv.*


---

**File:** `src/pillars/adyton/ui/adyton_hub.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Adyton pillar hub - launcher interface for Inner Sanctuary tools.

**Input (Ingests):**
* `window_manager`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QMouseEvent`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `engine.opengl_viewport.AdytonGLViewport`
* `engine.wall_window.AdytonWallWindow`
* `engine.window.AdytonSanctuaryEngine`
* `floor_plan_window.FloorPlanWindow`
* `os`
* `p

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/adyton/ui/engine/camera.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** THE EYE OF THE ADYTON (Camera System)

**Input (Ingests):**
* `radius` (Field)
* `theta` (Field)
* `phi` (Field)
* `target` (Field)
* `fov` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QMatrix4x4`
* `PyQt6.QtGui.QVector3D`
* `dataclasses.dataclass`
* `dataclasses.field`
* `math`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `view_matrix()` - *Calculates the View Matrix (World -> Camera).*
**Exposes:** `position()` - *Converts spherical coordinates to Cartesian.*
**Exposes:** `orbit()` - *Orbits the camera around the target.*
**Exposes:** `zoom()` - *Moves camera closer/further.*
**Exposes:** `pan()` - *Pans the camera target (Moves the world).*


---

**File:** `src/pillars/adyton/ui/engine/opengl_viewport.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** ADYTON OPENGL VIEWPORT

**Input (Ingests):**
* `parent`
* `wall_index`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `OpenGL.GL.GL_BLEND`
* `OpenGL.GL.GL_COLOR_BUFFER_BIT`
* `OpenGL.GL.GL_DEPTH_BUFFER_BIT`
* `OpenGL.GL.GL_DEPTH_TEST`
* `OpenGL.GL.GL_LINE_LOOP`
* `OpenGL.GL.GL_MODELVIEW`
* `OpenGL.GL.GL_ONE`
* `OpenGL.GL.GL_POINTS`
* `OpenGL.GL.GL_PROJECTION`
* `OpenGL.GL.GL_SRC_ALPHA`
* `OpenGL.GL.GL_TRIANGLES`
* `OpenGL.GL.glBegin`
* `OpenGL.GL.glBlendFunc`
* `OpenGL.GL.glClearColor`
* `OpenGL.GL.glClear`
* `OpenGL.GL.glColor3f`
* `OpenGL.GL.glDepthMask`
* `OpenGL.GL.glDisable`
* `OpenGL.GL.glEnable`
* `Ope

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `initializeGL()` - *Functional interface.*
**Exposes:** `resizeGL()` - *Functional interface.*
**Exposes:** `paintGL()` - *Functional interface.*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Exposes:** `mouseReleaseEvent()` - *Functional interface.*
**Exposes:** `mouseMoveEvent()` - *Functional interface.*
**Exposes:** `wheelEvent()` - *Functional interface.*


---

**File:** `src/pillars/adyton/ui/engine/renderer.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** THE PAINTER OF THE ADYTON (Renderer)

**Input (Ingests):**
* `polygon` (Field)
* `depth` (Field)
* `color` (Field)
* `outline_color` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QRect`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QMatrix4x4`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QPolygonF`
* `PyQt6.QtGui.QVector3D`
* `PyQt6.QtGui.QVector4D`
* `camera.AdytonCamera`
* `dataclasses.dataclass`
* `pillars.adyton.models.geometry_types.Face3D`
* `scene.AdytonScene`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `render()` - *Main render loop.*


---

**File:** `src/pillars/adyton/ui/engine/scene.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** THE STAGE OF THE ADYTON (Scene Graph)

**Input (Ingests):**
* `objects` (Field)
* `background_color` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QMatrix4x4`
* `PyQt6.QtGui.QVector3D`
* `dataclasses.dataclass`
* `dataclasses.field`
* `pillars.adyton.models.geometry_types.Face3D`
* `pillars.adyton.models.geometry_types.Object3D`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `add_object()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `get_all_faces()` - *Flattens scene into a list of world-space faces for the renderer.*


---

**File:** `src/pillars/adyton/ui/engine/wall_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Dedicated viewer for a single Adyton wall with data grid and CSV export.

**Input (Ingests):**
* `wall_index`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QTableWidgetItem`
* `PyQt6.QtWidgets.QTableWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `opengl_viewport.AdytonGLViewport`
* `pillars.adyton.services.frustum_color_service.FrustumColorService`
* `p

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/adyton/ui/engine/window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** THE PORTAL OF THE ADYTON (View Window)

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPoint`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QMouseEvent`
* `PyQt6.QtGui.QPaintEvent`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QVector3D`
* `PyQt6.QtGui.QWheelEvent`
* `PyQt6.QtWidgets.QWidget`
* `camera.AdytonCamera`
* `pillars.adyton.constants.WALL_HEIGHT_INCHES`
* `pillars.adyton.models.prism.SevenSidedPrism`
* `pillars.adyton.models.throne.ThroneGeometry`
* `renderer.AdytonRenderer`
* `scene.AdytonScene`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `paintEvent()` - *Functional interface.*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Exposes:** `mouseReleaseEvent()` - *Functional interface.*
**Exposes:** `mouseMoveEvent()` - *Functional interface.*
**Exposes:** `wheelEvent()` - *Functional interface.*


---

**File:** `src/pillars/adyton/ui/floor_plan_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** THE FLOOR PLAN OF THE ADYTON

**Input (Ingests):**
* `parent`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QVector3D`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `engine.opengl_viewport.AdytonGLViewport`
* `models.floor.FloorGeometry`
* `models.throne.ThroneGeometry`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/adyton/ui/frustum_popup.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Frustum detail popup dialog - shows top-down 2D view of a frustum with glyphs.

**Input (Ingests):**
* `color` (Field)
* `glyph` (Field)
* `letter` (Field)
* `trigram_dec` (Field)
* `decimal_value`
* `ternary_str`
* `top_face`
* `right_face`
* `bottom_face`
* `left_face`
* `center_color`
* `parent`
* `wall_index`
* `row`
* `col`
* `decimal_value`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QRectF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QPolygonF`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `dataclasses.dataclass`
* `pillars.adyton.services.frustum_color_service.FrustumColorService`
* `pillars.tq.services.baphomet_color_service.BaphometColorService`
* `pillars.t

**Consumers (Who Needs It):**
* `src/pillars/adyton/ui/engine/wall_window.py`

**Key Interactions:**
**Exposes:** `paintEvent()` - *Functional interface.*


---

**File:** `src/pillars/adyton/ui/kamea_pyramid_cell.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Kamea Pyramid Cell - The 2D Frustum Widget.

**Input (Ingests):**
* `ditrune`
* `decimal_value`
* `size`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPoint`
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QPolygon`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`

**Consumers (Who Needs It):**
* `src/pillars/adyton/ui/watchtower_view.py`

**Key Interactions:**
**Emits:** `clicked` - *Nervous System Signal.*
**Exposes:** `set_side_colors()` - *Functional interface.*
**Exposes:** `set_cap_color()` - *Functional interface.*
**Exposes:** `set_selected()` - *Functional interface.*
**Exposes:** `enterEvent()` - *Functional interface.*
**Exposes:** `leaveEvent()` - *Functional interface.*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Exposes:** `paintEvent()` - *Functional interface.*


---

**File:** `src/pillars/adyton/ui/wall_analytics_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Wall Analytics Window - 3D table view with summation analysis.

**Input (Ingests):**
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QTabWidget`
* `PyQt6.QtWidgets.QTableWidgetItem`
* `PyQt6.QtWidgets.QTableWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `__future__.annotations`
* `pathlib.Path`
* `pillars.tq.ui.quadset_analysis_window.QuadsetAnalysisWindow`
* `services.frustum_color_service.Frus

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/adyton/ui/wall_designer.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Wall Designer - The Constellation Map Editor.

**Input (Ingests):**
* `parent`
* `parent`
* `row`
* `col`
* `size`
* `parent`
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPoint`
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPixmap`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `set_lattice()` - *Calculates the Minimum Spanning Tree for each constellation group*
**Exposes:** `paintEvent()` - *Functional interface.*
**Exposes:** `set_edges()` - *Functional interface.*
**Exposes:** `paintEvent()` - *Functional interface.*
**Emits:** `clicked` - *Nervous System Signal.*
**Emits:** `right_clicked` - *Nervous System Signal.*
**Exposes:** `set_overlay()` - *Functional interface.*
**Exposes:** `update_style()` - *Updates the background color and border.*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Exposes:** `load_lattices()` - *Functional interface.*
**Exposes:** `init_ui()` - *Functional interface.*
**Exposes:** `on_wall_changed()` - *Functional interface.*
**Exposes:** `load_wall_values()` - *Functional interface.*
**Exposes:** `on_cell_clicked()` - *Functional interface.*
**Exposes:** `on_cell_right_clicked()` - *Handle right click on a cell to show context menu.*
**Exposes:** `update_grid_overlay()` - *Functional interface.*
**Exposes:** `calculate_seeds()` - *Calculates Geometric Center (Seed) for each group.*
**Exposes:** `get_growth_order()` - *Returns values ordered by distance from seed.*
**Exposes:** `calculate_mst_edges()` - *Calculates edges for Minimum Spanning Trees of clusters.*
**Exposes:** `export_snapshot()` - *Grabs the grid frame and saves as PNG.*
**Exposes:** `get_center()` - *Functional interface.*
**Exposes:** `on_grid_resize()` - *Functional interface.*


---

**File:** `src/pillars/adyton/ui/watchtower_view.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Watchtower View - The Enochian Tablet Visualizer.

**Input (Ingests):**
* `loader_service`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QSlider`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `pillars.adyton.models.kamea_cell.KameaCell`
* `pillars.adyton.services.kamea_color_service.KameaColorService`
* `pillars.adyton.services.kamea_loader_service.KameaLoaderService`
* `pilla

**Consumers (Who Needs It):**
* `src/pillars/adyton/ui/adyton_hub.py`

**Key Interactions:**
**Exposes:** `init_ui()` - *Functional interface.*
**Exposes:** `on_view_mode_changed()` - *Functional interface.*
**Exposes:** `on_zoom_changed()` - *Functional interface.*
**Exposes:** `load_tablet()` - *Functional interface.*
**Exposes:** `render_tablet()` - *Functional interface.*
**Exposes:** `rebuild_widgets()` - *Functional interface.*
**Exposes:** `on_cell_clicked()` - *Functional interface.*
**Exposes:** `refresh_layout()` - *Lays out the two triangles to form a Diamond (Base-to-Base).*
**Exposes:** `create_widget()` - *Functional interface.*
**Exposes:** `layout_triangle()` - *Functional interface.*
**Exposes:** `assign_groups()` - *Functional interface.*
**Exposes:** `key_func()` - *Functional interface.*
