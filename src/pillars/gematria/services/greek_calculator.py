"""Greek isopsephy calculator implementation."""
from typing import Dict
from .base_calculator import GematriaCalculator


class GreekGematriaCalculator(GematriaCalculator):
    """Calculator for Greek isopsephy (standard values).
    
    Also known as Isopsephy (ἰσοψηφία) - "equal counting"
    
    Greek isopsephy is the equivalent of Hebrew gematria, assigning numerical
    values to letters of the Greek alphabet:
    - Alpha through Theta: 1-9 (units)
    - Iota through Koppa: 10-90 (tens)
    - Rho through Sampi: 100-900 (hundreds)
    
    Includes three archaic letters used only for numbers:
    - Digamma (Ϝ ϝ): 6 (archaic 'w' sound)
    - Koppa (Ϙ ϙ): 90 (archaic 'q' sound)
    - Sampi (ϡ): 900 (archaic 's' sound)
    
    Historical Context:
    Isopsephy was practiced in ancient Greece, appearing in the works of
    philosophers, mathematicians, and mystics. It was used extensively in
    the Greco-Roman world for numerology, divination, and finding hidden
    meanings in texts. Early Christians used isopsephy to analyze New
    Testament Greek texts.
    
    Applications:
    - New Testament textual analysis
    - Ancient Greek philosophy and mysticism
    - Finding numerical relationships in classical texts
    - Gnostic and early Christian numerology
    
    Example:
    Ἰησοῦς (Iēsous, "Jesus"):
    Ι(10) + η(8) + σ(200) + ο(70) + ῦ(400) + ς(200) = 888
    
    Λόγος (Logos, "Word"):
    Λ(30) + ό(70) + γ(3) + ο(70) + ς(200) = 373
    
    The number 888 for "Jesus" is particularly significant in Christian
    numerology, contrasting with 666 (the "number of the beast").
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Greek (Isopsephy)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Greek letter-to-value mapping.
        
        Uses standard Greek isopsephy values:
        - Alpha through Theta: 1-9
        - Iota through Koppa: 10-90
        - Rho through Sampi: 100-900
        - Includes archaic letters (Digamma, Koppa, Sampi) used for numbers
        
        Returns:
            Dictionary mapping Greek letters to their isopsephy values
        """
        return {
            # Alpha through Theta (1-9)
            'Α': 1,   'α': 1,   # Alpha
            'Β': 2,   'β': 2,   # Beta
            'Γ': 3,   'γ': 3,   # Gamma
            'Δ': 4,   'δ': 4,   # Delta
            'Ε': 5,   'ε': 5,   # Epsilon
            'Ϝ': 6,   'ϝ': 6,   # Digamma (archaic)
            'Ζ': 7,   'ζ': 7,   # Zeta
            'Η': 8,   'η': 8,   # Eta
            'Θ': 9,   'θ': 9,   # Theta
            
            # Iota through Koppa (10-90)
            'Ι': 10,  'ι': 10,  # Iota
            'Κ': 20,  'κ': 20,  # Kappa
            'Λ': 30,  'λ': 30,  # Lambda
            'Μ': 40,  'μ': 40,  # Mu
            'Ν': 50,  'ν': 50,  # Nu
            'Ξ': 60,  'ξ': 60,  # Xi
            'Ο': 70,  'ο': 70,  # Omicron
            'Π': 80,  'π': 80,  # Pi
            'Ϙ': 90,  'ϙ': 90,  # Koppa (archaic)
            
            # Rho through Sampi (100-900)
            'Ρ': 100, 'ρ': 100, # Rho
            'Σ': 200, 'σ': 200, 'ς': 200, # Sigma (including final form)
            'Τ': 300, 'τ': 300, # Tau
            'Υ': 400, 'υ': 400, # Upsilon
            'Φ': 500, 'φ': 500, # Phi
            'Χ': 600, 'χ': 600, # Chi
            'Ψ': 700, 'ψ': 700, # Psi
            'Ω': 800, 'ω': 800, # Omega
            'ϡ': 900,           # Sampi (archaic, typically lowercase only)
        }


