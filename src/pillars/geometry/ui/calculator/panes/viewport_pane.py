"""
Viewport Pane - The Visual Canvas.
Center panel hosting the 2D/3D geometry visualization with scene rendering.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

from ..view_model import GeometryViewModel
from ...geometry_scene import GeometryScene
from ...geometry_view import GeometryView
from ...scene_adapter import build_scene_payload
from ...liturgy_styles import LiturgyColors, LiturgyPanels, LiturgyToolbar

class ViewportPane(QWidget):
    """
    Center panel: Hosts the GeometryView and handles 2D/3D visualization.
    """
    
    def __init__(self, view_model: GeometryViewModel, parent=None):
        """
          init   logic.
        
        Args:
            view_model: Description of view_model.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.view_model = view_model
        
        self._setup_ui()
        self._connect_signals()

    # Signals to toggle side panes
    toggle_input_requested = pyqtSignal(bool)
    toggle_controls_requested = pyqtSignal(bool)


    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Toolbar (Pane Management)
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(4, 0, 4, 8) # Bottom margin to separate from view
        
        # Input Pane Toggle (Left)
        self.btn_input = QPushButton("Input Panel")
        self.btn_input.setCheckable(True)
        self.btn_input.setChecked(True)
        self.btn_input.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_input.setStyleSheet(LiturgyToolbar.toggle_button())
        self.btn_input.toggled.connect(self.toggle_input_requested.emit)
        
        # Controls Pane Toggle (Right)
        self.btn_controls = QPushButton("Control Panel")
        self.btn_controls.setCheckable(True)
        self.btn_controls.setChecked(True)
        self.btn_controls.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_controls.setStyleSheet(LiturgyToolbar.toggle_button())
        self.btn_controls.toggled.connect(self.toggle_controls_requested.emit)
        
        toolbar.addWidget(self.btn_input)
        toolbar.addStretch()
        toolbar.addWidget(self.btn_controls)
        
        layout.addLayout(toolbar)
        
        # Container Frame (The Frame of the Void)
        self.container = QFrame()
        self.container.setStyleSheet(LiturgyPanels.viewport_container())
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(2, 2, 2, 2) # Thin border
        
        # Scene & View
        self.scene = GeometryScene()
        self.view = GeometryView(self.scene)
        
        # Liturgical rounding for the view itself to match container
        self.view.setStyleSheet(f"""
            QGraphicsView {{
                border: none;
                border-radius: 22px; 
                background: transparent;
            }}
        """)
        
        container_layout.addWidget(self.view)
        layout.addWidget(self.container)
        
        # Initial Render
        self._refresh_scene()

    def _connect_signals(self):
        self.view_model.calculation_completed.connect(self._refresh_scene)

    def _refresh_scene(self):
        """Rebuild scene from shape data."""
        shape = self.view_model.get_shape()
        instructions = shape.get_drawing_instructions()
        labels = shape.get_label_positions()
        payload = build_scene_payload(instructions, labels)
        self.scene.set_payload(payload)
        self.view.fit_scene()
        
        # Trigger dynamic label layout after fit (which sets initial transform)
        if hasattr(self.scene, "update_label_layout"):
            self.scene.update_label_layout(self.view.transform())
