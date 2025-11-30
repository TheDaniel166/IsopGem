"""Astrology pillar hub - launcher interface for astrology tools."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shared.ui import WindowManager


class AstrologyHub(QWidget):
    """Hub widget for Astrology pillar - displays available tools."""
    
    def __init__(self, window_manager: WindowManager):
        """
        Initialize the Astrology hub.
        
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
        title_label = QLabel("Astrology Pillar")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Cosmic calendar and zodiacal mappings\n\n"
            "Coming Soon:\n"
            "• Cosmic Calendar\n"
            "• Zodiac Chart Generator\n"
            "• Planetary Position Calculator\n"
            "• Aspect Analysis"
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_font = QFont()
        desc_font.setPointSize(12)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: #666; margin-top: 20px;")
        layout.addWidget(desc_label)
        
        layout.addStretch()