class GreekLetterValueCalculator(GematriaCalculator):
    """Calculator for Greek letter value (full spelling method).
    
    Also known as Arithmos Pleres (Αριθμός Πλήρης) - "Full Number"
    
    This method calculates the isopsephy value of each letter's spelled-out
    name in Greek:
    - Alpha (α) is spelled ἄλφα = α(1) + λ(30) + φ(500) + α(1) = 532
    - Beta (β) is spelled βῆτα = β(2) + η(8) + τ(300) + α(1) = 311
    
    Historical Context:
    This advanced technique appears in Pythagorean and neo-Platonic texts,
    where the "name" of a letter was considered to contain its essential
    spiritual nature. Gnostic texts used this method to reveal hidden
    cosmological meanings.
    
    Applications:
    - Gnostic textual analysis
    - Neo-Platonic philosophy
    - Deep numerological study of Greek texts
    - Understanding the spiritual essence of individual letters
    
    Example:
    The letter α (Alpha):
    Name: ἄλφα
    Value: α(1) + λ(30) + φ(500) + α(1) = 532
    
    The word αβ ("ab"):
    α (532) + β (311) = 843
    
    This reveals enormous numerical significance even in simple letter
    combinations when the full essence of each letter is considered.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Greek (Letter Value)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Greek letter-to-letter-value mapping.
        
        Uses the value of spelled-out letter names:
        - Alpha (Α α) = 532 (ἄλφα = α(1) + λ(30) + φ(500) + α(1))
        - Beta (Β β) = 311 (βῆτα = β(2) + η(8) + τ(300) + α(1))
        - etc.
        
        Returns:
            Dictionary mapping Greek letters to their letter values
        """
        return {
            # Letter values based on spelled-out names
            'Α': 532,  'α': 532,  # Alpha (ἄλφα)
            'Β': 311,  'β': 311,  # Beta (βῆτα)
            'Γ': 85,   'γ': 85,   # Gamma (γάμμα)
            'Δ': 340,  'δ': 340,  # Delta (δέλτα)
            'Ε': 865,  'ε': 865,  # Epsilon (ἔψιλον)
            'Ζ': 316,  'ζ': 316,  # Zeta (ζῆτα)
            'Η': 309,  'η': 309,  # Eta (ἦτα)
            'Θ': 318,  'θ': 318,  # Theta (θῆτα)
            'Ι': 1111, 'ι': 1111, # Iota (ἰῶτα)
            'Κ': 182,  'κ': 182,  # Kappa (κάππα)
            'Λ': 78,   'λ': 78,   # Lambda (λάμβδα)
            'Μ': 440,  'μ': 440,  # Mu (μῦ)
            'Ν': 450,  'ν': 450,  # Nu (νῦ)
            'Ξ': 70,   'ξ': 70,   # Xi (ξῖ)
            'Ο': 360,  'ο': 360,  # Omicron (ὂμικρον)
            'Π': 90,   'π': 90,   # Pi (πῖ)
            'Ρ': 900,  'ρ': 900,  # Rho (ῥῶ)
            'Σ': 254,  'σ': 254, 'ς': 254,  # Sigma (σίγμα)
            'Τ': 701,  'τ': 701,  # Tau (ταῦ)
            'Υ': 1260, 'υ': 1260, # Upsilon (ὔψιλον)
            'Φ': 510,  'φ': 510,  # Phi (φῖ)
            'Χ': 610,  'χ': 610,  # Chi (χῖ)
            'Ψ': 710,  'ψ': 710,  # Psi (ψῖ)
            'Ω': 849,  'ω': 849,  # Omega (ὦμέγα)
        }


