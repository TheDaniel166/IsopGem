"""Base class for gematria calculators following DRY principles."""
from abc import ABC, abstractmethod
from typing import Dict


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
    
    def calculate(self, text: str) -> int:
        """
        Calculate the gematria value of the given text.
        
        Args:
            text: The input text to calculate
            
        Returns:
            The total gematria value
        """
        total = 0
        for char in text:
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
    
    def get_breakdown(self, text: str) -> Dict[str, int]:
        """
        Get a breakdown of each character's value in the text.
        
        Args:
            text: The input text to analyze
            
        Returns:
            Dictionary mapping each character to its value
        """
        breakdown = {}
        for char in text:
            if char in self._letter_values:
                breakdown[char] = self._letter_values[char]
        return breakdown
