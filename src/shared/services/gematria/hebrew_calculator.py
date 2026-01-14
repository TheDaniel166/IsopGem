"""
SHARED JUSTIFICATION:
- RATIONALE: Domain Logic (GRANDFATHERED - pending refactor)
- USED BY: Gematria (4 references)
- CRITERION: Violation (Domain algorithms in shared)

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md

Hebrew gematria calculator implementation.
"""
from typing import Dict
from .base_calculator import GematriaCalculator


class HebrewGematriaCalculator(GematriaCalculator):
    """Calculator for Hebrew gematria (standard values).



    
    Also known as Mispar Hechrachi (מספר הכרחי) - "Absolute Value"
    
    This is the most common and traditional method of Hebrew gematria, assigning
    numerical values to each letter of the Hebrew alphabet:
    - Aleph through Yod: 1-10 (units)
    - Kaf through Tzadi: 20-90 (tens)
    - Qof through Tav: 100-400 (hundreds)
    
    Historical Context:
    The standard gematria system dates back to ancient times and was used by
    Jewish scholars for biblical exegesis, mysticism, and numerology. It forms
    the foundation of Kabbalah and appears in the Talmud and Midrash.
    
    Applications:
    - **Semantic Equivalence (Gezera Shava)**: Identifying words that share the same "soul" or essence despite different meanings (e.g., *Mashiach* (Messiah) and *Nachash* (Snake) both = 358, implying the redemption of the primal fall).
    - **Commentary Decoding**: Unlocking specific interpretations in Midrash where rabbis link verses based solely on numerical equality.
    - **Theological Validation**: Confirming the mystical legitimacy of a concept by finding its numerical "root" in Torah.
    
    Example:
    יהוה (YHWH, the Tetragrammaton):
    י(10) + ה(5) + ו(6) + ה(5) = 26
    
    אהבה (Ahavah, "love"):
    א(1) + ה(5) + ב(2) + ה(5) = 13
    
    אחד (Echad, "one"):
    א(1) + ח(8) + ד(4) = 13
    
    Note: אהבה and אחד both equal 13, revealing a mystical connection
    between "love" and "oneness" in Kabbalistic thought.
    """
    
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


