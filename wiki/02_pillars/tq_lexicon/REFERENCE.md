# TQ Lexicon Pillar - Anatomy Chart

<!-- Last Verified: 2026-01-03 -->

This pillar houses the **Holy Book → Concordance → Master Key** workflow: importing documents, indexing occurrences, and curating the lexicon.

---

**File:** `src/pillars/tq_lexicon/ui/unified_lexicon_window.py`

**Role:** `[Skin]` (UI/View)

**Purpose:** Unified tabbed workflow window:
1. Import & Parse
2. Candidates
3. Concordance
4. Master Key

**Dependencies (It Needs):**
* `shared.services.lexicon.holy_key_service.HolyKeyService`
* `shared.services.lexicon.concordance_indexer_service.ConcordanceIndexerService`
* `shared.services.lexicon.enrichment_service.EnrichmentService`

---

**File:** `src/pillars/tq_lexicon/ui/holy_book_concordance_window.py`

**Role:** `[Skin]` (UI/View)

**Purpose:** Earlier unified parse+index window.

**Status:** Deprecated (prefer `UnifiedLexiconWindow`).

---

**File:** `src/pillars/tq_lexicon/ui/lexicon_manager_window.py`

**Role:** `[Skin]` (UI/View)

**Purpose:** Earlier lexicon manager window.

**Status:** Deprecated (prefer `UnifiedLexiconWindow`).
