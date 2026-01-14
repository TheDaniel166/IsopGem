# The Law of the Shared Substrate

**"Shared" is not a dumping ground. It is sacred infrastructure.**

---

## Admission Criteria

A module belongs in `shared/` **if and only if** it meets ONE of these criteria **AND is not domain logic**:

### 1. **Cross-Pillar Infrastructure Port**
The module is a **port/adapter/contract** that abstracts infrastructure or cosmic dependencies.

**Examples:**
- ✅ `shared.services.time.ClockProvider` (Time boundary)
- ✅ `shared.contracts.calculator.GematriaCalculator` (Protocol/Interface only)
- ❌ `shared.services.gematria.hebrew_calculator` (Domain algorithm, even if used by 2+ pillars)

**Critical Distinction:** 
- **Contracts/Protocols** → Shared (defines "what")
- **Implementations** → Pillar (defines "how")

---

### 2. **Core Application Infrastructure**
The module is **essential for the application to function**, regardless of which pillars are installed.

**Examples:**
- ✅ `shared.database` (SQLAlchemy setup)
- ✅ `shared.config` (Path resolution)
- ✅ `shared.signals.navigation_bus` (Inter-pillar communication)
- ❌ Domain-specific business logic (belongs in pillar)

---

### 3. **Pure, Domain-Agnostic Utilities**
The module contains **zero domain semantics**—pure mathematical or string operations.

**Examples:**
- ✅ `shared.utils.math.phi()` (Mathematical constant)
- ✅ `shared.utils.text.normalize_unicode()` (Pure transformation)
- ❌ `shared.utils.gematria_normalize()` (Domain-specific logic)

**Test:** If the utility name contains a domain term (gematria, astrology, etc.), it's domain logic.

---

### 4. **Shared Data Contracts (DTOs / Events / Schemas)**
If two pillars must exchange structured data, the **shape** of that data belongs in `shared/`, even if the logic does not.

**Examples:**
- ✅ `shared.contracts.events.WindowRequestEvent` (Navigation bus payload)
- ✅ `shared.models.User` (If truly global, used by auth + multiple pillars)
- ✅ `shared.enums.WindowKey` (Registry identifiers)
- ❌ `shared.dto.GematriaResult` (Domain-specific DTO, unless multiple pillars need it)

**Rationale:** Keeps `shared.signals.navigation_bus` clean—the bus and its message types don't get split across pillars.

**Critical Test:** Does this define the **vocabulary of communication**, or does it implement **domain behavior**?
- **Vocabulary** → Shared (e.g., `@dataclass WindowRequest`)
- **Behavior** → Pillar (e.g., `GematriaCalculationService`)

---

## What Does NOT Belong in Shared

### ❌ **Single-Pillar Utilities**
If only one pillar uses it, it belongs in that pillar.

**Anti-example:**
```python
# shared/services/gematria/arabic_calculator.py
# ❌ If ONLY gematria pillar uses it
```

**Correct:**
```python
# pillars/gematria/calculators/arabic_calculator.py
# ✅ Domain logic in the domain
```

---

### ❌ **Domain-Specific Business Logic**
Even if "pure" or "reusable", domain logic belongs in the domain.

**Anti-example:**
```python
# shared/services/gematria/text_analysis.py
# ❌ This is gematria domain logic
```

**Correct:**
```python
# pillars/gematria/services/text_analysis_service.py
# ✅ Business logic in pillar
```

---

### ❌ **Premature Abstraction**
Do not move to `shared/` "just in case" another pillar might use it.

**Rule**: Move to `shared/` when the **second pillar** needs it, not before.

---

## Shared Contracts: The Clean Pattern

**Recommended Structure:**
```
shared/
├── contracts/              # Data contracts for inter-pillar communication
│   ├── events.py          # Navigation bus event payloads
│   ├── gematria.py        # GematriaCalculator protocol (interface only)
│   └── enums.py           # Shared enumerations
│
├── models/                # Global domain models (rare)
│   └── user.py            # If truly needed by 3+ pillars
│
├── services/              # Infrastructure services only
│   ├── time/              # ClockProvider (Port)
│   └── http/              # HttpClient (Port, when implemented)
│
└── ui/                    # UI infrastructure
    ├── theme.py           # Visual tokens
    └── kinetic_enforcer.py # Global event filters
```

