# Gematria Pillar

<cite>
**Referenced Files in This Document**   
- [__init__.py](file://src/pillars/gematria/__init__.py)
- [gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py)
- [calculation_service.py](file://src/pillars/gematria/services/calculation_service.py)
- [calculation_entity.py](file://src/pillars/gematria/models/calculation_entity.py)
- [calculation_record.py](file://src/pillars/gematria/models/calculation_record.py)
- [base_calculator.py](file://src/pillars/gematria/services/base_calculator.py)
- [hebrew_calculator.py](file://src/pillars/gematria/services/hebrew_calculator.py)
- [greek_calculator.py](file://src/pillars/gematria/services/greek_calculator.py)
- [tq_calculator.py](file://src/pillars/gematria/services/tq_calculator.py)
- [calculation_repository.py](file://src/pillars/gematria/repositories/calculation_repository.py)
- [sqlite_calculation_repository.py](file://src/pillars/gematria/repositories/sqlite_calculation_repository.py)
- [verse_parser.py](file://src/pillars/gematria/utils/verse_parser.py)
- [numeric_utils.py](file://src/pillars/gematria/utils/numeric_utils.py)
- [smart_filter_service.py](file://src/pillars/gematria/services/smart_filter_service.py)
- [text_analysis_service.py](file://src/pillars/gematria/services/text_analysis_service.py)
- [holy_book_teacher_window.py](file://src/pillars/gematria/ui/holy_book_teacher_window.py)
- [gematria_calculator_window.py](file://src/pillars/gematria/ui/gematria_calculator_window.py)
- [text_analysis_window.py](file://src/pillars/gematria/ui/text_analysis/main_window.py)
- [acrostic_service.py](file://src/pillars/gematria/services/acrostic_service.py)
- [chiasmus_service.py](file://src/pillars/gematria/services/chiasmus_service.py)
- [els_service.py](file://src/pillars/gematria/services/els_service.py)
- [acrostics_window.py](file://src/pillars/gematria/ui/acrostics_window.py)
- [chiastic_window.py](file://src/pillars/gematria/ui/chiastic_window.py)
- [els_search_window.py](file://src/pillars/gematria/ui/els_search_window.py)
- [els_models.py](file://src/pillars/gematria/models/els_models.py)
</cite>

## Update Summary
**Changes Made**   
- Added new sections for acrostics, chiasmus, and ELS (Equidistant Letter Sequences) detection capabilities
- Updated architecture overview to include new text analysis components
- Enhanced detailed component analysis with new service and UI components
- Updated dependency analysis to reflect new modules and their relationships
- Added new diagrams for the Strategy Pattern implementation of text analysis services
- Updated troubleshooting guide with new issues related to enhanced text analysis

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
The Gematria pillar is a modular component within the isopgem application dedicated to numerological analysis using Hebrew, Greek, and English gematria systems. This documentation provides a comprehensive architectural overview of the pillar, detailing its internal structure, component interactions, and specialized features. The system follows a standard pillar pattern with distinct layers for UI components, service logic, data models, repositories, and utility functions. The architecture implements the Strategy Pattern to enable pluggable calculator types, allowing flexible analysis across different gematria systems. The gematria_hub serves as the central interface that integrates all subcomponents into a cohesive user experience. Recent enhancements have expanded the text analysis capabilities to include acrostics, chiasmus, and ELS (Equidistant Letter Sequences) detection, providing advanced tools for discovering hidden patterns in sacred texts.

## Project Structure
The Gematria pillar follows a well-organized directory structure that separates concerns according to the standard pillar pattern. The component is located at `src/pillars/gematria/` and contains subdirectories for models, repositories, services, UI components, and utilities. The models directory contains data definitions for calculation entities and records, while the repositories directory implements persistence logic with both Whoosh and SQLite backends. The services directory houses the core business logic including the calculation service and various calculator implementations. The UI directory contains the hub, calculator windows, and text analysis tools, while the utils directory provides supporting functions for verse parsing and numeric operations. Recent additions include specialized services for acrostics, chiasmus, and ELS detection, along with corresponding UI components for these advanced analysis features.

```mermaid
graph TD
subgraph "Gematria Pillar"
subgraph "UI"
Hub[gematria_hub.py]
Calculator[calculator_window.py]
TextAnalysis[text_analysis_window.py]
HolyBook[holy_book_teacher_window.py]
Acrostics[acrostics_window.py]
Chiasmus[chiastic_window.py]
ELS[els_search_window.py]
end
subgraph "Services"
CalculationService[calculation_service.py]
BaseCalculator[base_calculator.py]
Hebrew[hebrew_calculator.py]
Greek[greek_calculator.py]
TQ[tq_calculator.py]
SmartFilter[smart_filter_service.py]
TextAnalysisService[text_analysis_service.py]
AcrosticService[acrostic_service.py]
ChiasmusService[chiasmus_service.py]
ELSService[els_service.py]
end
subgraph "Models"
Entity[calculation_entity.py]
Record[calculation_record.py]
ELSModels[els_models.py]
end
subgraph "Repositories"
WhooshRepo[calculation_repository.py]
SQLiteRepo[sqlite_calculation_repository.py]
end
subgraph "Utils"
VerseParser[verse_parser.py]
NumericUtils[numeric_utils.py]
end
Hub --> CalculationService
CalculationService --> BaseCalculator
BaseCalculator --> Hebrew
BaseCalculator --> Greek
BaseCalculator --> TQ
CalculationService --> WhooshRepo
CalculationService --> SQLiteRepo
TextAnalysis --> TextAnalysisService
TextAnalysisService --> SmartFilter
TextAnalysisService --> VerseParser
TextAnalysisService --> NumericUtils
Hub --> Acrostics
Hub --> Chiasmus
Hub --> ELS
Acrostics --> AcrosticService
Chiasmus --> ChiasmusService
ELS --> ELSService
ELSService --> ELSModels
end
```

**Diagram sources**
- [gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py)
- [calculation_service.py](file://src/pillars/gematria/services/calculation_service.py)
- [base_calculator.py](file://src/pillars/gematria/services/base_calculator.py)
- [hebrew_calculator.py](file://src/pillars/gematria/services/hebrew_calculator.py)
- [greek_calculator.py](file://src/pillars/gematria/services/greek_calculator.py)
- [tq_calculator.py](file://src/pillars/gematria/services/tq_calculator.py)
- [calculation_repository.py](file://src/pillars/gematria/repositories/calculation_repository.py)
- [sqlite_calculation_repository.py](file://src/pillars/gematria/repositories/sqlite_calculation_repository.py)
- [verse_parser.py](file://src/pillars/gematria/utils/verse_parser.py)
- [numeric_utils.py](file://src/pillars/gematria/utils/numeric_utils.py)
- [smart_filter_service.py](file://src/pillars/gematria/services/smart_filter_service.py)
- [text_analysis_service.py](file://src/pillars/gematria/services/text_analysis_service.py)
- [acrostic_service.py](file://src/pillars/gematria/services/acrostic_service.py)
- [chiasmus_service.py](file://src/pillars/gematria/services/chiasmus_service.py)
- [els_service.py](file://src/pillars/gematria/services/els_service.py)
- [els_models.py](file://src/pillars/gematria/models/els_models.py)
- [acrostics_window.py](file://src/pillars/gematria/ui/acrostics_window.py)
- [chiastic_window.py](file://src/pillars/gematria/ui/chiastic_window.py)
- [els_search_window.py](file://src/pillars/gematria/ui/els_search_window.py)

**Section sources**
- [__init__.py](file://src/pillars/gematria/__init__.py)
- [gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py)

## Core Components
The Gematria pillar consists of several core components that work together to provide comprehensive numerological analysis capabilities. The system is built around a service layer that processes text input through various calculator strategies to generate numerical insights. The calculation_service acts as the central coordinator, managing the lifecycle of calculation records and orchestrating interactions between calculators, repositories, and utility functions. The base_calculator defines an abstract interface that all specific calculator implementations follow, enabling the Strategy Pattern for pluggable calculation methods. The repository layer provides persistence through both Whoosh-based and SQLite-based implementations, allowing for flexible storage and retrieval of calculation results. Utility functions like verse_parser and numeric_utils provide specialized capabilities for text processing and numeric analysis. New text analysis components include the acrostic_service for discovering hidden messages in text, the chiasmus_service for identifying symmetrical patterns based on gematria values, and the els_service for detecting equidistant letter sequences in sacred texts.

**Section sources**
- [calculation_service.py](file://src/pillars/gematria/services/calculation_service.py)
- [base_calculator.py](file://src/pillars/gematria/services/base_calculator.py)
- [calculation_repository.py](file://src/pillars/gematria/repositories/calculation_repository.py)
- [sqlite_calculation_repository.py](file://src/pillars/gematria/repositories/sqlite_calculation_repository.py)
- [verse_parser.py](file://src/pillars/gematria/utils/verse_parser.py)
- [numeric_utils.py](file://src/pillars/gematria/utils/numeric_utils.py)
- [acrostic_service.py](file://src/pillars/gematria/services/acrostic_service.py)
- [chiasmus_service.py](file://src/pillars/gematria/services/chiasmus_service.py)
- [els_service.py](file://src/pillars/gematria/services/els_service.py)

## Architecture Overview
The Gematria pillar follows a layered architecture with clear separation of concerns between presentation, business logic, and data access layers. The system implements the Strategy Pattern to allow pluggable calculator types, enabling flexible analysis across different gematria systems. The architecture centers around the calculation_service, which coordinates the flow of data between UI components, calculator strategies, and persistence mechanisms. When a user inputs text for analysis, the request flows through the service layer where it is processed by the appropriate calculator strategy based on the selected gematria system. The results are then stored in the repository layer and made available for retrieval and further analysis. The enhanced text analysis capabilities include specialized services for detecting acrostics (hidden messages formed by first or last letters of words or lines), chiasmus (symmetrical patterns based on gematria values), and ELS (Equidistant Letter Sequences) which search for hidden words by sampling every n-th letter from sacred texts.

```mermaid
graph TD
A[User Interface] --> B[Calculation Service]
B --> C[Calculator Strategy]
C --> D[Text Processing]
D --> E[Numerical Analysis]
E --> F[Result Generation]
F --> G[Repository Storage]
G --> H[Data Retrieval]
H --> I[User Interface]
B --> J[Utility Functions]
J --> K[Verse Parsing]
J --> L[Numeric Utilities]
B --> M[Smart Filtering]
I --> N[Visualization]
N --> O[Insights]
P[Text Analysis] --> Q[Acrostic Service]
P --> R[Chiasmus Service]
P --> S[ELS Service]
Q --> T[Hidden Messages]
R --> U[Symmetrical Patterns]
S --> V[Equidistant Sequences]
P --> W[Text Analysis Service]
W --> X[Value Matching]
W --> Y[Statistics]
```

**Diagram sources**
- [calculation_service.py](file://src/pillars/gematria/services/calculation_service.py)
- [base_calculator.py](file://src/pillars/gematria/services/base_calculator.py)
- [calculation_repository.py](file://src/pillars/gematria/repositories/calculation_repository.py)
- [verse_parser.py](file://src/pillars/gematria/utils/verse_parser.py)
- [numeric_utils.py](file://src/pillars/gematria/utils/numeric_utils.py)
- [smart_filter_service.py](file://src/pillars/gematria/services/smart_filter_service.py)
- [text_analysis_service.py](file://src/pillars/gematria/services/text_analysis_service.py)
- [acrostic_service.py](file://src/pillars/gematria/services/acrostic_service.py)
- [chiasmus_service.py](file://src/pillars/gematria/services/chiasmus_service.py)
- [els_service.py](file://src/pillars/gematria/services/els_service.py)

## Detailed Component Analysis

### Service Layer Analysis
The service layer of the Gematria pillar is responsible for coordinating the core business logic and orchestrating interactions between different components. The calculation_service serves as the primary entry point for all calculation operations, providing methods for saving, updating, deleting, and searching calculation records. The service layer implements the Strategy Pattern through the base_calculator abstract class, which defines a common interface for all calculator implementations. This design allows the system to support multiple gematria systems (Hebrew, Greek, and English/TQ) while maintaining a consistent API for calculation operations. The enhanced text analysis capabilities include specialized services for detecting acrostics, chiasmus, and ELS patterns, each implementing their own algorithms for discovering hidden messages and patterns in text.

#### Strategy Pattern Implementation
The Strategy Pattern is implemented through the GematriaCalculator abstract base class, which defines the contract that all calculator implementations must follow. Each concrete calculator (Hebrew, Greek, TQ) inherits from this base class and provides its own implementation of the letter-to-value mapping and calculation logic. This design enables the system to easily extend support for new gematria systems by simply creating a new class that implements the required interface. Similarly, the text analysis services follow a similar pattern, with specialized services for acrostics, chiasmus, and ELS detection, each implementing their own algorithms for pattern discovery.

```mermaid
classDiagram
class GematriaCalculator {
<<abstract>>
+_letter_values : Dict[str, int]
+__init__()
+_initialize_mapping() : Dict[str, int]
+name : str
+normalize_text(text : str) : str
+calculate(text : str) : int
+get_letter_value(char : str) : int
+get_breakdown(text : str) : list
}
class HebrewGematriaCalculator {
+name : str
+_initialize_mapping() : Dict[str, int]
}
class GreekGematriaCalculator {
+name : str
+_initialize_mapping() : Dict[str, int]
}
class TQGematriaCalculator {
+name : str
+_initialize_mapping() : Dict[str, int]
}
GematriaCalculator <|-- HebrewGematriaCalculator
GematriaCalculator <|-- GreekGematriaCalculator
GematriaCalculator <|-- TQGematriaCalculator
class TextAnalysisService {
<<abstract>>
+find_value_matches(text : str, target_value : int, calculator : GematriaCalculator) : List[Tuple[str, int, int]]
+calculate_stats(text : str, calculator : GematriaCalculator) : Dict[str, Any]
+parse_verses(text : str, document_id : Optional[str]) : Dict[str, Any]
}
class AcrosticService {
+find_acrostics(text : str, check_first : bool, check_last : bool, mode : str) : List[AcrosticResult]
}
class ChiasmusService {
+scan_text(text : str, calculator : GematriaCalculator, max_depth : int) : List[ChiasmusPattern]
}
class ELSService {
+search_els(text : str, term : str, skip : Optional[int], min_skip : int, max_skip : int, direction : str) : ELSSearchSummary
+search_sequence(text : str, term : str, sequence_type : str, direction : str) : ELSSearchSummary
+search_chain(text : str, term : str, reverse : bool, max_results : int) : ChainSearchSummary
}
TextAnalysisService <|-- AcrosticService
TextAnalysisService <|-- ChiasmusService
TextAnalysisService <|-- ELSService
```

**Diagram sources**
- [base_calculator.py](file://src/pillars/gematria/services/base_calculator.py)
- [hebrew_calculator.py](file://src/pillars/gematria/services/hebrew_calculator.py)
- [greek_calculator.py](file://src/pillars/gematria/services/greek_calculator.py)
- [tq_calculator.py](file://src/pillars/gematria/services/tq_calculator.py)
- [acrostic_service.py](file://src/pillars/gematria/services/acrostic_service.py)
- [chiasmus_service.py](file://src/pillars/gematria/services/chiasmus_service.py)
- [els_service.py](file://src/pillars/gematria/services/els_service.py)

**Section sources**
- [base_calculator.py](file://src/pillars/gematria/services/base_calculator.py)
- [hebrew_calculator.py](file://src/pillars/gematria/services/hebrew_calculator.py)
- [greek_calculator.py](file://src/pillars/gematria/services/greek_calculator.py)
- [tq_calculator.py](file://src/pillars/gematria/services/tq_calculator.py)
- [acrostic_service.py](file://src/pillars/gematria/services/acrostic_service.py)
- [chiasmus_service.py](file://src/pillars/gematria/services/chiasmus_service.py)
- [els_service.py](file://src/pillars/gematria/services/els_service.py)

### Data Model Analysis
The data model of the Gematria pillar consists of two primary components: CalculationRecord and CalculationEntity. The CalculationRecord class represents the domain model for a saved gematria calculation, containing all the relevant metadata and calculation details. The CalculationEntity class represents the persistence model that maps to the database schema. This separation of concerns allows the system to maintain a clean domain model while providing flexibility in how data is stored and retrieved. The enhanced text analysis capabilities introduce new data models for representing acrostic results, chiasmus patterns, and ELS findings, including detailed information about the discovered patterns and their positions in the source text.

#### Data Model Relationships
The data model implements a pattern where the domain model (CalculationRecord) is converted to and from the persistence model (CalculationEntity) through dedicated methods. This approach provides a clear boundary between the business logic layer and the data access layer, allowing each to evolve independently. The new text analysis models include AcrosticResult for representing discovered acrostics, ChiasmusPattern for symmetrical patterns, and ELSResult for equidistant letter sequences, each containing detailed information about the discovered patterns and their positions in the source text.

```mermaid
classDiagram
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
+to_dict() : Dict
+from_dict(data : Dict) : CalculationRecord
+__str__() : str
}
class CalculationEntity {
+id : Mapped[str]
+text : Mapped[str]
+normalized_text : Mapped[str]
+value : Mapped[int]
+language : Mapped[str]
+method : Mapped[str]
+notes : Mapped[str]
+source : Mapped[str]
+tags : Mapped[str]
+breakdown : Mapped[str]
+character_count : Mapped[int]
+normalized_hash : Mapped[str]
+user_rating : Mapped[int]
+is_favorite : Mapped[bool]
+category : Mapped[str]
+related_ids : Mapped[str]
+date_created : Mapped[datetime]
+date_modified : Mapped[datetime]
+update_from_record(record : CalculationRecord) : None
+to_record() : CalculationRecord
}
class AcrosticResult {
+found_word : str
+method : str
+source_indices : List[int]
+source_text_units : List[str]
+is_valid_word : bool
+__init__(found_word : str, method : str, source_indices : List[int], source_text_units : List[str], is_valid_word : bool)
+__repr__() : str
}
class ChiasmusPattern {
+center_index : Optional[int]
+depth : int
+left_indices : List[int]
+right_indices : List[int]
+source_units : List[str]
+values : List[int]
}
class ELSResult {
+term : str
+skip : int
+start_pos : int
+direction : str
+letter_positions : List[int]
+intervening_segments : List[ELSInterveningSegment]
+term_gematria : int
+skip_gematria : int
+total_gematria : int
+get_row_col_coords(columns : int) : List[Tuple[int, int]]
}
class ELSSearchSummary {
+results : List[ELSResult]
+source_text_length : int
+source_document : Optional[str]
+total_hits : int
+skip_distribution : dict
}
CalculationEntity --> CalculationRecord : "converts to/from"
```

**Diagram sources**
- [calculation_record.py](file://src/pillars/gematria/models/calculation_record.py)
- [calculation_entity.py](file://src/pillars/gematria/models/calculation_entity.py)
- [acrostic_service.py](file://src/pillars/gematria/services/acrostic_service.py)
- [chiasmus_service.py](file://src/pillars/gematria/services/chiasmus_service.py)
- [els_service.py](file://src/pillars/gematria/services/els_service.py)
- [els_models.py](file://src/pillars/gematria/models/els_models.py)

**Section sources**
- [calculation_record.py](file://src/pillars/gematria/models/calculation_record.py)
- [calculation_entity.py](file://src/pillars/gematria/models/calculation_entity.py)
- [acrostic_service.py](file://src/pillars/gematria/services/acrostic_service.py)
- [chiasmus_service.py](file://src/pillars/gematria/services/chiasmus_service.py)
- [els_service.py](file://src/pillars/gematria/services/els_service.py)
- [els_models.py](file://src/pillars/gematria/models/els_models.py)

### Repository Layer Analysis
The repository layer provides persistence capabilities for the Gematria pillar through two distinct implementations: a Whoosh-based repository and a SQLite-based repository. The CalculationRepository class implements a Whoosh-based storage system that provides full-text search capabilities for calculation records. The SQLiteCalculationRepository class provides a relational database implementation using SQLAlchemy, offering robust transaction support and complex querying capabilities. Both repositories implement the same interface, allowing them to be used interchangeably within the application.

#### Repository Implementation Details
The repository layer follows the Repository Pattern, providing an abstraction over the underlying data storage mechanisms. This design allows the service layer to interact with the repositories through a consistent API, regardless of the specific storage technology being used. The repositories handle all data access operations, including saving, retrieving, updating, and deleting calculation records.

```mermaid
classDiagram
class CalculationRepository {
+index_dir : Path
+schema : Schema
+ix : Index
+_text_parser : MultifieldParser
+_match_all_query : Every
+__init__(index_dir : Optional[str])
+save(record : CalculationRecord) : CalculationRecord
+get_by_id(record_id : str) : Optional[CalculationRecord]
+delete(record_id : str) : bool
+search(query_str : Optional[str], language : Optional[str], value : Optional[int], tags : Optional[List[str]], favorites_only : bool, limit : int, page : int, summary_only : bool) : List[CalculationRecord]
+get_all(limit : int) : List[CalculationRecord]
+get_by_value(value : int, limit : int) : List[CalculationRecord]
+get_favorites(limit : int) : List[CalculationRecord]
+get_by_tags(tags : List[str], limit : int) : List[CalculationRecord]
+_result_to_summary(result) : CalculationRecord
+_result_to_record(result) : CalculationRecord
}
class SQLiteCalculationRepository {
+_session_factory : Callable[[], Session]
+__init__(session_factory : Callable[[], Session])
+_session() : Iterator[Session]
+save(record : CalculationRecord) : CalculationRecord
+get_by_id(record_id : str) : Optional[CalculationRecord]
+delete(record_id : str) : bool
+search(query_str : Optional[str], language : Optional[str], value : Optional[int], tags : Optional[Sequence[str]], favorites_only : bool, limit : int, page : int, summary_only : bool) : List[CalculationRecord]
+get_all(limit : int) : List[CalculationRecord]
+get_by_value(value : int, limit : int) : List[CalculationRecord]
+get_favorites(limit : int) : List[CalculationRecord]
+get_by_tags(tags : List[str], limit : int) : List[CalculationRecord]
}
CalculationRepository <|-- SQLiteCalculationRepository : "implements same interface"
```

**Diagram sources**
- [calculation_repository.py](file://src/pillars/gematria/repositories/calculation_repository.py)
- [sqlite_calculation_repository.py](file://src/pillars/gematria/repositories/sqlite_calculation_repository.py)

**Section sources**
- [calculation_repository.py](file://src/pillars/gematria/repositories/calculation_repository.py)
- [sqlite_calculation_repository.py](file://src/pillars/gematria/repositories/sqlite_calculation_repository.py)

### UI Component Analysis
The UI components of the Gematria pillar provide a cohesive interface for users to interact with the numerological analysis tools. The gematria_hub serves as the central launcher interface, providing access to all available tools including the gematria calculator, saved calculations browser, batch calculator, text analysis, database tools, and methods reference. Each tool is implemented as a separate window component that follows a consistent design pattern and integrates with the shared window manager. The enhanced text analysis capabilities include specialized UI components for acrostics, chiasmus, and ELS detection, providing intuitive interfaces for discovering hidden patterns in sacred texts.

#### UI Component Relationships
The UI components are organized in a hierarchical structure with the gematria_hub at the top level, coordinating the opening and management of other tool windows. The hub uses the window manager to instantiate and display the various tool windows, passing the necessary dependencies such as calculator instances and service objects. The new text analysis windows provide specialized interfaces for exploring acrostics, chiasmus patterns, and ELS sequences, with visualization tools to help users understand the discovered patterns.

```mermaid
classDiagram
class GematriaHub {
+window_manager : WindowManager
+__init__(window_manager : WindowManager)
+_setup_ui()
+_create_primary_button(label : str, base_color : str, hover_color : str, callback)
+_open_calculator()
+_open_saved_calculations()
+_open_batch_calculator()
+_open_text_analysis()
+_open_database_tools()
+_open_methods_reference()
+_open_els_search()
+_open_acrostics()
+_open_chiasmus()
}
class GematriaCalculatorWindow {
+__init__(calculators : List[GematriaCalculator])
+_setup_ui()
+_on_calculate()
+_on_save_calculation()
}
class TextAnalysisWindow {
+__init__(calculators : List[GematriaCalculator])
+_setup_ui()
+_on_analyze_text()
+_on_find_matches()
+_on_save_analysis()
}
class HolyBookTeacherWindow {
+document_id : int
+document_title : str
+allow_inline : bool
+_current_payload : Optional[Dict[str, Any]]
+_undo_stack : List[Tuple[List[Dict[str, Any]], str]]
+_redo_stack : List[Tuple[List[Dict[str, Any]], str]]
+__init__(document_id : int, document_title : str, allow_inline : bool, parent)
+_build_ui()
+_load_payload(from_parser : bool)
+_save_current_payload()
+_on_table_context_menu(pos)
+_on_table_double_clicked(row : int, col : int)
+_confirm_verse(row : int)
+_edit_verse(row : int)
+_merge_next(row : int)
+_split_verse(row : int)
+_renumber_verse(row : int)
+_ignore_verse(row : int)
+_jump_to_document(row : int)
+_create_rule_from_row(row : int)
}
class AcrosticsWindow {
+service : AcrosticService
+dict_service : CorpusDictionaryService
+__init__(window_manager : Optional[WindowManager], parent : Optional[QWidget])
+setup_ui()
+on_result_double_clicked(row : int, col : int)
+load_dictionary()
+view_dictionary()
+load_document_dialog()
+load_document_text(doc_id : int)
+calculate_gematria(text : str) : int
+run_search()
}
class ChiasticWindow {
+service : ChiasmusService
+patterns : List[ChiasmusPattern]
+calculators : Dict[str, GematriaCalculator]
+__init__(window_manager : Optional[WindowManager], parent : Optional[QWidget])
+setup_ui()
+load_document_dialog()
+load_document_text(doc_id : int)
+scan_text()
+display_pattern(row : int)
+generate_viz_html(p : ChiasmusPattern) : str
}
class ELSSearchWindow {
+_service : ELSSearchService
+_stripped_text : str
+_position_map : List[int]
+_current_results : List[ELSResult]
+__init__(window_manager : Optional[WindowManager], parent : Optional[QWidget])
+_setup_ui()
+_create_left_pane() : QWidget
+_create_right_pane() : QWidget
+_on_load_document()
+_on_paste_text()
+_on_load_from_database()
+_load_text(text : str, source : str)
+_on_factor_selected(index : int)
+_on_apply_grid()
+_on_search()
+_apply_gematria_filter()
+_on_export()
+_on_clear()
+_on_chain_result_selected(result : ChainResult)
}
GematriaHub --> GematriaCalculatorWindow : "opens"
GematriaHub --> TextAnalysisWindow : "opens"
GematriaHub --> HolyBookTeacherWindow : "opens"
GematriaHub --> AcrosticsWindow : "opens"
GematriaHub --> ChiasticWindow : "opens"
GematriaHub --> ELSSearchWindow : "opens"
TextAnalysisWindow --> HolyBookTeacherWindow : "integrates with"
```

**Diagram sources**
- [gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py)
- [gematria_calculator_window.py](file://src/pillars/gematria/ui/gematria_calculator_window.py)
- [text_analysis/main_window.py](file://src/pillars/gematria/ui/text_analysis/main_window.py)
- [holy_book_teacher_window.py](file://src/pillars/gematria/ui/holy_book_teacher_window.py)
- [acrostics_window.py](file://src/pillars/gematria/ui/acrostics_window.py)
- [chiastic_window.py](file://src/pillars/gematria/ui/chiastic_window.py)
- [els_search_window.py](file://src/pillars/gematria/ui/els_search_window.py)

**Section sources**
- [gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py)
- [gematria_calculator_window.py](file://src/pillars/gematria/ui/gematria_calculator_window.py)
- [text_analysis/main_window.py](file://src/pillars/gematria/ui/text_analysis/main_window.py)
- [holy_book_teacher_window.py](file://src/pillars/gematria/ui/holy_book_teacher_window.py)
- [acrostics_window.py](file://src/pillars/gematria/ui/acrostics_window.py)
- [chiastic_window.py](file://src/pillars/gematria/ui/chiastic_window.py)
- [els_search_window.py](file://src/pillars/gematria/ui/els_search_window.py)

### Utility Functions Analysis
The utility functions in the Gematria pillar provide specialized capabilities that support the core analysis features. The verse_parser module contains functions for parsing documents into numbered verses, which is essential for verse-based analysis in holy texts. The numeric_utils module provides functions for handling numeric face values in text, allowing the system to account for explicit numbers in addition to gematria calculations. The smart_filter_service uses NLP techniques to filter out linguistically invalid phrases, improving the quality of analysis results. The enhanced text analysis capabilities include specialized utility functions for processing and visualizing acrostics, chiasmus patterns, and ELS sequences.

#### Utility Function Workflows
The utility functions are designed to be used as supporting components within the larger analysis workflow. They are typically called from within the service layer or UI components to provide specific processing capabilities that are not part of the core calculation logic.

```mermaid
flowchart TD
A[Input Text] --> B{Contains Numbers?}
B --> |Yes| C[sum_numeric_face_values]
B --> |No| D[Proceed to Calculation]
C --> D
D --> E[Calculate Gematria Value]
E --> F{Multiple Phrases?}
F --> |Yes| G[SmartFilterService]
F --> |No| H[Return Result]
G --> I[Filter Invalid Phrases]
I --> H
J[Document Text] --> K[parse_verses]
K --> L[Verse Objects]
L --> M[Verse-Based Analysis]
N[Text for Acrostics] --> O[find_acrostics]
O --> P[Acrostic Results]
Q[Text for Chiasmus] --> R[scan_text]
R --> S[Chiasmus Patterns]
T[Text for ELS] --> U[search_els]
U --> V[ELS Results]
```

**Diagram sources**
- [verse_parser.py](file://src/pillars/gematria/utils/verse_parser.py)
- [numeric_utils.py](file://src/pillars/gematria/utils/numeric_utils.py)
- [smart_filter_service.py](file://src/pillars/gematria/services/smart_filter_service.py)
- [acrostic_service.py](file://src/pillars/gematria/services/acrostic_service.py)
- [chiasmus_service.py](file://src/pillars/gematria/services/chiasmus_service.py)
- [els_service.py](file://src/pillars/gematria/services/els_service.py)

**Section sources**
- [verse_parser.py](file://src/pillars/gematria/utils/verse_parser.py)
- [numeric_utils.py](file://src/pillars/gematria/utils/numeric_utils.py)
- [smart_filter_service.py](file://src/pillars/gematria/services/smart_filter_service.py)
- [acrostic_service.py](file://src/pillars/gematria/services/acrostic_service.py)
- [chiasmus_service.py](file://src/pillars/gematria/services/chiasmus_service.py)
- [els_service.py](file://src/pillars/gematria/services/els_service.py)

## Dependency Analysis
The Gematria pillar has a well-defined dependency structure that follows the dependency inversion principle. Higher-level components depend on abstractions rather than concrete implementations, allowing for flexibility and testability. The calculation_service depends on the abstract GematriaCalculator interface rather than specific calculator implementations, enabling the Strategy Pattern. The service layer depends on the repository interface rather than specific repository implementations, allowing the system to switch between Whoosh and SQLite storage backends. The UI components depend on the service layer and shared utilities rather than directly accessing lower-level components. The enhanced text analysis capabilities introduce new dependencies for acrostics, chiasmus, and ELS detection, with specialized services and models for each analysis type.

```mermaid
graph TD
UI[gematria_hub] --> Service[calculation_service]
Service --> Calculator[GematriaCalculator]
Service --> Repository[calculation_repository]
Service --> Utils[utility functions]
Calculator --> Hebrew[HebrewGematriaCalculator]
Calculator --> Greek[GreekGematriaCalculator]
Calculator --> TQ[TQGematriaCalculator]
Repository --> Whoosh[calculation_repository]
Repository --> SQLite[sqlite_calculation_repository]
UI --> TextAnalysis[text_analysis_service]
TextAnalysis --> SmartFilter[smart_filter_service]
TextAnalysis --> VerseParser[verse_parser]
TextAnalysis --> NumericUtils[numeric_utils]
UI --> Acrostics[acrostic_service]
UI --> Chiasmus[chiasmus_service]
UI --> ELS[els_service]
Acrostics --> Dictionary[corpus_dictionary_service]
Chiasmus --> Calculator
ELS --> ELSModels
```

**Diagram sources**
- [gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py)
- [calculation_service.py](file://src/pillars/gematria/services/calculation_service.py)
- [base_calculator.py](file://src/pillars/gematria/services/base_calculator.py)
- [hebrew_calculator.py](file://src/pillars/gematria/services/hebrew_calculator.py)
- [greek_calculator.py](file://src/pillars/gematria/services/greek_calculator.py)
- [tq_calculator.py](file://src/pillars/gematria/services/tq_calculator.py)
- [calculation_repository.py](file://src/pillars/gematria/repositories/calculation_repository.py)
- [sqlite_calculation_repository.py](file://src/pillars/gematria/repositories/sqlite_calculation_repository.py)
- [text_analysis_service.py](file://src/pillars/gematria/services/text_analysis_service.py)
- [smart_filter_service.py](file://src/pillars/gematria/services/smart_filter_service.py)
- [verse_parser.py](file://src/pillars/gematria/utils/verse_parser.py)
- [numeric_utils.py](file://src/pillars/gematria/utils/numeric_utils.py)
- [acrostic_service.py](file://src/pillars/gematria/services/acrostic_service.py)
- [chiasmus_service.py](file://src/pillars/gematria/services/chiasmus_service.py)
- [els_service.py](file://src/pillars/gematria/services/els_service.py)
- [corpus_dictionary_service.py](file://src/pillars/gematria/services/corpus_dictionary_service.py)
- [els_models.py](file://src/pillars/gematria/models/els_models.py)

**Section sources**
- [gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py)
- [calculation_service.py](file://src/pillars/gematria/services/calculation_service.py)
- [base_calculator.py](file://src/pillars/gematria/services/base_calculator.py)
- [calculation_repository.py](file://src/pillars/gematria/repositories/calculation_repository.py)
- [text_analysis_service.py](file://src/pillars/gematria/services/text_analysis_service.py)
- [acrostic_service.py](file://src/pillars/gematria/services/acrostic_service.py)
- [chiasmus_service.py](file://src/pillars/gematria/services/chiasmus_service.py)
- [els_service.py](file://src/pillars/gematria/services/els_service.py)

## Performance Considerations
The Gematria pillar has been designed with performance considerations in mind, particularly for text analysis operations that may involve processing large documents. The text_analysis_service implements a fast scan algorithm for finding value matches, which pre-calculates token values and uses a sliding window approach to efficiently identify phrases that match a target gematria value. The repository layer provides options for both full and summary record retrieval, allowing the system to minimize data transfer when only basic information is needed. The smart_filter_service uses batch processing with spaCy's NLP pipeline to efficiently analyze multiple phrases simultaneously. For large-scale analysis, the system can leverage the SQLite backend for faster querying and indexing capabilities compared to the Whoosh implementation. The enhanced text analysis capabilities include optimized algorithms for acrostics, chiasmus, and ELS detection, with careful consideration of performance implications when processing large texts.

## Troubleshooting Guide
When encountering issues with the Gematria pillar, consider the following common problems and solutions:

1. **Calculator not producing expected results**: Verify that the correct calculator type is selected and that the input text is properly formatted. Check for any diacritical marks or special characters that might affect the calculation.

2. **Performance issues with large documents**: For text analysis on large documents, consider using the SQLite repository backend instead of Whoosh, as it may provide better performance for large datasets. Also, adjust the max_words parameter in the find_value_matches method to limit the search space.

3. **Verse parsing not working correctly**: Ensure that the document contains properly formatted verse numbers. The verse_parser uses heuristics to identify verse markers, so inconsistent formatting may cause parsing issues. Use the Holy Book Teacher mode to manually correct and save verse boundaries.

4. **Smart filtering removing valid phrases**: The smart_filter_service uses NLP rules to identify linguistically valid phrases. If valid phrases are being filtered out, check the spaCy model loading and ensure that the "en_core_web_sm" model is properly installed.

5. **Repository storage issues**: If calculations are not being saved or retrieved correctly, verify that the storage directory has proper read/write permissions. For the SQLite backend, check that the database file is not corrupted and that the schema is up to date.

6. **Acrostics not being detected**: Ensure that the corpus dictionary is loaded. The acrostic_service requires a loaded dictionary to validate discovered words. Use the "Load Corpus Dictionary" button in the Acrostics window to load the dictionary.

7. **Chiasmus patterns not appearing**: Verify that the text contains sufficient words with matching gematria values. The chiasmus_service requires symmetrical patterns of gematria values to detect chiasmus structures.

8. **ELS search not finding expected sequences**: Check that the text has been properly stripped of non-letter characters. The els_service works with stripped text, so ensure that the input text is clean and properly formatted.

**Section sources**
- [calculation_service.py](file://src/pillars/gematria/services/calculation_service.py)
- [text_analysis_service.py](file://src/pillars/gematria/services/text_analysis_service.py)
- [verse_parser.py](file://src/pillars/gematria/utils/verse_parser.py)
- [smart_filter_service.py](file://src/pillars/gematria/services/smart_filter_service.py)
- [calculation_repository.py](file://src/pillars/gematria/repositories/calculation_repository.py)
- [sqlite_calculation_repository.py](file://src/pillars/gematria/repositories/sqlite_calculation_repository.py)
- [acrostic_service.py](file://src/pillars/gematria/services/acrostic_service.py)
- [chiasmus_service.py](file://src/pillars/gematria/services/chiasmus_service.py)
- [els_service.py](file://src/pillars/gematria/services/els_service.py)

## Conclusion
The Gematria pillar provides a comprehensive framework for numerological analysis using Hebrew, Greek, and English gematria systems. The architecture follows a modular design with clear separation of concerns between UI components, service logic, data models, repositories, and utility functions. The implementation of the Strategy Pattern through the base_calculator abstract class enables flexible support for multiple gematria systems while maintaining a consistent API. The system integrates specialized features like the Holy Book teacher mode, smart filtering, and verse-based analysis to provide advanced capabilities for textual analysis. The repository layer offers both Whoosh-based and SQLite-based storage options, providing flexibility in how calculation results are persisted and retrieved. Recent enhancements have expanded the text analysis capabilities to include acrostics, chiasmus, and ELS (Equidistant Letter Sequences) detection, providing powerful tools for discovering hidden patterns in sacred texts. Overall, the Gematria pillar demonstrates a well-structured, extensible architecture that effectively supports complex numerological analysis tasks.