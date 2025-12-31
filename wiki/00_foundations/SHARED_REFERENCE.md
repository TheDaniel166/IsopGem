---

**File:** `src/shared/database.py`

**Role:** `[Scout]`

**Purpose:** Shared database connection and session management.

**Input (Ingests):**
* Not yet audited.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `contextlib.contextmanager`
* `os`
* `pathlib.Path`
* `pillars.correspondences.models.correspondence_models`
* `pillars.document_manager.models`
* `re`
* `shared.paths.get_data_path`
* `sqlalchemy.create_engine`
* `sqlalchemy.event`
* `sqlalchemy.orm.declarative_base`
* `sqlalchemy.orm.sessionmaker`

**Consumers (Who Needs It):**
* `scripts/init_mindscape_db.py`
* `scripts/migrate_document_images.py`
* `scripts/migrate_gematria_whoosh_to_sqlite.py`
* `scripts/reproduce_crash_full.py`
* `scripts/verify_send_to.py`
* `scripts/wipe_mindscape.py`
* `src/main.py`
* `src/pillars/astrology/models/chart_record.py`
* `src/pillars/astrology/services/chart_storage_service.py`
* `src/pillars/correspondences/models/correspondence_models.py`
* `src/pillars/correspondences/ui/correspondence_hub.py`
* `src/pillars/document_manager/models/document.py`
* `src/pillars/document_manager/models/document_verse.py`
* `src/pillars/document_manager/models/notebook.py`
* `src/pillars/document_manager/services/document_service.py`
* `src/pillars/document_manager/services/notebook_service.py`
* `src/pillars/document_manager/services/verse_teacher_service.py`
* `src/pillars/gematria/models/calculation_entity.py`
* `src/pillars/gematria/repositories/sqlite_calculation_repository.py`
* `src/pillars/gematria/services/corpus_dictionary_service.py`
* `src/pillars/gematria/ui/acrostics_window.py`
* `src/pillars/gematria/ui/chiastic_window.py`
* `src/pillars/gematria/ui/document_selector.py`
* `src/pillars/tq/ui/quadset_analysis_window.py`
* `src/scripts/reset_mindscape_db.py`
* `tests/_legacy/test_db_persistence.py`
* `tests/_legacy/test_graph_persistence.py`
* `tests/_legacy/test_search_isolation.py`
* `tests/_legacy/test_search_logic.py`
* `tests/_legacy/test_search_panel.py`
* `tests/_legacy/test_wipe.py`
* `tests/astrology/test_chart_storage_service.py`
* `tests/document/test_document_service.py`
* `tests/gematria/test_sqlite_repository.py`
* `tests/rituals/rite_of_genesis_verification.py`
* `tests/rituals/rite_of_mindscape_tree.py`
* `tests/rituals/rite_of_notebooks.py`
* `tests/rituals/rite_of_search.py`
* `tests/verify_database_manager.py`

**Key Interactions:**
**Exposes:** `sqlite_regexp()` - *Functional interface.*
**Exposes:** `init_db()` - *Initialize the database tables.*
**Exposes:** `get_db()` - *Dependency for getting a database session.*
**Exposes:** `get_db_session()` - *Context manager wrapper around get_db() that always closes the session.*
**Exposes:** `regexp()` - *Functional interface.*










---

**File:** `src/shared/database.py`

**Role:** `[Scout]`

**Purpose:** Shared database connection and session management.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `contextlib.contextmanager`
* `os`
* `pathlib.Path`
* `pillars.correspondences.models.correspondence_models`
* `pillars.document_manager.models`
* `re`
* `shared.paths.get_data_path`
* `sqlalchemy.create_engine`
* `sqlalchemy.event`
* `sqlalchemy.orm.declarative_base`
* `sqlalchemy.orm.sessionmaker`

**Consumers (Who Needs It):**
* `scripts/init_mindscape_db.py`
* `scripts/migrate_document_images.py`
* `scripts/migrate_gematria_whoosh_to_sqlite.py`
* `scripts/verify_send_to.py`
* `scripts/wipe_mindscape.py`
* `src/main.py`
* `src/pillars/astrology/models/chart_record.py`
* `src/pillars/astrology/services/chart_storage_service.py`
* `src/pillars/correspondences/models/correspondence_models.py`
* `src/pillars/correspondences/ui/correspondence_hub.py`
* `src/pillars/gematria/repositories/sqlite_calculation_repository.py`
* `src/pillars/gematria/services/corpus_dictionary_service.py`
* `src/pillars/gematria/ui/acrostics_window.py`
* `src/pillars/gematria/ui/chiastic_window.py`
* `src/pillars/gematria/ui/document_selector.py`
* `src/pillars/tq/ui/quadset_analysis_window.py`
* `src/scripts/reset_mindscape_db.py`
* `src/shared/models/document_manager/document.py`
* `src/shared/models/document_manager/document_verse.py`
* `src/shared/models/document_manager/notebook.py`
* `src/shared/models/gematria.py`
* `src/shared/services/document_manager/document_service.py`
* `src/shared/services/document_manager/notebook_service.py`
* `src/shared/services/document_manager/verse_teacher_service.py`
* `tests/_legacy/test_db_persistence.py`
* `tests/_legacy/test_graph_persistence.py`
* `tests/_legacy/test_search_isolation.py`
* `tests/_legacy/test_search_logic.py`
* `tests/_legacy/test_search_panel.py`
* `tests/_legacy/test_wipe.py`
* `tests/astrology/test_chart_storage_service.py`
* `tests/document/test_document_service.py`
* `tests/gematria/test_sqlite_repository.py`
* `tests/rituals/rite_of_genesis_verification.py`
* `tests/rituals/rite_of_mindscape_tree.py`
* `tests/rituals/rite_of_notebooks.py`
* `tests/rituals/rite_of_search.py`
* `tests/verify_database_manager.py`

**Key Interactions:**
**Exposes:** `sqlite_regexp()` - *Sqlite regexp logic.*
**Exposes:** `init_db()` - *Initialize the database tables.*
**Exposes:** `get_db()` - *Dependency for getting a database session.*
**Exposes:** `get_db_session()` - *Context manager wrapper around get_db() that always closes the session.*
**Exposes:** `regexp()` - *Regexp logic.*


---

**File:** `src/shared/logging_config.py`

**Role:** `[Scout]`

**Purpose:** Centralized logging configuration for IsopGem.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `logging.handlers`
* `logging`
* `pathlib.Path`
* `sys`

**Consumers (Who Needs It):**
* `scripts/verify_horizon_phase4.py`

**Key Interactions:**
**Exposes:** `configure_logging()` - *Configure root logger with Console and RotatingFile handlers.*


---

**File:** `src/shared/models/document_manager/document.py`

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
* `src/pillars/document_manager/models/document.py`
* `src/pillars/gematria/ui/text_analysis/document_tab.py`
* `src/pillars/gematria/ui/text_analysis/main_window.py`
* `src/shared/repositories/document_manager/document_repository.py`
* `src/shared/repositories/document_manager/image_repository.py`
* `src/shared/repositories/document_manager/search_repository.py`
* `src/shared/services/document_manager/document_service.py`
* `src/shared/services/document_manager/notebook_service.py`
* `src/shared/services/document_manager/verse_teacher_service.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/shared/models/document_manager/document_verse.py`

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
* `src/pillars/document_manager/models/document_verse.py`
* `src/shared/repositories/document_manager/document_verse_repository.py`
* `src/shared/repositories/document_manager/verse_edit_log_repository.py`
* `src/shared/repositories/document_manager/verse_rule_repository.py`
* `src/shared/services/document_manager/document_service.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/shared/models/document_manager/dtos.py`

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
* `src/pillars/document_manager/models/dtos.py`
* `src/shared/repositories/document_manager/document_repository.py`
* `src/shared/services/document_manager/document_service.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/shared/models/document_manager/notebook.py`

**Role:** `[Bone] (Model)`

**Purpose:** Notebook Models - The Mindscape Structure.

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
* `src/pillars/document_manager/models/notebook.py`
* `src/shared/services/document_manager/notebook_service.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/shared/models/gematria.py`

**Role:** `[Bone] (Model)`

**Purpose:** Shared Gematria Models.

**Input (Ingests):**
* `text` (Field)
* `value` (Field)
* `language` (Field)
* `method` (Field)
* `id` (Field)
* `date_created` (Field)
* `date_modified` (Field)
* `notes` (Field)
* `source` (Field)
* `tags` (Field)
* `breakdown` (Field)
* `character_count` (Field)
* `normalized_text` (Field)
* `user_rating` (Field)
* `is_favorite` (Field)
* `category` (Field)
* `related_ids` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `dataclasses.field`
* `datetime.datetime`
* `json`
* `shared.database.Base`
* `sqlalchemy.String`
* `sqlalchemy.Text`
* `sqlalchemy.orm.Mapped`
* `sqlalchemy.orm.mapped_column`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.TYPE_CHECKING`
* `uuid`

**Consumers (Who Needs It):**
* `src/pillars/gematria/models/calculation_entity.py`
* `src/pillars/gematria/models/calculation_record.py`
* `src/pillars/tq/ui/quadset_analysis_window.py`

**Key Interactions:**
**Exposes:** `to_dict()` - *Convert to dictionary for storage.*
**Exposes:** `from_dict()` - *Create from dictionary.*
**Exposes:** `update_from_record()` - *Populate entity fields from a `CalculationRecord`.*
**Exposes:** `to_record()` - *Convert this entity into a `CalculationRecord`.*


---

**File:** `src/shared/models/time/thelemic_calendar_models.py`

**Role:** `[Bone] (Model)`

**Purpose:** Thelemic Calendar Models - Data Transfer Objects for the Zodiacal Circle.

**Input (Ingests):**
* `ditrune` (Field)
* `contrune` (Field)
* `difference` (Field)
* `zodiacal` (Field)
* `gregorian_date` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `dataclasses.dataclass`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/time_mechanics/models/thelemic_calendar_models.py`
* `src/shared/services/time/thelemic_calendar_service.py`

