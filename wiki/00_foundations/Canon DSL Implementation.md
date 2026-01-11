# **Canon DSL Implementation**

**Reference Document — v0.2**  
 *(Python-embedded DSL for Canon-compliant declarative geometry)*

**Aligned with:** Hermetic Geometry Canon v1.0 (Consecrated 2026-01-10)

## **1\. Purpose**

Implement a **Python-embedded DSL** that lets the app express geometry as **declarations** governed by the **Hermetic Geometry Canon v1.0**.

The DSL must support:

* Declaring **Forms** (Circle, Cube, VaultOfHestia, Spiral, etc.)

* Declaring **Relations** between forms (Inscribed, Contains, Intersects, Union, etc.)

* Declaring **Traced / Motion-revealed** forms (Article XII posture)

* Running **Canon validation**: structured findings with cited Canon articles

* Running **Realization**: converting validated declarations into computed metrics and render payloads (2D instructions, 3D meshes, etc.) via **pluggable realizers**

**Canon-first rule:** code can instantiate, but may not redefine or “interpret away” the declaration.

---

## **2\. Non-Goals (v0.1)**

* No text parser / external grammar yet (pure Python AST / dataclasses only)

* No UI imports (no PyQt; no rendering code)

* No full symbolic proof system

* No full library of every possible geometric form

* No dependence on external CAS tools

---

## **3\. Architectural Overview**

### **3.1 Core Concepts**

**Declaration (AST)** → **Validation (Canon Engine)** → **Realization (Realizers)**

* **Declaration** describes intent and structure (forms, relations, traces, invariants requested).

* **Canon Engine** enforces the Canon: produces a verdict \+ findings and prevents realization if “fatal” violations exist.

* **Realizers** are adapters that take validated declarations and produce runtime artifacts (metrics, payloads, drawing instructions).

### **3.2 Layer Boundaries**

* `canon_dsl` is a **pure core library**:

  * safe to import anywhere

  * must not import UI or heavyweight libs

* Geometry services (like `VaultOfHestiaSolidService`) live outside and plug in via a **registry**.

---

## **4\. Package Layout (recommended)**

`src/canon_dsl/`  
  `__init__.py`  
  `ast.py            # dataclasses: Form, Relation, Trace, Declaration, Constraints`  
  `canon_refs.py     # Canon article identifiers and helper utilities`  
  `findings.py       # Finding, Severity, Verdict`  
  `rules.py          # CanonRule interface + built-in rules`  
  `engine.py         # CanonEngine.validate(...)`  
  `realizers.py      # Realizer interface + registry`  
  `examples.py       # small runnable examples (no UI)`

---

## **5\. Data Model (AST)**

The DSL should be **AST-first**: immutable dataclasses that represent declarations.

### **5.1 Form**

A **Form** is a declarative object, not a mesh.

Fields (recommended):

* `id: str` — unique identifier within a declaration (e.g., `"circle_1"`)

* `kind: str` — `"Circle"`, `"Cube"`, `"VaultOfHestia"`, `"Spiral"`, `"OrbitTrace"`, `"SierpinskiTriangle"`, `"RecursiveForm"`, etc.

* `params: dict[str, Any]` — numeric / symbolic parameters (e.g., `{"radius": 10}`)

* `meaning: dict[str, Any]` — optional symbolic tags (non-binding)

* `orientation: Optional[str]` — `"CW"`, `"CCW"`, `"L"`, `"R"`, `"RH"`, `"LH"` etc.

* `symmetry_class: Optional[str]` — `"rotational_3"`, `"rotational_5"`, `"reflective"`, `"continuous"`, `"none"` (Canon II.5)

* `curvature_class: Optional[str]` — `"zero"`, `"constant"`, `"variable"` (Canon XIV.1)

* `dimensional_class: Optional[int]` — `1`=length, `2`=area, `3`=volume (Canon XI)

* `iteration_depth: Optional[int]` — for recursive forms; `None` means infinite/limit (Canon XIII)

* `truncated: bool` — `True` if this is a finite representation of an infinite form (Canon XIII.6)

* `notes: Optional[str]` — human documentation

Design note: keep `kind` as a string so new forms can be introduced without subclass sprawl.

### **5.2 Relation**

A **Relation** describes how forms relate.

Fields:

* `kind: str` — `"INSCRIBED"`, `"CIRCUMSCRIBED"`, `"CONTAINS"`, `"INTERSECTS"`, `"UNION"`, `"DIFFERENCE"`, `"TANGENT"`, `"GEODESIC_PATH"`, etc.

* `a: str` — form id (source)

* `b: str` — form id (target)

