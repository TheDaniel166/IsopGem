"""
THE PAINTER OF THE ADYTON (Renderer)

"Colors and Forms, projected on the Screen of the Mind."

This module implements the Software Rasterizer using the Painter's Algorithm.
It projects 3D faces onto the 2D QPainter canvas.
"""
from dataclasses import dataclass
from typing import List, Tuple
from PyQt6.QtCore import QPointF, QRect
from PyQt6.QtGui import QPainter, QPolygonF, QColor, QMatrix4x4, QVector3D, QVector4D, QBrush, QPen
from .scene import AdytonScene, Face3D
from .camera import AdytonCamera

@dataclass
class ProjectedFace:
    """A face that has been projected to screen coordinates."""
    polygon: QPolygonF
    depth: float
    color: QColor
    outline_color: QColor

class AdytonRenderer:
    def __init__(self):
        pass

    def render(self, painter: QPainter, scene: AdytonScene, camera: AdytonCamera, viewport: QRect):
        """
        Main render loop.
        """
        # 1. Setup Matrices
        view_matrix = camera.view_matrix()
        
        projection_matrix = QMatrix4x4()
        aspect_ratio = viewport.width() / max(1, viewport.height())
        projection_matrix.perspective(camera.fov, aspect_ratio, 10.0, 5000.0)
        
        # Combined VP Matrix
        vp_matrix = projection_matrix * view_matrix
        
        width = viewport.width()
        height = viewport.height()
        half_w = width / 2.0
        half_h = height / 2.0

        # 2. Collect and Project Faces
        faces = scene.get_all_faces()
        projected_faces: List[ProjectedFace] = []

        camera_pos = camera.position()

        for face in faces:
            # Simple Backface Culling (Optional, but good for optimization)
            # Check normal dot view_dir? 
            # For now, we skip culling to support translucent objects later or open shapes.
            
            # Distance from camera to centroid (for sorting)
            # We use the Z value in View Space for more accurate sorting usually,
            # but distance to camera is a decent approximation for non-intersecting convex objects.
            dist = camera_pos.distanceToPoint(face.centroid)
            
            poly = QPolygonF()
            all_valid = True
            
            for v in face.vertices:
                # MVP Transform
                vec4 = QVector4D(v.x(), v.y(), v.z(), 1.0)
                clip_space = vp_matrix * vec4
                w = clip_space.w()
                
                # Near plane clipping (Simple W check)
                if w <= 0.1: 
                    all_valid = False
                    break
                
                # NDC Division
                ndc_x = clip_space.x() / w
                ndc_y = clip_space.y() / w
                
                # Viewport Transform (Flip Y for screen coords)
                screen_x = (ndc_x * half_w) + half_w
                screen_y = half_h - (ndc_y * half_h) # In Qt, Y is down
                
                poly.append(QPointF(screen_x, screen_y))
            
            if all_valid:
                projected_faces.append(ProjectedFace(poly, dist, face.color, face.outline_color))

        # 3. Sort by Depth (Painter's Algorithm: Furthest first)
        projected_faces.sort(key=lambda f: f.depth, reverse=True)

        # 4. Draw
        if scene.background_color:
            painter.fillRect(viewport, scene.background_color)

        # Antialiasing is usually set by the widget
        for p_face in projected_faces:
            painter.setBrush(QBrush(p_face.color))
            painter.setPen(QPen(p_face.outline_color, 1.0))
            painter.drawPolygon(p_face.polygon)
