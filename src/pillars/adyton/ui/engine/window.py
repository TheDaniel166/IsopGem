"""
THE PORTAL OF THE ADYTON (View Window)

"Through the open door within the House of Tum."

This widget hosts the Adyton Engine and handles user interaction.
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPaintEvent, QPainter, QMouseEvent, QWheelEvent, QVector3D

from .scene import AdytonScene
from .camera import AdytonCamera
from .renderer import AdytonRenderer
from pillars.adyton.models.prism import SevenSidedPrism
from pillars.adyton.models.throne import ThroneGeometry
from pillars.adyton.constants import WALL_HEIGHT_INCHES

class AdytonSanctuaryEngine(QWidget):
    """
    The 3D Viewport for the Sanctuary.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Engine Components
        self.scene = AdytonScene()
        self.camera = AdytonCamera()
        self.renderer = AdytonRenderer()
        
        # Interaction State
        self.last_pos = QPoint()
        self.mouse_pressed = False
        
        # Manifest the Sanctuary Components
        self._init_sanctuary()

    def _init_sanctuary(self):
        """Initializes the Adyton Vault, Floor, and Throne."""
        # 1. Build the Prism (Walls, Corners, Floor)
        objects = SevenSidedPrism.build()
        for obj in objects:
            self.scene.add_object(obj)
            
        # 2. Build and Place the Throne of the Charioteer
        # Sits at center (0,0) on the sunken floor (y=-10)
        # Sits at -9.9 to avoid z-fighting with the floor face.
        throne = ThroneGeometry.build(y_offset=-9.9)
        self.scene.add_object(throne)
        
        # 3. Adjust Camera
        # Look at the Throne center
        self.camera.target = QVector3D(0, 0, 0) 
        self.camera.radius = 1200 
        self.camera.theta = 45    # Looking down into the sanctuary

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        self.renderer.render(painter, self.scene, self.camera, self.rect())
        
    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------
    def mousePressEvent(self, event: QMouseEvent):
        self.last_pos = event.position().toPoint()
        self.mouse_pressed = True

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.mouse_pressed = False

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.mouse_pressed:
            return
            
        pos = event.position().toPoint()
        dx = pos.x() - self.last_pos.x()
        dy = pos.y() - self.last_pos.y()
        self.last_pos = pos
        
        # Sensitivity
        orbit_speed = 0.5
        
        if event.buttons() & Qt.MouseButton.LeftButton:
            # Orbit
            self.camera.orbit(-dx * orbit_speed, -dy * orbit_speed)
            self.update()
        elif event.buttons() & Qt.MouseButton.RightButton:
            # Pan
            self.camera.pan(-dx, dy)
            self.update()

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        self.camera.zoom(delta * 0.5)
        self.update()
