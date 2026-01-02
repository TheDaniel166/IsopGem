"""Shared Substrate Widget to paint background textures."""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPixmap
from PyQt6.QtCore import Qt
from shared.ui.theme import COLORS

class SubstrateWidget(QWidget):
    """Widget that paints a background image scaled to fill the entire widget."""
    
    def __init__(self, image_path: str, parent=None):
        """
          init   logic.
        
        Args:
            image_path: Description of image_path.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self._pixmap = QPixmap(image_path)
        self._bg_color = QColor(COLORS['background'])
    
    def paintEvent(self, event):
        """
        Paintevent logic.
        
        Args:
            event: Description of event.
        
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        # Fill with background color first
        painter.fillRect(self.rect(), self._bg_color)
        
        # Scale pixmap to fill widget (aspect fill)
        if not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            # Center the scaled pixmap
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
