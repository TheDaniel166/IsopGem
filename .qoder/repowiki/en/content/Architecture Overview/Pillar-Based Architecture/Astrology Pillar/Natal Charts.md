# Natal Charts

<cite>
**Referenced Files in This Document**   
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)
- [location_lookup.py](file://src/pillars/astrology/services/location_lookup.py)
- [conversions.py](file://src/pillars/astrology/utils/conversions.py)
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)

## Introduction
The Natal Chart feature is a core component of the Astrology pillar in the IsopGem system, designed to generate and visualize birth charts based on user-provided birth data including date, time, and location. This documentation details the implementation of the natal chart functionality, focusing on the integration between the UI component `natal_chart_window.py`, the `openastro_service` for celestial calculations, and the `chart_storage_service` for persistence. The system handles data flow from input validation through ephemeris lookup to chart rendering, with support for aspect detection, house system configuration, and planetary placement interpretation. The feature integrates with the preferences system for default settings and uses timezone handling via location lookup to address common issues like daylight saving time discrepancies and geolocation accuracy.

## Project Structure
The Natal Chart feature is organized within the astrology pillar of the IsopGem project, following a modular architecture that separates concerns between UI, services, models, and repositories. The core components are located in the `src/pillars/astrology/` directory, with specific subdirectories for UI components, services, models, and repositories. The UI is implemented in the `ui/` subdirectory with `natal_chart_window.py` as the primary interface, while business logic is encapsulated in the `services/` directory with `openastro_service.py` and `chart_storage_service.py`. Data models are defined in `models/` and database interactions are handled by repositories in the `repositories/` directory. This structure enables clear separation of concerns and facilitates maintenance and extension of the feature.

```mermaid
graph TD
subgraph "UI Layer"
A[natal_chart_window.py]
B[astrology_hub.py]
end
subgraph "Service Layer"
C[openastro_service.py]
D[chart_storage_service.py]
E[location_lookup.py]
end
subgraph "Model Layer"
F[chart_models.py]
G[chart_record.py]
end
subgraph "Repository Layer"
H[chart_repository.py]
end
subgraph "Utility Layer"
I[preferences.py]
J[conversions.py]
end
A --> C
A --> D
A --> E
A --> I
C --> F
D --> G
D --> H
C --> J
D --> J
```

**Diagram sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py)
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)
- [conversions.py](file://src/pillars/astrology/utils/conversions.py)

**Section sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py)
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)
- [conversions.py](file://src/pillars/astrology/utils/conversions.py)

## Core Components
The Natal Chart feature consists of several core components that work together to provide a complete birth chart generation and visualization system. The primary UI component is `natal_chart_window.py`, which provides a comprehensive interface for users to input birth data and view chart results. This component integrates with `openastro_service.py` to perform celestial calculations using the OpenAstro2 library, and with `chart_storage_service.py` to persist charts in the database. The system uses data models defined in `chart_models.py` to represent chart data in memory and `chart_record.py` to define the database schema for persistent storage. Utility components like `preferences.py` and `location_lookup.py` provide additional functionality for managing user preferences and geolocation data.

**Section sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)
- [location_lookup.py](file://src/pillars/astrology/services/location_lookup.py)

## Architecture Overview
The Natal Chart feature follows a layered architecture with clear separation between presentation, business logic, and data access layers. The UI layer handles user interaction and display, the service layer orchestrates business logic and external integrations, and the data layer manages persistence. This architecture enables the system to handle the complex data flow required for natal chart generation, from input validation through ephemeris lookup to chart rendering. The system integrates with external services like OpenAstro2 for celestial calculations and Open-Meteo for geolocation lookup, while providing a robust persistence mechanism for storing and retrieving charts.

```mermaid
graph TD
A[User Interface] --> B[Service Layer]
B --> C[External Services]
B --> D[Data Layer]
D --> E[Database]
A --> |Input| B
B --> |Request| C
C --> |Response| B
B --> |Persist| D
D --> |Store| E
B --> |Render| A
```

**Diagram sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py)

## Detailed Component Analysis

