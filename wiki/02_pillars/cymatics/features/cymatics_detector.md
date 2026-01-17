# Cymatics Detector

<!-- Last Verified: 2026-01-16 -->

<cite>
**Referenced Files in This Document**
- [src/pillars/cymatics/ui/cymatics_detector_window.py](file://src/pillars/cymatics/ui/cymatics_detector_window.py)
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

Cymatics detector window for analyzing simulated patterns.:
- What user need does it address?
- What value does it provide?
- Who is the target user?

### Key Capabilities

**User Capabilities**:
- Interact with VBoxLayout, Widget, TextEdit, Label, DoubleSpinBox
- Perform actions
- Access 1 backend services:
- Primary action 1
- Primary action 2
- Primary action 3

### Access Points

- **cymatics_detector_window**: `src/pillars/cymatics/ui/cymatics_detector_window.py`

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

Detector view for cymatics patterns produced by the simulator.

## UI Components

### Main Window/Widget

**Implementation**: `src/pillars/cymatics/ui/cymatics_detector_window.py`

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
- QComboBox - (from source)
- QDoubleSpinBox - (from source)
- QFrame - (from source)
- QGridLayout - (from source)
- QHBoxLayout - (from source)
- QImage - (from source)
- QLabel - (from source)
- QPushButton - (from source)
- QTextEdit - (from source)
- QVBoxLayout - (from source)
- QWidget - (from source)
- Input fields
- Buttons
- Display areas
- Menus/toolbars

### User Interactions

**User Interactions:**
- 1. Start detection -> `_on_start_detection()` -> CymaticsDetectionService.analyze(audio or image) -> produces DetectionResult (nodal lines, symmetry metrics).
- 2. Adjust sensitivity -> `_on_sensitivity_changed()` -> updates detection thresholds and re-runs analysis.:
- Click actions
- Keyboard shortcuts
- Drag-and-drop
- Context menus

## Business Logic

### Core Services

**Services:**
- CymaticsDetectionService - (instantiated in source)

### Calculation/Processing

**Core Algorithms & Processing:**
- Uses FFT and pattern recognition to identify nodal lines and symmetry; emits detailed metrics used by visualization components.:
- What calculations are performed?
- What transformations happen?
- What validations occur?

### Business Rules

**Key Business Rules:**
- Clamps inputs to safe numerical ranges (using np.clip):
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

- No signals emitted

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
- [↑ Cymatics Index](../INDEX.md)
