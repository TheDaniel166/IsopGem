# Document Manager Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the Akaschic Archive, mapping the lifecycle of rich-text manuscripts and the visual "Mindscape" graph.



---

**File:** `src/pillars/document_manager/models/document.py`

**Role:** `[Bone] (Model)`

**Purpose:** Document database model.

**Input (Ingests):**
* `id` (Column)
* `document_id` (Column)
* `hash` (Column)
* `data` (Column)
* `mime_type` (Column)
* `original_filename` (Column)
* `width` (Column)
* `height` (Column)
* `created_at` (Column)
* `id` (Column)
* `source_id` (Column)
* `target_id` (Column)
* `created_at` (Column)
* `id` (Column)
* `title` (Column)
* `file_path` (Column)
* `file_type` (Column)
* `content` (Column)
* `raw_content` (Column)
* `author` (Column)
* `collection` (Column)
* `created_at` (Column)
* `updated_at` (Column)
* `section_id` (Column)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.database.Base`
* `sqlalchemy.Column`
* `sqlalchemy.DateTime`
* `sqlalchemy.ForeignKey`
* `sqlalchemy.Integer`
* `sqlalchemy.LargeBinary`
* `sqlalchemy.String`
* `sqlalchemy.Text`
* `sqlalchemy.orm.relationship`
* `sqlalchemy.sql.func`

**Consumers (Who Needs It):**
* `scripts/migrate_document_images.py`
* `src/pillars/document_manager/repositories/document_repository.py`
* `src/pillars/document_manager/repositories/image_repository.py`
* `src/pillars/document_manager/repositories/search_repository.py`
* `src/pillars/document_manager/services/document_service.py`
* `src/pillars/document_manager/services/notebook_service.py`
* `src/pillars/document_manager/ui/document_editor_window.py`
* `src/pillars/document_manager/ui/document_properties_dialog.py`
* `src/pillars/gematria/ui/text_analysis/document_tab.py`
* `src/pillars/gematria/ui/text_analysis/main_window.py`
* `tests/verify_database_manager.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/models/document_verse.py`

**Role:** `[Bone] (Model)`

**Purpose:** Models supporting curated Holy Book verses and parser training.

**Input (Ingests):**
* `id` (Column)
* `document_id` (Column)
* `verse_number` (Column)
* `start_offset` (Column)
* `end_offset` (Column)
* `text` (Column)
* `status` (Column)
* `confidence` (Column)
* `source_type` (Column)
* `rule_id` (Column)
* `notes` (Column)
* `extra_data` (Column)
* `created_at` (Column)
* `updated_at` (Column)
* `id` (Column)
* `scope_type` (Column)
* `scope_value` (Column)
* `description` (Column)
* `pattern_before` (Column)
* `pattern_after` (Column)
* `action` (Column)
* `parameters` (Column)
* `priority` (Column)
* `enabled` (Column)
* `hit_count` (Column)
* `created_at` (Column)
* `updated_at` (Column)
* `id` (Column)
* `document_id` (Column)
* `verse_id` (Column)
* `rule_id` (Column)
* `action` (Column)
* `payload` (Column)
* `notes` (Column)
* `created_at` (Column)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `shared.database.Base`
* `sqlalchemy.Boolean`
* `sqlalchemy.Column`
* `sqlalchemy.DateTime`
* `sqlalchemy.Float`
* `sqlalchemy.ForeignKey`
* `sqlalchemy.Index`
* `sqlalchemy.Integer`
* `sqlalchemy.String`
* `sqlalchemy.Text`
* `sqlalchemy.orm.relationship`
* `sqlalchemy.sql.func`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/services/document_service.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/models/dtos.py`

**Role:** `[Bone] (Model)`

**Purpose:** Data Transfer Objects for Document Manager.

**Input (Ingests):**
* `id` (Field)
* `title` (Field)
* `file_type` (Field)
* `collection` (Field)
* `author` (Field)
* `updated_at` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `dataclasses.dataclass`
* `datetime.datetime`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/repositories/document_repository.py`
* `src/pillars/document_manager/services/document_service.py`
* `src/pillars/document_manager/ui/document_properties_dialog.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/models/notebook.py`

**Role:** `[Bone] (Model)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `id` (Column)
* `title` (Column)
* `description` (Column)
* `created_at` (Column)
* `id` (Column)
* `title` (Column)
* `color` (Column)
* `notebook_id` (Column)
* `created_at` (Column)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `datetime.datetime`
* `shared.database.Base`
* `sqlalchemy.Column`
* `sqlalchemy.DateTime`
* `sqlalchemy.ForeignKey`
* `sqlalchemy.Integer`
* `sqlalchemy.String`
* `sqlalchemy.Text`
* `sqlalchemy.orm.relationship`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/services/notebook_service.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/repositories/document_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Repository for Document model.

**Input (Ingests):**
* `db`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `logging`
* `pillars.document_manager.models.document.Document`
* `pillars.document_manager.models.dtos.DocumentMetadataDTO`
* `sqlalchemy.orm.Session`
* `sqlalchemy.orm.defer`
* `sqlalchemy.orm.load_only`
* `time`
* `typing.Any`
* `typing.List`
* `typing.Optional`
* `typing.cast`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/services/document_service.py`
* `src/pillars/document_manager/services/verse_teacher_service.py`
* `src/pillars/gematria/services/corpus_dictionary_service.py`
* `src/pillars/gematria/ui/acrostics_window.py`
* `src/pillars/gematria/ui/chiastic_window.py`
* `src/pillars/gematria/ui/document_selector.py`

**Key Interactions:**
**Exposes:** `get()` - *Functional interface.*
**Exposes:** `get_by_ids()` - *Functional interface.*
**Exposes:** `get_all()` - *Functional interface.*
**Exposes:** `get_all_metadata()` - *Fetch all documents but only load lightweight metadata fields.*
**Exposes:** `search()` - *Functional interface.*
**Exposes:** `get_by_collection_name()` - *Find documents where the collection name contains the query string (case-insensitive).*
**Exposes:** `create()` - *Functional interface.*
**Exposes:** `update()` - *Functional interface.*
**Exposes:** `delete()` - *Functional interface.*
**Exposes:** `delete_all()` - *Delete all documents from the database.*


---

**File:** `src/pillars/document_manager/repositories/document_verse_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Repository helpers for document verse records.