### Natal Chart Window Analysis
The `natal_chart_window.py` file implements the primary UI for creating natal charts within the astrology pillar. It provides a comprehensive interface with tabs for configuration and results, allowing users to input birth data including name, date, time, location, and preferences. The window integrates with multiple services to provide location lookup, chart generation, and persistence functionality. It handles user interactions through a series of methods that validate input, generate charts, and manage the display of results. The component also provides functionality for saving and loading charts, viewing SVG visualizations, and managing default locations.

```mermaid
classDiagram
class NatalChartWindow {
+ZODIAC_SIGNS : List[str]
-_service : Optional[OpenAstroService]
-_service_error : Optional[str]
-_last_svg : Optional[str]
-_house_labels : Dict[str, str]
-_temp_svg_files : List[str]
-_location_lookup : LocationLookupService
-_storage_service : ChartStorageService
-_last_request : Optional[ChartRequest]
-_last_result : Optional[ChartResult]
-_preferences : AstrologyPreferences
-_default_location : Optional[DefaultLocation]
-_current_timezone_id : Optional[str]
+__init__(parent : Optional[QWidget])
+_build_ui() void
+_build_input_group() QGroupBox
+_build_action_row() QHBoxLayout
+_build_results_splitter() QSplitter
+_build_planet_group() QGroupBox
+_build_misc_group() QWidget
+_init_service() void
+_generate_chart() void
+_build_request() ChartRequest
+_clear_results() void
+_render_aspects(result : ChartResult) void
+_handle_svg(result : ChartResult) void
+_render_result(result) void
+_render_planets(result) void
+_render_houses(result) void
+_set_status(message : str) void
+_initialize_preferences() void
+_refresh_default_buttons() void
+_use_default_location() void
+_save_default_location() void
+_apply_default_location_fields(location : DefaultLocation, target_dt : Optional[datetime]) void
+_current_form_datetime() datetime
+_offset_for_timezone_id(timezone_id : Optional[str], dt : datetime) Optional[float]
+_generate_current_transit() void
+_tokenize(text : str) List[str]
+_search_location() void
+_select_location_candidate(results : List[LocationResult]) Optional[LocationResult]
+_apply_location_result(result : LocationResult) void
+_populate_from_request(request : ChartRequest) void
+_extract_house_system(request : ChartRequest) Optional[str]
+_save_chart() void
+_load_chart() void
+_prompt_for_chart_choice(matches : List[SavedChartSummary]) Optional[SavedChartSummary]
+_apply_timezone_offset(result : LocationResult) void
+_open_in_browser() void
+_launch_chrome(chrome_path : str, svg_path : str) bool
+_launch_default_browser(svg_path : str) bool
+_find_chrome_binary() Optional[str]
+_cleanup_temp_files() void
+closeEvent(a0 : Optional[QCloseEvent]) void
}
NatalChartWindow --> OpenAstroService : "uses"
NatalChartWindow --> ChartStorageService : "uses"
NatalChartWindow --> LocationLookupService : "uses"
NatalChartWindow --> AstrologyPreferences : "uses"
NatalChartWindow --> ChartRequest : "creates"
NatalChartWindow --> ChartResult : "displays"
```

**Diagram sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [location_lookup.py](file://src/pillars/astrology/services/location_lookup.py)
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)

**Section sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)

### OpenAstro Service Analysis
The `openastro_service.py` file implements a high-level orchestration layer for OpenAstro2 usage, isolating direct dependencies on the external library while providing a clean API surface for the UI. The service handles chart generation by converting user requests into the format expected by OpenAstro2, executing the calculations, and converting the results back into a normalized format. It provides methods for generating charts, listing supported house systems, and accessing default settings. The service includes error handling to wrap low-level exceptions that occur during chart generation, providing meaningful error messages to the user interface.

