"""TQ (Trigrammaton Qabbalah) English gematria calculator implementation."""
from typing import Dict
from .base_calculator import GematriaCalculator


class TQGematriaCalculator(GematriaCalculator):
    """Calculator for TQ (Trigrammaton Qabbalah) English gematria.
    
    Also known as TQ System or Trigrammaton Qabalah
    
    TQ is a modern English gematria system that assigns unique values (0-25)
    to the 26 letters of the English alphabet in a specific non-sequential order.
    The arrangement is based on sacred geometry and Qabalistic principles.
    
    Value Assignment:
    Row 1 (0-9):   I=0, L=1, C=2, H=3, P=4, A=5, X=6, J=7, W=8, T=9
    Row 2 (10-19): O=10, G=11, F=12, E=13, R=14, S=15, Q=16, K=17, Y=18, Z=19
    Row 3 (20-25): B=20, M=21, V=22, D=23, N=24, U=25
    
    Historical Context:
    The TQ system was developed in the modern era as an English equivalent
    to Hebrew gematria and Greek isopsephy. It's used in contemporary
    Western esoteric traditions, chaos magick, and modern Qabalah.
    
    The letter arrangement is non-arbitrary, based on:
    - Sacred geometric patterns
    - Qabalistic correspondences
    - Phonetic relationships
    - Esoteric letter symbolism
    
    Applications:
    - English language numerology
    - Modern Western Qabalah
    - Chaos magick sigilization
    - Finding numerical patterns in English text
    - Personal name analysis
    
    Example:
    LIGHT:
    L(1) + I(0) + G(11) + H(3) + T(9) = 24
    
    LOVE:
    L(1) + O(10) + V(22) + E(13) = 46
    
    TRUTH:
    T(9) + R(14) + U(25) + T(9) + H(3) = 60
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "English (TQ)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize TQ letter-to-value mapping.
        
        Uses Trigrammaton Qabbalah values:
        - i/I = 0, l/L = 1, c/C = 2, h/H = 3, p/P = 4
        - a/A = 5, x/X = 6, j/J = 7, w/W = 8, t/T = 9
        - o/O = 10, g/G = 11, f/F = 12, e/E = 13, r/R = 14
        - s/S = 15, q/Q = 16, k/K = 17, y/Y = 18, z/Z = 19
        - b/B = 20, m/M = 21, v/V = 22, d/D = 23, n/N = 24, u/U = 25
        
        Returns:
            Dictionary mapping English letters to their TQ values
        """
        return {
            # Row 1 (0-9)
            'i': 0,  'I': 0,
            'l': 1,  'L': 1,
            'c': 2,  'C': 2,
            'h': 3,  'H': 3,
            'p': 4,  'P': 4,
            'a': 5,  'A': 5,
            'x': 6,  'X': 6,
            'j': 7,  'J': 7,
            'w': 8,  'W': 8,
            't': 9,  'T': 9,
            
            # Row 2 (10-19)
            'o': 10, 'O': 10,
            'g': 11, 'G': 11,
            'f': 12, 'F': 12,
            'e': 13, 'E': 13,
            'r': 14, 'R': 14,
            's': 15, 'S': 15,
            'q': 16, 'Q': 16,
            'k': 17, 'K': 17,
            'y': 18, 'Y': 18,
            'z': 19, 'Z': 19,
            
            # Row 3 (20-25)
            'b': 20, 'B': 20,
            'm': 21, 'M': 21,
            'v': 22, 'V': 22,
            'd': 23, 'D': 23,
            'n': 24, 'N': 24,
            'u': 25, 'U': 25,
        }


class TQReducedCalculator(GematriaCalculator):
    """Calculator for TQ Reduced Value (sum of digits).
    
    Also known as TQ Reduction or Digital Root
    
    This method reduces the TQ value to a single digit (1-9) by repeatedly
    summing the digits until only one remains. This reveals the essential
    numerical essence of a word.
    
    Formula: Repeatedly sum digits until result is 1-9
    
    Historical Context:
    Digit reduction to find the "digital root" is used across many numerological
    traditions, from Pythagorean numerology to modern Western systems. In TQ,
    it reveals the core vibrational frequency of English words.
    
    Applications:
    - Quick numerological analysis
    - Finding core word essence
    - Life path number calculations
    - Simplified TQ readings
    
    Example:
    LIGHT:
    Standard TQ: L(1) + I(0) + G(11) + H(3) + T(9) = 24
    Reduced: 2 + 4 = 6
    
    LOVE:
    Standard TQ: 46
    Reduced: 4 + 6 = 10 → 1 + 0 = 1
    
    TRUTH:
    Standard TQ: 60
    Reduced: 6 + 0 = 6
    
    Interestingly, both LIGHT and TRUTH reduce to 6, suggesting a
    numerological connection between these concepts.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "English (TQ Reduced)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use standard TQ values."""
        return TQGematriaCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate TQ value and reduce to single digit.
        
        Args:
            text: The text to calculate
            
        Returns:
            Reduced value (sum of digits repeatedly until single digit)
        """
        normalized = self.normalize_text(text)
        total = super().calculate(normalized)
        
        # Reduce to single digit
        while total >= 10:
            total = sum(int(digit) for digit in str(total))
        
        return total


class TQSquareCalculator(GematriaCalculator):
    """Calculator for TQ Square Value (sum of squared letter values).
    
    Also known as TQ Square Sum or Quadratic TQ
    
    This method squares each letter's TQ value before summing, amplifying
    the numerical significance and revealing hidden power dynamics within words.
    
    Formula: Σ(letter_TQ_value²)
    
    Historical Context:
    Square values are used in advanced Western numerology to magnify the
    energetic signature of words. The squaring operation represents the
    manifestation of spiritual potential into material reality.
    
    Applications:
    - Advanced TQ numerology
    - Amplifying word power in magickal work
    - Finding hidden numerical relationships
    - Energetic signature analysis
    
    Example:
    LIGHT:
    Standard TQ: 24
    Square: L(1²=1) + I(0²=0) + G(11²=121) + H(3²=9) + T(9²=81) = 212
    
    LOVE:
    Standard TQ: 46
    Square: L(1) + O(100) + V(484) + E(169) = 754
    
    TRUTH:
    Standard TQ: 60
    Square: T(81) + R(196) + U(625) + T(81) + H(9) = 992
    
    The exponential increase reveals the intensified energetic power
    of these foundational concepts.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "English (TQ Square)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use standard TQ values."""
        return TQGematriaCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate sum of squared TQ letter values.
        
        Args:
            text: The text to calculate
            
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