**Input (Ingests):**
* `db`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `pillars.document_manager.models.DocumentVerse`
* `sqlalchemy.orm.Session`
* `typing.Iterable`
* `typing.List`
* `typing.Optional`
* `typing.Sequence`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/services/document_service.py`
* `src/pillars/document_manager/services/verse_teacher_service.py`

**Key Interactions:**
**Exposes:** `get()` - *Functional interface.*
**Exposes:** `get_by_document()` - *Functional interface.*
**Exposes:** `replace_document_verses()` - *Replace all verse rows for a document with the provided payload.*
**Exposes:** `delete_by_document()` - *Delete all verses tied to a document.*
**Exposes:** `save()` - *Functional interface.*
**Exposes:** `bulk_upsert()` - *Functional interface.*
**Exposes:** `count_for_document()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/repositories/image_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Repository for DocumentImage model.

**Input (Ingests):**
* `db`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `hashlib`
* `pillars.document_manager.models.document.DocumentImage`
* `sqlalchemy.orm.Session`
* `typing.List`
* `typing.Optional`
* `zlib`

**Consumers (Who Needs It):**
* `scripts/migrate_document_images.py`
* `src/pillars/document_manager/services/document_service.py`

**Key Interactions:**
**Exposes:** `get()` - *Get an image by ID.*
**Exposes:** `get_by_document()` - *Get all images for a document.*
**Exposes:** `get_by_hash()` - *Get an image by hash within a document (for deduplication).*
**Exposes:** `create()` - *Create a new image entry.*
**Exposes:** `get_decompressed_data()` - *Get decompressed image data.*
**Exposes:** `delete_by_document()` - *Delete all images for a document.*
**Exposes:** `delete()` - *Delete a specific image.*


---

**File:** `src/pillars/document_manager/repositories/search_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Whoosh-based repository for searching documents.

**Input (Ingests):**
* `index_dir`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `datetime.datetime`
* `os`
* `pathlib.Path`
* `pillars.document_manager.models.document.Document`
* `re`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `whoosh.analysis.StemmingAnalyzer`
* `whoosh.fields.DATETIME`
* `whoosh.fields.ID`
* `whoosh.fields.KEYWORD`
* `whoosh.fields.Schema`
* `whoosh.fields.TEXT`
* `whoosh.index`
* `whoosh.qparser.MultifieldParser`
* `whoosh.qparser.OrGroup`
* `whoosh.query.Term`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/services/document_service.py`
* `tests/document/test_document_search.py`

**Key Interactions:**
**Exposes:** `index_document()` - *Add or update a document in the search index.*
**Exposes:** `index_documents()` - *Add or update multiple documents in the search index efficiently.*
**Exposes:** `delete_document()` - *Remove a document from the search index.*
**Exposes:** `search()` - *Search for documents.*
**Exposes:** `rebuild_index()` - *Rebuild the entire index from a list of documents.*
**Exposes:** `clear_index()` - *Clear the entire search index.*


---

**File:** `src/pillars/document_manager/repositories/verse_edit_log_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Audit log repository for verse teaching actions.

**Input (Ingests):**
* `db`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `pillars.document_manager.models.VerseEditLog`
* `sqlalchemy.orm.Session`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/services/verse_teacher_service.py`

**Key Interactions:**
**Exposes:** `log()` - *Functional interface.*
**Exposes:** `list_recent()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/repositories/verse_rule_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Repository helpers for verse rules.

**Input (Ingests):**
* `db`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `pillars.document_manager.models.VerseRule`
* `sqlalchemy.orm.Session`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/services/verse_teacher_service.py`

**Key Interactions:**
**Exposes:** `get()` - *Functional interface.*
**Exposes:** `list_rules()` - *Functional interface.*
**Exposes:** `get_all_enabled()` - *Functional interface.*
**Exposes:** `save()` - *Functional interface.*
**Exposes:** `delete()` - *Functional interface.*
**Exposes:** `increment_hit()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/services/document_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service layer for Document Manager.

**Input (Ingests):**
* `db`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `contextlib.contextmanager`
* `logging`
* `pathlib.Path`
* `pillars.document_manager.models.document.DocumentImage`
* `pillars.document_manager.models.document.Document`
* `pillars.document_manager.models.document_verse.DocumentVerse`
* `pillars.document_manager.models.dtos.DocumentMetadataDTO`
* `pillars.document_manager.repositories.document_repository.DocumentRepository`
* `pillars.document_manager.repositories.document_verse_repository.DocumentVerseRepository`
* `pillars.document_manager.r

**Consumers (Who Needs It):**
* `scripts/debug_doc_collections.py`
* `scripts/debug_doc_tags.py`
* `src/pillars/document_manager/ui/database_manager.py`
* `src/pillars/document_manager/ui/document_editor_window.py`
* `src/pillars/document_manager/ui/document_library.py`
* `src/pillars/document_manager/ui/document_manager_hub.py`
* `src/pillars/document_manager/ui/document_search_window.py`
* `src/pillars/document_manager/ui/rich_text_editor.py`
* `src/pillars/gematria/ui/els_search_window.py`
* `src/pillars/gematria/ui/text_analysis/main_window.py`
* `tests/document/test_document_service.py`
* `tests/verify_database_manager.py`

