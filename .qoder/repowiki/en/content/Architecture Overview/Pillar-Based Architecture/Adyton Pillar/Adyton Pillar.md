# Adyton Pillar

<cite>
**Referenced Files in This Document**   
- [adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)
- [window.py](file://src/pillars/adyton/ui/engine/window.py)
- [scene.py](file://src/pillars/adyton/ui/engine/scene.py)
- [camera.py](file://src/pillars/adyton/ui/engine/camera.py)
- [renderer.py](file://src/pillars/adyton/ui/engine/renderer.py)
- [block.py](file://src/pillars/adyton/models/block.py)
- [corner.py](file://src/pillars/adyton/models/corner.py)
- [prism.py](file://src/pillars/adyton/models/prism.py)
- [geometry_types.py](file://src/pillars/adyton/models/geometry_types.py)
- [constants.py](file://src/pillars/adyton/constants.py)
- [main.py](file://src/main.py)
- [adyton_concept.md](file://Docs/architecture/adyton_concept.md)
- [floor_plan_window.py](file://src/pillars/adyton/ui/floor_plan_window.py)
- [floor.py](file://src/pillars/adyton/models/floor.py)
- [throne.py](file://src/pillars/adyton/models/throne.py)
- [wall_designer.py](file://src/pillars/adyton/ui/wall_designer.py)
- [kamea_pyramid_cell.py](file://src/pillars/adyton/ui/kamea_pyramid_cell.py)
- [kamea_cell.py](file://src/pillars/adyton/models/kamea_cell.py)
- [wall.py](file://src/pillars/adyton/models/wall.py)
- [watchtower_view.py](file://src/pillars/adyton/ui/watchtower_view.py)
</cite>

## Update Summary
**Changes Made**   
- Updated core components to include new visualization tools: throne, floor plan window, kamea pyramid cell, and wall designer
- Added new sections for the throne geometry, floor plan visualization, and wall designer functionality
- Enhanced architectural overview with new component interactions
- Updated detailed component analysis to reflect new UI and model classes
- Added new diagrams for the expanded component structure and data flow

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
The Adyton pillar serves as the 3D inner sanctuary engine within the isopgem application, providing an immersive visualization layer for esoteric geometries and sacred spaces. This architectural documentation details the engine's structure, components, and functionality, focusing on its role as a visualization system for complex mathematical and metaphysical concepts from other pillars of the application. The Adyton functions as a chamber of contemplation and analysis, rendering intricate geometric models that represent spiritual and mathematical principles. Recent updates have enhanced the visualization capabilities with new components including the throne, floor plan window, kamea pyramid cell, and wall designer.

## Project Structure
The Adyton pillar is organized within the src/pillars/adyton directory with a clear separation between models, UI components, and constants. The structure follows a modular design pattern with distinct components for scene management, camera control, rendering, and geometric modeling.

```mermaid
graph TB
subgraph "Adyton Pillar"
subgraph "UI"
subgraph "Engine"
window["window.py<br/>AdytonSanctuaryEngine"]
scene["scene.py<br/>AdytonScene"]
camera["camera.py<br/>AdytonCamera"]
renderer["renderer.py<br/>AdytonRenderer"]
end
hub["adyton_hub.py<br/>AdytonHub"]
floor_plan["floor_plan_window.py<br/>FloorPlanWindow"]
wall_designer["wall_designer.py<br/>WallDesignerWindow"]
watchtower["watchtower_view.py<br/>WatchtowerView"]
end
subgraph "Models"
block["block.py<br/>AshlarGeometry"]
corner["corner.py<br/>CornerStoneGeometry"]
prism["prism.py<br/>SevenSidedPrism"]
floor["floor.py<br/>FloorGeometry"]
throne["throne.py<br/>ThroneGeometry"]
wall["wall.py<br/>WallGeometry"]
kamea_cell["kamea_cell.py<br/>KameaCell"]
end
constants["constants.py"]
end
```

**Diagram sources**
- [adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)
- [window.py](file://src/pillars/adyton/ui/engine/window.py)
- [scene.py](file://src/pillars/adyton/ui/engine/scene.py)
- [camera.py](file://src/pillars/adyton/ui/engine/camera.py)
- [renderer.py](file://src/pillars/adyton/ui/engine/renderer.py)
- [block.py](file://src/pillars/adyton/models/block.py)
- [corner.py](file://src/pillars/adyton/models/corner.py)
- [prism.py](file://src/pillars/adyton/models/prism.py)
- [floor.py](file://src/pillars/adyton/models/floor.py)
- [throne.py](file://src/pillars/adyton/models/throne.py)
- [wall.py](file://src/pillars/adyton/models/wall.py)
- [kamea_cell.py](file://src/pillars/adyton/models/kamea_cell.py)
- [constants.py](file://src/pillars/adyton/constants.py)

**Section sources**
- [adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)
- [window.py](file://src/pillars/adyton/ui/engine/window.py)
- [scene.py](file://src/pillars/adyton/ui/engine/scene.py)
- [camera.py](file://src/pillars/adyton/ui/engine/camera.py)
- [renderer.py](file://src/pillars/adyton/ui/engine/renderer.py)
- [block.py](file://src/pillars/adyton/models/block.py)
- [corner.py](file://src/pillars/adyton/models/corner.py)
- [prism.py](file://src/pillars/adyton/models/prism.py)
- [floor.py](file://src/pillars/adyton/models/floor.py)
- [throne.py](file://src/pillars/adyton/models/throne.py)
- [wall.py](file://src/pillars/adyton/models/wall.py)
- [kamea_cell.py](file://src/pillars/adyton/models/kamea_cell.py)
- [constants.py](file://src/pillars/adyton/constants.py)

## Core Components
The Adyton pillar consists of several core components that work together to create an immersive 3D visualization environment. The adyton_hub serves as the main interface, providing access to the 3D engine. The scene.py module manages the 3D scene graph, camera.py handles viewpoint control, and renderer.py is responsible for visual output. These components work in concert with geometric models (block, corner, prism) that construct the sacred spaces visualized in the engine. Recent updates have expanded the component set to include specialized visualization tools: the throne geometry representing the seat of the adept, the floor plan window for precision foundation visualization, the kamea pyramid cell for 2D representation of truncated pyramids, and the wall designer for constellation map editing.

**Section sources**
- [adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)
- [window.py](file://src/pillars/adyton/ui/engine/window.py)
- [scene.py](file://src/pillars/adyton/ui/engine/scene.py)
- [camera.py](file://src/pillars/adyton/ui/engine/camera.py)
- [renderer.py](file://src/pillars/adyton/ui/engine/renderer.py)
- [block.py](file://src/pillars/adyton/models/block.py)
- [corner.py](file://src/pillars/adyton/models/corner.py)
- [prism.py](file://src/pillars/adyton/models/prism.py)
- [floor.py](file://src/pillars/adyton/models/floor.py)
- [throne.py](file://src/pillars/adyton/models/throne.py)
- [wall.py](file://src/pillars/adyton/models/wall.py)
- [kamea_cell.py](file://src/pillars/adyton/models/kamea_cell.py)
- [wall_designer.py](file://src/pillars/adyton/ui/wall_designer.py)
- [kamea_pyramid_cell.py](file://src/pillars/adyton/ui/kamea_pyramid_cell.py)
- [floor_plan_window.py](file://src/pillars/adyton/ui/floor_plan_window.py)

## Architecture Overview
The Adyton engine follows a classic 3D graphics architecture with distinct components for scene management, camera control, and rendering. The system uses a software rasterization approach with the Painter's Algorithm for depth sorting, implemented through PyQt6's QPainter. The architecture is designed to visualize complex esoteric geometries and sacred spaces, serving as a visualization layer for mathematical and metaphysical concepts from other pillars of the application. Recent updates have expanded the architecture to include specialized visualization tools for different aspects of the sanctuary.

```mermaid
graph TD
hub["AdytonHub<br/>Main Interface"] --> window["AdytonSanctuaryEngine<br/>Viewport"]
hub --> floor_plan["FloorPlanWindow<br/>Precision Foundation"]
hub --> wall_designer["WallDesignerWindow<br/>Constellation Editor"]
hub --> watchtower["WatchtowerView<br/>Enochian Tablet"]
window --> scene["AdytonScene<br/>Scene Graph"]
window --> camera["AdytonCamera<br/>View Control"]
window --> renderer["AdytonRenderer<br/>Software Rasterizer"]
scene --> geometry["Geometric Models<br/>(block, corner, prism, floor, throne)"]
camera --> renderer
scene --> renderer
renderer --> output["Visual Output<br/>3D Sanctuary"]
floor_plan --> floor_geometry["FloorGeometry<br/>Concentric Heptagons"]
floor_plan --> throne_geometry["ThroneGeometry<br/>Truncated Tetrahedron"]
wall_designer --> constellation_grid["ConstellationGrid<br/>Asterism Lines"]
wall_designer --> wall_cells["WallCell<br/>13×8 Grid"]
watchtower --> kamea_cells["KameaPyramidCell<br/>Flattened Truncated Pyramid"]
```

**Diagram sources**
- [adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)
- [window.py](file://src/pillars/adyton/ui/engine/window.py)
- [floor_plan_window.py](file://src/pillars/adyton/ui/floor_plan_window.py)
- [wall_designer.py](file://src/pillars/adyton/ui/wall_designer.py)
- [watchtower_view.py](file://src/pillars/adyton/ui/watchtower_view.py)
- [scene.py](file://src/pillars/adyton/ui/engine/scene.py)
- [camera.py](file://src/pillars/adyton/ui/engine/camera.py)
- [renderer.py](file://src/pillars/adyton/ui/engine/renderer.py)
- [block.py](file://src/pillars/adyton/models/block.py)
- [corner.py](file://src/pillars/adyton/models/corner.py)
- [prism.py](file://src/pillars/adyton/models/prism.py)
- [floor.py](file://src/pillars/adyton/models/floor.py)
- [throne.py](file://src/pillars/adyton/models/throne.py)
- [wall.py](file://src/pillars/adyton/models/wall.py)
- [kamea_cell.py](file://src/pillars/adyton/models/kamea_cell.py)
- [kamea_pyramid_cell.py](file://src/pillars/adyton/ui/kamea_pyramid_cell.py)

## Detailed Component Analysis

### Component A Analysis
The Adyton pillar's components work together to create an immersive visualization environment for esoteric geometries. The system is designed to render sacred spaces based on precise mathematical and metaphysical principles.

#### For Object-Oriented Components:
```mermaid
classDiagram
class AdytonHub {
+window_manager WindowManager
+_setup_ui() void
+_create_action_buttons(layout) void
+_open_sanctuary() void
+_open_floor_plan() void
+_open_wall_designer() void
+_open_watchtowers() void
}
class AdytonSanctuaryEngine {
+scene AdytonScene
+camera AdytonCamera
+renderer AdytonRenderer
+last_pos QPoint
+mouse_pressed bool
+__init__(parent) void
+_init_sanctuary() void
+paintEvent(event) void
+mousePressEvent(event) void
+mouseMoveEvent(event) void
+wheelEvent(event) void
}
class FloorPlanWindow {
+viewport FloorPlanViewport
+_setup_ui() void
}
class FloorPlanViewport {
+scene_objects Object3D[]
+draw_labels bool
+__init__(parent) void
}
class WallDesignerWindow {
+cells WallCell[][]
+planetary_lattices dict
+mythos_data dict
+__init__(window_manager) void
+init_ui() void
+on_wall_changed(wall_name) void
+on_cell_clicked(row, col) void
+on_cell_right_clicked(row, col, global_pos) void
+update_grid_overlay() void
}
class WatchtowerView {
+loader KameaLoaderService
+color_service KameaColorService
+cells_map dict
+current_tablet_cells KameaCell[]
+current_octants int[]
+__init__(loader_service) void
+init_ui() void
+load_tablet(tablet_name) void
+render_tablet(cells, octants) void
+rebuild_widgets() void
+refresh_layout() void
}
class AdytonScene {
+objects Object3D[]
+background_color QColor
+add_object(obj) void
+clear() void
+get_all_faces() Face3D[]
}
class AdytonCamera {
+radius float
+theta float
+phi float
+target QVector3D
+fov float
+view_matrix() QMatrix4x4
+position() QVector3D
+orbit(d_phi, d_theta) void
+zoom(delta) void
+pan(dx, dy) void
}
class AdytonRenderer {
+render(painter, scene, camera, viewport) void
}
class Object3D {
+faces Face3D[]
+position QVector3D
+rotation QVector3D
+scale QVector3D
+_world_faces Face3D[]
+update_world_transform() void
}
class Face3D {
+vertices QVector3D[]
+color QColor
+outline_color QColor
+centroid QVector3D
+recalculate_centroid() void
}
AdytonHub --> AdytonSanctuaryEngine : "launches"
AdytonHub --> FloorPlanWindow : "launches"
AdytonHub --> WallDesignerWindow : "launches"
AdytonHub --> WatchtowerView : "launches"
AdytonSanctuaryEngine --> AdytonScene : "contains"
AdytonSanctuaryEngine --> AdytonCamera : "controls"
AdytonSanctuaryEngine --> AdytonRenderer : "uses"
FloorPlanWindow --> FloorPlanViewport : "contains"
FloorPlanViewport --> AdytonScene : "extends"
FloorPlanViewport --> AdytonCamera : "controls"
FloorPlanViewport --> AdytonRenderer : "uses"
WallDesignerWindow --> ConstellationGrid : "contains"
WallDesignerWindow --> WallCell : "contains"
WatchtowerView --> KameaPyramidCell : "contains"
AdytonRenderer --> AdytonScene : "renders"
AdytonRenderer --> AdytonCamera : "uses"
AdytonScene --> Object3D : "contains"
Object3D --> Face3D : "contains"
```

**Diagram sources**
- [adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)
- [window.py](file://src/pillars/adyton/ui/engine/window.py)
- [floor_plan_window.py](file://src/pillars/adyton/ui/floor_plan_window.py)
- [wall_designer.py](file://src/pillars/adyton/ui/wall_designer.py)
- [watchtower_view.py](file://src/pillars/adyton/ui/watchtower_view.py)
- [scene.py](file://src/pillars/adyton/ui/engine/scene.py)
- [camera.py](file://src/pillars/adyton/ui/engine/camera.py)
- [renderer.py](file://src/pillars/adyton/ui/engine/renderer.py)
- [geometry_types.py](file://src/pillars/adyton/models/geometry_types.py)

#### For API/Service Components:
```mermaid
sequenceDiagram
participant User as "User"
participant Hub as "AdytonHub"
participant Engine as "AdytonSanctuaryEngine"
participant FloorPlan as "FloorPlanWindow"
participant WallDesigner as "WallDesignerWindow"
participant Watchtower as "WatchtowerView"
participant Scene as "AdytonScene"
participant Camera as "AdytonCamera"
participant Renderer as "AdytonRenderer"
User->>Hub : Clicks "Enter the Adyton"
Hub->>Engine : Launches AdytonSanctuaryEngine
Engine->>Scene : Initialize with SevenSidedPrism
Engine->>Camera : Set initial position and target
loop Render Loop
User->>Engine : Mouse movement
Engine->>Camera : Update orbit/pan based on input
Engine->>Renderer : Request render
Renderer->>Scene : Get all faces
Renderer->>Camera : Get view and projection matrices
Renderer->>Object3D : Update world transforms
Renderer->>Face3D : Project to screen coordinates
Renderer->>Face3D : Sort by depth (Painter's Algorithm)
Renderer->>Engine : Draw polygons
Engine->>User : Display rendered scene
end
User->>Hub : Clicks "Floor Plan"
Hub->>FloorPlan : Launches FloorPlanWindow
FloorPlan->>FloorPlanViewport : Initialize with FloorGeometry
FloorPlan->>FloorPlanViewport : Add ThroneGeometry
FloorPlan->>FloorPlanViewport : Set top-down camera
User->>Hub : Clicks "Constellations"
Hub->>WallDesigner : Launches WallDesignerWindow
WallDesigner->>WallDesigner : Load planetary lattices
WallDesigner->>WallDesigner : Load mythos data
WallDesigner->>ConstellationGrid : Calculate MST for asterism lines
User->>Hub : Clicks "Watchtowers"
Hub->>Watchtower : Launches WatchtowerView
Watchtower->>KameaLoaderService : Load Kamea grid
Watchtower->>KameaColorService : Resolve cell colors
Watchtower->>KameaPyramidCell : Render flattened pyramids
```

**Diagram sources**
- [adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)
- [window.py](file://src/pillars/adyton/ui/engine/window.py)
- [floor_plan_window.py](file://src/pillars/adyton/ui/floor_plan_window.py)
- [wall_designer.py](file://src/pillars/adyton/ui/wall_designer.py)
- [watchtower_view.py](file://src/pillars/adyton/ui/watchtower_view.py)
- [scene.py](file://src/pillars/adyton/ui/engine/scene.py)
- [camera.py](file://src/pillars/adyton/ui/engine/camera.py)
- [renderer.py](file://src/pillars/adyton/ui/engine/renderer.py)

#### For Complex Logic Components:
```mermaid
flowchart TD
Start([Application Start]) --> Hub["AdytonHub\nMain Interface"]
Hub --> Launch["User clicks\n'Enter the Adyton'"]
Launch --> Engine["AdytonSanctuaryEngine\nInitialize Components"]
Engine --> SceneInit["Initialize AdytonScene"]
Engine --> CameraInit["Initialize AdytonCamera"]
Engine --> RendererInit["Initialize AdytonRenderer"]
Engine --> Geometry["Build SevenSidedPrism\n728 Ashlar Blocks + 7 Corner Stones"]
Geometry --> Scene["Add objects to scene"]
Engine --> Throne["Build ThroneGeometry\nTruncated Tetrahedron"]
Throne --> Scene["Add throne to scene"]
Engine --> RenderLoop["Enter Render Loop"]
subgraph "Render Loop"
RenderLoop --> InputCheck["Check for User Input"]
InputCheck --> MouseInput{"Mouse Input?"}
MouseInput --> |Yes| HandleMouse["Handle Mouse Movement\n(Orbit/Pan)"]
MouseInput --> |No| CheckWheel{"Wheel Input?"}
CheckWheel --> |Yes| HandleZoom["Handle Zoom"]
CheckWheel --> |No| ContinueRender
ContinueRender --> PrepareRender["Prepare for Rendering"]
PrepareRender --> GetFaces["Scene.get_all_faces()"]
PrepareRender --> UpdateTransforms["Object3D.update_world_transform()"]
PrepareRender --> GetMatrices["Camera.view_matrix()\nRenderer.projection_matrix"]
GetMatrices --> ProjectFaces["Project Faces to Screen"]
ProjectFaces --> ClipFaces["Clip Faces to View Frustum"]
ClipFaces --> SortFaces["Sort by Depth\n(Painter's Algorithm)"]
SortFaces --> DrawFaces["Draw Polygons in Order"]
DrawFaces --> Display["Display Rendered Frame"]
Display --> InputCheck
end
Hub --> FloorPlan["User clicks\n'Floor Plan'"]
FloorPlan --> FloorPlanWin["FloorPlanWindow\nInitialize"]
FloorPlanWin --> FloorPlanViewport["FloorPlanViewport\nInitialize"]
FloorPlanViewport --> FloorGeo["FloorGeometry.build()"]
FloorPlanViewport --> ThroneGeo["ThroneGeometry.build()"]
FloorPlanViewport --> CameraSetup["Set top-down camera"]
Hub --> WallDesigner["User clicks\n'Constellations'"]
WallDesigner --> WallDesignerWin["WallDesignerWindow\nInitialize"]
WallDesignerWin --> LoadLattices["Load planetary_lattices.json"]
WallDesignerWin --> LoadMythos["Load constellation_mythos.json"]
WallDesignerWin --> InitUI["Initialize UI with 13×8 grid"]
Hub --> Watchtower["User clicks\n'Watchtowers'"]
Watchtower --> WatchtowerWin["WatchtowerView\nInitialize"]
WatchtowerWin --> LoadKamea["KameaLoaderService.load_grid()"]
WatchtowerWin --> InitColor["KameaColorService.resolve_colors()"]
WatchtowerWin --> RenderCells["Render 156 KameaPyramidCells"]
```

**Diagram sources**
- [adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)
- [window.py](file://src/pillars/adyton/ui/engine/window.py)
- [floor_plan_window.py](file://src/pillars/adyton/ui/floor_plan_window.py)
- [wall_designer.py](file://src/pillars/adyton/ui/wall_designer.py)
- [watchtower_view.py](file://src/pillars/adyton/ui/watchtower_view.py)
- [scene.py](file://src/pillars/adyton/ui/engine/scene.py)
- [camera.py](file://src/pillars/adyton/ui/engine/camera.py)
- [renderer.py](file://src/pillars/adyton/ui/engine/renderer.py)
- [prism.py](file://src/pillars/adyton/models/prism.py)
- [floor.py](file://src/pillars/adyton/models/floor.py)
- [throne.py](file://src/pillars/adyton/models/throne.py)

### Geometric Models
The Adyton pillar utilizes specific geometric models to construct sacred spaces based on esoteric principles. These models include the Ashlar block, Corner stone, Seven-Sided Prism, Floor, and Throne that form the complete sanctuary.

```mermaid
classDiagram
class AshlarGeometry {
+build(position, rotation_y, color) Object3D
}
class CornerStoneGeometry {
+build(position, rotation_y, color, height) Object3D
}
class SevenSidedPrism {
+build(center) Object3D[]
}
class FloorGeometry {
+build(ring_colors) Object3D
}
class ThroneGeometry {
+build(height, base_side, y_offset) Object3D
}
class WallGeometry {
+build(color, wall_index, center_color_fn, side_color_fn) Object3D
}
class KameaCell {
+x int
+y int
+ditrune str
+decimal_value int
+octant_id int
+tablet_id str
+is_singularity bool
+is_axis bool
}
class Object3D {
+faces Face3D[]
+position QVector3D
+rotation QVector3D
+scale QVector3D
+_world_faces Face3D[]
+update_world_transform() void
}
AshlarGeometry --> Object3D : "returns"
CornerStoneGeometry --> Object3D : "returns"
SevenSidedPrism --> Object3D : "returns multiple"
FloorGeometry --> Object3D : "returns"
ThroneGeometry --> Object3D : "returns"
WallGeometry --> Object3D : "returns"
SevenSidedPrism --> AshlarGeometry : "uses"
SevenSidedPrism --> CornerStoneGeometry : "uses"
SevenSidedPrism --> FloorGeometry : "uses"
```

**Diagram sources**
- [block.py](file://src/pillars/adyton/models/block.py)
- [corner.py](file://src/pillars/adyton/models/corner.py)
- [prism.py](file://src/pillars/adyton/models/prism.py)
- [floor.py](file://src/pillars/adyton/models/floor.py)
- [throne.py](file://src/pillars/adyton/models/throne.py)
- [wall.py](file://src/pillars/adyton/models/wall.py)
- [kamea_cell.py](file://src/pillars/adyton/models/kamea_cell.py)
- [geometry_types.py](file://src/pillars/adyton/models/geometry_types.py)

**Section sources**
- [block.py](file://src/pillars/adyton/models/block.py)
- [corner.py](file://src/pillars/adyton/models/corner.py)
- [prism.py](file://src/pillars/adyton/models/prism.py)
- [floor.py](file://src/pillars/adyton/models/floor.py)
- [throne.py](file://src/pillars/adyton/models/throne.py)
- [wall.py](file://src/pillars/adyton/models/wall.py)
- [kamea_cell.py](file://src/pillars/adyton/models/kamea_cell.py)
- [constants.py](file://src/pillars/adyton/constants.py)
- [adyton_concept.md](file://Docs/architecture/adyton_concept.md)

### New Component: Floor Plan Window
The FloorPlanWindow provides a dedicated viewport for visualizing the precision foundation of the Adyton sanctuary. It displays the concentric heptagonal floor with the central throne, offering a top-down view of the sacred geometry.

```mermaid
classDiagram
class FloorPlanWindow {
+viewport FloorPlanViewport
+__init__(parent) void
+_setup_ui() void
}
class FloorPlanViewport {
+scene_objects Object3D[]
+draw_labels bool
+__init__(parent) void
}
FloorPlanWindow --> FloorPlanViewport : "contains"
FloorPlanViewport --> FloorGeometry : "uses"
FloorPlanViewport --> ThroneGeometry : "uses"
FloorPlanViewport --> AdytonGLViewport : "extends"
```

**Diagram sources**
- [floor_plan_window.py](file://src/pillars/adyton/ui/floor_plan_window.py)
- [floor.py](file://src/pillars/adyton/models/floor.py)
- [throne.py](file://src/pillars/adyton/models/throne.py)
- [opengl_viewport.py](file://src/pillars/adyton/ui/engine/opengl_viewport.py)

**Section sources**
- [floor_plan_window.py](file://src/pillars/adyton/ui/floor_plan_window.py)
- [floor.py](file://src/pillars/adyton/models/floor.py)
- [throne.py](file://src/pillars/adyton/models/throne.py)

### New Component: Wall Designer
The WallDesignerWindow enables users to visualize and interact with planetary wall grids, displaying constellation patterns and providing detailed information about each constellation.

```mermaid
classDiagram
class WallDesignerWindow {
+cells WallCell[][]
+planetary_lattices dict
+mythos_data dict
+__init__(window_manager) void
+init_ui() void
+on_wall_changed(wall_name) void
+on_cell_clicked(row, col) void
+on_cell_right_clicked(row, col, global_pos) void
+update_grid_overlay() void
}
class ConstellationGrid {
+lattice list
+mst_edges list
+set_lattice(lattice, cells_layout_list) void
}
class AsterismOverlay {
+mst_edges list
+set_edges(edges) void
}
class WallCell {
+row int
+col int
+value int
+overlay_tint QColor
+group_id int
+is_seed bool
+set_overlay(group_id, tint_color, is_seed) void
+update_style() void
}
WallDesignerWindow --> ConstellationGrid : "contains"
WallDesignerWindow --> AsterismOverlay : "contains"
WallDesignerWindow --> WallCell : "contains multiple"
ConstellationGrid --> AsterismOverlay : "updates"
```

**Diagram sources**
- [wall_designer.py](file://src/pillars/adyton/ui/wall_designer.py)
- [wall.py](file://src/pillars/adyton/models/wall.py)

**Section sources**
- [wall_designer.py](file://src/pillars/adyton/ui/wall_designer.py)
- [wall.py](file://src/pillars/adyton/models/wall.py)

### New Component: Kamea Pyramid Cell
The KameaPyramidCell represents a 2D visualization of a flattened truncated pyramid, used to display cells in the Enochian watchtowers and kamea grids.

```mermaid
classDiagram
class KameaPyramidCell {
+ditrune str
+decimal_value int
+color_base QColor
+color_cap QColor
+color_top QColor
+color_bottom QColor
+color_left QColor
+color_right QColor
+is_hovered bool
+is_selected bool
+__init__(ditrune, decimal_value, size, parent) void
+set_side_colors(top, bottom, left, right) void
+set_cap_color(color) void
+set_selected(selected) void
+paintEvent(event) void
}
KameaPyramidCell --> QWidget : "extends"
```

**Diagram sources**
- [kamea_pyramid_cell.py](file://src/pillars/adyton/ui/kamea_pyramid_cell.py)

**Section sources**
- [kamea_pyramid_cell.py](file://src/pillars/adyton/ui/kamea_pyramid_cell.py)
- [kamea_cell.py](file://src/pillars/adyton/models/kamea_cell.py)

## Dependency Analysis
The Adyton pillar has a well-defined dependency structure with clear relationships between components. The system follows a layered architecture where higher-level components depend on lower-level ones without circular dependencies.

```mermaid
graph TD
hub["adyton_hub.py"] --> window["engine/window.py"]
hub --> floor_plan["ui/floor_plan_window.py"]
hub --> wall_designer["ui/wall_designer.py"]
hub --> watchtower["ui/watchtower_view.py"]
window --> scene["engine/scene.py"]
window --> camera["engine/camera.py"]
window --> renderer["engine/renderer.py"]
window --> prism["models/prism.py"]
window --> throne["models/throne.py"]
window --> constants["constants.py"]
floor_plan --> opengl_viewport["engine/opengl_viewport.py"]
floor_plan --> floor["models/floor.py"]
floor_plan --> throne["models/throne.py"]
wall_designer --> wall_cell["ui/wall_cell.py"]
wall_designer --> constellation_grid["ui/constellation_grid.py"]
wall_designer --> asterism_overlay["ui/asterism_overlay.py"]
watchtower --> kamea_loader["services/kamea_loader_service.py"]
watchtower --> kamea_color["services/kamea_color_service.py"]
watchtower --> kamea_pyramid_cell["ui/kamea_pyramid_cell.py"]
watchtower --> kamea_cell["models/kamea_cell.py"]
scene --> geometry_types["models/geometry_types.py"]
camera --> geometry_types
renderer --> scene
renderer --> camera
renderer --> geometry_types
block --> geometry_types
block --> constants
corner --> geometry_types
corner --> constants
prism --> block
prism --> corner
prism --> floor
prism --> constants
floor --> geometry_types
floor --> constants
throne --> geometry_types
throne --> constants
wall --> geometry_types
wall --> constants
main["main.py"] --> hub
```

**Diagram sources**
- [adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)
- [window.py](file://src/pillars/adyton/ui/engine/window.py)
- [floor_plan_window.py](file://src/pillars/adyton/ui/floor_plan_window.py)
- [wall_designer.py](file://src/pillars/adyton/ui/wall_designer.py)
- [watchtower_view.py](file://src/pillars/adyton/ui/watchtower_view.py)
- [scene.py](file://src/pillars/adyton/ui/engine/scene.py)
- [camera.py](file://src/pillars/adyton/ui/engine/camera.py)
- [renderer.py](file://src/pillars/adyton/ui/engine/renderer.py)
- [block.py](file://src/pillars/adyton/models/block.py)
- [corner.py](file://src/pillars/adyton/models/corner.py)
- [prism.py](file://src/pillars/adyton/models/prism.py)
- [floor.py](file://src/pillars/adyton/models/floor.py)
- [throne.py](file://src/pillars/adyton/models/throne.py)
- [wall.py](file://src/pillars/adyton/models/wall.py)
- [kamea_cell.py](file://src/pillars/adyton/models/kamea_cell.py)
- [kamea_pyramid_cell.py](file://src/pillars/adyton/ui/kamea_pyramid_cell.py)
- [geometry_types.py](file://src/pillars/adyton/models/geometry_types.py)
- [constants.py](file://src/pillars/adyton/constants.py)
- [main.py](file://src/main.py)

**Section sources**
- [adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)
- [window.py](file://src/pillars/adyton/ui/engine/window.py)
- [floor_plan_window.py](file://src/pillars/adyton/ui/floor_plan_window.py)
- [wall_designer.py](file://src/pillars/adyton/ui/wall_designer.py)
- [watchtower_view.py](file://src/pillars/adyton/ui/watchtower_view.py)
- [scene.py](file://src/pillars/adyton/ui/engine/scene.py)
- [camera.py](file://src/pillars/adyton/ui/engine/camera.py)
- [renderer.py](file://src/pillars/adyton/ui/engine/renderer.py)
- [block.py](file://src/pillars/adyton/models/block.py)
- [corner.py](file://src/pillars/adyton/models/corner.py)
- [prism.py](file://src/pillars/adyton/models/prism.py)
- [floor.py](file://src/pillars/adyton/models/floor.py)
- [throne.py](file://src/pillars/adyton/models/throne.py)
- [wall.py](file://src/pillars/adyton/models/wall.py)
- [kamea_cell.py](file://src/pillars/adyton/models/kamea_cell.py)
- [kamea_pyramid_cell.py](file://src/pillars/adyton/ui/kamea_pyramid_cell.py)
- [geometry_types.py](file://src/pillars/adyton/models/geometry_types.py)
- [constants.py](file://src/pillars/adyton/constants.py)
- [main.py](file://src/main.py)

## Performance Considerations
The Adyton engine implements several performance optimizations for real-time 3D rendering. The software rasterization approach using QPainter is optimized through efficient data structures and algorithms. The system uses the Painter's Algorithm for depth sorting, which is efficient for the types of scenes rendered in the Adyton. Object transformations are cached in the Object3D._world_faces field to avoid redundant calculations during rendering. The camera system implements orbit, pan, and zoom controls that provide smooth navigation through the 3D space. For complex scenes with many objects, the system could benefit from additional optimizations such as frustum culling or level-of-detail rendering, but the current implementation is sufficient for the intended use cases. The new components (floor plan window, wall designer, watchtower view) use specialized rendering approaches optimized for their specific visualization needs, with the wall designer using a minimum spanning tree algorithm to generate asterism lines and the watchtower view using efficient layout algorithms for the 156-cell display.

**Section sources**
- [renderer.py](file://src/pillars/adyton/ui/engine/renderer.py)
- [geometry_types.py](file://src/pillars/adyton/models/geometry_types.py)
- [window.py](file://src/pillars/adyton/ui/engine/window.py)
- [wall_designer.py](file://src/pillars/adyton/ui/wall_designer.py)
- [watchtower_view.py](file://src/pillars/adyton/ui/watchtower_view.py)

## Troubleshooting Guide
When encountering issues with the Adyton pillar, consider the following common problems and solutions:

1. **Rendering artifacts or incorrect geometry**: Verify that the transformation matrices are being applied correctly in the Object3D.update_world_transform method. Check that the vertex order for faces follows the correct winding order (counter-clockwise).

2. **Camera navigation issues**: Ensure that the camera's spherical coordinate system is properly converted to Cartesian coordinates in the position() method. Verify that the orbit, pan, and zoom controls are responding to user input correctly.

3. **Performance problems with complex scenes**: The current implementation creates individual Object3D instances for each geometric element. For very large scenes, consider batching similar objects or implementing view frustum culling to reduce the number of objects processed during rendering.

4. **Incorrect scene initialization**: Verify that the SevenSidedPrism.build method is correctly calculating the positions and rotations of the Ashlar blocks and Corner stones based on the heptagonal geometry.

5. **Floor plan visualization issues**: Check that the FloorGeometry.build method is correctly calculating the concentric heptagons and that the throne is positioned at the correct y-offset to avoid z-fighting.

6. **Wall designer grid problems**: Ensure that the planetary_lattices.json file is correctly formatted and that the constellation grid is properly calculating the minimum spanning tree for asterism lines.

7. **Kamea cell display errors**: Verify that the kamea_maut_ternary.csv file is present and correctly formatted, and that the KameaLoaderService is properly parsing the coordinate system.

**Section sources**
- [renderer.py](file://src/pillars/adyton/ui/engine/renderer.py)
- [camera.py](file://src/pillars/adyton/ui/engine/camera.py)
- [scene.py](file://src/pillars/adyton/ui/engine/scene.py)
- [prism.py](file://src/pillars/adyton/models/prism.py)
- [geometry_types.py](file://src/pillars/adyton/models/geometry_types.py)
- [floor.py](file://src/pillars/adyton/models/floor.py)
- [throne.py](file://src/pillars/adyton/models/throne.py)
- [wall_designer.py](file://src/pillars/adyton/ui/wall_designer.py)
- [kamea_loader_service.py](file://src/pillars/adyton/services/kamea_loader_service.py)

## Conclusion
The Adyton pillar serves as a sophisticated 3D visualization engine for esoteric geometries within the isopgem application. Its architecture combines a clean separation of concerns with efficient rendering techniques to create an immersive environment for exploring sacred spaces. The system's design reflects its purpose as a visualization layer for complex mathematical and metaphysical concepts, with geometric models based on precise measurements and proportions. Recent updates have enhanced the visualization capabilities with new components including the throne, floor plan window, kamea pyramid cell, and wall designer, expanding the ways users can interact with and understand the sacred geometries. The integration of the Adyton with other pillars of the application allows for a comprehensive exploration of esoteric knowledge through interactive 3D visualization.