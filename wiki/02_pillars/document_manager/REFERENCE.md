# Document Manager Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the Akaschic Archive, mapping the lifecycle of rich-text manuscripts and the visual "Mindscape" graph.










---

**File:** `src/pillars/document_manager/models/document.py`

**Role:** `[Bone] (Model)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.models.document_manager.document.DocumentImage`
* `shared.models.document_manager.document.DocumentLink`
* `shared.models.document_manager.document.Document`

**Consumers (Who Needs It):**
* `scripts/migrate_document_images.py`
* `src/pillars/document_manager/ui/document_editor_window.py`
* `src/pillars/document_manager/ui/document_properties_dialog.py`
* `src/pillars/document_manager/ui/mindscape_tree.py`
* `tests/verify_database_manager.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/models/document_verse.py`

**Role:** `[Bone] (Model)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.models.document_manager.document_verse.DocumentVerse`
* `shared.models.document_manager.document_verse.VerseEditLog`
* `shared.models.document_manager.document_verse.VerseRule`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/models/dtos.py`

**Role:** `[Bone] (Model)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.models.document_manager.dtos.DocumentMetadataDTO`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/ui/document_properties_dialog.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/models/notebook.py`

**Role:** `[Bone] (Model)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.models.document_manager.notebook.Notebook`
* `shared.models.document_manager.notebook.Section`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/repositories/document_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.repositories.document_manager.document_repository.DocumentRepository`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/repositories/document_verse_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.repositories.document_manager.document_verse_repository.DocumentVerseRepository`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/repositories/image_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.repositories.document_manager.image_repository.ImageRepository`

**Consumers (Who Needs It):**
* `scripts/migrate_document_images.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/repositories/search_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.repositories.document_manager.search_repository.DocumentSearchRepository`

**Consumers (Who Needs It):**
* `tests/document/test_document_search.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/repositories/verse_edit_log_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.repositories.document_manager.verse_edit_log_repository.VerseEditLogRepository`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/repositories/verse_rule_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.repositories.document_manager.verse_rule_repository.VerseRuleRepository`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/services/document_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.services.document_manager.document_service.DocumentService`
* `shared.services.document_manager.document_service.document_service_context`

**Consumers (Who Needs It):**
* `scripts/attic/debug_doc_collections.py`
* `scripts/attic/debug_doc_tags.py`
* `src/pillars/document_manager/ui/canvas/note_container.py`
* `src/pillars/document_manager/ui/database_manager.py`
* `src/pillars/document_manager/ui/document_editor_window.py`
* `src/pillars/document_manager/ui/document_library.py`
* `src/pillars/document_manager/ui/document_manager_hub.py`
* `src/pillars/document_manager/ui/document_search_window.py`
* `tests/document/test_document_service.py`
* `tests/verify_database_manager.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/services/etymology_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.services.document_manager.etymology_service.EtymologyService`
* `shared.services.document_manager.etymology_service.get_etymology_service`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/services/notebook_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.services.document_manager.notebook_service.NotebookService`
* `shared.services.document_manager.notebook_service.notebook_service_context`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_notebooks.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/services/spell_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.services.document_manager.spell_service.SpellService`
* `shared.services.document_manager.spell_service.get_spell_service`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/services/verse_teacher_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.services.document_manager.verse_teacher_service.VerseTeacherService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/ui/canvas/infinite_canvas.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Infinite Canvas - The Boundless Workspace.

**Input (Ingests):**
* `parent`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QMouseEvent`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtWidgets.QGraphicsScene`
* `PyQt6.QtWidgets.QGraphicsView`
* `json`
* `logging`
* `note_container.NoteContainerItemMovable`
* `shape_item.ArrowShapeItem`
* `shape_item.BaseShapeItem`
* `shape_item.EllipseShapeItem`
* `shape_item.LineShapeItem`
* `shape_item.PolygonShapeItem`
* `shape_item.RectShapeItem`
* `shape_item

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_canvas.py`

**Key Interactions:**
**Emits:** `content_changed` - *Nervous System Signal.*
**Emits:** `zoom_changed` - *Nervous System Signal.*
**Exposes:** `get_zoom()` - *Get current zoom factor (1.0 = 100%).*
**Exposes:** `set_zoom()` - *Set absolute zoom factor.*
**Exposes:** `zoom_in()` - *Zoom in by 25%.*
**Exposes:** `zoom_out()` - *Zoom out by 25%.*
**Exposes:** `zoom_reset()` - *Reset to 100% zoom.*
**Exposes:** `zoom_fit()` - *Fit all content in view.*
**Exposes:** `wheelEvent()` - *Handle mouse wheel for zooming (with Ctrl) or scrolling.*
**Exposes:** `mouseDoubleClickEvent()` - *Create new note container on double click.*
**Exposes:** `add_note_container()` - *Add note container logic.*
**Exposes:** `clear_canvas()` - *Clear canvas logic.*
**Exposes:** `add_shape()` - *Add a shape to the canvas.*
**Exposes:** `start_shape_insert()` - *Enter insert mode for shapes.*
**Exposes:** `cancel_shape_insert()` - *Cancel shape insert mode.*
**Exposes:** `mousePressEvent()` - *Handle mouse press - check for shape insert mode.*
**Exposes:** `keyPressEvent()` - *Handle delete key for shapes.*
**Exposes:** `get_json_data()` - *Serialize all items to JSON.*
**Exposes:** `get_searchable_text()` - *Extract plain text from all note containers for indexing.*
**Exposes:** `load_json_data()` - *Load items from JSON.*


---

**File:** `src/pillars/document_manager/ui/canvas/note_container.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Note Container - The Canvas Fragment.