**Key Interactions:**
**Exposes:** `document_service_context()` - *Yield a DocumentService backed by a managed DB session.*
**Exposes:** `import_document()` - *Import a document from a file path.*
**Exposes:** `search_documents()` - *Functional interface.*
**Exposes:** `search_documents_with_highlights()` - *Search documents and return results with highlights.*
**Exposes:** `get_all_documents()` - *Functional interface.*
**Exposes:** `get_all_documents_metadata()` - *Get all documents without loading heavy content fields.*
**Exposes:** `get_document()` - *Functional interface.*
**Exposes:** `get_document_with_images()` - *Get a document with images. *
**Exposes:** `get_image()` - *Get an image by ID.*
**Exposes:** `update_document()` - *Update document fields.*
**Exposes:** `update_documents()` - *Update multiple documents efficiently.*
**Exposes:** `delete_document()` - *Functional interface.*
**Exposes:** `delete_all_documents()` - *Delete all documents from database and search index.*
**Exposes:** `rebuild_search_index()` - *Rebuild the search index from the database.*
**Exposes:** `get_database_stats()` - *Get database statistics.*
**Exposes:** `cleanup_orphans()` - *Find and delete orphan images (stored in DB but not used in any document).*
**Exposes:** `get_document_verses()` - *Functional interface.*
**Exposes:** `replace_document_verses()` - *Functional interface.*
**Exposes:** `delete_document_verses()` - *Functional interface.*
**Exposes:** `store_image()` - *Functional interface.*
**Exposes:** `fetch_image()` - *Functional interface.*
**Exposes:** `store_image()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/services/etymology_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Etymology Service for Document Manager Pillar.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `bs4.BeautifulSoup`
* `ety`
* `functools.lru_cache`
* `logging`
* `re`
* `requests`
* `typing.Dict`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_etymology_service()` - *Get the global singleton instance of the EtymologyService.*
**Exposes:** `get_word_origin()` - *Get the origin of a word. Auto-detects script and routes accordingly.*
**Exposes:** `clean_html_text()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/services/notebook_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `db`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `contextlib.contextmanager`
* `logging`
* `pillars.document_manager.models.document.Document`
* `pillars.document_manager.models.notebook.Notebook`
* `pillars.document_manager.models.notebook.Section`
* `shared.database.get_db_session`
* `sqlalchemy.orm.Session`
* `sqlalchemy.orm.joinedload`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `src/pillars/gematria/ui/gematria_calculator_window.py`
* `tests/rituals/rite_of_notebooks.py`

**Key Interactions:**
**Exposes:** `notebook_service_context()` - *Provide a transactional scope for Notebook operations.*
**Exposes:** `get_notebooks_with_structure()` - *Fetch all notebooks with sections eagerly loaded.*
**Exposes:** `get_notebook()` - *Functional interface.*
**Exposes:** `create_notebook()` - *Functional interface.*
**Exposes:** `delete_notebook()` - *Functional interface.*
**Exposes:** `create_section()` - *Functional interface.*
**Exposes:** `delete_section()` - *Functional interface.*
**Exposes:** `get_section_pages()` - *Get all pages (Documents) in a section.*
**Exposes:** `create_page()` - *Create a new document linked to a section.*
**Exposes:** `move_page()` - *Move a page to a different section.*
**Exposes:** `delete_page()` - *Delete a page (Document).*
**Exposes:** `rename_notebook()` - *Functional interface.*
**Exposes:** `rename_section()` - *Functional interface.*
**Exposes:** `rename_page()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/services/spell_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Spell Check Service for Document Manager Pillar.

**Input (Ingests):**
* `language`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `enchant.checker.SpellChecker`
* `enchant`
* `logging`
* `os`
* `pathlib.Path`
* `re`
* `typing.List`
* `typing.Optional`
* `typing.Set`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_spell_service()` - *Get or create the singleton SpellService instance.*
**Exposes:** `is_enabled()` - *Check if spell checking is available and enabled.*
**Exposes:** `check()` - *Check if a word is spelled correctly.*
**Exposes:** `suggest()` - *Get spelling suggestions for a word.*
**Exposes:** `add_to_dictionary()` - *Add a word to the custom dictionary (persistent).*
**Exposes:** `ignore()` - *Ignore a word for this session only.*
**Exposes:** `ignore_all()` - *Ignore all occurrences of a word for this session.*
**Exposes:** `clear_session_ignores()` - *Clear the session ignore list.*
**Exposes:** `get_misspelled_words()` - *Get all misspelled words in text with their positions.*
**Exposes:** `get_available_languages()` - *Get list of available dictionary languages.*
**Exposes:** `set_language()` - *Change the spell check language.*


---

**File:** `src/pillars/document_manager/services/verse_teacher_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service that powers the Holy Book "teacher" workflow.

**Input (Ingests):**
* `db`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `contextlib.contextmanager`
* `json`
* `pillars.document_manager.models.Document`
* `pillars.document_manager.models.VerseRule`
* `pillars.document_manager.repositories.document_repository.DocumentRepository`
* `pillars.document_manager.repositories.document_verse_repository.DocumentVerseRepository`
* `pillars.document_manager.repositories.verse_edit_log_repository.VerseEditLogRepository`
* `pillars.document_manager.repositories.verse_rule_repository.VerseRuleReposit

**Consumers (Who Needs It):**
* `src/pillars/gematria/services/text_analysis_service.py`
* `src/pillars/gematria/ui/holy_book_teacher_window.py`

**Key Interactions:**
**Exposes:** `verse_teacher_service_context()` - *Yield a `VerseTeacherService` wired to a managed DB session.*
**Exposes:** `get_curated_verses()` - *Functional interface.*
**Exposes:** `get_or_parse_verses()` - *Functional interface.*
**Exposes:** `generate_parser_run()` - *Functional interface.*
**Exposes:** `save_curated_verses()` - *Functional interface.*
**Exposes:** `record_rule()` - *Functional interface.*
**Exposes:** `list_rules_for_document()` - *Functional interface.*
**Exposes:** `list_recent_edits()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/ui/canvas/infinite_canvas.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

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
**Exposes:** `add_note_container()` - *Functional interface.*
**Exposes:** `clear_canvas()` - *Functional interface.*
**Exposes:** `add_shape()` - *Add a shape to the canvas.*
**Exposes:** `start_shape_insert()` - *Enter insert mode for shapes.*
**Exposes:** `cancel_shape_insert()` - *Cancel shape insert mode.*
**Exposes:** `mousePressEvent()` - *Handle mouse press - check for shape insert mode.*
**Exposes:** `keyPressEvent()` - *Handle delete key for shapes.*
**Exposes:** `get_json_data()` - *Serialize all items to JSON.*
**Exposes:** `load_json_data()` - *Load items from JSON.*


