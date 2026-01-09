from dataclasses import dataclass
from typing import List, Callable, Optional
import logging
import requests
import time

from .occult_reference_service import OccultReferenceService
from .theosophical_glossary_service import TheosophicalGlossaryService
from .etymology_db_service import EtymologyDbService

logger = logging.getLogger(__name__)


@dataclass
class Suggestion:
    type: str       # 'Standard', 'Etymology', 'Occult', 'Botanical', 'Theosophical', etc.
    content: str    # The definition text
    source: str     # 'FreeDict API', 'Wiktionary', 'OpenOccult', 'Theosophical Glossary', etc.
    part_of_speech: Optional[str] = None
    category: Optional[str] = None  # For occult: 'crystal', 'botanical', 'rune', 'tarot'


class EnrichmentService:
    """
    Service for enriching the Holy Key Lexicon with external data.
    
    Sources (in order of query):
    1. Theosophical Glossary - G. de Purucker esoteric definitions
    2. OpenOccult - Local esoteric reference data (crystals, herbs, runes, tarot)
    3. Etymology-DB - Offline structured etymology database (4.2M relationships)
    4. Wiktionary - Standard definitions (online)
    5. FreeDict API - Standard English definitions (online)
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
        self._theosophical_service = None
        self._etymology_service = None
        
    @property
    def occult_service(self) -> OccultReferenceService:
        """Lazy-load the occult reference service."""
        if self._occult_service is None:
            self._occult_service = OccultReferenceService()
        return self._occult_service

    @property
    def theosophical_service(self) -> TheosophicalGlossaryService:
        """Lazy-load the Theosophical glossary service."""
        if self._theosophical_service is None:
            self._theosophical_service = TheosophicalGlossaryService()
        return self._theosophical_service
    
    @property
    def etymology_service(self) -> EtymologyDbService:
        """Lazy-load the etymology database service."""
        if self._etymology_service is None:
            self._etymology_service = EtymologyDbService()
        return self._etymology_service

    def get_suggestions(self, word: str) -> List[Suggestion]:
        """
        Fetch all available suggestions for a word.
        Returns a list of Suggestion objects for the UI to display.
        
        Query order (Principle of Apocalypsis - complete revelation):
        1. Theosophical Glossary (local) - G. de Purucker esoteric definitions
        2. OpenOccult (local) - crystals, herbs, runes, tarot
        3. Etymology-DB (local) - structured etymology relationships
        4. Wiktionary (online) - standard definitions
        5. FreeDict API (online) - standard definitions
        """
        suggestions = []
        
        # 1. Theosophical Glossary (Local esoteric - G. de Purucker)
        theo_entries = self.theosophical_service.lookup(word)
        for entry in theo_entries:
            # Format with language if present
            lang_note = f" ({entry.language})" if entry.language else ""
            suggestions.append(Suggestion(
                type="Theosophical",
                content=f"{entry.term}{lang_note}: {entry.definition}",
                source="Theosophical Glossary"
            ))
        
        # 2. OpenOccult (Local esoteric data - crystals, herbs, runes, tarot)
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
        
        # 3. Etymology-DB (local structured dataset)
        try:
            etym_relations = self.etymology_service.get_etymologies(word, lang="English", max_results=10)
            for rel in etym_relations:
                suggestions.append(Suggestion(
                    type="Etymology",
                    content=rel.to_display(),
                    source="Etymology-DB"
                ))
        except Exception as e:
            logger.debug(f"Etymology-DB lookup failed for '{word}': {e}")
        
        # 4. Wiktionary (standard definitions)
        wiki_defs = self._fetch_wiktionary_definitions(word)
        suggestions.extend(wiki_defs)
            
        # 5. Standard Definitions (FreeDict API)
        api_suggestions = self._fetch_freedict(word)
        suggestions.extend(api_suggestions)
            
        return suggestions

    def _fetch_wiktionary_definitions(self, word: str) -> List[Suggestion]:
        """Fetch standard definitions from Wiktionary (no etymology - that's in etymology-db now)."""
        suggestions = []

        def_url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{word}"

        try:
            response = requests.get(def_url, timeout=5, headers={
                'User-Agent': 'IsopGem/1.0 (Esoteric Research Tool)'
            })

            if response.status_code == 200:
                data = response.json()

                # Parse English entries for definitions
                for lang_entry in data.get('en', []):
                    pos = lang_entry.get('partOfSpeech', '')

                    for definition in lang_entry.get('definitions', []):
                        def_text = definition.get('definition', '')

                        # Clean HTML tags
                        import re
                        def_text = re.sub(r'<[^>]+>', '', def_text)

                        if def_text:
                            suggestions.append(Suggestion(
                                type="Standard",
                                content=f"({pos}) {def_text}",
                                source="Wiktionary",
                                part_of_speech=pos
                            ))
        except Exception as e:
            logger.debug(f"Wiktionary definition API error for '{word}': {e}")

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

    def enrich_batch(self, progress_callback: Callable[[int, int, str], None] = None):
        """
        Enrich all undefined keys (skeletons → flesh).
        Applies the Principle of Apocalypsis: ALL definitions, no limits.
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

        total_added = 0
        for i, (key_id, word) in enumerate(targets):
            if progress_callback:
                progress_callback(i + 1, total, f"Enriching: {word}")
            
            # Rate limit for API calls
            time.sleep(0.3)
            suggestions = self.get_suggestions(word)
            
            # Principle of Apocalypsis: ALL revelation, no veils
            for s in suggestions:
                self.hk_service.db.add_definition(key_id, s.type, s.content, source=s.source)
                total_added += 1
        
        if progress_callback:
            progress_callback(total, total, f"Complete. Added {total_added} definitions to {total} words.")
    
    def get_source_stats(self) -> dict:
        """Get statistics about available enrichment sources."""
        stats = {
            'etymology_db': self.etymology_service.get_stats() if self._etymology_service else {},
            'wiktionary_available': True,  # Always available (API)
            'freedict_available': True,  # Always available (API)
            'openoccult': self.occult_service.get_stats() if self._occult_service else {},
            'theosophical': 'Loaded' if self._theosophical_service else 'Not initialized'
        }
        return stats
