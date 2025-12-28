



---

**File:** `src/pillars/correspondences/models/correspondence_models.py`

**Role:** `[Bone] (Model)`

**Purpose:** Correspondence Models - The Emerald Scrolls.

**Input (Ingests):**
* `id` (Column)
* `name` (Column)
* `created_at` (Column)
* `updated_at` (Column)
* `content` (Column)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `datetime.datetime`
* `shared.database.Base`
* `sqlalchemy.Column`
* `sqlalchemy.DateTime`
* `sqlalchemy.JSON`
* `sqlalchemy.String`
* `uuid`

**Consumers (Who Needs It):**
* `scripts/reproduce_crash_full.py`
* `src/pillars/correspondences/repos/table_repository.py`
* `src/pillars/correspondences/services/table_service.py`
* `src/shared/database.py`

**Key Interactions:**
**Exposes:** `to_dict()` - *Clean serialization for UI/Transport.*


---

**File:** `src/pillars/correspondences/repos/table_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Table Repository - The Guardian of Emerald Tablets.

**Input (Ingests):**
* `session`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `datetime.datetime`
* `pillars.correspondences.models.correspondence_models.CorrespondenceTable`
* `sqlalchemy.orm.Session`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `scripts/verify_send_to.py`
* `src/pillars/correspondences/services/table_service.py`

**Key Interactions:**
**Exposes:** `create()` - *Create a new table.*
**Exposes:** `get_all()` - *List all tables.*
**Exposes:** `get_by_id()` - *Retrieve a specific table.*
**Exposes:** `update()` - *Save changes to a table.*
**Exposes:** `delete()` - *Destroy a table.*
**Exposes:** `update_content()` - *Update just the content of a table.*
**Exposes:** `update_name()` - *Rename a table.*


---

**File:** `src/pillars/correspondences/services/border_engine.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Border Engine - The Architect of Boundaries.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `calculate_borders()` - *Determines the new border configuration for a set of selected indexes.*
**Exposes:** `update_existing_borders()` - *Updates the STYLE (color, width) of existing borders without adding new ones.*


---

**File:** `src/pillars/correspondences/services/conditional_formatting.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Conditional Formatting - The Rule Engine.

**Input (Ingests):**
* `rule_type` (Field)
* `value` (Field)
* `format_style` (Field)
* `ranges` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QRect`
* `PyQt6.QtGui.QColor`
* `dataclasses.dataclass`
* `typing.Any`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `scripts/verify_conditional.py`
* `src/pillars/correspondences/ui/spreadsheet_view.py`
* `src/pillars/correspondences/ui/spreadsheet_window.py`

**Key Interactions:**
**Exposes:** `add_rule()` - *Functional interface.*
**Exposes:** `clear_all_rules()` - *Functional interface.*
**Exposes:** `get_style()` - *Returns format dict if any rule matches, else None.*


---

**File:** `src/pillars/correspondences/services/formula_engine.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Formula Engine - The Spreadsheet Logic Core.

**Input (Ingests):**
* `engine`
* `tokens`
* `data_context`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `enum.Enum`
* `enum.auto`
* `math`
* `pillars.gematria.services.GreekCubeCalculator`
* `pillars.gematria.services.GreekDigitalCalculator`
* `pillars.gematria.services.GreekFullValueCalculator`
* `pillars.gematria.services.GreekGematriaCalculator`
* `pillars.gematria.services.GreekKolelCalculator`
* `pillars.gematria.services.GreekLetterValueCalculator`
* `pillars.gematria.services.GreekNextLetterCalculator`
* `pillars.gematria.services.GreekOrdinalCalculator`
* `pillars.gematria.services.Greek

**Consumers (Who Needs It):**
* `scripts/reproduce_parser_error.py`
* `scripts/verification_seal.py`
* `scripts/verify_boolean.py`
* `scripts/verify_formula_range.py`
* `scripts/verify_parser.py`
* `scripts/verify_string_functions.py`
* `scripts/verify_textjoin_none.py`
* `src/pillars/correspondences/ui/spreadsheet_view.py`

