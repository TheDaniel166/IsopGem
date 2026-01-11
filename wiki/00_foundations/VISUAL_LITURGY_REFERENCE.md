# Visual Liturgy Quick Reference

> *The aesthetic laws of the Temple — colors, spacing, typography, and components.*

**Purpose**: This is the **implementation cheat sheet** for the UI. It contains the raw hex codes, spacing units, and code snippets required to build the interface.
**For Theory**: See [UI_UX_PHILOSOPHY.md](../01_blueprints/UI_UX_PHILOSOPHY.md) for the "Floating Temple" conceptual framework, tone of voice, and semantic reasoning.

**Version**: 2.2  
**Last Updated**: 2025-12-30

9: **Last Updated**: 2026-01-09
10: 
11: ---
12: 
13: ## The Exemption: Ritual Instruments
14: 
15: **"The View is Hollow, but the Instrument is Dense."**
16: 
17: A **Ritual Instrument** (e.g., Zodiacal Circle, Chart Canvas, Kamea) is distinct from UI Chrome.
18: 
19: *   **Content, Not Chrome**: Its geometry and color are semantic data, not decoration.
20: *   **Visual Cognition**: It is a tool for thinking, not just controlling.
21: *   **Bespoke Integrity**: Enforcing standard tokens would damage symbolical function.
22: 
23: **The Law:** Instruments are **Exempt** from Visual Liturgy token enforcement.
24: **The Sign:** Mark file with `@RiteExempt: Visual Liturgy`.
25: 
26: ---

## Color Palette

**Note:** HTML/CSS used for document rendering (e.g., inside `QTextBrowser`) is considered **content**, not UI chrome, and is **exempt** from Visual Liturgy token enforcement.

### 1. The Day Liturgy (Light Mode)

> *The default state of the Temple.*

| Token | Name | Hex | Usage |
|-------|------|-----|-------|
| `cloud` | **Cloud Slate** | `#f8fafc` | Substrate / Window Background |
| `marble` | **Marble Slate** | `#f1f5f9` | Tablets / Panels / Cards |
| `light` | **Pure Light** | `#ffffff` | Input Fields (The Vessel) |
| `void` | **Void Text** | `#0f172a` | Primary Content / Headers |
| `stone` | **Stone Text** | `#334155` | Secondary Content / Body |
| `ash` | **Ash** | `#cbd5e1` | Borders / Dividers |

### 2. The Night Liturgy (Dark Mode)

> *The inverted state for low-light environments.*

| Token | Name | Hex | Usage |
|-------|------|-----|-------|
| `temple_dark` | **Temple Dark** | `#1a1a2e` | Window Background |
| `card_surface` | **Card Surface** | `rgba(30, 30, 40, 0.85)` | Tablets / Panels |
| `void_deep` | **Deep Void** | `#0f0f1a` | Input Backgrounds |
| `text_primary_v2` | **Cloud Text** | `#F8FAFC` | Primary Content |
| `text_secondary_v2` | **Mist Text** | `#94A3B8` | Secondary Content |

### 3. Shared Accents (The Catalysts)

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Gold/Amber** | `#FFD700` | `(255, 215, 0)` | Primary accent, highlights |
| **Amber Glow** | `#F59E0B` | `(245, 158, 11)` | Secondary warm accent |
| **Celestial Blue** | `#3B82F6` | `(59, 130, 246)` | Links, interactive elements |
| **Purple Magus** | `#8B5CF6` | `(139, 92, 246)` | Special actions |

### 4. Semantic Colors

| Name | Hex | Usage |
|------|-----|-------|
| **Success** | `#22C55E` | Positive feedback |
| **Warning** | `#F59E0B` | Caution states |
| **Danger** | `#EF4444` | Destructive actions |
| **Muted** | `#64748B` | Secondary text |



---

## Typography

### Font Stack

```css
font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
```

### Scale

| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| **H1** | `24pt` | 800 | Window titles |
| **H2** | `18pt` | 700 | Section headers |
| **H3** | `14pt` | 600 | Card titles |
| **Body** | `11pt` | 400 | Content |
| **Small** | `9pt` | 400 | Captions, hints |

---

## Spacing

### Base Unit: `8px`

| Token | Value | Usage |
|-------|-------|-------|
| `spacing-xs` | `4px` | Tight inline spacing |
| `spacing-sm` | `8px` | Default element gap |
| `spacing-md` | `16px` | Section gaps |
| `spacing-lg` | `24px` | Card padding |
| `spacing-xl` | `32px` | Window margins |

