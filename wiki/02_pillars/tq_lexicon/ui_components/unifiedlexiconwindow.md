# UnifiedLexiconWindow

<!-- Last Verified: 2026-01-16 -->

<cite>
**Referenced Files in This Document**
- [src/pillars/tq_lexicon/ui/unified_lexicon_window.py](file://src/pillars/tq_lexicon/ui/unified_lexicon_window.py)
</cite>

## Table of Contents
1. [Component Overview](#component-overview)
2. [UI Layout](#ui-layout)
3. [Signals & Slots](#signals--slots)
4. [State Management](#state-management)
5. [User Interactions](#user-interactions)
6. [Integration](#integration)
7. [Implementation Details](#implementation-details)

## Component Overview

### Purpose

Unified window for the complete TQ Lexicon workflow.

Tabs:
1. Import & Parse - Select document and parse into verses
2. Candidates - Process word candidates from the active document
3. Concordance - View word occurrences across documents
4. Master Key - Full word database with definitions

### Component Type

**Base Classes**: QMainWindow

### Key Responsibilities

**TODO**: List the component's key responsibilities:
- Responsibility 1
- Responsibility 2
- Responsibility 3

## UI Layout

### Visual Structure

```
```
+------------------+
|  Component       |
|                  |
+------------------+
```
```

### Widget Hierarchy

**Widgets Used**:
- `QCheckBox`
- `QComboBox`
- `QGroupBox`
- `QLabel`
- `QLineEdit`
- `QListWidget`
- `QPushButton`
- `QTabWidget`
- `QTableWidget`
- `QTextEdit`
- `QTreeWidget`

```mermaid
graph TD
    A[UnifiedLexiconWindow]
    ```mermaid
graph TD
    Root[Root Widget] --> Child1[Child 1]
    Root --> Child2[Child 2]
``` B[MainLayout]
    B --> C[Widget1]
    B --> D[Widget2]
    D --> E[SubWidget]
    -->
```

### Layout Code Pattern

```python
# Implementation details in source
```

## Signals & Slots

### Signals Emitted

- **`progress`**: Emitted with arguments: `int, int, str`
- **`finished`**: Emitted with arguments: `object`
- **`error`**: Emitted with arguments: `str`
- **`progress`**: Emitted with arguments: `int, int, str`
- **`finished`**: Emitted with arguments: ``
- **`finished`**: Emitted with arguments: `list`

### Slots (Event Handlers)

#### `_on_doc_selected()`

Unified window for the complete TQ Lexicon workflow.

#### `_on_parse_and_index()`

Unified window for the complete TQ Lexicon workflow.

#### `_on_progress()`

Unified window for the complete TQ Lexicon workflow.

#### `_on_parse_finished()`

Unified window for the complete TQ Lexicon workflow.

#### `_on_parse_error()`

Unified window for the complete TQ Lexicon workflow.

#### `_on_conc_word_selected()`

Unified window for the complete TQ Lexicon workflow.

#### `_on_mk_double_click()`

Unified window for the complete TQ Lexicon workflow.

#### `_on_enrich_progress()`

Unified window for the complete TQ Lexicon workflow.

#### `_on_enrich_finished()`

Unified window for the complete TQ Lexicon workflow.

#### `_on_tab_changed()`

Unified window for the complete TQ Lexicon workflow.

### Signal Flow Diagram

```mermaid
sequenceDiagram
    [Content to be expanded]
```

## State Management

### Component State

**TODO**: Describe the component's internal state:
- What data does it track?
- How is state initialized?
- How does state change?

### State Transitions

```mermaid
stateDiagram-v2
    ```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Active
    Active --> Idle
``` Idle
    Idle --> Active: User Input
    Active --> Processing: Submit
    Processing --> Complete: Success
    Processing --> Error: Failure
    Complete --> Idle: Reset
    Error --> Idle: Reset
    -->
```

## User Interactions

### Supported Actions

**TODO**: List user actions:
- Click button X → Does Y
- Enter text in Z → Does W
- Drag object → Does V

### Keyboard Shortcuts

**Keyboard Shortcuts:**
- (None found)
- Ctrl+N: New
- Ctrl+S: Save
- Ctrl+Q: Quit

### Context Menus

Unified window for the complete TQ Lexicon workflow.

## Integration

### Parent/Owner

[Documentation needed: What creates this component? Where is it used?]

### Services Used

[Documentation needed: What services does this component depend on?]

### Communication Pattern

[Documentation needed: How does it communicate with other components?]

## Implementation Details

### Initialization

```python
# Implementation details in source
```

### Key Methods

**Event Handlers:**
- (No event handlers found in source)
- method_name(): description
### Styling & Theming

**TODO**: How is the component styled?
- QSS stylesheets?
- Dynamic styling?
- Theme integration?

---

**Last Updated**: 2026-01-16
**Status**: Auto-generated skeleton (needs AI enhancement)

**Navigation:**
- [← UI Components Index](./README.md)
- [↑ Tq_Lexicon Index](../INDEX.md)
