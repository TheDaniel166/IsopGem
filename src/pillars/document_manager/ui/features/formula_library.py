"""
Formula Library - Persistent Storage for Favorite LaTeX Equations.

**Purpose**:
Allow users to save, organize, and quickly access frequently-used formulas.
Stored in a JSON file in the user's config directory.

**Features**:
- Save formulas with name and category
- Search formulas by name or LaTeX code
- Organize by categories
- Import/Export collections
- Recent formulas tracking

**Usage**:
```python
library = FormulaLibrary()

# Save a formula
library.add_formula("Pythagorean", "a^2 + b^2 = c^2", "Geometry")

# Get all formulas in a category
formulas = library.get_by_category("Geometry")

# Search
results = library.search("pythag")

# Get recent
recent = library.get_recent(5)
```
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime

try:
    from config.app_config import get_config
except ImportError:
    # Fallback for when running outside main app context
    def get_config():
        from types import SimpleNamespace
        import tempfile
        return SimpleNamespace(config_dir=tempfile.gettempdir())

logger = logging.getLogger(__name__)


@dataclass
class Formula:
    """
    A saved formula.
    
    **Attributes**:
        name: Display name (e.g., "Pythagorean Theorem")
        latex: LaTeX code
        category: Category name (e.g., "Geometry", "Physics")
        description: Optional description
        tags: Tags for searching
        created_at: ISO timestamp of creation
        last_used: ISO timestamp of last use
        use_count: Number of times used
    """
    name: str
    latex: str
    category: str = "Uncategorized"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: str = ""
    last_used: str = ""
    use_count: int = 0
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_used:
            self.last_used = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Formula":
        """Create from dictionary."""
        return cls(**data)


class FormulaLibrary:
    """
    Manages a collection of saved formulas.
    
    **Storage**:
    Formulas are stored in:
    `{config_dir}/formula_library.json`
    
    **Structure**:
    ```json
    {
        "version": "1.0",
        "formulas": [
            {
                "name": "...",
                "latex": "...",
                "category": "...",
                ...
            }
        ]
    }
    ```
    """
    
    VERSION = "1.0"
    
    def __init__(self, custom_path: Optional[Path] = None):
        """
        Initialize formula library.
        
        **Args**:
            custom_path: Optional custom path for storage (default: uses config dir)
        """
        if custom_path:
            self.storage_path = custom_path
        else:
            config = get_config()
            config_dir = Path(config.config_dir)
            config_dir.mkdir(parents=True, exist_ok=True)
            self.storage_path = config_dir / "formula_library.json"
        
        self.formulas: List[Formula] = []
        self._load()
    
    def _load(self):
        """Load formulas from storage."""
        if not self.storage_path.exists():
            logger.info(f"Formula library not found, creating new: {self.storage_path}")
            self._save()  # Create empty file
            return
        
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            version = data.get("version", "1.0")
            if version != self.VERSION:
                logger.warning(f"Formula library version mismatch: {version} vs {self.VERSION}")
            
            formula_data = data.get("formulas", [])
            self.formulas = [Formula.from_dict(f) for f in formula_data]
            
            logger.info(f"Loaded {len(self.formulas)} formulas from library")
        
        except Exception as e:
            logger.error(f"Failed to load formula library: {e}")
            self.formulas = []
    
    def _save(self):
        """Save formulas to storage."""
        try:
            data = {
                "version": self.VERSION,
                "formulas": [f.to_dict() for f in self.formulas]
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved {len(self.formulas)} formulas to library")
        
        except Exception as e:
            logger.error(f"Failed to save formula library: {e}")
    
    def add_formula(
        self,
        name: str,
        latex: str,
        category: str = "Uncategorized",
        description: str = "",
        tags: Optional[List[str]] = None
    ) -> Formula:
        """
        Add a new formula to the library.
        
        **Args**:
            name: Display name
            latex: LaTeX code
            category: Category name
            description: Optional description
            tags: Optional tags
        
        **Returns**:
            Formula: The created formula
        
        **Example**:
        ```python
        formula = library.add_formula(
            "Energy-Mass",
            "E = mc^2",
            "Physics",
            "Einstein's mass-energy equivalence"
        )
        ```
        """
        # Check for duplicate
        existing = self.get_by_name(name)
        if existing:
            logger.warning(f"Formula '{name}' already exists, updating")
            updated = self.update_formula(name, latex, category, description, tags)
            if updated:
                return updated
        
        formula = Formula(
            name=name,
            latex=latex,
            category=category,
            description=description,
            tags=tags or []
        )
        
        self.formulas.append(formula)
        self._save()
        
        logger.info(f"Added formula: {name}")
        return formula
    
    def update_formula(
        self,
        name: str,
        latex: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Formula]:
        """
        Update an existing formula.
        
        **Args**:
            name: Formula name to update
            latex: New LaTeX code (if provided)
            category: New category (if provided)
            description: New description (if provided)
            tags: New tags (if provided)
        
        **Returns**:
            Formula or None if not found
        """
        formula = self.get_by_name(name)
        if not formula:
            logger.warning(f"Formula '{name}' not found for update")
            return None
        
        if latex is not None:
            formula.latex = latex
        if category is not None:
            formula.category = category
        if description is not None:
            formula.description = description
        if tags is not None:
            formula.tags = tags
        
        self._save()
        logger.info(f"Updated formula: {name}")
        return formula
    
    def remove_formula(self, name: str) -> bool:
        """
        Remove a formula by name.
        
        **Args**:
            name: Formula name to remove
        
        **Returns**:
            bool: True if removed, False if not found
        """
        for i, formula in enumerate(self.formulas):
            if formula.name == name:
                self.formulas.pop(i)
                self._save()
                logger.info(f"Removed formula: {name}")
                return True
        
        logger.warning(f"Formula '{name}' not found for removal")
        return False
    
    def get_by_name(self, name: str) -> Optional[Formula]:
        """Get a formula by exact name."""
        for formula in self.formulas:
            if formula.name == name:
                return formula
        return None
    
    def get_by_category(self, category: str, hierarchical: bool = True) -> List[Formula]:
        """
        Get all formulas in a category.
        
        **Args**:
            category: Category name
            hierarchical: If True, include subcategories (e.g., "Physics" includes "Physics: Mechanics")
        
        **Returns**:
            List of formulas in that category (and subcategories if hierarchical=True)
        
        **Examples**:
            - `get_by_category("Physics", hierarchical=True)` returns formulas in "Physics", 
              "Physics: Mechanics", "Physics: Quantum", etc.
            - `get_by_category("Physics", hierarchical=False)` returns only exact "Physics" matches
        """
        if hierarchical:
            # Match category and all subcategories (e.g., "Physics" matches "Physics: Mechanics")
            return [f for f in self.formulas if f.category == category or f.category.startswith(category + ":")]
        else:
            # Exact match only
            return [f for f in self.formulas if f.category == category]
    
    def get_categories(self, top_level_only: bool = False) -> List[str]:
        """
        Get all unique category names.
        
        **Args**:
            top_level_only: If True, return only top-level categories (e.g., "Physics" instead of "Physics: Mechanics")
        
        **Returns**:
            Sorted list of category names
        
        **Examples**:
            - `get_categories(top_level_only=False)` returns all categories including subcategories
            - `get_categories(top_level_only=True)` returns only parent categories
        """
        if top_level_only:
            # Extract top-level categories (before first colon)
            categories = set()
            for formula in self.formulas:
                # Get everything before the first colon
                top_cat = formula.category.split(':')[0].strip()
                categories.add(top_cat)
            return sorted(categories)
        else:
            # Return all categories as-is
            categories = set(f.category for f in self.formulas)
            return sorted(categories)
    
    def get_all(self) -> List[Formula]:
        """Get all formulas."""
        return self.formulas.copy()
    
    def search(self, query: str) -> List[Formula]:
        """
        Search formulas by name, LaTeX code, description, or tags.
        
        **Args**:
            query: Search string (case-insensitive)
        
        **Returns**:
            List of matching formulas
        """
        query_lower = query.lower()
        results = []
        
        for formula in self.formulas:
            if (query_lower in formula.name.lower() or
                query_lower in formula.latex.lower() or
                query_lower in formula.description.lower() or
                any(query_lower in tag.lower() for tag in formula.tags)):
                results.append(formula)
        
        return results
    
    def mark_used(self, name: str):
        """
        Mark a formula as used (updates last_used and use_count).
        
        **Args**:
            name: Formula name
        """
        formula = self.get_by_name(name)
        if formula:
            formula.last_used = datetime.now().isoformat()
            formula.use_count += 1
            self._save()
            logger.debug(f"Marked formula '{name}' as used (count: {formula.use_count})")
    
    def get_recent(self, limit: int = 10) -> List[Formula]:
        """
        Get recently used formulas.
        
        **Args**:
            limit: Maximum number to return
        
        **Returns**:
            List of formulas sorted by last_used (most recent first)
        """
        sorted_formulas = sorted(
            self.formulas,
            key=lambda f: f.last_used,
            reverse=True
        )
        return sorted_formulas[:limit]
    
    def get_most_used(self, limit: int = 10) -> List[Formula]:
        """
        Get most frequently used formulas.
        
        **Args**:
            limit: Maximum number to return
        
        **Returns**:
            List of formulas sorted by use_count (most used first)
        """
        sorted_formulas = sorted(
            self.formulas,
            key=lambda f: f.use_count,
            reverse=True
        )
        return sorted_formulas[:limit]
    
    def export_to_file(self, path: Path):
        """
        Export library to a file.
        
        **Args**:
            path: Destination file path
        """
        try:
            data = {
                "version": self.VERSION,
                "exported_at": datetime.now().isoformat(),
                "formulas": [f.to_dict() for f in self.formulas]
            }
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(self.formulas)} formulas to {path}")
        
        except Exception as e:
            logger.error(f"Failed to export library: {e}")
            raise
    
    def import_from_file(self, path: Path, merge: bool = True):
        """
        Import formulas from a file.
        
        **Args**:
            path: Source file path
            merge: If True, merge with existing formulas; if False, replace
        
        **Raises**:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            imported_formulas = [Formula.from_dict(f) for f in data.get("formulas", [])]
            
            if merge:
                # Merge: add imported formulas, skip duplicates by name
                existing_names = {f.name for f in self.formulas}
                new_formulas = [f for f in imported_formulas if f.name not in existing_names]
                self.formulas.extend(new_formulas)
                logger.info(f"Merged {len(new_formulas)} new formulas from {path}")
            else:
                # Replace: clear existing and use imported
                self.formulas = imported_formulas
                logger.info(f"Replaced library with {len(imported_formulas)} formulas from {path}")
            
            self._save()
        
        except FileNotFoundError:
            logger.error(f"Import file not found: {path}")
            raise
        except Exception as e:
            logger.error(f"Failed to import library: {e}")
            raise ValueError(f"Invalid formula library file: {e}")
    
    def clear(self):
        """Remove all formulas."""
        self.formulas.clear()
        self._save()
        logger.info("Cleared formula library")


