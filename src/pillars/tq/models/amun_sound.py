from typing import Dict, Any, Tuple
from ..services.ternary_service import TernaryService
from ..services.baphomet_color_service import BaphometColorService

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
    
    
    # Base Frequency for C2 (Low Bass)
    BASE_FREQ_C2 = 65.41
    
    # 9-State Timbre Values (Blue Channel)
    # Val 0   (00): Void -> sine
    # Val 37  (01): Deep -> sine_sub
    # Val 60  (02): Soft -> triangle
    # Val 97  (10): Float -> chorus
    # Val 134 (11): Balance -> square
    # Val 157 (12): Singing -> vibrato
    # Val 194 (20): Assert -> sawtooth
    # Val 231 (21): Tension -> dissonant
    # Val 254 (22): Fire -> noise
    TIMBRE_THRESHOLDS = [
        (0, 'sine'),
        (37, 'sine_sub'),
        (60, 'triangle'),
        (97, 'chorus'),
        (134, 'square'),
        (157, 'vibrato'),
        (194, 'sawtooth'),
        (231, 'dissonant'),
        (254, 'noise')
    ]

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
        ternary_string = base_ternary
        # Removed reversal [::-1] to align with MSB-first (Top-Down) logic 
        # where index 0 is Line 6 and index 5 is Line 1.
        # This matches the User's example: 210120 -> L6=2, L1=0.
        # Pair R (L1 & L6) logic below uses [0] + [5], so it effectively creates "TopBottom" pair?
        # User said "Red (Lines 1 & 6): 2 and 0 -> Bigram 20".
        # If [0]='2' and [5]='0', then [0]+[5] = "20". Correct.
        
        # Step B: Get Bigram Strings (Red, Green, Blue) from pairs
        # Red (Outer): Line 1 (0) & Line 6 (5)
        # Green (Inner): Line 2 (1) & Line 5 (4)
        # Blue (Core): Line 3 (2) & Line 4 (3)
        
        red_pair = ternary_string[0] + ternary_string[5]
        green_pair = ternary_string[1] + ternary_string[4]
        blue_pair = ternary_string[2] + ternary_string[3]
        
        # Step C: Get "Step Values" (0-254) from Baphomet Map
        red_val = BaphometColorService.STEP_MAP.get(red_pair, 0)
        green_val = BaphometColorService.STEP_MAP.get(green_pair, 0)
        blue_val = BaphometColorService.STEP_MAP.get(blue_pair, 0)
        
        # 1. Red -> PITCH (C2 to C6)
        # Range 0-254 maps to 4 octaves (2^0 to 2^4)
        # C2 = 65.41 Hz
        # Freq = Base * 2^( (val/254) * 4 )
        pitch_exponent = (red_val / 254.0) * 4.0
        pitch_freq = self.BASE_FREQ_C2 * (2.0 ** pitch_exponent)
        
        # 2. Green -> DYNAMICS (Amplitude)
        # Range 0-254 maps to 0.1 to 1.0 (Constraint applied)
        dynamics_amp = 0.1 + (green_val / 254.0) * 0.9
        
        # 3. Blue -> TIMBRE (Waveform) - 9 State Palette
        # We find the closest defined timbre state or use ranges.
        # User defined specific Step Values. We can use a closest-match or threshold approach.
        # Let's uses ranges based on midpoints between the values.
        # 0..18 -> sine
        # 19..48 -> sine_sub
        # 49..78 -> triangle
        # 79..115 -> chorus
        # 116..145 -> square
        # 146..175 -> vibrato
        # 176..212 -> sawtooth
        # 213..242 -> dissonant
        # 243..254 -> noise
        
        waveform = 'sine' # Default
        if blue_val < 19: waveform = 'sine'
        elif blue_val < 49: waveform = 'sine_sub'
        elif blue_val < 79: waveform = 'triangle'
        elif blue_val < 116: waveform = 'chorus'
        elif blue_val < 146: waveform = 'square'
        elif blue_val < 176: waveform = 'vibrato'
        elif blue_val < 213: waveform = 'sawtooth'
        elif blue_val < 243: waveform = 'dissonant'
        else: waveform = 'noise'

        # Structure return data
        return {
            "meta": {
                "decimal": decimal_value,
                "ternary": ternary_string
            },
            "parameters": {
                "red_value": red_val,
                "green_value": green_val,
                "blue_value": blue_val,
                "pitch_freq": pitch_freq,
                "dynamics_amp": dynamics_amp,
                "waveform": waveform
            },
            # Keeping legacy struct key for compatibility, but flattened
            "channels": {
                1: {"role": "Pitch (Red)", "value": red_val, "output": f"{pitch_freq:.2f} Hz"},
                2: {"role": "Dynamics (Green)", "value": green_val, "output": f"{dynamics_amp:.2f}"},
                3: {"role": "Timbre (Blue)", "value": blue_val, "output": waveform}
            }
        }


