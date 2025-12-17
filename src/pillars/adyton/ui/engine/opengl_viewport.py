"""
ADYTON OPENGL VIEWPORT

Depth-buffered viewport using QOpenGLWidget + PyOpenGL. This avoids manual
painter sorting by relying on the GL Z-buffer.
"""
from typing import List

from PyQt6.QtOpenGLWidgets import QOpenGLWidget
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
)
from PyQt6.QtCore import Qt, QPoint
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
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_PROJECTION,
    GL_MODELVIEW,
    GL_TRIANGLES,
    GL_LINE_LOOP,
)

from pillars.adyton.models.geometry_types import Object3D, Face3D
from pillars.adyton.models.prism import SevenSidedPrism
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
            # Use flat wall builder for front-facing isolated view
            self.scene_objects = SevenSidedPrism.build_wall_flat(wall_index)
            self.draw_labels = False
            # Configure camera to face wall front-on
            # Wall is at origin, interior faces toward -Z
            # Camera looks from -Z toward origin
            from pillars.adyton.constants import WALL_WIDTH_INCHES, WALL_HEIGHT_INCHES
            self.camera.target = QVector3D(0, WALL_HEIGHT_INCHES / 2, 0)
            self.camera.radius = max(WALL_WIDTH_INCHES, WALL_HEIGHT_INCHES) * 1.2
            self.camera.theta = 90.0  # horizontal
            self.camera.phi = 180.0   # looking from -Z toward +Z

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

        # DEBUG: Draw a test swatch in the corner to verify teal color
        # This should show the exact color that cell (0,0) should display
        self._draw_test_swatch()

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
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        painter.setFont(QFont("DejaVu Sans", 16, QFont.Weight.Bold))

        # Planet names for wall labels
        planet_names = ["Sun", "Mercury", "Moon", "Venus", "Mars", "Jupiter", "Saturn"]

        for obj in self.scene_objects:
            # Draw wall labels (planet names above walls)
            if hasattr(obj, "wall_index"):
                wall_idx = obj.wall_index
                planet_name = planet_names[wall_idx % len(planet_names)]
                
                # Get wall center position (top of wall)
                model = self._model_matrix(obj)
                # Project the top-center of the wall
                wall_top = QVector3D(0, 8.0, 0)  # Top center of wall (8 units = wall height)
                screen_pt = self._project_point(wall_top, model, view, projection)
                if screen_pt:
                    # Draw label with white text and black outline
                    painter.setPen(QColor(0, 0, 0))
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx != 0 or dy != 0:
                                painter.drawText(screen_pt.x() + dx, screen_pt.y() + dy, planet_name)
                    painter.setPen(QColor(255, 255, 255))
                    painter.drawText(screen_pt, planet_name)

            # Existing vowel ring labels
            if not hasattr(obj, "label_positions"):
                continue

            positions = getattr(obj, "label_positions", [])
            colors = getattr(obj, "label_colors", [])
            planets = getattr(obj, "label_planets", [])
            model = self._model_matrix(obj)

            for idx, pos in enumerate(positions):
                planet = planets[idx % len(planets)] if planets else ""
                greek = self._planet_to_greek(planet)
                if not greek:
                    continue

                ring_color = colors[idx % len(colors)] if colors else QColor(255, 255, 255)
                flash = QColor(255 - ring_color.red(), 255 - ring_color.green(), 255 - ring_color.blue())

                screen_pt = self._project_point(pos, model, view, projection)
                if screen_pt is None:
                    continue
                painter.setPen(flash)
                painter.drawText(screen_pt, greek)

        painter.end()



    def _project_point(self, point: QVector3D, model: QMatrix4x4, view: QMatrix4x4, proj: QMatrix4x4):
        vec = QVector4D(point.x(), point.y(), point.z(), 1.0)
        clip = proj * view * model * vec
        w = clip.w()
        if w == 0:
            return None
        ndc_x = clip.x() / w
        ndc_y = clip.y() / w
        if abs(ndc_x) > 1.2 or abs(ndc_y) > 1.2:
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

        col = face.color
        
        # Pass QColor values directly - they're already in sRGB space
        # which matches the monitor's color space for fixed-function OpenGL
        glColor3f(col.redF(), col.greenF(), col.blueF())

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

        # Outline for the face to emphasize frustum edges
        glColor3f(0.0, 0.0, 0.0)
        glLineWidth(1.0)
        glBegin(GL_LINE_LOOP)
        for v in verts:
            glVertex3f(v.x(), v.y(), v.z())
        glEnd()