* `params: dict[str, Any]` — e.g., `{"tangent": True}`, `{"minor_arc": True}`

### **5.3 Trace (Motion-as-Revelation)**

A **Trace** is a declaration that a form is revealed through motion (Canon Article XII).

Fields:

* `id: str`

* `kind: str` — `"TRACE"` (or more specific: `"ORBITAL_TRACE"`, `"LISSAJOUS_TRACE"`, `"SPIRAL_TRACE"`, `"EPICYCLOID_TRACE"`)

* `source_form: Optional[str]` — id of a moving form (if applicable)

* `frame: Optional[str]` — reference frame / relative-to

* `params: dict[str, Any]` — may include `period`, `closure_expected`, `steps`, `sampling`

* `invariants_claimed: list[str]` — e.g., `["closure_invariance", "period_ratio"]`

* `void_type: Optional[str]` — `"swept"`, `"instantaneous"`, `"time_averaged"` (Canon XII.9)

* `closure_status: str` — `"closed"`, `"asymptotic"`, `"open"`, `"indeterminate"` (Canon XII.6)

Trace does not compute. It asserts: "this path is a legitimate revealed form if invariants hold."

### **5.4 Constraint / Invariant Requests**

To support Canonical Tests (Article IX \+ Appendix C), include optional constraints.

Two types:

**InvariantConstraint**

* `name: str` — e.g., `"inradius_resonance_phi"`

* `expr: dict[str, Any]` — structured expectation, like:

  * `{ "equals": "phi", "tolerance": "epsilon" }`

  * `{ "approx": 1.618, "rel_tol": 1e-6 }`

**CanonTestRequest**

* `test: str` — e.g., `"VOID_MONOTONICITY"`, `"CLOSURE_INVARIANCE"`, `"DIMENSIONAL_ECHO"`

* `scope: list[str]` — involved form ids

* `params: dict[str, Any]`

### **5.5 Declaration**

A Declaration bundles everything.

Fields:

* `title: str`

* `forms: list[Form]`

* `relations: list[Relation]`

* `traces: list[Trace]`

* `constraints: list[InvariantConstraint]`

* `tests: list[CanonTestRequest]`

* `metadata: dict[str, Any]`

---

## **6\. Canon Findings & Verdict**

Validation must produce structured output.

### **6.1 Severity Levels**

Use four levels:

* `FATAL` — cannot realize

* `ERROR` — invalid unless overridden (v0.1 treat as fatal)

* `WARN` — admissible but questionable / incomplete declaration

* `INFO` — advisory

### **6.2 Finding structure**

Fields:

* `severity`

* `rule_id` — stable id (e.g., `"CANON-XII-ORIENTATION-DECLARATION"`)

* `message` — human-readable

* `articles: list[str]` — Canon references, e.g., `["XII.3", "V.4.5", "C.3"]`

* `subject_ids: list[str]` — form/relation ids involved

* `suggested_fix: Optional[str]`

### **6.3 Verdict**

* `ok: bool`

* `findings: list[Finding]`

---

## **7\. Canon Engine**

### **7.1 Entry point**

`CanonEngine.validate(decl: Declaration) -> Verdict`

Rules should be **composable** and **registered**, like a linter.

### **7.2 Rule Interface**

Each rule:

* has `id`, `title`, `articles`

* implements `check(decl) -> list[Finding]`

### **7.3 Required Built-in Rules (v0.1 minimum)**

Implement these first because they enforce the most important Canon constraints:

1. **Declaration Integrity**

* form ids unique

* relations reference existing forms

* required params for known form kinds (lightweight schema)

2. **Orientation Declaration Rule**

* If a form kind or relation kind is orientation-sensitive, require `orientation` explicitly.

* Canon refs: V.4.x (chirality & orientation), XII (traced path orientation)

3. **Motion-as-Parameter Rule**

* Traces must declare period/closure expectation or explicitly mark indeterminate.

* Must not treat time as substance; only as parameter (XII posture).

4. **No Implicit Reflection Rule**

* If relation implies reflection or coordinate handedness swap, require explicit `params["reflection"]=True`.

* Canon refs: V.4.3

5. **Epsilon Declaration Rule**

* If constraints/tests require numeric comparison, tolerance must be declared at declaration or engine config.

* Canon refs: Appendix C (epsilon law)

6. **Truncation Declaration Rule**

* Recursive forms with finite `iteration_depth` must set `truncated=True`.

* No truncated instance may be presented as the full form.

* Canon refs: XIII.6

7. **Symmetry Declaration Rule**

* Forms exhibiting symmetry must declare `symmetry_class`.

* A form without declared symmetry is treated as asymmetric.

