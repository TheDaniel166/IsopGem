# The Document Manager

**"In the beginning was the Word. We parse the Word to find the Number."**

## Architectural Role
The **Document Manager** is the **Scribe of the Akaschic Record**. It is responsible for ingesting, parsing, organizing, and analyzing the textual corpus provided by the Magus. It serves as the foundation for the Gematria Engine.

## The Core Logic (Services)

### **[document_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/services/document_service.py)**
*   **Architectural Role**: Sovereign Service (The Librarian)
*   **The Purpose**: Manages the lifecycle of a Document. It is the single point of truth for importing, updating, and retrieving texts.
*   **Key Logic**:
    *   `import_document`: Auto-detects file type (PDF/Docx/HTML/Text). Extracts Metadata (Author/Title). Hashes content to prevent duplicates.
    *   **Context Management**: Maintains the `document_service_context` global singleton.
*   **Signal Flow**:
    *   **Emits**: `document_imported`, `document_updated`.
*   **Dependencies**: `DocumentRepository`, `DocumentSearchRepository`, `parsers`.

### **[mindscape_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/services/mindscape_service.py)**
*   **Architectural Role**: Sovereign Service (The Weaver)
*   **The Purpose**: Manages the "Mindscape", a graph database of Linked Thoughts.
*   **Key Logic**:
    *   `create_node`: Instantiates a `MindNode` with visual appearance data (JSON).
    *   `link_nodes`: Creates a `MindEdge` between concepts.
    *   `get_graph`: returns the full adjacency list for the visualizer.
*   **Dependencies**: `MindscapeRepository`.

### **[parsers.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/services/parsers.py)**
*   **Architectural Role**: Service (The Translator)
*   **The Purpose**: Adapters for reading various file formats (`.pdf`, `.docx`, `.txt`, `.html`).
*   **Key Logic**: Extracts raw text and metadata.

### **[verse_teacher_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/services/verse_teacher_service.py)**
*   **Architectural Role**: Sovereign Service (The Rate)
*   **The Purpose**: Facilitates the segmentation of "Holy Books" into canonical verses (e.g., "Genesis 1:1").
*   **Key Logic**:
    *   `_apply_rules`: Uses a regex-based heuristics engine to split raw text.
    *   **Learning**: Adjusts rules based on Magus feedback during the "Teaching" phase.
*   **Dependencies**: `VerseRuleRepository`, `VerseEditLogRepository`.

## The Presentation Layer (UI)

### **[mindscape_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/ui/mindscape_window.py)**
*   **Architectural Role**: View (The Living Graph)
*   **The Purpose**: The visual interface for the Mindscape.
*   **Key Logic**:
    *   `_load_graph`: Asynchronously loads the graph data.
    *   `_show_context_menu`: Handles Right-Click -> Inspect/Delete logic.
    *   **Drag & Drop**: Accepts dropped "Search Results" to create new nodes.
*   **Signal Flow**:
    *   **Listens to**: `node_double_clicked` (Navigates to document).
*   **Dependencies**: `MindscapeView`, `NodeInspectorWidget`.

### **[mindscape_view.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/ui/mindscape_view.py)**
*   **Architectural Role**: View (The Canvas)
*   **The Purpose**: The specialized `QGraphicsView` for the Mindscape.
*   **Key Logic**: Handles zooming, panning, and item interaction (selection).

### **[mindscape_inspector.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/ui/mindscape_inspector.py)**
*   **Architectural Role**: View (The Lens)
*   **The Purpose**: Detailed property editor for a selected Node or Edge.

### **[rich_text_editor.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/ui/rich_text_editor.py)**
*   **Architectural Role**: View (The Quill)
*   **The Purpose**: A specialized "Ribbon-style" editor for composing and formatting text.
*   **Key Logic**:
    *   **Formatting**: Handlers for Bold, Italic, Underline, and Semantic Styles (Header, Quote).
    *   **Extensions**: Integrates `[image_features.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/ui/image_features.py)`, `[table_features.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/ui/table_features.py)`, and `[search_features.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/ui/search_features.py)` mixins.
    *   `_apply_style`: Applies `QTextCharFormat` to the cursor selection.
*   **Dependencies**: `[ribbon_widget.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/ui/ribbon_widget.py)`

### **[document_search_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/ui/document_search_window.py)**
*   **Architectural Role**: View (The Finder)
*   **The Purpose**: Dedicated searching interface.

### **[search_results_panel.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/ui/search_results_panel.py)**
*   **Architectural Role**: View (The Oracle)
*   **The Purpose**: Displays `Whoosh` search hits with context snippets.
*   **Key Logic**:
    *   `load_results`: Renders HTML snippets highlighting the search term.
    *   **Interaction**: Double-click jumps to the exact text location in the Editor.

### **[document_editor_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/ui/document_editor_window.py)**
*   **Architectural Role**: View (The Desk)
*   **The Purpose**: The container window for the `RichTextEditor`.

### **[verse_teacher_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/ui/verse_teacher_window.py)**
*   **Architectural Role**: View (The Classroom)
*   **The Purpose**: The interface for training the verse segmentation logic.
*   **Key Logic**:
    *   **Diff View**: Shows the "Before" (Raw) and "After" (Proposed) split for Magus verification.

### **[graph_physics.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/ui/graph_physics.py)**
*   **Architectural Role**: Business Logic (Physics Engine)
*   **The Purpose**: Calculates the layout of the Mindscape nodes.
*   **Key Logic**:
    *   `tick`: Applies Coulomb Repulsion (between all nodes) and Hooke's Law Attraction (along edges).
    *   **Damping**: simulation energy decay to stabilize the graph.

## Data Structures (Models)

### **[document.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/models/document.py)**
*   **Architectural Role**: Domain Model
*   **The Purpose**: SQL entity for a file.
*   **Key Logic**: Stores `content` (blob), `metadata` (JSON), and `tags`.

### **[document_verse.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/models/document_verse.py)**
*   **Architectural Role**: Domain Model
*   **The Purpose**: SQL entity for a single verse within a Holy Book.

### **[mindscape.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/models/mindscape.py)**
*   **Architectural Role**: Domain Model
*   **The Purpose**: Entities for `MindNode` and `MindEdge` (defined in `[mindscape_items.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/ui/mindscape_items.py)`).
*   **Key Logic**: Uses `JSON` columns to store flexible "Appearance" data (Color, Shape, Line Style) without schema migration.

## Infrastructure

### **[document_repository.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/repositories/document_repository.py)**
*   **Architectural Role**: Persistence Layer
*   **The Purpose**: Database access for Document metadata and content.

### **[verse_rule_repository.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/repositories/verse_rule_repository.py)**
*   **Architectural Role**: Persistence Layer
*   **The Purpose**: Storage for regex rules used by the Verse Teacher.

### **[search_repository.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/repositories/search_repository.py)**
*   **Architectural Role**: Persistence Layer (Search Engine)
*   **The Purpose**: Interface to the `Whoosh` full-text search library.
*   **Key Logic**:
    *   `index_document`: Tokenizes and stores text.
    *   `search`: Returns ranked results with highlighting.
