"""Reusable QGraphicsView wrapper with zoom and pan helpers."""
from __future__ import annotations
from typing import Optional

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
        if 0.1 <= new_scale <= 20:
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
    # Panning helpers
    # ------------------------------------------------------------------
    def mousePressEvent(self, event: Optional[QMouseEvent]):  # pragma: no cover - GUI interaction
        if event is None:
            return
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_active = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: Optional[QMouseEvent]):  # pragma: no cover - GUI interaction
        if event is None:
            return
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
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: Optional[QMouseEvent]):  # pragma: no cover - GUI interaction
        if event is None:
            return
        if event.button() == Qt.MouseButton.MiddleButton and self._pan_active:
            self._pan_active = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)


__all__ = ["GeometryView"]
