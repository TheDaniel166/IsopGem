# IsopGem Panel System Guide

## Overview
The IsopGem Panel System provides a flexible and robust way to create, manage, and display UI panels within the application. The system uses a combination of factories, registry, and manager patterns to ensure consistent panel creation and lifecycle management.

## Core Components

### 1. Panel Registry
The registry serves as a central factory for panel creation and management.

```python
from core.ui.panels.registry import get_registry

# Get panel registry instance
registry = get_registry()

# Register a panel factory
registry.register("My Panel", create_my_panel)

# Create a panel through registry
panel = registry.create_panel(
    panel_type="My Panel",
    panel_id="unique_id",  # Optional
    **kwargs              # Optional initialization parameters
)
```

### 2. Panel Manager
The manager handles panel lifecycle, docking, and state management.

```python
# Panel manager is accessed through MainWindow
manager = window.panel_manager

# Create panel with manager
dock = manager.create_panel(
    panel=my_panel_widget,
    panel_type="My Panel"
)
```

### 3. Base Panel
All panels should inherit from `BasePanel` for consistent behavior.

```python
from core.ui.panels.base import BasePanel

class MyPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent, title="My Panel")
        self.setup_ui()
        
    def setup_ui(self):
        # Panel-specific UI setup
        pass
```

## Panel Creation Methods

### Method 1: Through Registry (Recommended)
Best for panels that need factory pattern and lifecycle management.

```python
def show_my_panel(self):
    # Get registry instance
    registry = get_registry()
    
    # Create panel through registry
    panel = registry.create_panel(
        panel_type="My Panel",
        panel_id="unique_id",     # Optional
        content=some_content      # Optional initialization data
    )
    
    # Show panel through window
    if window := self.window():
        window.create_panel(
            panel=panel,
            name="My Panel"
        )
```

### Method 2: Direct Creation
For simpler panels or one-off instances.

```python
def show_simple_panel(self):
    # Create panel instance
    panel = MyPanel()
    
    # Show through window
    if window := self.window():
        window.create_panel(
            panel=panel,
            name="Simple Panel"
        )
```

## Panel Registration

### 1. Factory Registration
Register panel factories in `common_panels/__init__.py`:

```python
from ..registry import get_registry
from .my_panel import MyPanel

def create_my_panel():
    """Factory function for my panel"""
    return MyPanel()

# Register panel factories
registry = get_registry()
registry.register("My Panel", create_my_panel)
```

### 2. Panel Types
Common panel types include:
- Document Viewer
- Properties Panel
- Console Panel
- Theme Panel
- Custom Panels

## Best Practices

1. **Panel Creation**:
   - Always use named parameters for clarity
   - Provide unique IDs for panels that need persistence
   - Initialize content through factory if possible

2. **Panel Management**:
   - Let the manager handle panel lifecycle
   - Use registry for panel creation when possible
   - Store panel references appropriately

3. **Error Handling**:
   - Check window existence before panel creation
   - Handle panel creation failures gracefully
   - Log important panel lifecycle events

4. **State Management**:
   - Use panel IDs consistently
   - Save panel state when needed
   - Restore panel state appropriately

## Singleton Panels

Some panels in IsopGem need to maintain uniqueness and prevent duplicate initialization. These are called "Singleton Panels" and require special handling.

### Characteristics
- One instance per type/ID
- Self-protecting initialization
- State persistence
- Unique per context (e.g., one Document Viewer per document)

### Implementation Example
```python
class SingletonPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent, title="Singleton Panel")
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the panel UI with singleton protection"""
        # Guard against multiple initialization
        if hasattr(self, 'initialized') and self.initialized:
            logger.debug("Panel UI already initialized, skipping setup")
            return
            
        # Your UI setup code here
        self.toolbar = QToolBar()
        self.content_layout.addWidget(self.toolbar)
        
        # Mark as initialized
        self.initialized = True
```

### Registry Integration
The panel registry can be enhanced to support singleton panels by tracking 
existing instances and returning them instead of creating new ones:

```python
# Example registry method
def get_or_create_singleton_panel(panel_type, panel_id=None, **kwargs):
    """Get existing panel or create if not exists"""
    # Check for existing panel with ID
    if panel_id and panel_id in self.panels:
        panel = self.panels[panel_id]
        # Update with new kwargs if needed
        if hasattr(panel, 'initialize'):
            panel.initialize(**kwargs)
        return panel
        
    # Create new panel
    return self.create_panel(panel_type, panel_id, **kwargs)
```

### When to Use Singleton Panels
1. **Document Viewers**:
   - One viewer per document
   - Maintains document state
   - Prevents UI duplication

2. **Property Panels**:
   - Single properties view
   - Consistent state
   - Global application scope

3. **Console/Output Panels**:
   - Single output stream
   - Persistent history
   - Application-wide logging

### Benefits
- Prevents memory leaks
- Maintains consistent state
- Improves performance
- Self-documenting code
- Robust error prevention

### Best Practices
1. Add initialization guards in `setup_ui()`
2. Use clear sentinel attributes
3. Add debug logging for transparency
4. Keep initialization logic simple
5. Document singleton behavior

### Debugging Duplicate Panels
When troubleshooting duplicate panel issues, add debug logging to track panel creation:

```python
# In your panel creation code
logger.debug(f"Creating panel type={panel_type}, id={panel_id}")

# In your setup_ui guard
if hasattr(self, 'initialized') and self.initialized:
    logger.debug(f"Panel {self.objectName()} already initialized, skipping setup")
    return
```

### Initialization vs. Content Updates
While a singleton panel should protect against repeated UI initialization, 
it should still allow content updates. For example, a Document Viewer 
may need to display different documents while maintaining its singleton status.

## Example Implementation

```python
class MyTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.my_panel = None
        
    def show_my_panel(self):
        """Show my custom panel"""
        if window := self.window():
            # Create if not exists
            if not self.my_panel:
                registry = get_registry()
                self.my_panel = registry.create_panel(
                    panel_type="My Panel",
                    panel_id="my_unique_panel",
                    content=self.get_content()
                )
            
            # Show panel
            if self.my_panel:
                window.create_panel(
                    panel=self.my_panel,
                    name="My Panel"
                )
            else:
                logger.error("Failed to create panel")
```

## Troubleshooting

1. **Panel Not Showing**:
   - Check if window reference is valid
   - Verify panel type is registered
   - Ensure panel ID is unique

2. **Duplicate Panels**:
   - Use consistent panel IDs
   - Check panel creation logic
   - Verify manager state

3. **Panel State Issues**:
   - Check panel initialization
   - Verify dock widget creation
   - Review manager tracking