### Layout Margins

```python
# Window content margins
layout.setContentsMargins(14, 14, 14, 14)

# Card internal padding
card_layout.setContentsMargins(24, 32, 24, 32)
```

---

## Components

### Card Layout

### Card Layout

**Day Liturgy**:
```python
card.setStyleSheet("""
    QFrame[cardStyle="true"] {
        background-color: #f1f5f9; /* Marble Slate */
        border-radius: 12px;
        border: 1px solid #cbd5e1; /* Ash */
    }
""")
```

**Night Liturgy**:
```python
card.setStyleSheet("""
    QFrame[cardStyle="true"] {
        background-color: rgba(30, 30, 40, 0.85); /* Card Surface */
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
""")
```

# Shared Shadow
shadow = QGraphicsDropShadowEffect()
shadow.setBlurRadius(20)
shadow.setOffset(0, 4)
shadow.setColor(QColor(0, 0, 0, 80))
card.setGraphicsEffect(shadow)
```

### Buttons

**Primary (Gold)**:
```css
QPushButton[archetype="primary"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                stop:0 #F59E0B, stop:1 #D97706);
    color: #1a1a2e;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
}
```

**Ghost (Subtle) - Night Liturgy**:
```css
QPushButton {
    background-color: rgba(255, 255, 255, 0.1);
    color: #F8FAFC;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
}
QPushButton:hover {
    background-color: rgba(255, 255, 255, 0.15);
}
```

**Ghost (Subtle) - Day Liturgy**:
```css
QPushButton {
    background-color: rgba(0, 0, 0, 0.05); /* Faint Shadow */
    color: #0f172a; /* Void Text */
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
}
QPushButton:hover {
    background-color: rgba(0, 0, 0, 0.1);
}
```

**Danger**:
```css
QPushButton[archetype="danger"] {
    background-color: #EF4444;
    color: white;
}
```

### Input Fields

**Day Liturgy**:
```css
QLineEdit, QTextEdit, QSpinBox, QComboBox {
    background-color: #ffffff; /* Pure Light */
    border: 1px solid #cbd5e1; /* Ash */
    border-radius: 8px;
    padding: 10px 14px;
    color: #0f172a; /* Void */
    font-size: 11pt;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #F59E0B;
}
```

**Night Liturgy**:
```css
QLineEdit, QTextEdit, QSpinBox, QComboBox {
    background-color: rgba(15, 15, 26, 0.8); /* Void Deep */
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 10px 14px;
    color: #F8FAFC;
    font-size: 11pt;
}

QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #F59E0B;
}
```

### Vertical Tabs

```python
# Use QListWidget for navigation, QStackedWidget for content
tab_list = QListWidget()
tab_list.setFixedWidth(180)
tab_list.setStyleSheet("""
    QListWidget {
        background-color: transparent;
        border: none;
    }
    QListWidget::item {
        padding: 12px 16px;
        border-radius: 8px;
        margin: 2px 8px;
    }
    QListWidget::item:selected {
        background-color: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
    }
""")
```

---

## Effects

### Glassmorphism

```css
background-color: rgba(30, 30, 40, 0.7);
backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.1);
```

### The Aura (Hover Glow)

Applied automatically by `KineticEnforcer`:
- Gold glow for `primary` archetype
- Red glow for `danger` archetype
- Subtle white glow for default buttons

### Drop Shadow

```python
shadow = QGraphicsDropShadowEffect()
shadow.setBlurRadius(20)
shadow.setOffset(0, 4)
shadow.setColor(QColor(0, 0, 0, 80))
widget.setGraphicsEffect(shadow)
```

---

## Border Radius

| Element | Radius |
|---------|--------|
| Buttons | `8px` |
| Cards | `12px` |
| Input fields | `8px` |
| Dialogs | `16px` |
| Floating panels | `24px` |

---

## Quick Copy-Paste

### 1. Window Bases

**Day Liturgy (Light)**:
```python
self.setStyleSheet("""
    QMainWindow {
        background-color: #f8fafc; /* Cloud Slate */
    }
""")
```

**Night Liturgy (Dark)**:
```python
self.setStyleSheet("""
    QMainWindow {
        background-color: #1a1a2e; /* Temple Dark */
    }
""")
```

### Substrate Background
```python
from shared.ui.substrate_widget import SubstrateWidget
self.substrate = SubstrateWidget(self)
```

### Theme Colors Import
```python
from shared.ui.theme import COLORS
# COLORS['accent'], COLORS['surface'], etc.
```

---

## The Sacred Pattern: Archetype Buttons

### The Problem of Stylesheet Inheritance

**Critical Discovery**: When you call `.setStyleSheet()` on a parent widget, it creates a **local stylesheet** that:
1. Takes precedence over the application stylesheet
2. Applies to that widget AND all its children
3. **Blocks archetype styles** (e.g., `QPushButton[archetype="magus"]`) from reaching child buttons

This is Qt's stylesheet cascade behavior — local stylesheets **replace** rather than extend the app stylesheet.

### The Solution: Specific Object Selectors

Use **object name selectors** (`#ObjectName`) to ensure styles apply ONLY to that specific widget, not its children.

