# Astrology Chart Canvas

<cite>
**Referenced Files in This Document**
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [openastro_service.py](file://src/pillars/astrology/services/openastro_service.py)
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py)
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)
- [conversions.py](file://src/pillars/astrology/utils/conversions.py)
- [README.md](file://README.md)
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
This document explains the Astrology Chart Canvas, a custom in-app renderer for natal and transit charts. It focuses on how the canvas receives data from the astrology pipeline, how it renders the zodiac ring, houses, planets, and aspects, and how it integrates with the rest of the Astrology pillar (OpenAstro2 integration, persistence, and UI).

The canvas is implemented as a PyQt6 widget that draws celestial positions using vector graphics, with interactive hover feedback and aspect highlighting.

## Project Structure
The Astrology Chart Canvas lives in the Astrology pillar’s UI layer and is used by the Natal Chart window. It consumes normalized chart data from the astrology models and is driven by the OpenAstro2 service.

```mermaid
graph TB
subgraph "Astrology UI"
NC["NatalChartWindow<br/>src/pillars/astrology/ui/natal_chart_window.py"]
CC["ChartCanvas<br/>src/pillars/astrology/ui/chart_canvas.py"]
end
subgraph "Astrology Services"
OAS["OpenAstroService<br/>src/pillars/astrology/services/openastro_service.py"]
CSS["ChartStorageService<br/>src/pillars/astrology/services/chart_storage_service.py"]
end
subgraph "Astrology Models"
CM["Chart Models<br/>src/pillars/astrology/models/chart_models.py"]
CR["Chart Records<br/>src/pillars/astrology/models/chart_record.py"]
end
subgraph "Repositories"
CRP["ChartRepository<br/>src/pillars/astrology/repositories/chart_repository.py"]
end
NC --> OAS
NC --> CC
NC --> CSS
CSS --> CRP
CRP --> CR
OAS --> CM
CC --> CM
```

**Diagram sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py#L232-L246)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L1-L120)
- [openastro_service.py](file://src/pillars.astrology/services/openastro_service.py#L64-L94)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py#L48-L82)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py#L85-L112)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py#L37-L60)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py#L21-L60)

**Section sources**
- [README.md](file://README.md#L13-L24)
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py#L232-L246)

## Core Components
- ChartCanvas: A PyQt6 QWidget that renders the chart. It accepts lists of PlanetPosition and HousePosition and draws:
  - Background gradient
  - Zodiac ring with sign markers
  - House cusps and labels
  - Planetary orbs with glyphs and glow
  - Aspect lines from the hovered planet to others
  - Hover tooltips and cursor changes
- Chart models: PlanetPosition and HousePosition define the data contract for rendering.
- OpenAstroService: Produces ChartResult with normalized positions and optional SVG.
- ChartStorageService and ChartRepository: Persist and load chart requests/results with categories/tags.

**Section sources**
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L1-L120)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py#L85-L112)
- [openastro_service.py](file://src/pillars.astrology/services/openastro_service.py#L64-L94)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py#L48-L82)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py#L21-L60)

## Architecture Overview
The Natal Chart window orchestrates user input, builds a ChartRequest, calls OpenAstroService to compute a ChartResult, and then updates both the tabular report and the ChartCanvas.

```mermaid
sequenceDiagram
participant User as "User"
participant NC as "NatalChartWindow"
participant OAS as "OpenAstroService"
participant CC as "ChartCanvas"
User->>NC : "Click Generate"
NC->>NC : "_build_request()"
NC->>OAS : "generate_chart(request)"
OAS-->>NC : "ChartResult"
NC->>NC : "_render_result(result)"
NC->>CC : "set_data(planet_positions, house_positions)"
CC->>CC : "mouseMoveEvent() / paintEvent()"
CC-->>User : "Interactive chart with hover and aspect lines"
```

**Diagram sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py#L432-L461)
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py#L512-L519)
- [openastro_service.py](file://src/pillars.astrology/services/openastro_service.py#L64-L94)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L100-L135)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L145-L188)

## Detailed Component Analysis

### ChartCanvas: Rendering Pipeline
ChartCanvas is a stateful widget that:
- Receives normalized positions via set_data
- Filters and prioritizes planetary bodies
- Computes hitboxes for hover detection
- Renders in layers: background, houses, zodiac ring, planets, center decoration
- Draws aspect lines from the hovered planet to others
- Formats tooltips with zodiacal degree strings

Key behaviors:
- Data filtering: Only major bodies are shown; “True Node” supersedes “Mean Node”
- Angle mapping: Aligns House I to the left (9 o'clock) relative to the first house cusp
- Aspect detection: Compares angular separation against fixed orbs and draws colored lines
- Hover feedback: Updates tooltip, cursor, and highlights glow and label size for the hovered body

```mermaid
flowchart TD
Start(["paintEvent"]) --> ResetHB["Reset hitboxes"]
ResetHB --> BaseAngle["Compute base_cusp from first house"]
BaseAngle --> Houses["Draw houses and cusp markers"]
Houses --> Aspects{"Hovered planet?"}
Aspects --> |Yes| DrawAsp["Draw aspect lines to other planets"]
Aspects --> |No| SkipAsp["Skip aspect lines"]
DrawAsp --> Zodiac["Draw zodiac ring and sign dividers"]
SkipAsp --> Zodiac
Zodiac --> Planets["Draw planets with glyphs and glow"]
Planets --> Center["Draw center decoration"]
Center --> End(["Done"])
```

**Diagram sources**
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L145-L188)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L171-L183)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L358-L414)

**Section sources**
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L72-L99)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L100-L135)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L145-L188)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L195-L245)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L246-L306)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L307-L357)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L358-L414)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L415-L450)

