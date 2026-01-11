# ADR-010: Canon DSL Adoption

<!-- Last Verified: 2026-01-10 -->

**Status: Accepted** *(Approved by The Magus, 2026-01-10)*

**Aligned with:** Hermetic Geometry Canon v1.0 (Consecrated 2026-01-10)

---

## Context

IsopGem's geometry pillar has grown organically, with services computing forms imperatively:

```python
# Current pattern (imperative)
result = vault_service.build(side_length=10)
```

This approach suffers from several architectural weaknesses:

1. **No validation before computation** — Invalid parameters discovered only at runtime
2. **No Canon enforcement** — Magic numbers, undeclared orientations, and implicit reflections possible
3. **No provenance** — Artifacts cannot trace back to their defining intent
4. **Tight coupling** — Services know about rendering, computation, and validation simultaneously
5. **Testing requires instantiation** — Cannot validate declarations in isolation

The consecration of the **Hermetic Geometry Canon v1.0** establishes a rigorous framework of axioms, tests, and prohibitions. Without a mechanism to enforce the Canon, it remains aspirational rather than operational.

---

## Decision

We adopt the **Canon DSL** architecture as specified in `wiki/00_foundations/Canon DSL Implementation.md` (v0.2).

### Core Principle

**Declaration → Validation → Realization**

All geometry in IsopGem will transition from imperative construction to declarative specification:

```python
# New pattern (declarative, Canon-compliant)
decl = Declaration(
    title="Vault of Hestia",
    forms=[
        Form(id="vault", kind="VaultOfHestia", 
             params={"side_length": 10},
             symmetry_class="rotational_4",
             curvature_class="variable")
    ],
    constraints=[
        InvariantConstraint(name="phi_resonance", expr={"equals": "phi", "tolerance": "epsilon"})
    ]
)

verdict = canon_engine.validate(decl)
if verdict.ok:
    result = realizer_registry.realize(decl)
else:
    handle_violations(verdict.findings)
```

### Architectural Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `canon_dsl.ast` | `src/canon_dsl/ast.py` | Immutable dataclasses: Form, Relation, Trace, Declaration |
| `canon_dsl.engine` | `src/canon_dsl/engine.py` | CanonEngine with validation rules |
| `canon_dsl.realizers` | `src/canon_dsl/realizers.py` | Realizer interface + registry |
| `canon_dsl.findings` | `src/canon_dsl/findings.py` | Finding, Severity, Verdict structures |
| `canon_dsl.rules` | `src/canon_dsl/rules.py` | Built-in Canon validation rules |

### Validation Rules (v0.2)

1. Declaration Integrity (unique IDs, valid references)
2. Orientation Declaration Rule (V.4.x)
3. Motion-as-Parameter Rule (XII)
4. No Implicit Reflection Rule (V.4.3)
5. Epsilon Declaration Rule (Appendix C)
6. Truncation Declaration Rule (XIII.6)
7. Symmetry Declaration Rule (II.5)
8. Curvature Class Rule (XIV.1, XIV.3)
9. Void Type Rule (XII.9)

### Migration Strategy

**Phase 1: Infrastructure (Week 1-2)**
- Create `src/canon_dsl/` package
- Implement AST dataclasses
- Implement CanonEngine with rules 1-5
- Create basic realizers for Circle and VaultOfHestia

**Phase 2: Geometry Pillar Migration (Week 3-4)**
- Refactor `VaultOfHestiaSolidService` → `VaultOfHestiaRealizer`
- Refactor tessellation services → `TessellationRealizer`
- Update Geometry UI to submit Declarations

**Phase 3: Astronomy Pillar Migration (Week 5-6)**
- Venus Rose becomes `Trace` declaration with `OrbitalTraceRealizer`
- Enforce XII.8 tests (Closure Invariance, Period Ratio)

**Phase 4: Full Integration (Week 7-8)**
- Implement rules 6-9
- Add Canonical Tests engine (IX.1-7, XII.8.1-3)
- Establish "case law" library of validated declarations

### Architectural Guarantees

The following guarantees are structurally enforced:

1. **No Realization Without Validation**
   - `CanonEngine.realize()` always validates first
   - `skip_validation=True` raises `CanonBypassError` unless `allow_bypass=True`
   - Bypassed realizations emit `CanonBypassWarning` and log warnings

2. **Declaration Signatures**
   - Every declaration has a stable SHA-256 signature
   - Signatures enable verdict caching and reproducibility
   - Provenance includes signature and validation timestamp

