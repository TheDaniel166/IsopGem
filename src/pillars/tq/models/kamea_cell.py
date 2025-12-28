"""
Kamea Cell Model - The 27x27 Grid Unit.
Represents a single cell in the Kamea matrix with its coordinates, ternary value, and bigram decomposition.
"""
from dataclasses import dataclass
from typing import Tuple

@dataclass
class KameaCell:
    """
    Represents a single cell in the 27x27 Kamea grid.
    
    Attributes:
        x (int): Cartesian x-coordinate (-13 to +13).
        y (int): Cartesian y-coordinate (-13 to +13).
        ternary_value (str): The 6-digit ternary string (e.g., '102201').
        decimal_value (int): The decimal equivalent of the ternary value (0-728).
        bigrams (Tuple[int, int, int]): The 3 bigram decimal values (Region, Area, Cell).
        family_id (int): The Family ID (0-8) derived from the Core Bigram.
    """
    x: int
    y: int
    ternary_value: str
    decimal_value: int
    bigrams: Tuple[int, int, int]
    family_id: int

    @property
    def kamea_locator(self) -> str:
        """Returns the Kamea Locator string 'Region-Area-Cell'."""
        return f"{self.family_id}-{self.bigrams[1]}-{self.bigrams[2]}"

    @property
    def is_axis(self) -> bool:
        """Returns True if the cell lies on the X or Y axis."""
        return self.x == 0 or self.y == 0
    
    @property
    def is_origin(self) -> bool:
        return self.x == 0 and self.y == 0

    @property
    def pyx_count(self) -> int:
        """Returns the Dimensional Density (count of '0's)."""
        return self.ternary_value.count('0')

    @property
    def conrune_vector(self) -> int:
        """
        Returns the Magnitude of the Vector between Self and Conrune.
        |Self - Conrune(Self)|. Unique for each pair.
        """
        # Calculate Conrune
        c_chars = []
        for c in self.ternary_value:
            if c == '1': c_chars.append('2')
            elif c == '2': c_chars.append('1')
            else: c_chars.append('0')
        c_str = "".join(c_chars)
        c_val = int(c_str, 3)
        
        return abs(self.decimal_value - c_val)
