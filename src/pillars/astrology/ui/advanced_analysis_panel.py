"""
Advanced Analysis Panel — Reusable component for comprehensive chart analysis.

Provides the full suite of advanced chart analysis tabs:
- Fixed Stars
- Arabic Parts
- Midpoints (Tree/Dial/Table views)
- Harmonics (Dial/Table views)
- Maat Symbols
- Aspects (Grid/List/Legend views)

This component can be embedded in NatalChartWindow, SynastryWindow,
ProgressionsWindow, ReturnsWindow, or any other chart display window.
"""
from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import List, Optional, Any, cast

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QSpinBox, QComboBox, QCheckBox, QSlider, QPushButton,
    QTreeWidget, QTreeWidgetItem, QFrame, QListWidget, QStackedWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QFontDatabase

from shared.ui.theme import COLORS
from ..models.chart_models import PlanetPosition, HousePosition, ChartResult
from ..services.arabic_parts_service import ArabicPartsService
from ..services.harmonics_service import HarmonicsService
from ..services.maat_symbols_service import MaatSymbolsService
from ..services.midpoints_service import MidpointsService, Midpoint
from ..services.aspects_service import AspectsService
from ..services.fixed_stars_service import FixedStarsService
from ..services.dignities_service import DignitiesService, PlanetaryDignity
from ..utils.conversions import to_zodiacal_string

logger = logging.getLogger(__name__)


