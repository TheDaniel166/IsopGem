from dataclasses import dataclass
from typing import Optional

@dataclass
class CipherToken:
    """
    Represents a single entry in the TQ Base-27 Cipher.
    Maps a Decimal Value (0-26) to its Categorical, Symbolic, and Alphabetic correspondences.
    """
    decimal_value: int
    trigram: str
    category: Optional[str] = None
    symbol: Optional[str] = None
    letter: Optional[str] = None

    @property
    def label(self) -> str:
        """Returns a display label for the token (Symbol or Letter)."""
        return self.symbol if self.symbol else (self.letter if self.letter else str(self.decimal_value))

    @property
    def stratum(self) -> str:
        """
        Determines the ontological stratum based on Pyx (0) count.
        3 Zeros = VOID (Potential)
        2 Zeros = ELEMENT (Fundamental State)
        1 Zero  = ZODIAC (Cycle)
        0 Zeros = PLANET (Entity)
        """
        zeros = self.trigram.count('0')
        if zeros == 3: return "VOID"
        if zeros == 2: return "ELEMENT"
        if zeros == 1: return "ZODIAC"
        return "PLANET"
