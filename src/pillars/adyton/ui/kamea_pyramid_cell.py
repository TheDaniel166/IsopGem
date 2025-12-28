"""
Kamea Pyramid Cell - The 2D Frustum Widget.
A flattened top-down representation of a truncated pyramid with 4 trapezoidal sides and a central cap.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QColor, QPolygon, QBrush, QPen
from PyQt6.QtCore import Qt, QPoint, QSize, pyqtSignal

class KameaPyramidCell(QWidget):
    """
    A 2D Visualization of the "Flattened Truncated Pyramid" (Adyton Block).
    
    Visual Structure (Top-Down):
    -----------------------------
    | \   Top (Trapezoid)     / |
    |   \                   /   |
    |     \ --------------- /     |
    | Left |    Cap (Sq)   | Rght |
    | (Trap)|   Value       |(Trap)|
    |     / --------------- \     |
    |   /                   \   |
    | /   Bottom (Trapezoid)  \ |
    -----------------------------
    """
    
    clicked = pyqtSignal()
    
    def __init__(self, ditrune: str, decimal_value: int, size: int = 60, parent=None):
        super().__init__(parent)
        self.ditrune = ditrune
        self.decimal_value = decimal_value
        self.setFixedSize(size, size)
        
        # Colors (Default Style matching Adyton Dark Stone)
        self.color_base = QColor("#2A2A2A")
        self.color_cap = QColor("#404040")
        
        # Side Colors (Defaults)
        self.color_top = QColor("#333333")
        self.color_bottom = QColor("#222222")
        self.color_left = QColor("#282828")
        self.color_right = QColor("#1f1f1f")
        
        # Hover state
        self.is_hovered = False
        self.is_selected = False

    def set_side_colors(self, top: QColor, bottom: QColor, left: QColor, right: QColor):
        self.color_top = top
        self.color_bottom = bottom
        self.color_left = left
        self.color_right = right
        self.update()

    def set_cap_color(self, color: QColor):
        self.color_cap = color
        self.update()

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.update()

    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Geometry Constants
        margin = 0 # No margin for seamless tiling
        cap_ratio = 0.4  # Cap is 40% of the width
        
        # Outer Rect
        outer_rect = self.rect()
        x0, y0 = outer_rect.left(), outer_rect.top()
        x1, y1 = outer_rect.right(), outer_rect.bottom()
        
        # Inner Rect (Cap)
        cap_w = int(w * cap_ratio)
        cap_h = int(h * cap_ratio)
        cx = (x0 + x1) // 2
        cy = (y0 + y1) // 2
        
        ix0 = cx - cap_w // 2
        ix1 = cx + cap_w // 2
        iy0 = cy - cap_h // 2
        iy1 = cy + cap_h // 2
        
        # --- Draw Sides (Trapezoids) ---
        
        # TOP Side
        # Points: (x0, y0), (x1, y0), (ix1, iy0), (ix0, iy0)
        top_poly = QPolygon([
            QPoint(x0, y0),
            QPoint(x1, y0),
            QPoint(ix1, iy0),
            QPoint(ix0, iy0)
        ])
        painter.setBrush(QBrush(self.color_top))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(top_poly)
        
        # BOTTOM Side
        # Points: (x0, y1), (x1, y1), (ix1, iy1), (ix0, iy1)
        bottom_poly = QPolygon([
            QPoint(x0, y1),
            QPoint(x1, y1),
            QPoint(ix1, iy1),
            QPoint(ix0, iy1)
        ])
        painter.setBrush(QBrush(self.color_bottom))
        painter.drawPolygon(bottom_poly)
        
        # LEFT Side
        # Points: (x0, y0), (ix0, iy0), (ix0, iy1), (x0, y1)
        left_poly = QPolygon([
            QPoint(x0, y0),
            QPoint(ix0, iy0),
            QPoint(ix0, iy1),
            QPoint(x0, y1)
        ])
        painter.setBrush(QBrush(self.color_left))
        painter.drawPolygon(left_poly)

        # RIGHT Side
        # Points: (x1, y0), (ix1, iy0), (ix1, iy1), (x1, y1)
        right_poly = QPolygon([
            QPoint(x1, y0),
            QPoint(ix1, iy0),
            QPoint(ix1, iy1),
            QPoint(x1, y1)
        ])
        painter.setBrush(QBrush(self.color_right))
        painter.drawPolygon(right_poly)
        
        # --- Draw Cap (Center Square) ---
        cap_color = self.color_cap
        if self.is_hovered:
            cap_color = cap_color.lighter(130)
            
        painter.setBrush(QBrush(cap_color))
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.drawRect(ix0, iy0, cap_w, cap_h)
        
        # --- Draw Text ---
        painter.setPen(QColor("#FFFFFF"))
        font = painter.font()
        font.setPixelSize(10)
        font.setBold(True)
        painter.setFont(font)
        
        # Determine what to show (Decimal or Ditrune logic could go here)
        # For small cells, show fuzzy dots or small numbers
        text = str(self.decimal_value)
        if w > 50:
             # Standard display
             pass
             
        painter.drawText(ix0, iy0, cap_w, cap_h, Qt.AlignmentFlag.AlignCenter, text)
        
        
        # Draw Border if selected
        if self.is_selected:
             painter.setBrush(Qt.BrushStyle.NoBrush)
             pen = QPen(QColor("#00FFFF"), 2) # Cyan highlight
             painter.setPen(pen)
             painter.drawRect(outer_rect.adjusted(1,1,-1,-1)) # Adjust to draw inside

