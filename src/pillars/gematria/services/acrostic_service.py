"""Service for discovering acrostics and telestichs in text."""
import re
import logging
from typing import List, Dict, Optional, Tuple
from pillars.gematria.services.corpus_dictionary_service import CorpusDictionaryService

logger = logging.getLogger(__name__)

class AcrosticResult:
    """
    Acrostic Result class definition.
    
    Attributes:
        found_word: Description of found_word.
        method: Description of method.
        source_indices: Description of source_indices.
        source_text_units: Description of source_text_units.
        is_valid_word: Description of is_valid_word.
    
    """
    def __init__(self, 
                 found_word: str, 
                 method: str, 
                 source_indices: List[int],
                 source_text_units: List[str] = None, 
                 is_valid_word: bool = False):
        """
          init   logic.
        
        Args:
            found_word: Description of found_word.
            method: Description of method.
            source_indices: Description of source_indices.
            source_text_units: Description of source_text_units.
            is_valid_word: Description of is_valid_word.
        
        """
        self.found_word = found_word
        self.method = method  # "First Letter (Line)", "Last Letter (Word)", etc.
        self.source_indices = source_indices  # Indices of lines/words used
        self.source_text_units = source_text_units or []
        self.is_valid_word = is_valid_word

    def __repr__(self):
        return f"<Acrostic({self.found_word}, valid={self.is_valid_word})>"

class AcrosticService:
    """
    Acrostic Service class definition.
    
    Attributes:
        dictionary_service: Description of dictionary_service.
    
    """
    def __init__(self):
        """
          init   logic.
        
        """
        self.dictionary_service = CorpusDictionaryService()

    def find_acrostics(self, 
                      text: str, 
                      check_first: bool = True, 
                      check_last: bool = True,
                      mode: str = "Line") -> List[AcrosticResult]:
        """
        Finds acrostics in the given text.
        
        Args:
            text: The source text.
            check_first: Check for First Letter Acrostics.
            check_last: Check for Last Letter Telestichs.
            mode: "Line" (checks start/end of lines) or "Word" (checks start/end of every word).
        """
        results = []
        
        if mode == "Line":
            units = [line.strip() for line in text.splitlines() if line.strip()]
        else: # Word mode
            units = text.split()
            
        if not units:
            return []

        # 1. Extract Sequences
        first_letters = []
        last_letters = []
        
        valid_indices = [] # Indices of units that actually had letters
        
        for idx, unit in enumerate(units):
            # clean unit for letter extraction
            clean = re.sub(r'[^a-zA-Z]', '', unit)
            if not clean:
                continue
                
            if check_first:
                first_letters.append(clean[0].upper())
            if check_last:
                last_letters.append(clean[-1].upper())
            valid_indices.append(idx)

        # 2. Form Candidates and Scan for Substrings
        
        candidates = []
        if check_first:
            candidates.append(("First Letter", first_letters))
        if check_last:
            candidates.append(("Last Letter", last_letters))
            
        for method_name, letters in candidates:
            full_sequence = "".join(letters)
            seq_len = len(full_sequence)
            
            # If the sequence is short, check it directly
            if seq_len < 3:
                if self.dictionary_service.is_word(full_sequence):
                    # Map indices to source units
                    source_units = [units[i] for i in valid_indices]
                    results.append(AcrosticResult(full_sequence, f"{method_name} ({mode})", valid_indices, source_units, True))
                continue

            # Check for any valid sub-words
            found_any = False
            
            for length in range(3, seq_len + 1):
                for start in range(seq_len - length + 1):
                    end = start + length
                    sub = full_sequence[start:end]
                    
                    if self.dictionary_service.is_word(sub):
                        match_indices = valid_indices[start:end]
                        # Extract source units for this specific substring
                        source_units = [units[i] for i in match_indices]
                        
                        results.append(AcrosticResult(
                            sub, 
                            f"{method_name} ({mode})", 
                            match_indices,
                            source_units,
                            True
                        ))
                        found_any = True
            
            if not found_any:
                 # Map indices to source units
                 source_units = [units[i] for i in valid_indices]
                 results.append(AcrosticResult(full_sequence, f"{method_name} (Raw)", valid_indices, source_units, False))
        
        return results