class GreekOrdinalCalculator(GematriaCalculator):
    """Calculator for Greek Ordinal Value (Arithmos Taktikos / Αριθμός Τακτικός).
    
    Also known as Arithmos Taktikos (Αριθμός Τακτικός) - "Ordinal Number"
    
    This method assigns each letter a value based on its position in the
    extended Greek alphabet (1-27), including archaic letters:
    - Alpha = 1 (first letter)
    - Beta = 2 (second letter)
    - ...
    - Omega = 26 (twenty-sixth letter)
    - Sampi = 27 (twenty-seventh letter)
    
    Historical Context:
    Ordinal values provide a simplified alternative to standard isopsephy,
    useful in modern Greek numerology and when seeking patterns based on
    alphabetical structure rather than traditional numerical values.
    
    Applications:
    - Simplified Greek numerology
    - Finding ordinal patterns in text
    - Modern New Age applications
    - Structural analysis of Greek words
    
    Example:
    Λόγος ("Logos"):
    Standard: 373
    Ordinal: Λ(12) + ό(16) + γ(3) + ο(16) + ς(20) = 67
    
    Θεός ("Theos", "God"):
    Standard: Θ(9) + ε(5) + ό(70) + ς(200) = 284
    Ordinal: Θ(9) + ε(5) + ο(16) + ς(20) = 50
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Greek (Ordinal)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Greek letter-to-ordinal-value mapping.
        
        Uses the position of each letter in the extended alphabet (1-27):
        - Alpha = 1, Beta = 2, ..., Sampi = 27
        - Includes archaic letters (Digamma, Koppa, Sampi)
        
        Returns:
            Dictionary mapping Greek letters to their ordinal values
        """
        return {
            'Α': 1,   'α': 1,   # Alpha
            'Β': 2,   'β': 2,   # Beta
            'Γ': 3,   'γ': 3,   # Gamma
            'Δ': 4,   'δ': 4,   # Delta
            'Ε': 5,   'ε': 5,   # Epsilon
            'Ϝ': 6,   'ϝ': 6,   # Digamma (archaic)
            'Ζ': 7,   'ζ': 7,   # Zeta
            'Η': 8,   'η': 8,   # Eta
            'Θ': 9,   'θ': 9,   # Theta
            'Ι': 10,  'ι': 10,  # Iota
            'Κ': 11,  'κ': 11,  # Kappa
            'Λ': 12,  'λ': 12,  # Lambda
            'Μ': 13,  'μ': 13,  # Mu
            'Ν': 14,  'ν': 14,  # Nu
            'Ξ': 15,  'ξ': 15,  # Xi
            'Ο': 16,  'ο': 16,  # Omicron
            'Π': 17,  'π': 17,  # Pi
            'Ϙ': 18,  'ϙ': 18,  # Koppa (archaic)
            'Ρ': 19,  'ρ': 19,  # Rho
            'Σ': 20,  'σ': 20, 'ς': 20,  # Sigma (including final form)
            'Τ': 21,  'τ': 21,  # Tau
            'Υ': 22,  'υ': 22,  # Upsilon
            'Φ': 23,  'φ': 23,  # Phi
            'Χ': 24,  'χ': 24,  # Chi
            'Ψ': 25,  'ψ': 25,  # Psi
            'Ω': 26,  'ω': 26,  # Omega
            'ϡ': 27,            # Sampi (archaic)
        }


class GreekSmallValueCalculator(GematriaCalculator):
    """Calculator for Greek Small Value (Arithmos Mikros / Αριθμός Μικρός).
    
    Also known as Arithmos Mikros (Αριθμός Μικρός) - "Small Number"
    
    This reduction method simplifies isopsephy values by removing zeros:
    - Units (1-9) remain unchanged: α(1), β(2), ..., θ(9)
    - Tens (10-90) become: ι(1), κ(2), λ(3), ..., ϙ(9)
    - Hundreds (100-900) become: ρ(1), σ(2), τ(3), ..., ϡ(9)
    
    Historical Context:
    Small values appear in practical Greek numerology for quick calculations
    and are used in modern applications to find the essential numerical
    signature of words without large number complexity.
    
    Applications:
    - Quick numerological calculations
    - Finding core numerical essence
    - Modern Greek numerology
    - Pattern recognition in texts
    
    Example:
    Λόγος ("Logos"):
    Standard: Λ(30) + ό(70) + γ(3) + ο(70) + ς(200) = 373
    Small: Λ(3) + ό(7) + γ(3) + ο(7) + ς(2) = 22
    Further reduced: 2 + 2 = 4
    
    Θεός ("God"):
    Standard: 284
    Small: Θ(9) + ε(5) + ό(7) + ς(2) = 23
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Greek (Small Value)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Greek letter-to-small-value mapping.
        
        Reduces standard values to single digits by removing zeros:
        - Alpha through Theta: 1-9 (unchanged)
        - Iota through Koppa: 10-90 → 1-9
        - Rho through Sampi: 100-900 → 1-9
        
        Returns:
            Dictionary mapping Greek letters to their small values
        """
        return {
            # Alpha through Theta (1-9)
            'Α': 1,   'α': 1,   # Alpha
            'Β': 2,   'β': 2,   # Beta
            'Γ': 3,   'γ': 3,   # Gamma
            'Δ': 4,   'δ': 4,   # Delta
            'Ε': 5,   'ε': 5,   # Epsilon
            'Ϝ': 6,   'ϝ': 6,   # Digamma (6 → 6)
            'Ζ': 7,   'ζ': 7,   # Zeta
            'Η': 8,   'η': 8,   # Eta
            'Θ': 9,   'θ': 9,   # Theta
            
            # Iota through Koppa (10-90 → 1-9)
            'Ι': 1,   'ι': 1,   # Iota (10 → 1)
            'Κ': 2,   'κ': 2,   # Kappa (20 → 2)
            'Λ': 3,   'λ': 3,   # Lambda (30 → 3)
            'Μ': 4,   'μ': 4,   # Mu (40 → 4)
            'Ν': 5,   'ν': 5,   # Nu (50 → 5)
            'Ξ': 6,   'ξ': 6,   # Xi (60 → 6)
            'Ο': 7,   'ο': 7,   # Omicron (70 → 7)
            'Π': 8,   'π': 8,   # Pi (80 → 8)
            'Ϙ': 9,   'ϙ': 9,   # Koppa (90 → 9)
            
            # Rho through Sampi (100-900 → 1-9)
            'Ρ': 1,   'ρ': 1,   # Rho (100 → 1)
            'Σ': 2,   'σ': 2, 'ς': 2,  # Sigma (200 → 2)
            'Τ': 3,   'τ': 3,   # Tau (300 → 3)
            'Υ': 4,   'υ': 4,   # Upsilon (400 → 4)
            'Φ': 5,   'φ': 5,   # Phi (500 → 5)
            'Χ': 6,   'χ': 6,   # Chi (600 → 6)
            'Ψ': 7,   'ψ': 7,   # Psi (700 → 7)
            'Ω': 8,   'ω': 8,   # Omega (800 → 8)
            'ϡ': 9,             # Sampi (900 → 9)
        }


