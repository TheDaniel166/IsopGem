"""Astrology pillar hub - launcher interface for astrology tools."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame, 
    QGridLayout, QGraphicsDropShadowEffect, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from shared.ui import WindowManager
from .natal_chart_window import NatalChartWindow
from .current_transit_window import CurrentTransitWindow
from .planetary_positions_window import PlanetaryPositionsWindow
from .neo_aubrey_window import NeoAubreyWindow
from .venus_rose_window import VenusRoseWindow
from .differential_natal_window import DifferentialNatalWindow


class AstrologyHub(QWidget):
    """Hub widget for Astrology pillar - displays available tools."""
    
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
        
        title_label = QLabel("Astrology")
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 32pt;
                font-weight: 700;
                letter-spacing: -1px;
            }
        """)
        header_layout.addWidget(title_label)

        desc_label = QLabel("Cosmic calendar and zodiacal mappings powered by Swiss Ephemeris")
        desc_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12pt;
            }
        """)
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header)

        # Tools grid
        tools = [
            ("☉", "Natal Chart", "Generate birth charts with planetary placements", "#8b5cf6", self._open_natal_chart),
            ("Δ", "Differential", "Map planets to Conrune pairs", "#06b6d4", self._open_differential_chart),
            ("↻", "Transits", "View current planetary transits in real-time", "#3b82f6", self._open_transit_viewer),
            ("♈", "Positions", "Ephemeris table of planetary positions", "#10b981", self._open_planetary_positions),
            ("◐", "Eclipse Clock", "Neo-Aubrey eclipse timing calculator", "#f97316", self._open_neo_aubrey),
            ("♀", "Venus Rose", "The Cytherean Rose - Venus cycles", "#ec4899", self._open_venus_rose),
        ]

        grid = QGridLayout()
        grid.setSpacing(16)
        
        for i, (icon, title, desc, color, callback) in enumerate(tools):
            card = self._create_tool_card(icon, title, desc, color, callback)
            grid.addWidget(card, i // 3, i % 3)
        
        layout.addLayout(grid)
        
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

    def _open_natal_chart(self) -> None:
        """Launch the natal chart generator window."""
        self.window_manager.open_window(
            "astrology_natal_chart",
            NatalChartWindow,
            allow_multiple=False,
        )

    def _open_transit_viewer(self) -> None:
        """Launch the current transit viewer window."""
        self.window_manager.open_window(
            "astrology_transit_viewer",
            CurrentTransitWindow,
            allow_multiple=False,
        )

    def _open_planetary_positions(self) -> None:
        """Launch the planetary positions ephemeris window."""
        self.window_manager.open_window(
            "astrology_planetary_positions",
            PlanetaryPositionsWindow,
            allow_multiple=False,
            window_manager=self.window_manager,
        )

    def _open_neo_aubrey(self) -> None:
        """Launch the Neo-Aubrey Eclipse Clock."""
        self.window_manager.open_window(
            "astrology_neo_aubrey",
            NeoAubreyWindow,
            allow_multiple=False,
        )

    def _open_venus_rose(self) -> None:
        """Launch the Cytherean Rose window."""
        self.window_manager.open_window(
            "astrology_venus_rose",
            VenusRoseWindow,
            allow_multiple=False,
        )

    def _open_differential_chart(self) -> None:
        """Launch the Differential Natal Chart window."""
        self.window_manager.open_window(
            "astrology_differential_chart",
            DifferentialNatalWindow,
            allow_multiple=False,
            window_manager=self.window_manager,
        )