# The Adyton Sanctuary

**"The Stone that the builders rejected has become the Chief Cornerstone."**

## Architectural Role
The **Adyton (Sanctuary)** is the **Inner Chamber**. It is a specialized 3D engine dedicated to the construction and visualization of the "Chamber of the Adepts". Unlike the general-purpose `Geometry` pillar, Adyton allows the Magus to walk inside the structure.

## The Core Logic (Engine)

### **[renderer.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/adyton/ui/engine/renderer.py)**
*   **Architectural Role**: Sovereign Service (The Painter)
*   **The Purpose**: The custom rendering pipeline responsible for drawing the stone and light.
*   **Key Logic**:
    *   `render_frame`: Clears the buffer, sorts objects by depth (Painter's Algorithm), and draws faces.
    *   **Lighting**: Calculates simple flat shading based on Face Normals relative to a fixed light source.

### **[camera.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/adyton/ui/engine/camera.py)**
*   **Architectural Role**: Service (The Eye)
*   **The Purpose**: The "Eye" of the Magus, allowing first-person navigation through the Chamber.
*   **Key Logic**:
    *   **Matrices**: Maintains View and Projection matrices.
    *   `move`: Updates position vector (WASD logic).
    *   `look`: Updates Yaw/Pitch vectors (Mouse look).

### **[scene.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/adyton/ui/engine/scene.py)**
*   **Architectural Role**: Container
*   **The Purpose**: The container for the blocks and lights.
*   **Key Logic**:
    *   **Object Management**: list of `Block` entities.
    *   `add_block`: Validation logic for placing stones.

### **[frustum_color_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/adyton/services/frustum_color_service.py)**
*   **Architectural Role**: Service (The Painter)
*   **The Purpose**: Resolves the specific colors for the walls of the Chamber based on planetary correspondences.
*   **Key Logic**:
    *   **Wall Loading**: Ingests CSVs (e.g., `sun_wall.csv`) mapping the grid to colors.
    *   **Ternary Resolution**: Resolves colors for split-faces using Ditrune logic.

### **[kamea_loader_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/adyton/services/kamea_loader_service.py)**
*   **Architectural Role**: Service (The Mason)
*   **The Purpose**: Loads the Master Kamea of Maut from the foundational CSV.
*   **Key Logic**:
    *   **Parsing**: Maps (X, Y) coordinates to `KameaCell` objects containing Ditrunes.
    *   **Octant Logic**: Determines the spiritual "Octant" and "Tablet" for each cell.

### **[kamea_color_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/adyton/services/kamea_color_service.py)**
*   **Architectural Role**: Service (The Prism)
*   **The Purpose**: Resolves colors specifically for Kamea floor/ceiling tiles.

## The Building Blocks (Models)

### **[block.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/adyton/models/block.py)**
*   **Architectural Role**: Domain Model (The Stone)
*   **The Purpose**: Represents the fundamental masonry unit of the Chamber.
*   **Key Logic**:
    *   **Geometry**: Defined by 8 vertices (Cube).
    *   **Texture**: Stores UV coordinates (Placeholder) or Color data.

### **[prism.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/adyton/models/prism.py)**
*   **Architectural Role**: Domain Model (The Glass)
*   **The Purpose**: Defines the light-refracting or structural prisms within the sanctuary.
*   **Key Logic**:
    *   **Refraction**: (Future) Index of Refraction properties.

### **[corner.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/adyton/models/corner.py)**
*   **Architectural Role**: Domain Model (The Keystone)
*   **The Purpose**: Handles the complex joinery and geometry of the structure's vertices.
*   **Key Logic**:
    *   **Joinery**: Logic for mitering connections between blocks.

## The Presentation Layer (UI)

### **[window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/adyton/ui/engine/window.py)**
*   **Architectural Role**: View (The Viewport)
*   **The Purpose**: The Qt window hosting the rendering context.
*   **Key Logic**:
    *   **Input Handling**: Captures KeyPress (Movement) and MouseMove (Look) events and routes them to the `Camera`.
    *   **Game Loop**: Uses `QTimer` to trigger `Renderer.render_frame` at 60 FPS.

### **[adyton_hub.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/adyton/ui/adyton_hub.py)**
*   **Architectural Role**: View (The Gateway)
*   **The Purpose**: The sovereign entry point to the Sanctuary.
*   **Signal Flow**: Launches `Window` via `WindowManager`.
