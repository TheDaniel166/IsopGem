"""Frustum detail popup dialog - shows top-down 2D view of a frustum with glyphs."""
from dataclasses import dataclass
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt6.QtCore import QPointF, QRectF

from pillars.adyton.services.frustum_color_service import FrustumColorService
from shared.services.tq.ternary_service import TernaryService
from shared.services.tq.baphomet_color_service import BaphometColorService


@dataclass
class FrustumFaceData:
    """Data for a single frustum face."""
    color: QColor
    glyph: str
    letter: str
    trigram_dec: int


class FrustumCanvas(QWidget):
    """Canvas widget that draws the top-down 2D frustum view."""

    def __init__(
        self,
        decimal_value: int,
        ternary_str: str,
        top_face: FrustumFaceData,
        right_face: FrustumFaceData,
        bottom_face: FrustumFaceData,
        left_face: FrustumFaceData,
        center_color: QColor,
        parent=None,
    ):
        """
          init   logic.
        
        Args:
            decimal_value: Description of decimal_value.
            ternary_str: Description of ternary_str.
            top_face: Description of top_face.
            right_face: Description of right_face.
            bottom_face: Description of bottom_face.
            left_face: Description of left_face.
            center_color: Description of center_color.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.decimal_value = decimal_value
        self.ternary_str = ternary_str
        self.top_face = top_face
        self.right_face = right_face
        self.bottom_face = bottom_face
        self.left_face = left_face
        self.center_color = center_color
        self.setMinimumSize(280, 280)

    def paintEvent(self, event):  # type: ignore[reportIncompatibleMethodOverride, reportMissingParameterType, reportUnknownParameterType]
        """
        Paintevent logic.
        
        Args:
            event: Description of event.
        
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        margin = 20
        size = min(w, h) - 2 * margin
        
        # Center the drawing
        cx = w / 2
        cy = h / 2

        # Outer square (base of frustum)
        outer_half = size / 2
        # Inner square (top of frustum - smaller)
        inner_half = size / 4

        # Define the four trapezoid faces
        # Top face (pointing up)
        self._draw_trapezoid_face(
            painter,
            QPointF(cx - outer_half, cy - outer_half),  # outer left
            QPointF(cx + outer_half, cy - outer_half),  # outer right
            QPointF(cx + inner_half, cy - inner_half),  # inner right
            QPointF(cx - inner_half, cy - inner_half),  # inner left
            self.top_face,
        )

        # Right face
        self._draw_trapezoid_face(
            painter,
            QPointF(cx + outer_half, cy - outer_half),  # outer top
            QPointF(cx + outer_half, cy + outer_half),  # outer bottom
            QPointF(cx + inner_half, cy + inner_half),  # inner bottom
            QPointF(cx + inner_half, cy - inner_half),  # inner top
            self.right_face,
        )

        # Bottom face
        self._draw_trapezoid_face(
            painter,
            QPointF(cx + outer_half, cy + outer_half),  # outer right
            QPointF(cx - outer_half, cy + outer_half),  # outer left
            QPointF(cx - inner_half, cy + inner_half),  # inner left
            QPointF(cx + inner_half, cy + inner_half),  # inner right
            self.bottom_face,
        )

        # Left face
        self._draw_trapezoid_face(
            painter,
            QPointF(cx - outer_half, cy + outer_half),  # outer bottom
            QPointF(cx - outer_half, cy - outer_half),  # outer top
            QPointF(cx - inner_half, cy - inner_half),  # inner top
            QPointF(cx - inner_half, cy + inner_half),  # inner bottom
            self.left_face,
        )

        # Center rectangle (top of frustum)
        center_rect = QRectF(
            cx - inner_half, cy - inner_half,
            inner_half * 2, inner_half * 2
        )
        # Use setBrush + drawRect for proper fill
        painter.setBrush(QBrush(self.center_color))
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawRect(center_rect)

        # Draw decimal value in center
        painter.setPen(QPen(QColor(0, 0, 0)))
        font = QFont("DejaVu Sans", 14, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(center_rect, Qt.AlignmentFlag.AlignCenter, str(self.decimal_value))

        # Draw ternary below decimal
        if self.ternary_str:
            ternary_rect = QRectF(
                cx - inner_half, cy,
                inner_half * 2, inner_half
            )
            small_font = QFont("DejaVu Sans", 9)
            painter.setFont(small_font)
            painter.drawText(ternary_rect, Qt.AlignmentFlag.AlignCenter, self.ternary_str)

    def _draw_trapezoid_face(
        self,
        painter: QPainter,
        p1: QPointF,
        p2: QPointF,
        p3: QPointF,
        p4: QPointF,
        face_data: FrustumFaceData,
    ):
        """Draw a trapezoid face with color and glyph."""
        polygon = QPolygonF([p1, p2, p3, p4])
        
        # Fill with face color
        painter.setBrush(QBrush(face_data.color))
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawPolygon(polygon)

        # Calculate center of trapezoid for glyph
        center_x = (p1.x() + p2.x() + p3.x() + p4.x()) / 4
        center_y = (p1.y() + p2.y() + p3.y() + p4.y()) / 4

        # Draw glyph
        if face_data.glyph:
            # Use contrasting color for text
            brightness = (face_data.color.red() * 299 + 
                         face_data.color.green() * 587 + 
                         face_data.color.blue() * 114) / 1000
            text_color = QColor(0, 0, 0) if brightness > 128 else QColor(255, 255, 255)
            
            painter.setPen(QPen(text_color))
            font = QFont("DejaVu Sans", 18, QFont.Weight.Bold)
            painter.setFont(font)
            
            # Adjust position for the glyph  
            text_rect = QRectF(center_x - 20, center_y - 15, 40, 30)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, face_data.glyph)


