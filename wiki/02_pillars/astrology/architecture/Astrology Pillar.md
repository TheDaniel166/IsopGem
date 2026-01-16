# Astrology Pillar

<cite>
**Referenced Files in This Document**   
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [current_transit_window.py](file://src/pillars/astrology/ui/current_transit_window.py)
- [planetary_positions_window.py](file://src/pillars/astrology/ui/planetary_positions_window.py)
- [venus_rose_window.py](file://src/pillars/astrology/ui/venus_rose_window.py)
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)
- [location_lookup.py](file://src/pillars/astrology/services/location_lookup.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py)
- [conversions.py](file://src/pillars/astrology/utils/conversions.py)
- [ephemeris_provider.py](file://src/pillars/astrology/repositories/ephemeris_provider.py)
- [progressions_service.py](file://src/pillars/astrology/services/progressions_service.py)
- [returns_service.py](file://src/pillars/astrology/services/returns_service.py)
- [synastry_service.py](file://src/pillars/astrology/services/synastry_service.py)
- [chariot_service.py](file://src/pillars/astrology/services/chariot_service.py)
- [progressions_window.py](file://src/pillars/astrology/ui/progressions_window.py)
- [returns_window.py](file://src/pillars/astrology/ui/returns_window.py)
- [synastry_window.py](file://src/pillars/astrology/ui/synastry_window.py)
- [chariot_window.py](file://src/pillars/astrology/ui/chariot_window.py)
- [dignities_service.py](file://src/pillars/astrology/services/dignities_service.py)
- [venus_position_store.py](file://src/pillars/astrology/services/venus_position_store.py)
- [interpretation_service.py](file://src/pillars/astrology/services/interpretation_service.py)
- [interpretation_widget.py](file://src/pillars/astrology/ui/interpretation_widget.py)
- [interpretation_models.py](file://src/pillars/astrology/models/interpretation_models.py)
- [advanced_analysis_panel.py](file://src/pillars/astrology/ui/advanced_analysis_panel.py)
</cite>

## Update Summary
**Changes Made**   
- Added new dignities service for calculating essential and accidental dignities
- Enhanced Venus position overlay system with comprehensive heliocentric caching
- Improved interpretation panels with rich content models and enhanced widgets
- Updated chart storage service with enhanced persistence capabilities
- Added advanced analysis panel with integrated dignities display
- Enhanced Venus Rose visualization with real physics mode and event prediction

## Table of Contents
1. [Introduction](#introduction)
2. [Core Components](#core-components)
3. [Architecture Overview](#architecture-overview)
4. [Detailed Component Analysis](#detailed-component-analysis)
5. [Data Flow and Workflows](#data-flow-and-workflows)
6. [UI Components](#ui-components)
7. [Integration with Preferences System](#integration-with-preferences-system)
8. [Connection to Esoteric Analysis](#connection-to-esoteric-analysis)
9. [Conclusion](#conclusion)

## Introduction
The Astrology pillar of the isopgem application serves as a comprehensive astrological analysis platform that integrates with external calculation engines OpenAstro2 and pyswisseph for precise celestial calculations. This documentation provides a detailed architectural overview of the system, focusing on its component structure, data flow, user interface elements, and integration points. The pillar enables users to generate natal charts, analyze planetary positions, visualize transit patterns, and explore specialized astrological phenomena such as the Venus Rose. The system handles complex astronomical calculations while providing intuitive interfaces for both novice and advanced users. Recent enhancements have significantly expanded the platform's capabilities with new dignities calculation services, comprehensive Venus position caching, enhanced interpretation systems, and improved chart storage mechanisms.

## Core Components
The Astrology pillar consists of several key components that work together to provide a complete astrological analysis environment. The main interface is the astrology_hub, which serves as the central launcher for all astrology tools. The chart_storage_service manages the persistence of astrological charts, allowing users to save, retrieve, and organize their analyses. The chart_record model represents the core data structure for storing astrological information, including planetary positions, house cusps, and aspect data. The openastro_service acts as an integration layer between the application and the external OpenAstro2 calculation engine, handling the complex mathematical computations required for accurate astrological predictions. New components include the dignities_service for calculating planetary dignities, venus_position_store for caching heliocentric positions, interpretation_service for enhanced chart interpretation, and advanced_analysis_panel for comprehensive chart analysis.

**Section sources**
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [dignities_service.py](file://src/pillars/astrology/services/dignities_service.py)
- [venus_position_store.py](file://src/pillars/astrology/services/venus_position_store.py)
- [interpretation_service.py](file://src/pillars/astrology/services/interpretation_service.py)
- [advanced_analysis_panel.py](file://src/pillars/astrology/ui/advanced_analysis_panel.py)

## Architecture Overview
The Astrology pillar follows a layered architecture with clear separation between user interface, business logic, and data persistence layers. The system is designed around a service-oriented approach where specialized services handle specific aspects of astrological computation and data management. The enhanced architecture now includes additional services for advanced astrological techniques and comprehensive data management.

```mermaid
graph TD
subgraph "User Interface"
A[astrology_hub]
B[natal_chart_window]
C[current_transit_window]
D[planetary_positions_window]
E[venus_rose_window]
F[progressions_window]
G[returns_window]
H[synastry_window]
I[chariot_window]
J[advanced_analysis_panel]
K[interpretation_widget]
end
subgraph "Service Layer"
L[openastro_service]
M[chart_storage_service]
N[location_lookup]
O[dignities_service]
P[venus_position_store]
Q[interpretation_service]
R[progressions_service]
S[returns_service]
T[synastry_service]
U[chariot_service]
V[midpoints_service]
W[aspects_service]
end
subgraph "Data Layer"
X[chart_repository]
Y[chart_record]
Z[preferences]
AA[ephemeris_provider]
BB[interpretation_repository]
end
subgraph "External Systems"
CC[OpenAstro2]
DD[pyswisseph]
EE[Open-Meteo Geocoding API]
FF[Venus Position Database]
GG[Interpretation Data Files]
end
A --> L
B --> L
C --> L
D --> L
E --> L
F --> R
F --> L
G --> S
G --> L
H --> T
H --> L
I --> U
I --> L
J --> O
J --> V
J --> W
B --> M
C --> M
D --> M
F --> M
G --> M
H --> M
I --> M
J --> M
K --> Q
L --> CC
L --> DD
N --> EE
M --> X
X --> Y
M --> Z
N --> Z
O --> AA
P --> FF
Q --> BB
R --> AA
S --> AA
T --> L
U --> V
U --> L
```

**Diagram sources**
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)
- [location_lookup.py](file://src/pillars/astrology/services/location_lookup.py)
- [dignities_service.py](file://src/pillars/astrology/services/dignities_service.py)
- [venus_position_store.py](file://src/pillars/astrology/services/venus_position_store.py)
- [interpretation_service.py](file://src/pillars/astrology/services/interpretation_service.py)
- [advanced_analysis_panel.py](file://src/pillars/astrology/ui/advanced_analysis_panel.py)
- [interpretation_widget.py](file://src/pillars/astrology/ui/interpretation_widget.py)

## Detailed Component Analysis

### astrology_hub Analysis
The astrology_hub serves as the main interface for the Astrology pillar, providing a centralized launch point for all astrological tools. It presents users with a clean interface that includes buttons for accessing the natal chart generator, current transit viewer, planetary positions table, Neo-Aubrey Eclipse Clock, and the Cytherean Rose visualization. The hub has been enhanced to include new buttons for the progressions, returns, synastry, and chariot analysis windows.

```mermaid
classDiagram
class AstrologyHub {
+window_manager : WindowManager
-_setup_ui()
-_create_action_buttons(layout)
-_open_natal_chart()
-_open_transit_viewer()
-_open_planetary_positions()
-_open_neo_aubrey()
-_open_venus_rose()
-_open_progressions()
-_open_returns()
-_open_synastry()
-_open_chariot()
}
class WindowManager {
+open_window(window_id, window_class, allow_multiple)
}
AstrologyHub --> WindowManager : "uses"
```

**Diagram sources**
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)

### chart_storage_service Analysis
The chart_storage_service provides a high-level persistence facade for natal charts, handling the storage and retrieval of astrological data. It works in conjunction with the chart_repository to manage database operations while providing a clean API for other components. The service has been updated to support storage and retrieval of charts used in the new analysis types, with enhanced JSON export/import capabilities.

```mermaid
classDiagram
class ChartStorageService {
-_session_factory : ChartSessionFactory
+save_chart(name, request, result, categories, tags, description)
+list_recent(limit)
+search(text, categories, tags, limit)
+load_chart(chart_id)
+export_chart_to_json(chart_id)
+import_chart_from_json(json_str)
-_serialize_request(request)
-_deserialize_request(payload)
-_serialize_event(event)
-_deserialize_event(payload)
-_extract_house_system(request)
-_to_summary(record)
-_rehydrate_result(data)
}
class ChartRepository {
+create_chart(name, description, chart_type, include_svg, house_system, event_timestamp, timezone_offset, location_label, latitude, longitude, elevation, request_payload, result_payload, categories, tags)
+get_chart(chart_id)
+list_recent(limit)
+search(text, categories, tags, limit)
}
class SavedChartSummary {
+chart_id : int
+name : str
+event_timestamp : datetime
+location_label : str
+categories : List[str]
+tags : List[str]
+chart_type : str
}
class LoadedChart {
+chart_id : int
+request : ChartRequest
+categories : List[str]
+tags : List[str]
+description : Optional[str]
}
ChartStorageService --> ChartRepository : "uses"
ChartStorageService --> SavedChartSummary : "returns"
ChartStorageService --> LoadedChart : "returns"
```

**Diagram sources**
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py)

### chart_record Analysis
The chart_record module defines the SQLAlchemy models for persisting astrology charts in the database. It includes the main AstrologyChart entity along with supporting entities for categories and tags, enabling rich organization and filtering of stored charts. The model has been updated to support new chart types for the enhanced features.

```mermaid
classDiagram
class AstrologyChart {
+id : int
+name : str
+description : Optional[str]
+chart_type : str
+include_svg : bool
+house_system : Optional[str]
+event_timestamp : datetime
+timezone_offset : float
+location_label : str
+latitude : float
+longitude : float
+elevation : Optional[float]
+request_payload : Dict
+result_payload : Dict
+created_at : datetime
+updated_at : datetime
+categories : List[ChartCategory]
+tags : List[ChartTag]
}
class ChartCategory {
+id : int
+name : str
+charts : List[AstrologyChart]
}
class ChartTag {
+id : int
+name : str
+charts : List[AstrologyChart]
}
class chart_category_links {
+chart_id : int
+category_id : int
}
class chart_tag_links {
+chart_id : int
+tag_id : int
}
AstrologyChart --> chart_category_links : "has many"
AstrologyChart --> chart_tag_links : "has many"
ChartCategory --> chart_category_links : "has many"
ChartTag --> chart_tag_links : "has many"
chart_category_links --> AstrologyChart : "belongs to"
chart_category_links --> ChartCategory : "belongs to"
chart_tag_links --> AstrologyChart : "belongs to"
chart_tag_links --> ChartTag : "belongs to"
```

**Diagram sources**
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)

### openastro_service Analysis
The openastro_service acts as a high-level orchestration layer for OpenAstro2 usage, isolating direct dependencies on the external library while providing a clean API surface for the UI components. It handles chart generation, house system management, and error handling. The service serves as the foundation for the new specialized services.

```mermaid
classDiagram
class OpenAstroService {
+HOUSE_SYSTEM_LABELS : Dict[str, str]
-_logger : Logger
-_default_settings : Dict[str, Any]
+__init__(default_settings)
+generate_chart(request)
+list_house_systems()
+default_settings()
-_build_default_settings()
-_to_openastro_event(event)
-_build_chart_result(chart, request)
-_prime_chart(chart)
-_planet_data(chart)
-_extract_planet_positions(chart, planet_data)
-_extract_house_positions(chart)
-_extract_aspects(chart)
-_maybe_render_svg(chart, include_svg)
-_extract_raw_payload(chart, planet_data)
}
class ChartRequest {
+primary_event : AstrologyEvent
+chart_type : str
+reference_event : Optional[AstrologyEvent]
+include_svg : bool
+settings : Optional[Dict[str, Any]]
}
class ChartResult {
+chart_type : str
+planet_positions : List[PlanetPosition]
+house_positions : List[HousePosition]
+aspect_summary : Dict[str, Any]
+svg_document : Optional[str]
+raw_payload : Dict[str, Any]
+has_svg()
+to_dict()
}
class AstrologyEvent {
+name : str
+timestamp : datetime
+location : GeoLocation
+timezone_offset : Optional[float]
+metadata : Dict[str, Any]
+resolved_timezone_offset()
+to_openastro_kwargs()
}
class GeoLocation {
+name : str
+latitude : float
+longitude : float
+elevation : float
+country_code : Optional[str]
}
OpenAstroService --> ChartRequest : "consumes"
OpenAstroService --> ChartResult : "produces"
OpenAstroService --> AstrologyEvent : "converts"
OpenAstroService --> GeoLocation : "uses"
```

**Diagram sources**
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)

### dignities_service Analysis
The dignities_service calculates essential and accidental dignities for the Classic 7 planets, providing a comprehensive assessment of planetary strength and condition in a chart. It evaluates essential dignities (domicile, exaltation, detriment, fall) and accidental dignities (house placement, motion, solar proximity, mutual reception) with detailed scoring systems.

```mermaid
classDiagram
class DignitiesService {
+calculate_dignities(planet_positions, house_positions)
+_get_sign(degree)
+_get_essential_dignity(planet, sign)
+_get_accidental_dignities(planet, house, is_retrograde, planet_lon, sun_lon, mutual_receptions)
+_find_mutual_receptions(planet_signs)
+_build_house_cusps(house_positions)
+_get_house(degree, cusps)
+_angular_distance(lon1, lon2)
}
class PlanetaryDignity {
+planet : str
+sign : str
+degree : float
+house : int
+essential_dignity : str
+essential_score : int
+accidental_dignities : List[str]
+accidental_score : int
+total_score : int
+is_retrograde : bool
}
DignitiesService --> PlanetaryDignity : "creates"
```

**Diagram sources**
- [dignities_service.py](file://src/pillars/astrology/services/dignities_service.py)

### venus_position_store Analysis
The venus_position_store provides a comprehensive caching system for heliocentric (Sun-centered) positions of Venus and Earth, enabling fast repeated access to ephemeris data. It maintains a SQLite database with heliocentric coordinates at configurable cadence intervals, supporting both idealized and real physics modes.

```mermaid
classDiagram
class VenusPositionStore {
+db_path : Path
+is_built() bool
+connect() sqlite3.Connection
+ensure_schema(conn)
+get_heliocentric_position(dt, body, cadence_minutes, conn) HeliocentricPosition
+upsert_heliocentric_position(conn, pos)
+round_dt_to_cadence(dt, cadence_minutes) datetime
+to_dt_key(dt) str
}
class HeliocentricPosition {
+dt_utc : datetime
+body : str
+lon_deg : float
+lat_deg : float
+distance_au : float
}
VenusPositionStore --> HeliocentricPosition : "manages"
```

**Diagram sources**
- [venus_position_store.py](file://src/pillars/astrology/services/venus_position_store.py)

### interpretation_service Analysis
The interpretation_service orchestrates the generation of comprehensive chart interpretation reports, providing enhanced content models and structured interpretation data. It supports multiple interpretation types including chart interpretation, transit interpretation, and synastry interpretation with rich content formatting.

```mermaid
classDiagram
class InterpretationService {
+repository : InterpretationRepository
+aspects_service : AspectsService
+interpret_chart(chart, chart_name) InterpretationReport
+interpret_transits(transit_chart, natal_chart, aspects) InterpretationReport
+interpret_synastry(chart_a, chart_b, aspects) InterpretationReport
+_interpret_planets(planets, houses, report)
+_interpret_aspects(planets, report)
+_interpret_dominants(planets, report)
+_resolve_house(planet_degree, houses) int
+_is_between(target, start, end) bool
}
class InterpretationReport {
+chart_name : str
+segments : List[InterpretationSegment]
+add_segment(title, content, tags, weight)
+to_markdown() str
}
class InterpretationSegment {
+title : str
+content : RichInterpretationContent
+tags : List[str]
+weight : float
}
class RichInterpretationContent {
+text : str
+archetype : Optional[str]
+essence : Optional[str]
+shadow : Optional[str]
+gift : Optional[str]
+alchemical_process : Optional[str]
+keywords : List[str]
}
InterpretationService --> InterpretationReport : "creates"
InterpretationService --> InterpretationSegment : "uses"
InterpretationService --> RichInterpretationContent : "contains"
```

**Diagram sources**
- [interpretation_service.py](file://src/pillars/astrology/services/interpretation_service.py)
- [interpretation_models.py](file://src/pillars/astrology/models/interpretation_models.py)

### advanced_analysis_panel Analysis
The advanced_analysis_panel provides a comprehensive reusable component for advanced chart analysis, featuring integrated dignities display, fixed stars, Arabic parts, midpoints, harmonics, and Maat symbols. It serves as a central hub for displaying detailed astrological analysis across all chart types.

```mermaid
classDiagram
class AdvancedAnalysisPanel {
+sidebar : QListWidget
+tab_widgets : QStackedWidget
+services : Dict[str, Any]
+ASTRO_PLANETS : Dict[str, str]
+ASTRO_ZODIAC : Dict[str, str]
+ASPECT_COLORS : Dict[str, str]
+_setup_ui()
+_create_astro_item(text, is_symbol) QTableWidgetItem
+_get_planet_display(name, use_astro) str
+_get_aspect_display(name, use_astro) str
+_render_dignities()
+_render_fixed_stars()
+_render_arabic_parts()
+_render_midpoints()
+_render_harmonics()
+_render_maat_symbols()
+_render_aspects_table()
}
AdvancedAnalysisPanel --> DignitiesService : "uses"
AdvancedAnalysisPanel --> FixedStarsService : "uses"
AdvancedAnalysisPanel --> ArabicPartsService : "uses"
AdvancedAnalysisPanel --> MidpointsService : "uses"
AdvancedAnalysisPanel --> HarmonicsService : "uses"
AdvancedAnalysisPanel --> MaatSymbolsService : "uses"
```

**Diagram sources**
- [advanced_analysis_panel.py](file://src/pillars/astrology/ui/advanced_analysis_panel.py)

## Data Flow and Workflows

### Natal Chart Generation Workflow
The process of generating a natal chart follows a well-defined sequence from user input through calculation to visualization. This workflow demonstrates the integration between UI components, service layers, and external calculation engines.

```mermaid
sequenceDiagram
participant User as "User"
participant UI as "natal_chart_window"
participant Service as "openastro_service"
participant Engine as "OpenAstro2"
participant Storage as "chart_storage_service"
participant DB as "Database"
User->>UI : Enter birth data (date, time, location)
UI->>UI : Validate input parameters
UI->>Service : generate_chart(request)
Service->>Engine : Call OpenAstro2 with event data
Engine-->>Service : Return calculated chart data
Service-->>UI : Return ChartResult
UI->>UI : Render planetary positions, houses, aspects
User->>UI : Click "Save Chart"
UI->>Storage : save_chart(name, request, result, categories, tags)
Storage->>DB : Store chart data via chart_repository
DB-->>Storage : Return chart_id
Storage-->>UI : Confirmation
UI->>User : Display success message
```

**Diagram sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py)

### Transit Analysis Workflow
The transit analysis workflow enables users to compare current planetary positions with a natal chart, providing insights into current astrological influences. This process leverages the same calculation engine but with different input parameters.

```mermaid
sequenceDiagram
participant User as "User"
participant UI as "current_transit_window"
participant Service as "openastro_service"
participant Engine as "OpenAstro2"
participant Preferences as "AstrologyPreferences"
User->>UI : Open Current Transit Viewer
UI->>Preferences : load_default_location()
Preferences-->>UI : Return default location
UI->>UI : Populate location fields
User->>UI : Click "Generate Transit Now"
UI->>Service : generate_chart(request with current timestamp)
Service->>Engine : Call OpenAstro2 with current event
Engine-->>Service : Return calculated transit data
Service-->>UI : Return ChartResult
UI->>UI : Render transit planetary positions
UI->>User : Display transit chart with current planetary positions
```

**Diagram sources**
- [current_transit_window.py](file://src/pillars/astrology/ui/current_transit_window.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)

### Dignities Calculation Workflow
The dignities calculation workflow processes planetary positions and house cusps to determine essential and accidental dignities for each planet, providing a comprehensive assessment of planetary strength.

```mermaid
sequenceDiagram
participant UI as "AdvancedAnalysisPanel"
participant Service as "DignitiesService"
participant Provider as "EphemerisProvider"
UI->>Service : calculate_dignities(planet_data, house_data)
Service->>Service : Build house cusp lookup
Service->>Service : Extract planet positions and signs
Service->>Service : Calculate essential dignities
Service->>Service : Calculate accidental dignities
Service->>Service : Evaluate mutual receptions
Service->>Service : Calculate total scores
Service-->>UI : Return PlanetaryDignity objects
UI->>UI : Display dignities table with color-coded scores
UI->>UI : Update chart strength summary
```

**Diagram sources**
- [advanced_analysis_panel.py](file://src/pillars/astrology/ui/advanced_analysis_panel.py)
- [dignities_service.py](file://src/pillars/astrology/services/dignities_service.py)

### Venus Position Caching Workflow
The Venus position caching workflow enables efficient access to heliocentric positions for both Venus and Earth, supporting both idealized and real physics modes with configurable cadence intervals.

```mermaid
sequenceDiagram
participant UI as "VenusRoseWindow"
participant Store as "VenusPositionStore"
participant Provider as "EphemerisProvider"
UI->>Store : get_heliocentric_position(dt, "earth")
Store->>Store : Check if cache exists
Store-->>UI : Return cached position or None
UI->>Store : get_heliocentric_position(dt, "venus")
Store->>Store : Check if cache exists
Store-->>UI : Return cached position or None
UI->>Provider : get_heliocentric_ecliptic_latlon_distance()
Provider-->>UI : Return live ephemeris data
UI->>UI : Update positions with real physics mode
UI->>UI : Render trace lines and highlight events
```

**Diagram sources**
- [venus_rose_window.py](file://src/pillars/astrology/ui/venus_rose_window.py)
- [venus_position_store.py](file://src/pillars/astrology/services/venus_position_store.py)

### Enhanced Interpretation Workflow
The enhanced interpretation workflow provides comprehensive chart interpretation with rich content models, structured segments, and weighted interpretation scoring.

```mermaid
sequenceDiagram
participant UI as "NatalChartWindow"
participant Service as "InterpretationService"
participant Repo as "InterpretationRepository"
participant Aspects as "AspectsService"
UI->>Service : interpret_chart(chart, chart_name)
Service->>Service : _interpret_planets(planets, houses, report)
Service->>Repo : get_planet_sign_house_text()
Repo-->>Service : Return interpretation content
Service->>Service : _interpret_aspects(planets, report)
Service->>Aspects : calculate_aspects()
Aspects-->>Service : Return aspect data
Service->>Repo : get_aspect_text()
Repo-->>Service : Return aspect interpretation
Service->>Service : _interpret_dominants(planets, report)
Service-->>UI : Return InterpretationReport
UI->>UI : Display rich formatted interpretation
UI->>UI : Render markdown content with structured segments
```

**Diagram sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [interpretation_service.py](file://src/pillars/astrology/services/interpretation_service.py)
- [interpretation_widget.py](file://src/pillars/astrology/ui/interpretation_widget.py)

## UI Components

### Natal Chart Generator
The natal chart generator provides a comprehensive interface for creating birth charts. Users can input personal information including name, birth date and time, location, and timezone offset. The interface includes features for saving charts with categories and tags, searching for locations via the Open-Meteo geocoding API, and setting default locations for future use. The enhanced version now includes integrated interpretation generation and advanced analysis panel access.

**Section sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)

### Planetary Positions Table
The planetary positions table (ephemeris viewer) allows users to analyze planetary movements over time. Users can configure the time range, step size, and select specific planets to track. The interface supports exporting data to CSV format and displays positions in zodiacal notation with retrograde indicators.

**Section sources**
- [planetary_positions_window.py](file://src/pillars/astrology/ui/planetary_positions_window.py)

### Transit Dashboard
The transit dashboard provides a real-time view of current planetary positions relative to a user's default location. It includes controls for generating current transits, exporting SVG visualizations, and opening charts in external browsers. The interface automatically applies the user's saved default location and timezone settings.

**Section sources**
- [current_transit_window.py](file://src/pillars/astrology/ui/current_transit_window.py)

### Venus Rose Visualization
The Venus Rose visualization is a specialized tool that illustrates the Pentagram of Venus, showing the 13:8 orbital resonance between Earth and Venus. The interface includes animation controls, physics mode toggling (ideal vs. real), and predictive event tracking for inferior and superior conjunctions. The enhanced version now includes comprehensive heliocentric position caching and real physics mode with event prediction capabilities.

```mermaid
flowchart TD
Start([Venus Rose Window]) --> Configure["Set Date and Physics Mode"]
Configure --> CacheCheck{"Cache Available?"}
CacheCheck --> |Yes| CachedCalc["Use Cached Positions"]
CacheCheck --> |No| LiveCalc["Use Live Ephemeris"]
CachedCalc --> Update["Update Planet Positions"]
LiveCalc --> Update
Update --> Trace["Draw Trace Line"]
Trace --> CheckEvent["Check for Conjunction Events"]
CheckEvent --> |Event Detected| Highlight["Add Glowing Particle"]
CheckEvent --> |No Event| Continue["Continue Animation"]
Highlight --> Continue
Continue --> Update
Update --> Predict["Predict Future Events"]
Predict --> Table["Update Event Table"]
Table --> Continue
```

**Diagram sources**
- [venus_rose_window.py](file://src/pillars/astrology/ui/venus_rose_window.py)

**Section sources**
- [venus_rose_window.py](file://src/pillars/astrology/ui/venus_rose_window.py)

### Advanced Analysis Panel
The advanced analysis panel provides comprehensive chart analysis with integrated dignities display, fixed stars, Arabic parts, midpoints, harmonics, and Maat symbols. It serves as a central hub for displaying detailed astrological analysis across all chart types, with color-coded dignities scoring and interactive tables.

**Section sources**
- [advanced_analysis_panel.py](file://src/pillars/astrology/ui/advanced_analysis_panel.py)

### Enhanced Interpretation Widget
The enhanced interpretation widget displays comprehensive chart interpretation reports with rich content formatting, structured segments, and weighted interpretation scoring. It supports markdown rendering and provides detailed analysis of planetary conditions, aspects, and chart dynamics.

**Section sources**
- [interpretation_widget.py](file://src/pillars/astrology/ui/interpretation_widget.py)

### Progressions Window
The progressions window provides a focused interface for calculating Secondary Progressions and Solar Arc Directions. Users can input natal data and a target date to generate progressed charts, with options to display the results as a bi-wheel comparison with the natal chart.

**Section sources**
- [progressions_window.py](file://src/pillars/astrology/ui/progressions_window.py)

### Returns Window
The returns window enables users to calculate planetary returns such as Solar Returns and Lunar Returns. The interface allows for relocation of the return chart to a different location and provides precise calculation of the return moment.

**Section sources**
- [returns_window.py](file://src/pillars/astrology/ui/returns_window.py)

### Synastry Window
The synastry window provides a comprehensive interface for relationship astrology analysis. Users can input data for two individuals and choose between three analysis models: Synastry (bi-wheel), Composite (midpoint chart), and Davison (time/space midpoint chart). The window includes multiple tabs for different aspects of the analysis.

**Section sources**
- [synastry_window.py](file://src/pillars/astrology/ui/synastry_window.py)

### Chariot Window
The chariot window displays the complete Chariot Midpoints analysis, showing the 21 midpoints organized by their 7 Trios, the calculated Axles, the Chariot Point, and the Egyptian degree symbols from the Sacred Landscape. The interface features a tri-panel layout with a tree view, summary information, and degree symbol display.

**Section sources**
- [chariot_window.py](file://src/pillars/astrology/ui/chariot_window.py)

## Integration with Preferences System
The Astrology pillar integrates with a preferences system that allows users to save and recall their default settings, particularly their default location for transit calculations. This system uses JSON-based persistence to store user preferences across sessions.

```mermaid
classDiagram
class AstrologyPreferences {
-_path : Path
+load_default_location()
+save_default_location(location)
-_read()
-_write(payload)
}
class DefaultLocation {
+name : str
+latitude : float
+longitude : float
+elevation : float
+timezone_offset : float
+timezone_id : Optional[str]
}
AstrologyPreferences --> DefaultLocation : "stores"
natal_chart_window --> AstrologyPreferences : "uses"
current_transit_window --> AstrologyPreferences : "uses"
planetary_positions_window --> AstrologyPreferences : "uses"
progressions_window --> AstrologyPreferences : "uses"
returns_window --> AstrologyPreferences : "uses"
synastry_window --> AstrologyPreferences : "uses"
chariot_window --> AstrologyPreferences : "uses"
```

**Diagram sources**
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)

**Section sources**
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [current_transit_window.py](file://src/pillars/astrology/ui/current_transit_window.py)
- [planetary_positions_window.py](file://src/pillars/astrology/ui/planetary_positions_window.py)
- [progressions_window.py](file://src/pillars/astrology/ui/progressions_window.py)
- [returns_window.py](file://src/pillars/astrology/ui/returns_window.py)
- [synastry_window.py](file://src/pillars/astrology/ui/synastry_window.py)
- [chariot_window.py](file://src/pillars/astrology/ui/chariot_window.py)

## Connection to Esoteric Analysis
The Astrology pillar connects to broader esoteric analysis through planetary correspondences in gematria and TQ systems. These connections are facilitated through shared data models and integration points that allow astrological data to be used in conjunction with other esoteric calculations. The enhanced features deepen these connections, particularly through the Chariot system's integration with Egyptian degree symbols and the synastry analysis's connections to relationship dynamics in gematria.

```mermaid
graph TD
A[Astrology Pillar] --> B[Gematria System]
A --> C[TQ System]
B --> D[Planetary Correspondences]
C --> D
D --> E[Esoteric Analysis]
A --> F[Planetary Positions]
F --> D
A --> G[Zodiacal Signs]
G --> D
A --> H[Aspect Patterns]
H --> D
A --> I[Chariot Midpoints]
I --> D
A --> J[Synastry Aspects]
J --> D
A --> K[Progressions]
K --> D
A --> L[Returns]
L --> D
A --> M[Dignities Analysis]
M --> D
A --> N[Venus Position Overlay]
N --> D
A --> O[Enhanced Interpretations]
O --> D
```

**Diagram sources**
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)

**Section sources**
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)

## Conclusion
The Astrology pillar of the isopgem application provides a robust and comprehensive platform for astrological analysis, integrating external calculation engines OpenAstro2 and pyswisseph to deliver accurate celestial calculations. The system's architecture features a clear separation of concerns with well-defined components for user interface, service logic, and data persistence. Key features include natal chart generation, transit analysis, planetary position tracking, and specialized visualizations like the Venus Rose. Recent enhancements have significantly expanded the platform's capabilities with the addition of comprehensive dignities calculation services, advanced Venus position caching with real physics support, enhanced interpretation systems with rich content models, and improved chart storage mechanisms. The integration with user preferences allows for personalized settings, while the connection to broader esoteric analysis systems enables holistic interpretation of astrological data. The pillar demonstrates a sophisticated approach to handling complex astronomical calculations while maintaining an accessible user interface for both novice and advanced practitioners.