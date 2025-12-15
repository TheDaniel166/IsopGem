
# Spreadsheet Feature Roadmap & Complexity Analysis

This document outlines potential features for the `IsopGem` spreadsheet module, rated by implementation difficulty (1 = Easiest, 10 = Hardest) based on the current architecture (PyQt6 + Custom Model).

## 1. Core UX & Navigation
| Feature | Difficulty | Priority | Description |
| :--- | :---: | :---: | :--- |
| **Delete/Clear Key** | 1 | **MVP** | Allow `Delete` or `Backspace` to clear selected cells. |
| **Resize Rows/Cols** | 2 | **MVP** | Enable manual resizing of row heights and column widths (Native Qt feature). |
| **Search (Ctrl+F)** | 2 | High | Simple dialog to find text/numbers in the grid and jump to cell. |
| **Format Painter** | 3 | Med | Copy styling (bg, border, font) from one cell to another. |
| **Drag-to-Fill** | 5 | High | Handle bottom-right drag handle to auto-fill series or copy formulas. |
| **Multi-Level Undo** | 6 | **MVP** | Complex tracking of batched operations (Fill, Paste, Format). |

## 2. Formatting & Visuals
| Feature | Difficulty | Priority | Description |
| :--- | :---: | :---: | :--- |
| **Text Alignment** | 2 | High | Buttons for Left/Center/Right alignment (Qt AlignmentFlag). |
| **Number Formatting** | 3 | High | `Format` menu (Currency, Percentage, Date, Precision). Logic in `DisplayRole`. |
| **Range Borders** | 4 | Med | Apply borders to outer edges of a multi-cell selection. |
| **Cell Merging** | 5 | Low | Support `setSpan()`. Complicates selection and navigation logic. |
| **Conditional Formatting** | 6 | Low | Rules engine (e.g., "Color Red if < 0") applied during `paint`. |
| **Rich Text (Bold/Italic)** | 7 | Low | Partial rich text support inside cells (already partially explored). |

## 3. Formulas & Calculation
| Feature | Difficulty | Priority | Description |
| :--- | :---: | :---: | :--- |
| **Range Support** | 4 | **MVP** | Parse `A1:B5` and pass list of values to functions (e.g. `SUM(A1:B5)`). |
| **New Functions** | 2 | High | Add standard functions (`AVG`, `MAX`, `IF`, `LEN`) to `FormulaRegistry`. |
| **Named Ranges** | 5 | Med | Map "Sales" to `A1:A10` and use in formulas. |
| **Cross-Sheet Refs** | 6 | Low | Syntax `Sheet2!A1`. Requires multi-model architecture. |
| **Array Formulas** | 8 | Low | Formulas that return matrices (SPILL behavior). |
| **Dependency Graph** | 9 | High | Topical sort of cells for efficient recalculation on large sheets. |

## 4. Data Management
| Feature | Difficulty | Priority | Description |
| :--- | :---: | :---: | :--- |
| **Import/Export CSV** | 3 | **MVP** | Load/Save standard CSV files. |
| **Sort Ranges** | 4 | Med | Sort selected rows based on a key column. |
| **Data Validation** | 5 | Med | Dropdown lists (ComboBox Delegate) or Input restrictions (`Evaluate` check). |
| **Filter Views** | 6 | Low | Hide rows based on criteria without deleting data (`QSortFilterProxyModel`). |
| **Pivot Tables** | 9 | Low | Dynamic aggregation views. Requires separate model/view logic. |

## 5. Esoteric & App-Specific
| Feature | Difficulty | Description |
| :--- | :---: | :--- |
| **Gematria Heatmap** | 4 | Color scales based on Gematria value intensity or congruency. |
| **Planetary Data** | 6 | Function `PLANET("Venus", "Long")` fetching real-time data from Service. |
| **Kamea Generator** | 5 | Auto-populate grid with magic squares based on planetary number. |
| **Sigil Tracing** | 8 | Draw vector paths over the grid connecting specific numbers/letters. |
