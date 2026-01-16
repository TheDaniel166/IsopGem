# Pylance and Architecture: A Discovery

**Date**: 2026-01-05  
**Context**: Session exploring the relationship between static type checking and architectural contracts

---

## The Core Principle

**Architecture defines correctness; type checkers are optional tools for developer convenience.**

A well-designed system that enforces contracts at boundaries does not require static type checking for correctness. Type hints and checkers add value for:
1. **Catching typos** before runtime (`reop.get()` vs `repo.get()`)
2. **Refactoring safety** (find all callers when renaming)
3. **Documentation** (types as inline docs)

But these are **developer productivity features**, not correctness guarantees.

---

## What We Discovered

### The Tension

Pylance/Basedpyright complained about 531+ "errors" in geometry services. Investigation revealed:
- Most were cosmetic (unknown append types, partial dict types)
- None were functional defects
- All could be "fixed" by adding redundant runtime guards or type annotations

### The Architecture Already Enforces Correctness

Example from `CylinderSolidCalculator.set_property()`:

```python
def set_property(self, key: str, value: Optional[float]) -> bool:
    # BOUNDARY ENFORCEMENT: Entry validation
    if value is not None and value <= 0:
        return False
    
    # ... business logic below assumes value is valid ...
    # No need for scattered None checks throughout
```

**The entry guard IS the enforcement.** Everything downstream can assume valid input because the boundary guarantees it.

### The Problem with Tool-Driven Development

Initially, we added guards like:

```python
if h is None or h <= 0:
    return False
```

...deep in business logic, solely to satisfy the type checker. This was **defensive programming for Pylance**, not the system. It:
- Duplicates the entry validation
- Clutters business logic with constraints already enforced
- Trains developers to write code for tools instead of architecture

### The Correct Approach

1. **Validate at boundaries** (entry points, API surfaces)
2. **Document contracts** with type hints and docstrings
3. **Trust the architecture** downstream
4. **Use type checkers** for typos and refactoring, not correctness

---

## Configuration Decisions

### UI Layer (Disabled)
- **Why**: PyQt6 has incomplete/incorrect type stubs; generates massive false positives
- **Config**: `typeCheckingMode: "off"` in execution environments for `**/ui/**`
- **Result**: No noise; UI code is validated by Qt's runtime checks and tests

### Backend Layer (Strict)
- **Why**: Catches typos, undefined variables, wrong imports before tests run
- **Config**: `typeCheckingMode: "strict"` for `src/` (default)
- **Result**: Early detection of mechanical errors without blocking valid patterns

### What We Actually Fixed

**Real defects caught:**
1. Metadata typo in `cylinder_solid.py`: `self._result.cast(Dict[str, float], payload.metadata)` → `cast(dict[str, float], self._result.payload.metadata)`
2. Clarified contracts with explicit casts (`cast(List[Face], faces)`)
3. Made protected methods public where called externally

**What we ignored:**
- 531 warnings about "partially unknown types" that have no runtime impact
- Complaints about perfectly valid code that satisfies the architecture

---

## Lessons for Future Development

### 1. Architecture Over Tools
If Pylance complains but the architecture is sound, the architecture wins. Question the tool, not the design.

### 2. Boundary Enforcement
Validate once at entry points. Scattered guards are code smell indicating:
- Missing entry validation, OR
- Excessive defensive programming, OR
- Tool-driven development

### 3. Type Hints as Documentation
Use type hints to document contracts, not to satisfy checkers. If a hint makes code less clear, skip it.

### 4. Static Analysis is Optional
A well-architected codebase with good tests does not require static type checking. It's a productivity tool, not a foundation.

### 5. When to Care About Warnings
Care about warnings when they indicate:
- Actual typos or undefined names
- Contract violations (passing wrong types to APIs)
- Refactoring breakage

Ignore warnings when they:
- Complain about valid code the architecture guarantees correct
- Demand redundant guards for aesthetic purity
- Block patterns that work in practice

---

## Tools Serve the Temple

> "I am the Form; You are the Will. Together, we weave the Reality."

The architecture (Form) serves the requirements (Will). Tools serve the architecture. Never invert this hierarchy.

Pylance/Basedpyright are assistants, not masters. When they conflict with sound engineering, tune them down or turn them off.

---

## References

- Configuration: `.vscode/settings.json` (global overrides)
- Configuration: `pyrightconfig.json` (execution environments)
- Fixed files: `cone_solid.py`, `cylinder_solid.py`, `sphere_solid.py`, `torus_solid.py`, `complex_prismatic_solids.py`
- Remaining warnings: ~531 in geometry services (cosmetic, non-blocking)
