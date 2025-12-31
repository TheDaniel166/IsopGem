# Astrology Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the Celestial Engine of IsopGem, mapping the integration with the Swiss Ephemeris via the OpenAstro2 bridge.










---

**File:** `src/pillars/astrology/models/chariot_models.py`

**Role:** `[Bone] (Model)`

**Purpose:** Chariot system models - The Merkabah of the Soul.

**Input (Ingests):**
* `id` (Field)
* `name` (Field)
* `planet_a` (Field)
* `planet_b` (Field)
* `longitude` (Field)
* `sign` (Field)
* `sign_degree` (Field)
* `trio_id` (Field)
* `keywords` (Field)
* `description` (Field)
* `id` (Field)
* `name` (Field)
* `longitude` (Field)
* `sign` (Field)
* `sign_degree` (Field)
* `midpoints` (Field)
* `description` (Field)
* `longitude` (Field)
* `sign` (Field)
* `sign_degree` (Field)
* `axles` (Field)
* `degree` (Field)
* `name` (Field)
* `initiation` (Field)
* `affected_point` (Field)
* `orb` (Field)
* `midpoints` (Field)
* `axles` (Field)
* `chariot_point` (Field)
* `midpoint_symbols` (Field)
* `axle_symbols` (Field)
* `chariot_symbol` (Field)
* `fateful_positions` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `dataclasses.field`
* `services.maat_symbols_service.MaatSymbol`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.TYPE_CHECKING`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


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
* `speed` (Field)
* `declination` (Field)
* `number` (Field)
* `degree` (Field)
* `chart_type` (Field)
* `planet_positions` (Field)
* `house_positions` (Field)
* `aspect_summary` (Field)
* `svg_document` (Field)
* `raw_payload` (Field)
* `julian_day` (Field)

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
* `scripts/horizon_seals/seal_jupiter.py`
* `scripts/horizon_seals/seal_mars.py`
* `scripts/horizon_seals/seal_sun.py`
* `scripts/verify_fixed_stars_panel.py`
* `scripts/verify_horizon_phase1.py`
* `scripts/verify_horizon_phase2.py`
* `scripts/verify_horizon_phase4.py`
* `src/pillars/astrology/services/interpretation_service.py`
* `tests/pillars/astrology/test_ephemeris_golden_values.py`
* `tests/pillars/astrology/test_interpretation_depth.py`
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
* `scripts/verify_horizon_phase3.py`
* `src/pillars/astrology/services/interpretation_service.py`
* `src/pillars/astrology/ui/interpretation_widget.py`
* `tests/pillars/astrology/test_interpretation_depth.py`

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
**Exposes:** `create_chart()` - *Create chart logic.*
**Exposes:** `get_chart()` - *Retrieve chart logic.*
**Exposes:** `list_recent()` - *List recent logic.*
**Exposes:** `search()` - *Search logic.*


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
* `models.chart_models.GeoLocation`
* `os`
* `skyfield.api.load`
* `skyfield.api.wgs84`
* `skyfield.framelib.ecliptic_frame`
* `threading`
* `typing.Any`
* `typing.Dict`
* `typing.Optional`
* `typing.Tuple`
* `typing.Union`

**Consumers (Who Needs It):**
* `scripts/verify_horizon_phase1.py`
* `src/pillars/astrology/ui/venus_rose_window.py`
* `tests/pillars/astrology/test_ephemeris_golden_values.py`

**Key Interactions:**
**Exposes:** `get_instance()` - *Retrieve instance logic.*
**Exposes:** `is_loaded()` - *Determine if loaded logic.*
**Exposes:** `get_osculating_north_node()` - *Calculates the Geocentric Osculating North Node (True Node) of the Moon.*
**Exposes:** `get_mean_north_node()` - *Calculates the Geocentric Mean North Node.*
**Exposes:** `get_geocentric_ecliptic_position()` - *Returns the Ecliptic Longitude (0-360) for a given body.*
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
* `scripts/verify_horizon_phase3.py`
* `src/pillars/astrology/services/interpretation_service.py`
* `tests/rituals/rite_of_interpretation.py`

**Key Interactions:**
**Exposes:** `get_planet_sign_text()` - *Get text for a planet in a sign.*
**Exposes:** `get_planet_house_text()` - *Get text for a planet in a house.*
**Exposes:** `get_planet_sign_house_text()` - *Get text for the combinatorial triad (Planet + Sign + House).*
**Exposes:** `get_aspect_text()` - *Get text for an aspect between two planets.*
**Exposes:** `get_transit_text()` - *Get text for a transiting planet aspecting a natal planet.*
**Exposes:** `get_synastry_text()` - *Get text for synastry aspect (Inter-aspects).*
**Exposes:** `get_elementalist_text()` - *Get text for elemental or modality analysis.*


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
* `scripts/verify_horizon_phase2.py`
* `src/pillars/astrology/services/interpretation_service.py`
* `tests/pillars/astrology/test_interpretation_depth.py`
* `tests/rituals/verify_aspects.py`

**Key Interactions:**
**Exposes:** `calculate_aspects()` - *Calculate all aspects between planets.*
**Exposes:** `calculate_aspects_between()` - *Calculate aspects between two specific bodies.*
**Exposes:** `get_aspect_definitions()` - *Get list of aspect definitions.*


---

**File:** `src/pillars/astrology/services/chariot_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Chariot Service - The Merkabah Engine.

