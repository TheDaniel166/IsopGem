# Gematria Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the "Muscle" and "Skin" of the Gematria pillar, mapping the logic of sacred numerology and scriptural analysis.

---

**File:** `src/pillars/gematria/ui/gematria_hub.py`

**Role:** `[Skin]` (UI/View)

**Purpose:** The central navigator for Gematria tools. It manages the launch of specific analysis chambers, including the "Logos Abacus" (Calculator), "Records of Karnak" (Browser), and "The Resonant Chain" (ELS Search).

**The Input (Ingests):**
* `WindowManager` (Object)

**The Output (Emits):**
* None (Orchestrates tool spawning)

**Dependencies (It Needs):**
* `pillars.gematria.ui.gematria_calculator_window.GematriaCalculatorWindow`
* `pillars.gematria.services.*` (Multiple Calculators)

**Consumers (Who Needs It):**
* `src/main.py` (IsopGemMainWindow)

**Key Interactions:**
* **Downstream:** Injects calculator dependencies into tool windows upon launch.
* **Upstream:** None.

---

**File:** `src/pillars/gematria/services/calculation_service.py`

**Role:** `[Muscle]` (Service)

**Purpose:** The core business logic for Gematria records. It manages the lifecycle of calculations, including saving, updating metadata (Favorite, Category), searching by value, and finding "sibling" calculations (shared text).

**The Input (Ingests):**
* `CalculationRepository` (Memory layer)

**The Output (Emits):**
* `CalculationRecord` (Bone/Model)

**Dependencies (It Needs):**
* `pillars.gematria.models.CalculationRecord`
* `pillars.gematria.repositories.CalculationRepository`
* `pillars.gematria.services.base_calculator.GematriaCalculator`

**Consumers (Who Needs It):**
* `src/pillars/gematria/ui/gematria_calculator_window.py`
* `src/pillars/gematria/ui/saved_calculations_window.py`
* `src/pillars/gematria/ui/batch_calculator_window.py`

**Key Interactions:**
* **Downstream:** Persists data through the `CalculationRepository`.
* **Upstream:** Returns structured records and breakdown dictionaries to the presentation layer.

---

**File:** `src/pillars/gematria/models/calculation_record.py`

**Role:** `[Bone]` (Model)

**Purpose:** The essential data model for a gematria entry. It stores the raw and normalized text, the calculated value, the methods used, and audit metadata (date, category, notes).

**The Input (Ingests):**
* Data primitives (`int`, `str`, `datetime`).

**The Output (Emits):**
* Pure `CalculationRecord` Objects.

**Dependencies (It Needs):**
* `dataclasses.dataclass`

**Consumers (Who Needs It):**
* `src/pillars/gematria/services/calculation_service.py`
* `src/pillars/gematria/repositories/calculation_repository.py`

**Key Interactions:**
* **Downstream:** Serves as the DTO (Data Transfer Object) for database transactions.
* **Upstream:** Provides the type-safe structure used throughout the pillar.