**Input (Ingests):**
* `parent`
* `parent`
* `width`
* `height`
* `x`
* `y`
* `w`
* `content`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QRectF`
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtWidgets.QColorDialog`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsProxyWidget`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QSizeGrip`
* `PyQt6.QtWidgets.QStyleOptionGraphics

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `resize_delta` - *Nervous System Signal.*
**Emits:** `resize_started` - *Nervous System Signal.*
**Emits:** `resize_finished` - *Nervous System Signal.*
**Exposes:** `paintEvent()` - *Draw resize grip lines.*
**Exposes:** `mousePressEvent()` - *Mousepressevent logic.*
**Exposes:** `mouseMoveEvent()` - *Mousemoveevent logic.*
**Exposes:** `mouseReleaseEvent()` - *Mousereleaseevent logic.*
**Emits:** `resize_requested` - *Nervous System Signal.*
**Exposes:** `resizeEvent()` - *Keep resize grip in bottom-right corner.*
**Exposes:** `get_html()` - *Retrieve html logic.*
**Exposes:** `set_html()` - *Configure html logic.*
**Exposes:** `set_text()` - *Configure text logic.*
**Emits:** `content_changed` - *Nervous System Signal.*
**Exposes:** `mousePressEvent()` - *Mousepressevent logic.*
**Emits:** `content_changed` - *Nervous System Signal.*
**Exposes:** `mousePressEvent()` - *Mousepressevent logic.*
**Exposes:** `mouseMoveEvent()` - *Mousemoveevent logic.*
**Exposes:** `mouseDoubleClickEvent()` - *Mousedoubleclickevent logic.*
**Exposes:** `mouseReleaseEvent()` - *Mousereleaseevent logic.*
**Exposes:** `hoverEnterEvent()` - *Hoverenterevent logic.*
**Exposes:** `contextMenuEvent()` - *Show right-click context menu.*
**Exposes:** `to_dict()` - *Serialize container for saving.*
**Exposes:** `from_dict()` - *Create container from saved data.*


---

**File:** `src/pillars/document_manager/ui/database_manager.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Database Manager UI for Document Pillar.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QProgressBar`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QTabWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `logging`
* `pillars.document_manager.services.docu

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/ui/document_editor_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Document Editor Window - The Scribe's Sanctum.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QCloseEvent`
* `PyQt6.QtGui.QKeySequence`
* `PyQt6.QtPrintSupport.QPrinter`
* `PyQt6.QtWidgets.QDialogButtonBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMenuBar`
* `PyQt6.QtWidgets.QMes

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `load_document_model()` - *Load a document from the database model.*
**Exposes:** `new_document()` - *New document logic.*
**Exposes:** `open_document()` - *Open document logic.*
**Exposes:** `save_document()` - *Save document logic.*
**Exposes:** `save_as_document()` - *Save as document logic.*
**Exposes:** `export_pdf()` - *Export the current document to PDF.*
**Exposes:** `closeEvent()` - *Closeevent logic.*
**Exposes:** `filter_items()` - *Filter items logic.*
**Exposes:** `on_item_double_clicked()` - *Handle item double clicked logic.*


---

**File:** `src/pillars/document_manager/ui/document_library.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Document Library UI.

