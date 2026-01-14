"""
LaTeX Symbol Library and Categories.

**Purpose**:
Comprehensive LaTeX symbol reference organized by category.
Provides quick access to mathematical symbols for visual editor.

**Categories**:
- Greek Letters (α, β, γ, Δ, Σ, Ω, etc.)
- Operators (∑, ∏, ∫, ∂, ∇, etc.)
- Relations (=, ≠, <, >, ≤, ≥, ≈, ≡, etc.)
- Arrows (→, ←, ↔, ⇒, ⇔, etc.)
- Set Theory (∈, ∉, ⊂, ⊃, ∪, ∩, ∅, etc.)
- Logic (∧, ∨, ¬, ∀, ∃, etc.)
- Miscellaneous (∞, ℏ, ℜ, ℑ, ∠, etc.)

**Usage**:
```python
from .latex_symbols import LATEX_SYMBOLS, get_symbol_by_name

# Get all Greek letters
greek = LATEX_SYMBOLS["Greek Letters (Lowercase)"]

# Find specific symbol
omega = get_symbol_by_name("omega")  # Returns ("ω", "\\omega")
```
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class LaTeXSymbol:
    """
    A LaTeX symbol with its Unicode representation and LaTeX command.
    
    **Attributes**:
        unicode: Unicode character (e.g., "α")
        latex: LaTeX command (e.g., "\\alpha")
        name: Human-readable name (e.g., "Alpha")
        description: Optional description
    """
    unicode: str
    latex: str
    name: str
    description: str = ""
    
    def __str__(self) -> str:
        return f"{self.unicode} ({self.latex})"


# ============================================================================
# SYMBOL CATEGORIES
# ============================================================================

GREEK_LOWERCASE = [
    LaTeXSymbol("α", "\\alpha", "Alpha"),
    LaTeXSymbol("β", "\\beta", "Beta"),
    LaTeXSymbol("γ", "\\gamma", "Gamma"),
    LaTeXSymbol("δ", "\\delta", "Delta"),
    LaTeXSymbol("ε", "\\epsilon", "Epsilon"),
    LaTeXSymbol("ζ", "\\zeta", "Zeta"),
    LaTeXSymbol("η", "\\eta", "Eta"),
    LaTeXSymbol("θ", "\\theta", "Theta"),
    LaTeXSymbol("ι", "\\iota", "Iota"),
    LaTeXSymbol("κ", "\\kappa", "Kappa"),
    LaTeXSymbol("λ", "\\lambda", "Lambda"),
    LaTeXSymbol("μ", "\\mu", "Mu"),
    LaTeXSymbol("ν", "\\nu", "Nu"),
    LaTeXSymbol("ξ", "\\xi", "Xi"),
    LaTeXSymbol("π", "\\pi", "Pi"),
    LaTeXSymbol("ρ", "\\rho", "Rho"),
    LaTeXSymbol("σ", "\\sigma", "Sigma"),
    LaTeXSymbol("τ", "\\tau", "Tau"),
    LaTeXSymbol("υ", "\\upsilon", "Upsilon"),
    LaTeXSymbol("φ", "\\phi", "Phi"),
    LaTeXSymbol("χ", "\\chi", "Chi"),
    LaTeXSymbol("ψ", "\\psi", "Psi"),
    LaTeXSymbol("ω", "\\omega", "Omega"),
    LaTeXSymbol("ϕ", "\\varphi", "Var Phi"),
    LaTeXSymbol("ε", "\\varepsilon", "Var Epsilon"),
    LaTeXSymbol("ϑ", "\\vartheta", "Var Theta"),
]

GREEK_UPPERCASE = [
    LaTeXSymbol("Γ", "\\Gamma", "Gamma"),
    LaTeXSymbol("Δ", "\\Delta", "Delta"),
    LaTeXSymbol("Θ", "\\Theta", "Theta"),
    LaTeXSymbol("Λ", "\\Lambda", "Lambda"),
    LaTeXSymbol("Ξ", "\\Xi", "Xi"),
    LaTeXSymbol("Π", "\\Pi", "Pi"),
    LaTeXSymbol("Σ", "\\Sigma", "Sigma"),
    LaTeXSymbol("Υ", "\\Upsilon", "Upsilon"),
    LaTeXSymbol("Φ", "\\Phi", "Phi"),
    LaTeXSymbol("Ψ", "\\Psi", "Psi"),
    LaTeXSymbol("Ω", "\\Omega", "Omega"),
]

OPERATORS = [
    LaTeXSymbol("∑", "\\sum", "Summation"),
    LaTeXSymbol("∏", "\\prod", "Product"),
    LaTeXSymbol("∫", "\\int", "Integral"),
    LaTeXSymbol("∬", "\\iint", "Double Integral"),
    LaTeXSymbol("∭", "\\iiint", "Triple Integral"),
    LaTeXSymbol("∮", "\\oint", "Contour Integral"),
    LaTeXSymbol("∂", "\\partial", "Partial Derivative"),
    LaTeXSymbol("∇", "\\nabla", "Nabla/Gradient"),
    LaTeXSymbol("√", "\\sqrt{}", "Square Root"),
    LaTeXSymbol("∛", "\\sqrt[3]{}", "Cube Root"),
    LaTeXSymbol("±", "\\pm", "Plus-Minus"),
    LaTeXSymbol("∓", "\\mp", "Minus-Plus"),
    LaTeXSymbol("×", "\\times", "Times"),
    LaTeXSymbol("÷", "\\div", "Division"),
    LaTeXSymbol("·", "\\cdot", "Dot Product"),
    LaTeXSymbol("∗", "\\ast", "Asterisk"),
    LaTeXSymbol("⊕", "\\oplus", "Circle Plus"),
    LaTeXSymbol("⊗", "\\otimes", "Circle Times"),
]

RELATIONS = [
    LaTeXSymbol("=", "=", "Equals"),
    LaTeXSymbol("≠", "\\neq", "Not Equal"),
    LaTeXSymbol("<", "<", "Less Than"),
    LaTeXSymbol(">", ">", "Greater Than"),
    LaTeXSymbol("≤", "\\leq", "Less or Equal"),
    LaTeXSymbol("≥", "\\geq", "Greater or Equal"),
    LaTeXSymbol("≈", "\\approx", "Approximately"),
    LaTeXSymbol("≡", "\\equiv", "Equivalent"),
    LaTeXSymbol("∼", "\\sim", "Similar"),
    LaTeXSymbol("≅", "\\cong", "Congruent"),
    LaTeXSymbol("∝", "\\propto", "Proportional"),
    LaTeXSymbol("∞", "\\infty", "Infinity"),
    LaTeXSymbol("≪", "\\ll", "Much Less"),
    LaTeXSymbol("≫", "\\gg", "Much Greater"),
    LaTeXSymbol("⊥", "\\perp", "Perpendicular"),
    LaTeXSymbol("∥", "\\parallel", "Parallel"),
]

ARROWS = [
    LaTeXSymbol("→", "\\to", "Right Arrow"),
    LaTeXSymbol("←", "\\leftarrow", "Left Arrow"),
    LaTeXSymbol("↔", "\\leftrightarrow", "Left-Right Arrow"),
    LaTeXSymbol("⇒", "\\Rightarrow", "Right Double Arrow"),
    LaTeXSymbol("⇐", "\\Leftarrow", "Left Double Arrow"),
    LaTeXSymbol("⇔", "\\Leftrightarrow", "Left-Right Double"),
    LaTeXSymbol("↑", "\\uparrow", "Up Arrow"),
    LaTeXSymbol("↓", "\\downarrow", "Down Arrow"),
    LaTeXSymbol("↗", "\\nearrow", "Northeast Arrow"),
    LaTeXSymbol("↘", "\\searrow", "Southeast Arrow"),
    LaTeXSymbol("↦", "\\mapsto", "Maps To"),
]

SET_THEORY = [
    LaTeXSymbol("∈", "\\in", "Element Of"),
    LaTeXSymbol("∉", "\\notin", "Not Element Of"),
    LaTeXSymbol("⊂", "\\subset", "Subset"),
    LaTeXSymbol("⊃", "\\supset", "Superset"),
    LaTeXSymbol("⊆", "\\subseteq", "Subset or Equal"),
    LaTeXSymbol("⊇", "\\supseteq", "Superset or Equal"),
    LaTeXSymbol("∪", "\\cup", "Union"),
    LaTeXSymbol("∩", "\\cap", "Intersection"),
    LaTeXSymbol("∅", "\\emptyset", "Empty Set"),
    LaTeXSymbol("ℕ", "\\mathbb{N}", "Natural Numbers"),
    LaTeXSymbol("ℤ", "\\mathbb{Z}", "Integers"),
    LaTeXSymbol("ℚ", "\\mathbb{Q}", "Rationals"),
    LaTeXSymbol("ℝ", "\\mathbb{R}", "Real Numbers"),
    LaTeXSymbol("ℂ", "\\mathbb{C}", "Complex Numbers"),
]

LOGIC = [
    LaTeXSymbol("∧", "\\land", "And"),
    LaTeXSymbol("∨", "\\lor", "Or"),
    LaTeXSymbol("¬", "\\neg", "Not"),
    LaTeXSymbol("∀", "\\forall", "For All"),
    LaTeXSymbol("∃", "\\exists", "There Exists"),
    LaTeXSymbol("∄", "\\nexists", "Not Exists"),
    LaTeXSymbol("⊤", "\\top", "True"),
    LaTeXSymbol("⊥", "\\bot", "False"),
    LaTeXSymbol("⊢", "\\vdash", "Proves"),
    LaTeXSymbol("⊨", "\\models", "Models"),
]

MISCELLANEOUS = [
    LaTeXSymbol("∞", "\\infty", "Infinity"),
    LaTeXSymbol("ℏ", "\\hbar", "Reduced Planck"),
    LaTeXSymbol("ℜ", "\\Re", "Real Part"),
    LaTeXSymbol("ℑ", "\\Im", "Imaginary Part"),
    LaTeXSymbol("∠", "\\angle", "Angle"),
    LaTeXSymbol("°", "^\\circ", "Degree"),
    LaTeXSymbol("′", "'", "Prime"),
    LaTeXSymbol("″", "''", "Double Prime"),
    LaTeXSymbol("∴", "\\therefore", "Therefore"),
    LaTeXSymbol("∵", "\\because", "Because"),
    LaTeXSymbol("†", "\\dagger", "Dagger"),
    LaTeXSymbol("‡", "\\ddagger", "Double Dagger"),
    LaTeXSymbol("…", "\\ldots", "Ellipsis"),
    LaTeXSymbol("⋮", "\\vdots", "Vertical Dots"),
    LaTeXSymbol("⋱", "\\ddots", "Diagonal Dots"),
]

ACCENTS = [
    LaTeXSymbol("â", "\\hat{a}", "Hat"),
    LaTeXSymbol("ǎ", "\\check{a}", "Check"),
    LaTeXSymbol("ā", "\\bar{a}", "Bar"),
    LaTeXSymbol("á", "\\acute{a}", "Acute"),
    LaTeXSymbol("à", "\\grave{a}", "Grave"),
    LaTeXSymbol("ȧ", "\\dot{a}", "Dot"),
    LaTeXSymbol("ä", "\\ddot{a}", "Double Dot"),
    LaTeXSymbol("ã", "\\tilde{a}", "Tilde"),
    LaTeXSymbol("a⃗", "\\vec{a}", "Vector"),
]

# ============================================================================
# LATEX TEMPLATES
# ============================================================================

MATH_TEMPLATES = {
    "Basic": [
        ("Fraction", "\\frac{numerator}{denominator}"),
        ("Power", "x^{exponent}"),
        ("Subscript", "x_{subscript}"),
        ("Square Root", "\\sqrt{expression}"),
        ("Nth Root", "\\sqrt[n]{expression}"),
        ("Absolute Value", "|x|"),
        ("Norm", "\\|x\\|"),
    ],
    
    "Calculus": [
        ("Limit", "\\lim_{x \\to \\infty} f(x)"),
        ("Derivative", "\\frac{d}{dx} f(x)"),
        ("Partial Derivative", "\\frac{\\partial f}{\\partial x}"),
        ("Integral", "\\int_{a}^{b} f(x) \\, dx"),
        ("Double Integral", "\\iint_{D} f(x,y) \\, dA"),
        ("Triple Integral", "\\iiint_{V} f(x,y,z) \\, dV"),
        ("Summation", "\\sum_{i=1}^{n} a_i"),
        ("Product", "\\prod_{i=1}^{n} a_i"),
    ],
    
    "Linear Algebra": [
        ("Matrix 2x2", "\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}"),
        ("Matrix 3x3", "\\begin{pmatrix} a & b & c \\\\ d & e & f \\\\ g & h & i \\end{pmatrix}"),
        ("Determinant", "\\begin{vmatrix} a & b \\\\ c & d \\end{vmatrix}"),
        ("Vector", "\\begin{pmatrix} x \\\\ y \\\\ z \\end{pmatrix}"),
        ("Dot Product", "\\vec{a} \\cdot \\vec{b}"),
        ("Cross Product", "\\vec{a} \\times \\vec{b}"),
        ("Transpose", "A^T"),
        ("Inverse", "A^{-1}"),
    ],
    
    "Trigonometry": [
        ("Sine", "\\sin(x)"),
        ("Cosine", "\\cos(x)"),
        ("Tangent", "\\tan(x)"),
        ("Arcsine", "\\arcsin(x)"),
        ("Arccosine", "\\arccos(x)"),
        ("Arctangent", "\\arctan(x)"),
        ("Pythagorean", "a^2 + b^2 = c^2"),
        ("Sine Law", "\\frac{\\sin A}{a} = \\frac{\\sin B}{b} = \\frac{\\sin C}{c}"),
    ],
    
    "Physics": [
        ("Energy", "E = mc^2"),
        ("Force", "F = ma"),
        ("Newton's 2nd", "\\vec{F} = m\\vec{a}"),
        ("Kinetic Energy", "K = \\frac{1}{2}mv^2"),
        ("Potential Energy", "U = mgh"),
        ("Wave Equation", "v = f\\lambda"),
        ("Schrödinger", "i\\hbar\\frac{\\partial}{\\partial t}\\Psi = \\hat{H}\\Psi"),
        ("Maxwell", "\\nabla \\times \\vec{E} = -\\frac{\\partial \\vec{B}}{\\partial t}"),
    ],
    
    "Statistics": [
        ("Mean", "\\mu = \\frac{1}{n}\\sum_{i=1}^{n} x_i"),
        ("Variance", "\\sigma^2 = \\frac{1}{n}\\sum_{i=1}^{n} (x_i - \\mu)^2"),
        ("Std Deviation", "\\sigma = \\sqrt{\\sigma^2}"),
        ("Normal Distribution", "f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}}"),
        ("Binomial", "P(X=k) = \\binom{n}{k} p^k (1-p)^{n-k}"),
        ("Poisson", "P(X=k) = \\frac{\\lambda^k e^{-\\lambda}}{k!}"),
    ],
    
    "Logic": [
        ("Implication", "P \\Rightarrow Q"),
        ("Equivalence", "P \\Leftrightarrow Q"),
        ("Conjunction", "P \\land Q"),
        ("Disjunction", "P \\lor Q"),
        ("Negation", "\\neg P"),
        ("Universal", "\\forall x \\in X, P(x)"),
        ("Existential", "\\exists x \\in X, P(x)"),
    ],
}


# ============================================================================
# SYMBOL REGISTRY
# ============================================================================

LATEX_SYMBOLS: Dict[str, List[LaTeXSymbol]] = {
    "Greek (Lowercase)": GREEK_LOWERCASE,
    "Greek (Uppercase)": GREEK_UPPERCASE,
    "Operators": OPERATORS,
    "Relations": RELATIONS,
    "Arrows": ARROWS,
    "Set Theory": SET_THEORY,
    "Logic": LOGIC,
    "Accents": ACCENTS,
    "Miscellaneous": MISCELLANEOUS,
}


def get_symbol_by_name(name: str) -> Optional[LaTeXSymbol]:
    """
    Find a symbol by its name (case-insensitive).
    
    **Args**:
        name: Symbol name (e.g., "alpha", "pi", "infinity")
    
    **Returns**:
        LaTeXSymbol or None if not found
    """
    name_lower = name.lower()
    
    for category in LATEX_SYMBOLS.values():
        for symbol in category:
            if symbol.name.lower() == name_lower:
                return symbol
    
    return None


def get_all_symbols() -> List[LaTeXSymbol]:
    """Get a flat list of all symbols."""
    all_symbols = []
    for category in LATEX_SYMBOLS.values():
        all_symbols.extend(category)
    return all_symbols


def search_symbols(query: str) -> List[LaTeXSymbol]:
    """
    Search symbols by name or LaTeX command.
    
    **Args**:
        query: Search string (e.g., "alpha", "\\sum")
    
    **Returns**:
        List of matching symbols
    """
    query_lower = query.lower()
    results = []
    
    for symbol in get_all_symbols():
        if (query_lower in symbol.name.lower() or
            query_lower in symbol.latex.lower() or
            query_lower in symbol.unicode):
            results.append(symbol)
    
    return results
