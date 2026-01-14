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
    
    def get_by_category(self, category: str) -> List[Formula]:
        """
        Get all formulas in a category.
        
        **Args**:
            category: Category name
        
        **Returns**:
            List of formulas in that category
        """
        return [f for f in self.formulas if f.category == category]
    
    def get_categories(self) -> List[str]:
        """
        Get all unique category names.
        
        **Returns**:
            Sorted list of category names
        """
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
    # Physics
    ("Energy-Mass Equivalence", "E = mc^2", "Physics", "Einstein's famous equation"),
    ("Newton's Second Law", "F = ma", "Physics", "Force equals mass times acceleration"),
    ("Kinetic Energy", "K = \\frac{1}{2}mv^2", "Physics", "Energy of motion"),
    
    # Calculus
    ("Derivative Definition", "f'(x) = \\lim_{h \\to 0} \\frac{f(x+h) - f(x)}{h}", "Calculus", "Limit definition of derivative"),
    ("Fundamental Theorem", "\\int_{a}^{b} f'(x) \\, dx = f(b) - f(a)", "Calculus", "Fundamental theorem of calculus"),
    
    # Geometry
    ("Pythagorean Theorem", "a^2 + b^2 = c^2", "Geometry", "Right triangle relationship"),
    ("Circle Area", "A = \\pi r^2", "Geometry", "Area of a circle"),
    ("Sphere Volume", "V = \\frac{4}{3}\\pi r^3", "Geometry", "Volume of a sphere"),
    
    # Algebra
    ("Quadratic Formula", "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}", "Algebra", "Solve ax²+bx+c=0"),
    
    # Statistics
    ("Normal Distribution", "f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}} e^{-\\frac{(x-\\mu)^2}{2\\sigma^2}}", "Statistics", "Gaussian distribution"),
]


def seed_default_formulas(library: FormulaLibrary):
    """
    Add default formulas to library if it's empty.
    
    **Args**:
        library: FormulaLibrary instance
    """
    if len(library.get_all()) == 0:
        logger.info("Seeding formula library with default formulas")
        
        for name, latex, category, description in DEFAULT_FORMULAS:
            library.add_formula(name, latex, category, description)
        
        logger.info(f"Added {len(DEFAULT_FORMULAS)} default formulas")
