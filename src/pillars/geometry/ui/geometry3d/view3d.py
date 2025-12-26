"""Orthographic wireframe 3D widget for geometry solids."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

from PyQt6.QtCore import QPoint, QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QBrush,
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
from ...services.measurement_utils import (
    distance_3d, 
    polygon_area_3d, 
    triangle_area_3d,
    signed_tetrahedron_volume
)


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
        self._show_vertices = True
        self._show_dual = False
        
        # Measurement mode
        self._measure_mode = False
        self._selected_vertex_indices: List[int] = []  # Base polygon vertices
        self._apex_vertex_index: Optional[int] = None  # For 3D volume (pyramid apex)
        self._hovered_vertex_index: Optional[int] = None
        self._last_screen_points: List[QPointF] = []
        self._loop_closed = False  # True when base polygon is closed

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

    def set_vertices_visible(self, visible: bool):
        self._show_vertices = visible
        self.update()

    def vertices_visible(self) -> bool:
        return self._show_vertices

    def set_dual_visible(self, visible: bool):
        self._show_dual = visible
        self.update()

    def dual_visible(self) -> bool:
        return self._show_dual

    def set_measure_mode(self, enabled: bool):
        self._measure_mode = enabled
        self._selected_vertex_indices.clear()
        self._apex_vertex_index = None
        self._hovered_vertex_index = None
        self._loop_closed = False
        self.update()

    def measure_mode(self) -> bool:
        return self._measure_mode

    def clear_measurement(self):
        self._selected_vertex_indices.clear()
        self._apex_vertex_index = None
        self._loop_closed = False
        self.update()

    def selected_vertices(self) -> List[int]:
        return list(self._selected_vertex_indices)

    # Signal emitted when measurement is complete (vertex1, vertex2, distance)
    measurement_complete = pyqtSignal(int, int, float)


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

        # Store screen points for hit detection
        self._last_screen_points = screen_points

        # 5. Draw Vertices
        if self._show_vertices:
            self._draw_vertices(painter, screen_points, payload)

        # 6. Draw Measurement
        if self._measure_mode and self._selected_vertex_indices:
            self._draw_measurement(painter, screen_points, payload)

        self._draw_spheres(painter, payload, scale, pan_offset)
        self._draw_labels(painter, payload, matrix, scale, pan_offset)
        if self._show_axes:
            self._draw_axes(painter)
            
        if self._show_dual and payload.dual:
            self._draw_dual(painter, payload.dual, matrix, scale, pan_offset)

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
        pos = event.position().toPoint()
        self._last_mouse_pos = pos
        
        # Handle measurement mode clicks
        if self._measure_mode and (event.buttons() & Qt.MouseButton.LeftButton):
            vertex_idx = self._find_vertex_at_point(pos)
            if vertex_idx is not None:
                # 1. If loop is closed, click handles APEX selection
                if self._loop_closed:
                    if vertex_idx == self._apex_vertex_index:
                        # Click apex again to deselect
                        self._apex_vertex_index = None
                    elif vertex_idx not in self._selected_vertex_indices:
                        # Select new apex (must not be in base)
                        self._apex_vertex_index = vertex_idx
                    self.update()
                    return

                # 2. Check if clicking first vertex to close the loop
                if (len(self._selected_vertex_indices) >= 3 
                    and vertex_idx == self._selected_vertex_indices[0]):
                    # Close the loop - enables area calculation
                    self._loop_closed = True
                    self.update()
                    return
                
                # 3. Add vertex to selection (allow unlimited, but not if already selected)
                if vertex_idx not in self._selected_vertex_indices:
                    self._selected_vertex_indices.append(vertex_idx)
                    
                    # Emit signal for each new edge formed
                    if len(self._selected_vertex_indices) >= 2 and self._payload:
                        v1_idx = self._selected_vertex_indices[-2]
                        v2_idx = self._selected_vertex_indices[-1]
                        v1 = self._payload.vertices[v1_idx]
                        v2 = self._payload.vertices[v2_idx]
                        dist = distance_3d(v1, v2)
                        self.measurement_complete.emit(v1_idx, v2_idx, dist)
                self.update()
                return
        
        # Right-click clears steps backwards: Apex -> Closed Loop -> Vertices
        if self._measure_mode and (event.buttons() & Qt.MouseButton.RightButton):
            if self._apex_vertex_index is not None:
                self._apex_vertex_index = None
            elif self._loop_closed:
                self._loop_closed = False
            else:
                self._selected_vertex_indices.clear()
            self.update()
            return
        
        # Regular camera interaction
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
        pos = event.position().toPoint()
        
        # Update hover in measure mode
        if self._measure_mode:
            old_hover = self._hovered_vertex_index
            self._hovered_vertex_index = self._find_vertex_at_point(pos)
            if old_hover != self._hovered_vertex_index:
                self.update()
        
        # Regular camera interaction
        if self._last_mouse_pos is None or self._interaction_mode is None:
            return
        delta = pos - self._last_mouse_pos
        self._last_mouse_pos = pos

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

    def _draw_dual(self, painter: QPainter, dual_payload: SolidPayload, matrix: QMatrix4x4, scale: float, pan_offset: QPointF):
        """Draw the dual solid as a ghost overlay."""
        if not dual_payload.vertices:
            return
            
        screen_points = self._project_vertices(dual_payload, matrix, scale, pan_offset)
        
        # Draw Faces (Translucent Ghost)
        painter.setPen(Qt.PenStyle.NoPen)
        # Use a fixed ghost color (e.g., Cyan or Purple)
        ghost_color = QColor(255, 255, 255, 30) # Very faint white/glassy
        painter.setBrush(QBrush(ghost_color))
        
        if dual_payload.faces:
            # Simple painter's alg isn't strictly needed for ghost overlay if it's additive/alpha
            # But let's just draw them.
            for face_indices in dual_payload.faces:
                poly = [screen_points[i] for i in face_indices if i < len(screen_points)]
                if len(poly) < 3: continue
                painter.drawPolygon([p.toPoint() for p in poly])

        # Draw Edges (Distinct style)
        pen = QPen(QColor(255, 255, 255, 120), 1.0, Qt.PenStyle.DotLine)
        painter.setPen(pen)
        for edge in dual_payload.edges:
            if len(edge) != 2: continue
            i, j = edge
            if i < len(screen_points) and j < len(screen_points):
                painter.drawLine(screen_points[i], screen_points[j])
                
        # Draw Vertices (Small dots)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255, 180))
        for pt in screen_points:
            painter.drawEllipse(pt, 2, 2)

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

    def _draw_gizmo(self, painter: QPainter):
        """Draw small orientation axes in corner."""
        size = 40
        padding = 20
        origin = QPointF(padding + size/2, self.height() - padding - size/2)
        
        # Simple static axes for now, TODO: rotate with view
        axis_length = 15
        painter.setPen(QPen(QColor(239, 68, 68), 2.0))
        painter.drawLine(origin, QPointF(origin.x() + axis_length, origin.y()))
        painter.drawText(origin + QPointF(axis_length + 5, 0), "X")
        painter.setPen(QPen(QColor(16, 185, 129), 2.0))
        painter.drawLine(origin, QPointF(origin.x(), origin.y() - axis_length))
        painter.drawText(origin + QPointF(-10, -axis_length - 5), "Y")
        painter.setPen(QPen(QColor(59, 130, 246), 2.0))
        painter.drawLine(origin, QPointF(origin.x() - axis_length * 0.6, origin.y() + axis_length * 0.6))
        painter.drawText(origin + QPointF(-axis_length * 0.6 - 10, axis_length * 0.6 + 10), "Z")

    def _draw_vertices(self, painter: QPainter, screen_points: List[QPointF], payload: SolidPayload, center_point: QPointF = None):
        """Draw vertex markers at each vertex, including optional center."""
        painter.save()
        
        # Draw Center Point (Index -1) if visible
        if center_point:
            i = -1
            if i in self._selected_vertex_indices:
                painter.setPen(QPen(QColor(255, 215, 0), 2.0))
                painter.setBrush(QColor(255, 215, 0, 180))
                radius = 8
            elif i == self._hovered_vertex_index:
                painter.setPen(QPen(QColor(56, 189, 248), 2.0)) # Light Blue
                painter.setBrush(QColor(56, 189, 248, 150))
                radius = 7
            else:
                painter.setPen(QPen(QColor(56, 189, 248), 1.5)) # Blueish
                painter.setBrush(QColor(56, 189, 248, 80))
                radius = 4
            
            painter.drawEllipse(center_point, radius, radius)
            if i in self._selected_vertex_indices or i == self._hovered_vertex_index:
                painter.setPen(QColor(255, 255, 255))
                font = painter.font()
                font.setPointSize(9)
                painter.setFont(font)
                painter.drawText(center_point + QPointF(10, -10), "C")

        # Draw Mesh Vertices
        # Optimization: If too many vertices, only draw selected/hovered to avoid clutter
        show_all_vertices = len(screen_points) <= 200
        
        for i, point in enumerate(screen_points):
            is_selected = i in self._selected_vertex_indices
            is_hovered = i == self._hovered_vertex_index
            
            if not show_all_vertices and not is_selected and not is_hovered:
                continue

            # Highlight selected vertices
            if is_selected:
                painter.setPen(QPen(QColor(255, 215, 0), 2.0))  # Gold
                painter.setBrush(QColor(255, 215, 0, 180))
                radius = 8
            elif is_hovered:
                painter.setPen(QPen(QColor(255, 255, 255), 2.0))
                painter.setBrush(QColor(255, 255, 255, 150))
                radius = 7
            else:
                painter.setPen(QPen(QColor(220, 220, 220), 1.5))
                painter.setBrush(QColor(180, 180, 180, 120))
                radius = 5
            
            painter.drawEllipse(point, radius, radius)
            
            if is_selected or is_hovered:
                painter.setPen(QColor(255, 255, 255))
                font = painter.font()
                font.setPointSize(9)
                painter.setFont(font)
                painter.drawText(point + QPointF(10, -10), f"V{i}")
        
        painter.restore()

    def _draw_measurement(self, painter: QPainter, screen_points: List[QPointF], payload: SolidPayload):
        """Draw measurement lines between all selected vertices and show distances."""
        if len(self._selected_vertex_indices) < 2 or not payload.vertices:
            return
        
        painter.save()
        
        total_distance = 0.0
        num_verts = len(self._selected_vertex_indices)
        
        def get_pt_3d(idx):
            return (0.0, 0.0, 0.0) if idx == -1 else payload.vertices[idx]
            
        def get_pt_screen(idx):
             return self._center_screen_point if idx == -1 else screen_points[idx]
        
        # Draw lines between consecutive vertices
        for i in range(num_verts - 1):
            v1_idx = self._selected_vertex_indices[i]
            v2_idx = self._selected_vertex_indices[i + 1]
            p1 = get_pt_screen(v1_idx)
            p2 = get_pt_screen(v2_idx)
            
            # Draw measurement line
            painter.setPen(QPen(QColor(255, 215, 0), 2.0, Qt.PenStyle.DashLine))
            painter.drawLine(p1, p2)
            
            # Calculate 3D distance for this segment
            v1_3d = get_pt_3d(v1_idx)
            v2_3d = get_pt_3d(v2_idx)
            segment_dist = distance_3d(v1_3d, v2_3d)
            total_distance += segment_dist
            
            # Draw segment distance at midpoint
            mid = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
            self._draw_distance_label(painter, mid, f"{segment_dist:.4f}", small=True)
        
        # If loop is closed, draw closing edge and calculate area
        if self._loop_closed and num_verts >= 3:
            # Draw closing edge (last to first)
            v1_idx = self._selected_vertex_indices[-1]
            v2_idx = self._selected_vertex_indices[0]
            p1 = get_pt_screen(v1_idx)
            p2 = get_pt_screen(v2_idx)
            
            painter.setPen(QPen(QColor(255, 215, 0), 2.5, Qt.PenStyle.SolidLine))
            painter.drawLine(p1, p2)
            
            # Add closing edge distance
            v1_3d = get_pt_3d(v1_idx)
            v2_3d = get_pt_3d(v2_idx)
            closing_dist = distance_3d(v1_3d, v2_3d)
            total_distance += closing_dist
            
            mid = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)
            self._draw_distance_label(painter, mid, f"{closing_dist:.4f}", small=True)
            
            # Calculate polygon area (handles 0,0,0 if present)
            poly_verts = [get_pt_3d(i) for i in self._selected_vertex_indices]
            area = polygon_area_3d(poly_verts)
            
            # If Apex selected, calculate Volume and Surface Area
            if self._apex_vertex_index is not None:
                apex = get_pt_3d(self._apex_vertex_index)
                apex_pt = get_pt_screen(self._apex_vertex_index)
                
                # Draw edges to apex
                painter.setPen(QPen(QColor(236, 72, 153), 2.0, Qt.PenStyle.DashLine)) # Pink
                total_lateral_area = 0.0
                volume = 0.0
                
                for i in range(num_verts):
                    v_idx = self._selected_vertex_indices[i]
                    pt = get_pt_screen(v_idx)
                    painter.drawLine(pt, apex_pt)
                    
                    # Calculate lateral face area
                    next_idx = self._selected_vertex_indices[(i + 1) % num_verts]
                    v_curr = get_pt_3d(v_idx)
                    v_next = get_pt_3d(next_idx)
                    lateral_area = triangle_area_3d(apex, v_curr, v_next)
                    total_lateral_area += lateral_area
                    
                    # Calculate pyramid volume slice (tetrahedron)
                    if i < num_verts - 1: # Triangulate base from first vertex V0
                        v0 = get_pt_3d(self._selected_vertex_indices[0])
                        vi = get_pt_3d(self._selected_vertex_indices[i])
                        vi_plus_1 = get_pt_3d(self._selected_vertex_indices[i+1])
                        # Skip if i=0 since that gives degenerate (V0, V0, V1)
                        if i > 0:
                            # Volume of tetrahedron (Apex, V0, Vi, Vi+1)
                            vol_slice = abs(signed_tetrahedron_volume(apex, v0, vi, vi_plus_1))
                            volume += vol_slice

                total_surface_area = area + total_lateral_area
                
                # Draw Volume/Area labels
                # Calculate centroid of pyramid for label position
                base_center_x = sum(get_pt_screen(i).x() for i in self._selected_vertex_indices) / num_verts
                base_center_y = sum(get_pt_screen(i).y() for i in self._selected_vertex_indices) / num_verts
                base_center = QPointF(base_center_x, base_center_y)
                
                label_pos = QPointF(
                    (base_center.x() + apex_pt.x()) / 2,
                    (base_center.y() + apex_pt.y()) / 2
                )
                
                # Box for statistics
                stats_text = (f"Base Area: {area:.4f}\n"
                              f"Surface: {total_surface_area:.4f}\n"
                              f"Volume: {volume:.4f}")
                self._draw_multiline_label(painter, label_pos, stats_text)
                
            else:
                # Just draw base area label
                center_x = sum(get_pt_screen(i).x() for i in self._selected_vertex_indices) / num_verts
                center_y = sum(get_pt_screen(i).y() for i in self._selected_vertex_indices) / num_verts
                center = QPointF(center_x, center_y)
                self._draw_area_label(painter, center, area)
        
        # Show perimeter (total distance) at bottom
        if num_verts >= 3:
            label = f"Perimeter: {total_distance:.4f}"
            total_pos = QPointF(self.width() / 2, self.height() - 30)
            self._draw_distance_label(painter, total_pos, label, small=False)
        
        painter.restore()

    def _draw_distance_label(self, painter: QPainter, pos: QPointF, text: str, small: bool = False):
        """Helper to draw a distance label with background."""
        font = painter.font()
        font.setPointSize(9 if small else 11)
        font.setBold(True)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()
        
        # Background
        bg_rect = QRectF(pos.x() - text_width/2 - 6, pos.y() - text_height/2 - 3,
                         text_width + 12, text_height + 6)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 215, 0, 230))
        painter.drawRoundedRect(bg_rect, 6, 6)
        
        # Text
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, text)

    def _draw_area_label(self, painter: QPainter, pos: QPointF, area: float):
        """Draw an area label with a distinct appearance."""
        text = f"Area: {area:.4f}"
        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()
        
        # Green background for area
        bg_rect = QRectF(pos.x() - text_width/2 - 8, pos.y() - text_height/2 - 4,
                         text_width + 16, text_height + 8)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(16, 185, 129, 230))  # Green
        painter.drawRoundedRect(bg_rect, 8, 8)
        
        # White text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, text)

    def _draw_multiline_label(self, painter: QPainter, pos: QPointF, text: str):
        """Draw a multiline label with a distinct appearance for volume stats."""
        font = painter.font()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        
        # Calculate size for multiline text
        lines = text.split('\n')
        max_width = max(metrics.horizontalAdvance(line) for line in lines)
        line_height = metrics.height()
        total_height = line_height * len(lines)
        
        # Purple background for 3D stats
        bg_rect = QRectF(pos.x() - max_width/2 - 10, pos.y() - total_height/2 - 6,
                         max_width + 20, total_height + 12)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(139, 92, 246, 230))  # Violet
        painter.drawRoundedRect(bg_rect, 8, 8)
        
        # White text
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, text)

    def _find_vertex_at_point(self, pos: QPoint, threshold: float = 15.0) -> Optional[int]:
        """Find the nearest vertex to the given screen position, checking center too."""
        if not self._last_screen_points:
            return None
        
        min_dist = threshold
        nearest_idx = None
        
        # Check regular vertices
        for i, screen_pt in enumerate(self._last_screen_points):
            dx = pos.x() - screen_pt.x()
            dy = pos.y() - screen_pt.y()
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < min_dist:
                min_dist = dist
                nearest_idx = i
        
        # Check center point (-1)
        if getattr(self, '_center_screen_point', None):
            c_pt = self._center_screen_point
            dx = pos.x() - c_pt.x()
            dy = pos.y() - c_pt.y()
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < min_dist:
                # Center is closer than any vertex
                return -1
                
        return nearest_idx
