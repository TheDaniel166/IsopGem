# TQ Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the "Muscle" and "Bone" of the Trigrammaton Qabalah pillar, mapping the transformational engines of the Ternary path.








---

**File:** `src/pillars/tq/models/amun_sound.py`

**Role:** `[Bone] (Model)`

**Purpose:** Amun Sound Calculator - The Symphonic Engine.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `services.baphomet_color_service.BaphometColorService`
* `services.ternary_service.TernaryService`
* `symphony_config.SYMPHONY_FAMILIES`
* `symphony_config.SymphonyNucleation`
* `typing.Any`
* `typing.Dict`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `scripts/export_amun_data.py`
* `tests/test_amun_sound.py`

**Key Interactions:**
**Exposes:** `calculate_signature()` - *Calculate the full sound signature for a given Ditrune value.*


---

**File:** `src/pillars/tq/models/cipher_token.py`

**Role:** `[Bone] (Model)`

**Purpose:** Cipher Token Model - The Base-27 Alphabet.

**Input (Ingests):**
* `decimal_value` (Field)
* `trigram` (Field)
* `category` (Field)
* `symbol` (Field)
* `letter` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `dataclasses.dataclass`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `label()` - *Returns a display label for the token (Symbol or Letter).*
**Exposes:** `stratum()` - *Determines the ontological stratum based on Pyx (0) count.*


---

**File:** `src/pillars/tq/models/kamea_cell.py`

**Role:** `[Bone] (Model)`

**Purpose:** Kamea Cell Model - The 27x27 Grid Unit.

**Input (Ingests):**
* `x` (Field)
* `y` (Field)
* `ternary_value` (Field)
* `decimal_value` (Field)
* `bigrams` (Field)
* `family_id` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `dataclasses.dataclass`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `kamea_locator()` - *Returns the Kamea Locator string 'Region-Area-Cell'.*
**Exposes:** `is_axis()` - *Returns True if the cell lies on the X or Y axis.*
**Exposes:** `is_origin()` - *Functional interface.*
**Exposes:** `pyx_count()` - *Returns the Dimensional Density (count of '0's).*
**Exposes:** `conrune_vector()` - *Returns the Magnitude of the Vector between Self and Conrune.*


---

**File:** `src/pillars/tq/models/quadset_models.py`

**Role:** `[Bone] (Model)`

**Purpose:** Data models for Quadset Analysis.

**Input (Ingests):**
* `name` (Field)
* `decimal` (Field)
* `ternary` (Field)
* `properties` (Field)
* `original` (Field)
* `conrune` (Field)
* `reversal` (Field)
* `conrune_reversal` (Field)
* `upper_diff` (Field)
* `lower_diff` (Field)
* `transgram` (Field)
* `quadset_sum` (Field)
* `septad_total` (Field)
* `pattern_summary` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `dataclasses.dataclass`
* `dataclasses.field`
* `typing.Any`
* `typing.Dict`
* `typing.List`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `members()` - *Return the four main members as a list.*


---

**File:** `src/pillars/tq/models/symphony_config.py`

**Role:** `[Bone] (Model)`

**Purpose:** Symphony Configuration - The 9 Orchestral Archetypes.

**Input (Ingests):**
* `id` (Field)
* `name` (Field)
* `color_hex` (Field)
* `instrument` (Field)
* `audio_type` (Field)
* `detune_acolyte` (Field)
* `detune_temple` (Field)
* `ditrune` (Field)
* `core` (Field)
* `body` (Field)
* `skin` (Field)
* `pyx_count` (Field)
* `hierarchy_class` (Field)
* `coordinates` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `dataclasses.dataclass`
* `typing.Dict`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/tq/repositories/cipher_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Cipher Repository - The Base-27 Lookup.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `csv`
* `models.cipher_token.CipherToken`
* `os`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_all()` - *Returns all tokens sorted by decimal value.*
**Exposes:** `get_by_decimal()` - *Retrieves a token by its decimal value (0-26).*
**Exposes:** `get_by_letter()` - *Retrieves a token by its letter (Case-Insensitive).*


---

**File:** `src/pillars/tq/services/amun_audio_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Amun Audio Service - The Symphonic Synthesizer.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `os`
* `random`
* `struct`
* `tempfile`
* `wave`

