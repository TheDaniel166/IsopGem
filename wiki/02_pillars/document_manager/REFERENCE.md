# Document Manager Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the Akaschic Archive, mapping the lifecycle of rich-text manuscripts and the visual "Mindscape" graph.

---

**File:** `src/pillars/document_manager/ui/document_manager_hub.py`

**Role:** `[Skin]` (UI/View)

**Purpose:** The dispatcher for the Document Sovereignty. It manages access to "Thoth's Scribe" (Editor), "The Akaschic Record" (Library), and the "Mindscape" (Graph view).

**The Input (Ingests):**
* `WindowManager` (Object)

**The Output (Emits):**
* None (Orchestrates window spawning)

**Dependencies (It Needs):**
* `shared.ui.WindowManager`
* `pillars.document_manager.ui.document_editor_window.DocumentEditorWindow`
* `pillars.document_manager.ui.document_library.DocumentLibrary`

**Consumers (Who Needs It):**
* `src/main.py` (IsopGemMainWindow)

**Key Interactions:**
* **Downstream:** Connects the Library and Search windows to the Editor for document loading.
* **Upstream:** Raises managed windows via the `WindowManager` heartbeat.

---

**File:** `src/pillars/document_manager/services/document_service.py`

**Role:** `[Muscle]` (Service)

**Purpose:** The sovereign service for manuscript persistence. It orchestrates complex transactions, including full-text search index updates, image binary management, and verse-level cross-referencing.

**The Input (Ingests):**
* `DocumentRepository`, `SearchRepository`

**The Output (Emits):**
* `Document` (Model), `SearchResult` (DTO)

**Dependencies (It Needs):**
* `pillars.document_manager.models.document.Document`
* `pillars.document_manager.repositories.document_repository.DocumentRepository`

**Consumers (Who Needs It):**
* `src/pillars/document_manager/ui/rich_text_editor.py`
* `src/pillars/document_manager/ui/document_library.py`

**Key Interactions:**
* **Downstream:** Persists document metadata and binary assets to the DB and FS.
* **Upstream:** Returns structured HTML and metadata DTOs to the View.

---

**File:** `src/pillars/document_manager/models/document.py`

**Role:** `[Bone]` (Model)

**Purpose:** The fundamental representation of a manuscript. It contains the rich-text content, document ID, title, and metadata timestamps.

**The Input (Ingests):**
* Primitive types.

**The Output (Emits):**
* Pure `Document` Objects.

**Dependencies (It Needs):**
* `sqlalchemy` (Table mapping)

**Consumers (Who Needs It):**
* `src/pillars/document_manager/services/document_service.py`
* `src/pillars/document_manager/repositories/document_repository.py`

**Key Interactions:**
* **Downstream:** Acts as the primary DTO for persistence operations.
* **Upstream:** None.