---

**File:** `src/pillars/document_manager/ui/canvas/note_container.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

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
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Exposes:** `mouseMoveEvent()` - *Functional interface.*
**Exposes:** `mouseReleaseEvent()` - *Functional interface.*
**Emits:** `resize_requested` - *Nervous System Signal.*
**Exposes:** `resizeEvent()` - *Keep resize grip in bottom-right corner.*
**Exposes:** `get_html()` - *Functional interface.*
**Exposes:** `set_html()` - *Functional interface.*
**Exposes:** `set_text()` - *Functional interface.*
**Emits:** `content_changed` - *Nervous System Signal.*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Emits:** `content_changed` - *Nervous System Signal.*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Exposes:** `mouseMoveEvent()` - *Functional interface.*
**Exposes:** `mouseDoubleClickEvent()` - *Functional interface.*
**Exposes:** `mouseReleaseEvent()` - *Functional interface.*
**Exposes:** `hoverEnterEvent()` - *Functional interface.*
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

**File:** `src/pillars/document_manager/ui/dialogs/base_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Base dialog class with common utilities for Rich Text Editor dialogs.

**Input (Ingests):**
* `title`
* `parent`
* `min_width`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtWidgets.QColorDialog`
* `PyQt6.QtWidgets.QDialogButtonBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QVBoxLayout`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `layout()` - *Get the main layout for adding widgets.*
**Exposes:** `add_ok_cancel_buttons()` - *Add standard OK/Cancel buttons to the dialog.*
**Exposes:** `pick_color()` - *Show a color picker dialog and return the selected color.*
**Exposes:** `update_color_button()` - *Update a button's style to show the given color.*
**Exposes:** `create_form_layout()` - *Create and add a form layout to the dialog.*


---

**File:** `src/pillars/document_manager/ui/dialogs/export_pdf_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** PDF export dialog for Rich Text Editor.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QMarginsF`
* `PyQt6.QtGui.QPageLayout`
* `PyQt6.QtGui.QPageSize`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDialogButtonBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QVBoxLayout`
* `page_setup_dialog.PageSetupDialog`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_file_path()` - *Functional interface.*
**Exposes:** `get_page_size()` - *Functional interface.*
**Exposes:** `get_orientation()` - *Functional interface.*
**Exposes:** `get_margins()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/ui/dialogs/horizontal_rule_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Horizontal rule insertion dialog for Rich Text Editor.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QSpinBox`
* `PyQt6.QtWidgets.QToolButton`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `base_dialog.BaseEditorDialog`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_html()` - *Generate HTML for the horizontal rule using a table (better QTextEdit support).*


---

**File:** `src/pillars/document_manager/ui/dialogs/hyperlink_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Hyperlink insertion dialog for Rich Text Editor.

**Input (Ingests):**
* `selected_text`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QDialogButtonBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QVBoxLayout`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/ui/dialogs/page_setup_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Page setup dialog for Rich Text Editor.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QMarginsF`
* `PyQt6.QtGui.QPageLayout`
* `PyQt6.QtGui.QPageSize`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDialogButtonBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QVBoxLayout`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_page_size()` - *Functional interface.*
**Exposes:** `get_orientation()` - *Functional interface.*
**Exposes:** `get_margins()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/ui/dialogs/special_characters_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QStackedWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `char_selected` - *Nervous System Signal.*


---

**File:** `src/pillars/document_manager/ui/document_editor_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

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
* `scripts/reproduce_export_crash.py`
* `src/pillars/gematria/ui/chain_results_window.py`
* `src/pillars/gematria/ui/els_search_window.py`
* `src/pillars/gematria/ui/gematria_calculator_window.py`
* `src/pillars/time_mechanics/ui/zodiacal_circle_window.py`

**Key Interactions:**
**Exposes:** `load_document_model()` - *Load a document from the database model.*
**Exposes:** `new_document()` - *Functional interface.*
**Exposes:** `open_document()` - *Functional interface.*
**Exposes:** `save_document()` - *Functional interface.*
**Exposes:** `save_as_document()` - *Functional interface.*
**Exposes:** `export_pdf()` - *Export the current document to PDF.*
**Exposes:** `closeEvent()` - *Functional interface.*
**Exposes:** `filter_items()` - *Functional interface.*
**Exposes:** `on_item_double_clicked()` - *Functional interface.*


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
**Exposes:** `run()` - *Functional interface.*
**Emits:** `document_opened` - *Nervous System Signal.*
**Exposes:** `toggle_col()` - *Functional interface.*


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
**Exposes:** `get_common_value()` - *Functional interface.*
**Exposes:** `get_update_value()` - *Functional interface.*


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

**File:** `src/pillars/document_manager/ui/editor_constants.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Editor constants and page settings for the Rich Text Editor.

**Input (Ingests):**
* `page_size`
* `margins`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QPageSize`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `page_width_inches()` - *Page width in inches.*
**Exposes:** `page_height_inches()` - *Page height in inches.*
**Exposes:** `content_height_inches()` - *Content height (page height minus top and bottom margins).*
**Exposes:** `content_width_inches()` - *Content width (page width minus left and right margins).*
**Exposes:** `page_height_pixels()` - *Page height in pixels at screen DPI.*
**Exposes:** `content_height_pixels()` - *Content area height in pixels (for page break calculations).*
**Exposes:** `content_width_pixels()` - *Content area width in pixels.*


---

**File:** `src/pillars/document_manager/ui/etymology_feature.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Etymology Feature for Document Manager.