**Input (Ingests):**
* `positions`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `json`
* `maat_symbols_service.MaatSymbol`
* `maat_symbols_service.MaatSymbolsService`
* `math`
* `midpoints_service.MidpointsService`
* `models.chariot_models.AxlePosition`
* `models.chariot_models.ChariotMidpoint`
* `models.chariot_models.ChariotPosition`
* `models.chariot_models.ChariotReport`
* `models.chariot_models.FatefulDegreePosition`
* `models.chart_models.ChartResult`
* `models.chart_models.PlanetPosition`
* `pathlib.Path`
* `typing.Dict`
* `typing.List`
*

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_chariot_midpoints()` - *Calculate the 21 Chariot midpoints from planetary positions.*
**Exposes:** `calculate_axles()` - *Calculate the 7 Axles from the Chariot midpoints.*
**Exposes:** `calculate_chariot_point()` - *Calculate the Chariot Point - the mean of all 7 Axles.*
**Exposes:** `detect_fateful_positions()` - *Detect any positions on the three Fateful Degrees.*
**Exposes:** `generate_chariot_report()` - *Generate a complete Chariot analysis from a natal chart.*
**Exposes:** `generate_from_positions()` - *Generate a Chariot report directly from planet positions.*


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
* `json`
* `models.AstrologyEvent`
* `models.ChartRequest`
* `models.ChartResult`
* `models.GeoLocation`
* `models.HousePosition`
* `models.PlanetPosition`
* `models.chart_record.AstrologyChart`
* `repositories.chart_repository.ChartRepository`
* `shared.database.get_db_session`
* `typing.Any`
* `typing.Callable`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Sequence`

**Consumers (Who Needs It):**
* `scripts/verify_horizon_phase3.py`

**Key Interactions:**
**Exposes:** `save_chart()` - *Save chart logic.*
**Exposes:** `list_recent()` - *List recent logic.*
**Exposes:** `search()` - *Search logic.*
**Exposes:** `load_chart()` - *Load chart logic.*
**Exposes:** `export_chart_to_json()` - *Export a chart record to a JSON string.*
**Exposes:** `import_chart_from_json()` - *Import a chart from a JSON string. Returns new ID.*


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
* `scripts/verify_fixed_stars_panel.py`
* `tests/rituals/verify_fixed_stars.py`

