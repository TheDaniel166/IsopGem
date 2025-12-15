# The Geometry Engine

**"God Geometrizes. We trace the lines of Creation."**

## Architectural Role
The **Geometry Engine** is the **Weaver of Form**. It renders the sacred shapes, from the Vesica Piscis to the Platonic Solids, and calculates their extensive properties (Area, Perimeter, Volume, Surface Area). It serves as the visual manifestation of Number.

## The Core Logic (Services)

### **[archimedean_solids.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/services/archimedean_solids.py)**
*   **Architectural Role**: Sovereign Service (The Solid Builder)
*   **The Purpose**: Calculators for the 13 Archimedean solids.
*   **Key Logic**:
    *   `_order_face_vertices`: Geometric algorithm to ensure face vertices are listed in counter-clockwise order (normal vector calculation) for correct rendering.
    *   **Payload Construction**: Builds `SolidPayload` DTOs containing explicit Vertex/Edge/Face lists.

### **[figurate_3d.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/services/figurate_3d.py)**
*   **Architectural Role**: Service (The Projections)
*   **The Purpose**: Projects 3D figurate numbers (Tetrahedral, Pyramidal) into isometric 2D space.
*   **Key Logic**:
    *   `project_dynamic`: Implements the Isometric Projection Matrix (Rotation + Tilt).
    *   `tetrahedral_points`: Generates points $P(n) = n(n+1)(n+2)/6$.

### **[polygonal_numbers.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/services/polygonal_numbers.py)**
*   **Architectural Role**: Service (The Number Grid)
*   **The Purpose**: The numerological core for calculating Figurate Numbers ($P_n$) and Star Numbers.
*   **Key Logic**:
    *   `generalized_star_number_points`: Uses vector ray-casting to determine points for any $P$-gram star ($P \ge 3$).
    *   `centered_polygonal_points`: Generates concentric rings.

### **The Shape Library (2D)**
A collection of specific shape calculators inheriting from **`[base_shape.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/services/base_shape.py)**.
*   **`[circle_shape.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/services/circle_shape.py)**: Circle logic ($A=\pi r^2$).
*   **`[crescent_shape.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/services/crescent_shape.py)**: Lune/Crescent logic.
*   **`[polygon_shape.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/services/polygon_shape.py)**: Regular $N$-gon logic.
*   **`[square_shape.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/services/square_shape.py)**: Square logic.
*   **`[triangle_shape.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/services/triangle_shape.py)**: Solvers for all triangle types (Equilateral, Isosceles, Scalene, Right).
*   **`[vesica_piscis_shape.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/services/vesica_piscis_shape.py)**: The Mother of Form.
*   **And Others**: `annulus_shape`, `ellipse_shape`, `irregular_polygon_shape`, `quadrilateral_shape`, `rose_curve_shape`.

### **The Solid Library (3D)**
3D calculators inheriting from **`[base_solid.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/services/base_solid.py)**.
*   **Platonic Solids**: `tetrahedron_solid`, `cube_solid`, `octahedron_solid`, `dodecahedron_solid`, `icosahedron_solid`.
*   **Archimedean**: `archimedean_solids`, `regular_prism_solids`, `regular_antiprism_solids`.
*   **Pyramids**: `square_pyramid_solid`, `rectangular_pyramid_solid`, `step_pyramid_solid`, `golden_pyramid_solid`.
*   **Prisms**: `rectangular_prism_solid`, `oblique_prism_solid`.
*   **Exotic**: `tesseract_solid` (4D Hypercube).

## The Presentation Layer (UI)

### **[geometry_hub.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/ui/geometry_hub.py)**
*   **Architectural Role**: View (The Gateway)
*   **The Purpose**: The sovereign entry point for Geometry operations.

### **[geometry_calculator_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/ui/geometry_calculator_window.py)**
*   **Architectural Role**: View (The Measurer)
*   **The Purpose**: The primary interface for 2D shape analysis.
*   **Key Logic**:
    *   **3-Pane Layout**: Property List (Left), Canvas (Center), Results (Right).
    *   `_on_property_changed`: Triggers bidirectional recalculation. If user changes "Area", the "Radius" updates automatically.
*   **Dependencies**: `GeometryScene`, `GeometricShape`.

### **[geometry_scene.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/ui/geometry_scene.py)**
*   **Architectural Role**: View (The Canvas)
*   **The Purpose**: The interactive `QGraphicsScene` for drawing shapes.
*   **Key Logic**:
    *   `mousePressEvent`: Detects clicks on "Dots" (Points of Interest).
    *   **Rendering**: Transforms abstract `Primitive` DTOs (Line, Circle) into `QGraphicsItem`s.

### **[geometry_view.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/ui/geometry_view.py)**
*   **Architectural Role**: View (The Viewport)
*   **The Purpose**: Reusable QGraphicsView wrapper with zoom and pan helpers.

### **[geometry_interaction.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/ui/geometry_interaction.py)**
*   **Architectural Role**: Controller (The Interaction)
*   **The Purpose**: Manages "Connect the Dots" logic.
*   **Key Logic**:
    *   `process_draw_click`: State machine handling the start/end of line drawing between dots.
    *   **Groups**: Manages "Selection Groups" for pattern discovery.

### **[figurate_3d_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/ui/figurate_3d_window.py)**
*   **Architectural Role**: View (The Isometric Projector)
*   **The Purpose**: 3D Figurate Numbers Visualization Window.
*   **Key Logic**:
    *   `eventFilter`: Captures mouse drag to Rotate the Isometric View (Yaw/Pitch).
    *   **Z-Sorting**: Sorts points by depth before painting to handle occlusion.

## Data Structures (Models)

### **[solid_payload.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/shared/solid_payload.py)**
*   **Architectural Role**: DTO (The Blueprint)
*   **The Purpose**: Standardized transport for 3D geometry.
*   **Components**: `vertices` (List[Vec3]), `edges` (List[Tuple]), `faces` (List[List[int]]).

### **[primitives.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/geometry/ui/primitives.py)**
*   **Architectural Role**: DTO (The Drawing)
*   **The Purpose**: Decouples the Service layer from Qt. Services return `CirclePrimitive`, `LinePrimitive` (pure data), which the View converts to `QGraphicsEllipseItem`.