class HebrewSofitCalculator(GematriaCalculator):
    """Calculator for Hebrew gematria with final letter values (Mispar Sofit).
    
    Also known as Mispar Sofit (מספר סופית) - "Final Numbers"
    
    Five Hebrew letters have special forms when they appear at the end of a word:
    - Final Kaf (ך): 500 (instead of 20)
    - Final Mem (ם): 600 (instead of 40)
    - Final Nun (ן): 700 (instead of 50)
    - Final Pe (ף): 800 (instead of 80)
    - Final Tzadi (ץ): 900 (instead of 90)
    
    Historical Context:
    This system extends the Hebrew number system beyond 400 (Tav), allowing
    representation of larger numbers. It's used in Kabbalistic numerology to
    reveal deeper layers of meaning that standard gematria doesn't show.
    
    Applications:
    - **Eschatological Analysis**: Exploring concepts related to the "End of Days" or the final state of the Soul, as final letters represent the ultimate manifestation.
    - **Grounding Energy**: Distinguishing between an energy in transit vs. an energy that has fully precipitated into reality (Sofit values).
    - **Expansion of Scope**: Allowing for calculations of much larger cosmic cycles (e.g., the year 5784) without reducing to smaller units.
    
    Example:
    מלך (Melech, "king"):
    Standard: מ(40) + ל(30) + כ(20) = 90
    Sofit: מ(40) + ל(30) + ך(500) = 570
    
    The sofit value of 570 reveals additional layers of meaning associated
    with kingship and sovereignty in Kabbalistic interpretation.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Hebrew (Sofit)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Hebrew letter-to-value mapping with final letter values.
        
        Uses Mispar Sofit values:
        - Aleph through Yod: 1-10
        - Kaf through Tzadi: 20-90
        - Qof through Tav: 100-400
        - Final Kaf: 500
        - Final Mem: 600
        - Final Nun: 700
        - Final Pe: 800
        - Final Tzadi: 900
        
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
            'ך': 500, # Kaf (final) - SOFIT VALUE
            'ל': 30,  # Lamed
            'מ': 40,  # Mem
            'ם': 600, # Mem (final) - SOFIT VALUE
            'נ': 50,  # Nun
            'ן': 700, # Nun (final) - SOFIT VALUE
            'ס': 60,  # Samekh
            'ע': 70,  # Ayin
            'פ': 80,  # Pe
            'ף': 800, # Pe (final) - SOFIT VALUE
            'צ': 90,  # Tzadi
            'ץ': 900, # Tzadi (final) - SOFIT VALUE
            
            # Qof through Tav (100-400)
            'ק': 100, # Qof
            'ר': 200, # Resh
            'ש': 300, # Shin
            'ת': 400, # Tav
        }


class HebrewLetterValueCalculator(GematriaCalculator):
    """Computes numerical values for Hebrew letters using standard gematria.
    
    Also known as Mispar Gadol Sofit (מספר גדול סופית) - "Great Value with Finals"
    
    This method computes the numerical equivalent of each letter's spelled-out name using
    final letter values. For example:
    - Aleph (א) is spelled אלף, which equals 1 + 30 + 800 (final Pe) = 831
    - Bet (ב) is spelled בית, which equals 2 + 10 + 400 = 412
    
    Historical Context:
    This advanced Kabbalistic method is found in esoteric Jewish mysticism and
    is used to reveal deeper, hidden meanings within Hebrew text. It's based on
    the principle that the name of a letter contains its essential spiritual nature.
    
    Applications:
    - Deep Kabbalistic analysis of sacred texts
    - Understanding the spiritual essence of individual letters
    - Finding profound numerical connections between words
    - Advanced meditation on letter energies
    
    Example:
    The letter א (Aleph):
    Spelled: אלף
    Value: א(1) + ל(30) + ף(800) = 831
    
    The word אב ("father"):
    א (831) + ב (412) = 1,243
    
    This reveals that even a two-letter word can contain enormous numerical
    significance when each letter's full essence is considered.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Hebrew (Letter Value)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Hebrew letter-to-letter-value mapping.
        
        Uses the value of spelled-out letter names with final letter values:
        - Aleph (אלף) = 831 (using final Pe)
        - Bet (בית) = 412
        - etc.
        
        Returns:
            Dictionary mapping Hebrew letters to their letter values
        """
        return {
            # Letter values based on spelled-out names
            'א': 831,  # Aleph (ALPh) - אלף with final Pe
            'ב': 412,  # Bet (BITh) - בית
            'ג': 83,   # Gimel (GMIL) - גמל
            'ד': 434,  # Dalet (DLTh) - דלת
            'ה': 6,    # He (HA) - הא
            'ו': 12,   # Vav (VV) - וו
            'ז': 717,  # Zayin (ZIN) - זין
            'ח': 418,  # Het (CITh) - חית
            'ט': 419,  # Tet (TITh) - טית
            'י': 20,   # Yod (IVD) - יוד
            'כ': 820,  # Kaf (KPh) - כף with final Pe
            'ך': 820,  # Kaf (final) - same as regular
            'ל': 74,   # Lamed (LMD) - למד
            'מ': 640,  # Mem (MM) - מם with final Mem
            'ם': 640,  # Mem (final) - same as regular
            'נ': 756,  # Nun (NVN) - נון with final Nun
            'ן': 756,  # Nun (final) - same as regular
            'ס': 600,  # Samekh (SMKh) - סמך with final Kaf
            'ע': 780,  # Ayin (OIN) - עין with final Nun
            'פ': 85,   # Pe (PH) - פה
            'ף': 85,   # Pe (final) - same as regular
            'צ': 104,  # Tzadi (TzDI) - צדי
            'ץ': 104,  # Tzadi (final) - same as regular
            'ק': 906,  # Qof (QVPh) - קוף with final Pe
            'ר': 510,  # Resh (RISh) - ריש
            'ש': 1010, # Shin (ShIN) - שין with final Nun
            'ת': 406,  # Tav (TV) - תו
        }


class HebrewOrdinalCalculator(GematriaCalculator):
    """Calculator for Hebrew Ordinal Value (Mispar Siduri / מספר סידורי).
    
    Also known as Mispar Siduri (מספר סידורי) - "Ordinal Number"
    
    This method assigns each letter a value based on its position in the
    Hebrew alphabet (1-22), rather than its traditional numerical value:
    - Aleph = 1 (first letter)
    - Bet = 2 (second letter)
    - ...
    - Tav = 22 (twenty-second letter)
    
    Historical Context:
    This simplified system is used in modern Kabbalistic practice and new age
    numerology. It creates different numerical relationships than standard gematria,
    often revealing patterns related to the structural essence of words.
    
    Applications:
    - **Structural Blueprints**: Analyzing the "skeleton" of a word (its place in the alphabet) vs. its "flesh" (cosmic value).
    - **Inter-Language Comparison**: Offering a standardized baseline to compare Hebrew words with English/Greek words purely by alphabetic slot (1st letter = 1).
    - **Sequence Analysis**: Understanding the logical progression of concepts (e.g., why *Aleph* comes before *Bet*).
    
    Example:
    יהוה (YHWH):
    י(10th) + ה(5th) + ו(6th) + ה(5th) = 26
    (Note: Same value as standard gematria, but for different reasons)
    
    אהבה ("love"):
    א(1st) + ה(5th) + ב(2nd) + ה(5th) = 13
    (Also same as standard, showing the ordinal nature of early letters)
    
    משיח ("Messiah"):
    Standard: 40 + 300 + 10 + 8 = 358
    Ordinal: 13 + 21 + 10 + 8 = 52
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Hebrew (Ordinal)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Hebrew letter-to-ordinal-value mapping.
        
        Uses the position of each letter in the alphabet (1-22):
        - Aleph = 1, Bet = 2, ..., Tav = 22
        - Final forms have same values as their regular forms
        
        Returns:
            Dictionary mapping Hebrew letters to their ordinal values
        """
        return {
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
            'כ': 11,  # Kaf
            'ך': 11,  # Kaf (final)
            'ל': 12,  # Lamed
            'מ': 13,  # Mem
            'ם': 13,  # Mem (final)
            'נ': 14,  # Nun
            'ן': 14,  # Nun (final)
            'ס': 15,  # Samekh
            'ע': 16,  # Ayin
            'פ': 17,  # Pe
            'ף': 17,  # Pe (final)
            'צ': 18,  # Tzadi
            'ץ': 18,  # Tzadi (final)
            'ק': 19,  # Qof
            'ר': 20,  # Resh
            'ש': 21,  # Shin
            'ת': 22,  # Tav
        }


class HebrewSmallValueCalculator(GematriaCalculator):
    """Calculator for Hebrew Small Value (Mispar Katan / מספר קטן).
    
    Also known as Mispar Katan (מספר קטן) - "Small Number"
    
    This reduction method simplifies gematria values by removing zeros,
    reducing all values to single digits (1-9):
    - Units (1-9) remain unchanged: א(1), ב(2), ..., ט(9)
    - Tens (10-90) become: י(1), כ(2), ל(3), ..., צ(9)
    - Hundreds (100-400) become: ק(1), ר(2), ש(3), ת(4)
    
    Historical Context:
    This method is used in practical Kabbalah for quick calculations and is
    particularly useful when seeking the essential numerical essence of a word
    without the complexity of large numbers.
    
    Applications:
    - Rapid gematria calculations
    - Finding core numerical essence of words
    - Comparing words through their reduced values
    - Numerological interpretation in modern Kabbalah
    
    Example:
    שלום ("peace"):
    Standard: ש(300) + ל(30) + ו(6) + ם(40) = 376
    Small: ש(3) + ל(3) + ו(6) + ם(4) = 16
    
    Further reduced: 16 → 1 + 6 = 7
    
    אדם ("Adam/human"):
    Standard: א(1) + ד(4) + ם(40) = 45
    Small: א(1) + ד(4) + ם(4) = 9
    
    This reveals a more accessible numerical signature for meditation and study.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Hebrew (Small Value)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Hebrew letter-to-small-value mapping.
        
        Reduces standard values to single digits by removing zeros:
        - Aleph through Yod: 1-10 → 1-1 (10=1)
        - Kaf through Tzadi: 20-90 → 2-9
        - Qof through Tav: 100-400 → 1-4
        - Final forms use same reduction as regular forms
        
        Returns:
            Dictionary mapping Hebrew letters to their small values
        """
        return {
            # Aleph through Yod (1-10 → 1-1)
            'א': 1,   # Aleph (1)
            'ב': 2,   # Bet (2)
            'ג': 3,   # Gimel (3)
            'ד': 4,   # Dalet (4)
            'ה': 5,   # He (5)
            'ו': 6,   # Vav (6)
            'ז': 7,   # Zayin (7)
            'ח': 8,   # Het (8)
            'ט': 9,   # Tet (9)
            'י': 1,   # Yod (10 → 1)
            
            # Kaf through Tzadi (20-90 → 2-9)
            'כ': 2,   # Kaf (20 → 2)
            'ך': 2,   # Kaf (final)
            'ל': 3,   # Lamed (30 → 3)
            'מ': 4,   # Mem (40 → 4)
            'ם': 4,   # Mem (final)
            'נ': 5,   # Nun (50 → 5)
            'ן': 5,   # Nun (final)
            'ס': 6,   # Samekh (60 → 6)
            'ע': 7,   # Ayin (70 → 7)
            'פ': 8,   # Pe (80 → 8)
            'ף': 8,   # Pe (final)
            'צ': 9,   # Tzadi (90 → 9)
            'ץ': 9,   # Tzadi (final)
            
            # Qof through Tav (100-400 → 1-4)
            'ק': 1,   # Qof (100 → 1)
            'ר': 2,   # Resh (200 → 2)
            'ש': 3,   # Shin (300 → 3)
            'ת': 4,   # Tav (400 → 4)
        }


class HebrewAtBashCalculator(GematriaCalculator):
    """Calculator for Hebrew AtBash (אתב״ש) substitution cipher.
    
    Also known as AtBash (אתב״ש) - from aleph-tav-bet-shin
    
    This ancient Hebrew substitution cipher reverses the alphabet:
    - First letter (א Aleph) ↔ Last letter (ת Tav)
    - Second letter (ב Bet) ↔ Second-to-last (ש Shin)
    - Third letter (ג Gimel) ↔ Third-to-last (ר Resh)
    - And so on...
    
    The name "AtBash" comes from the first two pairs:
    א-ת (Aleph-Tav) and ב-ש (Bet-Shin)
    
    Historical Context:
    AtBash appears in the Hebrew Bible (Jeremiah 25:26, 51:41) where
    "Sheshach" (ששך) is an AtBash cipher for "Babel" (בבל). It's one of the
    oldest known encryption methods, dating back over 2,500 years.
    
    Applications:
    - Revealing hidden meanings in biblical text
    - Kabbalistic cryptography and secret teachings
    - Finding alternative interpretations of sacred words
    - Discovering concealed prophecies and mysteries
    
    Example:
    בבל (Babel):
    Standard: ב(2) + ב(2) + ל(30) = 34
    AtBash: ש(300) + ש(300) + כ(20) = 620 (ששך "Sheshach")
    
    This transformation reveals hidden layers of meaning, with the higher
    numerical value suggesting a deeper spiritual significance.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Hebrew (AtBash)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Hebrew letter-to-value mapping using AtBash substitution.
        
        AtBash reverses the alphabet:
        - Aleph (1st) ↔ Tav (22nd): א → ת (400)
        - Bet (2nd) ↔ Shin (21st): ב → ש (300)
        - Gimel (3rd) ↔ Resh (20th): ג → ר (200)
        - etc.
        
        Returns:
            Dictionary mapping Hebrew letters to their AtBash substitution values
        """
        # Standard values for the substituted letters
        standard_values = {
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6,
            'ז': 7, 'ח': 8, 'ט': 9, 'י': 10, 'כ': 20, 'ך': 20,
            'ל': 30, 'מ': 40, 'ם': 40, 'נ': 50, 'ן': 50, 'ס': 60,
            'ע': 70, 'פ': 80, 'ף': 80, 'צ': 90, 'ץ': 90,
            'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400
        }
        
        # AtBash substitution (reversed alphabet)
        return {
            'א': standard_values['ת'],   # Aleph → Tav (400)
            'ב': standard_values['ש'],   # Bet → Shin (300)
            'ג': standard_values['ר'],   # Gimel → Resh (200)
            'ד': standard_values['ק'],   # Dalet → Qof (100)
            'ה': standard_values['צ'],   # He → Tzadi (90)
            'ו': standard_values['פ'],   # Vav → Pe (80)
            'ז': standard_values['ע'],   # Zayin → Ayin (70)
            'ח': standard_values['ס'],   # Het → Samekh (60)
            'ט': standard_values['נ'],   # Tet → Nun (50)
            'י': standard_values['מ'],   # Yod → Mem (40)
            'כ': standard_values['ל'],   # Kaf → Lamed (30)
            'ך': standard_values['ל'],   # Kaf (final) → Lamed (30)
            'ל': standard_values['כ'],   # Lamed → Kaf (20)
            'מ': standard_values['י'],   # Mem → Yod (10)
            'ם': standard_values['י'],   # Mem (final) → Yod (10)
            'נ': standard_values['ט'],   # Nun → Tet (9)
            'ן': standard_values['ט'],   # Nun (final) → Tet (9)
            'ס': standard_values['ח'],   # Samekh → Het (8)
            'ע': standard_values['ז'],   # Ayin → Zayin (7)
            'פ': standard_values['ו'],   # Pe → Vav (6)
            'ף': standard_values['ו'],   # Pe (final) → Vav (6)
            'צ': standard_values['ה'],   # Tzadi → He (5)
            'ץ': standard_values['ה'],   # Tzadi (final) → He (5)
            'ק': standard_values['ד'],   # Qof → Dalet (4)
            'ר': standard_values['ג'],   # Resh → Gimel (3)
            'ש': standard_values['ב'],   # Shin → Bet (2)
            'ת': standard_values['א'],   # Tav → Aleph (1)
        }


class HebrewKolelCalculator(GematriaCalculator):
    """Calculator for Hebrew Kolel (מספר קולל) - adds number of letters.
    
    Also known as Mispar Kolel (מספר קולל) - "Collective Value"
    
    This method adds 1 for each letter to the standard gematria value,
    representing the idea that the whole is greater than the sum of its parts.
    The additional count acknowledges the "collective" nature of the word.
    
    Formula: Standard gematria value + number of letters
    
    Historical Context:
    Kolel is used in traditional Jewish gematria to account for the "unity"
    of a word - each letter contributes not just its value but also its
    presence. This method appears in classical Kabbalistic texts and is
    particularly significant in finding matches between related concepts.
    
    Applications:
    - **Bridging the Gap**: Connecting two concepts that are *almost* identical (off by 1), showing that they are essentially the same but separated by a thin veil (the *Kolel*).
    - **Inclusive Unity**: representing the "Whole" that contains the parts. Used when a word implies a group or a system.
    - **Correction of Deviation**: Accounting for slight transmission errors or "fuzziness" in the material manifestation of a spiritual concept.
    
    Example:
    תורה ("Torah"):
    Standard: ת(400) + ו(6) + ר(200) + ה(5) = 611
    Kolel: 611 + 4 letters = 615
    
    615 is significant because it equals the gematria of "mitzvot" (מצות),
    connecting Torah to the concept of commandments.
    
    אחד ("one"):
    Standard: 13
    Kolel: 13 + 3 letters = 16
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Hebrew (Kolel)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use standard Hebrew gematria values."""
        return HebrewGematriaCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate gematria value + number of letters (Kolel).
        
        Args:
            text: The Hebrew text to calculate
            
        Returns:
            Sum of letter values plus the count of letters
        """
        normalized = self.normalize_text(text)
        base_value = super().calculate(normalized)
        letter_count = len(normalized)
        return base_value + letter_count


