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
</cite>

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
The Astrology pillar of the isopgem application serves as a comprehensive astrological analysis platform that integrates with external calculation engines OpenAstro2 and pyswisseph for precise celestial calculations. This documentation provides a detailed architectural overview of the system, focusing on its component structure, data flow, user interface elements, and integration points. The pillar enables users to generate natal charts, analyze planetary positions, visualize transit patterns, and explore specialized astrological phenomena such as the Venus Rose. The system handles complex astronomical calculations while providing intuitive interfaces for both novice and advanced users.

## Core Components
The Astrology pillar consists of several key components that work together to provide a complete astrological analysis environment. The main interface is the astrology_hub, which serves as the central launcher for all astrology tools. The chart_storage_service manages the persistence of astrological charts, allowing users to save, retrieve, and organize their analyses. The chart_record model represents the core data structure for storing astrological information, including planetary positions, house cusps, and aspect data. The openastro_service acts as an integration layer between the application and the external OpenAstro2 calculation engine, handling the complex mathematical computations required for accurate astrological predictions.

**Section sources**
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)

## Architecture Overview
The Astrology pillar follows a layered architecture with clear separation between user interface, business logic, and data persistence layers. The system is designed around a service-oriented approach where specialized services handle specific aspects of astrological computation and data management.

```mermaid
graph TD
subgraph "User Interface"
A[astrology_hub]
B[natal_chart_window]
C[current_transit_window]
D[planetary_positions_window]
E[venus_rose_window]
end
subgraph "Service Layer"
F[openastro_service]
G[chart_storage_service]
H[location_lookup]
end
subgraph "Data Layer"
I[chart_repository]
J[chart_record]
K[preferences]
end
subgraph "External Systems"
L[OpenAstro2]
M[pyswisseph]
N[Open-Meteo Geocoding API]
end
A --> F
B --> F
C --> F
D --> F
E --> F
B --> G
C --> G
D --> G
F --> L
F --> M
H --> N
G --> I
I --> J
G --> K
H --> K
```

**Diagram sources **
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)
- [location_lookup.py](file://src/pillars/astrology/services/location_lookup.py)

## Detailed Component Analysis

### astrology_hub Analysis
The astrology_hub serves as the main interface for the Astrology pillar, providing a centralized launch point for all astrological tools. It presents users with a clean interface that includes buttons for accessing the natal chart generator, current transit viewer, planetary positions table, Neo-Aubrey Eclipse Clock, and the Cytherean Rose visualization.

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
}
class WindowManager {
+open_window(window_id, window_class, allow_multiple)
}
AstrologyHub --> WindowManager : "uses"
```

**Diagram sources **
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)

### chart_storage_service Analysis
The chart_storage_service provides a high-level persistence facade for natal charts, handling the storage and retrieval of astrological data. It works in conjunction with the chart_repository to manage database operations while providing a clean API for other components.

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

**Diagram sources **
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py)

### chart_record Analysis
The chart_record module defines the SQLAlchemy models for persisting astrology charts in the database. It includes the main AstrologyChart entity along with supporting entities for categories and tags, enabling rich organization and filtering of stored charts.

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

**Diagram sources **
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)

### openastro_service Analysis
The openastro_service acts as a high-level orchestration layer for OpenAstro2 usage, isolating direct dependencies on the external library while providing a clean API surface for the UI components. It handles chart generation, house system management, and error handling.

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

**Diagram sources **
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)

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

**Diagram sources **
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

**Diagram sources **
- [current_transit_window.py](file://src/pillars/astrology/ui/current_transit_window.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)

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

**Diagram sources **
- [venus_rose_window.py](file://src/pillars/astrology/ui/venus_rose_window.py)

**Section sources**
- [venus_rose_window.py](file://src/pillars/astrology/ui/venus_rose_window.py)

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
```

**Diagram sources **
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)

**Section sources**
- [preferences.py](file://src/pillars/astrology/utils/preferences.py)
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [current_transit_window.py](file://src/pillars/astrology/ui/current_transit_window.py)
- [planetary_positions_window.py](file://src/pillars/astrology/ui/planetary_positions_window.py)

## Connection to Esoteric Analysis
The Astrology pillar connects to broader esoteric analysis through planetary correspondences in gematria and TQ systems. These connections are facilitated through shared data models and integration points that allow astrological data to be used in conjunction with other esoteric calculations.

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
```

**Diagram sources **
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)

**Section sources**
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)

## Conclusion
The Astrology pillar of the isopgem application provides a robust and comprehensive platform for astrological analysis, integrating external calculation engines OpenAstro2 and pyswisseph to deliver accurate celestial calculations. The system's architecture features a clear separation of concerns with well-defined components for user interface, service logic, and data persistence. Key features include natal chart generation, transit analysis, planetary position tracking, and specialized visualizations like the Venus Rose. The integration with user preferences allows for personalized settings, while the connection to broader esoteric analysis systems enables holistic interpretation of astrological data. The pillar demonstrates a sophisticated approach to handling complex astronomical calculations while maintaining an accessible user interface for both novice and advanced practitioners.