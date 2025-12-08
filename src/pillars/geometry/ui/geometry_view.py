from __future__ import annotations
import math
from typing import Optional, List


from PyQt6.QtWidgets import QGraphicsView
from PyQt6.QtCore import QPoint, Qt, QRectF
from PyQt6.QtGui import QPainter, QMouseEvent, QWheelEvent

from .geometry_scene import GeometryScene
from .primitives import Bounds


class GeometryView(QGraphicsView):
    """Shared graphics view for rendering geometry scenes."""

    def __init__(self, scene: GeometryScene, parent=None):
        super().__init__(scene, parent)
        self._pan_active = False
        self._pan_start = QPoint()
        
        # Measurement state
        self._measuring_active = False
        self._measure_points: List[QPointF] = []
        self._snap_threshold = 15.0  # pixels
        self._temp_line_preview = None

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
            | QPainter.RenderHint.TextAntialiasing
        )
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setBackgroundBrush(scene.backgroundBrush())

    # ------------------------------------------------------------------
    # Zoom helpers
    # ------------------------------------------------------------------
    def wheelEvent(self, event: Optional[QWheelEvent]):  # pragma: no cover - GUI interaction
        if event is None:
            return
        angle = event.angleDelta().y()
        if angle == 0:
            return
        factor = 1.15 if angle > 0 else 1 / 1.15
        self._apply_zoom(factor)

    def zoom_in(self):
        self._apply_zoom(1.15)

    def zoom_out(self):
        self._apply_zoom(1 / 1.15)

    def reset_view(self):
        self.resetTransform()

    def fit_scene(self):
        scene = self.scene()
        if hasattr(scene, "get_current_bounds"):
            bounds = scene.get_current_bounds()  # type: ignore[attr-defined]
        else:
            bounds = None
        self.fit_to_bounds(bounds)

    def _apply_zoom(self, factor: float):
        current_scale = self.transform().m11()
        new_scale = current_scale * factor
        if 0.3 <= new_scale <= 6:
            self.scale(factor, factor)

    def fit_to_bounds(self, bounds: Optional[Bounds]):
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
            self.scene().set_vertex_highlights_visible(enabled)
            
        if enabled:
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def _snap_to_vertex(self, pos: QPoint, scene_pos: QPointF) -> QPointF:
        """Snap to nearest vertex if within threshold."""
        scene = self.scene()
        if not hasattr(scene, "get_vertices"):
            return scene_pos
            
        vertices = scene.get_vertices()
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
        if event is None:
            return
            
        # Pan handling (Middle button OR Left button if not measuring)
        should_pan = (event.button() == Qt.MouseButton.MiddleButton) or \
                     (event.button() == Qt.MouseButton.LeftButton and not self._measuring_active)

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
                start_pt_screen = self.mapFromScene(self._measure_points[0])
                if (event.pos() - start_pt_screen).manhattanLength() < self._snap_threshold:
                    # Close loop
                    if hasattr(self.scene(), "update_measurement_preview"):
                        self.scene().update_measurement_preview(self._measure_points, closed=True)
                    self._measuring_active = False # Finish measurement mode? Or just finish this shape?
                    # Let's keep mode active but reset points for new shape if user wants
                    # Actually better UX: Finish shape, keep markers.
                    # User needs to toggle off or reset to clear.
                    self._measure_points = [] # For next shape
                    # Re-enable highlights? They are already enabled.
                    event.accept()
                    return

            self._measure_points.append(snapped_pos)
            
            # Update preview
            if hasattr(self.scene(), "update_measurement_preview"):
                self.scene().update_measurement_preview(self._measure_points, closed=False)
            
            event.accept()
            return
            
        # Right click to reset measurement
        if self._measuring_active and event.button() == Qt.MouseButton.RightButton:
            self._measure_points.clear()
            if hasattr(self.scene(), "clear_temporary_items"):
                self.scene().clear_temporary_items()
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: Optional[QMouseEvent]):
        if event is None:
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
        if event is None:
            return
        is_pan_button = event.button() == Qt.MouseButton.MiddleButton or \
                        (event.button() == Qt.MouseButton.LeftButton and self._pan_active)
                        
        if is_pan_button and self._pan_active:
            self._pan_active = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)


__all__ = ["GeometryView"]