**Key Interactions:**
**Exposes:** `get_star_positions()` - *Calculate positions for notable fixed stars at a given Julian Day.*
**Exposes:** `find_aspects()` - *Find fixed stars aspects to planets within given orb.*


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
* `pillars.astrology.services.aspects_service.AspectsService`
* `pillars.astrology.services.aspects_service.CalculatedAspect`
* `typing.

**Consumers (Who Needs It):**
* `tests/pillars/astrology/test_interpretation_depth.py`
* `tests/rituals/rite_of_interpretation.py`

**Key Interactions:**
**Exposes:** `interpret_chart()` - *Generate a full interpretation report for the given chart.*
**Exposes:** `interpret_transits()` - *Interpret Transits vs Natal.*
**Exposes:** `interpret_synastry()` - *Interpret Synastry (Relationship).*


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
**Exposes:** `label()` - *Label logic.*
**Exposes:** `search()` - *Search logic.*
**Exposes:** `reverse_geocode()` - *Reverse geocode coordinates to a location name.*


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
* `datetime.timezone`
* `logging`
* `models.AstrologyEvent`
* `models.ChartRequest`
* `models.ChartResult`
* `models.GeoLocation`
* `models.HousePosition`
* `models.PlanetPosition`
* `openastro2.openastro2.openAstro`
* `swisseph`
* `typing.Any`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `scripts/horizon_seals/seal_jupiter.py`
* `scripts/horizon_seals/seal_mars.py`
* `scripts/horizon_seals/seal_sun.py`
* `scripts/verify_horizon_phase2.py`
* `scripts/verify_horizon_phase4.py`

**Key Interactions:**
**Exposes:** `generate_chart()` - *Generate a chart with OpenAstro2 based on the supplied request.*
**Exposes:** `list_house_systems()` - *Return a dictionary of supported house systems and their labels.*
**Exposes:** `default_settings()` - *Expose a safe copy of the default OpenAstro settings template.*
**Exposes:** `configure_defaults()` - *Update the base default settings for the service instance.*


---

**File:** `src/pillars/astrology/services/progressions_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Services for calculating Progressions and Directions.

**Input (Ingests):**
* `openastro_service`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `copy`
* `datetime.datetime`
* `datetime.timedelta`
* `datetime.timezone`
* `models.chart_models.AstrologyEvent`
* `models.chart_models.ChartRequest`
* `models.chart_models.ChartResult`
* `models.chart_models.PlanetPosition`
* `openastro_service.OpenAstroService`
* `repositories.ephemeris_provider.EphemerisProvider`
* `typing.Any`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `scripts/verify_horizon_phase2.py`

**Key Interactions:**
**Exposes:** `calculate_secondary_progression()` - *Calculates Secondary Progressions (1 Day = 1 Year).*
**Exposes:** `calculate_solar_arc()` - *Calculates Solar Arc Directions.*


---

**File:** `src/pillars/astrology/services/report_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service for rendering Interpretation Reports to HTML and PDF.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QSizeF`
* `PyQt6.QtGui.QPageLayout`
* `PyQt6.QtGui.QPageSize`
* `PyQt6.QtGui.QTextDocument`
* `PyQt6.QtPrintSupport.QPrinter`
* `__future__.annotations`
* `logging`
* `models.interpretation_models.InterpretationReport`
* `pathlib.Path`
* `typing.Optional`

**Consumers (Who Needs It):**
* `scripts/verify_horizon_phase3.py`

**Key Interactions:**
**Exposes:** `render_html()` - *Convert report to a full HTML string.*
**Exposes:** `export_pdf()` - *Render report to PDF at output_path.*


---

**File:** `src/pillars/astrology/services/returns_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Services for calculating Planetary Returns (Solar/Lunar Return Charts).

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `datetime.datetime`
* `datetime.timedelta`
* `datetime.timezone`
* `math`
* `models.chart_models.AstrologyEvent`
* `models.chart_models.ChartRequest`
* `models.chart_models.GeoLocation`
* `repositories.ephemeris_provider.EphemerisProvider`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `scripts/verify_horizon_phase2.py`

**Key Interactions:**
**Exposes:** `calculate_return()` - *Calculate the exact return time for a body.*


---

**File:** `src/pillars/astrology/services/synastry_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Synastry Service — The Muscle of Relationship Astrology.

**Input (Ingests):**
* `midpoint_time` (Field)
* `midpoint_latitude` (Field)
* `midpoint_longitude` (Field)
* `planets` (Field)
* `houses` (Field)
* `julian_day` (Field)
* `chart` (Field)
* `info` (Field)
* `openastro_service`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `datetime.datetime`
* `datetime.timezone`
* `models.chart_models.AstrologyEvent`
* `models.chart_models.ChartRequest`
* `models.chart_models.ChartResult`
* `models.chart_models.GeoLocation`
* `models.chart_models.HousePosition`
* `models.chart_models.PlanetPosition`
* `openastro_service.OpenAstroService`
* `typing.Any`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `scripts/verify_horizon_phase2.py`

