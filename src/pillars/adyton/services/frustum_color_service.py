"""
Frustum color resolver for Adyton walls.

Loads per-wall center-face values from CSVs and resolves them to QColor via:
1) decimal -> ternary (padded to 6 digits)
2) BaphometColorService.resolve_color

Wall index mapping aligns with WALL_COLORS order:
  0: Saturn, 1: Sun, 2: Mercury, 3: Moon, 4: Venus, 5: Jupiter, 6: Mars.
"""
from pathlib import Path
from typing import Dict, List, Optional

from PyQt6.QtGui import QColor

from shared.services.tq.ternary_service import TernaryService
from shared.services.tq.baphomet_color_service import BaphometColorService
from pillars.adyton.constants import (
    WALL_WIDTH_UNITS,
    FRUSTUM_FACE_TOP,
    FRUSTUM_FACE_RIGHT,
    FRUSTUM_FACE_BOTTOM,
    FRUSTUM_FACE_LEFT,
)


class FrustumColorService:
    """Resolves center-face colors for frustums based on per-wall CSV data."""

    WALL_FILES = {
        0: "sun_wall.csv",
        1: "mercury_wall.csv",
        2: "luna_wall.csv",
        3: "venus_wall.csv",
        4: "jupiter_wall.csv",
        5: "mars_wall.csv",
        6: "saturn_wall.csv",
    }

    def __init__(self, docs_root: Optional[Path] = None):
        """
          init   logic.
        
        Args:
            docs_root: Description of docs_root.
        
        """
        base = docs_root or Path(__file__).resolve().parents[4] / "Docs" / "adyton_walls"
        self.docs_root = base
        self._cache_center: Dict[int, List[List[QColor]]] = {}
        self._cache_ternary: Dict[int, List[List[str]]] = {}
        self._trigram_map: Dict[int, QColor] = self._load_trigram_map()
        self._zodiac_cycle: List[int] = self._build_zodiac_cycle()
        self._planet_color_codes: Dict[str, int] = self._build_planet_codes()
        # Rotated so Venus is the middle wall (index 3), preserving circular adjacency
        self._wall_planet_order: List[str] = [
            "sun",
            "mercury",
            "moon",
            "venus",
            "jupiter",
            "mars",
            "saturn",
        ]
        self._center_column = WALL_WIDTH_UNITS // 2
        self._top_rows = {0, 1, 2}
        self._middle_rows = {3, 4}
        self._bottom_rows = {5, 6, 7}
        self._cache_decimal: Dict[int, List[List[int]]] = {}

    def get_wall_decimals(self, wall_index: int) -> List[List[int]]:
        """Returns the raw decimal values from the wall CSV (8 rows × 13 cols)."""
        if wall_index in self._cache_decimal:
            return self._cache_decimal[wall_index]

        filename = self.WALL_FILES.get(wall_index)
        if not filename:
            return []

        path = self.docs_root / filename
        if not path.exists():
            return []

        grid: List[List[int]] = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                cells = line.split(",")
                row: List[int] = []
                for cell in cells:
                    cell = cell.strip()
                    try:
                        row.append(int(cell))
                    except ValueError:
                        row.append(0)
                grid.append(row)

        self._cache_decimal[wall_index] = grid
        return grid

    def get_center_color(self, wall_index: int, row: int, col: int) -> QColor:
        """
        Retrieve center color logic.
        
        Args:
            wall_index: Description of wall_index.
            row: Description of row.
            col: Description of col.
        
        Returns:
            Result of get_center_color operation.
        """
        grid = self._load_wall(wall_index)
        try:
            return grid[row][col]
        except IndexError:
            return QColor("#000000")

    def get_side_color(self, wall_index: int, row: int, col: int, face_index: int) -> QColor:
        """
        Retrieve side color logic.
        
        Args:
            wall_index: Description of wall_index.
            row: Description of row.
            col: Description of col.
            face_index: Description of face_index.
        
        Returns:
            Result of get_side_color operation.
        """
        if face_index == FRUSTUM_FACE_RIGHT:
            return self._resolve_face_two(wall_index, col)
        if face_index == FRUSTUM_FACE_LEFT:
            return self._resolve_face_four(wall_index, row)

        ternary_grid = self._load_wall_ternary(wall_index)
        if not ternary_grid:
            return QColor("#000000")
        try:
            ternary = ternary_grid[row][col]
        except IndexError:
            return QColor("#000000")

        ternary = ternary.rjust(6, "0") if not ternary.startswith("-") else ternary
        if len(ternary) < 6 or ternary.startswith("-"):
            return QColor("#000000")

        top_trigram = ternary[:3]
        bottom_trigram = ternary[3:]

        top_dec = TernaryService.ternary_to_decimal(top_trigram)
        bottom_dec = TernaryService.ternary_to_decimal(bottom_trigram)

        top_color = self._trigram_map.get(top_dec, QColor("#000000"))
        bottom_color = self._trigram_map.get(bottom_dec, QColor("#000000"))

        if face_index == FRUSTUM_FACE_TOP:
            return top_color
        if face_index == FRUSTUM_FACE_BOTTOM:
            return bottom_color
        return QColor("#000000")

    def _load_wall(self, wall_index: int) -> List[List[QColor]]:
        if wall_index in self._cache_center:
            return self._cache_center[wall_index]

        filename = self.WALL_FILES.get(wall_index)
        if not filename:
            self._cache_center[wall_index] = []
            return []

        path = self.docs_root / filename
        if not path.exists():
            self._cache_center[wall_index] = []
            return []

        grid: List[List[QColor]] = []
        ternary_grid: List[List[str]] = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                cells = line.split(",")
                colors_row: List[QColor] = []
                ternary_row: List[str] = []
                for cell in cells:
                    cell = cell.strip()
                    try:
                        dec_val = int(cell)
                    except ValueError:
                        colors_row.append(QColor("#000000"))
                        ternary_row.append("")
                        continue
                    ternary = TernaryService.decimal_to_ternary(dec_val)
                    ternary_padded = ternary.rjust(6, "0") if not ternary.startswith("-") else ternary
                    ternary_row.append(ternary_padded)
                    colors_row.append(BaphometColorService.resolve_color(ternary_padded))
                grid.append(colors_row)
                ternary_grid.append(ternary_row)

        self._cache_center[wall_index] = grid
        self._cache_ternary[wall_index] = ternary_grid
        return grid

    def _load_wall_ternary(self, wall_index: int) -> List[List[str]]:
        if wall_index in self._cache_ternary:
            return self._cache_ternary[wall_index]
        # populate by loading wall
        self._load_wall(wall_index)
        return self._cache_ternary.get(wall_index, [])

    def _load_trigram_map(self) -> Dict[int, QColor]:
        trigram_path = Path(__file__).resolve().parents[4] / "Docs" / "adyton_walls" / "trigram_color.csv"
        if not trigram_path.exists():
            return {}
        mapping: Dict[int, QColor] = {}
        self._trigram_glyphs: Dict[int, str] = {}
        self._trigram_letters: Dict[int, str] = {}
        with trigram_path.open("r", encoding="utf-8") as f:
            next(f, None)  # skip header
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(",")
                if len(parts) < 4:
                    continue
                try:
                    trigram_dec = int(parts[0])
                    r = int(parts[1])
                    g = int(parts[2])
                    b = int(parts[3])
                except ValueError:
                    continue
                mapping[trigram_dec] = QColor(r, g, b)
                # Load glyph and letter if present
                if len(parts) >= 5:
                    self._trigram_glyphs[trigram_dec] = parts[4].strip()
                if len(parts) >= 6:
                    self._trigram_letters[trigram_dec] = parts[5].strip()
        return mapping

    def get_trigram_glyph(self, trigram_dec: int) -> str:
        """Returns the glyph symbol for a trigram decimal value."""
        return self._trigram_glyphs.get(trigram_dec, "")

    def get_trigram_letter(self, trigram_dec: int) -> str:
        """Returns the letter for a trigram decimal value."""
        return self._trigram_letters.get(trigram_dec, "")

    def _build_zodiac_cycle(self) -> List[int]:
        # Standard zodiac order starting with Aries
        zodiac_codes = {
            "aries": 10,
            "taurus": 15,
            "gemini": 7,
            "cancer": 20,
            "leo": 12,
            "virgo": 5,
            "libra": 11,
            "scorpio": 24,
            "sagittarius": 4,
            "capricorn": 19,
            "aquarius": 21,
            "pisces": 8,
        }
        return [
            zodiac_codes["aries"],
            zodiac_codes["taurus"],
            zodiac_codes["gemini"],
            zodiac_codes["cancer"],
            zodiac_codes["leo"],
            zodiac_codes["virgo"],
            zodiac_codes["libra"],
            zodiac_codes["scorpio"],
            zodiac_codes["sagittarius"],
            zodiac_codes["capricorn"],
            zodiac_codes["aquarius"],
            zodiac_codes["pisces"],
        ]

    def _build_planet_codes(self) -> Dict[str, int]:
        return {
            "sun": 13,
            "saturn": 14,
            "mercury": 16,
            "venus": 17,
            "jupiter": 22,
            "mars": 25,
            "moon": 26,
        }

    def _resolve_face_two(self, wall_index: int, col: int) -> QColor:
        # Center column uses the ruling planet of the wall
        if col == self._center_column:
            planet_name = self._wall_planet_order[wall_index % len(self._wall_planet_order)]
            planet_code = self._planet_color_codes.get(planet_name)
            if planet_code is None:
                return QColor("#000000")
            return self._trigram_map.get(planet_code, QColor("#000000"))

        # Zodiac cycle across columns, repeating if width exceeds 12
        if not self._zodiac_cycle:
            return QColor("#000000")
        zodiac_code = self._zodiac_cycle[col % len(self._zodiac_cycle)]
        return self._trigram_map.get(zodiac_code, QColor("#000000"))

    def _resolve_face_four(self, wall_index: int, row: int) -> QColor:
        planet_name = self._wall_planet_order[wall_index % len(self._wall_planet_order)]

        def planet_by_offset(offset: int) -> Optional[str]:
            """
            Planet by offset logic.
            
            Args:
                offset: Description of offset.
            
            Returns:
                Result of planet_by_offset operation.
            """
            idx = (wall_index + offset) % len(self._wall_planet_order)
            return self._wall_planet_order[idx]

        # Top 3 rows: far-left (offset -3) to near-left (offset -1)
        if row == 0:
            target_planet = planet_by_offset(-3)
        elif row == 1:
            target_planet = planet_by_offset(-2)
        elif row == 2:
            target_planet = planet_by_offset(-1)
        # Middle 2 rows: ruling planet
        elif row in self._middle_rows:
            target_planet = planet_name
        # Bottom 3 rows: near-right (offset +1) to far-right (offset +3)
        elif row == 5:
            target_planet = planet_by_offset(1)
        elif row == 6:
            target_planet = planet_by_offset(2)
        elif row == 7:
            target_planet = planet_by_offset(3)
        else:
            target_planet = planet_name

        if target_planet is None:
            return QColor("#000000")

        code = self._planet_color_codes.get(target_planet)
        if code is None:
            return QColor("#000000")
        return self._trigram_map.get(code, QColor("#000000"))

    def get_left_face_trigram_code(self, wall_index: int, row: int) -> int:
        """Get the trigram code for the left face (planet-based)."""
        planet_name = self._wall_planet_order[wall_index % len(self._wall_planet_order)]

        def planet_by_offset(offset: int) -> Optional[str]:
            """
            Planet by offset logic.
            
            Args:
                offset: Description of offset.
            
            Returns:
                Result of planet_by_offset operation.
            """
            idx = (wall_index + offset) % len(self._wall_planet_order)
            return self._wall_planet_order[idx]

        if row == 0:
            target_planet = planet_by_offset(-3)
        elif row == 1:
            target_planet = planet_by_offset(-2)
        elif row == 2:
            target_planet = planet_by_offset(-1)
        elif row in self._middle_rows:
            target_planet = planet_name
        elif row == 5:
            target_planet = planet_by_offset(1)
        elif row == 6:
            target_planet = planet_by_offset(2)
        elif row == 7:
            target_planet = planet_by_offset(3)
        else:
            target_planet = planet_name

        if target_planet is None:
            return 0
        return self._planet_color_codes.get(target_planet, 0)

    def get_right_face_trigram_code(self, wall_index: int, col: int) -> int:
        """Get the trigram code for the right face (zodiac-based)."""
        if col == self._center_column:
            planet_name = self._wall_planet_order[wall_index % len(self._wall_planet_order)]
            return self._planet_color_codes.get(planet_name, 0)

        if not self._zodiac_cycle:
            return 0
        return self._zodiac_cycle[col % len(self._zodiac_cycle)]