**Consumers (Who Needs It):**
* `scripts/test_audio_aplay.py`
* `tests/test_amun_audio.py`

**Key Interactions:**
**Exposes:** `generate_wave_file()` - *Generate a temporary WAV file using Additive Synthesis (Symphonic Engine).*
**Exposes:** `generate_sequence()` - *Generate a single WAV file from a sequence of signatures.*


---

**File:** `src/pillars/tq/services/baphomet_color_service.py`

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

**Key Interactions:**
**Exposes:** `resolve_color()` - *Resolves the RGB color for a given 6-digit ternary string.*


---

**File:** `src/pillars/tq/services/conrune_pair_finder_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service to compute Conrune pair information.

**Input (Ingests):**
* `label` (Field)
* `ternary` (Field)
* `decimal` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `ternary_service.TernaryService`
* `typing.Dict`
* `typing.List`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `analyze()` - *Return Conrune pair information for the requested difference D.*


---

**File:** `src/pillars/tq/services/ditrunal_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Ditrunal Service - The Nuclear Mutation Engine.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `models.kamea_cell.KameaCell`
* `services.ternary_service.TernaryService`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `nuclear_mutation()` - *Performs a single step of Nuclear Mutation.*
**Exposes:** `find_prime()` - *Recursively applies Nuclear Mutation until a stable Prime or Cycle is found.*
**Exposes:** `analyze_mutation_path()` - *Returns the full path of mutation from the input to the Prime (or Cycle entry).*
**Exposes:** `get_family_id()` - *Determines the Family ID (0-8) based on the Prime.*
**Exposes:** `get_conrune_value()` - *Calculates the Conrune (Polarity Swap) of a ternary string.*
**Exposes:** `get_star_category()` - *Classifies a Ditrune based on the 'Star Correspondence' of its two Triunes.*
**Exposes:** `get_type()` - *Functional interface.*


---

**File:** `src/pillars/tq/services/geometric_transition_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Services for geometric-based vertex transitions.

**Input (Ingests):**
* `index` (Field)
* `label` (Field)
* `value` (Field)
* `x` (Field)
* `y` (Field)
* `skip` (Field)
* `from_index` (Field)
* `to_index` (Field)
* `from_value` (Field)
* `to_value` (Field)
* `from_ternary` (Field)
* `to_ternary` (Field)
* `result_ternary` (Field)
* `result_decimal` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `ternary_service.TernaryService`
* `ternary_transition_service.TernaryTransitionService`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Sequence`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_polygon_options()` - *Return supported polygon side counts for UI selectors.*
**Exposes:** `build_vertices()` - *Construct ordered vertices with coordinates.*
**Exposes:** `generate_skip_groups()` - *Return transition groups keyed by skip value.*
**Exposes:** `generate_special_sequences()` - *Return predefined transition sets for particular polygons.*


---

**File:** `src/pillars/tq/services/kamea_grid_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Kamea Grid Service - The 27x27 Matrix Oracle.

