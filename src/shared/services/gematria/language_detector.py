"""Language detection service for gematria calculations.

Detects the primary language of text based on Unicode character ranges.
Supports Hebrew, Greek, English, and other languages for appropriate cipher selection.
"""
from typing import Dict, Optional, Counter
from enum import Enum


class Language(Enum):
    """Supported languages for gematria calculation."""
    HEBREW = "Hebrew"
    GREEK = "Greek"
    ENGLISH = "English"
    LATIN = "Latin"
    ARABIC = "Arabic"
    UNKNOWN = "Unknown"


class LanguageDetector:
    """Detects the language of text for gematria cipher selection."""

    # Unicode ranges for language detection
    UNICODE_RANGES = {
        Language.HEBREW: [
            (0x0590, 0x05FF),  # Hebrew block
            (0xFB1D, 0xFB4F),  # Hebrew Presentation Forms
        ],
        Language.GREEK: [
            (0x0370, 0x03FF),  # Greek and Coptic
            (0x1F00, 0x1FFF),  # Greek Extended
        ],
        Language.ARABIC: [
            (0x0600, 0x06FF),  # Arabic
            (0x0750, 0x077F),  # Arabic Supplement
            (0x08A0, 0x08FF),  # Arabic Extended-A
        ],
        Language.LATIN: [
            (0x0100, 0x017F),  # Latin Extended-A
            (0x0180, 0x024F),  # Latin Extended-B
        ],
    }

    @classmethod
    def detect_character_language(cls, char: str) -> Language:
        """
        Detect the language of a single character.

        Args:
            char: Single character to detect

        Returns:
            Language enum value
        """
        if not char:
            return Language.UNKNOWN

        code_point = ord(char)

        # Check Unicode ranges
        for language, ranges in cls.UNICODE_RANGES.items():
            for start, end in ranges:
                if start <= code_point <= end:
                    return language

        # ASCII letters default to English
        if 'A' <= char <= 'Z' or 'a' <= char <= 'z':
            return Language.ENGLISH

        return Language.UNKNOWN

    @classmethod
    def detect_word_language(cls, word: str) -> Language:
        """
        Detect the primary language of a word.

        Uses majority voting - the language with the most characters wins.

        Args:
            word: Word to analyze

        Returns:
            Language enum value
        """
        if not word:
            return Language.UNKNOWN

        # Count characters by language
        lang_counts: Counter[Language] = Counter()

        for char in word:
            if char.isspace() or not char.isalpha():
                continue
            lang = cls.detect_character_language(char)
            if lang != Language.UNKNOWN:
                lang_counts[lang] += 1

        if not lang_counts:
            return Language.ENGLISH  # Default for empty/numeric strings

        # Return most common language
        return lang_counts.most_common(1)[0][0]

    @classmethod
    def detect_text_language(cls, text: str, min_chars: int = 3) -> Language:
        """
        Detect the primary language of a text passage.

        Uses character frequency analysis to determine dominant language.
        Requires at least min_chars alphabetic characters.

        Args:
            text: Text to analyze
            min_chars: Minimum alphabetic characters required

        Returns:
            Language enum value
        """
        if not text or len(text.strip()) < min_chars:
            return Language.ENGLISH  # Default

        # Count characters by language
        lang_counts: Counter[Language] = Counter()

        for char in text:
            if not char.isalpha():
                continue
            lang = cls.detect_character_language(char)
            if lang != Language.UNKNOWN:
                lang_counts[lang] += 1

        if not lang_counts:
            return Language.ENGLISH  # Default for empty/numeric strings

        # Return most common language
        return lang_counts.most_common(1)[0][0]

    @classmethod
    def get_language_stats(cls, text: str) -> Dict[Language, int]:
        """
        Get character count statistics for each language in text.

        Args:
            text: Text to analyze

        Returns:
            Dictionary mapping Language to character count
        """
        lang_counts: Counter[Language] = Counter()

        for char in text:
            if not char.isalpha():
                continue
            lang = cls.detect_character_language(char)
            if lang != Language.UNKNOWN:
                lang_counts[lang] += 1

        return dict(lang_counts)

    @classmethod
    def is_mixed_language(cls, text: str, threshold: float = 0.1) -> bool:
        """
        Check if text contains mixed languages.

        Args:
            text: Text to analyze
            threshold: Minimum ratio for secondary language (default 10%)

        Returns:
            True if text has significant secondary language presence
        """
        stats = cls.get_language_stats(text)

        if len(stats) < 2:
            return False

        total_chars = sum(stats.values())
        if total_chars == 0:
            return False

        # Sort by count
        sorted_langs = sorted(stats.items(), key=lambda x: x[1], reverse=True)

        # Check if second language meets threshold
        if len(sorted_langs) >= 2:
            secondary_ratio = sorted_langs[1][1] / total_chars
            return secondary_ratio >= threshold

        return False


# Convenience functions for quick detection
def detect_language(text: str) -> Language:
    """Detect primary language of text (convenience function)."""
    return LanguageDetector.detect_text_language(text)


def detect_word_language(word: str) -> Language:
    """Detect language of a single word (convenience function)."""
    return LanguageDetector.detect_word_language(word)


def is_hebrew(text: str) -> bool:
    """Check if text is primarily Hebrew."""
    return LanguageDetector.detect_text_language(text) == Language.HEBREW


def is_greek(text: str) -> bool:
    """Check if text is primarily Greek."""
    return LanguageDetector.detect_text_language(text) == Language.GREEK


def is_english(text: str) -> bool:
    """Check if text is primarily English."""
    return LanguageDetector.detect_text_language(text) == Language.ENGLISH
