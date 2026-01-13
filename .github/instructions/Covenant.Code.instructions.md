---
applyTo: 'src/**,scripts/**'
---
# Covenant Code Scrolls (mirror)

<!-- Last Verified: 2026-01-12 -->

---

02_spheres.md

# The Doctrine of Spheres (Section 2: Architecture)

**"The Universe is expanding. When a new Star is born, it must not collide with the old."**

The architecture of IsopGem is a growing galaxy. A "Pillar" is a repeatable, fractal pattern.

---

## 2.1 The Definition of a Sphere (Pillar)

A **Pillar** is a Sovereign Nation of Logic. It owns its own data, rules, and interface.

* **The Current Pantheon:** Gematria, Astrology, Geometry, Document Manager, TQ, Adyton, Correspondences
* **The Living Cosmos:** Designed to accept new Pillars (Tarot, Alchemy, I Ching) at any time

## 2.2 The Standard Topology (The Fractal Pattern)

Every Pillar **MUST** contain these five organs:

1. **`models/` (The Bones):** Pure Data Classes and SQLAlchemy Tables
   * *Constraint:* Zero dependencies on UI or Services

2. **`repositories/` (The Memory):** Only layer touching Database/File System
   * *Constraint:* Services ask Repositories for data; never query SQL directly

3. **`services/` (The Muscle):** Algorithms, Calculations, Business Logic
   * *Constraint:* Complex logic must be verifiable via the Seal

4. **`ui/` (The Skin):** Presentation Layer
   * *Mandate:* Must contain a `*Hub` class as single entry point

5. **`utils/` (The Tools):** Helper functions specific to this pillar only

## 2.3 The Infrastructure (Shared Base)

The `shared/` directory contains common foundation:
* **Database:** Connection engine and session factory
* **Navigation Bus:** Central nervous system for inter-pillar communication
* **Base Classes:** Shared abstract base classes for polymorphic consistency
* **Window Manager:** Diplomatic envoy that launches Sovereign Windows

## 2.4 The Ritual of Genesis (Adding a New Pillar)

1. **Scaffold the Void:** Create `src/pillars/[name]/` with five sub-organs and `__init__.py`
2. **The Diplomat (Hub):** Create `ui/[name]_hub.py` inheriting from `QWidget`
3. **The Registration:** Add lazy import in `window_manager.py`, update `wiki/SYSTEM_MAP.md`
4. **The Dependency Check:** Verify usage of `shared.database` and `shared.ui.theme`

## 2.5 The Law of Sovereignty

* **The Iron Rule:** `pillars/astrology` must **NEVER** directly import from `pillars/tq`
* **The Bridge:** Use the **Signal Bus** for inter-pillar communication
  1. Fire Signal: `navigation_bus.request_window.emit()`
  2. Window Manager catches and launches the Sovereign
  3. **Result:** Pillars touch but never hold hands — decoupled

---

03_verification.md

# The Law of the Seal (Section 3: Verification)

**"As the Seven Spheres govern the Heavens, so shall they judge the Code."**

We do not merely "test" code; we subject it to the **Planetary Trials**.

---

## 3.1 The Rite of the Seven Seals

Before declaring a task "Done," perform the **Planetary Trials**:

| Planet | Domain | The Check | Failure Condition |
|--------|--------|-----------|-------------------|
| ♄ Saturn | Structure | Circular imports, type hints, sovereignty | Linting errors, entangled imports |
| ♃ Jupiter | Load | Performance at scale (10,000 rows) | O(n²) on main thread |
| ♂ Mars | Conflict | Error handling (None, -1, garbage) | Uncaught exception |
| ☉ Sun | Truth | Core logic correctness | Incorrect calculation |
| ♀ Venus | Harmony | API contracts, data shapes | Malformed DTOs |
| ☿ Mercury | Signals | Logging, signal emission | Silent execution |
| ☾ Moon | Memory | State persistence, save/reload | Data corruption |

## 3.2 The Execution of the Rite

1. **Invocation:** `python scripts/covenant_scripts/verification_seal.py --target [FeatureName]`
2. **The Constraint:** Must run **Headless** (without UI)
3. **The Proof:** Present Planetary Report to The Magus

## 3.3 The Rite of the Zodiac (Architectural Audit)

A high-order analytic audit for core services and significant refactors:

