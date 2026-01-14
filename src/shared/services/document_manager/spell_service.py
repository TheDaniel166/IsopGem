"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: GRANDFATHERED - Unclear if infrastructure or pillar
- USED BY: Document_manager (2 references)
- CRITERION: 2 (if global) OR Violation (if pillar-specific)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""
Spell Check Service for Document Manager Pillar.
Provides spell checking functionality using PyEnchant (Hunspell wrapper).
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Optional, Set

logger = logging.getLogger(__name__)

# Try to import enchant
try:
    import enchant
    from enchant.checker import SpellChecker
    ENCHANT_AVAILABLE = True
except ImportError:
    ENCHANT_AVAILABLE = False
    logger.warning("pyenchant not installed. Spell checking disabled.")


class SpellService:
    """
    Service for spell checking words.
    
    Features:
    - Check if word is spelled correctly
    - Get spelling suggestions
    - Custom user dictionary (persistent)
    - Session ignore list
    """
    
    def __init__(self, language: str = "en_US"):
        """
          init   logic.
        
        Args:
            language: Description of language.
        
        """
        self._language = language
        self._dict: Optional[enchant.Dict] = None
        self._custom_words: Set[str] = set()
        self._session_ignore: Set[str] = set()
        self._enabled = ENCHANT_AVAILABLE
        
        # Custom dictionary path
        self._custom_dict_path = self._get_custom_dict_path()
        
        if self._enabled:
            self._initialize()
    
    def _get_custom_dict_path(self) -> Path:
        """Get path to custom dictionary file."""
        # Use ~/.isopgem directory
        home = Path.home()
        isopgem_dir = home / ".isopgem"
        isopgem_dir.mkdir(exist_ok=True)
        return isopgem_dir / "custom_dictionary.txt"
    
    def _initialize(self):
        """Initialize the spell checker."""
        try:
            # Check if language is available
            if enchant.dict_exists(self._language):
                self._dict = enchant.Dict(self._language)
                logger.info(f"Spell checker initialized with language: {self._language}")
            else:
                # Fallback to any available English
                available = enchant.list_languages()
                english_langs = [l for l in available if l.startswith("en")]
                if english_langs:
                    self._language = english_langs[0]
                    self._dict = enchant.Dict(self._language)
                    logger.info(f"Fallback to language: {self._language}")
                else:
                    logger.warning("No English dictionary available.")
                    self._enabled = False
                    return
            
            # Load custom dictionary
            self._load_custom_dictionary()
            
        except Exception as e:
            logger.error(f"Failed to initialize spell checker: {e}")
            self._enabled = False
    
    def _load_custom_dictionary(self):
        """Load custom words from file."""
        if self._custom_dict_path.exists():
            try:
                with open(self._custom_dict_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        word = line.strip()
                        if word:
                            self._custom_words.add(word.lower())
                logger.info(f"Loaded {len(self._custom_words)} custom words.")
            except Exception as e:
                logger.error(f"Failed to load custom dictionary: {e}")
    
    def _save_custom_dictionary(self):
        """Save custom words to file."""
        try:
            with open(self._custom_dict_path, 'w', encoding='utf-8') as f:
                for word in sorted(self._custom_words):
                    f.write(word + '\n')
        except Exception as e:
            logger.error(f"Failed to save custom dictionary: {e}")
    
    @property
    def is_enabled(self) -> bool:
        """Check if spell checking is available and enabled."""
        return self._enabled and self._dict is not None
    
    def check(self, word: str) -> bool:
        """
        Check if a word is spelled correctly.
        
        Returns True if:
        - Word is in dictionary
        - Word is in custom dictionary
        - Word is in session ignore list
        """
        if not self.is_enabled:
            return True  # Don't mark anything if disabled
        
        word_lower = word.lower()
        
        # Check session ignore list
        if word_lower in self._session_ignore:
            return True
        
        # Check custom dictionary
        if word_lower in self._custom_words:
            return True
        
        # Check main dictionary
        try:
            return self._dict.check(word)
        except Exception:
            return True  # Fail safe
    
    def suggest(self, word: str, max_suggestions: int = 5) -> List[str]:
        """Get spelling suggestions for a word."""
        if not self.is_enabled:
            return []
        
        try:
            suggestions = self._dict.suggest(word)
            return suggestions[:max_suggestions]
        except Exception:
            return []
    
    def add_to_dictionary(self, word: str):
        """Add a word to the custom dictionary (persistent)."""
        word_lower = word.lower()
        self._custom_words.add(word_lower)
        self._save_custom_dictionary()
        logger.info(f"Added '{word}' to custom dictionary.")
    
    def ignore(self, word: str):
        """Ignore a word for this session only."""
        self._session_ignore.add(word.lower())
    
    def ignore_all(self, word: str):
        """Ignore all occurrences of a word for this session."""
        self._session_ignore.add(word.lower())
    
    def clear_session_ignores(self):
        """Clear the session ignore list."""
        self._session_ignore.clear()
    
    def get_misspelled_words(self, text: str) -> List[tuple]:
        """
        Get all misspelled words in text with their positions.
        
        Returns list of (word, start_pos, end_pos) tuples.
        """
        if not self.is_enabled:
            return []
        
        misspelled = []
        # Match words (letters only, handles Unicode)
        word_pattern = re.compile(r'\b[a-zA-Z]+\b')
        
        for match in word_pattern.finditer(text):
            word = match.group()
            if len(word) > 1 and not self.check(word):
                misspelled.append((word, match.start(), match.end()))
        
        return misspelled
    
    def get_available_languages(self) -> List[str]:
        """Get list of available dictionary languages."""
        if not ENCHANT_AVAILABLE:
            return []
        try:
            return enchant.list_languages()
        except Exception:
            return []
    
    def set_language(self, language: str) -> bool:
        """Change the spell check language."""
        try:
            if enchant.dict_exists(language):
                self._dict = enchant.Dict(language)
                self._language = language
                logger.info(f"Spell check language changed to: {language}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to set language: {e}")
            return False


# Singleton instance
_spell_service: Optional[SpellService] = None


def get_spell_service() -> SpellService:
    """Get or create the singleton SpellService instance."""
    global _spell_service
    if _spell_service is None:
        _spell_service = SpellService()
    return _spell_service