#### ❌ WRONG: Generic Selector (Breaks Archetypes)

```python
# This breaks archetype buttons inside the container!
container = QWidget()
container.setStyleSheet(f"""
    QWidget {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 24px;
    }}
""")
```

**Result**: Child buttons lose their archetype styling (magus, ghost, seeker, etc.)

#### ✅ RIGHT: Specific Object Selector (Preserves Archetypes)

```python
# This preserves archetype buttons inside!
container = QFrame()  # Use QFrame for better semantics
container.setObjectName("MyContainer")
container.setStyleSheet(f"""
    QFrame#MyContainer {{
        background-color: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 24px;
    }}
""")
```

**Result**: Only `container` gets styled; child buttons retain archetype styles from app stylesheet.

### The Complete Pattern

```python
from PyQt6.QtWidgets import QFrame, QPushButton
from PyQt6.QtCore import Qt
from shared.ui.theme import COLORS, set_archetype, apply_tablet_shadow

# 1. Create container with specific object name
container = QFrame()
container.setObjectName("FloatingPanel")
container.setFrameShape(QFrame.Shape.StyledPanel)

# 2. Apply style ONLY to this specific widget
container.setStyleSheet(f"""
    QFrame#FloatingPanel {{
        background-color: {COLORS['light']};
        border: 2px solid {COLORS['magus_soft']};
        border-radius: 12px;
    }}
""")

# 3. Add shadow (optional)
apply_tablet_shadow(container)

# 4. Create button with archetype
button = QPushButton("Invoke")
button.setMinimumHeight(42)
button.clicked.connect(handler)
set_archetype(button, "magus")  # This works because container stylesheet is specific!
button.setCursor(Qt.CursorShape.PointingHandCursor)
```

### Key Rules

1. **Always use `QFrame#ObjectName` selector** when styling containers
2. **Never use generic selectors** like `QWidget {{` or `QPushButton {{` in local stylesheets
3. **Set archetype AFTER properties** but BEFORE adding to layout
4. **Use `QFrame` over `QWidget`** for containers that need styling (better semantics)
5. **Add cursor AFTER archetype** for consistent order

### Example: Floating Calculator Island

```python
# Floating overlay that preserves button archetypes
calculator_container = QFrame(parent_widget)
calculator_container.setObjectName("FloatingCalculator")
calculator_container.setFrameShape(QFrame.Shape.StyledPanel)

# Specific selector preserves child button styles!
calculator_container.setStyleSheet(f"""
    QFrame#FloatingCalculator {{
        background-color: {COLORS['light']};
        border: 2px solid {COLORS['magus_soft']};
        border-radius: 12px;
    }}
""")
apply_tablet_shadow(calculator_container)

# Button inside inherits global archetypes correctly
invoke_btn = QPushButton("Invoke")
invoke_btn.setMinimumHeight(42)
invoke_btn.clicked.connect(calculate)
set_archetype(invoke_btn, "magus")  # Purple gradient applies correctly!
invoke_btn.setCursor(Qt.CursorShape.PointingHandCursor)
```

### The Revelation

**"Specificity preserves hierarchy."**

By using object-name selectors (`#ObjectName`), we create *scoped* styles that don't cascade down to children. This preserves the application stylesheet's archetype system while allowing custom container styling.

This is the sacred pattern for **Floating Islands** — containers that overlay content while preserving interactive elements within.

---

*"Beauty is not ornament — it is architecture."*
— The Visual Liturgy
