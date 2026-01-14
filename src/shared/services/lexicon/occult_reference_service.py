"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: Domain Logic (GRANDFATHERED - should move to pillars/lexicon)
- USED BY: Internal shared/ modules only (1 references)
- CRITERION: Violation (Single-pillar domain logic)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""
Occult Reference Service - Esoteric definitions from OpenOccult data.

Provides lookup for crystals, botanicals, runes, tarot, and other
esoteric terms from the OpenOccult data repository.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class OccultReference:
    """A reference entry from the occult data sources."""
    term: str               # The term/name
    category: str           # 'crystal', 'botanical', 'rune', 'tarot'
    description: str        # Main description/properties
    attributes: Dict[str, Any]  # Additional attributes (element, planet, etc.)
    source: str = "OpenOccult"


class OccultReferenceService:
    """
    Service for querying local esoteric reference data.
    
    Data sources (from OpenOccult repository):
    - crystals.json: Crystal/stone properties and meanings
    - botanicals.json: Herb and plant magical properties
    - runes.json: Elder Futhark rune meanings
    - tarot.json: Tarot card interpretations
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            # Try multiple paths
            possible_paths = [
                Path(__file__).parent.parent.parent.parent.parent / "data" / "openoccult",
                Path("data/openoccult"),
                Path.home() / ".isopgem" / "openoccult"
            ]
            for p in possible_paths:
                if p.exists():
                    data_dir = p
                    break
        
        self.data_dir = data_dir
        self._cache: Dict[str, List[Dict]] = {}
        self._index: Dict[str, List[OccultReference]] = {}  # word -> references
        self._loaded = False
        
    def _ensure_loaded(self):
        """Lazy load all data files and build search index."""
        if self._loaded:
            return
            
        if not self.data_dir or not self.data_dir.exists():
            logger.warning(f"OpenOccult data directory not found: {self.data_dir}")
            self._loaded = True
            return
            
        # Load each category
        self._load_crystals()
        self._load_botanicals()
        self._load_runes()
        self._load_tarot()
        
        self._loaded = True
        logger.debug(f"Loaded {len(self._index)} occult reference terms")
        
    def _load_json(self, filename: str) -> List[Dict]:
        """Load a JSON file from the data directory."""
        filepath = self.data_dir / filename
        if not filepath.exists():
            logger.warning(f"Data file not found: {filepath}")
            return []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return []
    
    def _add_to_index(self, term: str, ref: OccultReference):
        """Add a reference to the search index."""
        key = term.lower().strip()
        if key not in self._index:
            self._index[key] = []
        self._index[key].append(ref)
        
    def _load_crystals(self):
        """Load crystal data and index by name."""
        data = self._load_json("crystals.json")
        self._cache['crystals'] = data
        
        for item in data:
            name = item.get('crystalName', '')
            if not name:
                continue
                
            ref = OccultReference(
                term=name,
                category='crystal',
                description=item.get('properties', ''),
                attributes={
                    'element': item.get('element'),
                    'attribute': item.get('attribute'),
                    'color': item.get('color'),
                    'mohs': item.get('mohs'),
                }
            )
            self._add_to_index(name, ref)
            
    def _load_botanicals(self):
        """Load botanical/herb data and index by name and aliases."""
        data = self._load_json("botanicals.json")
        self._cache['botanicals'] = data
        
        for item in data:
            name = item.get('HerbName', '')
            if not name:
                continue
                
            ref = OccultReference(
                term=name,
                category='botanical',
                description=item.get('Description', ''),
                attributes={
                    'gender': item.get('Gender'),
                    'planet': item.get('Planet'),
                    'sign': item.get('Sign'),
                    'element': item.get('Element'),
                    'deities': item.get('Deities'),
                    'also_called': item.get('AlsoCalled'),
                    'warning': item.get('Warning'),
                }
            )
            self._add_to_index(name, ref)
            
            # Also index by alternate names
            also_called = item.get('AlsoCalled', '')
            if also_called:
                for alias in also_called.split(','):
                    alias = alias.strip()
                    if alias:
                        self._add_to_index(alias, ref)
                        
    def _load_runes(self):
        """Load rune data and index by name."""
        data = self._load_json("runes.json")
        self._cache['runes'] = data
        
        for item in data:
            # Skip the list item if present
            if 'list' in item:
                continue
                
            name = item.get('rune_title', '')
            if not name:
                continue
            
            # Build description from multiple fields
            desc_parts = []
            if item.get('meaning'):
                desc_parts.append(f"Meaning: {item['meaning']}")
            if item.get('esoteric_meaning'):
                desc_parts.append(f"Esoteric: {item['esoteric_meaning']}")
            if item.get('keywords'):
                desc_parts.append(f"Keywords: {item['keywords']}")
            if item.get('magick'):
                desc_parts.append(f"Magick: {item['magick']}")
                
            ref = OccultReference(
                term=name,
                category='rune',
                description='\n'.join(desc_parts),
                attributes={
                    'phonetic': item.get('phonetic'),
                    'galdr': item.get('galdr'),
                    'meaning': item.get('meaning'),
                    'esoteric_meaning': item.get('esoteric_meaning'),
                }
            )
            self._add_to_index(name, ref)
            
    def _load_tarot(self):
        """Load tarot card data and index by name."""
        data = self._load_json("tarot.json")
        self._cache['tarot'] = data
        
        for item in data:
            name = item.get('name', '')
            if not name:
                continue
            
            # Build description from upright/reversed
            desc_parts = []
            upright = item.get('upright', {})
            reversed_data = item.get('reversed', {})
            
            if upright.get('keywords'):
                desc_parts.append(f"Upright: {', '.join(upright['keywords'])}")
            if upright.get('description'):
                desc_parts.append(upright['description'][:200])
            if reversed_data.get('keywords'):
                desc_parts.append(f"Reversed: {', '.join(reversed_data['keywords'])}")
                
            ref = OccultReference(
                term=name,
                category='tarot',
                description='\n'.join(desc_parts),
                attributes={
                    'number': item.get('number'),
                    'arcana': item.get('arcana'),
                    'suit': item.get('suit'),
                    'upright_keywords': upright.get('keywords', []),
                    'reversed_keywords': reversed_data.get('keywords', []),
                }
            )
            self._add_to_index(name, ref)
            
            # Also index without "The " prefix
            if name.startswith('The '):
                self._add_to_index(name[4:], ref)
    
    def lookup(self, term: str) -> List[OccultReference]:
        """
        Look up a term in the occult reference data.
        Returns all matching references (may be multiple categories).
        """
        self._ensure_loaded()
        key = term.lower().strip()
        return self._index.get(key, [])
    
    def lookup_by_category(self, term: str, category: str) -> Optional[OccultReference]:
        """Look up a term in a specific category."""
        refs = self.lookup(term)
        for ref in refs:
            if ref.category == category:
                return ref
        return None
    
    def search(self, query: str, limit: int = 20) -> List[OccultReference]:
        """
        Search for terms containing the query string.
        Returns partial matches, useful for autocomplete.
        """
        self._ensure_loaded()
        query = query.lower().strip()
        results = []
        
        for term, refs in self._index.items():
            if query in term:
                results.extend(refs)
                if len(results) >= limit:
                    break
                    
        return results[:limit]
    
    def get_all_terms(self, category: Optional[str] = None) -> List[str]:
        """Get all indexed terms, optionally filtered by category."""
        self._ensure_loaded()
        terms = set()
        
        for term, refs in self._index.items():
            for ref in refs:
                if category is None or ref.category == category:
                    terms.add(ref.term)
                    
        return sorted(terms)
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about loaded data."""
        self._ensure_loaded()
        stats = {
            'total_terms': len(self._index),
            'crystals': len(self._cache.get('crystals', [])),
            'botanicals': len(self._cache.get('botanicals', [])),
            'runes': len([r for r in self._cache.get('runes', []) if 'rune_title' in r]),
            'tarot': len(self._cache.get('tarot', [])),
        }
        return stats