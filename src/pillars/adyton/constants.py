"""
CONSTANTS OF THE ADYTON

"The measure of the Temple."
"""
from PyQt6.QtGui import QColor

# --- ADYTON FOUNDATION DIMENSIONS ---
# Side lengths for the Floor Heptagons
PERIMETER_SIDE_LENGTH = 185.0
KATALYSIS_SIDE_LENGTH = 166.0
VOWEL_DIFFERENTIAL = PERIMETER_SIDE_LENGTH - KATALYSIS_SIDE_LENGTH # 19

# --- MEASUREMENTS (The Law of the Z'Bit) ---
Z_BIT_INCHES = 19.0  # The Corner Chord (The differential bit)
# The wall has 13 pillars (columns). Its total width equals the KATALYSIS_SIDE_LENGTH.
BLOCK_UNIT = KATALYSIS_SIDE_LENGTH / 13.0  # 166 / 13 ≈ 12.769 units

# --- WALL DIMENSIONS ---
# Width = number of blocks along the chord; Height = number of courses.
WALL_WIDTH_UNITS = 13  # Pillars per wall
WALL_HEIGHT_UNITS = 8  # Courses per wall (104 cells total)

# Physical dimensions in units
WALL_WIDTH_INCHES = KATALYSIS_SIDE_LENGTH              # 166.0
WALL_HEIGHT_INCHES = WALL_HEIGHT_UNITS * BLOCK_UNIT    # ~102.15
 
# --- FRUSTUM GEOMETRY (Phi-based) ---
PHI = 1.61803398875
FRUSTUM_MARGIN = 2.0                     # 2-inch margin on the face
FRUSTUM_BASE = BLOCK_UNIT - FRUSTUM_MARGIN # ~12.23" (Creates a visual gap between blocks)
FRUSTUM_TOP = BLOCK_UNIT / PHI           # ~8.79"
FRUSTUM_HEIGHT = BLOCK_UNIT / (PHI**2)   # ~5.43"

# --- COLORS (The Amun Map - Placeholders) ---
COLOR_SATURN = QColor(50, 50, 55)
COLOR_SOL = QColor(255, 215, 0)
COLOR_MERCURY = QColor(200, 100, 0)
COLOR_LUNA = QColor(220, 220, 255)
COLOR_VENUS = QColor(0, 255, 150)
COLOR_JUPPITER = QColor(50, 0, 150)
COLOR_MARS = QColor(200, 0, 0)
COLOR_ARGON = QColor(170, 130, 255)  # Argon discharge glow (lavender-violet)
COLOR_KRYPTON = QColor(150, 130, 255)  # Krypton discharge glow (pale violet-blue)
COLOR_MAAT_BLUE = QColor(97, 97, 248)
COLOR_GOLD = QColor(255, 215, 0)    # Alchemical Gold (Vibrant)
COLOR_SILVER = QColor(230, 232, 250) # Sacred Silver (Vibrantly light)

# Vowel Ring Colors based on Phi ratios of 97: values 60, 97, 194, 254
VOWEL_RING_COLORS = [
    QColor(254, 97, 60),   # Alpha (Fire/Red-ish)
    QColor(254, 194, 97),  # Epsilon (Deeper yellow/orange)
    QColor(194, 254, 97),  # Eta (Vibrant Green-yellow)
    QColor(97, 254, 194),  # Iota (Cyan-green)
    QColor(60, 194, 254),  # Omicron (Sky Blue)
    QColor(97, 60, 254),   # Upsilon (Violet-Blue)
    QColor(194, 97, 254),  # Omega (Magenta-Violet)
]

# Frustum face indexing (per-block local faces on the wall interior)
FRUSTUM_FACE_TOP = 1
FRUSTUM_FACE_RIGHT = 2
FRUSTUM_FACE_BOTTOM = 3
FRUSTUM_FACE_LEFT = 4
FRUSTUM_FACE_CENTER = 5
FRUSTUM_FACE_ORDER = (
    FRUSTUM_FACE_TOP,
    FRUSTUM_FACE_RIGHT,
    FRUSTUM_FACE_BOTTOM,
    FRUSTUM_FACE_LEFT,
    FRUSTUM_FACE_CENTER,
)

# Planetary order (rotated so Venus occupies the middle wall): Sun, Mercury, Moon, Venus, Jupiter, Mars, Saturn
# Overridden to a uniform krypton discharge hue per request
WALL_COLORS = [
    COLOR_KRYPTON,
    COLOR_KRYPTON,
    COLOR_KRYPTON,
    COLOR_KRYPTON,
    COLOR_KRYPTON,
    COLOR_KRYPTON,
    COLOR_KRYPTON,
]