class GreekKolelCalculator(GematriaCalculator):
    """Calculator for Greek Kolel (Κολλέλ) - adds number of letters."""
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Greek (Kolel)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use standard Greek isopsephy values."""
        return GreekGematriaCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate isopsephy value + number of letters (Kolel).
        
        Args:
            text: The Greek text to calculate
            
        Returns:
            Sum of letter values plus the count of letters
        """
        normalized = self.normalize_text(text)
        base_value = super().calculate(normalized)
        letter_count = len(normalized)
        return base_value + letter_count


class GreekSquareCalculator(GematriaCalculator):
    """Calculator for Greek Square Value (Arithmos Tetragonos / Αριθμός Τετράγωνος).
    
    Also known as Arithmos Tetragonos (Αριθμός Τετράγωνος) - "Square Number"
    
    This mathematical method squares each letter's isopsephy value before
    summing, exponentially amplifying numerical significance.
    
    Formula: Σ(letter_value²)
    
    Historical Context:
    Square values appear in Pythagorean and neo-Platonic numerology,
    representing the "tetrad" or four-fold nature of reality. The squaring
    operation symbolizes manifestation on the material plane.
    
    Applications:
    - Pythagorean numerology
    - Neo-Platonic philosophy
    - Advanced isopsephy calculations
    - Finding amplified numerical patterns
    
    Example:
    αβ ("ab"):
    Standard: α(1) + β(2) = 3
    Square: α(1²=1) + β(2²=4) = 5
    
    Θεός ("God"):
    Standard: Θ(9) + ε(5) + ό(70) + ς(200) = 284
    Square: Θ(81) + ε(25) + ό(4900) + ς(40000) = 45,006
    
    The dramatic increase reflects the infinite power and transcendence
    of the divine concept.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Greek (Square)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use standard Greek isopsephy values."""
        return GreekGematriaCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate sum of squared letter values.
        
        Args:
            text: The Greek text to calculate
            
        Returns:
            Sum of (letter_value)²
        """
        normalized = self.normalize_text(text)
        total = 0
        
        for char in normalized:
            if char in self._letter_values:
                value = self._letter_values[char]
                total += value ** 2
        
        return total


class GreekCubeCalculator(GematriaCalculator):
    """Calculator for Greek Cube Value (Κυβική Αξία)."""
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Greek (Cube)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use standard Greek isopsephy values."""
        return GreekGematriaCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate sum of cubed letter values.
        
        Args:
            text: The Greek text to calculate
            
        Returns:
            Sum of (letter_value)³
        """
        normalized = self.normalize_text(text)
        total = 0
        
        for char in normalized:
            if char in self._letter_values:
                value = self._letter_values[char]
                total += value ** 3
        
        return total


class GreekTriangularCalculator(GematriaCalculator):
    """Calculator for Greek Triangular Value (Arithmos Trigonikos / Αριθμός Τριγωνικός).
    
    Also known as Arithmos Trigonikos (Αριθμός Τριγωνικός) - "Triangular Number"
    
    This method uses triangular numbers - the sum of all integers from 1 to n.
    For a letter with value n: T(n) = n(n+1)/2
    
    Triangular numbers were sacred to Pythagoras and represent the progressive
    accumulation of unity into multiplicity - the building blocks of reality.
    
    Formula: Σ(T(letter_value)) where T(n) = n(n+1)/2
    
    Historical Context:
    Triangular numbers appear throughout Pythagorean mathematics and philosophy
    as fundamental building blocks. They represent the tetraktys (sacred triangle
    of 10 dots) and the progressive manifestation of the Monad into creation.
    
    Applications:
    - Pythagorean mathematics
    - Finding cumulative spiritual significance
    - Neo-Platonic emanation theory
    - Advanced numerological analysis
    
    Example:
    αβ ("ab"):
    Standard: 3
    Triangular: T(1) + T(2) = 1 + 3 = 4
    
    Θεός ("God"):
    Standard: 284
    Triangular: T(9)=45 + T(5)=15 + T(70)=2485 + T(200)=20100 = 22,645
    
    The triangular value represents the cumulative manifestation of the
    Divine through all levels of reality.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Greek (Triangular)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use standard Greek isopsephy values."""
        return GreekGematriaCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate sum of triangular numbers for each letter.
        
        Triangular number formula: T(n) = n(n+1)/2
        
        Args:
            text: The Greek text to calculate
            
        Returns:
            Sum of T(letter_value)
        """
        normalized = self.normalize_text(text)
        total = 0
        
        for char in normalized:
            if char in self._letter_values:
                n = self._letter_values[char]
                triangular = n * (n + 1) // 2
                total += triangular
        
        return total


