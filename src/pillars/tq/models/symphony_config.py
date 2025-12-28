"""
Symphony Configuration - The 9 Orchestral Archetypes.
Defines the Family mappings, audio synthesis constants, and nucleation transport objects for the Amun Sound Engine.
"""
from dataclasses import dataclass
from typing import Dict

@dataclass
class SymphonyFamily:
    """
    Symphony Family class definition.
    
    """
    id: int
    name: str
    color_hex: str
    instrument: str
    audio_type: str
    # Frequency multipliers for harmony (Prime, Acolyte, Temple)
    detune_acolyte: tuple = (-0.05, 0, 0.05)
    detune_temple: tuple = (0, 2**(4/12)-1, 2**(7/12)-1) # Major Triad

# The 9 Orchestral Archetypes
SYMPHONY_FAMILIES: Dict[str, SymphonyFamily] = {
    '00': SymphonyFamily(0, 'Void', '#2a2a2a', 'Cosmic Breath', 'Ambient'),
    '01': SymphonyFamily(1, 'Pulse', '#7f1d1d', 'Taiko & Sub', 'Percussive'),
    '02': SymphonyFamily(2, 'Recoil', '#c2410c', 'String Ensemble', 'Sustained'),
    '10': SymphonyFamily(3, 'Projector', '#854d0e', 'Cinematic Brass', 'Brassy'),
    '11': SymphonyFamily(4, 'Monolith', '#365314', 'Cathedral Organ', 'Additive'),
    '12': SymphonyFamily(5, 'Weaver', '#064e3b', 'Woodwinds', 'Reedy'),
    '20': SymphonyFamily(6, 'Receiver', '#0e7490', 'Spectral Choir', 'Formant'),
    '21': SymphonyFamily(7, 'Splicer', '#1e3a8a', 'Crystalline Pluck', 'Plucked'),
    '22': SymphonyFamily(8, 'Abyss', '#581c87', 'Dark Matter Drone', 'Bass')
}

# Physics Constants (Shared between Standard and Grand Editions)
# C2 to C8 Base Frequencies
OCTAVE_FREQUENCIES = [65.41, 130.81, 261.63, 523.25, 1046.50, 2093.00, 4186.00]

# Just Intonation-ish Scale Ratios [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8, 2]
# Using decimal approx from reference
SCALE_RATIOS = [1, 1.125, 1.25, 1.333, 1.5, 1.666, 1.875, 2, 2.25]

@dataclass
class SymphonyNucleation:
    """Transport object for audio synthesis parameters."""
    ditrune: str
    core: str       # Determines Instrument
    body: str       # Determines Harmony Class
    skin: str       # Determines Pitch (Scale Degree)
    pyx_count: int  # Determines Octave
    hierarchy_class: str # Prime, Acolyte, Temple
    coordinates: tuple # (x, y) for Panning