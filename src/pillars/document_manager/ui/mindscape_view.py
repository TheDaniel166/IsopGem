"""CPU-rendered 3D-ish mindmap view (no GPU)."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Callable

from PyQt6.QtCore import QPoint, QPointF, Qt, QTimer, QSize, QRectF
from PyQt6.QtGui import QColor, QMatrix4x4, QMouseEvent, QPainter, QPainterPath, QPen, QVector3D, QWheelEvent, QPaintEvent
from PyQt6.QtWidgets import QWidget


@dataclass
class MindNode:
    node_id: int
    name: str
    pos: QVector3D
    color: QColor
    stroke_color: Optional[QColor] = None
    stroke_width: float = 1.6
    radius: float = 0.06
    pinned: bool = False
    shape: str = "circle"


@dataclass
class MindEdge:
    edge_id: int
    source_id: int
    target_id: int
    color: QColor
    width: float = 2.0
    style: str = "solid"


class CameraState:
    def __init__(self):
        self.distance = 4.0
        self.yaw_deg = 30.0
        self.pitch_deg = 25.0
        self.pan_x = 0.0
        self.pan_y = 0.0

    def rotation_matrix(self) -> QMatrix4x4:
        m = QMatrix4x4()
        m.rotate(self.pitch_deg, 1.0, 0.0, 0.0)
        m.rotate(self.yaw_deg, 0.0, 1.0, 0.0)
        return m


class MindscapeView(QWidget):
    """Lightweight painter-based view for mind maps."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._nodes: Dict[int, MindNode] = {}
        self._edges: List[MindEdge] = []
        self._camera = CameraState()
        self._last_mouse: Optional[QPoint] = None
        self._interaction: Optional[str] = None
        self._selected_node: Optional[int] = None
        self._selected_nodes: List[int] = []
        self._selected_edge: Optional[int] = None
        self._hover_node: Optional[int] = None
        self._hover_edge: Optional[int] = None
        self._box_start: Optional[QPointF] = None
        self._box_end: Optional[QPointF] = None
        self._selection_changed_cb = None
        self._edge_selection_changed_cb = None
        self._positions_changed_cb = None
        self._drag_accum: Dict[int, QVector3D] = {}

        # Throttle redraws slightly to keep CPU lower
        self._dirty = False
        self._repaint_timer = QTimer(self)
        self._repaint_timer.setInterval(16)
        self._repaint_timer.timeout.connect(self._maybe_update)
        self._repaint_timer.start()

        # Keyboard pan step
        self._pan_step = 0.15

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_data(self, nodes: List[MindNode], edges: List[MindEdge]):
        self._nodes = {n.node_id: n for n in nodes}
        self._edges = list(edges)
        self._drag_accum.clear()
        if self._selected_node not in self._nodes:
            self._selected_node = None
        self._selected_nodes = [nid for nid in self._selected_nodes if nid in self._nodes]
        edge_ids = {e.edge_id for e in self._edges}
        if self._selected_edge not in edge_ids:
            self._selected_edge = None
        self.update()

    def set_selection_changed_callback(self, cb):
        self._selection_changed_cb = cb

    def set_edge_selection_changed_callback(self, cb):
        self._edge_selection_changed_cb = cb

    def set_positions_changed_callback(self, cb):
        self._positions_changed_cb = cb

    def reset_camera(self):
        self._camera = CameraState()
        self.update()

    def fit_scene(self):
        if not self._nodes:
            self.reset_camera()
            return
        xs = [n.pos.x() for n in self._nodes.values()]
        ys = [n.pos.y() for n in self._nodes.values()]
        zs = [n.pos.z() for n in self._nodes.values()]
        span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 1.0)
        self._camera.distance = max(1.2, span * 1.5)
        self._camera.pan_x = 0
        self._camera.pan_y = 0
        self.update()

    def focus_on_selected_node(self):
        if self._selected_node is None:
            return
        node = self._nodes.get(self._selected_node)
        if node is None:
            return
        m = self._camera.rotation_matrix()
        rotated = m * node.pos
        # Center the rotated point in screen space by adjusting pan offsets
        self._camera.pan_x = -rotated.x()
        self._camera.pan_y = rotated.y()
        self._dirty = True

    def set_selected_node(self, node_id: Optional[int]):
        self._selected_node = node_id
        self._selected_nodes = [node_id] if node_id is not None else []
        if node_id is not None:
            self._selected_edge = None
        self.update()

    def get_selected_node(self) -> Optional[int]:
        return self._selected_node

    def get_selected_nodes(self) -> List[int]:
        return list(self._selected_nodes)

    def set_selected_edge(self, edge_id: Optional[int]):
        self._selected_edge = edge_id
        if edge_id is not None:
            self._selected_node = None
        self.update()

    def get_selected_edge(self) -> Optional[int]:
        return self._selected_edge

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------
    def paintEvent(self, a0: QPaintEvent | None):  # pragma: no cover - GUI
        if a0 is None:
            return
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(15, 23, 42))
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if not self._nodes:
            return

        matrix, scale, pan = self._projection_params()
        screen_points = {}
        for node in self._nodes.values():
            screen_points[node.node_id] = self._project(node.pos, matrix, scale, pan)

        self._draw_edges(painter, screen_points, scale)
        self._draw_nodes(painter, screen_points, scale)

    def wheelEvent(self, a0: QWheelEvent | None):  # pragma: no cover - GUI
        if a0 is None:
            return
        # Zoom toward cursor: keep the point under the cursor stationary in screen space
        delta = a0.angleDelta().y() / 120
        if delta == 0:
            return

        # Capture world position under cursor before zoom
        m, scale, pan = self._projection_params()
        inv_m = m.inverted()[0]
        cursor = a0.position()
        offset = cursor - pan
        world_rot = QVector3D(offset.x() / scale, -offset.y() / scale, 0)
        world_point = inv_m * world_rot

        # Apply zoom
        self._camera.distance = max(1.0, self._camera.distance * (0.9 ** delta))

        # Recompute scale and adjust pan so cursor stays put
        m_new, scale_new, _ = self._projection_params()
        rotated = m_new * world_point
        self._camera.pan_x = (cursor.x() - self.width() / 2 - rotated.x() * scale_new) / scale_new
        self._camera.pan_y = (cursor.y() - self.height() / 2 + rotated.y() * scale_new) / scale_new

        self._dirty = True

    def keyPressEvent(self, a0):  # pragma: no cover - GUI
        if a0 is None:
            return
        key = a0.key()
        step = self._pan_step
        if key in (Qt.Key.Key_W, Qt.Key.Key_Up):
            self._camera.pan_y += step
            self._dirty = True
        elif key in (Qt.Key.Key_S, Qt.Key.Key_Down):
            self._camera.pan_y -= step
            self._dirty = True
        elif key in (Qt.Key.Key_A, Qt.Key.Key_Left):
            self._camera.pan_x += step
            self._dirty = True
        elif key in (Qt.Key.Key_D, Qt.Key.Key_Right):
            self._camera.pan_x -= step
            self._dirty = True
        elif key == Qt.Key.Key_0:
            self.fit_scene()
        elif key == Qt.Key.Key_F:
            self.focus_on_selected_node()
        elif key == Qt.Key.Key_R:
            self.reset_camera()
        else:
            super().keyPressEvent(a0)

    def mousePressEvent(self, a0: QMouseEvent | None):  # pragma: no cover - GUI
        if a0 is None:
            return
        self._last_mouse = a0.position().toPoint()
        self._box_start = None
        self._box_end = None
        # Selection hit-test first
        picked_node = self._pick_node(a0.position(), commit=False)
        picked_edge = None
        if picked_node is None:
            picked_edge = self._pick_edge(a0.position(), commit=False)
        if picked_node is not None:
            self._selected_node = picked_node
            self._selected_nodes = [picked_node]
            self._selected_edge = None
            if self._selection_changed_cb:
                self._selection_changed_cb(picked_node)
            self._dirty = True
        elif picked_edge is not None:
            self._selected_edge = picked_edge
            self._selected_node = None
            self._selected_nodes = []
            if self._edge_selection_changed_cb:
                self._edge_selection_changed_cb(picked_edge)
            self._dirty = True
        else:
            if self._selected_node is not None or self._selected_edge is not None:
                self._selected_node = None
                self._selected_nodes = []
                self._selected_edge = None
                if self._selection_changed_cb:
                    self._selection_changed_cb(None)
                if self._edge_selection_changed_cb:
                    self._edge_selection_changed_cb(None)
                self._dirty = True

        if a0.buttons() & Qt.MouseButton.LeftButton:
            if a0.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self._interaction = 'drag_node'
                # ensure a node is selected for dragging
                if picked_node is None:
                    picked_node = self._pick_node(a0.position(), commit=True)
            elif a0.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self._interaction = 'box_select'
                self._box_start = a0.position()
                self._box_end = a0.position()
            else:
                self._interaction = 'rotate'
        elif a0.buttons() & Qt.MouseButton.MiddleButton:
            self._interaction = 'pan'
        elif a0.buttons() & Qt.MouseButton.RightButton and (a0.modifiers() & Qt.KeyboardModifier.AltModifier):
            # Alt + right-drag to pan even with context menu available on plain right-click
            self._interaction = 'pan'

    def mouseDoubleClickEvent(self, a0: QMouseEvent | None):  # pragma: no cover - GUI
        if a0 is None:
            return
        if a0.button() == Qt.MouseButton.LeftButton:
            self.fit_scene()

    def mouseMoveEvent(self, a0: QMouseEvent | None):  # pragma: no cover - GUI
        if a0 is None:
            return
        pos = a0.position()
        if self._interaction is None:
            # hover tracking
            self._hover_node = self._pick_node(pos, commit=False)
            if self._hover_node is None:
                self._hover_edge = self._pick_edge(pos, commit=False)
            else:
                self._hover_edge = None
            self._dirty = True
            return
        if self._last_mouse is None:
            self._last_mouse = pos.toPoint()
        delta = pos.toPoint() - self._last_mouse
        self._last_mouse = pos.toPoint()

        if self._interaction == 'rotate':
            self._camera.yaw_deg += delta.x() * 0.5
            self._camera.pitch_deg = max(-89.0, min(89.0, self._camera.pitch_deg + delta.y() * 0.5))
            self._dirty = True
        elif self._interaction == 'pan':
            self._camera.pan_x += delta.x() * 0.01
            self._camera.pan_y -= delta.y() * 0.01
            self._dirty = True
        elif self._interaction == 'drag_node' and self._selected_node is not None:
            self._drag_node(delta)
        elif self._interaction == 'box_select' and self._box_start is not None:
            self._box_end = pos
            self._selected_nodes = self._select_in_box(self._box_start, self._box_end)
            if self._selected_nodes:
                self._selected_node = self._selected_nodes[0]
                self._selected_edge = None
                if self._selection_changed_cb:
                    self._selection_changed_cb(self._selected_node)
            self._dirty = True

    def mouseReleaseEvent(self, a0: QMouseEvent | None):  # pragma: no cover - GUI
        if a0 is None:
            return
        if self._interaction == 'drag_node' and self._drag_accum and self._positions_changed_cb:
            # flush accumulated moves
            moves = [(nid, vec.x(), vec.y(), vec.z()) for nid, vec in self._drag_accum.items()]
            self._positions_changed_cb(moves)
        self._interaction = None
        self._drag_accum.clear()
        self._last_mouse = None
        if self._box_start is not None or self._box_end is not None:
            self._box_start = None
            self._box_end = None
            self._dirty = True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _projection_params(self):
        m = self._camera.rotation_matrix()
        base = min(self.width(), self.height()) / (2 * self._camera.distance)
        scale = base
        pan = QPointF(
            self.width() / 2 + self._camera.pan_x * scale,
            self.height() / 2 + self._camera.pan_y * scale,
        )
        return m, scale, pan

    @staticmethod
    def _project(vec: QVector3D, matrix: QMatrix4x4, scale: float, pan: QPointF) -> QPointF:
        rotated = matrix * vec
        x = rotated.x() * scale + pan.x()
        y = -rotated.y() * scale + pan.y()
        return QPointF(x, y)

    @staticmethod
    def _point_line_distance(p: QPointF, a: QPointF, b: QPointF) -> float:
        # Compute distance from point p to line segment ab in screen space
        ab = b - a
        ab_len_sq = ab.x() * ab.x() + ab.y() * ab.y()
        if ab_len_sq == 0:
            return (p - a).manhattanLength()
        t = ((p.x() - a.x()) * ab.x() + (p.y() - a.y()) * ab.y()) / ab_len_sq
        t = max(0.0, min(1.0, t))
        proj = QPointF(a.x() + t * ab.x(), a.y() + t * ab.y())
        dx = p.x() - proj.x()
        dy = p.y() - proj.y()
        return (dx * dx + dy * dy) ** 0.5

    def _select_in_box(self, start: QPointF, end: QPointF) -> List[int]:
        if not self._nodes:
            return []
        m, scale, pan = self._projection_params()
        x1, x2 = sorted([start.x(), end.x()])
        y1, y2 = sorted([start.y(), end.y()])
        selected = []
        for node in self._nodes.values():
            p = self._project(node.pos, m, scale, pan)
            if x1 <= p.x() <= x2 and y1 <= p.y() <= y2:
                selected.append(node.node_id)
        return selected

    def _draw_edges(self, painter: QPainter, pts: Dict[int, QPointF], scale: float):
        for edge in self._edges:
            if edge.source_id not in pts or edge.target_id not in pts:
                continue
            pen = QPen(edge.color, max(1.0, edge.width))
            if edge.style == 'dashed':
                pen.setStyle(Qt.PenStyle.DashLine)
            if self._selected_edge == edge.edge_id:
                pen.setWidthF(max(1.0, edge.width) * 1.6)
                pen.setColor(QColor(255, 255, 255))
            elif self._hover_edge == edge.edge_id:
                pen.setWidthF(max(1.0, edge.width) * 1.3)
                pen.setColor(edge.color.lighter(150))
            painter.setPen(pen)
            painter.drawLine(pts[edge.source_id], pts[edge.target_id])

    def _draw_nodes(self, painter: QPainter, pts: Dict[int, QPointF], scale: float):
        for node in self._nodes.values():
            p = pts[node.node_id]
            radius_px = max(10.0, node.radius * scale * 12.0)
            stroke = node.stroke_color or node.color.darker(140)
            pen_color = Qt.GlobalColor.white if self._selected_node == node.node_id else stroke
            if self._hover_node == node.node_id and self._selected_node != node.node_id:
                pen_color = stroke.lighter(150)
            pen = QPen(pen_color, max(0.8, node.stroke_width if self._selected_node == node.node_id else node.stroke_width * (1.05 if self._hover_node == node.node_id else 1.0)))
            painter.setPen(pen)
            painter.setBrush(node.color)

            shape = (node.shape or "circle").lower()
            if shape == "square":
                    painter.drawRect(QRectF(p.x() - radius_px, p.y() - radius_px, radius_px * 2, radius_px * 2))
            elif shape == "triangle":
                path = QPainterPath()
                h = radius_px * 1.4
                points = [
                    QPointF(p.x(), p.y() - h * 0.6),
                    QPointF(p.x() - h * 0.5, p.y() + h * 0.4),
                    QPointF(p.x() + h * 0.5, p.y() + h * 0.4),
                ]
                path.moveTo(points[0]); path.lineTo(points[1]); path.lineTo(points[2]); path.closeSubpath()
                painter.drawPath(path)
            elif shape == "diamond":
                path = QPainterPath()
                path.moveTo(p.x(), p.y() - radius_px)
                path.lineTo(p.x() + radius_px, p.y())
                path.lineTo(p.x(), p.y() + radius_px)
                path.lineTo(p.x() - radius_px, p.y())
                path.closeSubpath()
                painter.drawPath(path)
            elif shape == "hexagon":
                path = QPainterPath()
                for i in range(6):
                    theta = math.pi / 3 * i
                    x = p.x() + radius_px * math.cos(theta)
                    y = p.y() + radius_px * math.sin(theta)
                    if i == 0:
                        path.moveTo(x, y)
                    else:
                        path.lineTo(x, y)
                path.closeSubpath()
                painter.drawPath(path)
            else:
                painter.drawEllipse(p, radius_px, radius_px)

            label_pen = Qt.GlobalColor.white if self._selected_node == node.node_id else QColor(226, 232, 240)
            painter.setPen(label_pen)
            painter.drawText(p + QPointF(radius_px + 4, 4), node.name)

        # Draw selection box overlay
        if self._interaction == 'box_select' and self._box_start is not None and self._box_end is not None:
            rect = QRectF(self._box_start, self._box_end).normalized()
            pen = QPen(QColor(94, 234, 212), 1, Qt.PenStyle.DashLine)
            brush = QColor(94, 234, 212, 40)
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawRect(rect)

    def _pick_node(self, pos: QPointF, commit: bool = True) -> Optional[int]:
        if not self._nodes:
            return None
        m, scale, pan = self._projection_params()
        best = None
        best_dist = 1e9
        for node in self._nodes.values():
            p = self._project(node.pos, m, scale, pan)
            d = (p - pos).manhattanLength()
            if d < best_dist and d < 28:  # pick radius in px
                best = node.node_id
                best_dist = d
        if commit and best is not None:
            self._selected_node = best
            self._selected_nodes = [best]
            if self._selection_changed_cb:
                self._selection_changed_cb(best)
            self._dirty = True
        return best

    def _pick_edge(self, pos: QPointF, commit: bool = True) -> Optional[int]:
        if not self._edges:
            return None
        m, scale, pan = self._projection_params()
        pts = {nid: self._project(n.pos, m, scale, pan) for nid, n in self._nodes.items()}
        best = None
        best_dist = 1e9
        threshold = 10.0
        for edge in self._edges:
            a = pts.get(edge.source_id)
            b = pts.get(edge.target_id)
            if a is None or b is None:
                continue
            dist = self._point_line_distance(pos, a, b)
            if dist < threshold and dist < best_dist:
                best = edge.edge_id
                best_dist = dist
        if commit and best is not None:
            self._selected_edge = best
            if self._edge_selection_changed_cb:
                self._edge_selection_changed_cb(best)
            self._dirty = True
        return best

    def _drag_node(self, delta: QPoint):
        if not self._selected_nodes:
            return
        # Move in camera plane; convert screen delta to world delta
        m = self._camera.rotation_matrix()
        base = min(self.width(), self.height()) / (2 * self._camera.distance)
        scale = base
        dx_world = delta.x() / scale
        dy_world = -delta.y() / scale
        # apply inverse rotation on XY plane only
        inv = m.inverted()[0]
        move_vec = inv * QVector3D(dx_world, dy_world, 0)
        for nid in self._selected_nodes:
            node = self._nodes.get(nid)
            if node is None or node.pinned:
                continue
            node.pos += move_vec
            self._drag_accum[nid] = node.pos
        if self._drag_accum:
            self._dirty = True

    def _maybe_update(self):
        if self._dirty:
            self._dirty = False
            self.update()