**Key Interactions:**
**Exposes:** `is_prime_ditrune()` - *True if this is one of the 4 Prime Ditrune Sets (intercalary days).*
**Exposes:** `sign_letter()` - *Extract the zodiac sign letter (A-L) or None for Prime Ditrunes.*
**Exposes:** `sign_day()` - *Extract the day within the sign (0-29) or None for Prime Ditrunes.*


---

**File:** `src/shared/paths.py`

**Role:** `[Scout]`

**Purpose:** Centralized path management for IsopGem.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pathlib.Path`
* `sys`

**Consumers (Who Needs It):**
* `src/shared/database.py`

**Key Interactions:**
**Exposes:** `is_frozen()` - *Check if the application is running in a frozen (packaged) state.*
**Exposes:** `get_app_root()` - *Get the application root directory.*
**Exposes:** `get_project_root()` - *Get the project root directory.*
**Exposes:** `get_resource_path()` - *Get the absolute path to a resource file.*
**Exposes:** `get_data_path()` - *Get the path for data files (like the database).*
**Exposes:** `get_ephemeris_path()` - *Locate an ephemeris file.*


---

**File:** `src/shared/repositories/document_manager/document_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Repository for Document model.

**Input (Ingests):**
* `db`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `logging`
* `shared.models.document_manager.document.Document`
* `shared.models.document_manager.dtos.DocumentMetadataDTO`
* `sqlalchemy.orm.Session`
* `sqlalchemy.orm.defer`
* `sqlalchemy.orm.load_only`
* `time`
* `typing.Any`
* `typing.List`
* `typing.Optional`
* `typing.cast`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/repositories/document_repository.py`
* `src/pillars/gematria/services/corpus_dictionary_service.py`
* `src/pillars/gematria/ui/acrostics_window.py`
* `src/pillars/gematria/ui/chiastic_window.py`
* `src/pillars/gematria/ui/document_selector.py`
* `src/shared/services/document_manager/document_service.py`
* `src/shared/services/document_manager/verse_teacher_service.py`

**Key Interactions:**
**Exposes:** `get()` - *Retrieve logic.*
**Exposes:** `get_by_ids()` - *Retrieve by ids logic.*
**Exposes:** `get_all()` - *Retrieve all logic.*
**Exposes:** `get_all_metadata()` - *Fetch all documents but only load lightweight metadata fields.*
**Exposes:** `search()` - *Search logic.*
**Exposes:** `get_by_collection_name()` - *Find documents where the collection name contains the query string (case-insensitive).*
**Exposes:** `create()` - *Create logic.*
**Exposes:** `update()` - *Update logic.*
**Exposes:** `delete()` - *Remove logic.*
**Exposes:** `delete_all()` - *Delete all documents from the database.*


---

**File:** `src/shared/repositories/document_manager/document_verse_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Repository helpers for document verse records.

**Input (Ingests):**
* `db`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `shared.models.document_manager.document_verse.DocumentVerse`
* `sqlalchemy.orm.Session`
* `typing.Iterable`
* `typing.List`
* `typing.Optional`
* `typing.Sequence`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/repositories/document_verse_repository.py`
* `src/shared/services/document_manager/document_service.py`
* `src/shared/services/document_manager/verse_teacher_service.py`

**Key Interactions:**
**Exposes:** `get()` - *Retrieve logic.*
**Exposes:** `get_by_document()` - *Retrieve by document logic.*
**Exposes:** `replace_document_verses()` - *Replace all verse rows for a document with the provided payload.*
**Exposes:** `delete_by_document()` - *Delete all verses tied to a document.*
**Exposes:** `save()` - *Save logic.*
**Exposes:** `bulk_upsert()` - *Bulk upsert logic.*
**Exposes:** `count_for_document()` - *Count for document logic.*


---

**File:** `src/shared/repositories/document_manager/image_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Repository for DocumentImage model.

**Input (Ingests):**
* `db`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `hashlib`
* `shared.models.document_manager.document.DocumentImage`
* `sqlalchemy.orm.Session`
* `typing.List`
* `typing.Optional`
* `zlib`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/repositories/image_repository.py`
* `src/shared/services/document_manager/document_service.py`

**Key Interactions:**
**Exposes:** `get()` - *Get an image by ID.*
**Exposes:** `get_by_document()` - *Get all images for a document.*
**Exposes:** `get_by_hash()` - *Get an image by hash within a document (for deduplication).*
**Exposes:** `create()` - *Create a new image entry.*
**Exposes:** `get_decompressed_data()` - *Get decompressed image data.*
**Exposes:** `delete_by_document()` - *Delete all images for a document.*
**Exposes:** `delete()` - *Delete a specific image.*


---

**File:** `src/shared/repositories/document_manager/search_repository.py`

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
* `re`
* `shared.models.document_manager.document.Document`
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
* `src/pillars/document_manager/repositories/search_repository.py`
* `src/shared/services/document_manager/document_service.py`

**Key Interactions:**
**Exposes:** `index_document()` - *Add or update a document in the search index.*
**Exposes:** `index_documents()` - *Add or update multiple documents in the search index efficiently.*
**Exposes:** `delete_document()` - *Remove a document from the search index.*
**Exposes:** `search()` - *Search for documents.*
**Exposes:** `rebuild_index()` - *Rebuild the entire index from a list of documents.*
**Exposes:** `clear_index()` - *Clear the entire search index.*


---

**File:** `src/shared/repositories/document_manager/verse_edit_log_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Audit log repository for verse teaching actions.

**Input (Ingests):**
* `db`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `shared.models.document_manager.document_verse.VerseEditLog`
* `sqlalchemy.orm.Session`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/repositories/verse_edit_log_repository.py`
* `src/shared/services/document_manager/verse_teacher_service.py`

**Key Interactions:**
**Exposes:** `log()` - *Log logic.*
**Exposes:** `list_recent()` - *List recent logic.*


---

**File:** `src/shared/repositories/document_manager/verse_rule_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Repository helpers for verse rules.

**Input (Ingests):**
* `db`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `shared.models.document_manager.document_verse.VerseRule`
* `sqlalchemy.orm.Session`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/repositories/verse_rule_repository.py`
* `src/shared/services/document_manager/verse_teacher_service.py`

**Key Interactions:**
**Exposes:** `get()` - *Retrieve logic.*
**Exposes:** `list_rules()` - *List rules logic.*
**Exposes:** `get_all_enabled()` - *Retrieve all enabled logic.*
**Exposes:** `save()` - *Save logic.*
**Exposes:** `delete()` - *Remove logic.*
**Exposes:** `increment_hit()` - *Increment hit logic.*


---

**File:** `src/shared/services/astro_glyph_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Astrological Glyph Service - Centralized font-agnostic symbol provider.

**Input (Ingests):**
* `name` (Field)
* `zodiac_map` (Field)
* `planet_map` (Field)
* `degree_symbol` (Field)
* `minute_symbol` (Field)
* `use_font_numbers` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QFontDatabase`
* `__future__.annotations`
* `dataclasses.dataclass`
* `typing.Dict`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/astrology/ui/chariot_canvas.py`
* `src/pillars/astrology/ui/chariot_differentials_window.py`

**Key Interactions:**
**Exposes:** `get_font_family()` - *Return the font family name to use for glyphs.*
**Exposes:** `is_using_astronomicon()` - *Check if Astronomicon font is active.*
**Exposes:** `get_zodiac_glyph()` - *Get the glyph for a zodiac sign.*
**Exposes:** `get_planet_glyph()` - *Get the glyph for a planet.*
**Exposes:** `get_degree_symbol()` - *Get the degree symbol for current font.*
**Exposes:** `get_minute_symbol()` - *Get the minute symbol for current font.*
**Exposes:** `get_zodiac_name_from_degree()` - *Get the zodiac sign name from an absolute degree.*
**Exposes:** `to_zodiacal_string()` - *Convert absolute degree to zodiacal string with font-appropriate symbols.*


---

**File:** `src/shared/services/document_manager/document_service.py`

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
* `re`
* `shared.database.get_db_session`
* `shared.models.document_manager.document.DocumentImage`
* `shared.models.document_manager.document.Document`
* `shared.models.document_manager.document_verse.DocumentVerse`
* `shared.models.document_manager.dtos.DocumentMetadataDTO`
* `shared.repositories.document_manager.document_repository.DocumentRepository`
* `shared.repositories.document_manager.document_verse_repository.DocumentVerseRepos

**Consumers (Who Needs It):**
* `src/pillars/document_manager/services/document_service.py`
* `src/pillars/gematria/ui/els_search_window.py`
* `src/pillars/gematria/ui/text_analysis/main_window.py`

**Key Interactions:**
**Exposes:** `document_service_context()` - *Yield a DocumentService backed by a managed DB session.*
**Exposes:** `import_document()` - *Import a document from a file path.*
**Exposes:** `search_documents()` - *Search documents logic.*
**Exposes:** `search_documents_with_highlights()` - *Search documents and return results with highlights.*
**Exposes:** `get_all_documents()` - *Retrieve all documents logic.*
**Exposes:** `get_all_documents_metadata()` - *Get all documents without loading heavy content fields.*
**Exposes:** `get_document()` - *Retrieve document logic.*
**Exposes:** `get_document_with_images()` - *Get a document with images. *
**Exposes:** `get_image()` - *Get an image by ID.*
**Exposes:** `update_document()` - *Update document fields.*
**Exposes:** `update_documents()` - *Update multiple documents efficiently.*
**Exposes:** `delete_document()` - *Remove document logic.*
**Exposes:** `delete_all_documents()` - *Delete all documents from database and search index.*
**Exposes:** `rebuild_search_index()` - *Rebuild the search index from the database.*
**Exposes:** `get_database_stats()` - *Get database statistics.*
**Exposes:** `cleanup_orphans()` - *Find and delete orphan images (stored in DB but not used in any document).*
**Exposes:** `get_document_verses()` - *Retrieve document verses logic.*
**Exposes:** `replace_document_verses()` - *Replace document verses logic.*
**Exposes:** `delete_document_verses()` - *Remove document verses logic.*
**Exposes:** `store_image()` - *Store image logic.*
**Exposes:** `fetch_image()` - *Fetch image logic.*
**Exposes:** `store_image()` - *Store image logic.*


---

**File:** `src/shared/services/document_manager/etymology_service.py`

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
* `src/pillars/document_manager/services/etymology_service.py`
* `src/shared/ui/rich_text_editor/etymology_feature.py`

**Key Interactions:**
**Exposes:** `get_etymology_service()` - *Get the global singleton instance of the EtymologyService.*
**Exposes:** `get_word_origin()` - *Get the origin of a word. Auto-detects script and routes accordingly.*
**Exposes:** `clean_html_text()` - *Clean html text logic.*


---

**File:** `src/shared/services/document_manager/notebook_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Notebook Service - The Mindscape Navigator.

