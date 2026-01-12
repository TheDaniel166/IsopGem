# LaTeX Rendering in Geometry Derivations

## Overview

The Unified Geometry Viewer now supports **automatic LaTeX rendering** in derivation dialogs. Mathematical formulas written with standard LaTeX delimiters (`$...$` and `$$...$$`) will be beautifully rendered as mathematical notation.

## Quick Start

### Writing LaTeX in Derivations

In your `GeometrySolver.get_derivation()` method, simply wrap mathematical expressions with LaTeX delimiters:

**Inline math**: Use `$...$` for formulas within text
```
The sphere radius is $r = \frac{s}{2\varphi}$ where s is the cube side length.
```

**Display math**: Use `$$...$$` for standalone equations
```
$$V_{sphere} = \frac{4}{3}\pi r^3 = \frac{4}{3}\pi\left(\frac{s}{2\varphi}\right)^3$$
```

## Example: VaultOfHestia Derivations

See [vault_of_hestia_solver.py](../../src/pillars/geometry/canon/vault_of_hestia_solver.py#L509) for a complete example with LaTeX formulas.

### Before (Plain Text):
```
SPHERE RADIUS: r = s/(2φ)

The slant height from apex to midpoint of base edge:
    ℓ² = h² + (a/2)²
    ℓ² = s² + s²/4
    ℓ = s√5/2
```

### After (With LaTeX):
```
SPHERE RADIUS: $r = \frac{s}{2\varphi}$

The slant height from apex to midpoint of base edge:
    $$\ell^2 = h^2 + \left(\frac{a}{2}\right)^2$$
    $$\ell^2 = s^2 + \frac{s^2}{4} = \frac{5s^2}{4}$$
    $$\ell = \frac{s\sqrt{5}}{2}$$
```

The LaTeX will be automatically rendered when the user opens the derivation dialog via the 📖 button.

## How It Works

1. **User clicks the 📖 Derivation button** in the Unified Geometry Viewer
2. **UnifiedGeometryViewer._show_derivation_dialog()** is called
3. The dialog displays the derivation text with **automatic LaTeX rendering**
4. **MathRenderer** (using Matplotlib) converts LaTeX → PNG images
5. Images are embedded inline in the QTextEdit widget

### Manual Re-rendering

Users can click the **"🎨 Render Math"** button in the derivation dialog to re-render all formulas if needed.

## Common LaTeX Syntax

### Greek Letters
```latex
$\alpha, \beta, \gamma, \delta, \epsilon$
$\pi, \sigma, \tau, \omega$
$\Phi, \Psi, \Omega$  # Capital letters
$\varphi$  # Variant phi (recommended for golden ratio)
```

### Fractions
```latex
$\frac{numerator}{denominator}$
$\frac{a + b}{c - d}$
```

### Superscripts and Subscripts
```latex
$x^2, x^{10}, x^{n+1}$  # Superscripts (powers)
$V_{cube}, V_{sphere}$   # Subscripts
$V_{\text{sphere}}$      # Text in subscript
```

### Square Roots
```latex
$\sqrt{5}$
$\sqrt{x^2 + y^2}$
$\sqrt[3]{27}$  # Cube root
```

### Parentheses (auto-sizing)
```latex
$\left(\frac{a}{b}\right)^2$  # Auto-sized parentheses
$\left[\frac{x}{y}\right]$    # Brackets
$\left\{\frac{p}{q}\right\}$  # Braces
```

### Common Operators
```latex
$\times$  # Multiplication
$\cdot$   # Dot multiplication
$\div$    # Division
$\pm$     # Plus-minus
$\approx$ # Approximately equal
$\leq, \geq$  # Less/greater than or equal
```

## Migration Guide for Existing Derivations

When migrating derivation comments from old service files to new Canon solvers (per ADR-012), enhance the mathematical formulas with LaTeX:

### Step 1: Identify Math Formulas

Look for:
- Equations (e.g., `r = s/(2φ)`)
- Multi-line derivations
- Formulas with fractions, roots, exponents

### Step 2: Wrap with Delimiters

- **Inline**: `$r = \frac{s}{2\varphi}$`
- **Display**: `$$\ell = \frac{s\sqrt{5}}{2}$$`

### Step 3: Test Rendering

1. Run your geometry viewer
2. Select the shape
3. Click 📖 to open derivations
4. Verify LaTeX renders correctly

## Benefits

✅ **Visual Clarity**: Mathematical notation is rendered beautifully
✅ **Professionalism**: Academic-quality mathematical presentation
✅ **Preservation**: Formulas remain readable as plain text (copy-paste works)
✅ **Hermetic Compliance**: Enhances knowledge preservation (ADR-012 Pillar 3)

## Technical Details

- **Renderer**: `MathRenderer` using Matplotlib with Agg backend
- **Image Format**: PNG with transparency
- **DPI**: 140 (high resolution)
- **Font Size**: 13pt
- **Color**: `#1a202c` (void color from Visual Liturgy)
- **Fallback**: If rendering fails, plain text is displayed

## ADR-012 Compliance

This feature directly supports **ADR-012: Complete Canon Migration**, specifically:

> **PILLAR 3: Mathematical Knowledge Preservation 📚**
> - Derivation comments MUST be migrated to new Solver classes
> - Mathematical derivations preserved with LaTeX rendering support

LaTeX rendering ensures that mathematical knowledge is not only preserved but **enhanced** during migration, making derivations more accessible and visually stunning.

---

**Last Updated**: 2026-01-11
**Feature Added**: Unified Geometry Viewer v2.0
**See Also**:
- [ADR-012: Complete Canon Migration](../01_blueprints/decisions/ADR-012_complete_canon_migration.md)
- [Unified Geometry Viewer Architecture](../01_blueprints/decisions/ADR-011_unified_geometry_viewer.md)
