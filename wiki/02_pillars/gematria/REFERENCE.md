# Gematria Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the "Muscle" and "Skin" of the Gematria pillar, mapping the logic of sacred numerology and scriptural analysis.










---

**File:** `src/pillars/gematria/models/calculation_entity.py`

**Role:** `[Bone] (Model)`

**Purpose:** SQLAlchemy entity for persisting gematria calculations (Shim).

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.models.gematria.CalculationEntity`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/gematria/models/calculation_record.py`

**Role:** `[Bone] (Model)`

**Purpose:** Data model for stored gematria calculations (Shim).

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.models.gematria.CalculationRecord`

**Consumers (Who Needs It):**
* `tests/gematria/test_calculation_service.py`
* `tests/gematria/test_sqlite_repository.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/gematria/models/els_models.py`

**Role:** `[Bone] (Model)`

**Purpose:** ELS (Equidistant Letter Sequence) data models.

**Input (Ingests):**
* `from_letter` (Field)
* `to_letter` (Field)
* `letters` (Field)
* `gematria_value` (Field)
* `term` (Field)
* `skip` (Field)
* `start_pos` (Field)
* `direction` (Field)
* `letter_positions` (Field)
* `intervening_segments` (Field)
* `term_gematria` (Field)
* `skip_gematria` (Field)
* `results` (Field)
* `source_text_length` (Field)
* `source_document` (Field)
* `letter` (Field)
* `position` (Field)
* `interval` (Field)
* `intervening_letters` (Field)
* `intervening_gematria` (Field)
* `term` (Field)
* `steps` (Field)
* `results` (Field)
* `term` (Field)
* `source_text_length` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `dataclasses.dataclass`
* `dataclasses.field`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `total_gematria()` - *Sum of term gematria + skip gematria.*
**Exposes:** `get_row_col_coords()` - *Calculate (row, col) coordinates for current grid configuration.*
**Exposes:** `total_hits()` - *Total hits logic.*
**Exposes:** `skip_distribution()` - *Count of results per skip interval.*
**Exposes:** `positions()` - *Positions logic.*
**Exposes:** `total_length()` - *Total path length (last position - first position).*
**Exposes:** `interval_sum()` - *Sum of all intervals.*
**Exposes:** `total_gematria()` - *Sum of all intervening letters' gematria.*


---

**File:** `src/pillars/gematria/repositories/calculation_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Whoosh-based repository for storing and searching gematria calculations.

**Input (Ingests):**
* `index_dir`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `datetime.datetime`
* `models.CalculationRecord`
* `os`
* `pathlib.Path`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `uuid`
* `whoosh.fields.BOOLEAN`
* `whoosh.fields.DATETIME`
* `whoosh.fields.ID`
* `whoosh.fields.KEYWORD`
* `whoosh.fields.NUMERIC`
* `whoosh.fields.Schema`
* `whoosh.fields.TEXT`
* `whoosh.index`
* `whoosh.qparser.MultifieldParser`
* `whoosh.query.And`
* `whoosh.query.Every`
* `whoosh.query.Or`
* `whoosh.query.Phrase`
* `whoosh.query.Term`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `save()` - *Save a calculation record.*
**Exposes:** `get_by_id()` - *Retrieve a calculation by ID.*
**Exposes:** `delete()` - *Delete a calculation record.*
**Exposes:** `search()` - *Search for calculation records.*
**Exposes:** `get_all()` - *Get all calculation records.*
**Exposes:** `get_by_value()` - *Get all calculations with a specific value.*
**Exposes:** `get_favorites()` - *Get all favorite calculations.*
**Exposes:** `get_by_tags()` - *Get calculations by tags.*
**Exposes:** `get_by_text()` - *Get calculations with the exact same text.*


---