**Input (Ingests):**
* `query`
* `parent`
* `text`
* `sort_key`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QThread`
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtWidgets.QAbstractItemView`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWi

**Consumers (Who Needs It):**
* `scripts/verify_library_ui.py`

**Key Interactions:**
**Emits:** `results_ready` - *Nervous System Signal.*
**Exposes:** `run()` - *Execute logic.*
**Emits:** `document_opened` - *Nervous System Signal.*
**Exposes:** `toggle_col()` - *Toggle col logic.*


---

**File:** `src/pillars/document_manager/ui/document_manager_hub.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Document Manager pillar hub - launcher interface for document tools.

**Input (Ingests):**
* `window_manager`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `database_manager.DatabaseManagerWindow`
* `document_editor_window.DocumentEditorWindow`
* `document_library.DocumentLibrary`
* `document_search_window.DocumentSearchW

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/ui/document_properties_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Dialog for editing document metadata.

**Input (Ingests):**
* `documents`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QVBoxLayout`
* `pillars.document_manager.models.document.Document`
* `pillars.document_manager.models.dtos.DocumentMetadataDTO`
* `typing.Any`
* `typing.List`
* `typing.Optional`
* `typing.Union`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_data()` - *Returns dict of fields to update. None value means no change.*
**Exposes:** `get_common_value()` - *Retrieve common value logic.*
**Exposes:** `get_update_value()` - *Retrieve update value logic.*


---

**File:** `src/pillars/document_manager/ui/document_search_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Document Search Window.

**Input (Ingests):**
* `query`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QCoreApplication`
* `PyQt6.QtCore.QObject`
* `PyQt6.QtCore.QRunnable`
* `PyQt6.QtCore.QSettings`
* `PyQt6.QtCore.QThreadPool`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtCore.pyqtSlot`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QAbstractItemView`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QLabel`
* `PyQt

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `finished` - *Nervous System Signal.*
**Emits:** `error` - *Nervous System Signal.*
**Exposes:** `run()` - *Execute the search in background thread.*
**Emits:** `document_opened` - *Nervous System Signal.*


---

**File:** `src/pillars/document_manager/ui/font_manager_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Font Manager Window - The Glyph Atlas.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QIcon`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QTextEdit`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `shared.ui.font_loade

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/ui/graph_physics.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Graph Physics Engine for Mindscape.

**Input (Ingests):**
* `id` (Field)
* `x` (Field)
* `y` (Field)
* `vx` (Field)
* `vy` (Field)
* `mass` (Field)
* `radius` (Field)
* `fixed` (Field)
* `source_id` (Field)
* `target_id` (Field)
* `length` (Field)
* `stiffness` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `dataclasses.dataclass`
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `tests/document/test_graph_physics.py`

