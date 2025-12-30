"""Astrological Glyph Service - Centralized font-agnostic symbol provider.

This service provides astrological glyphs (zodiac signs, planets, aspects)
to the entire application without requiring callers to know which font is used.
It auto-detects available fonts and provides appropriate character mappings.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class FontConfig:
    """Configuration for a specific astrological font."""
    name: str
    zodiac_map: Dict[str, str]
    planet_map: Dict[str, str]
    degree_symbol: str  # Character for ° 
    minute_symbol: str  # Character for '
    use_font_numbers: bool  # If True, numbers are also font-specific


# Astronomicon font configuration
ASTRONOMICON_CONFIG = FontConfig(
    name="Astronomicon",
    zodiac_map={
        "aries": "A", "taurus": "B", "gemini": "C", "cancer": "D",
        "leo": "E", "virgo": "F", "libra": "G", "scorpio": "H",
        "sagittarius": "I", "capricorn": "J", "aquarius": "K", "pisces": "L"
    },
    planet_map={
        "sun": "Q", "moon": "R", "mercury": "S", "venus": "T",
        "mars": "U", "jupiter": "V", "saturn": "W", "uranus": "X",
        "neptune": "Y", "pluto": "Z", "north node": "g", "south node": "i",
        "mean node": "g", "true node": "g", "chiron": "q", "lilith": "z",
        "part of fortune": "}", "asc": "c", "mc": "d"
    },
    degree_symbol="^",  # Astronomicon uses ^ for degree
    minute_symbol="",   # No minutes symbol in Astronomicon
    use_font_numbers=False
)

# Unicode fallback configuration
UNICODE_CONFIG = FontConfig(
    name="Unicode",
    zodiac_map={
        "aries": "♈", "taurus": "♉", "gemini": "♊", "cancer": "♋",
        "leo": "♌", "virgo": "♍", "libra": "♎", "scorpio": "♏",
        "sagittarius": "♐", "capricorn": "♑", "aquarius": "♒", "pisces": "♓"
    },
    planet_map={
        "sun": "☉", "moon": "☽", "mercury": "☿", "venus": "♀",
        "mars": "♂", "jupiter": "♃", "saturn": "♄", "uranus": "♅",
        "neptune": "♆", "pluto": "♇", "north node": "☊", "south node": "☋",
        "mean node": "☊", "true node": "☊", "chiron": "⚷", "lilith": "⚸",
        "asc": "ASC", "mc": "MC"
    },
    degree_symbol="°",
    minute_symbol="'",
    use_font_numbers=False
)


class AstroGlyphService:
    """Provides astrological symbol glyphs in a font-agnostic way.
    
    The service auto-detects if the Astronomicon font is available and
    returns appropriate characters. Falls back to Unicode symbols if not.
    """
    
    # Zodiac sign order (for degree lookups)
    ZODIAC_ORDER = [
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"
    ]
    
    def __init__(self):
        """Initialize and detect available fonts."""
        self._font_family: Optional[str] = None
        self._config: FontConfig = UNICODE_CONFIG
        self._detect_font()
    
    def _detect_font(self) -> None:
        """Detect if Astronomicon font is available."""
        try:
            from PyQt6.QtGui import QFontDatabase
            families = QFontDatabase.families()
            
            for family in families:
                if "astronomicon" in family.lower():
                    self._font_family = family
                    self._config = ASTRONOMICON_CONFIG
                    return
            
            # No Astronomicon found - use system default
            self._font_family = "Arial"
            self._config = UNICODE_CONFIG
            
        except ImportError:
            # Qt not available (e.g., in tests)
            self._font_family = "Arial"
            self._config = UNICODE_CONFIG
    
    def get_font_family(self) -> str:
        """Return the font family name to use for glyphs."""
        return self._font_family or "Arial"
    
    def is_using_astronomicon(self) -> bool:
        """Check if Astronomicon font is active."""
        return self._config.name == "Astronomicon"
    
    def get_zodiac_glyph(self, sign_name: str) -> str:
        """Get the glyph for a zodiac sign."""
        key = sign_name.lower().strip()
        return self._config.zodiac_map.get(key, sign_name[:1])
    
    def get_planet_glyph(self, planet_name: str) -> str:
        """Get the glyph for a planet."""
        key = planet_name.lower().strip()
        return self._config.planet_map.get(key, planet_name[:1])
    
    def get_degree_symbol(self) -> str:
        """Get the degree symbol for current font."""
        return self._config.degree_symbol
    
    def get_minute_symbol(self) -> str:
        """Get the minute symbol for current font."""
        return self._config.minute_symbol
    
    def get_zodiac_name_from_degree(self, degree: float) -> str:
        """Get the zodiac sign name from an absolute degree."""
        norm_deg = degree % 360
        sign_idx = int(norm_deg / 30) % 12
        return self.ZODIAC_ORDER[sign_idx].title()
    
    def to_zodiacal_string(self, degree: float, use_glyphs: bool = True) -> str:
        """Convert absolute degree to zodiacal string with font-appropriate symbols.
        
        Args:
            degree: Absolute degree (0-360)
            use_glyphs: If True, use font glyphs; if False, use sign names
            
        Returns:
            Formatted string using current font's symbols
        """
        norm_deg = degree % 360
        sign_idx = int(norm_deg / 30) % 12
        sign_rem = norm_deg % 30
        
        d = int(sign_rem)
        m = int((sign_rem - d) * 60)
        
        sign_name = self.ZODIAC_ORDER[sign_idx].title()
        deg_sym = self._config.degree_symbol
        min_sym = self._config.minute_symbol
        
        if use_glyphs:
            glyph = self.get_zodiac_glyph(sign_name)
            if min_sym:
                return f"{d}{deg_sym}{glyph}{m:02d}{min_sym}"
            else:
                # No minutes symbol - just show degree and sign
                return f"{d}{deg_sym}{glyph}{m:02d}"
        else:
            return f"{d}° {sign_name} {m:02d}'"


# Singleton instance for app-wide use
astro_glyphs = AstroGlyphService()