**Key Interactions:**
**Exposes:** `func_gematria()` - *Functional interface.*
**Exposes:** `func_sum()` - *Functional interface.*
**Exposes:** `func_average()` - *Functional interface.*
**Exposes:** `func_count()` - *Functional interface.*
**Exposes:** `func_min()` - *Functional interface.*
**Exposes:** `func_max()` - *Functional interface.*
**Exposes:** `func_if()` - *Functional interface.*
**Exposes:** `func_concat()` - *Functional interface.*
**Exposes:** `func_abs()` - *Functional interface.*
**Exposes:** `func_round()` - *Functional interface.*
**Exposes:** `func_floor()` - *Functional interface.*
**Exposes:** `func_ceiling()` - *Functional interface.*
**Exposes:** `func_int()` - *Functional interface.*
**Exposes:** `func_sqrt()` - *Functional interface.*
**Exposes:** `func_power()` - *Functional interface.*
**Exposes:** `func_mod()` - *Functional interface.*
**Exposes:** `func_pi()` - *Functional interface.*
**Exposes:** `func_sin()` - *Functional interface.*
**Exposes:** `func_cos()` - *Functional interface.*
**Exposes:** `func_tan()` - *Functional interface.*
**Exposes:** `func_asin()` - *Functional interface.*
**Exposes:** `func_acos()` - *Functional interface.*
**Exposes:** `func_atan()` - *Functional interface.*
**Exposes:** `func_ln()` - *Functional interface.*
**Exposes:** `func_log10()` - *Functional interface.*
**Exposes:** `func_len()` - *Functional interface.*
**Exposes:** `func_upper()` - *Functional interface.*
**Exposes:** `func_lower()` - *Functional interface.*
**Exposes:** `func_proper()` - *Functional interface.*
**Exposes:** `func_left()` - *Functional interface.*
**Exposes:** `func_right()` - *Functional interface.*
**Exposes:** `func_mid()` - *Functional interface.*
**Exposes:** `func_trim()` - *Functional interface.*
**Exposes:** `func_replace()` - *Functional interface.*
**Exposes:** `func_substitute()` - *Functional interface.*
**Exposes:** `func_textjoin()` - *Functional interface.*
**Exposes:** `register()` - *Decorator to register a function with metadata.*
**Exposes:** `get()` - *Functional interface.*
**Exposes:** `get_metadata()` - *Functional interface.*
**Exposes:** `get_all_metadata()` - *Returns list of all available formulas sorted by name.*
**Exposes:** `get_cipher_names()` - *Returns list of all registered registered Gematria cipher names.*
**Exposes:** `tokenize()` - *Functional interface.*
**Exposes:** `eat()` - *Functional interface.*
**Exposes:** `parse()` - *Functional interface.*
**Exposes:** `expr()` - *Parse comparison operations (lowest precedence).*
**Exposes:** `concatenation()` - *Functional interface.*
**Exposes:** `additive()` - *Functional interface.*
**Exposes:** `multiplicative()` - *Functional interface.*
**Exposes:** `power()` - *Functional interface.*
**Exposes:** `atom()` - *Functional interface.*
**Exposes:** `evaluate()` - *Evaluate a formula string, tracking the current dependency stack to avoid cycles.*
**Exposes:** `add()` - *Functional interface.*
**Exposes:** `collect()` - *Functional interface.*
**Exposes:** `check()` - *Functional interface.*
**Exposes:** `collect()` - *Functional interface.*
**Exposes:** `collect()` - *Functional interface.*
**Exposes:** `collect()` - *Functional interface.*
**Exposes:** `collect()` - *Functional interface.*
**Exposes:** `adjust_references()` - *Shift cell references in a formula by (row_delta, col_delta).*
**Exposes:** `decorator()` - *Functional interface.*


---