class HebrewSquareCalculator(GematriaCalculator):
    """Calculator for Hebrew Square Value (Mispar Merubah / מספר מרובה).
    
    Also known as Mispar Bone'eh (מספר בונה) - "Building Number"
    
    This advanced mathematical method squares each letter's value before
    summing, amplifying the numerical significance exponentially.
    
    Formula: Σ(letter_value²)
    
    Historical Context:
    Square values appear in esoteric Kabbalistic texts as a way to magnify
    the spiritual power of sacred words. The squaring operation represents
    the "building" or "construction" of higher dimensional spiritual realities.
    
    Applications:
    - Advanced Kabbalistic numerology
    - Amplifying numerical significance of sacred names
    - Finding hidden mathematical patterns in text
    - Meditation on intensified spiritual energies
    
    Example:
    אב ("father"):
    Standard: א(1) + ב(2) = 3
    Square: א(1²=1) + ב(2²=4) = 5
    
    יהוה (YHWH):
    Standard: 26
    Square: י(10²=100) + ה(5²=25) + ו(6²=36) + ה(5²=25) = 186
    
    The dramatic increase in value represents the infinite expansion of the
    Divine Name's power and essence.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Hebrew (Square)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use standard Hebrew gematria values."""
        return HebrewGematriaCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate sum of squared letter values.
        
        Args:
            text: The Hebrew text to calculate
            
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


