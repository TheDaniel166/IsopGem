"""
THE FLOOR PLAN OF THE ADYTON
"As below, so it is laid in the dust."

A dedicated viewport for the Precision Floor.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QVector3D

from .engine.opengl_viewport import AdytonGLViewport
from ..models.floor import FloorGeometry
from ..models.throne import ThroneGeometry

class FloorPlanViewport(AdytonGLViewport):
    """Specialized GL Viewport for the Floor Plan."""
    def __init__(self, parent=None):
        # We don't want the full prism, so we'll customize scene_objects later
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        
        # Manifest floor and central throne
        # Lift throne slightly (-9.9) to avoid z-fighting with sunken floor (-10.0)
        self.scene_objects = [
            FloorGeometry.build(),
            ThroneGeometry.build(y_offset=-9.9)
        ]
        self.draw_labels = True # Show the Greek Vowels
        
        # Orient camera top-down (0.1 deg to avoid absolute zenith artifacts)
        self.camera.theta = 0.1
        self.camera.phi = 0.0
        self.camera.radius = 800.0
        self.camera.target = QVector3D(0, -10.0, 0)

class FloorPlanWindow(QWidget):
    """Window container for the Floor Plan visualization."""
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Adyton Floor Plan - The Foundation of 185")
        self.resize(800, 800)
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header Info
        header = QLabel("THE PRECISION FOUNDATION (185/166 Units)")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background: #0f172a;
                color: #94a3b8;
                font-weight: bold;
                padding: 8px;
                border-bottom: 2px solid #1e293b;
            }
        """)
        layout.addWidget(header, 0) # Stretch 0
        
        # The Viewport
        self.viewport = FloorPlanViewport(self)
        layout.addWidget(self.viewport, 1) # Stretch 1
        
        # Footer Legend
        footer = QLabel("Outer: 185 (Perimeter) | Inner: 166 (Katalysis) | Differential: 19 (Vowel Ring)")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("""
            QLabel {
                background: #0f172a;
                color: #64748b;
                font-size: 9pt;
                padding: 6px;
                border-top: 1px solid #1e293b;
            }
        """)
        layout.addWidget(footer, 0) # Stretch 0