# Window Manager Initialization and Injection

<cite>
**Referenced Files in This Document**
- [src/main.py](file://src/main.py)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py)
- [src/shared/ui/__init__.py](file://src/shared/ui/__init__.py)
- [src/pillars/gematria/ui/gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py)
- [src/pillars/geometry/ui/geometry_hub.py](file://src/pillars/geometry/ui/geometry_hub.py)
- [src/pillars/document_manager/ui/document_manager_hub.py](file://src/pillars/document_manager/ui/document_manager_hub.py)
- [src/pillars/astrology/ui/astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py)
- [src/pillars/tq/ui/tq_hub.py](file://src/pillars/tq/ui/tq_hub.py)
- [src/pillars/adyton/ui/adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py)
- [test/test_window_manager.py](file://test/test_window_manager.py)
</cite>

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
This document explains the Window Manager initialization and dependency injection mechanism in the isopgem application. It focuses on how the WindowManager singleton is created early in the application lifecycle, passed to the main window, and then injected into each pillar hub. It also details how the WindowManager coordinates floating tool windows, maintains UI state across pillars, and enables cross-component communication. Thread-safety considerations, event propagation patterns, and lifecycle management are covered, along with practical examples of how UI components register with and utilize the window manager for window coordination.

## Project Structure
The window manager sits in a shared UI module and is consumed by the main application entry point and all pillar hubs. The main entry point constructs the WindowManager and passes it to the main window, which in turn passes it to each hub. Hubs then use the WindowManager to open tool windows and coordinate their lifecycle.

```mermaid
graph TB
A["src/main.py<br/>Application entry point"] --> B["IsopGemMainWindow<br/>Creates WindowManager"]
B --> C["Pillar Hubs<br/>Gematria, Geometry,<br/>Document Manager, Astrology, TQ, Adyton"]
C --> D["WindowManager<br/>shared.ui.window_manager"]
D --> E["Tool Windows<br/>Floating windows"]
```

**Diagram sources**
- [src/main.py](file://src/main.py#L120-L163)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L15-L112)
- [src/pillars/gematria/ui/gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py#L49-L70)
- [src/pillars/geometry/ui/geometry_hub.py](file://src/pillars/geometry/ui/geometry_hub.py#L12-L20)
- [src/pillars/document_manager/ui/document_manager_hub.py](file://src/pillars/document_manager/ui/document_manager_hub.py#L14-L27)
- [src/pillars/astrology/ui/astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py#L13-L26)
- [src/pillars/tq/ui/tq_hub.py](file://src/pillars/tq/ui/tq_hub.py#L17-L30)
- [src/pillars/adyton/ui/adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py#L114-L148)

**Section sources**
- [src/main.py](file://src/main.py#L120-L163)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L15-L112)
- [src/shared/ui/__init__.py](file://src/shared/ui/__init__.py#L1-L6)

## Core Components
- WindowManager: Centralized coordinator for tool windows across the application. It tracks active windows, manages single-instance vs. multi-instance behavior, and raises windows on tab changes.
- Main Application Entry Point: Creates the QApplication, initializes the database, applies stylesheets, and constructs the main window with a WindowManager instance.
- Main Window: Holds the WindowManager and passes it to each pillar hub when constructing tabs.
- Pillar Hubs: Receive the WindowManager via constructor and use it to open tool windows. They encapsulate UI actions and delegate window creation to the WindowManager.

Key responsibilities:
- Early instantiation: WindowManager is created in the main window constructor before any hub tabs are initialized.
- Dependency injection: Each hub receives the WindowManager in its constructor and stores it for later use.
- Lifecycle management: WindowManager handles open/close/reuse semantics, window identification, and cleanup.
- Cross-component communication: Hubs can pass the WindowManager to tool windows to enable coordinated behavior.

**Section sources**
- [src/main.py](file://src/main.py#L51-L69)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L15-L112)
- [src/pillars/gematria/ui/gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py#L49-L70)
- [src/pillars/geometry/ui/geometry_hub.py](file://src/pillars/geometry/ui/geometry_hub.py#L12-L20)
- [src/pillars/document_manager/ui/document_manager_hub.py](file://src/pillars/document_manager/ui/document_manager_hub.py#L14-L27)
- [src/pillars/astrology/ui/astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py#L13-L26)
- [src/pillars/tq/ui/tq_hub.py](file://src/pillars/tq/ui/tq_hub.py#L17-L30)
- [src/pillars/adyton/ui/adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py#L114-L148)

## Architecture Overview
The WindowManager acts as a façade for window lifecycle operations. It is constructed in the main window and injected into each hub. Hubs call open_window with a window type, window class, and options to either reuse an existing window or create a new one. The WindowManager sets attributes, flags, and connects destruction signals to keep internal state consistent.

```mermaid
sequenceDiagram
participant App as "Application"
participant Main as "IsopGemMainWindow"
participant Hub as "Pillar Hub"
participant WM as "WindowManager"
participant Win as "Tool Window"
App->>Main : "Construct main window"
Main->>WM : "Instantiate WindowManager(parent)"
App->>Main : "Show main window"
Main->>Hub : "Construct hub with WindowManager"
Hub->>WM : "open_window(window_type, window_class, allow_multiple, ...)"
WM->>Win : "Create window with parent and flags"
WM-->>Hub : "Return window instance"
WM->>WM : "Track window by window_id"
WM->>Win : "Connect destroyed signal"
WM-->>Main : "Raise all windows on tab change"
```

**Diagram sources**
- [src/main.py](file://src/main.py#L51-L69)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L29-L112)
- [src/pillars/gematria/ui/gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py#L178-L188)

## Detailed Component Analysis

### WindowManager Class
The WindowManager centralizes window lifecycle management:
- Tracks active windows in a dictionary keyed by window_id.
- Maintains per-type counters for multi-instance windows.
- Supports single-instance reuse by checking existing active windows.
- Configures window attributes and flags appropriate for floating tool windows.
- Provides APIs to close specific windows, close all windows, close by type, query state, and raise all windows.

```mermaid
classDiagram
class WindowManager {
-parent : QWidget
-_active_windows : Dict[str, QWidget]
-_window_counters : Dict[str, int]
+open_window(window_type, window_class, allow_multiple, *args, **kwargs) QWidget
+close_window(window_id) bool
+close_all_windows() void
+close_windows_of_type(window_type) int
+is_window_open(window_id) bool
+get_window(window_id) QWidget
+get_active_windows() Dict[str, QWidget]
+get_window_count() int
+raise_all_windows() void
-_on_window_closed(window_id) void
}
```

**Diagram sources**
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L15-L221)

**Section sources**
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L15-L221)

### Main Application Entry Point and Main Window
- The main entry point initializes the database, creates the QApplication, applies stylesheets, and constructs the main window.
- The main window creates the WindowManager and passes it to each hub when adding tabs.
- The main window connects tab changes to raise all managed windows, ensuring floating tool windows remain visible when switching tabs.

```mermaid
sequenceDiagram
participant Entry as "main()"
participant App as "QApplication"
participant MW as "IsopGemMainWindow"
participant WM as "WindowManager"
participant Hub as "Pillar Hub"
Entry->>App : "Create QApplication"
Entry->>MW : "Construct IsopGemMainWindow()"
MW->>WM : "self.window_manager = WindowManager(self)"
MW->>Hub : "Add tabs with WindowManager"
MW->>WM : "Connect tabs.currentChanged to raise_all_windows"
```

**Diagram sources**
- [src/main.py](file://src/main.py#L120-L163)
- [src/main.py](file://src/main.py#L51-L69)

**Section sources**
- [src/main.py](file://src/main.py#L120-L163)
- [src/main.py](file://src/main.py#L51-L69)

### Dependency Injection Pattern Across Pillars
Each hub receives the WindowManager via its constructor and stores it as an instance attribute. This enables:
- Consistent window creation semantics across pillars.
- Uniform behavior for single-instance vs. multi-instance windows.
- Cross-component communication through shared window references.

Examples:
- GematriaHub: Stores the WindowManager and opens calculator windows with allow_multiple=True or False depending on the tool.
- GeometryHub: Uses the WindowManager to open geometry-related windows and 3D viewers.
- DocumentManagerHub: Opens editor, library, search, and mindscape windows via the WindowManager.
- AstrologyHub: Opens natal charts, transit viewers, and planetary positions windows.
- TQHub: Opens ternary converters, quadset analyzers, transitions, and sound widgets.
- AdytonHub: Opens sanctuary engines, GL viewports, wall windows, and analytics windows.

```mermaid
classDiagram
class GematriaHub {
+window_manager : WindowManager
+_open_calculator() void
+_open_saved_calculations() void
+_open_batch_calculator() void
+_open_database_tools() void
+_open_text_analysis() void
+_open_methods_reference() void
}
class GeometryHub {
+window_manager : WindowManager
+_open_polygon_calculator() void
+_open_advanced_scientific_calculator() void
}
class DocumentManagerHub {
+window_manager : WindowManager
+_open_document_editor() void
+_open_document_library() void
+_open_document_search() void
+_open_mindscape() void
}
class AstrologyHub {
+window_manager : WindowManager
+_open_natal_chart() void
+_open_transit_viewer() void
+_open_planetary_positions() void
+_open_neo_aubrey() void
+_open_venus_rose() void
}
class TQHub {
+window_manager : WindowManager
+_open_ternary_converter() void
+_open_quadset_analysis() void
+_open_transitions() void
+_open_geometric_transitions() void
+_open_geometric_transitions_3d() void
+_open_conrune_pair_finder() void
+_open_amun_sound() void
+_open_kamea() void
}
class AdytonHub {
+window_manager : WindowManager
+_open_sanctuary() void
+_open_sanctuary_gl() void
+_open_wall_view(wall_index) void
+_open_wall_analytics() void
}
class WindowManager
GematriaHub --> WindowManager : "uses"
GeometryHub --> WindowManager : "uses"
DocumentManagerHub --> WindowManager : "uses"
AstrologyHub --> WindowManager : "uses"
TQHub --> WindowManager : "uses"
AdytonHub --> WindowManager : "uses"
```

**Diagram sources**
- [src/pillars/gematria/ui/gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py#L49-L70)
- [src/pillars/geometry/ui/geometry_hub.py](file://src/pillars/geometry/ui/geometry_hub.py#L12-L20)
- [src/pillars/document_manager/ui/document_manager_hub.py](file://src/pillars/document_manager/ui/document_manager_hub.py#L14-L27)
- [src/pillars/astrology/ui/astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py#L13-L26)
- [src/pillars/tq/ui/tq_hub.py](file://src/pillars/tq/ui/tq_hub.py#L17-L30)
- [src/pillars/adyton/ui/adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py#L114-L148)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L15-L112)

**Section sources**
- [src/pillars/gematria/ui/gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py#L137-L188)
- [src/pillars/geometry/ui/geometry_hub.py](file://src/pillars/geometry/ui/geometry_hub.py#L12-L20)
- [src/pillars/document_manager/ui/document_manager_hub.py](file://src/pillars/document_manager/ui/document_manager_hub.py#L136-L183)
- [src/pillars/astrology/ui/astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py#L87-L127)
- [src/pillars/tq/ui/tq_hub.py](file://src/pillars/tq/ui/tq_hub.py#L17-L30)
- [src/pillars/adyton/ui/adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py#L114-L148)

### Example: Opening a Tool Window via WindowManager
- A hub calls open_window with a window_type, window_class, and allow_multiple flag.
- WindowManager either reuses an existing window (single-instance mode) or creates a new one (multi-instance mode).
- The WindowManager sets window attributes, flags, and connects the destroyed signal to keep internal state consistent.
- The hub receives the window instance and can pass additional parameters (e.g., calculators, window_manager references).

```mermaid
sequenceDiagram
participant Hub as "GematriaHub"
participant WM as "WindowManager"
participant Calc as "GematriaCalculatorWindow"
Hub->>WM : "open_window('gematria_calculator', GematriaCalculatorWindow, allow_multiple=True, calculators, window_manager)"
WM->>WM : "Generate window_id (multi-instance)"
WM->>Calc : "Instantiate with parent and kwargs"
WM->>WM : "Store window in _active_windows"
WM-->>Hub : "Return Calc instance"
```

**Diagram sources**
- [src/pillars/gematria/ui/gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py#L178-L188)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L29-L112)

**Section sources**
- [src/pillars/gematria/ui/gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py#L178-L188)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L29-L112)

### Event Propagation Patterns
- Tab change event in the main window triggers WindowManager.raise_all_windows, ensuring floating windows remain visible when the user switches tabs.
- Window destruction is tracked via the destroyed signal connected during window creation, allowing the WindowManager to remove entries from its internal registry.
- Some hubs connect signals emitted by windows (e.g., document_opened) to trigger subsequent window opening, demonstrating cross-component communication enabled by the shared WindowManager reference.

```mermaid
flowchart TD
Start(["Tab changed"]) --> Raise["WindowManager.raise_all_windows()"]
Raise --> Visible{"Window isVisible()?"}
Visible --> |Yes| BringToFront["window.raise_()"]
Visible --> |No| Skip["Skip"]
BringToFront --> End(["Done"])
Skip --> End
```

**Diagram sources**
- [src/main.py](file://src/main.py#L67-L76)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L213-L221)

**Section sources**
- [src/main.py](file://src/main.py#L67-L76)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L186-L195)
- [src/pillars/document_manager/ui/document_manager_hub.py](file://src/pillars/document_manager/ui/document_manager_hub.py#L136-L175)

### Lifecycle Management
- Creation: open_window constructs windows with appropriate attributes and flags, sets window_type and window_id properties, and registers them in _active_windows.
- Visibility: show, raise_, activateWindow ensure windows are brought to the front.
- Closing: close_window closes a specific window and proactively removes it from the registry; close_all_windows iterates over copies of keys to avoid mutation during iteration; close_windows_of_type closes all windows of a given type.
- Cleanup: destroyed signal triggers _on_window_closed to remove the window from the registry.

```mermaid
flowchart TD
A["open_window()"] --> B{"allow_multiple?"}
B --> |Yes| C["Increment counter<br/>Generate window_id"]
B --> |No| D{"Already open?"}
D --> |Yes| E["Reuse existing<br/>Bring to front"]
D --> |No| F["Create new window"]
F --> G["Configure attributes and flags"]
G --> H["Connect destroyed signal"]
H --> I["Store in _active_windows"]
I --> J["Show and focus"]
E --> J
J --> K["Return window"]
L["close_window(window_id)"] --> M["window.close()"]
M --> N["Remove from registry"]
N --> O["Return True"]
P["close_all_windows()"] --> Q["Iterate over copy of keys"]
Q --> R["Call close_window for each"]
S["close_windows_of_type(window_type)"] --> T["Iterate active windows"]
T --> U{"window_type matches?"}
U --> |Yes| V["close_window(wid)"]
U --> |No| W["Skip"]
V --> X["Count closed"]
W --> Y["Continue"]
X --> Z["Return count"]
```

**Diagram sources**
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L29-L112)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L113-L161)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L136-L161)

**Section sources**
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L29-L112)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L113-L161)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L136-L161)

### Thread Safety Considerations
- The WindowManager uses Python dictionaries and basic integer counters for tracking windows and instance counts. These are not inherently thread-safe.
- The application uses a single-threaded Qt event loop. All window operations occur on the main thread, minimizing race conditions.
- Recommendations:
  - Avoid invoking WindowManager methods from worker threads. If threading is introduced, guard shared state with locks or post events to the main thread.
  - Ensure window creation and destruction occur on the main thread to respect Qt’s thread affinity.

[No sources needed since this section provides general guidance]

### Cross-Component Communication Examples
- DocumentManagerHub demonstrates cross-component communication by connecting a signal from a search window to a library window, which then opens the editor window via the WindowManager.
- AdytonHub passes the WindowManager to a window constructor, enabling that window to coordinate with others.

**Section sources**
- [src/pillars/document_manager/ui/document_manager_hub.py](file://src/pillars/document_manager/ui/document_manager_hub.py#L136-L175)
- [src/pillars/adyton/ui/adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py#L141-L148)

## Dependency Analysis
- Coupling: Hubs depend on WindowManager for window creation and coordination. This is a controlled dependency injection pattern.
- Cohesion: WindowManager encapsulates window lifecycle concerns, keeping hubs focused on UI orchestration.
- External dependencies: WindowManager relies on PyQt6 for window attributes, flags, and signals.
- No circular dependencies observed between main, hubs, and WindowManager.

```mermaid
graph TB
WM["WindowManager"] --> |used by| GH["GematriaHub"]
WM --> |used by| GeoH["GeometryHub"]
WM --> |used by| DMH["DocumentManagerHub"]
WM --> |used by| AH["AstrologyHub"]
WM --> |used by| TH["TQHub"]
WM --> |used by| ADH["AdytonHub"]
Main["IsopGemMainWindow"] --> WM
Main --> GH
Main --> GeoH
Main --> DMH
Main --> AH
Main --> TH
Main --> ADH
```

**Diagram sources**
- [src/main.py](file://src/main.py#L51-L69)
- [src/pillars/gematria/ui/gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py#L49-L70)
- [src/pillars/geometry/ui/geometry_hub.py](file://src/pillars/geometry/ui/geometry_hub.py#L12-L20)
- [src/pillars/document_manager/ui/document_manager_hub.py](file://src/pillars/document_manager/ui/document_manager_hub.py#L14-L27)
- [src/pillars/astrology/ui/astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py#L13-L26)
- [src/pillars/tq/ui/tq_hub.py](file://src/pillars/tq/ui/tq_hub.py#L17-L30)
- [src/pillars/adyton/ui/adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py#L114-L148)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L15-L112)

**Section sources**
- [src/main.py](file://src/main.py#L51-L69)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L15-L112)
- [src/pillars/gematria/ui/gematria_hub.py](file://src/pillars/gematria/ui/gematria_hub.py#L49-L70)
- [src/pillars/geometry/ui/geometry_hub.py](file://src/pillars/geometry/ui/geometry_hub.py#L12-L20)
- [src/pillars/document_manager/ui/document_manager_hub.py](file://src/pillars/document_manager/ui/document_manager_hub.py#L14-L27)
- [src/pillars/astrology/ui/astrology_hub.py](file://src/pillars/astrology/ui/astrology_hub.py#L13-L26)
- [src/pillars/tq/ui/tq_hub.py](file://src/pillars/tq/ui/tq_hub.py#L17-L30)
- [src/pillars/adyton/ui/adyton_hub.py](file://src/pillars/adyton/ui/adyton_hub.py#L114-L148)

## Performance Considerations
- Window creation overhead: Creating many windows can increase memory usage. Prefer single-instance windows for heavy tools.
- Visibility operations: Raising windows is lightweight, but excessive calls can cause flicker. The main window raises windows on tab changes; avoid redundant calls from hubs.
- Registry size: Large numbers of open windows increase dictionary lookups. Consider periodically cleaning up closed windows if needed.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- Windows not appearing: Ensure WA_DeleteOnClose and WA_QuitOnClose are configured appropriately for tool windows.
- Duplicate windows: Use allow_multiple=False for single-instance tools to reuse existing windows.
- Windows not closing cleanly: Confirm destroyed signal is connected and _on_window_closed removes entries from the registry.
- Testing lifecycle: Unit tests demonstrate reuse and multi-instance behavior, as well as closing by type.

**Section sources**
- [test/test_window_manager.py](file://test/test_window_manager.py#L1-L63)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L80-L112)
- [src/shared/ui/window_manager.py](file://src/shared/ui/window_manager.py#L186-L195)

## Conclusion
The isopgem application employs a clean dependency injection pattern: the WindowManager is instantiated early in the main window and passed to each pillar hub. This design centralizes window lifecycle management, ensures consistent behavior across pillars, and enables cross-component communication. The WindowManager’s APIs support single-instance and multi-instance windows, visibility management, and robust cleanup. While the application remains single-threaded, future enhancements should preserve main-thread-only operations for window management to maintain stability.