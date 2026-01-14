# The Doctrine of Ports (Architectural Boundaries)

**"The Temple controls its reality; reality does not impose upon the Temple."**

---

## The Principle

Any service that **reaches outward** to the cosmos (time, filesystem, network, environment, randomness) must do so through an **injected port**.

This is not a migration. This is a **repeatable pattern** applied one seam at a time, with zero cascade risk.

---

## Non-Goals

This doctrine does not require ports for **pure computation**, **in-memory transformations**, or **domain logic**. It does not mandate abstraction where no cosmic dependency exists. It does not prohibit convenience imports in UI or adapter layers. Ports exist to manage **boundaries and non-determinism**, not to wrap every function in ceremony.

### Review Heuristic

**If a service uses `datetime`, `uuid`, `random`, `os`, `Path`, `requests`, or similar globals, reviewers should ask: "Is this a port?"**

---

## Two Classes of Outward

### 1. **Determinism Providers**
Sources of non-deterministic values that make testing unpredictable:
- Time (`datetime.now()`)
- Identity (`uuid.uuid4()`)
- Randomness (`random.randint()`)

### 2. **Boundary Gateways**
External systems that cross architectural boundaries:
- Filesystem (`Path().read_text()`)
- Network (`requests.get()`)
- Environment (`os.getenv()`)
- Subprocess (`subprocess.run()`)
- Database sessions (handled via Repository pattern)

---

## The Trinity of Determinism

### A) ClockProvider ✅ (Implemented)

**Rule**: If a service calls `datetime.now()`, that service is impure.

```python
from shared.services.time import ClockProvider, SystemClock, FixedClock

class MyService:
    def __init__(self, clock: ClockProvider = None):
        self.clock = clock or SystemClock()
    
    def do_work(self):
        timestamp = self.clock.now()
```

**Test**:
```python
clock = FixedClock(datetime(2023, 1, 1))
service = MyService(clock=clock)
```

---

### B) IdProvider (Pending)

**Rule**: If a service calls `uuid.uuid4()`, that service is impure.

**Port**:
```python
class IdProvider(Protocol):
    def generate_id(self) -> str:
        """Generate a unique identifier."""
        ...

class UuidProvider:
    """Production: Generate UUIDs."""
    def generate_id(self) -> str:
        return str(uuid.uuid4())

class SequentialIdProvider:
    """Test: Generate deterministic sequential IDs."""
    def __init__(self):
        self._counter = 0
    
    def generate_id(self) -> str:
        self._counter += 1
        return f"test-id-{self._counter}"
```

**Benefit**: Deterministic IDs in tests. Assert exact values, not "is not None".

---

### C) RngProvider (Pending)

**Rule**: If a service calls `random.randint()` or `random.choice()`, that service is impure.

**Port**:
```python
class RngProvider(Protocol):
    def randint(self, a: int, b: int) -> int: ...
    def choice(self, seq: list) -> any: ...

class SystemRng:
    """Production: Use system random."""
    def randint(self, a: int, b: int) -> int:
        return random.randint(a, b)

class FixedRng:
    """Test: Return predetermined values."""
    def __init__(self, sequence: list):
        self._sequence = sequence
        self._index = 0
    
    def randint(self, a: int, b: int) -> int:
        val = self._sequence[self._index % len(self._sequence)]
        self._index += 1
        return val
```

**Benefit**: Tests can assert exact behavior when randomness is involved.

---

## The Trinity of Boundaries

### D) ConfigProvider (Pending)

**Rule**: Services must not call `os.getenv()`, read `.env`, or reach into global settings.

**Port**:
```python
class ConfigProvider(Protocol):
    def get(self, key: str, default: str = "") -> str: ...
    def get_int(self, key: str, default: int = 0) -> int: ...
    def get_bool(self, key: str, default: bool = False) -> bool: ...

class EnvironmentConfig:
    """Production: Read from environment."""
    def get(self, key: str, default: str = "") -> str:
        return os.getenv(key, default)

class DictConfig:
    """Test: Use in-memory dict."""
    def __init__(self, config: dict[str, str]):
        self._config = config
    
    def get(self, key: str, default: str = "") -> str:
        return self._config.get(key, default)
```

