# Core Modules

<cite>
**Referenced Files in This Document**   
- [main.py](file://src/main.py)
- [gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py)
- [calculation_service.py](file://src/pillars/gematria/services/calculation_service.py)
- [calculation_record.py](file://src/pillars/gematria/models/calculation_record.py)
- [sqlite_calculation_repository.py](file://src/pillars/gematria/repositories/sqlite_calculation_repository.py)
- [geometry_hub.py](file://src/pillars/geometry/ui/geometry_hub.py)
- [solid_geometry.py](file://src/pillars/geometry/services/solid_geometry.py)
- [document_manager_hub.py](file://src/pillars/document_manager/ui/document_manager_hub.py)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py)
- [document.py](file://src/pillars/document_manager/models/document.py)
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py)
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)
- [tq_hub.py](file://src/pillars/tq/ui/tq_hub.py)
- [kamea_grid_service.py](file://src/pillars/tq/services/kamea_grid_service.py)
- [quadset_engine.py](file://src/pillars/tq/services/quadset_engine.py)
- [adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)
</cite>

## Table of Contents
1. [Gematria](#gematria)
2. [Geometry](#geometry)
3. [Document Manager](#document-manager)
4. [Astrology](#astrology)
5. [TQ](#tq)
6. [Adyton](#adyton)

## Gematria

The Gematria module serves as the primary numerical analysis engine within IsopGem, providing comprehensive tools for calculating and analyzing gematria values across Hebrew, Greek, and English systems. This module is designed for researchers and practitioners of esoteric traditions who require detailed numerical analysis of texts and phrases.

### Purpose and Key Features
The Gematria pillar enables users to perform various types of gematria calculations, including standard, ordinal, reduced, and specialized methods like AtBash and Albam for Hebrew, and digital, reverse substitution, and pair matching for Greek. The module supports saving calculations for future reference, batch processing of multiple texts, and detailed text analysis with statistical breakdowns.

Key features include:
- **Multiple Calculation Methods**: Support for over 30 different gematria systems across Hebrew, Greek, and English/TQ traditions
- **Persistent Storage**: Saved calculations with metadata including notes, sources, tags, and user ratings
- **Text Analysis Tools**: Comprehensive analysis of texts with breakdowns of individual character values
- **Batch Processing**: Ability to process multiple texts simultaneously
- **Database Management**: Tools for managing and organizing calculation records

### Architectural Structure
The Gematria module follows a clean layered architecture with distinct separation between UI, services, repositories, and models:

```mermaid
graph TD
A[GematriaHub] --> B[GematriaCalculatorWindow]
A --> C[SavedCalculationsWindow]
A --> D[BatchCalculatorWindow]
A --> E[TextAnalysisWindow]
A --> F[DatabaseToolsWindow]
A --> G[MethodsReferenceWindow]
B --> H[CalculationService]
C --> H
D --> H
E --> H
F --> H
G --> H
H --> I[SQLiteCalculationRepository]
I --> J[CalculationEntity]
H --> K[CalculationRecord]
```

**Diagram sources**
- [gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py)
- [calculation_service.py](file://src/pillars/gematria/services/calculation_service.py)
- [sqlite_calculation_repository.py](file://src/pillars/gematria/repositories/sqlite_calculation_repository.py)
- [calculation_record.py](file://src/pillars/gematria/models/calculation_record.py)

### Service Interfaces
The core service interface is provided by the `CalculationService` class, which manages all operations related to gematria calculations:

```mermaid
classDiagram
class CalculationService {
+save_calculation(text : str, value : int, calculator : GematriaCalculator, breakdown : List[tuple], notes : str, source : str, tags : List[str], category : str, user_rating : int, is_favorite : bool) CalculationRecord
+update_calculation(record_id : str, notes : Optional[str], source : Optional[str], tags : Optional[List[str]], category : Optional[str], user_rating : Optional[int], is_favorite : Optional[bool]) Optional[CalculationRecord]
+delete_calculation(record_id : str) bool
+get_calculation(record_id : str) Optional[CalculationRecord]
+search_calculations(query : Optional[str], language : Optional[str], value : Optional[int], tags : Optional[List[str]], favorites_only : bool, limit : int, page : int, summary_only : bool) List[CalculationRecord]
+get_all_calculations(limit : int) List[CalculationRecord]
+get_calculations_by_value(value : int) List[CalculationRecord]
+get_favorite_calculations() List[CalculationRecord]
+toggle_favorite(record_id : str) Optional[CalculationRecord]
+get_breakdown_from_record(record : CalculationRecord) List[tuple]
}
class CalculationRepository {
+save(record : CalculationRecord) CalculationRecord
+get_by_id(record_id : str) Optional[CalculationRecord]
+delete(record_id : str) bool
+search(query_str : Optional[str], language : Optional[str], value : Optional[int], tags : Optional[Sequence[str]], favorites_only : bool, limit : int, page : int, summary_only : bool) List[CalculationRecord]
+get_all(limit : int) List[CalculationRecord]
+get_by_value(value : int, limit : int) List[CalculationRecord]
+get_favorites(limit : int) List[CalculationRecord]
+get_by_tags(tags : List[str], limit : int) List[CalculationRecord]
}
class SQLiteCalculationRepository {
+save(record : CalculationRecord) CalculationRecord
+get_by_id(record_id : str) Optional[CalculationRecord]
+delete(record_id : str) bool
+search(query_str : Optional[str], language : Optional[str], value : Optional[int], tags : Optional[Sequence[str]], favorites_only : bool, limit : int, page : int, summary_only : bool) List[CalculationRecord]
+get_all(limit : int) List[CalculationRecord]
+get_by_value(value : int, limit : int) List[CalculationRecord]
+get_favorites(limit : int) List[CalculationRecord]
+get_by_tags(tags : List[str], limit : int) List[CalculationRecord]
}
class CalculationRecord {
+text : str
+value : int
+language : str
+method : str
+id : Optional[str]
+date_created : datetime
+date_modified : datetime
+notes : str
+source : str
+tags : List[str]
+breakdown : str
+character_count : int
+normalized_text : str
+user_rating : int
+is_favorite : bool
+category : str
+related_ids : List[str]
+to_dict() Dict
+from_dict(data : Dict) CalculationRecord
+__str__() str
}
CalculationService --> CalculationRepository : "uses"
CalculationRepository <|-- SQLiteCalculationRepository : "implements"
CalculationService --> CalculationRecord : "creates"
```

**Diagram sources**
- [calculation_service.py](file://src/pillars/gematria/services/calculation_service.py)
- [sqlite_calculation_repository.py](file://src/pillars/gematria/repositories/sqlite_calculation_repository.py)
- [calculation_record.py](file://src/pillars/gematria/models/calculation_record.py)

### User Interaction Patterns
Users interact with the Gematria module through the Gematria Hub, which provides access to various tools:

1. **Gematria Calculator**: The primary interface for performing calculations on single texts
2. **Saved Calculations**: Browser for viewing and managing previously saved calculations
3. **Batch Calculator**: Tool for processing multiple texts simultaneously
4. **Text Analysis**: Advanced analysis of texts with statistical breakdowns
5. **Database Tools**: Utilities for managing the calculation database
6. **Methods Reference**: Documentation and reference for different calculation methods

Each tool is launched as a separate window from the hub, allowing users to work with multiple tools simultaneously.

### Configuration and Customization
The Gematria module supports several customization options:
- **User-defined categories**: Organize calculations into custom categories
- **Tagging system**: Apply multiple tags to calculations for flexible organization
- **Rating system**: Rate calculations from 0-5 stars for prioritization
- **Favorite marking**: Mark important calculations as favorites for quick access
- **Source references**: Link calculations to specific sources or references

### Troubleshooting Guidance
Common issues and solutions:
- **Calculation not saving**: Ensure the database connection is active and the application has write permissions to the data directory
- **Search not returning expected results**: Verify that the search index is up to date; use the database tools to rebuild the index if necessary
- **Performance issues with large datasets**: Use filters to narrow down searches and avoid loading all calculations at once
- **Missing calculation methods**: Check that all required calculator classes are properly imported in the hub module

**Section sources**
- [gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py)
- [calculation_service.py](file://src/pillars/gematria/services/calculation_service.py)
- [calculation_record.py](file://src/pillars/gematria/models/calculation_record.py)
- [sqlite_calculation_repository.py](file://src/pillars/gematria/repositories/sqlite_calculation_repository.py)

## Geometry

The Geometry module provides comprehensive tools for analyzing and visualizing 2D and 3D geometric forms, with a focus on sacred geometry and mathematical relationships. This module serves as a powerful calculator and visualization platform for geometric shapes and solids.

### Purpose and Key Features
The Geometry pillar enables users to calculate properties of various geometric shapes and solids, from basic 2D forms to complex 3D polyhedra. The module supports both calculation and visualization, allowing users to explore geometric relationships in depth.

Key features include:
- **2D Shape Calculations**: Support for circles, ellipses, annuli, crescents, triangles, quadrilaterals, and regular polygons
- **3D Solid Calculations**: Comprehensive support for Platonic solids, Archimedean solids, pyramids, prisms, and antiprisms
- **3D Visualization**: Interactive 3D viewer for visualizing solids with rotation, zoom, and pan controls
- **Advanced Calculators**: Specialized tools for polygonal numbers, figurate numbers, and experimental star patterns
- **Scientific Calculator**: Advanced calculator with support for geometric functions

### Architectural Structure
The Geometry module follows a modular architecture with clear separation between UI components, service layers, and mathematical calculations:

```mermaid
graph TD
A[GeometryHub] --> B[GeometryCalculatorWindow]
A --> C[PolygonalNumberWindow]
A --> D[ExperimentalStarWindow]
A --> E[Figurate3DWindow]
A --> F[AdvancedScientificCalculatorWindow]
A --> G[Geometry3DWindow]
B --> H[Shape Services]
C --> I[PolygonalNumberService]
D --> J[StarPatternService]
E --> K[Figurate3DService]
F --> L[ScientificCalculatorService]
G --> M[Solid Services]
G --> N[SolidGeometry]
G --> O[Geometry3DView]
```

**Diagram sources**
- [geometry_hub.py](file://src/pillars/geometry/ui/geometry_hub.py)
- [solid_geometry.py](file://src/pillars/geometry/services/solid_geometry.py)

### Service Interfaces
The core functionality is provided by various service classes that handle specific types of geometric calculations:

```mermaid
classDiagram
class GeometryHub {
+_open_geometry_calculator()
+_open_polygon_calculator()
+_open_experimental_star()
+_open_figurate_3d()
+_open_advanced_scientific_calculator()
+_open_3d_viewer(solid_id : str)
}
class SolidGeometry {
+vec_add(a : Vec3, b : Vec3) Vec3
+vec_sub(a : Vec3, b : Vec3) Vec3
+vec_scale(a : Vec3, scalar : float) Vec3
+vec_dot(a : Vec3, b : Vec3) float
+vec_cross(a : Vec3, b : Vec3) Vec3
+vec_length(a : Vec3) float
+vec_normalize(a : Vec3) Vec3
+polygon_area(vertices : Sequence[Vec3], face : Face) float
+face_normal(vertices : Sequence[Vec3], face : Face) Vec3
+plane_distance_from_origin(vertices : Sequence[Vec3], face : Face) float
+compute_surface_area(vertices : Sequence[Vec3], faces : Sequence[Face]) float
+compute_volume(vertices : Sequence[Vec3], faces : Sequence[Face]) float
+edges_from_faces(faces : Sequence[Face]) List[Tuple[int, int]]
+face_centroid(vertices : Sequence[Vec3], face : Face) Vec3
+angle_around_axis(point : Vec3, axis : Vec3, ref_axis : Vec3) float
}
class TetrahedronSolidService {
+calculate_properties(edge_length : float) Dict
+generate_vertices(edge_length : float) List[Vec3]
+generate_faces() List[Face]
}
class CubeSolidService {
+calculate_properties(edge_length : float) Dict
+generate_vertices(edge_length : float) List[Vec3]
+generate_faces() List[Face]
}
class OctahedronSolidService {
+calculate_properties(edge_length : float) Dict
+generate_vertices(edge_length : float) List[Vec3]
+generate_faces() List[Face]
}
class DodecahedronSolidService {
+calculate_properties(edge_length : float) Dict
+generate_vertices(edge_length : float) List[Vec3]
+generate_faces() List[Face]
}
class IcosahedronSolidService {
+calculate_properties(edge_length : float) Dict
+generate_vertices(edge_length : float) List[Vec3]
+generate_faces() List[Face]
}
class Geometry3DWindow {
+set_solid_payload(payload : SolidPayload)
+reset_view()
+toggle_wireframe()
+toggle_faces()
}
class Geometry3DView {
+set_payload(payload : SolidPayload)
+rotate(x : float, y : float)
+pan(dx : float, dy : float)
+zoom(factor : float)
+render()
}
GeometryHub --> GeometryCalculatorWindow : "launches"
GeometryHub --> PolygonalNumberWindow : "launches"
GeometryHub --> ExperimentalStarWindow : "launches"
GeometryHub --> Figurate3DWindow : "launches"
GeometryHub --> AdvancedScientificCalculatorWindow : "launches"
GeometryHub --> Geometry3DWindow : "launches"
Geometry3DWindow --> Geometry3DView : "contains"
Geometry3DView --> SolidGeometry : "uses"
TetrahedronSolidService --> SolidGeometry : "uses"
CubeSolidService --> SolidGeometry : "uses"
OctahedronSolidService --> SolidGeometry : "uses"
DodecahedronSolidService --> SolidGeometry : "uses"
IcosahedronSolidService --> SolidGeometry : "uses"
```

**Diagram sources**
- [geometry_hub.py](file://src/pillars/geometry/ui/geometry_hub.py)
- [solid_geometry.py](file://src/pillars/geometry/services/solid_geometry.py)

### User Interaction Patterns
Users interact with the Geometry module through the Geometry Hub, which organizes tools by category:

1. **Circles**: Tools for circles, ellipses, annuli, crescents, and vesica piscis
2. **Triangles**: Various types of triangles including equilateral, right, isosceles, and specialized forms
3. **Quadrilaterals**: Tools for squares, rectangles, parallelograms, rhombuses, and other four-sided shapes
4. **Polygons**: Regular polygons from pentagons to dodecagons and custom n-gons
5. **Pyramids**: Square, rectangular, triangular, and other pyramid types including frustums
6. **Prisms**: Various prism types including triangular, rectangular, and hexagonal prisms
7. **Antiprisms**: Triangular, square, pentagonal, and other antiprism types
8. **Platonic Solids**: The five regular polyhedra
9. **Archimedean Solids**: Thirteen semi-regular polyhedra

The 3D viewer allows interactive exploration of solids with mouse controls for rotation, panning, and zooming.

### Configuration and Customization
The Geometry module supports several customization options:
- **Unit system**: Support for different measurement units
- **Display options**: Toggle between wireframe and solid rendering
- **Color schemes**: Customizable colors for different elements
- **Precision settings**: Control over decimal places in calculations
- **View presets**: Save and recall specific camera angles for 3D viewing

### Troubleshooting Guidance
Common issues and solutions:
- **3D viewer not rendering**: Ensure OpenGL is properly installed and supported by the system
- **Calculation inaccuracies**: Verify that input values are in the correct units and format
- **Performance issues with complex solids**: Reduce the rendering quality or simplify the display
- **Missing shape types**: Check that all required service classes are properly registered in the hub

**Section sources**
- [geometry_hub.py](file://src/pillars/geometry/ui/geometry_hub.py)
- [solid_geometry.py](file://src/pillars/geometry/services/solid_geometry.py)

## Document Manager

The Document Manager module provides a comprehensive system for organizing, analyzing, and connecting textual documents, with features inspired by Zettelkasten and wiki-style knowledge management systems.

### Purpose and Key Features
The Document Manager pillar enables users to import, organize, and analyze textual documents, creating a personal knowledge base with interconnected ideas. The module supports full-text search, document relationships, and visual network exploration.

Key features include:
- **Document Import**: Support for importing documents from various formats including TXT, HTML, PDF, DOCX, and RTF
- **Full-Text Search**: Powerful search capabilities with highlighting of matching terms
- **Document Relationships**: Wiki-style links using [[Title]] syntax to create connections between documents
- **Mindscape**: Visual graph representation of document relationships and connections
- **Rich Text Editing**: Advanced editor with formatting capabilities
- **Metadata Management**: Support for tags, collections, authors, and other metadata

### Architectural Structure
The Document Manager follows a layered architecture with clear separation between UI, services, repositories, and data models:

```mermaid
graph TD
A[DocumentManagerHub] --> B[DocumentEditorWindow]
A --> C[DocumentLibrary]
A --> D[DocumentSearchWindow]
A --> E[MindscapeWindow]
B --> F[DocumentService]
C --> F
D --> F
E --> F
F --> G[DocumentRepository]
F --> H[DocumentVerseRepository]
F --> I[DocumentSearchRepository]
G --> J[Document]
I --> K[Whoosh Index]
```

**Diagram sources**
- [document_manager_hub.py](file://src/pillars/document_manager/ui/document_manager_hub.py)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py)
- [document.py](file://src/pillars/document_manager/models/document.py)
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py)

### Service Interfaces
The core functionality is provided by the `DocumentService` class, which manages all document operations:

```mermaid
classDiagram
class DocumentManagerHub {
+_open_document_editor()
+_open_document_library()
+_open_document_search()
+_open_mindscape()
+_open_document_from_library(doc : Document, search_term : Optional[str])
+_open_document_by_id(doc_id : int, search_term : Optional[str])
}
class DocumentService {
+import_document(file_path : str, tags : Optional[str], collection : Optional[str]) Document
+search_documents(query : str, limit : Optional[int]) List[Document]
+search_documents_with_highlights(query : str, limit : Optional[int]) List[Dict]
+get_all_documents() List[Document]
+get_all_documents_metadata() List[Document]
+get_document(doc_id : int) Document
+update_document(doc_id : int, **kwargs) Document
+update_documents(doc_ids : list[int], **kwargs) List[Document]
+delete_document(doc_id : int) bool
+delete_all_documents() int
+rebuild_search_index()
+get_document_verses(doc_id : int, include_ignored : bool) List[DocumentVerse]
+replace_document_verses(doc_id : int, verses : List[dict]) int
+delete_document_verses(doc_id : int) int
}
class DocumentRepository {
+create(title : str, content : str, file_type : str, file_path : str, raw_content : str, tags : str, author : str, collection : str) Document
+get(doc_id : int) Document
+get_by_ids(ids : List[int]) List[Document]
+get_all() List[Document]
+get_all_metadata() List[Document]
+update(doc_id : int, **kwargs) Document
+delete(doc_id : int) bool
+delete_all() int
}
class DocumentSearchRepository {
+index_document(doc : Document)
+index_documents(docs : List[Document])
+search(query_str : str, limit : Optional[int]) List[Dict]
+rebuild_index(documents : List[Document])
+clear_index()
+delete_document(doc_id : int)
}
class Document {
+id : int
+title : str
+file_path : str
+file_type : str
+content : str
+raw_content : str
+tags : str
+author : str
+collection : str
+created_at : DateTime
+updated_at : DateTime
+outgoing_links : List[Document]
+incoming_links : List[Document]
+__repr__() str
}
class DocumentLink {
+id : int
+source_id : int
+target_id : int
+created_at : DateTime
}
DocumentManagerHub --> DocumentService : "uses"
DocumentService --> DocumentRepository : "uses"
DocumentService --> DocumentSearchRepository : "uses"
DocumentService --> Document : "manages"
Document --> DocumentLink : "has"
```

**Diagram sources**
- [document_manager_hub.py](file://src/pillars/document_manager/ui/document_manager_hub.py)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py)
- [document.py](file://src/pillars/document_manager/models/document.py)
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py)

### User Interaction Patterns
Users interact with the Document Manager through several key interfaces:

1. **Document Editor**: Create and edit documents with rich text formatting
2. **Document Library**: Browse and manage imported documents
3. **Document Search**: Search across all documents with result highlighting
4. **Mindscape**: Visualize document relationships as a network graph

The system automatically detects [[WikiLinks]] in document content and creates bidirectional relationships between documents.

### Configuration and Customization
The Document Manager supports several customization options:
- **Import settings**: Configure default tags and collections for imported documents
- **Search preferences**: Adjust search sensitivity and result limits
- **Display options**: Customize the appearance of the document library and mindscape
- **Metadata templates**: Define custom metadata fields for documents
- **File type associations**: Map specific file types to default collections or tags

### Troubleshooting Guidance
Common issues and solutions:
- **Search not finding expected results**: Rebuild the search index using the document service tools
- **Links not being detected**: Ensure links are formatted as [[Title]] with exact title matching
- **Import failures**: Verify file format compatibility and sufficient read permissions
- **Performance issues with large document sets**: Optimize the search index and consider archiving older documents
- **Mindscape not updating**: Refresh the mindscape view or check for circular link dependencies

**Section sources**
- [document_manager_hub.py](file://src/pillars/document_manager/ui/document_manager_hub.py)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py)
- [document.py](file://src/pillars/document_manager/models/document.py)
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py)

## Astrology

The Astrology module provides tools for creating and analyzing astrological charts, with integration to astronomical calculation engines for precise celestial data.

### Purpose and Key Features
The Astrology pillar enables users to generate and analyze natal charts, transit charts, and planetary positions. The module integrates with astronomical libraries to provide accurate celestial calculations.

Key features include:
- **Natal Chart Generation**: Create birth charts with planetary positions and aspects
- **Transit Analysis**: Compare current planetary positions to natal charts
- **Planetary Position Tables**: Detailed tables showing planetary positions over time
- **Chart Visualization**: Interactive charts with customizable displays
- **Location Services**: Tools for looking up geographic coordinates

### Architectural Structure
The Astrology module follows a service-oriented architecture with clear separation between UI components and calculation services:

```mermaid
graph TD
A[AstrologyHub] --> B[NatalChartWindow]
A --> C[CurrentTransitWindow]
A --> D[PlanetaryPositionsWindow]
A --> E[VenusRoseWindow]
A --> F[NeoAubreyWindow]
B --> G[ChartStorageService]
B --> H[OpenAstroService]
C --> G
C --> H
D --> G
D --> H
E --> G
E --> H
F --> G
F --> H
G --> I[ChartRepository]
H --> J[LocationLookup]
```

**Diagram sources**
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)

### Service Interfaces
The core functionality is provided by the `ChartStorageService` and `OpenAstroService` classes:

```mermaid
classDiagram
class AstrologyHub {
+_open_natal_chart()
+_open_current_transit()
+_open_planetary_positions()
+_open_venus_rose()
+_open_neo_aubrey()
}
class ChartStorageService {
+create_chart(person_name : str, birth_date : datetime, birth_time : time, location : str, latitude : float, longitude : float) ChartRecord
+get_chart(chart_id : str) ChartRecord
+save_chart(chart : ChartRecord) ChartRecord
+delete_chart(chart_id : str) bool
+get_all_charts() List[ChartRecord]
}
class OpenAstroService {
+calculate_planetary_positions(date : datetime, latitude : float, longitude : float) Dict[str, Dict]
+calculate_aspects(planet_positions : Dict) List[Aspect]
+calculate_houses(date : datetime, latitude : float, longitude : float, house_system : str) List[House]
+get_current_transits(base_date : datetime, latitude : float, longitude : float) Dict
+get_planetary_positions(date : datetime, latitude : float, longitude : float) Dict
}
class LocationLookup {
+lookup_location(location_name : str) Tuple[float, float]
+get_timezone(latitude : float, longitude : float) str
}
class ChartRepository {
+save(chart : ChartRecord) ChartRecord
+get_by_id(chart_id : str) ChartRecord
+get_all() List[ChartRecord]
+delete(chart_id : str) bool
}
class ChartRecord {
+id : str
+person_name : str
+birth_date : datetime
+birth_time : time
+location : str
+latitude : float
+longitude : float
+chart_data : Dict
+created_at : datetime
+updated_at : datetime
+to_dict() Dict
+from_dict(data : Dict) ChartRecord
}
AstrologyHub --> NatalChartWindow : "launches"
AstrologyHub --> CurrentTransitWindow : "launches"
AstrologyHub --> PlanetaryPositionsWindow : "launches"
AstrologyHub --> VenusRoseWindow : "launches"
AstrologyHub --> NeoAubreyWindow : "launches"
NatalChartWindow --> ChartStorageService : "uses"
NatalChartWindow --> OpenAstroService : "uses"
CurrentTransitWindow --> ChartStorageService : "uses"
CurrentTransitWindow --> OpenAstroService : "uses"
PlanetaryPositionsWindow --> ChartStorageService : "uses"
PlanetaryPositionsWindow --> OpenAstroService : "uses"
VenusRoseWindow --> ChartStorageService : "uses"
VenusRoseWindow --> OpenAstroService : "uses"
NeoAubreyWindow --> ChartStorageService : "uses"
NeoAubreyWindow --> OpenAstroService : "uses"
ChartStorageService --> ChartRepository : "uses"
ChartStorageService --> ChartRecord : "manages"
OpenAstroService --> LocationLookup : "uses"
```

**Diagram sources**
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)

### User Interaction Patterns
Users interact with the Astrology module through several specialized windows:

1. **Natal Chart**: Create and view birth charts with planetary positions and aspects
2. **Current Transit**: Compare current planetary positions to a natal chart
3. **Planetary Positions**: View detailed tables of planetary positions
4. **Venus Rose**: Visualize Venus retrograde cycles
5. **Neo Aubrey**: Specialized chart analysis tool

### Configuration and Customization
The Astrology module supports several customization options:
- **House systems**: Choose from different house calculation methods
- **Aspect orbs**: Customize the allowable orb for aspects
- **Display preferences**: Adjust chart colors, fonts, and layout
- **Default locations**: Set default geographic locations for calculations
- **Time zone handling**: Configure how time zones are processed

### Troubleshooting Guidance
Common issues and solutions:
- **Incorrect planetary positions**: Verify the accuracy of birth data and time zone settings
- **Location lookup failures**: Check internet connectivity and verify location names
- **Chart rendering issues**: Adjust display settings or refresh the chart view
- **Performance issues with complex charts**: Simplify the display or reduce the number of elements shown
- **Data persistence problems**: Verify database connectivity and permissions

**Section sources**
- [astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)
- [chart_storage_service.py](file://src/pillars/astrology/services/chart_storage_service.py)
- [chart_models.py](file://src/pillars/astrology/models/chart_models.py)

## TQ

The TQ (Trigrammaton QBLH) module provides specialized tools for research and analysis within the Trigrammaton Qabalah system, focusing on geometric transitions, kamea grids, and quadset analysis.

### Purpose and Key Features
The TQ pillar enables users to explore the complex relationships within the Trigrammaton Qabalah system, with tools for analyzing geometric transitions, kamea grids, and quadsets. The module supports both calculation and visualization of these esoteric structures.

Key features include:
- **Kamea Grid Analysis**: Tools for working with kamea grids including Baphomet and Maut grids
- **Quadset Analysis**: Analysis of quadsets and their relationships
- **Geometric Transitions**: Visualization of geometric transitions between forms
- **Conrune Pair Finding**: Tools for finding conrune pairs
- **Ternary Conversion**: Conversion between different ternary systems
- **Platonic Transitions**: Analysis of transitions between Platonic solids

### Architectural Structure
The TQ module follows a modular architecture with specialized services for different types of analysis:

```mermaid
graph TD
A[TQHub] --> B[KameaWindow]
A --> C[QuadsetAnalysisWindow]
A --> D[GeometricTransitionsWindow]
A --> E[GeometricTransitions3DWindow]
A --> F[ConrunePairFinderWindow]
A --> G[TernaryConverterWindow]
A --> H[TransitionsWindow]
A --> I[AmunVisualizer]
A --> J[BaphometPanel]
A --> K[NuclearMutationPanel]
A --> L[FractalNetworkDialog]
B --> M[KameaGridService]
C --> N[QuadsetEngine]
D --> O[GeometricTransitionService]
E --> O
F --> P[ConrunePairFinderService]
G --> Q[TernaryService]
H --> R[PlatonicTransitionService]
I --> S[AmunAudioService]
J --> T[BaphometColorService]
L --> U[KameaSymphonyService]
```

**Diagram sources**
- [tq_hub.py](file://src/pillars/tq/ui/tq_hub.py)
- [kamea_grid_service.py](file://src/pillars/tq/services/kamea_grid_service.py)
- [quadset_engine.py](file://src/pillars/tq/services/quadset_engine.py)

### Service Interfaces
The core functionality is provided by specialized service classes for different aspects of TQ analysis:

```mermaid
classDiagram
class TQHub {
+_open_kamea_grid()
+_open_quadset_analysis()
+_open_geometric_transitions()
+_open_geometric_transitions_3d()
+_open_conrune_pair_finder()
+_open_ternary_converter()
+_open_transitions()
+_open_amun_visualizer()
+_open_baphomet_panel()
+_open_nuclear_mutation_panel()
+_open_fractal_network()
}
class KameaGridService {
+load_kamea_grid(grid_type : str) List[List[int]]
+find_quadsets(grid : List[List[int]]) List[Quadset]
+analyze_symmetries(grid : List[List[int]]) Dict
+generate_kamea_fractal(grid : List[List[int]], iterations : int) List[List[int]]
}
class QuadsetEngine {
+find_quadsets_in_text(text : str, grid : List[List[int]]) List[QuadsetMatch]
+analyze_quadset_patterns(quadsets : List[Quadset]) Dict
+generate_quadset_sequences(start_quadset : Quadset, length : int) List[Quadset]
+find_quadset_transitions(quadsets : List[Quadset]) List[Transition]
}
class GeometricTransitionService {
+calculate_transition_matrix(from_shape : str, to_shape : str) List[List[float]]
+generate_transition_sequence(start_shape : str, end_shape : str, steps : int) List[Shape]
+analyze_transition_properties(matrix : List[List[float]]) Dict
}
class ConrunePairFinderService {
+find_conrune_pairs(text : str, grid : List[List[int]]) List[ConrunePair]
+validate_conrune_pair(pair : ConrunePair) bool
+generate_conrune_variants(pair : ConrunePair) List[ConrunePair]
}
class TernaryService {
+convert_to_ternary(value : int) str
+convert_from_ternary(ternary : str) int
+analyze_ternary_patterns(sequence : List[int]) Dict
+generate_ternary_sequences(length : int) List[str]
}
class PlatonicTransitionService {
+calculate_dual_transitions() List[Transition]
+generate_compound_solids() List[Solid]
+analyze_symmetry_transitions() Dict
}
class AmunAudioService {
+generate_amun_sound(frequency : float, duration : float) AudioData
+analyze_sound_patterns(audio : AudioData) Dict
+generate_ditrunal_sequence(pattern : List[int]) List[AudioData]
}
class BaphometColorService {
+generate_baphomet_colors(grid : List[List[int]]) List[Color]
+analyze_color_patterns(colors : List[Color]) Dict
+generate_color_transitions(start_color : Color, end_color : Color, steps : int) List[Color]
}
class KameaSymphonyService {
+generate_kamea_symphony(grid : List[List[int]], tempo : float) MusicalScore
+analyze_musical_patterns(score : MusicalScore) Dict
+generate_fractal_compositions(base_score : MusicalScore, iterations : int) List[MusicalScore]
}
TQHub --> KameaWindow : "launches"
TQHub --> QuadsetAnalysisWindow : "launches"
TQHub --> GeometricTransitionsWindow : "launches"
TQHub --> GeometricTransitions3DWindow : "launches"
TQHub --> ConrunePairFinderWindow : "launches"
TQHub --> TernaryConverterWindow : "launches"
TQHub --> TransitionsWindow : "launches"
TQHub --> AmunVisualizer : "launches"
TQHub --> BaphometPanel : "launches"
TQHub --> NuclearMutationPanel : "launches"
TQHub --> FractalNetworkDialog : "launches"
KameaWindow --> KameaGridService : "uses"
QuadsetAnalysisWindow --> QuadsetEngine : "uses"
GeometricTransitionsWindow --> GeometricTransitionService : "uses"
GeometricTransitions3DWindow --> GeometricTransitionService : "uses"
ConrunePairFinderWindow --> ConrunePairFinderService : "uses"
TernaryConverterWindow --> TernaryService : "uses"
TransitionsWindow --> PlatonicTransitionService : "uses"
AmunVisualizer --> AmunAudioService : "uses"
BaphometPanel --> BaphometColorService : "uses"
FractalNetworkDialog --> KameaSymphonyService : "uses"
```

**Diagram sources**
- [tq_hub.py](file://src/pillars/tq/ui/tq_hub.py)
- [kamea_grid_service.py](file://src/pillars/tq/services/kamea_grid_service.py)
- [quadset_engine.py](file://src/pillars/tq/services/quadset_engine.py)

### User Interaction Patterns
Users interact with the TQ module through specialized analysis windows:

1. **Kamea Grid**: Analyze kamea grids and their properties
2. **Quadset Analysis**: Find and analyze quadsets in texts
3. **Geometric Transitions**: Visualize transitions between geometric forms
4. **Conrune Pair Finder**: Identify conrune pairs in texts
5. **Ternary Converter**: Convert between decimal and ternary systems
6. **Transitions**: Analyze transitions between Platonic solids
7. **Amun Visualizer**: Visualize Amun sounds and patterns
8. **Baphomet Panel**: Explore Baphomet color mappings
9. **Nuclear Mutation Panel**: Analyze nuclear mutation patterns
10. **Fractal Network**: Generate fractal compositions from kamea grids

### Configuration and Customization
The TQ module supports several customization options:
- **Grid types**: Select different kamea grid types (Baphomet, Maut, etc.)
- **Analysis depth**: Configure the depth of quadset and transition analysis
- **Visualization settings**: Customize colors, shapes, and layouts for visualizations
- **Audio parameters**: Adjust frequency ranges and durations for sound generation
- **Pattern recognition**: Tune sensitivity for pattern detection algorithms

### Troubleshooting Guidance
Common issues and solutions:
- **Slow analysis performance**: Reduce the analysis depth or limit the scope of analysis
- **Visualization rendering issues**: Adjust display settings or simplify complex visualizations
- **Incorrect pattern recognition**: Verify input data and adjust sensitivity settings
- **Audio generation problems**: Check audio output configuration and system permissions
- **Data loading failures**: Verify file paths and permissions for kamea grid data files

**Section sources**
- [tq_hub.py](file://src/pillars/tq/ui/tq_hub.py)
- [kamea_grid_service.py](file://src/pillars/tq/services/kamea_grid_service.py)
- [quadset_engine.py](file://src/pillars/tq/services/quadset_engine.py)

## Adyton

The Adyton module provides advanced 3D modeling and visualization capabilities, focusing on architectural and geometric forms with a sacred geometry emphasis.

### Purpose and Key Features
The Adyton pillar enables users to create and manipulate complex 3D geometric forms and architectural models. The module provides a specialized 3D engine for rendering and interacting with these forms.

Key features include:
- **3D Modeling**: Create and manipulate 3D geometric primitives and complex forms
- **Architectural Elements**: Specialized tools for architectural components like blocks, corners, and prisms
- **Advanced Rendering**: High-quality 3D rendering with lighting and material effects
- **Camera Controls**: Sophisticated camera controls for viewing models from different angles
- **Scene Management**: Tools for organizing and managing complex 3D scenes

### Architectural Structure
The Adyton module follows a component-based architecture with specialized classes for different aspects of 3D modeling:

```mermaid
graph TD
A[AdytonHub] --> B[AdytonWindow]
B --> C[Scene]
B --> D[Camera]
B --> E[Renderer]
C --> F[Block]
C --> G[Corner]
C --> H[Prism]
C --> I[GeometryTypes]
D --> J[CameraControls]
E --> K[RenderingEngine]
```

**Diagram sources**
- [adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)

### Service Interfaces
The core functionality is provided by the Adyton UI components and 3D engine classes:

```mermaid
classDiagram
class AdytonHub {
+_open_adyton_window()
}
class AdytonWindow {
+set_scene(scene : Scene)
+set_camera(camera : Camera)
+set_renderer(renderer : Renderer)
+render()
}
class Scene {
+add_object(object : GeometryObject)
+remove_object(object : GeometryObject)
+get_objects() List[GeometryObject]
+clear()
}
class Camera {
+set_position(x : float, y : float, z : float)
+set_rotation(x : float, y : float, z : float)
+set_fov(fov : float)
+set_near_far(near : float, far : float)
}
class Renderer {
+render_scene(scene : Scene, camera : Camera)
+set_render_mode(mode : RenderMode)
+set_lighting(lighting : LightingSettings)
}
class Block {
+set_dimensions(width : float, height : float, depth : float)
+set_position(x : float, y : float, z : float)
+set_rotation(x : float, y : float, z : float)
}
class Corner {
+set_angle(angle : float)
+set_radius(radius : float)
+set_position(x : float, y : float, z : float)
}
class Prism {
+set_base_sides(sides : int)
+set_base_radius(radius : float)
+set_height(height : float)
+set_position(x : float, y : float, z : float)
}
class GeometryTypes {
+CUBE : str
+SPHERE : str
+CYLINDER : str
+CONE : str
+TORUS : str
}
AdytonHub --> AdytonWindow : "launches"
AdytonWindow --> Scene : "uses"
AdytonWindow --> Camera : "uses"
AdytonWindow --> Renderer : "uses"
Scene --> Block : "contains"
Scene --> Corner : "contains"
Scene --> Prism : "contains"
Scene --> GeometryTypes : "references"
AdytonWindow --> Camera : "controls"
AdytonWindow --> Renderer : "triggers"
```

**Diagram sources**
- [adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)

### User Interaction Patterns
Users interact with the Adyton module through the Adyton window, which provides a comprehensive 3D workspace:

1. **Scene Creation**: Create new 3D scenes and add geometric objects
2. **Object Manipulation**: Position, rotate, and scale 3D objects
3. **Camera Navigation**: Navigate the 3D space using camera controls
4. **Rendering**: Adjust rendering settings and view the scene in different modes
5. **Model Export**: Export models in various 3D formats

### Configuration and Customization
The Adyton module supports several customization options:
- **Rendering quality**: Adjust the quality and performance of 3D rendering
- **Display modes**: Switch between wireframe, solid, and textured rendering
- **Lighting settings**: Configure lighting for scenes
- **Material properties**: Customize materials for 3D objects
- **Unit system**: Set the measurement units for 3D modeling

### Troubleshooting Guidance
Common issues and solutions:
- **3D rendering failures**: Verify graphics drivers and OpenGL support
- **Performance issues**: Reduce rendering quality or simplify complex scenes
- **Object manipulation problems**: Check coordinate systems and transformation matrices
- **Camera navigation issues**: Reset camera settings or adjust navigation sensitivity
- **Export failures**: Verify file permissions and supported export formats

**Section sources**
- [adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)