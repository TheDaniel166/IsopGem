from PyQt6.QtWidgets import QStatusBar, QLabel, QSlider, QWidget, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from shared.ui.theme import COLORS

class SpreadsheetStatusBar(QStatusBar):
    """
    The grounding wire. Displays coordinates, messages, and zoom controls.
    Extends QStatusBar for proper integration with QMainWindow.
    """
    zoom_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        # Status label (permanent widget on the left)
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self.addWidget(self.lbl_status, 1)  # Stretch factor 1
        
        # Coordinates label
        self.lbl_coords = QLabel("")
        self.lbl_coords.setStyleSheet("font-weight: bold;")
        self.addPermanentWidget(self.lbl_coords)
        
        # Zoom controls container
        zoom_container = QWidget()
        zoom_layout = QHBoxLayout(zoom_container)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        zoom_layout.setSpacing(4)
        
        zoom_layout.addWidget(QLabel("Zoom:"))
        
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setRange(50, 200)
        self.slider_zoom.setValue(100)
        self.slider_zoom.setFixedWidth(100)
        self.slider_zoom.valueChanged.connect(self.zoom_changed.emit)
        zoom_layout.addWidget(self.slider_zoom)
        
        self.addPermanentWidget(zoom_container)
        
    def show_message(self, message: str, timeout: int = 0):
        # We might need to forward this to main window status bar if we want it there,
        # otherwise we update our local label.
        self.lbl_status.setText(message)
        # Timeout logic requires QTimer if we want to clear it locally.
        
    def set_coordinates(self, text: str):
        self.lbl_coords.setText(text)