**Key Insight:**
- `shared/contracts/` = **What** (schemas, protocols, enums)
- `pillars/*/` = **How** (implementations, algorithms, business logic)

---

## The Justification Header (Mandatory)

**Every module in `shared/` MUST begin with a justification header:**

```python
"""
Module description here.

SHARED JUSTIFICATION:
- RATIONALE: [Core Infrastructure | Port | Contract | Pure Utility]
- USED BY: [Pillar names, comma-separated]
- CRITERION: [1-4 from Law of Substrate]
"""
```

### Examples

**Example 1: Core Infrastructure**
```python
"""
Database session management and connection pooling.

SHARED JUSTIFICATION:
- RATIONALE: Core Infrastructure
- USED BY: All pillars
- CRITERION: 2 (Essential for app to function)
"""
```

**Example 2: Port/Boundary**
```python
"""
Clock provider for deterministic time in tests.

SHARED JUSTIFICATION:
- RATIONALE: Port (Time boundary abstraction)
- USED BY: Gematria, Lexicon
- CRITERION: 1 (Cross-pillar infrastructure port)
"""
```

**Example 3: Data Contract**
```python
"""
Navigation bus event payloads.

SHARED JUSTIFICATION:
- RATIONALE: Contract (Event schemas for inter-pillar communication)
- USED BY: All pillars
- CRITERION: 4 (Shared data contracts)
"""
```

**Example 4: Pure Utility**
```python
"""
Mathematical constants (phi, pi, e).

SHARED JUSTIFICATION:
- RATIONALE: Pure Utility (Domain-agnostic math)
- USED BY: Geometry, Astrology, Sacred patterns
- CRITERION: 3 (Pure, domain-agnostic utility)
"""
```

---

## Enforcement

### Automated Header Audit

Run this script quarterly (or in CI):

```python
#!/usr/bin/env python3
"""Audit shared/ for missing or invalid justification headers."""
import re
from pathlib import Path

SHARED_DIR = Path("src/shared")
HEADER_PATTERN = r"SHARED JUSTIFICATION:"

def audit_shared():
    violations = []
    
    for py_file in SHARED_DIR.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue  # Exempt __init__.py
        
        content = py_file.read_text()
        
        # Check header exists
        if "SHARED JUSTIFICATION:" not in content:
            violations.append({
                "file": str(py_file),
                "error": "Missing SHARED JUSTIFICATION header"
            })
            continue
        
        # Extract header
        match = re.search(r"SHARED JUSTIFICATION:(.*?)\"\"\"", content, re.DOTALL)
        if not match:
            violations.append({
                "file": str(py_file),
                "error": "Malformed SHARED JUSTIFICATION header"
            })
            continue
        
        header = match.group(1)
        
        # Verify required fields
        if "RATIONALE:" not in header:
            violations.append({
                "file": str(py_file),
                "error": "Missing RATIONALE field"
            })
        if "USED BY:" not in header:
            violations.append({
                "file": str(py_file),
                "error": "Missing USED BY field"
            })
        if "CRITERION:" not in header:
            violations.append({
                "file": str(py_file),
                "error": "Missing CRITERION field"
            })
    
    return violations

if __name__ == "__main__":
    violations = audit_shared()
    if violations:
        print(f"❌ Found {len(violations)} violations:\n")
        for v in violations:
            print(f"  {v['file']}")
            print(f"    → {v['error']}\n")
        exit(1)
    else:
        print("✅ All shared modules have valid justification headers")
```

### Usage Verification

After header audit, verify claimed usage:

```bash
# For each module claiming "USED BY: Gematria, Lexicon"
# Verify actual imports match

grep -r "from shared.X" src/pillars/gematria/
grep -r "from shared.X" src/pillars/lexicon/
```

If claimed pillars don't import it → Violation.

---

## Current Audit Findings (2026-01-13)

