# Emerald Tablet Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the "Spreadsheet of the Stars," mapping the logic of correspondences and formula-driven esoteric tables.

---

**File:** `src/pillars/correspondences/ui/correspondence_hub.py`

**Role:** `[Skin]` (UI/View)

**Purpose:** The central library for the "Emerald Tablet." It manages the ingestion of Excel/CSV files and organizes saved "Scrolls" into a browseable list.

**The Input (Ingests):**
* `WindowManager` (Object)
* `SessionLocal` (Database Session)

**The Output (Emits):**
* None (Launches Spreadsheet windows)

**Dependencies (It Needs):**
* `pillars.correspondences.ui.spreadsheet_window.SpreadsheetWindow`
* `pillars.correspondences.services.ingestion_service.IngestionService`
* `pillars.correspondences.services.table_service.TableService`

**Consumers (Who Needs It):**
* `src/main.py` (IsopGemMainWindow)

**Key Interactions:**
* **Downstream:** Triggers the `IngestionService` to process raw files into table models.
* **Upstream:** None.

---

**File:** `src/pillars/correspondences/services/table_service.py`

**Role:** `[Muscle]` (Service)

**Purpose:** The "Steward of the Tablets." It mediates between the UI and the persistence layer, managing the creation, retrieval, renaming, and destruction of correspondence tables.

**The Input (Ingests):**
* `sqlalchemy.orm.Session`

**The Output (Emits):**
* `CorrespondenceTable` (Bone/Model)

**Dependencies (It Needs):**
* `pillars.correspondences.repos.table_repository.TableRepository`
* `pillars.correspondences.models.correspondence_models.CorrespondenceTable`

**Consumers (Who Needs It):**
* `src/pillars/correspondences/ui/correspondence_hub.py`
* `src/pillars/correspondences/ui/spreadsheet_window.py`

**Key Interactions:**
* **Downstream:** Commits changes to the `TableRepository`.
* **Upstream:** Returns structured table objects to the presentation layer.

---

**File:** `src/pillars/correspondences/models/correspondence_models.py`

**Role:** `[Bone]` (Model)

**Purpose:** Defines the data structure for a "Tablet." It stores the table name, its grid content (JSON), and metadata (created/updated timestamps).

**The Input (Ingests):**
* Data primitives (`str`, `dict`, `datetime`).

**The Output (Emits):**
* `CorrespondenceTable` Objects.

**Dependencies (It Needs):**
* `sqlalchemy` (Table mapping)

**Consumers (Who Needs It):**
* `src/pillars/correspondences/services/table_service.py`
* `src/pillars/correspondences/repos/table_repository.py`

**Key Interactions:**
* **Downstream:** Serves as the persistence skeleton for SQL transactions.
* **Upstream:** None.
