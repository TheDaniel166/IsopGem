"""
Geometry View - The Sacred Canvas Viewport.
Graphics view for rendering geometry scenes with zoom, pan, and vertex measurement support.
"""
from __future__ import annotations
import math
from typing import Optional, List


from PyQt6.QtWidgets import QGraphicsView, QRubberBand
from PyQt6.QtCore import QPoint, Qt, QRectF, QSize, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QMouseEvent, QWheelEvent

from .geometry_scene import GeometryScene
from .primitives import Bounds


class GeometryView(QGraphicsView):
    """Shared graphics view for rendering geometry scenes."""
    
    # Signal emitted with list of selected dot indices
    dots_selected = pyqtSignal(list)

    def __init__(self, scene: GeometryScene, parent=None):
        """
          init   logic.
        
        Args:
            scene: Description of scene.
            parent: Description of parent.
        
        """
        super().__init__(scene, parent)
        self._pan_active = False
        self._pan_start = QPoint()
        
        # Measurement state
        self._measuring_active = False
        self._measure_points: List[QPointF] = []
        self._snap_threshold = 15.0  # pixels
        self._temp_line_preview = None
        
        # Selection state
        self._selection_mode = False
        self._rubber_band: Optional[QRubberBand] = None
        self._selection_origin = QPoint()

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
            | QPainter.RenderHint.TextAntialiasing
        )
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        # Do not set background brush on View, let Scene handle it.
        # self.setBackgroundBrush(scene.backgroundBrush())

        
    def resizeEvent(self, event):
        """
        Resizeevent logic.
        
        Args:
            event: Description of event.
        
        """
        super().resizeEvent(event)
        # Also update on resize if needed (though resize doesn't change transform usually, but fits might)
        scene = self.scene()
        if hasattr(scene, "update_label_layout"):
            scene.update_label_layout(self.transform())  # type: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess, reportUnknownMemberType]


    # ------------------------------------------------------------------
    # Zoom helpers
    # ------------------------------------------------------------------
    def wheelEvent(self, event: Optional[QWheelEvent]):  # pragma: no cover - GUI interaction
        """
        Wheelevent logic.
        
        Args:
            event: Description of event.
        
        """
        if event is None:
            return
        angle = event.angleDelta().y()
        if angle == 0:
            return
        factor = 1.15 if angle > 0 else 1 / 1.15
        self._apply_zoom(factor)

    def zoom_in(self):
        """
        Zoom in logic.
        
        """
        self._apply_zoom(1.15)

    def zoom_out(self):
        """
        Zoom out logic.
        
        """
        self._apply_zoom(1 / 1.15)

    def zoom(self, factor: float):
        """
        Zoom logic.
        
        Args:
            factor: Description of factor.
        
        """
        self._apply_zoom(factor)

    def reset_view(self):
        """
        Reset view logic.
        
        """
        self.resetTransform()
        scene = self.scene()
        if hasattr(scene, "update_label_layout"):
            scene.update_label_layout(self.transform())  # type: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess, reportUnknownMemberType]

    def fit_scene(self):
        """
        Fit scene logic.
        
        """
        scene = self.scene()
        if hasattr(scene, "get_current_bounds"):
            bounds = scene.get_current_bounds()  # type: ignore[attr-defined]
        else:
            bounds = None
        self.fit_to_bounds(bounds)

    def _apply_zoom(self, factor: float):
        current_scale = self.transform().m11()
        new_scale = current_scale * factor
        if 0.01 <= new_scale <= 400.0:
            self.scale(factor, factor)
            # Update label layout on zoom
            scene = self.scene()
            if hasattr(scene, "update_label_layout"):
                scene.update_label_layout(self.transform())  # type: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess, reportUnknownMemberType]


    def fit_to_bounds(self, bounds: Optional[Bounds]):
        """
        Fit to bounds logic.
        
        Args:
            bounds: Description of bounds.
        
        """
        if bounds is None:
            self.resetTransform()
            return
        padding = max(bounds.width, bounds.height) * 0.2
        padded = bounds.padded(padding if padding > 0 else 1.0)
        rect = QRectF(padded.min_x, padded.min_y, padded.width, padded.height)
        self.resetTransform()
        if rect.width() == 0 or rect.height() == 0:
            rect = QRectF(-1, -1, 2, 2)
        self.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)
        
        # Update label layout after fit operation
        scene = self.scene()
        if hasattr(scene, "update_label_layout"):
            scene.update_label_layout(self.transform())  # type: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess, reportUnknownMemberType]


    # ------------------------------------------------------------------
    # Measurement helpers
    # ------------------------------------------------------------------
    def set_measurement_mode(self, enabled: bool):
        """Enable or disable measurement mode."""
        self._measuring_active = enabled
        self._measure_points.clear()
        
        # Clear temporary measurement lines if disabling
        # if not enabled and hasattr(self.scene(), "clear_temporary_items"):
        #     self.scene().clear_temporary_items()
        
        # Toggle vertex highlights
        if hasattr(self.scene(), "set_vertex_highlights_visible"):
            self.scene().set_vertex_highlights_visible(enabled)  # type: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess, reportUnknownMemberType]
            
        if enabled:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def _snap_to_vertex(self, pos: QPoint, scene_pos: QPointF) -> QPointF:  # type: ignore[reportUndefinedVariable, reportUnknownParameterType]
        """Snap to nearest vertex if within threshold."""
        scene = self.scene()
        if not hasattr(scene, "get_vertices"):
            return scene_pos
            
        vertices = scene.get_vertices()  # type: ignore  # 4 errors
        closest_dist = float('inf')
        closest_pt = None
        
        for v in vertices:
            # Map vertex to view coordinates to check pixel distance
            view_pt = self.mapFromScene(v)
            dist = (pos - view_pt).manhattanLength()
            if dist < self._snap_threshold and dist < closest_dist:
                closest_dist = dist
                closest_pt = v
                
        return closest_pt if closest_pt else scene_pos

    # ------------------------------------------------------------------
    # Mouse Events
    # ------------------------------------------------------------------
    def mousePressEvent(self, event: Optional[QMouseEvent]):
        """
        Mousepressevent logic.
        
        Args:
            event: Description of event.
        
        """
        if event is None:
            return
        
        # Selection mode: Start rubber band
        if self._selection_mode and event.button() == Qt.MouseButton.LeftButton:
            self._selection_origin = event.pos()
            if not self._rubber_band:
                self._rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
            self._rubber_band.setGeometry(QRect(self._selection_origin, QSize()))
            self._rubber_band.show()
            event.accept()
            return
            
        # Pan handling: Only pan when DragMode allows it (NOT NoDrag)
        # NoDrag mode is used for drawing, so we let clicks pass through to scene.
        is_pan_mode = self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag
        should_pan = (event.button() == Qt.MouseButton.MiddleButton) or \
                     (event.button() == Qt.MouseButton.LeftButton and not self._measuring_active and is_pan_mode)

        if should_pan:
            self._pan_active = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        if self._measuring_active and event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            snapped_pos = self._snap_to_vertex(event.pos(), scene_pos)
            
            # Check for closing loop (clicking near start point)
            if len(self._measure_points) >= 3:
                start_pt_screen = self.mapFromScene(self._measure_points[0])  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
                if (event.pos() - start_pt_screen).manhattanLength() < self._snap_threshold:
                    # Close loop
                    if hasattr(self.scene(), "update_measurement_preview"):
                        self.scene().update_measurement_preview(self._measure_points, closed=True, view_scale=self.transform().m11())  # type: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess, reportUnknownMemberType]
                    self._measuring_active = False # Finish measurement mode? Or just finish this shape?
                    # Let's keep mode active but reset points for new shape if user wants
                    # Actually better UX: Finish shape, keep markers.
                    # User needs to toggle off or reset to clear.
                    self._measure_points = [] # For next shape
                    # Re-enable highlights? They are already enabled.
                    event.accept()
                    return

            self._measure_points.append(snapped_pos)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            
            # Update preview
            if hasattr(self.scene(), "update_measurement_preview"):
                self.scene().update_measurement_preview(self._measure_points, closed=False, view_scale=self.transform().m11())  # type: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess, reportUnknownMemberType]
            
            event.accept()
            return
            
        # Right click to reset measurement
        if self._measuring_active and event.button() == Qt.MouseButton.RightButton:
            self._measure_points.clear()
            if hasattr(self.scene(), "clear_temporary_items"):
                self.scene().clear_temporary_items()  # type: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess, reportUnknownMemberType]
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: Optional[QMouseEvent]):
        """
        Mousemoveevent logic.
        
        Args:
            event: Description of event.
        
        """
        if event is None:
            return

        # Selection mode: Resize rubber band
        if self._selection_mode and self._rubber_band and self._rubber_band.isVisible():
            self._rubber_band.setGeometry(QRect(self._selection_origin, event.pos()).normalized())
            event.accept()
            return

        # Pan move
        if self._pan_active:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            h_scrollbar = self.horizontalScrollBar()
            v_scrollbar = self.verticalScrollBar()
            if h_scrollbar is not None:
                h_scrollbar.setValue(h_scrollbar.value() - delta.x())
            if v_scrollbar is not None:
                v_scrollbar.setValue(v_scrollbar.value() - delta.y())
            event.accept()
            return

        # Measurement preview
        if self._measuring_active:
            # We could draw a dynamic line from last point to cursor here for better feedback
            # For now, relying on clicks is robust.
            pass

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: Optional[QMouseEvent]):  # pragma: no cover - GUI interaction
        """
        Mousereleaseevent logic.
        
        Args:
            event: Description of event.
        
        """
        if event is None:
            return
        
        # Selection mode: Complete selection
        if self._selection_mode and self._rubber_band and self._rubber_band.isVisible():
            self._rubber_band.hide()
            
            # Get selection rectangle in scene coordinates
            rect = self._rubber_band.geometry()
            scene_rect = QRectF(self.mapToScene(rect.topLeft()), self.mapToScene(rect.bottomRight()))
            
            # Query scene for dots in rect
            scene = self.scene()
            if hasattr(scene, 'get_dots_in_rect'):
                indices = scene.get_dots_in_rect(scene_rect)  # type: ignore  # 4 errors
                if indices:
                    self.dots_selected.emit(indices)
            
            event.accept()
            return
            
        is_pan_button = event.button() == Qt.MouseButton.MiddleButton or \
                        (event.button() == Qt.MouseButton.LeftButton and self._pan_active)
                        
        if is_pan_button and self._pan_active:
            self._pan_active = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def set_selection_mode(self, enabled: bool):
        """Enable or disable rubber-band selection mode."""
        self._selection_mode = enabled
        if enabled:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)


__all__ = ["GeometryView"]