* Canon refs: II.5

8. **Curvature Class Rule**

* Curved forms (Circle, Sphere, Spiral, etc.) must declare `curvature_class`.

* Variable curvature forms must include curvature law in `params`.

* Canon refs: XIV.1, XIV.3

9. **Void Type Rule (Traces)**

* Traces that make claims about void must declare `void_type`.

* Conflating void types violates canonical clarity.

* Canon refs: XII.9

That's enough for a meaningful v0.2.

---

## **8\. Realization Layer**

Validation does not compute geometry. Realization does.

### **8.1 Realizer Interface**

`Realizer.realize(decl: Declaration, context: RealizeContext) -> RealizeResult`

Where:

**RealizeContext** contains:

* numeric config (epsilon defaults, precision)

* access to external services (optional)

* feature flags

**RealizeResult** contains:

* `artifacts: dict[str, Any]` — payloads, metrics, computed properties

* `provenance: dict[str, Any]` — traceable mapping from decl → computations (Canon “result context” style)

### **8.2 Realizer Registry**

Implement a registry keyed by:

* `Form.kind` (e.g., `"VaultOfHestia"`)

* and/or special patterns of relations/traces.

Example:

* `"VaultOfHestia"` realizer calls your existing `VaultOfHestiaSolidService.build(side_length)`

* `"Circle"` realizer computes metrics and 2D drawing instructions

### **8.3 Canon-first gating**

Realization must require a passing verdict unless explicitly overridden by caller.

Default behavior:

* `validate → if fatal/error: stop → return verdict`

---

## **9\. Examples (must be included)**

Create at least three runnable examples (no UI), to prove the DSL is usable.

### **9.1 Circle in Square (inscription)**

* declare `Circle(radius=...)`

* declare `Square(side=...)`

* relation `INSCRIBED(circle, square)`

* constraint: `circumference == 2*pi*r` (or more basic)

* validate \+ realize (circle metrics)

### **9.2 Vault of Hestia (bridging to existing service)**

* form: `VaultOfHestia(side_length=10)`

* constraint: `inradius_resonance_phi == phi ± ε`

* realize: should return `SolidPayload` \+ computed metrics via your service

### **9.3 Traced Form (Venus Rose placeholder)**

* trace declaration: `Trace(kind="ORBITAL_TRACE", params={"period":"8y","closure_expected":True})`

* validate should enforce Article XII parameterization and closure claims

* realization may be stubbed in v0.1 (return placeholder artifact)

---

## **10\. Acceptance Criteria (Definition of Done)**

Sophia’s implementation is acceptable when:

1. You can declare forms/relations/traces in Python without any parser.

2. `CanonEngine.validate()` returns structured findings with Canon article references.

3. Validation catches at least:

   * missing ids

   * bad references

   * missing orientation when required

   * trace missing parameterization

   * missing epsilon for numeric constraints

4. Realizer registry works:

   * at least Circle and VaultOfHestia realizers are implemented

   * VaultOfHestia uses your existing service, not re-derived logic

5. No UI imports; code is unit-testable.

---

## **11\. Design Guardrails (avoid future pain)**

* Prefer **strings \+ schema** over deep inheritance.

* Keep Canon references as plain strings (e.g., `"XII.3"`), not hard dependencies.

* Every computed artifact should include **provenance** (what declaration produced it).

* Never infer: if something matters (symmetry type, reflection, orientation), require it to be declared or mark indeterminate.

---

## **12\. v0.2 / v0.3 Roadmap (optional)**

Once v0.2 is stable, likely next expansions:

* Text DSL parser (optional)

* More relations: intersection/union/difference \+ void promotion rules (Canon VI.1)

* **Canonical Tests Engine (full implementation)**:
  * IX.1 Proportional Recovery
  * IX.2 Dimensional Consistency
  * IX.3 Void Monotonicity
  * IX.4 Scaling Invariance
  * IX.5 Limit Behavior
  * IX.6 Recursive Stability
  * IX.7 Curvature Invariance
  * XII.8.1 Closure Invariance
  * XII.8.2 Period Ratio
  * XII.8.3 Symmetry Emergence

* **Curvature realizers**: geodesic computation, intrinsic/extrinsic distinction

* **Recursion realizers**: iteration engine with convergence detection

* "Case law" library: saved declarations \+ verdicts as precedents

---

## **A final note to Sophia (tone-setting)**

This DSL is not a “geometry scripting convenience.”  
 It is a **Canon-compliant declaration system**. The priority is:

**Law → Clarity → Extensibility → Computation → Rendering**

If a choice is between convenience and explicit declaration, choose explicit declaration.

