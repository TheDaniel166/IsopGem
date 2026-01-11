# The Architecture of the Temple

<!-- Last Verified: 2026-01-09 -->

> *"The structure must hold the weight of the vision."*

This scroll is the **definitive technical specification** for IsopGem. It details how the application is constructed not just as software, but as a system of **Sovereignty, Communication, and Shared Truth**.

---

## 1. Executive Summary

IsopGem is a **Local-First, Modular Monolith** designed for high-performance esoteric analysis.

*   **Platform**: Desktop (Linux/Windows/macOS) via Python 3.11 + PyQt6.
*   **Paradigm**: Event-Driven Architecture (Signal Bus) with Strict Module Isolation.
*   **Data**: SQLite (SQLAlchemy) for structured data, Whoosh for full-text indexing.
*   **Rendering**: 2D (QPainter), 3D (OpenGL/PyOpenGL), and Rich Text (HTML/CSS).
*   **Constraint**: No cloud dependencies. The application must function in a "Frozen" state (offline/air-gapped).

---

## 2. The Temple Metaphor (Core Patterns)

The architecture is enforced by **Five Principles**:

### I. The Law of Sovereignty
The system is divided into **Pillars** (Modules). Each Pillar strictly owns its own Data, Logic, and UI.
*   **Rule**: A Pillar may never import another Pillar's code directly.
*   **Why**: Prevents the "Ball of Mud" anti-pattern. Allows pillars to be added/removed without breaking the core.

### II. The Law of Orbit
The application follows a **Helio-Centric** window model.
*   **The Sun**: The Main Window (`IsopGemMainWindow`) is the gravitational center.
*   **The Satellites**: Tool windows are transient satellites. They are managed by the `WindowManager` and reference the Main Window as their orbital parent (for taskbar grouping) but are technically top-level windows.

### III. The Law of Signal
Communication is asynchronous and decoupled.
*   **Mechanism**: The `NavigationBus` (Signal/Slot).
*   **Rule**: Beings (Components) do not speak to each other directly; they release Signals into the ether, and those who listen react.
*   **Payload**: Communications use **DTOs** (Data Transfer Objects) or primitives, never internal model objects that would couple domains.

### IV. The Substrate
Beneath the Pillars lies the **Shared Substrate** (`src/shared`).
*   **Role**: Singleton infrastructure (Database, Config, Theme, Logging).
*   **Rule**: Pillars depend on the Substrate. The Substrate *never* depends on Pillars.

### V. The Liturgy
The Interface is not accidental; it is Liturgical.
*   **Mechanism**: `rite_of_nine.py` (Linter) and `KineticEnforcer.py` (Runtime).
*   **Rule**: UI components must use the centralized `theme.py` tokens. Hardcoded styles are interpreted as "Contamination."

---

## 3. The Pillar System (Module Architecture)

Located in `src/pillars/<name>/`, a Pillar is a self-contained domain.

### 3.1 The Standard Layout
```text
src/pillars/<name>/
├── ui/              # THE FACE (View)
│   ├── components/  # Reusable widgets
│   └── windows/     # Top-level windows
├── services/        # THE WILL (Logic)
│   └── calculations.py
├── models/          # THE SHAPE (Data definitions)
├── repositories/    # THE MEMORY (DB Access)
└── utils/           # THE TOOLS (Helpers)
```

### 3.2 The Separation of Realms
*   **The Service Layer**: Pure Python. "Blind" (Imports no UI). Safe to run in worker threads.
*   **The UI Layer**: Pure PyQt6. "Hollow" (Contains no business logic). Responsible only for rendering and user input.

---

## 4. The Nervous System (Signals & Events)

The **Navigation Bus** (`src/shared/signals/navigation_bus.py`) is the critical infrastructure for Module Sovereignty.

### 4.1 Topology: Hub-and-Spoke via Registry
Instead of importing Window classes directly (which would violate Sovereignty), the system uses a **Lazy-Loading Registry**.

