"""3D surface visualization widget for cymatics patterns.

Software-rendered 3D view using QPainter with Painter's algorithm
for depth-sorted face rendering. Displays cymatics amplitude field
as a height-mapped surface with orbital camera controls.

Pattern reference: src/pillars/geometry/ui/geometry3d/view3d.py
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QMatrix4x4,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
    QVector3D,
    QWheelEvent,
)
from PyQt6.QtWidgets import QWidget

from ..models import ColorGradient, SimulationResult
from ..services.cymatics_gradient_service import CymaticsGradientService


@dataclass
class CameraState:
    """Camera orientation for 3D view."""

    distance: float = 3.0
    yaw_deg: float = 30.0
    pitch_deg: float = 45.0
    pan_x: float = 0.0
    pan_y: float = 0.0

    def rotation_matrix(self) -> QMatrix4x4:
        """Build rotation matrix from yaw and pitch angles."""
        matrix = QMatrix4x4()
        matrix.rotate(self.pitch_deg, 1.0, 0.0, 0.0)
        matrix.rotate(self.yaw_deg, 0.0, 1.0, 0.0)
        return matrix


class Cymatics3DView(QWidget):
    """Software-rendered 3D surface visualization for cymatics patterns.

    Renders the cymatics amplitude field as a height-mapped 3D surface
    using QPainter with Painter's algorithm (back-to-front depth sorting).

    Features:
        - Orbital camera with mouse drag rotation
        - Scroll wheel zoom
        - Flat shading with directional lighting
        - Optional wireframe overlay
        - Color gradient support
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setMinimumSize(200, 200)

        self._result: Optional[SimulationResult] = None
        self._camera = CameraState()
        self._last_mouse_pos: Optional[QPoint] = None
        self._interaction_mode: Optional[str] = None

        # Rendering options
        self._show_wireframe = True
        self._show_faces = True
        self._height_scale = 0.4
        self._subsample = 4  # Render every Nth point for performance

        # Colors
        self._bg_color = QColor(15, 23, 42)
        self._face_color = QColor(0, 180, 255)
        self._edge_color = QColor(255, 255, 255, 40)

        # Gradient service for colored rendering
        self._gradient_service = CymaticsGradientService()
        self._use_gradient = True
        self._gradient_type = ColorGradient.PLASMA

    def set_result(self, result: SimulationResult) -> None:
        """Update with new simulation result."""
        self._result = result
        self.update()

    def set_height_scale(self, scale: float) -> None:
        """Set the height exaggeration factor (0.0 to 1.0)."""
        self._height_scale = max(0.0, min(1.0, scale))
        self.update()

    def set_subsample(self, value: int) -> None:
        """Set mesh subsampling (higher = faster but less detail)."""
        self._subsample = max(1, min(16, value))
        self.update()

    def set_wireframe(self, show: bool) -> None:
        """Toggle wireframe overlay."""
        self._show_wireframe = show
        self.update()

    def set_faces(self, show: bool) -> None:
        """Toggle filled faces."""
        self._show_faces = show
        self.update()

    def set_gradient(self, gradient_type: ColorGradient) -> None:
        """Set color gradient for surface coloring."""
        self._gradient_type = gradient_type
        self.update()

    def set_use_gradient(self, use: bool) -> None:
        """Toggle gradient coloring vs solid color."""
        self._use_gradient = use
        self.update()

    def reset_camera(self) -> None:
        """Reset camera to default position."""
        self._camera = CameraState()
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        """Render 3D surface using Painter's algorithm."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), self._bg_color)

        if self._result is None:
            self._draw_no_data_message(painter)
            return

        # Use height_map if available, otherwise use field
        height_data = self._result.height_map
        if height_data is None:
            height_data = self._result.field

        if height_data is None:
            self._draw_no_data_message(painter)
            return

        self._render_surface(painter, height_data, self._result.normalized)

    def _draw_no_data_message(self, painter: QPainter) -> None:
        """Draw placeholder message when no data available."""
        painter.setPen(QColor(100, 100, 100))
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            "No simulation data\nGenerate a pattern first",
        )

    def _render_surface(
        self, painter: QPainter, height_map: np.ndarray, normalized: np.ndarray
    ) -> None:
        """Render height map as 3D surface with depth sorting."""
        h, w = height_map.shape
        step = self._subsample

        # Build vertex array from height map
        vertices: List[Tuple[float, float, float]] = []
        colors: List[Tuple[int, int, int, int]] = []

        # Get color palette if using gradient
        if self._use_gradient:
            color_array = self._gradient_service.apply_gradient(
                normalized, self._gradient_type
            )

        for j in range(0, h - step, step):
            for i in range(0, w - step, step):
                # Normalized coordinates centered at origin
                x = (i / w) - 0.5
                z = (j / h) - 0.5
                y = float(height_map[j, i]) * self._height_scale
                vertices.append((x, y, z))

                if self._use_gradient:
                    colors.append(tuple(color_array[j, i]))
                else:
                    colors.append((
                        self._face_color.red(),
                        self._face_color.green(),
                        self._face_color.blue(),
                        200,
                    ))

        if not vertices:
            return

        # Build face indices (quads)
        cols = (w - 1) // step
        rows = (h - 1) // step
        faces: List[List[int]] = []

        for j in range(rows - 1):
            for i in range(cols - 1):
                v0 = j * cols + i
                v1 = v0 + 1
                v2 = v0 + cols
                v3 = v2 + 1
                if v3 < len(vertices):
                    faces.append([v0, v1, v3, v2])

        # Transform vertices
        matrix = self._camera.rotation_matrix()
        scale = min(self.width(), self.height()) / (2.5 * self._camera.distance)
        center = QPointF(
            self.width() / 2 + self._camera.pan_x,
            self.height() / 2 + self._camera.pan_y,
        )

        transformed: List[QVector3D] = []
        screen_pts: List[QPointF] = []

        for vx, vy, vz in vertices:
            vec = QVector3D(vx, vy, vz)
            rotated = matrix.map(vec)
            transformed.append(rotated)
            sx = rotated.x() * scale + center.x()
            sy = -rotated.y() * scale + center.y()
            screen_pts.append(QPointF(sx, sy))

        # Light direction for shading
        light_dir = QVector3D(-0.5, 0.8, 0.5).normalized()

        # Compute face data with depth and lighting
        face_data: List[Tuple[float, List[int], float, Tuple[int, int, int, int]]] = []

        for face_indices in faces:
            if len(face_indices) < 3:
                continue

            v_positions = [transformed[i] for i in face_indices]
            centroid_z = sum(v.z() for v in v_positions) / len(v_positions)

            # Calculate face normal for shading
            v0, v1, v2 = v_positions[:3]
            edge1 = v1 - v0
            edge2 = v2 - v0
            normal = QVector3D.crossProduct(edge1, edge2).normalized()

            # Lighting intensity
            dot = QVector3D.dotProduct(normal, light_dir)
            intensity = max(0.15, min(1.0, (dot + 1.0) * 0.5))

            # Average color for face
            face_color = colors[face_indices[0]]

            face_data.append((centroid_z, face_indices, intensity, face_color))

        # Sort by Z (farthest first for Painter's algorithm)
        face_data.sort(key=lambda x: x[0])

        # Draw faces
        if self._show_faces:
            painter.setPen(Qt.PenStyle.NoPen)
            for _, indices, intensity, base_color in face_data:
                poly = [screen_pts[i] for i in indices]
                r = int(base_color[0] * intensity)
                g = int(base_color[1] * intensity)
                b = int(base_color[2] * intensity)
                a = base_color[3] if len(base_color) > 3 else 200
                painter.setBrush(QColor(r, g, b, a))
                painter.drawPolygon([p.toPoint() for p in poly])

        # Draw wireframe
        if self._show_wireframe:
            painter.setPen(QPen(self._edge_color, 0.5))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for _, indices, _, _ in face_data:
                poly = [screen_pts[i] for i in indices]
                painter.drawPolygon([p.toPoint() for p in poly])

        # Draw info overlay
        self._draw_info_overlay(painter)

    def _draw_info_overlay(self, painter: QPainter) -> None:
        """Draw camera info in corner."""
        painter.setPen(QColor(150, 150, 150))
        info = f"Yaw: {self._camera.yaw_deg:.0f}° | Pitch: {self._camera.pitch_deg:.0f}°"
        painter.drawText(10, self.height() - 10, info)

    # ─────────────────────────────────────────────────────────────────
    # Mouse interaction
    # ─────────────────────────────────────────────────────────────────

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle scroll wheel for zoom."""
        delta = event.angleDelta().y() / 120
        zoom_factor = 0.9 if delta > 0 else 1.1
        self._camera.distance = max(0.5, min(10.0, self._camera.distance * zoom_factor))
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Handle mouse press for rotation/pan start."""
        self._last_mouse_pos = event.position().toPoint()
        if event.buttons() & Qt.MouseButton.LeftButton:
            self._interaction_mode = "rotate"
        elif event.buttons() & Qt.MouseButton.MiddleButton:
            self._interaction_mode = "pan"
        elif event.buttons() & Qt.MouseButton.RightButton:
            self._interaction_mode = "pan"

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handle mouse drag for rotation/pan."""
        if self._last_mouse_pos is None or self._interaction_mode is None:
            return

        pos = event.position().toPoint()
        delta = pos - self._last_mouse_pos
        self._last_mouse_pos = pos

        if self._interaction_mode == "rotate":
            self._camera.yaw_deg += delta.x() * 0.5
            self._camera.pitch_deg = max(
                -89, min(89, self._camera.pitch_deg + delta.y() * 0.5)
            )
        elif self._interaction_mode == "pan":
            self._camera.pan_x += delta.x()
            self._camera.pan_y += delta.y()

        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Handle mouse release."""
        self._interaction_mode = None
        self._last_mouse_pos = None
