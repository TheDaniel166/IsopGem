"""Orthographic wireframe 3D widget for geometry solids."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, List, Optional, Tuple, Union

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

if TYPE_CHECKING:
    from ..primitives import CirclePrimitive, PolygonPrimitive, LinePrimitive, GeometryScenePayload


class ColorTheme:
    """Customizable color theme for 3D viewport."""
    def __init__(
        self,
        background: QColor = None,
        face_default: QColor = None,
        edge: QColor = None,
        vertex_normal: QColor = None,
        vertex_selected: QColor = None,
        vertex_hovered: QColor = None,
        center_normal: QColor = None,
        center_selected: QColor = None,
        center_hovered: QColor = None,
        measure_line: QColor = None,
        measure_text_bg: QColor = None,
        measure_text_fg: QColor = None,
        measure_area_bg: QColor = None,
        measure_area_fg: QColor = None,
        measure_volume_bg: QColor = None,
        measure_volume_fg: QColor = None,
        axis_x: QColor = None,
        axis_y: QColor = None,
        axis_z: QColor = None,
        label_bg: QColor = None,
        label_fg: QColor = None,
        sphere_incircle: QColor = None,
        sphere_midsphere: QColor = None,
        sphere_circumsphere: QColor = None,
        angle_arc: QColor = None,
        angle_text_bg: QColor = None,
        angle_text_fg: QColor = None,
    ):
        # Background
        self.background = background or QColor(15, 23, 42)
        
        # Geometry elements
        self.face_default = face_default or QColor(0, 180, 255)
        self.edge = edge or QColor(255, 255, 255, 60)
        self.vertex_normal = vertex_normal or QColor(180, 180, 180, 120)
        self.vertex_selected = vertex_selected or QColor(255, 215, 0, 180)
        self.vertex_hovered = vertex_hovered or QColor(56, 189, 248, 150)
        
        # Center point
        self.center_normal = center_normal or QColor(56, 189, 248, 80)
        self.center_selected = center_selected or QColor(255, 215, 0, 180)
        self.center_hovered = center_hovered or QColor(56, 189, 248, 150)
        
        # Measurement tool
        self.measure_line = measure_line or QColor(255, 215, 0)
        self.measure_text_bg = measure_text_bg or QColor(255, 215, 0, 230)
        self.measure_text_fg = measure_text_fg or QColor(0, 0, 0)
        self.measure_area_bg = measure_area_bg or QColor(16, 185, 129, 230)
        self.measure_area_fg = measure_area_fg or QColor(255, 255, 255)
        self.measure_volume_bg = measure_volume_bg or QColor(139, 92, 246, 230)
        self.measure_volume_fg = measure_volume_fg or QColor(255, 255, 255)
        
        # Axes
        self.axis_x = axis_x or QColor(239, 68, 68)
        self.axis_y = axis_y or QColor(16, 185, 129)
        self.axis_z = axis_z or QColor(59, 130, 246)
        
        # Labels
        self.label_bg = label_bg or QColor(15, 23, 42, 220)
        self.label_fg = label_fg or QColor(248, 250, 252)
        
        # Spheres
        self.sphere_incircle = sphere_incircle or QColor(248, 113, 113)
        self.sphere_midsphere = sphere_midsphere or QColor(16, 185, 129)
        self.sphere_circumsphere = sphere_circumsphere or QColor(99, 102, 241)
        
        # Angle measurements
        self.angle_arc = angle_arc or QColor(255, 127, 80, 180)  # Coral
        self.angle_text_bg = angle_text_bg or QColor(255, 127, 80, 230)
        self.angle_text_fg = angle_text_fg or QColor(255, 255, 255)


@dataclass
class CameraState:
    """
    Camera State class definition.
    
    """
    distance: float = 4.0
    yaw_deg: float = 30.0
    pitch_deg: float = 25.0
    pan_x: float = 0.0
    pan_y: float = 0.0

    def rotation_matrix(self) -> QMatrix4x4:
        """
        Rotation matrix logic.
        
        Returns:
            Result of rotation_matrix operation.
        """
        matrix = QMatrix4x4()
        matrix.rotate(self.pitch_deg, 1.0, 0.0, 0.0)
        matrix.rotate(self.yaw_deg, 0.0, 1.0, 0.0)
        return matrix


class Geometry3DView(QWidget):
    """Lightweight software-rendered 3D viewport (handles both 2D and 3D payloads)."""

    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setMouseTracking(True)
        self._payload: Optional[SolidPayload] = None
        self._payload_scale: float = 1.0
        self._camera = CameraState()
        self._last_mouse_pos: Optional[QPoint] = None
        self._interaction_mode: Optional[str] = None
        self._show_axes = True
        self._show_faces = True
        self._show_edges = True
        self._sphere_visibility = {
            'incircle': False,
            'midsphere': False,
            'circumsphere': False,
        }
        self._show_labels = False  # Off by default
        self._show_vertices = False  # Off by default
        self._show_dual = False
        self._is_2d_mode = False  # Track if rendering 2D as flat 3D
        
        # Color theme
        self._color_theme = ColorTheme()
        
        # Measurement mode
        self._measure_mode = False
        self._show_angles = False  # Toggle for angle measurements
        self._angle_unit = "degrees"  # "degrees" or "radians"
        self._measure_precision = 4  # Decimal places for measurements
        self._snap_threshold = 15.0  # Pixel threshold for vertex snapping
        self._snap_to_canonical = False  # Snap to shape's canonical vertices
        self._selected_vertex_indices: List[int] = []  # Base polygon vertices
        self._apex_vertex_index: Optional[int] = None  # For 3D volume (pyramid apex)
        self._hovered_vertex_index: Optional[int] = None
        self._last_screen_points: List[QPointF] = []
        self._loop_closed = False  # True when base polygon is closed
    
    # ------------------------------------------------------------------
    # 2D-to-3D Conversion
    # ------------------------------------------------------------------
    
    def _convert_2d_to_3d(self, scene_payload: 'GeometryScenePayload') -> SolidPayload:
        """
        Convert 2D GeometryScenePayload to 3D SolidPayload at z=0.
        
        Circles are tessellated into polygons.
        Polygons become faces.
        Lines become edges.
        """
        from ..primitives import CirclePrimitive, PolygonPrimitive, LinePrimitive
        
        vertices: List[Tuple[float, float, float]] = []
        faces: List[List[int]] = []
        edges: List[Tuple[int, int]] = []
        
        vertex_map: dict[Tuple[float, float], int] = {}  # Deduplicate vertices
        
        def add_vertex(x: float, y: float) -> int:
            """Add vertex at z=0 and return its index."""
            key = (x, y)
            if key in vertex_map:
                return vertex_map[key]
            idx = len(vertices)
            vertices.append((x, y, 0.0))
            vertex_map[key] = idx
            return idx
        
        for primitive in scene_payload.primitives:
            if isinstance(primitive, CirclePrimitive):
                # Tessellate circle into 36-vertex polygon
                cx, cy = primitive.center
                r = primitive.radius
                indices = []
                for i in range(36):
                    angle = 2 * math.pi * i / 36
                    x = cx + r * math.cos(angle)
                    y = cy + r * math.sin(angle)
                    idx = add_vertex(x, y)
                    indices.append(idx)
                faces.append(indices)
                # Add edges around circle
                for i in range(len(indices)):
                    edges.append((indices[i], indices[(i + 1) % len(indices)]))
            
            elif isinstance(primitive, PolygonPrimitive):
                indices = [add_vertex(x, y) for x, y in primitive.points]
                if primitive.closed and len(indices) >= 3:
                    faces.append(indices)
                # Add edges
                for i in range(len(indices) - (0 if primitive.closed else 1)):
                    edges.append((indices[i], indices[(i + 1) % len(indices)]))
            
            elif isinstance(primitive, LinePrimitive):
                idx1 = add_vertex(*primitive.start)
                idx2 = add_vertex(*primitive.end)
                edges.append((idx1, idx2))
        
        return SolidPayload(
            vertices=vertices,
            edges=edges,
            faces=faces,
            metadata={"converted_from_2d": True}
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def set_payload(self, payload: Union[None, SolidPayload, 'GeometryScenePayload', Any]):
        """
        Configure payload logic (accepts 2D or 3D payloads).
        
        Args:
            payload: SolidPayload (3D), GeometryScenePayload (2D), or GeometryPayload wrapper
        """
        # Handle GeometryPayload wrapper
        if hasattr(payload, 'dimensional_class'):
            if payload.dimensional_class == 2:
                # Extract 2D scene payload and convert
                scene_payload = payload.scene_payload
                if scene_payload:
                    solid_payload = self._convert_2d_to_3d(scene_payload)
                    self._is_2d_mode = True
                    # Lock camera for 2D viewing (look down at z=0 plane)
                    self._camera.pitch_deg = 0.1  # Near horizontal for top-down view
                    self._camera.yaw_deg = 0.0
                    # Don't set distance here - let _set_solid_payload auto-calculate it
                    self._set_solid_payload(solid_payload)
                return
            elif payload.dimensional_class == 3:
                # Extract 3D solid payload
                solid_payload = payload.solid_payload
                if solid_payload:
                    self._is_2d_mode = False
                    self._set_solid_payload(solid_payload)
                return
        
        # Handle direct SolidPayload
        if isinstance(payload, SolidPayload) or payload is None:
            self._is_2d_mode = False
            self._set_solid_payload(payload)
        # Handle direct GeometryScenePayload (2D primitives)
        elif hasattr(payload, 'primitives'):
            self._is_2d_mode = True
            solid_payload = self._convert_2d_to_3d(payload)
            # For 2D: Look straight down at XY plane (minimal pitch for top-down view)
            self._camera.pitch_deg = 0.1  # Near horizontal gives top-down of z=0 plane
            self._camera.yaw_deg = 0.0
            # Don't set distance here - let _set_solid_payload auto-calculate it
            self._set_solid_payload(solid_payload)
    
    def _set_solid_payload(self, payload: Optional[SolidPayload]):
        """Internal method to set the solid payload."""
        # Handle if a GeometryScenePayload was passed by mistake - convert it
        if payload and hasattr(payload, 'primitives') and not hasattr(payload, 'vertices'):
            # This is a GeometryScenePayload, not a SolidPayload - convert it
            payload = self._convert_2d_to_3d(payload)
        
        # Clear measurement state if vertex count changes
        old_vertex_count = len(self._payload.vertices) if self._payload and self._payload.vertices else 0
        new_vertex_count = len(payload.vertices) if payload and payload.vertices else 0
        if old_vertex_count != new_vertex_count and self._measure_mode:
            # Vertex indices may be invalid, clear selection
            self._selected_vertex_indices.clear()
            self._apex_vertex_index = None
            self._hovered_vertex_index = None
            self._loop_closed = False
        
        self._payload = payload
        self._payload_scale = 1.0
        
        # Auto-adjust camera distance to keep visual size constant
        # Calculate payload bounds and set camera distance proportional to size
        if payload and payload.vertices:
            bounds = payload.bounds()
            if bounds:
                (min_x, min_y, min_z), (max_x, max_y, max_z) = bounds
                max_extent = max(
                    abs(max_x - min_x),
                    abs(max_y - min_y),
                    abs(max_z - min_z),
                    1.0
                )
                # Normalize camera distance to keep consistent visual size
                # Larger shapes = further camera distance
                self._camera.distance = max_extent * 2.0
        
        self.update()

    def reset_view(self):
        """
        Reset view logic.
        
        """
        self._camera = CameraState()
        self.update()

    def set_camera_angles(self, yaw_deg: float, pitch_deg: float):
        """
        Configure camera angles logic.
        
        Args:
            yaw_deg: Description of yaw_deg.
            pitch_deg: Description of pitch_deg.
        
        """
        self._camera.yaw_deg = yaw_deg
        self._camera.pitch_deg = max(-89.0, min(89.0, pitch_deg))
        self.update()

    def set_axes_visible(self, visible: bool):
        """
        Configure axes visible logic.
        
        Args:
            visible: Description of visible.
        
        """
        self._show_axes = visible
        self.update()

    def axes_visible(self) -> bool:
        """
        Axes visible logic.
        
        Returns:
            Result of axes_visible operation.
        """
        return self._show_axes

    def set_labels_visible(self, visible: bool):
        """
        Configure labels visible logic.
        
        Args:
            visible: Description of visible.
        
        """
        self._show_labels = visible
        self.update()

    def labels_visible(self) -> bool:
        """
        Labels visible logic.
        
        Returns:
            Result of labels_visible operation.
        """
        return self._show_labels

    def set_faces_visible(self, visible: bool):
        """Set face visibility (shows/hides filled polygons)."""
        self._show_faces = visible
        self.update()

    def faces_visible(self) -> bool:
        """Return current face visibility state."""
        return self._show_faces

    def set_edges_visible(self, visible: bool):
        """Set edge visibility (wireframe lines)."""
        self._show_edges = visible
        self.update()

    def edges_visible(self) -> bool:
        """Return current edge visibility state."""
        return self._show_edges

    def set_vertices_visible(self, visible: bool):
        """
        Configure vertices visible logic.
        
        Args:
            visible: Description of visible.
        
        """
        self._show_vertices = visible
        self.update()

    def vertices_visible(self) -> bool:
        """
        Vertices visible logic.
        
        Returns:
            Result of vertices_visible operation.
        """
        return self._show_vertices

    def set_dual_visible(self, visible: bool):
        """
        Configure dual visible logic.
        
        Args:
            visible: Description of visible.
        
        """
        self._show_dual = visible
        self.update()

    def dual_visible(self) -> bool:
        """
        Dual visible logic.
        
        Returns:
            Result of dual_visible operation.
        """
        return self._show_dual

    def set_measure_mode(self, enabled: bool):
        """
        Configure measure mode logic.
        
        Args:
            enabled: Description of enabled.
        
        """
        self._measure_mode = enabled
        self._selected_vertex_indices.clear()
        self._apex_vertex_index = None
        self._hovered_vertex_index = None
        self._loop_closed = False
        self.update()

    def measure_mode(self) -> bool:
        """
        Measure mode logic.
        
        Returns:
            Result of measure_mode operation.
        """
        return self._measure_mode

    def clear_measurement(self):
        """
        Clear measurement logic.
        
        """
        self._selected_vertex_indices.clear()
        self._apex_vertex_index = None
        self._loop_closed = False
        self.update()

    def selected_vertices(self) -> List[int]:
        """
        Selected vertices logic.
        
        Returns:
            Result of selected_vertices operation.
        """
        return list(self._selected_vertex_indices)

    # Signal emitted when measurement is complete (vertex1, vertex2, distance)
    measurement_complete = pyqtSignal(int, int, float)
    
    def set_color_theme(self, theme: ColorTheme) -> None:
        """Set the color theme and trigger a repaint."""
        self._color_theme = theme
        self.update()
    
    def get_color_theme(self) -> ColorTheme:
        """Get the current color theme."""
        return self._color_theme

    def set_show_angles(self, show: bool) -> None:
        """Toggle angle measurements display."""
        self._show_angles = show
        self.update()
    
    def set_angle_unit(self, unit: str) -> None:
        """Set angle display unit: 'degrees' or 'radians'."""
        self._angle_unit = unit
        self.update()
    
    def set_measure_precision(self, precision: int) -> None:
        """Set decimal precision for measurements."""
        self._measure_precision = max(0, min(8, precision))
        self.update()
    
    def set_snap_threshold(self, threshold: float) -> None:
        """Set pixel threshold for vertex snapping."""
        self._snap_threshold = max(5.0, min(50.0, threshold))
    
    def set_snap_to_canonical(self, snap: bool) -> None:
        """Toggle snapping to canonical shape vertices."""
        self._snap_to_canonical = snap
    
    def clear_measurements(self) -> None:
        """Clear all measurement selections."""
        self._selected_vertex_indices.clear()
        self._apex_vertex_index = None
        self._loop_closed = False
        self.update()


    def set_sphere_visible(self, kind: str, visible: bool):
        """
        Configure sphere visible logic.
        
        Args:
            kind: Description of kind.
            visible: Description of visible.
        
        """
        if kind in self._sphere_visibility:
            self._sphere_visibility[kind] = visible
            self.update()

    def sphere_visible(self, kind: str) -> bool:
        """
        Sphere visible logic.
        
        Args:
            kind: Description of kind.
        
        Returns:
            Result of sphere_visible operation.
        """
        return self._sphere_visibility.get(kind, False)

    def zoom_in(self):
        """
        Zoom in logic.
        
        """
        self._camera.distance = max(1.0, self._camera.distance * 0.85)
        self.update()

    def zoom_out(self):
        """
        Zoom out logic.
        
        """
        self._camera.distance = min(100.0, self._camera.distance / 0.85)
        self.update()
    
    # Aliases for unified viewer compatibility
    def set_show_faces(self, visible: bool):
        """Alias for set_faces_visible."""
        self.set_faces_visible(visible)
    
    def set_show_edges(self, visible: bool):
        """Alias for set_edges_visible."""
        self.set_edges_visible(visible)
    
    def set_show_vertices(self, visible: bool):
        """Alias for set_vertices_visible."""
        self.set_vertices_visible(visible)
    
    def set_elevation(self, degrees: float):
        """Set camera pitch (elevation)."""
        self._camera.pitch_deg = max(-89.0, min(89.0, degrees))
        self.update()
    
    def set_azimuth(self, degrees: float):
        """Set camera yaw (azimuth)."""
        self._camera.yaw_deg = degrees
        self.update()
    
    def fit_to_view(self):
        """Alias for fit_scene."""
        self.fit_scene()
    
    def take_snapshot(self):
        """Take a QPixmap snapshot of the current view."""
        from PyQt6.QtGui import QPixmap
        return self.grab()

    def fit_scene(self):
        """
        Fit scene logic.
        
        """
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
        """
        Paintevent logic.
        
        Args:
            a0: Description of a0.
        
        """
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._color_theme.background)

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
                z_sum = sum(v.z() for v in v_positions)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
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
            faces_to_draw.sort(key=lambda x: x[0])   # type: ignore[reportUnknownLambdaType, reportUnknownMemberType]

            # 3. Draw Faces (if enabled)
            if self._show_faces:
                painter.setPen(Qt.PenStyle.NoPen)
                for _, indices, intensity, original_idx in faces_to_draw:  # type: ignore[reportUnknownVariableType]
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
                        # Use theme default face color
                        base = self._color_theme.face_default
                        r = int(base.red() * intensity)
                        g = int(base.green() * intensity)
                        b = int(base.blue() * intensity)
                        alpha = base.alpha()

                    color = QColor(r, g, b, alpha)
                    painter.setBrush(color)
                    
                    qpoly = [p.toPoint() for p in poly] # drawPolygon needs QPoint  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
                    painter.drawPolygon(qpoly)

        # 4. Draw Edges (Wireframe overlay - if enabled)
        if self._show_edges:
            edge_pen = QPen(self._color_theme.edge, 1.0)
            painter.setPen(edge_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            for edge in payload.edges:
                if len(edge) != 2: continue
                i, j = edge
                painter.drawLine(screen_points[i], screen_points[j])

        # Store screen points for hit detection
        self._last_screen_points = screen_points
        
        # Calculate center point (geometric center of all vertices)
        center_point = None
        if payload.vertices and self._measure_mode:
            # Calculate 3D center
            cx = sum(v[0] for v in payload.vertices) / len(payload.vertices)
            cy = sum(v[1] for v in payload.vertices) / len(payload.vertices)
            cz = sum(v[2] for v in payload.vertices) / len(payload.vertices)
            # Project to screen space
            center_vec = QVector3D(cx, cy, cz)
            rotated_center = matrix * center_vec
            center_sx = rotated_center.x() * scale + pan_offset.x()
            center_sy = -rotated_center.y() * scale + pan_offset.y()
            center_point = QPointF(center_sx, center_sy)
            # Store for hit detection
            self._center_screen_point = center_point

        # 5. Draw Vertices (always show in measure mode, include center)
        if self._show_vertices or self._measure_mode:
            self._draw_vertices(painter, screen_points, payload, center_point)

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
        """
        Wheelevent logic.
        
        Args:
            a0: Description of a0.
        
        """
        if a0 is None:
            return
        event = a0
        delta = event.angleDelta().y() / 120
        self._camera.distance = max(1.0, self._camera.distance * (0.9 ** delta))
        self.update()

    def mousePressEvent(self, a0: QMouseEvent | None):  # pragma: no cover - GUI hook
        """
        Mousepressevent logic.
        
        Args:
            a0: Description of a0.
        
        """
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
        """
        Mousemoveevent logic.
        
        Args:
            a0: Description of a0.
        
        """
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
        """
        Mousereleaseevent logic.
        
        Args:
            a0: Description of a0.
        
        """
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
            ('incircle', 'inradius', self._color_theme.sphere_incircle),
            ('midsphere', 'midradius', self._color_theme.sphere_midsphere),
            ('circumsphere', 'circumradius', self._color_theme.sphere_circumsphere),
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
        pen = QPen(self._color_theme.edge, 1.0, Qt.PenStyle.DotLine)
        painter.setPen(pen)
        for edge in dual_payload.edges:
            if len(edge) != 2: continue
            i, j = edge
            if i < len(screen_points) and j < len(screen_points):
                painter.drawLine(screen_points[i], screen_points[j])
                
        # Draw Vertices (Small dots)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._color_theme.vertex_normal)
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
            painter.setBrush(self._color_theme.label_bg)
            painter.drawRoundedRect(background_rect, 6, 6)
            painter.setPen(self._color_theme.label_fg)
            baseline = QPointF(x, y + text_height - metrics.descent())
            painter.drawText(baseline, text)
        painter.restore()

    def _draw_axes(self, painter: QPainter):
        origin = QPointF(60, self.height() - 60)
        axis_length = 40
        pen = QPen(self._color_theme.edge, 1.5)
        painter.setPen(pen)
        painter.drawEllipse(origin, 3, 3)
        painter.setPen(QPen(self._color_theme.axis_x, 2.0))
        painter.drawLine(origin, QPointF(origin.x() + axis_length, origin.y()))
        painter.drawText(origin + QPointF(axis_length + 5, 0), "X")
        painter.setPen(QPen(self._color_theme.axis_y, 2.0))
        painter.drawLine(origin, QPointF(origin.x(), origin.y() - axis_length))
        painter.drawText(origin + QPointF(-10, -axis_length - 5), "Y")
        painter.setPen(QPen(self._color_theme.axis_z, 2.0))
        painter.drawLine(origin, QPointF(origin.x() - axis_length * 0.6, origin.y() + axis_length * 0.6))
        painter.drawText(origin + QPointF(-axis_length * 0.6 - 10, axis_length * 0.6 + 10), "Z")

    def _draw_gizmo(self, painter: QPainter):
        """Draw small orientation axes in corner."""
        size = 40
        padding = 20
        origin = QPointF(padding + size/2, self.height() - padding - size/2)
        
        # Simple static axes for now, TODO: rotate with view
        axis_length = 15
        painter.setPen(QPen(self._color_theme.axis_x, 2.0))
        painter.drawLine(origin, QPointF(origin.x() + axis_length, origin.y()))
        painter.drawText(origin + QPointF(axis_length + 5, 0), "X")
        painter.setPen(QPen(self._color_theme.axis_y, 2.0))
        painter.drawLine(origin, QPointF(origin.x(), origin.y() - axis_length))
        painter.drawText(origin + QPointF(-10, -axis_length - 5), "Y")
        painter.setPen(QPen(self._color_theme.axis_z, 2.0))
        painter.drawLine(origin, QPointF(origin.x() - axis_length * 0.6, origin.y() + axis_length * 0.6))
        painter.drawText(origin + QPointF(-axis_length * 0.6 - 10, axis_length * 0.6 + 10), "Z")

    def _draw_vertices(self, painter: QPainter, screen_points: List[QPointF], payload: SolidPayload, center_point: QPointF = None):
        """Draw vertex markers at each vertex, including optional center."""
        painter.save()
        
        # Draw Center Point (Index -1) if visible
        if center_point:
            i = -1
            if i in self._selected_vertex_indices:
                painter.setPen(QPen(self._color_theme.center_selected, 2.0))
                painter.setBrush(self._color_theme.center_selected)
                radius = 8
            elif i == self._hovered_vertex_index:
                painter.setPen(QPen(self._color_theme.center_hovered, 2.0))
                painter.setBrush(self._color_theme.center_hovered)
                radius = 7
            else:
                painter.setPen(QPen(self._color_theme.center_normal, 1.5))
                painter.setBrush(self._color_theme.center_normal)
                radius = 4
            
            painter.drawEllipse(center_point, radius, radius)
            if i in self._selected_vertex_indices or i == self._hovered_vertex_index:
                painter.setPen(self._color_theme.label_fg)
                font = painter.font()
                font.setPointSize(9)
                painter.setFont(font)
                painter.drawText(center_point + QPointF(10, -10), "C")

        # Draw Mesh Vertices
        # Optimization: If too many vertices, only draw selected/hovered to avoid clutter
        show_all_vertices = len(screen_points) <= 1000  # Increased from 200 to handle tessellated spheres

        for i, point in enumerate(screen_points):
            is_selected = i in self._selected_vertex_indices
            is_hovered = i == self._hovered_vertex_index
            
            if not show_all_vertices and not is_selected and not is_hovered:
                continue

            # Highlight selected vertices
            if is_selected:
                painter.setPen(QPen(self._color_theme.vertex_selected, 2.0))
                painter.setBrush(self._color_theme.vertex_selected)
                radius = 8
            elif is_hovered:
                painter.setPen(QPen(self._color_theme.vertex_hovered, 2.0))
                painter.setBrush(self._color_theme.vertex_hovered)
                radius = 7
            else:
                painter.setPen(QPen(self._color_theme.vertex_normal, 1.5))
                painter.setBrush(self._color_theme.vertex_normal)
                radius = 5
            
            painter.drawEllipse(point, radius, radius)

            if is_selected or is_hovered:
                painter.setPen(self._color_theme.label_fg)
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
        
        def get_pt_3d(idx):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
            """
            Retrieve pt 3d logic.
            
            Args:
                idx: Description of idx.
            
            Returns:
                Result of get_pt_3d operation.
            """
            return (0.0, 0.0, 0.0) if idx == -1 else payload.vertices[idx]
            
        def get_pt_screen(idx):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
             """
             Retrieve pt screen logic.
             
             Args:
                 idx: Description of idx.
             
             Returns:
                 Result of get_pt_screen operation.
             """
             return self._center_screen_point if idx == -1 else screen_points[idx]  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
        
        # Draw lines between consecutive vertices
        for i in range(num_verts - 1):
            v1_idx = self._selected_vertex_indices[i]
            v2_idx = self._selected_vertex_indices[i + 1]
            p1 = get_pt_screen(v1_idx)
            p2 = get_pt_screen(v2_idx)
            
            # Draw measurement line
            painter.setPen(QPen(self._color_theme.measure_line, 2.0, Qt.PenStyle.DashLine))
            painter.drawLine(p1, p2)
            
            # Calculate 3D distance for this segment
            v1_3d = get_pt_3d(v1_idx)
            v2_3d = get_pt_3d(v2_idx)
            segment_dist = distance_3d(v1_3d, v2_3d)
            total_distance += segment_dist
            
            # Draw segment distance at midpoint
            mid = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            self._draw_distance_label(painter, mid, f"{segment_dist:.{self._measure_precision}f}", small=True)
        
        # If loop is closed, draw closing edge and calculate area
        if self._loop_closed and num_verts >= 3:
            # Draw closing edge (last to first)
            v1_idx = self._selected_vertex_indices[-1]
            v2_idx = self._selected_vertex_indices[0]
            p1 = get_pt_screen(v1_idx)
            p2 = get_pt_screen(v2_idx)
            
            painter.setPen(QPen(self._color_theme.measure_line, 2.5, Qt.PenStyle.SolidLine))
            painter.drawLine(p1, p2)
            
            # Add closing edge distance
            v1_3d = get_pt_3d(v1_idx)
            v2_3d = get_pt_3d(v2_idx)
            closing_dist = distance_3d(v1_3d, v2_3d)
            total_distance += closing_dist
            
            mid = QPointF((p1.x() + p2.x()) / 2, (p1.y() + p2.y()) / 2)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            self._draw_distance_label(painter, mid, f"{closing_dist:.{self._measure_precision}f}", small=True)
            
            # Calculate polygon area (handles 0,0,0 if present)
            poly_verts = [get_pt_3d(i) for i in self._selected_vertex_indices]
            area = polygon_area_3d(poly_verts)
            
            # If Apex selected, calculate Volume and Surface Area
            if self._apex_vertex_index is not None:
                apex = get_pt_3d(self._apex_vertex_index)
                apex_pt = get_pt_screen(self._apex_vertex_index)
                
                # Draw edges to apex
                painter.setPen(QPen(self._color_theme.measure_line, 2.0, Qt.PenStyle.DashLine))
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
                base_center_x = sum(get_pt_screen(i).x() for i in self._selected_vertex_indices) / num_verts  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
                base_center_y = sum(get_pt_screen(i).y() for i in self._selected_vertex_indices) / num_verts  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
                base_center = QPointF(base_center_x, base_center_y)
                
                label_pos = QPointF(
                    (base_center.x() + apex_pt.x()) / 2,
                    (base_center.y() + apex_pt.y()) / 2
                )
                
                # Box for statistics
                stats_text = (f"Base Area: {area:.{self._measure_precision}f}\n"
                              f"Surface: {total_surface_area:.{self._measure_precision}f}\n"
                              f"Volume: {volume:.{self._measure_precision}f}")
                self._draw_multiline_label(painter, label_pos, stats_text)
                
            else:
                # Just draw base area label
                center_x = sum(get_pt_screen(i).x() for i in self._selected_vertex_indices) / num_verts  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
                center_y = sum(get_pt_screen(i).y() for i in self._selected_vertex_indices) / num_verts  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
                center = QPointF(center_x, center_y)
                self._draw_area_label(painter, center, area)
        
        # Show perimeter (total distance) at bottom
        if num_verts >= 3:
            label = f"Selection Perimeter: {total_distance:.{self._measure_precision}f}"
            total_pos = QPointF(self.width() / 2, self.height() - 30)
            self._draw_distance_label(painter, total_pos, label, small=False)
        
        # Show selection summary at top-left
        if num_verts >= 2:
            self._draw_selection_summary(painter, num_verts)
        
        # Draw angles if enabled and we have a closed polygon
        if self._show_angles and self._loop_closed and num_verts >= 3:
            self._draw_angles(painter, screen_points, payload)
        
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
        painter.setBrush(self._color_theme.measure_text_bg)
        painter.drawRoundedRect(bg_rect, 6, 6)
        
        # Text
        painter.setPen(self._color_theme.measure_text_fg)
        painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, text)

    def _draw_area_label(self, painter: QPainter, pos: QPointF, area: float):
        """Draw an area label with a distinct appearance."""
        text = f"Selection Area: {area:.{self._measure_precision}f}"
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
        painter.setBrush(self._color_theme.measure_area_bg)
        painter.drawRoundedRect(bg_rect, 8, 8)
        
        # White text
        painter.setPen(self._color_theme.measure_area_fg)
        painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, text)
    
    def _draw_selection_summary(self, painter: QPainter, num_verts: int):
        """Draw selection summary at top-left showing what's being measured."""
        # Determine selection type
        if not self._loop_closed:
            if num_verts == 2:
                summary = "Selection: Distance"
            else:
                summary = f"Selection: Path ({num_verts} points)"
        else:
            if num_verts == 3:
                summary = "Selection: Triangle (3 points)"
            elif num_verts == 4:
                summary = "Selection: Quadrilateral (4 points)"
            else:
                summary = f"Selection: Polygon ({num_verts} points)"
        
        # Draw at top-left with small font
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(summary)
        text_height = metrics.height()
        
        # Position in top-left corner with padding
        pos = QPointF(15 + text_width/2, 15 + text_height/2)
        
        bg_rect = QRectF(10, 10, text_width + 10, text_height + 6)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._color_theme.label_bg)
        painter.drawRoundedRect(bg_rect, 4, 4)
        
        painter.setPen(self._color_theme.label_fg)
        painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, summary)

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
        painter.setBrush(self._color_theme.measure_volume_bg)
        painter.drawRoundedRect(bg_rect, 8, 8)
        
        # White text
        painter.setPen(self._color_theme.measure_volume_fg)
        painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, text)

    def _find_vertex_at_point(self, pos: QPoint, threshold: float = None) -> Optional[int]:
        """Find the nearest vertex to the given screen position, checking center too."""
        if not self._last_screen_points:
            return None
        
        if threshold is None:
            threshold = self._snap_threshold
        
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
            c_pt = self._center_screen_point  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
            dx = pos.x() - c_pt.x()
            dy = pos.y() - c_pt.y()
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist < min_dist:
                # Center is closer than any vertex
                return -1
                
        return nearest_idx
    
    def _draw_angles(self, painter: QPainter, screen_points: List[QPointF], payload: SolidPayload):
        """Draw angle measurements at each vertex of the closed polygon."""
        if not self._selected_vertex_indices or len(self._selected_vertex_indices) < 3:
            return
        
        import math
        
        painter.save()
        num_verts = len(self._selected_vertex_indices)
        
        # Helper to get 3D position (handles center point at index -1)
        def get_pt_3d(idx):
            if idx == -1:
                # Return geometric center
                cx = sum(v[0] for v in payload.vertices) / len(payload.vertices)
                cy = sum(v[1] for v in payload.vertices) / len(payload.vertices)
                cz = sum(v[2] for v in payload.vertices) / len(payload.vertices)
                return (cx, cy, cz)
            return payload.vertices[idx]
        
        for i in range(num_verts):
            try:
                # Get three consecutive vertices
                prev_idx = self._selected_vertex_indices[(i - 1) % num_verts]
                curr_idx = self._selected_vertex_indices[i]
                next_idx = self._selected_vertex_indices[(i + 1) % num_verts]
                
                # Get 3D positions (handles center point)
                prev_3d = get_pt_3d(prev_idx)
                curr_3d = get_pt_3d(curr_idx)
                next_3d = get_pt_3d(next_idx)
                
                # Calculate vectors from current vertex
                v1 = (prev_3d[0] - curr_3d[0], prev_3d[1] - curr_3d[1], prev_3d[2] - curr_3d[2])
                v2 = (next_3d[0] - curr_3d[0], next_3d[1] - curr_3d[1], next_3d[2] - curr_3d[2])
                
                # Calculate angle using dot product
                dot = v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
                mag1 = math.sqrt(v1[0]**2 + v1[1]**2 + v1[2]**2)
                mag2 = math.sqrt(v2[0]**2 + v2[1]**2 + v2[2]**2)
                
                if mag1 < 0.0001 or mag2 < 0.0001:
                    continue
                
                cos_angle = dot / (mag1 * mag2)
                cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp to valid range
                angle_rad = math.acos(cos_angle)
                
                # Convert to desired unit
                if self._angle_unit == "degrees":
                    angle_value = math.degrees(angle_rad)
                    unit_str = "°"
                else:
                    angle_value = angle_rad
                    unit_str = " rad"
                
                # Get screen position (handles center point)
                def get_pt_screen(idx):
                    return self._center_screen_point if idx == -1 else screen_points[idx]
                
                curr_screen = get_pt_screen(curr_idx)
                prev_screen = get_pt_screen(prev_idx)
                next_screen = get_pt_screen(next_idx)
                
                # Calculate screen space vectors for arc drawing
                dx1 = prev_screen.x() - curr_screen.x()
                dy1 = prev_screen.y() - curr_screen.y()
                dx2 = next_screen.x() - curr_screen.x()
                dy2 = next_screen.y() - curr_screen.y()
                
                # Arc radius
                arc_radius = 30.0
                len1 = math.sqrt(dx1*dx1 + dy1*dy1)
                len2 = math.sqrt(dx2*dx2 + dy2*dy2)
                
                if len1 < 0.1 or len2 < 0.1:
                    continue
                
                # Calculate start and span angles in screen space
                start_angle = math.atan2(-dy1, dx1)  # Negative y because screen y is inverted
                end_angle = math.atan2(-dy2, dx2)
                
                # Ensure we take the smaller arc
                angle_diff = end_angle - start_angle
                if angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                elif angle_diff < -math.pi:
                    angle_diff += 2 * math.pi
                
                # Convert to Qt's angle format (degrees * 16)
                qt_start = math.degrees(start_angle) * 16
                qt_span = math.degrees(angle_diff) * 16
                
                # Draw arc
                painter.setPen(QPen(self._color_theme.angle_arc, 2.0))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                arc_rect = QRectF(
                    curr_screen.x() - arc_radius,
                    curr_screen.y() - arc_radius,
                    arc_radius * 2,
                    arc_radius * 2
                )
                painter.drawArc(arc_rect, int(qt_start), int(qt_span))
                
                # Draw angle label slightly offset from vertex
                label_offset = 45.0
                mid_angle = start_angle + angle_diff / 2
                label_x = curr_screen.x() + label_offset * math.cos(mid_angle)
                label_y = curr_screen.y() - label_offset * math.sin(mid_angle)
                label_pos = QPointF(label_x, label_y)
                
                self._draw_angle_label(painter, label_pos, f"{angle_value:.{self._measure_precision}f}{unit_str}")
            except Exception as e:
                # Skip this angle if there's any error
                logger.debug(f"Error drawing angle at vertex {i}: {e}")
                continue
        
        painter.restore()
    
    def _draw_angle_label(self, painter: QPainter, pos: QPointF, text: str):
        """Draw an angle label with themed colors."""
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(text)
        text_height = metrics.height()
        
        # Background
        bg_rect = QRectF(pos.x() - text_width/2 - 4, pos.y() - text_height/2 - 2,
                         text_width + 8, text_height + 4)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._color_theme.angle_text_bg)
        painter.drawRoundedRect(bg_rect, 4, 4)
        
        # Text
        painter.setPen(self._color_theme.angle_text_fg)
        painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, text)