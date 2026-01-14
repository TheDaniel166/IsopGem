"""
LaTeX Templates - Pre-built Equation Templates.

**Purpose**:
Provide categorized, ready-to-use LaTeX equation templates for common
mathematical domains (Calculus, Algebra, Geometry, Statistics, Physics).

**Usage**:
```python
from .latex_templates import LATEX_TEMPLATES, create_template

# Get template
template = LATEX_TEMPLATES["Derivative"]
latex_code = template["latex_code"]

# Or use AST-based creation
template_ast = create_template("Derivative")
```
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class LaTeXTemplate:
    """
    A LaTeX equation template.
    
    **Attributes**:
        name: Display name
        category: Category (Calculus, Algebra, etc.)
        description: Human-readable description
        latex_code: The LaTeX code
        placeholders: List of placeholder variable names
    """
    name: str
    category: str
    description: str
    latex_code: str
    placeholders: List[str]


# ============================================================================
# TEMPLATE DEFINITIONS
# ============================================================================

LATEX_TEMPLATES: Dict[str, Dict[str, str]] = {
    # ========================================================================
    # CALCULUS
    # ========================================================================
    "Limit Definition": {
        "category": "Calculus",
        "description": "Limit of a function",
        "latex_code": r"\lim_{x \to a} f(x) = L",
        "placeholders": ["x", "a", "f", "L"]
    },
    
    "Derivative": {
        "category": "Calculus",
        "description": "Derivative notation",
        "latex_code": r"\frac{dy}{dx} = f'(x)",
        "placeholders": ["y", "x", "f"]
    },
    
    "Integral": {
        "category": "Calculus",
        "description": "Definite integral",
        "latex_code": r"\int_{a}^{b} f(x) \, dx",
        "placeholders": ["a", "b", "f", "x"]
    },
    
    "Partial Derivative": {
        "category": "Calculus",
        "description": "Partial derivative",
        "latex_code": r"\frac{\partial f}{\partial x}",
        "placeholders": ["f", "x"]
    },
    
    "Taylor Series": {
        "category": "Calculus",
        "description": "Taylor series expansion",
        "latex_code": r"f(x) = \sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!}(x-a)^n",
        "placeholders": ["f", "x", "a", "n"]
    },
    
    "Chain Rule": {
        "category": "Calculus",
        "description": "Chain rule for derivatives",
        "latex_code": r"\frac{d}{dx}[f(g(x))] = f'(g(x)) \cdot g'(x)",
        "placeholders": ["f", "g", "x"]
    },
    
    "Integration by Parts": {
        "category": "Calculus",
        "description": "Integration by parts formula",
        "latex_code": r"\int u \, dv = uv - \int v \, du",
        "placeholders": ["u", "v"]
    },
    
    # ========================================================================
    # ALGEBRA
    # ========================================================================
    "Quadratic Formula": {
        "category": "Algebra",
        "description": "Solve ax²+bx+c=0",
        "latex_code": r"x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}",
        "placeholders": ["x", "a", "b", "c"]
    },
    
    "Binomial Theorem": {
        "category": "Algebra",
        "description": "Binomial expansion",
        "latex_code": r"(a+b)^n = \sum_{k=0}^{n} \binom{n}{k} a^{n-k} b^k",
        "placeholders": ["a", "b", "n", "k"]
    },
    
    "Exponential Identity": {
        "category": "Algebra",
        "description": "Euler's formula",
        "latex_code": r"e^{i\theta} = \cos\theta + i\sin\theta",
        "placeholders": ["theta"]
    },
    
    "Logarithm Laws": {
        "category": "Algebra",
        "description": "Logarithm product rule",
        "latex_code": r"\log(xy) = \log x + \log y",
        "placeholders": ["x", "y"]
    },
    
    "Polynomial": {
        "category": "Algebra",
        "description": "General polynomial",
        "latex_code": r"p(x) = a_n x^n + a_{n-1} x^{n-1} + \cdots + a_1 x + a_0",
        "placeholders": ["x", "n"]
    },
    
    # ========================================================================
    # GEOMETRY
    # ========================================================================
    "Pythagorean Theorem": {
        "category": "Geometry",
        "description": "Right triangle relationship",
        "latex_code": r"a^2 + b^2 = c^2",
        "placeholders": ["a", "b", "c"]
    },
    
    "Circle Equation": {
        "category": "Geometry",
        "description": "Equation of a circle",
        "latex_code": r"(x-h)^2 + (y-k)^2 = r^2",
        "placeholders": ["x", "y", "h", "k", "r"]
    },
    
    "Distance Formula": {
        "category": "Geometry",
        "description": "Distance between two points",
        "latex_code": r"d = \sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}",
        "placeholders": ["d", "x_1", "y_1", "x_2", "y_2"]
    },
    
    "Area of Circle": {
        "category": "Geometry",
        "description": "Area of a circle",
        "latex_code": r"A = \pi r^2",
        "placeholders": ["A", "r"]
    },
    
    "Volume of Sphere": {
        "category": "Geometry",
        "description": "Volume of a sphere",
        "latex_code": r"V = \frac{4}{3}\pi r^3",
        "placeholders": ["V", "r"]
    },
    
    "Surface Area of Sphere": {
        "category": "Geometry",
        "description": "Surface area of a sphere",
        "latex_code": r"A = 4\pi r^2",
        "placeholders": ["A", "r"]
    },
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    "Normal Distribution": {
        "category": "Statistics",
        "description": "Gaussian/normal distribution PDF",
        "latex_code": r"f(x) = \frac{1}{\sigma\sqrt{2\pi}} e^{-\frac{(x-\mu)^2}{2\sigma^2}}",
        "placeholders": ["x", "mu", "sigma"]
    },
    
    "Mean": {
        "category": "Statistics",
        "description": "Arithmetic mean",
        "latex_code": r"\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i",
        "placeholders": ["x", "n", "i"]
    },
    
    "Standard Deviation": {
        "category": "Statistics",
        "description": "Population standard deviation",
        "latex_code": r"\sigma = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(x_i - \mu)^2}",
        "placeholders": ["sigma", "n", "i", "x", "mu"]
    },
    
    "Variance": {
        "category": "Statistics",
        "description": "Population variance",
        "latex_code": r"\sigma^2 = \frac{1}{n}\sum_{i=1}^{n}(x_i - \mu)^2",
        "placeholders": ["sigma", "n", "i", "x", "mu"]
    },
    
    "Probability": {
        "category": "Statistics",
        "description": "Basic probability",
        "latex_code": r"P(A) = \frac{n(A)}{n(S)}",
        "placeholders": ["A", "S"]
    },
    
    "Bayes Theorem": {
        "category": "Statistics",
        "description": "Bayes' theorem",
        "latex_code": r"P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}",
        "placeholders": ["A", "B"]
    },
    
    # ========================================================================
    # PHYSICS
    # ========================================================================
    "Energy-Mass Equivalence": {
        "category": "Physics",
        "description": "Einstein's famous equation",
        "latex_code": r"E = mc^2",
        "placeholders": ["E", "m", "c"]
    },
    
    "Newton's Second Law": {
        "category": "Physics",
        "description": "Force equals mass times acceleration",
        "latex_code": r"F = ma",
        "placeholders": ["F", "m", "a"]
    },
    
    "Kinetic Energy": {
        "category": "Physics",
        "description": "Energy of motion",
        "latex_code": r"K = \frac{1}{2}mv^2",
        "placeholders": ["K", "m", "v"]
    },
    
    "Potential Energy": {
        "category": "Physics",
        "description": "Gravitational potential energy",
        "latex_code": r"U = mgh",
        "placeholders": ["U", "m", "g", "h"]
    },
    
    "Wave Equation": {
        "category": "Physics",
        "description": "One-dimensional wave equation",
        "latex_code": r"\frac{\partial^2 u}{\partial t^2} = c^2 \frac{\partial^2 u}{\partial x^2}",
        "placeholders": ["u", "t", "c", "x"]
    },
    
    "Ohm's Law": {
        "category": "Physics",
        "description": "Voltage, current, resistance relationship",
        "latex_code": r"V = IR",
        "placeholders": ["V", "I", "R"]
    },
    
    "Power": {
        "category": "Physics",
        "description": "Electrical power",
        "latex_code": r"P = IV",
        "placeholders": ["P", "I", "V"]
    },
    
    "Gravitational Force": {
        "category": "Physics",
        "description": "Newton's law of universal gravitation",
        "latex_code": r"F = G\frac{m_1 m_2}{r^2}",
        "placeholders": ["F", "G", "m_1", "m_2", "r"]
    },
}


# ============================================================================
# TEMPLATE CREATION
# ============================================================================

def create_template(name: str) -> Optional[LaTeXTemplate]:
    """
    Create a LaTeXTemplate object from a template name.
    
    **Args**:
        name: Template name (must exist in LATEX_TEMPLATES)
    
    **Returns**:
        LaTeXTemplate object or None if not found
    
    **Example**:
    ```python
    template = create_template("Derivative")
    print(template.latex_code)  # "\\frac{dy}{dx} = f'(x)"
    ```
    """
    if name not in LATEX_TEMPLATES:
        return None
    
    data = LATEX_TEMPLATES[name]
    
    return LaTeXTemplate(
        name=name,
        category=data["category"],
        description=data["description"],
        latex_code=data["latex_code"],
        placeholders=data.get("placeholders", [])
    )


def get_templates_by_category(category: str) -> List[LaTeXTemplate]:
    """
    Get all templates in a specific category.
    
    **Args**:
        category: Category name (e.g., "Calculus", "Physics")
    
    **Returns**:
        List of LaTeXTemplate objects
    
    **Example**:
    ```python
    physics_templates = get_templates_by_category("Physics")
    for template in physics_templates:
        print(template.name, template.latex_code)
    ```
    """
    templates = []
    
    for name, data in LATEX_TEMPLATES.items():
        if data["category"] == category:
            templates.append(create_template(name))
    
    return templates


def get_all_categories() -> List[str]:
    """
    Get all unique category names.
    
    **Returns**:
        Sorted list of category names
    """
    categories = set(data["category"] for data in LATEX_TEMPLATES.values())
    return sorted(categories)


def get_all_templates() -> List[LaTeXTemplate]:
    """
    Get all templates.
    
    **Returns**:
        List of all LaTeXTemplate objects
    """
    return [create_template(name) for name in LATEX_TEMPLATES.keys()]
