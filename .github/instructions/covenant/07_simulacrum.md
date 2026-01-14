# The Discipline of the Simulacrum (Proper Mocking)

**"A proper mock preserves reality while isolating responsibility."**

---

## The Philosophy

A mock is a *Simulacrum*—a representation of reality, not reality itself.
Good mocks enforce architectural boundaries; bad mocks conceal design failures.
Sprinkling `MagicMock` everywhere creates a "Potemkin Village"—a facade that collapses under the weight of interaction.

---

## 1. Mock Boundaries, Not Behavior

You mock **what you do not own** or **what crosses a boundary**.

- **Do Not Mock**: Pure functions, Value objects, Internal helpers you wrote.
- **Do Mock**: File I/O, Databases, Network calls, Time, OS/Environment, External libraries, Heavy subsystems.

*If you mock five things inside one function, the function is too large.*

## 2. Use `unittest.mock` Surgically

The standard library is sufficient. Avoid `MagicMock` unless protocol magic (`__enter__`, `__iter__`) is required.

## 3. Mock at the Import Location

Mock **where the dependency is used**, not where it is defined.

- ❌ `patch("requests.get")`
- ✅ `patch("your_module.requests.get")`

## 4. Prefer Dependency Injection Over Patching

Pass capabilities (repositories, clocks) as arguments. This produces cleaner architecture and simpler tests.
Refactoring to injection eliminates the need for complex patching and globals.

## 5. Use Spec or Autospec Aggressively

Mocks without specs lie. Use `spec=Class` or `autospec=True` to catch typos and interface drift.
Failure to do so creates tests that pass against imaginary APIs.

## 6. One Assertion of Effect, One of Interaction

Avoid brittle tests. Assert the *outcome* (Effect) and possibly *one* key side effect (Interaction), not the entire implementation detail.

## 7. Freeze the River of Time

Use deterministic control for Time, UUIDs, and Randomness. Inject a clock or patch `datetime`.

## 8. Fakes for Logic, Mocks for Interaction

- **Mock**: Use when testing *Interaction* (Did we call the database?).
- **Fake**: Use when testing *Logic* (Does the system behave correctly with state?). A `FakeRepo` (using a dict) is superior to a complex Mock for logic tests.

## 9. Never Mock What You Assert On

This is a cardinal sin. If you mock the object you are testing, you are testing nothing but your own imagination.

## 10. Folder Structure That Scales

- `tests/unit/`: Mock boundaries. Fast.
- `tests/integration/`: Real adapters (sqlite, temp files). Thorough.

## 11. Pytest + Fixtures = Sanity

Use fixtures (`@pytest.fixture`) to reduce duplication and improve clarity.

## 12. Listen to the Pain

Mock pain is architectural feedback. If testing is hard, the design is likely wrong (coupling, hidden globals).
Do not suppress the pain with more mocks; heal the design.

---

## Final Law

> **A test should fail for the right reason.**

---

## Field Notes & Learnings

**Verified 2026-01-13 during the Gematria Purification:**

1.  **Reality Check on Data Objects**:
    - When using real domain objects (e.g., `CalculationRecord`) instead of mocks, you **must** respect their constructor signatures (`language`, `method` required). This exposes coupling that loose mocks would hide.
    - *Lesson*: If initializing a data object in a test feels hard, the object might be too complex or doing too much.

2.  **The Path of Imports**:
    - `create_autospec` requires the class to be importable. Ensuring `PYTHONPATH` includes the source root (`src`) is critical for tests to verify against real specs.

3.  **Freezing Time Properly**:
    - Patching `datetime` must be done at the **module level** where it is imported (`pillars.gematria.services.calculation_service.datetime`), not globally (`datetime.datetime`).

4.  **Test Structure, Not Formatting**:
    - **Wrong**: `assert '"char": "T"' in saved_record.breakdown` (brittle substring check)
    - **Right**: `data = json.loads(saved_record.breakdown); assert data == [{"char": "T", ...}]` (tests serialization logic)
    - Substring checks are fragile and test implementation artifacts (whitespace, key order) rather than actual behavior.

5.  **Clock Injection (Time Under Law)**:
    - **Wrong**: Services call `datetime.now()` directly (cosmic dependency, requires patching in tests)
    - **Right**: Inject a `ClockProvider` (production: `SystemClock()`, test: `FixedClock(fixed_time)`)
    - **Architecture**: Created `shared.services.time.ClockProvider` protocol with `SystemClock` and `FixedClock` implementations
    - **Impact**: Removes patching, enables deterministic tests, makes time a first-class architectural boundary
    - Time is handed to the service, not asked from the cosmos.