**Input (Ingests):**
* `variant`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`
* `baphomet_color_service.BaphometColorService`
* `csv`
* `logging`
* `models.kamea_cell.KameaCell`
* `os`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `cells()` - *Exposes the list of cell objects.*
**Exposes:** `initialize()` - *Loads the grid from CSVs if not already loaded.*
**Exposes:** `get_cell()` - *Returns the cell at Cartesian coordinates (x, y).*
**Exposes:** `get_cell_by_locator()` - *Finds a cell by its Kamea Locator values.*
**Exposes:** `get_cell_color()` - *Returns the color for the cell based on the Baphomet Physics (used for all variants now).*
**Exposes:** `get_quadset()` - *Returns the list of related cells for (x, y).*
**Exposes:** `get_chord_values()` - *Returns the list of decimal values forming the Geometric Chord (Quadset)*


---

**File:** `src/pillars/tq/services/kamea_symphony_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Kamea Symphony Service - The Cinematic Audio Engine.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `io`
* `models.symphony_config.OCTAVE_FREQUENCIES`
* `models.symphony_config.SCALE_RATIOS`
* `models.symphony_config.SYMPHONY_FAMILIES`
* `models.symphony_config.SymphonyNucleation`
* `numpy`
* `scipy.io.wavfile`
* `scipy.signal.fftconvolve`
* `struct`
* `tempfile`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `generate_wav_file()` - *Generates audio and returns path to a temporary WAV file.*
**Exposes:** `generate_sequence()` - *Generates a sequence of notes (linear concatenation).*
**Exposes:** `generate_chord()` - *Generates a chord (simultaneous mixing).*


---

**File:** `src/pillars/tq/services/number_properties.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service for calculating number properties.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_quadset.py`

**Key Interactions:**
**Exposes:** `is_prime()` - *Check if a number is prime.*
**Exposes:** `get_factors()` - *Get all factors of a number.*
**Exposes:** `get_prime_factorization()` - *Get prime factorization.*
**Exposes:** `is_square()` - *Check if number is a perfect square.*
**Exposes:** `is_cube()` - *Check if number is a perfect cube.*
**Exposes:** `is_fibonacci()` - *Check if number is in Fibonacci sequence.*
**Exposes:** `digit_sum()` - *Calculate sum of decimal digits.*
**Exposes:** `is_happy()` - *Check if number is a Happy number.*
**Exposes:** `get_happy_iterations()` - *Get the number of iterations to reach 1 for a Happy number.*
**Exposes:** `get_happy_chain()` - *Get the chain of numbers from n until reaching 1 or entering a cycle.*
**Exposes:** `get_prime_ordinal()` - *Get the 1-based index of a prime number.*
**Exposes:** `get_polygonal_info()` - *Check for polygonal numbers (3 to 12 sides).*
**Exposes:** `get_centered_polygonal_info()` - *Check for centered polygonal numbers (3 to 12 sides).*
**Exposes:** `is_pronic()` - *Check if n is a pronic number (n = k*(k+1) for some k).*
**Exposes:** `get_pronic_index()` - *Get the index k if n is pronic (n = k*(k+1)), else return -1.*
**Exposes:** `get_figurate_3d_info()` - *Check for 3D figurate numbers: tetrahedral, square pyramidal, octahedral, cubic.*
**Exposes:** `get_properties()` - *Get a dictionary of all properties.*


---

**File:** `src/pillars/tq/services/pattern_analyzer.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service for analyzing mathematical patterns in Quadsets.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `models.QuadsetMember`
* `services.number_properties.NumberPropertiesService`
* `typing.List`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `analyze()` - *Generate a textual summary of patterns found in the quadset members.*


---

**File:** `src/pillars/tq/services/platonic_transition_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Platonic solid based transition helpers for 3D geometric analysis.

**Input (Ingests):**
* `index` (Field)
* `label` (Field)
* `value` (Field)
* `position` (Field)
* `family_key` (Field)
* `family_label` (Field)
* `distance` (Field)
* `from_index` (Field)
* `to_index` (Field)
* `from_value` (Field)
* `to_value` (Field)
* `from_ternary` (Field)
* `to_ternary` (Field)
* `result_ternary` (Field)
* `result_decimal` (Field)
* `key` (Field)
* `label` (Field)
* `distance` (Field)
* `transitions` (Field)
* `summary` (Field)
* `segments` (Field)
* `key` (Field)
* `name` (Field)
* `vertices` (Field)
* `edges` (Field)
* `faces` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `pillars.geometry.services.archimedean_solids.CuboctahedronSolidService`
* `pillars.geometry.services.cube_solid.CubeSolidService`
* `pillars.geometry.services.dodecahedron_solid.DodecahedronSolidService`
* `pillars.geometry.services.icosahedron_solid.IcosahedronSolidService`
* `pillars.geometry.services.octahedron_solid.OctahedronSolidService`
* `pillars.geometry.services.tetrahedron_solid.TetrahedronSolidService`
* `pillars.geomet

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_solid_options()` - *Return selectable Platonic solid metadata for UI controls.*
**Exposes:** `build_geometry()` - *Resolve vertices, edges, and faces for the requested solid.*
**Exposes:** `generate_families()` - *Functional interface.*
**Exposes:** `generate_face_sequences()` - *Functional interface.*


