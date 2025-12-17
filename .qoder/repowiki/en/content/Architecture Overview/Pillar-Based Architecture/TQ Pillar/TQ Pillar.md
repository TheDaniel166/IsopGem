# TQ Pillar

<cite>
**Referenced Files in This Document**   
- [tq_hub.py](file://src/pillars/tq/ui/tq_hub.py)
- [quadset_engine.py](file://src/pillars/tq/services/quadset_engine.py)
- [geometric_transition_service.py](file://src/pillars/tq/services/geometric_transition_service.py)
- [kamea_grid_service.py](file://src/pillars/tq/services/kamea_grid_service.py)
- [cipher_token.py](file://src/pillars/tq/models/cipher_token.py)
- [kamea_cell.py](file://src/pillars/tq/models/kamea_cell.py)
- [quadset_models.py](file://src/pillars/tq/models/quadset_models.py)
- [symphony_config.py](file://src/pillars/tq/models/symphony_config.py)
- [quadset_analysis_window.py](file://src/pillars/tq/ui/quadset_analysis_window.py)
- [kamea_baphomet_grid.csv](file://src/pillars/tq/data/kamea_baphomet_grid.csv)
- [kamea_baphomet_ternary.csv](file://src/pillars/tq/data/kamea_baphomet_ternary.csv)
- [conrune_pair_finder_service.py](file://src/pillars/tq/services/conrune_pair_finder_service.py)
- [ternary_service.py](file://src/pillars/tq/services/ternary_service.py)
- [ternary_transition_service.py](file://src/pillars/tq/services/ternary_transition_service.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Component Architecture](#component-architecture)
3. [Data Models](#data-models)
4. [UI Components](#ui-components)
5. [CSV Data Integration](#csv-data-integration)
6. [Rune Pairing and Geometric Transitions](#rune-pairing-and-geometric-transitions)
7. [Gematria and Sacred Geometry Integration](#gematria-and-sacred-geometry-integration)
8. [Conclusion](#conclusion)

## Introduction

The TQ (Trigrammaton QBLH) pillar of the isopgem application serves as a specialized research environment for advanced QBLH pattern analysis. This pillar focuses on the exploration of trigram patterns, kamea grids, and geometric transitions through a structured framework of quadsets. The system enables users to analyze complex relationships between numbers, symbols, and sacred geometries using ternary representations and transformation logic. The TQ pillar integrates multiple analytical tools that work in concert to reveal hidden patterns in numerical and symbolic data, providing insights into the underlying structure of QBLH systems.

**Section sources**
- [tq_hub.py](file://src/pillars/tq/ui/tq_hub.py#L1-L326)
- [__init__.py](file://src/pillars/tq/__init__.py#L1-L2)

## Component Architecture

The TQ pillar is structured around a central controller and several specialized services that handle specific aspects of QBLH analysis. The architecture follows a modular design pattern where each component has a well-defined responsibility and interacts with others through clearly defined interfaces.

### tq_hub as Central Controller

The `tq_hub` serves as the central controller and entry point for all TQ pillar functionality. It provides a unified interface that launches various analytical tools and manages their lifecycle. The hub implements a window management system that ensures consistent user experience across different tools. It coordinates the initialization of services and maintains references to active windows, allowing for proper resource management and state preservation.

```mermaid
classDiagram
class TQHub {
+window_manager : WindowManager
-_setup_ui()
-_open_ternary_converter()
-_open_quadset_analysis()
-_open_transitions()
-_open_geometric_transitions()
-_open_geometric_transitions_3d()
-_open_conrune_pair_finder()
-_open_amun_sound()
-_open_kamea_grid()
-_open_baphomet_grid()
}
class WindowManager {
+open_window()
}
TQHub --> WindowManager : "uses"
TQHub --> TernaryConverterWindow : "launches"
TQHub --> QuadsetAnalysisWindow : "launches"
TQHub --> TransitionsWindow : "launches"
TQHub --> GeometricTransitionsWindow : "launches"
TQHub --> GeometricTransitions3DWindow : "launches"
TQHub --> ConrunePairFinderWindow : "launches"
TQHub --> TernarySoundWidget : "launches"
TQHub --> KameaWindow : "launches"
```

**Diagram sources **
- [tq_hub.py](file://src/pillars/tq/ui/tq_hub.py#L17-L326)

**Section sources**
- [tq_hub.py](file://src/pillars/tq/ui/tq_hub.py#L1-L326)

### quadset_engine Processing Trigram Patterns

The `quadset_engine` is responsible for processing trigram patterns and performing comprehensive quadset analysis. It orchestrates the transformation pipeline that generates the complete result model from an input decimal number. The engine implements the core logic for calculating quadset members, differentials, and transgrams, following the established QBLH pattern analysis methodology.

```mermaid
classDiagram
class QuadsetEngine {
+ternary_service : TernaryService
+transition_service : TernaryTransitionService
+pattern_analyzer : PatternAnalyzer
+calculate(decimal_input : int) QuadsetResult
-_create_member(name : str, decimal : int, ternary : str) QuadsetMember
}
class TernaryService {
+decimal_to_ternary(n : int) str
+ternary_to_decimal(t : str) int
+conrune_transform(t : str) str
+reverse_ternary(t : str) str
}
class TernaryTransitionService {
+transition(t1 : str, t2 : str) str
+generate_sequence(start_t : str, modifier_t : str, iterations : int) List[Tuple]
}
class PatternAnalyzer {
+analyze(members : List[QuadsetMember]) str
}
QuadsetEngine --> TernaryService : "uses"
QuadsetEngine --> TernaryTransitionService : "uses"
QuadsetEngine --> PatternAnalyzer : "uses"
```

**Diagram sources **
- [quadset_engine.py](file://src/pillars/tq/services/quadset_engine.py#L11-L87)

**Section sources**
- [quadset_engine.py](file://src/pillars/tq/services/quadset_engine.py#L1-L87)

### geometric_transition_service Handling Shape-Based Transformations

The `geometric_transition_service` handles shape-based transformations on regular polygons, enabling the analysis of vertex transitions and geometric patterns. It supports polygons with 3 to 27 sides and provides functionality for generating skip groups and special sequences. The service implements algorithms for constructing vertices, calculating transitions, and summarizing results, making it a powerful tool for exploring geometric relationships in QBLH systems.

```mermaid
classDiagram
class GeometricTransitionService {
+MIN_SIDES : int
+MAX_SIDES : int
+MAX_SKIP_GROUPS : int
+SPECIAL_PATTERNS : Dict[int, List[Dict[str, object]]]
+get_polygon_options() List[Dict[str, object]]
+build_vertices(sides : int, values : Optional[Sequence[int]]) List[Vertex]
+generate_skip_groups(vertices : Sequence[Vertex], max_skip : Optional[int]) List[Dict[str, object]]
+generate_special_sequences(vertices : Sequence[Vertex]) List[Dict[str, object]]
-_build_transitions(vertices : Sequence[Vertex], skip : int) List[Transition]
-_build_custom_transition(vertices : Sequence[Vertex], from_index : int, to_index : int) Transition
-_summarize(transitions : Sequence[Transition]) Dict[str, object]
-_group_label(skip : int) str
-_normalize_values(sides : int, values : Optional[Sequence[int]]) List[int]
-_validate_sides(sides : int)
-_polygon_name(sides : int) str
}
class Vertex {
+index : int
+label : str
+value : int
+x : float
+y : float
}
class Transition {
+skip : int
+from_index : int
+to_index : int
+from_value : int
+to_value : int
+from_ternary : str
+to_ternary : str
+result_ternary : str
+result_decimal : int
}
GeometricTransitionService --> Vertex : "creates"
GeometricTransitionService --> Transition : "creates"
GeometricTransitionService --> TernaryService : "uses"
GeometricTransitionService --> TernaryTransitionService : "uses"
```

**Diagram sources **
- [geometric_transition_service.py](file://src/pillars/tq/services/geometric_transition_service.py#L38-L323)

**Section sources**
- [geometric_transition_service.py](file://src/pillars/tq/services/geometric_transition_service.py#L1-L323)

### kamea_grid_service Managing Magic Square Logic

The `kamea_grid_service` manages the 27x27 Kamea grid, serving as the source of truth for all grid-related operations. It loads data from validated CSV files and provides methods for accessing cells, calculating quadsets, and determining geometric chords. The service supports both Maut and Baphomet variants, with different logic for handling quadset relationships. It also integrates with the Baphomet color service to provide visual feedback based on cell properties.

```mermaid
classDiagram
class KameaGridService {
+_grid : Dict[Tuple[int, int], KameaCell]
+_decimal_map : Dict[int, Tuple[int, int]]
+_initialized : bool
+variant : str
+decimal_csv_path : str
+ternary_csv_path : str
+cells : List[KameaCell]
+initialize()
+get_cell(x : int, y : int) Optional[KameaCell]
+get_cell_by_locator(region : int, area : int, cell : int) Optional[KameaCell]
+get_cell_color(cell : KameaCell) QColor
+get_quadset(x : int, y : int) List[KameaCell]
+get_chord_values(decimal_value : int) List[int]
-_load_grid()
-_parse_grid_csv(filepath : str) Dict[Tuple[int, int], str]
}
class KameaCell {
+x : int
+y : int
+ternary_value : str
+decimal_value : int
+bigrams : Tuple[int, int, int]
+family_id : int
+kamea_locator : str
+is_axis : bool
+is_origin : bool
+pyx_count : int
+conrune_vector : int
}
class BaphometColorService {
+resolve_color(ternary_value : str) QColor
}
KameaGridService --> KameaCell : "contains"
KameaGridService --> BaphometColorService : "uses"
```

**Diagram sources **
- [kamea_grid_service.py](file://src/pillars/tq/services/kamea_grid_service.py#L11-L220)

**Section sources**
- [kamea_grid_service.py](file://src/pillars/tq/services/kamea_grid_service.py#L1-L220)

## Data Models

The TQ pillar employs several specialized data models to represent the various entities involved in QBLH pattern analysis. These models provide a structured way to store and manipulate data, ensuring consistency and integrity throughout the system.

### cipher_token Data Model

The `cipher_token` model represents a single entry in the TQ Base-27 Cipher, mapping a decimal value (0-26) to its categorical, symbolic, and alphabetic correspondences. Each token includes properties for the decimal value, trigram representation, category, symbol, and letter. The model also provides computed properties for determining the ontological stratum based on the count of zeros in the trigram.

```mermaid
classDiagram
class CipherToken {
+decimal_value : int
+trigram : str
+category : Optional[str]
+symbol : Optional[str]
+letter : Optional[str]
+label : str
+stratum : str
}
```

**Diagram sources **
- [cipher_token.py](file://src/pillars/tq/models/cipher_token.py#L5-L35)

**Section sources**
- [cipher_token.py](file://src/pillars/tq/models/cipher_token.py#L1-L35)

### kamea_cell Data Model

The `kamea_cell` model represents a single cell in the 27x27 Kamea grid, with attributes for Cartesian coordinates, ternary and decimal values, bigrams, and family ID. The model includes computed properties for determining the cell's position relative to the axes, its kamea locator string, and its dimensional density (count of zeros in the ternary value). It also provides a method for calculating the conrune vector, which represents the magnitude of the vector between the cell and its conrune.

```mermaid
classDiagram
class KameaCell {
+x : int
+y : int
+ternary_value : str
+decimal_value : int
+bigrams : Tuple[int, int, int]
+family_id : int
+kamea_locator : str
+is_axis : bool
+is_origin : bool
+pyx_count : int
+conrune_vector : int
}
```

**Diagram sources **
- [kamea_cell.py](file://src/pillars/tq/models/kamea_cell.py#L5-L59)

**Section sources**
- [kamea_cell.py](file://src/pillars/tq/models/kamea_cell.py#L1-L59)

### symphony_config Data Model

The `symphony_config` model defines the orchestral archetypes and physics constants used in the audio synthesis system. It includes a dataclass for `SymphonyFamily` that specifies the properties of each family, such as ID, name, color, instrument, and audio type. The model also defines the base frequencies for octaves and scale ratios for just intonation, providing the foundation for musical representation of QBLH patterns.

```mermaid
classDiagram
class SymphonyFamily {
+id : int
+name : str
+color_hex : str
+instrument : str
+audio_type : str
+detune_acolyte : tuple
+detune_temple : tuple
}
class SymphonyNucleation {
+ditrune : str
+core : str
+body : str
+skin : str
+pyx_count : int
+hierarchy_class : str
+coordinates : tuple
}
```

**Diagram sources **
- [symphony_config.py](file://src/pillars/tq/models/symphony_config.py#L5-L46)

**Section sources**
- [symphony_config.py](file://src/pillars/tq/models/symphony_config.py#L1-L46)

## UI Components

The TQ pillar includes several specialized UI components that provide interactive interfaces for quadset analysis, conrune pairing, and ternary conversion. These components are designed to be intuitive and informative, allowing users to explore complex QBLH patterns with ease.

### quadset_analysis_window

The `quadset_analysis_window` provides a comprehensive interface for quadset analysis, with tabs for overview, detailed member information, advanced calculations, and gematria database lookup. The window includes a visual representation of the quadset grid, with panels for each member showing decimal and ternary values. It also provides detailed property cards that display number type, factorization, factors analysis, geometric properties, and digit sum.

```mermaid
classDiagram
class QuadsetAnalysisWindow {
+window_manager : WindowManager
+engine : QuadsetEngine
+_setup_ui()
+_create_overview_tab() QWidget
+_create_detail_tab(title : str) QWidget
+_create_panel(title : str) QGroupBox
+_update_panel(panel : QGroupBox, member : QuadsetMember)
+_create_advanced_tab() QWidget
+_create_gematria_tab() QWidget
+_handle_geometry_menu(event, text_edit)
+_open_geometry_window(sides : int, index : int, mode : str)
+_update_tab(tab : QWidget, member : QuadsetMember)
}
class CardTextEdit {
+context_menu_handler : callable
+contextMenuEvent(event)
}
class QuadsetGlyph {
+_ternary : str
+set_ternary(ternary : str)
+paintEvent(event)
}
class PropertyCard {
+title_label : QLabel
+content_edit : CardTextEdit
+_adjust_height()
+set_content(text : str)
}
QuadsetAnalysisWindow --> CardTextEdit : "uses"
QuadsetAnalysisWindow --> QuadsetGlyph : "uses"
QuadsetAnalysisWindow --> PropertyCard : "uses"
QuadsetAnalysisWindow --> QuadsetEngine : "uses"
QuadsetAnalysisWindow --> WindowManager : "uses"
```

**Diagram sources **
- [quadset_analysis_window.py](file://src/pillars/tq/ui/quadset_analysis_window.py#L175-L800)

**Section sources**
- [quadset_analysis_window.py](file://src/pillars/tq/ui/quadset_analysis_window.py#L1-L800)

## CSV Data Integration

The TQ pillar integrates CSV data files to provide the source of truth for kamea grid values and ternary mappings. These files are loaded at initialization and used to populate the kamea grid service, ensuring consistency and accuracy in all grid-related operations.

### kamea_baphomet.csv Integration

The `kamea_baphomet.csv` file contains the decimal values for the 27x27 Kamea grid in a structured format. The file uses a header row for X coordinates (-13 to 13) and the first column for Y coordinates (+13 to -13), with the intersection representing the cell value. This format allows for easy parsing and mapping to the Cartesian coordinate system used in the application.

```mermaid
flowchart TD
Start([Application Start]) --> LoadCSV["Load kamea_baphomet.csv"]
LoadCSV --> ParseCSV["Parse CSV Data"]
ParseCSV --> CreateGrid["Create Kamea Grid"]
CreateGrid --> StoreCells["Store Cells in _grid Dictionary"]
StoreCells --> CreateMap["Create _decimal_map for Reverse Lookup"]
CreateMap --> Initialize["Grid Initialized"]
Initialize --> Ready["Service Ready for Queries"]
```

**Diagram sources **
- [kamea_baphomet_grid.csv](file://src/pillars/tq/data/kamea_baphomet_grid.csv#L1-L29)

**Section sources**
- [kamea_grid_service.py](file://src/pillars/tq/services/kamea_grid_service.py#L120-L182)

### ternary_mappings Integration

The ternary mapping files, including `kamea_baphomet_ternary.csv`, provide the ternary string representations for each cell in the Kamea grid. These files follow the same structure as the decimal CSV files, with headers for X coordinates and the first column for Y coordinates. The ternary values are used to calculate bigrams, determine cell properties, and perform conrune transformations.

```mermaid
flowchart TD
Start([Application Start]) --> LoadTernaryCSV["Load kamea_baphomet_ternary.csv"]
LoadTernaryCSV --> ParseTernaryCSV["Parse Ternary CSV Data"]
ParseTernaryCSV --> ExtractValues["Extract Ternary Values"]
ExtractValues --> PadValues["Pad with Leading Zeros to 6 Digits"]
PadValues --> ParseBigrams["Parse Bigrams (Region, Area, Cell)"]
ParseBigrams --> CreateCells["Create KameaCell Objects"]
CreateCells --> StoreCells["Store in _grid Dictionary"]
StoreCells --> Complete["Ternary Data Integrated"]
```

**Diagram sources **
- [kamea_baphomet_ternary.csv](file://src/pillars/tq/data/kamea_baphomet_ternary.csv#L1-L29)

**Section sources**
- [kamea_grid_service.py](file://src/pillars/tq/services/kamea_grid_service.py#L120-L182)

## Rune Pairing and Geometric Transitions

The TQ pillar implements specialized algorithms for rune pairing and geometric transitions, enabling the analysis of complex relationships between numbers and shapes. These algorithms are based on the principles of balanced ternary arithmetic and geometric transformations.

### Rune Pairing Logic

The rune pairing logic is implemented in the `conrune_pair_finder_service`, which analyzes pairs of numbers based on their difference. The service converts the difference to balanced ternary notation, where -1 is represented by a special symbol, and then maps this to the original ternary system. This allows for the identification of conrune pairs that have a specific difference, providing insights into the underlying structure of the number system.

```mermaid
sequenceDiagram
participant User as "User"
participant Service as "ConrunePairFinderService"
participant Ternary as "TernaryService"
User->>Service : analyze(difference : int)
Service->>Service : _decimal_to_balanced_ternary(difference)
Service->>Service : _balanced_to_original_ternary(balanced)
Service->>Ternary : conrune_transform(ternary_a)
Ternary-->>Service : ternary_b
Service->>Ternary : ternary_to_decimal(ternary_a)
Ternary-->>Service : decimal_a
Service->>Ternary : ternary_to_decimal(ternary_b)
Ternary-->>Service : decimal_b
Service->>Service : calculate_diff(decimal_a, decimal_b)
Service-->>User : {balanced, pairs, calculated_difference, expected_difference, verified}
```

**Diagram sources **
- [conrune_pair_finder_service.py](file://src/pillars/tq/services/conrune_pair_finder_service.py#L19-L82)

**Section sources**
- [conrune_pair_finder_service.py](file://src/pillars/tq/services/conrune_pair_finder_service.py#L1-L82)

### Geometric Transition Sequences

Geometric transition sequences are generated by the `geometric_transition_service`, which creates patterns of vertex transitions on regular polygons. The service supports both skip groups (perimeter and diagonal transitions) and special sequences (predefined patterns like the Lovely Star and Mountain Star). These sequences can be used to explore the geometric relationships between numbers and their symbolic representations.

```mermaid
sequenceDiagram
participant User as "User"
participant Service as "GeometricTransitionService"
User->>Service : generate_skip_groups(vertices, max_skip)
Service->>Service : _build_transitions(vertices, skip)
loop for each skip value
Service->>Service : Calculate transition for each vertex
Service->>Service : Apply ternary transition logic
Service->>Service : Store transition result
end
Service-->>User : List of skip groups with transitions
User->>Service : generate_special_sequences(vertices)
Service->>Service : Get predefined pattern for polygon
Service->>Service : _build_custom_transition for each edge
Service-->>User : List of special sequences with transitions
```

**Diagram sources **
- [geometric_transition_service.py](file://src/pillars/tq/services/geometric_transition_service.py#L127-L182)

**Section sources**
- [geometric_transition_service.py](file://src/pillars/tq/services/geometric_transition_service.py#L1-L323)

## Gematria and Sacred Geometry Integration

The TQ pillar integrates with gematria values and sacred geometry representations to provide a comprehensive analysis framework. This integration allows users to explore the relationships between numbers, words, and geometric forms, revealing deeper patterns in the QBLH system.

### Gematria Value Integration

The TQ pillar connects to gematria values through the quadset analysis window, which includes a dedicated tab for gematria database lookup. When a number is analyzed, the system queries the gematria database to find words or phrases that have the same numerical value. This allows users to explore the symbolic meaning of numbers in the context of sacred texts and esoteric traditions.

```mermaid
flowchart TD
Input([Input Number]) --> QuadsetEngine["QuadsetEngine.calculate()"]
QuadsetEngine --> QuadsetResult["QuadsetResult"]
QuadsetResult --> QuadsetAnalysisWindow["QuadsetAnalysisWindow"]
QuadsetAnalysisWindow --> GematriaTab["Gematria Tab"]
GematriaTab --> DatabaseQuery["Query Gematria Database"]
DatabaseQuery --> Results["Display Matching Words/Phrases"]
Results --> Analysis["Analyze Symbolic Meaning"]
```

**Section sources**
- [quadset_analysis_window.py](file://src/pillars/tq/ui/quadset_analysis_window.py#L777-L800)

### Sacred Geometry Representations

Sacred geometry representations are integrated through the geometric transition service and the polygonal number visualizer. Users can explore the geometric properties of numbers, such as whether they are triangular, square, or pentagonal numbers, and visualize these shapes in the application. The system also supports the visualization of centered polygonal numbers and star numbers, providing a comprehensive view of the geometric aspects of QBLH patterns.

```mermaid
flowchart TD
Number([Number]) --> Properties["Number Properties"]
Properties --> Geometry["Geometric Properties"]
Geometry --> Polygonal["Polygonal Info"]
Geometry --> Centered["Centered Polygonal Info"]
Geometry --> Star["Star Number Info"]
Polygonal --> Visualizer["Polygonal Number Visualizer"]
Centered --> Visualizer
Star --> Visualizer
Visualizer --> Display["Display Geometric Shape"]
```

**Section sources**
- [quadset_analysis_window.py](file://src/pillars/tq/ui/quadset_analysis_window.py#L659-L687)

## Conclusion

The TQ (Trigrammaton QBLH) pillar of the isopgem application provides a comprehensive research environment for advanced QBLH pattern analysis. Through its modular architecture, specialized data models, and integrated tools, the system enables users to explore complex relationships between numbers, symbols, and sacred geometries. The central `tq_hub` controller coordinates access to various analytical tools, while the `quadset_engine`, `geometric_transition_service`, and `kamea_grid_service` handle specific aspects of pattern analysis. The integration of CSV data files ensures consistency and accuracy in grid-related operations, while the specialized UI components provide intuitive interfaces for exploring quadset analysis, conrune pairing, and ternary conversion. The connection to gematria values and sacred geometry representations further enhances the system's analytical capabilities, making it a powerful tool for researchers in the field of QBLH studies.