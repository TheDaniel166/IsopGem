"""
ADYTON OPENGL VIEWPORT

Depth-buffered viewport using QOpenGLWidget + PyOpenGL. This avoids manual
painter sorting by relying on the GL Z-buffer.
"""
from typing import List

from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtCore import Qt, QPoint, QPointF
from PyQt6.QtGui import (
    QSurfaceFormat,
    QMatrix4x4,
    QMouseEvent,
    QWheelEvent,
    QPainter,
    QFont,
    QColor,
    QVector3D,
    QVector4D,
    QPolygonF,
    QTransform,
)
from OpenGL.GL import (
    glClearColor,
    glClear,
    glEnable,
    glDisable,
    glViewport,
    glMatrixMode,
    glLoadIdentity,
    glMultMatrixf,
    glBegin,
    glEnd,
    glColor3f,
    glVertex3f,
    glPointSize,
    glLineWidth,
    glBlendFunc,
    glDepthMask,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_BLEND,
    GL_SRC_ALPHA,
    GL_ONE,
    GL_PROJECTION,
    GL_MODELVIEW,
    GL_TRIANGLES,
    GL_LINE_LOOP,
    GL_POINTS,
)

from pillars.adyton.models.geometry_types import Object3D, Face3D
from pillars.adyton.models.prism import SevenSidedPrism
from ...constants import COLOR_GOLD, COLOR_SILVER
from .camera import AdytonCamera