**Input (Ingests):**
* `word`
* `parent`
* `main_editor`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QThread`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QTextCursor`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTextBrowser`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `qtawesome`
* `services.etymology_service.get_etymology_service`
* `shar

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `finished` - *Nervous System Signal.*
**Exposes:** `run()` - *Fetch etymology data from the service.*
**Exposes:** `setup_ui()` - *Initialize and layout visual components.*
**Exposes:** `set_search_callback()` - *Set the function to be called when a search is triggered.*
**Exposes:** `show_loading()` - *Display loading state for a specific word.*
**Exposes:** `show_result()` - *Update browser with research findings.*
**Exposes:** `create_action()` - *Construct the primary Ribbon action for this feature.*
**Exposes:** `research_selection()` - *Commence etymology research based on current editor selection.*
**Exposes:** `extend_context_menu()` - *Add etymology lookup option to the editor context menu.*


---

**File:** `src/pillars/document_manager/ui/font_manager_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

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
**Exposes:** `add_node()` - *Functional interface.*
**Exposes:** `remove_node()` - *Functional interface.*
**Exposes:** `add_edge()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `set_position()` - *Functional interface.*
**Exposes:** `set_fixed()` - *Functional interface.*
**Exposes:** `tick()` - *Step the simulation.*
**Exposes:** `get_position()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/ui/graph_view.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Deprecated knowledge graph placeholder; implementation removed.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* None.

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `removed_knowledge_graph()` - *Placeholder to avoid import errors after removing graph view.*


---

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

**Purpose:** Soul not yet specified.

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
**Exposes:** `get_data()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/ui/list_features.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `editor`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QIcon`
* `PyQt6.QtGui.QTextBlockFormat`
* `PyQt6.QtGui.QTextCursor`
* `PyQt6.QtGui.QTextListFormat`
* `PyQt6.QtWidgets.QDialogButtonBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QSpinBox`
* `PyQt6.QtWidgets.QToolButton`
* `PyQt6.QtWidgets.QVBoxLayout`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/ui/rich_text_editor.py`

**Key Interactions:**
**Exposes:** `toggle_list()` - *Toggle the specified list style for the current selection.*
**Exposes:** `set_list_style_by_name()` - *Set list style using the friendly name.*
**Exposes:** `set_start_number()` - *Set the starting number for a numbered list.*
**Exposes:** `show_start_number_dialog()` - *Show dialog to set the starting number for a list.*
**Exposes:** `remove_list()` - *Remove list formatting from the current selection.*
**Exposes:** `indent()` - *Increase indentation or list level.*
**Exposes:** `outdent()` - *Decrease indentation or list level.*
**Exposes:** `get_current_list_style_name()` - *Get the name of the current list style, or None.*
**Exposes:** `toggle_checklist()` - *Toggle checklist style (☐ / ☑) for the current line(s).*


---

**File:** `src/pillars/document_manager/ui/mindscape_page.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSlot`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QIcon`
* `PyQt6.QtGui.QTextCharFormat`
* `PyQt6.QtGui.QTextListFormat`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QColorDialog`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QFontComboBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushB

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `load_node()` - *Load content from Document.*
**Exposes:** `save_page()` - *Persist changes.*
**Exposes:** `clear()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/ui/mindscape_theme.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

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
**Exposes:** `set_mode()` - *Functional interface.*
**Exposes:** `get_color()` - *Functional interface.*
**Exposes:** `get_font()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/ui/mindscape_tree.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtWidgets.QAbstractItemView`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QTreeWidgetItem`
* `PyQt6.QtWidgets.QTreeWidget`
* `logging`
* `services.notebook_service.notebook_service_context`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `page_selected` - *Nervous System Signal.*
**Exposes:** `load_tree()` - *Reload the entire tree structure.*
**Exposes:** `dropEvent()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/ui/mindscape_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `mindscape_page.MindscapePageWidget`
* `mindscape_tree.MindscapeTreeWidget`

**Consumers (Who Needs It):**
* `src/pillars/gematria/ui/gematria_calculator_window.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/document_manager/ui/ribbon_widget.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `parent`
* `category`
* `panel`
* `gallery`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QIcon`
* `PyQt6.QtWidgets.QSizePolicy`
* `PyQt6.QtWidgets.QWidget`
* `pyqtribbon.RibbonBar`
* `pyqtribbon.RibbonCategoryStyle`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_ribbon.py`
* `tests/verification/verify_ribbon.py`

**Key Interactions:**
**Exposes:** `add_ribbon_tab()` - *Create and add a new category (tab) to the ribbon.*
**Exposes:** `add_context_category()` - *Add a context category (hidden by default).*
**Exposes:** `show_context_category()` - *Show a context category (only if not already visible).*
**Exposes:** `hide_context_category()` - *Hide a context category.*
**Exposes:** `add_file_menu()` - *Add the file menu to the application button.*
**Exposes:** `add_quick_access_button()` - *Add an action to the Quick Access Toolbar.*
**Exposes:** `add_group()` - *Add a labeled group (panel) of actions to this tab.*
**Exposes:** `add_widget()` - *Add a custom widget to the group.*
**Exposes:** `add_action()` - *Add an action as a button.*
**Exposes:** `add_separator()` - *Add a separator.*
**Exposes:** `add_gallery()` - *Add a gallery to the panel.*
**Exposes:** `add_item()` - *Add a button to the gallery.*
**Exposes:** `add_group()` - *Add a grouping (if supported) or just return self.*


---

