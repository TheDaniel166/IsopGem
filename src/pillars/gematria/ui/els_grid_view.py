"""ELS Grid View - Zoomable, pannable letter matrix visualization.

Inspired by the InfiniteCanvasView pattern for graph-paper style display.
"""
from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QBrush, QColor, QPen, QFont, QWheelEvent
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ELSGridView(QGraphicsView):
    """
    Zoomable, pannable letter grid for ELS visualization.
    
    Each letter occupies a fixed-size cell on a graph-paper grid.
    Supports highlighting sequences and centering on specific cells.
    """
    
    cell_clicked = pyqtSignal(int, int)  # row, col
    
    CELL_SIZE = 30  # Pixels per cell
    MIN_ZOOM = 0.1
    MAX_ZOOM = 4.0
    
    # Theme colors
    GRID_COLOR = QColor("#E2E8F0")
    CELL_BG = QColor("#FFFFFF")
    LETTER_COLOR = QColor("#1E293B")
    HIGHLIGHT_COLORS = [
        QColor(124, 58, 237, 100),   # Purple
        QColor(59, 130, 246, 100),   # Blue
        QColor(16, 185, 129, 100),   # Green
        QColor(245, 158, 11, 100),   # Amber
        QColor(239, 68, 68, 100),    # Red
    ]
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        
        # View settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        # Grid state
        self._letters = ""
        self._columns = 0
        self._rows = 0
        self._zoom_factor = 1.0
        self._cell_items: List[QGraphicsRectItem] = []
        self._text_items: List[QGraphicsTextItem] = []
        self._highlight_items: List[QGraphicsRectItem] = []
        
        # Font for letters
        self._font = QFont("Courier New", 14)
        self._font.setBold(True)
        
        self._scene.setBackgroundBrush(QBrush(QColor("#F8FAFC")))
    
    def set_grid(self, letters: str, columns: int):
        """
        Populate the grid with letters.
        
        Args:
            letters: String of letters (stripped, no spaces)
            columns: Number of columns in the grid
        """
        self._letters = letters
        self._columns = columns
        self._rows = (len(letters) + columns - 1) // columns if columns > 0 else 0
        
        self._rebuild_grid()
        logger.info(f"ELS grid set: {len(letters)} letters, {columns}×{self._rows}")
    
    def _rebuild_grid(self):
        """Rebuild the entire grid visualization."""
        # Clear existing
        self._scene.clear()
        self._cell_items.clear()
        self._text_items.clear()
        self._highlight_items.clear()
        
        if not self._letters or self._columns <= 0:
            return
        
        pen = QPen(self.GRID_COLOR, 1)
        brush = QBrush(self.CELL_BG)
        
        for i, char in enumerate(self._letters):
            row = i // self._columns
            col = i % self._columns
            
            x = col * self.CELL_SIZE
            y = row * self.CELL_SIZE
            
            # Cell background
            cell = self._scene.addRect(
                x, y, self.CELL_SIZE, self.CELL_SIZE,
                pen, brush
            )
            self._cell_items.append(cell)
            
            # Letter text
            text = self._scene.addText(char, self._font)
            text.setDefaultTextColor(self.LETTER_COLOR)
            
            # Center text in cell
            text_rect = text.boundingRect()
            text_x = x + (self.CELL_SIZE - text_rect.width()) / 2
            text_y = y + (self.CELL_SIZE - text_rect.height()) / 2
            text.setPos(text_x, text_y)
            
            self._text_items.append(text)
        
        # Set scene rect
        self._scene.setSceneRect(
            0, 0,
            self._columns * self.CELL_SIZE,
            self._rows * self.CELL_SIZE
        )
    
    def highlight_sequence(self, positions: List[int], color_index: int = 0):
        """
        Highlight cells at given positions.
        
        Args:
            positions: List of linear positions in the text
            color_index: Index into HIGHLIGHT_COLORS
        """
        color = self.HIGHLIGHT_COLORS[color_index % len(self.HIGHLIGHT_COLORS)]
        
        for pos in positions:
            if 0 <= pos < len(self._letters):
                row = pos // self._columns
                col = pos % self._columns
                
                x = col * self.CELL_SIZE
                y = row * self.CELL_SIZE
                
                highlight = self._scene.addRect(
                    x + 2, y + 2,
                    self.CELL_SIZE - 4, self.CELL_SIZE - 4,
                    QPen(color.darker(150), 2),
                    QBrush(color)
                )
                highlight.setZValue(10)  # Above cells
                self._highlight_items.append(highlight)
    
    def clear_highlights(self):
        """Remove all highlight overlays."""
        for item in self._highlight_items:
            self._scene.removeItem(item)
        self._highlight_items.clear()
    
    def center_on_cell(self, row: int, col: int):
        """
        Center the view on a specific cell.
        
        Args:
            row: Row index (0-based)
            col: Column index (0-based)
        """
        x = (col + 0.5) * self.CELL_SIZE
        y = (row + 0.5) * self.CELL_SIZE
        self.centerOn(x, y)
    
    def center_on_position(self, pos: int):
        """Center view on a linear position."""
        if self._columns > 0 and 0 <= pos < len(self._letters):
            row = pos // self._columns
            col = pos % self._columns
            self.center_on_cell(row, col)
    
    def get_zoom(self) -> float:
        """Get current zoom factor."""
        return self._zoom_factor
    
    def set_zoom(self, factor: float):
        """Set absolute zoom factor."""
        factor = max(self.MIN_ZOOM, min(self.MAX_ZOOM, factor))
        scale = factor / self._zoom_factor
        self._zoom_factor = factor
        self.scale(scale, scale)
    
    def zoom_in(self):
        """Zoom in by 25%."""
        self.set_zoom(self._zoom_factor * 1.25)
    
    def zoom_out(self):
        """Zoom out by 25%."""
        self.set_zoom(self._zoom_factor / 1.25)
    
    def zoom_reset(self):
        """Reset to 100% zoom."""
        self.set_zoom(1.0)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming (with Ctrl) or scrolling."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)