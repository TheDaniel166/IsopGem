# Astrology Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the Celestial Engine of IsopGem, mapping the integration with the Swiss Ephemeris via the OpenAstro2 bridge.








---

**File:** `src/pillars/astrology/models/chart_models.py`

**Role:** `[Bone] (Model)`

**Purpose:** Astrology domain models for OpenAstro2 integration.

**Input (Ingests):**
* `name` (Field)
* `latitude` (Field)
* `longitude` (Field)
* `elevation` (Field)
* `country_code` (Field)
* `name` (Field)
* `timestamp` (Field)
* `location` (Field)
* `timezone_offset` (Field)
* `metadata` (Field)
* `primary_event` (Field)
* `chart_type` (Field)
* `reference_event` (Field)
* `include_svg` (Field)
* `settings` (Field)
* `name` (Field)
* `degree` (Field)
* `sign_index` (Field)
* `number` (Field)
* `degree` (Field)
* `chart_type` (Field)
* `planet_positions` (Field)
* `house_positions` (Field)
* `aspect_summary` (Field)
* `svg_document` (Field)
* `raw_payload` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.asdict`
* `dataclasses.dataclass`
* `dataclasses.field`
* `dataclasses.is_dataclass`
* `datetime.datetime`
* `datetime.timezone`
* `typing.Any`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/astrology/services/interpretation_service.py`
* `tests/rituals/render_chart_preview.py`
* `tests/rituals/rite_of_interpretation.py`

**Key Interactions:**
**Exposes:** `resolved_timezone_offset()` - *Return the timezone offset in hours, deriving it from tzinfo when missing.*
**Exposes:** `to_openastro_kwargs()` - *Serialize the event into the kwargs OpenAstro2 expects.*
**Exposes:** `has_svg()` - *Return True when the chart includes SVG output.*
**Exposes:** `to_dict()` - *Serialize the result into primitives for persistence or transport.*


---

**File:** `src/pillars/astrology/models/chart_record.py`

**Role:** `[Bone] (Model)`

**Purpose:** SQLAlchemy models for persisting astrology charts.

**Input (Ingests):**
* `id` (Column)
* `name` (Column)
* `description` (Column)
* `chart_type` (Column)
* `include_svg` (Column)
* `house_system` (Column)
* `event_timestamp` (Column)
* `timezone_offset` (Column)
* `location_label` (Column)
* `latitude` (Column)
* `longitude` (Column)
* `elevation` (Column)
* `request_payload` (Column)
* `result_payload` (Column)
* `created_at` (Column)
* `updated_at` (Column)
* `id` (Column)
* `name` (Column)
* `id` (Column)
* `name` (Column)

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
* `sqlalchemy.Integer`
* `sqlalchemy.JSON`
* `sqlalchemy.String`
* `sqlalchemy.Table`
* `sqlalchemy.Text`
* `sqlalchemy.func`
* `sqlalchemy.orm.relationship`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/astrology/models/interpretation_models.py`

**Role:** `[Bone] (Model)`

**Purpose:** Domain models for Chart Interpretation.

**Input (Ingests):**
* `text` (Field)
* `archetype` (Field)
* `essence` (Field)
* `shadow` (Field)
* `gift` (Field)
* `alchemical_process` (Field)
* `keywords` (Field)
* `title` (Field)
* `content` (Field)
* `tags` (Field)
* `weight` (Field)
* `chart_name` (Field)
* `segments` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `dataclasses.field`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/astrology/services/interpretation_service.py`
* `src/pillars/astrology/ui/interpretation_widget.py`

**Key Interactions:**
**Exposes:** `add_segment()` - *Add a segment to the report.*
**Exposes:** `to_markdown()` - *Render the report as a Markdown string.*


---

