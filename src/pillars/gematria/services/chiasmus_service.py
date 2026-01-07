"""
Service for discovering Chiastic (Mirror) patterns in text based on Gematria values.
"""
import re
import logging
from typing import List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ChiasmusPattern:
    """
    Chiasmus Pattern class definition.
    
    """
    center_index: Optional[int]  # None if even length center (A-B-B-A), int if odd (A-B-C-B-A)
    depth: int                  # How many layers deep (excluding center)
    left_indices: List[int]     # Indices of the left side [A, B...]
    right_indices: List[int]    # Indices of the right side [...B, A]
    source_units: List[str]     # The actual words
    values: List[int]           # The gematria values
    symmetry_mode: str = "Exact Match"  # Which mode found this pattern

class ChiasmusService:
    """
    Chiasmus Service class definition.
    
    """
    def __init__(self):
        """
          init   logic.
        
        """
        pass
    
    @staticmethod
    def _digit_root(n: int) -> int:
        """Calculate digit root (mod 9 reduction)."""
        if n == 0:
            return 0
        return ((n - 1) % 9) + 1
    
    @staticmethod
    def _values_match(v1: int, v2: int, mode: str) -> bool:
        """Check if two values match according to the symmetry mode."""
        if mode == "Exact Match":
            return v1 == v2
        elif mode == "Fuzzy (±10%)":
            if v1 == 0 or v2 == 0:
                return v1 == v2
            tolerance = 0.10
            ratio = v1 / v2 if v2 != 0 else 0
            return (1 - tolerance) <= ratio <= (1 + tolerance)
        elif mode == "Digit Root":
            return ChiasmusService._digit_root(v1) == ChiasmusService._digit_root(v2)
        else:  # Sum Balance handled separately
            return False

    def scan_text(self, text: str, calculator, min_depth: int = 1, max_depth: int = 10, symmetry_mode: str = "Exact Match") -> List[ChiasmusPattern]:
        """
        Scans text for Gematria-based Chiastic patterns.
        
        Args:
            text: Input text
            calculator: GematriaCalculator instance (must have .calculate(str) -> int)
            min_depth: Minimum number of mirrored layers required (filters results)
            max_depth: Maximum number of mirrored layers to scan for (limits search depth)
            symmetry_mode: Matching algorithm - "Exact Match", "Fuzzy (±10%)", "Digit Root", or "Sum Balance"
        """
        # 1. Tokenize
        # Split by non-alphanumeric to get words
        raw_units = re.findall(r'\b[a-zA-Z]+\b', text)
        if not raw_units:
            return []
            
        units = []
        values = []
        original_indices = [] # To map back if needed, currently 1:1 with raw_units
        
        for i, word in enumerate(raw_units):
            val = calculator.calculate(word)
            if val > 0:
                units.append(word)
                values.append(val)
                original_indices.append(i)
                
        n = len(values)
        if n == 0:
            return []

        found_patterns = []
        
        # Special handling for Sum Balance mode
        if symmetry_mode == "Sum Balance":
            return self._scan_sum_balance(units, values, min_depth, max_depth)

        # 2. Scan for Odd Patterns (A-B-C-B-A) -> Single Pivot
        for center in range(1, n - 1):
            depth = 0
            left_idxs = []
            right_idxs = []
            
            l = center - 1
            r = center + 1
            
            while l >= 0 and r < n and depth < max_depth:
                if self._values_match(values[l], values[r], symmetry_mode):
                    depth += 1
                    left_idxs.append(l)
                    right_idxs.append(r)
                    l -= 1
                    r += 1
                else:
                    break
            
            if depth >= min_depth:
                left_idxs.reverse()
                right_idxs.reverse()
                
                full_slice_indices = left_idxs + [center] + right_idxs[::-1] 
                
                p = ChiasmusPattern(
                    center_index=center,
                    depth=depth,
                    left_indices=left_idxs, # Outer -> Inner
                    right_indices=right_idxs, # Outer -> Inner
                    source_units=[units[i] for i in full_slice_indices],
                    values=[values[i] for i in full_slice_indices],
                    symmetry_mode=symmetry_mode
                )
                found_patterns.append(p)

        # 3. Scan for Even Patterns (A-B-B-A) -> No Pivot, just mirror
        for i in range(n - 1):
            if self._values_match(values[i], values[i+1], symmetry_mode):
                # Potential even center found
                depth = 1
                left_idxs = [i]
                right_idxs = [i+1]
                
                l = i - 1
                r = i + 2
                
                while l >= 0 and r < n and depth < max_depth:
                    if self._values_match(values[l], values[r], symmetry_mode):
                        depth += 1
                        left_idxs.append(l)
                        right_idxs.append(r)
                        l -= 1
                        r += 1
                    else:
                        break
                
                if depth >= min_depth:
                    left_idxs.reverse() # Outer -> Inner
                    right_idxs.reverse() # Outer -> Inner
                    
                    full_slice_indices = left_idxs + right_idxs[::-1]
                    
                    p = ChiasmusPattern(
                        center_index=None,
                        depth=depth,
                        left_indices=left_idxs,
                        right_indices=right_idxs,
                        source_units=[units[i] for i in full_slice_indices],
                        values=[values[i] for i in full_slice_indices],
                        symmetry_mode=symmetry_mode
                    )
                    found_patterns.append(p)

        return found_patterns
    
    def _scan_sum_balance(self, units: List[str], values: List[int], min_depth: int, max_depth: int) -> List[ChiasmusPattern]:
        """Special scanner for Sum Balance mode - finds patterns where left sum = right sum."""
        n = len(values)
        found_patterns = []
        
        # Scan for odd patterns (with center)
        for center in range(1, n - 1):
            for depth in range(min_depth, min(max_depth + 1, center + 1, n - center)):
                left_start = center - depth
                right_end = center + depth
                
                if left_start < 0 or right_end >= n:
                    break
                
                left_idxs = list(range(left_start, center))
                right_idxs = list(range(center + 1, right_end + 1))
                
                left_sum = sum(values[i] for i in left_idxs)
                right_sum = sum(values[i] for i in right_idxs)
                
                if left_sum == right_sum:
                    full_slice = left_idxs + [center] + right_idxs[::-1]
                    p = ChiasmusPattern(
                        center_index=center,
                        depth=depth,
                        left_indices=left_idxs,
                        right_indices=right_idxs,
                        source_units=[units[i] for i in full_slice],
                        values=[values[i] for i in full_slice],
                        symmetry_mode="Sum Balance"
                    )
                    found_patterns.append(p)
        
        # Scan for even patterns (no center)
        for i in range(n - 1):
            for depth in range(min_depth, min(max_depth + 1, i + 1, n - i - 1)):
                left_start = i - depth + 1
                right_end = i + depth
                
                if left_start < 0 or right_end >= n:
                    break
                
                left_idxs = list(range(left_start, i + 1))
                right_idxs = list(range(i + 1, right_end + 1))
                
                left_sum = sum(values[j] for j in left_idxs)
                right_sum = sum(values[j] for j in right_idxs)
                
                if left_sum == right_sum:
                    full_slice = left_idxs + right_idxs[::-1]
                    p = ChiasmusPattern(
                        center_index=None,
                        depth=depth,
                        left_indices=left_idxs,
                        right_indices=right_idxs,
                        source_units=[units[j] for j in full_slice],
                        values=[values[j] for j in full_slice],
                        symmetry_mode="Sum Balance"
                    )
                    found_patterns.append(p)

        return found_patterns