class HebrewCubeCalculator(GematriaCalculator):
    """Calculator for Hebrew Cube Value (Mispar Meshulash / מספר משולש).
    
    Also known as Mispar Meshulash (מספר משולש) - "Triangular/Tripled Number"
    
    This highly advanced method cubes each letter's value, representing
    the three-dimensional or three-fold nature of reality (physical,
    emotional, spiritual) in Kabbalistic thought.
    
    Formula: Σ(letter_value³)
    
    Historical Context:
    Cube values are found in the most esoteric Kabbalistic teachings,
    particularly those dealing with the three pillars of the Tree of Life
    and the three-dimensional structure of the universe.
    
    Applications:
    - Deep esoteric Kabbalistic study
    - Exploring three-dimensional spiritual realities
    - Finding profound numerical relationships
    - Meditation on the threefold nature of creation
    
    Example:
    אב ("father"):
    Standard: 3
    Square: 5
    Cube: א(1³=1) + ב(2³=8) = 9
    
    יהוה (YHWH):
    Standard: 26
    Square: 186
    Cube: י(10³=1000) + ה(5³=125) + ו(6³=216) + ה(5³=125) = 1,466
    
    The exponential increase reflects the infinite, multi-dimensional nature
    of the Divine Name across all levels of reality.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Hebrew (Cube)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use standard Hebrew gematria values."""
        return HebrewGematriaCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate sum of cubed letter values.
        
        Args:
            text: The Hebrew text to calculate
            
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


