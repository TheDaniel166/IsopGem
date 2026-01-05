"""
Amun Sound Calculator - The Unified Meditative Sound Model.

Translates Ditrune values into sound parameters through the Three Principles:
    1. Pitch (Frequency) - from Ditrune position (1-728)
    2. Timbre (Waveform) - from Skin bigram (d1, d6)
    3. Entrainment (Pulse Rate) - from Body bigram (d2, d5)

Ditrune 0 is the Invisible Origin - no sound.
Ditrunes 1-728 map logarithmically to C0-C8 (16.35 Hz to 4186 Hz).

Philosophy:
    The number gives the form.
    The initiate gives the life.
"""
from dataclasses import dataclass
from typing import Dict, Optional

from ..services.ternary_service import TernaryService


# =============================================================================
# Core Constants
# =============================================================================

# Piano range (97 keys span C0 to C8)
FREQ_C0 = 16.35       # Hz - lowest audible
FREQ_C8 = 4186.0      # Hz - highest piano key

# Entrainment range (brainwave frequencies)
PULSE_THETA_LOW = 4.0   # Hz - Deep theta (trance)
PULSE_ALPHA_HIGH = 13.0  # Hz - High alpha (alert relaxation)


# =============================================================================
# The 9 Waveform Types (Timbre from Skin)
# =============================================================================
# d1 (first digit of skin) = Waveform family (0=Sine, 1=Triangle, 2=Sawtooth)
# d6 (second digit of skin) = Intensity within family (0=soft, 2=full)

@dataclass(frozen=True)
class WaveformSpec:
    """Specification for waveform synthesis."""
    name: str
    odd_harmonics: bool      # True = odd only (sine/triangle), False = all (saw)
    max_harmonic: int        # Number of harmonics (1-9)
    rolloff_exp: float       # Harmonic rolloff: 1/n^exp (higher = softer)


WAVEFORM_SPECS: Dict[str, WaveformSpec] = {
    # Sine family (d1=0): Only fundamental or near-sine
    '00': WaveformSpec('Pure Sine', odd_harmonics=True, max_harmonic=1, rolloff_exp=2.0),
    '01': WaveformSpec('Soft Sine', odd_harmonics=True, max_harmonic=2, rolloff_exp=2.5),
    '02': WaveformSpec('Warm Sine', odd_harmonics=True, max_harmonic=3, rolloff_exp=2.5),
    
    # Triangle family (d1=1): Odd harmonics with rolloff
    '10': WaveformSpec('Soft Triangle', odd_harmonics=True, max_harmonic=5, rolloff_exp=2.0),
    '11': WaveformSpec('Triangle', odd_harmonics=True, max_harmonic=7, rolloff_exp=2.0),
    '12': WaveformSpec('Bright Triangle', odd_harmonics=True, max_harmonic=9, rolloff_exp=1.8),
    
    # Sawtooth family (d1=2): All harmonics
    '20': WaveformSpec('Soft Sawtooth', odd_harmonics=False, max_harmonic=5, rolloff_exp=1.5),
    '21': WaveformSpec('Sawtooth', odd_harmonics=False, max_harmonic=7, rolloff_exp=1.2),
    '22': WaveformSpec('Full Sawtooth', odd_harmonics=False, max_harmonic=9, rolloff_exp=1.0),
}


# =============================================================================
# The 9 Entrainment Rates (Body bigram → Pulse Hz)
# =============================================================================
# Maps Body bigram to brainwave entrainment pulse rate

ENTRAINMENT_RATES: Dict[str, float] = {
    '00': 4.0,    # Deep Theta - trance
    '01': 5.0,    # Theta - deep meditation
    '02': 6.0,    # Theta - meditation
    '10': 7.0,    # Theta/Alpha border - relaxed awareness
    '11': 8.0,    # Low Alpha - calm, centered (neutral)
    '12': 10.0,   # Alpha - relaxed focus
    '20': 11.0,   # Alpha - light meditation
    '21': 12.0,   # High Alpha - alert relaxation
    '22': 13.0,   # Alpha/Beta border - focused, present
}


# =============================================================================
# SoundFrame: Output structure for synthesis
# =============================================================================

@dataclass
class SoundFrame:
    """Complete sound specification for one ditrune."""
    decimal: int              # Original ditrune (0-728)
    ternary: str              # 6-digit ternary string
    
    # The Three Principles
    frequency: float          # Pitch in Hz (0 for invisible, else C0-C8)
    waveform: WaveformSpec    # Timbre specification
    pulse_rate: float         # Entrainment rate in Hz
    
    # Derived bigrams
    skin: str                 # d1 + d6
    body: str                 # d2 + d5
    core: str                 # d3 + d4 (for reference)
    
    @property
    def is_audible(self) -> bool:
        """Whether this ditrune produces sound."""
        return self.decimal > 0


# =============================================================================
# Calculator
# =============================================================================