# ============================================================================
# DEFAULT FORMULAS (Seed the library on first use)
# ============================================================================

DEFAULT_FORMULAS = [
    # ========================================================================
    # PHYSICS - CLASSICAL MECHANICS
    # ========================================================================
    ("Energy-Mass Equivalence", "E = mc^2", "Physics: Relativity", "Einstein's famous equation"),
    ("Newton's Second Law", "F = ma", "Physics: Mechanics", "Force equals mass times acceleration"),
    ("Newton's Third Law", "F_{12} = -F_{21}", "Physics: Mechanics", "Action-reaction pair"),
    ("Newton's Law of Gravitation", "F = G\\frac{m_1 m_2}{r^2}", "Physics: Mechanics", "Universal gravitation"),
    ("Kinetic Energy", "K = \\frac{1}{2}mv^2", "Physics: Mechanics", "Energy of motion"),
    ("Potential Energy (Gravity)", "U = mgh", "Physics: Mechanics", "Gravitational potential energy"),
    ("Work-Energy Theorem", "W = \\Delta K = K_f - K_i", "Physics: Mechanics", "Work changes kinetic energy"),
    ("Power", "P = \\frac{dW}{dt} = \\vec{F} \\cdot \\vec{v}", "Physics: Mechanics", "Rate of energy transfer"),
    ("Momentum", "\\vec{p} = m\\vec{v}", "Physics: Mechanics", "Linear momentum"),
    ("Impulse-Momentum", "\\vec{J} = \\Delta \\vec{p} = \\int \\vec{F} \\, dt", "Physics: Mechanics", "Impulse changes momentum"),
    ("Angular Momentum", "\\vec{L} = \\vec{r} \\times \\vec{p}", "Physics: Mechanics", "Rotational momentum"),
    ("Torque", "\\vec{\\tau} = \\vec{r} \\times \\vec{F}", "Physics: Mechanics", "Rotational force"),
    ("Moment of Inertia (Point)", "I = mr^2", "Physics: Mechanics", "Rotational inertia for point mass"),
    ("Rotational Kinetic Energy", "K = \\frac{1}{2}I\\omega^2", "Physics: Mechanics", "Energy of rotation"),
    ("Centripetal Acceleration", "a_c = \\frac{v^2}{r}", "Physics: Mechanics", "Acceleration toward center"),
    ("Hooke's Law", "F = -kx", "Physics: Mechanics", "Spring force"),
    ("Simple Harmonic Motion", "x(t) = A\\cos(\\omega t + \\phi)", "Physics: Mechanics", "Oscillatory motion"),
    ("Period of Spring", "T = 2\\pi\\sqrt{\\frac{m}{k}}", "Physics: Mechanics", "Oscillation period"),
    ("Period of Pendulum", "T = 2\\pi\\sqrt{\\frac{L}{g}}", "Physics: Mechanics", "Small angle approximation"),
    
    # ========================================================================
    # PHYSICS - ELECTROMAGNETISM
    # ========================================================================
    ("Coulomb's Law", "F = k_e\\frac{q_1 q_2}{r^2}", "Physics: Electromagnetism", "Electric force between charges"),
    ("Electric Field", "\\vec{E} = \\frac{\\vec{F}}{q}", "Physics: Electromagnetism", "Force per unit charge"),
    ("Electric Potential", "V = \\frac{U}{q}", "Physics: Electromagnetism", "Energy per unit charge"),
    ("Gauss's Law", "\\oint \\vec{E} \\cdot d\\vec{A} = \\frac{Q_{enc}}{\\epsilon_0}", "Physics: Electromagnetism", "Electric flux through closed surface"),
    ("Capacitance", "C = \\frac{Q}{V}", "Physics: Electromagnetism", "Charge storage capacity"),
    ("Parallel Plate Capacitor", "C = \\epsilon_0 \\frac{A}{d}", "Physics: Electromagnetism", "Capacitance of parallel plates"),
    ("Energy in Capacitor", "U = \\frac{1}{2}CV^2", "Physics: Electromagnetism", "Stored electrical energy"),
    ("Ohm's Law", "V = IR", "Physics: Electromagnetism", "Voltage-current relationship"),
    ("Resistivity", "R = \\rho\\frac{L}{A}", "Physics: Electromagnetism", "Resistance from material properties"),
    ("Power (Electrical)", "P = IV = I^2R = \\frac{V^2}{R}", "Physics: Electromagnetism", "Electrical power dissipation"),
    ("Kirchhoff's Voltage Law", "\\sum V = 0", "Physics: Electromagnetism", "Sum of voltages in loop is zero"),
    ("Kirchhoff's Current Law", "\\sum I = 0", "Physics: Electromagnetism", "Sum of currents at node is zero"),
    ("Magnetic Force (Lorentz)", "\\vec{F} = q\\vec{v} \\times \\vec{B}", "Physics: Electromagnetism", "Force on moving charge"),
    ("Magnetic Force on Wire", "\\vec{F} = I\\vec{L} \\times \\vec{B}", "Physics: Electromagnetism", "Force on current-carrying wire"),
    ("Biot-Savart Law", "d\\vec{B} = \\frac{\\mu_0}{4\\pi}\\frac{Id\\vec{l} \\times \\hat{r}}{r^2}", "Physics: Electromagnetism", "Magnetic field from current element"),
    ("Ampere's Law", "\\oint \\vec{B} \\cdot d\\vec{l} = \\mu_0 I_{enc}", "Physics: Electromagnetism", "Magnetic field around current"),
    ("Faraday's Law", "\\mathcal{E} = -\\frac{d\\Phi_B}{dt}", "Physics: Electromagnetism", "Induced EMF from changing flux"),
    ("Lenz's Law", "\\mathcal{E} = -N\\frac{d\\Phi}{dt}", "Physics: Electromagnetism", "Direction of induced current"),
    ("Inductance", "\\mathcal{E} = -L\\frac{dI}{dt}", "Physics: Electromagnetism", "Self-inductance"),
    ("Energy in Inductor", "U = \\frac{1}{2}LI^2", "Physics: Electromagnetism", "Magnetic energy storage"),
    ("Maxwell-Faraday Equation", "\\nabla \\times \\vec{E} = -\\frac{\\partial \\vec{B}}{\\partial t}", "Physics: Electromagnetism", "Faraday's law in differential form"),
    ("Maxwell-Ampere Equation", "\\nabla \\times \\vec{B} = \\mu_0\\vec{J} + \\mu_0\\epsilon_0\\frac{\\partial \\vec{E}}{\\partial t}", "Physics: Electromagnetism", "Ampere's law with displacement current"),
    
    # ========================================================================
    # PHYSICS - WAVES & OPTICS
    # ========================================================================
    ("Wave Speed", "v = f\\lambda", "Physics: Waves", "Relationship between frequency and wavelength"),
    ("Wave Equation (1D)", "\\frac{\\partial^2 y}{\\partial t^2} = v^2\\frac{\\partial^2 y}{\\partial x^2}", "Physics: Waves", "Classical wave equation"),
    ("Doppler Effect", "f' = f\\frac{v \\pm v_o}{v \\mp v_s}", "Physics: Waves", "Frequency shift due to motion"),
    ("Snell's Law", "n_1\\sin\\theta_1 = n_2\\sin\\theta_2", "Physics: Optics", "Refraction at interface"),
    ("Lens Equation", "\\frac{1}{f} = \\frac{1}{d_o} + \\frac{1}{d_i}", "Physics: Optics", "Thin lens formula"),
    ("Magnification", "m = -\\frac{d_i}{d_o} = \\frac{h_i}{h_o}", "Physics: Optics", "Image size ratio"),
    ("Double Slit Interference", "d\\sin\\theta = m\\lambda", "Physics: Optics", "Constructive interference condition"),
    ("Single Slit Diffraction", "a\\sin\\theta = m\\lambda", "Physics: Optics", "Minima condition"),
    ("Bragg's Law", "n\\lambda = 2d\\sin\\theta", "Physics: Optics", "X-ray diffraction in crystals"),
    ("Rayleigh Criterion", "\\theta_{min} = 1.22\\frac{\\lambda}{D}", "Physics: Optics", "Minimum resolvable angle"),
    
    # ========================================================================
    # PHYSICS - THERMODYNAMICS
    # ========================================================================
    ("Ideal Gas Law", "PV = nRT", "Physics: Thermodynamics", "Equation of state for ideal gas"),
    ("First Law of Thermodynamics", "\\Delta U = Q - W", "Physics: Thermodynamics", "Energy conservation"),
    ("Second Law (Entropy)", "dS \\geq \\frac{dQ}{T}", "Physics: Thermodynamics", "Entropy increases"),
    ("Entropy Change", "\\Delta S = nR\\ln\\frac{V_f}{V_i}", "Physics: Thermodynamics", "Isothermal process"),
    ("Heat Transfer", "Q = mc\\Delta T", "Physics: Thermodynamics", "Sensible heat"),
    ("Latent Heat", "Q = mL", "Physics: Thermodynamics", "Phase change energy"),
    ("Carnot Efficiency", "\\eta = 1 - \\frac{T_C}{T_H}", "Physics: Thermodynamics", "Maximum heat engine efficiency"),
    ("Stefan-Boltzmann Law", "P = \\sigma A T^4", "Physics: Thermodynamics", "Blackbody radiation power"),
    ("Boltzmann Distribution", "n_i = n_0 e^{-E_i/kT}", "Physics: Thermodynamics", "Energy state population"),
    
    # ========================================================================
    # PHYSICS - QUANTUM MECHANICS
    # ========================================================================
    ("Planck-Einstein Relation", "E = hf = \\hbar\\omega", "Physics: Quantum", "Energy of photon"),
    ("de Broglie Wavelength", "\\lambda = \\frac{h}{p}", "Physics: Quantum", "Matter wave wavelength"),
    ("Heisenberg Uncertainty", "\\Delta x \\Delta p \\geq \\frac{\\hbar}{2}", "Physics: Quantum", "Position-momentum uncertainty"),
    ("Schrödinger Equation (Time)", "i\\hbar\\frac{\\partial\\psi}{\\partial t} = \\hat{H}\\psi", "Physics: Quantum", "Time-dependent wave equation"),
    ("Schrödinger Equation (Time-Ind)", "\\hat{H}\\psi = E\\psi", "Physics: Quantum", "Time-independent eigenvalue equation"),
    ("Particle in Box (Energy)", "E_n = \\frac{n^2\\pi^2\\hbar^2}{2mL^2}", "Physics: Quantum", "Quantized energy levels"),
    ("Harmonic Oscillator (Energy)", "E_n = \\hbar\\omega\\left(n + \\frac{1}{2}\\right)", "Physics: Quantum", "Quantum oscillator levels"),
    ("Hydrogen Atom Energy", "E_n = -\\frac{13.6 \\text{ eV}}{n^2}", "Physics: Quantum", "Bohr model energy levels"),
    ("Compton Scattering", "\\lambda' - \\lambda = \\frac{h}{m_e c}(1 - \\cos\\theta)", "Physics: Quantum", "Photon-electron scattering"),
    
    # ========================================================================
    # PHYSICS - SPECIAL RELATIVITY
    # ========================================================================
    ("Time Dilation", "\\Delta t = \\frac{\\Delta t_0}{\\sqrt{1 - v^2/c^2}}", "Physics: Relativity", "Moving clocks run slow"),
    ("Length Contraction", "L = L_0\\sqrt{1 - v^2/c^2}", "Physics: Relativity", "Moving objects contract"),
    ("Lorentz Factor", "\\gamma = \\frac{1}{\\sqrt{1 - v^2/c^2}}", "Physics: Relativity", "Relativistic correction factor"),
    ("Relativistic Momentum", "\\vec{p} = \\gamma m\\vec{v}", "Physics: Relativity", "Momentum at high speeds"),
    ("Relativistic Energy", "E = \\gamma mc^2", "Physics: Relativity", "Total energy"),
    ("Energy-Momentum Relation", "E^2 = (pc)^2 + (mc^2)^2", "Physics: Relativity", "Invariant mass relation"),
    
    # ========================================================================
    # CALCULUS - SINGLE VARIABLE
    # ========================================================================
    ("Derivative Definition", "f'(x) = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}", "Calculus: Derivatives", "Limit definition of derivative"),
    ("Power Rule", "\\frac{d}{dx}x^n = nx^{n-1}", "Calculus: Derivatives", "Derivative of power"),
    ("Product Rule", "\\frac{d}{dx}[f(x)g(x)] = f'(x)g(x) + f(x)g'(x)", "Calculus: Derivatives", "Derivative of product"),
    ("Quotient Rule", "\\frac{d}{dx}\\left[\\frac{f(x)}{g(x)}\\right] = \\frac{f'(x)g(x) - f(x)g'(x)}{[g(x)]^2}", "Calculus: Derivatives", "Derivative of quotient"),
    ("Chain Rule", "\\frac{d}{dx}f(g(x)) = f'(g(x))g'(x)", "Calculus: Derivatives", "Derivative of composition"),
    ("L'Hôpital's Rule", "\\lim_{x \\to a}\\frac{f(x)}{g(x)} = \\lim_{x \\to a}\\frac{f'(x)}{g'(x)}", "Calculus: Limits", "Limit of indeterminate forms"),
    ("Fundamental Theorem I", "\\frac{d}{dx}\\int_a^x f(t) \\, dt = f(x)", "Calculus: Integration", "Derivative of integral"),
    ("Fundamental Theorem II", "\\int_{a}^{b} f'(x) \\, dx = f(b) - f(a)", "Calculus: Integration", "Integral evaluates to antiderivative"),
    ("Integration by Parts", "\\int u \\, dv = uv - \\int v \\, du", "Calculus: Integration", "Product integration technique"),
    ("U-Substitution", "\\int f(g(x))g'(x) \\, dx = \\int f(u) \\, du", "Calculus: Integration", "Change of variables"),
    
    # ========================================================================
    # CALCULUS - MULTIVARIABLE
    # ========================================================================
    ("Partial Derivative", "\\frac{\\partial f}{\\partial x} = \\lim_{h \\to 0}\\frac{f(x+h,y) - f(x,y)}{h}", "Calculus: Multivariable", "Derivative holding other variables constant"),
    ("Gradient", "\\nabla f = \\frac{\\partial f}{\\partial x}\\hat{i} + \\frac{\\partial f}{\\partial y}\\hat{j} + \\frac{\\partial f}{\\partial z}\\hat{k}", "Calculus: Multivariable", "Vector of partial derivatives"),
    ("Directional Derivative", "D_{\\vec{u}}f = \\nabla f \\cdot \\vec{u}", "Calculus: Multivariable", "Derivative in direction u"),
    ("Divergence", "\\nabla \\cdot \\vec{F} = \\frac{\\partial F_x}{\\partial x} + \\frac{\\partial F_y}{\\partial y} + \\frac{\\partial F_z}{\\partial z}", "Calculus: Multivariable", "Scalar field from vector field"),
    ("Curl", "\\nabla \\times \\vec{F} = \\left(\\frac{\\partial F_z}{\\partial y} - \\frac{\\partial F_y}{\\partial z}\\right)\\hat{i} + \\cdots", "Calculus: Multivariable", "Rotation of vector field"),
    ("Laplacian", "\\nabla^2 f = \\frac{\\partial^2 f}{\\partial x^2} + \\frac{\\partial^2 f}{\\partial y^2} + \\frac{\\partial^2 f}{\\partial z^2}", "Calculus: Multivariable", "Sum of second derivatives"),
    ("Green's Theorem", "\\oint_C (P \\, dx + Q \\, dy) = \\iint_D \\left(\\frac{\\partial Q}{\\partial x} - \\frac{\\partial P}{\\partial y}\\right) dA", "Calculus: Multivariable", "Line integral to double integral"),
    ("Stokes' Theorem", "\\oint_C \\vec{F} \\cdot d\\vec{r} = \\iint_S (\\nabla \\times \\vec{F}) \\cdot d\\vec{S}", "Calculus: Multivariable", "Line integral to surface integral"),
    ("Divergence Theorem", "\\iiint_V (\\nabla \\cdot \\vec{F}) \\, dV = \\oiint_S \\vec{F} \\cdot d\\vec{S}", "Calculus: Multivariable", "Volume integral to surface integral"),
    
    # ========================================================================
    # CALCULUS - SERIES & SEQUENCES
    # ========================================================================
    ("Taylor Series", "f(x) = \\sum_{n=0}^{\\infty} \\frac{f^{(n)}(a)}{n!}(x-a)^n", "Calculus: Series", "Function expansion around point a"),
    ("Maclaurin Series", "f(x) = \\sum_{n=0}^{\\infty} \\frac{f^{(n)}(0)}{n!}x^n", "Calculus: Series", "Taylor series at x=0"),
    ("Exponential Series", "e^x = \\sum_{n=0}^{\\infty} \\frac{x^n}{n!}", "Calculus: Series", "Maclaurin series for e^x"),
    ("Sine Series", "\\sin x = \\sum_{n=0}^{\\infty} \\frac{(-1)^n x^{2n+1}}{(2n+1)!}", "Calculus: Series", "Maclaurin series for sine"),
    ("Cosine Series", "\\cos x = \\sum_{n=0}^{\\infty} \\frac{(-1)^n x^{2n}}{(2n)!}", "Calculus: Series", "Maclaurin series for cosine"),
    ("Geometric Series", "\\sum_{n=0}^{\\infty} ar^n = \\frac{a}{1-r}, \\quad |r| < 1", "Calculus: Series", "Infinite geometric series sum"),
    ("Ratio Test", "\\lim_{n \\to \\infty} \\left|\\frac{a_{n+1}}{a_n}\\right| < 1", "Calculus: Series", "Convergence test"),
    ("P-Series", "\\sum_{n=1}^{\\infty} \\frac{1}{n^p} \\text{ converges if } p > 1", "Calculus: Series", "Convergence of p-series"),
    
    # ========================================================================
    # ALGEBRA - BASICS
    # ========================================================================
    ("Quadratic Formula", "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}", "Algebra", "Solve ax²+bx+c=0"),
    ("Discriminant", "\\Delta = b^2 - 4ac", "Algebra", "Determines nature of roots"),
    ("Binomial Theorem", "(a+b)^n = \\sum_{k=0}^{n} \\binom{n}{k} a^{n-k} b^k", "Algebra", "Binomial expansion"),
    ("Difference of Squares", "a^2 - b^2 = (a+b)(a-b)", "Algebra", "Factoring identity"),
    ("Sum of Cubes", "a^3 + b^3 = (a+b)(a^2 - ab + b^2)", "Algebra", "Factoring identity"),
    ("Difference of Cubes", "a^3 - b^3 = (a-b)(a^2 + ab + b^2)", "Algebra", "Factoring identity"),
    ("Euler's Formula", "e^{i\\theta} = \\cos\\theta + i\\sin\\theta", "Algebra: Complex", "Complex exponential"),
    ("Euler's Identity", "e^{i\\pi} + 1 = 0", "Algebra: Complex", "Beautiful identity"),
    ("De Moivre's Theorem", "(\\cos\\theta + i\\sin\\theta)^n = \\cos(n\\theta) + i\\sin(n\\theta)", "Algebra: Complex", "Powers of complex numbers"),
    
    # ========================================================================
    # LINEAR ALGEBRA
    # ========================================================================
    ("Matrix Multiplication", "(AB)_{ij} = \\sum_k A_{ik}B_{kj}", "Linear Algebra", "Product of matrices"),
    ("Determinant (2x2)", "\\det(A) = ad - bc", "Linear Algebra", "For 2×2 matrix"),
    ("Determinant (3x3)", "\\det(A) = a_{11}(a_{22}a_{33} - a_{23}a_{32}) - \\cdots", "Linear Algebra", "Cofactor expansion"),
    ("Matrix Inverse", "AA^{-1} = I", "Linear Algebra", "Inverse matrix property"),
    ("Cramer's Rule", "x_i = \\frac{\\det(A_i)}{\\det(A)}", "Linear Algebra", "Solve linear system"),
    ("Eigenvalue Equation", "A\\vec{v} = \\lambda\\vec{v}", "Linear Algebra", "Eigenvector definition"),
    ("Characteristic Polynomial", "\\det(A - \\lambda I) = 0", "Linear Algebra", "Find eigenvalues"),
    ("Trace", "\\text{tr}(A) = \\sum_i a_{ii} = \\sum_i \\lambda_i", "Linear Algebra", "Sum of diagonal elements"),
    ("Dot Product", "\\vec{a} \\cdot \\vec{b} = \\sum_i a_i b_i = |\\vec{a}||\\vec{b}|\\cos\\theta", "Linear Algebra", "Inner product"),
    ("Cross Product Magnitude", "|\\vec{a} \\times \\vec{b}| = |\\vec{a}||\\vec{b}|\\sin\\theta", "Linear Algebra", "Cross product magnitude"),
    ("Cauchy-Schwarz Inequality", "|\\vec{a} \\cdot \\vec{b}| \\leq |\\vec{a}||\\vec{b}|", "Linear Algebra", "Inner product bound"),
    ("Triangle Inequality", "|\\vec{a} + \\vec{b}| \\leq |\\vec{a}| + |\\vec{b}|", "Linear Algebra", "Vector length inequality"),
    
    # ========================================================================
    # GEOMETRY
    # ========================================================================
    ("Pythagorean Theorem", "a^2 + b^2 = c^2", "Geometry: Euclidean", "Right triangle relationship"),
    ("Distance Formula (2D)", "d = \\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}", "Geometry: Analytic", "Distance between points"),
    ("Distance Formula (3D)", "d = \\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2 + (z_2-z_1)^2}", "Geometry: Analytic", "3D distance"),
    ("Circle Equation", "(x-h)^2 + (y-k)^2 = r^2", "Geometry: Analytic", "Standard form of circle"),
    ("Ellipse Equation", "\\frac{(x-h)^2}{a^2} + \\frac{(y-k)^2}{b^2} = 1", "Geometry: Analytic", "Standard form of ellipse"),
    ("Hyperbola Equation", "\\frac{(x-h)^2}{a^2} - \\frac{(y-k)^2}{b^2} = 1", "Geometry: Analytic", "Standard form of hyperbola"),
    ("Parabola Equation", "y = a(x-h)^2 + k", "Geometry: Analytic", "Vertex form"),
    ("Circle Area", "A = \\pi r^2", "Geometry: Area", "Area of circle"),
    ("Circle Circumference", "C = 2\\pi r", "Geometry: Perimeter", "Circumference of circle"),
    ("Sphere Volume", "V = \\frac{4}{3}\\pi r^3", "Geometry: Volume", "Volume of sphere"),
    ("Sphere Surface Area", "A = 4\\pi r^2", "Geometry: Area", "Surface area of sphere"),
    ("Cylinder Volume", "V = \\pi r^2 h", "Geometry: Volume", "Volume of cylinder"),
    ("Cylinder Surface Area", "A = 2\\pi r^2 + 2\\pi rh", "Geometry: Area", "Total surface area of cylinder"),
    ("Cone Volume", "V = \\frac{1}{3}\\pi r^2 h", "Geometry: Volume", "Volume of cone"),
    ("Triangle Area (Heron)", "A = \\sqrt{s(s-a)(s-b)(s-c)}, \\quad s = \\frac{a+b+c}{2}", "Geometry: Area", "Triangle area from sides"),
    ("Law of Sines", "\\frac{a}{\\sin A} = \\frac{b}{\\sin B} = \\frac{c}{\\sin C}", "Geometry: Trigonometry", "Triangle side-angle relationship"),
    ("Law of Cosines", "c^2 = a^2 + b^2 - 2ab\\cos C", "Geometry: Trigonometry", "Generalized Pythagorean"),
    
    # ========================================================================
    # TRIGONOMETRY
    # ========================================================================
    ("Sine Definition", "\\sin\\theta = \\frac{\\text{opposite}}{\\text{hypotenuse}}", "Trigonometry", "Right triangle ratio"),
    ("Cosine Definition", "\\cos\\theta = \\frac{\\text{adjacent}}{\\text{hypotenuse}}", "Trigonometry", "Right triangle ratio"),
    ("Tangent Definition", "\\tan\\theta = \\frac{\\sin\\theta}{\\cos\\theta} = \\frac{\\text{opposite}}{\\text{adjacent}}", "Trigonometry", "Right triangle ratio"),
    ("Pythagorean Identity", "\\sin^2\\theta + \\cos^2\\theta = 1", "Trigonometry", "Fundamental identity"),
    ("Tangent Identity", "1 + \\tan^2\\theta = \\sec^2\\theta", "Trigonometry", "Derived identity"),
    ("Cotangent Identity", "1 + \\cot^2\\theta = \\csc^2\\theta", "Trigonometry", "Derived identity"),
    ("Angle Sum (Sine)", "\\sin(\\alpha \\pm \\beta) = \\sin\\alpha\\cos\\beta \\pm \\cos\\alpha\\sin\\beta", "Trigonometry", "Sine of sum/difference"),
    ("Angle Sum (Cosine)", "\\cos(\\alpha \\pm \\beta) = \\cos\\alpha\\cos\\beta \\mp \\sin\\alpha\\sin\\beta", "Trigonometry", "Cosine of sum/difference"),
    ("Double Angle (Sine)", "\\sin(2\\theta) = 2\\sin\\theta\\cos\\theta", "Trigonometry", "Double angle formula"),
    ("Double Angle (Cosine)", "\\cos(2\\theta) = \\cos^2\\theta - \\sin^2\\theta", "Trigonometry", "Double angle formula"),
    ("Half Angle (Sine)", "\\sin\\frac{\\theta}{2} = \\pm\\sqrt{\\frac{1-\\cos\\theta}{2}}", "Trigonometry", "Half angle formula"),
    ("Half Angle (Cosine)", "\\cos\\frac{\\theta}{2} = \\pm\\sqrt{\\frac{1+\\cos\\theta}{2}}", "Trigonometry", "Half angle formula"),
    
    # ========================================================================
    # STATISTICS & PROBABILITY
    # ========================================================================
    ("Normal Distribution", "f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}}", "Statistics", "Gaussian distribution PDF"),
    ("Standard Normal", "Z = \\frac{X - \\mu}{\\sigma}", "Statistics", "Z-score transformation"),
    ("Mean (Population)", "\\mu = \\frac{1}{N}\\sum_{i=1}^{N} x_i", "Statistics", "Average of population"),
    ("Mean (Sample)", "\\bar{x} = \\frac{1}{n}\\sum_{i=1}^{n} x_i", "Statistics", "Average of sample"),
    ("Variance (Population)", "\\sigma^2 = \\frac{1}{N}\\sum_{i=1}^{N}(x_i - \\mu)^2", "Statistics", "Population variance"),
    ("Variance (Sample)", "s^2 = \\frac{1}{n-1}\\sum_{i=1}^{n}(x_i - \\bar{x})^2", "Statistics", "Sample variance with Bessel correction"),
    ("Standard Deviation", "\\sigma = \\sqrt{\\sigma^2}", "Statistics", "Square root of variance"),
    ("Covariance", "\\text{Cov}(X,Y) = E[(X-\\mu_X)(Y-\\mu_Y)]", "Statistics", "Joint variability"),
    ("Correlation Coefficient", "\\rho = \\frac{\\text{Cov}(X,Y)}{\\sigma_X \\sigma_Y}", "Statistics", "Standardized covariance"),
    ("Linear Regression (Slope)", "b = \\frac{\\sum(x_i - \\bar{x})(y_i - \\bar{y})}{\\sum(x_i - \\bar{x})^2}", "Statistics", "Least squares slope"),
    ("Linear Regression (Intercept)", "a = \\bar{y} - b\\bar{x}", "Statistics", "Least squares intercept"),
    ("R-Squared", "R^2 = 1 - \\frac{SS_{res}}{SS_{tot}}", "Statistics", "Coefficient of determination"),
    ("Binomial Probability", "P(X=k) = \\binom{n}{k}p^k(1-p)^{n-k}", "Statistics", "Discrete probability"),
    ("Poisson Probability", "P(X=k) = \\frac{\\lambda^k e^{-\\lambda}}{k!}", "Statistics", "Events in interval"),
    ("Exponential Distribution", "f(x) = \\lambda e^{-\\lambda x}", "Statistics", "Continuous waiting time"),
    ("Chi-Square Statistic", "\\chi^2 = \\sum \\frac{(O_i - E_i)^2}{E_i}", "Statistics", "Goodness of fit test"),
    ("T-Statistic", "t = \\frac{\\bar{x} - \\mu}{s/\\sqrt{n}}", "Statistics", "Test statistic for mean"),
    ("Bayes' Theorem", "P(A|B) = \\frac{P(B|A)P(A)}{P(B)}", "Probability", "Conditional probability update"),
    ("Law of Total Probability", "P(B) = \\sum_i P(B|A_i)P(A_i)", "Probability", "Partition theorem"),
    ("Permutations", "P(n,r) = \\frac{n!}{(n-r)!}", "Combinatorics", "Ordered selections"),
    ("Combinations", "C(n,r) = \\binom{n}{r} = \\frac{n!}{r!(n-r)!}", "Combinatorics", "Unordered selections"),
    
    # ========================================================================
    # CHEMISTRY
    # ========================================================================
    ("Ideal Gas Law", "PV = nRT", "Chemistry: Gas Laws", "Equation of state"),
    ("Combined Gas Law", "\\frac{P_1V_1}{T_1} = \\frac{P_2V_2}{T_2}", "Chemistry: Gas Laws", "Combined P, V, T relationship"),
    ("Boyle's Law", "P_1V_1 = P_2V_2", "Chemistry: Gas Laws", "Pressure-volume at constant T"),
    ("Charles's Law", "\\frac{V_1}{T_1} = \\frac{V_2}{T_2}", "Chemistry: Gas Laws", "Volume-temperature at constant P"),
    ("Avogadro's Law", "\\frac{V_1}{n_1} = \\frac{V_2}{n_2}", "Chemistry: Gas Laws", "Volume-moles relationship"),
    ("Van der Waals Equation", "\\left(P + \\frac{an^2}{V^2}\\right)(V - nb) = nRT", "Chemistry: Gas Laws", "Real gas equation"),
    ("Enthalpy Change", "\\Delta H = \\Delta U + P\\Delta V", "Chemistry: Thermodynamics", "Heat at constant pressure"),
    ("Gibbs Free Energy", "\\Delta G = \\Delta H - T\\Delta S", "Chemistry: Thermodynamics", "Spontaneity criterion"),
    ("Entropy Change", "\\Delta S = \\frac{Q_{rev}}{T}", "Chemistry: Thermodynamics", "Reversible heat transfer"),
    ("Nernst Equation", "E = E^\\circ - \\frac{RT}{nF}\\ln Q", "Chemistry: Electrochemistry", "Cell potential"),
    ("Henderson-Hasselbalch", "\\text{pH} = \\text{pK}_a + \\log\\frac{[A^-]}{[HA]}", "Chemistry: Acid-Base", "Buffer pH equation"),
    ("Arrhenius Equation", "k = Ae^{-E_a/RT}", "Chemistry: Kinetics", "Rate constant temperature dependence"),
    ("Integrated Rate Law (1st)", "\\ln[A] = \\ln[A]_0 - kt", "Chemistry: Kinetics", "First-order reaction"),
    ("Integrated Rate Law (2nd)", "\\frac{1}{[A]} = \\frac{1}{[A]_0} + kt", "Chemistry: Kinetics", "Second-order reaction"),
    ("Half-Life (1st Order)", "t_{1/2} = \\frac{\\ln 2}{k}", "Chemistry: Kinetics", "First-order half-life"),
    ("Equilibrium Constant", "K = \\frac{[C]^c[D]^d}{[A]^a[B]^b}", "Chemistry: Equilibrium", "For aA + bB ⇌ cC + dD"),
    ("Reaction Quotient", "Q = \\frac{[C]^c[D]^d}{[A]^a[B]^b}", "Chemistry: Equilibrium", "Non-equilibrium ratio"),
    ("Le Chatelier's Principle", "\\text{System shifts to oppose change}", "Chemistry: Equilibrium", "Response to stress"),
    ("Rydberg Formula", "\\frac{1}{\\lambda} = R_H\\left(\\frac{1}{n_1^2} - \\frac{1}{n_2^2}\\right)", "Chemistry: Quantum", "Hydrogen spectral lines"),
    
    # ========================================================================
    # NUMBER THEORY
    # ========================================================================
    ("Fundamental Theorem of Arithmetic", "n = p_1^{a_1} p_2^{a_2} \\cdots p_k^{a_k}", "Number Theory", "Unique prime factorization"),
    ("Euclidean Algorithm", "\\gcd(a,b) = \\gcd(b, a \\bmod b)", "Number Theory", "Greatest common divisor"),
    ("Fermat's Little Theorem", "a^{p-1} \\equiv 1 \\pmod{p}", "Number Theory", "For prime p and gcd(a,p)=1"),
    ("Euler's Totient Function", "\\phi(n) = n\\prod_{p|n}\\left(1 - \\frac{1}{p}\\right)", "Number Theory", "Count of coprime integers"),
    ("Sum of Divisors", "\\sigma(n) = \\sum_{d|n} d", "Number Theory", "Divisor function"),
    ("Möbius Function", "\\mu(n) = \\begin{cases} 1 & \\text{if } n \\text{ square-free, even primes} \\\\ -1 & \\text{if } n \\text{ square-free, odd primes} \\\\ 0 & \\text{otherwise} \\end{cases}", "Number Theory", "Multiplicative function"),
    
    # ========================================================================
    # DIFFERENTIAL EQUATIONS
    # ========================================================================
    ("First-Order Linear ODE", "\\frac{dy}{dx} + P(x)y = Q(x)", "Differential Equations", "Linear first-order"),
    ("Separable ODE", "\\frac{dy}{dx} = g(x)h(y)", "Differential Equations", "Separable form"),
    ("Homogeneous Linear (2nd)", "ay'' + by' + cy = 0", "Differential Equations", "Second-order homogeneous"),
    ("Characteristic Equation", "ar^2 + br + c = 0", "Differential Equations", "For second-order linear"),
    ("Heat Equation", "\\frac{\\partial u}{\\partial t} = \\alpha\\nabla^2 u", "Differential Equations: PDE", "Heat diffusion"),
    ("Wave Equation", "\\frac{\\partial^2 u}{\\partial t^2} = c^2\\nabla^2 u", "Differential Equations: PDE", "Wave propagation"),
    ("Laplace's Equation", "\\nabla^2 u = 0", "Differential Equations: PDE", "Steady-state potential"),
    ("Poisson's Equation", "\\nabla^2 u = f", "Differential Equations: PDE", "Generalized Laplace"),
    
    # ========================================================================
    # COMPUTER SCIENCE
    # ========================================================================
    ("Big-O Notation", "f(n) = O(g(n)) \\text{ if } \\exists c, n_0: f(n) \\leq cg(n) \\, \\forall n \\geq n_0", "Computer Science", "Upper bound complexity"),
    ("Big-Omega Notation", "f(n) = \\Omega(g(n)) \\text{ if } \\exists c, n_0: f(n) \\geq cg(n) \\, \\forall n \\geq n_0", "Computer Science", "Lower bound complexity"),
    ("Big-Theta Notation", "f(n) = \\Theta(g(n)) \\text{ if } f(n) = O(g(n)) \\text{ and } f(n) = \\Omega(g(n))", "Computer Science", "Tight bound complexity"),
    ("Shannon Entropy", "H(X) = -\\sum_i P(x_i)\\log_2 P(x_i)", "Information Theory", "Information content"),
    ("Mutual Information", "I(X;Y) = H(X) + H(Y) - H(X,Y)", "Information Theory", "Shared information"),
    ("Master Theorem", "T(n) = aT(n/b) + f(n)", "Algorithms", "Divide-and-conquer recurrence"),
    ("Stirling's Approximation", "n! \\approx \\sqrt{2\\pi n}\\left(\\frac{n}{e}\\right)^n", "Algorithms", "Factorial approximation"),
    
    # ========================================================================
    # ECONOMICS & FINANCE
    # ========================================================================
    ("Present Value", "PV = \\frac{FV}{(1+r)^n}", "Finance", "Time value of money"),
    ("Future Value", "FV = PV(1+r)^n", "Finance", "Compound interest"),
    ("Compound Interest", "A = P\\left(1 + \\frac{r}{n}\\right)^{nt}", "Finance", "Interest compounded n times per year"),
    ("Continuous Compounding", "A = Pe^{rt}", "Finance", "Continuous interest"),
    ("Annuity Present Value", "PV = PMT\\frac{1-(1+r)^{-n}}{r}", "Finance", "Present value of payments"),
    ("Bond Price", "P = \\sum_{t=1}^{n}\\frac{C}{(1+r)^t} + \\frac{F}{(1+r)^n}", "Finance", "Discounted cash flows"),
    ("Black-Scholes (Call)", "C = S_0N(d_1) - Ke^{-rt}N(d_2)", "Finance", "Option pricing"),
    ("Elasticity of Demand", "E_d = \\frac{\\%\\Delta Q}{\\%\\Delta P} = \\frac{dQ}{dP}\\frac{P}{Q}", "Economics", "Price sensitivity"),
    ("GDP (Expenditure)", "\\text{GDP} = C + I + G + (X - M)", "Economics", "National accounts identity"),
    ("Money Multiplier", "m = \\frac{1}{r}", "Economics", "Banking multiplier"),
    ("Cobb-Douglas Production", "Y = AK^\\alpha L^{1-\\alpha}", "Economics", "Production function"),
    ("Solow Growth Model", "\\dot{k} = sy - (n+\\delta)k", "Economics", "Capital accumulation"),
]


def seed_default_formulas(library: FormulaLibrary):
    """
    Add default formulas to library, merging with existing formulas.
    
    **Strategy**:
    - Checks each default formula by name
    - Only adds formulas that don't already exist
    - Preserves user's custom formulas
    - Updates existing formulas if they match by name
    
    **Args**:
        library: FormulaLibrary instance
    """
    existing_names = {f.name for f in library.get_all()}
    added_count = 0
    updated_count = 0
    
    logger.info(f"Seeding formula library (currently has {len(existing_names)} formulas)")
    
    for name, latex, category, description in DEFAULT_FORMULAS:
        if name in existing_names:
            # Formula exists - optionally update it
            # (Skip updating to preserve user modifications)
            continue
        else:
            # New formula - add it
            library.add_formula(name, latex, category, description)
            added_count += 1
    
    if added_count > 0:
        logger.info(f"Added {added_count} new default formulas")
    else:
        logger.debug("All default formulas already present")