---

**File:** `src/pillars/tq/services/quadset_engine.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Engine for Quadset calculations.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `models.QuadsetMember`
* `models.QuadsetResult`
* `services.number_properties.NumberPropertiesService`
* `services.pattern_analyzer.PatternAnalyzer`
* `services.ternary_service.TernaryService`
* `services.ternary_transition_service.TernaryTransitionService`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_quadset.py`

**Key Interactions:**
**Exposes:** `calculate()` - *Perform a full Quadset analysis on a decimal number.*


---

**File:** `src/pillars/tq/services/ternary_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service for ternary conversions.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* None.

**Consumers (Who Needs It):**
* `scripts/universal_pattern_search.py`
* `src/pillars/adyton/services/frustum_color_service.py`
* `src/pillars/adyton/services/kamea_color_service.py`
* `src/pillars/adyton/ui/frustum_popup.py`

**Key Interactions:**
**Exposes:** `decimal_to_ternary()` - *Convert a decimal integer to a ternary string.*
**Exposes:** `ternary_to_decimal()` - *Convert a ternary string to a decimal integer.*
**Exposes:** `conrune_transform()` - *Apply Conrune transformation to a ternary string.*
**Exposes:** `reverse_ternary()` - *Reverse a ternary string.*


---

**File:** `src/pillars/tq/services/ternary_transition_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service for Ternary Transition System.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `typing.Dict`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `transition()` - *Apply transition between two ternary numbers.*
**Exposes:** `generate_sequence()` - *Generate a sequence of transitions.*
**Exposes:** `get_digit_info()` - *Get philosophical info for a digit.*


---

**File:** `src/pillars/tq/ui/amun_visualizer.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Amun Visualizer - The Sacred Geometry Mandala.

**Input (Ingests):**
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
* `PyQt6.QtGui.QPainterPath`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QRadialGradient`
* `PyQt6.QtWidgets.QWidget`
* `math`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `update_parameters()` - *Update visualization target parameters from Symphony data.*
**Exposes:** `stop()` - *Functional interface.*
**Exposes:** `update_animation()` - *Functional interface.*
**Exposes:** `paintEvent()` - *Functional interface.*


---

**File:** `src/pillars/tq/ui/baphomet_panel.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Baphomet Panel - The Converse Analysis Inspector.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `models.kamea_cell.KameaCell`
* `services.baphomet_color_service.BaphometColorService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `analyze_cell()` - *Updates the panel with the selected cell's Converse data.*


---

**File:** `src/pillars/tq/ui/conrune_pair_finder_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** UI for Conrune Pair Finder.

**Input (Ingests):**
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTableWidgetItem`
* `PyQt6.QtWidgets.QTableWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `__future__.annotations`
* `

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/tq/ui/fractal_network_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Fractal Network Dialog - The Dimensional Descent Viewer.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `update_network()` - *Updates the view with the path for the given Ditrune.*


---

