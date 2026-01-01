import re
import logging
from typing import List, Dict, Set, Optional, Tuple
from .key_database import KeyDatabase
from shared.services.gematria.tq_calculator import TQPositionCalculator

logger = logging.getLogger(__name__)

class HolyKeyService:
    """
    Sovereign service for managing the Holy Book Key.
    Coordinates between document scanning, the Master Key database,
    and Gematria calculations.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.db = KeyDatabase(db_path)
        self.calculator = TQPositionCalculator() 

    def scan_text(self, text: str) -> List[str]:
        """
        Scan text for 'Candidates' - words that are:
        1. Not yet in the Master Key
        2. Not in the Ignored Words list
        3. Valid alphanumeric words
        
        Returns a sorted list of unique candidate words.
        """
        # 1. Tokenize (simple regex for now, can be enhanced)
        # Using a pattern that captures words with hyphens or apostrophes if desired, 
        # but TQ usually strictly alphanumeric.
        # Let's strip non-alphanumeric for safe TQ calculation.
        raw_words = re.findall(r"\b[a-zA-Z]+\b", text)
        
        candidates = set()
        
        # Cache ignored list to avoid DB hits in loop
        ignored_set = set(self.db.get_all_ignored())
        
        for word in raw_words:
            w = word.lower()
            if len(w) < 2:  # Skip single letters? key decision. Let's keep them for now if meaningful (I 'I').
                continue
                
            if w in ignored_set:
                continue
                
            # Check if exists in master key (could optimize this with bulk check)
            if self.db.get_id_by_word(w) is not None:
                continue
                
            candidates.add(w)
            
        return sorted(list(candidates))

    def approve_candidate(self, word: str) -> int:
        """
        Approve a word for the Master Key.
        Calculates its TQ value and adds it to the DB.
        Returns the new Key ID.
        """
        # Calculate TQ Value
        # value, breakdown = self.calculator.calculate(word)
        # TQPositionCalculator.calculate returns (value, breakdown) or just value depending on implementation
        # Let's check calculate method signature
        result = self.calculator.calculate(word)
        if isinstance(result, tuple):
             val = result[0]
        else:
             val = result
             
        return self.db.add_word(word, val)

    def ignore_candidate(self, word: str):
        """Add word to the Ignore (Opt-out) list."""
        self.db.ignore_word(word)

    def get_lexicon_stats(self) -> Dict[str, int]:
        """Return stats for UI dashboard."""
        conn = self.db._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM master_key WHERE is_active = 1")
        total_keys = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM definitions")
        total_defs = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ignored_words")
        total_ignored = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_keys": total_keys,
            "total_definitions": total_defs,
            "total_ignored": total_ignored
        }
