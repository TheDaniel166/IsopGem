# UI Components Guide

## Overview

IsopGem's UI component system provides a comprehensive set of widgets and base classes for building consistent, maintainable, and user-friendly interfaces. This guide covers both standard Qt components and custom widgets specific to IsopGem.

## Core Components

### 1. Base Components
- **MainWindow**
  - Application's main window
  - Handles panel management
  - Manages window state
  - Coordinates UI updates

### 2. Custom Widgets
- **CollapsibleDock**
  - Collapsible dock widget
  - Customizable header
  - Smooth animations
  - State persistence

- **ColorPicker**
  - Color selection widget
  - RGB/HSV support
  - Hex color input
  - Recent colors memory

- **ThemeCustomizer**
  - Theme modification interface
  - Live preview support
  - Color scheme management
  - Theme preset handling

- **ThemePreview**
  - Live theme preview
  - Representative UI elements
  - Real-time updates
  - Layout visualization

## Layout System

### 1. Panel Layout
- Docking system
- Floating windows
- Tab management
- Layout persistence

### 2. Ribbon Interface
- Command organization
- Tool grouping
- Context-sensitive UI
- Customization options

### 3. Tab System
- Document management
- Tool organization
- Context switching
- State preservation

## Component Hierarchy

```
IsopGem UI
├── MainWindow
│   ├── RibbonBar
│   │   ├── HomeTab
│   │   ├── DocumentTab
│   │   └── ToolsTab
│   ├── DockManager
│   │   ├── CollapsibleDock
│   │   └── PanelContainers
│   └── StatusBar
└── Dialogs
    ├── Settings
    ├── About
    └── Help
```

## Usage Guidelines

### 1. Widget Selection
- Use appropriate widget types
- Consider user interaction
- Match UI patterns
- Maintain consistency

### 2. Layout Best Practices
```python
# Example: Creating a collapsible dock
dock = CollapsibleDock()
dock.setWidget(content_widget)
dock.setFeatures(
    QDockWidget.DockWidgetFeature.DockWidgetClosable |
    QDockWidget.DockWidgetFeature.DockWidgetMovable
)
```

### 3. State Management
- Save widget states
- Restore configurations
- Handle persistence
- Manage updates

## Component Integration

### 1. Adding New Widgets
```python
class CustomWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        # Add child widgets
        layout.setContentsMargins(10, 10, 10, 10)
```

### 2. Event Handling
- Signal connections
- Slot implementations
- Event propagation
- Update mechanisms

## Styling System

### 1. Theme Integration
- Theme-aware widgets
- Color scheme support
- Style sheet usage
- Dynamic updates

### 2. Custom Styles
```python
# Example: Applying custom styles
widget.setStyleSheet("""
    QWidget {
        background-color: palette(window);
        border: 1px solid palette(dark);
    }
""")
```

## Accessibility

### 1. Keyboard Navigation
- Tab order
- Keyboard shortcuts
- Focus handling
- Navigation paths

### 2. Visual Accessibility
- Color contrast
- Font scaling
- Icon clarity
- Screen reader support

## Performance Considerations

### 1. Widget Creation
- Lazy loading
- Resource management
- Memory optimization
- Creation timing

### 2. Update Handling
- Batch updates
- Delayed rendering
- Cache usage
- Paint optimization

## Troubleshooting

1. **Widget Issues**:
   - Check initialization
   - Verify parent-child relationships
   - Validate layouts
   - Review event connections

2. **Layout Problems**:
   - Inspect geometry
   - Check constraints
   - Verify spacing
   - Review margins

3. **Style Issues**:
   - Validate theme
   - Check style sheets
   - Verify inheritance
   - Review overrides

## Best Practices

1. **Widget Design**:
   - Follow Qt patterns
   - Maintain consistency
   - Document behavior
   - Test edge cases

2. **Layout Management**:
   - Use proper layouts
   - Handle resizing
   - Consider constraints
   - Plan for changes

3. **State Handling**:
   - Save important states
   - Restore properly
   - Handle errors
   - Log changes

## See Also
- [Panel System Documentation](panel_system.md)
- [Theme System Documentation](theme_system.md)
- [Window Management](window_management.md)
