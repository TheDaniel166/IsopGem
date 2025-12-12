from PyQt6.QtGui import QColor

class BaphometColorService:
    """
    Service for resolving the specific color physics of the Kamea of Baphomet.
    Algorithm:
    - Red Channel: Bigram(1, 6) [Indices 0, 5 in 0-indexed string]
    - Green Channel: Bigram(2, 5) [Indices 1, 4]
    - Blue Channel: Bigram(3, 4) [Indices 2, 3]
    
    Mapping (Bigram -> Hex/Int):
    00 -> 0x00 (0)
    01 -> 0x25 (37)
    02 -> 0x3C (60)
    10 -> 0x61 (97)
    11 -> 0x86 (134)
    12 -> 0x9D (157)
    20 -> 0xC2 (194)
    21 -> 0xE7 (231)
    22 -> 0xFE (254)
    """
    
    STEP_MAP = {
        "00": 0x00,
        "01": 0x25,
        "02": 0x3C,
        "10": 0x61,
        "11": 0x86,
        "12": 0x9D,
        "20": 0xC2,
        "21": 0xE7,
        "22": 0xFE
    }

    @staticmethod
    def resolve_color(ternary6: str) -> QColor:
        """
        Resolves the RGB color for a given 6-digit ternary string.
        """
        if len(ternary6) != 6:
            return QColor("#000000")
            
        # Extract Digits (0-indexed)
        # d1=0, d2=1, d3=2, d4=3, d5=4, d6=5
        d1, d2, d3, d4, d5, d6 = list(ternary6)
        
        # Red Channel: Lines 1 & 6 -> d1 + d6
        bg_red = d1 + d6
        
        # Green Channel: Lines 2 & 5 -> d2 + d5
        bg_green = d2 + d5
        
        # Blue Channel: Lines 3 & 4 -> d3 + d4
        bg_blue = d3 + d4
        
        # Resolve Intensities
        r_val = BaphometColorService.STEP_MAP.get(bg_red, 0)
        g_val = BaphometColorService.STEP_MAP.get(bg_green, 0)
        b_val = BaphometColorService.STEP_MAP.get(bg_blue, 0)
        
        return QColor(r_val, g_val, b_val)
