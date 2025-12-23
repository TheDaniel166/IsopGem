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
    center_index: Optional[int]  # None if even length center (A-B-B-A), int if odd (A-B-C-B-A)
    depth: int                  # How many layers deep (excluding center)
    left_indices: List[int]     # Indices of the left side [A, B...]
    right_indices: List[int]    # Indices of the right side [...B, A]
    source_units: List[str]     # The actual words
    values: List[int]           # The gematria values

class ChiasmusService:
    def __init__(self):
        pass

    def scan_text(self, text: str, calculator, max_depth: int = 10) -> List[ChiasmusPattern]:
        """
        Scans text for Gematria-based Chiastic patterns.
        
        Args:
            text: Input text
            calculator: GematriaCalculator instance (must have .calculate(str) -> int)
            max_depth: Maximum number of mirrored layers to scan for.
                       Limits the size of the found patterns.
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

        # 2. Scan for Odd Patterns (A-B-C-B-A) -> Single Pivot
        for center in range(1, n - 1):
            depth = 0
            left_idxs = []
            right_idxs = []
            
            l = center - 1
            r = center + 1
            
            while l >= 0 and r < n and depth < max_depth:
                if values[l] == values[r]:
                    depth += 1
                    left_idxs.append(l)
                    right_idxs.append(r)
                    l -= 1
                    r += 1
                else:
                    break
            
            if depth >= 1:
                left_idxs.reverse()
                right_idxs.reverse()
                
                full_slice_indices = left_idxs + [center] + right_idxs[::-1] 
                
                p = ChiasmusPattern(
                    center_index=center,
                    depth=depth,
                    left_indices=left_idxs, # Outer -> Inner
                    right_indices=right_idxs, # Outer -> Inner
                    source_units=[units[i] for i in full_slice_indices],
                    values=[values[i] for i in full_slice_indices]
                )
                found_patterns.append(p)

        # 3. Scan for Even Patterns (A-B-B-A) -> No Pivot, just mirror
        for i in range(n - 1):
            if values[i] == values[i+1]:
                # Potential even center found
                depth = 1
                left_idxs = [i]
                right_idxs = [i+1]
                
                l = i - 1
                r = i + 2
                
                while l >= 0 and r < n and depth < max_depth:
                    if values[l] == values[r]:
                        depth += 1
                        left_idxs.append(l)
                        right_idxs.append(r)
                        l -= 1
                        r += 1
                    else:
                        break
                
                if depth >= 1:
                    left_idxs.reverse() # Outer -> Inner
                    right_idxs.reverse() # Outer -> Inner
                    
                    full_slice_indices = left_idxs + right_idxs[::-1]
                    
                    p = ChiasmusPattern(
                        center_index=None,
                        depth=depth,
                        left_indices=left_idxs,
                        right_indices=right_idxs,
                        source_units=[units[i] for i in full_slice_indices],
                        values=[values[i] for i in full_slice_indices]
                    )
                    found_patterns.append(p)

        return found_patterns
