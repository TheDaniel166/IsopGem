"""
Thelemic Calendar Service - Loads and queries the Thelemic Calendar CSV.

Provides lookup methods for Conrune pairs by:
- Difference (degree position 1-364)
- Gregorian date
- Zodiacal position
"""
import csv
import os
from typing import Dict, List, Optional
from pathlib import Path

from ..models.thelemic_calendar_models import ConrunePair


class ThelemicCalendarService:
    """
    Service for accessing Thelemic Calendar data.
    
    Loads the first 5 columns of Thelemic Calendar.csv:
    - Ditrune, Contrune, Difference, Zodiacal, Day
    
    The Difference column (1-364) determines the degree position.
    """
    
    def __init__(self):
        self._pairs_by_difference: Dict[int, ConrunePair] = {}
        self._pairs_by_date: Dict[str, ConrunePair] = {}
        self._all_pairs: List[ConrunePair] = []
        self._loaded = False
    
    def load_calendar(self, csv_path: Optional[str] = None) -> bool:
        """
        Load the Thelemic Calendar from CSV.
        
        Args:
            csv_path: Path to CSV file. If None, uses default location.
            
        Returns:
            True if loaded successfully, False otherwise.
        """
        if csv_path is None:
            # Find project root and construct path
            current_dir = Path(__file__).parent
            project_root = current_dir.parent.parent.parent.parent
            csv_path = project_root / "Docs" / "time_mechanics" / "Thelemic Calendar.csv"
        
        csv_path = Path(csv_path)
        
        if not csv_path.exists():
            print(f"[WARNING] Thelemic Calendar not found: {csv_path}")
            return False
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip header
                
                for row in reader:
                    if len(row) < 5:
                        continue
                    
                    # Parse first 5 columns
                    try:
                        ditrune = int(row[0].strip())
                        contrune = int(row[1].strip())
                        difference = int(row[2].strip())
                        zodiacal = row[3].strip()
                        gregorian = row[4].strip()
                    except (ValueError, IndexError):
                        continue
                    
                    pair = ConrunePair(
                        ditrune=ditrune,
                        contrune=contrune,
                        difference=difference,
                        zodiacal=zodiacal,
                        gregorian_date=gregorian
                    )
                    
                    self._all_pairs.append(pair)
                    self._pairs_by_difference[difference] = pair
                    self._pairs_by_date[gregorian.lower()] = pair
            
            self._loaded = True
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to load Thelemic Calendar: {e}")
            return False
    
    def ensure_loaded(self) -> None:
        """Ensure the calendar is loaded, loading if necessary."""
        if not self._loaded:
            self.load_calendar()
    
    def get_pair_by_difference(self, difference: int) -> Optional[ConrunePair]:
        """
        Get Conrune pair by Difference value (degree position 1-364).
        
        Args:
            difference: The difference/degree value (1-364)
            
        Returns:
            ConrunePair if found, None otherwise.
        """
        self.ensure_loaded()
        return self._pairs_by_difference.get(difference)
    
    def get_pair_by_date(self, date_str: str) -> Optional[ConrunePair]:
        """
        Get Conrune pair by Gregorian date string.
        
        Args:
            date_str: Date string (e.g., "21-Mar", "1-Apr")
            
        Returns:
            ConrunePair if found, None otherwise.
        """
        self.ensure_loaded()
        return self._pairs_by_date.get(date_str.lower())
    
    def get_all_pairs(self) -> List[ConrunePair]:
        """Get all Conrune pairs in order."""
        self.ensure_loaded()
        return self._all_pairs.copy()
    
    def get_prime_ditrune_pairs(self) -> List[ConrunePair]:
        """Get the 4 Prime Ditrune Sets (intercalary days)."""
        self.ensure_loaded()
        return [p for p in self._all_pairs if p.is_prime_ditrune]
    
    def difference_to_zodiac_degree(self, difference: int) -> float:
        """
        Convert a Difference value to zodiacal degrees (0-360).
        
        The 364 days map to 360 degrees with 4 intercalary positions.
        Regular days: difference 1-360 map to degrees 0-359
        Intercalary days: at cardinal points (90, 180, 270, 0)
        
        Args:
            difference: Difference value (1-364)
            
        Returns:
            Zodiacal degree (0-360)
        """
        pair = self.get_pair_by_difference(difference)
        if pair is None:
            return 0.0
        
        if pair.is_prime_ditrune:
            # Prime Ditrunes at cardinal points
            # diff 91 -> 90° (Summer Solstice)
            # diff 182 -> 180° (Autumn Equinox)
            # diff 273 -> 270° (Winter Solstice)
            # diff 364 -> 0° (Spring Equinox)
            if difference == 91:
                return 90.0
            elif difference == 182:
                return 180.0
            elif difference == 273:
                return 270.0
            elif difference == 364:
                return 0.0
        
        # Regular days: map sign + day to degrees
        sign_idx = 0
        day_in_sign = 0
        
        sign_letter = pair.sign_letter
        if sign_letter:
            from ..models.thelemic_calendar_models import ZODIAC_SIGNS
            if sign_letter in ZODIAC_SIGNS:
                _, sign_idx = ZODIAC_SIGNS[sign_letter]
        
        day_in_sign = pair.sign_day or 0
        
        # Each sign is 30 degrees
        return (sign_idx * 30 + day_in_sign) % 360
    
    def get_reversal_pair(self, pair: ConrunePair) -> Optional[ConrunePair]:
        """
        Find the reversal pair where Ditrune and Contrune are swapped.
        
        For a pair (A, B), finds the pair where ditrune=B and contrune=A.
        
        Args:
            pair: The original ConrunePair
            
        Returns:
            The reversal ConrunePair if found, None otherwise.
        """
        self.ensure_loaded()
        
        target_ditrune = pair.contrune
        target_contrune = pair.ditrune
        
        for p in self._all_pairs:
            if p.ditrune == target_ditrune and p.contrune == target_contrune:
                return p
        
        return None

