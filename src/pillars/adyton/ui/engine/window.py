"""
THE PORTAL OF THE ADYTON (View Window)

"Through the open door within the House of Tum."

This widget hosts the Adyton Engine and handles user interaction.
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QPaintEvent, QPainter, QMouseEvent, QWheelEvent, QVector3D, QColor

from .scene import AdytonScene, Object3D, Face3D
from .camera import AdytonCamera
from .renderer import AdytonRenderer
from pillars.adyton.models.prism import SevenSidedPrism
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
        
        # Test Geometry (Will be replaced by Phase 2 models)
        self._init_test_cube()

    def _init_test_cube(self):
        """Initializes the Adyton Vault."""
        # 1. Build the Prism (List of Ashlar Blocks)
        blocks = SevenSidedPrism.build()
        for block in blocks:
            self.scene.add_object(block)
        
        # 2. Adjust Camera to see it
        # Center is at (0, 0, 0). Height is ~500. Radius ~350,
        # We want to be inside or outside?
        # Let's start OUTSIDE to see the structure.
        self.camera.target = QVector3D(0, WALL_HEIGHT_INCHES / 2, 0) # Look at center height
        self.camera.radius = 1200 # Far enough back
        self.camera.theta = 70    # Low angle

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