```mermaid
classDiagram
class OpenAstroService {
+HOUSE_SYSTEM_LABELS : Dict[str, str]
-_logger : Logger
-_default_settings : Dict[str, Any]
-_service : Optional[OpenAstroService]
+__init__(default_settings : Optional[Dict[str, Any]])
+generate_chart(request : ChartRequest) ChartResult
+list_house_systems() Dict[str, str]
+default_settings() Dict[str, Any]
+_build_default_settings() Dict[str, Any]
+_to_openastro_event(event : AstrologyEvent) Dict[str, Any]
+_build_chart_result(chart : Any, request : ChartRequest) ChartResult
+_prime_chart(chart : Any) void
+_planet_data(chart : Any) Dict[str, Dict[str, Any]]
+_extract_planet_positions(chart : Any, planet_data : Dict[str, Dict[str, Any]]) List[PlanetPosition]
+_extract_house_positions(chart : Any) List[HousePosition]
+_extract_aspects(chart : Any) Dict[str, Any]
+_maybe_render_svg(chart : Any, include_svg : bool) Optional[str]
+_extract_raw_payload(chart : Any, planet_data : Dict[str, Dict[str, Any]]) Dict[str, Any]
}
OpenAstroService --> ChartRequest : "processes"
OpenAstroService --> ChartResult : "returns"
OpenAstroService --> AstrologyEvent : "converts"
OpenAstroService --> PlanetPosition : "creates"
OpenAstroService --> HousePosition : "creates"
```

**Diagram sources**
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)

**Section sources**
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)

### Chart Storage Service Analysis
The `chart_storage_service.py` file implements a high-level persistence facade for natal charts, providing methods for saving, loading, and searching charts in the database. The service uses a repository pattern to separate the business logic from the data access layer, with `ChartRepository` handling the direct database interactions. It provides methods for saving charts with associated metadata, listing recent charts, searching charts by text or tags, and loading specific charts by ID. The service handles serialization and deserialization of chart data, converting between in-memory objects and database records.

```mermaid
classDiagram
class ChartStorageService {
-_session_factory : ChartSessionFactory
+save_chart(name : str, request : ChartRequest, result : ChartResult, categories : Sequence[str], tags : Sequence[str], description : Optional[str]) int
+list_recent(limit : int) List[SavedChartSummary]
+search(text : Optional[str], categories : Optional[Sequence[str]], tags : Optional[Sequence[str]], limit : int) List[SavedChartSummary]
+load_chart(chart_id : int) Optional[LoadedChart]
+_serialize_request(request : ChartRequest) Dict[str, object]
+_deserialize_request(payload : Dict[str, object]) ChartRequest
+_serialize_event(event : AstrologyEvent) Dict[str, object]
+_deserialize_event(payload : Dict[str, object]) AstrologyEvent
+_extract_house_system(request : ChartRequest) Optional[str]
+_to_summary(record : AstrologyChart) SavedChartSummary
}
ChartStorageService --> ChartRepository : "uses"
ChartStorageService --> ChartRequest : "serializes"
ChartStorageService --> ChartResult : "serializes"
ChartStorageService --> SavedChartSummary : "returns"
ChartStorageService --> LoadedChart : "returns"
```

**Diagram sources**
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)

**Section sources**
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)

### Data Models Analysis
The `chart_models.py` file defines the core data models used throughout the Natal Chart feature, providing a consistent representation of chart data across the system. These models use Python dataclasses to define structured data with type hints, ensuring type safety and clarity. The models include `GeoLocation` for geographic coordinates, `AstrologyEvent` for event descriptors, `ChartRequest` for user requests, `PlanetPosition` and `HousePosition` for celestial positions, and `ChartResult` for the final chart output. These models serve as the contract between different components of the system, ensuring consistent data representation.

