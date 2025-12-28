"""
Kamea Grid View - The 2D Matrix Renderer.
A QGraphicsView-based visualization of the 27x27 Kamea grid with quadset highlighting and dimension filtering.
"""
import logging
import math
from typing import Dict, Tuple, Optional
from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsItem,
    QToolTip
)
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QPointF
from PyQt6.QtGui import (
    QBrush, QPen, QColor, QPainter, QRadialGradient, QFont,
    QMouseEvent, QTransform, QFontMetrics
)
from PyQt6.QtWidgets import QGraphicsSimpleTextItem
from ..models.kamea_cell import KameaCell
from ..services.kamea_grid_service import KameaGridService

logger = logging.getLogger(__name__)

class KameaCellItem(QGraphicsRectItem):
    """
    Visual representation of a single Kamea Cell.
    """
    def __init__(self, cell: KameaCell, size: float, base_color: QColor, tooltip_enabled: bool = True):
        super().__init__(0, 0, size, size)
        self.cell = cell
        self.tooltip_enabled = tooltip_enabled
        self.setPos(cell.x * size, -cell.y * size) # Invert Y for screen coords
        
        self.setAcceptHoverEvents(True)
        
        # Color Logic based on Family
        # Families: 
        # Color is now passed in from the service to support variants
        self.base_color = base_color
        
        # Default Brush
        self.setBrush(QBrush(self.base_color))
        self.setPen(QPen(Qt.GlobalColor.transparent))
        
        self.original_opacity = 0.8
        self.setOpacity(self.original_opacity)
        
        # Text Item
        self.text_item = QGraphicsSimpleTextItem(self)
        self.text_item.setBrush(QBrush(QColor("#ffffff")))
        self._update_text()
        
        # Highlight State
        self.is_highlighted = False
        self.highlight_pen = QPen(Qt.GlobalColor.transparent)

    def set_highlight(self, mode: str):
        """
        Sets the highlight mode for the cell.
        Args:
            mode: 'primary' (Gold Halo), 'sibling' (Cyan Halo), 'none' (Clear).
        """
        if mode == 'primary':
            self.setOpacity(1.0)
            self.highlight_pen = QPen(QColor("#FFD700")) # Gold
            self.highlight_pen.setWidthF(3.0)
            self.setPen(self.highlight_pen)
            self.is_highlighted = True
        elif mode == 'sibling':
            self.setOpacity(0.9)
            self.highlight_pen = QPen(QColor("#00FFFF")) # Cyan
            self.highlight_pen.setWidthF(2.0)
            self.setPen(self.highlight_pen)
            self.is_highlighted = True
        else: # none
            self.setOpacity(self.original_opacity)
            self.setPen(QPen(Qt.GlobalColor.transparent))
            self.is_highlighted = False
            
    def set_dimmed(self, dimmed: bool):
        """Dims the cell if filtered out."""
        if dimmed:
            self.setOpacity(0.05) # Very faint
            self.original_opacity = 0.05 # Store so hover restore works correctly
        else:
            self.setOpacity(0.8)
            self.original_opacity = 0.8

    def set_view_mode(self, mode: str):
        """Updates the text based on view mode ('decimal' or 'ternary')."""
        self.view_mode = mode
        self._update_text()

    def _update_text(self):
        """Redraws the text content."""
        if getattr(self, 'view_mode', 'decimal') == 'decimal':
            text = str(self.cell.decimal_value)
            font_size = 8
        else: # ternary
            text = self.cell.ternary_value
            font_size = 6
            
        self.text_item.setText(text)
        font = QFont("Arial", font_size)
        font.setBold(True)
        self.text_item.setFont(font)
        
        # Center Text
        rect = self.text_item.boundingRect()
        x_offset = (self.rect().width() - rect.width()) / 2
        y_offset = (self.rect().height() - rect.height()) / 2
        self.text_item.setPos(x_offset, y_offset)


    def hoverEnterEvent(self, event):
        self.setOpacity(1.0)
        # Glow Effect (simulated by brighter color or stroke)
        pen = QPen(QColor("#ffffff"))
        pen.setWidthF(2.0)
        self.setPen(pen)
        
        if self.tooltip_enabled:
            # Tooltip
            tooltip_text = (
                f"<b>Locator:</b> {self.cell.kamea_locator}<br>"
                f"<b>Coord:</b> ({self.cell.x}, {self.cell.y})<br>"
                f"<b>Ternary:</b> {self.cell.ternary_value}<br>"
                f"<b>Decimal:</b> {self.cell.decimal_value}<br>"
                f"<b>Family:</b> {self.cell.family_id}"
            )
            QToolTip.showText(event.screenPos(), tooltip_text)
            
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        if not self.is_highlighted:
            self.setOpacity(self.original_opacity)
            self.setPen(QPen(Qt.GlobalColor.transparent))
        else:
            # Restore highlight pen if highlighted
            self.setPen(self.highlight_pen)
            
        QToolTip.hideText()
        super().hoverLeaveEvent(event)
        
    def mousePressEvent(self, event):
        # Propagate to View
        # Standard QGraphicsItem doesn't automatically emit to scene/view
        # We can handle this in the scene or just call the view directly if we had a ref.
        # Better: Scene handles `selectionChanged`.
        # Simplest: manually trigger.
        super().mousePressEvent(event) 