class HebrewTriangularCalculator(GematriaCalculator):
    """Calculator for Hebrew Triangular Value (Mispar Kidmi / מספר קדמי).
    
    Also known as Mispar Kidmi (מספר קדמי) - "Prior/Progressive Number"
    
    This method uses triangular numbers - the sum of all integers from 1 to n.
    For a letter with value n, its triangular number is: T(n) = n(n+1)/2
    
    Triangular numbers represent accumulation and progressive growth,
    symbolizing the building up of spiritual energy from the foundation.
    
    Formula: Σ(T(letter_value)) where T(n) = n(n+1)/2
    
    Historical Context:
    Triangular numbers appear in Pythagorean mathematics and were adopted
    into Kabbalah as representing the cumulative essence of a number. They
    symbolize progression from unity to multiplicity.
    
    Applications:
    - Finding cumulative spiritual significance
    - Exploring progressive numerical patterns
    - Kabbalistic meditation on growth and development
    - Mathematical analysis of sacred texts
    
    Example:
    אב ("father"):
    Standard: 3
    Triangular: T(1) + T(2) = 1 + 3 = 4
    
    יהוה (YHWH):
    Standard: 26
    Triangular: T(10)=55 + T(5)=15 + T(6)=21 + T(5)=15 = 106
    
    The triangular value 106 represents the cumulative, progressive
    revelation of the Divine Name through all levels.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Hebrew (Triangular)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use standard Hebrew gematria values."""
        return HebrewGematriaCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate sum of triangular numbers for each letter.
        
        Triangular number formula: T(n) = n(n+1)/2
        
        Args:
            text: The Hebrew text to calculate
            
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


