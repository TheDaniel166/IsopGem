"""
Amun Sound Calculator - The Symphonic Engine.
Translates Ditrune values (0-728) into sound signatures using a 3-channel RGB folding system.
Each channel maps to musical parameters: Pitch (Red), Dynamics (Green), and Harmonic Density (Blue).
"""
from typing import Dict, Any, Tuple
from ..services.ternary_service import TernaryService
from ..services.baphomet_color_service import BaphometColorService
from .symphony_config import SYMPHONY_FAMILIES, SymphonyNucleation

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
    
    # Red Channel: Orchestral Register (Fundamental Frequency)
    RED_MAP = {
        '00': {'note': 'C2', 'freq': 65.41,  'desc': "Double Basses (Subtlety)"},
        '01': {'note': 'G2', 'freq': 98.00,  'desc': "Cellos (Low)"},
        '02': {'note': 'C3', 'freq': 130.81, 'desc': "Cellos (High)"},
        '10': {'note': 'G3', 'freq': 196.00, 'desc': "Violas (Warmth)"},
        '11': {'note': 'C4', 'freq': 261.63, 'desc': "Middle C (Foundation)"},
        '12': {'note': 'G4', 'freq': 392.00, 'desc': "Violins (Mid)"},
        '20': {'note': 'C5', 'freq': 523.25, 'desc': "Violins (High)"},
        '21': {'note': 'G5', 'freq': 783.99, 'desc': "Flutes (Bright)"},
        '22': {'note': 'C6', 'freq': 1046.50, 'desc': "Piccolo/Soprano (Radiance)"}
    }

    # Green Channel: Articulation (Envelope)
    GREEN_MAP = {
        '00': {'atk': 2.0, 'rel': 3.0, 'desc': "Cinematic Swell (Slow)"},
        '01': {'atk': 1.5, 'rel': 2.5, 'desc': "Molto Legato"},
        '02': {'atk': 1.0, 'rel': 2.0, 'desc': "Legato"},
        '10': {'atk': 0.5, 'rel': 1.5, 'desc': "Espressivo"},
        '11': {'atk': 0.1, 'rel': 1.0, 'desc': "Moderato (Natural)"},
        '12': {'atk': 0.05, 'rel': 0.8, 'desc': "Detache"},
        '20': {'atk': 0.02, 'rel': 0.5, 'desc': "Staccato"},
        '21': {'atk': 0.01, 'rel': 0.3, 'desc': "Spiccato"},
        '22': {'atk': 0.005, 'rel': 0.1, 'desc': "Marcato (Sharp Impact)"}
    }

    # Blue Channel: Harmonic Density (The "Symphony" Factor)
    BLUE_MAP = {
        '00': {'layers': 1, 'detune': 0,  'desc': "Solo Voice (Pure)"},
        '01': {'layers': 2, 'detune': 5,  'desc': "Duet (Intimate)"},
        '02': {'layers': 3, 'detune': 8,  'desc': "Trio (Warm)"},
        '10': {'layers': 4, 'detune': 10, 'desc': "Chamber Ensemble"},
        '11': {'layers': 5, 'detune': 12, 'desc': "Small Orchestra (Chordal)"},
        '12': {'layers': 6, 'detune': 15, 'desc': "Full Strings"},
        '20': {'layers': 8, 'detune': 20, 'desc': "Symphonic Tutti"},
        '21': {'layers': 10, 'detune': 25, 'desc': "Grand Orchestra"},
        '22': {'layers': 12, 'detune': 30, 'desc': "Cosmic Choir (Massive)"}
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
        ternary_string = base_ternary
        # Removed reversal [::-1] to align with MSB-first (Top-Down) logic 
        # where index 0 is Line 6 and index 5 is Line 1.
        # This matches the User's example: 210120 -> L6=2, L1=0.
        # Pair R (L1 & L6) logic below uses [0] + [5], so it effectively creates "TopBottom" pair?
        # User said "Red (Lines 1 & 6): 2 and 0 -> Bigram 20".
        # If [0]='2' and [5]='0', then [0]+[5] = "20". Correct.
        
        # Red (Pitch)
        # We need the Bigram Key (e.g. "00").
        # My ternary_string is "210120" (Top-Down).
        # Red: Lines 1 & 6. Indices [0] and [5] (Wait, if [0] is Line 6 and [5] is Line 1)
        # The JS says: "Red = s[0] + s[5]".
        # My code previously said Red Pair = L1 & L6.
        # If I use ternary_string from decimal_to_ternary (MSB first):
        # s[0] is MSB (Line 6). s[5] is LSB (Line 1).
        # JS: "Red = s[0] + s[5]".
        # Example 210120 -> s[0]=2, s[5]=0 -> "20".
        # This matches my previous logic.
        
        red_key = ternary_string[0] + ternary_string[5]
        green_key = ternary_string[1] + ternary_string[4]
        blue_key = ternary_string[2] + ternary_string[3]
        
        # Lookups with Fallback to '00'
        r_data = self.RED_MAP.get(red_key, self.RED_MAP['00'])
        g_data = self.GREEN_MAP.get(green_key, self.GREEN_MAP['00'])
        b_data = self.BLUE_MAP.get(blue_key, self.BLUE_MAP['00'])
        
        # Symphony Family Mapping (Blue Channel is Core/Instrument)
        family = SYMPHONY_FAMILIES.get(blue_key, SYMPHONY_FAMILIES['00'])
        
        # Audio Parameters for Synthesis
        params = {
            'freq': r_data['freq'],
            'attack': g_data['atk'],
            'release': g_data['rel'],
            'layers': b_data['layers'],
            'detune': b_data['detune'],
            
            # Symphony Archetype Data
            'family_id': family.id,
            'family_name': family.name,
            'instrument': family.instrument,
            'audio_type': family.audio_type,
            'color_hex': family.color_hex,
            
            # Metadata for UI
            'red_desc': r_data['desc'],
            'green_desc': g_data['desc'],
            'blue_desc': f"{family.instrument} ({family.name})", # Override with Symphony Info
            'red_val': red_key, 
            'green_val': green_key, 
            'blue_val': blue_key
        }

        # Construct Nucleation Object
        # Coordinates mapping is complex in Quadset service, 
        # but for Audio we can infer from Region logic or just default to (0,0) for now if not available.
        # Ideally, we should receive Bigram logic from input.
        # But 'decimal_value' -> Ternary (Length 6).
        # We can implement minimal logic here or just pass (0,0).
        # To get proper panning, we need X/Y.
        # Let's define simple mapping for now using TernaryService logic via a placeholder or calc.
        # Actually, Kamea region logic is better handled by Grid Service. 
        # AmunSoundCalculator is low level. 
        # We'll default coords to (0,0) unless we want to replicate Grid logic here.
        
        # Skin Value is Outer Bigram.
        skin_key = ternary_string[0] + ternary_string[5] # Wait, standard model says Skin is Outer?
        # My earlier RED logic uses s[0]+s[5]. 
        # SymphonyNucleation expects 'skin' string.
        
        nucleation = SymphonyNucleation(
            ditrune=ternary_string,
            core=blue_key,       # Center Bigram (Blue/Soul)
            body=green_key,      # Middle Bigram (Green/Role) - Wait, previous mapping might be diff?
            skin=red_key,        # Outer Bigram (Red/State)
            # Map Hierarchy Class based on Equality
            hierarchy_class='Prime' if (blue_key == green_key == red_key) else \
                            'Acolyte' if (blue_key == green_key) else 'Temple',
            # Pyx Count (Zeros)
            pyx_count=ternary_string.count('0'),
            coordinates=(0, 0) # Placeholder
        )

        # Structure return data
        return {
            "meta": {
                "decimal": decimal_value,
                "ternary": ternary_string
            },
            "parameters": params,
            "nucleation": nucleation, # Added for Kamea Service
            "channels": {
                1: {
                    "role": "Red (Pitch)",
                    "value": red_key,
                    "output": f"{r_data['note']} ({r_data['freq']} Hz)",
                    "desc": r_data['desc']
                },
                2: {
                    "role": "Green (Dynamics)",
                    "value": green_key,
                    "output": f"Atk {g_data['atk']}s",
                    "desc": g_data['desc']
                },
                3: {
                    "role": "Blue (Soul)",
                    "value": blue_key,
                    "output": family.name,
                    "desc": f"{family.instrument} [{family.audio_type}]"
                }
            }
        }