**Benefit**: No environment pollution in tests. Security: only one place touches env.

---

### E) HttpClient (Pending)

**Rule**: Never call `requests` from services. Ever.

**Port**:
```python
class HttpClient(Protocol):
    def get(self, url: str, params: dict = None, headers: dict = None, timeout: int = 30) -> Response: ...
    def post(self, url: str, data: any = None, json: dict = None) -> Response: ...

class RequestsClient:
    """Production: Use requests library."""
    def get(self, url: str, **kwargs) -> Response:
        return requests.get(url, **kwargs)

class FakeHttpClient:
    """Test: Return canned responses."""
    def __init__(self, responses: dict[str, str]):
        self._responses = responses
    
    def get(self, url: str, **kwargs) -> Response:
        return FakeResponse(self._responses.get(url, ""))
```

**Better**: Often better to wrap in domain-specific clients (`EtymologyApi`, `SefariaClient`).

**Benefit**: No network calls in tests. Complete control over responses.

---

### F) FileSystemProvider (Pending)

**Rule**: Any `Path()`, `open()`, `glob()`, `mkdir()` inside services is boundary leakage.

**Port**:
```python
class FileSystemProvider(Protocol):
    def read_text(self, path: str) -> str: ...
    def write_text(self, path: str, content: str) -> None: ...
    def exists(self, path: str) -> bool: ...
    def list_dir(self, path: str) -> list[str]: ...

class RealFileSystem:
    """Production: Use real filesystem."""
    def read_text(self, path: str) -> str:
        return Path(path).read_text()

class InMemoryFileSystem:
    """Test: Use in-memory dict."""
    def __init__(self):
        self._files: dict[str, str] = {}
    
    def read_text(self, path: str) -> str:
        if path not in self._files:
            raise FileNotFoundError(path)
        return self._files[path]
```

**Benefit**: No temp files in tests. Complete isolation. Fast.

---

## The Protocol

### When to Apply

**Apply this pattern when:**
1. A new service is created that needs any of these dependencies
2. An existing service is being refactored or tested
3. A cosmic dependency is causing test pain

**Do not apply:**
- As a big-bang migration across the entire codebase
- To code that's stable and not under active development
- When the service is already properly architected

### How to Apply

1. **Identify the cosmic dependency** (e.g., `datetime.now()`, `uuid.uuid4()`, `os.getenv()`)
2. **Create the port** (if it doesn't exist) in `shared/services/<domain>/`
3. **Inject the port** into the service constructor with a sensible default
4. **Replace the cosmic call** with the port method call
5. **Test with the fake** implementation

### Migration Safety

This pattern has **zero cascade risk** because:
- New code uses the port from day one
- Old code continues to work (default implementations are production-ready)
- Refactoring happens one service at a time
- Tests prove correctness at each step

---

## Current Status

| Port | Status | Location | Notes |
|------|--------|----------|-------|
| **ClockProvider** | ✅ Implemented | `shared.services.time.clock_provider` | Used in `CalculationService` |
| **IdProvider** | 📋 Pending | TBD | High leverage, easy win |
| **RngProvider** | 📋 Pending | TBD | Apply when randomness is needed |
| **ConfigProvider** | 📋 Pending | TBD | Centralizes env access |
| **HttpClient** | 📋 Pending | TBD | Needed for etymology, Sefaria APIs |
| **FileSystemProvider** | 📋 Pending | TBD | Apply when FS I/O is added/refactored |

---

## References

- **Hexagonal Architecture** (Ports & Adapters): Alistair Cockburn
- **Functional Core, Imperative Shell**: Gary Bernhardt
- **Dependency Injection**: Martin Fowler

---

**Version**: 1.0.0 (2026-01-13)
**Authority**: The Magus & Sophia, aligned with the Simulacrum discipline
