from typing import Dict, Any, Tuple
from ..services.ternary_service import TernaryService

class AmunSoundCalculator:
    """
    Calculates the Amun Sound Signature from a Ditrune (0-728).
    
    System Logic:
    1. Input: Decimal Integer (0-728).
    2. Conversion: 6-digit Ternary String.
    3. Folding: 3 Channels from concentric pairs.
        - Ch1: Line 1 (Bottom, index 0) & Line 6 (Top, index 5)
        - Ch2: Line 2 (index 1) & Line 5 (index 4)
        - Ch3: Line 3 (index 2) & Line 4 (index 3)
    4. Bigram Value: (LowerLine * 3) + UpperLine.
    5. Ratios: Mapped from Bigram Value (0-8).
    """
    
    BASE_FREQUENCY = 97.0
    
    # Mapping Bigram Value (0-8) to (Ratio, Description)
    # 0 (0-0): Ratio 1.0 ("Base Void") - Modified from 0.0 to ensure audibility
    # 1 (0-1): Ratio 1.0 ("Unison")
    # 2 (0-2): Ratio 1.125 ("Major 2nd")
    RATIO_MAP = {
        0: (1.0, "Base Void"),
        1: (1.0, "Unison"),
        2: (1.125, "Major 2nd"),
        3: (1.25, "Major 3rd"),
        4: (1.333, "Perfect 4th"),
        5: (1.5, "Perfect 5th"),
        6: (1.666, "Major 6th"),
        7: (1.875, "Minor 7th"),
        8: (2.0, "Octave")
    }

    # Custom Mapping from (Lower, Upper) pair to Bigram Value
    # As per user specification:
    # (0,0)->0, (0,1)->1, (0,2)->2
    # (1,0)->3, (1,1)->5, (1,2)->6  <-- Deviation from base-3 math
    # (2,0)->4, (2,1)->7, (2,2)->8  <-- Deviation from base-3 math
    BIGRAM_LOOKUP = {
        (0, 0): 0, (0, 1): 1, (0, 2): 2,
        (1, 0): 3, (1, 1): 5, (1, 2): 6,
        (2, 0): 4, (2, 1): 7, (2, 2): 8
    }

    # Octave Multipliers based on Ch1 Bigram (The 9-Octave Ladder)
    # 0: Sub-Bass (Earth Core) - 24.25Hz
    # 1: Bass - 48.5Hz
    # 2: Root - 97Hz
    # 3: Tenor - 194Hz
    # 4: Alto - 388Hz
    # 5: Soprano - 776Hz
    # 6: Presence - 1552Hz
    # 7: Brilliance - 3104Hz
    # 8: Radiance - 6208Hz
    OCTAVE_MAP = {
        0: (0.25, "Sub-Bass"),
        1: (0.5, "Bass"),
        2: (1.0, "Root"),
        3: (2.0, "Tenor"),
        4: (4.0, "Alto"),
        5: (8.0, "Soprano"),
        6: (16.0, "Presence"),
        7: (32.0, "Brilliance"),
        8: (64.0, "Radiance")
    }

    def calculate_signature(self, decimal_value: int) -> Dict[str, Any]:
        """
        Calculate the full sound signature for a given Ditrune value.
        
        Args:
            decimal_value: Integer between 0-728.
            
        Returns:
            Dictionary containing structure, channels, and summary.
        """
        # Validate Input
        if not isinstance(decimal_value, int) or not (0 <= decimal_value <= 728):
            raise ValueError("Input must be an integer between 0 and 728.")
            
        # Step A: Input Conversion
        # Default conversion gives MSB at index 0.
        # We want Line 1 (Index 0) to be the Bottom/Foundation (LSD).
        # So we reverse the string.
        base_ternary = TernaryService.decimal_to_ternary(decimal_value).zfill(6)
        ternary_string = base_ternary[::-1]
        
        # Step B & C: Channel Mapping and Bigram Calculation
        # The ternary string indices: 0 (Line 1/Bottom) to 5 (Line 6/Top)
        # Ch1 (Container): Line 1 & Line 6 -> indices 0 and 5
        # Ch2 (Pitch): Line 2 & Line 5 -> indices 1 and 4
        # Ch3 (Rhythm): Line 3 & Line 4 -> indices 2 and 3
        
        # Note: Spec says "LowerLine * 3 + UpperLine"
        # For Ch1: Lower is Line 1 (idx 0), Upper is Line 6 (idx 5)
        ch1_pair = (int(ternary_string[0]), int(ternary_string[5]))
        ch2_pair = (int(ternary_string[1]), int(ternary_string[4]))
        ch3_pair = (int(ternary_string[2]), int(ternary_string[3]))
        
        ch1_val = self._calculate_bigram_value(ch1_pair[0], ch1_pair[1])
        ch2_val = self._calculate_bigram_value(ch2_pair[0], ch2_pair[1])
        ch3_val = self._calculate_bigram_value(ch3_pair[0], ch3_pair[1])
        
        # Step D & E: Audio Parameter Lookup and Output Generation
        ch1_ratio, ch1_desc = self.RATIO_MAP[ch1_val]
        ch2_ratio, ch2_desc = self.RATIO_MAP[ch2_val]
        ch3_ratio, ch3_desc = self.RATIO_MAP[ch3_val]
        
        # Ch1 Output: Interval Name + "Width" (container metaphor)
        # Using the description as the base, e.g., "Major 2nd Width"
        ch1_output = f"{ch1_desc} Width"
        
        # Map Ch1 Ratio to Amplitude Factor (0.2 to 1.0)
        # This allows the "Container" to shape the volume.
        # ensure it's never fully silent if Ch2 is active, unless ratio is 0?
        # Let's map 0-2 ratio to 0.4-1.0 range for better audibility.
        ch1_amp = 0.4 + (ch1_ratio * 0.3)
        
        # Calculate Octave Plane based on Ch1 Bigram (The 9-Octave Ladder)
        octave_mult, plane_name = self.OCTAVE_MAP.get(ch1_val, (1.0, "Root"))
        
        # Ch2 Output: Calculated Frequency (Base * Ratio * Octave)
        ch2_freq = (self.BASE_FREQUENCY * ch2_ratio) * octave_mult
        
        # Ch3 Output: Calculated Modulation Rate
        ch3_rate = ch2_ratio * 1.0 # Wait, spec says "Ratio * 1.0" for Ch3. 
                                   # "Ch3 Output: Calculated Modulation Rate in Hz (Ratio * 1.0)."
                                   # It refers to the ratio of Ch3? Or Ch2? 
                                   # Logic implies it's the ratio derived from Ch3's bigram.
        ch3_rate = ch3_ratio * 1.0

        return {
            "meta": {
                "decimal": decimal_value,
                "ternary": ternary_string
            },
            "channels": {
                1: {
                    "role": "Container",
                    "pair": ch1_pair, # (Bottom, Top)
                    "bigram_value": ch1_val,
                    "ratio": ch1_ratio,
                    "interval": ch1_desc,
                    "output": ch1_output,
                    "output_amp": ch1_amp,
                    "octave_plane": plane_name
                },
                2: {
                    "role": "Pitch",
                    "pair": ch2_pair,
                    "bigram_value": ch2_val,
                    "ratio": ch2_ratio,
                    "interval": ch2_desc,
                    "output_freq": ch2_freq
                },
                3: {
                    "role": "Rhythm",
                    "pair": ch3_pair,
                    "bigram_value": ch3_val,
                    "ratio": ch3_ratio,
                    "interval": ch3_desc,
                    "output_rate": ch3_rate
                }
            }
        }

    def _calculate_bigram_value(self, lower: int, upper: int) -> int:
        """Calculate Bigram Value using custom lookup."""
        return self.BIGRAM_LOOKUP.get((lower, upper), 0)