class AmunSoundCalculator:
    """
    Calculates Amun Sound parameters from Ditrunes.
    
    The Three Principles:
        1. Pitch = Ditrune position (1-728) → Frequency (C0-C8)
        2. Timbre = Skin (d1+d6) → Waveform (Sine→Triangle→Sawtooth)
        3. Entrainment = Body (d2+d5) → Pulse Rate (4-13 Hz)
    
    Ditrune 0 is invisible (no sound).
    """
    
    @staticmethod
    def ditrune_to_frequency(decimal: int) -> float:
        """
        Map ditrune (1-728) to frequency (C0-C8) logarithmically.
        
        Ditrune 0 = invisible (frequency 0).
        Ditrune 1 = C0 (16.35 Hz).
        Ditrune 728 = C8 (4186 Hz).
        """
        if decimal <= 0:
            return 0.0  # Invisible origin
        
        # Logarithmic mapping: 1 → C0, 728 → C8
        ratio = (decimal - 1) / 727  # 0.0 to 1.0
        frequency = FREQ_C0 * (FREQ_C8 / FREQ_C0) ** ratio
        
        return frequency
    
    @staticmethod
    def calculate_signature(ditrune: str) -> SoundFrame:
        """
        Calculate the complete sound signature for a Ditrune.
        
        Args:
            ditrune: 6-digit ternary string OR decimal integer.
        
        Returns:
            SoundFrame with all sound parameters.
        """
        # Handle decimal input
        if isinstance(ditrune, int):
            decimal = ditrune
            ditrune = TernaryService.decimal_to_ternary(decimal).zfill(6)
        else:
            # Validate ternary string
            if len(ditrune) != 6 or not all(c in '012' for c in ditrune):
                ditrune = '000000'
            decimal = int(ditrune, 3)
        
        # Extract bigrams
        d1, d2, d3, d4, d5, d6 = ditrune
        skin = d1 + d6    # Timbre
        body = d2 + d5    # Entrainment
        core = d3 + d4    # (for reference)
        
        # Calculate the Three Principles
        frequency = AmunSoundCalculator.ditrune_to_frequency(decimal)
        waveform = WAVEFORM_SPECS.get(skin, WAVEFORM_SPECS['11'])
        pulse_rate = ENTRAINMENT_RATES.get(body, ENTRAINMENT_RATES['11'])
        
        return SoundFrame(
            decimal=decimal,
            ternary=ditrune,
            frequency=frequency,
            waveform=waveform,
            pulse_rate=pulse_rate,
            skin=skin,
            body=body,
            core=core,
        )
    
    @staticmethod
    def calculate_signature_legacy(decimal_value: int) -> dict:
        """
        Legacy wrapper for backward compatibility with UI.
        
        Returns a dict with the old-style structure expected by ternary_sound_widget.
        """
        ditrune = TernaryService.decimal_to_ternary(decimal_value).zfill(6)
        frame = AmunSoundCalculator.calculate_signature(ditrune)
        
        # Build legacy response matching UI expectations
        skin = ditrune[0] + ditrune[5]
        body = ditrune[1] + ditrune[4]
        core = ditrune[2] + ditrune[3]
        
        return {
            # Meta section (required by UI)
            'meta': {
                'decimal': decimal_value,
                'ternary': ditrune,
            },
            # Channels keyed by number (required by UI)
            'channels': {
                1: {
                    'bigram': skin,
                    'desc': 'Timbre (Skin)',
                    'output': frame.waveform.name,
                },
                2: {
                    'bigram': body,
                    'desc': 'Entrainment (Body)',
                    'output': f'{frame.pulse_rate:.1f} Hz',
                },
                3: {
                    'bigram': core,
                    'desc': 'Core',
                    'output': f'{frame.frequency:.1f} Hz',
                },
            },
            # Parameters section (for visualizer compatibility)
            'parameters': {
                'family_name': frame.waveform.name.split()[0],
                'color_hex': '#86868e',  # Neutral color for now
                # Visualizer keys
                'red_val': skin,         # For polygon sides calculation
                'layers': frame.waveform.max_harmonic,  # Number of harmonics as layers
                'attack': 1.0 / frame.pulse_rate if frame.pulse_rate > 0 else 0.5,  # Inverse of pulse rate
            },
            # New unified values
            'frame': frame,
            'frequency': frame.frequency,
            'waveform': frame.waveform.name,
            'pulse_rate': frame.pulse_rate,
        }


# =============================================================================
# The 97 Piano Keys
# =============================================================================
# Ditrunes that align with the 97 piano key frequencies

THE_97_KEYS = [
    1, 9, 16, 24, 31, 39, 46, 54, 62, 69, 77, 84, 92, 99, 107, 115, 122, 130,
    137, 145, 152, 160, 168, 175, 183, 190, 198, 205, 213, 221, 228, 236, 243,
    251, 258, 266, 274, 281, 289, 296, 304, 311, 319, 327, 334, 342, 349, 357,
    364, 372, 380, 387, 395, 402, 410, 418, 425, 433, 440, 448, 455, 463, 471,
    478, 486, 493, 501, 508, 516, 524, 531, 539, 546, 554, 561, 569, 577, 584,
    592, 599, 607, 614, 622, 630, 637, 645, 652, 660, 667, 675, 683, 690, 698,
    705, 713, 720, 728
]


# =============================================================================
# Backward Compatibility Aliases
# =============================================================================
# For UI code still using old names

# StateFrame alias (UI imports this name)
StateFrame = SoundFrame

# Legacy scale definitions (UI references SCALE_AXIS)
SCALE_AXIS = [
    364,  # Axis center (111111)
    455,  # Radiance
    546,  # Mass  
    637,  # Motion
    728,  # Veil (end)
    637,  # Motion (return)
    546,  # Mass
    455,  # Radiance
    364,  # Axis (return to center)
]

# Legacy force definitions for backward compatibility
BIGRAM_FORCES = ENTRAINMENT_RATES  # Maps to pulse rates now