**File:** `src/pillars/tq/ui/geometric_transitions_3d_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** 3D geometric transitions window built on Platonic solids.

**Input (Ingests):**
* `parent`
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QMouseEvent`
* `PyQt6.QtGui.QPaintEvent`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.Q

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `rotation_changed` - *Nervous System Signal.*
**Exposes:** `set_geometry()` - *Functional interface.*
**Exposes:** `set_family_segments()` - *Functional interface.*
**Exposes:** `set_pattern_segments()` - *Functional interface.*
**Exposes:** `set_transition()` - *Functional interface.*
**Exposes:** `paintEvent()` - *Functional interface.*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Exposes:** `mouseMoveEvent()` - *Functional interface.*
**Exposes:** `mouseReleaseEvent()` - *Functional interface.*
**Exposes:** `set_rotation()` - *Functional interface.*
**Exposes:** `reset_view()` - *Functional interface.*


---

**File:** `src/pillars/tq/ui/geometric_transitions_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Geometric transitions analysis window.

**Input (Ingests):**
* `parent`
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidg

**Consumers (Who Needs It):**
* `src/pillars/adyton/ui/wall_designer.py`
* `src/pillars/astrology/ui/differential_natal_window.py`

**Key Interactions:**
**Exposes:** `set_vertices()` - *Functional interface.*
**Exposes:** `set_highlight()` - *Functional interface.*
**Exposes:** `set_special_segments()` - *Functional interface.*
**Exposes:** `paintEvent()` - *Functional interface.*


---

**File:** `src/pillars/tq/ui/kamea_fractal_view.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Kamea Fractal View - The 3D Canopy Visualizer.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QTransform`
* `PyQt6.QtWidgets.QGraphicsEllipseItem`
* `PyQt6.QtWidgets.QGraphicsLineItem`
* `PyQt6.QtWidgets.QGraphicsScene`
* `PyQt6.QtWidgets.QGraphicsView`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QToolTip`
* `PyQt6

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `cell_clicked` - *Nervous System Signal.*
**Emits:** `focus_changed` - *Nervous System Signal.*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Exposes:** `mouseMoveEvent()` - *Functional interface.*
**Exposes:** `mouseReleaseEvent()` - *Functional interface.*
**Exposes:** `contextMenuEvent()` - *Functional interface.*
**Exposes:** `set_focused_ditrune()` - *Functional interface.*
**Exposes:** `wheelEvent()` - *Functional interface.*
**Exposes:** `set_show_connections()` - *Functional interface.*
**Exposes:** `is_descendant()` - *Functional interface.*


---

**File:** `src/pillars/tq/ui/kamea_grid_view.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Kamea Grid View - The 2D Matrix Renderer.

**Input (Ingests):**
* `cell`
* `size`
* `base_color`
* `tooltip_enabled`
* `service`
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
* `PyQt6.QtGui.QFontMetrics`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QMouseEvent`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QRadialGradient`
* `PyQt6.QtGui.QTransform`
* `PyQt6.QtWidgets.QGraphicsItem`
* `PyQt6.QtWidgets.QGraphicsRectItem`
* `PyQt6.QtWidgets.QGraphicsScene`
* `PyQt6.QtWidgets.QGraphicsSimpleTextItem`
* `PyQt6.QtWidgets.QGr

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `set_highlight()` - *Sets the highlight mode for the cell.*
**Exposes:** `set_dimmed()` - *Dims the cell if filtered out.*
**Exposes:** `set_view_mode()` - *Updates the text based on view mode ('decimal' or 'ternary').*
**Exposes:** `hoverEnterEvent()` - *Functional interface.*
**Exposes:** `hoverLeaveEvent()` - *Functional interface.*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Emits:** `cell_selected` - *Nervous System Signal.*
**Exposes:** `set_dimension_filter()` - *Filters the grid by Pyx Count (Dimensional Density).*
**Exposes:** `set_view_mode()` - *Propagates view mode to all cells.*
**Exposes:** `initialize_scene()` - *Builds the visual grid.*
**Exposes:** `wheelEvent()` - *Smooth Zoom.*


---

**File:** `src/pillars/tq/ui/kamea_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Kamea Window - The Unified Field Visualizer.

