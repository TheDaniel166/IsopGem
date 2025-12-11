"""Adyton pillar hub - launcher interface for Inner Sanctuary tools."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shared.ui import WindowManager
from .engine.window import AdytonSanctuaryEngine

class AdytonHub(QWidget):
    """Hub widget for Adyton pillar - displays available tools."""
    
    def __init__(self, window_manager: WindowManager):
        """
        Initialize the Adyton hub.
        
        Args:
            window_manager: Shared window manager instance
        """
        super().__init__()
        self.window_manager = window_manager
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the hub interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Adyton Mechanics")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "The Inner Sanctuary of the Seven.\n\n"
            "Chamber of the Adepts, Amun Color Map, and Sacred Geometry."
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_font = QFont()
        desc_font.setPointSize(12)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: #666; margin-top: 20px;")
        layout.addWidget(desc_label)

        self._create_action_buttons(layout)
        
        layout.addStretch()

    def _create_action_buttons(self, layout: QVBoxLayout) -> None:
        """Add launchers for Adyton tools."""
        sanctuary_btn = QPushButton("Enter the Adyton (3D Engine)")
        sanctuary_btn.setMinimumHeight(48)
        sanctuary_btn.clicked.connect(self._open_sanctuary)
        layout.addWidget(sanctuary_btn)

    def _open_sanctuary(self) -> None:
        """Launch the Adyton Engine window."""
        self.window_manager.open_window(
            "adyton_sanctuary_engine",
            AdytonSanctuaryEngine,
            allow_multiple=False,
        )
