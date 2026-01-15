# Canon DSL Migration Template
# ═══════════════════════════════════════════════════════════════════════

**Use this template to migrate any shape to Canon DSL (ADR-012).**

**Reference Implementations:**
- **3D**: `vault_of_hestia_solver.py` + `vault_of_hestia_realizer.py`
- **2D**: `circle_solver.py` + `circle_realizer.py`

---

## Step 1: Create the Solver

**File:** `src/pillars/geometry/canon/{shape}_solver.py`

```python
"""
{ShapeName} Solver - Full Canon-compliant bidirectional solver.

Reference: VaultOfHestiaSolver (3D) or CircleSolver (2D)
Reference: Hermetic Geometry Canon v1.0, Article II — Canonical Forms
"""

from __future__ import annotations

import math
from typing import Optional

from canon_dsl import Declaration, Form, InvariantConstraint, SolveResult, SolveProvenance

from .geometry_solver import GeometrySolver, PropertyDefinition


class {ShapeName}Solver(GeometrySolver):
    """
    Bidirectional solver for {shape_name}s.
    
    Canonical Parameter: {canonical_param} ({symbol})
    
    All derivations preserved from legacy {ShapeName}Shape with LaTeX formatting.
    """
    
    # ─────────────────────────────────────────────────────────────────
    # GeometrySolver Properties (Required)
    # ─────────────────────────────────────────────────────────────────
    
    @property
    def dimensional_class(self) -> int:
        """{ShapeName} is a {2 or 3}D form."""
        return {2 or 3}
    
    @property
    def form_type(self) -> str:
        """Canon form type."""
        return "{ShapeName}"
    
    @property
    def canonical_key(self) -> str:
        """The canonical parameter this solver produces."""
        return "{canonical_param}"
    
    @property
    def supported_keys(self) -> set[str]:
        """Properties that can be used as input to solve for {canonical_param}."""
        return {"{param1}", "{param2}", "{param3}", ...}
    
    # ─────────────────────────────────────────────────────────────────
    # Property Definitions for UI
    # ─────────────────────────────────────────────────────────────────
    
    def get_editable_properties(self) -> list[PropertyDefinition]:
        """Return editable properties with LaTeX formulas."""
        return [
            PropertyDefinition(
                key="{canonical_param}",
                label="{Display Name} ({symbol})",
                unit="units",  # or "units²" or "units³"
                editable=True,
                category="Core",
                tooltip="Description of the parameter",
                format_spec=".6f",
                formula=r"{LaTeX formula}",
            ),
            # Add more properties...
        ]
    
    # ─────────────────────────────────────────────────────────────────
    # Bidirectional Solving
    # ─────────────────────────────────────────────────────────────────
    
    def solve_from(self, key: str, value: float) -> SolveResult:
        """
        Convert any supported property to the canonical parameter.
        
        Args:
            key: The property being set (e.g., "volume", "surface_area")
            value: The value entered by the user
        
        Returns:
            SolveResult with canonical parameter and provenance
        """
        if key == "{canonical_param}":
            canonical_value = value
            formula = r"{symbol} = {symbol}"
        elif key == "{param2}":
            canonical_value = {conversion formula using value}
            formula = r"{LaTeX conversion formula}"
        # Add more conversions...
        else:
            return SolveResult.invalid(
                key, 
                value, 
                f"Unknown property: {key}. Supported: {self.supported_keys}"
            )
        
        # Build provenance for traceability
        provenance = SolveProvenance(
            source_key=key,
            source_value=value,
            formula_used=formula,
            canonical_key="{canonical_param}",
            canonical_value=canonical_value,
        )
        
        return SolveResult.success(
            canonical_parameter=canonical_value,
            canonical_key="{canonical_param}",
            provenance=provenance,
        )
    
    def get_all_properties(self, canonical_value: float) -> dict[str, float]:
        """
        Compute all derived properties from {canonical_param}.
        
        This is the forward calculation after solving.
        """
        return {
            "{canonical_param}": canonical_value,
            "{property2}": {formula},
            "{property3}": {formula},
            # Add all derived properties...
        }
    
    # ─────────────────────────────────────────────────────────────────
    # Declaration Creation (Canon DSL Integration)
    # ─────────────────────────────────────────────────────────────────
    
    def create_declaration(
        self,
        canonical_value: float,  # or dict for multi-param shapes
        *,
        title: Optional[str] = None,
    ) -> Declaration:
        """
        Create a Canon-compliant Declaration for a {ShapeName}.
        
        This is the bridge from Solver output to Canon validation.
        
        Args:
            canonical_value: The {canonical_param}
            title: Custom title for the declaration
        
        Returns:
            A Declaration ready for Canon validation and realization
        """
        forms = [
            Form(
                id="{shape_id}",
                kind="{ShapeName}",
                params={"{canonical_param}": canonical_value},
                symmetry_class="{symmetry}",  # e.g., "rotational_4", "rotational_infinite"
                curvature_class="{curvature}",  # "flat", "constant", "variable"
                dimensional_class={2 or 3},
                notes="{Any special notes}",
            ),
        ]
        
        # Optional: Add invariant constraints
        constraints = []
        # Example:
        # constraints.append(
        #     InvariantConstraint(
        #         name="phi_resonance",
        #         expr={"equals": "phi", "tolerance": 1e-6},
        #         scope=["{shape_id}"],
        #         notes="Some golden ratio relationship",
        #     )
        # )
        
        return Declaration(
            title=title or f"{ShapeName} ({symbol}={canonical_value:.4f})",
            forms=forms,
            constraints=constraints,
            epsilon=1e-9,
            metadata={
                "canon_ref": "Article {X} — {Reference}",
                "solver": "{ShapeName}Solver",
            },
        )
    
    # ─────────────────────────────────────────────────────────────────
    # Mathematical Derivations (Preserved from Legacy)
    # ─────────────────────────────────────────────────────────────────
    
    def get_derivation(self) -> str:
        """
        Return the mathematical derivation with LaTeX formatting.
        
        This is the sacred geometry commentary explaining why the formulas work.
        All equations MUST be converted to LaTeX math strings for proper rendering.
        
        CRITICAL FORMATTING RULES:
        1. Inline math: Use $formula$ (e.g., $\pi r^2$)
        2. Display math: Use $$formula$$ on its own line
        3. Multi-line equations: Use $$\\begin{align}...\\end{align}$$
        4. Greek letters: \alpha, \beta, \pi, \phi, etc.
        5. Fractions: \frac{numerator}{denominator}
        6. Square roots: \sqrt{x}
        7. Superscripts: x^2
        8. Subscripts: x_1
        """
        return r'''
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    THE {SHAPENAME} — DERIVATIONS                              ║
║                        {Short Description}                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

DEFINITION
══════════

{Clear definition of the shape with LaTeX equations}


{PROPERTY 1 NAME}: ${LaTeX formula}$
═══════════════════════════════════════

**Derivation:**
{Step-by-step derivation with LaTeX}

Example:
For a square pyramid with base side $a$ and height $h$:
$$V = \frac{1}{3} \times \text{base area} \times \text{height} = \frac{1}{3}a^2h$$


{PROPERTY 2 NAME}: ${LaTeX formula}$
═══════════════════════════════════════

**Derivation Method 1:**
{Method 1 with LaTeX}

**Derivation Method 2:**
{Alternative method}


CANONICAL PROPORTIONS (Canon Article III.1)
════════════════════════════════════════════

The {shape} embodies **proportion over magnitude**:

$${key proportion formula}$$

**Dimensional Echo (Canon III.2):**
- Length ($1$-dimensional): $L \propto {canonical}^1$
- Area ($2$-dimensional): $A \propto {canonical}^2$
- Volume ($3$-dimensional): $V \propto {canonical}^3$


SYMMETRY (Canon Article II.5)
══════════════════════════════

{Describe symmetry properties using group theory}
- **Symmetry group**: {group name}


APPLICATIONS
════════════

**Physics:**
{Physical applications}

**Sacred Geometry:**
{Esoteric/symbolic meanings}


ESOTERIC SIGNIFICANCE
═════════════════════

In the M.I.X. (Magickal Isopsephy eXchange), the {ShapeName} is:
- **{Symbolic meaning 1}**
- **{Symbolic meaning 2}**

{Closing mystical commentary}
'''
    
    def get_derivation_title(self) -> str:
        """Return the title for the derivation dialog."""
        return "{ShapeName} — {Subtitle}"
```

