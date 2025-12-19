from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class TzolkinDate:
    """
    Immutable representation of a date in the Tzolkin cycle.
    """
    gregorian_date: date
    kin: int            # 1 to 260
    tone: int           # 1 to 13
    sign: int           # 1 to 20
    sign_name: str      # e.g., "Imix", "Ik", etc. (or Thelemic equivalent)
    cycle: int          # Cycle count since Epoch (2020-01-12)
    ditrune_decimal: int # The decimal value from the grid
    ditrune_ternary: str # The ternary string from the grid

    def __repr__(self):
        return (f"TzolkinDate(Kin={self.kin}, {self.tone}-{self.sign_name}, "
                f"Cycle={self.cycle}, Ditrune={self.ditrune_decimal})")
