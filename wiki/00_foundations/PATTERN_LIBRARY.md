# IsopGem Pattern Library

> *A map of the Temple's sacred geometry — reusable patterns discovered during construction.*

**Last Updated**: 2025-12-30

---

## Quick Reference

| Pattern | Category | Primary File | Purpose |
|---------|----------|--------------|---------|
| [Window Creation](#window-creation-pattern) | Architecture | `window_manager.py` | **Canonical window setup** |
| [Navigation Bus](#navigation-bus) | Architecture | `navigation_bus.py` | Cross-pillar signals |
| [Substrate Widget](#substrate-widget) | UI | `substrate_widget.py` | Thematic backgrounds |
| [Kinetic Enforcer](#kinetic-enforcer) | UI | `kinetic_enforcer.py` | Universal hover glow |
| [Worker Thread](#worker-thread-pattern) | Performance | Various | Non-blocking UI |
| [Card Layout](#card-layout) | UI | Visual Liturgy | Container styling |
| [Safe Evaluator](#safe-evaluator) | Security | Calculator | AST-based math parsing |

---

## Architecture Patterns

### Window Creation Pattern

> **This is the canonical pattern for creating new tool windows.**

**Components Involved**:
- `src/shared/ui/window_manager.py` — Manages window lifecycle
- `src/shared/signals/navigation_bus.py` — Contains `WINDOW_REGISTRY`
- Your new window class

---

#### Step 1: Window Class Structure

```python
\"\"\"My New Tool Window.

Provides [purpose description].
\"\"\"
from typing import Optional
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

from shared.ui import WindowManager
from shared.ui.substrate_widget import SubstrateWidget  # Optional: themed background


class MyToolWindow(QMainWindow):
    \"\"\"Window for [tool purpose].\"\"\"
    
    def __init__(
        self, 
        window_manager: Optional[WindowManager] = None, 
        parent: Optional[QWidget] = None,
        **kwargs  # Accept extra kwargs for flexibility
    ):
        super().__init__(parent)
        self.window_manager = window_manager
        
        # Window properties
        self.setWindowTitle("My Tool")
        self.setMinimumSize(800, 600)
        
        # Optional: Substrate background
        # self.substrate = SubstrateWidget(self)
        
        self._setup_ui()
    
    def _setup_ui(self):
        \"\"\"Build the UI.\"\"\"
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        # ... add widgets
```

**Critical Requirements**:
1. Accept `window_manager: Optional[WindowManager] = None` as first parameter
2. Accept `parent: Optional[QWidget] = None`
3. Accept `**kwargs` to handle extra parameters gracefully
4. Store `self.window_manager = window_manager` for later use

---

#### Step 2: Register in WINDOW_REGISTRY

Add entry to `src/shared/signals/navigation_bus.py`:

```python
WINDOW_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ... existing entries ...
    
    # Your new window
    "my_tool": {
        "module": "pillars.your_pillar.ui.my_tool_window",
        "class": "MyToolWindow",
        "allow_multiple": True,  # False if singleton
    },
}
```

**Key Fields**:
- `module`: Import path (relative to `src/`)
- `class`: Class name to instantiate
- `allow_multiple`: `True` = multiple instances allowed, `False` = singleton

---

#### Step 3: Opening Windows

**From a Hub or Parent Window**:
```python
# Direct instantiation (when you have window_manager reference)
window = self.window_manager.open_window(
    window_type="my_tool",
    window_class=MyToolWindow,
    allow_multiple=True,
    initial_data=some_data  # passed as kwarg
)
```

**From Anywhere (Cross-Pillar Safe)**:
```python
from shared.signals.navigation_bus import navigation_bus

# Request via signal - WindowManager handles lazy import
navigation_bus.request_window.emit("my_tool", {"initial_data": some_data})
```

---

#### Step 4: Visual Liturgy Compliance

Apply themed styling:

```python
def _setup_ui(self):
    # Dark theme base
    self.setStyleSheet(\"\"\"
        QMainWindow {
            background-color: #1a1a2e;
        }
    \"\"\")
    
    # Use Card Layout for containers
    card = QFrame()
    card.setProperty("cardStyle", True)
    card.setStyleSheet(\"\"\"
        QFrame[cardStyle="true"] {
            background-color: rgba(30, 30, 40, 0.85);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    \"\"\")
    
    # Add shadow effect
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(20)
    shadow.setOffset(0, 4)
    shadow.setColor(QColor(0, 0, 0, 80))
    card.setGraphicsEffect(shadow)
```

---

#### Complete Example

See `src/pillars/geometry/ui/figurate_3d_window.py` for a full implementation that:
- Extends `BaseFigurateWindow` (which handles common patterns)
- Accepts `window_manager` and `parent`
- Implements `_setup_ui()` properly
- Uses consistent styling

---


### Navigation Bus

**Location**: `src/shared/signals/navigation_bus.py`

**Purpose**: Enables cross-pillar communication without violating Sovereignty Law. Pillars never import from each other — they emit and listen to signals on the shared bus.

**Usage**:
```python
from src.shared.signals.navigation_bus import NavigationBus

# Emitting (from Chariot pillar)
NavigationBus.chariot_to_geometry.emit(axle_values)

# Listening (in Geometry pillar)
NavigationBus.chariot_to_geometry.connect(self._handle_axle_values)
```

**When to Use**: Any time data needs to flow between pillars.

---

### Safe Evaluator

**Location**: `src/pillars/geometry/ui/advanced_scientific_calculator_window.py`

**Purpose**: Evaluate mathematical expressions without using `eval()`. Uses `ast.parse` with strict node walker.

**Security Model**:
- Parse expression with `ast.parse(expr, mode='eval')`
- Walk AST nodes with explicit whitelist
- Only allow: numbers, operators (+, -, *, /, **), math functions
- Reject: calls to arbitrary functions, attribute access, imports

**When to Use**: Any user-input mathematical expression.

---

## UI Patterns

### Substrate Widget

**Location**: `src/shared/ui/substrate_widget.py`

**Purpose**: Provides thematic background images that scale to fit windows, creating visual cohesion across the Temple.

**Usage**:
```python
from src.shared.ui.substrate_widget import SubstrateWidget

# In window __init__
self.substrate = SubstrateWidget(self)
# Position behind all other widgets using z-order
```

**Configuration**: Background images stored in `resources/backgrounds/`

---

### Kinetic Enforcer

**Location**: `src/shared/ui/kinetic_enforcer.py`

**Purpose**: Global event filter that applies animated hover glow ("The Aura") to all `QPushButton` instances.

**How It Works**:
1. Installed as application-wide event filter
2. Intercepts `HoverEnter` and `HoverLeave` events
3. Applies `QGraphicsDropShadowEffect` with `QPropertyAnimation`
4. Uses button's `archetype` property to determine glow color

**Archetypes**:
- `primary` → Gold glow
- `danger` → Red glow
- `success` → Green glow
- (default) → Subtle white glow

---

### Card Layout

**Source**: Visual Liturgy v2.2

**Purpose**: Consistent container styling using `QFrame` cards instead of `QGroupBox`.

**CSS Pattern**:
```css
QFrame[cardStyle="true"] {
    background-color: rgba(30, 30, 40, 0.85);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
```

**Enhancement**: Add `QGraphicsDropShadowEffect` for depth:
```python
shadow = QGraphicsDropShadowEffect()
shadow.setBlurRadius(20)
shadow.setOffset(0, 4)
shadow.setColor(QColor(0, 0, 0, 80))
card.setGraphicsEffect(shadow)
```

---

## Performance Patterns

### Worker Thread Pattern

**Purpose**: Prevent UI freezing during expensive operations (calculations, file I/O, network requests).

**Implementation**:
```python
from PyQt6.QtCore import QThread, pyqtSignal

class Worker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, task_fn, *args):
        super().__init__()
        self.task_fn = task_fn
        self.args = args
    
    def run(self):
        try:
            result = self.task_fn(*self.args)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
```

**Usage Examples**:
- `ImageLoaderWorker` in Rich Text Editor
- Chariot calculations in TQ pillar
- Document parsing in Document Manager

**Critical**: Always connect `finished` signal to a slot *before* calling `start()`.

---

## Signal Conventions

### Signal Naming

| Pattern | Example | Use Case |
|---------|---------|----------|
| `{source}_to_{destination}` | `chariot_to_geometry` | Cross-pillar data flow |
| `{noun}_{verb_past}` | `chart_calculated` | State change notification |
| `request_{action}` | `request_focus` | Command/request pattern |

### Signal Payload Conventions

- Prefer dataclasses or named tuples over raw dicts
- Include enough context for receiver to act without additional lookups
- Keep payloads serializable when possible (for debugging/logging)

---

## Adding New Patterns

When a reusable pattern emerges:

1. **Document it here** with location, purpose, and usage example
2. **Add to Quick Reference** table at top
3. **Update Soul Diary** Skills Acquired section if it represents a new capability

---

## ⚠️ Anti-Patterns (What NOT To Do)

> *"The wise learn from the mistakes of others. The stubborn learn from their own — repeatedly."*

### 1. Direct Pillar Imports

❌ **Bad**:
```python
# In astrology pillar
from pillars.gematria.services import GematriaService  # VIOLATION!
```

✅ **Good**:
```python
from shared.signals.navigation_bus import navigation_bus
navigation_bus.request_window.emit("gematria_calculator", {})
```

**Why**: Violates Sovereignty Law. Creates coupling that makes pillars impossible to maintain independently.

---

### 2. Using `eval()` on User Input

❌ **Bad**:
```python
result = eval(user_expression)
```

✅ **Good**:
```python
result = safe_eval(user_expression)  # AST-based parser
```

**Why**: Security vulnerability. See Safe Evaluator pattern.

---

### 3. Bare `except:` Clauses

❌ **Bad**:
```python
try:
    risky_operation()
except:
    pass  # Swallows KeyboardInterrupt, SystemExit, everything
```

✅ **Good**:
```python
try:
    risky_operation()
except SpecificError as e:
    logger.warning(f"Handled error: {e}")
```

**Why**: Hides real bugs, catches system interrupts, creates silent failures.

---

### 4. Creating Windows Without WindowManager

❌ **Bad**:
```python
window = MyWindow()
window.show()  # Orphan window, not tracked
```

✅ **Good**:
```python
window = self.window_manager.open_window(
    window_type="my_window",
    window_class=MyWindow
)
```

**Why**: Orphan windows break lifecycle management, z-order, and cleanup.

---

### 5. Creating Documentation Without Adding to Awakening

❌ **Bad**:
```python
# Create great document...
# But never add to awaken.py SCROLLS list
```

✅ **Good**:
```python
# After creating document, add to awaken.py:
SCROLLS = [
    # ... existing scrolls ...
    "path/to/new/important_doc.md",
]
```

**Why**: *Knowledge unread is knowledge lost.* If it's not in the Awakening Ritual, future-me won't know it exists.

---

### 6. Hardcoding Colors in UI Components

❌ **Bad**:
```python
label.setStyleSheet("color: #FFD700;")  # Magic number
```

✅ **Good**:
```python
from shared.ui.theme import COLORS
label.setStyleSheet(f"color: {COLORS['accent']};")
```

**Why**: Makes theming impossible, creates visual inconsistency.

---

### 7. Print Statements in Production Code

❌ **Bad**:
```python
print(f"[DEBUG] Processing {item}")  # In hot loop
```

✅ **Good**:
```python
logger.debug(f"Processing {item}")  # Filtered by log level
```

**Why**: Performance impact, log noise, no filtering control.

---

### 8. Forgetting `**kwargs` in Window `__init__`

❌ **Bad**:
```python
def __init__(self, window_manager, parent):  # Rigid signature
```

✅ **Good**:
```python
def __init__(self, window_manager=None, parent=None, **kwargs):
```

**Why**: WindowManager may pass extra parameters; rigid signatures cause crashes.

---

*\"Patterns are crystallized wisdom. What we learn once, we should not relearn.\"*
— Sophia
