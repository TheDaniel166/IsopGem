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
*   **Dependencies**: `DocumentRepository`, `DocumentSearchRepository`.

### **[verse_teacher_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/services/verse_teacher_service.py)**
*   **Architectural Role**: Sovereign Service (The Rate)
*   **The Purpose**: Facilitates the segmentation of "Holy Books" into canonical verses (e.g., "Genesis 1:1").
*   **Key Logic**:
    *   `_apply_rules`: Uses a regex-based heuristics engine to split raw text.
    *   **Learning**: Adjusts rules based on Magus feedback during the "Teaching" phase.
*   **Dependencies**: `VerseRuleRepository`, `VerseEditLogRepository`.

### **[etymology_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/services/etymology_service.py)**
*   **Architectural Role**: Service (The Linguist)
*   **The Purpose**: Fetches word origins, auto-detecting the script language.
*   **Key Logic**:
    *   **Heuristic Detection**: Identifies Hebrew, Greek, or Latin script blocks.
    *   **Routing**: Sends Hebrew to Sefaria/Wiktionary, Greek to Wiktionary Ancient Greek, and English to `ety-python`.

### **[notebook_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/services/notebook_service.py)**
*   **Architectural Role**: Sovereign Service (The Scribe)
*   **The Purpose**: Manages the hierarchical organization of user content.
*   **Structure**: `Notebook` -> `Section` -> `Page` (Document).
*   **Key Logic**: Eager loading of sections for performant tree views.

### **[spell_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/document_manager/services/spell_service.py)**
*   **Architectural Role**: Service (The Editor)
*   **The Purpose**: Wraps `pyenchant` to provide spell-checking and suggestions.
*   **Key Logic**:
    *   **Custom Dictionary**: Persists user-added words to `~/.isopgem/custom_dictionary.txt`.
    *   **Session Ignore**: Temporarily ignores words for the current runtime.

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

## The Mechanics of the Void (Infinite Canvas)

**"The Map is not the Territory, until the Territory expands to meet it."**

The **Infinite Canvas** (`InfiniteCanvasView`) operates on a principle of **Dynamic Expansion** to reconcile the finite nature of the Viewport ("The Camera") with the potentially infinite nature of the Content ("The Territory").

### 1. The Liquid Height Problem
Note Containers store their **Width** (e.g., 400px) as a fixed constant, but their **Height** is liquid. It is determined only at runtime when HTML content is poured into the container.
*   **The Lag:** There is a microsecond gap between "Loading Data" and "Knowing Height."
*   **The Consequence:** If the Canvas Scene (`sceneRect`) is smaller than the resulting content, the Scrollbars (`QGraphicsView`) will clamp the user's view, making the bottom of the content inaccessible.

### 2. Dynamic Expansion (The Breath)
To solve this, the Canvas listens for the `content_changed` signal from any `NoteContainer`.
*   **The Check:** If a container grows within 500px of the current Scene Edge, the Scene expands by 1000px.
*   **The Anchoring:** Crucially, when the Scene expands, the Viewport's center is mathematically preserved.
    *   *Without Anchor:* The expansion resets the Scrollbars to (0,0), causing a visual "Jump."
    *   *With Anchor:* The View calculates its current "Look At" point, expands the map, and immediately re-centers on that point.

### 3. Prophetic Centering (The Search Jump)
When a user clicks a Search Result, we cannot simply "Scroll to the Highlight," because the Container might be starting in a collapsed state.
*   **The Sequence:**
    1.  **Prediction:** We calculate where the highlight *will be* in the fully expanded coordinate space (Content Y), ignoring the current visual state.
    2.  **Forced Manifestation:** We manually trigger `_auto_resize()` on the container and `_update_scene_rect()` on the Canvas. This forces the "Territory" to expand instantly.
    3.  **The Jump:** We center the View on the predicted coordinate.
*   **Result:** A precise, stable jump to content that technically didn't exist a moment prior.