3. **Pillar Sovereignty**
   - `canon_dsl/` contains only abstract interfaces (no pillar imports)
   - Concrete realizers live in their respective pillars
   - Example: `VaultOfHestiaRealizer` → `src/pillars/geometry/realizers/`

4. **Calculator Independence**
   - Calculators are UI assistive tools, not realization paths
   - Calculator outputs flow through declarations, not directly to builders
   - This prevents unvalidated side channels

5. **Legacy Path Screaming**
   - `use_canon_dsl=False` entries trigger visible warnings
   - New geometry entries default to Canon path
   - Legacy flag is scaffolding, not permanence

---

## Consequences

### Positive

1. **Canon Enforcement** — The Canon is no longer aspirational; it is executable
2. **Provenance** — Every geometric artifact traces to a validated declaration
3. **Testability** — Declarations can be validated without UI instantiation
4. **Extensibility** — New forms plug into the registry without modifying core code
5. **Error Prevention** — Invalid geometry fails at declaration, not at render time
6. **Documentation** — Declarations are self-documenting specifications

### Negative

1. **Migration Cost** — Existing services must be refactored to realizers
2. **Learning Curve** — Contributors must understand the DSL pattern
3. **Verbosity** — Simple cases require more boilerplate than direct calls
4. **Performance** — Validation adds overhead (mitigated by caching verdicts)

### Neutral

1. **UI Unchanged** — Windows, widgets, and rendering code remain as-is
2. **Pillar Sovereignty** — Each pillar owns its realizers; DSL lives in shared substrate
3. **Signal Bus** — Navigation and events unchanged

---

## Alternatives Considered

### Alternative 1: Schema Validation Only
Add JSON Schema or Pydantic validation to existing services without DSL.

**Rejected because:** Schema validation checks structure, not Canon semantics. Cannot enforce "orientation must be declared" or "truncation must be explicit."

### Alternative 2: Decorator-Based Validation
Add `@canon_compliant` decorators to existing service methods.

**Rejected because:** Validation remains entangled with computation. Cannot validate intent before execution.

### Alternative 3: External DSL with Parser
Create a text-based DSL with grammar and parser.

**Deferred to v0.3:** Python-embedded DSL is sufficient for v0.2. Text parser adds complexity without proportional benefit yet.

---

## Implementation Checklist

### Phase 1: Core Infrastructure ✓ COMPLETE

- [x] Create `src/canon_dsl/__init__.py`
- [x] Implement `ast.py` with Form, Relation, Trace, Declaration
- [x] Implement `findings.py` with Finding, Severity, Verdict
- [x] Implement `rules.py` with CanonRule interface + 9 built-in rules
- [x] Implement `engine.py` with CanonEngine.validate() + bypass protection
- [x] Implement `realizers.py` with Realizer interface and registry
- [x] Implement `canon_refs.py` with Canon article constants
- [x] Create `examples.py` with Circle-in-Square, Vault of Hestia, Venus Rose, Sierpinski
- [x] Add declaration signatures for provenance
- [x] Add CanonBypassError / CanonBypassWarning for safety

### Phase 2: Geometry Pillar Migration ✓ COMPLETE

- [x] Create `src/pillars/geometry/canon/` directory  *(used canon/ instead of realizers/)*
- [x] Implement VaultOfHestiaRealizer (wrapping existing service)
- [x] Implement VaultOfHestiaSolver (bidirectional calculation)
- [x] Create declaration factory (`create_declaration()` in Solver)
- [x] Add `use_canon_dsl` flag to geometry_definitions.py
- [x] Update solid viewer (window3d.py) to use Canon path when flag is set
- [ ] Write unit tests for VaultOfHestia declarations *(deferred)*

### Phase 3: Astronomy Pillar Migration

- [ ] Create OrbitalTraceRealizer for Venus Rose
- [ ] Implement XII.8 tests (Closure Invariance, Period Ratio)
- [ ] Update Venus Rose window to use declarations

### Phase 4: Polish

- [ ] Document migration guide for contributors
- [ ] Establish "case law" library of validated declarations
- [ ] Create Canon Finding panel for UI feedback

---

## References

- [Hermetic Geometry Canon v1.0](../HERMETIC_GEOMETRY_CANON.md)
- [Canon DSL Implementation Spec v0.2](../../00_foundations/Canon%20DSL%20Implementation.md)
- [ADR-009: Sovereignty Purification](./ADR-009_sovereignty_purification.md)

---

*"I am the Form; You are the Will. Together, we weave the Reality."*

*This ADR consecrates the bridge between eternal Canon and executable code.*
