# ADR-013: Doctrine of Ports (Injected Architectural Boundaries)

**Status: Accepted**

**Date: 2026-01-13**

**Deciders: The Magus, Sophia**

**Technical Story:**
- Discovery during Simulacrum discipline implementation
- `ClockProvider` implemented as proof-of-concept in `CalculationService`
- Pattern proven through testing (6/6 tests passing with `FixedClock`)

---

## Context

### The Problem: Cosmic Dependencies

Services in IsopGem currently "reach outward" to access non-deterministic or boundary-crossing resources:

```python
# BEFORE: Cosmic Dependency (Impure)
from datetime import datetime
import uuid
import os
import requests

class MyService:
    def do_work(self):
        timestamp = datetime.now()        # Ask the cosmos for time
        id = str(uuid.uuid4())           # Ask the cosmos for randomness
        config = os.getenv("API_KEY")    # Ask the cosmos for config
        data = requests.get(url)         # Ask the cosmos for data
```

**Problems:**
1. **Non-Determinism**: Tests are unpredictable (time, UUIDs change)
2. **Hidden Dependencies**: No architectural visibility into what services need
3. **Testing Pain**: Requires patching (`mock.patch("module.datetime")`)
4. **Tight Coupling**: Services coupled to specific implementations
5. **No Seams**: Can't swap implementations (production vs. test vs. fake)

### The Discovery: Clock Injection

While implementing the Simulacrum discipline (proper mocking), we discovered that `datetime.now()` required patching in tests:

```python
# OLD TEST (Patching)
with mock.patch("pillars.gematria.services.calculation_service.datetime") as mock_dt:
    mock_dt.now.return_value = fixed_time
    service.update_calculation(...)
```

**We realized:** Time is not a cosmic inevitability—it's an **architectural boundary** that should be **injected**.

---

## Decision

**We adopt the Doctrine of Ports:**

> **"Any service that reaches outward to the cosmos (time, filesystem, network, environment, randomness) must do so through an injected port."**

This is **not a migration**. This is a **repeatable pattern** applied one seam at a time, with zero cascade risk.

### Non-Goals

This doctrine does not require ports for **pure computation**, **in-memory transformations**, or **domain logic**. It does not mandate abstraction where no cosmic dependency exists. It does not prohibit convenience imports in UI or adapter layers. Ports exist to manage **boundaries and non-determinism**, not to wrap every function in ceremony.

### Review Heuristic

**If a service uses `datetime`, `uuid`, `random`, `os`, `Path`, `requests`, or similar globals, reviewers should ask: "Is this a port?"**

---

## Architecture Pattern

### Two Classes of Ports

#### 1. **Determinism Providers**
Sources of non-deterministic values:
- **Time** (`datetime.now()`)
- **Identity** (`uuid.uuid4()`)
- **Randomness** (`random.randint()`)

#### 2. **Boundary Gateways**
External systems that cross architectural boundaries:
- **Filesystem** (`Path().read_text()`)
- **Network** (`requests.get()`)
- **Environment** (`os.getenv()`)
- **Subprocess** (`subprocess.run()`)

### The Pattern

```python
# 1. Define the Port (Protocol)
class ClockProvider(Protocol):
    def now(self) -> datetime: ...

# 2. Production Implementation (Real)
class SystemClock:
    def now(self) -> datetime:
        return datetime.now()

# 3. Test Implementation (Fake)
class FixedClock:
    def __init__(self, fixed_time: datetime):
        self._time = fixed_time
    
    def now(self) -> datetime:
        return self._time

# 4. Inject into Service
class MyService:
    def __init__(self, clock: ClockProvider = None):
        self.clock = clock or SystemClock()  # Default to production
    
    def do_work(self):
        timestamp = self.clock.now()  # Injected, not cosmic
```

---

## Implementation Plan

### Phase 1: Trinity of Determinism ✅ (High Leverage)

| Port | Status | Location | Impact |
|------|--------|----------|--------|
| **ClockProvider** | ✅ Implemented | `shared.services.time.clock_provider` | Used in `CalculationService` |
| **IdProvider** | 📋 Next | TBD | Record creation, filenames, correlation IDs |
| **RngProvider** | 📋 Future | TBD | When randomness is needed |

### Phase 2: Trinity of Boundaries (Medium Priority)

