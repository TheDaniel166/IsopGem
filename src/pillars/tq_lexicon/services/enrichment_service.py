from dataclasses import dataclass
from typing import List, Tuple, Callable, Optional
import logging
import requests
import time

try:
    import ety
    ETY_AVAILABLE = True
except ImportError:
    ETY_AVAILABLE = False

from .occult_reference_service import OccultReferenceService

logger = logging.getLogger(__name__)


@dataclass
class Suggestion:
    type: str       # 'Standard', 'Etymology', 'Occult', 'Botanical', 'Crystal', 'Rune', 'Tarot'
    content: str    # The definition text
    source: str     # 'FreeDict API', 'ety-python', 'OpenOccult', etc.
    part_of_speech: Optional[str] = None
    category: Optional[str] = None  # For occult: 'crystal', 'botanical', 'rune', 'tarot'


class EnrichmentService:
    """
    Service for enriching the Holy Key Lexicon with external data.
    
    Sources (in order of query):
    1. OpenOccult - Local esoteric reference data (crystals, herbs, runes, tarot)
    2. ety library - Etymology/word origins
    3. FreeDict API - Standard English definitions
    """
    
    # Map OpenOccult categories to definition types
    CATEGORY_TYPE_MAP = {
        'crystal': 'Alchemical',
        'botanical': 'Botanical', 
        'rune': 'Occult',
        'tarot': 'Divinatory',
    }
    
    def __init__(self, holy_key_service=None):
        self.hk_service = holy_key_service
        self._occult_service = None
        
    @property
    def occult_service(self) -> OccultReferenceService:
        """Lazy-load the occult reference service."""
        if self._occult_service is None:
            self._occult_service = OccultReferenceService()
        return self._occult_service

    def get_suggestions(self, word: str) -> List[Suggestion]:
        """
        Fetch all available suggestions (etymology + definitions + occult) for a word.
        Returns a list of Suggestion objects for the UI to display.
        
        Query order:
        1. OpenOccult (local, fast) - esoteric meanings
        2. Etymology (local) - word origins
        3. FreeDict API (online) - standard definitions
        """
        suggestions = []
        
        # 1. OpenOccult (Local esoteric data - query first as it's fast and specialized)
        occult_refs = self.occult_service.lookup(word)
        for ref in occult_refs:
            def_type = self.CATEGORY_TYPE_MAP.get(ref.category, 'Occult')
            
            # Format content based on category
            if ref.category == 'crystal':
                attrs = ref.attributes
                content = f"[{attrs.get('attribute', '')}] {ref.description[:300]}"
                if attrs.get('element'):
                    content += f" (Element: {attrs['element']})"
            elif ref.category == 'botanical':
                attrs = ref.attributes
                content = ref.description[:300]
                extras = []
                if attrs.get('planet'):
                    extras.append(f"Planet: {attrs['planet']}")
                if attrs.get('element'):
                    extras.append(f"Element: {attrs['element']}")
                if attrs.get('deities'):
                    extras.append(f"Deities: {attrs['deities']}")
                if extras:
                    content += f" ({'; '.join(extras)})"
            elif ref.category == 'rune':
                attrs = ref.attributes
                content = f"'{attrs.get('meaning', '')}' - {attrs.get('esoteric_meaning', '')}"
            elif ref.category == 'tarot':
                content = ref.description[:300]
            else:
                content = ref.description[:300]
                
            suggestions.append(Suggestion(
                type=def_type,
                content=content,
                source="OpenOccult",
                category=ref.category
            ))
        
        # 2. Etymology (Local)
        etyms = self.get_etymology(word)
        if etyms:
            content = "Recursive Origins: " + "; ".join(etyms[:5])
            suggestions.append(Suggestion(
                type="Etymology",
                content=content,
                source="ety-python"
            ))
            
        # 3. Standard Definitions (API)
        api_suggestions = self._fetch_freedict(word)
        suggestions.extend(api_suggestions)
            
        return suggestions
    
    def _fetch_freedict(self, word: str) -> List[Suggestion]:
        """Fetch definitions from FreeDict API."""
        suggestions = []
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list):
                    entry = data[0]
                    
                    # Phonetics
                    phonetics = entry.get('phonetics', [])
                    for p in phonetics:
                        if p.get('text'):
                            suggestions.append(Suggestion(
                                type="Phonetic",
                                content=f"IPA: {p.get('text')}",
                                source="FreeDict API"
                            ))
                            break

                    # Meanings
                    for m in entry.get('meanings', []):
                        pos = m.get('partOfSpeech', 'unknown')
                        for d in m.get('definitions', []):
                            def_text = d.get('definition')
                            if def_text:
                                suggestions.append(Suggestion(
                                    type="Standard",
                                    content=f"({pos}) {def_text}",
                                    source="FreeDict API",
                                    part_of_speech=pos
                                ))
        except Exception as e:
            logger.warning(f"FreeDict API Error for '{word}': {e}")
            
        return suggestions

    def fetch_definitions(self, word: str) -> List[str]:
        """Legacy helper for batch mode (just returns strings)."""
        suggs = self.get_suggestions(word)
        return [s.content for s in suggs if s.type == "Standard"]

    def get_etymology(self, word: str) -> List[str]:
        """Fetch etymology using local 'ety' library."""
        if not ETY_AVAILABLE:
            return []
        try:
            origins = ety.origins(word, recursive=True)
            if origins:
                return [f"{o.word} ({o.language.name})" for o in origins[:5]]
        except Exception as e:
            logger.warning(f"Etymology Error for '{word}': {e}")
        return []
    
    def get_etymology_tree(self, word: str) -> Optional[str]:
        """Get a formatted etymology tree for a word."""
        if not ETY_AVAILABLE:
            return None
        try:
            tree = ety.tree(word)
            if tree:
                return str(tree)
        except Exception:
            pass
        return None

    def enrich_batch(self, progress_callback: Callable[[int, int, str], None] = None):
        """
        Enrich all undefined keys.
        progress_callback: (current, total, status_message)
        """
        if not self.hk_service:
            logger.error("No holy_key_service configured for batch enrichment")
            return
            
        targets = self.hk_service.get_undefined_keys()
        total = len(targets)
        
        if total == 0:
            if progress_callback:
                progress_callback(0, 0, "No keys require enrichment.")
            return

        for i, (key_id, word) in enumerate(targets):
            if progress_callback:
                progress_callback(i + 1, total, f"Enriching: {word}")
            
            # Rate limit for API calls
            time.sleep(0.3)
            suggestions = self.get_suggestions(word)
            
            # Track what types we've added to avoid duplicates
            added_types = set()
            
            for s in suggestions:
                # Add Etymology (one per word)
                if s.type == "Etymology" and "Etymology" not in added_types:
                    self.hk_service.db.add_definition(key_id, s.type, s.content, source=s.source)
                    added_types.add("Etymology")
                    
                # Add Occult/Esoteric types (prioritize these)
                elif s.type in ('Occult', 'Alchemical', 'Botanical', 'Divinatory'):
                    if s.type not in added_types:
                        self.hk_service.db.add_definition(key_id, s.type, s.content, source=s.source)
                        added_types.add(s.type)
                        
                # Add Standard definitions (limit to 2)
                elif s.type == "Standard":
                    current_defs = self.hk_service.db.get_definitions(key_id)
                    standard_count = len([d for d in current_defs if d.type == "Standard"])
                    if standard_count < 2:
                        self.hk_service.db.add_definition(key_id, s.type, s.content, source=s.source)
    
    def get_source_stats(self) -> dict:
        """Get statistics about available enrichment sources."""
        stats = {
            'ety_available': ETY_AVAILABLE,
            'freedict_available': True,  # Always available (API)
            'openoccult': self.occult_service.get_stats() if self._occult_service else {}
        }
        return stats
