"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: Domain Logic (GRANDFATHERED - should move to pillars/lexicon)
- USED BY: Internal shared/ modules only (2 references)
- CRITERION: Violation (Single-pillar domain logic)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""
Thin wrapper service for unified lexicon lookups.

This service provides a simplified interface for the etymology_service
to perform lookups without duplicating the routing logic. It returns
raw LexiconEntry objects from the underlying services (comprehensive + classical).
"""

import logging
from typing import List, Optional, Set

from .comprehensive_lexicon_service import ComprehensiveLexiconService, LexiconEntry
from .classical_lexicon_service import ClassicalLexiconService

logger = logging.getLogger(__name__)


class LexiconResolver:
    """
    Thin wrapper providing unified access to all lexicon sources.

    This service doesn't duplicate logic - it just provides a clean
    interface for looking up words across all available lexicons.
    The etymology_service handles formatting and presentation.
    """

    def __init__(self):
        self.comprehensive = ComprehensiveLexiconService()
        self.classical = ClassicalLexiconService()

    def lookup_hebrew(self, word: str) -> List[LexiconEntry]:
        """
        Lookup Hebrew word across all sources.
        Returns entries from comprehensive lexicon + Strong's.
        """
        # Classical service already combines comprehensive + Strong's
        return self.classical.lookup_hebrew(word)

    def lookup_greek(self, word: str, prefer_classical: bool = True) -> List[LexiconEntry]:
        """
        Lookup Greek word across all sources.
        Returns entries from comprehensive lexicon + Strong's.
        """
        # Classical service already combines comprehensive + Strong's + Perseus
        return self.classical.lookup_greek(word, prefer_classical=prefer_classical)

    def lookup_by_language(self, word: str, language: str) -> List[LexiconEntry]:
        """
        Generic language lookup using the comprehensive lexicon.
        Supports: Latin, English, Sanskrit, Aramaic, Proto-Indo-European, etc.
        """
        return self.comprehensive.lookup(word, language)

    def lookup_latin(self, word: str) -> List[LexiconEntry]:
        """Lookup Latin word."""
        return self.classical.lookup_latin(word)

    def lookup_english(self, word: str) -> List[LexiconEntry]:
        """Lookup English word."""
        return self.classical.lookup_english(word)

    def lookup_sanskrit(self, word: str) -> List[LexiconEntry]:
        """Lookup Sanskrit word."""
        return self.classical.lookup_sanskrit(word)

    def lookup_aramaic(self, word: str) -> List[LexiconEntry]:
        """Lookup Aramaic word."""
        return self.classical.lookup_aramaic(word)

    def lookup_proto_indo_european(self, word: str) -> List[LexiconEntry]:
        """Lookup Proto-Indo-European word."""
        return self.classical.lookup_proto_indo_european(word)

    def lookup(self, word: str, preferred_languages: Optional[List[str]] = None) -> List[LexiconEntry]:
        """
        Auto-detect language and perform lookup across all relevant sources.

        This method is used by enrichment_service for unified lookups.
        It detects the script (Hebrew, Greek, Latin) and queries appropriate sources.

        Args:
            word: The word to look up
            preferred_languages: Optional list of language names to prioritize

        Returns:
            List of LexiconEntry objects from all relevant sources
        """
        results: List[LexiconEntry] = []

        # Detect script
        scripts = self._detect_scripts(word)

        # Hebrew words
        if "hebrew" in scripts:
            results.extend(self.lookup_hebrew(word))

        # Greek words
        if "greek" in scripts:
            results.extend(self.lookup_greek(word))

        # Latin/English words (or if no script detected)
        if "latin" in scripts or not scripts:
            # Try preferred languages first
            if preferred_languages:
                for lang in preferred_languages:
                    entries = self.comprehensive.lookup(word, lang)
                    results.extend(entries)

            # If no results yet, try common languages
            if not results:
                for lang in ["English", "Latin"]:
                    entries = self.comprehensive.lookup(word, lang)
                    results.extend(entries)
                    if entries:  # Stop after first hit
                        break

        return results

    @staticmethod
    def _detect_scripts(word: str) -> Set[str]:
        """
        Detect which scripts are present in the word.

        Returns:
            Set of script names: "hebrew", "greek", "latin"
        """
        scripts: Set[str] = set()

        for ch in word:
            code = ord(ch)
            # Hebrew Unicode range
            if 0x0590 <= code <= 0x05FF:
                scripts.add("hebrew")
            # Greek Unicode ranges
            elif (0x0370 <= code <= 0x03FF) or (0x1F00 <= code <= 0x1FFF):
                scripts.add("greek")

        # Default to latin if no specific script detected
        if not scripts:
            scripts.add("latin")

        return scripts