class AdvancedAnalysisPanel(QWidget):
    """
    Reusable panel for comprehensive chart analysis.
    
    Provides all advanced analysis tabs that can be used with any chart data.
    Accepts ChartResult or individual planet/house positions.
    Styled according to Visual Liturgy v2.2.
    Uses Astronomicon font for astrological symbols.
    """
    
    # Astronomicon font mappings
    ASTRO_PLANETS = {
        "Sun": "Q", "Moon": "R", "Mercury": "S", "Venus": "T",
        "Mars": "U", "Jupiter": "V", "Saturn": "W", "Uranus": "X",
        "Neptune": "Y", "Pluto": "Z", "North Node": "g", "True Node": "g",
        "South Node": "i", "Chiron": "q", "Lilith": "z", "Part of Fortune": "}",
        "Asc": "c", "Mc": "d"
    }
    
    ASTRO_ZODIAC = {
        "Aries": "A", "Taurus": "B", "Gemini": "C", "Cancer": "D",
        "Leo": "E", "Virgo": "F", "Libra": "G", "Scorpio": "H",
        "Sagittarius": "I", "Capricorn": "J", "Aquarius": "K", "Pisces": "L",
    }
    
    ASTRO_ASPECTS = {
        "Conjunction": "!", # Tentative, screenshot shows Mars-like symbol, but usually ! in astro fonts
        "Opposition": "@",  # Tentative/Fallback
        "Trine": "$", 
        "Square": "#",
        "Sextile": "%", 
        "Quincunx": "&", 
        "Semi-sextile": "(", 
        "Semi-square": ")",
        "Quintile": "*",
        "Sesquiquadrate": "_", # Guessing based on placement
    }
    
    # Fallback Unicode glyphs (for non-Astronomicon display)
    PLANET_GLYPHS = {
        "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
        "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
        "Neptune": "♆", "Pluto": "♇", "North Node": "☊", "True Node": "☊",
        "South Node": "☋", "Chiron": "⚷",
    }
    
    # Main 10 planets
    MAIN_BODIES = {"sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"}
    
    # Classic 7 planets
    CLASSIC_7 = {"sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"}
    
    # Aspect colors for display
    ASPECT_COLORS = {
        "Conjunction": "#ffee00",
        "Opposition": "#ff2a6d",
        "Trine": "#4deeea",
        "Square": "#f000ff",
        "Sextile": "#74ee15",
        "Quincunx": "#cccc88",
        "Semi-sextile": "#88aa88",
        "Semi-square": "#aaaaaa",
        "Sesquiquadrate": "#aaaaaa",
        "Quintile": "#88ccff",
        "Biquintile": "#88ccff",
    }
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Data
        self._planets: List[PlanetPosition] = []
        self._houses: List[HousePosition] = []
        self._fixed_stars: List[Any] = []  # From ChartResult
        self._julian_day: Optional[float] = None
        
        # Services
        self._arabic_service = ArabicPartsService()
        self._fixed_stars_service = FixedStarsService()
        self._harmonics_service = HarmonicsService()
        self._maat_service = MaatSymbolsService()
        self._midpoints_service = MidpointsService()
        self._aspects_service = AspectsService()
        self._dignities_service = DignitiesService()

        # Load Astronomicon font
        self._astro_font_family = self._get_astronomicon_font()
        
        self._setup_ui()
    
    def _get_astronomicon_font(self) -> str:
        """Return the Astronomicon font family name if available."""
        families = QFontDatabase.families()
        for family in families:
            if "astronomicon" in family.lower():
                return family
        return "Arial"  # Fallback
    
    def _create_astro_item(self, text: str, is_symbol: bool = True) -> QTableWidgetItem:
        """Create a table widget item with Astronomicon font for symbols."""
        item = QTableWidgetItem(text)
        if is_symbol and self._astro_font_family != "Arial":
            font = QFont(self._astro_font_family, 14)
            item.setFont(font)
        return item
    
    def _get_planet_display(self, name: str, use_astro: bool = True) -> str:
        """Get display character for a planet name."""
        if use_astro and self._astro_font_family != "Arial":
            return self.ASTRO_PLANETS.get(name, name[0].lower())
        return self.PLANET_GLYPHS.get(name, name)
    
    def _get_aspect_display(self, name: str, use_astro: bool = True) -> str:
        """Get display character for an aspect name."""
        if use_astro and self._astro_font_family != "Arial":
            return self.ASTRO_ASPECTS.get(name, "?")
        # Fallback Unicode symbols
        aspect_symbols = {
            "Conjunction": "☌", "Opposition": "☍", "Trine": "△", "Square": "□",
            "Sextile": "⚹", "Quincunx": "⚻", "Semi-sextile": "⚺",
        }
        return aspect_symbols.get(name, name[:3])
    
    def _setup_ui(self):
        """Build UI with Visual Liturgy styling - vertical sidebar navigation."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Sidebar navigation (Vertical tab list)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(160)
        self.sidebar.setFrameShape(QFrame.Shape.NoFrame)
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e293b, stop:1 #334155);
                border: none;
                outline: none;
                padding-top: 8px;
            }}
            QListWidget::item {{
                height: 48px;
                padding: 12px 16px;
                color: #94a3b8;
                border-left: 3px solid transparent;
                font-size: 10pt;
                font-weight: 500;
            }}
            QListWidget::item:selected {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(59, 130, 246, 0.2), stop:1 transparent);
                color: #ffffff;
                border-left: 3px solid #3b82f6;
                font-weight: 600;
            }}
            QListWidget::item:hover:!selected {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(148, 163, 184, 0.15), stop:1 transparent);
                color: #e2e8f0;
                border-left: 3px solid #64748b;
            }}
        """)
        
        # Navigation items
        nav_items = ["Dignities", "Fixed Stars", "Arabic Parts", "Midpoints", "Harmonics", "Maat Symbols", "Aspects"]
        for item in nav_items:
            self.sidebar.addItem(item)
        
        self.sidebar.currentRowChanged.connect(self._on_nav_changed)
        layout.addWidget(self.sidebar)
        
        # Content area (stacked widget)
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"background-color: {COLORS['background']};")
        layout.addWidget(self.content_stack, stretch=1)

        # Build each tab content (order must match nav_items)
        self._build_dignities_tab()
        self._build_fixed_stars_tab()
        self._build_arabic_parts_tab()
        self._build_midpoints_tab()
        self._build_harmonics_tab()
        self._build_maat_tab()
        self._build_aspects_tab()
        
        # Select first item
        self.sidebar.setCurrentRow(0)
    
    def _on_nav_changed(self, index: int):
        """Handle sidebar navigation change."""
        self.content_stack.setCurrentIndex(index)
    
    def _get_table_style(self) -> str:
        """Get consistent table styling for Visual Liturgy."""
        return f"""
            QTableWidget {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                gridline-color: {COLORS['border']};
                selection-background-color: {COLORS['primary_light']};
                selection-color: {COLORS['primary']};
                font-size: 10pt;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: {COLORS['primary']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['background_alt']};
                padding: 10px 8px;
                border: none;
                border-bottom: 2px solid {COLORS['border']};
                border-right: 1px solid {COLORS['border']};
                font-weight: 600;
                font-size: 9pt;
                color: {COLORS['text_primary']};
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
        """
    
    def _get_control_style(self) -> str:
        """Get consistent control styling for Visual Liturgy."""
        return f"""
            QCheckBox {{
                color: {COLORS['text_primary']};
                font-size: 10pt;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS['border']};
                border-radius: 4px;
                background-color: {COLORS['surface']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['primary']};
                border-color: {COLORS['primary']};
            }}
            QSpinBox {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 11pt;
                min-height: 32px;
                color: {COLORS['text_primary']};
            }}
            QSpinBox:focus {{
                border-color: {COLORS['focus']};
            }}
            QComboBox {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 6px 12px;
                min-height: 32px;
                color: {COLORS['text_primary']};
                font-size: 10pt;
            }}
            QComboBox:hover {{
                border-color: {COLORS['focus']};
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 8px;
            }}
            QSlider::groove:horizontal {{
                height: 6px;
                background: {COLORS['border']};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                width: 16px;
                height: 16px;
                margin: -5px 0;
                background: {COLORS['primary']};
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {COLORS['primary_hover']};
            }}
            QPushButton {{
                background-color: {COLORS['navigator']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 10pt;
                font-weight: 500;
                min-height: 28px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['navigator_hover']};
            }}
        """
    
    def _create_content_wrapper(self) -> QWidget:
        """Create a styled content wrapper with padding."""
        wrapper = QWidget()
        wrapper.setStyleSheet(f"background-color: {COLORS['background']};")
        return wrapper
    
    # =========================================================================
    # TAB BUILDERS
    # =========================================================================

    def _build_dignities_tab(self):
        """Build Planetary Dignities tab."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {COLORS['background']};")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QLabel("Planetary Dignities")
        header.setStyleSheet(f"font-size: 18pt; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(header)

        # Subheader
        subheader = QLabel("Essential & Accidental dignity analysis (Classic 7 planets)")
        subheader.setStyleSheet(f"color: {COLORS['text_secondary']}; font-style: italic; font-size: 10pt;")
        layout.addWidget(subheader)

        # Main dignities table
        self.dignities_table = QTableWidget(0, 6)
        self.dignities_table.setHorizontalHeaderLabels([
            "Planet", "Sign", "Essential", "Accidental", "Score", "Details"
        ])
        self.dignities_table.setStyleSheet(self._get_table_style())
        self._stretch_last_section(self.dignities_table)
        self.dignities_table.setColumnWidth(0, 80)
        self.dignities_table.setColumnWidth(1, 100)
        self.dignities_table.setColumnWidth(2, 90)
        self.dignities_table.setColumnWidth(3, 90)
        self.dignities_table.setColumnWidth(4, 60)
        self.dignities_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.dignities_table.setWordWrap(True)
        self._set_vertical_section_size(self.dignities_table, 40)
        layout.addWidget(self.dignities_table)

        # Summary section
        summary_frame = QFrame()
        summary_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        summary_layout = QHBoxLayout(summary_frame)

        self.dignities_summary_label = QLabel("Total Chart Strength: --")
        self.dignities_summary_label.setStyleSheet(f"""
            font-size: 12pt;
            font-weight: 600;
            color: {COLORS['text_primary']};
        """)
        summary_layout.addWidget(self.dignities_summary_label)
        summary_layout.addStretch()

        layout.addWidget(summary_frame)

        self.content_stack.addWidget(widget)

    def _build_fixed_stars_tab(self):
        """Build Fixed Stars tab."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {COLORS['background']};")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("Fixed Stars")
        header.setStyleSheet(f"font-size: 18pt; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(header)
        
        self.fixed_stars_table = QTableWidget(0, 3)
        self.fixed_stars_table.setHorizontalHeaderLabels(["Star", "Position", "Aspects"])
        self.fixed_stars_table.setStyleSheet(self._get_table_style())
        self._stretch_last_section(self.fixed_stars_table)
        self.fixed_stars_table.setColumnWidth(0, 150)
        self.fixed_stars_table.setColumnWidth(1, 100)
        layout.addWidget(self.fixed_stars_table)
        
        self.content_stack.addWidget(widget)
    
    def _build_arabic_parts_tab(self):
        """Build Arabic Parts tab."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {COLORS['background']};")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("Arabic Parts")
        header.setStyleSheet(f"font-size: 18pt; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(header)
        
        self.arabic_parts_table = QTableWidget(0, 3)
        self.arabic_parts_table.setHorizontalHeaderLabels(["Part", "Formula", "Position"])
        self.arabic_parts_table.setStyleSheet(self._get_table_style())
        self._stretch_last_section(self.arabic_parts_table)
        layout.addWidget(self.arabic_parts_table)
        
        self.content_stack.addWidget(widget)
    
    def _build_midpoints_tab(self):
        """Build Midpoints tab with Tree/Dial/Table subtabs."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {COLORS['background']}; " + self._get_control_style())
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("Midpoints")
        header.setStyleSheet(f"font-size: 18pt; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(header)
        
        # Controls row
        controls = QHBoxLayout()
        self.classic7_checkbox = QCheckBox("Classic 7 Only")
        self.classic7_checkbox.setChecked(True)
        self.classic7_checkbox.stateChanged.connect(self._on_midpoints_filter_changed)
        controls.addWidget(self.classic7_checkbox)
        controls.addStretch()
        layout.addLayout(controls)
        
        # Sub-tabs
        self.midpoints_subtabs = QTabWidget()
        
        # Tree view
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        self.midpoints_tree = QTreeWidget()
        self.midpoints_tree.setHeaderLabels(["Planet / Midpoint", "Position"])
        self.midpoints_tree.setColumnWidth(0, 200)
        self.midpoints_tree.setStyleSheet(self._get_table_style())
        tree_layout.addWidget(self.midpoints_tree)
        self.midpoints_subtabs.addTab(tree_widget, "Tree")
        
        # Dial view
        try:
            from .midpoints_dial import MidpointsDial
            self.midpoints_dial = MidpointsDial()
            self.midpoints_subtabs.addTab(self.midpoints_dial, "Dial")
        except ImportError:
            pass
        
        # Table view
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        self.midpoints_table = QTableWidget(0, 2)
        self.midpoints_table.setHorizontalHeaderLabels(["Pair", "Midpoint"])
        self.midpoints_table.setStyleSheet(self._get_table_style())
        self._stretch_last_section(self.midpoints_table)
        table_layout.addWidget(self.midpoints_table)
        self.midpoints_subtabs.addTab(table_widget, "Table")
        
        layout.addWidget(self.midpoints_subtabs)
        self.content_stack.addWidget(widget)
    
    def _build_harmonics_tab(self):
        """Build Harmonics tab with Dial/Table subtabs."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {COLORS['background']}; " + self._get_control_style())
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("Harmonics")
        header.setStyleSheet(f"font-size: 18pt; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(header)
        
        # Controls row
        controls = QHBoxLayout()
        lbl = QLabel("Harmonic:")
        lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 600;")
        controls.addWidget(lbl)
        self.harmonic_spinbox = QSpinBox()
        self.harmonic_spinbox.setRange(1, 360)
        self.harmonic_spinbox.setValue(4)
        self.harmonic_spinbox.valueChanged.connect(self._on_harmonic_changed)
        controls.addWidget(self.harmonic_spinbox)
        
        # Preset buttons
        for h in [4, 5, 7, 9]:
            btn = QPushButton(str(h))
            btn.setToolTip(f"Harmonic {h}")
            btn.setMinimumWidth(40)
            btn.setMaximumWidth(50)

            def _on_preset_clicked(checked: bool, hval: int = h) -> None:
                self._set_harmonic(hval)

            btn.clicked.connect(_on_preset_clicked)
            controls.addWidget(btn)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Sub-tabs
        self.harmonics_subtabs = QTabWidget()
        
        # Dial view
        try:
            from .harmonics_dial import HarmonicsDial
            self.harmonics_dial = HarmonicsDial()
            self.harmonics_subtabs.addTab(self.harmonics_dial, "Dial")
        except ImportError:
            pass
        
        # Table view
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        self.harmonics_table = QTableWidget(0, 3)
        self.harmonics_table.setHorizontalHeaderLabels(["Planet", "Natal", "Harmonic"])
        self.harmonics_table.setStyleSheet(self._get_table_style())
        self._stretch_last_section(self.harmonics_table)
        table_layout.addWidget(self.harmonics_table)
        self.harmonics_subtabs.addTab(table_widget, "Table")
        
        layout.addWidget(self.harmonics_subtabs)
        self.content_stack.addWidget(widget)
    
    def _build_maat_tab(self):
        """Build Maat Symbols tab."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {COLORS['background']};")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("Maat Symbols")
        header.setStyleSheet(f"font-size: 18pt; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(header)
        
        # Info label
        info = QLabel("Egyptian degree symbols — each degree has a unique symbolic description")
        info.setStyleSheet(f"color: {COLORS['text_secondary']}; font-style: italic; font-size: 10pt;")
        layout.addWidget(info)
        
        self.maat_table = QTableWidget(0, 4)
        self.maat_table.setHorizontalHeaderLabels(["Planet", "Position", "Heaven", "Symbol"])
        self.maat_table.setStyleSheet(self._get_table_style())
        self._stretch_last_section(self.maat_table)
        self.maat_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.maat_table.setWordWrap(True)
        self._set_vertical_section_size(self.maat_table, 60)
        layout.addWidget(self.maat_table)
        
        self.content_stack.addWidget(widget)
    
    def _build_aspects_tab(self):
        """Build Aspects tab with Grid/List/Legend subtabs."""
        widget = QWidget()
        widget.setStyleSheet(f"background-color: {COLORS['background']}; " + self._get_control_style())
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header = QLabel("Aspects")
        header.setStyleSheet(f"font-size: 18pt; font-weight: 700; color: {COLORS['text_primary']};")
        layout.addWidget(header)
        
        # Controls row
        controls = QHBoxLayout()
        
        lbl1 = QLabel("Show:")
        lbl1.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 600;")
        controls.addWidget(lbl1)
        self.aspect_tier_combo = QComboBox()
        self.aspect_tier_combo.addItems([
            "Major Only",
            "Major + Common Minor",
            "Major + All Minor",
            "All Aspects"
        ])
        self.aspect_tier_combo.currentIndexChanged.connect(self._on_aspects_filter_changed)
        controls.addWidget(self.aspect_tier_combo)
        
        lbl2 = QLabel("Orb:")
        lbl2.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 600; margin-left: 16px;")
        controls.addWidget(lbl2)
        self.orb_slider = QSlider(Qt.Orientation.Horizontal)
        self.orb_slider.setRange(50, 150)
        self.orb_slider.setValue(100)
        self.orb_slider.setFixedWidth(100)
        self.orb_slider.valueChanged.connect(self._on_orb_changed)
        controls.addWidget(self.orb_slider)
        
        self.orb_label = QLabel("100%")
        self.orb_label.setStyleSheet(f"color: {COLORS['text_primary']}; font-weight: 600;")
        controls.addWidget(self.orb_label)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Sub-tabs
        self.aspects_subtabs = QTabWidget()
        
        # Grid view
        grid_widget = QWidget()
        grid_layout = QVBoxLayout(grid_widget)
        self.aspects_grid = QTableWidget()
        self.aspects_grid.setStyleSheet(self._get_table_style())
        self.aspects_grid.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        grid_layout.addWidget(self.aspects_grid)
        self.aspects_subtabs.addTab(grid_widget, "Grid")
        
        # List view
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        self.aspects_table = QTableWidget(0, 5)
        self.aspects_table.setHorizontalHeaderLabels(["Planet A", "Aspect", "Planet B", "Orb", "Type"])
        self.aspects_table.setStyleSheet(self._get_table_style())
        self._stretch_last_section(self.aspects_table)
        list_layout.addWidget(self.aspects_table)
        self.aspects_subtabs.addTab(list_widget, "List")
        
        # Legend tab
        legend_widget = QWidget()
        legend_layout = QVBoxLayout(legend_widget)
        self.aspects_legend = QTableWidget()
        self.aspects_legend.setColumnCount(3)
        self.aspects_legend.setHorizontalHeaderLabels(["Symbol", "Aspect", "Angle"])
        self.aspects_legend.setStyleSheet(self._get_table_style())
        self._stretch_last_section(self.aspects_legend)
        self.aspects_legend.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        legend_layout.addWidget(self.aspects_legend)
        self.aspects_subtabs.addTab(legend_widget, "Legend")
        
        layout.addWidget(self.aspects_subtabs)
        self.content_stack.addWidget(widget)
    
    # =========================================================================
    # DATA SETTING
    # =========================================================================
    
    def set_data(self, planets: List[PlanetPosition], houses: List[HousePosition],
                 fixed_stars: Optional[List[Any]] = None, julian_day: Optional[float] = None):
        """Set chart data and refresh all tabs."""
        self._planets = planets or []
        self._houses = houses or []
        self._fixed_stars = fixed_stars or []
        self._julian_day = julian_day
        self._refresh_all()
    
    def set_chart_result(self, result: ChartResult):
        """Set data from a ChartResult object."""
        self._planets = result.planet_positions or []
        self._houses = result.house_positions or []
        self._fixed_stars = getattr(result, 'fixed_stars', []) or []
        self._julian_day = result.julian_day
        self._refresh_all()
    
    def _refresh_all(self):
        """Refresh all tabs with current data."""
        self._render_dignities()
        self._render_fixed_stars()
        self._render_arabic_parts()
        self._render_midpoints()
        self._render_harmonics()
        self._render_maat_symbols()
        self._render_aspects_table()
    
    # =========================================================================
    # RENDER METHODS
    # =========================================================================

    def _render_dignities(self):
        """Populate Planetary Dignities table."""
        self.dignities_table.setRowCount(0)

        if not self._planets or not self._houses:
            self.dignities_summary_label.setText("Total Chart Strength: --")
            return

        try:
            # Convert PlanetPosition/HousePosition objects to dicts for the service
            planet_data = []
            for p in self._planets:
                planet_data.append({
                    "name": p.name,
                    "degree": p.degree,
                    "is_retrograde": p.is_retrograde,
                })

            house_data = []
            for h in self._houses:
                house_data.append({
                    "number": h.number,
                    "degree": h.degree,
                })

            dignities = self._dignities_service.calculate_dignities(planet_data, house_data)

            total_score = 0

            for dignity in dignities:
                row = self.dignities_table.rowCount()
                self.dignities_table.insertRow(row)

                # Planet (with glyph)
                p_glyph = self.PLANET_GLYPHS.get(dignity.planet, "")
                planet_item = QTableWidgetItem(f"{p_glyph} {dignity.planet}")
                self.dignities_table.setItem(row, 0, planet_item)

                # Sign
                self.dignities_table.setItem(row, 1, QTableWidgetItem(dignity.sign))

                # Essential Dignity (color-coded)
                essential_item = QTableWidgetItem(dignity.essential_dignity)
                if dignity.essential_score > 0:
                    essential_item.setForeground(QColor("#4ade80"))  # Green
                elif dignity.essential_score < 0:
                    essential_item.setForeground(QColor("#f87171"))  # Red
                else:
                    essential_item.setForeground(QColor("#94a3b8"))  # Gray for Peregrine
                self.dignities_table.setItem(row, 2, essential_item)

                # Accidental Score (color-coded)
                accidental_item = QTableWidgetItem(f"{dignity.accidental_score:+d}")
                if dignity.accidental_score > 0:
                    accidental_item.setForeground(QColor("#4ade80"))
                elif dignity.accidental_score < 0:
                    accidental_item.setForeground(QColor("#f87171"))
                self.dignities_table.setItem(row, 3, accidental_item)

                # Total Score (color-coded)
                score_item = QTableWidgetItem(f"{dignity.total_score:+d}")
                if dignity.total_score > 0:
                    score_item.setForeground(QColor("#4ade80"))
                elif dignity.total_score < 0:
                    score_item.setForeground(QColor("#f87171"))
                font = score_item.font()
                font.setBold(True)
                score_item.setFont(font)
                self.dignities_table.setItem(row, 4, score_item)

                # Details (accidental dignities list)
                details = ", ".join(dignity.accidental_dignities)
                details_item = QTableWidgetItem(details)
                details_item.setToolTip(details)
                self.dignities_table.setItem(row, 5, details_item)

                total_score += dignity.total_score

            # Update summary
            if total_score > 0:
                strength_color = "#4ade80"
                strength_text = "Strong"
            elif total_score < -10:
                strength_color = "#f87171"
                strength_text = "Weak"
            else:
                strength_color = "#fbbf24"
                strength_text = "Moderate"

            self.dignities_summary_label.setText(
                f"Total Chart Strength: {total_score:+d} ({strength_text})"
            )
            self.dignities_summary_label.setStyleSheet(f"""
                font-size: 12pt;
                font-weight: 600;
                color: {strength_color};
            """)

        except Exception as exc:
            logger.warning(f"Dignities calculation failed: {exc}")
            self.dignities_summary_label.setText("Total Chart Strength: Error")

    def _render_fixed_stars(self):
        """Populate Fixed Stars table."""
        self.fixed_stars_table.setRowCount(0)
        
        # Calculate if missing and we have a JD
        if not self._fixed_stars and self._julian_day:
            try:
                self._fixed_stars = self._fixed_stars_service.get_star_positions(self._julian_day)
            except Exception as e:
                logger.error(f"Failed to calculate fixed stars: {e}")
        
        if not self._fixed_stars:
            return
            
        # Calculate aspects
        planet_lons = [(p.name, p.degree) for p in self._planets]
        hits_by_star: dict[str, list[str]] = {}
        try:
            # find_aspects returns (planet_name, star, aspect_name, orb)
            found_list = self._fixed_stars_service.find_aspects(
                planet_lons, self._fixed_stars, orb=2.0
            ) 
            
            for pname, star, aspect_name, orb_val in found_list:
                sname = str(getattr(star, "name", star))
                if sname not in hits_by_star:
                    hits_by_star[sname] = []
                
                # Format: "☉ ☌ (0.5°)" - using Unicode glyphs
                p_glyph = self._get_planet_display(pname, use_astro=False)
                a_glyph = self._get_aspect_display(aspect_name, use_astro=False)
                hits_by_star[sname].append(f"{p_glyph} {a_glyph} ({orb_val}°)")
        except Exception as e:
            logger.warning(f"Failed to calc star aspects: {e}")
        
        for star in self._fixed_stars:
            row = self.fixed_stars_table.rowCount()
            self.fixed_stars_table.insertRow(row)
            
            name = str(getattr(star, "name", star))
            degree = getattr(star, 'degree', getattr(star, 'longitude', 0)) # handle both models
            
            self.fixed_stars_table.setItem(row, 0, QTableWidgetItem(name))
            self.fixed_stars_table.setItem(row, 1, QTableWidgetItem(to_zodiacal_string(degree)))
            
            # Aspects
            aspects_str = ", ".join(hits_by_star.get(name, []))
            self.fixed_stars_table.setItem(row, 2, QTableWidgetItem(aspects_str))
    
    def _render_arabic_parts(self):
        """Populate Arabic Parts table."""
        self.arabic_parts_table.setRowCount(0)
        
        if not self._planets or not self._houses:
            return
        
        try:
            # Build lookups
            planet_lons = {p.name.strip(): p.degree for p in self._planets}
            house_cusps = {h.number: h.degree for h in self._houses}
            
            # Day/night determination
            sun_lon = planet_lons.get("Sun", 0)
            asc_lon = house_cusps.get(1, 0)
            is_day = self._arabic_service.is_day_chart(sun_lon, asc_lon)
            
            parts = self._arabic_service.calculate_parts(planet_lons, house_cusps, is_day)
            
            for part in parts:
                row = self.arabic_parts_table.rowCount()
                self.arabic_parts_table.insertRow(row)
                
                self.arabic_parts_table.setItem(row, 0, QTableWidgetItem(part.name))
                self.arabic_parts_table.setItem(row, 1, QTableWidgetItem(part.formula))
                self.arabic_parts_table.setItem(row, 2, QTableWidgetItem(to_zodiacal_string(part.longitude)))
                
        except Exception as exc:
            logger.warning(f"Arabic Parts calculation failed: {exc}")
    
    def _render_midpoints(self):
        """Populate Midpoints views."""
        self.midpoints_table.setRowCount(0)
        
        if not self._planets:
            return
        
        try:
            planet_lons: dict[str, float] = {p.name.strip(): p.degree for p in self._planets}
            classic_only = self.classic7_checkbox.isChecked()
            
            midpoints: list[Midpoint] = self._midpoints_service.calculate_midpoints(planet_lons, classic_only)
            
            for mp in midpoints:
                row = self.midpoints_table.rowCount()
                self.midpoints_table.insertRow(row)
                
                # Format pair as "a/b" with Astronomicon font
                p1 = self._get_planet_display(mp.planet_a)
                p2 = self._get_planet_display(mp.planet_b)
                pair_str = f"{p1}/{p2}"
                
                self.midpoints_table.setItem(row, 0, self._create_astro_item(pair_str))
                self.midpoints_table.setItem(row, 1, QTableWidgetItem(to_zodiacal_string(mp.longitude)))
            
            self._render_midpoints_tree(midpoints)
            
            # Update dial
            if hasattr(self, 'midpoints_dial'):
                dial_data: list[tuple[str, str, float]] = [
                    (mp.planet_a, mp.planet_b, mp.longitude) for mp in midpoints
                ]
                filtered_lons = {k: v for k, v in planet_lons.items() if k.lower() in self.CLASSIC_7}
                self.midpoints_dial.set_data(dial_data, filtered_lons)
                
        except Exception as exc:
            logger.warning(f"Midpoints calculation failed: {exc}")
    
    def _render_midpoints_tree(self, midpoints: Sequence[Midpoint]) -> None:
        """Populate midpoints tree view grouped by planet."""
        self.midpoints_tree.clear()
        
        # Group by planet
        grouped: dict[str, list[Midpoint]] = {}
        for mp in midpoints:
            if mp.planet_a not in grouped:
                grouped[mp.planet_a] = []
            grouped[mp.planet_a].append(mp)
            
            if mp.planet_b not in grouped:
                grouped[mp.planet_b] = []
            grouped[mp.planet_b].append(mp)
        
        if self._astro_font_family != "Arial":
            item_font = QFont(self._astro_font_family, 14)
        else:
            item_font = None

        for planet, m_list in sorted(grouped.items()):
            # Planet Glyph
            display_name = self._get_planet_display(planet)
            
            root = QTreeWidgetItem([display_name, ""])
            if item_font:
                root.setFont(0, item_font)
            
            for mp in m_list:
                # Pair glyphs
                p1 = self._get_planet_display(mp.planet_a)
                p2 = self._get_planet_display(mp.planet_b)
                pair_str = f"{p1}/{p2}"
                
                child = QTreeWidgetItem([pair_str, to_zodiacal_string(mp.longitude)])
                if item_font:
                    child.setFont(0, item_font)
                root.addChild(child)
            
            self.midpoints_tree.addTopLevelItem(root)
        
        self.midpoints_tree.expandAll()
    
    def _render_harmonics(self):
        """Populate Harmonics views."""
        self.harmonics_table.setRowCount(0)
        
        if not self._planets:
            return
        
        try:
            planet_lons = {p.name.strip(): p.degree for p in self._planets}
            harmonic = self.harmonic_spinbox.value()
            
            positions = self._harmonics_service.calculate_harmonic(planet_lons, harmonic)
            
            for hp in positions:
                row = self.harmonics_table.rowCount()
                self.harmonics_table.insertRow(row)
                
                # Planet glyph
                p_char = self._get_planet_display(hp.planet)
                self.harmonics_table.setItem(row, 0, self._create_astro_item(p_char))
                
                self.harmonics_table.setItem(row, 1, QTableWidgetItem(to_zodiacal_string(hp.natal_longitude)))
                self.harmonics_table.setItem(row, 2, QTableWidgetItem(to_zodiacal_string(hp.harmonic_longitude)))
            
            # Update dial
            if hasattr(self, 'harmonics_dial'):
                dial_data = [(hp.planet, hp.harmonic_longitude) for hp in positions if hp.planet.lower() in self.MAIN_BODIES]
                self.harmonics_dial.set_data(dial_data, harmonic)
                
        except Exception as exc:
            logger.warning(f"Harmonics calculation failed: {exc}")
    
    def _render_maat_symbols(self):
        """Populate Maat Symbols table."""
        self.maat_table.setRowCount(0)
        
        if not self._planets:
            return
        
        heaven_colors = {
            1: "#FFD700", 2: "#98FB98", 3: "#87CEEB", 4: "#FF6347",
            5: "#DDA0DD", 6: "#808080", 7: "#FFA500",
        }
        
        for pos in self._planets:
            if pos.name.strip().lower() not in self.MAIN_BODIES:
                continue
            
            planet_name = pos.name.strip().title()
            
            try:
                symbol = self._maat_service.get_symbol(pos.degree)
            except Exception:
                continue
            
            row = self.maat_table.rowCount()
            self.maat_table.insertRow(row)
            
            glyph = self.PLANET_GLYPHS.get(planet_name, "")
            self.maat_table.setItem(row, 0, QTableWidgetItem(f"{glyph} {planet_name}"))
            self.maat_table.setItem(row, 1, QTableWidgetItem(to_zodiacal_string(pos.degree)))
            
            heaven_str = f"{symbol.heaven}. {symbol.heaven_name}"
            heaven_item = QTableWidgetItem(heaven_str)
            heaven_item.setForeground(QColor(heaven_colors.get(symbol.heaven, "#FFFFFF")))
            self.maat_table.setItem(row, 2, heaven_item)
            
            symbol_item = QTableWidgetItem(symbol.text)
            font = symbol_item.font()
            font.setItalic(True)
            symbol_item.setFont(font)
            self.maat_table.setItem(row, 3, symbol_item)
        
        self.maat_table.resizeColumnsToContents()
        self.maat_table.setColumnWidth(3, 400)
    
    def _render_aspects_table(self):
        """Populate Aspects views."""
        self.aspects_table.setRowCount(0)
        
        if not self._planets:
            return
        
        try:
            planet_lons = {p.name.strip(): p.degree for p in self._planets}
            tier = self.aspect_tier_combo.currentIndex()
            orb_factor = self.orb_slider.value() / 100.0
            
            aspects = self._aspects_service.calculate_aspects(planet_lons, tier, orb_factor)
            
            for asp in aspects:
                row = self.aspects_table.rowCount()
                self.aspects_table.insertRow(row)
                
                # Planet A
                pa_char = self._get_planet_display(asp.planet_a)
                self.aspects_table.setItem(row, 0, self._create_astro_item(pa_char))
                
                # Aspect Symbol
                asp_char = self._get_aspect_display(asp.aspect.name)
                item_aspect = self._create_astro_item(asp_char)
                item_aspect.setToolTip(asp.aspect.name) # Show name on hover
                self.aspects_table.setItem(row, 1, item_aspect)
                
                # Planet B
                pb_char = self._get_planet_display(asp.planet_b)
                self.aspects_table.setItem(row, 2, self._create_astro_item(pb_char))
                
                self.aspects_table.setItem(row, 3, QTableWidgetItem(f"{asp.orb:.1f}°"))
                self.aspects_table.setItem(row, 4, QTableWidgetItem("Applying" if asp.is_applying else "Separating"))
            
            self._render_aspects_grid()
            self._render_aspects_legend()
                
        except Exception as exc:
            logger.warning(f"Aspects calculation failed: {exc}")
    
    def _render_aspects_grid(self):
        """Populate Aspects grid matrix."""
        self.aspects_grid.clearContents()
        self.aspects_grid.setRowCount(0)
        self.aspects_grid.setColumnCount(0)
        
        if not self._planets:
            return
        
        try:
            planet_names = [p.name.strip() for p in self._planets]
            planet_lons = {p.name.strip(): p.degree for p in self._planets}
            
            planets = [p for p in planet_names if p.lower() in self.MAIN_BODIES]
            if not planets:
                return
            
            n = len(planets)
            self.aspects_grid.setRowCount(n)
            self.aspects_grid.setColumnCount(n)
            
            headers = [self.PLANET_GLYPHS.get(p.title(), p[:2]) for p in planets]
            # Prepare headers with symbols
            if self._astro_font_family != "Arial":
                header_font = QFont(self._astro_font_family, 12)
                horizontal_header = cast(QHeaderView, self.aspects_grid.horizontalHeader())
                vertical_header = cast(QHeaderView, self.aspects_grid.verticalHeader())
                horizontal_header.setFont(header_font)
                vertical_header.setFont(header_font)
                
                headers = [self._get_planet_display(p) for p in planets]
                self.aspects_grid.setHorizontalHeaderLabels(headers)
                self.aspects_grid.setVerticalHeaderLabels(headers)
            else:
                self.aspects_grid.setHorizontalHeaderLabels(planets)
                self.aspects_grid.setVerticalHeaderLabels(planets)
            
            tier = self.aspect_tier_combo.currentIndex()
            orb_factor = self.orb_slider.value() / 100.0
            
            grid_planet_lons = {p: planet_lons[p] for p in planets if p in planet_lons}
            aspects = self._aspects_service.calculate_aspects(grid_planet_lons, tier, orb_factor)
            
            # Build lookup
            aspect_lookup = {}
            for asp in aspects:
                key1 = (asp.planet_a.title(), asp.planet_b.title())
                key2 = (asp.planet_b.title(), asp.planet_a.title())
                aspect_lookup[key1] = asp
                aspect_lookup[key2] = asp
            
            for i, p1_name in enumerate(planets):
                if p1_name not in planet_lons: continue
                
                # Fill cells (lower triangle + diagonal)
                for j, p2_name in enumerate(planets):
                    if j > i: continue # Only lower triangle
                    
                    if i == j:
                        # Diagonal: Planet Glyph
                        p_char = self._get_planet_display(p1_name)
                        item = self._create_astro_item(p_char)
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        item.setBackground(QColor("#1e293b"))
                        self.aspects_grid.setItem(i, j, item)
                        continue
                    
                    # Aspect Check
                    asp_list = self._aspects_service.calculate_aspects_between(
                        p1_name, planet_lons[p1_name],
                        p2_name, planet_lons[p2_name]
                    )
                    
                    if asp_list:
                        # Take tightest aspect
                        best = min(asp_list, key=lambda x: x.orb)
                        
                        # Aspect Symbol
                        asp_char = self._get_aspect_display(best.aspect.name)
                        item = self._create_astro_item(asp_char)
                        item.setToolTip(f"{best.aspect.name} ({best.orb:.1f}°)")
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        
                        # Get color
                        color_hex = self.ASPECT_COLORS.get(best.aspect.name, COLORS['text_secondary'])
                             
                        item.setForeground(QColor(color_hex))
                        self.aspects_grid.setItem(i, j, item)
                        
                        # Mirror for upper triangle? Usually grid is half or full.
                        # Let's do full grid
                        item_mirror = self._create_astro_item(asp_char)
                        item_mirror.setToolTip(f"{best.aspect.name} ({best.orb:.1f}°)")
                        item_mirror.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        item_mirror.setForeground(QColor(color_hex))
                        self.aspects_grid.setItem(j, i, item_mirror)
            
            self.aspects_grid.resizeColumnsToContents()
            
        except Exception as exc:
            logger.warning(f"Aspects grid rendering failed: {exc}")
    
    def _render_aspects_legend(self):
        """Populate Aspects legend."""
        self.aspects_legend.setRowCount(0)

        for def_obj in self._aspects_service.get_aspect_definitions(include_minor=True):
            row = self.aspects_legend.rowCount()
            self.aspects_legend.insertRow(row)
            
            aspect_char = self._get_aspect_display(def_obj.name)
            self.aspects_legend.setItem(row, 0, self._create_astro_item(aspect_char))
            
            self.aspects_legend.setItem(row, 1, QTableWidgetItem(def_obj.name))
            self.aspects_legend.setItem(row, 2, QTableWidgetItem(f"{def_obj.angle}°"))
    
    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================
    
    def _on_midpoints_filter_changed(self, state: int):
        self._render_midpoints()
    
    def _on_harmonic_changed(self, value: int):
        self._render_harmonics()
    
    def _set_harmonic(self, value: int):
        self.harmonic_spinbox.setValue(value)
    
    def _on_aspects_filter_changed(self, index: int):
        self._render_aspects_table()
    
    def _on_orb_changed(self, value: int):
        self.orb_label.setText(f"{value}%")
        self._render_aspects_table()
    
    # =========================================================================
    # HELPERS
    # =========================================================================
    
    @staticmethod
    def _stretch_last_section(table: QTableWidget):
        header = table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
    
    @staticmethod
    def _set_vertical_section_size(table: QTableWidget, size: int):
        header = table.verticalHeader()
        if header:
            header.setDefaultSectionSize(size)