class GreekDigitalCalculator(GematriaCalculator):
    """Calculator for Greek Digital Value (Arithmos Psephiakos / Αριθμός Ψηφιακός).
    
    Also known as Arithmos Psephiakos (Αριθμός Ψηφιακός) - "Digital Number"
    
    This reduction method sums the individual digits of each letter's value:
    - Λ (30) becomes 3+0 = 3
    - ό (70) becomes 7+0 = 7
    - σ (200) becomes 2+0+0 = 2
    
    Formula: Σ(sum of digits of each letter value)
    
    Historical Context:
    Digital reduction is used in modern Greek numerology to find the
    "digital root" of words. While not ancient, it follows principles
    similar to Pythagorean digit summation.
    
    Applications:
    - Modern Greek numerology
    - Finding digital root connections
    - Simplified isopsephy calculations
    - Pattern recognition in texts
    
    Example:
    Λόγος ("Logos"):
    Standard: Λ(30) + ό(70) + γ(3) + ο(70) + ς(200) = 373
    Digital: 3 + 7 + 3 + 7 + 2 = 22
    Further reduced: 2 + 2 = 4
    
    Θεός ("God"):
    Standard: 284
    Digital: 9 + 5 + 7 + 2 = 23
    Further reduced: 2 + 3 = 5
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Greek (Digital)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use standard Greek isopsephy values."""
        return GreekGematriaCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate sum of digit sums for each letter value.
        
        Example: Λ(30) → 3+0 = 3
        
        Args:
            text: The Greek text to calculate
            
        Returns:
            Sum of digit sums for all letters
        """
        normalized = self.normalize_text(text)
        total = 0
        
        for char in normalized:
            if char in self._letter_values:
                value = self._letter_values[char]
                # Sum the digits of this value
                digit_sum = sum(int(digit) for digit in str(value))
                total += digit_sum
        
        return total


class GreekOrdinalSquareCalculator(GematriaCalculator):
    """Calculator for Greek Ordinal Square Value (Arithmos Taktikos Tetragonos / Αριθμός Τακτικός Τετράγωνος)."""
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Greek (Ordinal Square)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use ordinal values (letter positions 1-27)."""
        return GreekOrdinalCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate sum of squared ordinal values.
        
        Args:
            text: The Greek text to calculate
            
        Returns:
            Sum of (ordinal_position)²
        """
        normalized = self.normalize_text(text)
        total = 0
        
        for char in normalized:
            if char in self._letter_values:
                ordinal = self._letter_values[char]
                total += ordinal ** 2
        
        return total


class GreekFullValueCalculator(GematriaCalculator):
    """Calculator for Greek Full Value (Arithmos Pleres / Αριθμός Πλήρης)."""
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Greek (Full Value)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Map letters to their full spelling values.
        
        Example: α = ἄλφα = α(1) + λ(30) + φ(500) + α(1) = 532
        
        This is the same as GreekLetterValueCalculator.
        """
        return GreekLetterValueCalculator()._initialize_mapping()


