"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: Contract (Data schemas) - GRANDFATHERED
- USED BY: Time_mechanics (5 references)
- CRITERION: 4 (Shared data contract) - needs verification

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""
Thelemic Calendar Models - Data Transfer Objects for the Zodiacal Circle.

These models represent the Conrune pairs from the Thelemic Calendar system,
which maps 364 days to Ditrune/Contrune pairs with zodiacal positions.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ConrunePair:
    """
    Represents a single day's Conrune pair from the Thelemic Calendar.
    
    The Difference determines the degree position in the Zodiacal Circle (1-364).
    Prime Ditrune Sets (intercalary days) have zodiacal = "XXXX".
    """
    ditrune: int          # The Day-aspect value (lighter)
    contrune: int         # The Night-aspect value (heavier)
    difference: int       # The tension between Day and Night (determines degree)
    zodiacal: str         # Sign + Day (e.g., "15 A") or "XXXX" for intercalary
    gregorian_date: str   # Gregorian date (e.g., "21-Mar")
    
    @property
    def is_prime_ditrune(self) -> bool:
        """True if this is one of the 4 Prime Ditrune Sets (intercalary days)."""
        return self.zodiacal == "XXXX"
    
    @property
    def sign_letter(self) -> Optional[str]:
        """Extract the zodiac sign letter (A-L) or None for Prime Ditrunes."""
        if self.is_prime_ditrune:
            return None
        parts = self.zodiacal.strip().split()
        return parts[-1] if parts else None
    
    @property
    def sign_day(self) -> Optional[int]:
        """Extract the day within the sign (0-29) or None for Prime Ditrunes."""
        if self.is_prime_ditrune:
            return None
        parts = self.zodiacal.strip().split()
        try:
            return int(parts[0]) if len(parts) >= 2 else None
        except ValueError:
            return None


# Mapping of sign letters to indices and names
ZODIAC_SIGNS = {
    'A': ('Aries', 0),
    'B': ('Taurus', 1),
    'C': ('Gemini', 2),
    'D': ('Cancer', 3),
    'E': ('Leo', 4),
    'F': ('Virgo', 5),
    'G': ('Libra', 6),
    'H': ('Scorpio', 7),
    'I': ('Sagittarius', 8),
    'J': ('Capricorn', 9),
    'K': ('Aquarius', 10),
    'L': ('Pisces', 11),
}

# Astronomicon font character mapping (UPPERCASE)
ASTRONOMICON_CHARS = {
    'A': 'A',  # Aries
    'B': 'B',  # Taurus
    'C': 'C',  # Gemini
    'D': 'D',  # Cancer
    'E': 'E',  # Leo
    'F': 'F',  # Virgo
    'G': 'G',  # Libra
    'H': 'H',  # Scorpio
    'I': 'I',  # Sagittarius
    'J': 'J',  # Capricorn (European style)
    'K': 'K',  # Aquarius
    'L': 'L',  # Pisces
}