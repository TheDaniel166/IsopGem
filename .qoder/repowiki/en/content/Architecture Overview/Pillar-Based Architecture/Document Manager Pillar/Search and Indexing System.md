# Search and Indexing System

<cite>
**Referenced Files in This Document**   
- [document_search_window.py](file://src/pillars/document_manager/ui/document_search_window.py)
- [search_results_panel.py](file://src/pillars/document_manager/ui/search_results_panel.py)
- [search_features.py](file://src/pillars/document_manager/ui/search_features.py)
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py)
- [document.py](file://src/pillars/document_manager/models/document.py)
- [verse_teacher_service.py](file://src/pillars/document_manager/services/verse_teacher_service.py)
- [document_library.py](file://src/pillars/document_manager/ui/document_library.py)
- [text_analysis_service.py](file://src/pillars/gematria/services/text_analysis_service.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Indexing Strategies](#indexing-strategies)
4. [Query Parsing and Search Implementation](#query-parsing-and-search-implementation)
5. [Search Interfaces](#search-interfaces)
6. [Advanced Search Features](#advanced-search-features)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Configuration Options](#configuration-options)

## Introduction
The Search and Indexing System in the Document Manager pillar provides comprehensive full-text search capabilities using the Whoosh library. This system enables users to efficiently search through large document collections with advanced features including verse-level filtering, Holy Book teacher mode integration, and gematria analysis. The implementation combines a robust indexing strategy with sophisticated query parsing and result ranking to deliver accurate and relevant search results. The system is designed to handle document updates efficiently while maintaining search accuracy and performance.

## Architecture Overview
The Search and Indexing System follows a layered architecture with clear separation of concerns between the user interface, service layer, and repository layer. The system uses Whoosh as the underlying search engine for full-text search capabilities, providing efficient indexing and querying of document content.

```mermaid
graph TD
subgraph "User Interface"
A[Document Search Window]
B[Search Results Panel]
C[Search Features]
end
subgraph "Service Layer"
D[Document Service]
E[Verse Teacher Service]
end
subgraph "Repository Layer"
F[Search Repository]
G[Document Repository]
H[Verse Repository]
end
subgraph "Data Storage"
I[Whoosh Index]
J[SQL Database]
end
A --> D
B --> D
C --> D
D --> F
D --> G
E --> H
F --> I
G --> J
H --> J
style A fill:#f9f,stroke:#333
style B fill:#f9f,stroke:#333
style C fill:#f9f,stroke:#333
style D fill:#bbf,stroke:#333
style E fill:#bbf,stroke:#333
style F fill:#9f9,stroke:#333
style G fill:#9f9,stroke:#333
style H fill:#9f9,stroke:#333
style I fill:#f96,stroke:#333
style J fill:#f96,stroke:#333
```

**Diagram sources**
- [document_search_window.py](file://src/pillars/document_manager/ui/document_search_window.py)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py)
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py)
- [document.py](file://src/pillars/document_manager/models/document.py)

**Section sources**
- [document_search_window.py](file://src/pillars/document_manager/ui/document_search_window.py)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py)
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py)

## Indexing Strategies
The system implements a comprehensive indexing strategy using Whoosh to create a searchable index of document content. The indexing process is designed to handle various document types and metadata efficiently.

### Schema Design
The search index uses a carefully designed schema that includes multiple fields for comprehensive search capabilities:

```mermaid
erDiagram
SEARCH_INDEX {
string id PK
string title
string content
string file_type
string tags
string author
string collection
datetime created_at
datetime updated_at
}
```

**Diagram sources**
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py#L37-L47)

The schema includes the following fields:
- **id**: Unique identifier for the document (stored and unique)
- **title**: Document title with field boost of 2.0 for higher relevance in search results
- **content**: Full text content of the document
- **file_type**: Document format (txt, html, pdf, docx, rtf)
- **tags**: Comma-separated tags with scorable capability
- **author**: Document author
- **collection**: Virtual folder or collection name
- **created_at**: Document creation timestamp
- **updated_at**: Last modification timestamp

### Index Management
The system implements several methods for managing the search index:

```mermaid
classDiagram
class DocumentSearchRepository {
+__init__(index_dir : Optional[str])
+index_document(doc : Document)
+index_documents(docs : List[Document])
+delete_document(doc_id : int)
+search(query_str : str, limit : Optional[int]) List[Dict]
+rebuild_index(documents : List[Document])
+clear_index()
}
```

**Diagram sources**
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py#L15-L201)

Key indexing operations include:
- **index_document**: Adds or updates a single document in the index
- **index_documents**: Efficiently adds or updates multiple documents in a single transaction
- **delete_document**: Removes a document from the index by ID
- **rebuild_index**: Rebuilds the entire index from a list of documents
- **clear_index**: Clears the entire search index

The indexing process is triggered automatically when documents are created, updated, or deleted through the Document Service, ensuring the search index remains synchronized with the database.

**Section sources**
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py#L15-L201)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py#L152-L212)

## Query Parsing and Search Implementation
The search system implements sophisticated query parsing and result ranking to deliver relevant search results.

### Query Parsing
The system uses Whoosh's MultifieldParser to parse search queries across multiple fields (title, content, tags, author). The parser supports various query syntax elements:

```mermaid
flowchart TD
Start([Search Query]) --> ParseQuery["Parse Query String"]
ParseQuery --> CheckSyntax{"Syntax Valid?"}
CheckSyntax --> |No| ReturnError["Return Error"]
CheckSyntax --> |Yes| AnalyzeTerms["Analyze Search Terms"]
AnalyzeTerms --> ApplyStemming["Apply Stemming"]
ApplyStemming --> BuildQuery["Build Whoosh Query"]
BuildQuery --> ExecuteSearch["Execute Search"]
ExecuteSearch --> ProcessResults["Process Results"]
ProcessResults --> GenerateSnippets["Generate Snippets with Highlights"]
GenerateSnippets --> ReturnResults["Return Results"]
```

**Diagram sources**
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py#L133-L163)

### Search Implementation
The search implementation follows a two-step process to ensure accurate and efficient results:

```mermaid
sequenceDiagram
participant UI as Document Search Window
participant Service as Document Service
participant Repository as Search Repository
participant Whoosh as Whoosh Engine
UI->>Service : search_documents_with_highlights(query)
Service->>Repository : search(query, limit)
Repository->>Whoosh : parse query with MultifieldParser
Whoosh-->>Repository : parsed query
Repository->>Whoosh : execute search
Whoosh-->>Repository : search results
Repository->>Repository : generate highlights
Repository-->>Service : results with highlights
Service-->>UI : results with highlights
UI->>UI : display results in table
```

**Diagram sources**
- [document_search_window.py](file://src/pillars/document_manager/ui/document_search_window.py#L78-L115)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py#L98-L133)
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py#L133-L163)

The search process includes:
1. Query parsing using MultifieldParser across title, content, tags, and author fields
2. Execution of the search with Whoosh
3. Generation of highlighted snippets for context
4. Formatting of results for UI display

### Search Query Syntax
The system supports a rich query syntax for advanced searching:

| Feature | Syntax | Example |
|--------|--------|--------|
| Wildcards | * | gem* (matches gematria, gemstone, etc.) |
| Phrase Search | "quotes" | "holy book" (exact phrase) |
| Boolean Logic | AND, OR | gematria AND number |
| Field Search | field:value | author:John |
| Proximity Search | "phrase"~n | "divine number"~5 |

**Section sources**
- [document_search_window.py](file://src/pillars/document_manager/ui/document_search_window.py#L47-L51)
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py#L145-L146)

## Search Interfaces
The system provides multiple interfaces for searching and displaying results.

### Document Search Window
The primary search interface is the DocumentSearchWindow, which provides a comprehensive search experience:

```mermaid
classDiagram
class DocumentSearchWindow {
-search_input : QLineEdit
-btn_search : QPushButton
-table : QTableWidget
-lbl_status : QLabel
+_setup_ui()
+_perform_search()
+_on_row_double_clicked()
}
```

**Diagram sources**
- [document_search_window.py](file://src/pillars/document_manager/ui/document_search_window.py#L10-L125)

Key components of the search window:
- Search input field with placeholder text
- Search button to initiate search
- Results table with columns for Title, Snippet, and Created date
- Status label to display search progress and results count
- Double-click functionality to open documents

### Search Results Panel
The SearchResultsPanel provides a side panel interface for displaying search results:

```mermaid
classDiagram
class SearchResultsPanel {
-list_widget : QListWidget
-header : QLabel
+load_results(results : list, term : str)
+_on_double_click()
+_show_context_menu()
}
```

**Diagram sources**
- [search_results_panel.py](file://src/pillars/document_manager/ui/search_results_panel.py#L9-L140)

Features of the results panel:
- List-based display of search results
- Context menu for adding documents to mindscape or opening them
- Support for rich text snippets with highlighting
- Visual styling for selected and hovered items

### Search Features
The system includes additional search features for document editing:

```mermaid
classDiagram
class SearchReplaceFeature {
-editor : QTextEdit
-_dialog : SearchDialog
+show_search_dialog()
+find_next()
+find_all()
+replace_current()
+replace_all()
+navigate_to()
}
```

**Diagram sources**
- [search_features.py](file://src/pillars/document_manager/ui/search_features.py#L189-L365)

These features provide:
- Find and replace functionality within documents
- Case-sensitive and whole-word matching options
- Results list with context snippets
- Navigation between search results

**Section sources**
- [document_search_window.py](file://src/pillars/document_manager/ui/document_search_window.py)
- [search_results_panel.py](file://src/pillars/document_manager/ui/search_results_panel.py)
- [search_features.py](file://src/pillars/document_manager/ui/search_features.py)

## Advanced Search Features
The system implements several advanced search features to enhance the user experience.

### Verse-Level Filtering
The Holy Book teacher mode integration enables verse-level filtering and analysis:

```mermaid
sequenceDiagram
participant UI as Text Analysis Window
participant Service as Text Analysis Service
participant VerseService as Verse Teacher Service
participant Parser as Verse Parser
UI->>Service : find_value_matches(text, target_value)
Service->>Service : tokenize text
Service->>Service : calculate gematria values
Service->>Service : apply sliding window algorithm
Service-->>UI : matches with positions
UI->>VerseService : parse_verses(document_id)
VerseService->>Parser : parse_verses(text)
Parser-->>VerseService : raw verses
VerseService->>VerseService : apply rules and enrichment
VerseService-->>UI : enriched verses with metadata
```

**Diagram sources**
- [text_analysis_service.py](file://src/pillars/gematria/services/text_analysis_service.py#L8-L113)
- [verse_teacher_service.py](file://src/pillars/document_manager/services/verse_teacher_service.py#L33-L77)

### Gematria Analysis
The system integrates gematria analysis for numerical pattern searches:

```mermaid
flowchart TD
Start([Text Input]) --> Tokenize["Tokenize Text"]
Tokenize --> CalculateValue["Calculate Gematria Value"]
CalculateValue --> CheckTarget{"Matches Target?"}
CheckTarget --> |Yes| StoreMatch["Store Match with Position"]
CheckTarget --> |No| ExpandWindow["Expand Window"]
ExpandWindow --> SumValues["Sum Values"]
SumValues --> CheckTarget
StoreMatch --> Continue["Continue Search"]
Continue --> End([Return Matches])
```

**Diagram sources**
- [text_analysis_service.py](file://src/pillars/gematria/services/text_analysis_service.py#L8-L113)

Key features of gematria analysis:
- Support for multiple gematria calculation methods
- Fast scan algorithm for finding value matches
- Sliding window approach for phrase analysis
- Integration with face value analysis

### Faceted Filtering
The document library provides faceted filtering capabilities:

```mermaid
classDiagram
class DocumentLibrary {
-search_input : QLineEdit
-tree : QTreeWidget
-table : QTableWidget
+_search_documents()
+_populate_tree()
+_on_collection_selected()
}
```

**Diagram sources**
- [document_library.py](file://src/pillars/document_manager/ui/document_library.py#L19-L599)

Faceted filtering includes:
- Collection-based filtering via tree view
- Tag-based filtering
- Type-based filtering
- Full-text search with live filtering

**Section sources**
- [text_analysis_service.py](file://src/pillars/gematria/services/text_analysis_service.py)
- [verse_teacher_service.py](file://src/pillars/document_manager/services/verse_teacher_service.py)
- [document_library.py](file://src/pillars/document_manager/ui/document_library.py)

## Performance Optimization
The system implements several performance optimization techniques to handle large document collections efficiently.

### Indexing Performance
The indexing system is optimized for both speed and memory usage:

```mermaid
graph TD
A[Indexing Strategy] --> B[Batch Operations]
A --> C[Incremental Updates]
A --> D[Schema Optimization]
B --> E[Multiple documents in single transaction]
C --> F[Update only changed documents]
D --> G[Field boosting for relevance]
D --> H[Stemming analyzer for better matching]
```

**Diagram sources**
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py)

Optimization techniques include:
- Batch indexing of multiple documents in a single transaction
- Incremental updates that only modify changed documents
- Use of stemming analyzer to improve search matching
- Field boosting to prioritize title matches

### Search Performance
The search implementation includes several performance optimizations:

```mermaid
flowchart TD
Start([Search Request]) --> CheckCache{"Results Cached?"}
CheckCache --> |Yes| ReturnCached["Return Cached Results"]
CheckCache --> |No| OptimizeQuery["Optimize Query"]
OptimizeQuery --> ExecuteSearch["Execute Search"]
ExecuteSearch --> GenerateSnippets["Generate Snippets"]
GenerateSnippets --> CacheResults["Cache Results"]
CacheResults --> ReturnResults["Return Results"]
```

**Diagram sources**
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py#L133-L163)

Performance optimizations:
- Result caching to avoid redundant searches
- Query optimization to reduce search time
- Efficient snippet generation with controlled length
- Asynchronous search execution to maintain UI responsiveness

### Memory Usage
The system manages memory usage effectively:

```mermaid
classDiagram
class DocumentSearchRepository {
-index_dir : Path
-schema : Schema
-ix : Index
+__init__(index_dir : Optional[str])
+index_document(doc : Document)
+search(query_str : str, limit : Optional[int]) List[Dict]
}
```

**Diagram sources**
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py#L15-L201)

Memory management strategies:
- Use of context managers for resource cleanup
- Efficient data structures for search results
- Proper disposal of search resources
- Configurable result limits to control memory usage

**Section sources**
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py)

## Troubleshooting Guide
This section provides guidance for common search issues and their solutions.

### Common Issues and Solutions
| Issue | Possible Cause | Solution |
|------|---------------|---------|
| No search results | Index not built or corrupted | Rebuild search index using Document Library |
| Slow search performance | Large document collection | Implement result limits and optimize queries |
| Missing documents in search | Document not indexed | Check document import process and indexing |
| Incorrect highlights | HTML content parsing issues | Ensure proper text extraction from documents |
| Schema mismatch errors | Index schema changed | Rebuild index to update schema |

### Diagnostic Steps
When troubleshooting search issues, follow these steps:

```mermaid
flowchart TD
A[Identify Issue] --> B[Check Index Status]
B --> C{Index Exists?}
C --> |No| D[Rebuild Index]
C --> |Yes| E[Verify Document Count]
E --> F{Count Matches DB?}
F --> |No| G[Reindex Documents]
F --> |Yes| H[Test Simple Query]
H --> I{Works?}
I --> |No| J[Check Query Syntax]
I --> |Yes| K[Test Complex Query]
K --> L{Works?}
L --> |No| M[Check Field Mappings]
L --> |Yes| N[System Working]
```

**Diagram sources**
- [document_library.py](file://src/pillars/document_manager/ui/document_library.py#L404-L420)
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py)

### Recovery Procedures
For index recovery, use the following procedures:

1. **Rebuild Index**: Use the "Rebuild Search Index" option in the Document Library
2. **Clear Index**: Delete the index directory and restart the application
3. **Verify Data**: Check that documents exist in the database
4. **Reimport**: Reimport documents if necessary

**Section sources**
- [document_library.py](file://src/pillars/document_manager/ui/document_library.py)
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py)

## Configuration Options
The search system provides several configuration options to customize search behavior.

### Index Configuration
The search index can be configured through the following parameters:

```mermaid
classDiagram
class DocumentSearchRepository {
+__init__(index_dir : Optional[str])
-index_dir : Path
-schema : Schema
-ix : Index
}
```

**Diagram sources**
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py#L18-L31)

Configuration options:
- **index_dir**: Directory for the Whoosh index (defaults to ~/.isopgem/documents)
- **schema**: Search schema with field definitions and analyzers
- **field boosting**: Priority for title field (2.0) to improve relevance

### Search Parameters
Search behavior can be customized through various parameters:

| Parameter | Default | Description |
|---------|--------|------------|
| limit | None | Maximum number of results (None for unlimited) |
| case_sensitive | False | Whether to match case in searches |
| whole_words | False | Whether to match whole words only |
| maxchars | 300 | Maximum characters in snippet |
| surround | 50 | Characters to show around match |

### System Integration
The search system integrates with other components through well-defined interfaces:

```mermaid
graph TD
A[Document Manager] --> B[Search System]
B --> C[Gematria System]
B --> D[Verse Teacher]
C --> E[Numerical Analysis]
D --> F[Holy Book Mode]
E --> G[Pattern Recognition]
F --> H[Verse Filtering]
```

**Diagram sources**
- [document_service.py](file://src/pillars/document_manager/services/document_service.py)
- [text_analysis_service.py](file://src/pillars/gematria/services/text_analysis_service.py)

Integration points:
- Document Service for indexing and search operations
- Verse Teacher Service for verse-level analysis
- Text Analysis Service for gematria calculations
- Document Library for faceted filtering

**Section sources**
- [search_repository.py](file://src/pillars/document_manager/repositories/search_repository.py)
- [document_service.py](file://src/pillars/document_manager/services/document_service.py)
- [text_analysis_service.py](file://src/pillars/gematria/services/text_analysis_service.py)