**File:** `src/pillars/gematria/repositories/sqlite_calculation_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** SQLite-backed repository for gematria calculations.

**Input (Ingests):**
* `session_factory`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `contextlib.contextmanager`
* `datetime.datetime`
* `models.CalculationEntity`
* `models.CalculationRecord`
* `shared.database.SessionLocal`
* `sqlalchemy.or_`
* `sqlalchemy.orm.Session`
* `sqlalchemy.select`
* `typing.Callable`
* `typing.Iterator`
* `typing.List`
* `typing.Optional`
* `typing.Sequence`
* `uuid`

**Consumers (Who Needs It):**
* `scripts/migrate_gematria_whoosh_to_sqlite.py`
* `tests/gematria/test_sqlite_repository.py`
* `tests/rituals/rite_of_search.py`

**Key Interactions:**
**Exposes:** `save()` - *Insert or update a record, returning the saved version.*
**Exposes:** `get_by_id()` - *Fetch a record by primary key.*
**Exposes:** `delete()` - *Remove a record by ID.*
**Exposes:** `search()` - *Search calculations by metadata.*
**Exposes:** `get_all()` - *Retrieve all logic.*
**Exposes:** `get_by_value()` - *Retrieve by value logic.*
**Exposes:** `get_favorites()` - *Retrieve favorites logic.*
**Exposes:** `get_by_tags()` - *Retrieve by tags logic.*
**Exposes:** `get_by_text()` - *Fetch records with exact text match.*


---

**File:** `src/pillars/gematria/services/acrostic_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service for discovering acrostics and telestichs in text.

**Input (Ingests):**
* `found_word`
* `method`
* `source_indices`
* `source_text_units`
* `is_valid_word`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `logging`
* `pillars.gematria.services.corpus_dictionary_service.CorpusDictionaryService`
* `re`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `src/pillars/gematria/ui/acrostics_window.py`
* `tests/rituals/rite_of_acrostics.py`
* `tests/rituals/rite_of_word_acrostics.py`

**Key Interactions:**
**Exposes:** `find_acrostics()` - *Finds acrostics in the given text.*


---

**File:** `src/pillars/gematria/services/base_calculator.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Backward compatibility shim for BaseCalculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.services.gematria.base_calculator.GematriaCalculator`

**Consumers (Who Needs It):**
* `scripts/verify_gematria_send.py`
* `scripts/verify_text_analysis_send.py`
* `tests/gematria/test_calculation_service.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/gematria/services/batch_io_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Batch IO Service - The Granary Guard.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `csv`
* `pandas`
* `pathlib.Path`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `is_pandas_available()` - *Check if pandas is available for advanced file formats.*
**Exposes:** `read_file()` - *Read a file and return a list of dictionaries with normalized keys.*


---

**File:** `src/pillars/gematria/services/calculation_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service layer for managing gematria calculations.

**Input (Ingests):**
* `repository`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `datetime.datetime`
* `json`
* `models.CalculationRecord`
* `repositories.CalculationRepository`
* `shared.services.gematria.base_calculator.GematriaCalculator`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `tests/gematria/test_calculation_service.py`

**Key Interactions:**
**Exposes:** `save_calculation()` - *Save a new calculation.*
**Exposes:** `update_calculation()` - *Update an existing calculation's metadata.*
**Exposes:** `delete_calculation()` - *Delete a calculation.*
**Exposes:** `get_calculation()` - *Get a calculation by ID.*
**Exposes:** `search_calculations()` - *Search for calculations.*
**Exposes:** `get_all_calculations()` - *Get all calculations.*
**Exposes:** `get_calculations_by_value()` - *Find all calculations with a specific value.*
**Exposes:** `get_siblings_by_text()` - *Find all calculations sharing the same text (Siblings).*
**Exposes:** `get_favorite_calculations()` - *Get all favorite calculations.*
**Exposes:** `toggle_favorite()` - *Toggle the favorite status of a calculation.*
**Exposes:** `get_breakdown_from_record()` - *Parse breakdown JSON from record.*


---

