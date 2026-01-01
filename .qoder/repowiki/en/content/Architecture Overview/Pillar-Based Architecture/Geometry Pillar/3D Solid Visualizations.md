# 3D Solid Visualizations

<cite>
**Referenced Files in This Document**   
- [GEOMETRY_3D_PLAN.md](file://Docs/GEOMETRY_3D_PLAN.md)
- [geometry3d/view3d.py](file://src/pillars/geometry/ui/geometry3d/view3d.py)
- [geometry3d/window3d.py](file://src/pillars/geometry/ui/geometry3d/window3d.py)
- [solid_payload.py](file://src/shared/services/geometry/solid_payload.py)
- [tetrahedron.py](file://src/shared/services/geometry/tetrahedron.py)
- [cube.py](file://src/shared/services/geometry/cube.py)
- [geometry_hub.py](file://src/pillars/geometry/ui/geometry_hub.py)
- [geometry_definitions.py](file://src/pillars/geometry/ui/geometry_definitions.py)
- [figurate_3d_window.py](file://src/pillars/geometry/ui/figurate_3d_window.py)
- [geometric_transitions_3d_window.py](file://src/pillars/tq/ui/geometric_transitions_3d_window.py)
- [quadset_analysis_window.py](file://src/pillars/tq/ui/quadset_analysis_window.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [3D Solid Implementations](#3d-solid-implementations)
5. [Visualization Features](#visualization-features)
6. [User Interaction](#user-interaction)
7. [Integration Points](#integration-points)
8. [Conclusion](#conclusion)

## Introduction

The 3D solid visualization system provides a comprehensive framework for rendering and interacting with three-dimensional geometric solids. This system enables users to visualize Platonic and Archimedean solids with detailed mathematical properties, wireframe rendering, and interactive controls. The implementation supports both educational and analytical use cases, allowing users to explore geometric relationships, calculate advanced metrics, and examine dual forms of polyhedra.

The visualization system is designed with modularity in mind, separating mathematical calculations from rendering logic to ensure maintainability and testability. The architecture follows a clean separation of concerns, with dedicated components for mathematical computation, data representation, and user interface rendering.

**Section sources**
- [GEOMETRY_3D_PLAN.md](file://Docs/GEOMETRY_3D_PLAN.md#L1-L65)

## Architecture Overview

The 3D visualization system follows a layered architecture that separates mathematical computation from rendering and user interface concerns. This design enables independent development and testing of mathematical algorithms while providing a flexible rendering framework.

```mermaid
graph TD
GeometryHub[Geometry Hub] --> SolidService[Solid Shape Service]
SolidService --> PayloadAdapter[SolidPayload Adapter]
PayloadAdapter --> Geometry3DWindow[Geometry3DWindow]
PayloadAdapter --> SolidMathEngine[SolidMathEngine]
Geometry3DWindow --> Geometry3DView[Geometry3DView]
Geometry3DView --> CameraState[CameraState]
SolidMathEngine --> tetrahedron[Tetrahedron.py]
SolidMathEngine --> cube[Cube.py]
SolidMathEngine --> dodecahedron[Dodecahedron.py]
SolidMathEngine --> icosahedron[Icosahedron.py]
SolidMathEngine --> octahedron[Octahedron.py]
```

**Diagram sources**
- [GEOMETRY_3D_PLAN.md](file://Docs/GEOMETRY_3D_PLAN.md#L9-L35)
- [geometry3d/window3d.py](file://src/pillars/geometry/ui/geometry3d/window3d.py#L31-L753)
- [geometry3d/view3d.py](file://src/pillars/geometry/ui/geometry3d/view3d.py#L58-L92)

The architecture consists of four main components:

1. **Geometry Hub**: The central controller that manages the creation and display of 3D visualizations, serving as the entry point for users to access different solid types.

2. **Solid Shape Services**: Mathematical engines that compute the geometric properties and vertex positions for each solid type, implemented as pure Python functions for easy testing.

3. **SolidPayload Adapter**: The data contract between mathematical services and the visualization layer, containing vertices, edges, faces, labels, and metadata.

4. **Geometry3DWindow and View**: The user interface components that render the 3D scene and handle user interactions, including camera controls and measurement tools.

This separation ensures that mathematical calculations can be unit-tested independently of the GUI framework, while the visualization components can be developed and refined without affecting the underlying geometry algorithms.

**Section sources**
- [GEOMETRY_3D_PLAN.md](file://Docs/GEOMETRY_3D_PLAN.md#L9-L35)
- [geometry3d/window3d.py](file://src/pillars/geometry/ui/geometry3d/window3d.py#L31-L753)

## Core Components

The 3D visualization system is built around several core components that work together to provide a seamless user experience. These components include the data model, rendering engine, and user interface controls.

### SolidPayload Data Model

The `SolidPayload` class serves as the central data structure for representing 3D solids. It contains all the necessary information to render a solid and display its properties.

```mermaid
classDiagram
class SolidPayload {
+List[Vec3] vertices
+List[Tuple[int, int]] edges
+List[List[int]] faces
+List[SolidLabel] labels
+dict metadata
+List[Optional[Tuple[int, int, int, int]]] face_colors
+Optional[float] suggested_scale
+Optional[SolidPayload] dual
+__init__(vertices, edges, faces, labels, metadata, face_colors, suggested_scale, dual)
+bounds() Optional[Tuple[Vec3, Vec3]]
}
class SolidLabel {
+str text
+Vec3 position
+bool align_center
}
SolidPayload "1" *-- "0..*" SolidLabel : contains
```

**Diagram sources**
- [solid_payload.py](file://src/shared/services/geometry/solid_payload.py#L25-L87)

The `SolidPayload` class includes:

- **Vertices**: A list of 3D coordinates (x, y, z) that define the corners of the solid
- **Edges**: A list of vertex index pairs that define the lines connecting vertices
- **Faces**: A list of vertex index sequences that define the polygonal faces
- **Labels**: Text annotations positioned in 3D space
- **Metadata**: Key-value pairs containing calculated properties like surface area and volume
- **Face Colors**: Optional color definitions for individual faces
- **Suggested Scale**: A hint for appropriate rendering scale
- **Dual**: A reference to the dual solid's payload for visualization

This data structure serves as the contract between the mathematical computation layer and the rendering layer, ensuring consistent data exchange.

### Geometry3DView Rendering Engine

The `Geometry3DView` widget is responsible for rendering 3D solids using orthographic projection. It handles camera controls, wireframe rendering, and user interaction.

```mermaid
classDiagram
class Geometry3DView {
+Optional[SolidPayload] _payload
+float _payload_scale
+CameraState _camera
+Optional[QPoint] _last_mouse_pos
+Optional[str] _interaction_mode
+bool _show_axes
+dict _sphere_visibility
+bool _show_labels
+bool _show_vertices
+bool _show_dual
+bool _measure_mode
+List[int] _selected_vertex_indices
+Optional[int] _apex_vertex_index
+Optional[int] _hovered_vertex_index
+List[QPointF] _last_screen_points
+bool _loop_closed
+__init__(parent)
+set_payload(payload)
+set_camera_state(state)
+toggle_axes()
+toggle_labels()
+toggle_vertices()
+toggle_dual()
+set_measure_mode(enabled)
+paintEvent(event)
+mousePressEvent(event)
+mouseMoveEvent(event)
+wheelEvent(event)
}
class CameraState {
+float distance
+float yaw_deg
+float pitch_deg
+float pan_x
+float pan_y
+rotation_matrix() QMatrix4x4
}
Geometry3DView --> CameraState : uses
```

**Diagram sources**
- [geometry3d/view3d.py](file://src/pillars/geometry/ui/geometry3d/view3d.py#L58-L92)

The rendering engine supports orthographic projection with camera controls for rotation (yaw and pitch), panning, and zooming. It renders wireframe primitives with configurable colors and handles user interactions through mouse events.

### Geometry3DWindow Interface

The `Geometry3DWindow` class provides a complete user interface for 3D solid visualization, combining the rendering view with control panels and property displays.

```mermaid
classDiagram
class Geometry3DWindow {
+Optional[WindowManager] window_manager
+Optional[QWidget] parent
+Geometry3DView _view
+QTabWidget _tab_widget
+QScrollArea _metrics_area
+QScrollArea _calculator_area
+QLineEdit _edge_input
+QPushButton _reset_view_btn
+QPushButton _zoom_in_btn
+QPushButton _zoom_out_btn
+QCheckBox _axes_checkbox
+QCheckBox _labels_checkbox
+QCheckBox _vertices_checkbox
+QCheckBox _dual_checkbox
+QLabel _status_label
+Optional[CubeSolidCalculator] _calculator
+Optional[SolidPayload] _current_payload
+bool _updating_inputs
+dict _property_inputs
+__init__(window_manager, parent)
+set_payload(payload)
+set_calculator(calculator)
+set_solid_context(title, summary)
+_setup_ui()
+_create_control_panel()
+_create_metrics_panel()
+_create_calculator_panel()
+_update_status(payload)
+_update_calculator_from_inputs()
+_update_inputs_from_calculator()
+_show_property_error(error)
+_on_zoom_in()
+_on_zoom_out()
+_on_reset_view()
+_on_axes_toggled()
+_on_labels_toggled()
+_on_vertices_toggled()
+_on_dual_toggled()
+_clear_calculator()
+_clear_layout(layout)
+_format_value(value)
}
Geometry3DWindow --> Geometry3DView : contains
Geometry3DWindow --> CubeSolidCalculator : uses
```

**Diagram sources**
- [geometry3d/window3d.py](file://src/pillars/geometry/ui/geometry3d/window3d.py#L31-L753)

The window provides a comprehensive interface with:

- A main 3D view area for solid visualization
- Control buttons for zoom and reset operations
- Checkboxes to toggle display elements (axes, labels, vertices, dual)
- Tabbed panels for metrics and calculator views
- Status display for current solid information
- Integration with mathematical calculators for bidirectional property editing

**Section sources**
- [geometry3d/view3d.py](file://src/pillars/geometry/ui/geometry3d/view3d.py#L58-L92)
- [geometry3d/window3d.py](file://src/pillars/geometry/ui/geometry3d/window3d.py#L31-L753)
- [solid_payload.py](file://src/shared/services/geometry/solid_payload.py#L25-L87)

## 3D Solid Implementations

The system implements several Platonic solids with comprehensive mathematical properties and visualization capabilities. Each solid type is implemented as a service class that computes geometric properties and generates the corresponding payload.

### Tetrahedron Implementation

The tetrahedron is implemented as an equilateral triangular pyramid with four faces, six edges, and four vertices. The implementation provides comprehensive mathematical properties and bidirectional calculation capabilities.

```mermaid
classDiagram
class TetrahedronMetrics {
+float edge_length
+float height
+float face_area
+float surface_area
+float volume
+float inradius
+float midradius
+float circumradius
+float incircle_circumference
+float midsphere_circumference
+float circumcircle_circumference
+int faces
+int edges
+int vertices
+int face_sides
+int vertex_valence
+float dihedral_angle_deg
+float solid_angle_sr
+float face_inradius
+float face_circumradius
+float insphere_surface_area
+float insphere_volume
+float midsphere_surface_area
+float midsphere_volume
+float circumsphere_surface_area
+float circumsphere_volume
+float sphericity
+float isoperimetric_quotient
+float surface_to_volume_ratio
+float moment_inertia_solid
+float moment_inertia_shell
+float angular_defect_vertex_deg
+float total_angular_defect_deg
+int euler_characteristic
+float packing_density
+int symmetry_group_order
+int rotational_symmetry_order
+str symmetry_group_name
+str dual_solid_name
+float golden_ratio_factor
}
class TetrahedronSolidResult {
+SolidPayload payload
+TetrahedronMetrics metrics
}
class TetrahedronSolidService {
+build(edge_length) TetrahedronSolidResult
+payload(edge_length) SolidPayload
}
class TetrahedronSolidCalculator {
+properties() List[SolidProperty]
+set_property(key, value) bool
+clear()
+payload() Optional[SolidPayload]
+metadata() Dict[str, float]
+metrics() Optional[TetrahedronMetrics]
}
TetrahedronSolidService --> TetrahedronMetrics : creates
TetrahedronSolidService --> SolidPayload : creates
TetrahedronSolidResult --> SolidPayload : contains
TetrahedronSolidResult --> TetrahedronMetrics : contains
TetrahedronSolidCalculator --> SolidProperty : uses
TetrahedronSolidCalculator --> TetrahedronSolidResult : uses
```

**Diagram sources**
- [tetrahedron.py](file://src/shared/services/geometry/tetrahedron.py#L111-L564)

The tetrahedron implementation includes:

- **Canonical Coordinates**: Base vertices centered at the origin with edge length 2√2
- **Comprehensive Metrics**: Surface area, volume, inradius, midradius, circumradius, and advanced properties
- **Bidirectional Calculator**: Allows editing any property and recalculating all others
- **Dual Form**: Automatically generates the dual octahedron for visualization
- **Quality Metrics**: Sphericity, isoperimetric quotient, and surface-to-volume ratio

The implementation uses a base scale for calculations and applies scaling factors to generate solids of any size while maintaining geometric accuracy.

### Cube Implementation

The cube is implemented as a regular hexahedron with eight vertices, twelve edges, and six square faces. Like the tetrahedron, it provides comprehensive mathematical properties and visualization features.

```mermaid
classDiagram
class CubeMetrics {
+float edge_length
+float face_area
+float surface_area
+float volume
+float face_diagonal
+float space_diagonal
+float inradius
+float midradius
+float circumradius
+float incircle_circumference
+float midsphere_circumference
+float circumcircle_circumference
+int faces
+int edges
+int vertices
+int face_sides
+int vertex_valence
+float dihedral_angle_deg
+float solid_angle_sr
+float face_inradius
+float face_circumradius
+float insphere_surface_area
+float insphere_volume
+float midsphere_surface_area
+float midsphere_volume
+float circumsphere_surface_area
+float circumsphere_volume
+float sphericity
+float isoperimetric_quotient
+float surface_to_volume_ratio
+float moment_inertia_solid
+float moment_inertia_shell
+float angular_defect_vertex_deg
+float total_angular_defect_deg
+int euler_characteristic
+float packing_density
+int symmetry_group_order
+int rotational_symmetry_order
+str symmetry_group_name
+str dual_solid_name
+float golden_ratio_factor
}
class CubeSolidResult {
+SolidPayload payload
+CubeMetrics metrics
}
class CubeSolidService {
+build(edge_length) CubeSolidResult
+payload(edge_length) SolidPayload
}
class CubeSolidCalculator {
+properties() List[SolidProperty]
+set_property(key, value) bool
+clear()
+payload() Optional[SolidPayload]
+metadata() Dict[str, float]
+metrics() Optional[CubeMetrics]
}
CubeSolidService --> CubeMetrics : creates
CubeSolidService --> SolidPayload : creates
CubeSolidResult --> SolidPayload : contains
CubeSolidResult --> CubeMetrics : contains
CubeSolidCalculator --> SolidProperty : uses
CubeSolidCalculator --> CubeSolidResult : uses
```

**Diagram sources**
- [cube.py](file://src/shared/services/geometry/cube.py#L127-L618)

The cube implementation includes:

- **Base Vertices**: Eight vertices defined at (±1, ±1, ±1) with appropriate scaling
- **Face Definitions**: Six square faces with proper vertex ordering
- **Edge Calculation**: Automatic generation of edges from face definitions
- **Comprehensive Metrics**: All standard and advanced geometric properties
- **Dual Form**: Automatically generates the dual octahedron
- **Bidirectional Calculator**: Supports editing any property with automatic recalculation

The implementation uses helper functions to compute scaled values based on the edge length, ensuring accurate geometric relationships across different sizes.

### Other Platonic Solids

In addition to the tetrahedron and cube, the system implements other Platonic solids including the octahedron, dodecahedron, and icosahedron. These solids follow the same architectural pattern with dedicated service classes, metrics dataclasses, and calculator implementations.

The system also supports Archimedean solids and various figurate numbers, providing a comprehensive library of 3D geometric forms. Each solid type is accessible through the geometry hub interface, allowing users to explore different geometric relationships and properties.

**Section sources**
- [tetrahedron.py](file://src/shared/services/geometry/tetrahedron.py#L111-L564)
- [cube.py](file://src/shared/services/geometry/cube.py#L127-L618)
- [geometry_definitions.py](file://src/pillars/geometry/ui/geometry_definitions.py#L785-L1005)

## Visualization Features

The 3D visualization system provides several features to enhance the user experience and facilitate geometric exploration.

### Dual Solid Visualization

One of the key features is the ability to visualize the dual of any solid. The dual is generated by computing the centroids of the original solid's faces and connecting adjacent face centroids.

```mermaid
flowchart TD
Primal[Solid Payload] --> ComputeCentroids[Compute Face Centroids]
ComputeCentroids --> DualVertices[Create Dual Vertices]
Primal --> FindAdjacentFaces[Find Adjacent Faces]
FindAdjacentFaces --> DualEdges[Create Dual Edges]
Primal --> MapVertexFaces[Map Vertices to Faces]
MapVertexFaces --> SortFaces[Sort Faces Around Vertex]
SortFaces --> DualFaces[Create Dual Faces]
DualVertices --> FinalPayload[Create Dual SolidPayload]
DualEdges --> FinalPayload
DualFaces --> FinalPayload
FinalPayload --> Display[Display Dual Solid]
```

**Diagram sources**
- [geometry_visuals.py](file://src/shared/services/geometry/geometry_visuals.py#L24-L163)

The dual visualization feature allows users to explore the reciprocal relationships between Platonic solids:
- Tetrahedron is self-dual
- Cube and octahedron are duals
- Dodecahedron and icosahedron are duals

This feature is particularly useful for understanding geometric symmetry and transformation properties.

### Measurement and Analysis Tools

The system includes tools for measuring distances, areas, and volumes in 3D space. Users can select vertices to calculate various geometric properties.

The measurement system supports:
- Distance between two points in 3D space
- Area of polygonal faces
- Volume of the solid
- Angles between edges and faces
- Radii of inscribed and circumscribed spheres

These measurements are calculated using vector mathematics and are displayed in the interface for user reference.

### Quality and Advanced Metrics

The visualization system calculates and displays advanced geometric metrics that provide insight into the properties of each solid:

- **Sphericity**: Measures how closely the solid approximates a sphere
- **Isoperimetric Quotient**: Relates surface area to volume
- **Surface-to-Volume Ratio**: Important for physical applications
- **Moment of Inertia**: Physics properties for rotational dynamics
- **Angular Defect**: Topological property related to curvature
- **Packing Density**: How efficiently the solid fills space

These metrics are valuable for both mathematical analysis and practical applications in physics and engineering.

**Section sources**
- [geometry_visuals.py](file://src/shared/services/geometry/geometry_visuals.py#L24-L163)
- [tetrahedron.py](file://src/shared/services/geometry/tetrahedron.py#L111-L564)
- [cube.py](file://src/shared/services/geometry/cube.py#L127-L618)

## User Interaction

The 3D visualization system provides intuitive user interaction through mouse and keyboard controls.

### Camera Controls

Users can manipulate the camera to view solids from different angles:

- **Rotation**: Left mouse drag rotates the view around the center
- **Panning**: Middle mouse drag or Shift+left drag moves the view
- **Zoom**: Mouse wheel zooms in and out
- **Reset**: Button returns to default view

The camera uses orthographic projection to maintain consistent scaling regardless of distance, which is ideal for geometric analysis.

### Display Toggle Controls

Users can customize the visualization by toggling various display elements:

- **Axes**: Show or hide coordinate axes
- **Labels**: Show or hide text labels
- **Vertices**: Show or hide vertex markers
- **Dual**: Show or hide the dual solid
- **Measurement Mode**: Enable vertex selection for measurements

These controls allow users to focus on specific aspects of the geometry without visual clutter.

### Property Editing

The system includes a bidirectional calculator that allows users to edit any geometric property and see the solid update accordingly. When a user changes a property like volume or surface area, the system recalculates the edge length and updates the visualization.

This feature supports exploratory learning, allowing users to understand how changing one property affects all other properties of the solid.

**Section sources**
- [geometry3d/view3d.py](file://src/pillars/geometry/ui/geometry3d/view3d.py#L58-L92)
- [geometry3d/window3d.py](file://src/pillars/geometry/ui/geometry3d/window3d.py#L31-L753)

## Integration Points

The 3D visualization system integrates with various components throughout the application.

### Geometry Hub Integration

The primary entry point for 3D visualizations is through the Geometry Hub, which provides access to different solid types.

```mermaid
sequenceDiagram
participant User
participant GeometryHub
participant WindowManager
participant Geometry3DWindow
User->>GeometryHub : Select solid type
GeometryHub->>GeometryHub : Lookup configuration
GeometryHub->>WindowManager : Open Geometry3DWindow
WindowManager->>Geometry3DWindow : Create window instance
Geometry3DWindow->>Geometry3DWindow : Set solid context
Geometry3DWindow->>Geometry3DWindow : Set calculator or payload
Geometry3DWindow-->>User : Display 3D visualization
```

**Diagram sources**
- [geometry_hub.py](file://src/pillars/geometry/ui/geometry_hub.py#L388-L421)

The hub uses configuration data to determine which calculator or payload to use for each solid type, providing a consistent interface across different geometric forms.

### Figurate Number Visualization

The system integrates with figurate number visualizations, allowing users to explore 3D number patterns.

```mermaid
flowchart TD
Link[Geometry Link] --> QuadsetAnalysis[Quadset Analysis Window]
QuadsetAnalysis --> HandleLink[_handle_link_activation]
HandleLink --> CheckPrefix{Link starts with geo3d:}
CheckPrefix --> |Yes| ParseLink[Parse shape type and index]
ParseLink --> OpenVisualizer[_open_figurate_3d_window]
OpenVisualizer --> WindowManager[Window Manager]
WindowManager --> Figurate3D[Figurate3DWindow]
Figurate3D --> Display[Display 3D Figurate Number]
```

**Diagram sources**
- [quadset_analysis_window.py](file://src/pillars/tq/ui/quadset_analysis_window.py#L871-L900)
- [figurate_3d_window.py](file://src/pillars/geometry/ui/figurate_3d_window.py#L44-L69)

This integration allows users to visualize mathematical sequences as 3D geometric arrangements, connecting number theory with spatial geometry.

### Geometric Transitions

The system supports visualization of geometric transitions between different solid forms, particularly for Platonic solids.

The `GeometricTransitions3DWindow` provides an interactive interface for exploring how one solid can transform into another, highlighting the geometric relationships and symmetries between different forms.

**Section sources**
- [geometry_hub.py](file://src/pillars/geometry/ui/geometry_hub.py#L388-L421)
- [quadset_analysis_window.py](file://src/pillars/tq/ui/quadset_analysis_window.py#L871-L900)
- [figurate_3d_window.py](file://src/pillars/geometry/ui/figurate_3d_window.py#L44-L69)
- [geometric_transitions_3d_window.py](file://src/pillars/tq/ui/geometric_transitions_3d_window.py#L313-L333)

## Conclusion

The 3D solid visualization system provides a comprehensive framework for exploring geometric solids with mathematical precision and interactive capabilities. By separating mathematical computation from rendering and user interface concerns, the system achieves a clean architecture that is both maintainable and extensible.

Key strengths of the system include:
- Modular design with clear separation of concerns
- Comprehensive mathematical properties for each solid
- Interactive visualization with camera controls
- Dual solid generation and display
- Bidirectional property editing
- Integration with broader mathematical concepts

The system serves as an educational tool for understanding geometric relationships and as an analytical tool for exploring advanced mathematical properties. Its extensible architecture allows for the addition of new solid types and visualization features, making it a valuable component of the overall application.