```mermaid
classDiagram
class GeoLocation {
+name : str
+latitude : float
+longitude : float
+elevation : float
+country_code : Optional[str]
+__post_init__() void
}
class AstrologyEvent {
+name : str
+timestamp : datetime
+location : GeoLocation
+timezone_offset : Optional[float]
+metadata : Dict[str, Any]
+resolved_timezone_offset() float
+to_openastro_kwargs() Dict[str, Any]
}
class ChartRequest {
+primary_event : AstrologyEvent
+chart_type : str
+reference_event : Optional[AstrologyEvent]
+include_svg : bool
+settings : Optional[Dict[str, Any]]
}
class PlanetPosition {
+name : str
+degree : float
+sign_index : Optional[int]
}
class HousePosition {
+number : int
+degree : float
}
class ChartResult {
+chart_type : str
+planet_positions : List[PlanetPosition]
+house_positions : List[HousePosition]
+aspect_summary : Dict[str, Any]
+svg_document : Optional[str]
+raw_payload : Dict[str, Any]
+has_svg() bool
+to_dict() Dict[str, Any]
+_serialize_dataclass(instance : Any) Dict[str, Any]
}
AstrologyEvent --> GeoLocation : "contains"
ChartRequest --> AstrologyEvent : "contains"
ChartResult --> PlanetPosition : "contains"
ChartResult --> HousePosition : "contains"
```

**Diagram sources**
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)

**Section sources**
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)

### Chart Record Analysis
The `chart_record.py` file defines the SQLAlchemy models used for persisting astrology charts in the database. These models define the schema for storing chart data, including the main `AstrologyChart` table and related tables for categories and tags. The models use SQLAlchemy's ORM features to define relationships between tables, with foreign keys and join tables to handle many-to-many relationships. The models include fields for chart metadata, event details, and serialized request and result data, allowing complete chart information to be stored and retrieved.

```mermaid
erDiagram
AstrologyChart ||--o{ ChartCategory : "has"
AstrologyChart ||--o{ ChartTag : "has"
AstrologyChart {
int id PK
string name
text description
string chart_type
boolean include_svg
string house_system
datetime event_timestamp
float timezone_offset
string location_label
float latitude
float longitude
float elevation
json request_payload
json result_payload
datetime created_at
datetime updated_at
}
ChartCategory {
int id PK
string name UK
}
ChartTag {
int id PK
string name UK
}
chart_category_links {
int chart_id FK
int category_id FK
}
chart_tag_links {
int chart_id FK
int tag_id FK
}
```

**Diagram sources**
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)

**Section sources**
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)

### Preferences System Analysis
The `preferences.py` file implements a simple JSON-backed preference store for the astrology pillar, allowing users to save and retrieve default location settings. The system uses a `DefaultLocation` dataclass to represent location preferences and an `AstrologyPreferences` class to manage reading and writing preferences to a JSON file. This enables users to save their default location once and use it for multiple chart generations, improving usability and reducing input errors. The preferences are stored in a file within the application's data directory, with automatic creation of the directory if it doesn't exist.

```mermaid
classDiagram
class DefaultLocation {
+name : str
+latitude : float
+longitude : float
+elevation : float
+timezone_offset : float
+timezone_id : Optional[str]
}
class AstrologyPreferences {
-_path : Path
+load_default_location() Optional[DefaultLocation]
+save_default_location(location : DefaultLocation) None
+_read() Dict[str, Any]
+_write(payload : Dict[str, Any]) None
}
AstrologyPreferences --> DefaultLocation : "manages"
```

**Diagram sources**
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)

**Section sources**
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)

### Location Lookup Service Analysis
The `location_lookup.py` file implements a service for querying the Open-Meteo geocoding API to obtain coordinates for city names. This service allows users to search for locations by name and select from a list of matching results, improving accuracy and reducing input errors. The service handles network requests to the geocoding API, parses the response, and returns a list of `LocationResult` objects with coordinates, elevation, and timezone information. This integration enables automatic timezone detection based on location, addressing common issues with manual timezone input.

```mermaid
classDiagram
class LocationResult {
+name : str
+latitude : float
+longitude : float
+country : Optional[str]
+admin1 : Optional[str]
+elevation : Optional[float]
+timezone_id : Optional[str]
+label : str
}
class LocationLookupService {
+API_URL : str
-_session : requests.Session
+search(query : str, count : int, language : str) List[LocationResult]
+_safe_float(value : Optional[float]) Optional[float]
}
LocationLookupService --> LocationResult : "returns"
```

