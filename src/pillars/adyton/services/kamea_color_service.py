"""
Kamea Color Service - The Chromatic Resolver.
Calculates 5-face color assignments for Adyton Kamea cells using Trigram, Zodiac, and Baphomet mappings.
"""
from pathlib import Path
from typing import Dict, List, Tuple
from PyQt6.QtGui import QColor

from pillars.tq.services.ternary_service import TernaryService
from pillars.tq.services.baphomet_color_service import BaphometColorService
from pillars.adyton.models.kamea_cell import KameaCell

class KameaColorService:
    """
    Resolves colors for Kamea Cells, mirroring the logic of Adyton Walls.
    """

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self._trigram_map: Dict[int, QColor] = self._load_trigram_map()
        self._setup_cycles()

    def _setup_cycles(self):
        # Zodiac Cycle for X-Axis (Right Face)
        # 0=Aries, etc.
        self.zodiac_codes = [
            10, 15, 7, 20, 12, 5, 11, 24, 4, 19, 21, 8
        ]
        
        # Planet Cycle for Y-Axis (Left Face)
        # Using Chaldean Order? Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon
        self.planet_codes = [
            14, 22, 25, 13, 17, 16, 26
        ]

    def _load_trigram_map(self) -> Dict[int, QColor]:
        trigram_path = self.project_root / "Docs" / "adyton_walls" / "trigram_color.csv"
        mapping: Dict[int, QColor] = {}
        
        if not trigram_path.exists():
            print(f"Warning: Trigram map not found at {trigram_path}")
            return {}
            
        with trigram_path.open("r", encoding="utf-8") as f:
            next(f, None)  # skip header
            for line in f:
                line = line.strip()
                if not line: continue
                parts = line.split(",")
                if len(parts) < 4: continue
                try:
                    trigram_dec = int(parts[0])
                    r = int(parts[1])
                    g = int(parts[2])
                    b = int(parts[3])
                    mapping[trigram_dec] = QColor(r, g, b)
                except ValueError:
                    continue
        return mapping

    def resolve_colors(self, cell: KameaCell) -> Tuple[QColor, QColor, QColor, QColor, QColor]:
        """
        Returns (Top, Bottom, Left, Right, Cap) colors.
        """
        # 1. Top/Bottom from Ditrune Trigrams
        ditrune = cell.ditrune.rjust(6, '0')
        top_tri = ditrune[:3]
        bot_tri = ditrune[3:]
        
        top_val = TernaryService.ternary_to_decimal(top_tri)
        bot_val = TernaryService.ternary_to_decimal(bot_tri)
        
        c_top = self._trigram_map.get(top_val, QColor("#333333"))
        c_bot = self._trigram_map.get(bot_val, QColor("#222222"))
        
        # 2. Right from X (Zodiac)
        # Shift X to positive index. Max range -13..13. 
        # offset 13 -> 0..26.
        x_idx = cell.x + 13
        zodiac_code = self.zodiac_codes[x_idx % 12]
        c_right = self._trigram_map.get(zodiac_code, QColor("#1f1f1f"))
        
        # 3. Left from Y (Planets)
        # Shift Y.
        y_idx = cell.y + 13
        planet_code = self.planet_codes[y_idx % 7]
        c_left = self._trigram_map.get(planet_code, QColor("#282828"))
        
        # 4. Cap from Baphomet Logic (Specific Color of the Ditrune)
        c_cap = BaphometColorService.resolve_color(ditrune)
        
        return c_top, c_bot, c_left, c_right, c_cap
