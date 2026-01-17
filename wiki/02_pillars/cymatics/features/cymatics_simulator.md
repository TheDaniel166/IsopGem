# Cymatics Simulator

<!-- Last Verified: 2026-01-16 -->

<cite>
**Referenced Files in This Document**
- [src/pillars/cymatics/ui/cymatics_simulator_window.py](file://src/pillars/cymatics/ui/cymatics_simulator_window.py)
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

Cymatics simulator window for visual standing-wave patterns.:
- What user need does it address?
- What value does it provide?
- Who is the target user?

### Key Capabilities

**User Capabilities**:
- Interact with VBoxLayout, StackedWidget, SpinBox, Rect, Widget
- Perform actions
- Access 6 backend services:
- Primary action 1
- Primary action 2
- Primary action 3

### Access Points

- **cymatics_simulator_window**: `src/pillars/cymatics/ui/cymatics_simulator_window.py`

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

Visual simulator for cymatics patterns with advanced features.

## UI Components

### Main Window/Widget

**Implementation**: `src/pillars/cymatics/ui/cymatics_simulator_window.py`

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
- QDoubleSpinBox - (from source)
- QFrame - (from source)
- QGridLayout - (from source)
- QHBoxLayout - (from source)
- QLabel - (from source)
- QMainWindow - (from source)
- QMessageBox - (from source)
- QPushButton - (from source)
- QScrollArea - (from source)
- QSlider - (from source)
- QSpinBox - (from source)
- QSplitter - (from source)
- QStackedWidget - (from source)
- QVBoxLayout - (from source)
- QWidget - (from source)
- Input fields
- Buttons
- Display areas
- Menus/toolbars

### User Interactions

**User Interactions:**
- 1. Adjust frequency slider -> `_on_frequency_changed(value)` -> updates label and, if auto-refresh enabled, regenerates pattern.
- 2. Select plate shape dropdown -> `_on_shape_changed(index)` -> resets particle state and regenerates pattern with new boundary conditions.
- 3. Click "Generate" -> `_on_generate()` -> builds `SimulationParams` and calls `CymaticsSimulationService.simulate(params)` -> updates views (`Cymatics3DView`, `CymaticsParticleView`).
- 4. Toggle 3D view -> switches between 2D canvas and 3D OpenGL widget.
- 5. Export -> `_handle_export()` -> uses `CymaticsExportService` to save PNG/GIF.:
- Click actions
- Keyboard shortcuts
- Drag-and-drop
- Context menus

## Business Logic

### Core Services

**Services:**
- CymaticsSimulationService - (instantiated in source)
- CymaticsGradientService - (instantiated in source)
- CymaticsParticleService - (instantiated in source)
- CymaticsPresetService - (instantiated in source)
- CymaticsExportService - (instantiated in source)
- CymaticsAudioService - (instantiated in source)

### Calculation/Processing

**Core Algorithms & Processing:**
- Uses `hz_to_modes(frequency_hz, params)` to map frequency to (m,n) modes with material correction and logarithmic mapping.
- `simulate(params, phase)` dispatches to shape-specific generators and returns `SimulationResult` including amplitude grid and metadata.
- Caches Bessel function zeros (`_BESSEL_ZEROS_CACHE`) to avoid expensive recomputation and uses fallback approximations when needed.
- Circular plates use Bessel modes and boundary conditions; rectangular/hexagonal shapes have dedicated field generators.:
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