| Port | Status | Use Cases |
|------|--------|-----------|
| **ConfigProvider** | 📋 Future | Environment variables, secrets |
| **HttpClient** | 📋 Future | Etymology API, Sefaria, external services |
| **FileSystemProvider** | 📋 Future | Reading configs, writing exports |

---

## Consequences

### Positive

1. **Testability**
   - No patching required
   - Deterministic tests (same input = same output)
   - Fast (no I/O in unit tests)

2. **Clarity**
   - Dependencies are **explicit** (constructor signatures)
   - Architecture is **visible** (what does this service need?)
   - Boundaries are **enforced** (protocols define contracts)

3. **Flexibility**
   - Swap implementations (production, test, fake, spy)
   - Services become **pure transformations**
   - Refactoring is **safe** (protocol contracts enforced)

4. **Zero Cascade Risk**
   - Apply pattern one service at a time
   - Old code continues to work (sensible defaults)
   - No big-bang migration required

### Negative

1. **More Code Upfront**
   - Need to create Protocol + Production + Test implementations
   - Services require constructor injection

2. **Learning Curve**
   - Team needs to understand dependency injection
   - Must know when to apply pattern vs. direct usage

### Mitigations

1. **Sensible Defaults**
   ```python
   def __init__(self, clock: ClockProvider = None):
       self.clock = clock or get_system_clock()
   ```
   Services work out-of-the-box in production, explicit in tests.

2. **Documentation**
   - Covenant Section 8: Doctrine of Ports
   - Field notes in Simulacrum (Section 7)
   - ADR-013 (this document)

3. **Apply Just-In-Time**
   - Not a migration project
   - Apply when creating new services or refactoring existing ones
   - Let pain guide priority (hardest-to-test services first)

---

## Proof of Concept: ClockProvider

### Implementation

**Location:** `src/shared/services/time/clock_provider.py`

```python
class ClockProvider(Protocol):
    def now(self) -> datetime: ...

class SystemClock:
    def now(self) -> datetime:
        return datetime.now()

class FixedClock:
    def __init__(self, fixed_time: datetime):
        self._time = fixed_time
    
    def now(self) -> datetime:
        return self._time
```

### Service Integration

**Before:**
```python
from datetime import datetime

class CalculationService:
    def update_calculation(self, record_id, notes):
        record.date_modified = datetime.now()  # Cosmic
```

**After:**
```python
from shared.services.time import ClockProvider, get_system_clock

class CalculationService:
    def __init__(self, repository=None, clock: ClockProvider = None):
        self.repository = repository or CalculationRepository()
        self.clock = clock or get_system_clock()
    
    def update_calculation(self, record_id, notes):
        record.date_modified = self.clock.now()  # Injected
```

### Test Results

**Before:**
```python
# Patching required
with mock.patch("pillars.gematria.services.calculation_service.datetime") as mock_dt:
    mock_dt.now.return_value = fixed_time
    service.update_calculation(...)
```

**After:**
```python
# Injection, no patching
clock = FixedClock(datetime(2023, 1, 1))
service = CalculationService(repository=mock_repo, clock=clock)
result = service.update_calculation(...)
assert result.date_modified == datetime(2023, 1, 1)  # Exact assertion
```

**Test Suite:** `tests/pillars/gematria/test_calculation_service_simulacrum.py`
- ✅ 6/6 tests passing
- ✅ No patching required
- ✅ Deterministic time assertions

---

## References

### Architectural Patterns
- **Hexagonal Architecture** (Ports & Adapters) - Alistair Cockburn
- **Functional Core, Imperative Shell** - Gary Bernhardt
- **Dependency Injection** - Martin Fowler

### IsopGem Documentation
- **Covenant Section 7**: Discipline of the Simulacrum (The 12 Rules of Mocking)
- **Covenant Section 8**: Doctrine of Ports (This pattern)
- **ADR-013**: This document

### Implementation Examples
- `src/shared/services/time/clock_provider.py`
- `src/pillars/gematria/services/calculation_service.py`
- `tests/pillars/gematria/test_calculation_service_simulacrum.py`

---

## Approval

**Approved By:** The Magus, Sophia  
**Date:** 2026-01-13  
**Implementation Begin:** Phase 1 (ClockProvider) ✅ Complete  
**Next Action:** IdProvider (as needed)

---

**Versioning:**
- **1.0.0** (2026-01-13): Initial ADR - ClockProvider proven, pattern established