**File:** `src/pillars/astrology/repositories/chart_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Persistence helpers for astrology chart records.

**Input (Ingests):**
* `session`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `models.chart_record.AstrologyChart`
* `models.chart_record.ChartCategory`
* `models.chart_record.ChartTag`
* `sqlalchemy.func`
* `sqlalchemy.orm.Session`
* `typing.List`
* `typing.Optional`
* `typing.Sequence`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `create_chart()` - *Functional interface.*
**Exposes:** `get_chart()` - *Functional interface.*
**Exposes:** `list_recent()` - *Functional interface.*
**Exposes:** `search()` - *Functional interface.*


---

**File:** `src/pillars/astrology/repositories/ephemeris_provider.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Ephemeris Provider - The Celestial Engine.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `datetime.datetime`
* `datetime.timedelta`
* `datetime.timezone`
* `math`
* `os`
* `skyfield.api.load`
* `skyfield.framelib.ecliptic_frame`
* `threading`

**Consumers (Who Needs It):**
* `src/pillars/astrology/ui/venus_rose_window.py`

**Key Interactions:**
**Exposes:** `get_instance()` - *Functional interface.*
**Exposes:** `is_loaded()` - *Functional interface.*
**Exposes:** `get_osculating_north_node()` - *Calculates the Geocentric Osculating North Node (True Node) of the Moon.*
**Exposes:** `get_geocentric_ecliptic_position()` - *Returns the Geocentric Ecliptic Longitude (0-360) for a given body.*
**Exposes:** `get_heliocentric_ecliptic_position()` - *Returns the Heliocentric Ecliptic Longitude (0-360) for a given body.*
**Exposes:** `get_extended_data()` - *Returns a dictionary of extended orbital data:*


---

**File:** `src/pillars/astrology/repositories/interpretation_repository.py`

**Role:** `[Memory] (Repository)`

**Purpose:** Repository for accessing chart interpretation data.

**Input (Ingests):**
* `data_dir`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `json`
* `logging`
* `models.interpretation_models.RichInterpretationContent`
* `pathlib.Path`
* `typing.Any`
* `typing.Dict`
* `typing.Optional`

**Consumers (Who Needs It):**
* `src/pillars/astrology/services/interpretation_service.py`
* `tests/rituals/rite_of_interpretation.py`

**Key Interactions:**
**Exposes:** `get_planet_sign_text()` - *Get text for a planet in a sign.*
**Exposes:** `get_planet_house_text()` - *Get text for a planet in a house.*
**Exposes:** `get_planet_sign_house_text()` - *Get text for the combinatorial triad (Planet + Sign + House).*
**Exposes:** `get_aspect_text()` - *Get text for an aspect between two planets.*


---

**File:** `src/pillars/astrology/services/arabic_parts_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Arabic Parts (Lots) calculation service.

**Input (Ingests):**
* `name` (Field)
* `longitude` (Field)
* `formula` (Field)
* `category` (Field)
* `name` (Field)
* `day_add` (Field)
* `day_sub` (Field)
* `reverse_at_night` (Field)
* `category` (Field)
* `description` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `typing.Callable`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `tests/rituals/verify_arabic_parts.py`

**Key Interactions:**
**Exposes:** `calculate_parts()` - *Calculate all Arabic Parts for a chart.*
**Exposes:** `is_day_chart()` - *Determine if chart is diurnal (day) or nocturnal (night).*


---

**File:** `src/pillars/astrology/services/aspects_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Comprehensive aspects calculation service.

**Input (Ingests):**
* `name` (Field)
* `angle` (Field)
* `default_orb` (Field)
* `symbol` (Field)
* `is_major` (Field)
* `planet_a` (Field)
* `planet_b` (Field)
* `aspect` (Field)
* `orb` (Field)
* `is_applying` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `itertools.combinations`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `src/pillars/astrology/services/interpretation_service.py`
* `tests/rituals/verify_aspects.py`

**Key Interactions:**
**Exposes:** `calculate_aspects()` - *Calculate all aspects between planets.*
**Exposes:** `get_aspect_definitions()` - *Get list of aspect definitions.*


---

