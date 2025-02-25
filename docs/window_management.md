# Window Management

## Overview

IsopGem's window management system provides a robust framework for handling application windows, their states, and layouts. The system is built around the `MainWindow` class and integrates with various managers to provide a cohesive user experience.

## Core Components

### 1. Main Window
- Central application window
- Manages overall layout
- Coordinates managers
- Handles window state

### 2. Window Hierarchy
```
MainWindow
├── CentralWidget
│   ├── MainLayout
│   └── TabManager
├── PanelManager
│   ├── DockWidgets
│   └── Panels
├── ThemeManager
└── StatusBar
```

## Window Lifecycle

### 1. Initialization
```python
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IsopGem")
        
        # Set up central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Initialize managers
        self.panel_manager = PanelManager(self)
        self.theme_manager = ThemeManager.get_instance()
        
        # Set initial size
        self.resize(1200, 800)
```

### 2. Layout Management
- Central widget setup
- Layout configuration
- Margin handling
- Spacing control

### 3. State Management
- Window geometry
- Dock positions
- Panel states
- Layout persistence

## Manager Integration

### 1. Panel Manager
- Dock widget handling
- Panel creation
- Layout restoration
- State persistence

### 2. Tab Manager
- Tab organization
- Content management
- Navigation control
- State coordination

### 3. Theme Manager
- Window styling
- Color schemes
- Visual consistency
- Dynamic updates

## Window Features

### 1. Docking System
- Flexible dock areas
- Drag-and-drop support
- Nested docking
- Float capability

### 2. Status Bar
- Status messages
- Progress indicators
- System notifications
- State feedback

### 3. Layout Persistence
- Save window state
- Restore positions
- Remember sizes
- Maintain preferences

## State Management

### 1. Window State
```python
def save_window_state(self):
    """Save current window state"""
    settings = QSettings()
    settings.setValue("geometry", self.saveGeometry())
    settings.setValue("windowState", self.saveState())
    settings.setValue("size", self.size())
    settings.setValue("pos", self.pos())
```

### 2. Layout State
- Dock positions
- Panel visibility
- Tab arrangement
- Tool locations

### 3. View State
- Active panels
- Current tab
- Scroll positions
- Selection states

## Event Handling

### 1. Window Events
- Resize events
- Move events
- Focus events
- Close events

### 2. Layout Events
- Dock movements
- Panel changes
- Tab switches
- State updates

## Multi-Window Support

### 1. Window Creation
```python
def create_child_window(self):
    """Create a new child window"""
    child = ChildWindow(self)
    child.setAttribute(Qt.WA_DeleteOnClose)
    child.show()
    return child
```

### 2. Window Communication
- Parent-child relationship
- Event propagation
- State synchronization
- Resource sharing

## Best Practices

### 1. Window Management
- Handle window lifecycle
- Manage state properly
- Coordinate managers
- Control resources

### 2. Layout Handling
- Use proper layouts
- Maintain flexibility
- Consider scaling
- Handle resizing

### 3. State Persistence
- Save important states
- Restore correctly
- Handle errors
- Log changes

## Troubleshooting

1. **Window Issues**:
   - Check initialization
   - Verify geometry
   - Review state
   - Validate managers

2. **Layout Problems**:
   - Inspect dock areas
   - Check constraints
   - Verify spacing
   - Review margins

3. **State Issues**:
   - Validate saving
   - Check restoration
   - Debug persistence
   - Review logging

## Performance Considerations

### 1. Window Creation
- Lazy loading
- Resource management
- Memory optimization
- Creation timing

### 2. State Updates
- Batch updates
- Delayed saving
- Cache usage
- Event throttling

## See Also
- [Panel System Documentation](panel_system.md)
- [Theme System Documentation](theme_system.md)
- [UI Components Guide](ui_components.md)