**File:** `src/pillars/document_manager/ui/rich_text_editor.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Reusable Rich Text Editor widget with Ribbon UI.

**Input (Ingests):**
* `parent`
* `parent`
* `placeholder_text`
* `show_ui`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PIL.ImageEnhance`
* `PIL.ImageFilter`
* `PIL.ImageOps`
* `PIL.Image`
* `PyQt6.QtCore.QBuffer`
* `PyQt6.QtCore.QIODevice`
* `PyQt6.QtCore.QMarginsF`
* `PyQt6.QtCore.QMimeData`
* `PyQt6.QtCore.QPoint`
* `PyQt6.QtCore.QSizeF`
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.QUrl`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QActionGroup`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QDesktopServices`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QImage`
* `P

**Consumers (Who Needs It):**
* `src/pillars/correspondences/ui/spreadsheet_view.py`
* `src/pillars/document_manager/ui/canvas/note_container.py`
* `src/pillars/gematria/ui/saved_calculations_window.py`
* `tests/document/test_document_search.py`
* `tests/verification/verify_alignment_mutex.py`
* `tests/verification/verify_clear_highlight.py`
* `tests/verification/verify_headings.py`
* `tests/verification/verify_headings_gui.py`
* `tests/verification/verify_lists.py`
* `tests/verification/verify_ribbon.py`
* `tests/verify_fixes.py`

**Key Interactions:**
**Exposes:** `page_height()` - *Get page height from settings.*
**Exposes:** `show_page_breaks()` - *Functional interface.*
**Exposes:** `show_page_breaks()` - *Functional interface.*
**Exposes:** `paintEvent()` - *Paint the text, then overlay page break lines.*
**Exposes:** `loadResource()` - *Handle custom resource loading, specifically for docimg:// scheme.*
**Exposes:** `insertFromMimeData()` - *Override paste behavior to protect against freezing.*
**Emits:** `text_changed` - *Nervous System Signal.*
**Emits:** `wiki_link_requested` - *Nervous System Signal.*
**Exposes:** `insertFromMimeData()` - *Override paste behavior to protect against 'Paste Attacks' (Mars Seal).*
**Exposes:** `show_search()` - *Public API for Global Ribbon.*
**Exposes:** `toggle_list()` - *Public API for Global Ribbon.*
**Exposes:** `set_alignment()` - *Public API for Global Ribbon.*
**Exposes:** `insert_table()` - *Public API for Global Ribbon.*
**Exposes:** `insert_image()` - *Public API for Global Ribbon.*
**Exposes:** `set_highlight()` - *Public API for Global Ribbon.*
**Exposes:** `clear_formatting()` - *Public API*
**Exposes:** `toggle_strikethrough()` - *Functional interface.*
**Exposes:** `toggle_subscript()` - *Functional interface.*
**Exposes:** `toggle_superscript()` - *Functional interface.*
**Exposes:** `insert_hyperlink()` - *Open dialog to insert a hyperlink.*
**Exposes:** `page_setup()` - *Open page setup dialog.*
**Exposes:** `insert_horizontal_rule()` - *Insert a horizontal rule.*
**Exposes:** `get_html()` - *Functional interface.*
**Exposes:** `set_html()` - *Functional interface.*
**Exposes:** `get_text()` - *Functional interface.*
**Exposes:** `set_text()` - *Functional interface.*
**Exposes:** `set_markdown()` - *Set the editor content from Markdown.*
**Exposes:** `get_markdown()` - *Get the editor content as Markdown.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `find_text()` - *Find first occurrence of text and select it.*
**Exposes:** `find_all_matches()` - *Count all matches and position cursor at first. Returns match count.*
**Exposes:** `find_next()` - *Navigate to next match. Returns True if found.*
**Exposes:** `find_previous()` - *Navigate to previous match. Returns True if found.*
**Exposes:** `get_match_info()` - *Get current match position info. Returns (current, total).*
**Exposes:** `clear_search()` - *Clear search state.*
**Exposes:** `new_document()` - *Clear the editor for a new document.*
**Exposes:** `open_document()` - *Open a file (Markdown, HTML, Text).*
**Exposes:** `save_document()` - *Save the document (Markdown, HTML, Text).*
**Exposes:** `on_width_changed()` - *Functional interface.*
**Exposes:** `on_height_changed()` - *Functional interface.*
**Exposes:** `update_w_range()` - *Functional interface.*
**Exposes:** `update_h_range()` - *Functional interface.*
**Exposes:** `sepia_pixel()` - *Functional interface.*
**Exposes:** `shift_channel()` - *Functional interface.*
**Exposes:** `shift_channel()` - *Functional interface.*
**Exposes:** `shift_channel()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/ui/search_features.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Search and Replace features for RichTextEditor.

**Input (Ingests):**
* `parent`
* `editor`
* `parent_widget`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QTextCursor`
* `PyQt6.QtGui.QTextDocument`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `find_next_requested` - *Nervous System Signal.*
**Emits:** `find_all_requested` - *Nervous System Signal.*
**Emits:** `replace_requested` - *Nervous System Signal.*
**Emits:** `replace_all_requested` - *Nervous System Signal.*
**Emits:** `navigate_requested` - *Nervous System Signal.*
**Exposes:** `set_not_found_state()` - *Functional interface.*
**Exposes:** `show_results()` - *Display list of results.*
**Exposes:** `show_search_dialog()` - *Open (and create if needed) the search dialog.*
**Exposes:** `find_next()` - *Find next occurrence of text.*
**Exposes:** `find_all()` - *Find all occurrences and populate results list.*
**Exposes:** `navigate_to()` - *Jump cursor to specific position.*
**Exposes:** `replace_current()` - *Replace current selection if it matches, then find next.*
**Exposes:** `replace_all()` - *Replace all occurrences.*


---

**File:** `src/pillars/document_manager/ui/search_results_panel.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

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