**Input (Ingests):**
* `service`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QStackedLayout`
* `PyQt6.QtWidgets.QStatusBar`
* `PyQt6.QtWidgets.QToolBar`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `baphomet_panel.BaphometPanel`
* `fractal_network_dialog.FractalNetworkDialog`
* `kamea_fractal_view.KameaFractalView`
* `kamea_grid_view.KameaGridV

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/tq/ui/nuclear_mutation_panel.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Nuclear Mutation Panel - The Reactor Sidebar.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `models.kamea_cell.KameaCell`
* `repositories.cipher_repository.CipherRepository`
* `services.ditrunal_service.DitrunalService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `analyze_cell()` - *Performs Soul Analysis on the cell.*


---

**File:** `src/pillars/tq/ui/quadset_analysis_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Quadset Analysis Window - The Ternary Transformation Explorer.

**Input (Ingests):**
* `text`
* `parent`
* `context_menu_handler`
* `parent`
* `title`
* `content`
* `parent`
* `link_handler`
* `image_path`
* `parent`
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QRect`
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QPixmap`
* `PyQt6.QtGui.QTextCursor`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHe

**Consumers (Who Needs It):**
* `src/pillars/adyton/ui/wall_analytics_window.py`
* `src/pillars/adyton/ui/wall_designer.py`
* `src/pillars/astrology/ui/differential_natal_window.py`
* `src/pillars/gematria/ui/gematria_calculator_window.py`
* `src/pillars/gematria/ui/text_analysis/main_window.py`
* `src/pillars/geometry/ui/geometry3d/window3d.py`

**Key Interactions:**
**Exposes:** `get_super()` - *Functional interface.*
**Exposes:** `contextMenuEvent()` - *Functional interface.*
**Exposes:** `sizeHint()` - *Functional interface.*
**Exposes:** `minimumSizeHint()` - *Functional interface.*
**Exposes:** `set_ternary()` - *Update the glyph with a ternary string and repaint.*
**Exposes:** `paintEvent()` - *Functional interface.*
**Exposes:** `set_content()` - *Functional interface.*
**Exposes:** `paintEvent()` - *Functional interface.*
**Exposes:** `create_card()` - *Functional interface.*


---

**File:** `src/pillars/tq/ui/ternary_converter_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Ternary converter tool window.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `os`
* `services.ternary_service.TernaryService`
* `shared.ui.catalyst_styles.get_navigator_style`
* `shared.ui.theme.COLORS`
* `shared.ui.theme.ge

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/tq/ui/ternary_sound_widget.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Ternary Sound Widget - The Amun Sound System Interface.

**Input (Ingests):**
* `output_display`
* `main_window`
* `main_window`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QUrl`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtMultimedia.QAudioOutput`
* `PyQt6.QtMultimedia.QMediaPlayer`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QPlainTextEdit`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QTabWidget`
* `PyQt6.QtWidgets.QTextEdit`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `init_ui()` - *Functional interface.*
**Exposes:** `calculate()` - *Functional interface.*
**Exposes:** `play_sound()` - *Functional interface.*
**Exposes:** `init_ui()` - *Functional interface.*
**Exposes:** `parse_sequence()` - *Functional interface.*
**Exposes:** `play_sequence()` - *Functional interface.*
**Exposes:** `play_chord()` - *Play all notes simultaneously.*
**Exposes:** `map_chord()` - *Takes the first valid number in the input, finds its Quadset,*
**Exposes:** `update_visualizer()` - *Update the visualizer with new signature data.*


---

**File:** `src/pillars/tq/ui/tq_hub.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** TQ pillar hub - launcher interface for TQ tools.

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
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `conrune_pair_finder_window.ConrunePairFinderWindow`
* `geometric_transitions_3d_window.GeometricTransitions3DWindow`
* `geometric_transitions_window.GeometricTransitionsWindow`
* `kamea_window.KameaWindow`
* `quadset_analysis_wind

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/tq/ui/transitions_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Transitions tool window - aligned with Visual Liturgy.

**Input (Ingests):**
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPixmap`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTableWidgetItem`
* `PyQt6.

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.