1.  **Request**: Pillar A emits `request_window("gematria_calculator", params)`.
2.  **Routing**: `WindowManager` hears the signal.
3.  **Lookup**: It checks `WINDOW_REGISTRY` for the string key.
4.  **Import**: It performs a lazy (runtime) import of the target module: `pillars.gematria.ui...`.
5.  **Instantiate**: The window is created and tracked.

### 4.2 Signal Contract
*   **Request**: `request_window(key: str, params: dict)`
*   **Response**: `window_response(req_id: str, key: str, data: Any)`
*   **Broadcast**: `lexicon_updated(id: int, word: str)`

This ensures that `Pillar A` needs to know *nothing* about `Pillar B`'s implementation, only its "Call Sign" (Key).

---

## 5. The Shared Substrate (Infrastructure)

### 5.1 Configuration Sovereignty
**File**: `src/shared/config.py`
The Single Source of Truth for the file system.
*   **Paths**: All directory paths are calculated here. No `pathlib` math in UI code.
*   **Env**: All environment variable reading happens here.
*   **Frozen State**: Detects if running as `.py` or compiled binary (`sys.frozen`) and adjusts paths accordingly.

### 5.2 The Deep Memory (Database)
**File**: `src/shared/database.py`
*   **Engine**: SQLAlchemy (SQLite).
*   **Lifecycle**: `init_db()` is called at startup (`main.py`) to ensure schema exists.
*   **Threading**: Connection pooling is managed by SQLAlchemy. Services must handle sessions carefully (create/commit/close) to avoid locking.

### 5.3 The Visual Liturgy (Theme Engine)
**File**: `src/shared/ui/theme.py`
The central registry of `COLORS`, `FONTS`, and `DIMENSIONS`.
*   **Kinetic Enforcer**: A global event filter (`src/shared/ui/kinetic_enforcer.py`) that watches *all* buttons in the application. It automatically applies the "Glow" animation on hover, meaning individual buttons don't need custom logic.

---

## 6. The Visual Philosophy

### 6.1 The Hollow View
A UI component should be "Hollow."
*   **Bad**: A widget that calculates a Gematria sum when a button is clicked.
*   **Good**: A widget that emits `text_changed(str)`. The controller/service calculates the sum and calls `widget.set_sum(int)`.

### 6.2 The Exemption: Instrument Windows
A special class of window is the **Ritual Instrument** (e.g., Zodiacal Circle).
*   **Definition**: Windows where geometry and color are *semantic data*, not UI chrome.
*   **Status**: **Exempt** from Visual Liturgy token enforcement.
*   **Sign**: Marked with `@RiteExempt: Visual Liturgy` in the source file.

---

## 7. The Laws of the Code (Anti-Patterns)

**Strictly Forbidden:**

1.  **The Sin of Crossing**: Importing `pillars.astrology` inside `pillars.gematria`.
    *   *Correction*: Use `NavigationBus`.
2.  **The Sin of Logic in View**: Writing SQL queries or math inside a `QWidget`.
    *   *Correction*: Move to `services/` or `repositories/`.
3.  **The Sin of the Frozen Wheel**: Running a >100ms calculation on the Main Thread.
    *   *Correction*: Use `Worker` / `QThread`.
4.  **The Sin of Hardcoding**: Using `#FF0000` instead of `COLORS['danger']`.
    *   *Correction*: Use `theme.py`. (Unless it is an Instrument).

---

## 8. Development Lifecycle

1.  **Plan**: Update `task.md` and `implementation_plan.md`.
2.  **Scout**: Run `rite_of_nine.py` to check for violations.
3.  **Code**: Implement changes respecting Sovereignty.
4.  **Verify**: Run tests and manual verification.
5.  **Inscribe**: Update `session_walkthrough.md`.

> *"The Code is the Law, and the Architecture is the Temple."*