**Input (Ingests):**
* `page_id` (Field)
* `title` (Field)
* `snippet` (Field)
* `notebook_name` (Field)
* `section_name` (Field)
* `db`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `contextlib.contextmanager`
* `dataclasses.dataclass`
* `json`
* `logging`
* `shared.database.get_db_session`
* `shared.models.document_manager.document.Document`
* `shared.models.document_manager.notebook.Notebook`
* `shared.models.document_manager.notebook.Section`
* `sqlalchemy.or_`
* `sqlalchemy.orm.Session`
* `sqlalchemy.orm.joinedload`
* `typing.Generator`
* `typing.Iterator`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/services/notebook_service.py`
* `src/pillars/gematria/ui/gematria_calculator_window.py`

**Key Interactions:**
**Exposes:** `notebook_service_context()` - *Provide a transactional scope for Notebook operations.*
**Exposes:** `get_notebooks_with_structure()` - *Fetch all notebooks with sections eagerly loaded.*
**Exposes:** `get_notebook()` - *Retrieve notebook logic.*
**Exposes:** `create_notebook()` - *Create notebook logic.*
**Exposes:** `delete_notebook()` - *Remove notebook logic.*
**Exposes:** `create_section()` - *Create section logic.*
**Exposes:** `delete_section()` - *Remove section logic.*
**Exposes:** `get_section_pages()` - *Get all pages (Documents) in a section.*
**Exposes:** `create_page()` - *Create a new document linked to a section.*
**Exposes:** `move_page()` - *Move a page to a different section.*
**Exposes:** `delete_page()` - *Delete a page (Document).*
**Exposes:** `rename_notebook()` - *Rename notebook logic.*
**Exposes:** `rename_section()` - *Rename section logic.*
**Exposes:** `rename_page()` - *Rename page logic.*
**Exposes:** `adopt_document()` - *Adopts an existing library document into a notebook section.*
**Exposes:** `search_global()` - *Search across all notebooks, sections, and pages for text.*


---

**File:** `src/shared/services/document_manager/spell_service.py`

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
* `src/pillars/document_manager/services/spell_service.py`
* `src/shared/ui/rich_text_editor/spell_feature.py`

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

**File:** `src/shared/services/document_manager/utils/image_utils.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Image extraction utilities for document processing.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base64`
* `hashlib`
* `logging`
* `mimetypes`
* `re`
* `typing.Callable`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/utils/image_utils.py`
* `src/shared/services/document_manager/document_service.py`
* `tests/verify_image_utils.py`

**Key Interactions:**
**Exposes:** `extract_images_from_html()` - *Extract base64 images from HTML and replace with docimg:// references.*
**Exposes:** `restore_images_in_html()` - *Replace docimg:// references with actual base64 data for display.*
**Exposes:** `has_embedded_images()` - *Check if HTML contains embedded base64 images.*
**Exposes:** `has_docimg_references()` - *Check if HTML contains docimg:// references.*
**Exposes:** `count_embedded_images()` - *Count the number of embedded base64 images in HTML.*
**Exposes:** `replace_image()` - *Replace image logic.*
**Exposes:** `replace_docimg()` - *Replace docimg logic.*


---

**File:** `src/shared/services/document_manager/utils/parsers.py`

**Role:** `[Muscle] (Service)`

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
* `src/pillars/document_manager/utils/parsers.py`
* `src/shared/services/document_manager/document_service.py`

**Key Interactions:**
**Exposes:** `handle_data()` - *Append text data to the buffer.*
**Exposes:** `handle_starttag()` - *Process start tags, adding newlines for breaks.*
**Exposes:** `handle_endtag()` - *Process end tags, ensuring proper spacing for block elements.*
**Exposes:** `get_text()` - *Return the aggregated, suppressed text content.*
**Exposes:** `parse_file()` - *Parse a file and return (content_text, raw_html, file_type, metadata).*
**Exposes:** `extract_table_text()` - *Recursively extract text from a table, including nested tables.*


---

**File:** `src/shared/services/document_manager/verse_teacher_service.py`

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
* `pillars.document_manager.models.VerseRule`
* `re`
* `shared.database.get_db_session`
* `shared.models.document_manager.document.Document`
* `shared.repositories.document_manager.document_repository.DocumentRepository`
* `shared.repositories.document_manager.document_verse_repository.DocumentVerseRepository`
* `shared.repositories.document_manager.verse_edit_log_repository.VerseEditLogRepository`
* `shared.repositories.document_

**Consumers (Who Needs It):**
* `src/pillars/document_manager/services/verse_teacher_service.py`
* `src/pillars/gematria/services/text_analysis_service.py`
* `src/pillars/gematria/ui/holy_book_teacher_window.py`

**Key Interactions:**
**Exposes:** `verse_teacher_service_context()` - *Yield a `VerseTeacherService` wired to a managed DB session.*
**Exposes:** `get_curated_verses()` - *Retrieve curated verses logic.*
**Exposes:** `get_or_parse_verses()` - *Retrieve or parse verses logic.*
**Exposes:** `generate_parser_run()` - *Generate parser run logic.*
**Exposes:** `save_curated_verses()` - *Save curated verses logic.*
**Exposes:** `record_rule()` - *Record rule logic.*
**Exposes:** `list_rules_for_document()` - *List rules for document logic.*
**Exposes:** `list_recent_edits()` - *List recent edits logic.*


---

**File:** `src/shared/services/gematria/base_calculator.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Base class for gematria calculators following DRY principles.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `abc.ABC`
* `abc.abstractmethod`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`
* `unicodedata`

**Consumers (Who Needs It):**
* `src/pillars/correspondences/services/formula_engine.py`
* `src/pillars/gematria/services/base_calculator.py`
* `src/pillars/gematria/services/calculation_service.py`

**Key Interactions:**
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `normalize_text()` - *Normalize text by removing diacritical marks and accents.*
**Exposes:** `calculate()` - *Calculate the gematria value of the given text.*
**Exposes:** `get_letter_value()` - *Get the gematria value of a single character.*
**Exposes:** `get_breakdown()` - *Get a breakdown of each character's value in the text.*


---

**File:** `src/shared/services/gematria/greek_calculator.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Greek isopsephy calculator implementation.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_calculator.GematriaCalculator`
* `typing.Dict`

**Consumers (Who Needs It):**
* `scripts/verify_ui_startup.py`
* `src/pillars/gematria/services/greek_calculator.py`

**Key Interactions:**
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate isopsephy value + number of letters (Kolel).*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate sum of squared letter values.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate sum of cubed letter values.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate sum of triangular numbers for each letter.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate sum of digit sums for each letter value.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate sum of squared ordinal values.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*


---

**File:** `src/shared/services/gematria/hebrew_calculator.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Hebrew gematria calculator implementation.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_calculator.GematriaCalculator`
* `typing.Dict`

**Consumers (Who Needs It):**
* `scripts/verify_ui_startup.py`
* `src/pillars/gematria/services/hebrew_calculator.py`

**Key Interactions:**
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate gematria value + number of letters (Kolel).*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate sum of squared letter values.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate sum of cubed letter values.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate sum of triangular numbers for each letter.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate sum of digit sums for each letter value.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate sum of squared ordinal values.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*


---

**File:** `src/shared/services/gematria/tq_calculator.py`

**Role:** `[Muscle] (Service)`

**Purpose:** TQ (Trigrammaton Qabbalah) English gematria calculator implementation.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_calculator.GematriaCalculator`
* `typing.Dict`

**Consumers (Who Needs It):**
* `scripts/verify_ui_startup.py`
* `src/pillars/gematria/services/tq_calculator.py`

**Key Interactions:**
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate TQ value and reduce to single digit.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate sum of squared TQ letter values.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Calculate sum of triangular numbers for each letter.*
**Exposes:** `name()` - *Return the name of this gematria system.*
**Exposes:** `calculate()` - *Multiply each letter's TQ value by its position in the word, then sum.*


---

**File:** `src/shared/services/geometry/archimedean.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Archimedean solid services and calculators.

**Input (Ingests):**
* `edge_length` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `face_count` (Field)
* `edge_count` (Field)
* `vertex_count` (Field)
* `face_sides` (Field)
* `face_metrics` (Field)
* `payload` (Field)
* `metrics` (Field)
* `key` (Field)
* `name` (Field)
* `canonical_vertices` (Field)
* `faces` (Field)
* `edges` (Field)
* `base_edge_length` (Field)
* `base_surface_area` (Field)
* `base_volume` (Field)
* `face_sides` (Field)
* `edge_length`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `archimedean_data.ARCHIMEDEAN_DATA`
* `dataclasses.dataclass`
* `math`
* `solid_geometry.compute_surface_area`
* `solid_geometry.compute_volume`
* `solid_geometry.edges_from_faces`
* `solid_geometry.vec_cross`
* `solid_geometry.vec_dot`
* `solid_geometry.vec_length`
* `solid_geometry.vec_normalize`
* `solid_geometry.vec_sub`
* `solid_payload.Edge`
* `solid_payload.Face`
* `solid_payload.SolidLabel`
* `solid_payload.SolidPayload`
* `solid_payload.Vec3`
* `solid_proper

