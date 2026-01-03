"""Interactive UI for generating natal charts through OpenAstro2."""
from __future__ import annotations

import logging
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
    QFrame,
    QGraphicsDropShadowEffect,
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

logger = logging.getLogger(__name__)

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
from .advanced_analysis_panel import AdvancedAnalysisPanel
from shared.ui.theme import COLORS

from ..ui.chart_picker_dialog import ChartPickerDialog
from .astro_settings_dialog import AstroSettingsDialog
from .location_search_dialog import LocationSearchDialog
from shared.ui.substrate_widget import SubstrateWidget
    
    
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
        self._chart_settings: Dict[str, Any] = {}  # User-selected calculation settings

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
        # Level 0: The Substrate (Thematic background)
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        bg_path = os.path.join(base_path, "assets", "textures", "natal_substrate.png")
        
        central = SubstrateWidget(bg_path)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # Header Title (The Sigil)
        title = QLabel("Natal Chart Generator")
        title.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 28pt;
            font-weight: 900;
            letter-spacing: -1px;
            background-color: transparent;
        """)
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

        # Tab 4: Advanced (uses reusable AdvancedAnalysisPanel)
        self.advanced_panel = AdvancedAnalysisPanel()
        self.tabs.addTab(self.advanced_panel, "Advanced")

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
        self.search_location_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.search_location_button.setProperty("archetype", "seeker")
        self.search_location_button.clicked.connect(self._search_location)
        location_row.addWidget(self.search_location_button)
        location_row_widget = QWidget()
        location_row_widget.setLayout(location_row)
        form.addRow("Location Label", location_row_widget)

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

        # The Seeker (Gold) - Uncover/Reveal
        self.load_chart_button = QPushButton("Load Chart...")
        self.load_chart_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.load_chart_button.setProperty("archetype", "seeker")
        self.load_chart_button.clicked.connect(self._load_chart)
        row.addWidget(self.load_chart_button)

        # Settings Button (⚙️)
        self.settings_button = QPushButton("⚙️ Settings")
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_button.setProperty("archetype", "navigator")
        self.settings_button.clicked.connect(self._open_settings_dialog)
        row.addWidget(self.settings_button)

        # The Scribe (Emerald) - Preserve/Etch
        self.save_chart_button = QPushButton("Save Chart")
        self.save_chart_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_chart_button.setProperty("archetype", "scribe")
        self.save_chart_button.clicked.connect(self._save_chart)
        self.save_chart_button.setEnabled(False)
        row.addWidget(self.save_chart_button)

        # The Navigator (Slate) - Traverse
        self.transit_button = QPushButton("Current Transit")
        self.transit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.transit_button.setProperty("archetype", "navigator")
        self.transit_button.clicked.connect(self._generate_current_transit)
        row.addWidget(self.transit_button)

        # The Magus (Violet) - Transmute/Execute - PRIMARY ACTION
        self.generate_button = QPushButton("Generate Chart")
        self.generate_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.generate_button.setProperty("archetype", "magus")
        self.generate_button.clicked.connect(self._generate_chart)
        row.addWidget(self.generate_button)

        # The Navigator (Slate) - Clear
        self.clear_button = QPushButton("Clear Results")
        self.clear_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_button.setProperty("archetype", "navigator")
        self.clear_button.clicked.connect(self._clear_results)
        row.addWidget(self.clear_button)

        # The Magus (Violet) - Interpret
        self.interpret_button = QPushButton("Interpret")
        self.interpret_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.interpret_button.setProperty("archetype", "magus")
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
            self._temp_request = request # Stash for async callbacks
        except ValueError as exc:
            QMessageBox.warning(self, "Invalid Input", str(exc))
            return

        # Use Background Worker
        self._set_status("Calculating...", busy=True)
        self.generate_button.setEnabled(False)
        self.tabs.setEnabled(False) # Prevent interaction
        
        # We need to wrap the service call
        # Since BackgroundWorker takes a function, we pass self._service.generate_chart
        # and arguments.
        
        from shared.ui.worker import BackgroundWorker
        from PyQt6.QtCore import QThreadPool
        
        worker = BackgroundWorker(self._service.generate_chart, request)
        worker.signals.result.connect(self._on_chart_generated)
        worker.signals.error.connect(self._on_service_error)
        worker.signals.finished.connect(self._on_service_finished)
        
        QThreadPool.globalInstance().start(worker)

    def _on_chart_generated(self, result: ChartResult) -> None:
        """Handle async chart result."""
        self._last_result = result
        self._last_request = self._temp_request # We need to store who requested it
        
        self.save_chart_button.setEnabled(True)
        self.interpret_button.setEnabled(True)
        self._render_result(result)
        self.tabs.setCurrentWidget(self.results_tab)
        self._set_status("Chart generated successfully.")
        
        # Auto-interpret?
        # self._generate_interpretation(switch_tab=False) 
        # Better to let user click or run async again. 
        # If we run async immediately, we need another worker.

    def _on_service_error(self, err_tuple):
        """Handle async error."""
        exctype, value, traceback_str = err_tuple
        QMessageBox.critical(self, "Calculation Error", str(value))
        self._set_status(f"Error: {value}")

    def _on_service_finished(self):
        """Cleanup after worker."""
        self.generate_button.setEnabled(True)
        self.tabs.setEnabled(True)
        self.unsetCursor()
        # Ensure status isn't stuck on "Calculating..."
        if self.status_label.text() == "Calculating...":
             self._set_status("Ready")

    def _set_status(self, text: str, busy: bool = False) -> None:
        self.status_label.setText(text)
        if busy:
             self.setCursor(Qt.CursorShape.BusyCursor)
        else:
             self.unsetCursor()

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
                 logger.exception("Auto-interpretation failed")
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
        
        # Merge house system from combo with advanced settings from dialog
        selected_house = self.house_system_combo.currentData()
        settings = {"astrocfg": {"houses_system": selected_house}} if selected_house else {}
        
        # Merge user-selected calculation settings (from Settings dialog)
        if self._chart_settings:
            astrocfg = settings.get("astrocfg", {})
            dialog_cfg = self._chart_settings.get("astrocfg", {})
            astrocfg.update(dialog_cfg)
            settings["astrocfg"] = astrocfg
        
        request = ChartRequest(
            primary_event=event,
            include_svg=self.include_svg_checkbox.isChecked(),
            settings=settings
        )
        return request

    def _open_settings_dialog(self) -> None:
        """Open the calculation settings dialog."""
        dialog = AstroSettingsDialog(current_settings=self._chart_settings, parent=self)
        dialog.settings_changed.connect(self._apply_chart_settings)
        dialog.exec()

    def _apply_chart_settings(self, settings: Dict[str, Any]) -> None:
        """Apply settings from the dialog."""
        self._chart_settings = settings
        self._set_status("Calculation settings updated. Generate chart to apply.")

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
        self._handle_svg(result)
        
        # Populate the advanced analysis panel
        if hasattr(self, 'advanced_panel'):
            fixed_stars = getattr(result, 'fixed_stars', None)
            self.advanced_panel.set_data(
                result.planet_positions,
                result.house_positions,
                fixed_stars,
                julian_day=result.julian_day
            )

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


    # ------------------------------------------------------------------
    # Preferences and defaults
    # ------------------------------------------------------------------
    def _initialize_preferences(self) -> None:
        self._default_location = self._preferences.load_default_location()
        if self._default_location:
            self._apply_default_location_fields(self._default_location)

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
        """Open the location search dialog."""
        dialog = LocationSearchDialog(preferences=self._preferences, parent=self)
        dialog.location_selected.connect(self._on_location_selected)
        dialog.exec()

    def _on_location_selected(self, location) -> None:
        """Handle location selection from the search dialog."""
        # Check if it's a DefaultLocation or LocationResult
        from ..utils import DefaultLocation
        if isinstance(location, DefaultLocation):
            self._apply_default_location_fields(location)
            self._set_status("Default location applied.")
        else:
            self._apply_location_result(location)
            self._set_status("Location populated from search.")

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

 