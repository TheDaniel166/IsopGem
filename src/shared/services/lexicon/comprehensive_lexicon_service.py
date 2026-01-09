"""
Comprehensive Lexicon Service - Dynamic multi-language support.

Automatically supports all configured languages in language_config.py
without requiring manual method creation for each one.
"""
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from .language_config import (
    LANGUAGE_CONFIGS,
    LanguageConfig,
    get_language_by_name,
    get_language_by_slug,
    get_source_filename,
    get_index_filename_base
)

logger = logging.getLogger(__name__)


@dataclass
class LexiconEntry:
    """A lexicon entry with full linguistic data."""
    word: str
    language: str
    transliteration: str
    definition: str
    etymology: Optional[str] = None
    strong_number: Optional[str] = None
    morphology: Optional[str] = None
    source: str = "Unknown"


class ComprehensiveLexiconService:
    """
    Comprehensive lexicon service supporting all configured languages.

    Features:
    - Automatic support for all languages in language_config.py
    - Lazy loading of dictionaries (only load when queried)
    - Compact index-based lookups for fast performance
    - Fallback to Strong's dictionaries for Hebrew/Greek
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            data_dir = Path(__file__).parent.parent.parent.parent.parent / "data" / "lexicons"

        self.data_dir = data_dir
        self.index_dir = data_dir / "indexes"

        # Lazy-loaded indexes and file handles (keyed by language slug)
        self._compact_indexes: Dict[str, Optional[Dict[str, int]]] = {}
        self._compact_handles: Dict[str, Optional[Any]] = {}

        # Strong's dictionaries (legacy support)
        self._strongs_greek: Optional[List[Dict]] = None
        self._strongs_hebrew: Optional[List[Dict]] = None

    def lookup(self, word: str, language: str) -> List[LexiconEntry]:
        """
        Look up a word in a specific language.

        Args:
            word: The word to look up
            language: Language name (e.g., "Old English", "Coptic", "Akkadian")

        Returns:
            List of lexicon entries
        """
        # Get language config
        lang_config = get_language_by_name(language)
        if not lang_config:
            logger.warning(f"Unknown language: {language}")
            return []

        # Try compact index lookup
        results = self._query_compact(word, lang_config)

        # Fallback to Strong's for Hebrew/Greek if available
        if not results and language.lower() in ["hebrew", "greek", "ancient greek"]:
            if "hebrew" in language.lower():
                results = self._query_strongs_hebrew(word)
            else:
                results = self._query_strongs_greek(word)

        return results

    def lookup_multi_language(self, word: str, languages: List[str]) -> Dict[str, List[LexiconEntry]]:
        """
        Look up a word across multiple languages.

        Args:
            word: The word to look up
            languages: List of language names

        Returns:
            Dict mapping language name to list of entries
        """
        results = {}
        for language in languages:
            entries = self.lookup(word, language)
            if entries:
                results[language] = entries
        return results

    def lookup_by_category(self, word: str, category: str) -> Dict[str, List[LexiconEntry]]:
        """
        Look up a word across all languages in a category.

        Args:
            word: The word to look up
            category: Category name (e.g., "core_ancient", "medieval_bridge")

        Returns:
            Dict mapping language name to list of entries
        """
        from .language_config import get_languages_by_category

        languages = get_languages_by_category(category)
        results = {}

        for lang_config in languages:
            entries = self._query_compact(word, lang_config)
            if entries:
                results[lang_config.name] = entries

        return results

    def _load_compact_index(self, lang_config: LanguageConfig) -> bool:
        """Lazy-load compact index for a language."""
        slug = lang_config.slug

        # Already attempted to load
        if slug in self._compact_indexes:
            return self._compact_indexes[slug] is not None

        index_path = self.index_dir / f"{get_index_filename_base(lang_config)}-index.json"

        if not index_path.exists():
            logger.debug(f"No index for {lang_config.name} at {index_path}")
            self._compact_indexes[slug] = None
            return False

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                self._compact_indexes[slug] = json.load(f)
            logger.debug(f"Loaded index for {lang_config.name}: {len(self._compact_indexes[slug])} keys")
            return True
        except Exception as e:
            logger.error(f"Failed to load index for {lang_config.name}: {e}")
            self._compact_indexes[slug] = None
            return False

    def _get_compact_handle(self, lang_config: LanguageConfig) -> Optional[Any]:
        """Get or create file handle for compact data file."""
        slug = lang_config.slug

        # Already have handle
        if slug in self._compact_handles:
            return self._compact_handles[slug]

        data_path = self.index_dir / f"{get_index_filename_base(lang_config)}-mini.jsonl"

        if not data_path.exists():
            logger.debug(f"No mini data for {lang_config.name} at {data_path}")
            self._compact_handles[slug] = None
            return None

        try:
            handle = open(data_path, 'r', encoding='utf-8')
            self._compact_handles[slug] = handle
            return handle
        except Exception as e:
            logger.error(f"Failed to open data file for {lang_config.name}: {e}")
            self._compact_handles[slug] = None
            return None

    def _query_compact(self, word: str, lang_config: LanguageConfig) -> List[LexiconEntry]:
        """Query compact index/data files for a language."""
        # Load index
        if not self._load_compact_index(lang_config):
            return []

        index = self._compact_indexes[lang_config.slug]
        if not index:
            return []

        # Get file handle
        handle = self._get_compact_handle(lang_config)
        if not handle:
            return []

        # Try multiple search variants
        from .classical_lexicon_service import remove_accents

        word_lower = word.lower()
        word_no_accents = remove_accents(word_lower)
        word_no_hyphen = word_no_accents.replace('-', '')

        # For PIE, also try without leading asterisk
        search_variants = [word, word_lower, word_no_accents, word_no_hyphen]
        if word.startswith('*'):
            search_variants.append(word[1:])
            search_variants.append(word[1:].lower())

        # Try each variant
        for variant in search_variants:
            offset = index.get(variant)
            if offset is None:
                continue

            try:
                handle.seek(offset)
                line = handle.readline()
                if not line:
                    continue

                data = json.loads(line)

                # Extract entry data
                lemma = data.get('word', word)
                romanization = data.get('romanization', '')
                glosses = data.get('glosses', [])
                definition = '; '.join(glosses[:8]) if glosses else ''
                etymology_text = data.get('etymology_text') or None
                pos = data.get('pos', 'unknown')
                morphology = f"Part of speech: {pos}" if pos != 'unknown' else None

                return [LexiconEntry(
                    word=lemma,
                    language=lang_config.name,
                    transliteration=romanization,
                    definition=definition,
                    etymology=etymology_text,
                    morphology=morphology,
                    source="Kaikki.org Wiktionary (compact)"
                )]
            except Exception as e:
                logger.error(f"Compact query failed for {lang_config.name}: {e}")
                continue

        return []

    def _load_strongs_greek(self):
        """Lazy-load Strong's Greek dictionary."""
        if self._strongs_greek is not None:
            return

        json_path = self.data_dir / "strongs_greek.json"
        if not json_path.exists():
            logger.debug("Strong's Greek not found")
            self._strongs_greek = []
            return

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self._strongs_greek = json.load(f)
            logger.debug(f"Loaded {len(self._strongs_greek)} Strong's Greek entries")
        except Exception as e:
            logger.error(f"Failed to load Strong's Greek: {e}")
            self._strongs_greek = []

    def _load_strongs_hebrew(self):
        """Lazy-load Strong's Hebrew dictionary."""
        if self._strongs_hebrew is not None:
            return

        json_path = self.data_dir / "strongs_hebrew.json"
        if not json_path.exists():
            logger.debug("Strong's Hebrew not found")
            self._strongs_hebrew = []
            return

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self._strongs_hebrew = json.load(f)
            logger.debug(f"Loaded {len(self._strongs_hebrew)} Strong's Hebrew entries")
        except Exception as e:
            logger.error(f"Failed to load Strong's Hebrew: {e}")
            self._strongs_hebrew = []

    def _query_strongs_greek(self, word: str) -> List[LexiconEntry]:
        """Query Strong's Greek dictionary."""
        from .classical_lexicon_service import remove_accents

        self._load_strongs_greek()
        if not self._strongs_greek:
            return []

        results = []
        word_lower = word.lower()
        word_no_accents = remove_accents(word_lower)

        for entry in self._strongs_greek:
            entry_word = entry.get('word', '')
            entry_translit = entry.get('translit', '')

            if (entry_word and remove_accents(entry_word.lower()) == word_no_accents) or \
               (entry_translit and remove_accents(entry_translit.lower()) == word_no_accents):
                results.append(LexiconEntry(
                    word=entry.get('word', word),
                    language="Greek",
                    transliteration=entry.get('translit', ''),
                    definition=entry.get('definition', ''),
                    etymology=entry.get('derivation'),
                    strong_number=entry.get('strongs'),
                    source="Strong's"
                ))

        return results

    def _query_strongs_hebrew(self, word: str) -> List[LexiconEntry]:
        """Query Strong's Hebrew dictionary."""
        from .classical_lexicon_service import remove_accents

        self._load_strongs_hebrew()
        if not self._strongs_hebrew:
            return []

        results = []
        word_lower = word.lower()
        word_no_accents = remove_accents(word_lower)

        for entry in self._strongs_hebrew:
            entry_word = entry.get('word', '')
            entry_translit = entry.get('translit', '')

            if (entry_word and remove_accents(entry_word.lower()) == word_no_accents) or \
               (entry_translit and remove_accents(entry_translit.lower()) == word_no_accents):
                results.append(LexiconEntry(
                    word=entry.get('word', word),
                    language="Hebrew",
                    transliteration=entry.get('translit', ''),
                    definition=entry.get('definition', ''),
                    etymology=entry.get('derivation'),
                    strong_number=entry.get('strongs'),
                    source="Strong's"
                ))

        return results

    def get_available_languages(self) -> List[str]:
        """Get list of languages with available data."""
        available = []

        for lang_config in LANGUAGE_CONFIGS:
            index_path = self.index_dir / f"{get_index_filename_base(lang_config)}-index.json"
            data_path = self.index_dir / f"{get_index_filename_base(lang_config)}-mini.jsonl"

            if index_path.exists() and data_path.exists():
                available.append(lang_config.name)

        return available

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about available lexicons."""
        available = self.get_available_languages()

        return {
            'total_configured': len(LANGUAGE_CONFIGS),
            'total_available': len(available),
            'available_languages': available,
            'categories': {
                'core_ancient': len([l for l in LANGUAGE_CONFIGS if l.category == 'core_ancient']),
                'medieval_bridge': len([l for l in LANGUAGE_CONFIGS if l.category == 'medieval_bridge']),
                'ancient_semitic': len([l for l in LANGUAGE_CONFIGS if l.category == 'ancient_semitic']),
                'ancient_ie': len([l for l in LANGUAGE_CONFIGS if l.category == 'ancient_ie']),
                'modern_major': len([l for l in LANGUAGE_CONFIGS if l.category == 'modern_major']),
                'other_ancient': len([l for l in LANGUAGE_CONFIGS if l.category == 'other_ancient']),
            }
        }

    def __del__(self):
        """Cleanup: close all open file handles."""
        for handle in self._compact_handles.values():
            if handle:
                try:
                    handle.close()
                except:
                    pass