---

## Step 2: Create the Realizer

**File:** `src/pillars/geometry/canon/{shape}_realizer.py`

```python
"""
{ShapeName} Realizer - Full Canon-compliant realization.

Reference: VaultOfHestiaRealizer (3D) or CircleRealizer (2D)
Reference: ADR-010: Canon DSL Adoption
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from canon_dsl import Realizer, FormRealization, RealizeContext

if TYPE_CHECKING:
    from canon_dsl import Form


# Service version for provenance tracking
_SERVICE_VERSION = "1.0"


class {ShapeName}Realizer(Realizer):
    """
    Realizer for {ShapeName} forms.
    
    Converts validated {ShapeName} Declarations into drawable artifacts
    by delegating to the existing {ShapeName}ShapeService (or SolidService).
    
    This realizer:
    - Accepts only Form.kind == "{ShapeName}"
    - Extracts {canonical_param} from form.params
    - Calls {ShapeName}ShapeService.build({canonical_param}=...)
    - Returns artifact with full metrics and provenance
    
    It does NOT:
    - Perform validation (CanonEngine already did that)
    - Reimplement geometry computation (delegates to existing service)
    - Import UI components (stays pure)
    """
    
    @property
    def supported_kinds(self) -> set[str]:
        """This realizer handles only {ShapeName} forms."""
        return {"{ShapeName}"}
    
    def realize_form(self, form: Form, context: RealizeContext) -> FormRealization:
        """
        Realize a {ShapeName} form into a drawable artifact.
        
        Args:
            form: The {ShapeName} Form from a validated Declaration
            context: Realization context with epsilon and config
        
        Returns:
            FormRealization containing:
            - artifact: Drawing/solid instructions from service
            - metrics: Key derived metrics
            - provenance: Full traceability data
        
        Raises:
            ValueError: If form.kind is not "{ShapeName}"
        """
        # Sanity check (should never fail if CanonEngine is routing correctly)
        if form.kind not in self.supported_kinds:
            raise ValueError(
                f"{ShapeName}Realizer received unsupported kind: {form.kind}"
            )
        
        # Extract canonical parameter(s)
        {canonical_param} = form.params.get("{canonical_param}", {default_value})
        
        # Delegate to existing service (no reimplementation!)
        
        # FOR 2D SHAPES ONLY (Circle, Square, Ellipse, etc.):
        from ..services.{shape}_shape import {ShapeName}ShapeService
        from ..ui.scene_adapter import build_scene_payload
        from ..ui.unified.payloads import GeometryPayload
            
            # Get drawing instructions from service
            drawing_dict = {ShapeName}ShapeService.build({canonical_param}={canonical_param})
            
            # Convert to proper scene payload with primitives
            scene_payload = build_scene_payload(drawing_dict, labels=[])
            
            # Wrap in GeometryPayload
            result = GeometryPayload.from_scene_payload(
                scene_payload,
                form_type="{ShapeName}",
                title=f"{ShapeName} ({symbol}={{canonical_param}:.4f})",
                params={{"{canonical_param}": {canonical_param}}},
                validation_status="valid",
            )
        
        # Extract metrics for the realization result
        metrics = self._extract_metrics({canonical_param})
        
        # Build provenance for traceability
        provenance = self._build_provenance(form, {canonical_param}, context)
        
        return FormRealization(
            artifact=result,  # GeometryPayload (not raw dict!)
            metrics=metrics,
            provenance=provenance,
        )
    
    def _extract_metrics(self, {canonical_param}: float) -> dict:
        """
        Extract key metrics from the realization.
        
        These are the metrics most useful for verification and display.
        """
        import math
        
        return {
            # Canonical parameter
            "{canonical_param}": {canonical_param},
            
            # Core measurements
            "{property1}": {formula},
            "{property2}": {formula},
            
            # Proportions (Canon III.1)
            "{ratio1}": {invariant ratio},
        }
    
    def _build_provenance(
        self,
        form: Form,
        {canonical_param}: float,
        context: RealizeContext,
    ) -> dict:
        """
        Build provenance data for full traceability.
        
        Provenance enables:
        - Debugging ("why does this look like this?")
        - Reproducibility ("same declaration → same artifact")
        - Case law storage ("this declaration was valid/invalid")
        """
        import math
        
        return {
            # Declaration source
            "form_id": form.id,
            "form_kind": form.kind,
            "declaration_title": context.declaration.title,
            
            # Service identity
            "service": "{ShapeName}ShapeService",
            "service_version": _SERVICE_VERSION,
            "realizer": "{ShapeName}Realizer",
            
            # Canon references
            "canon_refs": [
                "Article {X} — {Reference}",
                "III.1 — Proportion over Magnitude",
            ],
            
            # Key invariants verified by this realization
            "invariants": {
                "{invariant1_name}": {formula},
            },
            
            # Configuration
            "epsilon": context.epsilon,
        }


# ═══════════════════════════════════════════════════════════════════════
# NOTE FOR 3D SOLIDS
# ═══════════════════════════════════════════════════════════════════════
# For 3D solids (Cube, Tetrahedron, etc.), use VaultOfHestiaRealizer as template.
# The pattern is similar but simpler:
# 1. Call {Shape}SolidService.build() - returns a result with .payload and .metrics
# 2. Use GeometryPayload.from_solid_payload(result.payload, ...) to wrap it
# 3. No need for scene_adapter - solids return SolidPayload directly
#
# See: src/pillars/geometry/canon/vault_of_hestia_realizer.py
```

