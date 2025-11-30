# IsopGem UI Architecture & Workflow

## Overview

The IsopGem application follows a **Hub-and-Spoke** UI pattern where each pillar has a central hub that launches individual tool windows.

## UI Component Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Application                          │
│                  (IsopGemMainWindow)                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Tab Widget                                 │ │
│  │  ┌──────┬──────┬──────┬──────┬──────┐                 │ │
│  │  │ Gem  │ Geom │ Docs │Astro │  TQ  │                 │ │
│  │  └──┬───┴──────┴──────┴──────┴──────┘                 │ │
│  │     │                                                   │ │
│  │     ▼                                                   │ │
│  │  ┌─────────────────────────────────┐                  │ │
│  │  │      Pillar Hub Widget          │                  │ │
│  │  │  ┌─────────┐  ┌─────────┐      │                  │ │
│  │  │  │ Tool 1  │  │ Tool 2  │      │                  │ │
│  │  │  │ [Open]  │  │ [Open]  │      │                  │ │
│  │  │  └─────────┘  └─────────┘      │                  │ │
│  │  └─────────────────────────────────┘                  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                         │
                         │ (Window Manager)
                         ▼
              ┌──────────────────────┐
              │   Tool Window 1      │  (Separate QMainWindow)
              │  (GematriaCalculator)│
              └──────────────────────┘
              ┌──────────────────────┐
              │   Tool Window 2      │  (Separate QMainWindow)
              │  (NumberAnalyzer)    │
              └──────────────────────┘
```

## User Workflow

### 1. Application Launch
```
User opens app
  ↓
Main window displays with 5 tabs (one per pillar)
  ↓
Default tab: Gematria (first pillar)
```

### 2. Navigating Pillars
```
User clicks tab (e.g., "📖 Gematria")
  ↓
Hub widget displays for that pillar
  ↓
Hub shows:
  - Pillar title & description
  - Grid of available tools
  - Each tool has: icon, title, description, "Open" button
```

### 3. Launching Tools
```
User clicks "Open" on a tool card
  ↓
Hub calls window_manager.open_window()
  ↓
Window Manager checks if window already exists
  ├─ If exists: brings to front
  └─ If new: creates and shows window
  ↓
Tool window appears (separate from main window)
  ↓
User can launch multiple tools simultaneously
```

### 4. Working with Tools
```
Tool windows are independent QMainWindow instances
  ↓
User can:
  - Move/resize tool windows freely
  - Keep multiple tools open
  - Switch between tools
  - Return to hub to launch more tools
  ↓
