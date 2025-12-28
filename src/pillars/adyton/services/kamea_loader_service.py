"""
Kamea Loader Service - The Grid Parser.
Loads the 27x27 Kamea of Maut from CSV, mapping coordinates to Ditrunes, Octants, and Enochian Tablets.
"""
import csv
import os
from typing import List, Dict, Tuple
from pillars.adyton.models.kamea_cell import KameaCell

class KameaLoaderService:
    """
    Responsible for loading the Kamea of Maut from the foundational CSV
    and parsing it into a structured coordinate system.
    """
    
    # Path to the source of truth
    # We assume the user has placed the file at this location relative to project root
    CSV_PATH = "Docs/kamea/kamea_maut_ternary - Sheet1.csv"

    def __init__(self, project_root: str):
        self.project_root = project_root
        self._cache: Dict[Tuple[int, int], KameaCell] = {}

    def load_grid(self) -> Dict[Tuple[int, int], KameaCell]:
        """
        Parses the CSV and returns a dictionary mapping (x, y) -> KameaCell.
        """
        if self._cache:
            return self._cache

        full_path = os.path.join(self.project_root, self.CSV_PATH)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Kamea CSV not found at: {full_path}")

        cells = {}
        
        with open(full_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)

            # Row 0 is the header: ,-13,-12...
            # Column 0 of subsequent rows is the Y index: 13, 12...
            
            # Parse header to get X coordinates (skipping the first empty cell)
            header = rows[0]
            x_coords = [int(x) for x in header[1:]] # [-13, -12, ..., 13]

            # Iterate through data rows
            for row_idx, row_data in enumerate(rows[1:]):
                if not row_data: continue
                
                # First element is the Y coordinate
                y_coord = int(row_data[0])
                
                # Subsequent elements are the Ditrunes corresponding to x_coords
                ditrunes = row_data[1:]
                
                for i, ditrune in enumerate(ditrunes):
                    if i >= len(x_coords): break
                    
                    x = x_coords[i]
                    
                    # Clean the ditrune (just in case of whitespace)
                    ditrune = ditrune.strip()
                    if not ditrune: continue

                    # Calculate metadata
                    decimal_value = self._ternary_to_decimal(ditrune)
                    octant_id = self._determine_octant(x, y_coord)
                    tablet_id = self._determine_tablet(octant_id)
                    
                    cell = KameaCell(
                        x=x,
                        y=y_coord,
                        ditrune=ditrune,
                        decimal_value=decimal_value,
                        octant_id=octant_id,
                        tablet_id=tablet_id
                    )
                    cells[(x, y_coord)] = cell

        self._cache = cells
        return cells

    def _ternary_to_decimal(self, ternary: str) -> int:
        """Converts a ternary string to decimal."""
        try:
            return int(ternary, 3)
        except ValueError:
            return 0

    def _determine_octant(self, x: int, y: int) -> int:
        """
        Determines the Octant ID (1-8) based on Cartesian coordinates.
        1: +y > +x (Top-Center Rightish? No, let's define standard octants)
        
        Standard Octant Definition (Counter-Clockwise starting from East):
        Wait, let's align with the Watchtowers logic.
        
        Octant 1 (Air-1):   x > 0, y > 0, y < x  (East-North) - actually this is usually sector 1 in math
        
        Let's use the explicit geometric bounds:
        Axes/Diagonals are 0.
        
        Sector 1: x > 0, y > 0, x > y  (East, upper part)
        Sector 2: x > 0, y > 0, y > x  (North, right part)
        Sector 3: x < 0, y > 0, y > -x (North, left part)
        Sector 4: x < 0, y > 0, -x > y (West, upper part)
        Sector 5: x < 0, y < 0, -x > -y (West, lower part) 
        Sector 6: x < 0, y < 0, -y > -x (South, left part)
        Sector 7: x > 0, y < 0, -y > x (South, right part)
        Sector 8: x > 0, y < 0, x > -y (East, lower part)
        
        Wait, simplier check:
        """
        if x == 0 or y == 0 or abs(x) == abs(y):
            return 0 # Axis or Diagonal
            
        if x > 0 and y > 0:
            return 1 if x > y else 2
        elif x < 0 and y > 0:
            return 3 if y > abs(x) else 4
        elif x < 0 and y < 0:
            return 5 if abs(x) > abs(y) else 6
        elif x > 0 and y < 0:
            return 7 if abs(y) > x else 8
        return 0

    def _determine_tablet(self, octant_id: int) -> str:
        """
        Maps Octant to Enochian Element.
        Using the 'Fusion of Opposites' logic:
        1 + 5 = Air ? 
        Let's map based on direction first.
        
        East (Air): Octants around +X axis? That would be 8 and 1.
        North (Earth): Octants around +Y axis? 2 and 3.
        West (Water): Octants around -X axis? 4 and 5.
        South (Fire): Octants around -Y axis? 6 and 7.
        
        BUT, the User said "Opposite Octants".
        If we fuse 1 (East-North) and 5 (West-South)...
        
        Let's stick to the user's specific mapping if given, otherwise infer:
        User said: "Triangle of 78 facing upward"
        
        Let's assign placeholder 'Spirit' to 0.
        Let's tentatively map:
        1, 5 -> Air
        3, 7 -> Water
        2, 6 -> Fire
        4, 8 -> Earth
        
        (This will be refined in visual verification).
        """
        if octant_id == 0: return "Spirit"
        if octant_id in [1, 5]: return "Air"
        if octant_id in [3, 7]: return "Water"
        if octant_id in [2, 6]: return "Fire"
        if octant_id in [4, 8]: return "Earth"
        return "Spirit"

    def load_wall_map(self) -> Dict[int, int]:
        """
        Loads the authentic Value -> Wall Index mapping from zodiacal_heptagon.csv.
        Returns: {decimal_value: wall_index (0-6)}
        """
        path = os.path.join(self.project_root, "Docs", "adyton_walls", "zodiacal_heptagon.csv")
        mapping = {}
        
        if not os.path.exists(path):
            print(f"Warning: Wall map file not found at {path}")
            return mapping

        try:
            with open(path, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)
                
                # Dynamic index map
                col_map = {}
                for i, h in enumerate(headers):
                    col_map[h.strip()] = i
                    
                for row_idx, row in enumerate(reader):
                    if not row: continue
                    
                    # Iterate Walls 1 through 7
                    for w in range(1, 8):
                        a_key = f"A{w}"
                        b_key = f"B{w}"
                        
                        if a_key in col_map and b_key in col_map:
                            try:
                                val_a = int(row[col_map[a_key]])
                                val_b = int(row[col_map[b_key]])
                                
                                # Wall Index 0-6
                                w_idx = w - 1
                                
                                mapping[val_a] = w_idx
                                mapping[val_b] = w_idx
                            except (ValueError, IndexError):
                                continue
                                
        except Exception as e:
            print(f"Error loading zodiacal_heptagon.csv: {e}")
            
        return mapping