class HebrewIntegralReducedCalculator(GematriaCalculator):
    """Calculator for Hebrew Integral Reduced Value (Mispar Mispari / מספר מספרי).
    
    Also known as Mispar Mispari (מספר מספרי) - "Number of Numbers"
    
    This reduction method sums the individual digits of each letter's value:
    - ש (300) becomes 3+0+0 = 3
    - ל (30) becomes 3+0 = 3
    - ו (6) remains 6
    - ם (40) becomes 4+0 = 4
    
    Formula: Σ(sum of digits of each letter value)
    
    Historical Context:
    Integral reduction is used in modern Kabbalistic numerology to find
    the "digital root" of words. This method reveals patterns that connect
    words sharing similar digit-sum structures.
    
    Applications:
    - Modern numerological analysis
    - Finding digital root connections between words
    - Simplified gematria for practical use
    - Revealing underlying numerical patterns
    
    Example:
    שלום ("peace"):
    Standard: ש(300) + ל(30) + ו(6) + ם(40) = 376
    Integral Reduced: 3 + 3 + 6 + 4 = 16
    Further reduced: 1 + 6 = 7
    
    יהוה (YHWH):
    Standard: 26
    Integral Reduced: 1 + 0 + 5 + 6 + 5 = 17
    (Note: The zero from 10 is included in the digit sum)
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Hebrew (Integral Reduced)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use standard Hebrew gematria values."""
        return HebrewGematriaCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate sum of digit sums for each letter value.
        
        Example: ש(300) → 3+0+0 = 3
        
        Args:
            text: The Hebrew text to calculate
            
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


