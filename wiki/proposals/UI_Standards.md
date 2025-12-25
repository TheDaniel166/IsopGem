# The IsopGem Visual Standard (Draft)

**Objective**: To unify the aesthetic and functional experience across all Pillars, ensuring the application feels like a cohesive "Temple" rather than a collection of tools.

## 1. The Aesthetic Philosophy ("The Floating Temple")

The interface defines a specific Z-axis hierarchy to create depth.

*   **Level 0 (The Background)**:
    *   **Concept**: The substrate reality.
    *   **Style**: Patterned Texture overlaid with a light color (`#f8fafc`).
    *   **Rule**: Never place controls directly on Level 0.
    *   **The "Nano Banana" Protocol**:
        *   The Background Image MUST be **thematically generated** using the AI Artificer (`generate_image`).
        *   **Requirement**: It must be a seamless, subtle texture relevant to the Pillar (e.g., "sacred geometry pattern", "subtle starfield", "ancient papyrus texture").
        *   **Standard Prompts**: "Seamless pattern, subtle [Theme], light grey and white, minimalist, high resolution".
        *   **Implementation**: Use `border-image` to stretch the texture across the full window (simulating a unified surface like a scroll or table) rather than `background-image` (tiling), which can create visible seams with complex organic textures.
            ```css
            QWidget#CentralContainer {
                border-image: url("path/to/texture.png") 0 0 0 0 stretch stretch;
                border: none;
            }
            ```

*   **Level 1 (The Panels)**:
    *   **Concept**: Floating cards containing specific functional domains (e.g., "Control Panel", "Results Panel").
    *   **Style**:
        *   Background: Pure White (`#ffffff`) or Translucent White (`rgba(255,255,255, 0.7)`).
        *   Border: Subtle Slate (`#cbd5e1`).
        *   Radius: **24px** (Heavy rounding).
        *   Shadow: **Essential**. `QGraphicsDropShadowEffect(Blur=20, Offset=4, Color=Black@15%)`.
    *   **Rule**: All interaction happens here.

## 2. Color Palette (The Alchemical Spectrum)

### Primary Tones (Slate)
| Role | Hex | Use Case |
| :--- | :--- | :--- |
| **Void** | `#0f172a` | Headers, High-contrast text |
| **Stone** | `#334155` | Body text, unselected icons |
| **Mist** | `#64748b` | Subtitles, metadata |
| **Ash** | `#cbd5e1` | Borders, dividers |
| **Cloud** | `#f8fafc` | App Backgrounds (Level 0) |

### Functional Semantics (The Button Logic)

| Action Role | Color Name | Base Hex | Gradient Start | Gradient Stop | Usage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Magus (Process)** | **Mystic Violet** | `#7c3aed` | `#8b5cf6` | `#7c3aed` | Central Calculations, "Reap Harvest", "Run Analysis" |
| **Seeker (Inquiry)** | **Alchemical Gold** | `#d97706` | `#f59e0b` | `#d97706` | Search, Find, Open File, Filter |
| **Scribe (Preservation)** | **Emerald** | `#059669` | `#10b981` | `#059669` | Save, Commit, "Preserve in Chronicle" |
| **Destroyer (Purging)** | **Crimson** | `#ef4444` | `#ef4444` | `#b91c1c` | Clear, various Deletions |
| **Navigator (Transition)** | **Void Slate** | `#475569` | `#64748b` | `#475569` | Open new windows, Switch tabs |

### The "Alchemical Gradient"
All primary buttons use a generic gradient structure:
`qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 [Light], stop:1 [Dark])`

## 3. Typographic Scale

We use **Inter** or system sans-serif.

| Level | Size | Weight | Tracking | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **H1 (Logo)** | `28pt` | 900 (Black) | `-1px` | Pillar Titles |
| **H2 (Section)** | `22pt` | 800 (ExtraBold) | `-0.5px` | Window Headers |
| **H3 (Label)** | `15pt` | 800 (ExtraBold) | `0` | Major Actions, Input Values |
| **Body** | `11pt` | 400 (Regular) | `0` | Standard Content |
| **Micro** | `8pt` | 700 (Bold) | `0.1em` | Labels, tooltips, all-caps headers |

## 4. The 8px Grid System

All spacing must be multiples of **8px**.

*   **Panel Padding**: `32px` or `40px` (Generous breath).
*   **Gap (Layouts)**: `16px` or `24px`.
*   **Control Height**:
    *   **Large (Primary Inputs)**: `56px` (7 * 8).
    *   **Medium (Buttons)**: `48px` (6 * 8).
    *   **Small (Chips/Tags)**: `32px` (4 * 8).

## 5. Standard QSS Snippets

### The Floating Panel
```css
QFrame#FloatingPanel {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 24px;
}
```

### The Magus Button (Process - Violet)
```css
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #7c3aed);
    border: 1px solid #6d28d9;
    /* ... common props ... */
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #8b5cf6);
}
```

### The Seeker Button (Inquiry - Gold)
```css
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
    border: 1px solid #b45309;
    color: white; /* or #fffbeb for warmth */
}
```

### The Input Field (The Vessel)
```css
QLineEdit {
    font-size: 15pt;
    min-height: 54px;
    padding: 0px 16px;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    background-color: #ffffff;
    color: #0f172a;
    selection-background-color: #bfdbfe;
}
QLineEdit:focus {
    border: 2px solid #3b82f6;
}
```

## 6. Layout & Structure

### The Rule of Splitters vs. Tabs
**"Depth over Breadth."**

*   **When to use Splitters (Preferred)**:
    *   When the user needs to see the **Cause** (Input) and **Effect** (Result) simultaneously.
    *   Example: `GematriaCalculatorWindow` (Input Left | Results Right).
    *   Example: `SavedCalculationsWindow` (List Left | Details Right).

*   **When to use Stacked Widgets**:
    *   When an object changes **Mode** (Viewing vs. Editing).
    *   Example: Viewing a Note -> Clicking "Edit" -> View replaced by Editor (The Forge).

*   **When to use Tabs (The Warning)**:
    *   **Rule**: Avoid Tabs *within* a window unless the contexts are strictly parallel and independent.
    *   *Bad Usage*: Tab 1: "Input", Tab 2: "Results". (User loses context).
    *   *Good Usage*: Tab 1: "Analysis", Tab 2: "Settings".

### Space & Density

*   **Margins**: Generous. `20px` to `40px` inside panels.
*   **Spacing**: Elements should breathe. `10px` minimum between controls.
*   **Inputs**: Large, touch-friendly touch targets. `Min-Height: 50px` for primary inputs and buttons.

## 4. Visibility Rules

*   **The "Empty State"**: Never show a blank white void.
    *   Use a `status_label` or placeholder text centered in the panel explaining *why* it is empty (e.g., "The archive is silent. Consult the records...").
*   **Progressive Disclosure**:
    *   Hide complex tools (like the Virtual Keyboard or Detailed Breakdown) until requested.
    *   Toggle buttons should be iconic and unobtrusive.