---

## Step 3: Register in `__init__.py`

**File:** `src/pillars/geometry/canon/__init__.py`

```python
# Add imports
from .{shape}_solver import {ShapeName}Solver
from .{shape}_realizer import {ShapeName}Realizer

# Add to __all__
__all__ = [
    # ...existing exports...
    "{ShapeName}Solver",
    "{ShapeName}Realizer",
]
```

---

## Step 4: Register in `geometry_definitions.py`

**File:** `src/pillars/geometry/ui/geometry_definitions.py`

```python
# Add to imports from ..canon
from ..canon import (
    # ...existing...
    {ShapeName}Solver,
    {ShapeName}Realizer,
)

# Find the shape entry in CATEGORY_DEFINITIONS and add:
{
    "name": "{Display Name}",
    "summary": "{Short description}",
    "factory": None,  # Remove old factory if present
    "esoteric_description": { /* ... */ },
    "use_canon_dsl": True,  # ADD THIS
    "solver": {ShapeName}Solver,  # ADD THIS
    "realizer": {ShapeName}Realizer,  # ADD THIS
    "default_canonical": {{"{canonical_param}": {default_value}}},  # ADD THIS
}
```

---

## Step 5: Test

```bash
# Run smoke test
cd /path/to/isopgem && ./run.sh

# In the app:
1. Open Geometry Hub
2. Select your shape
3. Verify the Canon shape viewer opens
4. Test bidirectional solving (change different properties)
5. Click "Show Derivations" button
6. Verify LaTeX equations render properly
```

