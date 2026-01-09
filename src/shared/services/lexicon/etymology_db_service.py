"""
Etymology Database Service.

Manages the etymology-db dataset (https://github.com/droher/etymology-db):
- 4.2M+ etymological relationships from Wiktionary
- 31 relationship types (inherited_from, borrowed_from, etc.)
- Structured, comprehensive, offline

Dataset schema:
- term_id: hash of term + language
- lang: language code  
- term: the word
- reltype: relationship type
- related_term_id, related_lang, related_term: etymological source
- position, group_tag, parent_tag, parent_position: complex relationships
"""
import csv
import gzip
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EtymologyRelation:
    """A single etymological relationship from the dataset."""
    term: str
    lang: str
    reltype: str
    related_term: Optional[str] = None
    related_lang: Optional[str] = None
    position: int = 0
    
    def to_display(self) -> str:
        """Format for UI display."""
        if not self.related_term:
            return f"{self.reltype.replace('_', ' ').title()}"
        
        # Format relationship types for readability
        rel_display = self.reltype.replace('_from', '').replace('_', ' ')
        
        if self.related_lang and self.related_lang != self.lang:
            return f"From {self.related_lang} '{self.related_term}' ({rel_display})"
        else:
            return f"From '{self.related_term}' ({rel_display})"


