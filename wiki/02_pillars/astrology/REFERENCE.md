# Astrology Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the Celestial Engine of IsopGem, mapping the integration with the Swiss Ephemeris via the OpenAstro2 bridge.

---

**File:** `src/pillars/astrology/ui/astrology_hub.py`

**Role:** `[Skin]` (UI/View)

**Purpose:** The high-level command deck for celestial analysis. It launches specialized windows for Natal Charts, transits, planetary positions, and the Venus Rose.

**The Input (Ingests):**
* `WindowManager` (Object)

**The Output (Emits):**
* None (Spawns windows)

**Dependencies (It Needs):**
* `shared.ui.WindowManager`
* `pillars.astrology.ui.natal_chart_window.NatalChartWindow`
* `pillars.astrology.ui.current_transit_window.CurrentTransitWindow`

**Consumers (Who Needs It):**
* `src/main.py` (IsopGemMainWindow)

**Key Interactions:**
* **Downstream:** Requests the `WindowManager` to instantiate specific astrology windows.
* **Upstream:** None.

---

**File:** `src/pillars/astrology/services/openastro_service.py`

**Role:** `[Muscle]` (Service)

**Purpose:** The primary conductor for the OpenAstro2 engine. It manages chart generation (Radix, Composite, Transit), house system configuration (Placidus, Koch, etc.), and SVG rendering of celestial charts.

**The Input (Ingests):**
* `ChartRequest` (DTO)
* `openastro2` (Library dependency)

**The Output (Emits):**
* `ChartResult` (DTO)

**Dependencies (It Needs):**
* `pillars.astrology.models.ChartRequest`
* `pillars.astrology.models.ChartResult`

**Consumers (Who Needs It):**
* `src/pillars/astrology/ui/natal_chart_window.py`
* `src/pillars/astrology/ui/planetary_positions_window.py`

**Key Interactions:**
* **Downstream:** Performs heavy math on planetary UT coordinates and sign indices.
* **Upstream:** Emits structured results containing planet positions and aspect summaries to the View layer.

---

**File:** `src/pillars/astrology/models/chart_models.py`

**Role:** `[Bone]` (Model)

**Purpose:** Defines the immutable data structures of the cosmos. Encapsulates `GeoLocation`, `AstrologyEvent`, and the resulting `PlanetPosition` mappings.

**The Input (Ingests):**
* Primitive types (`float`, `datetime`).

**The Output (Emits):**
* Data Transfer Objects (DTOs).

**Dependencies (It Needs):**
* `dataclasses.dataclass`

**Consumers (Who Needs It):**
* `src/pillars/astrology/services/openastro_service.py`
* `src/pillars/astrology/ui/natal_chart_window.py`

**Key Interactions:**
* **Downstream:** Provides the type-safe contract for all astronomical data transport.
* **Upstream:** None.
