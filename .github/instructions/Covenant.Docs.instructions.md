---
applyTo: 'wiki/**'
---
# Covenant Docs Scrolls (mirror)

<!-- Last Verified: 2026-01-13 -->

---

01_akaschic_record.md

# The Akaschic Record (Section 1: Documentation)

**"As Above, So Below. The Code is the Body; the Documentation is the Soul."**

We maintain a **Living Library (The Wiki)**. If the Documentation does not match the Code, the Temple is built on lies.

---

## 1.1 The Structure of the Grand Archive

The `wiki/` is organized into **Five Halls**. Each file must bear the **Header of Validity**:
```markdown
<!-- Last Verified: YYYY-MM-DD -->
```

**Hall 0: The Foundations (`wiki/00_foundations/`)**
* `SETUP_RITUAL.md`: Zero-to-Hero guide
* `THE_COVENANT.md`: This Rulebook
* `DEPENDENCY_MANIFEST.md`: Why we use specific libraries

**Hall 1: The Blueprints (`wiki/01_blueprints/`)**
* `SYSTEM_MAP.md`: High-level topology (C4 Model)
* `decisions/`: Architecture Decision Records (ADRs)
* `UI_UX_PHILOSOPHY.md`: Visual guidelines

**Hall 2: The Grimoires (`wiki/02_pillars/`)**
* Folder per Pillar with three **Diátaxis** scrolls:
  1. `REFERENCE.md` — Technical anatomy ("What it is")
  2. `EXPLANATION.md` — Theoretical foundations ("Why it is")
  3. `GUIDES.md` — Practical how-to ("How to use it")
* `CHANGELOG.md`: Pillar-specific history

**Hall 3: The Lexicon (`wiki/03_lexicon/`)**
* `DATA_DICTIONARY.md`: Complex data model definitions
* `GLOSSARY.md`: Domain term definitions

**Hall 4: The Prophecies (`wiki/04_prophecies/`)**
* `CURRENT_CYCLE.md`: Current sprint
* `THE_HORIZON.md`: Backlog
* `KNOWN_DISTORTIONS.md`: Known bugs and tech debt

## 1.2 The Ban on Banality

I am forbidden from using "Empty Words":
* **Forbidden**: "Standard boilerplate", "Standard method arguments", "None detected"
* **Required**: Explain **Intent**, not just mechanics

## 1.3 The Ritual of Reflection & Consultation

Before entering **EXECUTION** phase:
1. **Consult the Blueprints**: Scan `SYSTEM_MAP.md` and relevant ADRs
2. **Consult the Grimoire**: Read the Pillar's `REFERENCE.md`
3. **Consult the Sentinel**: Run `verify_manifest.py`

Additional rules:
* Before complex logic (Complexity > 5), write the doc entry *first*
* If refactoring a class name, grep the `wiki/` to rename it in texts
* Use **Mermaid Diagrams** when words are insufficient

## 1.4 The Deep Analysis Pattern

When documenting in the Wiki:
* **Architectural Role**: Service, Model, or View
* **The Problem**: Why does this exist?
* **Key Logic**: Detailed explanation of *algorithms*

## 1.5 The Sacred Templates

**A. The Pillar Reference (`REFERENCE.md`):**
```
**File:** `src/pillars/[pillar]/[path]/[file].py`
**Role:** `[Muscle]` (Service), `[Bone]` (Model), or `[Skin]` (View)
**Purpose:** Brief summary
**Input (Ingests):** Types accepted
**Output (Emits):** Values returned
**Dependencies:** Explicit imports
**Consumers:** Files that import this
**Key Interactions:** Downstream/Upstream signals
```

**B. Architecture Decision Record (ADR):**
```
**Title:** `ADR-[ID]: [Title]`
**Status:** Proposed | Accepted | Superseded
**Context:** What problem prompted this?
**Decision:** The chosen path
**Consequences:** Cost and gain
```

## 1.6 The Law of the Pyre

**"When the Body dies, the Soul must be released."**

If a file is deleted:
* Delete/archive its wiki entry
* Strip from `REFERENCE.md`
* Update broken links
* **Constraint**: No orphaned links in the Akaschic Record

## 1.7 The Rite of Completion

**"A Thing is not Done until it is Written."**

When a task is finished:
* Append to `wiki/04_prophecies/CURRENT_CYCLE.md` under "Completed Milestones"
* Format: `- **YYYY-MM-DD**: [Brief description]`

---

Do not edit here. Update the canonical scrolls instead:
- Canonical source: `wiki/00_foundations/covenant/`
- VS Code mirror: `.github/instructions/covenant/`

Regenerate mirrors and these bundles with:
`.venv/bin/python scripts/covenant_scripts/sync_covenant.py`
