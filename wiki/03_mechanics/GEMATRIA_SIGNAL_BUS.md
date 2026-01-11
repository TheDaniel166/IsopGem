# The Gematria Signal Bus Protocol

**Date:** 2026-01-10  
**Status:** 🟢 Active  
**Covenant Reference:** Section 2 (Doctrine of Spheres)

---

## Purpose

The **Gematria Signal Bus** enables any pillar to request Gematria calculations **without** directly importing the Gematria pillar or calculator classes. This preserves **Pillar Sovereignty** as mandated by The Covenant.

---

## Architecture

```
┌──────────────────┐          ┌──────────────────┐
│  Correspondence  │          │    Gematria      │
│     Pillar       │          │     Pillar       │
│                  │          │                  │
│  formula_engine  │          │  gematria_service│
│       ↓          │          │       ↑          │
│  gematria_bus    │◄────────►│  gematria_bus    │
│  .request()      │  Signal  │  .subscribe()    │
└──────────────────┘          └──────────────────┘
         ↓                             ↑
         └─────────────────────────────┘
              shared/signals/gematria_bus.py
```

**Key Principle:** The Signal Bus is the **ONLY** communication channel between pillars.

---

## Signal Definitions

### 1. `calculation_requested`
**Signature:** `pyqtSignal(str, str)`  
**Args:** `(text: str, cipher: str)`  
**Purpose:** Request a Gematria calculation

**Emitter:** Any pillar (e.g., Correspondence, Document Manager)  
**Subscriber:** Gematria pillar (service layer)

### 2. `calculation_completed`
**Signature:** `pyqtSignal(str, str, object)`  
**Args:** `(text: str, cipher: str, result: Any)`  
**Purpose:** Return calculation result

**Emitter:** Gematria pillar  
**Subscriber:** Requesting pillar (handled automatically by `request_calculation()`)

### 3. `cipher_list_requested`
**Signature:** `pyqtSignal()`  
**Purpose:** Request list of available ciphers

**Emitter:** Any pillar  
**Subscriber:** Gematria pillar

### 4. `cipher_list_completed`
**Signature:** `pyqtSignal(list)`  
**Args:** `(cipher_names: List[str])`  
**Purpose:** Return list of available cipher names

**Emitter:** Gematria pillar  
**Subscriber:** Requesting pillar

---

## Usage Examples

### Requesting a Calculation (Synchronous)

```python
from shared.signals import gematria_bus

# Simple calculation (blocks until result or timeout)
result = gematria_bus.request_calculation("Hello World", "English (TQ)")
# Returns: 153 (or "#CIPHER?" if cipher unknown, "#TIMEOUT!" if no response)
```

### Requesting a Calculation (Asynchronous)

```python
from shared.signals import gematria_bus

def handle_result(text, cipher, result):
    print(f"Gematria of '{text}' using {cipher}: {result}")

# Connect to response signal
gematria_bus.calculation_completed.connect(handle_result)

# Emit request
gematria_bus.calculation_requested.emit("Hello World", "English (TQ)")
```

### Listing Available Ciphers

```python
from shared.signals import gematria_bus

ciphers = gematria_bus.request_cipher_list()
# Returns: ["English (TQ)", "Hebrew Gematria", "Greek Isopsephy", ...]
```

---

## Implementation Requirements

### For Requesting Pillars (e.g., Correspondences)

1. Import `gematria_bus` from `shared.signals`
2. Call `gematria_bus.request_calculation(text, cipher)`
3. Handle return values:
   - `int`: Successful calculation
   - `str` starting with `#`: Error code

**DO NOT:**
- Import calculator classes directly
- Import from `pillars.gematria.*`
- Import from `shared.services.gematria.*` (domain logic doesn't belong in shared)

### For Providing Pillar (Gematria)

The Gematria pillar **MUST** implement a signal handler service:

**File:** `pillars/gematria/services/gematria_signal_handler.py`

```python
from PyQt6.QtCore import QObject
from shared.signals import gematria_bus
from typing import Dict
from shared.services.gematria.base_calculator import GematriaCalculator
# ... import all calculator classes

class GematriaSignalHandler(QObject):
    """Handles Gematria calculation requests from other pillars via Signal Bus."""
    
    def __init__(self):
        super().__init__()
        self._registry: Dict[str, GematriaCalculator] = self._build_registry()
        
        # Subscribe to signals
        gematria_bus.calculation_requested.connect(self._handle_calculation)
        gematria_bus.cipher_list_requested.connect(self._handle_cipher_list)
    
    def _build_registry(self) -> Dict[str, GematriaCalculator]:
        """Build calculator registry."""
        calculators = [
            HebrewGematriaCalculator(),
            GreekGematriaCalculator(),
            TQGematriaCalculator(),
            # ... all calculators
        ]
        return {c.name.upper(): c for c in calculators}
    
    def _handle_calculation(self, text: str, cipher: str):
        """Handle calculation request and emit result."""
        cipher_key = cipher.upper()
        calculator = self._registry.get(cipher_key)
        
        if not calculator:
            result = f"#CIPHER? ({cipher})"
        else:
            try:
                result = calculator.calculate(text)
            except Exception as e:
                result = "#ERROR!"
        
        gematria_bus.calculation_completed.emit(text, cipher, result)
    
    def _handle_cipher_list(self):
        """Handle cipher list request and emit result."""
        cipher_names = [c.name for c in self._registry.values()]
        gematria_bus.cipher_list_completed.emit(cipher_names)
```

**Initialization:** The handler must be initialized when the application starts:

```python
# In main.py or wherever pillars are initialized
from pillars.gematria.services.gematria_signal_handler import GematriaSignalHandler

# Keep reference to prevent garbage collection
gematria_handler = GematriaSignalHandler()
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| `#CIPHER?` | Unknown cipher name |
| `#ERROR!` | Calculation failed (exception) |
| `#TIMEOUT!` | No response within timeout period |

---

## Testing

### Unit Test (No Gematria Pillar)

```python
def test_gematria_formula_without_handler():
    """Test that formula doesn't crash when handler is unavailable."""
    from shared.signals import gematria_bus
    
    result = gematria_bus.request_calculation("Test", "English (TQ)", timeout_ms=100)
    assert result == "#TIMEOUT!"  # No handler connected
```

### Integration Test (With Gematria Pillar)

```python
def test_gematria_formula_with_handler():
    """Test that formula works with handler connected."""
    from pillars.gematria.services.gematria_signal_handler import GematriaSignalHandler
    handler = GematriaSignalHandler()
    
    result = gematria_bus.request_calculation("Hello", "English (TQ)")
    assert isinstance(result, int)
    assert result > 0
```

---

## Migration Checklist

- [x] Create `shared/signals/gematria_bus.py`
- [x] Update `shared/signals/__init__.py` to export `gematria_bus`
- [x] Refactor `formula_engine.py` to use `gematria_bus.request_calculation()`
- [x] Remove direct imports from `shared.services.gematria` in `formula_engine.py`
- [ ] Create `pillars/gematria/services/gematria_signal_handler.py`
- [ ] Initialize handler in application startup
- [ ] Test spreadsheet formulas with Gematria calculations
- [ ] Update Formula Wizard to use `gematria_bus.request_cipher_list()`

---

## Covenant Compliance

✅ **Section 2 (Doctrine of Spheres):** Pillars communicate via Signal Bus, not direct imports  
✅ **Section 4 (Purity):** Service layer (`formula_engine`) is decoupled from domain logic  
✅ **Section 5 (Shield):** Errors are caught and returned as error codes, not exceptions  

**"The Signal is the Bridge. The Pillar is Sovereign."**