**Key Interactions:**
**Exposes:** `add_node()` - *Add node logic.*
**Exposes:** `remove_node()` - *Remove node logic.*
**Exposes:** `add_edge()` - *Add edge logic.*
**Exposes:** `clear()` - *Clear logic.*
**Exposes:** `set_position()` - *Configure position logic.*
**Exposes:** `set_fixed()` - *Configure fixed logic.*
**Exposes:** `tick()` - *Step the simulation.*
**Exposes:** `get_position()` - *Retrieve position logic.*




**File:** `src/pillars/document_manager/ui/image_features.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Image management features for RichTextEditor.

**Input (Ingests):**
* `fmt`
* `parent`
* `path`
* `parent`
* `editor`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PIL.ImageEnhance`
* `PIL.ImageFilter`
* `PIL.ImageOps`
* `PIL.Image`
* `PIL`
* `PyQt6.QtCore.QBuffer`
* `PyQt6.QtCore.QByteArray`
* `PyQt6.QtCore.QIODevice`
* `PyQt6.QtCore.QObject`
* `PyQt6.QtCore.QPoint`
* `PyQt6.QtCore.QRect`
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.QThread`
* `PyQt6.QtCore.QUrl`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QIcon`
* `PyQt6.QtGui.QImage`
* `PyQt6.QtGui.QPixmap`
* `PyQt6.QtGui.QTextCursor`
* `PyQt6.QtGui.QTextDocument`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `selection_changed` - *Nervous System Signal.*
**Exposes:** `set_display_rect()` - *Functional interface.*
**Exposes:** `clear_selection()` - *Clear the current crop selection.*
**Exposes:** `has_selection()` - *Check if there's a valid pending selection.*
**Exposes:** `get_selection()` - *Get the pending selection rect (normalized to display_rect origin).*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Exposes:** `mouseMoveEvent()` - *Functional interface.*
**Exposes:** `mouseReleaseEvent()` - *Functional interface.*
**Exposes:** `apply_to_format()` - *Functional interface.*
**Emits:** `finished` - *Nervous System Signal.*
**Exposes:** `run()` - *Functional interface.*
**Exposes:** `get_final_qimage()` - *Functional interface.*
**Exposes:** `get_final_bytes_png()` - *Functional interface.*
**Exposes:** `create_toolbar_action()` - *Return the insert image action for the toolbar.*
**Exposes:** `extend_context_menu()` - *Add image actions to context menu if applicable.*
**Exposes:** `insert_image()` - *Functional interface.*
**Exposes:** `sepia_pixel()` - *Functional interface.*
**Exposes:** `shift_channel()` - *Functional interface.*
**Exposes:** `fade()` - *Functional interface.*




---

**File:** `src/pillars/document_manager/ui/import_options_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Import Options Dialog - The Collection Selector.

**Input (Ingests):**
* `existing_collections`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDialogButtonBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QVBoxLayout`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_data()` - *Retrieve data logic.*


---

**File:** `src/pillars/document_manager/ui/mindscape_page.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Mindscape Page - The Canvas Editor.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QTextCharFormat`
* `PyQt6.QtGui.QTextListFormat`
* `PyQt6.QtWidgets.QColorDialog`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QFontComboBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSlider`
* `PyQt6.QtWidgets.Q

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `load_node()` - *Load content from Document.*
**Exposes:** `highlight_search_term()` - *Find text in any note container and jump to it.*
**Exposes:** `save_page()` - *Persist changes.*
**Exposes:** `clear()` - *Clear logic.*
**Exposes:** `do_center()` - *Do center logic.*


---

**File:** `src/pillars/document_manager/ui/mindscape_theme.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Mindscape Theme - The Visual Palette.

**Input (Ingests):**
* `mode`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `set_mode()` - *Configure mode logic.*
**Exposes:** `get_color()` - *Retrieve color logic.*
**Exposes:** `get_font()` - *Retrieve font logic.*


---

