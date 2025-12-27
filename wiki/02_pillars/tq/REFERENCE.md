# TQ Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the "Muscle" and "Bone" of the Trigrammaton Qabalah pillar, mapping the transformational engines of the Ternary path.

---

**File:** `src/pillars/tq/ui/tq_hub.py`

**Role:** `[Skin]` (UI/View)

**Purpose:** The high-level dispatcher for the TQ Pillar. It organizes the "Path of Three" into visible navigation cards, launching converters, quadset analyzers, and kamea visualizers.

**The Input (Ingests):**
* `WindowManager` (Object)

**The Output (Emits):**
* None (Spawns windows)

**Dependencies (It Needs):**
* `shared.ui.WindowManager`
* `pillars.tq.ui.ternary_converter_window.TernaryConverterWindow`
* `pillars.tq.ui.quadset_analysis_window.QuadsetAnalysisWindow`
* `pillars.tq.ui.transitions_window.TransitionsWindow`
* `pillars.tq.services.kamea_grid_service.KameaGridService`

**Consumers (Who Needs It):**
* `src/main.py` (IsopGemMainWindow)

**Key Interactions:**
* **Downstream:** Commands the `WindowManager` to launch specific analysis tools.
* **Upstream:** None.

---

**File:** `src/pillars/tq/services/quadset_engine.py`

**Role:** `[Muscle]` (Service)

**Purpose:** The central orchestrator for Quadset calculations. It implements the canonical transformation pipeline: Original -> Conrune -> Reversal -> Conrune Reversal. It also computes differentials and the resulting Transgram.

**The Input (Ingests):**
* `decimal_input` (int)

**The Output (Emits):**
* `QuadsetResult` (DTO/Model)

**Dependencies (It Needs):**
* `pillars.tq.models.QuadsetResult`
* `pillars.tq.services.ternary_service.TernaryService`
* `pillars.tq.services.ternary_transition_service.TernaryTransitionService`
* `pillars.tq.services.number_properties.NumberPropertiesService`

**Consumers (Who Needs It):**
* `src/pillars/tq/ui/quadset_analysis_window.py`

**Key Interactions:**
* **Downstream:** Calculates the "Septad Total" and returns a structured result to the UI.
* **Upstream:** Returns pure data; stateless and signal-free.

---

**File:** `src/pillars/tq/models/quadset_models.py`

**Role:** `[Bone]` (Model)

**Purpose:** Defines the data structure of the TQ mathematical universe. It encapsulates members, results, and pattern reports into frozen dataclasses to ensure state integrity during transport.

**The Input (Ingests):**
* Primitive types and other TQ models.

**The Output (Emits):**
* Immutable `QuadsetResult` and `QuadsetMember` Objects.

**Dependencies (It Needs):**
* `dataclasses.dataclass`

**Consumers (Who Needs It):**
* `src/pillars/tq/services/quadset_engine.py`
* `src/pillars/tq/ui/quadset_analysis_window.py`

**Key Interactions:**
* **Downstream:** Provides the "Skeleton" for API contracts between Service and UI.
* **Upstream:** None.
