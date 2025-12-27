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
**Exposes:** `add_nodes()` - *Functional interface.*


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
* `src/pillars/astrology/ui/interpretation_widget.py`
* `src/pillars/tq/ui/geometric_transitions_window.py`
* `src/pillars/tq/ui/quadset_analysis_window.py`
* `src/pillars/tq/ui/ternary_converter_window.py`
* `src/pillars/tq/ui/transitions_window.py`

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
* `src/pillars/document_manager/ui/etymology_feature.py`
* `tests/rituals/rite_of_keyboard_styling.py`

**Key Interactions:**
**Exposes:** `get_shared_virtual_keyboard()` - *Return a singleton virtual keyboard instance, reparenting it if needed.*
**Emits:** `character_typed` - *Nervous System Signal.*
**Emits:** `backspace_pressed` - *Nervous System Signal.*
**Exposes:** `set_target_input()` - *Functional interface.*
**Exposes:** `set_target_editor()` - *Functional interface.*
**Exposes:** `set_layout()` - *Public method to force switch layout (e.g. from external menu).*
**Exposes:** `showEvent()` - *Auto-position the keyboard when shown.*


---

**File:** `src/shared/ui/window_manager.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Centralized window manager for IsopGem application.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QWidget`
* `logging`
* `typing.Dict`
* `typing.Optional`
* `typing.Type`

**Consumers (Who Needs It):**
* `scripts/verify_send_to.py`
* `src/pillars/astrology/ui/planetary_positions_window.py`
* `src/pillars/gematria/ui/gematria_calculator_window.py`
* `src/pillars/time_mechanics/ui/zodiacal_circle_window.py`
* `tests/common/test_window_manager.py`

**Key Interactions:**
**Exposes:** `open_window()` - *Open a tool window, allowing multiple instances if specified.*
**Exposes:** `close_window()` - *Close a specific window by ID.*
**Exposes:** `close_all_windows()` - *Close all managed windows.*
**Exposes:** `close_windows_of_type()` - *Close all open windows matching a given window type.*
**Exposes:** `is_window_open()` - *Check if a window is currently open.*
**Exposes:** `get_window()` - *Get reference to an open window.*
**Exposes:** `get_active_windows()` - *Get all currently active windows.*
**Exposes:** `get_window_count()` - *Get the number of currently open windows.*
**Exposes:** `raise_all_windows()` - *Bring all active windows to the front.*
**Exposes:** `do_raise()` - *Functional interface.*


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
**Exposes:** `default_state()` - *Functional interface.*
**Exposes:** `get_default_state_path()` - *Return user-specific state path using XDG base directory.*
**Exposes:** `load_state()` - *Load state from JSON.*
**Exposes:** `save_state()` - *Persist state to JSON.*


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