| Module | Pillars Using | Contains | Verdict | Action |
|--------|---------------|----------|---------|--------|
| `shared.ui.theme` | ALL | Infrastructure | ✅ Valid | Keep |
| `shared.database` | ALL | Infrastructure | ✅ Valid | Keep |
| `shared.services.time` | Gematria | Port/Boundary | ✅ Valid | Keep as Port pattern |
| `shared.services.gematria.*` | Gematria, Lexicon | **Domain logic** | ⚠️ **DANGER ZONE** | See refactoring plan below |

---

## The Danger Zone: `shared.services.gematria.*`

**Current State:**
```python
# shared/services/gematria/
├── base_calculator.py          # Protocol (valid)
├── hebrew_calculator.py        # Implementation (INVALID)
├── greek_calculator.py         # Implementation (INVALID)
├── arabic_calculator.py        # Implementation (INVALID)
├── tq_calculator.py            # Implementation (INVALID)
└── multi_language_calculator.py  # Implementation (INVALID)
```

**Problem:** These are **domain algorithms**, not infrastructure ports. Even though used by 2 pillars (Gematria + Lexicon), they are **gematria-specific logic** that doesn't belong in `shared/`.

**Why it's dangerous:**
- Sets precedent: "If 2 pillars use it, dump in shared"
- Blurs the line between infrastructure and domain
- Invites other domains to add `shared.services.astrology.*`, `shared.services.tarot.*`, etc.

---

## Refactoring Plan: Contracts vs. Implementations

**Step 1: Extract the Contract (Protocol)**
```python
# shared/contracts/gematria.py  (NEW)
from typing import Protocol

class GematriaCalculator(Protocol):
    """Contract for gematria calculation algorithms."""
    name: str
    
    def calculate(self, text: str) -> int: ...
    def get_breakdown(self, text: str) -> list: ...
    def normalize_text(self, text: str) -> str: ...
```

**Step 2: Move Implementations to Gematria Pillar**
```python
# pillars/gematria/calculators/
├── hebrew.py
├── greek.py
├── arabic.py
├── tq.py
└── multi_language.py
```

**Step 3: Handle Cross-Pillar Access**

**Option A:** Lexicon imports from Gematria (Acceptable for "Library Pillars")
```python
# pillars/lexicon/services/holy_key_service.py
from pillars.gematria.calculators.tq import TQGematriaCalculator
```

**Option B:** Dependency Injection (Preferred)
```python
# pillars/lexicon/services/holy_key_service.py
from shared.contracts.gematria import GematriaCalculator

class HolyKeyService:
    def __init__(self, calculator: GematriaCalculator):
        self.calculator = calculator  # Injected, not imported
```

**Option C:** Create a `gematria-core` package (Nuclear Option)
- Extract calculators to separate package
- Both pillars depend on it
- Only if this becomes a true shared library across multiple projects

---

## Migration Timeline

**Phase 1: Assess Pain** (Week 1)
- Count import statements across codebase
- Estimate refactoring complexity
- Decide if worth the disruption

**Phase 2: Create Contract** (Week 2)
```bash
# Create shared/contracts/gematria.py
# Extract GematriaCalculator protocol
```

**Phase 3: Move Implementations** (Week 3)
```bash
# Move calculators to pillars/gematria/calculators/
# Update all imports in gematria pillar
```

**Phase 4: Fix Lexicon** (Week 4)
```bash
# Update lexicon imports
# Choose: Direct import vs. injection
```

**Phase 5: Delete Danger Zone** (Week 5)
```bash
# Remove shared/services/gematria/
# Verify no broken imports
```

---

## Decision: Defer or Refactor?

**Arguments for Refactoring NOW:**
- Prevents bad precedent
- Clarifies architecture
- Demonstrates commitment to the Law

**Arguments for Deferring:**
- Low pain currently
- "If it ain't broke..."
- Other priorities

**Recommendation:** 
- **Immediate:** Document as violation, add to tech debt log
- **Next Refactor Window:** Apply when touching this code anyway
- **Guideline:** No NEW domain logic in `shared/`, existing gets grandfathered but monitored

---

## The Principle

> **Shared is for bridges, not buildings. Buildings belong in pillars.**

---

**Version**: 1.0.0 (2026-01-13)