**Consumers (Who Needs It):**
* `src/pillars/geometry/services/archimedean_solids.py`
* `src/pillars/tq/services/platonic_transition_service.py`

**Key Interactions:**
**Exposes:** `build()` - *Build logic.*
**Exposes:** `payload()` - *Payload logic.*
**Exposes:** `properties()` - *Properties logic.*
**Exposes:** `set_property()` - *Configure property logic.*
**Exposes:** `clear()` - *Clear logic.*
**Exposes:** `payload()` - *Payload logic.*
**Exposes:** `metadata()` - *Metadata logic.*
**Exposes:** `metrics()` - *Metrics logic.*


---

**File:** `src/shared/services/geometry/archimedean_data.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Canonical Archimedean solid datasets auto-generated from dmccooey.com.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* None.

**Consumers (Who Needs It):**
* `src/pillars/geometry/services/archimedean_data.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/shared/services/geometry/cube.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Cube solid math utilities and calculator.

**Input (Ingests):**
* `edge_length` (Field)
* `face_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `face_diagonal` (Field)
* `space_diagonal` (Field)
* `inradius` (Field)
* `midradius` (Field)
* `circumradius` (Field)
* `incircle_circumference` (Field)
* `midsphere_circumference` (Field)
* `circumcircle_circumference` (Field)
* `faces` (Field)
* `edges` (Field)
* `vertices` (Field)
* `face_sides` (Field)
* `vertex_valence` (Field)
* `dihedral_angle_deg` (Field)
* `solid_angle_sr` (Field)
* `face_inradius` (Field)
* `face_circumradius` (Field)
* `insphere_surface_area` (Field)
* `insphere_volume` (Field)
* `midsphere_surface_area` (Field)
* `midsphere_volume` (Field)
* `circumsphere_surface_area` (Field)
* `circumsphere_volume` (Field)
* `sphericity` (Field)
* `isoperimetric_quotient` (Field)
* `surface_to_volume_ratio` (Field)
* `moment_inertia_solid` (Field)
* `moment_inertia_shell` (Field)
* `angular_defect_vertex_deg` (Field)
* `total_angular_defect_deg` (Field)
* `euler_characteristic` (Field)
* `packing_density` (Field)
* `symmetry_group_order` (Field)
* `rotational_symmetry_order` (Field)
* `symmetry_group_name` (Field)
* `dual_solid_name` (Field)
* `golden_ratio_factor` (Field)
* `payload` (Field)
* `metrics` (Field)
* `edge_length`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `geometry_visuals.compute_dual_payload`
* `math`
* `platonic_constants.ANGULAR_DEFECT_VERTEX_DEG`
* `platonic_constants.DIHEDRAL_ANGLES_DEG`
* `platonic_constants.DUAL_SOLID_NAME`
* `platonic_constants.GOLDEN_RATIO_FACTOR`
* `platonic_constants.MOMENT_INERTIA_SHELL_K`
* `platonic_constants.MOMENT_INERTIA_SOLID_K`
* `platonic_constants.PACKING_DENSITY`
* `platonic_constants.PlatonicSolid`
* `platonic_constants.ROTATIONAL_SYMMETRY_ORDER`
* `pl

**Consumers (Who Needs It):**
* `src/pillars/geometry/services/cube_solid.py`
* `src/pillars/tq/services/platonic_transition_service.py`

**Key Interactions:**
**Exposes:** `build()` - *Build logic.*
**Exposes:** `payload()` - *Payload logic.*
**Exposes:** `properties()` - *Return all properties in display order.*
**Exposes:** `set_property()` - *Set a property and recalculate all others.*
**Exposes:** `clear()` - *Clear logic.*
**Exposes:** `payload()` - *Payload logic.*
**Exposes:** `metadata()` - *Metadata logic.*
**Exposes:** `metrics()` - *Metrics logic.*
**Exposes:** `solver()` - *Solver logic.*


---

**File:** `src/shared/services/geometry/dodecahedron.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Dodecahedron solid math utilities and calculator.

**Input (Ingests):**
* `edge_length` (Field)
* `face_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `inradius` (Field)
* `midradius` (Field)
* `circumradius` (Field)
* `incircle_circumference` (Field)
* `midsphere_circumference` (Field)
* `circumcircle_circumference` (Field)
* `faces` (Field)
* `edges` (Field)
* `vertices` (Field)
* `face_sides` (Field)
* `vertex_valence` (Field)
* `dihedral_angle_deg` (Field)
* `solid_angle_sr` (Field)
* `face_inradius` (Field)
* `face_circumradius` (Field)
* `insphere_surface_area` (Field)
* `insphere_volume` (Field)
* `midsphere_surface_area` (Field)
* `midsphere_volume` (Field)
* `circumsphere_surface_area` (Field)
* `circumsphere_volume` (Field)
* `sphericity` (Field)
* `isoperimetric_quotient` (Field)
* `surface_to_volume_ratio` (Field)
* `moment_inertia_solid` (Field)
* `moment_inertia_shell` (Field)
* `angular_defect_vertex_deg` (Field)
* `total_angular_defect_deg` (Field)
* `euler_characteristic` (Field)
* `packing_density` (Field)
* `symmetry_group_order` (Field)
* `rotational_symmetry_order` (Field)
* `symmetry_group_name` (Field)
* `dual_solid_name` (Field)
* `golden_ratio_factor` (Field)
* `payload` (Field)
* `metrics` (Field)
* `edge_length`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `geometry_visuals.compute_dual_payload`
* `math`
* `platonic_constants.ANGULAR_DEFECT_VERTEX_DEG`
* `platonic_constants.DIHEDRAL_ANGLES_DEG`
* `platonic_constants.DUAL_SOLID_NAME`
* `platonic_constants.GOLDEN_RATIO_FACTOR`
* `platonic_constants.MOMENT_INERTIA_SHELL_K`
* `platonic_constants.MOMENT_INERTIA_SOLID_K`
* `platonic_constants.PACKING_DENSITY`
* `platonic_constants.PlatonicSolid`
* `platonic_constants.ROTATIONAL_SYMMETRY_ORDER`
* `pl

**Consumers (Who Needs It):**
* `src/pillars/geometry/services/dodecahedron_solid.py`
* `src/pillars/tq/services/platonic_transition_service.py`

**Key Interactions:**
**Exposes:** `build()` - *Build logic.*
**Exposes:** `payload()` - *Payload logic.*
**Exposes:** `properties()` - *Properties logic.*
**Exposes:** `set_property()` - *Configure property logic.*
**Exposes:** `clear()` - *Clear logic.*
**Exposes:** `payload()` - *Payload logic.*
**Exposes:** `metadata()` - *Metadata logic.*
**Exposes:** `metrics()` - *Metrics logic.*
**Exposes:** `solver()` - *Solver logic.*


---

**File:** `src/shared/services/geometry/geometry_visuals.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Geometry visualization services.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `solid_payload.SolidLabel`
* `solid_payload.SolidPayload`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Set`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `src/pillars/geometry/services/geometry_visuals.py`

**Key Interactions:**
**Exposes:** `compute_dual_payload()` - *Generate the dual solid for a given primal polyhedron.*


---

**File:** `src/shared/services/geometry/icosahedron.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Icosahedron solid math utilities and calculator.

**Input (Ingests):**
* `edge_length` (Field)
* `face_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `inradius` (Field)
* `midradius` (Field)
* `circumradius` (Field)
* `incircle_circumference` (Field)
* `midsphere_circumference` (Field)
* `circumcircle_circumference` (Field)
* `faces` (Field)
* `edges` (Field)
* `vertices` (Field)
* `face_sides` (Field)
* `vertex_valence` (Field)
* `dihedral_angle_deg` (Field)
* `solid_angle_sr` (Field)
* `face_inradius` (Field)
* `face_circumradius` (Field)
* `insphere_surface_area` (Field)
* `insphere_volume` (Field)
* `midsphere_surface_area` (Field)
* `midsphere_volume` (Field)
* `circumsphere_surface_area` (Field)
* `circumsphere_volume` (Field)
* `sphericity` (Field)
* `isoperimetric_quotient` (Field)
* `surface_to_volume_ratio` (Field)
* `moment_inertia_solid` (Field)
* `moment_inertia_shell` (Field)
* `angular_defect_vertex_deg` (Field)
* `total_angular_defect_deg` (Field)
* `euler_characteristic` (Field)
* `packing_density` (Field)
* `symmetry_group_order` (Field)
* `rotational_symmetry_order` (Field)
* `symmetry_group_name` (Field)
* `dual_solid_name` (Field)
* `golden_ratio_factor` (Field)
* `payload` (Field)
* `metrics` (Field)
* `edge_length`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `geometry_visuals.compute_dual_payload`
* `math`
* `platonic_constants.ANGULAR_DEFECT_VERTEX_DEG`
* `platonic_constants.DIHEDRAL_ANGLES_DEG`
* `platonic_constants.DUAL_SOLID_NAME`
* `platonic_constants.GOLDEN_RATIO_FACTOR`
* `platonic_constants.MOMENT_INERTIA_SHELL_K`
* `platonic_constants.MOMENT_INERTIA_SOLID_K`
* `platonic_constants.PACKING_DENSITY`
* `platonic_constants.PlatonicSolid`
* `platonic_constants.ROTATIONAL_SYMMETRY_ORDER`
* `pl

**Consumers (Who Needs It):**
* `src/pillars/geometry/services/icosahedron_solid.py`
* `src/pillars/tq/services/platonic_transition_service.py`

**Key Interactions:**
**Exposes:** `build()` - *Build logic.*
**Exposes:** `payload()` - *Payload logic.*
**Exposes:** `properties()` - *Properties logic.*
**Exposes:** `set_property()` - *Configure property logic.*
**Exposes:** `clear()` - *Clear logic.*
**Exposes:** `payload()` - *Payload logic.*
**Exposes:** `metadata()` - *Metadata logic.*
**Exposes:** `metrics()` - *Metrics logic.*
**Exposes:** `solver()` - *Solver logic.*