**File:** `src/pillars/document_manager/ui/shape_features.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Shape insertion feature for the Rich Text Editor.

**Input (Ingests):**
* `shape_name`
* `shape_class`
* `parent`
* `parent`
* `parent`
* `shape`
* `parent`
* `editor`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QEvent`
* `PyQt6.QtCore.QObject`
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QRectF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QIcon`
* `PyQt6.QtGui.QPainterPath`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QPixmap`
* `PyQt6.QtGui.QPolygonF`
* `PyQt6.QtWidgets.QColorDialog`
* `PyQt6.QtWidgets.QDialogButtonBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtW

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_config()` - *Return (sides, skip) configuration.*
**Emits:** `shape_selected` - *Nervous System Signal.*
**Exposes:** `get_selected_type()` - *Return the selected shape type.*
**Exposes:** `accept()` - *Apply changes and close.*
**Exposes:** `eventFilter()` - *Handle editor resize to update overlay.*
**Exposes:** `create_toolbar_button()` - *Create a toolbar button with shape menu.*
**Exposes:** `show_shape_picker()` - *Show the shape picker dialog.*
**Exposes:** `show_properties()` - *Show properties dialog for selected shape.*
**Exposes:** `get_shapes_data()` - *Get serialized shapes data.*
**Exposes:** `load_shapes_data()` - *Load shapes from serialized data.*
**Exposes:** `clear_shapes()` - *Remove all shapes.*
**Exposes:** `custom_press()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/ui/shape_item.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Shape items for the Rich Text Editor overlay.

**Input (Ingests):**
* `position`
* `parent`
* `x`
* `y`
* `width`
* `height`
* `x`
* `y`
* `width`
* `height`
* `x`
* `y`
* `width`
* `height`
* `x`
* `y`
* `width`
* `height`
* `x`
* `y`
* `width`
* `height`
* `x`
* `y`
* `width`
* `height`
* `x`
* `y`
* `width`
* `height`
* `sides`
* `skip`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QLineF`
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QRectF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QCursor`
* `PyQt6.QtGui.QPainterPath`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QPolygonF`
* `PyQt6.QtWidgets.QColorDialog`
* `PyQt6.QtWidgets.QGraphicsEllipseItem`
* `PyQt6.QtWidgets.QGraphicsItem`
* `PyQt6.QtWidgets.QGraphicsLineItem`
* `PyQt6.QtWidgets.QGraphicsPathItem`
* `PyQt6.QtWidgets.QGraphicsPolygonItem`
* `PyQt6.Qt

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `create_shape_from_dict()` - *Factory function to create shape from dictionary.*
**Exposes:** `boundingRect()` - *Return the bounding rectangle.*
**Exposes:** `itemChange()` - *Handle item changes.*
**Exposes:** `mousePressEvent()` - *Handle mouse press for resize.*
**Exposes:** `mouseMoveEvent()` - *Handle mouse move for resize.*
**Exposes:** `mouseReleaseEvent()` - *Handle mouse release.*
**Exposes:** `contextMenuEvent()` - *Show right-click context menu.*
**Exposes:** `fill_color()` - *Functional interface.*
**Exposes:** `fill_color()` - *Functional interface.*
**Exposes:** `stroke_color()` - *Functional interface.*
**Exposes:** `stroke_color()` - *Functional interface.*
**Exposes:** `stroke_width()` - *Functional interface.*
**Exposes:** `stroke_width()` - *Functional interface.*
**Exposes:** `to_dict()` - *Serialize shape to dictionary.*
**Exposes:** `from_dict()` - *Create shape from dictionary.*
**Exposes:** `corner_radius()` - *Functional interface.*
**Exposes:** `corner_radius()` - *Functional interface.*
**Exposes:** `paint()` - *Functional interface.*
**Exposes:** `paint()` - *Functional interface.*
**Exposes:** `paint()` - *Functional interface.*
**Exposes:** `angle()` - *Functional interface.*
**Exposes:** `angle()` - *Functional interface.*
**Exposes:** `mousePressEvent()` - *Handle mouse press - check for rotation vs resize.*
**Exposes:** `mouseMoveEvent()` - *Handle mouse move for rotation or resize.*
**Exposes:** `boundingRect()` - *Override to include end decorations in bounding rect.*
**Exposes:** `start_style()` - *Functional interface.*
**Exposes:** `start_style()` - *Functional interface.*
**Exposes:** `end_style()` - *Functional interface.*
**Exposes:** `end_style()` - *Functional interface.*
**Exposes:** `start_arrow()` - *Functional interface.*
**Exposes:** `start_arrow()` - *Functional interface.*
**Exposes:** `end_arrow()` - *Functional interface.*
**Exposes:** `end_arrow()` - *Functional interface.*
**Exposes:** `paint()` - *Functional interface.*
**Exposes:** `to_dict()` - *Functional interface.*
**Exposes:** `from_dict()` - *Functional interface.*
**Exposes:** `contextMenuEvent()` - *Extended context menu with end style options.*
**Exposes:** `sides()` - *Functional interface.*
**Exposes:** `sides()` - *Functional interface.*
**Exposes:** `skip()` - *Functional interface.*
**Exposes:** `skip()` - *Functional interface.*
**Exposes:** `is_star()` - *True if this is a star polygon (skip > 1).*
**Exposes:** `paint()` - *Functional interface.*
**Exposes:** `to_dict()` - *Serialize shape to dictionary.*
**Exposes:** `from_dict()` - *Create shape from dictionary.*
**Exposes:** `contextMenuEvent()` - *Extended context menu with polygon-specific options.*


---

**File:** `src/pillars/document_manager/ui/shape_overlay.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Shape overlay for the Rich Text Editor.