**File:** `src/pillars/document_manager/ui/mindscape_tree.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Mindscape Tree - The Notebook Sidebar.

**Input (Ingests):**
* `filepath`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QObject`
* `PyQt6.QtCore.QPoint`
* `PyQt6.QtCore.QRunnable`
* `PyQt6.QtCore.QThreadPool`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtCore.pyqtSlot`
* `PyQt6.QtGui.QDropEvent`
* `PyQt6.QtWidgets.QAbstractItemView`
* `PyQt6.QtWidgets.QDialogButtonBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMenu`
* `Py

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `finished` - *Nervous System Signal.*
**Emits:** `error` - *Nervous System Signal.*
**Exposes:** `run()` - *Execute logic.*
**Emits:** `page_selected` - *Nervous System Signal.*
**Exposes:** `load_tree()` - *Reload the entire tree structure.*
**Exposes:** `dropEvent()` - *Dropevent logic.*


---

**File:** `src/pillars/document_manager/ui/mindscape_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Mindscape Window - The Knowledge Tree.

**Input (Ingests):**
* `title`
* `path`
* `snippet`
* `parent`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QStackedWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `mindscape_page.MindscapePageWidget`
* `mindscape_tree.MindscapeTreeWidget`
* `qtawesome`
* `services.notebo

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/ui/ribbon_widget.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.ui.rich_text_editor.ribbon_widget.RibbonWidget`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_ribbon.py`
* `tests/verification/verify_ribbon.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/ui/rich_text_editor.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Backward compatibility shim for RichTextEditor.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.ui.rich_text_editor.RichTextEditor`
* `shared.ui.rich_text_editor.SafeTextEdit`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/ui/canvas/note_container.py`
* `tests/document/test_document_search.py`
* `tests/verification/verify_alignment_mutex.py`
* `tests/verification/verify_clear_highlight.py`
* `tests/verification/verify_headings.py`
* `tests/verification/verify_headings_gui.py`
* `tests/verification/verify_lists.py`
* `tests/verification/verify_ribbon.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/ui/search_results_panel.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Search Results Panel - The Librarian's List.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `re`

**Consumers (Who Needs It):**
* `tests/_legacy/test_search_panel.py`

**Key Interactions:**
**Emits:** `add_to_graph_requested` - *Nervous System Signal.*
**Emits:** `open_document_requested` - *Nervous System Signal.*
**Exposes:** `load_results()` - *Populate the list with search results.*


---

**File:** `src/pillars/document_manager/ui/shape_item.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.ui.rich_text_editor.shape_item.ArrowShapeItem`
* `shared.ui.rich_text_editor.shape_item.BaseShapeItem`
* `shared.ui.rich_text_editor.shape_item.EllipseShapeItem`
* `shared.ui.rich_text_editor.shape_item.LineShapeItem`
* `shared.ui.rich_text_editor.shape_item.RectShapeItem`
* `shared.ui.rich_text_editor.shape_item.TriangleShapeItem`
* `shared.ui.rich_text_editor.shape_item.create_shape_from_dict`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/utils/image_utils.py`

**Role:** `[Tool] (Utility)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.services.document_manager.utils.image_utils.MAX_IMG_SIZE`
* `shared.services.document_manager.utils.image_utils.extract_images_from_html`
* `shared.services.document_manager.utils.image_utils.has_docimg_references`
* `shared.services.document_manager.utils.image_utils.has_embedded_images`
* `shared.services.document_manager.utils.image_utils.restore_images_in_html`

**Consumers (Who Needs It):**
* `scripts/migrate_document_images.py`
* `tests/verify_image_utils.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/utils/parsers.py`

**Role:** `[Tool] (Utility)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.services.document_manager.utils.parsers.DocumentParser`

**Consumers (Who Needs It):**
* `tests/manual_metadata_test.py`
* `tests/mock_metadata_test.py`
* `tests/verify_list_parsing.py`

**Key Interactions:**
* Internal logic only.