---

**File:** `src/shared/services/geometry/octahedron.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Octahedron solid math utilities and calculator.

**Input (Ingests):**
* `edge_length` (Field)
* `face_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `inradius` (Field)
* `midradius` (Field)
* `circumradius` (Field)
* `incircle_circumference` (Field)
* `midsphere_circumference` (Field)
* `circumcircle_circumference` (Field)
* `faces` (Field)
* `edges` (Field)
* `vertices` (Field)
* `face_sides` (Field)
* `vertex_valence` (Field)
* `dihedral_angle_deg` (Field)
* `solid_angle_sr` (Field)
* `face_inradius` (Field)
* `face_circumradius` (Field)
* `insphere_surface_area` (Field)
* `insphere_volume` (Field)
* `midsphere_surface_area` (Field)
* `midsphere_volume` (Field)
* `circumsphere_surface_area` (Field)
* `circumsphere_volume` (Field)
* `sphericity` (Field)
* `isoperimetric_quotient` (Field)
* `surface_to_volume_ratio` (Field)
* `moment_inertia_solid` (Field)
* `moment_inertia_shell` (Field)
* `angular_defect_vertex_deg` (Field)
* `total_angular_defect_deg` (Field)
* `euler_characteristic` (Field)
* `packing_density` (Field)
* `symmetry_group_order` (Field)
* `rotational_symmetry_order` (Field)
* `symmetry_group_name` (Field)
* `dual_solid_name` (Field)
* `golden_ratio_factor` (Field)
* `payload` (Field)
* `metrics` (Field)
* `edge_length`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `geometry_visuals.compute_dual_payload`
* `math`
* `platonic_constants.ANGULAR_DEFECT_VERTEX_DEG`
* `platonic_constants.DIHEDRAL_ANGLES_DEG`
* `platonic_constants.DUAL_SOLID_NAME`
* `platonic_constants.GOLDEN_RATIO_FACTOR`
* `platonic_constants.MOMENT_INERTIA_SHELL_K`
* `platonic_constants.MOMENT_INERTIA_SOLID_K`
* `platonic_constants.PACKING_DENSITY`
* `platonic_constants.PlatonicSolid`
* `platonic_constants.ROTATIONAL_SYMMETRY_ORDER`
* `pl

**Consumers (Who Needs It):**
* `src/pillars/geometry/services/octahedron_solid.py`
* `src/pillars/tq/services/platonic_transition_service.py`

**Key Interactions:**
**Exposes:** `build()` - *Build logic.*
**Exposes:** `payload()` - *Payload logic.*
**Exposes:** `properties()` - *Properties logic.*
**Exposes:** `set_property()` - *Configure property logic.*
**Exposes:** `clear()` - *Clear logic.*
**Exposes:** `payload()` - *Payload logic.*
**Exposes:** `metadata()` - *Metadata logic.*
**Exposes:** `metrics()` - *Metrics logic.*
**Exposes:** `solver()` - *Solver logic.*


---

**File:** `src/shared/services/geometry/platonic_constants.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Platonic Solid Constants and Formulas.

**Input (Ingests):**
* `p` (Field)
* `q` (Field)
* `faces` (Field)
* `vertices` (Field)
* `edges` (Field)
* `name` (Field)
* `key` (Field)
* `unit` (Field)
* `precision` (Field)
* `power` (Field)
* `base_value` (Field)
* `editable` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `enum.Enum`
* `math`
* `typing.Dict`

**Consumers (Who Needs It):**
* `src/pillars/geometry/services/platonic_constants.py`

**Key Interactions:**
**Exposes:** `face_inradius()` - *Inradius of a regular p-gon face.*
**Exposes:** `face_circumradius()` - *Circumradius of a regular p-gon face.*
**Exposes:** `face_area()` - *Area of a regular p-gon face.*
**Exposes:** `edge_from_face_inradius()` - *Derive edge length from face inradius.*
**Exposes:** `edge_from_face_circumradius()` - *Derive edge length from face circumradius.*
**Exposes:** `edge_from_face_area()` - *Derive edge length from face area.*
**Exposes:** `sphere_surface_area()` - *Surface area of a sphere: 4πr²*
**Exposes:** `sphere_volume()` - *Volume of a sphere: (4/3)πr³*
**Exposes:** `radius_from_sphere_surface_area()` - *Derive radius from sphere surface area.*
**Exposes:** `radius_from_sphere_volume()` - *Derive radius from sphere volume.*
**Exposes:** `sphericity()` - *Sphericity: how close to a sphere.*
**Exposes:** `isoperimetric_quotient()` - *Isoperimetric quotient (IQ).*
**Exposes:** `surface_to_volume_ratio()` - *Surface area to volume ratio.*
**Exposes:** `angular_defect_vertex()` - *Angular defect at a vertex in radians.*
**Exposes:** `euler_characteristic()` - *V - E + F = 2 for convex polyhedra.*
**Exposes:** `scale()` - *Scale base value to given edge length.*
**Exposes:** `solve_edge()` - *Solve for edge length given this property's value.*


---

**File:** `src/shared/services/geometry/solid_geometry.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Utility math helpers for solid geometry computations.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `math`
* `typing.Iterable`
* `typing.List`
* `typing.Sequence`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `src/pillars/geometry/services/solid_geometry.py`

**Key Interactions:**
**Exposes:** `vec_add()` - *Vec add logic.*
**Exposes:** `vec_sub()` - *Vec sub logic.*
**Exposes:** `vec_scale()` - *Vec scale logic.*
**Exposes:** `vec_dot()` - *Vec dot logic.*
**Exposes:** `vec_cross()` - *Vec cross logic.*
**Exposes:** `vec_length()` - *Vec length logic.*
**Exposes:** `vec_normalize()` - *Vec normalize logic.*
**Exposes:** `polygon_area()` - *Polygon area logic.*
**Exposes:** `face_normal()` - *Face normal logic.*
**Exposes:** `plane_distance_from_origin()` - *Plane distance from origin logic.*
**Exposes:** `compute_surface_area()` - *Compute surface area logic.*
**Exposes:** `compute_volume()` - *Compute volume logic.*
**Exposes:** `edges_from_faces()` - *Edges from faces logic.*
**Exposes:** `face_centroid()` - *Face centroid logic.*
**Exposes:** `angle_around_axis()` - *Angle around axis logic.*


---

**File:** `src/shared/services/geometry/solid_payload.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Shared 3D solid payload structures.

**Input (Ingests):**
* `text` (Field)
* `position` (Field)
* `align_center` (Field)
* `vertices` (Field)
* `edges` (Field)
* `faces` (Field)
* `labels` (Field)
* `metadata` (Field)
* `face_colors` (Field)
* `suggested_scale` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `dataclasses.field`
* `typing.List`
* `typing.Optional`
* `typing.Sequence`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `src/pillars/geometry/shared/solid_payload.py`
* `src/pillars/tq/services/platonic_transition_service.py`

**Key Interactions:**
**Exposes:** `bounds()` - *Bounds logic.*


---

**File:** `src/shared/services/geometry/solid_property.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Shared dataclasses for 3D solid calculators.

**Input (Ingests):**
* `name` (Field)
* `key` (Field)
* `unit` (Field)
* `value` (Field)
* `precision` (Field)
* `editable` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/geometry/services/solid_property.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/shared/services/geometry/tetrahedron.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Equilateral tetrahedron solid math + payload builder.

**Input (Ingests):**
* `edge_length` (Field)
* `height` (Field)
* `face_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `inradius` (Field)
* `midradius` (Field)
* `circumradius` (Field)
* `incircle_circumference` (Field)
* `midsphere_circumference` (Field)
* `circumcircle_circumference` (Field)
* `faces` (Field)
* `edges` (Field)
* `vertices` (Field)
* `face_sides` (Field)
* `vertex_valence` (Field)
* `dihedral_angle_deg` (Field)
* `solid_angle_sr` (Field)
* `face_inradius` (Field)
* `face_circumradius` (Field)
* `insphere_surface_area` (Field)
* `insphere_volume` (Field)
* `midsphere_surface_area` (Field)
* `midsphere_volume` (Field)
* `circumsphere_surface_area` (Field)
* `circumsphere_volume` (Field)
* `sphericity` (Field)
* `isoperimetric_quotient` (Field)
* `surface_to_volume_ratio` (Field)
* `moment_inertia_solid` (Field)
* `moment_inertia_shell` (Field)
* `angular_defect_vertex_deg` (Field)
* `total_angular_defect_deg` (Field)
* `euler_characteristic` (Field)
* `packing_density` (Field)
* `symmetry_group_order` (Field)
* `rotational_symmetry_order` (Field)
* `symmetry_group_name` (Field)
* `dual_solid_name` (Field)
* `golden_ratio_factor` (Field)
* `payload` (Field)
* `metrics` (Field)
* `edge_length`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `geometry_visuals.compute_dual_payload`
* `math`
* `platonic_constants.ANGULAR_DEFECT_VERTEX_DEG`
* `platonic_constants.DIHEDRAL_ANGLES_DEG`
* `platonic_constants.DUAL_SOLID_NAME`
* `platonic_constants.GOLDEN_RATIO_FACTOR`
* `platonic_constants.MOMENT_INERTIA_SHELL_K`
* `platonic_constants.MOMENT_INERTIA_SOLID_K`
* `platonic_constants.PACKING_DENSITY`
* `platonic_constants.PlatonicSolid`
* `platonic_constants.ROTATIONAL_SYMMETRY_ORDER`
* `pl

**Consumers (Who Needs It):**
* `src/pillars/geometry/services/tetrahedron_solid.py`
* `src/pillars/tq/services/platonic_transition_service.py`

**Key Interactions:**
**Exposes:** `build()` - *Build logic.*
**Exposes:** `payload()` - *Convenience accessor when only the payload is required.*
**Exposes:** `properties()` - *Return all properties in display order.*
**Exposes:** `set_property()` - *Set a property and recalculate all others.*
**Exposes:** `clear()` - *Clear logic.*
**Exposes:** `payload()` - *Payload logic.*
**Exposes:** `metadata()` - *Metadata logic.*
**Exposes:** `metrics()` - *Metrics logic.*
**Exposes:** `solver()` - *Solver logic.*


---

**File:** `src/shared/services/help_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** The Librarian Service (Help System Backend).