class AdytonGLViewport(QOpenGLWidget):
    """Depth-buffered Sanctuary viewport."""

    def __init__(self, parent=None, wall_index: int | None = None):
        super().__init__(parent)

        fmt = QSurfaceFormat()
        fmt.setRenderableType(QSurfaceFormat.RenderableType.OpenGL)
        fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.NoProfile)
        fmt.setVersion(2, 1)  # Broad compatibility
        fmt.setDepthBufferSize(24)
        self.setFormat(fmt)

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.camera = AdytonCamera()
        self.wall_index = wall_index
        if wall_index is None:
            self.scene_objects: List[Object3D] = SevenSidedPrism.build()
            self.draw_labels = False  # disable overlays by default (stability)
        else:
            self.scene_objects = SevenSidedPrism.build_wall(wall_index)
            self.draw_labels = False  # wall-only view; no overlays/floor
        # Starfield fully disabled; no data allocated
        self.star_service = None
        self.star_points = []

        self.last_pos: QPoint = QPoint()
        self.mouse_pressed: bool = False

    # ------------------------------------------------------------------
    # GL lifecycle
    # ------------------------------------------------------------------
    def initializeGL(self):
        glClearColor(0.02, 0.02, 0.03, 1.0)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, w: int, h: int):
        glViewport(0, 0, max(1, w), max(1, h))

    def paintGL(self):
        glClear(int(GL_COLOR_BUFFER_BIT) | int(GL_DEPTH_BUFFER_BIT))

        aspect = self.width() / max(1.0, float(self.height()))
        projection = QMatrix4x4()
        projection.perspective(self.camera.fov, aspect, 10.0, 5000.0)

        view = self.camera.view_matrix()

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMultMatrixf(projection.data())

        for obj in self.scene_objects:
            model = self._model_matrix(obj)
            mv = view * model

            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            glMultMatrixf(mv.data())

            self._draw_object(obj)

        if self.draw_labels:
            self._draw_overlays(projection, view)

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------
    def mousePressEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        if event is None:
            return
        self.last_pos = event.position().toPoint()
        self.mouse_pressed = True

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        if event is None:
            return
        self.mouse_pressed = False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # type: ignore[override]
        if event is None or not self.mouse_pressed:
            return
        pos = event.position().toPoint()
        dx = pos.x() - self.last_pos.x()
        dy = pos.y() - self.last_pos.y()
        self.last_pos = pos

        orbit_speed = 0.5
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.camera.orbit(-dx * orbit_speed, -dy * orbit_speed)
            self.update()
        elif event.buttons() & Qt.MouseButton.RightButton:
            self.camera.pan(-dx, dy)
            self.update()

    def wheelEvent(self, event: QWheelEvent) -> None:  # type: ignore[override]
        if event is None:
            return
        delta = event.angleDelta().y()
        self.camera.zoom(delta * 0.5)
        self.update()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _model_matrix(self, obj: Object3D) -> QMatrix4x4:
        m = QMatrix4x4()
        m.translate(obj.position)
        m.rotate(obj.rotation.x(), 1, 0, 0)
        m.rotate(obj.rotation.y(), 0, 1, 0)
        m.rotate(obj.rotation.z(), 0, 0, 1)
        m.scale(obj.scale)
        return m

    def _draw_object(self, obj: Object3D):
        for face in obj.faces:
            self._draw_face(face)

    # ------------------------------------------------------------------
    # Overlay text (Greek letters on vowel ring)
    # ------------------------------------------------------------------
    def _draw_overlays(self, projection: QMatrix4x4, view: QMatrix4x4):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        
        # KILL RAYS: Ensure nothing draws outside the widget's bounds
        painter.setClipRect(self.rect())
        
        # Use a standard font for Greek support
        font = QFont("DejaVu Sans", 36, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(COLOR_GOLD)

        for obj in self.scene_objects:
            # Check if object has valid label metadata
            positions = getattr(obj, "label_positions", None)
            if not positions:
                continue

            planets = getattr(obj, "label_planets", [])
            model = self._model_matrix(obj)

            for idx, pos in enumerate(positions):
                planet = planets[idx % len(planets)] if planets else ""
                greek = self._planet_to_greek(planet)
                if not greek:
                    continue

                # Local orientation for the slanted surface
                # radial_dir points horizontally away from center
                radial_dir = QVector3D(pos.x(), 0, pos.z()).normalized()
                
                # The 'slant' vector points from bottom (inner) to top (outer)
                # Outer is at y=0, inner is at y=-10.
                # So the vector 'up the slant' has a positive Y and positive radial component.
                # We can derive it by assuming it's orthogonal to the tangent.
                right_vec = QVector3D.crossProduct(QVector3D(0, 1, 0), radial_dir).normalized()
                
                # Calculate slant direction: diagonal from inner-bottom to outer-top
                # Vowel ring width is ~19 units, depth is 10.
                # We approximate the slant 'up' vector:
                up_vec = (radial_dir * 1.9 + QVector3D(0, 1.0, 0)).normalized()
                
                # Letter size on the slant
                h_size = 14.0
                w_size = 14.0
                
                # Quad corners on the diagonal plane
                p_bottom_left  = pos - (w_size/2)*right_vec - (h_size/2)*up_vec
                p_bottom_right = pos + (w_size/2)*right_vec - (h_size/2)*up_vec
                p_top_right    = pos + (w_size/2)*right_vec + (h_size/2)*up_vec
                p_top_left     = pos - (w_size/2)*right_vec + (h_size/2)*up_vec

                # Project to screen
                sp0 = self._project_point(p_bottom_left,  model, view, projection)
                sp1 = self._project_point(p_bottom_right, model, view, projection)
                sp2 = self._project_point(p_top_right,    model, view, projection)
                sp3 = self._project_point(p_top_left,     model, view, projection)

                if any(p is None for p in [sp0, sp1, sp2, sp3]):
                    continue

                # Sanity check: ensure the quad has some area and is not too extreme
                # (prevents 'golden rays' when viewed edge-on)
                target_quad = QPolygonF([
                    QPointF(sp0), QPointF(sp1), QPointF(sp2), QPointF(sp3)
                ])
                
                # Simple bounding rect check to avoid massive overflows
                br = target_quad.boundingRect()
                if br.width() > self.width() * 2 or br.height() > self.height() * 2:
                    continue
                if br.width() < 1 or br.height() < 1:
                    continue

                rect_size = 200
                source_rect = QPolygonF([
                    QPointF(0, rect_size),          # Bottom Left
                    QPointF(rect_size, rect_size),  # Bottom Right
                    QPointF(rect_size, 0),          # Top Right
                    QPointF(0, 0)                  # Top Left
                ])

                transform = QTransform()
                if QTransform.quadToQuad(source_rect, target_quad, transform):
                    # DETECTOR OF DISTORTION:
                    # If the transform is nearly singular or wildly scaled, skip it.
                    # This prevents the 'Golden Rays' from degenerate perspective.
                    if abs(transform.determinant()) < 1e-6:
                        continue
                        
                    painter.save()
                    painter.setTransform(transform, True)
                    temp_font = QFont("DejaVu Sans", 120, QFont.Weight.Bold)
                    painter.setFont(temp_font)
                    painter.drawText(0, 0, rect_size, rect_size, Qt.AlignmentFlag.AlignCenter, greek)
                    painter.restore()

        painter.end()

    def _project_point(self, point: QVector3D, model: QMatrix4x4, view: QMatrix4x4, proj: QMatrix4x4):
        vec = QVector4D(point.x(), point.y(), point.z(), 1.0)
        clip = proj * view * model * vec
        w = clip.w()
        
        # Clip if behind near plane or degenerate
        # Tightened from 10.0 to 15.0 to hide distant/distorted text
        if w < 15.0:
            return None
            
        ndc_x = clip.x() / w
        ndc_y = clip.y() / w
        
        # TIGHTENED SEAL: Direct NDC clip
        # If any point is even slightly outside the NDC hull [ -1, 1 ], 
        # we discard the label to prevent perspective overflow.
        if abs(ndc_x) > 1.0 or abs(ndc_y) > 1.0:
            return None
            
        screen_x = (ndc_x * 0.5 + 0.5) * self.width()
        screen_y = (1.0 - (ndc_y * 0.5 + 0.5)) * self.height()
        return QPoint(int(screen_x), int(screen_y))

    def _planet_to_greek(self, planet: str) -> str:
        """Chaldean order vowel assignment: Mercury=Α, …, Saturn=Ω."""
        mapping = {
            "mercury": "Α",  # Alpha
            "moon": "Ε",     # Epsilon
            "venus": "Η",    # Eta
            "sun": "Ι",      # Iota
            "mars": "Ο",     # Omicron
            "jupiter": "Υ",  # Upsilon
            "saturn": "Ω",   # Omega
        }
        return mapping.get(planet.lower(), "")

    def _draw_face(self, face: Face3D):
        verts = face.vertices
        if len(verts) < 3:
            return

        # Simple ambient + directional shading
        if face.shading:
            light_dir = QVector3D(0.25, -0.6, 0.75).normalized()
            v0, v1, v2 = verts[0], verts[1], verts[2]
            normal = QVector3D.crossProduct(v1 - v0, v2 - v0).normalized()
            ambient = 0.35
            diffuse = max(0.0, QVector3D.dotProduct(normal, light_dir))
            shade = min(1.0, ambient + diffuse * 0.75)
        else:
            shade = 1.0

        col = face.color
        glColor3f(col.redF() * shade, col.greenF() * shade, col.blueF() * shade)

        glBegin(GL_TRIANGLES)
        if len(verts) == 3:
            for v in verts:
                glVertex3f(v.x(), v.y(), v.z())
        elif len(verts) == 4:
            v0, v1, v2, v3 = verts
            glVertex3f(v0.x(), v0.y(), v0.z())
            glVertex3f(v1.x(), v1.y(), v1.z())
            glVertex3f(v2.x(), v2.y(), v2.z())

            glVertex3f(v0.x(), v0.y(), v0.z())
            glVertex3f(v2.x(), v2.y(), v2.z())
            glVertex3f(v3.x(), v3.y(), v3.z())
        else:
            v0 = verts[0]
            for i in range(1, len(verts) - 1):
                v1 = verts[i]
                v2 = verts[i + 1]
                glVertex3f(v0.x(), v0.y(), v0.z())
                glVertex3f(v1.x(), v1.y(), v1.z())
                glVertex3f(v2.x(), v2.y(), v2.z())
        glEnd()

        # Outline for the face (only if different, for 'solidity')
        oc = face.outline_color
        if oc != col:
            glColor3f(oc.redF(), oc.greenF(), oc.blueF())
            glLineWidth(2.0)
            glBegin(GL_LINE_LOOP)
            for v in verts:
                glVertex3f(v.x(), v.y(), v.z())
            glEnd()

    # Starfield removed (kept stub for future use)
    def _draw_starfield(self, projection: QMatrix4x4, view: QMatrix4x4):
        return
