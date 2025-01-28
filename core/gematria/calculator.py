import unicodedata

class GematriaCalculator:
    def __init__(self):
        self.tq_values = {
            'I': 0, 'L': 1, 'C': 2, 'H': 3, 'P': 4, 'A': 5,
            'X': 6, 'J': 7, 'W': 8, 'T': 9, 'O': 10, 'G': 11,
            'F': 12, 'E': 13, 'R': 14, 'S': 15, 'Q': 16, 'K': 17,
            'Y': 18, 'Z': 19, 'B': 20, 'M': 21, 'V': 22, 'D': 23,
            'N': 24, 'U': 25
        }
        
        self.hebrew_standard = {
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
            'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
            'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400,
            'ך': 20, 'ם': 40, 'ן': 50, 'ף': 80, 'ץ': 90  # Finals with standard values
        }
        
        self.hebrew_gadol = {
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
            'י': 10, 'כ': 20, 'ל': 30, 'מ': 40, 'נ': 50, 'ס': 60, 'ע': 70, 'פ': 80, 'צ': 90,
            'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400,
            'ך': 500, 'ם': 600, 'ן': 700, 'ף': 800, 'ץ': 900  # Finals with mispar gadol values
        }
        
        self.greek_values = {
            'α': 1, 'β': 2, 'γ': 3, 'δ': 4, 'ε': 5, 'ϝ': 6, 'ζ': 7, 'η': 8, 'θ': 9,
            'ι': 10, 'κ': 20, 'λ': 30, 'μ': 40, 'ν': 50, 'ξ': 60, 'ο': 70, 'π': 80,
            'ϙ': 90, 'ρ': 100, 'σ': 200, 'τ': 300, 'υ': 400, 'φ': 500, 'χ': 600,
            'ψ': 700, 'ω': 800, 'ϡ': 900,
            'Α': 1, 'Β': 2, 'Γ': 3, 'Δ': 4, 'Ε': 5, 'Ϝ': 6, 'Ζ': 7, 'Η': 8, 'Θ': 9,
            'Ι': 10, 'Κ': 20, 'Λ': 30, 'Μ': 40, 'Ν': 50, 'Ξ': 60, 'Ο': 70, 'Π': 80,
            'Ϙ': 90, 'Ρ': 100, 'Σ': 200, 'Τ': 300, 'Υ': 400, 'Φ': 500, 'Χ': 600,
            'Ψ': 700, 'Ω': 800, 'Ϡ': 900
        }

    def strip_marks(self, text):
        return ''.join(c for c in unicodedata.normalize('NFKD', text)
                      if not unicodedata.combining(c))
        
    def calculate_tq(self, text):
        return sum(self.tq_values.get(char.upper(), 0) for char in text)

    def calculate_hebrew_standard(self, text):
        clean_text = self.strip_marks(text)
        return sum(self.hebrew_standard.get(char, 0) for char in clean_text)

    def calculate_hebrew_gadol(self, text):
        clean_text = self.strip_marks(text)
        return sum(self.hebrew_gadol.get(char, 0) for char in clean_text)

    def calculate_greek(self, text):
        clean_text = self.strip_marks(text)
        total = 0
        for char in clean_text:
            if char == 'ς':  # Handle final sigma
                total += self.greek_values.get('σ', 0)
            else:
                total += self.greek_values.get(char, 0)
        return total

    def calculate(self, text, cipher_type):
        calculators = {
            'TQ English': self.calculate_tq,
            'Hebrew Standard': self.calculate_hebrew_standard,
            'Hebrew Gadol': self.calculate_hebrew_gadol,
            'Greek': self.calculate_greek
        }
        return calculators[cipher_type](text)

# TODO: Add more cipher systems:
# TODO: Add Latin/Roman numeral system
# TODO: Add Arabic Abjad system
# TODO: Add Sanskrit numerology
# TODO: Add Chinese numerology
# TODO: Add Coptic system
# TODO: Add custom cipher creation capability

# TODO: Add variant Hebrew methods:
# TODO: Add Mispar Katan (reduced value)
# TODO: Add Mispar Kolel (plus 1 for the word)
# TODO: Add AtBash cipher
# TODO: Add AlBam cipher
# TODO: Add Mispar Siduri (ordinal value)
# TODO: Add Mispar Bone'eh (building value)

# TODO: Add variant Greek methods:
# TODO: Add Isopsephy variants
# TODO: Add Modern Greek values

# TODO: Add input validation:
# TODO: Add character validation for each cipher system
# TODO: Add warning system for invalid characters
# TODO: Add support for mixed script detection
# TODO: Add validation for custom cipher definitions

# TODO: Add advanced calculation features:
# TODO: Add word root analysis
# TODO: Add phrase relationship detection
# TODO: Add numerical pattern detection
# TODO: Add mathematical relationships between words
# TODO: Add support for calculations across different cipher systems
# TODO: Add support for compound calculations

# TODO: Add analysis tools:
# TODO: Add statistical analysis of results
# TODO: Add frequency analysis
# TODO: Add pattern matching algorithms
# TODO: Add common value detection

# TODO: Add performance improvements:
# TODO: Add caching mechanism for frequent calculations
# TODO: Add batch processing capabilities
# TODO: Add parallel processing for large texts
# TODO: Optimize character normalization
# TODO: Add memory efficient processing for large texts

# TODO: Add documentation features:
# TODO: Add historical context for each cipher
# TODO: Add calculation method documentation
# TODO: Add usage examples
# TODO: Add cipher system metadata
# TODO: Add version tracking for cipher systems
