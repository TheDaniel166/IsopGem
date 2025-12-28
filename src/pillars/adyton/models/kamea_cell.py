"""
Kamea Cell - The Adyton Grid Unit.
Represents a single cell in the Kamea of Maut with position, Ditrune value, and Enochian Tablet mapping.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class KameaCell:
    """
    Represents a single cell in the Kamea of Maut.
    
    Attributes:
        x (int): Cartesian X coordinate (-13 to +13).
        y (int): Cartesian Y coordinate (-13 to +13).
        ditrune (str): The 6-digit ternary string (e.g., '102201').
        decimal_value (int): The decimal value of the ditrune.
        octant_id (int): The Octant ID (1-8) this cell belongs to.
                         0 if it lies exactly on an axis or center.
        tablet_id (str): The Enochian Element ('Air', 'Water', 'Earth', 'Fire', 'Spirit')
                         mapped from the Octant.
    """
    x: int
    y: int
    ditrune: str
    decimal_value: int
    octant_id: int
    tablet_id: str

    @property
    def is_singularity(self) -> bool:
        """
        Determine if singularity logic.
        
        Returns:
            Result of is_singularity operation.
        """
        return self.x == 0 and self.y == 0
    
    @property
    def is_axis(self) -> bool:
        """
        Determine if axis logic.
        
        Returns:
            Result of is_axis operation.
        """
        return (self.x == 0 or self.y == 0 or abs(self.x) == abs(self.y)) and not self.is_singularity