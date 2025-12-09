"""Astrology pillar hub - launcher interface for astrology tools."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shared.ui import WindowManager
from .natal_chart_window import NatalChartWindow
from .current_transit_window import CurrentTransitWindow
from .planetary_positions_window import PlanetaryPositionsWindow
from .neo_aubrey_window import NeoAubreyWindow
from .venus_rose_window import VenusRoseWindow


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
            "New dependency stack: OpenAstro2 + Swiss Ephemeris\n"
            "(currently validated on Linux builds)."
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
        """Add placeholder feature launchers for upcoming tools."""
        natal_chart_btn = QPushButton("Natal Chart Generator")
        natal_chart_btn.setMinimumHeight(48)
        natal_chart_btn.clicked.connect(self._open_natal_chart)
        layout.addWidget(natal_chart_btn)

        transit_btn = QPushButton("Current Transit Viewer")
        transit_btn.setMinimumHeight(48)
        transit_btn.clicked.connect(self._open_transit_viewer)
        layout.addWidget(transit_btn)

        planet_positions_btn = QPushButton("Planetary Positions Table")
        planet_positions_btn.setMinimumHeight(48)
        planet_positions_btn.clicked.connect(self._open_planetary_positions)
        layout.addWidget(planet_positions_btn)

        neo_aubrey_btn = QPushButton("Neo-Aubrey Eclipse Clock")
        neo_aubrey_btn.setMinimumHeight(48)
        neo_aubrey_btn.clicked.connect(self._open_neo_aubrey)
        layout.addWidget(neo_aubrey_btn)

        rose_btn = QPushButton("The Cytherean Rose")
        rose_btn.setMinimumHeight(48)
        rose_btn.clicked.connect(self._open_venus_rose)
        layout.addWidget(rose_btn)


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
