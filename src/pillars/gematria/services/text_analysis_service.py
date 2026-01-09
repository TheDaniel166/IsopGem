"""
Text Analysis Service - The Resonance Scanner.
Service for value matching, text statistics, and verse parsing in gematria analysis.
"""
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from shared.services.gematria.language_detector import LanguageDetector
from shared.services.gematria.multi_language_calculator import MultiLanguageCalculator

from ..services.base_calculator import GematriaCalculator
from ..utils.numeric_utils import sum_numeric_face_values

logger = logging.getLogger(__name__)

class TextAnalysisService:
    """Service for handling text analysis operations."""

    def find_value_matches(
        self, 
        text: str, 
        target_value: int, 
        calculator: GematriaCalculator, 
        include_face_values: bool = False,
        max_words: int = 8
    ) -> List[Tuple[str, int, int]]:
        """
        Find all text segments that match the target gematria value using Fast Scan.
        
        Args:
            text: The text to search
            target_value: The target gematria value
            calculator: The calculator strategy to use
            include_face_values: Whether to add numeric face values
            max_words: Maximum number of words in a phrase to check
            
        Returns:
            List of (match_text, start_pos, end_pos) tuples
        """
        matches = []
        
        # 1. Tokenize and Pre-calculate
        # Store tuples of (word_value, start_index, end_index)
        # We don't store the word text yet to save memory, we slice it later if needed?
        # Actually storing text is fine, strings are interned often.
        token_data = [] 
        
        current_word = ""
        start_pos = 0
        
        # O(N) pass to tokenize
        for i, char in enumerate(text):
            if char.isspace() or char in '.,;:!?()[]{}"\'–—-:':
                if current_word:
                    # Calculate value once
                    try:
                        val = calculator.calculate(current_word)
                        if include_face_values:
                            val += sum_numeric_face_values(current_word)
                        token_data.append((val, start_pos, i))
                    except (AttributeError, TypeError) as e:
                        logger.debug(
                            "TextAnalysisService: skipping token (%s): %s",
                            type(e).__name__,
                            e,
                        )
                    current_word = ""
            else:
                if not current_word:
                    start_pos = i
                current_word += char
        
        # Handle last word
        if current_word:
            try:
                val = calculator.calculate(current_word)
                if include_face_values:
                    val += sum_numeric_face_values(current_word)
                token_data.append((val, start_pos, len(text)))
            except (AttributeError, TypeError) as e:
                logger.debug(
                    "TextAnalysisService: skipping trailing token (%s): %s",
                    type(e).__name__,
                    e,
                )
                
        # 2. Integer Sliding Window
        n_tokens = len(token_data)
        if n_tokens == 0:
            return []

        # Optimization: Single word check
        for val, start, end in token_data:  # type: ignore[reportUnknownVariableType]
            if val == target_value:
                matches.append((text[start:end], start, end))

        # Optimization: Limit max_words to actual word count
        limit = min(max_words, n_tokens)
        
        # Sliding window for sizes 2 to limit
        # Optimized: Instead of re-summing for every window, we can just look ahead
        # OR use a running window sum? 
        # Running window sum is tricky because window size varies.
        # Simple nested loop with integer addition is fast enough for 9999 words locally
        # compared to string processing.
        
        for i in range(n_tokens):
            current_sum = token_data[i][0]
            
            # Start expanding window from i
            # j is the offset from i
            for j in range(1, limit):
                if i + j >= n_tokens:
                    break
                    
                next_val, _, end = token_data[i + j]  # type: ignore[reportUnknownVariableType]
                current_sum += next_val
                
                if current_sum == target_value:
                    start = token_data[i][1]
                    matches.append((text[start:end], start, end))
                
                # Heuristic: If we exceeded target and values are always positive, we can break?
                # Gematria implies positive values usually. 
                # Exception: Some ciphers might have negative/zero? 
                # Assuming standard positive gematria for optimization.
                if current_sum > target_value:
                    # Only safe if ensure all inputs are non-negative
                    # Safe to assume for most Gematria
                    break
                    
        return matches

    def calculate_text(self, text: str, calculator: GematriaCalculator, include_numbers: bool = False) -> int:
        """Calculate value for text helper."""
        val = calculator.calculate(text)
        if include_numbers:
            val += sum_numeric_face_values(text)

        return val

    def calculate_stats(
        self,
        text: str,
        calculator: GematriaCalculator,
        multi_language_calculator: Optional[MultiLanguageCalculator] = None,
    ) -> Dict[str, Any]:
        """
        Calculate statistics for the text.

        If a multi-language calculator is provided, compute per-language breakdowns and
        totals using the configured cipher for each detected language. Otherwise, use the
        supplied calculator for the entire text.
        """
        if not text:
            return {
                "word_count": 0,
                "char_count": 0,
                "total_value": 0,
                "avg_word_val": 0,
                "language_breakdown": [],
            }

        if multi_language_calculator:
            return self._calculate_multi_language_stats(text, multi_language_calculator)

        return self._calculate_single_language_stats(text, calculator)

    # --- Internal helpers -------------------------------------------------

    def _calculate_single_language_stats(
        self,
        text: str,
        calculator: GematriaCalculator,
    ) -> Dict[str, Any]:
        """Calculate aggregate stats using a single calculator."""
        words = re.findall(r"\w+", text, re.UNICODE)
        word_count = len(words)
        char_count = len(text)
        total_value = 0

        for word in words:
            try:
                total_value += calculator.calculate(word)
            except (AttributeError, TypeError) as exc:
                logger.debug(
                    "TextAnalysisService: skipping word in stats (%s): %s",
                    type(exc).__name__,
                    exc,
                )

        avg = total_value / word_count if word_count > 0 else 0

        return {
            "word_count": word_count,
            "char_count": char_count,
            "total_value": total_value,
            "avg_word_val": round(avg, 2),
            "language_breakdown": [],
        }

    def _calculate_multi_language_stats(
        self,
        text: str,
        multi_language_calculator: MultiLanguageCalculator,
    ) -> Dict[str, Any]:
        """Calculate stats with per-language breakdown using preferred ciphers."""
        words = re.findall(r"\w+", text, re.UNICODE)
        word_count = len(words)
        char_count = len(text)

        if word_count == 0:
            return {
                "word_count": 0,
                "char_count": char_count,
                "total_value": 0,
                "avg_word_val": 0,
                "language_breakdown": [],
            }

        per_language: Dict[str, Dict[str, Any]] = {}
        total_value = 0

        for word in words:
            language = LanguageDetector.detect_word_language(word)
            calculator = multi_language_calculator.get_calculator_for_language(language)
            cipher_name = calculator.name if calculator else "None"

            try:
                value = calculator.calculate(word) if calculator else 0
            except (AttributeError, TypeError) as exc:
                logger.debug(
                    "TextAnalysisService: skipping word in stats (%s): %s",
                    type(exc).__name__,
                    exc,
                )
                value = 0

            total_value += value

            bucket = per_language.setdefault(
                language.value,
                {"word_count": 0, "total_value": 0, "cipher": cipher_name},
            )
            bucket["word_count"] += 1
            bucket["total_value"] += value

            # Ensure cipher is recorded even if first word had no calculator
            if calculator and bucket.get("cipher") != cipher_name:
                bucket["cipher"] = cipher_name

        avg = total_value / word_count if word_count > 0 else 0

        breakdown = [
            {
                "language": lang,
                "word_count": data["word_count"],
                "total_value": data["total_value"],
                "cipher": data.get("cipher", "None"),
            }
            for lang, data in sorted(
                per_language.items(), key=lambda item: item[1]["word_count"], reverse=True
            )
        ]

        return {
            "word_count": word_count,
            "char_count": char_count,
            "total_value": total_value,
            "avg_word_val": round(avg, 2),
            "language_breakdown": breakdown,
        }

    def parse_verses(self, text: str, document_id: Optional[str] = None, allow_inline: bool = True) -> Dict[str, Any]:
        """
        Parse text into verses, using metadata if available.
        Returns a dictionary with 'verses', 'source', etc.
        """
        from ..utils.verse_parser import parse_verses
        from shared.services.document_manager.verse_teacher_service import verse_teacher_service_context
        import logging

        metadata = None
        if document_id:
            try:
                with verse_teacher_service_context() as service:
                    metadata = service.get_or_parse_verses(
                        document_id,
                        allow_inline=allow_inline,
                        apply_rules=True
                    )
            except Exception as e:
                logging.getLogger(__name__).warning(f"Verse teacher load failed: {e}")

        if metadata:
            return metadata
        
        # Fallback
        fallback = parse_verses(text, allow_inline=allow_inline)
        return {
            'verses': fallback,
            'source': 'local-parser'
        }