**File:** `src/pillars/gematria/services/chiasmus_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service for discovering Chiastic (Mirror) patterns in text based on Gematria values.

**Input (Ingests):**
* `center_index` (Field)
* `depth` (Field)
* `left_indices` (Field)
* `right_indices` (Field)
* `source_units` (Field)
* `values` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `dataclasses.dataclass`
* `logging`
* `re`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `src/pillars/gematria/ui/chiastic_window.py`
* `tests/rituals/rite_of_chiasmus.py`

**Key Interactions:**
**Exposes:** `scan_text()` - *Scans text for Gematria-based Chiastic patterns.*


---

**File:** `src/pillars/gematria/services/corpus_dictionary_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service for building and managing a corpus-based dictionary.

**Input (Ingests):**
* `db_session`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `logging`
* `re`
* `shared.database.get_db`
* `shared.repositories.document_manager.document_repository.DocumentRepository`
* `sqlalchemy.orm.Session`
* `typing.Optional`
* `typing.Set`

**Consumers (Who Needs It):**
* `src/pillars/gematria/services/acrostic_service.py`
* `src/pillars/gematria/ui/acrostics_window.py`

**Key Interactions:**
**Exposes:** `load_dictionary()` - *Loads words from documents matching the collection filter.*
**Exposes:** `get_words()` - *Return a sorted list of all words in the dictionary.*
**Exposes:** `is_word()` - *Check if a candidate string exists in the loaded dictionary.*
**Exposes:** `word_count()` - *Word count logic.*


---

**File:** `src/pillars/gematria/services/els_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** ELS (Equidistant Letter Sequence) Search Service.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `logging`
* `models.els_models.ChainResult`
* `models.els_models.ChainSearchSummary`
* `models.els_models.ChainStep`
* `models.els_models.ELSInterveningSegment`
* `models.els_models.ELSResult`
* `models.els_models.ELSSearchSummary`
* `re`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_els.py`

**Key Interactions:**
**Exposes:** `prepare_text()` - *Strip text of non-letters, return stripped text and position map.*
**Exposes:** `get_grid_factors()` - *Calculate grid dimensions, handling primes and sparse factor counts.*
**Exposes:** `suggest_better_counts()` - *Suggest nearby letter counts with better factorization.*
**Exposes:** `search_els()` - *Search for ELS patterns in text.*
**Exposes:** `extract_intervening_letters()` - *Extract the letters between each pair of ELS hit positions.*
**Exposes:** `build_matrix()` - *Arrange stripped text into a grid for visualization.*
**Exposes:** `generate_triangular_positions()` - *Generate positions using triangular numbers: 0, 1, 3, 6, 10...*
**Exposes:** `generate_square_positions()` - *Generate positions using square numbers: 0, 1, 4, 9, 16...*
**Exposes:** `generate_fibonacci_positions()` - *Generate positions using cumulative Fibonacci skips: 0, 1, 2, 4, 7, 12, 20...*
**Exposes:** `search_sequence()` - *Search for patterns using arithmetical sequences.*
**Exposes:** `search_chain()` - *Search for term by finding nearest occurrence of each letter in sequence.*


---

**File:** `src/pillars/gematria/services/greek_calculator.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Backward compatibility shim for GreekCalculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.services.gematria.greek_calculator.GreekCubeCalculator`
* `shared.services.gematria.greek_calculator.GreekDigitalCalculator`
* `shared.services.gematria.greek_calculator.GreekFullValueCalculator`
* `shared.services.gematria.greek_calculator.GreekGematriaCalculator`
* `shared.services.gematria.greek_calculator.GreekKolelCalculator`
* `shared.services.gematria.greek_calculator.GreekLetterValueCalculator`
* `shared.services.gematria.greek_calculator.GreekNextLetterCalculator`
* `shared.se

**Consumers (Who Needs It):**
* `src/pillars/gematria/ui/chiastic_window.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/gematria/services/hebrew_calculator.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Backward compatibility shim for HebrewCalculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.services.gematria.hebrew_calculator.HebrewAlbamCalculator`
* `shared.services.gematria.hebrew_calculator.HebrewAtBashCalculator`
* `shared.services.gematria.hebrew_calculator.HebrewCubeCalculator`
* `shared.services.gematria.hebrew_calculator.HebrewFullValueCalculator`
* `shared.services.gematria.hebrew_calculator.HebrewGematriaCalculator`
* `shared.services.gematria.hebrew_calculator.HebrewIntegralReducedCalculator`
* `shared.services.gematria.hebrew_calculator.HebrewKolelCalculator`


**Consumers (Who Needs It):**
* `src/pillars/gematria/ui/chiastic_window.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/gematria/services/smart_filter_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Smart Filter Service - The Linguistic Sieve.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `logging`
* `spacy`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `load_model()` - *Lazy loads the spacy model.*
**Exposes:** `filter_phrases()` - *Filters a list of matches.*


