"""Astrology Settings Dialog - Configuration for chart calculation options."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFormLayout, QGroupBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict, Any

from shared.ui.theme import COLORS


class AstroSettingsDialog(QDialog):
    """Modal dialog for configuring astrological calculation settings."""
    
    settings_changed = pyqtSignal(dict)
    
    # Available options
    ZODIAC_TYPES = [
        ("Tropical", "tropical"),
        ("Sidereal", "sidereal"),
    ]
    
    AYANAMSA_SYSTEMS = [
        ("Lahiri", "LAHIRI"),
        ("Raman", "RAMAN"),
        ("Krishnamurti (KP)", "KRISHNAMURTI"),
        ("Fagan-Bradley", "FAGAN_BRADLEY"),
    ]
    
    NODE_TYPES = [
        ("True Node (Osculating)", "true"),
        ("Mean Node", "mean"),
    ]
    
    POSITION_TYPES = [
        ("Geocentric (Earth Center)", "geo"),
        ("Topocentric (Observer)", "topo"),
    ]
    
    HOUSE_SYSTEMS = [
        ("Placidus", "P"),
        ("Whole Sign", "W"),
        ("Koch", "K"),
        ("Regiomontanus", "R"),
        ("Campanus", "C"),
        ("Equal (ASC)", "A"),
        ("Equal (MC)", "X"),
        ("Porphyry", "O"),
    ]
    
    def __init__(self, current_settings: Dict[str, Any] = None, parent=None):
        """
        Initialize the settings dialog.
        
        Args:
            current_settings: Current chart settings to pre-populate the form.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle("Chart Calculation Settings")
        self.setMinimumWidth(400)
        self.setModal(True)
        
        self._current_settings = current_settings or {}
        self._setup_ui()
        self._load_current_settings()
        self._connect_signals()
    
    def _setup_ui(self):
        """Build the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Title
        title = QLabel("⚙️ Calculation Settings")
        title.setFont(QFont("", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Zodiac Group
        zodiac_group = self._create_group("Zodiac System")
        zodiac_layout = QFormLayout(zodiac_group)
        
        self._zodiac_combo = QComboBox()
        for label, value in self.ZODIAC_TYPES:
            self._zodiac_combo.addItem(label, value)
        zodiac_layout.addRow("Zodiac:", self._zodiac_combo)
        
        self._ayanamsa_combo = QComboBox()
        for label, value in self.AYANAMSA_SYSTEMS:
            self._ayanamsa_combo.addItem(label, value)
        self._ayanamsa_label = QLabel("Ayanamsa:")
        zodiac_layout.addRow(self._ayanamsa_label, self._ayanamsa_combo)
        
        layout.addWidget(zodiac_group)
        
        # Nodes Group
        nodes_group = self._create_group("Lunar Nodes")
        nodes_layout = QFormLayout(nodes_group)
        
        self._node_combo = QComboBox()
        for label, value in self.NODE_TYPES:
            self._node_combo.addItem(label, value)
        nodes_layout.addRow("Node Type:", self._node_combo)
        
        layout.addWidget(nodes_group)
        
        # Position Group
        position_group = self._create_group("Observer Position")
        position_layout = QFormLayout(position_group)
        
        self._position_combo = QComboBox()
        for label, value in self.POSITION_TYPES:
            self._position_combo.addItem(label, value)
        position_layout.addRow("Position:", self._position_combo)
        
        layout.addWidget(position_group)
        
        # House System Group
        house_group = self._create_group("House System")
        house_layout = QFormLayout(house_group)
        
        self._house_combo = QComboBox()
        for label, value in self.HOUSE_SYSTEMS:
            self._house_combo.addItem(label, value)
        house_layout.addRow("System:", self._house_combo)
        
        layout.addWidget(house_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("Apply")
        apply_btn.setDefault(True)
        apply_btn.setProperty("archetype", "magus")  # Use archetype for styling
        apply_btn.clicked.connect(self._apply_settings)
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
        
        # Apply theme
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['surface']};
            }}
            QLabel {{
                color: {COLORS['text_primary']};
            }}
            QComboBox {{
                background-color: {COLORS['surface']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 200px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }}
        """)
    
    def _create_group(self, title: str) -> QGroupBox:
        """Create a styled group box."""
        group = QGroupBox(title)
        return group
    
    def _connect_signals(self):
        """Connect UI signals."""
        self._zodiac_combo.currentIndexChanged.connect(self._on_zodiac_changed)
        self._on_zodiac_changed()  # Initial state
    
    def _on_zodiac_changed(self):
        """Show/hide ayanamsa based on zodiac type."""
        is_sidereal = self._zodiac_combo.currentData() == "sidereal"
        self._ayanamsa_combo.setVisible(is_sidereal)
        self._ayanamsa_label.setVisible(is_sidereal)
    
    def _load_current_settings(self):
        """Pre-populate form with current settings."""
        astrocfg = self._current_settings.get("astrocfg", {})
        
        # Zodiac
        zodiac = astrocfg.get("zodiactype", "tropical")
        idx = self._zodiac_combo.findData(zodiac)
        if idx >= 0:
            self._zodiac_combo.setCurrentIndex(idx)
        
        # Ayanamsa
        ayanamsa = astrocfg.get("ayanamsa", "LAHIRI")
        idx = self._ayanamsa_combo.findData(ayanamsa)
        if idx >= 0:
            self._ayanamsa_combo.setCurrentIndex(idx)
        
        # Node Type
        node_type = astrocfg.get("node_type", "true")
        idx = self._node_combo.findData(node_type)
        if idx >= 0:
            self._node_combo.setCurrentIndex(idx)
        
        # Position Type
        postype = astrocfg.get("postype", "geo")
        idx = self._position_combo.findData(postype)
        if idx >= 0:
            self._position_combo.setCurrentIndex(idx)
        
        # House System
        house = astrocfg.get("houses_system", "P")
        idx = self._house_combo.findData(house)
        if idx >= 0:
            self._house_combo.setCurrentIndex(idx)
    
    def _apply_settings(self):
        """Emit the new settings and close."""
        settings = {
            "astrocfg": {
                "zodiactype": self._zodiac_combo.currentData(),
                "ayanamsa": self._ayanamsa_combo.currentData(),
                "node_type": self._node_combo.currentData(),
                "postype": self._position_combo.currentData(),
                "houses_system": self._house_combo.currentData(),
            }
        }
        self.settings_changed.emit(settings)
        self.accept()
    
    def get_settings(self) -> Dict[str, Any]:
        """Return the currently selected settings."""
        return {
            "astrocfg": {
                "zodiactype": self._zodiac_combo.currentData(),
                "ayanamsa": self._ayanamsa_combo.currentData(),
                "node_type": self._node_combo.currentData(),
                "postype": self._position_combo.currentData(),
                "houses_system": self._house_combo.currentData(),
            }
        }
