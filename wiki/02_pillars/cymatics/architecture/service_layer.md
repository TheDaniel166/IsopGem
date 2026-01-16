# Service Layer

<!-- Last Verified: 2026-01-16 -->

<cite>
**Referenced Files in This Document**
- [src/pillars/cymatics/services/cymatics_detection_service.py](file://src/pillars/cymatics/services/cymatics_detection_service.py)
- [src/pillars/cymatics/services/cymatics_simulation_service.py](file://src/pillars/cymatics/services/cymatics_simulation_service.py)
- [src/pillars/cymatics/services/cymatics_gradient_service.py](file://src/pillars/cymatics/services/cymatics_gradient_service.py)
- [src/pillars/cymatics/services/cymatics_particle_service.py](file://src/pillars/cymatics/services/cymatics_particle_service.py)
- [src/pillars/cymatics/services/cymatics_preset_service.py](file://src/pillars/cymatics/services/cymatics_preset_service.py)
</cite>

## Table of Contents
1. [Pattern Overview](#pattern-overview)
2. [Architectural Diagram](#architectural-diagram)
3. [Key Components](#key-components)
4. [Data Flow](#data-flow)
5. [Implementation Details](#implementation-details)
6. [Trade-offs & Rationale](#trade-offs--rationale)
7. [Evolution & History](#evolution--history)

## Pattern Overview

**Pattern Type**: Layer

Business logic services separating UI from data

**Purpose**: Separates business logic into reusable service classes that can be tested independently of the UI.

**Problem Solved**: Without service layer, business logic becomes tangled with UI code, making testing difficult and code reuse impossible.

**Key Benefits**:
- Services (cymatics_session_store, cymatics_detection_service, cymatics_simulation_service) contain zero UI dependencies
- Same service can be used by multiple windows
- Unit testing without Qt instantiation
- Clear separation of concerns

## Architectural Diagram

```mermaid
```mermaid
graph TD
    A[Component A] --> B[Component B]
    B --> C[Component C]
```
```

## Key Components

### Core Classes

#### `CymaticsDetectionService`

**Location**: `src/pillars/cymatics/services/cymatics_detection_service.py`

**TODO**: Add:
- Class responsibility
- Key methods
- Usage example

#### `CymaticsSimulationService`

**Location**: `src/pillars/cymatics/services/cymatics_simulation_service.py`

**TODO**: Add:
- Class responsibility
- Key methods
- Usage example

#### `CymaticsGradientService`

**Location**: `src/pillars/cymatics/services/cymatics_gradient_service.py`

**TODO**: Add:
- Class responsibility
- Key methods
- Usage example

#### `CymaticsParticleService`

**Location**: `src/pillars/cymatics/services/cymatics_particle_service.py`

**TODO**: Add:
- Class responsibility
- Key methods
- Usage example

#### `CymaticsPresetService`

**Location**: `src/pillars/cymatics/services/cymatics_preset_service.py`

**TODO**: Add:
- Class responsibility
- Key methods
- Usage example

## Data Flow

```mermaid
sequenceDiagram
    ```mermaid
sequenceDiagram
    User->>System: Action
    System-->>User: Response
```
```

## Implementation Details

### Pattern Application

**TODO**: Explain how the pattern is implemented:
- How are components instantiated?
- How do components communicate?
- What are the extension points?

### Code Example

```python
# Implementation details in source
```

## Trade-offs & Rationale

### Advantages

[Documentation needed: List specific advantages in this pillar]

### Disadvantages

[Documentation needed: List any downsides or complexity costs]

### Alternative Approaches Considered

[Documentation needed: What other patterns were considered and why rejected?]

## Evolution & History

**TODO**: Add:
- When was this pattern introduced?
- Has it changed over time?
- Are there plans to refactor?

---

**Last Updated**: 2026-01-16
**Status**: Auto-generated skeleton (needs AI enhancement)

**Navigation:**
- [← Architecture Index](./README.md)
- [↑ Cymatics Index](../INDEX.md)
