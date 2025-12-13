import logging
import csv
from typing import Dict, List, Optional, Tuple
from ..models.kamea_cell import KameaCell
from .baphomet_color_service import BaphometColorService
from PyQt6.QtGui import QColor
import os

logger = logging.getLogger(__name__)

class KameaGridService:
    """
    Service for loading and interacting with the 27x27 Kamea Grid.
    Acts as the Source of Truth by loading from validated CSVs.
    """

    def __init__(self, variant: str = "Maut"):
        self._grid: Dict[Tuple[int, int], KameaCell] = {}
        self._decimal_map: Dict[int, Tuple[int, int]] = {} # Reverse Lookup
        self._initialized = False
        self.variant = variant
        
        # Paths to Source of Truth CSVs
        if self.variant == "Baphomet":
            # Baphomet Data
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.decimal_csv_path = os.path.join(current_dir, "..", "data", "kamea_baphomet_grid.csv")
            self.ternary_csv_path = os.path.join(current_dir, "..", "data", "kamea_baphomet_ternary.csv")
        else:
            # Default Maut Data
            self.decimal_csv_path = "/home/burkettdaniel927/projects/isopgem/Docs/kamea/kamea_maut.csv"
            self.ternary_csv_path = "/home/burkettdaniel927/projects/isopgem/Docs/kamea/kamea_maut_ternary - Sheet1.csv"
        
    @property
    def cells(self) -> List[KameaCell]:
        """Exposes the list of cell objects."""
        if not self._initialized:
            self.initialize()
        return list(self._grid.values())

    def initialize(self):
        """Loads the grid from CSVs if not already loaded."""
        if self._initialized:
            return

        try:
            self._load_grid()
            self._initialized = True
            logger.info(f"Kamea Grid ({self.variant}) initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Kamea Grid: {e}")
            raise

    def get_cell(self, x: int, y: int) -> Optional[KameaCell]:
        """Returns the cell at Cartesian coordinates (x, y)."""
        if not self._initialized:
            self.initialize()
        return self._grid.get((x, y))
        
    def get_cell_by_locator(self, region: int, area: int, cell: int) -> Optional[KameaCell]:
        """Finds a cell by its Kamea Locator values."""
        if not self._initialized:
            self.initialize()
            
        # This is O(N) but N=729, so it's negligible. 
        # Optimized lookup can be added if needed.
        for c in self._grid.values():
            if c.bigrams == (region, area, cell):
                return c
                return c
        return None

    def get_cell_color(self, cell: KameaCell) -> QColor:
        """Returns the color for the cell based on the Baphomet Physics (used for all variants now)."""
        return BaphometColorService.resolve_color(cell.ternary_value)

    def get_quadset(self, x: int, y: int) -> List[KameaCell]:
        """
        Returns the list of related cells for (x, y).
        Variant 'Maut': Returns Quadset (Identity, Conrune, Conrune-Reversal, Reversal).
        Variant 'Baphomet': Returns Converse Pair (Horizontal Reflection).
        """
        if self.variant == "Baphomet":
            # Baphomet Logic: Horizontal Reflection only
            # (x, y) <-> (-x, y)
            # If x=0, Identity (just self)
            if x == 0:
                coords = [(0, y)]
            else:
                coords = [(x, y), (-x, y)]
        else:
            # Maut Logic: Full Quadset
            # (x, y), (-x, -y), (-x, y), (x, -y)
            coords = [(x, y), (-x, -y), (-x, y), (x, -y)]
            
        quadset = []
        for cx, cy in coords:
            cell = self.get_cell(cx, cy)
            if cell:
                quadset.append(cell)
        return quadset

    def get_chord_values(self, decimal_value: int) -> List[int]:
        """
        Returns the list of decimal values forming the Geometric Chord (Quadset)
        for the given input number.
        """
        if not self._initialized:
            self.initialize()
            
        coords = self._decimal_map.get(decimal_value)
        if not coords:
            return [decimal_value] # Return self if not found (or should we return empty?)
            
        quadset_cells = self.get_quadset(coords[0], coords[1])
        # Return unique values sorted (to match user expectation of a set)
        values = sorted(list(set(c.decimal_value for c in quadset_cells)))
        return values

    def _load_grid(self):
        """
        Parses the CSV files and builds the cell objects.
        The CSV structure has headers for X coordinates -13 to 13.
        Rows correspond to Y coordinates +13 to -13.
        """
        decimals = self._parse_grid_csv(self.decimal_csv_path)
        ternaries = self._parse_grid_csv(self.ternary_csv_path)

        # Coordinate Space: x in [-13, 13], y in [-13, 13]
        for y in range(-13, 14):
            for x in range(-13, 14):
                try:
                    dec_val = int(decimals[(x, y)])
                    tern_val = ternaries[(x, y)]
                    
                    # Ensure ternary value is 6 digits (pad with leading zeros)
                    tern_val = tern_val.zfill(6)
                    
                    # Parse Bigrams
                    # Digits indices: 01 23 45
                    # Bigram 1 (Core/Region): 3,4 (indices 2,3) -> Wait, Doc says Bigram 3 is Core?
                    # Let's check "The Kamea Doctrine" Part I, Section 3
                    # Macro (3rd Bigram) d3, d4 -> Region
                    # Meso (2nd Bigram) d2, d5 -> Area
                    # Micro (1st Bigram) d1, d6 -> Cell
                    
                    # Indices in 0-based string:
                    # d1=0, d2=1, d3=2, d4=3, d5=4, d6=5
                    
                    # Core (Region): d3, d4 -> indices 2, 3
                    d3 = int(tern_val[2])
                    d4 = int(tern_val[3])
                    region_val = 3 * d3 + d4
                    
                    # Body (Area): d2, d5 -> indices 1, 4
                    d2 = int(tern_val[1])
                    d5 = int(tern_val[4])
                    area_val = 3 * d2 + d5
                    
                    # Skin (Cell): d1, d6 -> indices 0, 5
                    d1 = int(tern_val[0])
                    d6 = int(tern_val[5])
                    cell_val = 3 * d1 + d6
                    
                    bigrams = (region_val, area_val, cell_val)
                    family_id = region_val # Regions 0-8 determine Family
                    
                    cell = KameaCell(
                        x=x,
                        y=y,
                        decimal_value=dec_val,
                        ternary_value=tern_val,
                        bigrams=bigrams,
                        family_id=family_id
                    )
                    self._grid[(x, y)] = cell
                    self._decimal_map[dec_val] = (x, y)

                except KeyError:
                    # Handle cases where CSV might be missing cells (shouldn't happen in full grid)
                    logger.warning(f"Missing data for coordinate ({x}, {y})")
                    continue

    def _parse_grid_csv(self, filepath: str) -> Dict[Tuple[int, int], str]:
        """
        Generic parser for the grid CSV format.
        Assumes:
        - Header row contains X coordinates.
        - First column contains Y coordinates.
        - Intersection is value.
        """
        data = {}
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
            # Map column index to X coord
            # Header[0] is empty. Header[1] is start.
            # CSV Header: ,-13,-12...
            col_map = {}
            for i, h in enumerate(headers):
                if i == 0: continue
                try:
                    col_map[i] = int(h)
                except ValueError:
                    continue
            
            for row in reader:
                try:
                    y_coord = int(row[0]) # First col is Y
                except ValueError:
                    continue
                    
                for i in range(1, len(row)):
                    if i in col_map:
                        x_coord = col_map[i]
                        val = row[i]
                        data[(x_coord, y_coord)] = val
        return data
