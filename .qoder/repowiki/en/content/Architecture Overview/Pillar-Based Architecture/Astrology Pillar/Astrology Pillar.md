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
</cite>

## Update Summary
**Changes Made**   
- Added new sections for chariot midpoints, progressions, returns, and synastry analysis
- Updated architecture overview to include new services and UI components
- Added detailed component analysis for new services and windows
- Added new workflows for progressions, returns, and synastry analysis
- Updated UI components section to include new windows
- Added new diagrams for new services and workflows

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
The Astrology pillar of the isopgem application serves as a comprehensive astrological analysis platform that integrates with external calculation engines OpenAstro2 and pyswisseph for precise celestial calculations. This documentation provides a detailed architectural overview of the system, focusing on its component structure, data flow, user interface elements, and integration points. The pillar enables users to generate natal charts, analyze planetary positions, visualize transit patterns, and explore specialized astrological phenomena such as the Venus Rose. The system handles complex astronomical calculations while providing intuitive interfaces for both novice and advanced users. Recent enhancements have expanded the platform's capabilities to include chariot midpoints, progressions, returns, and synastry analysis with corresponding UI windows and services.

## Core Components
The Astrology pillar consists of several key components that work together to provide a complete astrological analysis environment. The main interface is the astrology_hub, which serves as the central launcher for all astrology tools. The chart_storage_service manages the persistence of astrological charts, allowing users to save, retrieve, and organize their analyses. The chart_record model represents the core data structure for storing astrological information, including planetary positions, house cusps, and aspect data. The openastro_service acts as an integration layer between the application and the external OpenAstro2 calculation engine, handling the complex mathematical computations required for accurate astrological predictions. New components include the chariot_service for calculating chariot midpoints, progressions_service for secondary progressions and solar arc directions, returns_service for planetary returns, and synastry_service for relationship astrology calculations.

