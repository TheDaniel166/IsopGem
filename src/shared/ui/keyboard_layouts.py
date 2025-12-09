"""
Keyboard layout definitions for the Virtual Keyboard.
Separating data from UI logic to reduce complexity.
"""
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class KeyboardLayout:
    """Definition of a virtual keyboard layout."""
    name: str
    display_name: str
    rows: List[List[str]]
    has_shift: bool = False
    is_esoteric: bool = False

# Layout Definitions
HEBREW_LAYOUT = KeyboardLayout(
    name="hebrew",
    display_name="Hebrew",
    rows=[
        ['ק', 'ר', 'א', 'ט', 'ו', 'ן', 'ם', 'פ'],
        ['ש', 'ד', 'ג', 'כ', 'ע', 'י', 'ח', 'ל', 'ך', 'ף'],
        ['ז', 'ס', 'ב', 'ה', 'נ', 'מ', 'צ', 'ת', 'ץ'],
    ]
)

GREEK_LAYOUT = KeyboardLayout(
    name="greek",
    display_name="Greek",
    rows=[
        ['ς', 'ε', 'ρ', 'τ', 'υ', 'θ', 'ι', 'ο', 'π'],
        ['α', 'σ', 'δ', 'φ', 'γ', 'η', 'ξ', 'κ', 'λ'],
        ['ζ', 'χ', 'ψ', 'ω', 'β', 'ν', 'μ'],
    ],
    has_shift=True
)

SPECIAL_LAYOUT = KeyboardLayout(
    name="special",
    display_name="Special",
    rows=[
        ['Å', '<', '>', '→', '↓', '↑'],
        ['×', '°', '∞', '≈', '±', '•']
    ]
)

ESOTERIC_LAYOUT = KeyboardLayout(
    name="esoteric",
    display_name="Esoteric",
    rows=[
        # Zodiac
        ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'],
        # Planets (+ Chiron)
        ['☉', '☾', '☿', '♀', '♂', '♃', '♄', '♅', '♆', '♇', '⚷'],
        # Elements / Alchemy / Misc
        ['🜂', '🜄', '🜁', '🜃', '∞', '∆', '∇', '★', '☆']
    ],
    is_esoteric=True
)

# Registry
LAYOUTS: Dict[str, KeyboardLayout] = {
    "hebrew": HEBREW_LAYOUT,
    "greek": GREEK_LAYOUT,
    "special": SPECIAL_LAYOUT,
    "esoteric": ESOTERIC_LAYOUT
}
