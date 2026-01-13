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