---

**File:** `src/pillars/gematria/services/text_analysis_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Text Analysis Service - The Resonance Scanner.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `logging`
* `services.base_calculator.GematriaCalculator`
* `shared.services.document_manager.verse_teacher_service.verse_teacher_service_context`
* `typing.Any`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`
* `utils.numeric_utils.sum_numeric_face_values`
* `utils.verse_parser.parse_verses`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `find_value_matches()` - *Find all text segments that match the target gematria value using Fast Scan.*
**Exposes:** `calculate_text()` - *Calculate value for text helper.*
**Exposes:** `calculate_stats()` - *Calculate statistics for the text using the given calculator.*
**Exposes:** `parse_verses()` - *Parse text into verses, using metadata if available.*


---

**File:** `src/pillars/gematria/services/tq_calculator.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Backward compatibility shim for TQCalculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.services.gematria.tq_calculator.TQGematriaCalculator`
* `shared.services.gematria.tq_calculator.TQPositionCalculator`
* `shared.services.gematria.tq_calculator.TQReducedCalculator`
* `shared.services.gematria.tq_calculator.TQSquareCalculator`
* `shared.services.gematria.tq_calculator.TQTriangularCalculator`

**Consumers (Who Needs It):**
* `src/pillars/gematria/ui/chiastic_window.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/gematria/ui/acrostics_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Window for the Acrostic Discovery Tool.

**Input (Ingests):**
* `window_manager`
* `parent`
* `words`
* `parent`
* `source_units`
* `method`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTableWidgetItem`
* `PyQt6.QtWidgets.QTableWidget`
* `PyQt6.QtWidgets.QTextEdit`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `setup_ui()` - *Setup ui logic.*
**Exposes:** `on_result_double_clicked()` - *Opens the highlight dialog for the selected result.*
**Exposes:** `load_dictionary()` - *Loads the dictionary from the 'Holy' corpus.*
**Exposes:** `view_dictionary()` - *View dictionary logic.*
**Exposes:** `load_document_dialog()` - *Load document dialog logic.*
**Exposes:** `load_document_text()` - *Load document text logic.*
**Exposes:** `calculate_gematria()` - *Simple TQ Cipher (A=1, B=2...) calculation.*
**Exposes:** `run_search()` - *Execute search logic.*
**Exposes:** `update_list()` - *Update list logic.*
**Exposes:** `filter_list()` - *Filter list logic.*
**Exposes:** `generate_html()` - *Generates HTML with red bolded letters for the acrostic.*


---

**File:** `src/pillars/gematria/ui/batch_calculator_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Great Harvest window for sowing seeds (importing) and reaping calculations.

**Input (Ingests):**
* `data`
* `calculators`
* `service`
* `calculators`
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.QThread`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QCloseEvent`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QImage`
* `PyQt6.QtGui.QPalette`
* `PyQt6.QtGui.QPixmap`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt

**Consumers (Who Needs It):**
* `scripts/verify_batch_send.py`
* `scripts/verify_planetary_send.py`