**File:** `src/pillars/astrology/services/chart_storage_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service layer for persisting and retrieving natal chart definitions.

**Input (Ingests):**
* `chart_id` (Field)
* `name` (Field)
* `event_timestamp` (Field)
* `location_label` (Field)
* `categories` (Field)
* `tags` (Field)
* `chart_type` (Field)
* `chart_id` (Field)
* `request` (Field)
* `categories` (Field)
* `tags` (Field)
* `description` (Field)
* `session_factory`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `contextlib.AbstractContextManager`
* `dataclasses.dataclass`
* `datetime.datetime`
* `models.AstrologyEvent`
* `models.ChartRequest`
* `models.ChartResult`
* `models.GeoLocation`
* `models.chart_record.AstrologyChart`
* `repositories.chart_repository.ChartRepository`
* `shared.database.get_db_session`
* `typing.Callable`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Sequence`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `save_chart()` - *Functional interface.*
**Exposes:** `list_recent()` - *Functional interface.*
**Exposes:** `search()` - *Functional interface.*
**Exposes:** `load_chart()` - *Functional interface.*


---

**File:** `src/pillars/astrology/services/fixed_stars_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Fixed Stars calculation service using Swiss Ephemeris.

**Input (Ingests):**
* `name` (Field)
* `constellation` (Field)
* `longitude` (Field)
* `latitude` (Field)
* `distance` (Field)
* `magnitude` (Field)
* `nature` (Field)
* `ephemeris_path`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `openastro2`
* `os`
* `pathlib.Path`
* `swisseph`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `tests/rituals/verify_fixed_stars.py`

**Key Interactions:**
**Exposes:** `get_star_positions()` - *Calculate positions for notable fixed stars at a given Julian Day.*
**Exposes:** `find_conjunctions()` - *Find fixed stars conjunct to planets within given orb.*


---

**File:** `src/pillars/astrology/services/harmonics_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Harmonic chart calculation service.

**Input (Ingests):**
* `planet` (Field)
* `natal_longitude` (Field)
* `harmonic_longitude` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `typing.Dict`
* `typing.List`

**Consumers (Who Needs It):**
* `tests/rituals/verify_harmonics.py`

**Key Interactions:**
**Exposes:** `calculate_harmonic()` - *Calculate harmonic chart positions.*
**Exposes:** `get_preset_info()` - *Get name and description for a harmonic preset.*


---

**File:** `src/pillars/astrology/services/interpretation_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service for generating chart interpretations.

**Input (Ingests):**
* `repository`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `logging`
* `pillars.astrology.models.chart_models.ChartResult`
* `pillars.astrology.models.chart_models.HousePosition`
* `pillars.astrology.models.chart_models.PlanetPosition`
* `pillars.astrology.models.interpretation_models.InterpretationReport`
* `pillars.astrology.repositories.interpretation_repository.InterpretationRepository`
* `pillars.astrology.services.aspects_service.CalculatedAspect`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_interpretation.py`

**Key Interactions:**
**Exposes:** `interpret_chart()` - *Generate a full interpretation report for the given chart.*


---

**File:** `src/pillars/astrology/services/location_lookup.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Location lookup helpers for the astrology pillar.

**Input (Ingests):**
* `name` (Field)
* `latitude` (Field)
* `longitude` (Field)
* `country` (Field)
* `admin1` (Field)
* `elevation` (Field)
* `timezone_id` (Field)
* `session`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `requests`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `label()` - *Functional interface.*
**Exposes:** `search()` - *Functional interface.*


---

**File:** `src/pillars/astrology/services/maat_symbols_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Maat Symbols service - Egyptian degree symbols for astrology.

**Input (Ingests):**
* `degree` (Field)
* `sign` (Field)
* `sign_degree` (Field)
* `heaven` (Field)
* `heaven_name` (Field)
* `text` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `re`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_symbol()` - *Get the Maat symbol for a given ecliptic longitude.*
**Exposes:** `get_symbols_for_positions()` - *Get Maat symbols for a dict of planet positions.*


---

**File:** `src/pillars/astrology/services/midpoints_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Midpoints calculation service.

**Input (Ingests):**
* `planet_a` (Field)
* `planet_b` (Field)
* `longitude` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `itertools.combinations`
* `typing.Dict`
* `typing.List`
* `typing.Set`

**Consumers (Who Needs It):**
* `tests/rituals/verify_midpoints.py`

**Key Interactions:**
**Exposes:** `calculate_midpoints()` - *Calculate midpoints between all planet pairs.*


---

