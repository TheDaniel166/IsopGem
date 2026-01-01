import re
import logging
from typing import List, Dict, Set, Optional, Tuple
from .key_database import KeyDatabase
from shared.services.gematria.tq_calculator import TQGematriaCalculator

logger = logging.getLogger(__name__)

class HolyKeyService:
    """
    Sovereign service for managing the Holy Book Key.
    Coordinates between document scanning, the Master Key database,
    and Gematria calculations.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.db = KeyDatabase(db_path)
        self.calculator = TQGematriaCalculator()

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

    def approve_candidate(self, word: str, source: Optional[str] = None) -> int:
        """
        Approve a word for the Master Key.
        Calculates TQ value, adds to Master Key,
        and optionally adds a default 'Standard' definition with the Source.
        """
        # Calculate TQ Value
        result = self.calculator.calculate(word)
        if isinstance(result, tuple):
             val = result[0]
        else:
             val = result
             
        new_id = self.db.add_word(word, val)
        
        # If source provided, record it as an Occurrence (Concordance)
        if source:
            self.db.add_occurrence(
                key_id=new_id,
                doc_path=source,
                line=0,
                context="Imported from batch scan"
            )
            # Do NOT create a dummy definition per user request
            
        return new_id

    def ignore_candidate(self, word: str):
        """Add word to the Ignore (Opt-out) list."""
        self.db.ignore_word(word)

    def get_undefined_keys(self) -> List[tuple]:
        """
        Return list of (id, word) for keys that have NO definitions.
        Used for batch enrichment.
        """
        conn = self.db._get_conn()
        cursor = conn.cursor()
        
        # Subquery to find keys not in definitions table
        cursor.execute("""
            SELECT id, word FROM master_key 
            WHERE is_active = 1 
            AND id NOT IN (SELECT DISTINCT key_id FROM definitions)
        """)
        
        rows = cursor.fetchall()
        conn.close()
        return [(row['id'], row['word']) for row in rows]

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

    def process_batch(self, words: List[str], source: str = "Magus") -> Tuple[int, int]:
        """
        Process a batch of words - add to Master Key.
        
        Args:
            words: List of words to add
            source: Source attribution for the batch
            
        Returns:
            Tuple of (added_count, already_existed_count)
        """
        added = 0
        already_existed = 0
        
        for word in words:
            w = word.lower()
            existing_id = self.db.get_id_by_word(w)
            
            if existing_id is not None:
                already_existed += 1
                continue
            
            # Calculate TQ and add
            tq_value = self.calculator.calculate(w)
            self.db.add_word(w, tq_value)
            added += 1
        
        return added, already_existed

    def bulk_ignore(self, words: List[str]):
        """
        Add multiple words to the ignore list.
        
        Args:
            words: List of words to ignore
        """
        for word in words:
            self.db.ignore_word(word.lower())
