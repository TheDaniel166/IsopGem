"""Document language scanner for pre-analysis before loading documents.

Scans document text to detect which languages are present and their prevalence.
Used to prompt user for cipher selection when opening a document (clicking "Open Scroll").
All subsequent views (document text, interlinear, search, frequency analysis) use the selected ciphers.
"""
from typing import Dict, List, Set
from collections import Counter
from .language_detector import Language, LanguageDetector


class LanguageScanResult:
    """Result of scanning a document for languages."""

    def __init__(self, text: str):
        """Initialize scan result.

        Args:
            text: The document text that was scanned
        """
        self.text = text
        self.languages_detected: Set[Language] = set()
        self.language_stats: Dict[Language, int] = {}
        self.total_chars = 0
        self.word_count = 0

    def has_language(self, language: Language) -> bool:
        """Check if a specific language was detected."""
        return language in self.languages_detected

    def has_non_english(self) -> bool:
        """Check if any non-English languages were detected."""
        return any(lang != Language.ENGLISH and lang != Language.UNKNOWN
                   for lang in self.languages_detected)

    def get_percentage(self, language: Language) -> float:
        """Get percentage of text that is in the specified language."""
        if self.total_chars == 0:
            return 0.0
        char_count = self.language_stats.get(language, 0)
        return (char_count / self.total_chars) * 100

    def get_non_english_languages(self) -> List[Language]:
        """Get list of detected non-English languages, sorted by prevalence."""
        non_english = [
            lang for lang in self.languages_detected
            if lang not in (Language.ENGLISH, Language.UNKNOWN)
        ]
        # Sort by character count (most prevalent first)
        return sorted(non_english, key=lambda l: self.language_stats.get(l, 0), reverse=True)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'languages_detected': [lang.value for lang in self.languages_detected],
            'language_stats': {lang.value: count for lang, count in self.language_stats.items()},
            'total_chars': self.total_chars,
            'word_count': self.word_count,
            'percentages': {lang.value: self.get_percentage(lang) for lang in self.languages_detected}
        }


class DocumentLanguageScanner:
    """Scans document text to detect languages present."""

    @staticmethod
    def scan(text: str, min_threshold: float = 1.0) -> LanguageScanResult:
        """
        Scan document text and detect languages present.

        Args:
            text: Document text to scan
            min_threshold: Minimum percentage for a language to be considered present (default 1%)

        Returns:
            LanguageScanResult with detected languages and statistics
        """
        result = LanguageScanResult(text)

        # Get language statistics from LanguageDetector
        stats = LanguageDetector.get_language_stats(text)
        result.language_stats = stats
        result.total_chars = sum(stats.values())

        # Count words (rough estimate)
        import re
        words = re.findall(r'\w+', text, re.UNICODE)
        result.word_count = len(words)

        # Determine which languages meet threshold
        for language, char_count in stats.items():
            if result.total_chars > 0:
                percentage = (char_count / result.total_chars) * 100
                if percentage >= min_threshold:
                    result.languages_detected.add(language)

        return result

    @staticmethod
    def get_supported_languages() -> List[Language]:
        """Get list of languages we can calculate gematria for."""
        return [
            Language.HEBREW,
            Language.GREEK,
            Language.ENGLISH,
            # Language.ARABIC,  # Uncomment when Arabic calculator available
            # Language.LATIN,   # Uses English calculator
        ]

    @staticmethod
    def needs_cipher_selection(scan_result: LanguageScanResult) -> bool:
        """
        Check if user needs to select ciphers (has non-English languages).

        Args:
            scan_result: Result of document scan

        Returns:
            True if cipher selection dialog should be shown
        """
        return scan_result.has_non_english()

    @staticmethod
    def get_languages_for_selection(scan_result: LanguageScanResult) -> List[tuple[Language, float]]:
        """
        Get languages that need cipher selection with their percentages.

        Args:
            scan_result: Result of document scan

        Returns:
            List of (Language, percentage) tuples for non-English languages
        """
        languages = scan_result.get_non_english_languages()
        return [(lang, scan_result.get_percentage(lang)) for lang in languages]


def scan_document(text: str) -> LanguageScanResult:
    """Convenience function to scan document text."""
    return DocumentLanguageScanner.scan(text)
