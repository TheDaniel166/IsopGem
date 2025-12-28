"""TQ pillar hub - launcher interface for TQ tools."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, 
    QGridLayout, QGraphicsDropShadowEffect, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from shared.ui import WindowManager
from .ternary_converter_window import TernaryConverterWindow
from .quadset_analysis_window import QuadsetAnalysisWindow
from .transitions_window import TransitionsWindow
from .geometric_transitions_window import GeometricTransitionsWindow
from .geometric_transitions_3d_window import GeometricTransitions3DWindow
from .conrune_pair_finder_window import ConrunePairFinderWindow
from .ternary_sound_widget import TernarySoundWidget
from .kamea_window import KameaWindow
from ..services.kamea_grid_service import KameaGridService


class TQHub(QWidget):
    """Hub widget for TQ pillar - displays available tools."""
    
    def __init__(self, window_manager: WindowManager):
        """
          init   logic.
        
        Args:
            window_manager: Description of window_manager.
        
        """
        super().__init__()
        self.window_manager = window_manager
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the hub interface."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 32, 40, 40)

        # Header section
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Trigrammaton Qabalah")
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 32pt;
                font-weight: 700;
                letter-spacing: -1px;
            }
        """)
        header_layout.addWidget(title_label)

        desc_label = QLabel("Ternary systems, transitions, and pattern analysis")
        desc_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12pt;
            }
        """)
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header)

        # Primary tools grid
        tools = [
            ("≣", "Ternary Converter", "Convert between ternary and decimal", "#3b82f6", self._open_ternary_converter),
            ("▦", "Quadset Analysis", "Analyze quadset relationships", "#8b5cf6", self._open_quadset_analysis),
            ("⇄", "Transitions", "Explore ternary state transitions", "#10b981", self._open_transitions),
            ("△", "Geo Transitions", "2D geometric transition mapping", "#dc2626", self._open_geometric_transitions),
            ("⬡", "3D Transitions", "3D geometric transition space", "#0f766e", self._open_geometric_transitions_3d),
            ("⊜", "Conrune Finder", "Find conrune pairs and matches", "#f97316", self._open_conrune_pair_finder),
            ("♫", "Amun Sound", "Ternary sound calculator", "#8b5cf6", self._open_amun_sound),
        ]

        grid = QGridLayout()
        grid.setSpacing(16)
        
        for i, (icon, title, desc, color, callback) in enumerate(tools):
            card = self._create_tool_card(icon, title, desc, color, callback)
            grid.addWidget(card, i // 3, i % 3)
        
        layout.addLayout(grid)

        # Kamea section header
        kamea_header = QLabel("Kamea Grids")
        kamea_header.setStyleSheet("""
            QLabel {
                color: #475569;
                font-size: 14pt;
                font-weight: 600;
                margin-top: 16px;
            }
        """)
        layout.addWidget(kamea_header)

        # Kamea grids
        kamea_tools = [
            ("◫", "Kamea of Maut", "Primary kamea grid visualizer", "#0f172a", self._open_kamea_grid),
            ("⛋", "Kamea of Baphomet", "Baphomet variant kamea grid", "#7f1d1d", self._open_baphomet_grid),
        ]

        kamea_grid = QGridLayout()
        kamea_grid.setSpacing(16)
        
        for i, (icon, title, desc, color, callback) in enumerate(kamea_tools):
            card = self._create_tool_card(icon, title, desc, color, callback)
            kamea_grid.addWidget(card, 0, i)
        
        layout.addLayout(kamea_grid)
        
        # Coming soon
        coming_soon = QLabel("Coming Soon: Trigrammaton Mapper \u2022 QBLH Pattern Analyzer")
        coming_soon.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 10pt;
                padding: 20px;
            }
        """)
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(coming_soon)
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _create_tool_card(self, icon: str, title: str, description: str, accent_color: str, callback) -> QFrame:
        """Create a modern tool card."""
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 0;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f5f9);
                border-color: {accent_color};
            }}
        """)
        card.setMinimumSize(200, 140)
        card.setMaximumHeight(160)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 25))
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(8)
        
        icon_container = QLabel(icon)
        icon_container.setFixedSize(48, 48)
        icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.setStyleSheet(f"""
            QLabel {{
                background: {accent_color}20;
                border-radius: 10px;
                font-size: 22pt;
            }}
        """)
        card_layout.addWidget(icon_container)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 13pt;
                font-weight: 600;
                background: transparent;
            }
        """)
        card_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 9pt;
                background: transparent;
            }
        """)
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)
        
        card_layout.addStretch()
        
        card.mousePressEvent = lambda e: callback()
        
        return card

    def _open_ternary_converter(self):
        """Open the ternary converter window."""
        self.window_manager.open_window(
            "ternary_converter",
            TernaryConverterWindow
        )

    def _open_quadset_analysis(self):
        """Open the quadset analysis window."""
        self.window_manager.open_window(
            "quadset_analysis",
            QuadsetAnalysisWindow,
            window_manager=self.window_manager
        )

    def _open_transitions(self):
        """Open the transitions window."""
        self.window_manager.open_window(
            "transitions",
            TransitionsWindow,
            window_manager=self.window_manager
        )

    def _open_geometric_transitions(self):
        """Open the geometric transitions window."""
        self.window_manager.open_window(
            "geometric_transitions",
            GeometricTransitionsWindow,
            window_manager=self.window_manager
        )

    def _open_geometric_transitions_3d(self):
        """Open the 3D geometric transitions window."""
        self.window_manager.open_window(
            "geometric_transitions_3d",
            GeometricTransitions3DWindow,
            window_manager=self.window_manager
        )

    def _open_conrune_pair_finder(self):
        """Open the Conrune Pair Finder window."""
        self.window_manager.open_window(
            "conrune_pair_finder",
            ConrunePairFinderWindow,
            window_manager=self.window_manager
        )

    def _open_amun_sound(self):
        """Open the Amun Sound Calculator window."""
        self.window_manager.open_window(
            "amun_sound_calculator",
            TernarySoundWidget
        )

    def _open_kamea_grid(self):
        """Open the Kamea Grid Visualizer."""
        # Create Service Instance
        # Ideally this should be dependency injected, but for now we create it here.
        service = KameaGridService()
        
        self.window_manager.open_window(
            "kamea_grid",
            KameaWindow,
            service=service
        )

    def _open_baphomet_grid(self):
        """Open the Kamea of Baphomet Visualizer."""
        service = KameaGridService(variant="Baphomet")
        
        self.window_manager.open_window(
            "kamea_baphomet",
            KameaWindow,
            service=service
        )