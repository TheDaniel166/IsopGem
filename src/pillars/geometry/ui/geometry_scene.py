"""Central QGraphicsScene implementation for the geometry pillar."""
from __future__ import annotations
import math
from typing import List, Optional

from PyQt6.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsSimpleTextItem
from PyQt6.QtGui import QPen, QBrush, QColor, QPolygonF, QPainter
from PyQt6.QtCore import Qt, QPointF, QRectF

from .primitives import (
    Bounds,
    CirclePrimitive,
    GeometryScenePayload,
    LabelPrimitive,
    LinePrimitive,
    PenStyle,
    PolygonPrimitive,
    Primitive,
)


class GeometryScene(QGraphicsScene):
    """Shared graphics scene that can render any supported geometry shape."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._payload: Optional[GeometryScenePayload] = None
        self._grid_spacing: float = 1.0
        self._label_items: List[QGraphicsSimpleTextItem] = []
        self._axes_items: List[QGraphicsItem] = []
        self._label_primitives: List[LabelPrimitive] = []

        self.grid_visible: bool = True
        self.axes_visible: bool = True
        self.labels_visible: bool = True

        self._grid_color = QColor(226, 232, 240)
        self._themes = {
            "Daylight": ((248, 250, 252), (226, 232, 240)),
            "Midnight": ((15, 23, 42), (51, 65, 85)),
            "Slate": ((30, 41, 59), (71, 85, 105)),
            "Pearl": ((255, 255, 255), (209, 213, 219)),
        }
        self._theme_name = "Daylight"
        self.setBackgroundBrush(QColor(*self._themes[self._theme_name][0]))
        self.setSceneRect(-5, -5, 10, 10)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_payload(self, payload: Optional[GeometryScenePayload]):
        """Replace the scene content with the provided payload."""
        self._payload = payload
        self._rebuild_scene()

    def clear_payload(self):
        self._payload = None
        self._rebuild_scene()

    def set_grid_visible(self, visible: bool):
        if self.grid_visible != visible:
            self.grid_visible = visible
            self.update()

    def set_axes_visible(self, visible: bool):
        if self.axes_visible != visible:
            self.axes_visible = visible
            self._refresh_axes()

    def set_labels_visible(self, visible: bool):
        if self.labels_visible != visible:
            self.labels_visible = visible
            self._refresh_labels()

    def apply_theme(self, theme: str):
        palette = self._themes.get(theme, self._themes["Daylight"])
        self._theme_name = theme if theme in self._themes else "Daylight"
        bg_rgb, grid_rgb = palette
        self.setBackgroundBrush(QColor(*bg_rgb))
        self._grid_color = QColor(*grid_rgb)
        self.update()

    def get_current_bounds(self) -> Optional[Bounds]:
        if not self._payload:
            return None
        if self._payload.bounds:
            return self._payload.bounds
        if self._payload.primitives:
            return self._derive_bounds(self._payload.primitives)
        return None

    # ------------------------------------------------------------------
    # Rendering hooks
    # ------------------------------------------------------------------
    def drawBackground(self, painter: Optional[QPainter], rect: QRectF):  # pragma: no cover - Qt hook
        if painter is None:
            return

        super().drawBackground(painter, rect)

        if not self.grid_visible:
            return

        painter.save()
        painter.setPen(QPen(self._grid_color, 0))

        spacing = max(self._grid_spacing, 0.1)
        left = math.floor(rect.left() / spacing) * spacing
        right = math.ceil(rect.right() / spacing) * spacing
        top = math.floor(rect.top() / spacing) * spacing
        bottom = math.ceil(rect.bottom() / spacing) * spacing

        x = left
        while x <= right:
            painter.drawLine(QPointF(x, top), QPointF(x, bottom))
            x += spacing

        y = top
        while y <= bottom:
            painter.drawLine(QPointF(left, y), QPointF(right, y))
            y += spacing

        painter.restore()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _rebuild_scene(self):
        self.blockSignals(True)
        self.clear()
        self.blockSignals(False)
        self._label_items.clear()
        self._axes_items.clear()
        self._label_primitives = []

        if not self._payload or not self._payload.primitives:
            self.setSceneRect(-5, -5, 10, 10)
            return

        bounds = self._payload.bounds or self._derive_bounds(self._payload.primitives)
        padded_bounds = bounds.padded(max(bounds.width, bounds.height) * 0.1)
        self.setSceneRect(
            padded_bounds.min_x,
            padded_bounds.min_y,
            padded_bounds.width,
            padded_bounds.height,
        )

        self._grid_spacing = self._compute_grid_spacing(bounds)

        for primitive in self._payload.primitives:
            self._add_primitive(primitive)

        self._label_primitives = list(self._payload.labels)
        if self.labels_visible:
            self._label_items = self._create_label_items(self._label_primitives)

        if self.axes_visible:
            self._axes_items = self._create_axes(bounds)

    def _compute_grid_spacing(self, bounds: Bounds) -> float:
        span = max(bounds.width, bounds.height)
        if span <= 1:
            return 0.1
        if span <= 10:
            return 0.5
        if span <= 50:
            return 1.0
        return span / 50

    def _derive_bounds(self, primitives: List[Primitive]) -> Bounds:
        xs: List[float] = []
        ys: List[float] = []

        for primitive in primitives:
            if isinstance(primitive, CirclePrimitive):
                cx, cy = primitive.center
                r = abs(primitive.radius)
                xs.extend([cx - r, cx + r])
                ys.extend([cy - r, cy + r])
            elif isinstance(primitive, PolygonPrimitive):
                for px, py in primitive.points:
                    xs.append(px)
                    ys.append(py)
            elif isinstance(primitive, LinePrimitive):
                xs.extend([primitive.start[0], primitive.end[0]])
                ys.extend([primitive.start[1], primitive.end[1]])

        if not xs or not ys:
            return Bounds(-1, 1, -1, 1)

        return Bounds(min(xs), max(xs), min(ys), max(ys))

    def _add_primitive(self, primitive: Primitive):
        if isinstance(primitive, CirclePrimitive):
            self._add_circle(primitive)
        elif isinstance(primitive, PolygonPrimitive):
            self._add_polygon(primitive)
        elif isinstance(primitive, LinePrimitive):
            self._add_line(primitive)

    def _add_circle(self, primitive: CirclePrimitive):
        cx, cy = primitive.center
        radius = primitive.radius
        diameter = radius * 2
        ellipse = self.addEllipse(
            cx - radius,
            cy - radius,
            diameter,
            diameter,
            self._qt_pen(primitive.pen),
            self._qt_brush(primitive.brush),
        )
        if ellipse is not None:
            ellipse.setZValue(0)

    def _add_polygon(self, primitive: PolygonPrimitive):
        points = [QPointF(x, y) for x, y in primitive.points]
        polygon = QPolygonF(points)
        item = self.addPolygon(polygon, self._qt_pen(primitive.pen), self._qt_brush(primitive.brush))
        if item is not None:
            item.setZValue(0)

    def _add_line(self, primitive: LinePrimitive):
        line = self.addLine(
            primitive.start[0],
            primitive.start[1],
            primitive.end[0],
            primitive.end[1],
            self._qt_pen(primitive.pen),
        )
        if line is not None:
            line.setZValue(1)

    def _create_label_items(self, labels: List[LabelPrimitive]) -> List[QGraphicsSimpleTextItem]:
        label_items: List[QGraphicsSimpleTextItem] = []
        for label in labels:
            item = QGraphicsSimpleTextItem(label.text)
            item.setBrush(QColor(236, 242, 255))
            item.setZValue(2)
            item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
            font = item.font()
            font.setPointSizeF(8.0)
            item.setFont(font)
            offset_x = -item.boundingRect().width() / 2 if label.align_center else 0
            offset_y = item.boundingRect().height() / 2 if label.align_center else 0
            item.setPos(label.position[0] + offset_x, label.position[1] - offset_y)
            self.addItem(item)
            label_items.append(item)
        return label_items

    def _create_axes(self, bounds: Bounds) -> List[QGraphicsItem]:
        span = max(bounds.width, bounds.height) * 0.7
        pen = QPen(QColor(148, 163, 184), 0)
        axes: List[QGraphicsItem] = []
        horizontal = self.addLine(-span, 0, span, 0, pen)
        vertical = self.addLine(0, -span, 0, span, pen)
        for item in (horizontal, vertical):
            if item is not None:
                item.setZValue(-1)
                axes.append(item)
        return axes

    def _refresh_labels(self):
        if self.labels_visible:
            if not self._label_items and self._label_primitives:
                self._label_items = self._create_label_items(self._label_primitives)
            for item in self._label_items:
                item.setVisible(True)
        else:
            for item in self._label_items:
                item.setVisible(False)

    def _refresh_axes(self):
        if self.axes_visible:
            if not self._axes_items and self._payload and (self._payload.bounds or self._payload.primitives):
                bounds = self._payload.bounds or self._derive_bounds(self._payload.primitives)
                self._axes_items = self._create_axes(bounds)
            for item in self._axes_items:
                item.setVisible(True)
        else:
            for item in self._axes_items:
                item.setVisible(False)

    @staticmethod
    def _qt_pen(style: PenStyle) -> QPen:
        color = QColor(*style.color)
        pen = QPen(color, style.width)
        if style.dashed:
            pen.setStyle(Qt.PenStyle.DashLine)
        pen.setCosmetic(True)
        return pen

    @staticmethod
    def _qt_brush(style) -> QBrush:
        if not style.enabled:
            return QBrush(Qt.BrushStyle.NoBrush)
        return QBrush(QColor(*style.color))


__all__ = ["GeometryScene"]
