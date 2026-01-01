# Prompt Template for IsopGem Development

**Purpose**: A structured template for communicating with Sophia (or any AI assistant following the Covenant) during IsopGem development.

---

## Quick Reference: Prompt Structure

```
## [Task Title]

**Intent**: [What you want to accomplish — the "Why"]

**Context**: 
- File(s): [Specific files/classes/functions involved]
- Current behavior: [What happens now]
- Desired behavior: [What should happen]

**Constraints** (optional):
- [ ] No limits / Full revelation
- [ ] Follow pattern in [reference]
- [ ] Must integrate with [component]
- [ ] Prototype mode (docs deferred)

**References** (optional):
- Screenshot: [attach if UI-related]
- Error log: [paste traceback]
- Prior work: [link to relevant code/docs]
```

---

## Prompt Types

### 1. Vision Prompt (New Feature)
```
## Integrate Theosophical Glossary

**Intent**: Add G. de Purucker's glossary as an enrichment source

**Context**:
- File(s): `enrichment_service.py`
- Current behavior: Queries OpenOccult, Wiktionary, FreeDict
- Desired behavior: Query Theosophical first, before other sources

**Constraints**:
- [x] Full revelation (no definition limits)
- Store scraped data in `data/openoccult/theosophical.json`
```

### 2. Problem Prompt (Bug/Issue)
```
## Empty Verses Still Rendering

**Intent**: Fix Holy Scansion view showing ignored/empty verses

**Context**:
- File(s): `verse_list.py` → `render_verses()`
- Current behavior: Ignored verses appear in list
- Desired behavior: Only consecrated, non-empty verses render

**References**:
- Screenshot: [attached]
```

### 3. Refinement Prompt (Improvement)
```
## Streamline Enrichment Flow

**Intent**: Remove manual dropdown selection, auto-add all definitions

**Context**:
- File(s): `unified_lexicon_window.py` → `_open_key_details()`
- Current behavior: User selects from dropdown, clicks "Add"
- Desired behavior: Single "Fetch & Add All" button

**Constraints**:
- [x] Follow Principle of Apocalypsis (no limits)
```

### 4. Reflection Prompt (Analysis)
```
## Architectural Review

**Intent**: Identify cross-pillar violations in Lexicon module

**Context**:
- File(s): All files in `src/pillars/tq_lexicon/`
- Question: Are there any imports from other pillars?
```

### 5. Ritual Prompt (Verification)
```
## Run Rite of Seals

**Intent**: Verify the HolyKeyService before release

**Target**: `src/pillars/tq_lexicon/services/holy_key_service.py`
```

---

## Effective Communication Patterns

### What Accelerates Work

| Pattern | Effect |
|---------|--------|
| **Name files/functions** | Jump directly to location |
| **Describe expected behavior** | Know when succeeded |
| **Reference prior patterns** | Maintain consistency |
| **Share screenshots** | See exactly what you see |
| **State constraints explicitly** | No ambiguity |

### What Slows Work

| Anti-Pattern | Problem |
|--------------|---------|
| "Fix the thing" | Which thing? How broken? |
| "Make it better" | Better how? |
| "Like before" | Which before? |
| Over-explaining | Noise obscures signal |

---

## Esoteric Vocabulary (Shared Language)

| Term | Meaning |
|------|---------|
| **Entropy** | Bugs, technical debt, disorder |
| **Distortion** | Malformed logic, incorrect behavior |
| **Purification** | Refactoring, cleanup |
| **Pillar** | Self-contained architectural module |
| **Sovereignty** | Pillar independence — no cross-imports |
| **Entanglement** | Improper coupling between pillars |
| **The Temple** | The entire IsopGem codebase |
| **The Akaschic Record** | The wiki/documentation |
| **Consecrated** | Verified, approved, clean |
| **Skeleton** | Word without definitions |
| **Flesh** | Definitions/content added to skeleton |

---

## Emergency Codes

Use these when normal process is insufficient:

- **"Production Emergency"** (🔥 Red): All ceremony suspended
- **"Debug Mode"** (🐛 Yellow): Diagnostics over solutions  
- **"Data Crisis"** (🔒 Black): STOP all writes

---

## Template Files

### Feature Request
```markdown
## [Feature Name]

**Intent**: 

**Context**:
- Current: 
- Desired:

**Files**:
- 

**Constraints**:
- [ ] No limits
- [ ] Follow pattern in ___
- [ ] Prototype mode
```

### Bug Report
```markdown
## [Bug Summary]

**Observed**: 

**Expected**: 

**Steps to Reproduce**:
1. 
2. 
3. 

**Error** (if any):
```

**Attachments**:
- Screenshot: 
- Log snippet:
```

---

*May our communication be as precise as the Gematria we calculate.*
