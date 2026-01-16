"""
Tzolkin Service - The Temporal Navigator.
Manages 260-day harmonic cycle calculations with Ditrune mapping and Conrune logic.
"""
import csv
import os
import logging
from datetime import date
from typing import List, Tuple, Dict, Optional
from ..models.tzolkin_models import TzolkinDate

logger = logging.getLogger(__name__)

class TzolkinService:
    """
    Sovereign Service for Tzolkin Calculations.
    Manages the 260-day harmonic cycle and Ditrune mapping.
    """
    
    # The Epoch: January 12, 2020 = Kin 1, Cycle 1
    EPOCH = date(2020, 1, 12)
    
    # Traditional / IsopGem Sign Names (1-20)
    # Using the primary Maya names for now, can be mapped to Thelemic later
    SIGN_NAMES = [
        "Imix", "Ik", "Akbal", "Kan", "Chicchan",
        "Cimi", "Manik", "Lamat", "Muluc", "Oc",
        "Chuen", "Eb", "Ben", "Ix", "Men",
        "Cib", "Caban", "Etznab", "Cauac", "Ahau"
    ]

    def __init__(self):
        """
          init   logic.
        
        """
        self._decimal_grid: List[List[int]] = []
        self._ternary_grid: List[List[str]] = []
        self._cell_true_tokens_by_sign_tone: Dict[Tuple[int, int], str] = {}
        self._load_grid_data()
        self._load_cell_names()

    def _load_cell_names(self) -> None:
        """Loads structural cell names (pure Greek tokens) for the 260-cell calendar."""
        csv_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "../../../../data/time_mechanics/Tzolkin_CellNames.csv"
        ))

        if not os.path.exists(csv_path):
            logger.warning(f"Tzolkin_CellNames.csv not found at {csv_path}")
            return

        try:
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        sign = int(row.get('row', '0'))
                        tone = int(row.get('col', '0'))
                    except Exception:
                        continue

                    true_token = (row.get('true_token') or '').strip()
                    if sign and tone and true_token:
                        self._cell_true_tokens_by_sign_tone[(sign, tone)] = true_token

            if len(self._cell_true_tokens_by_sign_tone) != 260:
                logger.info(
                    "Loaded %d/260 Tzolkin cell names from CSV",
                    len(self._cell_true_tokens_by_sign_tone),
                )
        except Exception as e:
            logger.error(f"Failed to load Tzolkin cell names: {e}")

    def get_true_token_for_kin(self, kin: int) -> Optional[str]:
        """Return the pure Greek structural name (true_token) for a Kin (1-260)."""
        if not (1 <= int(kin) <= 260):
            return None
        kin_index = int(kin) - 1
        tone = (kin_index % 13) + 1
        sign = (kin_index % 20) + 1
        return self._cell_true_tokens_by_sign_tone.get((sign, tone))

    def _load_grid_data(self):
        """Loads the Tzolkin Cycle.csv data into memory."""
        # Path relative to project root
        # Ideally this path should be resolved more robustly
        csv_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "../../../../data/time_mechanics/Tzolkin Cycle.csv"
        ))
        
        if not os.path.exists(csv_path):
            logger.error(f"Tzolkin Cycle.csv not found at {csv_path}")
            return

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # Lines 0-19 are Decimal values (rows 1-20 in file)
                # Parse lines 0-19
                for i in range(20):
                    if i < len(lines):
                        row_vals = [int(x.strip()) for x in lines[i].split(',') if x.strip()]
                        if len(row_vals) == 13:
                            self._decimal_grid.append(row_vals)
                
                # Lines 21-40 are Ternary values (rows 22-41 in file)
                # Skip line 20 (empty separator)
                start_ternary = 21 
                for i in range(20):
                    idx = start_ternary + i
                    if idx < len(lines):
                        row_vals = [x.strip() for x in lines[idx].split(',') if x.strip()]
                        if len(row_vals) == 13:
                            self._ternary_grid.append(row_vals)
                            
            logger.info("Tzolkin Grid loaded successfully.")
            
        except Exception as e:
            logger.error(f"Failed to load Tzolkin Grid: {e}")

    def from_gregorian(self, target_date: date) -> TzolkinDate:
        """
        Convert a Gregorian Date to a Tzolkin Date.
        """
        # Calculate delta days
        delta = (target_date - self.EPOCH).days
        
        # Calculate Kin (1-260). Delta 0 = Kin 1.
        # Python modulo handles negative numbers correctly for cycles
        # delta = 0 -> kin_index = 0 -> Kin 1
        # delta = -1 -> kin_index = 259 -> Kin 260
        kin_index = delta % 260
        kin = kin_index + 1
        
        # Calculate Cycle Number
        # delta 0 to 259 -> Cycle 1
        # delta 260 -> Cycle 2
        # delta -1 -> Cycle 0
        cycle = (delta // 260) + 1
        
        # Calculate Tone (1-13) and Sign (1-20)
        # Note: The Grid logic might differ from standard Tzolkin (Tone/Sign independent cycles)
        # Standard Tzolkin: Tone cycles 1-13, Sign cycles 1-20 independently.
        # Let's verify if the CSV grid follows this standard mapping.
        # The CSV has 20 rows and 13 columns.
        # Usually Tzolkin is visualized as 20 signs x 13 tones.
        # If the CSV is row=Sign(0-19), col=Tone(0-12)? 
        # But wait, standard Tzolkin: Kin 1 = 1 Imix. Kin 2 = 2 Ik. 
        # Sign 1, Tone 1. Sign 2, Tone 2.
        # They increment together.
        # 
        # Let's assume for now the CSV is indexed by the STANDARD Tone/Sign calculation.
        # Standard calculation:
        # Tone index = kin_index % 13 (0-12) -> Tone = index + 1
        # Sign index = kin_index % 20 (0-19) -> Sign = index + 1
        
        tone_idx = kin_index % 13
        sign_idx = kin_index % 20
        
        tone = tone_idx + 1
        sign = sign_idx + 1
        sign_name = self.SIGN_NAMES[sign_idx]
        
        # Lookup in Grid
        # The CSV structure needs to be mapped to these indices.
        # Is the CSV row = Sign and col = Tone?
        # Let's assume Row = Sign (0-19) and Col = Tone (0-12).
        # We will verify this assumption with the "Rite of Tzolkin".
        
        if self._decimal_grid and self._ternary_grid:
            ditrune_dec = self._decimal_grid[sign_idx][tone_idx]
            ditrune_ter = self._ternary_grid[sign_idx][tone_idx]
        else:
            ditrune_dec = 0
            ditrune_ter = "000000"
            
        return TzolkinDate(
            gregorian_date=target_date,
            kin=kin,
            tone=tone,
            sign=sign,
            sign_name=sign_name,
            cycle=cycle,
            ditrune_decimal=ditrune_dec,
            ditrune_ternary=ditrune_ter
        )


    def get_epoch(self) -> date:
        """
        Retrieve epoch logic.
        
        Returns:
            Result of get_epoch operation.
        """
        return self.EPOCH

    def get_conrune(self, ditrune: str) -> str:
        """
        Calculate the Conrune (Anti-Self) of a Ditrune.
        Operation: Invert 1s and 2s. 0 remains 0.
        """
        conrune = []
        for char in ditrune:
            if char == '1':
                conrune.append('2')
            elif char == '2':
                conrune.append('1')
            else:
                conrune.append('0')
        return "".join(conrune)

    def get_trigrams(self, ditrune: str) -> Tuple[str, str]:
        """
        Split a Ditrune into its Upper (Sky) and Lower (Earth) Trigrams.
        Returns: (Upper [d1-d3], Lower [d4-d6])
        """
        if len(ditrune) != 6:
            # Fallback for invalid data, though shouldn't happen with valid grid
            return ("000", "000")
        return (ditrune[:3], ditrune[3:])