**Diagram sources**
- [location_lookup.py](file://src/pillars/astrology/services/location_lookup.py)

**Section sources**
- [location_lookup.py](file://src/pillars/astrology/services/location_lookup.py)

### Conversions Utility Analysis
The `conversions.py` file provides utility functions for converting between different coordinate systems and formatting astronomical data for display. The primary function `to_zodiacal_string` converts absolute degrees (0-360) to zodiacal degree notation (Deg Sign Min), which is the standard format used in astrology. This function takes a degree value and returns a formatted string showing the degree, sign name, and minutes, making it easier for users to interpret planetary positions. The function uses a lookup table of zodiac signs to determine the appropriate sign name based on the degree value.

```mermaid
flowchart TD
A[Input Degree] --> B{Normalize to 0-360}
B --> C[Calculate Sign Index]
C --> D[Calculate Sign Remainder]
D --> E[Extract Degrees]
E --> F[Calculate Minutes]
F --> G[Get Sign Name]
G --> H[Format Output String]
H --> I[Return Formatted String]
```

**Diagram sources**
- [conversions.py](file://src/pillars/astrology/utils/conversions.py)

**Section sources**
- [conversions.py](file://src/pillars/astrology/utils/conversions.py)

## Dependency Analysis
The Natal Chart feature has a well-defined dependency structure that follows the dependency inversion principle, with higher-level modules depending on abstractions rather than concrete implementations. The UI component `natal_chart_window.py` depends on service interfaces rather than directly on external libraries, allowing for easier testing and maintenance. The service layer depends on data models and external APIs, while the data layer depends on the database schema and ORM. This structure enables the system to be modular and extensible, with clear boundaries between components.

```mermaid
graph TD
A[natal_chart_window.py] --> B[openastro_service.py]
A --> C[chart_storage_service.py]
A --> D[location_lookup.py]
A --> E[preferences.py]
B --> F[chart_models.py]
C --> G[chart_record.py]
C --> H[chart_repository.py]
D --> I[requests]
E --> J[json]
F --> K[dataclasses]
G --> L[SQLAlchemy]
H --> M[SQLAlchemy]
```

**Diagram sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [location_lookup.py](file://src/pillars/astrology/services/location_lookup.py)
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py)

**Section sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [location_lookup.py](file://src/pillars/astrology/services/location_lookup.py)
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py)

## Performance Considerations
The Natal Chart feature is designed with performance in mind, minimizing unnecessary computations and optimizing data access patterns. The system uses efficient data structures and algorithms for handling chart data, with dataclasses providing fast attribute access and JSON serialization for persistence. The service layer caches frequently accessed data, such as house system labels, to reduce redundant computations. Database queries are optimized with appropriate indexing and query patterns, with recent charts loaded in descending order of event timestamp. Network requests are handled asynchronously where possible, with timeouts and error handling to prevent UI blocking. The system also includes mechanisms for cleaning up temporary files, such as SVG files created for browser viewing, to prevent disk space issues.

## Troubleshooting Guide
Common issues with the Natal Chart feature typically relate to external dependencies, configuration, or data input. If OpenAstro2 is not available, the system will display an error message indicating that the library needs to be installed. Geolocation lookup issues may occur if the Open-Meteo API is unreachable or returns no results, which can be addressed by checking network connectivity or trying alternative search terms. Timezone discrepancies can occur due to daylight saving time rules or incorrect location input, which can be mitigated by using the location lookup service to automatically detect timezone information. Database issues may arise from file permissions or schema mismatches, which can be resolved by checking the database file location and running any necessary migration scripts. Users experiencing issues with chart generation should verify their input data, particularly the date, time, and location, and ensure that the OpenAstro2 library is properly installed and configured.

**Section sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [location_lookup.py](file://src/pillars/astrology/services/location_lookup.py)

## Conclusion
The Natal Chart feature provides a comprehensive system for generating and visualizing birth charts based on user-provided birth data. The implementation follows a clean, modular architecture with clear separation of concerns between UI, services, models, and data access layers. The system integrates with external services for celestial calculations and geolocation lookup, while providing robust persistence for chart data. The feature includes extensive error handling and user feedback mechanisms to ensure a smooth user experience. While the current implementation does not show direct integration with gematria values and TQ systems for cross-pillar analysis, the architecture is extensible and could support such integrations in the future through additional service components or data model extensions.