**Input (Ingests):**
* `id` (Field)
* `title` (Field)
* `path` (Field)
* `children` (Field)
* `is_category` (Field)
* `project_root`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `dataclasses.dataclass`
* `dataclasses.field`
* `logging`
* `os`
* `pathlib.Path`
* `re`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `scripts/verify_help.py`

**Key Interactions:**
**Exposes:** `index_content()` - *Scan the wiki directory and build the TOC.*
**Exposes:** `get_toc()` - *Return the calculated Table of Contents.*
**Exposes:** `search()` - *Simple text search.*
**Exposes:** `get_content()` - *Get the HTML content for a topic (Markdown rendered).*


---

**File:** `src/shared/services/time/thelemic_calendar_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Thelemic Calendar Service - Loads and queries the Thelemic Calendar CSV.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `csv`
* `os`
* `pathlib.Path`
* `shared.models.time.thelemic_calendar_models.ConrunePair`
* `shared.models.time.thelemic_calendar_models.ZODIAC_SIGNS`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/astrology/ui/chariot_differentials_window.py`
* `src/pillars/astrology/ui/differential_natal_window.py`
* `src/pillars/time_mechanics/services/thelemic_calendar_service.py`

**Key Interactions:**
**Exposes:** `load_calendar()` - *Load the Thelemic Calendar from CSV.*
**Exposes:** `ensure_loaded()` - *Ensure the calendar is loaded, loading if necessary.*
**Exposes:** `get_pair_by_difference()` - *Get Conrune pair by Difference value (degree position 1-364).*
**Exposes:** `get_pair_by_date()` - *Get Conrune pair by Gregorian date string.*
**Exposes:** `get_all_pairs()` - *Get all Conrune pairs in order.*
**Exposes:** `get_prime_ditrune_pairs()` - *Get the 4 Prime Ditrune Sets (intercalary days).*
**Exposes:** `search_by_value()` - *Search for pairs where a specific field matches the given value.*
**Exposes:** `difference_to_zodiac_degree()` - *Convert a Difference value to zodiacal degrees (0-360).*
**Exposes:** `zodiac_degree_to_difference()` - *Convert a zodiacal degree (0-360) to a Difference value.*
**Exposes:** `get_reversal_pair()` - *Find the reversal pair using ternary string reversal.*
**Exposes:** `decimal_to_ternary()` - *Decimal to ternary logic.*
**Exposes:** `ternary_to_decimal()` - *Ternary to decimal logic.*


---

**File:** `src/shared/services/tq/baphomet_color_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Baphomet Color Service - The RGB Resolver.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`

**Consumers (Who Needs It):**
* `src/pillars/adyton/services/frustum_color_service.py`
* `src/pillars/adyton/services/kamea_color_service.py`
* `src/pillars/adyton/ui/frustum_popup.py`
* `src/pillars/tq/services/baphomet_color_service.py`

**Key Interactions:**
**Exposes:** `resolve_color()` - *Resolves the RGB color for a given 6-digit ternary string.*


---

**File:** `src/shared/services/tq/ternary_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service for ternary conversions.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* None.

**Consumers (Who Needs It):**
* `src/pillars/adyton/services/frustum_color_service.py`
* `src/pillars/adyton/services/kamea_color_service.py`
* `src/pillars/adyton/ui/frustum_popup.py`
* `src/pillars/tq/services/ternary_service.py`

**Key Interactions:**
**Exposes:** `decimal_to_ternary()` - *Convert a decimal integer to a ternary string.*
**Exposes:** `ternary_to_decimal()` - *Convert a ternary string to a decimal integer.*
**Exposes:** `conrune_transform()` - *Apply Conrune transformation to a ternary string.*
**Exposes:** `reverse_ternary()` - *Reverse a ternary string.*


---

**File:** `src/shared/signals/navigation_bus.py`

**Role:** `[Scout]`

**Purpose:** Navigation Signal Bus for decoupled window launching.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QObject`
* `PyQt6.QtCore.pyqtSignal`
* `typing.Any`
* `typing.Dict`

**Consumers (Who Needs It):**
* `scripts/verify_ui_startup.py`
* `src/pillars/adyton/ui/wall_analytics_window.py`
* `src/pillars/adyton/ui/wall_designer.py`
* `src/pillars/astrology/ui/chariot_differentials_window.py`
* `src/pillars/astrology/ui/differential_natal_window.py`
* `src/pillars/astrology/ui/planetary_positions_window.py`
* `src/pillars/gematria/ui/batch_calculator_window.py`
* `src/pillars/gematria/ui/chain_results_window.py`
* `src/pillars/gematria/ui/els_search_window.py`
* `src/pillars/gematria/ui/gematria_calculator_window.py`
* `src/pillars/gematria/ui/text_analysis/main_window.py`
* `src/pillars/geometry/ui/geometry3d/window3d.py`
* `src/pillars/time_mechanics/ui/zodiacal_circle_window.py`
* `src/pillars/tq/ui/conrune_pair_finder_window.py`
* `src/pillars/tq/ui/geometric_transitions_3d_window.py`
* `src/pillars/tq/ui/geometric_transitions_window.py`
* `src/pillars/tq/ui/quadset_analysis_window.py`
* `src/pillars/tq/ui/transitions_window.py`
* `src/shared/ui/window_manager.py`

**Key Interactions:**
**Exposes:** `get_window_info()` - *Get registration info for a window key.*
**Emits:** `request_window` - *Nervous System Signal.*
**Emits:** `window_response` - *Nervous System Signal.*
**Exposes:** `emit_navigation()` - *Convenience method to request a window.*


---

**File:** `src/shared/ui/catalyst_styles.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Catalyst Button Styles — Visual Liturgy v2.2 §10.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* None.

**Consumers (Who Needs It):**
* `src/pillars/document_manager/ui/document_search_window.py`
* `src/pillars/tq/ui/ternary_converter_window.py`

**Key Interactions:**
**Exposes:** `get_seeker_style()` - *The Seeker (Gold) — Reveals hidden knowledge, uncovers, searches.*
**Exposes:** `get_magus_style()` - *The Magus (Violet) — Transmutes, executes, primary action.*
**Exposes:** `get_scribe_style()` - *The Scribe (Emerald) — Preserves, etches, saves.*
**Exposes:** `get_destroyer_style()` - *The Destroyer (Crimson) — Purges, banishes, deletes.*
**Exposes:** `get_navigator_style()` - *The Navigator (Void Slate) — Traverses, refreshes, secondary action.*
**Exposes:** `get_filter_chip_style()` - *Filter chip button style with Magus Violet checked state.*


---

**File:** `src/shared/ui/components.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Reusable UI components for Visual Liturgy v2.2.

**Input (Ingests):**
* `text`
* `archetype`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QEasingCurve`
* `PyQt6.QtCore.QPropertyAnimation`
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QPushButton`
* `catalyst_styles.get_destroyer_style`
* `catalyst_styles.get_magus_style`
* `catalyst_styles.get_navigator_style`
* `catalyst_styles.get_scribe_style`
* `catalyst_styles.get_seeker_style`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/gematria/ui/gematria_calculator_window.py`

**Key Interactions:**
**Exposes:** `enterEvent()` - *Trigger Aura on hover.*
**Exposes:** `leaveEvent()` - *Extinguish Aura on exit.*


---

**File:** `src/shared/ui/font_loader.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QFontDatabase`
* `logging`
* `os`
* `pathlib.Path`
* `shutil`

**Consumers (Who Needs It):**
* `src/main.py`
* `src/pillars/document_manager/ui/font_manager_window.py`
* `tests/rituals/rite_of_font_manager.py`
* `tests/rituals/rite_of_keyboard_styling.py`

**Key Interactions:**
**Exposes:** `load_custom_fonts()` - *Load custom fonts from src/assets/fonts directory.*
**Exposes:** `install_new_font()` - *Install a new font file: copy to assets and load it.*


---

**File:** `src/shared/ui/help_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** The Akaschic Archive (Help Window).

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QIcon`
* `PyQt6.QtGui.QKeySequence`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QTabWidget`
* `PyQt6.QtWidgets.QTextBrowser`
* `PyQt6.QtWidgets.QTreeWidgetItem`
* `PyQt6.QtWidgets.QTreeWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6

**Consumers (Who Needs It):**
* `scripts/verify_help.py`
* `src/main.py`

**Key Interactions:**
**Exposes:** `add_nodes()` - *Add nodes logic.*


---

**File:** `src/shared/ui/keyboard_layouts.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Keyboard layout definitions for the Virtual Keyboard.

**Input (Ingests):**
* `name` (Field)
* `display_name` (Field)
* `rows` (Field)
* `has_shift` (Field)
* `is_esoteric` (Field)
* `font_family` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `dataclasses.dataclass`
* `typing.Dict`
* `typing.List`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/shared/ui/kinetic_enforcer.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Global Kinetic Enforcer — The Spirit of the Button.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QEasingCurve`
* `PyQt6.QtCore.QEvent`
* `PyQt6.QtCore.QObject`
* `PyQt6.QtCore.QPropertyAnimation`
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QPushButton`

**Consumers (Who Needs It):**
* `scripts/verify_kinetic_enforcer.py`
* `src/main.py`

**Key Interactions:**
**Exposes:** `eventFilter()` - *Functional interface.*


---

**File:** `src/shared/ui/rich_text_editor/dialogs/base_dialog.py`

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

**File:** `src/shared/ui/rich_text_editor/dialogs/export_pdf_dialog.py`

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
**Exposes:** `get_file_path()` - *Retrieve file path logic.*
**Exposes:** `get_page_size()` - *Retrieve page size logic.*
**Exposes:** `get_orientation()` - *Retrieve orientation logic.*
**Exposes:** `get_margins()` - *Retrieve margins logic.*