| Sign | Domain | The Check |
|------|--------|-----------|
| ♈ Aries | Boot Velocity | Module must boot < 150ms |
| ♉ Taurus | Structure | Valid data model annotations |
| ♊ Gemini | Contracts | Public functions have docstrings |
| ♋ Cancer | Isolation | UI not touching SQL, Services not touching PyQt |
| ♌ Leo | Performance | Average op speed < 0.5ms |
| ♍ Virgo | Purity | Type-hint coverage > 80% |
| ♎ Libra | Balance | Memory growth < 64KB during churn |
| ♏ Scorpio | Chaos | Survives fuzzing without crash |
| ♐ Sagittarius | Integration | All dependencies reachable |
| ♑ Capricorn | Debt | No TODO comments or deprecation warnings |
| ♒ Aquarius | Concurrency | Thread-safe under parallel access |
| ♓ Pisces | Depth | Test coverage > 90% |

**Execution:** `python3 scripts/covenant_scripts/rite_of_zodiac.py [module.path]`

## 3.4 The Seven Planetary Workflows

| Planet | Workflow | Script | Enforces |
|--------|----------|--------|----------|
| ♄ Saturn | `/verify_covenant` | `verify_sentinel.py` | Law 0.5 (Dual Inscription) |
| ♃ Jupiter | `/purify_vicinity` | `purify_vicinity.py` | Section 6 (Scout's Code) |
| ♂ Mars | `/rite_of_pyre` | `rite_of_pyre.py` | Law 1.6 (No Ghosts) |
| ☉ Sun | `/rite_of_sovereignty` | `rite_of_sovereignty.py` | Law 2.4 (Pillar Boundaries) |
| ♀ Venus | `/rite_of_contamination` | `rite_of_contamination.py` | Law 4.2 (UI Purity) |
| ☿ Mercury | `/rite_of_seals` | `verification_seal.py` | Section 3 (7 Trials) |
| ☾ Moon | `/rite_of_inscription` | `rite_of_inscription.py` | Law 1.2 (Ban on Banality) |

**Invocation:** `.venv/bin/python scripts/covenant_scripts/<script_name>.py [arguments]`

---

## 3.5 The Seal of Completion (Sophia's Mandatory Verification)

**"Before the Word 'Done' is spoken, the Seal must be invoked."**

**THIS IS NOT A SUGGESTION. THIS IS A STRUCTURAL REQUIREMENT.**

Sophia is **FORBIDDEN** from declaring work complete without verification. Any work presented without seal invocation is **INCOMPLETE AND INVALID**.

### The Mandatory Protocol

Before returning ANY code to The Magus, Sophia **MUST**:

1. **Consult working examples** (`sophia_consult` or direct file reading)
2. **Verify signatures match** (dataclasses, function parameters, return types)
3. **Invoke the appropriate verification seal**
4. **Present proof of passage** (seal output) or document violations
5. **ONLY THEN present code to The Magus**

**Failure to follow this sequence renders the work VOID.**

### Seal Selection by Work Type (MANDATORY)

| Work Type | Seal to Invoke | Verification Target |
|-----------|----------------|---------------------|
| Pillar code changes | `sophia_seal sovereignty` | No inter-pillar imports |
| UI modifications | `sophia_seal ui_purity` | No heavy libs in UI |
| Covenant/documentation | `sophia_seal dual_inscription` | Canonical ↔ mirror sync |
| Major refactoring | `sophia_seal all` | All architectural rules |
| Structural changes | `sophia_scout all` | No missing files, orphans |

### The Tools

Sophia invokes these through the **sophia-tools** extension:

- `sophia_seal` - Run verification rituals programmatically
- `sophia_scout` - Structural inventory and health check
- `sophia_trace` - Dependency impact analysis (pre-change)
- `sophia_align` - Documentation drift detection

### Example Completion Report (REQUIRED FORMAT)

```
✅ [Feature Name] complete

Pre-Delivery Verification:
1. Consulted: [working_example.py] (read lines 1-195)
2. Verified signatures: FormRealization(artifact, metrics, provenance) ✓
3. sophia_seal sovereignty: PASS (0 violations in 381 files)
4. sophia_scout: Structure intact, no orphaned files

Work is sealed and verified. Code delivery authorized.
```

### The Exception (Seal Failure Protocol)

If a seal **fails**, Sophia **MUST IMMEDIATELY**:
1. **HALT delivery** - do not present incomplete code
2. Report the failure to The Magus
3. Present the specific violations
4. Propose remediation
5. Re-verify after fix
6. Only then resume delivery

**ABSOLUTE RULE: No work is "Done" until the Seal passes. Period.**

---

## 3.6 Pre-Implementation Consultation (MANDATORY)

Before implementing ANY feature that follows an existing pattern, Sophia **MUST**:

1. **Identify the canonical example** (e.g., VaultOfHestiaRealizer for realizers)
2. **Read the complete implementation** (not just scan it)
3. **Extract the pattern**:
   - Required imports
   - Dataclass signatures
   - Method signatures
   - Helper method patterns
   - Return structures
4. **Replicate the pattern exactly**

**Violation of this protocol produces structurally invalid code and is FORBIDDEN.**

---

04_purity_resilience.md

# The Doctrine of Purity & Resilience (Sections 4-5)

---

## Section 4: The Doctrine of Purity

**"The Eye does not think; it sees. The Mind thinks; it does not see."**

The **View** (UI) and the **Logic** (Service) inhabit different planes of existence.

### 4.1 The Definition of Realms

**The Realm of Form (The View - `ui/`)**
* **Purpose:** Present the Shadow of Truth
* **Allowed:** Layout, painting, animations, capturing clicks
* **The Limit:** The View is "Hollow" — knows nothing of database, math, or stars
* **Exemption (Rendered Content):** HTML/CSS used for document rendering (e.g., QTextBrowser content) is considered content, not UI chrome, and is not subject to Visual Liturgy token enforcement.

**The Realm of Essence (The Service - `services/`)**
* **Purpose:** Calculate the Truth
* **Allowed:** Complex math, DB queries, file parsing, API requests
* **The Limit:** The Service is "Blind" — must never import `PyQt6.QtWidgets`

### 4.2 The Law of Contamination

A UI file is **Desecrated** if it imports:
* `sqlalchemy` (Direct Database Access)
* `pandas` (Heavy Data Processing)
* `requests` / `urllib` (Network IO)
* `lxml` / `bs4` (Parsing Logic)

**The Correction:** Extract logic to a Service.

### 4.3 The Nervous System (Signals & Slots)

The Mind and Body communicate via the **Signal Bus**:
* **Downstream (Command):** UI fires Signal (`request_calculation`)
* **Upstream (Revelation):** Service fires Signal (`calculation_ready`)
* **Constraint:** Pass **DTOs** (dicts/dataclasses), never raw SQLAlchemy models

### 4.4 The Sin of the Frozen Wheel

If calculation takes > 100ms, it is **Forbidden** on the Main Thread.

**The Ritual of Threading:**
1. Encapsulate in `QRunnable` or `Worker` class
2. Offload to `QThreadPool`
3. Await Signal of Completion

### 4.5 The Law of Configuration Sovereignty

**"The roots of the Temple must be known, not scattered."**

All configuration and path access must flow through **singular channels** to ensure testability, auditability, and deployment flexibility.

#### 4.5.1 The Doctrine of Centralization

**Mandatory Centralization** (via `get_config()`):
* **Environment Variables:** All `os.environ` access (except `main.py` bootstrapping)
* **User-Modifiable Paths:** State, config, preferences, cache
* **Critical System Paths:** Database locations, application-wide resources
* **Deployment-Variant Paths:** Paths that differ between frozen/dev builds

**Rationale:** These concerns affect system stability, security, and testing. Centralization provides a single source of truth.

#### 4.5.2 The Doctrine of Pragmatism

**Permitted Direct Access** (via utility functions like `get_data_path()`):
* **Read-Only Static Data:** Lexicon directories, ephemeris files
* **Immutable Resources:** Asset paths, icon directories
* **Development-Time Helpers:** Simple path construction for non-critical resources

**Rationale:** Not all path access requires heavy configuration machinery. Simple utilities serve simple needs.

#### 4.5.3 The Forbidden Patterns

**Never:**
* Hardcoded absolute paths (`/usr/share/isopgem/data`)
* Repeated construction of the same path (`get_data_path() / "databases" / "isopgem.db"` when `config.paths.main_db` exists)
* Environment access scattered across services (except whitelisted bootstrap files)

#### 4.5.4 The Test of Living Reason

Before centralizing a path or configuration value, ask:
* **Does this vary by deployment?** (Yes → Centralize)
* **Is this user-configurable?** (Yes → Centralize)
* **Would changing this require touching multiple files?** (Yes → Centralize)
* **Is this a simple, static, read-only resource?** (Yes → Direct access acceptable)

**The Caution:** Avoid centralization for its own sake. Ossified rules without living reasons become sediment, not structure.

#### 4.5.5 The Implementation

**Single Source of Truth:**
```python
# shared/config.py - The Canonical Registry
from shared.config import get_config

config = get_config()
db_path = config.paths.main_db          # ✓ Centralized critical path
state_path = config.paths.user_state    # ✓ User-modifiable path
lexicon_dir = config.paths.lexicons     # ✓ Defined once, used many
```

**Permitted Utility Access:**
```python
# For simple, static data directory access
from shared.paths import get_data_path

data_dir = get_data_path()
lexicons = data_dir / "lexicons"  # ✓ Simple, direct, acceptable
```

---

## Section 5: The Law of the Shield

**"The Temple is built on shifting sands. When the earth shakes, the structure must sway, not shatter."**

### 5.1 The Principle of Containment

* **The Rule:** A crash in one Pillar must **NEVER** bring down the application
* **The Mechanism:**
  - Wrap public Service methods in `try/except`
  - Catch specific exceptions, log them
  - Return Result Object (Success/Failure) instead of propagating

### 5.2 The Voice of the Temple

`print()` is forbidden. Write to **The Chronicle (Logger)**:

| Level | Use Case |
|-------|----------|
| **INFO** | Routine life ("Engine initialized") |
| **WARNING** | Recoverable deviation ("API unreachable; using cache") |
| **ERROR** | Local failure ("Failed to parse file") |
| **CRITICAL** | Total failure ("Database missing") |

**Mandate:** Every `except` block MUST emit a log.

### 5.3 Graceful Degradation

* Offer **Degraded State** rather than blank screen
* Return `None` or `EmptyList` over raising Exceptions
* UI handles `None` by displaying "No Data Available"

### 5.4 The Rite of Disclosure

**Feedback Loop:**
* **Trivial Events:** Status Bar
* **Process Failures:** Non-Modal Toast
* **Critical Stops:** Modal Dialog (`QMessageBox`)

**Error Language:** Human-readable, not `KeyError: 'Sun'`

### 5.5 The Law of Observability

Every Service method must be observable:

**The Three Truths:**
1. Entry Logging: `logger.info("Operation initiated")`
2. Error Logging: `logger.error(f"Failed: {e}")`
3. Exit Logging: `logger.info("Operation complete")`

**Performance Instrumentation:**
```python
start = time.perf_counter()
# ... expensive operation ...
if (elapsed := time.perf_counter() - start) > 0.5:
    logger.warning(f"Slow operation: {elapsed:.3f}s")
```

## Section 6: The Completeness Protocol

**"A structure half-built is a ruin in the making."**

The Magus demands **Demonstrated Competence**, not just intent.

### 6.1 The Law of Pre-Flight
Before the Agent presents code to the Magus, it MUST pass the **Rite of Integrity**:
1.  **Check:** Run `scripts/covenant_scripts/verify_integrity.py` on the modified file.
2.  **Verify:**
    *   No `SyntaxError` (The structure holds).
    *   No `NameError` (The names are known).
    *   No Missing Imports (The connections are forged).
3.  **Correction:** If the Rite fails, the Agent must heal the code **before** notification.

### 6.2 The Init Discipline
When adding a new attribute (`self.new_attr`) to a class:
*   **Mandate:** The Agent must simultaneously update `__init__` to initialize it.
*   **The Sin:** Creating a property that exists only after a specific method is called. All state must be born in `__init__`.

---

05_maintenance.md

# Maintenance, Visuals & Time (Sections 6-8)

---

## Section 6: The Ritual of the Scout

**"Entropy is the shadow that follows Creation. We sweep it away with every step."**

### 6.1 The Law of Vicinity

When opening a file, heal the code in the **immediate vicinity**:
* **The Radius:** Responsible for the class/function being touched
* **The Mandate:** Do not close a file until local entropy is reduced

### 6.2 The Four Acts of Purification

1. **The Pruning (Unused Imports):** Delete gray imports, order by: StdLib → Third Party → Local
2. **The Illumination (Type Hints):** `def calculate(value: int) -> float:`
3. **The Inscription (Docstrings):** Explain **Intent**, not mechanics
4. **The Exorcism (Dead Code):** Delete commented-out code — Git remembers

### 6.3 The Constraint of Scope

* **Allowed:** Incidental refactoring (rename variable for clarity)
* **Forbidden:** Structural refactoring unless that IS the task

---

## Section 7: The Visual Language

**"Words are shadows of meaning; Geometry is the light."**

### 7.1 The Mandate of Illustration

Generate diagrams when:
* Two Sovereigns interact (inter-pillar traffic)
* Class hierarchy extends beyond 2 levels
* Data undergoes more than 3 transformations

### 7.2 The Sacred Shapes

| Diagram | Use Case |
|---------|----------|
| **C4 (Context/Container)** | "Which worlds exist?" (Hall 1 only) |
| **Sequence Diagram** | "Who speaks to whom?" (Signal Bus, flows) |
| **Class Diagram** | "What is it made of?" (Models, schemas) |
| **Flowchart** | "Where does the data go?" (Algorithms) |

### 7.3 The Syntax of Clarity

* Label arrows with **Data** being passed, not generic verbs
* Time flows down (TD) or right (LR), never up

---

## Section 8: The Law of Time

**"Time flows forward, but History allows us to return."**

### 8.1 The Atomic Moment

* **The Rule:** One Commit = One Idea
* **Constraint:** Don't mix Refactor with Feature in same commit

### 8.2 Conventional Commits

| Key | Purpose |
|-----|---------|
| `feat:` | New capability |
| `fix:` | Repair broken logic |
| `docs:` | Wiki/documentation only |
| `style:` | Formatting, no code change |
| `refactor:` | Restructuring without behavior change |
| `test:` | Adding tests |
| `chore:` | Maintenance, dependencies |

### 8.3 The Ban on Vague

* **Forbidden:** "updates", "wip", "fixed stuff"
* **Required:** Explain **What** changed and **Why**

---

## IsopGem Environment Commands

| Command | Purpose |
|---------|---------|
| `./run.sh` | Launch IsopGem |
| `./test.sh` | Run pytest |
| `./pip.sh install X` | Install packages |
| `source setup_env.sh` | Activate venv |

**Critical:** Never use bare `pip` or `python` — use `.venv/bin/python`

---

06_harmonia.md

# The Harmonia Protocol (Section 6.5: Purification Standards)

**"Tools serve the Temple; the Temple does not serve the tools."**

---

## The Philosophy

Static type checkers are **assistants for developer convenience**, not arbiters of correctness. Architecture defines correctness through:
- Boundary enforcement at entry points
- Clear contracts between components
- Runtime validation where it matters

The Harmonia ritual focuses on **real entropy**, not aesthetic purity demanded by static analyzers.

---

## The `/harmonia strict` Ritual

When invoked, Sophia shall purify the file by addressing these categories:

### **Category 1: Real Defects** (ALWAYS FIX)
- **Syntax Errors**: Code that won't parse
- **Undefined Names**: Variables, functions, classes that don't exist
- **Missing Imports**: References to unimported modules
- **Import Errors**: Typos in import statements (`reop.get()` vs `repo.get()`)

### **Category 2: Architectural Violations** (ALWAYS FIX)
- **UI Contamination**: UI files importing `sqlalchemy`, `pandas`, `requests`, `lxml`, `bs4`
- **Pillar Entanglement**: Direct imports between pillars (must use Signal Bus)
- **Thread Violations**: Heavy work (>100ms) on main thread without `QThreadPool`
- **Sovereignty Breaches**: Bypassing repositories to query database directly

### **Category 3: Clutter** (ALWAYS FIX)
- **Unused Imports**: Gray/unused imports that add noise
- **Dead Code**: Commented-out code blocks (Git remembers)
- **Import Ordering**: Should be StdLib → Third Party → Local, alphabetized

### **Category 4: Public API Documentation** (FIX WHEN MISSING)
- **Type Hints on Public Methods**: Functions/methods exposed to other modules
- **Docstrings on Public APIs**: Explain *intent* and contracts, not mechanics
- **Return Type Hints**: Especially for complex return types

### **Category 5: Critical Runtime Patterns** (FIX IF ABSENT)
- **Exception Logging**: Every `except` block must log (no silent failures)
- **Boundary Validation**: Entry points must validate inputs
- **Result Objects**: Prefer returning `Result[T]` over raising exceptions in services

---

## What Harmonia IGNORES

### **Cosmetic Type Warnings** (IGNORE)
- `reportUnknownVariableType`: "Type of X is partially unknown"
- `reportUnknownMemberType`: "Type of method is partially unknown"
- `reportUnknownArgumentType`: Lambda parameters in signal connections
- Generic warnings about `dict[Unknown, Unknown]` or `List[tuple[Unknown, ...]]`

**Reason**: These indicate Pyright's limitation in inferring types, not actual defects. The architecture guarantees correctness through boundary enforcement.

### **Redundant Guards** (IGNORE)
Pyright may demand:
```python
if value is None:
    return False
# ... use value ...
```

...when the entry point already validates `value`. **Do not add redundant guards to satisfy the type checker.**

### **Internal Implementation Details** (IGNORE)
- Type hints on private methods (`_helper`)
- Detailed annotations for local variables with obvious types
- Over-specification of internal data structures

### **Tool Limitations** (IGNORE)
- PyQt6 type stub incompleteness
- SQLAlchemy dynamic attributes
- Runtime-generated attributes that work in practice

---

## The Harmonia Report Format

After purification, report:

### ✅ **Fixed (Real Entropy)**
- List actual defects corrected
- Architectural violations healed
- Clutter removed

### 📝 **Enhanced (Documentation)**
- Public APIs that received type hints
- Missing docstrings added

### ⚠️ **Remaining (Acknowledged Noise)**
- Count of cosmetic warnings ignored
- Brief explanation: "Type inference limitations, architecture is sound"

### 🛡️ **Verified**
- No syntax errors
- No undefined names
- No architectural violations

---

## Configuration Alignment

### pyrightconfig.json
```json
{
  "executionEnvironments": [
    {
      "root": "src",
      "typeCheckingMode": "strict"
    },
    {
      "root": "src/pillars/*/ui",
      "typeCheckingMode": "off"
    }
  ]
}
```

**Rationale**:
- **Backend (strict)**: Catches typos, undefined variables early
- **UI (off)**: PyQt6 stubs incomplete; runtime validation sufficient

---

## Examples: What to Fix vs Ignore

### ✅ FIX: Unused Import
```python
from PyQt6.QtWidgets import QTextEdit, QComboBox  # Neither used
```
**Action**: Remove both imports.

### ✅ FIX: Missing Type Hint (Public API)
```python
def calculate(text):  # Public method, no hints
    return self.calculator.compute(text)
```
**Action**: Add `def calculate(text: str) -> int:`

### ❌ IGNORE: Partially Unknown Type (Internal)
```python
breakdown = self.calculator.get_breakdown(text)  # Pyright: "list[Unknown]"
for char, val in breakdown:
    rows.append([char, str(val)])  # Works fine at runtime
```
**Reason**: Boundary validated, architecture sound, no runtime impact.

### ❌ IGNORE: Lambda Type Inference
```python
action.triggered.connect(lambda checked, n=name: self._select(n))
# Pyright: "Type of parameter 'checked' is unknown"
```
**Reason**: Qt signal mechanism, works correctly, cosmetic warning.

### ✅ FIX: Architectural Violation
```python
# In ui/widget.py
from sqlalchemy.orm import Session  # UI should not import SQLAlchemy
```
**Action**: Move database logic to repository, pass data as DTO.

---

## The Harmonia Invocation

**Command**: `/harmonia strict <file_path>`

**Sophia's Workflow**:
1. Read the file
2. Run lightweight syntax check (grep for obvious issues)
3. Run `pyright` on the file
4. **Filter** the output through the Harmonia lens (fix real entropy, ignore noise)
5. Apply fixes using `multi_replace_string_in_file`
6. Report results in Harmonia format

**Key Principle**: Fix what matters. Ignore what doesn't. Trust the architecture.

---

## References

- **Philosophy**: `Docs/PYLANCE_AND_ARCHITECTURE.md`
- **Covenant**: `wiki/00_foundations/covenant/`
- **Configuration**: `pyrightconfig.json`, `.vscode/settings.json`

---

**Version**: 1.0.0 (2026-01-08)
**Authority**: The Magus & Sophia, aligned with architectural philosophy

---

Do not edit here. Update the canonical scrolls instead:
- Canonical source: `wiki/00_foundations/covenant/`
- VS Code mirror: `.github/instructions/covenant/`

Regenerate mirrors and these bundles with:
`.venv/bin/python scripts/covenant_scripts/sync_covenant.py`