class HebrewOrdinalSquareCalculator(GematriaCalculator):
    """Calculator for Hebrew Ordinal Square Value (Mispar Boneah Siduri / מספר בונה סידורי).
    
    Also known as Mispar Boneah Siduri (מספר בונה סידורי) - "Ordinal Building Number"
    
    This method combines two concepts:
    1. Ordinal values (letter positions 1-22)
    2. Square operation (position²)
    
    Formula: Σ(letter_position²)
    
    Historical Context:
    This hybrid method is found in modern Kabbalistic study, combining the
    simplicity of ordinal values with the amplification of squaring. It
    reveals patterns based on alphabetical structure rather than traditional
    numerical values.
    
    Applications:
    - Structural analysis of Hebrew words
    - Finding patterns in letter positions
    - Modern numerological calculations
    - Exploring positional relationships
    
    Example:
    אבג (Aleph-Bet-Gimel):
    Ordinal: 1 + 2 + 3 = 6
    Ordinal Square: 1² + 2² + 3² = 1 + 4 + 9 = 14
    
    יהוה (YHWH):
    Ordinal: 10 + 5 + 6 + 5 = 26
    Ordinal Square: 10² + 5² + 6² + 5² = 100 + 25 + 36 + 25 = 186
    
    This creates a different amplification than standard square values,
    emphasizing positional significance.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Hebrew (Ordinal Square)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """Use ordinal values (letter positions 1-22)."""
        return HebrewOrdinalCalculator()._initialize_mapping()
    
    def calculate(self, text: str) -> int:
        """
        Calculate sum of squared ordinal values.
        
        Args:
            text: The Hebrew text to calculate
            
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


class HebrewFullValueCalculator(GematriaCalculator):
    """Calculator for Hebrew Full Value without finals (Mispar Gadol / מספר גדול).
    
    Also known as Mispar Gadol (מספר גדול) - "Great Value"
    
    This method uses the gematria value of each letter's spelled-out name,
    but WITHOUT using final letter forms. For example:
    - א (Aleph) is spelled אלפ = 1 + 30 + 80 = 111 (using regular פ, not final ף)
    - ב (Bet) is spelled בית = 2 + 10 + 400 = 412
    
    Historical Context:
    This is the traditional "full spelling" method used in classical
    Kabbalistic texts before the sofit (final letter) variation became
    common. It represents the essential name-value of each letter.
    
    Applications:
    - Traditional Kabbalistic calculations
    - Finding letter-name equivalences
    - Comparing to Full Value with Finals
    - Classical mystical text analysis
    
    Example:
    The letter א (Aleph):
    Spelled: אלפ
    Value: א(1) + ל(30) + פ(80) = 111
    (Compare to 831 with finals)
    
    The word אב ("father"):
    א (111) + ב (412) = 523
    (Compare to 1,243 with finals)
    
    This creates significantly different numerical signatures,
    revealing alternate layers of meaning.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Hebrew (Full Value)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Map letters to their full spelling values WITHOUT final letters.
        
        Example: א = אלף = א(1) + ל(30) + פ(80) = 111
        """
        return {
            'א': 111,  # Aleph (ALPh) - אלף without final Pe = 1+30+80
            'ב': 412,  # Bet (BITh) - בית
            'ג': 83,   # Gimel (GMIL) - גמל
            'ד': 434,  # Dalet (DLTh) - דלת
            'ה': 6,    # He (HA) - הא
            'ו': 12,   # Vav (VV) - וו
            'ז': 67,   # Zayin (ZIN) - זין
            'ח': 418,  # Het (CITh) - חית
            'ט': 419,  # Tet (TITh) - טית
            'י': 20,   # Yod (IVD) - יוד
            'כ': 100,  # Kaf (KPh) - כף without final Pe = 20+80
            'ך': 100,  # Kaf (final)
            'ל': 74,   # Lamed (LMD) - למד
            'מ': 80,   # Mem (MM) - מם without final Mem = 40+40
            'ם': 80,   # Mem (final)
            'נ': 106,  # Nun (NVN) - נון without final Nun = 50+6+50
            'ן': 106,  # Nun (final)
            'ס': 120,  # Samekh (SMKh) - סמך without final Kaf = 60+40+20
            'ע': 130,  # Ayin (OIN) - עין without final Nun = 70+10+50
            'פ': 85,   # Pe (PH) - פה
            'ף': 85,   # Pe (final)
            'צ': 104,  # Tzadi (TzDI) - צדי
            'ץ': 104,  # Tzadi (final)
            'ק': 186,  # Qof (QVPh) - קוף without final Pe = 100+6+80
            'ר': 510,  # Resh (RISh) - ריש
            'ש': 360,  # Shin (ShIN) - שין without final Nun = 300+10+50
            'ת': 406,  # Tav (TV) - תו
        }


