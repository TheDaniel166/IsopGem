# The Grimoire of Correspondences

<!-- Last Verified: 2026-01-01 -->

> *"As above, so below. To accomplish the miracles of the One Thing."*

The **Correspondences Pillar** is the domain of **The Emerald Tablets** (Spreadsheets). It allows the Magus to map relationships between concepts, numbers, and symbols using a dynamic, formula-driven grid.

---

## I. The Emerald Tablet (The Spreadsheet)

**Location**: `src/pillars/correspondences/ui/spreadsheet_window.py`

The Tablet is more than a grid; it is a canvas for magical calculus.
- **Persistence**: Content is stored as a JSON object, containing an array of **Scrolls** (Sheets).
- **Format**: JSON Structure: `{ "scrolls": [...], "active_scroll_index": 0 }`

### 1. Multi-Scroll Architecture
A single Tablet can hold multiple **Scrolls** (Sheets).
- **Navigation**: The `ScrollTabBar` allows switching between active sheets.
- **Isolation**: Each scroll has its own formula context, though future expansions may allow cross-scroll references.

### 2. The Formula Engine
**Location**: `src/pillars/correspondences/services/formula_engine.py`

The engine evaluates cells starting with `=`. It supports:
- **Arithmetic**: `+`, `-`, `*`, `/`, `^`, `%`.
- **Functions**: `SUM`, `AVG`, `COUNT`, `MIN`, `MAX`, `IF`.
- **Gematria**: `=GEM("text", "cipher")` integrates directly with the Gematria Pillar.
- **String Ops**: `UPPER`, `LOWER`, `CONCAT`, `TEXTJOIN`.

### 3. Verification & Logic
- **Reference Adjustment**: Drag-to-fill automatically adjusts cell references (e.g., `A1` -> `A2`) using the `FormulaHelper`.
- **Cycle Detection**: The engine prevents infinite recursion (e.g., A1 referencing B1 referencing A1).

---

## II. The Editor Interface

**Location**: `src/pillars/correspondences/ui/spreadsheet_view.py`

The View is the tangible surface of the Tablet.
- **Rich Text**: Cells support HTML formatting.
- **Borders**: A complex `BorderEngine` allows drawing borders on cell edges.
- **Drag-to-Fill**: A fill handle allows rapid pattern replication and formula extension.

---

## III. Integration

The Correspondences Pillar is the bridge between **Data** and **Meaning**.
- **Ingestion**: Can import CSV and Excel files via `IngestionService`.
- **Gematria Link**: The `GEM()` function pulls in values from the Gematria Pillar, allowing you to build dynamic calculators for names and phrases.

> *"The Sun is its father, the Moon its mother, the Wind hath carried it in its belly, the Earth is its nurse."*