**Key Interactions:**
**Emits:** `progress_updated` - *Nervous System Signal.*
**Emits:** `calculation_completed` - *Nervous System Signal.*
**Emits:** `processing_finished` - *Nervous System Signal.*
**Exposes:** `run()` - *Process all calculations.*
**Exposes:** `stop()` - *Stop processing.*
**Exposes:** `closeEvent()` - *Closeevent logic.*


---

**File:** `src/pillars/gematria/ui/chain_results_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Chain Search Results Window - Non-modal window for displaying chain search results.

**Input (Ingests):**
* `summary`
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSpinBox`
* `PyQt6.QtWidgets.QTableWidgetItem`
* `PyQt6.QtWidgets.QTableWidget`
* `PyQt6.QtWidgets.QTextBrowser`
* `PyQt6.QtWidg

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `result_selected` - *Nervous System Signal.*
**Exposes:** `set_highlight_callback()` - *Set callback for when a result is selected.*


---

**File:** `src/pillars/gematria/ui/chiastic_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Window for the Chiastic TQ Finder tool.

**Input (Ingests):**
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSpinBox`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QTextEdit`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `pillars.gematria.services.chiasmus_service.ChiasmusService`
* `pillars.gematria.

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `setup_ui()` - *Setup ui logic.*
**Exposes:** `load_document_dialog()` - *Load document dialog logic.*
**Exposes:** `load_document_text()` - *Load document text logic.*
**Exposes:** `scan_text()` - *Scan text logic.*
**Exposes:** `display_pattern()` - *Display pattern logic.*
**Exposes:** `generate_viz_html()` - *Generates V-shape or Mirror HTML.*


---

**File:** `src/pillars/gematria/ui/components.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** UI Components - The Gematria Display Widgets.

**Input (Ingests):**
* `char`
* `value`
* `parent`
* `value`
* `system_name`
* `parent`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPoint`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QSizePolicy`
* `PyQt6.QtWidgets.QSpacerItem`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `totalContextMenuRequested` - *Nervous System Signal.*
**Exposes:** `clear()` - *Clear the dashboard and reset to initial state.*
**Exposes:** `display_results()` - *Update the dashboard with new results.*
**Exposes:** `display_comparison()` - *Update the dashboard with comparison results.*


---

**File:** `src/pillars/gematria/ui/database_tools_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Database management tools window for cleaning and maintaining calculation database.

**Input (Ingests):**
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QProgressDialog`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTableWidgetItem`
* `PyQt6.QtWidgets.QTableWidget`
* `PyQt6.QtWidgets.

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/gematria/ui/document_selector.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Document Selector - The Archive Picker.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QVBoxLayout`
* `shared.database.get_db`
* `shared.repositories.document_manager.document_repository.DocumentRepository`

**Consumers (Who Needs It):**
* `src/pillars/gematria/ui/acrostics_window.py`
* `src/pillars/gematria/ui/chiastic_window.py`

**Key Interactions:**
**Exposes:** `load_docs()` - *Load docs logic.*
**Exposes:** `update_list()` - *Update list logic.*
**Exposes:** `filter_list()` - *Filter list logic.*
**Exposes:** `get_selected_doc_id()` - *Retrieve selected doc id logic.*


---

**File:** `src/pillars/gematria/ui/els_grid_view.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** ELS Grid View - Zoomable, pannable letter matrix visualization.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QRectF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QWheelEvent`
* `PyQt6.QtWidgets.QGraphicsRectItem`
* `PyQt6.QtWidgets.QGraphicsScene`
* `PyQt6.QtWidgets.QGraphicsTextItem`
* `PyQt6.QtWidgets.QGraphicsView`
* `logging`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `cell_clicked` - *Nervous System Signal.*
**Exposes:** `set_grid()` - *Populate the grid with letters.*
**Exposes:** `highlight_sequence()` - *Highlight cells at given positions.*
**Exposes:** `clear_highlights()` - *Remove all highlight overlays.*
**Exposes:** `center_on_cell()` - *Center the view on a specific cell.*
**Exposes:** `center_on_position()` - *Center view on a linear position.*
**Exposes:** `get_zoom()` - *Get current zoom factor.*
**Exposes:** `set_zoom()` - *Set absolute zoom factor.*
**Exposes:** `zoom_in()` - *Zoom in by 25%.*
**Exposes:** `zoom_out()` - *Zoom out by 25%.*
**Exposes:** `zoom_reset()` - *Reset to 100% zoom.*
**Exposes:** `wheelEvent()` - *Handle mouse wheel for zooming (with Ctrl) or scrolling.*


---

**File:** `src/pillars/gematria/ui/els_search_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** TQ Text Sequencer Window - Three-pane interface for ELS searching.