class GreekReverseSubstitutionCalculator(GematriaCalculator):
    """Calculator for Greek Reverse Substitution / Greek AtBash (Antistrophē Antikatastaseē / Αντίστροφη Αντικατάσταση).
    
    Also known as Antistrophē Antikatastaseē (Αντίστροφη Αντικατάσταση)
    "Reverse Substitution" - the Greek equivalent of Hebrew AtBash
    
    This ancient substitution cipher reverses the Greek alphabet:
    - First letter (α Alpha) ↔ Last letter (ϡ Sampi)
    - Second letter (β Beta) ↔ Second-to-last (ω Omega)
    - Third letter (γ Gamma) ↔ Third-to-last (ψ Psi)
    - And so on through the 27-letter extended alphabet...
    
    Historical Context:
    Greek reverse substitution appears in Gnostic texts and early Christian
    mystical writings. It was used to conceal sacred teachings and reveal
    hidden meanings in scripture, following the Hebrew AtBash tradition.
    
    Applications:
    - Gnostic text analysis
    - Early Christian mysticism
    - Finding hidden meanings in New Testament
    - Revealing alternative interpretations
    
    Example:
    αβγ (Alpha-Beta-Gamma):
    Standard: α(1) + β(2) + γ(3) = 6
    Reverse: ϡ(900) + ω(800) + ψ(700) = 2400
    
    This transformation reveals hidden numerical layers, with the dramatic
    increase suggesting deeper esoteric significance.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Greek (Reverse Substitution)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Greek letter-to-value mapping using reverse substitution.
        
        Reverses the alphabet (Greek AtBash):
        - Alpha (1st) ↔ Sampi (27th): α → ϡ (900)
        - Beta (2nd) ↔ Omega (26th): β → ω (800)
        - etc.
        """
        standard_values = {
            'Α': 1,   'α': 1,   'Β': 2,   'β': 2,   'Γ': 3,   'γ': 3,
            'Δ': 4,   'δ': 4,   'Ε': 5,   'ε': 5,   'Ϝ': 6,   'ϝ': 6,
            'Ζ': 7,   'ζ': 7,   'Η': 8,   'η': 8,   'Θ': 9,   'θ': 9,
            'Ι': 10,  'ι': 10,  'Κ': 20,  'κ': 20,  'Λ': 30,  'λ': 30,
            'Μ': 40,  'μ': 40,  'Ν': 50,  'ν': 50,  'Ξ': 60,  'ξ': 60,
            'Ο': 70,  'ο': 70,  'Π': 80,  'π': 80,  'Ϙ': 90,  'ϙ': 90,
            'Ρ': 100, 'ρ': 100, 'Σ': 200, 'σ': 200, 'ς': 200,
            'Τ': 300, 'τ': 300, 'Υ': 400, 'υ': 400, 'Φ': 500, 'φ': 500,
            'Χ': 600, 'χ': 600, 'Ψ': 700, 'ψ': 700, 'Ω': 800, 'ω': 800,
            'ϡ': 900
        }
        
        # Reverse substitution
        return {
            'Α': 900, 'α': 900,   # Alpha → Sampi
            'Β': 800, 'β': 800,   # Beta → Omega
            'Γ': 700, 'γ': 700,   # Gamma → Psi
            'Δ': 600, 'δ': 600,   # Delta → Chi
            'Ε': 500, 'ε': 500,   # Epsilon → Phi
            'Ϝ': 400, 'ϝ': 400,   # Digamma → Upsilon
            'Ζ': 300, 'ζ': 300,   # Zeta → Tau
            'Η': 200, 'η': 200,   # Eta → Sigma
            'Θ': 100, 'θ': 100,   # Theta → Rho
            'Ι': 90,  'ι': 90,    # Iota → Koppa
            'Κ': 80,  'κ': 80,    # Kappa → Pi
            'Λ': 70,  'λ': 70,    # Lambda → Omicron
            'Μ': 60,  'μ': 60,    # Mu → Xi
            'Ν': 50,  'ν': 50,    # Nu → Nu (middle)
            'Ξ': 40,  'ξ': 40,    # Xi → Mu
            'Ο': 30,  'ο': 30,    # Omicron → Lambda
            'Π': 20,  'π': 20,    # Pi → Kappa
            'Ϙ': 10,  'ϙ': 10,    # Koppa → Iota
            'Ρ': 9,   'ρ': 9,     # Rho → Theta
            'Σ': 8,   'σ': 8, 'ς': 8,  # Sigma → Eta
            'Τ': 7,   'τ': 7,     # Tau → Zeta
            'Υ': 6,   'υ': 6,     # Upsilon → Digamma
            'Φ': 5,   'φ': 5,     # Phi → Epsilon
            'Χ': 4,   'χ': 4,     # Chi → Delta
            'Ψ': 3,   'ψ': 3,     # Psi → Gamma
            'Ω': 2,   'ω': 2,     # Omega → Beta
            'ϡ': 1,               # Sampi → Alpha
        }


