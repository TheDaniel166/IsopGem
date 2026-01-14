"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: Domain Logic (GRANDFATHERED - should move to pillars/lexicon)
- USED BY: Gematria (3 references)
- CRITERION: Violation (Single-pillar domain logic)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""


"""
Classical Lexicon Service - Greek and Hebrew word lookups.

Integrates:
1. Strong's Greek Dictionary (~5,500 Biblical Greek entries)
2. Strong's Hebrew Dictionary (~8,600 Biblical Hebrew entries)
3. Perseus Liddell-Scott Lexicon (~116,000 Classical Greek entries)

Provides deep etymological and morphological analysis for
classical language terms.
"""
import json
import logging
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict
import re
import unicodedata

logger = logging.getLogger(__name__)


def remove_accents(text: str) -> str:
    """Remove diacritical marks (accents) from text for fuzzy matching."""
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )


def phonetic_normalize_greek(text: str) -> str:
    """Normalize Greek text for phonetic fuzzy matching.
    
    Handles common vowel confusions:
    - η (eta) ↔ ε (epsilon) - both can sound like 'e'
    - ω (omega) ↔ ο (omicron) - both can sound like 'o'
    - ι (iota), η (eta), υ (upsilon) can all sound like 'i'
    
    This allows users who type βετα to find βῆτα.
    """
    # Remove accents first
    text = remove_accents(text)
    
    # Normalize vowel variations to their "simple" forms
    # η → ε (eta to epsilon)
    text = text.replace('η', 'ε')
    # ω → ο (omega to omicron)
    text = text.replace('ω', 'ο')
    # Also handle uppercase
    text = text.replace('Η', 'Ε')
    text = text.replace('Ω', 'Ο')
    
    return text


@dataclass
class LexiconEntry:
    """A lexicon entry with full linguistic data."""
    word: str
    language: str  # "Greek", "Hebrew"
    transliteration: str
    definition: str
    etymology: Optional[str] = None
    strong_number: Optional[str] = None
    morphology: Optional[str] = None
    source: str = "Unknown"  # "Strong's", "Perseus"