**File:** `src/pillars/astrology/services/openastro_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Wrapper service that integrates OpenAstro2 with IsopGem.

**Input (Ingests):**
* `default_settings`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `copy`
* `logging`
* `models.AstrologyEvent`
* `models.ChartRequest`
* `models.ChartResult`
* `models.GeoLocation`
* `models.HousePosition`
* `models.PlanetPosition`
* `openastro2.openastro2.openAstro`
* `typing.Any`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `generate_chart()` - *Generate a chart with OpenAstro2 based on the supplied request.*
**Exposes:** `list_house_systems()` - *Return a dictionary of supported house systems and their labels.*
**Exposes:** `default_settings()` - *Expose a safe copy of the default OpenAstro settings template.*


---

**File:** `src/pillars/astrology/ui/astrology_hub.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Astrology pillar hub - launcher interface for astrology tools.

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
* `current_transit_window.CurrentTransitWindow`
* `differential_natal_window.DifferentialNatalWindow`
* `natal_chart_window.NatalChartWindow`
* `neo_aubrey_window.NeoAubreyWindow`
* `planetary_positions_window.PlanetaryPositionsWindo

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/astrology/ui/chart_canvas.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Custom in-app chart renderer (no browser dependency).

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QRectF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QLinearGradient`
* `PyQt6.QtGui.QMouseEvent`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QRadialGradient`
* `PyQt6.QtWidgets.QWidget`
* `math`
* `models.chart_models.HousePosition`
* `models.chart_models.PlanetPosition`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `tests/rituals/render_chart_preview.py`

**Key Interactions:**
**Exposes:** `set_data()` - *Functional interface.*
**Exposes:** `set_aspect_options()` - *Set aspect display options.*
**Exposes:** `mouseMoveEvent()` - *Functional interface.*
**Exposes:** `paintEvent()` - *Functional interface.*
**Exposes:** `angle_for()` - *Functional interface.*


---

**File:** `src/pillars/astrology/ui/chart_picker_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Chart Picker Dialog - The Saved Chart Selector.

**Input (Ingests):**
* `storage`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTableWidgetItem`
* `PyQt6.QtWidgets.QTableWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `services.ChartStorageService`
* `services.SavedChartSummary`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/astrology/ui/conversions.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Conversions (UI) - Zodiacal String Formatter.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `to_zodiacal_string()` - *Convert absolute degree (0-360) to zodiacal degree notation (Deg Sign Min).*


---

**File:** `src/pillars/astrology/ui/current_transit_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Current transit viewer window.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QCloseEvent`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QDoubleSpinBox`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPlainTextEdit`
* `PyQt6.QtWidget

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `closeEvent()` - *Functional interface.*


---

**File:** `src/pillars/astrology/ui/differential_natal_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Differential Natal Chart Window - Maps planetary positions to Conrune pairs.

**Input (Ingests):**
* `parent`
* `window_manager`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QDate`
* `PyQt6.QtCore.QTime`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QDateEdit`
* `PyQt6.QtWidgets.QDoubleSpinBox`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QM

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/astrology/ui/harmonics_dial.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Harmonics Dial widget - circular visualization of harmonic positions.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QRectF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QRadialGradient`
* `PyQt6.QtWidgets.QToolTip`
* `PyQt6.QtWidgets.QWidget`
* `__future__.annotations`
* `math`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `set_data()` - *Set harmonic positions. positions = [(name, harmonic_degree), ...]*
**Exposes:** `mouseMoveEvent()` - *Handle mouse move for tooltips.*
**Exposes:** `paintEvent()` - *Functional interface.*


---

**File:** `src/pillars/astrology/ui/interpretation_widget.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Interpretation Result Widget.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QTextEdit`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `__future__.annotations`
* `pillars.astrology.models.interpretation_models.InterpretationReport`
* `shared.ui.theme.COLORS`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `display_report()` - *Render the report into the text view.*


---

**File:** `src/pillars/astrology/ui/midpoints_dial.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Midpoints Dial widget - circular visualization of midpoint positions.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QRectF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QRadialGradient`
* `PyQt6.QtWidgets.QToolTip`
* `PyQt6.QtWidgets.QWidget`
* `__future__.annotations`
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `set_data()` - *Set midpoint data and planet positions for planet-on-midpoint detection.*
**Exposes:** `mouseMoveEvent()` - *Functional interface.*
**Exposes:** `paintEvent()` - *Functional interface.*


---

**File:** `src/pillars/astrology/ui/natal_chart_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Interactive UI for generating natal charts through OpenAstro2.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QDateTime`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QCloseEvent`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDateTimeEdit`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QDoubleSpinBox`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QInputDialog`

**Consumers (Who Needs It):**
* `src/pillars/astrology/ui/venus_rose_window.py`

**Key Interactions:**
**Exposes:** `closeEvent()` - *Functional interface.*


---

**File:** `src/pillars/astrology/ui/neo_aubrey_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Neo-Aubrey Window - The Eclipse Clock Simulator.