class FrustumDetailPopup(QDialog):
    """Popup dialog showing frustum details with 2D top-down view."""

    def __init__(
        self,
        wall_index: int,
        row: int,
        col: int,
        decimal_value: int,
        parent=None,
    ):
        """
          init   logic.
        
        Args:
            wall_index: Description of wall_index.
            row: Description of row.
            col: Description of col.
            decimal_value: Description of decimal_value.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.wall_index = wall_index
        self.row = row
        self.col = col
        self.decimal_value = decimal_value
        self.service = FrustumColorService()
        
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(f"Frustum [{self.row + 1}, {self.col + 1}] - Value: {self.decimal_value}")
        self.setMinimumSize(320, 380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = QLabel(f"Wall {self.wall_index + 1} • Row {self.row + 1} • Col {self.col + 1}")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Get face data
        ternary = TernaryService.decimal_to_ternary(self.decimal_value)
        ternary_padded = ternary.rjust(6, "0") if not ternary.startswith("-") else ternary

        # Parse trigrams for top/bottom faces
        if len(ternary_padded) >= 6 and not ternary_padded.startswith("-"):
            top_trigram = ternary_padded[:3]
            bottom_trigram = ternary_padded[3:]
            top_dec = TernaryService.ternary_to_decimal(top_trigram)
            bottom_dec = TernaryService.ternary_to_decimal(bottom_trigram)
        else:
            top_dec = 0
            bottom_dec = 0

        # Get colors and glyphs for each face
        top_color = self.service._trigram_map.get(top_dec, QColor("#000000"))
        bottom_color = self.service._trigram_map.get(bottom_dec, QColor("#000000"))
        right_color = self.service.get_side_color(self.wall_index, self.row, self.col, 2)  # FRUSTUM_FACE_RIGHT
        left_color = self.service.get_side_color(self.wall_index, self.row, self.col, 4)  # FRUSTUM_FACE_LEFT

        # Get glyphs
        top_glyph = self.service.get_trigram_glyph(top_dec)
        bottom_glyph = self.service.get_trigram_glyph(bottom_dec)
        # For right/left faces we need to find the trigram used
        # Right = zodiac, Left = planet - we need their decimal values
        # For now use letters as placeholders
        top_letter = self.service.get_trigram_letter(top_dec)
        bottom_letter = self.service.get_trigram_letter(bottom_dec)

        top_face = FrustumFaceData(top_color, top_glyph, top_letter, top_dec)
        bottom_face = FrustumFaceData(bottom_color, bottom_glyph, bottom_letter, bottom_dec)
        
        # Right and left faces use zodiac/planet codes from service
        right_trigram_dec = self.service.get_right_face_trigram_code(self.wall_index, self.col)
        left_trigram_dec = self.service.get_left_face_trigram_code(self.wall_index, self.row)
        
        right_glyph = self.service.get_trigram_glyph(right_trigram_dec)
        right_letter = self.service.get_trigram_letter(right_trigram_dec)
        left_glyph = self.service.get_trigram_glyph(left_trigram_dec)
        left_letter = self.service.get_trigram_letter(left_trigram_dec)

        right_face = FrustumFaceData(right_color, right_glyph, right_letter, right_trigram_dec)
        left_face = FrustumFaceData(left_color, left_glyph, left_letter, left_trigram_dec)

        # Center color - use BaphometColorService directly with ternary
        center_color = BaphometColorService.resolve_color(ternary_padded)

        # Canvas
        canvas = FrustumCanvas(
            self.decimal_value,
            ternary_padded,
            top_face,
            right_face,
            bottom_face,
            left_face,
            center_color,
        )
        layout.addWidget(canvas)

        # Info label
        info = QLabel(
            f"Decimal: {self.decimal_value}\n"
            f"Ternary: {ternary_padded}\n"
            f"Top Trigram: {top_dec} | Bottom Trigram: {bottom_dec}"
        )
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