Windows persist until user closes them
```

## Component Responsibilities

### Main Window (`main.py`)
- **Responsibility**: Application shell
- **Contains**: Tab widget with pillar hubs
- **Manages**: Window manager instance
- **Does NOT**: Contain tool logic

### Window Manager (`shared/ui/window_manager.py`)
- **Responsibility**: Window lifecycle management
- **Functions**:
  - `open_window()` - Create or focus window
  - `close_window()` - Close specific window
  - `close_all_windows()` - Cleanup on app exit
  - `is_window_open()` - Check window state
  - `get_window()` - Get window reference
- **Tracks**: All active tool windows
- **Prevents**: Duplicate windows

### Pillar Hub Widgets (`pillars/*/ui/*_hub.py`)
- **Responsibility**: Tool launcher interface
- **Contains**: 
  - Pillar branding
  - Tool cards/buttons
  - Launch callbacks
- **Does NOT**: Contain tool implementation

### Tool Windows (`pillars/*/ui/*_window.py`)
- **Responsibility**: Actual tool functionality
- **Contains**: 
  - Tool UI
  - Business logic integration
  - User interactions
- **Type**: QMainWindow (independent windows)

## Directory Structure

```
src/
├── main.py                              # Main application entry
├── shared/
│   └── ui/
│       ├── window_manager.py            # Window lifecycle manager
│       └── __init__.py
└── pillars/
    ├── gematria/
    │   ├── ui/
    │   │   ├── gematria_hub.py          # Hub with tool buttons
    │   │   ├── gematria_calculator_window.py  # Tool window
    │   │   └── __init__.py
    │   └── services/
    │       └── ...                       # Business logic
    ├── geometry/
    │   └── ui/
    │       ├── geometry_hub.py
    │       └── ...                       # Future tool windows
    └── ...
```

## Code Flow Example

### Opening the Gematria Calculator

1. **User Action**: Clicks "Open" on Gematria Calculator card

2. **GematriaHub** (`gematria_hub.py`):
```python
def _open_calculator(self):
    calculators = [HebrewGematriaCalculator()]
    
    self.window_manager.open_window(
        window_id="gematria_calculator",
        window_class=GematriaCalculatorWindow,
        calculators=calculators
    )
```

3. **WindowManager** (`window_manager.py`):
```python
def open_window(self, window_id, window_class, *args, **kwargs):
    # Check if already open
    if window_id in self._active_windows:
        self._active_windows[window_id].raise_()
        return
    
    # Create new window
    window = window_class(*args, **kwargs)
    window.destroyed.connect(lambda: self._cleanup(window_id))
    self._active_windows[window_id] = window
    window.show()
```

4. **GematriaCalculatorWindow** (`gematria_calculator_window.py`):
```python
class GematriaCalculatorWindow(QMainWindow):
    def __init__(self, calculators):
        super().__init__()
        self.calculators = calculators
        self._setup_ui()
        # Tool-specific logic
```

## Adding New Tools

### Step 1: Create Tool Window
```python
# pillars/gematria/ui/new_tool_window.py
from PyQt6.QtWidgets import QMainWindow

class NewToolWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Tool")
        # Setup UI
```

### Step 2: Add to Hub
```python
# pillars/gematria/ui/gematria_hub.py
def _open_new_tool(self):
    self.window_manager.open_window(
        window_id="gematria_new_tool",
        window_class=NewToolWindow
    )

# In _setup_ui():
new_tool_btn = self._create_tool_button(
    "New Tool",
    "Description of new tool",
    self._open_new_tool,
    enabled=True
)
```

### Step 3: Done!
No changes needed to:
- Main window
- Window manager
- Other pillars

## Benefits of This Architecture

### ✅ Separation of Concerns
- Hubs handle navigation
- Window Manager handles lifecycle
- Tool windows handle functionality

### ✅ Scalability
- Add tools without modifying core
- Each pillar is independent
- No tight coupling

### ✅ Reusability
- Window Manager is shared across all pillars
- Hub pattern is consistent
- Tool windows are self-contained

### ✅ User Experience
- Clean, organized interface
- Multiple tools can be open
- No duplicate windows
- Easy tool discovery

### ✅ Maintainability
- Clear code organization
- Easy to debug
- Simple to extend
- Consistent patterns

## Window Management Features

### Singleton Windows
Each window has a unique ID. Opening the same tool twice brings the existing window to front instead of creating a duplicate.

### Automatic Cleanup
When a window is closed, the Window Manager automatically removes it from tracking.

### Parent Relationship
Tool windows are independent but can optionally have parent relationship for better window management.

### Lifecycle Hooks
Windows can be tracked throughout their lifecycle for analytics, state persistence, etc.

## Future Enhancements

### Planned Features
1. **Window State Persistence**
   - Remember window positions
   - Restore open windows on app restart

2. **Window Grouping**
   - Group related tool windows
   - Tab groups within tool windows

3. **Workspace Management**
   - Save/load window layouts
   - Predefined workspace configurations

4. **Enhanced Hub Features**
   - Recent tools list
   - Favorite tools
   - Tool search/filter
   - Usage statistics

5. **Inter-Window Communication**
   - Share data between tools
   - Event bus for tool coordination

## Best Practices

### For Hub Widgets
- Keep hubs focused on navigation
- Use consistent button styling
- Provide clear tool descriptions
- Group related tools logically

### For Tool Windows
- Inherit from QMainWindow for independence
- Set appropriate window titles
- Handle window close events properly
- Save state before closing

### For Window Manager Usage
- Use descriptive window IDs
- Check if window is open before operations
- Clean up resources in window destructors
- Handle edge cases (nullptr, etc.)

## Summary

The IsopGem UI architecture provides a clean, scalable framework for building a multi-pillar application where:

1. **Main Window** provides the shell and tab navigation
2. **Pillar Hubs** act as tool launchers
3. **Window Manager** handles window lifecycle centrally
4. **Tool Windows** contain the actual functionality

This separation makes the application easy to extend, maintain, and use.
