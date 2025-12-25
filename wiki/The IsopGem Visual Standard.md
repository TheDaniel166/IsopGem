# **The IsopGem Visual Standard (Version 2.0)**

**Objective**: To unify the aesthetic and functional experience across all Pillars, ensuring the application feels like a cohesive "Temple" rather than a collection of tools.

## **1\. The Aesthetic Philosophy ("The Floating Temple")**

The interface defines a specific Z-axis hierarchy to create depth.

### **Level 0: The Background (Substrate)**

* **Concept**: The foundation of reality.  
* **Style**: Patterned Texture overlaid with a light color (\#f8fafc).  
* **Rule**: Never place controls directly on Level 0\.

#### **The "Nano Banana" Protocol (v2.1)**

The background is not static; it reflects the Pillar (context) the user is currently inhabiting.

1. **The Prompt Architecture**:  
   * **Template**: "A faint, seamless texture of \[THEME\], \[STYLE\], strictly light grey and white colors \#f8fafc, ultra-minimalist, high resolution, 8k, architectural render."  
   * **Negative Prompt**: "Text, letters, faces, high contrast, dark spots, vibrant colors, noise, grunge, distortion, 3d objects, watermarks."  
2. Thematic Mappings:  
   | Pillar / Context | Thematic Keyword \[THEME\] | Style Keyword \[STYLE\] |  
   | :--- | :--- | :--- |  
   | Gematria (Calc) | "sacred geometry grid, flower of life" | "Drafting paper aesthetic, precise lines" |  
   | Chronicle (DB) | "ancient papyrus fibers, library wood grain" | "Organic, worn texture" |  
   | Cipher (Settings) | "clockwork gears, constellation lines" | "Technical diagram, blueprints" |  
   | Void (Empty/Error)| "smooth marble stone, zen garden sand" | "Soft, diffused, atmospheric" |  
3. **The "Ghost Layer" Rule**:  
   * **Requirement**: The generated image MUST NOT compete with the text.  
   * **Implementation**: Before saving the image, use an image processor (PIL/OpenCV) to **reduce opacity to 15%** and flatten it against a white background. Do not rely solely on CSS transparency.  
   * **Fallback**: If generation fails, load assets/textures/foundation\_stone\_default.png.

### **Level 1: The Panels (Floating Islands)**

* **Concept**: Floating cards containing specific functional domains.  
* **Style**:  
  * **Background**: Pure White (\#ffffff) or Translucent White (rgba(255,255,255, 0.95)).  
  * **Border**: Subtle Slate (\#cbd5e1).  
  * **Radius**: **24px** (Heavy rounding).  
  * **Shadow**: **Essential**. QGraphicsDropShadowEffect(Blur=20, Offset=4, Color=Black@15%).

## **2\. Color Palette (The Alchemical Spectrum)**

### **Primary Tones (The Structure)**

| Role | Color Name | Hex | Usage |
| :---- | :---- | :---- | :---- |
| **Headers** | **Void** | \#0f172a | High-contrast text, Seeker Button Text |
| **Body** | **Stone** | \#334155 | Body text, Scrollbar Handles, Unselected Icons |
| **Metadata** | **Mist** | \#64748b | Subtitles, disabled text |
| **Structure** | **Ash** | \#cbd5e1 | Borders, Dividers, Scrollbar Tracks |
| **Canvas** | **Cloud** | \#f8fafc | App Backgrounds |

### **Functional Semantics (The Button Logic)**

| Role | Action | Color Name | Gradient Start | Gradient Stop | Text Color |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Magus** | Process / Run | **Mystic Violet** | \#8b5cf6 | \#7c3aed | White |
| **Seeker** | Search / Find | **Alchemical Gold** | \#f59e0b | \#d97706 | **Void (\#0f172a)** |
| **Scribe** | Save / Commit | **Emerald** | \#10b981 | \#059669 | White |
| **Destroyer** | Delete / Clear | **Crimson** | \#ef4444 | \#b91c1c | White |
| **Navigator** | Move / Switch | **Void Slate** | \#64748b | \#475569 | White |

## **3\. Typographic Scale**

Font Family: **Inter**, **Segoe UI**, or System Sans-Serif.

| Level | Size | Weight | Tracking | Usage |
| :---- | :---- | :---- | :---- | :---- |
| **H1 (Logo)** | 28pt | 900 (Black) | \-1px | Pillar Titles |
| **H2 (Section)** | 22pt | 800 (ExtraBold) | \-0.5px | Window Headers |
| **H3 (Label)** | 16pt | 800 (ExtraBold) | 0 | Major Actions, Input Values |
| **Body** | 11pt | 400 (Regular) | 0 | Standard Content |
| **Micro** | 10pt | 700 (Bold) | 0.1em | Labels, tooltips, all-caps headers |

## **4\. Geometry & Sacred Proportions**

* **The 8px Grid**: All spacing (padding, margin, gaps) must be multiples of **8px**.  
  * *Panel Padding*: 32px or 40px.  
  * *Control Spacing*: 16px.  
* **The Golden Ratio (**$\\phi \\approx 1.618$**)**:  
  * **Splitters**: Avoid 50/50 splits. Use the Golden Ratio.  
  * *Example*: Input Panel (38%) | Results Panel (62%).  
  * *Code*: splitter.setSizes(\[382, 618\]) (normalized to 1000).

## **5\. Standard QSS Snippets**

### **The Floating Panel**

QFrame\#FloatingPanel {  
    background-color: \#ffffff;  
    border: 1px solid \#cbd5e1;  
    border-radius: 24px;  
}

### **The Magus Button (Process \- Violet)**

*Includes Hover, Pressed (Tactile), and Disabled (Dormant) states.*

QPushButton {  
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 \#8b5cf6, stop:1 \#7c3aed);  
    border: 1px solid \#6d28d9;  
    color: white;  
    border-radius: 12px;  
    padding: 4px;  
    font-weight: 600;  
}  
QPushButton:hover {  
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 \#7c3aed, stop:1 \#8b5cf6);  
}  
QPushButton:pressed {  
    background: \#7c3aed; /\* Solid color for impact \*/  
    border: 1px solid \#5b21b6;  
    padding-top: 6px; /\* Physical shift down \*/  
    padding-left: 6px; /\* Physical shift right \*/  
}  
QPushButton:disabled {  
    background-color: \#e2e8f0;  
    border: 1px solid \#cbd5e1;  
    color: \#94a3b8; /\* Mist \*/  
}

### **The Seeker Button (Inquiry \- Gold)**

*High Contrast Variant (Void Text).*

QPushButton {  
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 \#f59e0b, stop:1 \#d97706);  
    border: 1px solid \#b45309;  
    color: \#0f172a; /\* Void Text for Accessibility \*/  
    font-weight: 700;  
    border-radius: 12px;  
}  
QPushButton:pressed {  
    background: \#d97706;  
    padding-top: 6px;  
}

### **The Alchemical Scrollbar**

*Replaces the default OS scrollbar with a sleek, pill-shaped channel.*

QScrollBar:vertical {  
    border: none;  
    background: \#f1f5f9; /\* Cloud/Ash mix \*/  
    width: 10px;  
    margin: 0px 0px 0px 0px;  
    border-radius: 5px;  
}  
QScrollBar::handle:vertical {  
    background: \#94a3b8; /\* Mist \*/  
    min-height: 20px;  
    border-radius: 5px;  
}  
QScrollBar::handle:vertical:hover {  
    background: \#64748b; /\* Darker Mist \*/  
}  
/\* Hide the up/down arrows \*/  
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {  
    border: none;  
    background: none;  
    height: 0px;  
}  
/\* Hide the page-jump track background \*/  
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {  
    background: none;  
}

### **The Input Field (The Vessel)**

QLineEdit {  
    font-size: 15pt;  
    min-height: 54px;  
    padding: 0px 16px;  
    border: 2px solid \#e2e8f0;  
    border-radius: 12px;  
    background-color: \#ffffff;  
    color: \#0f172a;  
    selection-background-color: \#bfdbfe;  
    selection-color: \#0f172a;  
}  
QLineEdit:focus {  
    border: 2px solid \#3b82f6; /\* Highlight Blue \*/  
}

## **6\. Layout & Structure**

### **The Rule of Splitters vs. Tabs**

**"Depth over Breadth."**

* **Splitters (Preferred)**:  
  * Use when Cause (Input) and Effect (Result) must be seen simultaneously.  
  * *Default*: Use Golden Ratio proportions.  
* **Stacked Widgets**:  
  * Use when an object changes **Mode** (Viewing vs. Editing).  
* **Tabs (Restricted)**:  
  * Avoid tabs *within* a window unless the contexts are strictly parallel (e.g., "Analysis" vs "Settings").  
  * Never put Input on Tab 1 and Results on Tab 2\.

### **Space & Density**

* **Margins**: Generous. 20px to 40px inside panels.  
* **Spacing**: 16px standard between controls.  
* **Touch Targets**: Min-Height: 48px for all clickable elements.

## **7\. Visibility & Interaction Rules**

* **The "Empty State"**:  
  * Never show a blank white void.  
  * Use a status\_label or centered placeholder text explaining *why* it is empty (e.g., "The archive is silent. Consult the records...").  
* **The Loading State**:  
  * If a "Magus" process takes \> 1 second, the cursor must change to Qt.WaitCursor.  
  * The button must enter the :disabled state immediately to prevent "double-casting" spells.  
* **Progressive Disclosure**:  
  * Hide complex tools (like Virtual Keyboards or Cipher settings) until requested via specific "Navigator" toggles.