**Input (Ingests):**
* `parent`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QEvent`
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QMouseEvent`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QGraphicsScene`
* `PyQt6.QtWidgets.QGraphicsView`
* `PyQt6.QtWidgets.QWidget`
* `shape_item.ArrowShapeItem`
* `shape_item.BaseShapeItem`
* `shape_item.EllipseShapeItem`
* `shape_item.LineShapeItem`
* `shape_item.RectShapeItem`
* `shape_item.TriangleShapeItem`
* `shape_item.c

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `shape_selected` - *Nervous System Signal.*
**Exposes:** `eventFilter()` - *Filter events from parent to detect shape hover.*
**Exposes:** `mousePressEvent()` - *Handle mouse press.*
**Exposes:** `mouseReleaseEvent()` - *Handle mouse release.*
**Exposes:** `mouseMoveEvent()` - *Handle mouse move.*
**Exposes:** `keyPressEvent()` - *Handle key press for shape deletion.*
**Exposes:** `add_shape()` - *Add a shape to the overlay.*
**Exposes:** `remove_shape()` - *Remove a shape from the overlay.*
**Exposes:** `get_shapes()` - *Get all shapes in the overlay.*
**Exposes:** `get_selected_shapes()` - *Get currently selected shapes.*
**Exposes:** `clear_shapes()` - *Remove all shapes.*
**Exposes:** `start_insert_mode()` - *Enter insert mode - next click will create a shape.*
**Exposes:** `cancel_insert_mode()` - *Cancel insert mode.*
**Exposes:** `to_list()` - *Serialize all shapes to a list of dictionaries.*
**Exposes:** `from_list()` - *Load shapes from a list of dictionaries.*
**Exposes:** `resizeEvent()` - *Handle resize to match parent.*


---

**File:** `src/pillars/document_manager/ui/spell_feature.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Spell Check Feature for Document Manager.

**Input (Ingests):**
* `document`
* `enabled`
* `editor`
* `parent`
* `main_editor`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QSyntaxHighlighter`
* `PyQt6.QtGui.QTextCharFormat`
* `PyQt6.QtGui.QTextCursor`
* `PyQt6.QtGui.QTextDocument`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTextEdit`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `enabled()` - *Functional interface.*
**Exposes:** `enabled()` - *Functional interface.*
**Exposes:** `highlightBlock()` - *Called for each text block to apply highlighting.*
**Exposes:** `start_check()` - *Start checking from the beginning of the document.*
**Exposes:** `enabled()` - *Functional interface.*
**Exposes:** `enabled()` - *Functional interface.*
**Exposes:** `toggle()` - *Toggle spell checking on/off.*
**Exposes:** `create_ribbon_action()` - *Create action for the ribbon.*
**Exposes:** `create_toggle_action()` - *Create toggle action for enabling/disabling spell check.*
**Exposes:** `show_dialog()` - *Show the spell check dialog.*
**Exposes:** `extend_context_menu()` - *Add spelling suggestions to context menu if cursor is on misspelled word.*


---

**File:** `src/pillars/document_manager/ui/table_features.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Table management features for RichTextEditor.

**Input (Ingests):**
* `parent`
* `fmt`
* `parent`
* `fmt`
* `parent`
* `fmt`
* `parent`
* `length`
* `parent`
* `editor`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QTextCharFormat`
* `PyQt6.QtGui.QTextCursor`
* `PyQt6.QtGui.QTextFrameFormat`
* `PyQt6.QtGui.QTextLength`
* `PyQt6.QtGui.QTextTableCellFormat`
* `PyQt6.QtGui.QTextTableFormat`
* `PyQt6.QtWidgets.QColorDialog`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDialogButtonBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QDoubleSpinBox`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QHBox

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_data()` - *Functional interface.*
**Exposes:** `apply_to_format()` - *Functional interface.*
**Exposes:** `apply_to_format()` - *Apply the border settings to the cell format.*
**Exposes:** `apply_to_format()` - *Functional interface.*
**Exposes:** `get_length()` - *Functional interface.*
**Exposes:** `create_toolbar_button()` - *Create and configure the toolbar button for tables.*
**Exposes:** `extend_context_menu()` - *Add table actions to a context menu.*
**Exposes:** `insert_table()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/utils/image_utils.py`

**Role:** `[Tool] (Utility)`

**Purpose:** Image extraction utilities for document processing.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base64`
* `hashlib`
* `re`
* `typing.Callable`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `scripts/migrate_document_images.py`
* `src/pillars/document_manager/services/document_service.py`
* `tests/verify_image_utils.py`

**Key Interactions:**
**Exposes:** `extract_images_from_html()` - *Extract base64 images from HTML and replace with docimg:// references.*
**Exposes:** `restore_images_in_html()` - *Replace docimg:// references with actual base64 data for display.*
**Exposes:** `has_embedded_images()` - *Check if HTML contains embedded base64 images.*
**Exposes:** `has_docimg_references()` - *Check if HTML contains docimg:// references.*
**Exposes:** `count_embedded_images()` - *Count the number of embedded base64 images in HTML.*
**Exposes:** `replace_image()` - *Functional interface.*
**Exposes:** `replace_docimg()` - *Functional interface.*


---

**File:** `src/pillars/document_manager/utils/parsers.py`

**Role:** `[Tool] (Utility)`

**Purpose:** File parsing utilities for document import.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base64`
* `docx`
* `fitz`
* `html.parser.HTMLParser`
* `io`
* `mammoth`
* `os`
* `pathlib.Path`
* `pdf2docx.Converter`
* `pypdf`
* `striprtf.striprtf.rtf_to_text`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/services/document_service.py`
* `tests/manual_metadata_test.py`
* `tests/mock_metadata_test.py`
* `tests/verify_fixes.py`
* `tests/verify_list_parsing.py`

**Key Interactions:**
**Exposes:** `handle_data()` - *Functional interface.*
**Exposes:** `handle_starttag()` - *Functional interface.*
**Exposes:** `handle_endtag()` - *Functional interface.*
**Exposes:** `get_text()` - *Functional interface.*
**Exposes:** `parse_file()` - *Parse a file and return (content_text, raw_html, file_type, metadata).*
