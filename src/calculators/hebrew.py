"""Hebrew gematria calculator implementation."""
from typing import Dict
from .base import GematriaCalculator


class HebrewGematriaCalculator(GematriaCalculator):
    """Calculator for Hebrew gematria (standard values)."""
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Hebrew (Standard)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Hebrew letter-to-value mapping.
        
        Uses standard Hebrew gematria values:
        - Aleph through Yod: 1-10
        - Kaf through Tzadi: 20-90
        - Qof through Tav: 100-400
        - Final forms have same values as their regular forms
        
        Returns:
            Dictionary mapping Hebrew letters to their gematria values
        """
        return {
            # Aleph through Yod (1-10)
            'א': 1,   # Aleph
            'ב': 2,   # Bet
            'ג': 3,   # Gimel
            'ד': 4,   # Dalet
            'ה': 5,   # He
            'ו': 6,   # Vav
            'ז': 7,   # Zayin
            'ח': 8,   # Het
            'ט': 9,   # Tet
            'י': 10,  # Yod
            
            # Kaf through Tzadi (20-90)
            'כ': 20,  # Kaf
            'ך': 20,  # Kaf (final)
            'ל': 30,  # Lamed
            'מ': 40,  # Mem
            'ם': 40,  # Mem (final)
            'נ': 50,  # Nun
            'ן': 50,  # Nun (final)
            'ס': 60,  # Samekh
            'ע': 70,  # Ayin
            'פ': 80,  # Pe
            'ף': 80,  # Pe (final)
            'צ': 90,  # Tzadi
            'ץ': 90,  # Tzadi (final)
            
            # Qof through Tav (100-400)
            'ק': 100, # Qof
            'ר': 200, # Resh
            'ש': 300, # Shin
            'ת': 400, # Tav
        }
