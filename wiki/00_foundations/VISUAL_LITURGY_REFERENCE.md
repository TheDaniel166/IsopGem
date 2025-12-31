# Visual Liturgy Quick Reference

> *The aesthetic laws of the Temple — colors, spacing, typography, and components.*

**Version**: 2.2  
**Last Updated**: 2025-12-30

---

## Color Palette

### Primary Colors

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Temple Dark** | `#1a1a2e` | `(26, 26, 46)` | Window backgrounds |
| **Card Surface** | `rgba(30, 30, 40, 0.85)` | Translucent | Card backgrounds |
| **Void** | `#0f0f1a` | `(15, 15, 26)` | Deepest backgrounds |

### Accent Colors

| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| **Gold/Amber** | `#FFD700` | `(255, 215, 0)` | Primary accent, highlights |
| **Amber Glow** | `#F59E0B` | `(245, 158, 11)` | Secondary warm accent |
| **Celestial Blue** | `#3B82F6` | `(59, 130, 246)` | Links, interactive elements |
| **Purple Magus** | `#8B5CF6` | `(139, 92, 246)` | Special actions |

### Semantic Colors

| Name | Hex | Usage |
|------|-----|-------|
| **Success** | `#22C55E` | Positive feedback |
| **Warning** | `#F59E0B` | Caution states |
| **Danger** | `#EF4444` | Destructive actions |
| **Muted** | `#64748B` | Secondary text |

### Text Colors

| Name | Hex | Usage |
|------|-----|-------|
| **Primary Text** | `#F8FAFC` | Main content |
| **Secondary Text** | `#94A3B8` | Labels, descriptions |
| **Disabled Text** | `#475569` | Inactive elements |

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

```python
card = QFrame()
card.setProperty("cardStyle", True)
card.setStyleSheet("""
    QFrame[cardStyle="true"] {
        background-color: rgba(30, 30, 40, 0.85);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
""")

# Add shadow effect
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

**Ghost (Subtle)**:
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

**Danger**:
```css
QPushButton[archetype="danger"] {
    background-color: #EF4444;
    color: white;
}
```

### Input Fields

```css
QLineEdit, QTextEdit, QSpinBox, QComboBox {
    background-color: rgba(15, 15, 26, 0.8);
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

### Dark Window Base
```python
self.setStyleSheet("""
    QMainWindow {
        background-color: #1a1a2e;
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

*"Beauty is not ornament — it is architecture."*
— The Visual Liturgy