**File:** `src/pillars/correspondences/services/formula_helper.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Formula Helper - The Wizard's Apprentice.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `formula_engine.FormulaMetadata`
* `formula_engine.FormulaRegistry`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `scripts/verification_seal.py`

**Key Interactions:**
**Exposes:** `get_all_definitions()` - *Returns all registered formulas.*
**Exposes:** `get_categories()` - *Returns unique list of categories (e.g. Math, Esoteric).*
**Exposes:** `search()` - *Search for formulas by name or description.*
**Exposes:** `validate_syntax()` - *Basic syntax check.*


---

**File:** `src/pillars/correspondences/services/ingestion_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Ingestion Service - The Alchemist.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pandas`
* `typing.Any`
* `typing.Dict`

**Consumers (Who Needs It):**
* `src/pillars/correspondences/ui/correspondence_hub.py`

**Key Interactions:**
**Exposes:** `ingest_file()` - *Read a file and return the JSON structure for the CorrespondenceTable.*
**Exposes:** `create_empty()` - *Create a blank grid (larger default for immediate usability).*
**Exposes:** `col_label()` - *Functional interface.*
**Exposes:** `sanitize_value()` - *Functional interface.*


---

**File:** `src/pillars/correspondences/services/table_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Table Service - The Steward of the Tablets.

**Input (Ingests):**
* `session`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `pillars.correspondences.models.correspondence_models.CorrespondenceTable`
* `pillars.correspondences.repos.table_repository.TableRepository`
* `sqlalchemy.orm.Session`
* `typing.Any`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/correspondences/ui/correspondence_hub.py`
* `src/pillars/correspondences/ui/spreadsheet_window.py`

**Key Interactions:**
**Exposes:** `create_table()` - *Create a new correspondence table.*
**Exposes:** `list_tables()` - *Retrieve all scrolls from the library.*
**Exposes:** `get_table()` - *Retrieve a specific scroll.*
**Exposes:** `save_content()` - *Update the content of a scroll.*
**Exposes:** `rename_table()` - *Rename a scroll.*
**Exposes:** `destoy_table()` - *Destroy a scroll forever.*


---

**File:** `src/pillars/correspondences/services/undo_commands.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Undo Commands - The Chronicle of Edits.

**Input (Ingests):**
* `model`
* `index`
* `new_value`
* `role`
* `model`
* `position`
* `rows`
* `model`
* `position`
* `rows`
* `model`
* `position`
* `columns`
* `model`
* `position`
* `columns`
* `model`
* `range_rect`
* `old_block`
* `new_block`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QModelIndex`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QUndoCommand`

**Consumers (Who Needs It):**
* `src/pillars/correspondences/ui/spreadsheet_view.py`

**Key Interactions:**
**Exposes:** `redo()` - *Functional interface.*
**Exposes:** `undo()` - *Functional interface.*
**Exposes:** `redo()` - *Functional interface.*
**Exposes:** `undo()` - *Functional interface.*
**Exposes:** `redo()` - *Functional interface.*
**Exposes:** `undo()` - *Functional interface.*
**Exposes:** `redo()` - *Functional interface.*
**Exposes:** `undo()` - *Functional interface.*
**Exposes:** `redo()` - *Functional interface.*
**Exposes:** `undo()` - *Functional interface.*
**Exposes:** `redo()` - *Functional interface.*
**Exposes:** `undo()` - *Functional interface.*


---

**File:** `src/pillars/correspondences/ui/correspondence_hub.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Correspondence Hub - The Emerald Tablet Library.

**Input (Ingests):**
* `path`
* `parent`
* `parent`
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QObject`
* `PyQt6.QtCore.QPoint`
* `PyQt6.QtCore.QThread`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtWidgets.QDialogButtonBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt

**Consumers (Who Needs It):**
* `scripts/reproduce_crash_full.py`
* `scripts/verify_send_to.py`
* `src/pillars/astrology/ui/planetary_positions_window.py`
* `src/pillars/gematria/ui/batch_calculator_window.py`
* `src/pillars/gematria/ui/gematria_calculator_window.py`
* `src/pillars/gematria/ui/text_analysis/main_window.py`
* `src/pillars/time_mechanics/ui/zodiacal_circle_window.py`
* `src/pillars/tq/ui/transitions_window.py`

