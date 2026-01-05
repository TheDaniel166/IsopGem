"""Arabic gematria calculator implementation (Abjad system)."""
from typing import Dict
from .base_calculator import GematriaCalculator


class ArabicGematriaCalculator(GematriaCalculator):
    """Calculator for Arabic gematria using the Abjad system.
    
    The Abjad system (أبجد) is the traditional Arabic numerology system,
    similar to Hebrew gematria. It assigns numerical values to the 28 letters
    of the Arabic alphabet in their traditional alphabetical order (not the
    modern order).
    
    Value Ranges:
    - Alif through Ya: 1-10 (units)
    - Kaf through Qaf: 20-100 (tens)
    - Ra through Ghayn: 200-1000 (hundreds)
    
    Historical Context:
    The Abjad system predates modern Arabic numerals and was used for:
    - Recording dates in Islamic manuscripts
    - Mystical interpretation of the Quran (Ilm al-Huruf)
    - Magical talismans and amulets
    - Poetry and wordplay
    
    The traditional ordering follows the Levantine sequence:
    أبجد هوز حطي كلمن سعفص قرشت ثخذ ضظغ
    (Abjad Hawaz Hutti Kalaman Sa'fas Qurshat Thakhath Dadhagh)
    
    Applications:
    - **Chronograms**: Encoding dates in poetry or inscriptions
    - **Quranic Analysis**: Finding numerical patterns in scripture
    - **Mysticism**: Sufi interpretation of divine names
    - **Divination**: Traditional Arabic letter magic (simiya)
    
    Example:
    الله (Allah, "God"):
    ا(1) + ل(30) + ل(30) + ه(5) = 66
    
    محمد (Muhammad):
    م(40) + ح(8) + م(40) + د(4) = 92
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Arabic (Abjad)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Arabic letter-to-value mapping (Abjad order).
        
        The Abjad system uses the traditional alphabetical order,
        not the modern Arabic alphabet order:
        - Units: ا ب ج د ه و ز ح ط ي (1-10)
        - Tens: ك ل م ن س ع ف ص ق (20-90, 100)
        - Hundreds: ر ش ت ث خ ذ ض ظ غ (200-1000)
        
        Returns:
            Dictionary mapping Arabic letters to their Abjad values
        """
        return {
            # Units (1-10)
            'ا': 1,    # Alif
            'ب': 2,    # Ba
            'ج': 3,    # Jim
            'د': 4,    # Dal
            'ه': 5,    # Ha
            'و': 6,    # Waw
            'ز': 7,    # Zay
            'ح': 8,    # Ha (emphatic)
            'ط': 9,    # Ta (emphatic)
            'ي': 10,   # Ya
            
            # Tens (20-100)
            'ك': 20,   # Kaf
            'ل': 30,   # Lam
            'م': 40,   # Mim
            'ن': 50,   # Nun
            'س': 60,   # Sin
            'ع': 70,   # Ayn
            'ف': 80,   # Fa
            'ص': 90,   # Sad
            'ق': 100,  # Qaf
            
            # Hundreds (200-1000)
            'ر': 200,  # Ra
            'ش': 300,  # Shin
            'ت': 400,  # Ta
            'ث': 500,  # Tha
            'خ': 600,  # Kha
            'ذ': 700,  # Dhal
            'ض': 800,  # Dad
            'ظ': 900,  # Dha (emphatic)
            'غ': 1000, # Ghayn
        }


class ArabicMaghrebiCalculator(GematriaCalculator):
    """Calculator for Western Arabic (Maghrebi) Abjad variant.
    
    The Maghrebi system uses a slightly different ordering than the Eastern
    Abjad system, reflecting regional variations in North Africa and Al-Andalus.
    
    Key differences from Eastern Abjad:
    - Sād (ص) and Dād (ض) swap positions
    - Slightly different ordering in the hundreds range
    
    Historical Context:
    Used in Morocco, Algeria, Tunisia, Libya, and medieval Islamic Spain.
    Important for interpreting manuscripts and inscriptions from these regions.
    
    Example:
    بسم (Bism, "In the name"):
    ب(2) + س(60) + م(40) = 102
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Arabic (Maghrebi)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Maghrebi Abjad mapping with regional ordering.
        
        Returns:
            Dictionary mapping Arabic letters to Maghrebi values
        """
        return {
            # Units (1-10) - same as Eastern
            'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5,
            'و': 6, 'ز': 7, 'ح': 8, 'ط': 9, 'ي': 10,
            
            # Tens (20-100) - Sād and Dād swapped
            'ك': 20, 'ل': 30, 'م': 40, 'ن': 50, 'س': 60,
            'ع': 70, 'ف': 80, 'ض': 90, 'ق': 100,  # Note: ض here instead of ص
            
            # Hundreds (200-1000)
            'ر': 200, 'ش': 300, 'ت': 400, 'ث': 500, 'خ': 600,
            'ذ': 700, 'ص': 800, 'ظ': 900, 'غ': 1000,  # Note: ص here instead of ض
        }


class ArabicSmallValueCalculator(GematriaCalculator):
    """Calculator for Arabic small value (Mispar Katan) method.
    
    Reduces all letters to single digits (1-9) by using only the units digit.
    This parallels the Hebrew Small Value (Mispar Katan) method.
    
    Example:
    محمد (Muhammad):
    م(4) + ح(8) + م(4) + ד(4) = 20
    
    Note: م (Mim) = 40, units digit = 4
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Arabic (Small Value)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Initialize small value mapping (units digit only)."""
        return {
            'ا': 1, 'ب': 2, 'ج': 3, 'د': 4, 'ه': 5,
            'و': 6, 'ز': 7, 'ح': 8, 'ط': 9, 'ي': 1,  # 10 → 1
            'ك': 2, 'ل': 3, 'م': 4, 'ن': 5, 'س': 6,  # 20-60 → 2-6
            'ع': 7, 'ف': 8, 'ص': 9, 'ق': 1,           # 70-100 → 7-9, 1
            'ر': 2, 'ش': 3, 'ت': 4, 'ث': 5, 'خ': 6,  # 200-600 → 2-6
            'ذ': 7, 'ض': 8, 'ظ': 9, 'غ': 1,           # 700-1000 → 7-9, 1
        }


class ArabicOrdinalCalculator(GematriaCalculator):
    """Calculator for Arabic ordinal (Mispar Siduri) method.
    
    Assigns sequential values 1-28 based on the modern Arabic alphabet order,
    not the traditional Abjad order.
    
    Modern Arabic alphabet order:
    ا ب ت ث ج ح خ د ذ ر ز س ش ص ض ط ظ ع غ ف ق ك ل م ن ه و ي
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Arabic (Ordinal)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Initialize ordinal mapping (modern alphabetical order 1-28)."""
        return {
            'ا': 1,  'ب': 2,  'ت': 3,  'ث': 4,  'ج': 5,  'ح': 6,  'خ': 7,
            'د': 8,  'ذ': 9,  'ر': 10, 'ز': 11, 'س': 12, 'ش': 13, 'ص': 14,
            'ض': 15, 'ط': 16, 'ظ': 17, 'ع': 18, 'غ': 19, 'ف': 20, 'ق': 21,
            'ك': 22, 'ل': 23, 'م': 24, 'ن': 25, 'ه': 26, 'و': 27, 'ي': 28,
        }
