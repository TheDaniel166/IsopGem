# Time Mechanics Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the "Keeper of Time," mapping the harmonic cycles of the Tzolkin and the temporal circulation of energies.








---

**File:** `src/pillars/time_mechanics/models/thelemic_calendar_models.py`

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
* None detected.

**Key Interactions:**
**Exposes:** `is_prime_ditrune()` - *True if this is one of the 4 Prime Ditrune Sets (intercalary days).*
**Exposes:** `sign_letter()` - *Extract the zodiac sign letter (A-L) or None for Prime Ditrunes.*
**Exposes:** `sign_day()` - *Extract the day within the sign (0-29) or None for Prime Ditrunes.*


---

**File:** `src/pillars/time_mechanics/models/tzolkin_models.py`

**Role:** `[Bone] (Model)`

**Purpose:** Tzolkin Models - The Harmonic Cycle Data.

**Input (Ingests):**
* `gregorian_date` (Field)
* `kin` (Field)
* `tone` (Field)
* `sign` (Field)
* `sign_name` (Field)
* `cycle` (Field)
* `ditrune_decimal` (Field)
* `ditrune_ternary` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `dataclasses.dataclass`
* `datetime.date`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/time_mechanics/services/thelemic_calendar_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Thelemic Calendar Service - Loads and queries the Thelemic Calendar CSV.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `csv`
* `models.thelemic_calendar_models.ConrunePair`
* `models.thelemic_calendar_models.ZODIAC_SIGNS`
* `os`
* `pathlib.Path`
* `tq.services.ternary_service.TernaryService`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/astrology/ui/differential_natal_window.py`

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
**Exposes:** `decimal_to_ternary()` - *Functional interface.*
**Exposes:** `ternary_to_decimal()` - *Functional interface.*


---

**File:** `src/pillars/time_mechanics/services/tzolkin_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Tzolkin Service - The Temporal Navigator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `csv`
* `datetime.date`
* `logging`
* `models.tzolkin_models.TzolkinDate`
* `os`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `scripts/analyze_matrix_properties.py`
* `scripts/analyze_ternary_patterns.py`
* `scripts/analyze_trigram_tensor.py`
* `scripts/generate_conrune_deltas.py`
* `scripts/generate_cycle_nomenclature.py`
* `scripts/generate_kairos_names.py`
* `scripts/generate_spiral_deltas.py`
* `scripts/generate_spiral_matrix.py`
* `scripts/verify_columnar_symmetry.py`
* `scripts/verify_three_laws.py`
* `tests/rituals/rite_of_dynamis.py`
* `tests/rituals/rite_of_tzolkin.py`
* `tests/rituals/rite_of_tzolkin_grid.py`

**Key Interactions:**
**Exposes:** `from_gregorian()` - *Convert a Gregorian Date to a Tzolkin Date.*
**Exposes:** `get_epoch()` - *Functional interface.*
**Exposes:** `get_conrune()` - *Calculate the Conrune (Anti-Self) of a Ditrune.*
**Exposes:** `get_trigrams()` - *Split a Ditrune into its Upper (Sky) and Lower (Earth) Trigrams.*


---

**File:** `src/pillars/time_mechanics/ui/dynamis_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Dynamis Window - The Circulation of Energies.

**Input (Ingests):**
* `trigram_str`
* `size`
* `color`
* `style`
* `color`
* `radius`
* `parent`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QRectF`
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QLinearGradient`
* `PyQt6.QtGui.QPainterPath`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QRadialGradient`
* `PyQt6.QtWidgets.QGraphicsItem`
* `PyQt6.QtWidgets.QGraphicsScene`
* `PyQt6.QtWidgets.QGraphicsView`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QPushButton`
* `PyQ

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_hyperphysics.py`

**Key Interactions:**
**Exposes:** `boundingRect()` - *Functional interface.*
**Exposes:** `paint()` - *Functional interface.*
**Exposes:** `update_trigram()` - *Functional interface.*
**Exposes:** `boundingRect()` - *Functional interface.*
**Exposes:** `update_state()` - *Functional interface.*
**Exposes:** `paint()` - *Functional interface.*
**Exposes:** `boundingRect()` - *Functional interface.*
**Exposes:** `paint()` - *Functional interface.*
**Exposes:** `drawBackground()` - *Functional interface.*
**Exposes:** `drawForeground()` - *Functional interface.*
**Exposes:** `on_slider_change()` - *Functional interface.*
**Exposes:** `toggle_animation()` - *Functional interface.*
**Exposes:** `advance_frame()` - *Functional interface.*
**Exposes:** `update_positions()` - *Functional interface.*


---

**File:** `src/pillars/time_mechanics/ui/time_mechanics_hub.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Time Mechanics Hub - The Keeper of Time.

**Input (Ingests):**
* `window_manager`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `dynamis_window.TzolkinDynamisWindow`
* `tzolkin_window.TzolkinCalculatorWindow`
* `zodiacal_circle_window.ZodiacalCircleWindow`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `launch()` - *The method invoked by the WindowManager to show this sovereign domain.*
**Exposes:** `launch_tzolkin()` - *Functional interface.*
**Exposes:** `launch_dynamis()` - *Functional interface.*
**Exposes:** `launch_zodiacal_circle()` - *Functional interface.*


---

**File:** `src/pillars/time_mechanics/ui/tzolkin_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Tzolkin Calculator Window - The Harmonic Grid.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QDate`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QDateEdit`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTableWidgetItem`
* `PyQt6.QtWidgets.QTableWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `datetime.date`
* `datetime.timedelta`
* `models.tzolkin_models.Tzol

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/time_mechanics/ui/zodiacal_circle_widget.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Zodiacal Circle Widget - Interactive circular visualization.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QRectF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFontDatabase`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QRadialGradient`
* `PyQt6.QtWidgets.QToolTip`
* `PyQt6.QtWidgets.QWidget`
* `__future__.annotations`
* `datetime.datetime`
* `math`
* `models.thelemic_calendar_models.ASTRONOMICON_CHARS`
* `models.thelemic_calendar_models.ConrunePair`
* `models

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `degree_clicked` - *Nervous System Signal.*
**Exposes:** `mouseMoveEvent()` - *Handle mouse movement for hover effects.*
**Exposes:** `mousePressEvent()` - *Handle mouse click to select a degree.*
**Exposes:** `paintEvent()` - *Functional interface.*
**Exposes:** `set_selected_difference()` - *Programmatically select a difference value.*
**Exposes:** `set_active_divisors()` - *Set which divisors to show relationship lines for.*
**Exposes:** `get_divisors()` - *Return all available divisors with their info.*
**Exposes:** `set_show_reversal()` - *Toggle showing the reversal pair line.*
**Exposes:** `set_center_perspective()` - *Toggle center perspective mode.*


---

**File:** `src/pillars/time_mechanics/ui/zodiacal_circle_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Zodiacal Circle Window - Main window for Trigrammic Time Keeping.

**Input (Ingests):**
* `parent`
* `window_manager`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QDate`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDateEdit`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QSizePolicy`
* `PyQt6.QtWidgets.QSpinBox`
* `PyQt6.QtWidgets.QTabWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.
