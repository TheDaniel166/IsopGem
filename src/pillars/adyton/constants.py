"""
CONSTANTS OF THE ADYTON

"The measure of the Temple."
"""
from PyQt6.QtGui import QColor

# --- MEASUREMENTS (The Law of the Z'Bit) ---
Z_BIT_INCHES = 19.0
BLOCK_UNIT = 2 * Z_BIT_INCHES  # 38.0 inches (The Ashlar Base)

# --- WALL DIMENSIONS ---
WALL_WIDTH_UNITS = 8   # Pillars per wall
WALL_HEIGHT_UNITS = 13 # Courses per wall

# Physical dimensions in inches
WALL_WIDTH_INCHES = WALL_WIDTH_UNITS * BLOCK_UNIT   # 304.0"
WALL_HEIGHT_INCHES = WALL_HEIGHT_UNITS * BLOCK_UNIT # 494.0"

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

WALL_COLORS = [
    COLOR_SATURN, COLOR_SOL, COLOR_MERCURY, COLOR_LUNA,
    COLOR_VENUS, COLOR_JUPPITER, COLOR_MARS
]