**Key Interactions:**
**Emits:** `finished` - *Nervous System Signal.*
**Emits:** `failed` - *Nervous System Signal.*
**Exposes:** `run()` - *Functional interface.*
**Exposes:** `get_values()` - *Functional interface.*
**Exposes:** `receive_import()` - *Public API: specific import method for other pillars.*


---

**File:** `src/pillars/correspondences/ui/find_replace_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Find Replace Dialog - The Seeker's Lens.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QVBoxLayout`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `find_next_requested` - *Nervous System Signal.*
**Emits:** `find_all_requested` - *Nervous System Signal.*
**Emits:** `replace_requested` - *Nervous System Signal.*
**Emits:** `replace_all_requested` - *Nervous System Signal.*
**Emits:** `navigation_requested` - *Nervous System Signal.*
**Exposes:** `show_find_mode()` - *Focus Find input.*
**Exposes:** `show_replace_mode()` - *Focus Replace input (but usually Find is first).*
**Exposes:** `get_options()` - *Functional interface.*
**Exposes:** `show_results()` - *Populate the list widget.*


---

**File:** `src/pillars/correspondences/ui/formula_wizard.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Formula Wizard - The Scribe's Grimoire.

**Input (Ingests):**
* `parent`
* `metadata`
* `engine`
* `parent`
* `engine`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDialogButtonBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QTextBrowser`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `services

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `valueChanged` - *Nervous System Signal.*
**Exposes:** `text()` - *Returns the formatted cipher string.*
**Exposes:** `setText()` - *Functional interface.*
**Exposes:** `update_active_input()` - *Called by parent window when grid selection changes.*
**Exposes:** `get_formula_text()` - *Reconstructs =NAME(Arg1, Arg2, ...)*
**Exposes:** `get_selected_formula()` - *Functional interface.*
**Exposes:** `get_insertion_text()` - *Functional interface.*
**Exposes:** `on_focus()` - *Functional interface.*


---

**File:** `src/pillars/correspondences/ui/scroll_tab_bar.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Scroll Tab Bar - The Sheet Navigator.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QIcon`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QStyle`
* `PyQt6.QtWidgets.QTabBar`
* `PyQt6.QtWidgets.QToolButton`
* `PyQt6.QtWidgets.QWidget`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `tab_added` - *Nervous System Signal.*
**Emits:** `tab_changed` - *Nervous System Signal.*
**Emits:** `tab_renamed` - *Nervous System Signal.*
**Emits:** `show_all_tabs` - *Nervous System Signal.*
**Exposes:** `add_tab()` - *Functional interface.*
**Exposes:** `set_current_index()` - *Functional interface.*
**Exposes:** `count()` - *Functional interface.*
**Exposes:** `set_tab_text()` - *Functional interface.*
**Exposes:** `update_menu()` - *Populate the ≡ menu with actions to jump to tabs.*


---