class EtymologyDbService:
    """
    Service for querying the etymology-db dataset.
    
    Uses word index for instant lookups when available, falls back to scanning.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the service.
        
        Args:
            db_path: Path to holy_key.db (not used, kept for compatibility)
        """
        self.csv_path = Path(__file__).parent.parent.parent.parent.parent / "data" / "etymology_db" / "etymology.csv.gz"
        self.index_path = self.csv_path.parent / "word_index.json"
        self.index: Optional[Dict[str, Dict[str, int]]] = None
        
        # Check if dataset exists
        self._ensure_loaded()
    
    def _ensure_loaded(self):
        """Check if CSV exists and load index if available."""
        if not self.csv_path.exists():
            logger.warning(f"Etymology CSV not found at {self.csv_path}")
            logger.warning("Download from: https://github.com/droher/etymology-db")
        else:
            logger.debug(f"Etymology CSV ready: {self.csv_path}")
        
        # Load index if exists
        if self.index_path.exists():
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    self.index = json.load(f)
                if self.index:
                    logger.debug(f"Loaded word index: {len(self.index):,} words")
            except Exception as e:
                logger.warning(f"Failed to load word index: {e}")
                self.index = None
        else:
            logger.debug("No word index found - queries will scan CSV (slower)")
            logger.debug(f"Build index with: python scripts/build_etymology_index.py")
    
    
    def get_etymologies(self, word: str, lang: str = "English", max_results: int = 10, max_scan_rows: int = 500_000) -> List[EtymologyRelation]:
        """
        Get etymology relationships for a word.
        
        Uses word index for instant lookup if available, otherwise scans CSV.
        
        Args:
            word: The word to look up
            lang: Language (default: English)
            max_results: Maximum number of results to return
            max_scan_rows: Maximum rows to scan if no index (500k ≈ 2s max)
            
        Returns:
            List of etymology relationships, prioritized by type
        """
        if not self.csv_path.exists():
            return []
        
        word_lower = word.lower()
        
        # Use index if available
        if self.index and lang == "English":
            return self._query_with_index(word_lower, max_results)
        else:
            return self._query_sequential(word_lower, lang, max_results, max_scan_rows)
    
    def _query_with_index(self, word: str, max_results: int) -> List[EtymologyRelation]:
        """Fast indexed lookup."""
        if not self.index or word not in self.index:
            return []
        
        word_info = self.index[word]
        start_row = word_info['start_row']
        expected_count = word_info['count']
        
        # If word is too far in file (>2M rows), fall back to sequential scan
        # Skipping through gzipped CSV is still sequential and slow
        if start_row > 2_000_000:
            logger.debug(f"Word '{word}' at row {start_row:,} - using sequential scan")
            return self._query_sequential(word, "English", max_results, 500_000)
        
        results: List[Tuple[int, EtymologyRelation]] = []
        
        # Priority order for relationship types
        priority = {
            'inherited_from': 1,
            'borrowed_from': 2,
            'learned_borrowing_from': 3,
            'derived_from': 4,
            'has_root': 5,
            'compound_of': 6
        }
        
        try:
            with gzip.open(self.csv_path, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Skip to start row (fast skip for rows < 2M)
                for _ in range(start_row - 1):
                    next(reader)
                
                # Collect all rows for this word
                found_count = 0
                for row in reader:
                    if row.get('term', '').lower() == word and row.get('lang') == 'English':
                        rel = EtymologyRelation(
                            term=row.get('term', ''),
                            lang=row.get('lang', ''),
                            reltype=row.get('reltype', ''),
                            related_term=row.get('related_term'),
                            related_lang=row.get('related_lang'),
                            position=int(row.get('position', 0)) if row.get('position') else 0
                        )
                        results.append((priority.get(rel.reltype, 10), rel))
                        found_count += 1
                        
                        # Stop when we've found all expected entries
                        if found_count >= expected_count:
                            break
                    elif found_count > 0:
                        # We've moved past this word's entries
                        break
            
            # Sort by priority, then position
            results.sort(key=lambda x: (x[0], x[1].position))
            return [rel for _, rel in results[:max_results]]
            
        except Exception as e:
            logger.error(f"Error reading etymology CSV: {e}")
            return []
    
    def _query_sequential(self, word: str, lang: str, max_results: int, max_scan_rows: int) -> List[EtymologyRelation]:
        """Fallback sequential scan (slower)."""
        results: List[Tuple[int, EtymologyRelation]] = []
        
        # Priority order for relationship types
        priority = {
            'inherited_from': 1,
            'borrowed_from': 2,
            'learned_borrowing_from': 3,
            'derived_from': 4,
            'has_root': 5,
            'compound_of': 6
        }
        
        try:
            with gzip.open(self.csv_path, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows_scanned = 0
                
                for row in reader:
                    rows_scanned += 1
                    
                    # Stop scanning after limit (prevents hangs on missing words)
                    if rows_scanned >= max_scan_rows:
                        if results:
                            logger.debug(f"Reached scan limit ({max_scan_rows:,} rows) - returning partial results")
                        else:
                            logger.debug(f"Word '{word}' not found in first {max_scan_rows:,} rows")
                        break
                    
                    # Only match our word and language
                    if row.get('term', '').lower() == word and row.get('lang') == lang:
                        rel = EtymologyRelation(
                            term=row.get('term', ''),
                            lang=row.get('lang', ''),
                            reltype=row.get('reltype', ''),
                            related_term=row.get('related_term'),
                            related_lang=row.get('related_lang'),
                            position=int(row.get('position', 0)) if row.get('position') else 0
                        )
                        results.append((priority.get(rel.reltype, 10), rel))
                        
                        # Stop early if we have enough
                        if len(results) >= max_results * 2:  # Get extra to sort
                            logger.debug(f"Found {len(results)} results after scanning {rows_scanned:,} rows")
                            break
            
            # Sort by priority, then position
            results.sort(key=lambda x: (x[0], x[1].position))
            return [rel for _, rel in results[:max_results]]
            
        except Exception as e:
            logger.error(f"Error reading etymology CSV: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the dataset (lightweight check)."""
        stats: Dict[str, Any] = {
            'dataset_source': 'etymology-db (2023-12-05)',
            'estimated_relationships': 4_200_000,
            'csv_exists': self.csv_path.exists()
        }
        
        if self.index:
            stats['indexed_words'] = len(self.index)
            stats['query_mode'] = 'indexed (fast)'
        else:
            stats['query_mode'] = 'sequential scan (slower)'
        
        return stats