class HebrewAlbamCalculator(GematriaCalculator):
    """Calculator for Hebrew Albam (אלבם) substitution cipher.
    
    Also known as Albam (אלבם) - from aleph-lamed-bet-mem
    
    This ancient Hebrew substitution cipher pairs the first half of the
    alphabet with the second half:
    - א (Aleph, 1st) ↔ ל (Lamed, 12th)
    - ב (Bet, 2nd) ↔ מ (Mem, 13th)
    - ג (Gimel, 3rd) ↔ נ (Nun, 14th)
    - And so on through the alphabet...
    
    The name "Albam" comes from the first two pairs:
    א-ל (Aleph-Lamed) and ב-מ (Bet-Mem)
    
    Historical Context:
    Albam is mentioned in the Talmud and medieval Kabbalistic texts as one
    of the classical substitution ciphers alongside AtBash. It's used to
    reveal hidden teachings and alternate interpretations of sacred texts.
    
    Applications:
    - Discovering hidden meanings in Torah
    - Kabbalistic cryptography
    - Finding alternative numerical relationships
    - Exploring dual aspects of letters (first/second half of alphabet)
    
    Example:
    אבג (Aleph-Bet-Gimel):
    Standard: א(1) + ב(2) + ג(3) = 6
    Albam: ל(30) + מ(40) + נ(50) = 120 (למנ Lamed-Mem-Nun)
    
    This transformation reveals how concepts encoded in the first half of
    the alphabet relate to concepts in the second half, representing a
    reflection or complementary relationship.
    """
    
    @property
    def name(self) -> str:
        """Return the name of this gematria system."""
        return "Hebrew (Albam)"
    
    def _initialize_mapping(self) -> Dict[str, int]:
        """
        Initialize Hebrew letter-to-value mapping using Albam substitution.
        
        Albam pairs first half with second half:
        - Aleph (1st) ↔ Lamed (12th): א → ל (30)
        - Bet (2nd) ↔ Mem (13th): ב → מ (40)
        - etc.
        """
        standard_values = {
            'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6,
            'ז': 7, 'ח': 8, 'ט': 9, 'י': 10, 'כ': 20, 'ך': 20,
            'ל': 30, 'מ': 40, 'ם': 40, 'נ': 50, 'ן': 50, 'ס': 60,
            'ע': 70, 'פ': 80, 'ף': 80, 'צ': 90, 'ץ': 90,
            'ק': 100, 'ר': 200, 'ש': 300, 'ת': 400
        }
        
        # Albam substitution (first half pairs with second half)
        return {
            'א': standard_values['ל'],   # Aleph → Lamed (30)
            'ב': standard_values['מ'],   # Bet → Mem (40)
            'ג': standard_values['נ'],   # Gimel → Nun (50)
            'ד': standard_values['ס'],   # Dalet → Samekh (60)
            'ה': standard_values['ע'],   # He → Ayin (70)
            'ו': standard_values['פ'],   # Vav → Pe (80)
            'ז': standard_values['צ'],   # Zayin → Tzadi (90)
            'ח': standard_values['ק'],   # Het → Qof (100)
            'ט': standard_values['ר'],   # Tet → Resh (200)
            'י': standard_values['ש'],   # Yod → Shin (300)
            'כ': standard_values['ת'],   # Kaf → Tav (400)
            'ך': standard_values['ת'],   # Kaf (final) → Tav (400)
            'ל': standard_values['א'],   # Lamed → Aleph (1)
            'מ': standard_values['ב'],   # Mem → Bet (2)
            'ם': standard_values['ב'],   # Mem (final) → Bet (2)
            'נ': standard_values['ג'],   # Nun → Gimel (3)
            'ן': standard_values['ג'],   # Nun (final) → Gimel (3)
            'ס': standard_values['ד'],   # Samekh → Dalet (4)
            'ע': standard_values['ה'],   # Ayin → He (5)
            'פ': standard_values['ו'],   # Pe → Vav (6)
            'ף': standard_values['ו'],   # Pe (final) → Vav (6)
            'צ': standard_values['ז'],   # Tzadi → Zayin (7)
            'ץ': standard_values['ז'],   # Tzadi (final) → Zayin (7)
            'ק': standard_values['ח'],   # Qof → Het (8)
            'ר': standard_values['ט'],   # Resh → Tet (9)
            'ש': standard_values['י'],   # Shin → Yod (10)
            'ת': standard_values['כ'],   # Tav → Kaf (20)
        }