class KameaGridView(QGraphicsView):
    """
    Cosmic Visualization of the Kamea Grid.
    """
    cell_selected = pyqtSignal(object) # Emit KameaCell

    def __init__(self, service: KameaGridService, parent=None):
        super().__init__(parent)
        self.service = service
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Graphic Settings
        self.setBackgroundBrush(QBrush(QColor("#050510"))) # Deep Space
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        self.CELL_SIZE = 40.0
        self.item_map = {}
        
        self.initialize_scene()
        self.scene.selectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self):
        """Handle cell selection to visualize Quadsets."""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            self._clear_highlights()
            return
            
        # We only care about the first/primary selection for the Quadset
        primary_item = selected_items[0]
        if not isinstance(primary_item, KameaCellItem):
            return
            
        self._highlight_quadset(primary_item)

    def _clear_highlights(self):
        """Clears all highlights."""
        for item in self.item_map.values():
            item.set_highlight('none')

    def _highlight_quadset(self, primary_item: KameaCellItem):
        """Visualizes the Quadset Physics."""
        self._clear_highlights()
        
        # Highlight Primary
        primary_item.set_highlight('primary')
        self.cell_selected.emit(primary_item.cell)
        
        # Get Quadset Members
        # The service returns cells, we need to look up items.
        quadset_cells = self.service.get_quadset(primary_item.cell.x, primary_item.cell.y)
        
        for cell in quadset_cells:
            # Skip if it's the primary itself (already highlighted)
            if cell.x == primary_item.cell.x and cell.y == primary_item.cell.y:
                continue
                
            item = self.item_map.get((cell.x, cell.y))
            if item:
                item.set_highlight('sibling')

    def set_dimension_filter(self, pyx_count: Optional[int]):
        """Filters the grid by Pyx Count (Dimensional Density)."""
        self._clear_highlights()
        
        for item in self.item_map.values():
            if pyx_count is None:
                # Show All
                item.set_dimmed(False)
            elif item.cell.pyx_count == pyx_count:
                # Match
                item.set_dimmed(False)
            else:
                # No Match - Dim it
                item.set_dimmed(True)

    def set_view_mode(self, mode: str):
        """Propagates view mode to all cells."""
        for item in self.item_map.values():
            item.set_view_mode(mode)

    def initialize_scene(self):
        """Builds the visual grid."""
        if not self.service._initialized:
            self.service.initialize()
            
        # Draw Grid
        grid_cells = self.service._grid

        
        # Determine tooltip strategy based on variant
        # Baphomet -> No Tooltips
        tooltip_enabled = (self.service.variant != "Baphomet")
        
        for coord, cell in grid_cells.items():
            base_color = self.service.get_cell_color(cell)
            item = KameaCellItem(cell, self.CELL_SIZE, base_color, tooltip_enabled=tooltip_enabled)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            self.scene.addItem(item)
            self.item_map[coord] = item
            
        # Center View
        self.centerOn(0, 0)
        
    def wheelEvent(self, event):
        """Smooth Zoom."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        self.scale(zoom_factor, zoom_factor)
