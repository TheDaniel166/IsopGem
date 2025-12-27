# Time Mechanics Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the "Keeper of Time," mapping the harmonic cycles of the Tzolkin and the temporal circulation of energies.

---

**File:** `src/pillars/time_mechanics/ui/time_mechanics_hub.py`

**Role:** `[Skin]` (UI/View)

**Purpose:** The diplomatic entry point for temporal tools. It provides navigation to the Tzolkin Calculator, the Dynamis (energy circulation) window, and the Zodiacal Circle.

**The Input (Ingests):**
* `WindowManager` (Object)

**The Output (Emits):**
* None (Spawns temporal windows)

**Dependencies (It Needs):**
* `shared.ui.WindowManager`
* `pillars.time_mechanics.ui.tzolkin_window.TzolkinCalculatorWindow`
* `pillars.time_mechanics.ui.dynamis_window.TzolkinDynamisWindow`

**Consumers (Who Needs It):**
* `src/main.py` (IsopGemMainWindow)

**Key Interactions:**
* **Downstream:** Commands the `WindowManager` to open specific cycle analysis windows.
* **Upstream:** None.

---

**File:** `src/pillars/time_mechanics/services/tzolkin_service.py`

**Role:** `[Muscle]` (Service)

**Purpose:** The sovereign service for Tzolkin harmonics. It calculates Kin, Tone, and Sign from Gregorian dates relative to the 2020 Epoch. It also maps these results to the ternary "Ditrune" grid.

**The Input (Ingests):**
* `datetime.date`
* `Docs/time_mechanics/Tzolkin Cycle.csv` (Raw Data)

**The Output (Emits):**
* `TzolkinDate` (Bone/Model)

**Dependencies (It Needs):**
* `pillars.time_mechanics.models.tzolkin_models.TzolkinDate`

**Consumers (Who Needs It):**
* `src/pillars/time_mechanics/ui/tzolkin_window.py`
* `src/pillars/time_mechanics/ui/dynamis_window.py`

**Key Interactions:**
* **Downstream:** Loads and caches the Tzolkin Grid CSV for efficient lookups.
* **Upstream:** Returns structured `TzolkinDate` objects containing Ditrune patterns.

---

**File:** `src/pillars/time_mechanics/models/tzolkin_models.py`

**Role:** `[Bone]` (Model)

**Purpose:** A crystallized data structure representing a harmonic moment. It holds the Kin, Tone (1-13), Sign (1-20), Sign Name, and related Ditrune values.

**The Input (Ingests):**
* Primitive types (`int`, `str`, `date`).

**The Output (Emits):**
* Immutable `TzolkinDate` Objects.

**Dependencies (It Needs):**
* `dataclasses.dataclass`

**Consumers (Who Needs It):**
* `src/pillars/time_mechanics/services/tzolkin_service.py`
* `src/pillars/time_mechanics/ui/tzolkin_window.py`

**Key Interactions:**
* **Downstream:** Pure state; acts as the contract for temporal data.
* **Upstream:** None.