**Input (Ingests):**
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtWidgets.QButtonGroup`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDialogButtonBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidg

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/gematria/ui/gematria_calculator_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Gematria calculator tool window.

**Input (Ingests):**
* `calculators`
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QRadioButton`
* `PyQt6.QtWidgets.QSplitter`
*

**Consumers (Who Needs It):**
* `scripts/verify_gematria_send.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/gematria/ui/gematria_hub.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Gematria pillar hub - launcher interface for gematria tools.

**Input (Ingests):**
* `window_manager`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `acrostics_window.AcrosticsWindow`
* `batch_calculator_window.GreatHarvestWindow`
* `chiastic_window.ChiasticWindow`
* `database_tools_window.Dat

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/gematria/ui/holy_book_teacher_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Dialog for teaching the Holy Book parser and saving curated verses.

**Input (Ingests):**
* `document_id`
* `document_title`
* `allow_inline`
* `parent`
* `verse`
* `row`
* `teacher`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QKeySequence`
* `PyQt6.QtGui.QShortcut`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `verses_saved` - *Nervous System Signal.*


---

**File:** `src/pillars/gematria/ui/methods_reference_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Methods Reference Window - lists all gematria calculation systems with descriptions.

**Input (Ingests):**
* `calculators`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QTextEdit`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `services.base_calculator.GematriaCalculator`
* `typing.Dict`
* `typing.Lis

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `closeEvent()` - *Closeevent logic.*


---

**File:** `src/pillars/gematria/ui/saved_calculations_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Saved calculations browser window.

**Input (Ingests):**
* `window_manager`
* `parent`
* `initial_value`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMai

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `add_field()` - *Add field logic.*


---

**File:** `src/pillars/gematria/ui/text_analysis/document_tab.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Document Tab - The Text Analysis Container.

**Input (Ingests):**
* `document`
* `analysis_service`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QTextDocument`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QStackedWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `document_viewer.DocumentViewer`
* `services.text_analysis_service.TextAnalysisService`
* `shared.models.document_manager.document.Document`
* `typing.Optional`
* `verse_list.VerseList`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `text_selected` - *Nervous System Signal.*
**Emits:** `save_verse_requested` - *Nervous System Signal.*
**Emits:** `save_all_requested` - *Nervous System Signal.*
**Emits:** `save_text_requested` - *Nervous System Signal.*
**Emits:** `open_quadset_requested` - *Nervous System Signal.*
**Emits:** `teach_requested` - *Nervous System Signal.*
**Exposes:** `set_view_mode()` - *Configure view mode logic.*
**Exposes:** `refresh_verse_list()` - *Refresh verse list logic.*
**Exposes:** `update_settings()` - *Update settings logic.*
**Exposes:** `get_text()` - *Retrieve text logic.*
**Exposes:** `highlight_ranges()` - *Highlight ranges logic.*
**Exposes:** `clear_highlights()` - *Clear highlights logic.*


---

**File:** `src/pillars/gematria/ui/text_analysis/document_viewer.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Document Viewer - The Sacred Text Display.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QTextCharFormat`
* `PyQt6.QtGui.QTextCursor`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QTextEdit`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `text_selected` - *Nervous System Signal.*
**Emits:** `save_requested` - *Nervous System Signal.*
**Emits:** `calculate_requested` - *Nervous System Signal.*
**Emits:** `send_to_quadset_requested` - *Nervous System Signal.*
**Exposes:** `set_text()` - *Configure text logic.*
**Exposes:** `get_text()` - *Retrieve text logic.*
**Exposes:** `get_selected_text()` - *Retrieve selected text logic.*
**Exposes:** `select_range()` - *Select range logic.*
**Exposes:** `highlight_ranges()` - *Highlight list of (start, end) ranges.*
**Exposes:** `clear_highlights()` - *Clear highlights logic.*


