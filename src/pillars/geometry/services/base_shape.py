"""Base class for geometric shape calculators."""
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ShapeProperty:
    """Represents a calculable property of a shape."""
    name: str           # Display name (e.g., "Radius", "Area")
    key: str            # Internal key (e.g., "radius", "area")
    value: Optional[float] = None  # Current value
    unit: str = ""      # Unit suffix (e.g., "cm", "cm²")
    readonly: bool = False  # If True, can't be edited (calculated only)
    precision: int = 4  # Decimal places for display
    default: Optional[float] = None # Default value for initialization


class GeometricShape(ABC):
    """Abstract base class for all geometric shapes."""
    
    def __init__(self):
        """Initialize the shape with its properties."""
        self.properties: Dict[str, ShapeProperty] = {}
        self._init_properties()
    
    @abstractmethod
    def _init_properties(self):
        """Initialize the shape's properties. Must be implemented by subclasses."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this shape."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a brief description of this shape."""
        pass
        
    @property
    def calculation_hint(self) -> str:
        """
        Return a hint about required fields for calculation.
        Defaults to 'Calculate from any field' for 1-DoF shapes.
        """
        return "Calculate from any field"
    
    @abstractmethod
    def calculate_from_property(self, property_key: str, value: float) -> bool:
        """
        Calculate all other properties from a given property value.
        
        Args:
            property_key: The key of the property being set
            value: The new value for that property
            
        Returns:
            True if calculation succeeded, False otherwise
        """
        pass
    
    @abstractmethod
    def get_drawing_instructions(self) -> Dict:
        """
        Get instructions for drawing this shape in the viewport.
        
        Returns:
            Dictionary with drawing data (points, curves, labels, etc.)
        """
        pass
    
    @abstractmethod
    def get_label_positions(self) -> List[Tuple[str, float, float]]:
        """
        Get positions for labels in the viewport.
        
        Returns:
            List of tuples: (label_text, x_position, y_position)
        """
        pass
    
    def set_property(self, key: str, value: float) -> bool:
        """
        Set a property value and recalculate dependent properties.
        
        Args:
            key: Property key
            value: New value
            
        Returns:
            True if successful
        """
        if key not in self.properties:
            return False
        
        if self.properties[key].readonly:
            return False
        
        return self.calculate_from_property(key, value)
    
    def get_property(self, key: str) -> Optional[float]:
        """Get a property value."""
        if key in self.properties:
            return self.properties[key].value
        return None
    
    def get_all_properties(self) -> List[ShapeProperty]:
        """Get all properties in order."""
        return list(self.properties.values())
    
    def get_editable_properties(self) -> List[ShapeProperty]:
        """Get only editable properties."""
        return [p for p in self.properties.values() if not p.readonly]
    
    def get_readonly_properties(self) -> List[ShapeProperty]:
        """Get only readonly (calculated) properties."""
        return [p for p in self.properties.values() if p.readonly]
    
    def validate_value(self, key: str, value: float) -> Tuple[bool, str]:
        """
        Validate a property value.
        
        Args:
            key: Property key
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation - must be positive for most geometric properties
        if value <= 0:
            return False, f"{self.properties[key].name} must be positive"
        
        return True, ""
    
    def clear_all(self):
        """Clear all property values."""
        for prop in self.properties.values():
            prop.value = None
