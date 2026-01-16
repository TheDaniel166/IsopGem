# Model-View Separation

<!-- Last Verified: 2026-01-16 -->

<cite>
**Referenced Files in This Document**
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

**Pattern Type**: MVC (Model-View-Controller)

Clear separation between data models (cymatics_models.py), business logic (services/), and UI components (ui/).

**Problem Solved**: Cymatics simulations involve complex mathematical calculations (Bessel functions, FFT analysis, wave equations) that must remain decoupled from the UI layer. Without this separation, UI changes would risk breaking physics calculations, and reusing simulation logic would be impossible.

**Why This Pattern**: 
- **Physics Integrity**: Mathematical models (PlateShape, PlateMaterial, SimulationParams) define rigorous physical properties independent of visualization
- **Multiple Views**: Same simulation can be displayed as 2D heatmaps, 3D surfaces, or particle systems
- **Testability**: Services can be unit-tested without instantiating Qt widgets
- **Reusability**: Core simulation engine could be used in CLI tools or web services

**Key Benefits**:
- UI can be redesigned without touching wave equations
- Services encapsulate complex algorithms (Bessel zeros, FFT, frequency mapping)
- Models are pure data classes with no Qt dependencies
- Clear data flow: UI → Service → Model → Result → UI

## Architectural Diagram

```mermaid
graph TD
    subgraph "View Layer (ui/)"
        Hub[CymaticsHub]
        SimWin[CymaticsSimulatorWindow]
        DetWin[CymaticsDetectorWindow]
        View3D[Cymatics3DView]
        ViewParticle[CymaticsParticleView]
    end
    
    subgraph "Service Layer (services/)"
        SimSvc[CymaticsSimulationService]
        DetSvc[CymaticsDetectionService]
        AudioSvc[CymaticsAudioService]
        GradSvc[CymaticsGradientService]
        PartSvc[CymaticsParticleService]
    participant User
    participant SimWindow as CymaticsSimulatorWindow<br/>(View)
    participant SimService as CymaticsSimulationService<br/>(Service)
    participant Models as SimulationParams<br/>(Model)
    participant View3D as Cymatics3DView<br/>(Visualization)
    
    User->>SimWindow: Adjust frequency slider
    SimWindow->>SimWindow: Update UI labels
    User->>SimWindow: Click "Generate"
    
    SimWindow->>Models: Create SimulationParams
    Note over Models: shape, dimensions,<br/>frequency, material
    
    SimWindow->>SimService: generate_pattern(params)
    activate SimService
    SimService->>SimService: Calculate Bessel modes
    SimService->>SimService: Apply boundary conditions
    SimService->>SimService: Compute standing wave
    SimService->>Models: Create SimulationResult
    Note over Models: amplitude_grid,<br/>metadata
    SimService-->>SimWindow: Return SimulationResult
    deactivate SimService
    
    SimWindow->>View3D: update_pattern(result.amplitude_grid)
    View3D->>View3D: Convert to OpenGL vertices
    View3D->>View3D: Render 3D surface
    View3D-->>User: Display visualization SimParams[SimulationParams]
        SimResult[SimulationResult]
        PlateShape[PlateShape enum]
        PlateMaterial[PlateMaterial enum]
        DetParams[DetectionParams]
    end
    
    Hub --> SimWin
    Hub --> DetWin
    SimWin --> SimSvc
    SimWin --> GradSvc
    SimWin --> PresSvc
    DetWin --> DetSvc
    DetWin --> AudioSvc
    SimWin --> View3D
    SimWin --> ViewParticle
    
    SimSvc --> SimParams
    SimSvc --> SimResult
    SimSvc --> PlateShape
    SimSvc --> PlateMaterial
    DetSvc --> DetParams
    PartSvc --> SimResult
    
    style Hub fill:#e1f5ff
    style SimWin fill:#e1f5ff
    style DetWin fill:#e1f5ff
    style SimSvc fill:#fff4e6
    style DetSvc fill:#fff4e6
    style SimParams fill:#f0f0f0
**Instantiation**:
- `CymaticsHub` creates window instances on demand via lambda callbacks
- Windows receive `WindowManager` for lifecycle management
- Services are instantiated per-window (no shared state)
- Models are created transiently for each calculation

**Communication**:
- Views call Service methods directly (no event bus for simplicity)
- Services return immutable result objects (SimulationResult, DetectionResult)
- Qt signals/slots only within UI layer (not across to services)
- No bidirectional coupling: Services never reference UI classes

**Extension Points**:
- New plate shapes: Add to `PlateShape` enum + implement boundary logic in service
- New visualizations: Subclass `QWidget`, consume `SimulationResult.amplitude_grid`
- New material presets: Add to `PlateMaterial` enum with physical properties
- Custom gradients: Extend `CymaticsGradientService` color mapping

### Code Example

```python
# From cymatics_simulator_window.py - shows clean MVC separation

# VIEW: Collect user input
params = SimulationParams(
    shape=PlateShape.CIRCULAR,
    dimensions=(1.0, 1.0),  # 1m diameter
    frequency=440.0,  # A4 note
    resolution=256,
    material=PlateMaterial.BRASS
)

# SERVICE: Execute physics calculation (no Qt dependencies)
service = CymaticsSimulationService()
result = service.generate_pattern(params)  # Returns SimulationResult

# VIEW: Display result in multiple visualizations
self._3d_view.update_pattern(result.amplitude_grid)
**In Cymatics Pillar**:
- Physics algorithms verified independently in unit tests (no GUI required)
- Same simulation service used by both Detector and Simulator windows
- 3D OpenGL view and 2D canvas view consume identical data model
- Audio service decoupled from visualization (can run detection without display)
- Preset service reusable: loads/saves params without knowing UI structure

### Disadvantages

**Complexity Costs**:
- Boilerplate: Must create param objects instead of passing primitives
- No reactive binding: UI must manually poll/subscribe to result changes
- Memory copies: Data marshaled from service → model → view (no shared buffers)
- Learning curve: Developers must understand layer boundaries

### Alternative Approaches Considered

**Rejected: Monolithic Widget**
- Initial prototype embedded simulation in `CymaticsSimulatorWindow.__init__`
- **Problem**: Couldn't test Bessel calculations without instantiating Qt
- **Problem**: Couldn't reuse simulation for audio detection feature

**Rejected: Shared State Manager**
- Considered global cymatics state object with observers
- **Problem**: Introduces hidden coupling, harder to reason about data flow
- **Problem**: Threading issues with concurrent simulations

**Rejected: Event Bus**
- Evaluated signal-based pub/sub between layers
- **Problem**: Overkill for synchronous calculations (no async needed)
- **Problem**: Makes data flow implicit (harder to debug)

## Implementation Details

### Pattern Application

**TODO**: Explain how the pattern is implemented:
- How are components instantiated?
- How do components communicate?
- What are the extension points?

**Initial Implementation** (2024-Q4):
- Started with monolithic `CymaticsWindow` containing all logic
- Simulation methods were private methods of the window class
- Testing required mocking Qt components

**Refactor 1** (2025-Q1):
- Extracted `CymaticsSimulationService` to separate file
- Created `SimulationParams` and `SimulationResult` dataclasses
- Added preset service for save/load functionality

**Current State** (2026-Q1):
- Full 3-layer separation enforced
- Service layer has zero Qt imports (verified in tests)
- Multiple view types consuming same service
- Enum-based material/shape system for type safety

**Future Plans**:
- **No major changes planned**: Pattern working well
- Possible enhancement: Async service methods for long calculations (hexagonal modes)
- Consider: WebAssembly export of service layer for browser demos

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
