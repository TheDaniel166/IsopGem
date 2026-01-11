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