class ClassicalLexiconService:
    """
    Service for querying Greek and Hebrew lexicons.

    Automatically uses the best source:
    - Strong's for Biblical terms (faster, focused)
    - Perseus for Classical Greek (comprehensive)
    """

    def __init__(self, data_dir: Optional[Path] = None):
        if data_dir is None:
            from shared.config import get_config
            config = get_config()
            data_dir = config.paths.lexicons

        self.data_dir = data_dir
        self._strongs_greek: Optional[List[Dict]] = None
        self._strongs_hebrew: Optional[List[Dict]] = None
        self._perseus_loaded = False
        self._perseus_path = data_dir / "perseus_lsj.xml"
        self._lsj_cex_path = data_dir / "lsj_index.txt"
        self._lsj_cex_index: Optional[Dict[str, Dict]] = None
        self._kaikki_path = data_dir / "kaikki.org-dictionary-AncientGreek-words.jsonl"
        self._kaikki_index: Optional[Dict[str, Dict]] = None
        self._kaikki_hebrew_path = data_dir / "kaikki.org-dictionary-Hebrew-words.jsonl"
        self._kaikki_hebrew_index: Optional[Dict[str, Dict]] = None
        self._kaikki_latin_path = data_dir / "kaikki.org-dictionary-Latin.jsonl"
        self._kaikki_latin_index: Optional[Dict[str, Dict]] = None
        self._kaikki_english_path = data_dir / "kaikki.org-dictionary-English.jsonl"
        self._kaikki_english_index: Optional[Dict[str, Dict]] = None
        self._kaikki_sanskrit_path = data_dir / "kaikki.org-dictionary-Sanskrit.jsonl"
        self._kaikki_sanskrit_index: Optional[Dict[str, Dict]] = None
        self._kaikki_aramaic_path = data_dir / "kaikki.org-dictionary-Aramaic.jsonl"
        self._kaikki_aramaic_index: Optional[Dict[str, Dict]] = None
        self._kaikki_pie_path = data_dir / "kaikki.org-dictionary-ProtoIndoEuropean.jsonl"
        self._kaikki_pie_index: Optional[Dict[str, Dict]] = None

        # Compact index/artifacts for faster UI loads (built by scripts/build_kaikki_indexes.py)
        self._kaikki_index_dir = data_dir / "indexes"
        self._kaikki_english_compact_data_path = self._kaikki_index_dir / "kaikki-english-mini.jsonl"
        self._kaikki_english_compact_index_path = self._kaikki_index_dir / "kaikki-english-index.json"
        self._kaikki_english_compact_index: Optional[Dict[str, int]] = None
        self._kaikki_english_compact_handle = None

        self._kaikki_latin_compact_data_path = self._kaikki_index_dir / "kaikki-latin-mini.jsonl"
        self._kaikki_latin_compact_index_path = self._kaikki_index_dir / "kaikki-latin-index.json"
        self._kaikki_latin_compact_index: Optional[Dict[str, int]] = None
        self._kaikki_latin_compact_handle = None

        self._kaikki_sanskrit_compact_data_path = self._kaikki_index_dir / "kaikki-sanskrit-mini.jsonl"
        self._kaikki_sanskrit_compact_index_path = self._kaikki_index_dir / "kaikki-sanskrit-index.json"
        self._kaikki_sanskrit_compact_index: Optional[Dict[str, int]] = None
        self._kaikki_sanskrit_compact_handle = None

        self._kaikki_aramaic_compact_data_path = self._kaikki_index_dir / "kaikki-aramaic-mini.jsonl"
        self._kaikki_aramaic_compact_index_path = self._kaikki_index_dir / "kaikki-aramaic-index.json"
        self._kaikki_aramaic_compact_index: Optional[Dict[str, int]] = None
        self._kaikki_aramaic_compact_handle = None

        self._kaikki_pie_compact_data_path = self._kaikki_index_dir / "kaikki-pie-mini.jsonl"
        self._kaikki_pie_compact_index_path = self._kaikki_index_dir / "kaikki-pie-index.json"
        self._kaikki_pie_compact_index: Optional[Dict[str, int]] = None
        self._kaikki_pie_compact_handle = None

    def lookup_greek(self, word: str, prefer_classical: bool = False) -> List[LexiconEntry]:
        """
        Look up a Greek word.

        Args:
            word: Greek word (Unicode or transliteration)
            prefer_classical: If True, query Perseus LSJ first (uses CEX index for beta code lookup)

        Returns:
            List of matching lexicon entries
        """
        results = []

        # Strategy: Query BOTH sources for comprehensive results
        # Order by preference, but include all available data
        
        if prefer_classical:
            # Classical priority: kaikki.org first, then Strong's
            results.extend(self._query_kaikki(word))
            results.extend(self._query_strongs_greek(word))
        else:
            # Biblical priority: Strong's first, then kaikki.org
            results.extend(self._query_strongs_greek(word))
            results.extend(self._query_kaikki(word))

        return results

    def lookup_hebrew(self, word: str) -> List[LexiconEntry]:
        """Look up a Hebrew word (uses Strong's and kaikki.org)."""
        results = []
        # Query both sources for comprehensive results
        results.extend(self._query_kaikki_hebrew(word))
        results.extend(self._query_strongs_hebrew(word))
        return results

    def lookup_latin(self, word: str) -> List[LexiconEntry]:
        """Look up a Latin word (kaikki.org)."""
        return self._query_kaikki_latin(word)

    def lookup_english(self, word: str) -> List[LexiconEntry]:
        """Look up an English word (kaikki.org)."""
        return self._query_kaikki_english(word)

    def lookup_sanskrit(self, word: str) -> List[LexiconEntry]:
        """Look up a Sanskrit word (kaikki.org)."""
        return self._query_kaikki_sanskrit(word)

    def lookup_aramaic(self, word: str) -> List[LexiconEntry]:
        """Look up an Aramaic word (kaikki.org)."""
        return self._query_kaikki_aramaic(word)

    def lookup_proto_indo_european(self, word: str) -> List[LexiconEntry]:
        """Look up a Proto-Indo-European root (kaikki.org)."""
        return self._query_kaikki_pie(word)

    def _load_strongs_greek(self):
        """Lazy-load Strong's Greek dictionary."""
        if self._strongs_greek is not None:
            return

        json_path = self.data_dir / "strongs_greek.json"

        if not json_path.exists():
            logger.warning(f"Strong's Greek not found at {json_path}")
            logger.warning("Run: python scripts/download_lexicons.py")
            self._strongs_greek = []
            return

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self._strongs_greek = json.load(f)
            logger.info(f"Loaded {len(self._strongs_greek)} Strong's Greek entries")
        except Exception as e:
            logger.error(f"Failed to load Strong's Greek: {e}")
            self._strongs_greek = []

    def _load_strongs_hebrew(self):
        """Lazy-load Strong's Hebrew dictionary."""
        if self._strongs_hebrew is not None:
            return

        json_path = self.data_dir / "strongs_hebrew.json"

        if not json_path.exists():
            logger.warning(f"Strong's Hebrew not found at {json_path}")
            logger.warning("Run: python scripts/download_lexicons.py")
            self._strongs_hebrew = []
            return

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self._strongs_hebrew = json.load(f)
            logger.info(f"Loaded {len(self._strongs_hebrew)} Strong's Hebrew entries")
        except Exception as e:
            logger.error(f"Failed to load Strong's Hebrew: {e}")
            self._strongs_hebrew = []

    def _load_kaikki(self):
        """Lazy-load kaikki.org Wiktionary JSONL into memory with fuzzy indexing."""
        if self._kaikki_index is not None:
            return

        if not self._kaikki_path.exists():
            logger.warning(f"Kaikki.org dictionary not found at {self._kaikki_path}")
            self._kaikki_index = {}
            return

        try:
            self._kaikki_index = {}
            entry_count = 0
            
            with open(self._kaikki_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line)
                        word = data.get('word', '')
                        if not word:
                            continue
                        
                        entry_count += 1
                        
                        # Index by exact Unicode
                        self._kaikki_index[word] = data
                        
                        # Also index lowercase
                        word_lower = word.lower()
                        if word_lower != word and word_lower not in self._kaikki_index:
                            self._kaikki_index[word_lower] = data
                        
                        # Index without accents for fuzzy matching
                        word_no_accents = remove_accents(word_lower)
                        if word_no_accents != word_lower and word_no_accents not in self._kaikki_index:
                            self._kaikki_index[word_no_accents] = data
                        
                        # Also index without hyphens (for compound words)
                        word_no_hyphen = word_no_accents.replace('-', '')
                        if word_no_hyphen != word_no_accents and word_no_hyphen not in self._kaikki_index:
                            self._kaikki_index[word_no_hyphen] = data
                        
                        # Phonetic normalization for vowel confusion (βετα → βῆτα)
                        word_phonetic = phonetic_normalize_greek(word_lower)
                        if word_phonetic != word_no_hyphen and word_phonetic not in self._kaikki_index:
                            self._kaikki_index[word_phonetic] = data
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON at line {line_num}: {e}")
                        continue
            
            logger.info(f"Loaded {entry_count} kaikki.org entries ({len(self._kaikki_index)} index keys)")
            
        except Exception as e:
            logger.error(f"Failed to load kaikki.org: {e}")
            self._kaikki_index = {}

    def _load_kaikki_hebrew(self):
        """Lazy-load kaikki.org Hebrew Wiktionary JSONL into memory with fuzzy indexing."""
        if self._kaikki_hebrew_index is not None:
            return

        if not self._kaikki_hebrew_path.exists():
            logger.warning(f"Kaikki.org Hebrew dictionary not found at {self._kaikki_hebrew_path}")
            self._kaikki_hebrew_index = {}
            return

        try:
            self._kaikki_hebrew_index = {}
            entry_count = 0
            
            with open(self._kaikki_hebrew_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line)
                        word = data.get('word', '')
                        if not word:
                            continue
                        
                        entry_count += 1
                        
                        # Index by exact Unicode
                        self._kaikki_hebrew_index[word] = data
                        
                        # Also index lowercase
                        word_lower = word.lower()
                        if word_lower != word and word_lower not in self._kaikki_hebrew_index:
                            self._kaikki_hebrew_index[word_lower] = data
                        
                        # Index without accents/vowel points for fuzzy matching
                        word_no_accents = remove_accents(word_lower)
                        if word_no_accents != word_lower and word_no_accents not in self._kaikki_hebrew_index:
                            self._kaikki_hebrew_index[word_no_accents] = data
                        
                        # Also index without hyphens (for compound words)
                        word_no_hyphen = word_no_accents.replace('-', '')
                        if word_no_hyphen != word_no_accents and word_no_hyphen not in self._kaikki_hebrew_index:
                            self._kaikki_hebrew_index[word_no_hyphen] = data
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON at line {line_num}: {e}")
                        continue
            
            logger.info(f"Loaded {entry_count} kaikki.org Hebrew entries ({len(self._kaikki_hebrew_index)} index keys)")
            
        except Exception as e:
            logger.error(f"Failed to load kaikki.org Hebrew: {e}")
            self._kaikki_hebrew_index = {}

    def _load_kaikki_generic(self, language_name: str, path_attr: str, index_attr: str):
        """Generic loader for kaikki.org dictionaries."""
        if getattr(self, index_attr) is not None:
            return

        path = getattr(self, path_attr)
        if not path.exists():
            logger.warning(f"Kaikki.org {language_name} dictionary not found at {path}")
            setattr(self, index_attr, {})
            return

        try:
            index = {}
            entry_count = 0
            
            with open(path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line)
                        word = data.get('word', '')
                        if not word:
                            continue
                        
                        entry_count += 1
                        
                        # Index by exact Unicode
                        index[word] = data
                        
                        # Also index lowercase
                        word_lower = word.lower()
                        if word_lower != word and word_lower not in index:
                            index[word_lower] = data
                        
                        # Index without accents for fuzzy matching
                        word_no_accents = remove_accents(word_lower)
                        if word_no_accents != word_lower and word_no_accents not in index:
                            index[word_no_accents] = data
                        
                        # Also index without hyphens (for compound words)
                        word_no_hyphen = word_no_accents.replace('-', '')
                        if word_no_hyphen != word_no_accents and word_no_hyphen not in index:
                            index[word_no_hyphen] = data
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"Invalid JSON at line {line_num}: {e}")
                        continue
            
            setattr(self, index_attr, index)
            logger.info(f"Loaded {entry_count} kaikki.org {language_name} entries ({len(index)} index keys)")
            
        except Exception as e:
            logger.error(f"Failed to load kaikki.org {language_name}: {e}")
            setattr(self, index_attr, {})

    def _load_compact_index(self, language_name: str, index_path_attr: str, index_attr: str):
        """Lazy-load compact index (key -> byte offset) for a language."""
        if getattr(self, index_attr) is not None:
            return

        index_path = getattr(self, index_path_attr)
        if not index_path.exists():
            logger.warning(f"Compact index for {language_name} not found at {index_path}")
            setattr(self, index_attr, {})
            return

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                setattr(self, index_attr, json.load(f))
        except Exception as e:
            logger.error(f"Failed to load compact index for {language_name}: {e}")
            setattr(self, index_attr, {})

    def _query_compact_kaikki(self, word: str, language_name: str, index_path_attr: str, index_attr: str,
                               data_path_attr: str, handle_attr: str) -> List[LexiconEntry]:
        """Query compact Kaikki mini file via index + byte seek."""
        self._load_compact_index(language_name, index_path_attr, index_attr)

        index = getattr(self, index_attr, {})
        if not index:
            return []

        data_path = getattr(self, data_path_attr)
        if not data_path.exists():
            return []

        # Open handle lazily
        handle = getattr(self, handle_attr)
        if handle is None:
            try:
                handle = open(data_path, 'r', encoding='utf-8')
                setattr(self, handle_attr, handle)
            except Exception as e:
                logger.error(f"Failed to open compact data file for {language_name}: {e}")
                return []

        word_lower = word.lower()
        word_no_accents = remove_accents(word_lower)
        word_no_hyphen = word_no_accents.replace('-', '')
        search_variants = [word, word_lower, word_no_accents, word_no_hyphen]

        # PIE/Wiktionary lemmas often omit leading asterisks; include starless variants.
        expanded_variants = []
        for variant in search_variants:
            expanded_variants.append(variant)
            stripped = variant.lstrip('*')
            if stripped != variant:
                expanded_variants.append(stripped)

        # Preserve order but drop duplicates
        seen = set()
        deduped_variants = []
        for v in expanded_variants:
            if v in seen:
                continue
            seen.add(v)
            deduped_variants.append(v)

        for variant in deduped_variants:
            offset = index.get(variant)
            if offset is None:
                continue
            try:
                handle.seek(offset)
                line = handle.readline()
                if not line:
                    continue
                data = json.loads(line)
                lemma = data.get('word', word)
                pos = data.get('pos', 'unknown')
                romanization = data.get('romanization', '')
                glosses = data.get('glosses', [])
                definition = '; '.join(glosses[:8]) if glosses else ''
                ety = data.get('etymology_text') or None
                morphology = f"Part of speech: {pos}" if pos != 'unknown' else None
                return [LexiconEntry(
                    word=lemma,
                    language=language_name,
                    transliteration=romanization,
                    definition=definition,
                    etymology=ety,
                    morphology=morphology,
                    source="Kaikki.org Wiktionary (compact)"
                )]
            except Exception as e:
                logger.error(f"Compact query failed for {language_name}: {e}")
                continue

        return []

    def _load_kaikki_latin(self):
        """Lazy-load kaikki.org Latin dictionary."""
        self._load_kaikki_generic("Latin", "_kaikki_latin_path", "_kaikki_latin_index")

    def _load_kaikki_english(self):
        """Lazy-load kaikki.org English dictionary."""
        self._load_kaikki_generic("English", "_kaikki_english_path", "_kaikki_english_index")

    def _load_kaikki_sanskrit(self):
        """Lazy-load kaikki.org Sanskrit dictionary."""
        self._load_kaikki_generic("Sanskrit", "_kaikki_sanskrit_path", "_kaikki_sanskrit_index")

    def _load_kaikki_aramaic(self):
        """Lazy-load kaikki.org Aramaic dictionary."""
        self._load_kaikki_generic("Aramaic", "_kaikki_aramaic_path", "_kaikki_aramaic_index")

    def _load_kaikki_pie(self):
        """Lazy-load kaikki.org Proto-Indo-European dictionary."""
        self._load_kaikki_generic("Proto-Indo-European", "_kaikki_pie_path", "_kaikki_pie_index")

    def _load_lsj_cex(self):
        """Lazy-load LSJ CEX index into memory."""
        if self._lsj_cex_index is not None:
            return

        if not self._lsj_cex_path.exists():
            logger.warning(f"LSJ CEX index not found at {self._lsj_cex_path}")
            logger.warning("Run: python scripts/download_lexicons.py")
            self._lsj_cex_index = {}
            return

        try:
            self._lsj_cex_index = {}
            with open(self._lsj_cex_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Parse CEX format: entry_id#lemma#beta_code#preview_text
                    parts = line.split('#', 3)
                    if len(parts) < 4:
                        continue
                    
                    entry_id = parts[0].strip()
                    lemma = parts[1].strip()
                    beta_code = parts[2].strip()
                    preview = parts[3].strip()
                    
                    # Store with Unicode lemma as primary key
                    # Also store variations for fuzzy matching
                    entry = {
                        'entry_id': entry_id,
                        'lemma': lemma,
                        'beta_code': beta_code,
                        'preview': preview,
                        'line_number': line_num
                    }
                    
                    # Primary key: exact Unicode lemma
                    if lemma and lemma not in self._lsj_cex_index:
                        self._lsj_cex_index[lemma] = entry
                    
                    # Also index lowercase version for case-insensitive lookup
                    if lemma:
                        lemma_lower = lemma.lower()
                        if lemma_lower != lemma and lemma_lower not in self._lsj_cex_index:
                            self._lsj_cex_index[lemma_lower] = entry
                        
                        # Also index accent-stripped version
                        lemma_no_accents = remove_accents(lemma_lower)
                        if lemma_no_accents and lemma_no_accents not in self._lsj_cex_index:
                            self._lsj_cex_index[lemma_no_accents] = entry
                        
                        # Also index without hyphens (for compound words like κατά-λυσις)
                        lemma_no_hyphen = lemma_no_accents.replace('-', '')
                        if lemma_no_hyphen != lemma_no_accents and lemma_no_hyphen not in self._lsj_cex_index:
                            self._lsj_cex_index[lemma_no_hyphen] = entry
            
            logger.info(f"Loaded LSJ CEX index: {len(self._lsj_cex_index)} entries")
        except Exception as e:
            logger.error(f"Failed to load LSJ CEX index: {e}")
            self._lsj_cex_index = {}

    def _query_lsj_cex(self, word: str) -> List[LexiconEntry]:
        """Query LSJ CEX index.
        
        Uses a tiered matching strategy:
        1. Exact Unicode match (preserves accents)
        2. Case-insensitive match
        3. Accent-insensitive match
        
        Args:
            word: Greek word to look up (Unicode)
            
        Returns:
            List of matching lexicon entries (typically 0 or 1)
        """
        self._load_lsj_cex()
        
        if not self._lsj_cex_index:
            return []
        
        word_normalized = word.strip()
        
        # Strategy 1: Exact match
        if word_normalized in self._lsj_cex_index:
            entry = self._lsj_cex_index[word_normalized]
            return [LexiconEntry(
                word=entry['lemma'],
                language="Ancient Greek",
                transliteration=entry['beta_code'],
                definition=entry['preview'],
                etymology=None,
                source="LSJ (CEX index)"
            )]
        
        # Strategy 2: Case-insensitive match
        word_lower = word_normalized.lower()
        if word_lower in self._lsj_cex_index:
            entry = self._lsj_cex_index[word_lower]
            return [LexiconEntry(
                word=entry['lemma'],
                language="Ancient Greek",
                transliteration=entry['beta_code'],
                definition=entry['preview'],
                etymology=None,
                source="LSJ (CEX index)"
            )]
        
        # Strategy 3: Accent-insensitive match
        word_no_accents = remove_accents(word_lower)
        if word_no_accents in self._lsj_cex_index:
            entry = self._lsj_cex_index[word_no_accents]
            return [LexiconEntry(
                word=entry['lemma'],
                language="Ancient Greek",
                transliteration=entry['beta_code'],
                definition=entry['preview'],
                etymology=None,
                source="LSJ (CEX index)"
            )]
        
        # No match found
        return []

    def _query_strongs_greek(self, word: str) -> List[LexiconEntry]:
        """Query Strong's Greek dictionary."""
        self._load_strongs_greek()

        if not self._strongs_greek:
            return []

        results = []
        word_normalized = word.strip()
        word_lower = word_normalized.lower()
        word_no_accents = remove_accents(word_lower)
        
        # Special case: Greek letter names to single letters
        # e.g., "αλφα" or "ἄλφα" should match Strong's "Α"
        letter_names = {
            'αλφα': 'Α', 'ἄλφα': 'Α', 'alpha': 'Α',
            'βητα': 'Β', 'βῆτα': 'Β', 'βετα': 'Β', 'beta': 'Β',
            'γαμμα': 'Γ', 'γάμμα': 'Γ', 'gamma': 'Γ',
            'δελτα': 'Δ', 'δέλτα': 'Δ', 'delta': 'Δ',
            'ωμεγα': 'Ω', 'ὠμέγα': 'Ω', 'omega': 'Ω'
        }
        
        # Check if user is searching for a letter name
        letter_to_search = letter_names.get(word_lower) or letter_names.get(word_no_accents)

        for entry in self._strongs_greek:
            # Match on Greek word or transliteration (case-insensitive, accent-insensitive)
            match = False

            entry_word = entry.get('word', '')
            entry_translit = entry.get('translit', '')
            
            # NEW: Check if searching for a letter name
            if letter_to_search and entry_word == letter_to_search:
                match = True

            # Try multiple matching strategies:
            # 1. Exact match
            if not match and entry_word and entry_word == word_normalized:
                match = True
            elif not match and entry_translit and entry_translit == word_normalized:
                match = True
            # 2. Case-insensitive match
            elif not match and entry_word and entry_word.lower() == word_lower:
                match = True
            elif not match and entry_translit and entry_translit.lower() == word_lower:
                match = True
            # 3. Accent-insensitive match (for transliterations)
            elif not match and entry_translit and remove_accents(entry_translit.lower()) == word_no_accents:
                match = True
            elif entry_word and remove_accents(entry_word.lower()) == word_no_accents:
                match = True

            if match:
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
        self._load_strongs_hebrew()

        if not self._strongs_hebrew:
            return []

        results = []
        word_normalized = word.strip()
        word_lower = word_normalized.lower()
        word_no_accents = remove_accents(word_lower)

        for entry in self._strongs_hebrew:
            # Match on Hebrew word or transliteration (with fuzzy matching)
            match = False

            entry_word = entry.get('word', '')
            entry_translit = entry.get('translit', '')
            
            # Try multiple matching strategies:
            # 1. Exact match
            if not match and entry_word and entry_word == word_normalized:
                match = True
            elif not match and entry_translit and entry_translit == word_normalized:
                match = True
            # 2. Case-insensitive match
            elif not match and entry_word and entry_word.lower() == word_lower:
                match = True
            elif not match and entry_translit and entry_translit.lower() == word_lower:
                match = True
            # 3. Accent-insensitive match (for vowel points)
            elif not match and entry_translit and remove_accents(entry_translit.lower()) == word_no_accents:
                match = True
            elif entry_word and remove_accents(entry_word.lower()) == word_no_accents:
                match = True

            if match:
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

    def _query_kaikki(self, word: str) -> List[LexiconEntry]:
        """Query kaikki.org Wiktionary for a Greek word."""
        self._load_kaikki()
        
        if not self._kaikki_index:
            return []
        
        # Try progressively fuzzier matches
        word_lower = word.lower()
        word_no_accents = remove_accents(word_lower)
        word_no_hyphen = word_no_accents.replace('-', '')
        word_phonetic = phonetic_normalize_greek(word_lower)
        
        search_variants = [
            word,
            word_lower,
            word_no_accents,
            word_no_hyphen,
            word_phonetic  # NEW: handles βετα → βῆτα
        ]
        
        entry_data = None
        for variant in search_variants:
            if variant in self._kaikki_index:
                entry_data = self._kaikki_index[variant]
                break
        
        if not entry_data:
            return []
        
        # Extract data
        lemma = entry_data.get('word', word)
        pos = entry_data.get('pos', 'unknown')
        
        # Get romanization from forms if available
        romanization = ""
        forms = entry_data.get('forms', [])
        for form in forms:
            if 'romanization' in form.get('tags', []):
                romanization = form.get('form', '')
                break
        if not romanization and forms:
            # Try to get from first form
            romanization = forms[0].get('romanization', '')
        
        # Extract glosses from senses
        glosses = []
        senses = entry_data.get('senses', [])
        for sense in senses[:10]:  # Limit to first 10 senses
            sense_glosses = sense.get('glosses', [])
            if sense_glosses:
                glosses.extend(sense_glosses)
        
        if not glosses:
            return []
        
        definition = '; '.join(glosses[:8])  # Limit to first 8 glosses
        
        # Get etymology if available
        etymology_text = entry_data.get('etymology_text', '')
        
        return [LexiconEntry(
            word=lemma,
            language="Ancient Greek",
            transliteration=romanization,
            definition=definition,
            etymology=etymology_text if etymology_text else None,
            morphology=f"Part of speech: {pos}" if pos != 'unknown' else None,
            source="Kaikki.org Wiktionary"
        )]

    def _query_kaikki_hebrew(self, word: str) -> List[LexiconEntry]:
        """Query kaikki.org Wiktionary for a Hebrew word."""
        self._load_kaikki_hebrew()
        
        if not self._kaikki_hebrew_index:
            return []
        
        # Try progressively fuzzier matches
        word_lower = word.lower()
        word_no_accents = remove_accents(word_lower)
        word_no_hyphen = word_no_accents.replace('-', '')
        
        search_variants = [
            word,
            word_lower,
            word_no_accents,
            word_no_hyphen
        ]
        
        entry_data = None
        for variant in search_variants:
            if variant in self._kaikki_hebrew_index:
                entry_data = self._kaikki_hebrew_index[variant]
                break
        
        if not entry_data:
            return []
        
        # Extract data
        lemma = entry_data.get('word', word)
        pos = entry_data.get('pos', 'unknown')
        
        # Get romanization from forms if available
        romanization = ""
        forms = entry_data.get('forms', [])
        for form in forms:
            if 'romanization' in form.get('tags', []):
                romanization = form.get('form', '')
                break
        if not romanization and forms:
            # Try to get from first form
            romanization = forms[0].get('romanization', '')
        
        # Extract glosses from senses
        glosses = []
        senses = entry_data.get('senses', [])
        for sense in senses[:10]:  # Limit to first 10 senses
            sense_glosses = sense.get('glosses', [])
            if sense_glosses:
                glosses.extend(sense_glosses)
        
        if not glosses:
            return []
        
        definition = '; '.join(glosses[:8])  # Limit to first 8 glosses
        
        # Get etymology if available
        etymology_text = entry_data.get('etymology_text', '')
        
        return [LexiconEntry(
            word=lemma,
            language="Hebrew",
            transliteration=romanization,
            definition=definition,
            etymology=etymology_text if etymology_text else None,
            morphology=f"Part of speech: {pos}" if pos != 'unknown' else None,
            source="Kaikki.org Wiktionary"
        )]

    def _query_kaikki_generic(self, word: str, language_name: str, index_attr: str) -> List[LexiconEntry]:
        """Generic query method for kaikki.org dictionaries."""
        # Load the index dynamically
        load_method_name = f"_load{index_attr.replace('_index', '')}"
        if hasattr(self, load_method_name):
            getattr(self, load_method_name)()
        
        index = getattr(self, index_attr, {})
        if not index:
            return []
        
        # Try progressively fuzzier matches
        word_lower = word.lower()
        word_no_accents = remove_accents(word_lower)
        word_no_hyphen = word_no_accents.replace('-', '')
        
        search_variants = [word, word_lower, word_no_accents, word_no_hyphen]
        
        entry_data = None
        for variant in search_variants:
            if variant in index:
                entry_data = index[variant]
                break
        
        if not entry_data:
            return []
        
        # Extract data
        lemma = entry_data.get('word', word)
        pos = entry_data.get('pos', 'unknown')
        
        # Get romanization from forms if available
        romanization = ""
        forms = entry_data.get('forms', [])
        for form in forms:
            if 'romanization' in form.get('tags', []):
                romanization = form.get('form', '')
                break
        if not romanization and forms:
            romanization = forms[0].get('romanization', '')
        
        # Extract glosses from senses
        glosses = []
        senses = entry_data.get('senses', [])
        for sense in senses[:10]:
            sense_glosses = sense.get('glosses', [])
            if sense_glosses:
                glosses.extend(sense_glosses)
        
        if not glosses:
            return []
        
        definition = '; '.join(glosses[:8])
        etymology_text = entry_data.get('etymology_text', '')
        
        return [LexiconEntry(
            word=lemma,
            language=language_name,
            transliteration=romanization,
            definition=definition,
            etymology=etymology_text if etymology_text else None,
            morphology=f"Part of speech: {pos}" if pos != 'unknown' else None,
            source="Kaikki.org Wiktionary"
        )]

    def _query_kaikki_latin(self, word: str) -> List[LexiconEntry]:
        """Query kaikki.org Wiktionary for a Latin word."""
        compact = self._query_compact_kaikki(
            word,
            "Latin",
            "_kaikki_latin_compact_index_path",
            "_kaikki_latin_compact_index",
            "_kaikki_latin_compact_data_path",
            "_kaikki_latin_compact_handle",
        )
        return compact

    def _query_kaikki_english(self, word: str) -> List[LexiconEntry]:
        """Query kaikki.org Wiktionary for an English word."""
        compact = self._query_compact_kaikki(
            word,
            "English",
            "_kaikki_english_compact_index_path",
            "_kaikki_english_compact_index",
            "_kaikki_english_compact_data_path",
            "_kaikki_english_compact_handle",
        )
        return compact

    def _query_kaikki_sanskrit(self, word: str) -> List[LexiconEntry]:
        """Query kaikki.org Wiktionary for a Sanskrit word."""
        compact = self._query_compact_kaikki(
            word,
            "Sanskrit",
            "_kaikki_sanskrit_compact_index_path",
            "_kaikki_sanskrit_compact_index",
            "_kaikki_sanskrit_compact_data_path",
            "_kaikki_sanskrit_compact_handle",
        )
        return compact

    def _query_kaikki_aramaic(self, word: str) -> List[LexiconEntry]:
        """Query kaikki.org Wiktionary for an Aramaic word."""
        compact = self._query_compact_kaikki(
            word,
            "Aramaic",
            "_kaikki_aramaic_compact_index_path",
            "_kaikki_aramaic_compact_index",
            "_kaikki_aramaic_compact_data_path",
            "_kaikki_aramaic_compact_handle",
        )
        return compact

    def _query_kaikki_pie(self, word: str) -> List[LexiconEntry]:
        """Query kaikki.org Wiktionary for a Proto-Indo-European root."""
        compact = self._query_compact_kaikki(
            word,
            "Proto-Indo-European",
            "_kaikki_pie_compact_index_path",
            "_kaikki_pie_compact_index",
            "_kaikki_pie_compact_data_path",
            "_kaikki_pie_compact_handle",
        )
        return compact

    def _query_perseus_via_cex(self, word: str) -> List[LexiconEntry]:
        """Query Perseus LSJ using CEX index to get entry ID.
        
        Strategy:
        1. Look up word in CEX index to get entry ID (e.g., "n4754")
        2. Use entry ID to find entry in Perseus XML
        3. If not in Perseus, return CEX preview as fallback
        """
        # First, get the entry ID from CEX index
        cex_entry = self._lookup_in_cex_index(word)
        if not cex_entry:
            return []
        
        entry_id = cex_entry.get('entry_id', '')
        if not entry_id:
            return []
        
        # Try Perseus XML first (for entries n0-n18949)
        perseus_results = self._query_perseus_by_id(entry_id, cex_entry.get('lemma', word))
        if perseus_results:
            return perseus_results
        
        # Perseus doesn't have it, so return CEX preview as fallback
        # (Perseus is abridged, only has ~19k entries; CEX has 116k+)
        lemma = cex_entry.get('lemma', word)
        beta_code = cex_entry.get('beta_code', '')
        preview = cex_entry.get('preview', '')
        
        # Format the preview text for better readability
        preview_formatted = ' '.join(preview.split())[:500]  # First 500 chars, cleaned
        
        return [LexiconEntry(
            word=lemma,
            language="Ancient Greek",
            transliteration=beta_code,
            definition=f"[CEX Preview] {preview_formatted}",
            etymology=None,
            source=f"LSJ CEX Index (entry {entry_id}, not in Perseus)"
        )]

    def _lookup_in_cex_index(self, word: str) -> Optional[Dict]:
        """Helper to look up word in CEX index and return entry dict."""
        self._load_lsj_cex()
        
        if not self._lsj_cex_index:
            return None
        
        word_normalized = word.strip()
        
        # Try exact match
        if word_normalized in self._lsj_cex_index:
            return self._lsj_cex_index[word_normalized]
        
        # Try case-insensitive
        word_lower = word_normalized.lower()
        if word_lower in self._lsj_cex_index:
            return self._lsj_cex_index[word_lower]
        
        # Try accent-insensitive
        word_no_accents = remove_accents(word_lower)
        if word_no_accents in self._lsj_cex_index:
            return self._lsj_cex_index[word_no_accents]
        
        return None

    def _extract_sense_definition(self, sense_elem) -> str:
        """Extract clean definition from a Perseus sense element.
        
        Strategy:
        1. Remove citation elements (bibl, author, title, biblScope, cit, quote)
        2. Keep descriptive text, translations (<tr>), and foreign language references
        3. Clean up whitespace
        """
        # Get all text nodes, but skip citation elements
        result_parts = []
        
        def extract_text_skip_citations(elem, skip_tags={'bibl', 'author', 'title', 'biblScope', 'cit', 'quote'}):
            """Recursively extract text, skipping citation tags."""
            # Check if this element should be skipped
            tag = elem.tag
            if '}' in tag:
                tag = tag.split('}', 1)[1]  # Remove namespace
            
            if tag in skip_tags:
                return ""
            
            # Get direct text
            text_parts = []
            if elem.text:
                text_parts.append(elem.text)
            
            # Process children
            for child in elem:
                text_parts.append(extract_text_skip_citations(child, skip_tags))
                if child.tail:
                    text_parts.append(child.tail)
            
            return ''.join(text_parts)
        
        text = extract_text_skip_citations(sense_elem)
        
        # Clean excessive whitespace
        text = ' '.join(text.split())
        
        # Remove common artifacts and unwanted patterns
        text = text.replace('v. A a init.;', '').replace('cf.', '').replace(',;', ';').strip()
        text = text.replace('al.', '').strip()  # "and others" abbreviation
        
        # Clean up punctuation issues
        text = text.replace('  ', ' ').replace(' ,', ',').replace(' ;', ';').replace(' .', '.')
        text = text.replace(',,', ',').replace(',.', '.').strip()
        
        # Remove artifacts like orphaned parentheses and commas
        if text.startswith('),'):
            text = text[2:].strip()
        if text.startswith(','):
            text = text[1:].strip()
        if text.endswith(','):
            text = text[:-1].strip()
        
        # Filter out very short or meaningless entries
        if len(text) < 3 or text in ['),', ',', ';', '.']:
            return ""
        
        # Filter out citation artifacts (e.g., "Calliasap.,;.")
        # These end with multiple punctuation marks
        if len(text) < 20 and text.endswith(('.;.', '.,;.', ',;.')):
            return ""
        
        return text

    def _query_perseus_by_id(self, entry_id: str, lemma: str) -> List[LexiconEntry]:
        """Query Perseus LSJ by entry ID for fast lookup."""
        if not self._perseus_path.exists():
            return []

        try:
            results = []
            
            # Parse incrementally to find the specific entry ID
            context = ET.iterparse(self._perseus_path, events=('start', 'end'))

            for event, elem in context:
                if event == 'end' and elem.tag.endswith('entryFree'):
                    # Check if this is our entry
                    elem_id = elem.get('id', '')
                    
                    if elem_id == entry_id:
                        # Found it! Extract definition
                        definition_parts = []

                        # Get all sense elements (definitions)
                        for sense in elem.findall('.//{http://www.tei-c.org/ns/1.0}sense'):
                            sense_def = self._extract_sense_definition(sense)
                            if sense_def:
                                definition_parts.append(sense_def)
                        
                        # Also try without namespace
                        if not definition_parts:
                            for sense in elem.findall('.//sense'):
                                sense_def = self._extract_sense_definition(sense)
                                if sense_def:
                                    definition_parts.append(sense_def)

                        if definition_parts:
                            results.append(LexiconEntry(
                                word=lemma,
                                language="Ancient Greek",
                                transliteration="",
                                definition="; ".join(definition_parts[:5]),  # First 5 senses
                                etymology=None,
                                source="Perseus LSJ"
                            ))
                        
                        # Clear element and stop searching
                        elem.clear()
                        break

                    # Clear processed elements to save memory
                    elem.clear()

            return results

        except Exception as e:
            logger.debug(f"Perseus query failed for entry_id '{entry_id}': {e}")
            return []

    def _query_perseus(self, word: str) -> List[LexiconEntry]:
        """Query Perseus Liddell-Scott lexicon (streaming XML parse)."""
        if not self._perseus_path.exists():
            return []

        try:
            # Stream parse XML to avoid loading 30MB into memory
            results = []
            word_lower = word.lower().strip()

            # Parse incrementally
            context = ET.iterparse(self._perseus_path, events=('start', 'end'))

            for event, elem in context:
                if event == 'end' and elem.tag.endswith('entry'):
                    # Extract entry data
                    key = elem.get('key', '')

                    if key.lower() == word_lower:
                        # Found match - extract definition
                        definition_parts = []

                        for sense in elem.findall('.//{*}sense'):
                            sense_text = ''.join(sense.itertext()).strip()
                            if sense_text:
                                definition_parts.append(sense_text)

                        if definition_parts:
                            results.append(LexiconEntry(
                                word=key,
                                language="Greek",
                                transliteration="",  # LSJ uses Greek script
                                definition="; ".join(definition_parts[:3]),  # First 3 senses
                                etymology=None,
                                source="Perseus LSJ"
                            ))

                    # Clear element to free memory
                    elem.clear()

                    # Stop after finding results (can adjust limit)
                    if len(results) >= 3:
                        break

            return results

        except Exception as e:
            logger.debug(f"Perseus query failed for '{word}': {e}")
            return []

    def format_for_display(self, entries: List[LexiconEntry]) -> str:
        """Format lexicon entries for HTML display."""
        if not entries:
            return ""

        html_parts = []

        for entry in entries:
            html_parts.append(f"<h3 style='color: #9333ea; margin-top: 15px;'>🏛️ {entry.source} Lexicon</h3>")

            # Word and transliteration
            if entry.transliteration:
                html_parts.append(f"""
                    <div style='background: #faf5ff; padding: 12px; margin: 8px 0; border-left: 4px solid #9333ea; border-radius: 4px;'>
                        <b style='font-size: 18px;'>{entry.word}</b>
                        <span style='color: #6b7280; margin-left: 10px;'>({entry.transliteration})</span>
                    </div>
                """)
            else:
                html_parts.append(f"""
                    <div style='background: #faf5ff; padding: 12px; margin: 8px 0; border-left: 4px solid #9333ea; border-radius: 4px;'>
                        <b style='font-size: 18px;'>{entry.word}</b>
                    </div>
                """)

            # Strong's number
            if entry.strong_number:
                html_parts.append(f"<p style='color: #6b7280; font-size: 12px; margin: 4px 0 8px 0;'>Strong's {entry.strong_number}</p>")

            # Definition
            if entry.definition:
                html_parts.append(f"""
                    <div style='background: #f9fafb; padding: 12px; margin: 8px 0; border-radius: 4px;'>
                        <b>Definition:</b><br>
                        {entry.definition}
                    </div>
                """)

            # Etymology/Derivation
            if entry.etymology:
                html_parts.append(f"""
                    <div style='background: #fef3c7; padding: 12px; margin: 8px 0; border-left: 4px solid #f59e0b; border-radius: 4px;'>
                        <b>Etymology:</b><br>
                        {entry.etymology}
                    </div>
                """)

        return "".join(html_parts)

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about loaded lexicons."""
        self._load_strongs_greek()
        self._load_strongs_hebrew()
        self._load_lsj_cex()

        return {
            'strongs_greek': len(self._strongs_greek) if self._strongs_greek else 0,
            'strongs_hebrew': len(self._strongs_hebrew) if self._strongs_hebrew else 0,
            'lsj_cex_entries': len(self._lsj_cex_index) if self._lsj_cex_index else 0,
            'perseus_available': self._perseus_path.exists()
        }