class TQTriangularCalculator(GematriaCalculator):
    """Calculator for TQ Triangular Value (sum of triangular numbers).
    
    Also known as TQ Triangular Sum or Progressive TQ
    
    This method uses triangular numbers for each letter's TQ value.
    Triangular number T(n) = n(n+1)/2 represents the progressive
    accumulation from 1 to n.
    
    Formula: Σ(T(letter_TQ_value)) where T(n) = n(n+1)/2
    
    Historical Context:
    Triangular numbers have been sacred since Pythagorean times, representing
    the building blocks of reality. In TQ, they reveal the cumulative,
    progressive nature of word energies.
    
    Applications:
    - Progressive numerological analysis
    - Finding cumulative word power
    - Sacred geometry applications
    - Meditation on growth and manifestation
    
    Example:
    LIGHT:
    Standard TQ: 24
    Triangular: T(1)=1 + T(0)=0 + T(11)=66 + T(3)=6 + T(9)=45 = 118
    
    LOVE:
    Standard TQ: 46
    Triangular: T(1)=1 + T(10)=55 + T(22)=253 + T(13)=91 = 400
    
    TRUTH:
    Standard TQ: 60
    Triangular: T(9)=45 + T(14)=105 + T(25)=325 + T(9)=45 + T(3)=6 = 526
    
    The triangular values represent the full progressive manifestation
    of each word's spiritual potential.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "English (TQ Triangular)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use standard TQ values."""
        return TQGematriaCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate sum of triangular numbers for each letter.
        
        Triangular number formula: T(n) = n(n+1)/2
        
        Args:
            text: The text to calculate
            
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


class TQPositionCalculator(GematriaCalculator):
    """Calculator for TQ Letter Position Value - multiplies value by position in word.
    
    Also known as TQ Positional Weighting or Sequential TQ
    
    This method multiplies each letter's TQ value by its position in the word
    (1st letter × 1, 2nd letter × 2, etc.), giving more weight to letters
    appearing later in the word.
    
    Formula: Σ(letter_TQ_value × position_in_word)
    
    Historical Context:
    Positional weighting appears in advanced numerological systems where
    the placement of letters is considered as significant as their values.
    This recognizes that the same letters in different positions create
    different energetic signatures.
    
    Applications:
    - Advanced TQ analysis
    - Word structure significance
    - Finding positional patterns
    - Magickal name construction
    
    Example:
    LIGHT:
    Standard TQ: 24
    Position: L(1×1=1) + I(0×2=0) + G(11×3=33) + H(3×4=12) + T(9×5=45) = 91
    
    LOVE:
    Standard TQ: 46
    Position: L(1×1=1) + O(10×2=20) + V(22×3=66) + E(13×4=52) = 139
    
    TRUTH:
    Standard TQ: 60
    Position: T(9×1=9) + R(14×2=28) + U(25×3=75) + T(9×4=36) + H(3×5=15) = 163
    
    This method reveals that letter order matters - "LOVE" and "EVOL"
    would have different position values despite identical letter composition.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "English (TQ Position)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use standard TQ values."""
        return TQGematriaCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Multiply each letter's TQ value by its position in the word, then sum.
        
        Example: LIGHT = L(1×1=1) + I(0×2=0) + G(11×3=33) + H(3×4=12) + T(9×5=45) = 91
        
        Args:
            text: The text to calculate
            
        Returns:
            Sum of (letter_value × position_in_word)
        """
        normalized = self.normalize_text(text)
        total = 0
        
        for position, char in enumerate(normalized, start=1):
            if char in self._letter_values:
                value = self._letter_values[char]
                total += value * position
        
        return total
