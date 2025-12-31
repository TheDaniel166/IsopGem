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
* `src/pillars/correspondences/repos/table_repository.py`
* `src/pillars/correspondences/services/table_service.py`
* `src/shared/database.py`

**Key Interactions:**
**Exposes:** `to_dict()` - *Clean serialization for UI/Transport.*



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
**Exposes:** `add_rule()` - *Add rule logic.*
**Exposes:** `clear_all_rules()` - *Clear all rules logic.*
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
* `re`
* `shared.services.gematria.GreekCubeCalculator`
* `shared.services.gematria.GreekDigitalCalculator`
* `shared.services.gematria.GreekFullValueCalculator`
* `shared.services.gematria.GreekGematriaCalculator`
* `shared.services.gematria.GreekKolelCalculator`
* `shared.services.gematria.GreekLetterValueCalculator`
* `shared.services.gematria.GreekNextLetterCalculator`
* `shared.services.gematria.GreekOrdinalCalculator`
* `shared.services.gematria.GreekOr

**Consumers (Who Needs It):**
* `scripts/verify_boolean.py`
* `scripts/verify_formula_range.py`
* `scripts/verify_parser.py`
* `scripts/verify_string_functions.py`
* `scripts/verify_textjoin_none.py`
* `src/pillars/correspondences/ui/spreadsheet_view.py`
* `workflow_scripts/verification_seal.py`

**Key Interactions:**
**Exposes:** `func_gematria()` - *Func gematria logic.*
**Exposes:** `func_sum()` - *Func sum logic.*
**Exposes:** `func_average()` - *Func average logic.*
**Exposes:** `func_count()` - *Func count logic.*
**Exposes:** `func_min()` - *Func min logic.*
**Exposes:** `func_max()` - *Func max logic.*
**Exposes:** `func_if()` - *Func if logic.*
**Exposes:** `func_concat()` - *Func concat logic.*
**Exposes:** `func_abs()` - *Func abs logic.*
**Exposes:** `func_round()` - *Func round logic.*
**Exposes:** `func_floor()` - *Func floor logic.*
**Exposes:** `func_ceiling()` - *Func ceiling logic.*
**Exposes:** `func_int()` - *Func int logic.*
**Exposes:** `func_sqrt()` - *Func sqrt logic.*
**Exposes:** `func_power()` - *Func power logic.*
**Exposes:** `func_mod()` - *Func mod logic.*
**Exposes:** `func_pi()` - *Func pi logic.*
**Exposes:** `func_sin()` - *Func sin logic.*
**Exposes:** `func_cos()` - *Func cos logic.*
**Exposes:** `func_tan()` - *Func tan logic.*
**Exposes:** `func_asin()` - *Func asin logic.*
**Exposes:** `func_acos()` - *Func acos logic.*
**Exposes:** `func_atan()` - *Func atan logic.*
**Exposes:** `func_ln()` - *Func ln logic.*
**Exposes:** `func_log10()` - *Func log10 logic.*
**Exposes:** `func_len()` - *Func len logic.*
**Exposes:** `func_upper()` - *Func upper logic.*
**Exposes:** `func_lower()` - *Func lower logic.*
**Exposes:** `func_proper()` - *Func proper logic.*
**Exposes:** `func_left()` - *Func left logic.*
**Exposes:** `func_right()` - *Func right logic.*
**Exposes:** `func_mid()` - *Func mid logic.*
**Exposes:** `func_trim()` - *Func trim logic.*
**Exposes:** `func_replace()` - *Func replace logic.*
**Exposes:** `func_substitute()` - *Func substitute logic.*
**Exposes:** `func_textjoin()` - *Func textjoin logic.*
**Exposes:** `register()` - *Decorator to register a function with metadata.*
**Exposes:** `get()` - *Retrieve logic.*
**Exposes:** `get_metadata()` - *Retrieve metadata logic.*
**Exposes:** `get_all_metadata()` - *Returns list of all available formulas sorted by name.*
**Exposes:** `get_cipher_names()` - *Returns list of all registered registered Gematria cipher names.*
**Exposes:** `tokenize()` - *Tokenize logic.*
**Exposes:** `eat()` - *Eat logic.*
**Exposes:** `parse()` - *Parse logic.*
**Exposes:** `expr()` - *Parse comparison operations (lowest precedence).*
**Exposes:** `concatenation()` - *Concatenation logic.*
**Exposes:** `additive()` - *Additive logic.*
**Exposes:** `multiplicative()` - *Multiplicative logic.*
**Exposes:** `power()` - *Power logic.*
**Exposes:** `atom()` - *Atom logic.*
**Exposes:** `evaluate()` - *Evaluate a formula string, tracking the current dependency stack to avoid cycles.*
**Exposes:** `add()` - *Add logic.*
**Exposes:** `collect()` - *Collect logic.*
**Exposes:** `check()` - *Check logic.*
**Exposes:** `collect()` - *Collect logic.*
**Exposes:** `collect()` - *Collect logic.*
**Exposes:** `collect()` - *Collect logic.*
**Exposes:** `collect()` - *Collect logic.*
**Exposes:** `adjust_references()` - *Shift cell references in a formula by (row_delta, col_delta).*
**Exposes:** `decorator()` - *Decorator logic.*


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
* `workflow_scripts/verification_seal.py`

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
**Exposes:** `col_label()` - *Col label logic.*
**Exposes:** `sanitize_value()` - *Sanitize value logic.*


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
**Exposes:** `redo()` - *Redo logic.*
**Exposes:** `undo()` - *Undo logic.*
**Exposes:** `redo()` - *Redo logic.*
**Exposes:** `undo()` - *Undo logic.*
**Exposes:** `redo()` - *Redo logic.*
**Exposes:** `undo()` - *Undo logic.*
**Exposes:** `redo()` - *Redo logic.*
**Exposes:** `undo()` - *Undo logic.*
**Exposes:** `redo()` - *Redo logic.*
**Exposes:** `undo()` - *Undo logic.*
**Exposes:** `redo()` - *Redo logic.*
**Exposes:** `undo()` - *Undo logic.*


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
* `scripts/verify_send_to.py`

**Key Interactions:**
**Emits:** `finished` - *Nervous System Signal.*
**Emits:** `failed` - *Nervous System Signal.*
**Exposes:** `run()` - *Execute logic.*
**Exposes:** `get_values()` - *Retrieve values logic.*
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
**Exposes:** `get_options()` - *Retrieve options logic.*
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
**Exposes:** `setText()` - *Settext logic.*
**Exposes:** `update_active_input()` - *Called by parent window when grid selection changes.*
**Exposes:** `get_formula_text()` - *Reconstructs =NAME(Arg1, Arg2, ...)*
**Exposes:** `get_selected_formula()` - *Retrieve selected formula logic.*
**Exposes:** `get_insertion_text()` - *Retrieve insertion text logic.*
**Exposes:** `on_focus()` - *Handle focus logic.*


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
**Exposes:** `add_tab()` - *Add tab logic.*
**Exposes:** `set_current_index()` - *Configure current index logic.*
**Exposes:** `count()` - *Count logic.*
**Exposes:** `set_tab_text()` - *Configure tab text logic.*
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
* `scripts/verify_planetary_send.py`
* `tests/test_correspondences_cycles.py`
* `workflow_scripts/verification_seal.py`

**Key Interactions:**
**Exposes:** `fill_selection()` - *Fill target_rect with data/pattern from source_rect.*
**Exposes:** `clear_eval_cache()` - *Reset cached formula evaluations after mutations.*
**Exposes:** `get_cell_raw()` - *Retrieve cell raw logic.*
**Exposes:** `evaluate_cell()` - *Return the evaluated value for a cell with cycle protection and caching.*
**Exposes:** `get_cell_value()` - *Helper for Formula Engine to resolve references.*
**Exposes:** `rowCount()` - *Rowcount logic.*
**Exposes:** `columnCount()` - *Columncount logic.*
**Exposes:** `data()` - *Data logic.*
**Exposes:** `setData()` - *Setdata logic.*
**Exposes:** `headerData()` - *Headerdata logic.*
**Exposes:** `insertRows()` - *Insertrows logic.*
**Exposes:** `removeRows()` - *Removerows logic.*
**Exposes:** `insertColumns()` - *Insertcolumns logic.*
**Exposes:** `removeColumns()` - *Removecolumns logic.*
**Exposes:** `flags()` - *Flags logic.*
**Exposes:** `to_json()` - *Convert to json logic.*
**Exposes:** `sort_range()` - *Sorts the data in the given range based on key_col.*
**Exposes:** `paint()` - *Paint logic.*
**Exposes:** `createEditor()` - *Custom Editor to fix clipping and style issues.*
**Exposes:** `updateEditorGeometry()` - *Ensure editor fills the cell exactly.*
**Exposes:** `setEditorData()` - *Get raw data (formula) for editing.*
**Exposes:** `setModelData()` - *Save text back to model.*
**Exposes:** `get_html()` - *Retrieve html logic.*
**Emits:** `formula_return_pressed` - *Nervous System Signal.*
**Emits:** `editor_text_changed` - *Nervous System Signal.*
**Exposes:** `set_border_ui()` - *Receive Actions from Window.*
**Exposes:** `autofit()` - *Resize all columns and rows to fit content.*
**Exposes:** `resizeEvent()` - *Resizeevent logic.*
**Exposes:** `selectionChanged()` - *Selectionchanged logic.*
**Exposes:** `mouseMoveEvent()` - *Mousemoveevent logic.*
**Exposes:** `mousePressEvent()` - *Mousepressevent logic.*
**Exposes:** `mouseReleaseEvent()` - *Mousereleaseevent logic.*
**Exposes:** `keyPressEvent()` - *Intercept Copy/Paste Shortcuts.*
**Exposes:** `sort_key()` - *Sort key logic.*
**Exposes:** `get_pen()` - *Retrieve pen logic.*
**Exposes:** `draw_line()` - *Draw line logic.*


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
**Exposes:** `set_border_style()` - *Configure border style logic.*
**Exposes:** `set_border_width()` - *Configure border width logic.*
**Exposes:** `pick_border_color()` - *Pick border color logic.*
**Exposes:** `col_to_letter()` - *Col to letter logic.*
**Exposes:** `col_to_letter()` - *Col to letter logic.*
**Exposes:** `col_to_letter()` - *Col to letter logic.*
**Exposes:** `col_to_letter()` - *Col to letter logic.*
**Exposes:** `col_to_letter()` - *Col to letter logic.*
