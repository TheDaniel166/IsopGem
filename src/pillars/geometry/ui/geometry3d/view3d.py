"""Orthographic wireframe 3D widget for geometry solids."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

from PyQt6.QtCore import QPoint, QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QFont,
    QMatrix4x4,
    QMouseEvent,
    QPaintEvent,
    QPainter,
    QPainterPath,
    QPen,
    QVector3D,
    QWheelEvent,
)
from PyQt6.QtWidgets import QWidget

from ...shared.solid_payload import SolidPayload


@dataclass
class CameraState:
    distance: float = 4.0
    yaw_deg: float = 30.0
    pitch_deg: float = 25.0
    pan_x: float = 0.0
    pan_y: float = 0.0

    def rotation_matrix(self) -> QMatrix4x4:
        matrix = QMatrix4x4()
        matrix.rotate(self.pitch_deg, 1.0, 0.0, 0.0)
        matrix.rotate(self.yaw_deg, 0.0, 1.0, 0.0)
        return matrix


class Geometry3DView(QWidget):
    """Lightweight software-rendered 3D viewport."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._payload: Optional[SolidPayload] = None
        self._payload_scale: float = 1.0
        self._camera = CameraState()
        self._last_mouse_pos: Optional[QPoint] = None
        self._interaction_mode: Optional[str] = None
        self._show_axes = True
        self._sphere_visibility = {
            'incircle': False,
            'midsphere': False,
            'circumsphere': False,
        }
        self._show_labels = True

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_payload(self, payload: Optional[SolidPayload]):
        self._payload = payload
        self._payload_scale = max(1e-6, getattr(payload, 'suggested_scale', 1.0) or 1.0)
        self.update()

    def reset_view(self):
        self._camera = CameraState()
        self.update()

    def set_camera_angles(self, yaw_deg: float, pitch_deg: float):
        self._camera.yaw_deg = yaw_deg
        self._camera.pitch_deg = max(-89.0, min(89.0, pitch_deg))
        self.update()

    def set_axes_visible(self, visible: bool):
        self._show_axes = visible
        self.update()

    def axes_visible(self) -> bool:
        return self._show_axes

    def set_labels_visible(self, visible: bool):
        self._show_labels = visible
        self.update()

    def labels_visible(self) -> bool:
        return self._show_labels

    def set_sphere_visible(self, kind: str, visible: bool):
        if kind in self._sphere_visibility:
            self._sphere_visibility[kind] = visible
            self.update()

    def sphere_visible(self, kind: str) -> bool:
        return self._sphere_visibility.get(kind, False)

    def zoom_in(self):
        self._camera.distance = max(1.0, self._camera.distance * 0.85)
        self.update()

    def zoom_out(self):
        self._camera.distance = min(100.0, self._camera.distance / 0.85)
        self.update()

    def fit_scene(self):
        if not self._payload or not self._payload.vertices:
            self.reset_view()
            return
        bounds = self._payload.bounds()
        if not bounds:
            self.reset_view()
            return
        (min_x, min_y, min_z), (max_x, max_y, max_z) = bounds
        span = max(
            (max_x - min_x) / self._payload_scale,
            (max_y - min_y) / self._payload_scale,
            (max_z - min_z) / self._payload_scale,
            1.0,
        )
        self._camera.distance = max(1.2, span * 1.2)
        self._camera.pan_x = 0.0
        self._camera.pan_y = 0.0
        self.update()

    # ------------------------------------------------------------------
    # QWidget overrides
    # ------------------------------------------------------------------
    def paintEvent(self, a0: QPaintEvent | None):  # pragma: no cover - GUI hook
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(15, 23, 42))

        # HighQualityAntialiasing is missing on some Qt builds, so guard the flag.
        basics = QPainter.RenderHint.Antialiasing
        high_quality = getattr(QPainter.RenderHint, 'HighQualityAntialiasing', None)
        if high_quality is not None:
            painter.setRenderHints(basics | high_quality)
        else:
            painter.setRenderHint(basics)

        payload = self._payload
        if not payload or not payload.vertices:
            return

        matrix, scale, pan_offset = self._projection_parameters()
        
        # 1. Transform all vertices to World Space (rotated) and Screen Space
        transformed_verts = []
        screen_points = []
        
        for vx, vy, vz in payload.vertices:
            vec = QVector3D(vx, vy, vz)
            rotated = matrix * vec
            transformed_verts.append(rotated)
            
            sx = rotated.x() * scale + pan_offset.x()
            sy = -rotated.y() * scale + pan_offset.y()
            screen_points.append(QPointF(sx, sy))

        # 2. Collect and Sort Faces (Painter's Algorithm)
        #    Sort by centroid Z (depth). Positive Z is towards camera in standard OpenGL,
        #    but here let's check coordinate system. Qt 3D usually: Y up, X right, Z out of screen?
        #    Actually we just need relative sort.
        
        faces_to_draw = []
        light_dir = QVector3D(-0.5, 0.5, 1.0).normalized() # Light from top-left-front
        
        if payload.faces:
            for i, face_indices in enumerate(payload.faces):
                # Calc Centroid & Normal
                v_positions = [transformed_verts[i] for i in face_indices]
                if len(v_positions) < 3:
                    continue
                    
                # Centroid Z for sorting
                z_sum = sum(v.z() for v in v_positions)
                centroid_z = z_sum / len(v_positions)
                
                # Normal (using first 3 points, assuming planar-ish)
                v0 = v_positions[0]
                v1 = v_positions[1]
                v2 = v_positions[2]
                normal = QVector3D.crossProduct(v1 - v0, v2 - v0).normalized()
                
                # Flat Shading
                # Dot product: -1 (backlit) to 1 (facing light)
                # Clamp to [0, 1] for simple diffuse
                dot = QVector3D.dotProduct(normal, light_dir)
                intensity = max(0.1, min(1.0, (dot + 1.0) * 0.5)) # Remap -1..1 to 0..1 for ambient+diffuse look
                
                faces_to_draw.append((centroid_z, face_indices, intensity, i))
                
            # Sort: Farthest Z first.
            # In our camera, if distance is positive, larger Z might be closer?
            # Camera rotation is simple rotation. 
            # Usually Z-buffer sorts by depth.
            # Let's try sorting by Z descending (paint farthest/smallest Z first? No, paint farthest Z first).
            # If Z points to viewer, negative Z is far. So paint smallest Z first.
            faces_to_draw.sort(key=lambda x: x[0]) 

            # 3. Draw Faces
            painter.setPen(Qt.PenStyle.NoPen)
            for _, indices, intensity, original_idx in faces_to_draw:
                poly = [screen_points[i] for i in indices]
                
                
                # Color Logic
                base_color = None
                if payload.face_colors and original_idx < len(payload.face_colors):
                     raw_color = payload.face_colors[original_idx]
                     if raw_color:
                         base_color = QColor(*raw_color)
                
                if base_color:
                    # Modulate intensity
                    # Scaling RGB
                    r = int(base_color.red() * intensity)
                    g = int(base_color.green() * intensity)
                    b = int(base_color.blue() * intensity)
                    alpha = base_color.alpha()
                else:
                    # Default "Crystal" Color
                    r = int(0 * intensity)
                    g = int(180 * intensity)
                    b = int(255 * intensity)
                    alpha = 210

                color = QColor(r, g, b, alpha)
                painter.setBrush(color)
                
                qpoly = [p.toPoint() for p in poly] # drawPolygon needs QPoint
                painter.drawPolygon(qpoly)

        # 4. Draw Edges (Wireframe overlay - simpler, cleaner)
        #    Draw edges faint or bright?
        #    Let's draw edges for definition
        edge_pen = QPen(QColor(255, 255, 255, 60), 1.0)
        painter.setPen(edge_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Optimization: Only draw edges that are part of the payload.edges list
        # If no explicit edges, do we infer? 
        # The payload currently has explicit edges.
        
        # To avoid Z-fighting/mess, maybe only draw silhouette or boundary?
        # For "Prism", allow wireframe on top for now.
        for edge in payload.edges:
            if len(edge) != 2: continue
            i, j = edge
            painter.drawLine(screen_points[i], screen_points[j])

        self._draw_spheres(painter, payload, scale, pan_offset)
        self._draw_labels(painter, payload, matrix, scale, pan_offset)
        if self._show_axes:
            self._draw_axes(painter)

    def wheelEvent(self, a0: QWheelEvent | None):  # pragma: no cover - GUI hook
        if a0 is None:
            return
        event = a0
        delta = event.angleDelta().y() / 120
        self._camera.distance = max(1.0, self._camera.distance * (0.9 ** delta))
        self.update()

    def mousePressEvent(self, a0: QMouseEvent | None):  # pragma: no cover - GUI hook
        if a0 is None:
            return
        event = a0
        self._last_mouse_pos = event.position().toPoint()
        if event.buttons() & Qt.MouseButton.LeftButton:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self._interaction_mode = 'pan'
            else:
                self._interaction_mode = 'rotate'
        elif event.buttons() & Qt.MouseButton.MiddleButton:
            self._interaction_mode = 'pan'

    def mouseMoveEvent(self, a0: QMouseEvent | None):  # pragma: no cover - GUI hook
        if a0 is None:
            return
        event = a0
        if self._last_mouse_pos is None or self._interaction_mode is None:
            return
        delta = event.position().toPoint() - self._last_mouse_pos
        self._last_mouse_pos = event.position().toPoint()

        if self._interaction_mode == 'rotate':
            self._camera.yaw_deg += delta.x() * 0.5
            self._camera.pitch_deg = max(-89.0, min(89.0, self._camera.pitch_deg + delta.y() * 0.5))
        elif self._interaction_mode == 'pan':
            self._camera.pan_x += delta.x() * 0.01
            self._camera.pan_y -= delta.y() * 0.01
        self.update()

    def mouseReleaseEvent(self, a0: QMouseEvent | None):  # pragma: no cover - GUI hook
        self._interaction_mode = None
        self._last_mouse_pos = None

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def _projection_parameters(self):
        matrix = self._camera.rotation_matrix()
        base_scale = min(self.width(), self.height()) / (2 * self._camera.distance)
        scale = base_scale / self._payload_scale
        pan_offset = QPointF(
            self.width() / 2 + self._camera.pan_x * scale,
            self.height() / 2 + self._camera.pan_y * scale,
        )
        return matrix, scale, pan_offset

    def _project_vertices(self, payload: SolidPayload, matrix: QMatrix4x4, scale: float, pan_offset: QPointF):
        return [self._project_point(vx, vy, vz, matrix, scale, pan_offset) for vx, vy, vz in payload.vertices]

    @staticmethod
    def _project_point(
        vx: float,
        vy: float,
        vz: float,
        matrix: QMatrix4x4,
        scale: float,
        pan_offset: QPointF,
    ) -> QPointF:
        vec = QVector3D(vx, vy, vz)
        rotated = matrix * vec
        x = rotated.x() * scale + pan_offset.x()
        y = -rotated.y() * scale + pan_offset.y()
        return QPointF(x, y)

    def _draw_spheres(self, painter: QPainter, payload: SolidPayload, scale: float, pan_offset: QPointF):
        metadata = payload.metadata or {}
        sphere_specs = (
            ('incircle', 'inradius', QColor(248, 113, 113)),
            ('midsphere', 'midradius', QColor(16, 185, 129)),
            ('circumsphere', 'circumradius', QColor(99, 102, 241)),
        )
        center = pan_offset
        for kind, radius_key, color in sphere_specs:
            if not self._sphere_visibility.get(kind):
                continue
            radius_value = metadata.get(radius_key)
            if not radius_value or radius_value <= 0:
                continue
            pixel_radius = radius_value * scale
            pen = QPen(color, 1.4, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(center, pixel_radius, pixel_radius)

    def _draw_labels(
        self,
        painter: QPainter,
        payload: SolidPayload,
        matrix: QMatrix4x4,
        scale: float,
        pan_offset: QPointF,
    ):
        if not payload.labels or not self._show_labels:
            return
        painter.save()
        font = QFont(painter.font())
        font.setPointSize(10)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        for label in payload.labels:
            point = self._project_point(*label.position, matrix, scale, pan_offset)
            text = label.text
            text_width = metrics.horizontalAdvance(text)
            text_height = metrics.height()
            if label.align_center:
                x = point.x() - text_width / 2
            else:
                x = point.x()
            y = point.y() - text_height / 2
            background_rect = QRectF(x - 6, y - 3, text_width + 12, text_height + 6)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(15, 23, 42, 220))
            painter.drawRoundedRect(background_rect, 6, 6)
            painter.setPen(QColor(248, 250, 252))
            baseline = QPointF(x, y + text_height - metrics.descent())
            painter.drawText(baseline, text)
        painter.restore()

    def _draw_axes(self, painter: QPainter):
        origin = QPointF(60, self.height() - 60)
        axis_length = 40
        pen = QPen(QColor(255, 255, 255), 1.5)
        painter.setPen(pen)
        painter.drawEllipse(origin, 3, 3)
        painter.setPen(QPen(QColor(239, 68, 68), 2.0))
        painter.drawLine(origin, QPointF(origin.x() + axis_length, origin.y()))
        painter.drawText(origin + QPointF(axis_length + 5, 0), "X")
        painter.setPen(QPen(QColor(16, 185, 129), 2.0))
        painter.drawLine(origin, QPointF(origin.x(), origin.y() - axis_length))
        painter.drawText(origin + QPointF(-10, -axis_length - 5), "Y")
        painter.setPen(QPen(QColor(59, 130, 246), 2.0))
        painter.drawLine(origin, QPointF(origin.x() - axis_length * 0.6, origin.y() + axis_length * 0.6))
        painter.drawText(origin + QPointF(-axis_length * 0.6 - 10, axis_length * 0.6 + 10), "Z")
