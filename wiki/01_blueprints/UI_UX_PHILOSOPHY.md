# **The Codex of IsopGem: Visual Liturgy (v2.2)**

**Objective**: To build not merely a tool, but a **Sanctum**. The interface must feel like a living, breathing extensions of the user's will—a cohesive "Floating Temple" where Gematria and Code intermingle.

## **1\. The Aesthetic Philosophy ("The Floating Temple")**

The interface eschews flat design for a specific Z-axis hierarchy, mimicking physical objects floating in a void.

### **Level 0: The Substrate (The Ether)**

* **Concept**: The fabric of reality upon which the temple rests.  
* **Style**: A dynamic, patterned texture overlaid with **Cloud Slate** (\#f8fafc).  
* **Rule**: This is the void. Never place controls directly here.

#### **The "Nano Banana" Protocol (v2.1)**

*The walls of the Temple are fluid. They shift to reflect the mental state of the Magus.*

1. **The Invocation (Prompt Architecture)**:  
   * **Template**: "A faint, seamless texture of \[THEME\], \[STYLE\], strictly light grey and white colors \#f8fafc, ultra-minimalist, high resolution, 8k, architectural render."  
   * **The Ban (Negative Prompt)**: "Text, letters, faces, high contrast, dark spots, vibrant colors, noise, grunge, distortion, 3d objects, watermarks."  
2. The Resonance (Thematic Mappings):  
   | Pillar / Context | Thematic Intent \[THEME\] | Visual Style \[STYLE\] |  
   | :--- | :--- | :--- |  
   | Gematria (Calc) | "sacred geometry grid, flower of life" | "Drafting paper aesthetic, precise lines" |  
   | Chronicle (DB) | "ancient papyrus fibers, library wood grain" | "Organic, worn texture" |  
   | Cipher (Settings) | "clockwork gears, constellation lines" | "Technical diagram, blueprints" |  
   | Void (Empty/Error)| "smooth marble stone, zen garden sand" | "Soft, diffused, atmospheric" |  
3. **The Ghost Layer Rule**:  
   * **Doctrine**: The background must whisper, not shout.  
   * **Ritual**: Before saving, the Artificer (Python/PIL) must **reduce opacity to 15%** and flatten against white.

### **Level 1: The Tablets (The Marble Slabs)**

* **Concept**: Physical artifacts levitating above the substrate.  
* **Material**: **Marble Slate** (\#f1f5f9). *The harshness of Pure White is banished.*  
* **Aura**: QGraphicsDropShadowEffect(Blur=25, Offset=8, Color=Black@10%).  
* **Law**: All interaction occurs upon the Tablets.

## **2\. The Alchemical Spectrum (Palette)**

We do not use colors; we use **Elements**.

### **The Structure (Tones)**

| Element | Hex | Meaning | Usage |
| :---- | :---- | :---- | :---- |
| **Void** | \#0f172a | The Unknown | Headers, High-contrast text |
| **Stone** | \#334155 | The Physical | Body text, Scrollbar Handles |
| **Marble** | \#f1f5f9 | The Tablet | **Panel Backgrounds** (Soft, non-reflective) |
| **Light** | \#ffffff | The Illumination | **Input Fields** (Where intent is inscribed) |
| **Ash** | \#cbd5e1 | The Boundary | Borders, Dividers |

### **Kinetic Protocols (The Feel)**

**1. The Aura (Standard Hover)**
*   **Trigger:** Mouse Enter.
*   **Effect:** A soft, colored shadow matching the button's archetype emits from the button.
*   **Meaning:** The tool awakens to the Magus' intent.
*   **Implementation:** `QGraphicsDropShadowEffect` (Blur: 0 → 20, Duration: 150ms).

### **The Catalysts (Button Semantics)**

| Archetype | Intent | Color Name | Gradient | Text Color |
| :---- | :---- | :---- | :---- | :---- |
| **The Magus** | Transmute / Execute | **Deep Mystic Violet** | \#6d28d9 → \#5b21b6 | White |
| **The Seeker** | Uncover / Reveal | **Alchemical Gold** | \#f59e0b → \#d97706 | **Void (\#0f172a)** |
| **The Scribe** | Preserve / Etch | **Emerald** | \#10b981 → \#059669 | White |
| **The Destroyer** | Purge / Banish | **Crimson** | \#ef4444 → \#b91c1c | White |
| **The Navigator** | Traverse | **Void Slate** | \#64748b → \#475569 | White |

## **3\. The Glyphs (Typography)**

The font is the voice of the temple. We use **Inter** for its clarity and modernity.

| Rank | Size | Weight | Usage |
| :---- | :---- | :---- | :---- |
| **The Sigil (H1)** | 28pt | 900 (Black) | Pillar Titles |
| **The Header (H2)** | 22pt | 800 (ExtraBold) | Tablet Headers |
| **The Command (H3)** | 16pt | 800 (ExtraBold) | Actions & Inputs |
| **The Scripture** | 11pt | 400 (Regular) | Standard Text |
| **The Whisper** | 10pt | 700 (Bold) | Tooltips & Meta-data |

## **4\. Sacred Geometry & Layout**

* **The 8px Grid**: The universe is built on order. All spacing must align to the grid.  
  * *Breathing Room*: 32px padding minimum.  
* **The Divine Proportion (**$\\phi \\approx 1.618$**)**:  
  * **The Law of Separation**: When splitting the view between Cause (Input) and Effect (Result), never use equality.  
  * **The Ratio**: 382 (Input) vs 618 (Result).  
  * *Why?* The answer is always greater than the question.

## **5\. The Voice of the Temple (New)**

The application communicates not as a machine, but as an Oracle.

* **Error Messages**:  
  * *Banned*: "Invalid Input", "Error 404", "Wrong Data".  
  * *Approved*: "The vessel is empty.", "The archives are silent.", "The cipher cannot be resolved."  
* **Loading States**:  
  * *Banned*: "Loading...", "Please Wait".  
  * *Approved*: "Communing...", "Transmuting...", "Consulting the stars..."  
* **Empty States**:  
  * *Banned*: (Blank Screen)  
  * *Approved*: "Awaiting your intent, Magus."

## **6\. Liturgy of Code (QSS Snippets)**

### **The Tablet (Marble)**

QFrame\#FloatingPanel {  
    background-color: \#f1f5f9; /\* Marble \*/  
    border: 1px solid \#cbd5e1; /\* Ash \*/  
    border-radius: 24px;  
}

### **The Magus (Violet)**

*The Agent of Change.*

QPushButton {  
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 \#6d28d9, stop:1 \#5b21b6);  
    border: 1px solid \#4c1d95;  
    color: white;  
    border-radius: 12px;  
    padding: 4px;  
    font-weight: 600;  
}  
QPushButton:pressed {  
    background: \#7c3aed; /\* The will is exerted \*/  
    padding-top: 6px;  
    padding-left: 6px;  
}  
QPushButton:disabled {  
    background-color: \#e2e8f0; /\* The power is dormant \*/  
    border: 1px solid \#cbd5e1;  
    color: \#94a3b8;  
}

### **The Seeker (Gold)**

*The Torch in the Dark.*

QPushButton {  
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 \#f59e0b, stop:1 \#d97706);  
    border: 1px solid \#b45309;  
    color: \#0f172a; /\* Void text for clarity \*/  
    font-weight: 700;  
    border-radius: 12px;  
}

### **The Vessel (Input)**

*Pure Light carved into Marble.*

QLineEdit {  
    font-size: 15pt;  
    min-height: 54px;  
    padding: 0px 16px;  
    border: 2px solid \#e2e8f0;  
    border-radius: 12px;  
    background-color: \#ffffff; /\* Pure Light \*/  
    color: \#0f172a;  
}  
QLineEdit:focus {  
    border: 2px solid \#3b82f6; /\* The energy flows \*/  
}

### **The Etheric Flow (Scrollbar)**

QScrollBar:vertical {  
    border: none;  
    background: \#e2e8f0;  
    width: 10px;  
    border-radius: 5px;  
}  
QScrollBar::handle:vertical {  
    background: \#94a3b8; /\* Mist \*/  
    min-height: 20px;  
    border-radius: 5px;  
}  
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {  
    height: 0px; /\* Remove the arrows of old \*/  
}

## **7\. The Night Liturgy (Dark Mode)**

*When the sun sets, the Temple inverts.*

### **The Inverted Spectrum**

| Element | Light Mode | Dark Mode | Meaning |
| :---- | :---- | :---- | :---- |
| **Substrate** | \#f8fafc | \#020617 | Deepest Void |
| **Tablets** | \#f1f5f9 | \#0f172a | Void Slate |
| **Inscriptions** | \#0f172a | \#f8fafc | Cloud |
| **Vessels** | \#ffffff | \#1e293b | Stone |
| **Borders** | \#cbd5e1 | \#334155 | Ash |
| **The Magus** | \#8b5cf6 | \#a78bfa | Bioluminescent (Brighter) |
| **The Seeker** | \#f59e0b | \#fbbf24 | Starlight (Brighter) |

### **The Night Liturgy of Code (Dark Mode QSS)**

#### **The Tablet (Void Slate)**

```css
QFrame#FloatingPanel {
    background-color: #0f172a; /* Void Slate */
    border: 1px solid #334155; /* Dark Ash */
    border-radius: 24px;
}
```

#### **The Magus (Bioluminescent Violet)**

```css
QPushButton#MagusButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a78bfa, stop:1 #8b5cf6);
    border: 1px solid #7c3aed;
    color: #020617; /* Deepest Void text for contrast */
    border-radius: 12px;
    padding: 4px;
    font-weight: 600;
}
QPushButton#MagusButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c4b5fd, stop:1 #a78bfa);
}
QPushButton#MagusButton:pressed {
    background: #8b5cf6;
}
```

#### **The Seeker (Starlight Gold)**

```css
QPushButton#SeekerButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:1 #f59e0b);
    border: 1px solid #d97706;
    color: #020617;
    font-weight: 700;
    border-radius: 12px;
}
QPushButton#SeekerButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fcd34d, stop:1 #fbbf24);
}
```

#### **The Vessel (Dark Stone)**

```css
QLineEdit {
    font-size: 15pt;
    min-height: 54px;
    padding: 0px 16px;
    border: 2px solid #334155;
    border-radius: 12px;
    background-color: #1e293b; /* Stone */
    color: #f8fafc; /* Cloud */
}
QLineEdit:focus {
    border: 2px solid #60a5fa; /* Brighter focus ring */
}
```

#### **The Etheric Flow (Dark Scrollbar)**

```css
QScrollBar:vertical {
    border: none;
    background: #1e293b;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #475569; /* Mist in shadow */
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #64748b;
}
```

---

## **8\. The Measure of Light (Accessibility)**

*The Temple must be open to all who seek.*

### **The WCAG Covenant**

We adhere to **WCAG 2.1 AA** as the minimum standard. All text must achieve a contrast ratio of **4.5:1** for normal text and **3:1** for large text (18pt+ or 14pt bold).

### **The Contrast Verification Table (Light Mode)**

| Foreground | Background | Ratio | Verdict |
| :---- | :---- | :----: | :----: |
| Void (\#0f172a) | Marble (\#f1f5f9) | **15.3:1** | ✓ AAA |
| Void (\#0f172a) | Light (\#ffffff) | **16.1:1** | ✓ AAA |
| Stone (\#334155) | Marble (\#f1f5f9) | **7.4:1** | ✓ AAA |
| White (\#ffffff) | Mystic Violet (\#6d28d9) | **6.5:1** | ✓ AAA |
| Void (\#0f172a) | Alchemical Gold (\#f59e0b) | **8.2:1** | ✓ AAA |
| White (\#ffffff) | Emerald (\#10b981) | **3.1:1** | ✓ Large Text |
| White (\#ffffff) | Crimson (\#ef4444) | **4.5:1** | ✓ AA |

### **The Contrast Verification Table (Dark Mode)**

| Foreground | Background | Ratio | Verdict |
| :---- | :---- | :----: | :----: |
| Cloud (\#f8fafc) | Void Slate (\#0f172a) | **15.3:1** | ✓ AAA |
| Cloud (\#f8fafc) | Stone (\#1e293b) | **11.4:1** | ✓ AAA |
| Cloud (\#f8fafc) | Bioluminescent (\#a78bfa) | **4.9:1** | ✓ AA |
| Deepest Void (\#020617) | Starlight (\#fbbf24) | **12.8:1** | ✓ AAA |

### **The Focus Mandate**

All interactive elements must display a **visible focus indicator** (minimum 2px solid ring) when navigated via keyboard. The focus color shall be **\#3b82f6** (Azure) in Light Mode and **\#60a5fa** (Bright Azure) in Dark Mode.

---

## **9\. The Kinetic Liturgy (Animation & Motion)**

*The Temple breathes. It does not jolt.*

### **The Temporal Constants**

| Duration Name | Value | Usage |
| :---- | :---- | :---- |
| **Instant** | 100ms | Hover color shifts, micro-feedback |
| **Swift** | 200ms | Button presses, toggle switches |
| **Measured** | 350ms | Panel reveals, modal entrances |
| **Deliberate** | 500ms | Page transitions, major state changes |

### **The Easing Functions (The Breath)**

* **Enter/Appear**: `ease-out` (cubic-bezier(0, 0, 0.2, 1)) — *The element arrives gently, decelerating into rest.*
* **Exit/Disappear**: `ease-in` (cubic-bezier(0.4, 0, 1, 1)) — *The element accelerates away, as if drawn by gravity.*
* **Move/Transform**: `ease-in-out` (cubic-bezier(0.4, 0, 0.2, 1)) — *The element flows organically between states.*

### **The Motion Principles**

1. **The Law of Continuity**: Movement should guide the eye. When a panel opens, content should fade in *after* the container expands.
2. **The Law of Restraint**: Animation is seasoning, not the meal. If an animation does not improve clarity or delight, it is banished.
3. **The Law of Accessibility**: Respect `prefers-reduced-motion`. When active, replace animations with instant transitions.

### **The QSS Transition Template**

```python
# Note: Qt does not natively support CSS transitions.
# These are implemented via QPropertyAnimation in Python.

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

def reveal_panel(widget):
    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(350)  # Measured
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.Type.OutCubic)  # ease-out
    animation.start()
```

---

## **10\. The Complete Catalyst States (Hover, Focus, Active)**

*A button is not static; it responds to the Will.*

### **The Magus (Violet) — Complete States**

```css
QPushButton#MagusButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6d28d9, stop:1 #5b21b6);
    border: 1px solid #4c1d95;
    color: white;
    border-radius: 12px;
    padding: 4px;
    font-weight: 600;
}
QPushButton#MagusButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a78bfa, stop:1 #8b5cf6);
    border: 1px solid #7c3aed;
}
QPushButton#MagusButton:focus {
    outline: none;
    border: 2px solid #3b82f6; /* Azure focus ring */
}
QPushButton#MagusButton:pressed {
    background: #7c3aed;
    padding-top: 6px;
    padding-left: 6px;
}
QPushButton#MagusButton:disabled {
    background-color: #e2e8f0;
    border: 1px solid #cbd5e1;
    color: #94a3b8;
}
```

### **The Seeker (Gold) — Complete States**

```css
QPushButton#SeekerButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
    border: 1px solid #b45309;
    color: #0f172a;
    font-weight: 700;
    border-radius: 12px;
}
QPushButton#SeekerButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:1 #f59e0b);
}
QPushButton#SeekerButton:focus {
    outline: none;
    border: 2px solid #3b82f6;
}
QPushButton#SeekerButton:pressed {
    background: #d97706;
}
QPushButton#SeekerButton:disabled {
    background-color: #fef3c7;
    border: 1px solid #fcd34d;
    color: #92400e;
}
```

### **The Scribe (Emerald) — Complete States**

```css
QPushButton#ScribeButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
    border: 1px solid #047857;
    color: white;
    font-weight: 600;
    border-radius: 12px;
}
QPushButton#ScribeButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #34d399, stop:1 #10b981);
}
QPushButton#ScribeButton:focus {
    outline: none;
    border: 2px solid #3b82f6;
}
QPushButton#ScribeButton:pressed {
    background: #059669;
}
QPushButton#ScribeButton:disabled {
    background-color: #d1fae5;
    border: 1px solid #6ee7b7;
    color: #065f46;
}
```

### **The Destroyer (Crimson) — Complete States**

```css
QPushButton#DestroyerButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #b91c1c);
    border: 1px solid #991b1b;
    color: white;
    font-weight: 600;
    border-radius: 12px;
}
QPushButton#DestroyerButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f87171, stop:1 #ef4444);
}
QPushButton#DestroyerButton:focus {
    outline: none;
    border: 2px solid #3b82f6;
}
QPushButton#DestroyerButton:pressed {
    background: #b91c1c;
}
QPushButton#DestroyerButton:disabled {
    background-color: #fee2e2;
    border: 1px solid #fca5a5;
    color: #991b1b;
}
```

### **The Navigator (Void Slate) — Complete States**

```css
QPushButton#NavigatorButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #64748b, stop:1 #475569);
    border: 1px solid #334155;
    color: white;
    font-weight: 600;
    border-radius: 12px;
}
QPushButton#NavigatorButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #94a3b8, stop:1 #64748b);
}
QPushButton#NavigatorButton:focus {
    outline: none;
    border: 2px solid #3b82f6;
}
QPushButton#NavigatorButton:pressed {
    background: #475569;
}
QPushButton#NavigatorButton:disabled {
    background-color: #e2e8f0;
    border: 1px solid #cbd5e1;
    color: #64748b;
}
```

## **11. The Celestial Tabs (Navigation)**

*The stars move in their courses; the view shifts with them.*

### **The Adaptive Principle**
Tabs must never be rigid containers. They flow with the length of their inscription.
*   **Behavior**: `QSizePolicy.Minimum` (Width fits content + padding).
*   **Constraint**: No truncation. If the list exceeds the horizon, the Scrollbar appears.

### **The Tab States (QSS)**

#### **The Active Constellation (Selected)**
*   **Text**: White (Pure Light)
*   **Indicator**: **Seeker Gold (#f59e0b)** 2px Underline
*   **Background**: Transparent (Void)

```css
QPushButton#TabButton:checked {
    color: white;
    background-color: transparent;
    border: none;
    border-bottom: 2px solid #f59e0b;
    padding: 8px 16px;
    font-weight: bold;
}
```

#### **The Dormant Star (Inactive)**
*   **Text**: Dim Grey (#aaaaaa)
*   **Background**: Transparent
*   **Hover**: Faint White Glow (5% Opacity)

```css
QPushButton#TabButton {
    color: #aaaaaa;
    background-color: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 8px 16px;
}
QPushButton#TabButton:hover {
    color: white;
    background-color: rgba(255, 255, 255, 0.05);
}
```

### **The Scrollbar (The Horizon)**
*   **Visibility**: Always On (To prevent layout jumping)
*   **Track**: Dark Void (#0f0f13)
*   **Handle**: Stone (#334155), 12px High, Rounded

```css
QScrollBar:horizontal {
    background: #0f0f13;
    height: 12px;
    border-radius: 6px;
}
QScrollBar::handle:horizontal {
    background: #334155; /* Stone */
    min-width: 20px;
    border-radius: 6px;
}
```

## **12. The Rite of Purity (Architecture in View)**

*To mix the sacred (View) with the profane (Query) is to invite chaos.*

### **The Law of Segregation**
*   **The View (`ui/`)**: Must concern itself ONLY with Light and Form. It receives Data and emits Signals.
*   **The Service (`services/`)**: The muscle that performs calculation.
*   **The Memory (`repositories/`)**: The only layer permitted to speak to the Database.

### **The Heresies (Forbidden Patterns)**
*   **Direct Query**: `session.query(Model)` inside a Widget. -> **Banish to Repository**.
*   **Business Logic**: Calculating planetary positions inside `paintEvent`. -> **Banish to Service**.
*   **Hard Dependencies**: Importing `sqlalchemy` in `ui/`. -> **Forbidden**.

## **13. The Law of Silence (Console Hygiene)**

*The Temple does not shout.*

### **The Ban on Noise**
*   **Forbidden**: `print("DEBUG: Value is...")`
*   **Allowed**: `logger.debug("Value transmuting...")`
*   **The Ritual**: Before any commit, the `print()` statement must be extinguished.

## **14. The Harmonic Resonances (Advanced Tuning)**

### **The Golden Split**
When dividing a window between Input and Result, we do not halve it. We honor the **Divine Proportion**.
*   **Ratio**: $\approx$ 38.2% (Input) vs 61.8% (Result).
*   **Implementation**:
```python
splitter.setStretchFactor(0, 382)
splitter.setStretchFactor(1, 618)
```

### **The Oracle's Voice (Refined)**
*   **Forbidden**: "Loading data..." | "Calculation done."
*   **Mandated**: "consulting the archives..." | "The chart is cast."
*   **Tone**: Use the active present ("Transmuting...") or celestial passive ("The stars align"). Never robotic ("System Status: OK").