from PyQt5.QtWidgets import QGraphicsView, QMenu
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from .items import GeometryPoint, GeometryLine

class GeometryView(QGraphicsView):
    """View for handling user interaction with the geometry scene."""
    
    def __init__(self, scene):
        super().__init__(scene)
        self.setup_view_properties()
        self.setup_interaction()
        
        # View state
        self.drawing_mode = True
        self.zoom_factor = 1.15
        self.last_mouse_pos = None
        self.selection_distance = 20
        self.panning = False
        self.last_pan_point = None
        
    def setup_view_properties(self):
        """Configure view display properties."""
        # Enable antialiasing for smoother drawing
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # Enable scrollbars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Set anchor points for transformations
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
        # Set scene rect to be large enough
        self.setSceneRect(-2000, -2000, 4000, 4000)
        
        # Set minimum size
        self.setMinimumSize(400, 400)
        
        # Enable drag mode
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
    def setup_interaction(self):
        """Configure interaction modes and flags."""
        self.setInteractive(True)
        
    def set_drawing_mode(self, enabled: bool):
        """Toggle between drawing and selection modes."""
        self.drawing_mode = enabled
        if enabled:
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.CrossCursor)
        else:
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.setCursor(Qt.ArrowCursor)
            
    def handle_drawing_click(self, pos):
        """Handle clicks in drawing mode."""
        nearest_point = self.scene().get_nearest_point(pos)
        
        if nearest_point:
            if self.scene().last_clicked_point is None:
                # First point of line
                self.scene().last_clicked_point = nearest_point
                nearest_point.highlight(True)
                self.start_preview_line(nearest_point.scenePos())
            else:
                # Second point - complete the line
                if nearest_point != self.scene().last_clicked_point:
                    self.create_line(self.scene().last_clicked_point, nearest_point)
                
                # Reset state
                self.scene().last_clicked_point.highlight(False)
                self.scene().last_clicked_point = None
                self.end_preview_line()
            
    def handle_item_selection(self, item, event):
        """Handle selection of an item."""
        if event.modifiers() & Qt.ControlModifier:
            # Toggle selection with Ctrl
            item.setSelected(not item.isSelected())
        else:
            # Clear selection and select only this item
            self.scene().clearSelection()
            item.setSelected(True)
            
        # Highlight the selected item
        if isinstance(item, (GeometryPoint, GeometryLine)):
            item.highlight(item.isSelected())
            
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() == Qt.AltModifier):
            # Start panning
            self.panning = True
            self.last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        elif event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            if self.drawing_mode:
                self.handle_drawing_click(scene_pos)
            else:
                # Try to select nearest item first
                item = self.get_item_at_position(scene_pos)
                if item:
                    self.handle_item_selection(item, event)
                else:
                    # If no item found, allow rubber band selection
                    super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)
            
    def get_item_at_position(self, pos):
        """Find the nearest selectable item at the given position."""
        # Check for points first (they're smaller)
        nearest_point = self.scene().get_nearest_point(pos)
        if nearest_point and self.is_within_selection_distance(pos, nearest_point):
            return nearest_point
            
        # Then check for lines
        nearest_line = self.scene().get_nearest_line(pos)
        if nearest_line and self.is_within_selection_distance(pos, nearest_line):
            return nearest_line
            
        return None
        
    def is_within_selection_distance(self, pos, item):
        """Check if position is within selection distance of item."""
        if isinstance(item, GeometryPoint):
            distance = (item.scenePos() - pos).manhattanLength()
            return distance <= self.selection_distance
        elif isinstance(item, GeometryLine):
            line = item.line()
            distance = self.scene().distance_to_line_segment(
                pos,
                line.p1(),
                line.p2()
            )
            return distance <= self.selection_distance
        return False
        
    def mouseMoveEvent(self, event):
        """Handle mouse movement."""
        if self.panning and self.last_pan_point:
            # Calculate how far to move the view
            delta = event.pos() - self.last_pan_point
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y())
            self.last_pan_point = event.pos()
            event.accept()
        elif self.drawing_mode and self.scene().last_clicked_point:
            # Update line preview
            scene_pos = self.mapToScene(event.pos())
            self.update_preview_line(scene_pos)
            self.last_mouse_pos = scene_pos
        
        super().mouseMoveEvent(event)
            
    def wheelEvent(self, event):
        """Handle zooming with mouse wheel."""
        if event.modifiers() == Qt.ControlModifier:
            # Get the current position before zoom
            old_pos = self.mapToScene(event.pos())
            
            # Zoom
            zoom_in = event.angleDelta().y() > 0
            factor = self.zoom_factor if zoom_in else 1.0 / self.zoom_factor
            self.scale(factor, factor)
            
            # Get the new position after zoom
            new_pos = self.mapToScene(event.pos())
            
            # Move scene to keep the point under cursor
            delta = new_pos - old_pos
            self.translate(delta.x(), delta.y())
            
            event.accept()
        else:
            super().wheelEvent(event)
            
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key_Escape:
            # Cancel line creation if in progress
            if self.scene().last_clicked_point and self.scene().preview_line:
                self.scene().last_clicked_point = None
                self.end_preview_line()
                self.scene().drawing_mode = True

        # Navigation
        elif event.key() == Qt.Key_Space:
            # Toggle between scroll hand and rubber band selection
            if self.dragMode() == QGraphicsView.ScrollHandDrag:
                self.setDragMode(QGraphicsView.RubberBandDrag)
            else:
                self.setDragMode(QGraphicsView.ScrollHandDrag)
        elif event.key() == Qt.Key_F:
            # Fit view to content
            self.fitInView(self.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
        
        # Zoom Controls
        elif event.key() == Qt.Key_Plus and event.modifiers() == Qt.ControlModifier:
            # Zoom in
            self.scale(self.zoom_factor, self.zoom_factor)
        elif event.key() == Qt.Key_Minus and event.modifiers() == Qt.ControlModifier:
            # Zoom out
            self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
        elif event.key() == Qt.Key_0 and event.modifiers() == Qt.ControlModifier:
            # Reset zoom
            self.resetTransform()

        # Mode Switching
        elif event.key() == Qt.Key_D:
            # Toggle drawing mode
            self.drawing_mode = not self.drawing_mode
            self.set_drawing_mode(self.drawing_mode)
        elif event.key() == Qt.Key_S:
            # Switch to selection mode
            self.drawing_mode = False
            self.set_drawing_mode(False)
        
        # Selection
        elif event.key() == Qt.Key_A and event.modifiers() == Qt.ControlModifier:
            # Select all
            for item in self.scene().items():
                item.setSelected(True)
                if isinstance(item, (GeometryPoint, GeometryLine)):
                    item.highlight(True)
        elif event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            # Delete selected items
            for item in self.scene().selectedItems():
                self.scene().removeItem(item)

        # View Reset
        elif event.key() == Qt.Key_R:
            # Reset view (zoom and position)
            self.resetTransform()
            self.centerOn(0, 0)
        
        else:
            super().keyPressEvent(event)
            
    def start_preview_line(self, start_pos):
        """Start showing a preview line from the first point."""
        if not self.scene().preview_line:
            self.scene().preview_line = self.scene().addLine(
                start_pos.x(), start_pos.y(),
                start_pos.x(), start_pos.y(),
                QPen(QColor("gray"), 2, Qt.DashLine)
            )
            
    def update_preview_line(self, end_pos):
        """Update the preview line end position."""
        if self.scene().preview_line and self.scene().last_clicked_point:
            start_pos = self.scene().last_clicked_point.scenePos()
            self.scene().preview_line.setLine(
                start_pos.x(), start_pos.y(),
                end_pos.x(), end_pos.y()
            )
            
    def end_preview_line(self):
        """Remove the preview line."""
        if self.scene().preview_line:
            self.scene().removeItem(self.scene().preview_line)
            self.scene().preview_line = None
            
    def create_line(self, start_point, end_point):
        """Create a new line between two points."""
        line = GeometryLine(
            start_point,
            end_point,
            GeometryLine.Type.CUSTOM
        )
        self.scene().addItem(line)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and event.modifiers() == Qt.AltModifier):
            self.panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        elif event.button() == Qt.LeftButton and not self.drawing_mode:
            super().mouseReleaseEvent(event)
            # Update highlights for all selected items
            for item in self.scene().selectedItems():
                if isinstance(item, (GeometryPoint, GeometryLine)):
                    item.highlight(True)
        else:
            super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        """Handle right-click context menu."""
        item = self.get_item_at_position(self.mapToScene(event.pos()))
        if not item:
            return
            
        menu = QMenu(self)
        
        # Define common colors
        colors = [
            ("Blue", QColor("dodgerblue")),
            ("Orange", QColor(255, 165, 0)),
            ("Red", QColor(255, 0, 0)),
            ("Green", QColor(0, 255, 0)),
            ("Purple", QColor(147, 112, 219))
        ]
        
        if isinstance(item, GeometryLine):
            # Line-specific actions
            delete_action = menu.addAction("Delete Line")
            delete_action.triggered.connect(lambda: self.scene().removeItem(item))
            
            color_menu = menu.addMenu("Change Line Color")
            for name, color in colors:
                action = color_menu.addAction(name)
                action.triggered.connect(lambda checked, c=color: self.change_line_color(item, c))
                
        elif isinstance(item, GeometryPoint):
            # Point-specific actions
            delete_action = menu.addAction("Delete Point")
            delete_action.triggered.connect(lambda: self.scene().removeItem(item))
            
            color_menu = menu.addMenu("Change Point Color")
            for name, color in colors:
                action = color_menu.addAction(name)
                action.triggered.connect(lambda checked, c=color: self.change_point_color(item, c))
            
        menu.exec_(event.globalPos())
        
    def change_line_color(self, line, color):
        """Change the color of a line."""
        pen = line.pen()
        pen.setColor(color)
        line.setPen(pen)
        
    def change_point_color(self, point, color):
        """Change the color of a point."""
        point.setBrush(QBrush(color))
        point.setPen(QPen(color))

    def set_selected_items_color(self, color):
        """Helper method to set color of selected items."""
        for item in self.scene().selectedItems():
            if isinstance(item, GeometryPoint):
                item.set_color(color)
            elif isinstance(item, GeometryLine):
                item.set_color(color) 