
# Spreadsheet Feature Roadmap & Complexity Analysis

This document outlines potential features for the `IsopGem` spreadsheet module, rated by implementation difficulty (1 = Easiest, 10 = Hardest) based on the current architecture (PyQt6 + Custom Model).

## 1. Core UX & Navigation
| Feature | Difficulty | Priority | Status | Description |
| :--- | :---: | :---: | :---: | :--- |
| **Delete/Clear Key** | 1 | **MVP** | Done | Delete/Backspace clears selection (undo-supported). |
| **Resize Rows/Cols** | 2 | **MVP** | Done | Qt interactive header resizing enabled. |
| **Search (Ctrl+F)** | 2 | High | Done | Find dialog to jump to matches. |
| **Format Painter** | 3 | Med | Todo | Copy styling (bg, border, font) from one cell to another. |
| **Drag-to-Fill** | 5 | High | Todo | Drag handle to auto-fill series or copy formulas. |
| **Multi-Level Undo** | 6 | **MVP** | Partial | Undo stack exists; needs batching for large pastes/fills. |
| **Multi-Sheet UI** | 3 | High | Done | Tab bar, Add/Rename sheets, Multi-Model architecture. |

## 2. Formatting & Visuals
| Feature | Difficulty | Priority | Status | Description |
| :--- | :---: | :---: | :---: | :--- |
| **Text Alignment** | 2 | High | Done | Left/Center/Right buttons wired to alignment role. |
| **Number Formatting** | 3 | High | Todo | Format menu (currency, percent, date) via DisplayRole. |
| **Range Borders** | 4 | Med | Done | Border engine applies outer edges; style/width/color supported. |
| **Cell Merging** | 5 | Low | Todo | `setSpan()` integration; impacts selection/nav. |
| **Conditional Formatting** | 6 | Med | Done | Rules engine applies bg/fg during paint; extend to font later. |
| **Rich Text (Bold/Italic)** | 7 | Low | Partial | Basic font styles supported; inline rich text limited. |

## 3. Formulas & Calculation
| Feature | Difficulty | Priority | Status | Description |
| :--- | :---: | :---: | :---: | :--- |
| **Range Support** | 4 | **MVP** | Done | Parser handles ranges; SUM/others consume lists. |
| **New Functions** | 2 | High | Done | Core math/text/logic set registered (SUM, AVERAGE, MIN/MAX, IF, LEN, etc.). |
| **Named Ranges** | 5 | Med | Todo | Map names to ranges and resolve in parser. |
| **Cross-Sheet Refs** | 6 | Low | Todo | `Sheet2!A1` logic (Architecture ready). |
| **Array Formulas** | 8 | Low | Todo | Matrix-returning formulas (SPILL). |
| **Dependency Graph** | 9 | High | Todo | Topological recalc for large sheets. |

## 4. Data Management
| Feature | Difficulty | Priority | Status | Description |
| :--- | :---: | :---: | :---: | :--- |
| **Import/Export CSV** | 3 | **MVP** | Done | CSV import/export implemented; hub import runs async. |
| **Sort Ranges** | 4 | Med | Done | Range sort with undo support. |
| **Data Validation** | 5 | Med | Todo | Dropdowns or rule checks on edit. |
| **Filter Views** | 6 | Low | Todo | Row hiding via filter proxy. |
| **Pivot Tables** | 9 | Low | Todo | Aggregation model/view. |

## 5. Esoteric & App-Specific
| Feature | Difficulty | Status | Description |
| :--- | :---: | :---: | :--- |
| **Gematria Heatmap** | 4 | Todo | Color scales based on Gematria value intensity or congruency. |
| **Planetary Data** | 6 | Todo | `PLANET("Venus", "Long")` fetching real-time data from Service. |
| **Kamea Generator** | 5 | Todo | Auto-populate grid with magic squares based on planetary number. |
| **Sigil Tracing** | 8 | Todo | Draw vector paths over the grid connecting specific numbers/letters. |