---

**File:** `src/pillars/gematria/ui/text_analysis/main_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Exegesis Main Window - The Scriptural Inquiry.

**Input (Ingests):**
* `calculators`
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QImage`
* `PyQt6.QtGui.QPalette`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSplitter`
* `

**Consumers (Who Needs It):**
* `scripts/verify_text_analysis_send.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/gematria/ui/text_analysis/search_panel.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Search Panel - The Value Finder.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSpinBox`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `search_requested` - *Nervous System Signal.*
**Emits:** `result_selected` - *Nervous System Signal.*
**Emits:** `save_matches_requested` - *Nervous System Signal.*
**Emits:** `export_requested` - *Nervous System Signal.*
**Emits:** `smart_filter_requested` - *Nervous System Signal.*
**Emits:** `clear_requested` - *Nervous System Signal.*
**Exposes:** `set_active_tab()` - *Configure active tab logic.*
**Exposes:** `set_results()` - *Set matches and refresh display.*
**Exposes:** `clear_results()` - *Clear results logic.*
**Emits:** `send_to_tablet_requested` - *Nervous System Signal.*
**Exposes:** `contextMenuEvent()` - *Context menu for results.*


---

**File:** `src/pillars/gematria/ui/text_analysis/smart_filter_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Smart Filter Dialog - The Linguistic Purifier.

**Input (Ingests):**
* `matches`
* `matches`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QThread`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QProgressBar`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `services.smart_filter_service.SmartFilterService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `finished` - *Nervous System Signal.*
**Exposes:** `run()` - *Execute logic.*


---

**File:** `src/pillars/gematria/ui/text_analysis/stats_panel.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Stats Panel - The Numerological Summary.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `update_stats()` - *Update labels with stats dict.*


---

**File:** `src/pillars/gematria/ui/text_analysis/verse_list.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Verse List - The Sacred Stanza Catalog.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `typing.Any`
* `typing.Dict`
* `typing.List`
* `utils.numeric_utils.sum_numeric_face_values`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `verse_jump_requested` - *Nervous System Signal.*
**Emits:** `verse_save_requested` - *Nervous System Signal.*
**Emits:** `save_all_requested` - *Nervous System Signal.*
**Exposes:** `render_verses()` - *Render verses into the list.*
**Exposes:** `clear()` - *Clear logic.*


---

**File:** `src/pillars/gematria/ui/text_analysis_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Text Analysis Window - Redirect to new modular implementation.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `text_analysis.main_window.ExegesisWindow`

**Consumers (Who Needs It):**
* `src/pillars/gematria/ui/holy_book_teacher_window.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/gematria/utils/numeric_utils.py`

**Role:** `[Tool] (Utility)`

**Purpose:** Utility functions for numeric handling in gematria utilities.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `re`
* `typing.Any`

**Consumers (Who Needs It):**
* `tests/document/test_verse_parser.py`

**Key Interactions:**
**Exposes:** `sum_numeric_face_values()` - *Sum occurrences of numeric tokens in the text.*


---

**File:** `src/pillars/gematria/utils/verse_parser.py`

**Role:** `[Tool] (Utility)`

**Purpose:** Backward compatibility shim for verse_parser.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.utils.verse_parser.parse_verses`

**Consumers (Who Needs It):**
* `tests/document/test_verse_parser.py`

**Key Interactions:**
* Internal logic only.