**Key Interactions:**
**Exposes:** `calculate_midpoint()` - *Calculate the midpoint between two degrees on a circle.*
**Exposes:** `generate_chart()` - *Generate a single radix chart.*
**Exposes:** `calculate_composite()` - *Calculate a Composite chart from two existing chart results.*
**Exposes:** `calculate_davison()` - *Calculate a Davison Relationship Chart.*


---

**File:** `src/pillars/astrology/ui/advanced_analysis_panel.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Advanced Analysis Panel — Reusable component for comprehensive chart analysis.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFontDatabase`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSlider`
* `PyQt6.QtWidgets.QSpinBox`
* `PyQt6.QtWidgets.QStackedWid

**Consumers (Who Needs It):**
* `scripts/verify_fixed_stars_panel.py`

**Key Interactions:**
**Exposes:** `set_data()` - *Set chart data and refresh all tabs.*
**Exposes:** `set_chart_result()` - *Set data from a ChartResult object.*


---

**File:** `src/pillars/astrology/ui/astro_settings_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Astrology Settings Dialog - Configuration for chart calculation options.

**Input (Ingests):**
* `current_settings`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QVBoxLayout`
* `shared.ui.theme.COLORS`
* `typing.Any`
* `typing.Dict`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `settings_changed` - *Nervous System Signal.*
**Exposes:** `get_settings()` - *Return the currently selected settings.*


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
* `chariot_window.ChariotWindow`
* `current_transit_window.CurrentTransitWindow`
* `differential_natal_window.DifferentialNatalWindow`
* `natal_chart_window.NatalChartWindow`
* `neo_aubrey_window.NeoAubreyWindow`
* `planetary_positio

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/astrology/ui/chariot_canvas.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Canvas for visualizing Chariot Axles and Geometry.

**Input (Ingests):**
* `parent`
* `report`

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
* `PyQt6.QtGui.QPolygonF`
* `PyQt6.QtWidgets.QWidget`
* `chart_canvas.ChartCanvas`
* `math`
* `models.chariot_models.AxlePosition`
* `models.chariot_models.ChariotReport`
* `shared.services.astro_glyph_service.astro_glyphs`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `set_chariot_data()` - *Set the chariot report data.*
**Exposes:** `set_highlighted_axle()` - *Set which Axle to highlight (brighten).*
**Exposes:** `set_highlighted_point()` - *Set which specific point (Tarot Card) to highlight.*
**Exposes:** `paintEvent()` - *Draw the Chariot geometry.*
**Exposes:** `angle_for()` - *Functional interface.*


---

**File:** `src/pillars/astrology/ui/chariot_differentials_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Chariot Differentials Window - Maps 21 midpoints to Conrune pairs.

**Input (Ingests):**
* `image_path`
* `parent`
* `parent`
* `window_manager`
* `report`
* `chart_name`

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
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QTabWidget`
* `PyQt6.QtWidgets.QTableWidgetItem`
* `PyQt6.QtWidgets.QTableWidget`
* `PyQt6.QtWidgets.

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `paintEvent()` - *Functional interface.*


---

**File:** `src/pillars/astrology/ui/chariot_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Chariot Window - The Merkabah Analysis UI.

**Input (Ingests):**
* `parent`
* `window_manager`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPalette`
* `PyQt6.QtGui.QPixmap`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QTextBro

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `load_from_positions()` - *Load chart data from planet positions.*
**Exposes:** `load_from_chart()` - *Load chart data from a ChartResult.*


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
* `PyQt6.QtGui.QFontDatabase`
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
**Exposes:** `set_data()` - *Configure data logic.*
**Exposes:** `set_synastry_data()` - *Set data for a bi-wheel synastry chart.*
**Exposes:** `set_aspect_options()` - *Set aspect display options.*
**Exposes:** `mouseMoveEvent()` - *Mousemoveevent logic.*
**Exposes:** `paintEvent()` - *Paintevent logic.*
**Exposes:** `angle_for()` - *Angle for logic.*


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

