# Shared Base - Anatomy Chart

<!-- Last Verified: 2024-12-28 -->

This manifest details the common infrastructure that supports all Sovereign Pillars.

---

## Infrastructure

**File:** `src/shared/signals/navigation_bus.py`

**Role:** `[Nervous System] (Signal Bus)`

**Purpose:** The central communication hub for inter-pillar window requests. Allows Pillars to request UI resources without direct imports.

**Input (Ingests):**
* `window_key` (str): Unique identifier for the window (e.g., "gematria_calculator").
* `params` (dict): Optional parameters to pass to the window.

**Output (Emits):**
* `request_window` Signal.

---

**File:** `src/shared/ui/window_manager.py`

**Role:** `[Diplomat] (Manager)`

**Purpose:** Manages the lifecycle of all Sovereign Windows. Listens to the Navigation Bus and instantiates windows lazily.

**Input (Ingests):**
* `NavigationBus` signals.

**Key Interactions:**
* **Lazy Loading:** Imports window classes only when requested to reduce startup time.
* **Tracking:** Maintains references to open windows to prevent garbage collection.
* **Positioning:** Cashes and restores window geometry.

---

## Shared Services

**File:** `src/shared/services/gematria/base_calculator.py`

**Role:** `[Muscle] (Base Class)`

**Purpose:** Abstract Base Class for all Gematria Calculators. Ensures polymorphic behavior across Pillars.

**Input (Ingests):**
* `text` (str)

**Output (Emits):**
* `value` (int)

**Key Interactions:**
* Used by `Gematria`, `TQ`, and `Correspondences` pillars.

---

**File:** `src/shared/services/document_manager/document_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** core CRUD operations for Documents and Verses.

**Consumers:**
* `Gematria Pillar` (for Text Analysis)
* `Document Manager Pillar` (for managing the Library)

---

## Shared UI Components

**File:** `src/shared/ui/rich_text_editor/editor.py`

**Role:** `[Skin] (Component)`

**Purpose:** A reusable, high-fidelity Rich Text Editor with integrated Gematria features.

**Key Features:**
* Pattern highlighting.
* Export to HTML/Markdown.
* Integrated spell check and etymology (via context menu).

---

## Shared Geometry

**File:** `src/shared/services/geometry/solid_geometry.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Mathematical definitions for Platonic Solids (Vertices, Edges, Faces).

**Consumers:**
* `Geometry Pillar`
* `Adyton` (Throne generation)
