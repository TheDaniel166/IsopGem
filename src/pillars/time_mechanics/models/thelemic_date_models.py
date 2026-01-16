"""
Thelemic Date Models - Era Legis Calendar Data.

Immutable dataclass representing dates in the Thelemic calendar system,
which counts from the reception of Liber AL vel Legis in 1904 e.v.

The Thelemic calendar uses a two-tiered system:
- Upper tier: 22-year cycles called "docosades" (corresponding to Tarot Trumps)
- Lower tier: Years within the current docosade (0-21)

Date format includes:
- Anno (year): e.g., "V:x" meaning docosade V, year 10
- Sol position: Sun's zodiacal position (e.g., "Sol in 27° Capricorni")
- Luna position: Moon's zodiacal position (e.g., "Luna in 15° Leonis")
- Dies: Day of the week in Latin (e.g., "Dies Jovis" for Thursday)
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


# Tarot Trump correspondences for years 0-21 (Major Arcana)
TAROT_TRUMPS = [
    "The Fool",           # 0
    "The Magus",          # 1
    "The Priestess",      # 2
    "The Empress",        # 3
    "The Emperor",        # 4
    "The Hierophant",     # 5
    "The Lovers",         # 6
    "The Chariot",        # 7
    "Adjustment",         # 8 (Crowley's name for Justice)
    "The Hermit",         # 9
    "Fortune",            # 10
    "Lust",               # 11 (Crowley's name for Strength)
    "The Hanged Man",     # 12
    "Death",              # 13
    "Art",                # 14 (Crowley's name for Temperance)
    "The Devil",          # 15
    "The Tower",          # 16
    "The Star",           # 17
    "The Moon",           # 18
    "The Sun",            # 19
    "The Aeon",           # 20 (Crowley's name for Judgement)
    "The Universe",       # 21 (Crowley's name for The World)
]

# Latin names for days of the week
DIES_NAMES = {
    0: ("Dies Lunae", "Monday", "Luna"),       # Monday
    1: ("Dies Martis", "Tuesday", "Mars"),     # Tuesday
    2: ("Dies Mercurii", "Wednesday", "Mercury"),  # Wednesday
    3: ("Dies Jovis", "Thursday", "Jupiter"),  # Thursday
    4: ("Dies Veneris", "Friday", "Venus"),    # Friday
    5: ("Dies Saturnii", "Saturday", "Saturn"), # Saturday
    6: ("Dies Solis", "Sunday", "Sol"),        # Sunday
}

# Zodiac signs in Latin genitive (possessive) form
ZODIAC_LATIN = [
    ("Aries", "Arietis"),
    ("Taurus", "Tauri"),
    ("Gemini", "Geminorum"),
    ("Cancer", "Cancri"),
    ("Leo", "Leonis"),
    ("Virgo", "Virginis"),
    ("Libra", "Librae"),
    ("Scorpio", "Scorpionis"),
    ("Sagittarius", "Sagittarii"),
    ("Capricorn", "Capricorni"),
    ("Aquarius", "Aquarii"),
    ("Pisces", "Piscium"),
]


@dataclass(frozen=True)
class ThelemicDate:
    """
    Immutable representation of a date in the Thelemic calendar.

    The Thelemic calendar begins on March 20, 1904 (Vernal Equinox)
    when Aleister Crowley received The Book of the Law.

    Year Format: UPPER:lower (e.g., V:x)
    - UPPER: Docosade number (22-year cycle) in uppercase Roman numerals
    - lower: Year within docosade (0-21) in lowercase Roman numerals

    Full Date Format:
    "Sol in [deg]° [Sign] : Luna in [deg]° [Sign] : Anno [UPPER:lower]"

    Optional additions:
    - Dies [Latin day name] (day of week)
    """
    gregorian_date: date
    gregorian_time: Optional[datetime]  # For precise Sol/Luna positions

    # Year components
    thelemic_year: int          # Years since 1904 (0-based after March 20)
    docosade: int               # Which 22-year cycle (0, 1, 2, ...)
    year_in_docosade: int       # Year within cycle (0-21)

    # Astronomical positions (degrees 0-360)
    sol_longitude: float        # Sun's ecliptic longitude
    luna_longitude: float       # Moon's ecliptic longitude

    # Day of week
    weekday: int                # 0=Monday, 6=Sunday (Python convention)

    @property
    def docosade_roman(self) -> str:
        """Return docosade number in uppercase Roman numerals."""
        return self._to_roman_upper(self.docosade)

    @property
    def year_roman(self) -> str:
        """Return year-in-docosade in lowercase Roman numerals."""
        return self._to_roman_lower(self.year_in_docosade)

    @property
    def anno(self) -> str:
        """Return the Thelemic year in standard format (e.g., 'V:x')."""
        return f"{self.docosade_roman}:{self.year_roman}"

    @property
    def docosade_trump(self) -> str:
        """Return the Tarot Trump for the current docosade."""
        if 0 <= self.docosade < len(TAROT_TRUMPS):
            return TAROT_TRUMPS[self.docosade]
        return f"Trump {self.docosade}"

    @property
    def year_trump(self) -> str:
        """Return the Tarot Trump for the current year within the docosade."""
        if 0 <= self.year_in_docosade < len(TAROT_TRUMPS):
            return TAROT_TRUMPS[self.year_in_docosade]
        return f"Trump {self.year_in_docosade}"

    @property
    def sol_sign(self) -> tuple[str, str]:
        """Return (sign name, Latin genitive) for Sun's position."""
        return self._longitude_to_sign(self.sol_longitude)

    @property
    def sol_degree(self) -> int:
        """Return degree within the zodiac sign (0-29)."""
        return int(self.sol_longitude % 30)

    @property
    def luna_sign(self) -> tuple[str, str]:
        """Return (sign name, Latin genitive) for Moon's position."""
        return self._longitude_to_sign(self.luna_longitude)

    @property
    def luna_degree(self) -> int:
        """Return degree within the zodiac sign (0-29)."""
        return int(self.luna_longitude % 30)

    @property
    def dies_latin(self) -> str:
        """Return Latin name for day of week."""
        return DIES_NAMES.get(self.weekday, ("Dies ???",))[0]

    @property
    def dies_english(self) -> str:
        """Return English name for day of week."""
        return DIES_NAMES.get(self.weekday, ("", "Unknown"))[1]

    @property
    def dies_planet(self) -> str:
        """Return planetary ruler for day of week."""
        return DIES_NAMES.get(self.weekday, ("", "", "Unknown"))[2]

    def format_full(self, include_dies: bool = True) -> str:
        """
        Return the full Thelemic date string.

        Format: "Sol in [deg]° [Sign] : Luna in [deg]° [Sign] : Anno [UPPER:lower]"
        With optional Dies prefix.
        """
        parts = []

        if include_dies:
            parts.append(self.dies_latin)

        sol_str = f"Sol in {self.sol_degree}° {self.sol_sign[1]}"
        luna_str = f"Luna in {self.luna_degree}° {self.luna_sign[1]}"
        anno_str = f"Anno {self.anno}"

        parts.extend([sol_str, luna_str, anno_str])

        return " : ".join(parts)

    def format_short(self) -> str:
        """Return abbreviated Thelemic date (just Anno)."""
        return f"Anno {self.anno}"

    def format_tarot(self) -> str:
        """Return Tarot correspondence description."""
        return f"The docosade of {self.docosade_trump}, and the year of {self.year_trump}"

    @staticmethod
    def _to_roman_upper(n: int) -> str:
        """Convert integer to uppercase Roman numerals."""
        if n == 0:
            return "0"

        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syms = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']

        result = ''
        num = n
        for i, v in enumerate(val):
            while num >= v:
                result += syms[i]
                num -= v
        return result

    @staticmethod
    def _to_roman_lower(n: int) -> str:
        """Convert integer to lowercase Roman numerals."""
        if n == 0:
            return "0"
        return ThelemicDate._to_roman_upper(n).lower()

    @staticmethod
    def _longitude_to_sign(longitude: float) -> tuple[str, str]:
        """Convert ecliptic longitude to zodiac sign."""
        sign_idx = int(longitude // 30) % 12
        return ZODIAC_LATIN[sign_idx]

    def __repr__(self) -> str:
        return (
            f"ThelemicDate({self.gregorian_date}, "
            f"Anno {self.anno}, "
            f"Sol {self.sol_degree}° {self.sol_sign[0]}, "
            f"Luna {self.luna_degree}° {self.luna_sign[0]})"
        )
