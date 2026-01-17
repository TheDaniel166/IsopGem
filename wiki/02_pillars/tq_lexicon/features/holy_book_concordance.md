# Holy Book Concordance

<!-- Last Verified: 2026-01-16 -->

<cite>
**Referenced Files in This Document**
- [src/pillars/tq_lexicon/ui/holy_book_concordance_window.py](file://src/pillars/tq_lexicon/ui/holy_book_concordance_window.py)
</cite>

## Table of Contents
1. [Feature Overview](#feature-overview)
2. [User Workflows](#user-workflows)
3. [UI Components](#ui-components)
4. [Business Logic](#business-logic)
5. [Data Model](#data-model)
6. [Integration Points](#integration-points)
7. [Future Enhancements](#future-enhancements)

## Feature Overview

### Purpose

Unified Holy Book Concordance Window.:
- What user need does it address?
- What value does it provide?
- Who is the target user?

### Key Capabilities

**User Capabilities**:
- Interact with ProgressBar, VBoxLayout, Widget, TextEdit, Label
- Perform actions
- Access 2 backend services:
- Primary action 1
- Primary action 2
- Primary action 3

### Access Points

- **holy_book_concordance_window**: `src/pillars/tq_lexicon/ui/holy_book_concordance_window.py`

## User Workflows

### Primary Workflow

```mermaid
flowchart TD
    ```mermaid
sequenceDiagram
    User->>System: Action
    System-->>User: Response
``` Action1
    Action1 --> Decision
    Decision -->|Yes| Action2
    Decision -->|No| Action3
    Action2 --> End
    Action3 --> End
    -->
```

### Step-by-Step Instructions

1. [Documentation needed: Add step 1]
2. [Documentation needed: Add step 2]
3. [Documentation needed: Add step 3]

### Alternative Workflows

Unified window for parsing holy books and indexing to the concordance.

## UI Components

### Main Window/Widget

**Implementation**: `src/pillars/tq_lexicon/ui/holy_book_concordance_window.py`

```
```
+------------------+
|  Component       |
|                  |
+------------------+
```
```

### UI Elements

**Key UI Elements:**
- QCheckBox - (from source)
- QComboBox - (from source)
- QFrame - (from source)
- QGroupBox - (from source)
- QHBoxLayout - (from source)
- QLabel - (from source)
- QProgressBar - (from source)
- QPushButton - (from source)
- QSplitter - (from source)
- QTableWidget - (from source)
- QTableWidgetItem - (from source)
- QTextEdit - (from source)
- QVBoxLayout - (from source)
- QWidget - (from source)
- Input fields
- Buttons
- Display areas
- Menus/toolbars

### User Interactions

**User Interactions:**
- `_apply_filter()` -> Triggers internal handler.
- `_load_documents()` -> Triggers internal handler.
- `_on_doc_double_clicked()` -> Initiates export via export service.
- `_on_doc_selected()` -> Initiates export via export service.
- `_on_error()` -> Triggers internal handler.
- `_on_finished()` -> Initiates export via export service.
- `_on_parse_and_index()` -> Initiates export via export service.
- `_on_parse_only()` -> Initiates export via export service.
- `_on_progress()` -> Initiates export via export service.
- `_open_lexicon_manager()` -> Triggers internal handler.
- `_open_teacher_window()` -> Triggers internal handler.
- `close()` -> Triggers internal handler.:
- Click actions
- Keyboard shortcuts
- Drag-and-drop
- Context menus

## Business Logic

### Core Services

**Services:**
- ConcordanceIndexerService - (instantiated in source)
- DocumentService - (instantiated in source)
- HolyKeyService - (instantiated in source)

### Calculation/Processing

**Core Algorithms & Processing:**
- (No specific algorithmic hints found in source; check service implementations):
- What calculations are performed?
- What transformations happen?
- What validations occur?

### Business Rules

**Key Business Rules:**
- (No explicit business rules found in source):
- Rule 1
- Rule 2
- Rule 3

## Data Model

### Input Data

[Documentation needed: What data does the feature accept?]

### Output Data

[Documentation needed: What data does the feature produce?]

### Persistence

[Documentation needed: Is data saved? Where? In what format?]

## Integration Points

### Dependencies

[Documentation needed: What other pillars/features does this depend on?]

### Signals & Events

- **`progress`**: Emitted with arguments: `int, int, str`
- **`finished`**: Emitted with arguments: `object`
- **`error`**: Emitted with arguments: `str`
- **`documents_updated`**: Emitted with arguments: ``

### External APIs

[Documentation needed: Does it use external libraries or APIs?]

## Future Enhancements

### Planned Features

[Documentation needed: List planned improvements]

### Known Limitations

[Documentation needed: List current limitations]

### User Requests

[Documentation needed: List common user requests]

---

**Last Updated**: 2026-01-16
**Status**: Auto-generated skeleton (needs AI enhancement)

**Navigation:**
- [← Features Index](./README.md)
- [↑ Tq_Lexicon Index](../INDEX.md)
