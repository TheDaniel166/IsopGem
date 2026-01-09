#!/usr/bin/env python3
"""Test script for multi-language gematria system.

This script verifies that language detection and cipher selection
are working correctly.
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from shared.services.gematria.greek_calculator import GreekGematriaCalculator
from shared.services.gematria.hebrew_calculator import HebrewGematriaCalculator
from shared.services.gematria.tq_calculator import TQGematriaCalculator
from shared.services.gematria.multi_language_calculator import MultiLanguageCalculator
from shared.services.gematria.language_detector import Language, LanguageDetector


def main():
    print("=" * 60)
    print("Multi-Language Gematria System Test")
    print("=" * 60)
    print()

    # Create calculators
    calculators = [
        TQGematriaCalculator(),
        GreekGematriaCalculator(),
        HebrewGematriaCalculator()
    ]

    print("Available Calculators:")
    for calc in calculators:
        print(f"  ✓ {calc.name}")
    print()

    # Create multi-lang calculator
    multi_calc = MultiLanguageCalculator(calculators)

    # Test cases
    test_cases = [
        ("Αγγελικος", Language.GREEK, "Greek word from screenshot"),
        ("Αραχνη", Language.GREEK, "Greek word - spider"),
        ("Κοσμου", Language.GREEK, "Greek word - cosmos"),
        ("שָׁלוֹם", Language.HEBREW, "Hebrew word - shalom"),
        ("λόγος", Language.GREEK, "Greek word - logos"),
        ("love", Language.ENGLISH, "English word"),
    ]

    print("Language Detection Tests:")
    print("-" * 60)
    for word, expected_lang, description in test_cases:
        detected_lang = LanguageDetector.detect_word_language(word)
        calc = multi_calc.get_calculator_for_word(word)
        value = multi_calc.calculate(word)

        status = "✓" if detected_lang == expected_lang else "✗"
        print(f"{status} {word:15} → {detected_lang.value:10} ({description})")
        if calc:
            print(f"   Value: {value:4} using {calc.name}")
        else:
            print(f"   ✗ ERROR: No calculator found!")
        print()

    # Mixed-language text test
    print("=" * 60)
    print("Mixed-Language Text Test")
    print("=" * 60)
    print()

    mixed_text = "The word λόγος means דָּבָר in Hebrew"
    print(f"Text: {mixed_text}")
    print()

    breakdown = multi_calc.get_word_breakdown(mixed_text)
    print("Word-by-Word Breakdown:")
    for word, value, lang, cipher in breakdown:
        print(f"  {word:15} = {value:4} ({lang:10}, {cipher})")

    print()
    total = multi_calc.calculate(mixed_text)
    print(f"Total Value: {total}")

    print()
    stats = multi_calc.get_language_stats(mixed_text)
    print("Language Statistics:")
    for lang, data in stats.items():
        print(f"  {lang:10}: {data['character_count']:3} chars "
              f"({data['percentage']:.1f}%) - {data['cipher']}")

    print()
    print("=" * 60)
    print("✓ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
