from PyQt6.QtWidgets import QStatusBar, QLabel, QSlider, QWidget, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
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
        
        # Reference Mode Indicator
        self.lbl_ref_mode = QLabel("")
        self.lbl_ref_mode.setStyleSheet(f"padding: 2px 6px; border-radius: 3px;")
        self.addPermanentWidget(self.lbl_ref_mode)
        self.set_ref_mode(False)  # Start with Enter mode (off)
        
        # Zoom controls container
        zoom_container = QWidget()
        zoom_layout = QHBoxLayout(zoom_container)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        zoom_layout.setSpacing(4)
        
        zoom_layout.addWidget(QLabel("Zoom:"))
        
        self.lbl_zoom_pct = QLabel("100%")
        self.lbl_zoom_pct.setMinimumWidth(35)
        zoom_layout.addWidget(self.lbl_zoom_pct)
        
        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setRange(50, 200)
        self.slider_zoom.setValue(100)
        self.slider_zoom.setFixedWidth(100)
        self.slider_zoom.valueChanged.connect(self._on_zoom_value_changed)
        zoom_layout.addWidget(self.slider_zoom)
        
        self.addPermanentWidget(zoom_container)
        
    def _on_zoom_value_changed(self, value: int):
        """Update label and emit signal."""
        self.lbl_zoom_pct.setText(f"{value}%")
        self.zoom_changed.emit(value)

    def show_message(self, message: str, timeout: int = 0):
        """Display a message, optionally clearing after timeout ms."""
        self.lbl_status.setText(message)
        if timeout > 0:
            QTimer.singleShot(timeout, lambda: self.lbl_status.setText("Ready"))
        
    def set_coordinates(self, text: str):
        self.lbl_coords.setText(text)

    def set_ref_mode(self, is_ref_mode: bool):
        """Updates the Reference Mode indicator."""
        if is_ref_mode:
            self.lbl_ref_mode.setText("REF")
            self.lbl_ref_mode.setStyleSheet(
                f"background: {COLORS.get('accent', '#FFA500')}; "
                f"color: {COLORS.get('surface', '#1a1a2e')}; "
                "padding: 2px 6px; border-radius: 3px; font-weight: bold;"
            )
        else:
            self.lbl_ref_mode.setText("EDIT")
            self.lbl_ref_mode.setStyleSheet(
                f"background: {COLORS.get('surface_variant', '#2a2a4a')}; "
                f"color: {COLORS.get('text_secondary', '#888')}; "
                "padding: 2px 6px; border-radius: 3px;"
            )
