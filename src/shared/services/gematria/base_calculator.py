"""
SHARED JUSTIFICATION:
- RATIONALE: Contract (Gematria calculator protocol)
- USED BY: Gematria (15 references)
- CRITERION: 4 (Shared data contract)

Base class for gematria calculators following DRY principles.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
import unicodedata


class GematriaCalculator(ABC):
    """Abstract base class for all gematria calculation systems."""


    
    def __init__(self):
        """Initialize the calculator with its letter-value mapping."""
        self._letter_values: Dict[str, int] = self._initialize_mapping()
    
    @abstractmethod
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize and return the letter-to-value mapping for this system.
        
        Returns:
            Dictionary mapping characters to their numeric values
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this gematria system."""
        pass
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text by removing diacritical marks and accents.
        
        This removes:
        - Hebrew nikud (vowel points) and cantillation marks
        - Greek accent marks (tonos, dialytika, etc.)
        - Other combining diacritical marks
        
        Args:
            text: The input text to normalize
            
        Returns:
            Normalized text with diacritics removed
        """
        # NFD normalization separates base characters from combining marks
        normalized = unicodedata.normalize('NFD', text)
        
        # Filter out combining characters (category Mn = Nonspacing_Mark)
        # This removes Hebrew nikud, Greek accents, etc.
        result = ''.join(
            char for char in normalized
            if unicodedata.category(char) != 'Mn'
        )
        
        # Return to NFC (composed) form
        return unicodedata.normalize('NFC', result)
    
    def calculate(self, text: str) -> int:
        """
        Calculate the gematria value of the given text.
        
        Args:
            text: The input text to calculate
            
        Returns:
            The total gematria value
        """
        # Normalize text before calculation
        normalized_text = self.normalize_text(text)
        
        total = 0
        for char in normalized_text:
            value = self._letter_values.get(char, 0)
            total += value
        return total
    
    def get_letter_value(self, char: str) -> int:
        """
        Get the gematria value of a single character.
        
        Args:
            char: Single character to look up
            
        Returns:
            The numeric value or 0 if not found
        """
        return self._letter_values.get(char, 0)
    
    def get_breakdown(self, text: str) -> list:
        """
        Get a breakdown of each character's value in the text.
        
        Args:
            text: The input text to analyze
            
        Returns:
            List of tuples (character, value) preserving order and duplicates
        """
        # Normalize text before breakdown
        normalized_text = self.normalize_text(text)
        
        breakdown = []
        for char in normalized_text:
            if char in self._letter_values:
                breakdown.append((char, self._letter_values[char]))
        return breakdown