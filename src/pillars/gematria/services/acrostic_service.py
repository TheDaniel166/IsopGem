"""Service for discovering acrostics and telestichs in text."""
import re
import logging
from typing import List, Dict, Optional, Tuple  # type: ignore[reportUnusedImport]
from pillars.gematria.services.corpus_dictionary_service import CorpusDictionaryService

logger = logging.getLogger(__name__)

# Common stopwords to filter out if requested
STOPWORDS = {
    "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER", "WAS", "ONE",
    "OUR", "OUT", "HAD", "HAS", "HIS", "HOW", "MAN", "OLD", "SEE", "VERY", "WHEN",
    "WHO", "NOW", "THAN", "FIND", "HERE", "JUST", "LIKE", "LONG", "MAKE", "MANY", "OVER",
    "SUCH", "TAKE", "THEM", "WELL", "ONLY", "COME", "INTO", "YEAR", "YOUR", "GOOD", "SOME",
    "COULD", "THERE", "THEIR", "ABOUT", "WOULD", "THESE", "OTHER", "WHICH", "FIRST", "AFTER"
}

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
                      mode: str = "Line",
                      min_length: int = 3,
                      longest_only: bool = False,
                      filter_stopwords: bool = False,
                      skip_pattern: int = 1) -> List[AcrosticResult]:
        """
        Finds acrostics in the given text.
        
        Args:
            text: The source text.
            check_first: Check for First Letter Acrostics.
            check_last: Check for Last Letter Telestichs.
            mode: "Line" (checks start/end of lines) or "Word" (checks start/end of every word).
            min_length: Minimum word length to consider (3-10).
            longest_only: If True, only return longest non-overlapping matches.
            filter_stopwords: If True, exclude common stopwords (the, and, for, etc.).
            skip_pattern: Extract every Nth letter (1=consecutive, 2=every other, etc.).
        """
        results = []
        
        if mode == "Line":
            units = [line.strip() for line in text.splitlines() if line.strip()]
        else: # Word mode
            units = text.split()
            
        if not units:
            return []

        # 1. Extract Sequences with skip pattern support
        first_letters = []
        last_letters = []
        
        valid_indices = [] # Indices of units that actually had letters
        
        for idx, unit in enumerate(units):
            # Apply skip pattern (e.g., skip_pattern=2 means every other unit)
            if idx % skip_pattern != 0:
                continue
                
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
            if seq_len < min_length:
                if self.dictionary_service.is_word(full_sequence):
                    if filter_stopwords and full_sequence in STOPWORDS:
                        continue
                    # Map indices to source units
                    source_units = [units[i] for i in valid_indices]
                    results.append(AcrosticResult(full_sequence, f"{method_name} ({mode})", valid_indices, source_units, True))  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
                continue

            # Check for any valid sub-words
            found_words = []
            
            for length in range(min_length, seq_len + 1):
                for start in range(seq_len - length + 1):
                    end = start + length
                    sub = full_sequence[start:end]
                    
                    if self.dictionary_service.is_word(sub):
                        # Apply stopword filter
                        if filter_stopwords and sub in STOPWORDS:
                            continue
                            
                        match_indices = valid_indices[start:end]
                        source_units = [units[i] for i in match_indices]
                        
                        found_words.append({
                            'word': sub,
                            'start': start,
                            'end': end,
                            'indices': match_indices,
                            'units': source_units
                        })
            
            # Filter to longest-only if requested
            if longest_only and found_words:
                found_words = self._filter_longest_only(found_words)
            
            # Add results
            for word_data in found_words:
                results.append(AcrosticResult(
                    word_data['word'],
                    f"{method_name} ({mode})",
                    word_data['indices'],
                    word_data['units'],
                    True
                ))
            
            if not found_words:
                 # Map indices to source units
                 source_units = [units[i] for i in valid_indices]
                 results.append(AcrosticResult(full_sequence, f"{method_name} (Raw)", valid_indices, source_units, False))  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        
        return results
    
    def _filter_longest_only(self, found_words: List[dict]) -> List[dict]:
        """Filter to keep only longest non-overlapping matches."""
        if not found_words:
            return []
        
        # Sort by length (descending), then by start position
        sorted_words = sorted(found_words, key=lambda w: (-len(w['word']), w['start']))
        
        kept = []
        used_positions = set()
        
        for word_data in sorted_words:
            # Check if this word overlaps with any kept word
            positions = set(range(word_data['start'], word_data['end']))
            if not positions.intersection(used_positions):
                kept.append(word_data)
                used_positions.update(positions)
        
        # Sort back by start position for display
        return sorted(kept, key=lambda w: w['start'])