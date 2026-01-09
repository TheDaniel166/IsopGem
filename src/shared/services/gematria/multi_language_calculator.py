"""Multi-language gematria calculator service.

Automatically selects the appropriate cipher based on detected language
and user preferences. Handles mixed-language documents correctly.
"""
from typing import Dict, List, Tuple, Optional
from .base_calculator import GematriaCalculator
from .language_detector import Language, LanguageDetector
from .cipher_preferences import CipherPreferences, get_cipher_preferences


class MultiLanguageCalculator:
    """
    Calculator that automatically selects appropriate cipher based on language.

    This service:
    1. Detects the language of input text
    2. Looks up user's preferred cipher for that language
    3. Delegates calculation to the appropriate calculator
    4. Handles mixed-language documents by calculating per-word
    """

    def __init__(self, calculators: List[GematriaCalculator], preferences: Optional[CipherPreferences] = None):
        """
        Initialize multi-language calculator.

        Args:
            calculators: List of available calculator instances
            preferences: Optional cipher preferences (uses global if None)
        """
        # Build calculator lookup by name
        self.calculators: Dict[str, GematriaCalculator] = {
            calc.name: calc for calc in calculators
        }

        # Get preferences
        self.preferences = preferences or get_cipher_preferences()

        # Build language-to-calculator cache
        self._lang_calc_cache: Dict[Language, Optional[GematriaCalculator]] = {}
        self._update_calculator_cache()

    def _update_calculator_cache(self):
        """Update the language-to-calculator cache based on preferences."""
        self._lang_calc_cache.clear()

        for language in Language:
            cipher_name = self.preferences.get_cipher(language)
            calculator = self.calculators.get(cipher_name)
            self._lang_calc_cache[language] = calculator

    def get_calculator_for_language(self, language: Language) -> Optional[GematriaCalculator]:
        """
        Get the preferred calculator for a specific language.

        Args:
            language: Language enum

        Returns:
            Calculator instance or None if not available
        """
        return self._lang_calc_cache.get(language)

    def get_calculator_for_text(self, text: str) -> Optional[GematriaCalculator]:
        """
        Get the appropriate calculator for a text passage.

        Detects language and returns matching calculator.

        Args:
            text: Text to analyze

        Returns:
            Calculator instance or None
        """
        language = LanguageDetector.detect_text_language(text)
        return self.get_calculator_for_language(language)

    def get_calculator_for_word(self, word: str) -> Optional[GematriaCalculator]:
        """
        Get the appropriate calculator for a single word.

        Args:
            word: Word to analyze

        Returns:
            Calculator instance or None
        """
        language = LanguageDetector.detect_word_language(word)
        return self.get_calculator_for_language(language)

    def calculate(self, text: str) -> int:
        """
        Calculate gematria value using language-appropriate cipher.

        For single-language text, uses the appropriate cipher.
        For mixed-language text, calculates per-word and sums.

        Args:
            text: Text to calculate

        Returns:
            Total gematria value
        """
        # Check if mixed language
        if LanguageDetector.is_mixed_language(text):
            return self.calculate_mixed_language(text)

        # Single language - use appropriate calculator
        calculator = self.get_calculator_for_text(text)
        if calculator:
            return calculator.calculate(text)

        # Fallback to 0 if no calculator available
        return 0

    def calculate_mixed_language(self, text: str) -> int:
        """
        Calculate gematria value for mixed-language text.

        Splits into words, detects language per word, and sums.

        Args:
            text: Text containing multiple languages

        Returns:
            Total gematria value
        """
        import re

        # Extract words (Unicode-aware)
        words = re.findall(r'\w+', text, re.UNICODE)

        total = 0
        for word in words:
            calc = self.get_calculator_for_word(word)
            if calc:
                total += calc.calculate(word)

        return total

    def get_breakdown(self, text: str) -> List[Tuple[str, int, str]]:
        """
        Get breakdown with language information.

        Returns list of (character, value, language_name) tuples.

        Args:
            text: Text to analyze

        Returns:
            List of (char, value, language) tuples
        """
        breakdown = []
        for char in text:
            if not char.isalpha():
                continue

            lang = LanguageDetector.detect_character_language(char)
            calc = self.get_calculator_for_language(lang)

            if calc:
                value = calc.get_letter_value(char)
                if value > 0:
                    breakdown.append((char, value, lang.value))

        return breakdown

    def get_word_breakdown(self, text: str) -> List[Tuple[str, int, str, str]]:
        """
        Get word-level breakdown for mixed-language documents.

        Returns list of (word, value, language, cipher_name) tuples.

        Args:
            text: Text to analyze

        Returns:
            List of (word, value, language, cipher) tuples
        """
        import re

        words = re.findall(r'\w+', text, re.UNICODE)
        breakdown = []

        for word in words:
            lang = LanguageDetector.detect_word_language(word)
            calc = self.get_calculator_for_language(lang)

            if calc:
                value = calc.calculate(word)
                breakdown.append((word, value, lang.value, calc.name))
            else:
                breakdown.append((word, 0, lang.value, "None"))

        return breakdown

    def set_preference(self, language: Language, cipher_name: str):
        """
        Update cipher preference for a language.

        Args:
            language: Language to configure
            cipher_name: Name of cipher to use
        """
        if cipher_name not in self.calculators:
            raise ValueError(f"Calculator '{cipher_name}' not available")

        self.preferences.set_cipher(language, cipher_name)
        self._update_calculator_cache()

    def get_language_stats(self, text: str) -> Dict[str, Dict[str, any]]:
        """
        Get statistics about languages in text.

        Returns breakdown of character counts and values per language.

        Args:
            text: Text to analyze

        Returns:
            Dict with language statistics
        """
        stats = LanguageDetector.get_language_stats(text)

        result = {}
        for lang, char_count in stats.items():
            calc = self.get_calculator_for_language(lang)
            result[lang.value] = {
                'character_count': char_count,
                'cipher': calc.name if calc else 'None',
                'percentage': 0.0  # Will be calculated below
            }

        # Calculate percentages
        total_chars = sum(stats.values())
        if total_chars > 0:
            for lang_name in result:
                result[lang_name]['percentage'] = (
                    result[lang_name]['character_count'] / total_chars * 100
                )

        return result


def create_multi_language_calculator(calculators: List[GematriaCalculator]) -> MultiLanguageCalculator:
    """
    Create a multi-language calculator instance.

    Convenience function for creating calculator with global preferences.

    Args:
        calculators: List of available calculators

    Returns:
        MultiLanguageCalculator instance
    """
    return MultiLanguageCalculator(calculators)
