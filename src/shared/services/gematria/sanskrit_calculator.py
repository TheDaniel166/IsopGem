"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: Domain Logic (GRANDFATHERED - pending refactor)
- USED BY: Internal shared/ modules only (1 references)
- CRITERION: Violation (Domain algorithms in shared)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""

"""Sanskrit gematria calculator implementation (Katapayadi system)."""
from typing import Dict, List, Tuple
from .base_calculator import GematriaCalculator


class SanskritKatapayadiCalculator(GematriaCalculator):
    """Calculator for Sanskrit Katapayadi system.

    
    The Katapayadi system (कटपयादि) maps Sanskrit letters to digits,
    allowing numbers to be encoded as words or verses.
    
    Key Principles:
    1.  **Positional System**: Returns a sequence of digits, not a sum.
        Example: "Gopi" (ga=3, pa=1) -> 31
    2.  **Mapping**:
        - 1: Ka, Ta, Pa, Ya
        - 2: Kha, Tha, Pha, Ra
        - 3: Ga, Da, Ba, La
        - 4: Gha, Dha, Bha, Va
        - 5: Nga, Na, Ma, Sha
        - 6: Cha, Ta, Sha
        - 7: Chha, Tha, Sa
        - 8: Ja, Da, Ha
        - 9: Jha, Dha
        - 0: Nya, Na
    3.  **Conjuncts (Samyuktakshara)**:
        - Only the LAST consonant in a conjunct group counts.
        - Previous consonants are ignored.
    4.  **Vowels**:
        - Standalone vowels (Svara) = 0.
        - Attached vowels (Matras) = Ignored (facilitators).
    5.  **Halant (Virama)**: Consonants with Halant (no vowel) are ignored.
        (This simplifies the 'last consonant' rule: a consonant is only valid if followed by a vowel or at end of word?)
        Actually, standard rule: "Only the consonant immediately preceding a vowel has value".
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Sanskrit (Katapayadi)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Sanskrit letter-to-digit mapping.
        Note: This mapping is used for individual character lookup fallback.
        """
        return {
            # Group Ka (1-5)
            'क': 1, 'ख': 2, 'ग': 3, 'घ': 4, 'ङ': 5,
            # Group Cha (6-0)
            'च': 6, 'छ': 7, 'ज': 8, 'झ': 9, 'ञ': 0,
            # Group Ta (Retroflex) (1-5)
            'ट': 1, 'ठ': 2, 'ड': 3, 'ढ': 4, 'ण': 5,
            # Group Ta (Dental) (6-0)
            'त': 6, 'थ': 7, 'द': 8, 'ध': 9, 'न': 0,
            # Group Pa (1-5)
            'प': 1, 'फ': 2, 'ब': 3, 'भ': 4, 'म': 5,
            # Group Ya (1-8) + 9?? No, Ya group is usually 1-8/9
            'य': 1, 'र': 2, 'ल': 3, 'व': 4,
            'श': 5, 'ष': 6, 'स': 7, 'ह': 8,
            
            # Standalone Vowels (Svara) = 0
            'अ': 0, 'आ': 0, 'इ': 0, 'ई': 0, 'उ': 0, 'ऊ': 0,
            'ऋ': 0, 'ॠ': 0, 'ऌ': 0, 'ॡ': 0, 'ए': 0, 'ऐ': 0, 
            'ओ': 0, 'औ': 0, 'अं': 0, 'अः': 0
        }
    
    def calculate(self, text: str) -> int:
        """
        Calculate Katapayadi value.
        Returns the integer representation of the digit sequence.
        Example: 3, 1, 4 -> 314
        """
        digits = self._get_digits(text)
        if not digits:
            return 0
        
        # Join digits to form the number string, then parse int
        num_str = "".join(str(d) for d in digits)
        return int(num_str)

    def get_breakdown(self, text: str) -> List[Tuple[str, int]]:
        """
        Get breakdown of calculation.
        """
        # Try using the library first
        try:
            from katapayadi import katapayadi
            # The library likely parses syllable by syllable.
            # If we just want the output, calculate() uses _get_digits which loops back here?
            # No, _get_digits calls get_breakdown.
            # Let's inspect what the library offers.
            # Standard library usage: katapayadi.decrypt('gopi') -> '31' (string?)
            pass
        except ImportError:
            pass

        # For breakdown, we want (char, value).
        # Since the library gives the final output, reverse engineering the breakdown 
        # from the library might be tricky if it doesn't align char-to-char.
        
        # We will keep the custom implementation for breakdown to ensure visual feedback,
        # but rely on library for the definitive calculation if possible?
        # Actually, if we use the library, we should trust its parsing logic.
        
        # Implementation Plan Decision:
        # Use library for calculate() logic primarily.
        # But get_breakdown needs to map parts.
        
        # Let's stick to the manual implementation for get_breakdown for now,
        # but use the library in calculate if available to ensure accuracy of the total.
        
        # ... logic ...
        return self._manual_breakdown(text)

    def _get_digits(self, text: str) -> List[int]:
        """Extract the sequence of digits."""
        # Try library first
        try:
            import katapayadi
            # The library appears to be broken in Python 3 (relative import issues).
            # But we implement the hook here in case it's fixed or patched.
            if hasattr(katapayadi, 'decrypt'):
                val_str = katapayadi.decrypt(text)
                return [int(d) for d in str(val_str) if d.isdigit()]
        except (ImportError, AttributeError, Exception):
            # Fallback to manual implementation on any library failure
            pass
            
        # Fallback to manual
        breakdown = self._manual_breakdown(text)
        return [val for _, val in breakdown]

    def _manual_breakdown(self, text: str) -> List[Tuple[str, int]]:
        """Manual parsing logic."""
        breakdown = []
        HALANT = '\u094D'
        chars = list(text)
        n = len(chars)
        
        i = 0
        while i < n:
            char = chars[i]
            val = self._letter_values.get(char)
            
            if val is not None:
                # Check for Halant interaction
                is_followed_by_halant = (i + 1 < n) and (chars[i+1] == HALANT)
                
                if is_followed_by_halant:
                    # Dead consonant -> Ignore
                    pass
                else:
                    # Live consonant or vowel
                    breakdown.append((char, val))
            i += 1
        return breakdown