**Input (Ingests):**
* `x`
* `y`
* `r`
* `index`
* `label`
* `color`
* `label`
* `scene`
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
* `PyQt6.QtGui.QPainterPath`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QPolygonF`
* `PyQt6.QtGui.QWheelEvent`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QGraphicsEllipseItem`
* `PyQt6.QtWidgets.QGraphicsItem`
* `PyQt6.QtWidgets.QGraphicsLineItem`
* `PyQt6.QtWidgets.QGraphicsScen

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `set_markers()` - *Update marker positions based on Zodiac Longitude (0-360).*
**Exposes:** `wheelEvent()` - *Functional interface.*
**Exposes:** `get_stone_idx()` - *Functional interface.*


---

**File:** `src/pillars/astrology/ui/planetary_positions_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Ephemeris-style planetary positions viewer.

**Input (Ingests):**
* `timestamp` (Field)
* `body` (Field)
* `degree` (Field)
* `sign_label` (Field)
* `retrograde` (Field)
* `speed` (Field)
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QDateTimeEdit`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QDoubleSpinBox`
* `PyQt6.QtWidgets.QFileDialog`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.

**Consumers (Who Needs It):**
* `scripts/verify_planetary_send.py`

**Key Interactions:**
**Exposes:** `populate()` - *Functional interface.*


---

**File:** `src/pillars/astrology/ui/venus_rose_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Cytherean Rose Clock

**Input (Ingests):**
* `color`
* `size`
* `label`
* `x`
* `y`
* `is_inferior`
* `scene`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QDateTime`
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QRectF`
* `PyQt6.QtCore.QTimeZone`
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QRadialGradient`
* `PyQt6.QtGui.QWheelEvent`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QGraphicsEllipseItem`
* `PyQt6.QtWidgets.QGraphicsItem`
* `PyQt6.QtWidgets.QGraphicsLineItem`
* `PyQt6.QtWidgets.QGraphicsScene`
* `PyQt6.QtWidgets.Q

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `update_positions_by_date()` - *Updates planet positions based on actual datetime using J2000 epoch.*
**Exposes:** `add_highlight()` - *Functional interface.*
**Exposes:** `clear_trace()` - *Functional interface.*
**Exposes:** `wheelEvent()` - *Functional interface.*
**Exposes:** `get_diff()` - *Functional interface.*


---

**File:** `src/pillars/astrology/utils/conversions.py`

**Role:** `[Tool] (Utility)`

**Purpose:** Conversions (Utilities) - Zodiacal String Formatter.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `typing.Tuple`

**Consumers (Who Needs It):**
* `experiments/compare_venus_cycles.py`
* `src/pillars/astrology/ui/venus_rose_window.py`

**Key Interactions:**
**Exposes:** `to_zodiacal_string()` - *Convert absolute degree (0-360) to zodiacal degree notation (Deg Sign Min).*


---

**File:** `src/pillars/astrology/utils/preferences.py`

**Role:** `[Tool] (Utility)`

**Purpose:** Preferences storage for the astrology pillar.

**Input (Ingests):**
* `name` (Field)
* `latitude` (Field)
* `longitude` (Field)
* `elevation` (Field)
* `timezone_offset` (Field)
* `timezone_id` (Field)
* `path`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.asdict`
* `dataclasses.dataclass`
* `json`
* `pathlib.Path`
* `typing.Any`
* `typing.Dict`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `load_default_location()` - *Functional interface.*
**Exposes:** `save_default_location()` - *Functional interface.*