class GreekPairMatchingCalculator(GematriaCalculator):
    """Calculator for Greek Pair Matching / Greek Albam (Antistoichisi Zeugous / Αντιστοίχιση Ζεύγους)."""
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Greek (Pair Matching)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Greek letter-to-value mapping using pair matching substitution.
        
        Pairs first half with second half (like Hebrew Albam):
        - Alpha (1st) → Lambda (12th): α → λ (30)
        - Beta (2nd) → Mu (13th): β → μ (40)
        - etc.
        """
        standard_values = {
            'Α': 1,   'α': 1,   'Β': 2,   'β': 2,   'Γ': 3,   'γ': 3,
            'Δ': 4,   'δ': 4,   'Ε': 5,   'ε': 5,   'Ϝ': 6,   'ϝ': 6,
            'Ζ': 7,   'ζ': 7,   'Η': 8,   'η': 8,   'Θ': 9,   'θ': 9,
            'Ι': 10,  'ι': 10,  'Κ': 20,  'κ': 20,  'Λ': 30,  'λ': 30,
            'Μ': 40,  'μ': 40,  'Ν': 50,  'ν': 50,  'Ξ': 60,  'ξ': 60,
            'Ο': 70,  'ο': 70,  'Π': 80,  'π': 80,  'Ϙ': 90,  'ϙ': 90,
            'Ρ': 100, 'ρ': 100, 'Σ': 200, 'σ': 200, 'ς': 200,
            'Τ': 300, 'τ': 300, 'Υ': 400, 'υ': 400, 'Φ': 500, 'φ': 500,
            'Χ': 600, 'χ': 600, 'Ψ': 700, 'ψ': 700, 'Ω': 800, 'ω': 800,
            'ϡ': 900
        }
        
        # Pair matching substitution (first 13 pair with last 14, with Nu in middle)
        return {
            'Α': 30,  'α': 30,    # Alpha → Lambda
            'Β': 40,  'β': 40,    # Beta → Mu
            'Γ': 50,  'γ': 50,    # Gamma → Nu
            'Δ': 60,  'δ': 60,    # Delta → Xi
            'Ε': 70,  'ε': 70,    # Epsilon → Omicron
            'Ϝ': 80,  'ϝ': 80,    # Digamma → Pi
            'Ζ': 90,  'ζ': 90,    # Zeta → Koppa
            'Η': 100, 'η': 100,   # Eta → Rho
            'Θ': 200, 'θ': 200,   # Theta → Sigma
            'Ι': 300, 'ι': 300,   # Iota → Tau
            'Κ': 400, 'κ': 400,   # Kappa → Upsilon
            'Λ': 1,   'λ': 1,     # Lambda → Alpha
            'Μ': 2,   'μ': 2,     # Mu → Beta
            'Ν': 3,   'ν': 3,     # Nu → Gamma
            'Ξ': 4,   'ξ': 4,     # Xi → Delta
            'Ο': 5,   'ο': 5,     # Omicron → Epsilon
            'Π': 6,   'π': 6,     # Pi → Digamma
            'Ϙ': 7,   'ϙ': 7,     # Koppa → Zeta
            'Ρ': 8,   'ρ': 8,     # Rho → Eta
            'Σ': 9,   'σ': 9, 'ς': 9,  # Sigma → Theta
            'Τ': 10,  'τ': 10,    # Tau → Iota
            'Υ': 20,  'υ': 20,    # Upsilon → Kappa
            'Φ': 500, 'φ': 500,   # Phi → Phi (remains)
            'Χ': 600, 'χ': 600,   # Chi → Chi (remains)
            'Ψ': 700, 'ψ': 700,   # Psi → Psi (remains)
            'Ω': 800, 'ω': 800,   # Omega → Omega (remains)
            'ϡ': 900,             # Sampi → Sampi (remains)
        }


class GreekNextLetterCalculator(GematriaCalculator):
    """Calculator for Greek Next Letter Value (Arithmos Epomenos / Αριθμός Ἐπόμενος).
    
    Also known as Arithmos Epomenos (Αριθμός Ἐπόμενος) - "Following Number"
    
    This unique substitution method replaces each letter with the value of
    the following letter in the alphabet:
    - α (Alpha) → β (Beta, value 2)
    - β (Beta) → γ (Gamma, value 3)
    - ...
    - ω (Omega) → ϡ (Sampi, value 900)
    - ϡ (Sampi) → α (Alpha, value 1, wrapping around)
    
    Historical Context:
    This progressive substitution appears in Byzantine cryptography and
    represents the concept of succession, progression, and the cyclical
    nature of creation. Each letter points to what follows it.
    
    Applications:
    - Byzantine cryptographic analysis
    - Finding progressive patterns
    - Exploring cyclical relationships
    - Philosophical meditation on succession
    
    Example:
    αβγ (Alpha-Beta-Gamma):
    Standard: α(1) + β(2) + γ(3) = 6
    Next Letter: β(2) + γ(3) + δ(4) = 9
    
    This method reveals the "forward momentum" inherent in each letter,
    representing the eternal progression of existence.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Greek (Next Letter)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Map each letter to the value of the following letter.
        
        Example: α → β (2), β → γ (3), etc.
        """
        return {
            'Α': 2,   'α': 2,    # Alpha → Beta
            'Β': 3,   'β': 3,    # Beta → Gamma
            'Γ': 4,   'γ': 4,    # Gamma → Delta
            'Δ': 5,   'δ': 5,    # Delta → Epsilon
            'Ε': 6,   'ε': 6,    # Epsilon → Digamma
            'Ϝ': 7,   'ϝ': 7,    # Digamma → Zeta
            'Ζ': 8,   'ζ': 8,    # Zeta → Eta
            'Η': 9,   'η': 9,    # Eta → Theta
            'Θ': 10,  'θ': 10,   # Theta → Iota
            'Ι': 20,  'ι': 20,   # Iota → Kappa
            'Κ': 30,  'κ': 30,   # Kappa → Lambda
            'Λ': 40,  'λ': 40,   # Lambda → Mu
            'Μ': 50,  'μ': 50,   # Mu → Nu
            'Ν': 60,  'ν': 60,   # Nu → Xi
            'Ξ': 70,  'ξ': 70,   # Xi → Omicron
            'Ο': 80,  'ο': 80,   # Omicron → Pi
            'Π': 90,  'π': 90,   # Pi → Koppa
            'Ϙ': 100, 'ϙ': 100,  # Koppa → Rho
            'Ρ': 200, 'ρ': 200,  # Rho → Sigma
            'Σ': 300, 'σ': 300, 'ς': 300,  # Sigma → Tau
            'Τ': 400, 'τ': 400,  # Tau → Upsilon
            'Υ': 500, 'υ': 500,  # Upsilon → Phi
            'Φ': 600, 'φ': 600,  # Phi → Chi
            'Χ': 700, 'χ': 700,  # Chi → Psi
            'Ψ': 800, 'ψ': 800,  # Psi → Omega
            'Ω': 900, 'ω': 900,  # Omega → Sampi
            'ϡ': 1,              # Sampi → Alpha (wrap around)
        }
