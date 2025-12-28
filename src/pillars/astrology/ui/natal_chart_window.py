"""Interactive UI for generating natal charts through OpenAstro2."""
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import tempfile
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import pytz
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QCloseEvent, QFont, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDateTimeEdit,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSlider,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QVBoxLayout,
    QWidget,
)

from ..models import AstrologyEvent, ChartRequest, ChartResult, GeoLocation
from ..models.chart_models import PlanetPosition, HousePosition
from ..services import (
    ArabicPartsService,
    AspectsService,
    ChartComputationError,
    ChartStorageService,
    FixedStarsService,
    HarmonicsService,
    LocationLookupError,
    LocationResult,
    LocationLookupService,
    MidpointsService,
    OpenAstroNotAvailableError,
    OpenAstroService,
    SavedChartSummary,
)
from ..utils import AstrologyPreferences, DefaultLocation
from ..utils.conversions import to_zodiacal_string
from .chart_canvas import ChartCanvas
from .interpretation_widget import InterpretationWidget
from ..services.interpretation_service import InterpretationService
from ..repositories.interpretation_repository import InterpretationRepository


from ..ui.chart_picker_dialog import ChartPickerDialog
    
    
class NatalChartWindow(QMainWindow):


    """Primary UI for creating natal charts inside the astrology pillar."""

    ZODIAC_SIGNS = [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]

    def __init__(self, *_, parent: Optional[QWidget] = None):
        """
          init   logic.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Natal Chart Generator")
        self.resize(1200, 760)

        self._service: Optional[OpenAstroService] = None
        self._service_error: Optional[str] = None
        self._last_svg: Optional[str] = None
        self._house_labels: Dict[str, str] = {}
        self._temp_svg_files: List[str] = []
        self._location_lookup: LocationLookupService = LocationLookupService()
        self._storage_service = ChartStorageService()
        self._fixed_stars_service = FixedStarsService()
        self._arabic_parts_service = ArabicPartsService()
        self._midpoints_service = MidpointsService()
        self._harmonics_service = HarmonicsService()
        self._aspects_service = AspectsService()
        from ..services.maat_symbols_service import MaatSymbolsService
        self._maat_service = MaatSymbolsService()
        self._interpretation_service = InterpretationService(repository=InterpretationRepository())

        self._last_request: Optional[ChartRequest] = None
        self._last_result: Optional[ChartResult] = None
        self._preferences = AstrologyPreferences()
        self._default_location: Optional[DefaultLocation] = None
        self._current_timezone_id: Optional[str] = None

        self._init_service()
        self._build_ui()
        self._initialize_preferences()

    def _stretch_last_section(self, table: QTableWidget) -> None:
        """Safely stretch the last header section when a header exists."""
        header = table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)

    def _set_vertical_section_size(self, table: QTableWidget, size: int) -> None:
        """Safely apply a default row height when a vertical header exists."""
        v_header = table.verticalHeader()
        if v_header:
            v_header.setDefaultSectionSize(size)

    # ------------------------------------------------------------------
    # UI assembly
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header Title
        title = QLabel("Generate Natal Charts with OpenAstro2")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Tab Widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Configuration
        self.config_tab = QWidget()
        config_layout = QVBoxLayout(self.config_tab)
        config_layout.setContentsMargins(8, 8, 8, 8)
        config_layout.addWidget(self._build_input_group())
        config_layout.addStretch()  # Push inputs to top
        self.tabs.addTab(self.config_tab, "Configuration")

        # Tab 2: Report & Visualization
        self.results_tab = QWidget()
        results_layout = QVBoxLayout(self.results_tab)
        results_layout.setContentsMargins(8, 8, 8, 8)
        results_layout.addWidget(self._build_results_splitter())
        self.tabs.addTab(self.results_tab, "Report & Visualization")

        # Tab 3: Chart Canvas (custom in-app rendering)
        self.canvas_tab = QWidget()
        canvas_layout = QVBoxLayout(self.canvas_tab)
        canvas_layout.setContentsMargins(8, 8, 8, 8)
        self.chart_canvas = ChartCanvas()
        canvas_layout.addWidget(self.chart_canvas)
        self.tabs.addTab(self.canvas_tab, "Chart Canvas")

        # Tab 4: Advanced
        self.advanced_tab = QWidget()
        adv_layout = QVBoxLayout(self.advanced_tab)
        adv_layout.setContentsMargins(8, 8, 8, 8)
        adv_layout.addWidget(self._build_advanced_tab())
        self.tabs.addTab(self.advanced_tab, "Advanced")

        # Tab 5: Interpretation
        self.interpretation_tab = QWidget()
        interp_layout = QVBoxLayout(self.interpretation_tab)
        interp_layout.setContentsMargins(0, 0, 0, 0)
        self.interpretation_widget = InterpretationWidget()
        interp_layout.addWidget(self.interpretation_widget)
        self.tabs.addTab(self.interpretation_tab, "Interpretation")

        # Persistent Action Row (Bottom)
        layout.addLayout(self._build_action_row())

        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.status_label)

        if self._service_error:
            self._set_status(self._service_error)

    def _build_input_group(self) -> QGroupBox:
        group = QGroupBox("Chart Details")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit("Sample Chart")
        form.addRow("Chart Name", self.name_input)

        self.datetime_input = QDateTimeEdit(QDateTime.currentDateTimeUtc())
        self.datetime_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.datetime_input.setCalendarPopup(True)
        form.addRow("Date & Time", self.datetime_input)

        self.timezone_input = QDoubleSpinBox()
        self.timezone_input.setRange(-14.0, 14.0)
        self.timezone_input.setSingleStep(0.25)
        self.timezone_input.setDecimals(2)
        self.timezone_input.setValue(0.0)
        form.addRow("Timezone Offset (hrs)", self.timezone_input)

        self.location_name_input = QLineEdit("Jerusalem, IL")
        location_row = QHBoxLayout()
        location_row.addWidget(self.location_name_input, stretch=1)
        self.search_location_button = QPushButton("Search City...")
        self.search_location_button.clicked.connect(self._search_location)
        location_row.addWidget(self.search_location_button)
        location_row_widget = QWidget()
        location_row_widget.setLayout(location_row)
        form.addRow("Location Label", location_row_widget)

        defaults_row = QHBoxLayout()
        self.use_default_button = QPushButton("Use Default")
        self.use_default_button.clicked.connect(self._use_default_location)
        self.use_default_button.setEnabled(False)
        defaults_row.addWidget(self.use_default_button)
        self.save_default_button = QPushButton("Save as Default")
        self.save_default_button.clicked.connect(self._save_default_location)
        defaults_row.addWidget(self.save_default_button)
        defaults_row.addStretch()
        defaults_widget = QWidget()
        defaults_widget.setLayout(defaults_row)
        form.addRow("Defaults", defaults_widget)

        self.latitude_input = QDoubleSpinBox()
        self.latitude_input.setRange(-90.0, 90.0)
        self.latitude_input.setDecimals(6)
        self.latitude_input.setValue(31.7683)
        form.addRow("Latitude", self.latitude_input)

        self.longitude_input = QDoubleSpinBox()
        self.longitude_input.setRange(-180.0, 180.0)
        self.longitude_input.setDecimals(6)
        self.longitude_input.setValue(35.2137)
        form.addRow("Longitude", self.longitude_input)

        self.elevation_input = QSpinBox()
        self.elevation_input.setRange(-500, 9000)
        self.elevation_input.setValue(754)
        form.addRow("Elevation (m)", self.elevation_input)

        self.categories_input = QLineEdit()
        self.categories_input.setPlaceholderText("Comma separated (e.g. Clients, Family)")
        form.addRow("Categories", self.categories_input)

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Comma separated (e.g. natal, follow-up)")
        form.addRow("Tags", self.tags_input)

        self.house_system_combo = QComboBox()
        for code, label in sorted(self._house_labels.items()):
            self.house_system_combo.addItem(f"{label} ({code})", code)
        if self.house_system_combo.count() == 0:
            self.house_system_combo.addItem("Placidus (P)", "P")
        form.addRow("House System", self.house_system_combo)

        self.include_svg_checkbox = QCheckBox("Include SVG diagram")
        self.include_svg_checkbox.setChecked(True)
        form.addRow("SVG Output", self.include_svg_checkbox)

        self.notes_input = QPlainTextEdit()
        self.notes_input.setPlaceholderText("Chart notes / description")
        self.notes_input.setFixedHeight(70)
        form.addRow("Notes", self.notes_input)

        return group

    def _build_action_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addStretch()

        self.load_chart_button = QPushButton("Load Chart...")
        self.load_chart_button.clicked.connect(self._load_chart)
        row.addWidget(self.load_chart_button)

        self.save_chart_button = QPushButton("Save Chart")
        self.save_chart_button.clicked.connect(self._save_chart)
        self.save_chart_button.setEnabled(False)
        row.addWidget(self.save_chart_button)

        self.transit_button = QPushButton("Current Transit")
        self.transit_button.clicked.connect(self._generate_current_transit)
        row.addWidget(self.transit_button)

        self.generate_button = QPushButton("Generate Chart")
        self.generate_button.clicked.connect(self._generate_chart)
        row.addWidget(self.generate_button)

        self.clear_button = QPushButton("Clear Results")
        self.clear_button.clicked.connect(self._clear_results)
        row.addWidget(self.clear_button)

        self.interpret_button = QPushButton("Interpret")
        self.interpret_button.clicked.connect(lambda: self._generate_interpretation(switch_tab=True))
        self.interpret_button.setEnabled(False)
        row.addWidget(self.interpret_button)

        if self._service is None:
            self.generate_button.setEnabled(False)

        return row

    def _build_results_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        splitter.addWidget(self._build_planet_group())
        splitter.addWidget(self._build_misc_group())

        splitter.setSizes([650, 450])
        return splitter

    def _build_advanced_tab(self) -> QWidget:
        """Build the nested tabs for advanced features."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.advanced_tabs = QTabWidget()
        layout.addWidget(self.advanced_tabs)
        
        # 1. Fixed Stars
        self.fixed_stars_tab = QWidget()
        self.fixed_stars_table = QTableWidget(0, 2)
        self.fixed_stars_table.setHorizontalHeaderLabels(["Star", "Position"])
        self._stretch_last_section(self.fixed_stars_table)
        
        fs_layout = QVBoxLayout(self.fixed_stars_tab)
        fs_layout.addWidget(self.fixed_stars_table)
        self.advanced_tabs.addTab(self.fixed_stars_tab, "Fixed Stars")
        
        # 2. Arabic Parts
        self.arabic_parts_tab = QWidget()
        self.arabic_parts_table = QTableWidget(0, 3)
        self.arabic_parts_table.setHorizontalHeaderLabels(["Part", "Formula", "Position"])
        self._stretch_last_section(self.arabic_parts_table)
        
        ap_layout = QVBoxLayout(self.arabic_parts_tab)
        ap_layout.addWidget(self.arabic_parts_table)
        self.advanced_tabs.addTab(self.arabic_parts_tab, "Arabic Parts")
        
        # 3. Midpoints
        self.midpoints_tab = QWidget()
        mp_main_layout = QVBoxLayout(self.midpoints_tab)
        
        # Controls row
        mp_controls = QHBoxLayout()
        
        # Classic 7 filter checkbox
        self.classic7_checkbox = QCheckBox("Classic 7 Only")
        self.classic7_checkbox.setChecked(True)
        self.classic7_checkbox.stateChanged.connect(self._on_midpoints_filter_changed)
        mp_controls.addWidget(self.classic7_checkbox)
        mp_controls.addStretch()
        mp_main_layout.addLayout(mp_controls)
        
        # Sub-tabs for Tree, Dial, and Table views
        self.midpoints_subtabs = QTabWidget()
        
        # Tree view
        from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
        tree_widget = QWidget()
        tree_layout = QVBoxLayout(tree_widget)
        self.midpoints_tree = QTreeWidget()
        self.midpoints_tree.setHeaderLabels(["Planet / Midpoint", "Position"])
        self.midpoints_tree.setColumnWidth(0, 200)
        tree_layout.addWidget(self.midpoints_tree)
        self.midpoints_subtabs.addTab(tree_widget, "Tree")
        
        # Dial view
        from .midpoints_dial import MidpointsDial
        self.midpoints_dial = MidpointsDial()
        self.midpoints_subtabs.addTab(self.midpoints_dial, "Dial")
        
        # Table view (original)
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        self.midpoints_table = QTableWidget(0, 2)
        self.midpoints_table.setHorizontalHeaderLabels(["Pair", "Midpoint"])
        self._stretch_last_section(self.midpoints_table)
        table_layout.addWidget(self.midpoints_table)
        self.midpoints_subtabs.addTab(table_widget, "Table")
        
        mp_main_layout.addWidget(self.midpoints_subtabs)
        self.advanced_tabs.addTab(self.midpoints_tab, "Midpoints")
        
        # 4. Harmonics
        self.harmonics_tab = QWidget()
        h_layout = QVBoxLayout(self.harmonics_tab)
        
        # Controls row
        controls_layout = QHBoxLayout()
        
        # Harmonic number spinbox
        controls_layout.addWidget(QLabel("Harmonic:"))
        self.harmonic_spinbox = QSpinBox()
        self.harmonic_spinbox.setRange(1, 360)
        self.harmonic_spinbox.setValue(4)
        self.harmonic_spinbox.valueChanged.connect(self._on_harmonic_changed)
        controls_layout.addWidget(self.harmonic_spinbox)
        
        # Preset buttons
        for h in [4, 5, 7, 9]:
            btn = QPushButton(str(h))
            btn.setToolTip(f"Harmonic {h}")
            btn.setMinimumWidth(50)
            btn.setMaximumWidth(50)
            btn.clicked.connect(lambda checked, hval=h: self._set_harmonic(hval))
            controls_layout.addWidget(btn)
        
        controls_layout.addStretch()
        h_layout.addLayout(controls_layout)
        
        # Sub-tabs for Dial and Table views
        self.harmonics_subtabs = QTabWidget()
        
        # Dial view
        from .harmonics_dial import HarmonicsDial
        self.harmonics_dial = HarmonicsDial()
        self.harmonics_subtabs.addTab(self.harmonics_dial, "Dial")
        
        # Table view
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        self.harmonics_table = QTableWidget(0, 3)
        self.harmonics_table.setHorizontalHeaderLabels(["Planet", "Natal", "Harmonic"])
        self._stretch_last_section(self.harmonics_table)
        table_layout.addWidget(self.harmonics_table)
        self.harmonics_subtabs.addTab(table_widget, "Table")
        
        h_layout.addWidget(self.harmonics_subtabs)
        
        self.advanced_tabs.addTab(self.harmonics_tab, "Harmonics")
        
        # 5. Maat Symbols
        self.maat_tab = QWidget()
        maat_layout = QVBoxLayout(self.maat_tab)
        
        # Info label
        maat_info = QLabel("Egyptian degree symbols - each degree has a unique symbolic description")
        maat_info.setStyleSheet("color: #888; font-style: italic;")
        maat_layout.addWidget(maat_info)
        
        # Table for planet symbols
        self.maat_table = QTableWidget(0, 4)
        self.maat_table.setHorizontalHeaderLabels(["Planet", "Position", "Heaven", "Symbol"])
        self._stretch_last_section(self.maat_table)
        self.maat_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.maat_table.setWordWrap(True)
        self._set_vertical_section_size(self.maat_table, 60)  # Taller rows
        maat_layout.addWidget(self.maat_table)
        
        self.advanced_tabs.addTab(self.maat_tab, "Maat Symbols")

        
        # 5. Aspects Table
        self.aspects_tab = QWidget()
        asp_layout = QVBoxLayout(self.aspects_tab)
        
        # Controls row
        asp_controls = QHBoxLayout()
        
        # Aspect tier dropdown
        asp_controls.addWidget(QLabel("Show:"))
        self.aspect_tier_combo = QComboBox()
        self.aspect_tier_combo.addItems([
            "Major Only",
            "Major + Common Minor",
            "Major + All Minor",
            "All Aspects"
        ])
        self.aspect_tier_combo.setCurrentIndex(0)
        self.aspect_tier_combo.currentIndexChanged.connect(self._on_aspects_filter_changed)
        asp_controls.addWidget(self.aspect_tier_combo)
        
        # Orb slider
        asp_controls.addWidget(QLabel("Orb:"))
        self.orb_slider = QSlider(Qt.Orientation.Horizontal)
        self.orb_slider.setRange(50, 150)
        self.orb_slider.setValue(100)
        self.orb_slider.setFixedWidth(100)
        self.orb_slider.valueChanged.connect(self._on_orb_changed)
        asp_controls.addWidget(self.orb_slider)
        
        self.orb_label = QLabel("100%")
        asp_controls.addWidget(self.orb_label)
        
        asp_controls.addStretch()
        asp_layout.addLayout(asp_controls)
        
        # Sub-tabs for Grid and List views
        self.aspects_subtabs = QTabWidget()
        
        # Grid view tab
        grid_widget = QWidget()
        grid_layout = QVBoxLayout(grid_widget)
        self.aspects_grid = QTableWidget()
        self.aspects_grid.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        grid_layout.addWidget(self.aspects_grid)
        self.aspects_subtabs.addTab(grid_widget, "Grid")
        
        # List view tab (existing table)
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        self.aspects_table = QTableWidget(0, 5)
        self.aspects_table.setHorizontalHeaderLabels(["Planet A", "Aspect", "Planet B", "Orb", "Type"])
        self._stretch_last_section(self.aspects_table)
        list_layout.addWidget(self.aspects_table)
        self.aspects_subtabs.addTab(list_widget, "List")
        
        # Legend tab
        legend_widget = QWidget()
        legend_layout = QVBoxLayout(legend_widget)
        self.aspects_legend = QTableWidget()
        self.aspects_legend.setColumnCount(3)
        self.aspects_legend.setHorizontalHeaderLabels(["Symbol", "Aspect", "Angle"])
        self._stretch_last_section(self.aspects_legend)
        self.aspects_legend.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        legend_layout.addWidget(self.aspects_legend)
        self.aspects_subtabs.addTab(legend_widget, "Legend")
        
        asp_layout.addWidget(self.aspects_subtabs)
        
        self.advanced_tabs.addTab(self.aspects_tab, "Aspects")
        
        return container

    # ------------------------------------------------------------------
    # UI assembly
    # ------------------------------------------------------------------
    def _build_planet_group(self) -> QGroupBox:
        group = QGroupBox("Planetary Positions")
        layout = QVBoxLayout(group)

        # Changed to 2 columns: Body, Position
        self.planets_table = QTableWidget(0, 2)
        self.planets_table.setHorizontalHeaderLabels(["Body", "Position"])
        header = self.planets_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
        layout.addWidget(self.planets_table)
        return group

    def _build_misc_group(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        
        # Houses
        dup_grp = QGroupBox("House Cusps")
        dup_layout = QVBoxLayout(dup_grp)
        self.houses_table = QTableWidget(0, 2)
        self.houses_table.setHorizontalHeaderLabels(["House", "Position"])
        dup_layout.addWidget(self.houses_table)
        layout.addWidget(dup_grp)

        # Aspects
        asp_grp = QGroupBox("Aspects / Data")
        asp_layout = QVBoxLayout(asp_grp)
        self.aspects_text = QPlainTextEdit()
        self.aspects_text.setReadOnly(True)
        asp_layout.addWidget(self.aspects_text)
        layout.addWidget(asp_grp)

        return container

    # ------------------------------------------------------------------
    # Service wiring
    # ------------------------------------------------------------------
    def _init_service(self) -> None:
        try:
            self._service = OpenAstroService()
            self._house_labels = self._service.list_house_systems()
        except OpenAstroNotAvailableError as exc:
            self._service_error = str(exc)
            self._service = None
            self._house_labels = {}

    def _generate_chart(self) -> None:
        if self._service is None:
            QMessageBox.warning(self, "Unavailable", "OpenAstro2 is not available.")
            return

        try:
            request = self._build_request()
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid Input", str(exc))
            return

        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
        try:
            result = self._service.generate_chart(request)
        except ChartComputationError as exc:
            QMessageBox.critical(self, "Calculation Error", str(exc))
            self._set_status(str(exc))
        except Exception as exc: 
            QMessageBox.critical(self, "Unexpected Error", str(exc))
            self._set_status(f"Error: {exc}")
        else:
            self._last_request = request
            self._last_result = result
            self.save_chart_button.setEnabled(True)
            self.interpret_button.setEnabled(True)
            self._render_result(result)
            self.tabs.setCurrentWidget(self.results_tab)
            self._set_status("Chart generated successfully.")
            
            # Auto-generate interpretation (without switching tabs) so it is ready
            self._generate_interpretation(switch_tab=False)

    def _generate_interpretation(self, switch_tab: bool = True) -> None:
        """Generate and display the chart interpretation."""
        if not self._last_result:
            return
            
        try:
            # We don't necessarily need busy cursor for this fast operation, 
            # but we keep it if switching tabs to indicate activity.
            if switch_tab:
                QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
                
            chart_name = self._last_request.primary_event.name if self._last_request else "Chart"
            report = self._interpretation_service.interpret_chart(self._last_result, chart_name)
            self.interpretation_widget.display_report(report)
            
            if switch_tab:
                self.tabs.setCurrentWidget(self.interpretation_tab)
                
        except Exception as e:
             # Only show error if user explicitly requested it (clicked button), 
             # otherwise log it to avoid spamming user on auto-gen
             if switch_tab:
                 QMessageBox.critical(self, "Interpretation Error", str(e))
             else:
                 print(f"Auto-interpretation failed: {e}")
        finally:
            if switch_tab:
                QApplication.restoreOverrideCursor()

    def _build_request(self) -> ChartRequest:
        dt = self.datetime_input.dateTime().toPyDateTime()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
            
        loc = GeoLocation(
            name=self.location_name_input.text().strip() or "Unknown",
            latitude=self.latitude_input.value(),
            longitude=self.longitude_input.value(),
            elevation=float(self.elevation_input.value())
        )
        
        event = AstrologyEvent(
            name=self.name_input.text().strip() or "Natal Chart",
            timestamp=dt,
            location=loc,
            timezone_offset=self.timezone_input.value()
        )
        
        selected_house = self.house_system_combo.currentData()
        settings = {"astrocfg": {"houses_system": selected_house}} if selected_house else {}
        
        request = ChartRequest(
            primary_event=event,
            include_svg=self.include_svg_checkbox.isChecked(),
            settings=settings
        )
        return request

    def _clear_results(self) -> None:
        self.planets_table.setRowCount(0)
        self.houses_table.setRowCount(0)
        self.aspects_text.clear()
        self._last_result = None
        self._last_svg = None
        self.save_chart_button.setEnabled(False)
        if hasattr(self, 'chart_canvas'):
            self.chart_canvas.set_data([], [])
        self._set_status("Results cleared.")

    def _render_aspects(self, result: ChartResult) -> None:
        if hasattr(self, 'aspects_text'):
             data = result.aspect_summary or result.raw_payload
             text = json.dumps(data, indent=2, default=str)
             self.aspects_text.setPlainText(text)

    def _handle_svg(self, result: ChartResult) -> None:
        self._last_svg = result.svg_document
        # SVG viewing now in-app; no external browser dependency

    def _render_result(self, result) -> None:
        self._render_planets(result)
        self._render_houses(result)
        self._render_aspects(result)
        self._render_fixed_stars(result)
        self._render_arabic_parts(result)
        self._render_midpoints(result)
        self._render_harmonics(result)
        self._render_aspects_table(result)
        self._render_maat_symbols(result)
        self._handle_svg(result)

        if hasattr(self, 'chart_canvas'):
            self.chart_canvas.set_data(result.planet_positions, result.house_positions)

    def _render_planets(self, result) -> None:
        self.planets_table.setRowCount(0)
        for position in result.planet_positions:
            row = self.planets_table.rowCount()
            self.planets_table.insertRow(row)
            self.planets_table.setItem(row, 0, QTableWidgetItem(position.name))
            
            # Format: DD° Sign MM'
            formatted_pos = to_zodiacal_string(position.degree)
            self.planets_table.setItem(row, 1, QTableWidgetItem(formatted_pos))

    def _render_houses(self, result) -> None:
        self.houses_table.setRowCount(0)
        for house in result.house_positions:
            row = self.houses_table.rowCount()
            self.houses_table.insertRow(row)
            self.houses_table.setItem(row, 0, QTableWidgetItem(str(house.number)))
            
            formatted_pos = to_zodiacal_string(house.degree)
            self.houses_table.setItem(row, 1, QTableWidgetItem(formatted_pos))

    def _render_fixed_stars(self, result: ChartResult) -> None:
        """Populate the Fixed Stars table with star positions."""
        if not hasattr(self, 'fixed_stars_table'):
            return
            
        self.fixed_stars_table.setRowCount(0)
        
        # Get Julian Day from the request
        if not self._last_request:
            return
            
        try:
            import swisseph as swe
            dt = self._last_request.primary_event.timestamp
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            
            # Convert to Julian Day
            jd = swe.julday(
                dt.year, dt.month, dt.day,
                dt.hour + dt.minute / 60.0 + dt.second / 3600.0
            )
            
            # Get fixed star positions
            star_positions = self._fixed_stars_service.get_star_positions(jd)
            
            for star in star_positions:
                row = self.fixed_stars_table.rowCount()
                self.fixed_stars_table.insertRow(row)
                
                # Star name + constellation
                name_item = QTableWidgetItem(f"{star.name} ({star.constellation})")
                self.fixed_stars_table.setItem(row, 0, name_item)
                
                # Position in zodiacal format
                pos_str = to_zodiacal_string(star.longitude)
                self.fixed_stars_table.setItem(row, 1, QTableWidgetItem(pos_str))
                
        except Exception as exc:
            # Log but don't crash
            import logging
            logging.getLogger(__name__).warning(f"Fixed stars calculation failed: {exc}")

    def _render_arabic_parts(self, result: ChartResult) -> None:
        """Populate the Arabic Parts table."""
        if not hasattr(self, 'arabic_parts_table'):
            return
            
        self.arabic_parts_table.setRowCount(0)
        
        if not result.planet_positions or not result.house_positions:
            return
            
        try:
            # Build lookup dicts
            planet_lons = {}
            for pos in result.planet_positions:
                # Normalize name for lookup
                name = pos.name.strip()
                planet_lons[name] = pos.degree
            
            house_cusps = {}
            for h in result.house_positions:
                house_cusps[h.number] = h.degree
            
            # Determine if day or night chart
            sun_lon = planet_lons.get("Sun", 0)
            asc_lon = house_cusps.get(1, 0)
            is_day = self._arabic_parts_service.is_day_chart(sun_lon, asc_lon)
            
            # Calculate Parts
            parts = self._arabic_parts_service.calculate_parts(
                planet_lons, house_cusps, is_day
            )
            
            for part in parts:
                row = self.arabic_parts_table.rowCount()
                self.arabic_parts_table.insertRow(row)
                
                # Part name
                self.arabic_parts_table.setItem(row, 0, QTableWidgetItem(part.name))
                
                # Formula
                self.arabic_parts_table.setItem(row, 1, QTableWidgetItem(part.formula))
                
                # Position in zodiacal format
                pos_str = to_zodiacal_string(part.longitude)
                self.arabic_parts_table.setItem(row, 2, QTableWidgetItem(pos_str))
                
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(f"Arabic Parts calculation failed: {exc}")

    def _render_midpoints(self, result: ChartResult) -> None:
        """Populate the Midpoints table."""
        if not hasattr(self, 'midpoints_table'):
            return
            
        self.midpoints_table.setRowCount(0)
        
        if not result.planet_positions:
            return
            
        try:
            # Build planet longitude dict
            planet_lons = {}
            for pos in result.planet_positions:
                planet_lons[pos.name.strip()] = pos.degree
            
            # Get filter state
            classic_only = self.classic7_checkbox.isChecked() if hasattr(self, 'classic7_checkbox') else True
            
            # Calculate midpoints
            midpoints = self._midpoints_service.calculate_midpoints(planet_lons, classic_only)
            
            for mp in midpoints:
                row = self.midpoints_table.rowCount()
                self.midpoints_table.insertRow(row)
                
                # Pair name
                pair_str = f"{mp.planet_a}/{mp.planet_b}"
                self.midpoints_table.setItem(row, 0, QTableWidgetItem(pair_str))
                
                # Midpoint position
                pos_str = to_zodiacal_string(mp.longitude)
                self.midpoints_table.setItem(row, 1, QTableWidgetItem(pos_str))
            
            # Update tree view
            self._render_midpoints_tree(midpoints)
            
            # Update dial view
            if hasattr(self, 'midpoints_dial'):
                dial_data = [(mp.planet_a, mp.planet_b, mp.longitude) for mp in midpoints]
                # Filter planet_lons to main bodies
                main_bodies = {"sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"}
                filtered_lons = {k: v for k, v in planet_lons.items() if k.lower() in main_bodies}
                self.midpoints_dial.set_data(dial_data, filtered_lons)
                
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(f"Midpoints calculation failed: {exc}")

    def _render_midpoints_tree(self, midpoints) -> None:
        """Populate the midpoints tree view grouped by planet."""
        if not hasattr(self, 'midpoints_tree'):
            return
        
        from PyQt6.QtWidgets import QTreeWidgetItem
        
        self.midpoints_tree.clear()
        
        # Group midpoints by planet
        tree_data: dict = {}
        for mp in midpoints:
            # Add to planet A's tree
            if mp.planet_a not in tree_data:
                tree_data[mp.planet_a] = []
            tree_data[mp.planet_a].append(mp)
            
            # Add to planet B's tree
            if mp.planet_b not in tree_data:
                tree_data[mp.planet_b] = []
            tree_data[mp.planet_b].append(mp)
        
        # Planet glyphs
        glyphs = {
            "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
            "Mars": "♂", "Jupiter": "♃", "Saturn": "♄",
        }
        
        # Build tree
        for planet, mps in sorted(tree_data.items()):
            glyph = glyphs.get(planet.title(), planet[:2])
            planet_item = QTreeWidgetItem([f"{glyph} {planet.title()}", ""])
            
            for mp in mps:
                other = mp.planet_b if mp.planet_a == planet else mp.planet_a
                other_glyph = glyphs.get(other.title(), other[:2])
                pos_str = to_zodiacal_string(mp.longitude)
                child = QTreeWidgetItem([f"  {glyph}/{other_glyph}", pos_str])
                planet_item.addChild(child)
            
            self.midpoints_tree.addTopLevelItem(planet_item)
        
        self.midpoints_tree.expandAll()


    def _on_midpoints_filter_changed(self, state: int) -> None:
        """Re-render midpoints when filter changes."""
        if self._last_result:
            self._render_midpoints(self._last_result)

    def _render_harmonics(self, result: ChartResult) -> None:
        """Populate the Harmonics table."""
        if not hasattr(self, 'harmonics_table'):
            return
            
        self.harmonics_table.setRowCount(0)
        
        if not result.planet_positions:
            return
            
        try:
            # Build planet longitude dict
            planet_lons = {}
            for pos in result.planet_positions:
                planet_lons[pos.name.strip()] = pos.degree
            
            # Get harmonic number
            harmonic = self.harmonic_spinbox.value() if hasattr(self, 'harmonic_spinbox') else 4
            
            # Calculate harmonic positions
            positions = self._harmonics_service.calculate_harmonic(planet_lons, harmonic)
            
            for hp in positions:
                row = self.harmonics_table.rowCount()
                self.harmonics_table.insertRow(row)
                
                # Planet name
                self.harmonics_table.setItem(row, 0, QTableWidgetItem(hp.planet))
                
                # Natal position
                natal_str = to_zodiacal_string(hp.natal_longitude)
                self.harmonics_table.setItem(row, 1, QTableWidgetItem(natal_str))
                
                # Harmonic position
                harmonic_str = to_zodiacal_string(hp.harmonic_longitude)
                self.harmonics_table.setItem(row, 2, QTableWidgetItem(harmonic_str))
            
            # Update dial widget (filter to main 10 planets only)
            if hasattr(self, 'harmonics_dial'):
                main_bodies = {"sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"}
                dial_data = [(hp.planet, hp.harmonic_longitude) for hp in positions if hp.planet.lower() in main_bodies]
                self.harmonics_dial.set_data(dial_data, harmonic)
                
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(f"Harmonics calculation failed: {exc}")

    def _render_maat_symbols(self, result: ChartResult) -> None:
        """Populate the Maat Symbols table with symbols for each planet's degree."""
        if not hasattr(self, 'maat_table'):
            return
        
        self.maat_table.setRowCount(0)
        
        if not result.planet_positions:
            return
        
        # Planet glyphs
        glyphs = {
            "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
            "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
            "Neptune": "♆", "Pluto": "♇",
        }
        
        # Heaven colors for visual distinction
        heaven_colors = {
            1: "#FFD700",  # Ptah - Gold
            2: "#98FB98",  # Hathor - Pale Green
            3: "#87CEEB",  # Thoth - Sky Blue
            4: "#FF6347",  # Horus/Set - Tomato Red
            5: "#DDA0DD",  # Ma'at - Plum
            6: "#808080",  # Osiris - Gray
            7: "#FFA500",  # Ra - Orange
        }
        
        # Main 10 planets only
        main_bodies = {"sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"}
        
        for pos in result.planet_positions:
            if pos.name.strip().lower() not in main_bodies:
                continue
            
            planet_name = pos.name.strip().title()
            
            # Get Maat symbol
            symbol = self._maat_service.get_symbol(pos.degree)
            
            row = self.maat_table.rowCount()
            self.maat_table.insertRow(row)
            
            # Planet name with glyph
            glyph = glyphs.get(planet_name, "")
            planet_item = QTableWidgetItem(f"{glyph} {planet_name}")
            self.maat_table.setItem(row, 0, planet_item)
            
            # Position
            pos_str = to_zodiacal_string(pos.degree)
            self.maat_table.setItem(row, 1, QTableWidgetItem(pos_str))
            
            # Heaven
            heaven_str = f"{symbol.heaven}. {symbol.heaven_name}"
            heaven_item = QTableWidgetItem(heaven_str)
            color = heaven_colors.get(symbol.heaven, "#FFFFFF")
            heaven_item.setForeground(QColor(color))
            self.maat_table.setItem(row, 2, heaven_item)
            
            # Symbol text (italicized)
            symbol_item = QTableWidgetItem(symbol.text)
            font = symbol_item.font()
            font.setItalic(True)
            symbol_item.setFont(font)
            self.maat_table.setItem(row, 3, symbol_item)
        
        # Resize columns
        self.maat_table.resizeColumnsToContents()
        self.maat_table.setColumnWidth(3, 400)  # Symbol column wider


    def _on_harmonic_changed(self, value: int) -> None:
        """Re-render harmonics when spinbox value changes."""
        if self._last_result:
            self._render_harmonics(self._last_result)

    def _set_harmonic(self, value: int) -> None:
        """Set harmonic spinbox to preset value."""
        if hasattr(self, 'harmonic_spinbox'):
            self.harmonic_spinbox.setValue(value)

    def _render_aspects_table(self, result: ChartResult) -> None:
        """Populate the Aspects table."""
        if not hasattr(self, 'aspects_table'):
            return
            
        self.aspects_table.setRowCount(0)
        
        if not result.planet_positions:
            return
            
        try:
            # Build planet longitude dict
            planet_lons = {}
            for pos in result.planet_positions:
                planet_lons[pos.name.strip()] = pos.degree
            
            # Get filter settings
            tier = self.aspect_tier_combo.currentIndex() if hasattr(self, 'aspect_tier_combo') else 0
            orb_factor = self.orb_slider.value() / 100.0 if hasattr(self, 'orb_slider') else 1.0
            
            # Calculate aspects
            aspects = self._aspects_service.calculate_aspects(planet_lons, tier, orb_factor)
            
            for asp in aspects:
                row = self.aspects_table.rowCount()
                self.aspects_table.insertRow(row)
                
                # Planet A
                self.aspects_table.setItem(row, 0, QTableWidgetItem(asp.planet_a))
                
                # Aspect with symbol
                aspect_str = f"{asp.aspect.symbol} {asp.aspect.name}"
                self.aspects_table.setItem(row, 1, QTableWidgetItem(aspect_str))
                
                # Planet B
                self.aspects_table.setItem(row, 2, QTableWidgetItem(asp.planet_b))
                
                # Orb
                orb_str = f"{asp.orb:.1f}°"
                self.aspects_table.setItem(row, 3, QTableWidgetItem(orb_str))
                
                # Type (applying/separating)
                type_str = "Applying" if asp.is_applying else "Separating"
                self.aspects_table.setItem(row, 4, QTableWidgetItem(type_str))
                
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(f"Aspects calculation failed: {exc}")
        
        # Also render grid and legend
        self._render_aspects_grid(result)
        self._render_aspects_legend()

    def _render_aspects_grid(self, result: ChartResult) -> None:
        """Populate the Aspects grid matrix."""
        if not hasattr(self, 'aspects_grid'):
            return
            
        self.aspects_grid.clearContents()
        self.aspects_grid.setRowCount(0)
        self.aspects_grid.setColumnCount(0)
        
        if not result.planet_positions:
            return
            
        try:
            # Get planet list
            planet_names = [pos.name.strip() for pos in result.planet_positions]
            planet_lons = {pos.name.strip(): pos.degree for pos in result.planet_positions}
            
            # Planet glyphs
            glyphs = {
                "Sun": "☉", "Moon": "☽", "Mercury": "☿", "Venus": "♀",
                "Mars": "♂", "Jupiter": "♃", "Saturn": "♄", "Uranus": "♅",
                "Neptune": "♆", "Pluto": "♇", "North Node": "☊", "True Node": "☊",
                "South Node": "☋", "Chiron": "⚷",
            }
            
            # Filter to main bodies (case-insensitive)
            main_bodies_lower = {"sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"}
            planets = [p for p in planet_names if p.lower() in main_bodies_lower]
            

            if not planets:
                return
            
            n = len(planets)
            self.aspects_grid.setRowCount(n)
            self.aspects_grid.setColumnCount(n)
            
            # Set headers with glyphs (use title case for lookup)
            headers = [glyphs.get(p.title(), p[:2]) for p in planets]
            self.aspects_grid.setHorizontalHeaderLabels(headers)
            self.aspects_grid.setVerticalHeaderLabels(headers)
            
            # Get filter settings
            tier = self.aspect_tier_combo.currentIndex() if hasattr(self, 'aspect_tier_combo') else 0
            orb_factor = self.orb_slider.value() / 100.0 if hasattr(self, 'orb_slider') else 1.0
            
            # Filter planet_lons to only main bodies for grid calculation
            grid_planet_lons = {p: planet_lons[p] for p in planets if p in planet_lons}
            
            # Calculate aspects only for the 10 main planets
            aspects = self._aspects_service.calculate_aspects(grid_planet_lons, tier, orb_factor)
            

            # Build lookup dict (normalize keys to title case)
            aspect_lookup = {}
            for asp in aspects:
                key1 = (asp.planet_a.title(), asp.planet_b.title())
                key2 = (asp.planet_b.title(), asp.planet_a.title())
                aspect_lookup[key1] = asp.aspect.symbol
                aspect_lookup[key2] = asp.aspect.symbol
            

            # Fill grid (normalize planet names for lookup)
            for i, p1 in enumerate(planets):
                for j, p2 in enumerate(planets):
                    if i == j:
                        item = QTableWidgetItem("-")
                    else:
                        symbol = aspect_lookup.get((p1.title(), p2.title()), "")
                        item = QTableWidgetItem(symbol)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.aspects_grid.setItem(i, j, item)
            
            # Resize columns to fit
            self.aspects_grid.resizeColumnsToContents()
            self.aspects_grid.resizeRowsToContents()
                
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(f"Aspects grid failed: {exc}")

    def _render_aspects_legend(self) -> None:
        """Populate the aspects legend table."""
        if not hasattr(self, 'aspects_legend'):
            return
            
        from ..services.aspects_service import ASPECT_TIERS
        
        tier = self.aspect_tier_combo.currentIndex() if hasattr(self, 'aspect_tier_combo') else 0
        aspects_defs = ASPECT_TIERS.get(tier, [])
        
        self.aspects_legend.setRowCount(len(aspects_defs))
        
        for i, asp in enumerate(aspects_defs):
            # Symbol
            self.aspects_legend.setItem(i, 0, QTableWidgetItem(asp.symbol))
            # Name
            self.aspects_legend.setItem(i, 1, QTableWidgetItem(asp.name))
            # Angle
            angle_str = f"{asp.angle}°"
            self.aspects_legend.setItem(i, 2, QTableWidgetItem(angle_str))
        
        self.aspects_legend.resizeColumnsToContents()


    def _on_aspects_filter_changed(self, state: int) -> None:
        """Re-render aspects and update chart when filter changes."""
        if self._last_result:
            self._render_aspects_table(self._last_result)
            self._sync_chart_aspects()

    def _on_orb_changed(self, value: int) -> None:
        """Update orb label and re-render when orb slider changes."""
        if hasattr(self, 'orb_label'):
            self.orb_label.setText(f"{value}%")
        if self._last_result:
            self._render_aspects_table(self._last_result)
            self._sync_chart_aspects()

    def _sync_chart_aspects(self) -> None:
        """Sync aspect settings with chart canvas."""
        if hasattr(self, 'chart_canvas'):
            tier = self.aspect_tier_combo.currentIndex() if hasattr(self, 'aspect_tier_combo') else 0
            include_minor = tier > 0  # Any tier above 0 shows some minor aspects
            orb_factor = self.orb_slider.value() / 100.0 if hasattr(self, 'orb_slider') else 1.0
            if hasattr(self.chart_canvas, 'set_aspect_options'):
                self.chart_canvas.set_aspect_options(include_minor, orb_factor)
            self.chart_canvas.update()

    def _set_status(self, message: str) -> None:
        if hasattr(self, "status_label"):
            self.status_label.setText(message)

    def _initialize_preferences(self) -> None:
        self._default_location = self._preferences.load_default_location()
        if self._default_location:
            self._apply_default_location_fields(self._default_location)
        self._refresh_default_buttons()

    def _refresh_default_buttons(self) -> None:
        has_default = self._default_location is not None
        if hasattr(self, "use_default_button"):
            self.use_default_button.setEnabled(has_default)

    def _use_default_location(self) -> None:
        if not self._default_location:
            QMessageBox.information(self, "No Default", "Save a default location first.")
            return
        self._apply_default_location_fields(self._default_location)
        self._set_status("Default location applied.")

    def _save_default_location(self) -> None:
        location = DefaultLocation(
            name=self.location_name_input.text().strip() or "Default Location",
            latitude=self.latitude_input.value(),
            longitude=self.longitude_input.value(),
            elevation=float(self.elevation_input.value()),
            timezone_offset=self.timezone_input.value(),
            timezone_id=self._current_timezone_id,
        )
        try:
            self._preferences.save_default_location(location)
        except OSError as exc:  # pragma: no cover - filesystem errors
            QMessageBox.critical(self, "Save Failed", str(exc))
            return
        self._default_location = location
        self._refresh_default_buttons()
        self._set_status("Default location saved.")

    def _apply_default_location_fields(
        self, location: DefaultLocation, target_dt: Optional[datetime] = None
    ) -> None:
        self.location_name_input.setText(location.name)
        self.latitude_input.setValue(location.latitude)
        self.longitude_input.setValue(location.longitude)
        self.elevation_input.setValue(int(location.elevation))
        self._current_timezone_id = location.timezone_id
        base_dt = target_dt or self._current_form_datetime()
        offset = self._offset_for_timezone_id(location.timezone_id, base_dt)
        self.timezone_input.setValue(offset if offset is not None else location.timezone_offset)

    def _current_form_datetime(self) -> datetime:
        dt = self.datetime_input.dateTime().toPyDateTime()
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def _offset_for_timezone_id(self, timezone_id: Optional[str], dt: datetime) -> Optional[float]:
        if not timezone_id:
            return None
        try:
            tz = pytz.timezone(timezone_id)
            base = dt
            if base.tzinfo is None:
                base = base.replace(tzinfo=timezone.utc)
            localized = base.astimezone(tz)
            offset = localized.utcoffset()
        except (pytz.UnknownTimeZoneError, Exception):  # pragma: no cover - defensive
            return None
        if offset is None:
            return None
        return round(offset.total_seconds() / 3600.0, 2)

    def _generate_current_transit(self) -> None:
        if not self._default_location:
            QMessageBox.information(
                self,
                "Default Required",
                "Save a default location before generating a transit chart.",
            )
            return

        now_dt = datetime.now(timezone.utc)
        now_qt = QDateTime.currentDateTimeUtc()
        self._apply_default_location_fields(self._default_location, target_dt=now_dt)
        self.datetime_input.setDateTime(now_qt)
        offset = self._offset_for_timezone_id(self._current_timezone_id, now_dt)
        if offset is not None:
            self.timezone_input.setValue(offset)
        self._generate_chart()

    def _tokenize(self, text: str) -> List[str]:
        return [token.strip() for token in text.split(",") if token.strip()]

    def _search_location(self) -> None:
        query, accepted = QInputDialog.getText(self, "Search City", "Enter a city or place name:", text=self.location_name_input.text())
        if not accepted or not query.strip():
            return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            results = self._location_lookup.search(query)
        except LocationLookupError as exc:
            QMessageBox.information(self, "No Results", str(exc))
            return
        except Exception as exc:  # pragma: no cover - network related
            QMessageBox.critical(self, "Lookup Failed", str(exc))
            return
        finally:
            QApplication.restoreOverrideCursor()

        selection = self._select_location_candidate(results)
        if selection is None:
            return
        self._apply_location_result(selection)
        self._set_status("Location populated from lookup.")

    def _select_location_candidate(self, results: List[LocationResult]) -> Optional[LocationResult]:
        if len(results) == 1:
            return results[0]

        options = [
            f"{item.label} ({item.latitude:.2f}, {item.longitude:.2f})"
            for item in results
        ]
        choice, accepted = QInputDialog.getItem(
            self,
            "Select Location",
            "Multiple matches found. Choose the correct one:",
            options,
            0,
            False,
        )
        if not accepted or not choice:
            return None
        return results[options.index(choice)]

    def _apply_location_result(self, result: LocationResult) -> None:
        self.location_name_input.setText(result.label)
        self.latitude_input.setValue(result.latitude)
        self.longitude_input.setValue(result.longitude)
        if result.elevation is not None:
            self.elevation_input.setValue(int(result.elevation))
        self._apply_timezone_offset(result)

    def _populate_from_request(self, request: ChartRequest) -> None:
        primary = request.primary_event
        self.name_input.setText(primary.name)
        self.location_name_input.setText(primary.location.name)
        self.latitude_input.setValue(primary.location.latitude)
        self.longitude_input.setValue(primary.location.longitude)
        self.elevation_input.setValue(int(primary.location.elevation))
        self.timezone_input.setValue(primary.resolved_timezone_offset())

        qt_dt = QDateTime(primary.timestamp)
        self.datetime_input.setDateTime(qt_dt)

        house_code = self._extract_house_system(request)
        if house_code:
            index = self.house_system_combo.findData(house_code)
            if index >= 0:
                self.house_system_combo.setCurrentIndex(index)

        self.include_svg_checkbox.setChecked(request.include_svg)
        self._current_timezone_id = None

    def _extract_house_system(self, request: ChartRequest) -> Optional[str]:
        if not request.settings:
            return None
        cfg = request.settings.get("astrocfg")
        if isinstance(cfg, dict):
            value = cfg.get("houses_system")
            if isinstance(value, str):
                return value
        return None

    def _save_chart(self) -> None:
        if self._storage_service is None:
            QMessageBox.warning(self, "Unavailable", "Chart storage is not available.")
            return
        if self._last_request is None or self._last_result is None:
            QMessageBox.information(self, "No Chart", "Generate a chart before saving.")
            return

        categories = self._tokenize(self.categories_input.text())
        tags = self._tokenize(self.tags_input.text())
        description = self.notes_input.toPlainText().strip() or None
        name = self.name_input.text().strip() or self._last_request.primary_event.name

        try:
            chart_id = self._storage_service.save_chart(
                name=name,
                request=self._last_request,
                result=self._last_result,
                categories=categories,
                tags=tags,
                description=description,
            )
        except Exception as exc:  # pragma: no cover - storage failures
            QMessageBox.critical(self, "Save Failed", str(exc))
        else:
            self._set_status(f"Chart saved (ID {chart_id}).")

    def _load_chart(self) -> None:
        if self._storage_service is None:
            QMessageBox.warning(self, "Unavailable", "Chart storage is not available.")
            return

        picker = ChartPickerDialog(self._storage_service, self)
        if picker.exec() != QDialog.DialogCode.Accepted or picker.selected is None:
            return

        chosen = picker.selected

        loaded = self._storage_service.load_chart(chosen.chart_id)
        if loaded is None:
            QMessageBox.warning(self, "Missing", "The selected chart could not be loaded.")
            return

        self._populate_from_request(loaded.request)
        self.categories_input.setText(", ".join(loaded.categories))
        self.tags_input.setText(", ".join(loaded.tags))
        self.notes_input.setPlainText(loaded.description or "")
        self._last_request = loaded.request
        self._last_result = None
        self.save_chart_button.setEnabled(False)
        self._set_status("Chart loaded. Generate to view results.")

    def _apply_timezone_offset(self, result: LocationResult) -> None:
        if not result.timezone_id:
            return
        try:
            tz = pytz.timezone(result.timezone_id)
        except pytz.UnknownTimeZoneError:
            return

        dt = self.datetime_input.dateTime().toPyDateTime()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        try:
            localized = dt.astimezone(tz)
            offset = localized.utcoffset()
        except Exception:  # pragma: no cover - unforeseen timezone issues
            return
        if offset is None:
            return
        hours = round(offset.total_seconds() / 3600.0, 2)
        self.timezone_input.setValue(hours)
        self._current_timezone_id = result.timezone_id

    def _open_in_browser(self) -> None:
        if not self._last_svg:
            QMessageBox.information(self, "SVG Unavailable", "Generate a chart with SVG output first.")
            return

        tmp_path: Optional[str] = None
        try:
            tmp_handle = tempfile.NamedTemporaryFile("w", suffix=".svg", prefix="natal_chart_", delete=False, encoding="utf-8")
            tmp_handle.write(self._last_svg)
            tmp_handle.close()
            tmp_path = tmp_handle.name
            self._temp_svg_files.append(tmp_path)
        except OSError as exc:
            QMessageBox.critical(self, "Temp File Error", f"Failed to prepare SVG for the browser: {exc}")
            return

        chrome_path = self._find_chrome_binary()
        if chrome_path:
            if self._launch_chrome(chrome_path, tmp_path):
                return
        if self._launch_default_browser(tmp_path):
            return
        QMessageBox.warning(self, "Browser Launch Failed", "Could not open the SVG in any browser. Save it manually instead.")

    def _launch_chrome(self, chrome_path: str, svg_path: str) -> bool:
        try:
            subprocess.Popen(
                [
                    chrome_path,
                    "--disable-gpu",
                    "--ozone-platform=wayland",
                    "--new-tab",
                    svg_path,
                ]
            )
        except OSError as exc:
            QMessageBox.critical(self, "Chrome Launch Failed", f"Could not launch Chrome: {exc}")
            self._cleanup_temp_files()
            return False
        self._set_status("Opened SVG in Chrome.")
        return True

    def _launch_default_browser(self, svg_path: str) -> bool:
        try:
            uri = Path(svg_path).as_uri()
        except (ValueError, OSError):
            uri = f"file://{svg_path}"
        try:
            opened = webbrowser.open(uri, new=2)
        except webbrowser.Error:
            opened = False
        if opened:
            self._set_status("Opened SVG in default browser.")
        return opened

    def _find_chrome_binary(self) -> Optional[str]:
        for candidate in ("google-chrome", "google-chrome-stable", "chrome", "chromium-browser", "chromium"):
            chrome_path = shutil.which(candidate)
            if chrome_path:
                return chrome_path
        return None

    def _cleanup_temp_files(self) -> None:
        while self._temp_svg_files:
            path = self._temp_svg_files.pop()
            try:
                if path and os.path.exists(path):
                    os.unlink(path)
            except OSError:
                continue

    def closeEvent(self, a0: Optional[QCloseEvent]) -> None:  # noqa: N802 - Qt signature
        """
        Closeevent logic.
        
        Args:
            a0: Description of a0.
        
        Returns:
            Result of closeEvent operation.
        """
        self._cleanup_temp_files()
        super().closeEvent(a0)

 