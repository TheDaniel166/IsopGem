"""
Conversions (Utilities) - Zodiacal String Formatter.
Utility functions for converting ecliptic degrees to zodiacal notation used by astrology services.
"""
from typing import Tuple

ZODIAC_SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

def to_zodiacal_string(degree: float) -> str:
    """
    Convert absolute degree (0-360) to zodiacal degree notation (Deg Sign Min).
    Example: 12.5 -> 12° Aries 30'
    Example: 32.1 -> 2° Taurus 06'
    """
    norm_deg = degree % 360
    sign_idx = int(norm_deg / 30)
    sign_rem = norm_deg % 30
    
    d = int(sign_rem)
    m = int((sign_rem - d) * 60)
    
    # Handle edge case where minutes round up to 60? 
    # Usually easier to just leave as is, or rigorous math checks.
    # Simple truncation is standard for most astro software unless highly precise.
    
    sign_name = ZODIAC_SIGNS[sign_idx % 12]
    return f"{d}° {sign_name} {m:02d}'"