**Section sources**
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [progressions_service.py](file://src/pillars/astrology/services/progressions_service.py)
- [returns_service.py](file://src/pillars/astrology/services/returns_service.py)
- [synastry_service.py](file://src/pillars/astrology/services/synastry_service.py)
- [chariot_service.py](file://src/pillars/astrology/services/chariot_service.py)

## Architecture Overview
The Astrology pillar follows a layered architecture with clear separation between user interface, business logic, and data persistence layers. The system is designed around a service-oriented approach where specialized services handle specific aspects of astrological computation and data management. The enhanced architecture now includes additional services for advanced astrological techniques.

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
end
subgraph "Service Layer"
J[openastro_service]
K[chart_storage_service]
L[location_lookup]
M[progressions_service]
N[returns_service]
O[synastry_service]
P[chariot_service]
Q[midpoints_service]
end
subgraph "Data Layer"
R[chart_repository]
S[chart_record]
T[preferences]
U[ephemeris_provider]
end
subgraph "External Systems"
V[OpenAstro2]
W[pyswisseph]
X[Open-Meteo Geocoding API]
end
A --> J
B --> J
C --> J
D --> J
E --> J
F --> M
F --> J
G --> N
G --> J
H --> O
H --> J
I --> P
I --> J
B --> K
C --> K
D --> K
F --> K
G --> K
H --> K
I --> K
J --> V
J --> W
L --> X
K --> R
R --> S
K --> T
L --> T
M --> U
N --> U
O --> J
P --> Q
P --> J
```

**Diagram sources**
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)
- [location_lookup.py](file://src/pillars/astrology/services/location_lookup.py)
- [progressions_service.py](file://src/pillars/astrology/services/progressions_service.py)
- [returns_service.py](file://src/pillars/astrology/services/returns_service.py)
- [synastry_service.py](file://src/pillars/astrology/services/synastry_service.py)
- [chariot_service.py](file://src/pillars/astrology/services/chariot_service.py)
- [midpoints_service.py](file://src/pillars/astrology/services/midpoints_service.py)

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
The chart_storage_service provides a high-level persistence facade for natal charts, handling the storage and retrieval of astrological data. It works in conjunction with the chart_repository to manage database operations while providing a clean API for other components. The service has been updated to support storage and retrieval of charts used in the new analysis types.

```mermaid
classDiagram
class ChartStorageService {
-_session_factory : ChartSessionFactory
+save_chart(name, request, result, categories, tags, description)
+list_recent(limit)
+search(text, categories, tags, limit)
+load_chart(chart_id)
-_serialize_request(request)
-_deserialize_request(payload)
-_serialize_event(event)
-_deserialize_event(payload)
-_extract_house_system(request)
-_to_summary(record)
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

### progressions_service Analysis
The progressions_service calculates Secondary Progressions (1 Day = 1 Year) and Solar Arc Directions. Secondary Progressions advance the natal chart by one day for each year of life, while Solar Arc Directions move all planets by the arc between the natal Sun and progressed Sun.

```mermaid
classDiagram
class ProgressionsService {
-_ephemeris : EphemerisProvider
-_openastro : OpenAstroService
+__init__(openastro_service)
+calculate_secondary_progression(natal_req, target_date)
+calculate_solar_arc(natal_req, target_date)
}
class EphemerisProvider {
+get_instance()
+get_geocentric_ecliptic_position(body_name, timestamp)
+get_extended_data(body_name, timestamp)
}
class OpenAstroService {
+generate_chart(request)
}
ProgressionsService --> EphemerisProvider : "uses"
ProgressionsService --> OpenAstroService : "uses"
```

**Diagram sources**
- [progressions_service.py](file://src/pillars/astrology/services/progressions_service.py)
- [ephemeris_provider.py](file://src/pillars/astrology/repositories/ephemeris_provider.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)

### returns_service Analysis
The returns_service calculates the exact moment when a planet returns to its natal longitude, such as Solar Returns (annual birthday charts) and Lunar Returns (monthly mood indicators). The service uses iterative solving to find the precise return time.

```mermaid
classDiagram
class ReturnsService {
-_ephemeris : EphemerisProvider
+__init__()
+calculate_return(natal_event, target_year, body_name, return_count)
+_estimate_start_time(natal_dt, target_year, body_name, count)
+_solve_exact_time(body_name, target_lon, start_estimate)
+_shortest_distance(a, b)
}
class EphemerisProvider {
+get_instance()
+get_geocentric_ecliptic_position(body_name, timestamp)
+get_extended_data(body_name, timestamp)
}
ReturnsService --> EphemerisProvider : "uses"
```

**Diagram sources**
- [returns_service.py](file://src/pillars/astrology/services/returns_service.py)
- [ephemeris_provider.py](file://src/pillars/astrology/repositories/ephemeris_provider.py)

### synastry_service Analysis
The synastry_service calculates relationship charts including Synastry (bi-wheel comparison), Composite (midpoint of corresponding planets), and Davison (chart cast for time/space midpoint). The service provides the mathematical foundation for relationship astrology.

```mermaid
classDiagram
class SynastryService {
-_openastro : OpenAstroService
+__init__(openastro_service)
+generate_chart(event)
+calculate_composite(result_a, result_b)
+calculate_davison(event_a, event_b)
}
class DavisonInfo {
+midpoint_time : datetime
+midpoint_latitude : float
+midpoint_longitude : float
}
class CompositeResult {
+planets : List[PlanetPosition]
+houses : List[HousePosition]
+julian_day : Optional[float]
}
class DavisonResult {
+chart : ChartResult
+info : DavisonInfo
}
SynastryService --> OpenAstroService : "uses"
```

**Diagram sources**
- [synastry_service.py](file://src/pillars/astrology/services/synastry_service.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)

### chariot_service Analysis
The chariot_service calculates the Chariot Midpoints System, synthesizing planetary midpoints into Major Arcana correspondences, grouping them into functional Trios, deriving Axles of Will, and computing the ultimate Chariot Point. The service builds upon midpoints_service and maat_symbols_service.

```mermaid
classDiagram
class ChariotService {
+midpoints_service : MidpointsService
+maat_service : MaatSymbolsService
+_definitions : Optional[Dict]
+__init__()
+_load_definitions()
+_degree_to_sign(longitude)
+_calculate_mean_longitude(longitudes)
+get_chariot_midpoints(planet_positions)
+calculate_axles(midpoints)
+calculate_chariot_point(axles)
+detect_fateful_positions(midpoints, axles, chariot_point)
+generate_chariot_report(chart)
+generate_from_positions(planet_positions)
}
class MidpointsService {
+calculate_midpoints(planet_positions, classic_only)
}
class MaatSymbolsService {
+get_symbol(degree)
}
ChariotService --> MidpointsService : "uses"
ChariotService --> MaatSymbolsService : "uses"
```

**Diagram sources**
- [chariot_service.py](file://src/pillars/astrology/services/chariot_service.py)
- [midpoints_service.py](file://src/pillars/astrology/services/midpoints_service.py)
- [maat_symbols_service.py](file://src/pillars/astrology/services/maat_symbols_service.py)

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

### Progressions Workflow
The progressions workflow allows users to calculate Secondary Progressions or Solar Arc Directions for a natal chart at a target date, providing insights into personal development and timing of events.

```mermaid
sequenceDiagram
participant User as "User"
participant UI as "progressions_window"
participant Service as "progressions_service"
participant Engine as "OpenAstro2"
participant Storage as "chart_storage_service"
User->>UI : Enter natal data and target date
UI->>Service : calculate_secondary_progression() or calculate_solar_arc()
Service->>Engine : Generate natal chart
Engine-->>Service : Return natal chart data
Service->>Engine : Calculate progressed chart
Engine-->>Service : Return progressed chart data
Service-->>UI : Return both charts
UI->>UI : Render bi-wheel comparison
User->>UI : Click "Save Chart"
UI->>Storage : save_chart()
Storage-->>UI : Confirmation
UI->>User : Display success message
```

**Diagram sources**
- [progressions_window.py](file://src/pillars/astrology/ui/progressions_window.py)
- [progressions_service.py](file://src/pillars/astrology/services/progressions_service.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)

### Returns Workflow
The returns workflow calculates the exact time when a planet returns to its natal position, creating a chart for that moment which provides insights into the themes of the coming year (Solar Return) or month (Lunar Return).

```mermaid
sequenceDiagram
participant User as "User"
participant UI as "returns_window"
participant Service as "returns_service"
participant Engine as "OpenAstro2"
participant Ephemeris as "EphemerisProvider"
User->>UI : Enter natal data and target year
UI->>Service : calculate_return()
Service->>Ephemeris : Get natal longitude
Ephemeris-->>Service : Return natal longitude
Service->>Service : Estimate start time
Service->>Ephemeris : Solve for exact return time
Ephemeris-->>Service : Return exact time
Service->>Engine : Generate chart for return time
Engine-->>Service : Return chart data
Service-->>UI : Return chart result
UI->>UI : Render return chart
UI->>User : Display return chart with planetary positions
```

**Diagram sources**
- [returns_window.py](file://src/pillars/astrology/ui/returns_window.py)
- [returns_service.py](file://src/pillars/astrology/services/returns_service.py)
- [ephemeris_provider.py](file://src/pillars/astrology/repositories/ephemeris_provider.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)

### Synastry Analysis Workflow
The synastry analysis workflow enables users to compare two charts for relationship analysis, supporting three different models: Synastry (bi-wheel), Composite (midpoint chart), and Davison (time/space midpoint chart).

```mermaid
sequenceDiagram
participant User as "User"
participant UI as "synastry_window"
participant Service as "synastry_service"
participant Engine as "OpenAstro2"
participant Storage as "chart_storage_service"
User->>UI : Enter data for Person A and Person B
UI->>Service : generate_chart() for both persons
Service->>Engine : Generate chart for Person A
Engine-->>Service : Return chart A
Service->>Engine : Generate chart for Person B
Engine-->>Service : Return chart B
Service->>Service : Calculate composite or Davison chart
Service-->>UI : Return all chart data
UI->>UI : Render selected chart type
User->>UI : Switch between Aspects, Midpoints, and Analysis tabs
UI->>UI : Display cross-chart analysis
```

**Diagram sources**
- [synastry_window.py](file://src/pillars/astrology/ui/synastry_window.py)
- [synastry_service.py](file://src/pillars/astrology/services/synastry_service.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)

### Chariot Analysis Workflow
The chariot analysis workflow calculates the complete Chariot Midpoints system from a natal chart, including the 21 midpoints, 7 axles, and the Chariot Point, providing a synthesis of the soul's will and purpose.

```mermaid
sequenceDiagram
participant User as "User"
participant UI as "chariot_window"
participant Service as "chariot_service"
participant SubService as "midpoints_service"
participant SymbolService as "maat_symbols_service"
participant Engine as "OpenAstro2"
participant Storage as "chart_storage_service"
User->>UI : Load natal chart
UI->>Storage : load_chart()
Storage-->>UI : Return chart data
UI->>Service : generate_chariot_report()
Service->>SubService : calculate_midpoints()
SubService-->>Service : Return midpoints
Service->>Service : Group midpoints into trios
Service->>Service : Calculate axles and chariot point
Service->>SymbolService : get_symbol() for each position
SymbolService-->>Service : Return degree symbols
Service-->>UI : Return complete chariot report
UI->>UI : Populate tree, summary, and symbol panels
UI->>User : Display complete chariot analysis
```

**Diagram sources**
- [chariot_window.py](file://src/pillars/astrology/ui/chariot_window.py)
- [chariot_service.py](file://src/pillars/astrology/services/chariot_service.py)
- [midpoints_service.py](file://src/pillars/astrology/services/midpoints_service.py)
- [maat_symbols_service.py](file://src/pillars/astrology/services/maat_symbols_service.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)

## UI Components

### Natal Chart Generator
The natal chart generator provides a comprehensive interface for creating birth charts. Users can input personal information including name, birth date and time, location, and timezone offset. The interface includes features for saving charts with categories and tags, searching for locations via the Open-Meteo geocoding API, and setting default locations for future use.

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
The Venus Rose visualization is a specialized tool that illustrates the Pentagram of Venus, showing the 13:8 orbital resonance between Earth and Venus. The interface includes animation controls, physics mode toggling (ideal vs. real), and predictive event tracking for inferior and superior conjunctions.

```mermaid
flowchart TD
Start([Venus Rose Window]) --> Configure["Set Date and Physics Mode"]
Configure --> Animate["Start Animation"]
Animate --> Update["Update Planet Positions"]
Update --> Trace["Draw Trace Line"]
Trace --> CheckEvent["Check for Conjunction Events"]
CheckEvent --> |Event Detected| Highlight["Add Glowing Particle"]
CheckEvent --> |No Event| Continue["Continue Animation"]
Highlight --> Continue
Continue --> Update
Animate --> |Stop| End([Animation Stopped])
Update --> |Reset| Start
```

**Diagram sources**
- [venus_rose_window.py](file://src/pillars/astrology/ui/venus_rose_window.py)

**Section sources**
- [venus_rose_window.py](file://src/pillars/astrology/ui/venus_rose_window.py)

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
```

**Diagram sources**
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)

**Section sources**
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)

## Conclusion
The Astrology pillar of the isopgem application provides a robust and comprehensive platform for astrological analysis, integrating external calculation engines OpenAstro2 and pyswisseph to deliver accurate celestial calculations. The system's architecture features a clear separation of concerns with well-defined components for user interface, service logic, and data persistence. Key features include natal chart generation, transit analysis, planetary position tracking, and specialized visualizations like the Venus Rose. Recent enhancements have significantly expanded the platform's capabilities with the addition of chariot midpoints, progressions, returns, and synastry analysis, each with corresponding UI windows and services. The integration with user preferences allows for personalized settings, while the connection to broader esoteric analysis systems enables holistic interpretation of astrological data. The pillar demonstrates a sophisticated approach to handling complex astronomical calculations while maintaining an accessible user interface for both novice and advanced practitioners.