---

**File:** `src/shared/ui/rich_text_editor/dialogs/horizontal_rule_dialog.py`

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

**File:** `src/shared/ui/rich_text_editor/dialogs/hyperlink_dialog.py`

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

**File:** `src/shared/ui/rich_text_editor/dialogs/page_setup_dialog.py`

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
**Exposes:** `get_page_size()` - *Retrieve page size logic.*
**Exposes:** `get_orientation()` - *Retrieve orientation logic.*
**Exposes:** `get_margins()` - *Retrieve margins logic.*


---

**File:** `src/shared/ui/rich_text_editor/dialogs/special_characters_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Special Characters Dialog - The Symbol Palette.

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

**File:** `src/shared/ui/rich_text_editor/editor.py`

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
* None detected.

**Key Interactions:**
**Exposes:** `page_height()` - *Get page height from settings.*
**Exposes:** `show_page_breaks()` - *Display page breaks logic.*
**Exposes:** `show_page_breaks()` - *Display page breaks logic.*
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
**Exposes:** `toggle_strikethrough()` - *Toggle strikethrough logic.*
**Exposes:** `toggle_subscript()` - *Toggle subscript logic.*
**Exposes:** `toggle_superscript()` - *Toggle superscript logic.*
**Exposes:** `insert_hyperlink()` - *Open dialog to insert a hyperlink.*
**Exposes:** `page_setup()` - *Open page setup dialog.*
**Exposes:** `insert_horizontal_rule()` - *Insert a horizontal rule.*
**Exposes:** `get_html()` - *Retrieve html logic.*
**Exposes:** `set_html()` - *Configure html logic.*
**Exposes:** `get_text()` - *Retrieve text logic.*
**Exposes:** `set_text()` - *Configure text logic.*
**Exposes:** `set_markdown()` - *Set the editor content from Markdown.*
**Exposes:** `get_markdown()` - *Get the editor content as Markdown.*
**Exposes:** `clear()` - *Clear logic.*
**Exposes:** `find_text()` - *Find first occurrence of text and select it.*
**Exposes:** `find_all_matches()` - *Count all matches and position cursor at first. Returns match count.*
**Exposes:** `find_next()` - *Navigate to next match. Returns True if found.*
**Exposes:** `find_previous()` - *Navigate to previous match. Returns True if found.*
**Exposes:** `get_match_info()` - *Get current match position info. Returns (current, total).*
**Exposes:** `clear_search()` - *Clear search state.*
**Exposes:** `new_document()` - *Clear the editor for a new document.*
**Exposes:** `open_document()` - *Open a file (Markdown, HTML, Text).*
**Exposes:** `save_document()` - *Save the document (Markdown, HTML, Text).*
**Exposes:** `on_width_changed()` - *Handle width changed logic.*
**Exposes:** `on_height_changed()` - *Handle height changed logic.*
**Exposes:** `update_w_range()` - *Update w range logic.*
**Exposes:** `update_h_range()` - *Update h range logic.*
**Exposes:** `sepia_pixel()` - *Sepia pixel logic.*
**Exposes:** `shift_channel()` - *Shift channel logic.*
**Exposes:** `shift_channel()` - *Shift channel logic.*
**Exposes:** `shift_channel()` - *Shift channel logic.*


---

**File:** `src/shared/ui/rich_text_editor/editor_constants.py`

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

**File:** `src/shared/ui/rich_text_editor/etymology_feature.py`

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
* `shared.services.document_manager.etymology_service.get_et

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

**File:** `src/shared/ui/rich_text_editor/image_features.py`

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
**Exposes:** `set_display_rect()` - *Configure display rect logic.*
**Exposes:** `clear_selection()` - *Clear the current crop selection.*
**Exposes:** `has_selection()` - *Check if there's a valid pending selection.*
**Exposes:** `get_selection()` - *Get the pending selection rect (normalized to display_rect origin).*
**Exposes:** `mousePressEvent()` - *Mousepressevent logic.*
**Exposes:** `mouseMoveEvent()` - *Mousemoveevent logic.*
**Exposes:** `mouseReleaseEvent()` - *Mousereleaseevent logic.*
**Exposes:** `apply_to_format()` - *Apply to format logic.*
**Emits:** `finished` - *Nervous System Signal.*
**Exposes:** `run()` - *Execute logic.*
**Exposes:** `get_final_qimage()` - *Retrieve final qimage logic.*
**Exposes:** `get_final_bytes_png()` - *Retrieve final bytes png logic.*
**Exposes:** `create_toolbar_action()` - *Return the insert image action for the toolbar.*
**Exposes:** `extend_context_menu()` - *Add image actions to context menu if applicable.*
**Exposes:** `insert_image()` - *Insert image logic.*
**Exposes:** `sepia_pixel()` - *Sepia pixel logic.*
**Exposes:** `shift_channel()` - *Shift channel logic.*
**Exposes:** `fade()` - *Fade logic.*


---

**File:** `src/shared/ui/rich_text_editor/list_features.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** List Features - The Ordinal Forge.

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
* None detected.

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

**File:** `src/shared/ui/rich_text_editor/ribbon_widget.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Ribbon Widget - The Office-Style Toolbar.

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
* `src/pillars/document_manager/ui/ribbon_widget.py`

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

**File:** `src/shared/ui/rich_text_editor/search_features.py`

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
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QTextCursor`
* `PyQt6.QtGui.QTextDocument`
* `PyQt6.QtGui.QTextFormat`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTextEdit`
*

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `find_next_requested` - *Nervous System Signal.*
**Emits:** `find_all_requested` - *Nervous System Signal.*
**Emits:** `replace_requested` - *Nervous System Signal.*
**Emits:** `replace_all_requested` - *Nervous System Signal.*
**Emits:** `navigate_requested` - *Nervous System Signal.*
**Exposes:** `set_not_found_state()` - *Configure not found state logic.*
**Exposes:** `show_results()` - *Display list of results.*
**Exposes:** `show_search_dialog()` - *Open (and create if needed) the search dialog.*
**Exposes:** `find_next()` - *Find next occurrence of text using document().find() for reliable selection.*
**Exposes:** `find_all()` - *Find all occurrences and populate results list.*
**Exposes:** `navigate_to()` - *Jump cursor to specific position, select the match, and center it.*
**Exposes:** `apply_highlight()` - *Apply a temporary light blue background highlight to the current selection.*
**Exposes:** `clear_highlight()` - *Clear the temporary search highlight.*
**Exposes:** `replace_current()` - *Replace current selection if it matches, then find next.*
**Exposes:** `replace_all()` - *Replace all occurrences.*


---

**File:** `src/shared/ui/rich_text_editor/shape_features.py`

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
**Exposes:** `custom_press()` - *Custom press logic.*


---

**File:** `src/shared/ui/rich_text_editor/shape_item.py`

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
* `src/pillars/document_manager/ui/shape_item.py`

**Key Interactions:**
**Exposes:** `create_shape_from_dict()` - *Factory function to create shape from dictionary.*
**Exposes:** `boundingRect()` - *Return the bounding rectangle.*
**Exposes:** `itemChange()` - *Handle item changes.*
**Exposes:** `mousePressEvent()` - *Handle mouse press for resize.*
**Exposes:** `mouseMoveEvent()` - *Handle mouse move for resize.*
**Exposes:** `mouseReleaseEvent()` - *Handle mouse release.*
**Exposes:** `contextMenuEvent()` - *Show right-click context menu.*
**Exposes:** `fill_color()` - *Fill color logic.*
**Exposes:** `fill_color()` - *Fill color logic.*
**Exposes:** `stroke_color()` - *Stroke color logic.*
**Exposes:** `stroke_color()` - *Stroke color logic.*
**Exposes:** `stroke_width()` - *Stroke width logic.*
**Exposes:** `stroke_width()` - *Stroke width logic.*
**Exposes:** `to_dict()` - *Serialize shape to dictionary.*
**Exposes:** `from_dict()` - *Create shape from dictionary.*
**Exposes:** `corner_radius()` - *Corner radius logic.*
**Exposes:** `corner_radius()` - *Corner radius logic.*
**Exposes:** `paint()` - *Paint logic.*
**Exposes:** `paint()` - *Paint logic.*
**Exposes:** `paint()` - *Paint logic.*
**Exposes:** `angle()` - *Angle logic.*
**Exposes:** `angle()` - *Angle logic.*
**Exposes:** `mousePressEvent()` - *Handle mouse press - check for rotation vs resize.*
**Exposes:** `mouseMoveEvent()` - *Handle mouse move for rotation or resize.*
**Exposes:** `boundingRect()` - *Override to include end decorations in bounding rect.*
**Exposes:** `start_style()` - *Start style logic.*
**Exposes:** `start_style()` - *Start style logic.*
**Exposes:** `end_style()` - *End style logic.*
**Exposes:** `end_style()` - *End style logic.*
**Exposes:** `start_arrow()` - *Start arrow logic.*
**Exposes:** `start_arrow()` - *Start arrow logic.*
**Exposes:** `end_arrow()` - *End arrow logic.*
**Exposes:** `end_arrow()` - *End arrow logic.*
**Exposes:** `paint()` - *Paint logic.*
**Exposes:** `to_dict()` - *Convert to dict logic.*
**Exposes:** `from_dict()` - *From dict logic.*
**Exposes:** `contextMenuEvent()` - *Extended context menu with end style options.*
**Exposes:** `sides()` - *Sides logic.*
**Exposes:** `sides()` - *Sides logic.*
**Exposes:** `skip()` - *Skip logic.*
**Exposes:** `skip()` - *Skip logic.*
**Exposes:** `is_star()` - *True if this is a star polygon (skip > 1).*
**Exposes:** `paint()` - *Paint logic.*
**Exposes:** `to_dict()` - *Serialize shape to dictionary.*
**Exposes:** `from_dict()` - *Create shape from dictionary.*
**Exposes:** `contextMenuEvent()` - *Extended context menu with polygon-specific options.*