---

## Critical Conversion Rules

### LaTeX Math Formatting

**DO:**
- Inline: `$\pi r^2$`
- Display: `$$V = \frac{4}{3}\pi r^3$$`
- Greek: `\alpha, \beta, \gamma, \Delta, \pi, \phi, \Omega`
- Fractions: `\frac{a}{b}`
- Roots: `\sqrt{x}` or `\sqrt[n]{x}`
- Superscripts: `x^{2}` or `e^{-t}`
- Subscripts: `x_{1}` or `V_{\text{cube}}`

**DON'T:**
- Plain text equations: `V = (4/3)πr³` ❌
- Unicode symbols without LaTeX: `π` ❌ (use `$\pi$` ✓)
- HTML entities: `&pi;` ❌

### Derivation Preservation

**CRITICAL:** Do NOT lose the mathematical derivations from legacy files!

1. Find the old `{shape}_shape.py` Calculator class
2. Look for docstrings with derivations
3. Copy ALL derivation comments
4. Convert to LaTeX format
5. Place in `get_derivation()` method

---

## Troubleshooting

### "Can't instantiate abstract class {Shape}Solver"

Missing one of these required methods:
- `dimensional_class` property
- `form_type` property
- `canonical_key` property
- `supported_keys` property
- `solve_from()` method
- `get_all_properties()` method
- `create_declaration()` method

### "unsupported format string passed to dict.__format__"

Multi-parameter shapes (Ellipse, Rectangle) pass a `dict` to `create_declaration()`.
Fix the signature:
```python
def create_declaration(
    self,
    canonical_value: float | dict,  # Accept both!
    *,
    title: Optional[str] = None,
) -> Declaration:
    # Handle dict case
    if isinstance(canonical_value, dict):
        param1 = canonical_value.get("param1", default1)
        param2 = canonical_value.get("param2", default2)
    else:
        param1 = canonical_value
        param2 = default_param2
```

### Derivations not accessible

Make sure you implemented:
- `get_derivation()` method in the Solver
- `get_derivation_title()` method in the Solver

The UI will automatically add a "Show Derivations" button.

---

## Summary Checklist

- [ ] Create `{shape}_solver.py` following template
- [ ] Create `{shape}_realizer.py` following template
- [ ] Add imports to `canon/__init__.py`
- [ ] Update shape entry in `geometry_definitions.py`
- [ ] Preserve ALL mathematical derivations from legacy
- [ ] Convert ALL equations to LaTeX format
- [ ] Test in UI (open, solve, view derivations)
- [ ] Mark old Calculator/Shape class as deprecated

**Time estimate:** 30-60 minutes per shape (once you have the pattern)