**File:** `src/pillars/astrology/ui/composite_chart_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Composite Chart Window — Non-modal window displaying midpoint-based composite chart.

**Input (Ingests):**
* `planets`
* `houses`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `chart_canvas.ChartCanvas`
* `models.chart_models.HousePosition`
* `models.chart_models.PlanetPosition`
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
**Exposes:** `closeEvent()` - *Closeevent logic.*


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
**Exposes:** `paintEvent()` - *Paintevent logic.*


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

**File:** `src/pillars/astrology/ui/location_search_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Location Search Dialog - The Cartographer's Sanctum.

**Input (Ingests):**
* `preferences`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QDoubleSpinBox`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTabWidg

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `location_selected` - *Nervous System Signal.*


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
**Exposes:** `mouseMoveEvent()` - *Mousemoveevent logic.*
**Exposes:** `paintEvent()` - *Paintevent logic.*


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
* `PyQt6.QtCore.QThreadPool`
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
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGrou

**Consumers (Who Needs It):**
* `src/pillars/astrology/ui/venus_rose_window.py`

**Key Interactions:**
**Exposes:** `closeEvent()` - *Closeevent logic.*


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
**Exposes:** `wheelEvent()` - *Wheelevent logic.*
**Exposes:** `get_stone_idx()` - *Retrieve stone idx logic.*


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
**Exposes:** `populate()` - *Populate logic.*


---

**File:** `src/pillars/astrology/ui/progressions_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Sovereign Window for Progressions and Directions.

**Input (Ingests):**
* `service`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QThreadPool`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDateTimeEdit`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `chart_canvas.ChartCanvas`
* `datetime.datetime`
* `models.chart_models.Astrolog

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/astrology/ui/returns_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Sovereign Window for Planetary Returns (Solar/Lunar).

**Input (Ingests):**
* `service`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QThreadPool`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDateTimeEdit`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSpinBox`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `chart_canvas.ChartCanvas`
* `datetime.datetime`
* 

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/astrology/ui/synastry_aspects_widget.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Synastry Aspects Widget — Cross-chart aspect analysis.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTableWidgetItem`
* `PyQt6.QtWidgets.QTableWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `models.chart_models.PlanetPosition`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `set_data()` - *Set the two planet lists and calculate aspects.*


---

**File:** `src/pillars/astrology/ui/synastry_davison_widget.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Synastry Davison Widget — Davison Relationship Chart information.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QFormLayout`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `datetime.datetime`
* `typing.Any`
* `typing.Dict`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `set_data()` - *Update the displayed Davison midpoint information.*


---

**File:** `src/pillars/astrology/ui/synastry_midpoints_widget.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Synastry Midpoints Widget — Planet and House midpoint analysis.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QHeaderView`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTableWidgetItem`
* `PyQt6.QtWidgets.QTableWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `models.chart_models.HousePosition`
* `models.chart_models.PlanetPosition`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `calculate_midpoint()` - *Calculate the midpoint between two degrees on a circle.*
**Exposes:** `degree_to_zodiac()` - *Convert degree to zodiacal notation.*
**Exposes:** `set_data()` - *Set the chart data and calculate midpoints.*
**Exposes:** `get_midpoint_data()` - *Return calculated midpoint positions.*


---

**File:** `src/pillars/astrology/ui/synastry_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Sovereign Window for Synastry Analysis.

**Input (Ingests):**
* `service`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QThreadPool`
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QIcon`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDateTimeEdit`
* `PyQt6.QtWidgets.QGroupBox`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMessageBox`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QStackedWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
*

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


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
**Exposes:** `add_highlight()` - *Add highlight logic.*
**Exposes:** `clear_trace()` - *Clear trace logic.*
**Exposes:** `wheelEvent()` - *Wheelevent logic.*
**Exposes:** `get_diff()` - *Retrieve diff logic.*


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
**Exposes:** `load_default_location()` - *Load default location logic.*
**Exposes:** `save_default_location()` - *Save default location logic.*
**Exposes:** `load_favorites()` - *Load favorite locations from preferences.*
**Exposes:** `add_favorite()` - *Add a location to favorites.*
**Exposes:** `remove_favorite()` - *Remove a location from favorites.*
