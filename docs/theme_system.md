# Theme System Documentation

## Overview

The IsopGem Theme System provides a flexible and user-friendly way to customize the application's appearance. It supports dynamic theme switching, color customization, and real-time preview capabilities.

## Core Components

### 1. Theme Manager
- Singleton instance for global theme management
- Handles theme switching and mode changes
- Emits signals for theme-related events
- Manages theme persistence

### 2. Theme Panel
- Dedicated panel for theme customization
- Fixed size (1200x700) for optimal layout
- Integrated with Theme Manager
- Houses the Theme Customizer widget

### 3. Theme Customizer
- Main widget for theme modification
- Color picker integration
- Real-time theme preview
- Theme import/export capabilities
- Theme preset management

### 4. Theme Preview
- Live preview of theme changes
- Representative UI elements
- Instant feedback for color adjustments

## Theme Structure

### Color Scheme
- Primary Colors
  - Main application color
  - Accent colors
  - Highlight colors
- Secondary Colors
  - Background colors
  - Text colors
  - Border colors
- State Colors
  - Success/Error states
  - Warning indicators
  - Information highlights

### Theme Modes
1. **Light Mode**
   - Default daytime theme
   - High contrast for readability
   - Lighter background palette

2. **Dark Mode**
   - Eye-friendly night theme
   - Reduced brightness
   - Dark background palette

## Usage Guide

### 1. Accessing Theme Customization
- Open Theme Panel from menu
- Use keyboard shortcut (if configured)
- Access via settings

### 2. Customizing Colors
```python
# Example: Changing theme color programmatically
theme_manager = ThemeManager.get_instance()
theme_manager.set_color("primary", "#FF5733")
```

### 3. Saving Themes
- Export current theme
- Import existing theme
- Create theme presets
- Apply theme to application

### 4. Best Practices
- Use consistent color schemes
- Test themes in both modes
- Consider accessibility
- Maintain color contrast
- Save changes frequently

## Implementation Example

```python
class ThemePanel(BasePanel):
    """Panel for theme customization"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Theme Customization")
        self._setup_ui()
        
        # Set fixed size and position
        self.setFixedSize(1200, 700)
        self.move(100, 100)
    
    def _setup_ui(self):
        """Set up the panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add theme customizer
        customizer = ThemeCustomizer()
        layout.addWidget(customizer)
```

## Event System

### Theme Changed Event
- Triggered on theme updates
- Propagates changes to UI
- Updates all themed components

### Mode Changed Event
- Handles light/dark mode switching
- Updates color schemes
- Maintains theme consistency

## Troubleshooting

1. **Theme Not Applying**:
   - Check theme manager instance
   - Verify color values
   - Ensure proper signal connections

2. **Preview Issues**:
   - Validate preview widget
   - Check theme updates
   - Verify color picker state

3. **Theme Persistence**:
   - Check save location
   - Verify file permissions
   - Validate theme format

## See Also
- [Panel System Documentation](panel_system.md)
- [UI Components Guide](ui_components.md)
- [Window Management](window_management.md)
