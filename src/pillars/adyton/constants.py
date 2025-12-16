"""
CONSTANTS OF THE ADYTON

"The measure of the Temple."
"""
from PyQt6.QtGui import QColor

# --- MEASUREMENTS (The Law of the Z'Bit) ---
Z_BIT_INCHES = 19.0
BLOCK_UNIT = 2 * Z_BIT_INCHES  # 38.0 inches (The Ashlar Base)

# --- WALL DIMENSIONS ---
# Width = number of blocks along the chord; Height = number of courses.
WALL_WIDTH_UNITS = 13  # Pillars per wall
WALL_HEIGHT_UNITS = 8  # Courses per wall

# Physical dimensions in inches
WALL_WIDTH_INCHES = WALL_WIDTH_UNITS * BLOCK_UNIT   # 494.0"
WALL_HEIGHT_INCHES = WALL_HEIGHT_UNITS * BLOCK_UNIT # 304.0"

# --- FRUSTUM GEOMETRY (Phi-based) ---
PHI = 1.61803398875
FRUSTUM_MARGIN = 2.0                     # 2-inch margin on the face
FRUSTUM_BASE = BLOCK_UNIT - FRUSTUM_MARGIN # 36.0" (Creates a visual gap between blocks)
FRUSTUM_TOP = BLOCK_UNIT / PHI           # ~23.48"
FRUSTUM_HEIGHT = BLOCK_UNIT / (PHI**2)   # ~14.52"

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
VOWEL_RING_COLORS = [
    QColor(22, 64, 133),
    QColor(32, 86, 153),
    QColor(42, 108, 170),
    QColor(52, 126, 186),
    QColor(64, 144, 199),
    QColor(76, 162, 210),
    QColor(88, 178, 220),
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