---

**File:** `src/shared/ui/rich_text_editor/shape_overlay.py`

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

**File:** `src/shared/ui/rich_text_editor/spell_feature.py`

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
**Exposes:** `enabled()` - *Enabled logic.*
**Exposes:** `enabled()` - *Enabled logic.*
**Exposes:** `highlightBlock()` - *Called for each text block to apply highlighting.*
**Exposes:** `start_check()` - *Start checking from the beginning of the document.*
**Exposes:** `enabled()` - *Enabled logic.*
**Exposes:** `enabled()` - *Enabled logic.*
**Exposes:** `toggle()` - *Toggle spell checking on/off.*
**Exposes:** `create_ribbon_action()` - *Create action for the ribbon.*
**Exposes:** `create_toggle_action()` - *Create toggle action for enabling/disabling spell check.*
**Exposes:** `show_dialog()` - *Show the spell check dialog.*
**Exposes:** `extend_context_menu()` - *Add spelling suggestions to context menu if cursor is on misspelled word.*


---

**File:** `src/shared/ui/rich_text_editor/table_features.py`

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
**Exposes:** `get_data()` - *Retrieve data logic.*
**Exposes:** `apply_to_format()` - *Apply to format logic.*
**Exposes:** `apply_to_format()` - *Apply the border settings to the cell format.*
**Exposes:** `apply_to_format()` - *Apply to format logic.*
**Exposes:** `get_length()` - *Retrieve length logic.*
**Exposes:** `create_toolbar_button()` - *Create and configure the toolbar button for tables.*
**Exposes:** `extend_context_menu()` - *Add table actions to a context menu.*
**Exposes:** `insert_table()` - *Insert table logic.*


---

**File:** `src/shared/ui/scrollable_tab_bar.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QSizePolicy`
* `PyQt6.QtWidgets.QWidget`
* `shared.ui.theme.COLORS`

**Consumers (Who Needs It):**
* `src/pillars/astrology/ui/synastry_window.py`

**Key Interactions:**
**Emits:** `currentChanged` - *Nervous System Signal.*
**Exposes:** `add_tab()` - *Add a new tab button.*
**Exposes:** `set_current_index()` - *Set the active tab index.*
**Exposes:** `current_index()` - *Functional interface.*
**Exposes:** `count()` - *Functional interface.*


---

**File:** `src/shared/ui/theme.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Modern UI theme and styling for IsopGem application.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QPalette`
* `PyQt6.QtWidgets.QApplication`

**Consumers (Who Needs It):**
* `src/pillars/astrology/ui/advanced_analysis_panel.py`
* `src/pillars/astrology/ui/astro_settings_dialog.py`
* `src/pillars/astrology/ui/chariot_differentials_window.py`
* `src/pillars/astrology/ui/chariot_window.py`
* `src/pillars/astrology/ui/interpretation_widget.py`
* `src/pillars/astrology/ui/location_search_dialog.py`
* `src/pillars/astrology/ui/natal_chart_window.py`
* `src/pillars/astrology/ui/progressions_window.py`
* `src/pillars/astrology/ui/returns_window.py`
* `src/pillars/astrology/ui/synastry_window.py`
* `src/pillars/geometry/ui/nested_heptagons_window.py`
* `src/pillars/tq/ui/geometric_transitions_window.py`
* `src/pillars/tq/ui/quadset_analysis_window.py`
* `src/pillars/tq/ui/ternary_converter_window.py`
* `src/pillars/tq/ui/transitions_window.py`
* `src/shared/ui/scrollable_tab_bar.py`

**Key Interactions:**
**Exposes:** `get_app_stylesheet()` - *Get the complete application stylesheet.*
**Exposes:** `get_accent_button_style()` - *Get style for accent/success buttons.*
**Exposes:** `get_accent_button_hover_style()` - *Get hover style for accent buttons.*
**Exposes:** `get_card_style()` - *Get style for card-like containers.*
**Exposes:** `get_title_style()` - *Get style for title labels.*
**Exposes:** `apply_light_theme()` - *Apply a consistent light theme to the application using QPalette.*
**Exposes:** `get_subtitle_style()` - *Get style for subtitle labels.*


---

**File:** `src/shared/ui/virtual_keyboard.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Virtual keyboard widget for Hebrew and Greek text input.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QPalette`
* `PyQt6.QtWidgets.QButtonGroup`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLayoutItem`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTextEdit`
* `PyQt6.Q

**Consumers (Who Needs It):**
* `src/pillars/correspondences/ui/spreadsheet_window.py`
* `src/shared/ui/rich_text_editor/etymology_feature.py`
* `tests/rituals/rite_of_keyboard_styling.py`

**Key Interactions:**
**Exposes:** `get_shared_virtual_keyboard()` - *Return a singleton virtual keyboard instance, reparenting it if needed.*
**Emits:** `character_typed` - *Nervous System Signal.*
**Emits:** `backspace_pressed` - *Nervous System Signal.*
**Exposes:** `set_target_input()` - *Configure target input logic.*
**Exposes:** `set_target_editor()` - *Configure target editor logic.*
**Exposes:** `set_layout()` - *Public method to force switch layout (e.g. from external menu).*
**Exposes:** `showEvent()` - *Auto-position the keyboard when shown.*


---

**File:** `src/shared/ui/window_manager.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Centralized window manager for IsopGem application.

**Input (Ingests):**
* `parent`
* `main_window`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QWidget`
* `importlib`
* `logging`
* `shared.signals.navigation_bus.get_window_info`
* `shared.signals.navigation_bus.navigation_bus`
* `typing.Any`
* `typing.Dict`
* `typing.Optional`
* `typing.Type`

**Consumers (Who Needs It):**
* `scripts/verify_orbital_physics.py`
* `scripts/verify_send_to.py`
* `src/pillars/astrology/ui/planetary_positions_window.py`
* `src/pillars/gematria/ui/gematria_calculator_window.py`
* `src/pillars/time_mechanics/ui/zodiacal_circle_window.py`
* `tests/common/test_window_manager.py`

**Key Interactions:**
**Exposes:** `set_main_window()` - *Set the main window reference.*
**Exposes:** `open_window()` - *Open a tool window, allowing multiple instances if specified.*
**Exposes:** `close_window()` - *Close a specific window by ID.*
**Exposes:** `close_all_windows()` - *Close all managed windows.*
**Exposes:** `close_windows_of_type()` - *Close all open windows matching a given window type.*
**Exposes:** `is_window_open()` - *Check if a window is currently open.*
**Exposes:** `get_window()` - *Get reference to an open window.*
**Exposes:** `get_active_windows()` - *Get all currently active windows.*
**Exposes:** `get_window_count()` - *Get the number of currently open windows.*
**Exposes:** `raise_all_windows()` - *Bring all active windows to the front.*
**Exposes:** `do_raise()` - *Do raise logic.*


---

**File:** `src/shared/ui/worker.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Standardized Background Worker pattern for IsopGem.

**Input (Ingests):**
* `fn`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QObject`
* `PyQt6.QtCore.QRunnable`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtCore.pyqtSlot`
* `sys`
* `traceback`
* `typing.Any`
* `typing.Callable`
* `typing.Optional`

**Consumers (Who Needs It):**
* `scripts/verify_horizon_phase4.py`
* `src/pillars/astrology/ui/natal_chart_window.py`
* `src/pillars/astrology/ui/progressions_window.py`
* `src/pillars/astrology/ui/returns_window.py`
* `src/pillars/astrology/ui/synastry_window.py`

**Key Interactions:**
**Emits:** `finished` - *Nervous System Signal.*
**Emits:** `error` - *Nervous System Signal.*
**Emits:** `result` - *Nervous System Signal.*
**Emits:** `progress` - *Nervous System Signal.*
**Exposes:** `run()` - *Initialise the runner function with passed args, kwargs.*


---

**File:** `src/shared/utils/calculator_persistence.py`

**Role:** `[Tool] (Utility)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `version` (Field)
* `angle_mode` (Field)
* `memory` (Field)
* `history` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `json`
* `os`
* `pathlib.Path`
* `typing.Any`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/geometry/ui/advanced_scientific_calculator_window.py`

**Key Interactions:**
**Exposes:** `default_state()` - *Default state logic.*
**Exposes:** `get_default_state_path()` - *Return user-specific state path using XDG base directory.*
**Exposes:** `load_state()` - *Load state from JSON.*
**Exposes:** `save_state()` - *Persist state to JSON.*


---

**File:** `src/shared/utils/image_loader.py`

**Role:** `[Tool] (Utility)`

**Purpose:** Image Loader Utility.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PIL.ImageQt.ImageQt`
* `PIL.Image`
* `PyQt6.QtGui.QImage`
* `PyQt6.QtGui.QPixmap`
* `pathlib.Path`
* `sys`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `load_pixmap()` - *Load an image from a path into a QPixmap.*


---

**File:** `src/shared/utils/measure_conversion.py`

**Role:** `[Tool] (Utility)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `input_value` (Field)
* `from_name` (Field)
* `to_name` (Field)
* `base_value` (Field)
* `base_unit` (Field)
* `converted_value` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `typing.Any`
* `typing.Dict`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `src/pillars/geometry/ui/advanced_scientific_calculator_window.py`

**Key Interactions:**
**Exposes:** `parse_measure_value()` - *Parse a human-friendly numeric value.*
**Exposes:** `convert_between_units()` - *Convert between units using `to_si` factors and a shared `si_unit` base.*


---

**File:** `src/shared/utils/verse_parser.py`

**Role:** `[Tool] (Utility)`

**Purpose:** Utilities for parsing documents into verses by number.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `re`
* `typing.Any`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/gematria/utils/verse_parser.py`
* `src/shared/services/document_manager/verse_teacher_service.py`

**Key Interactions:**
**Exposes:** `parse_verses()` - *Parse the given plain text into numbered verses.*
**Exposes:** `next_non_space_char()` - *Next non space char logic.*
