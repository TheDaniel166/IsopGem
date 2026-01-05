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
    font_family: str = None # Optional custom font

# Reusable English Rows
ENGLISH_ROWS = [
    ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
    ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
    ['z', 'x', 'c', 'v', 'b', 'n', 'm']
]

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

TRIGRAMMATON_LAYOUT = KeyboardLayout(
    name="trigrammaton",
    display_name="Trigrammaton",
    rows=ENGLISH_ROWS,
    has_shift=True,
    font_family="Trigrammaton"
)

ASTRONOMICON_LAYOUT = KeyboardLayout(
    name="astronomicon",
    display_name="Astronomicon",
    rows=ENGLISH_ROWS,
    has_shift=True,
    font_family="Astronomicon"
)

ARABIC_LAYOUT = KeyboardLayout(
    name="arabic",
    display_name="Arabic",
    rows=[
        ['ض', 'ص', 'ث', 'ق', 'ف', 'غ', 'ع', 'ه', 'خ', 'ح', 'ج', 'د'],
        ['ش', 'س', 'ي', 'ب', 'ل', 'ا', 'ت', 'ن', 'م', 'ك', 'ط'],
        ['ظ', 'ز', 'و', 'ة', 'ى', 'ر', 'ذ', 'ء', 'ئ']
    ]
)

SANSKRIT_LAYOUT = KeyboardLayout(
    name="sanskrit",
    display_name="Sanskrit",
    rows=[
        ['औ', 'ऐ', 'आ', 'ई', 'ऊ', 'भ', 'ङ', 'घ', 'ध', 'झ', 'ढ', 'ञ'],
        ['ओ', 'ए', 'अ', 'इ', 'उ', 'फ', 'र', 'क', 'त', 'च', 'ट', 'व'],
        ['ं','ः','म','न','ण','ल','स','य','श','ष','प','द','ज','ड','ख','थ','छ','ठ','ग','ब','ह']
    ]
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
    "arabic": ARABIC_LAYOUT,
    "sanskrit": SANSKRIT_LAYOUT,
    "trigrammaton": TRIGRAMMATON_LAYOUT,
    "astronomicon": ASTRONOMICON_LAYOUT,
    "special": SPECIAL_LAYOUT,
    "esoteric": ESOTERIC_LAYOUT
}