### Data Models: PlanetPosition and HousePosition
These models carry the minimal data needed for rendering:
- PlanetPosition: name, degree, optional sign_index
- HousePosition: number, degree

They are populated by OpenAstroService and consumed by ChartCanvas and UI tables.

**Section sources**
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py#L85-L112)

### OpenAstroService: Chart Computation
OpenAstroService wraps OpenAstro2, converting AstrologyEvent to OpenAstro events, computing charts, extracting positions, houses, aspects, and optionally SVG. It validates house systems and exposes default settings.

```mermaid
classDiagram
class OpenAstroService {
+generate_chart(request) ChartResult
+list_house_systems() Dict
+default_settings() Dict
-_to_openastro_event(event) Dict
-_build_chart_result(chart, request) ChartResult
-_prime_chart(chart) void
-_extract_planet_positions(chart, planet_data) PlanetPosition[]
-_extract_house_positions(chart) HousePosition[]
-_extract_aspects(chart) Dict
-_maybe_render_svg(chart, include_svg) str?
-_extract_raw_payload(chart, planet_data) Dict
}
```

**Diagram sources**
- [openastro_service.py](file://src/pillars.astrology/services/openastro_service.py#L64-L94)
- [openastro_service.py](file://src/pillars.astrology/services/openastro_service.py#L124-L139)
- [openastro_service.py](file://src/pillars.astrology/services/openastro_service.py#L164-L201)
- [openastro_service.py](file://src/pillars.astrology/services/openastro_service.py#L203-L213)
- [openastro_service.py](file://src/pillars.astrology/services/openastro_service.py#L214-L236)
- [openastro_service.py](file://src/pillars.astrology/services/openastro_service.py#L237-L254)

**Section sources**
- [openastro_service.py](file://src/pillars.astrology/services/openastro_service.py#L31-L63)
- [openastro_service.py](file://src/pillars.astrology/services/openastro_service.py#L64-L94)

### Persistence: ChartStorageService and ChartRepository
ChartStorageService serializes/deserializes ChartRequest and ChartResult for persistence. ChartRepository handles creation, listing recent charts, and text/category/tag search.

```mermaid
classDiagram
class ChartStorageService {
+save_chart(name, request, result, categories, tags, description) int
+list_recent(limit) SavedChartSummary[]
+search(text, categories, tags, limit) SavedChartSummary[]
+load_chart(chart_id) LoadedChart?
-_serialize_request(request) Dict
-_deserialize_request(payload) ChartRequest
-_serialize_event(event) Dict
-_deserialize_event(payload) AstrologyEvent
-_extract_house_system(request) str?
-_to_summary(record) SavedChartSummary
}
class ChartRepository {
+create_chart(...)
+get_chart(chart_id) AstrologyChart?
+list_recent(limit) AstrologyChart[]
+search(text, categories, tags, limit) AstrologyChart[]
-_resolve_categories(names) ChartCategory[]
-_resolve_tags(names) ChartTag[]
-_resolve_terms(model, names) List
}
ChartStorageService --> ChartRepository : "uses"
```

**Diagram sources**
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py#L48-L116)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py#L21-L107)

**Section sources**
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py#L19-L47)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py#L12-L20)

### UI Integration: NatalChartWindow
NatalChartWindow wires the OpenAstroService, renders tabular results, and feeds ChartCanvas with normalized positions. It also manages persistence and default locations.

```mermaid
sequenceDiagram
participant NC as "NatalChartWindow"
participant OAS as "OpenAstroService"
participant CC as "ChartCanvas"
NC->>OAS : "generate_chart(request)"
OAS-->>NC : "ChartResult"
NC->>NC : "_render_planets/_render_houses/_render_aspects"
NC->>CC : "set_data(planet_positions, house_positions)"
CC-->>NC : "hover updates via mouseMoveEvent"
```

**Diagram sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py#L432-L461)
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py#L512-L519)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L100-L135)

**Section sources**
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py#L232-L246)
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py#L432-L461)
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py#L512-L519)

## Dependency Analysis
- ChartCanvas depends on:
  - PyQt6 for rendering and input handling
  - Chart models for data
  - Conversion utilities for zodiacal formatting
- NatalChartWindow depends on:
  - OpenAstroService for computation
  - ChartCanvas for visualization
  - ChartStorageService for persistence
- OpenAstroService depends on:
  - OpenAstro2 library (import guarded)
  - Astrology models for data conversion
- ChartStorageService depends on:
  - SQLAlchemy ORM models and repository for persistence

```mermaid
graph LR
CC["ChartCanvas"] --> CM["PlanetPosition/HousePosition"]
NC["NatalChartWindow"] --> CC
NC --> OAS["OpenAstroService"]
OAS --> CM
CSS["ChartStorageService"] --> CRP["ChartRepository"]
CRP --> CR["AstrologyChart/Category/Tag"]
```

**Diagram sources**
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L1-L120)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py#L85-L112)
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py#L232-L246)
- [openastro_service.py](file://src/pillars.astrology/services/openastro_service.py#L64-L94)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py#L48-L82)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py#L21-L60)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py#L37-L60)

**Section sources**
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L1-L120)
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py#L232-L246)
- [openastro_service.py](file://src/pillars.astrology/services/openastro_service.py#L64-L94)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py#L48-L82)
- [chart_repository.py](file://src/pillars/astrology/repositories/chart_repository.py#L21-L60)
- [chart_record.py](file://src/pillars/astrology/models/chart_record.py#L37-L60)

## Performance Considerations
- Rendering cost scales with the number of planets and houses; the canvas uses simple hitbox rectangles and avoids expensive operations in the paint loop.
- Aspect line drawing recalculates positions for hovered planet; this is acceptable for small datasets but could be optimized by caching positions if performance becomes a concern.
- Antialiasing is enabled for smooth visuals; keep the widget size reasonable to avoid excessive GPU/CPU work.
- Consider batching updates and deferring expensive operations off the UI thread if integrating with larger datasets.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
Common issues and resolutions:
- OpenAstro2 not installed: The service raises a specific error when the dependency is missing. The UI disables the Generate button and shows a warning.
- No chart data: Ensure set_data is called with non-empty lists; otherwise, the canvas clears and no hover feedback occurs.
- Hover not responding: Verify mouse tracking is enabled and that hitboxes are being built in paintEvent.
- Incorrect house alignment: Confirm the first house cusp is passed; the canvas rotates so House I aligns to the left.
- Aspect lines not appearing: Hover a planet and ensure the difference angles fall within the defined orbs.

**Section sources**
- [openastro_service.py](file://src/pillars.astrology/services/openastro_service.py#L23-L30)
- [natal_chart_window.py](file://src/pillars/astrology/ui/natal_chart_window.py#L432-L461)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L100-L135)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L145-L188)
- [chart_canvas.py](file://src/pillars/astrology/ui/chart_canvas.py#L358-L414)

## Conclusion
The Astrology Chart Canvas provides a fast, interactive, and visually rich rendering of natal and transit charts. It integrates tightly with the OpenAstroService for computation and the persistence layer for saving/loading chart definitions. Its layered design keeps rendering logic isolated and testable, while the UI remains responsive and user-friendly.

[No sources needed since this section summarizes without analyzing specific files]