**File:** `src/pillars/correspondences/ui/spreadsheet_view.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Spreadsheet View - The Emerald Grid Renderer.

**Input (Ingests):**
* `data_json`
* `parent`
* `initial_html`
* `parent`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QAbstractTableModel`
* `PyQt6.QtCore.QEvent`
* `PyQt6.QtCore.QItemSelectionModel`
* `PyQt6.QtCore.QItemSelectionRange`
* `PyQt6.QtCore.QModelIndex`
* `PyQt6.QtCore.QPoint`
* `PyQt6.QtCore.QRect`
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAbstractTextDocumentLayout`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QKeyEvent`
* `PyQt6.QtGui.QKeySequence`
* `

**Consumers (Who Needs It):**
* `scripts/verification_seal.py`
* `scripts/verify_planetary_send.py`
* `tests/test_correspondences_cycles.py`

**Key Interactions:**
**Exposes:** `fill_selection()` - *Fill target_rect with data/pattern from source_rect.*
**Exposes:** `clear_eval_cache()` - *Reset cached formula evaluations after mutations.*
**Exposes:** `get_cell_raw()` - *Functional interface.*
**Exposes:** `evaluate_cell()` - *Return the evaluated value for a cell with cycle protection and caching.*
**Exposes:** `get_cell_value()` - *Helper for Formula Engine to resolve references.*
**Exposes:** `rowCount()` - *Functional interface.*
**Exposes:** `columnCount()` - *Functional interface.*
**Exposes:** `data()` - *Functional interface.*
**Exposes:** `setData()` - *Functional interface.*
**Exposes:** `headerData()` - *Functional interface.*
**Exposes:** `insertRows()` - *Functional interface.*
**Exposes:** `removeRows()` - *Functional interface.*
**Exposes:** `insertColumns()` - *Functional interface.*
**Exposes:** `removeColumns()` - *Functional interface.*
**Exposes:** `flags()` - *Functional interface.*
**Exposes:** `to_json()` - *Functional interface.*
**Exposes:** `sort_range()` - *Sorts the data in the given range based on key_col.*
**Exposes:** `paint()` - *Functional interface.*
**Exposes:** `createEditor()` - *Custom Editor to fix clipping and style issues.*
**Exposes:** `updateEditorGeometry()` - *Ensure editor fills the cell exactly.*
**Exposes:** `setEditorData()` - *Get raw data (formula) for editing.*
**Exposes:** `setModelData()` - *Save text back to model.*
**Exposes:** `get_html()` - *Functional interface.*
**Emits:** `formula_return_pressed` - *Nervous System Signal.*
**Emits:** `editor_text_changed` - *Nervous System Signal.*
**Exposes:** `set_border_ui()` - *Receive Actions from Window.*
**Exposes:** `autofit()` - *Resize all columns and rows to fit content.*
**Exposes:** `resizeEvent()` - *Functional interface.*
**Exposes:** `selectionChanged()` - *Functional interface.*
**Exposes:** `mouseMoveEvent()` - *Functional interface.*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Exposes:** `mouseReleaseEvent()` - *Functional interface.*
**Exposes:** `keyPressEvent()` - *Intercept Copy/Paste Shortcuts.*
**Exposes:** `sort_key()` - *Functional interface.*
**Exposes:** `get_pen()` - *Functional interface.*
**Exposes:** `draw_line()` - *Functional interface.*


---

**File:** `src/pillars/correspondences/ui/spreadsheet_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Spreadsheet Window - The Sovereign Tablet Editor.

**Input (Ingests):**
* `table_id`
* `name`
* `content`
* `service`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QEvent`
* `PyQt6.QtCore.QItemSelectionRange`
* `PyQt6.QtCore.QItemSelection`
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QIcon`
* `PyQt6.QtWidgets.QColorDialog`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDockWidget`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QFontComboBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.Q

**Consumers (Who Needs It):**
* `scripts/reproduce_textjoin.py`
* `scripts/verify_context_menu.py`
* `scripts/verify_copy_paste.py`
* `scripts/verify_copy_values.py`
* `scripts/verify_csv_io.py`
* `scripts/verify_delete_key.py`
* `scripts/verify_keyboard_nav.py`
* `scripts/verify_sorting.py`
* `scripts/verify_unified_edit.py`
* `src/pillars/correspondences/ui/correspondence_hub.py`

**Key Interactions:**
**Exposes:** `eventFilter()` - *Hijack mouse clicks and KEY PRESSES on the viewport/editor when in Reference Mode.*
**Exposes:** `set_border_style()` - *Functional interface.*
**Exposes:** `set_border_width()` - *Functional interface.*
**Exposes:** `pick_border_color()` - *Functional interface.*
**Exposes:** `col_to_letter()` - *Functional interface.*
**Exposes:** `col_to_letter()` - *Functional interface.*
**Exposes:** `col_to_letter()` - *Functional interface.*
**Exposes:** `col_to_letter()` - *Functional interface.*
**Exposes:** `col_to_letter()` - *Functional interface.*
