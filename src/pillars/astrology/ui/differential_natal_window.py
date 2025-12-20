"""
Differential Natal Chart Window - Maps planetary positions to Conrune pairs.

This window bridges the Astrology and Time Mechanics pillars by:
1. Calculating planetary positions for a birth chart
2. Mapping each planet's zodiacal degree to its corresponding Conrune pair
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox,
    QDateEdit, QTimeEdit, QLineEdit, QHeaderView, QApplication,
    QGroupBox, QFormLayout, QDoubleSpinBox, QInputDialog, QMenu
)

from ..services import (
    OpenAstroService, OpenAstroNotAvailableError, ChartComputationError,
    LocationLookupService, LocationLookupError, LocationResult,
    ChartStorageService
)
from ..models import AstrologyEvent, ChartRequest, GeoLocation
from ..ui.chart_picker_dialog import ChartPickerDialog
from pillars.time_mechanics.services.thelemic_calendar_service import ThelemicCalendarService


# Classic 7 planets (lowercase to match OpenAstro output)
CLASSIC_PLANETS = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]

# Planet symbols (keyed by lowercase name)
PLANET_SYMBOLS = {
    "sun": "☉",
    "moon": "☽",
    "mercury": "☿",
    "venus": "♀",
    "mars": "♂",
    "jupiter": "♃",
    "saturn": "♄",
}


class DifferentialNatalWindow(QWidget):
    """Window for calculating Differential Natal Charts."""
    
    def __init__(self, parent: Optional[QWidget] = None, window_manager=None, **kwargs):
        super().__init__(parent)
        self.setWindowTitle("Differential Natal Chart")
        self.resize(950, 650)
        
        self.window_manager = window_manager
        self._openastro_service: Optional[OpenAstroService] = None
        self._calendar_service = ThelemicCalendarService()
        self._location_service = LocationLookupService()
        self._storage_service = ChartStorageService()
        
        # Store computed values for context menu
        self._planet_differences: List[int] = []
        self._planet_ditrunes: List[int] = []
        self._planet_contrunes: List[int] = []
        self._total_difference = 0
        self._total_ditrune = 0
        self._total_contrune = 0
        
        self._build_ui()
        self._init_services()
    
    def _init_services(self) -> None:
        """Initialize the astrology service."""
        try:
            self._openastro_service = OpenAstroService()
        except OpenAstroNotAvailableError:
            self._openastro_service = None
    
    def _build_ui(self) -> None:
        """Build the window UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)
        
        # Title
        title = QLabel("Δ Differential Natal Chart")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #8b5cf6;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        subtitle = QLabel("Map planetary positions to Conrune pairs")
        subtitle.setStyleSheet("color: #64748b; font-size: 11pt;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)
        
        # Input Section
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(16, 16, 16, 16)
        input_layout.setSpacing(24)
        
        # Date input
        date_group = QGroupBox("Birth Date")
        date_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        date_layout = QFormLayout(date_group)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        date_layout.addRow(self.date_edit)
        input_layout.addWidget(date_group)
        
        # Time input
        time_group = QGroupBox("Birth Time")
        time_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        time_layout = QFormLayout(time_group)
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(12, 0))
        self.time_edit.setDisplayFormat("HH:mm")
        time_layout.addRow(self.time_edit)
        input_layout.addWidget(time_group)
        
        # Location input with Search
        loc_group = QGroupBox("Location")
        loc_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        loc_layout = QVBoxLayout(loc_group)
        
        # Location name with search button
        name_row = QHBoxLayout()
        self.location_name = QLineEdit("Jerusalem, IL")
        self.location_name.setPlaceholderText("City name")
        name_row.addWidget(self.location_name, 1)
        
        self.search_btn = QPushButton("🔍")
        self.search_btn.setToolTip("Search City")
        self.search_btn.setFixedWidth(32)
        self.search_btn.clicked.connect(self._search_location)
        name_row.addWidget(self.search_btn)
        loc_layout.addLayout(name_row)
        
        # Lat/Lon spinboxes
        coords_layout = QHBoxLayout()
        self.lat_input = QDoubleSpinBox()
        self.lat_input.setRange(-90.0, 90.0)
        self.lat_input.setDecimals(4)
        self.lat_input.setValue(31.7683)
        self.lat_input.setPrefix("Lat: ")
        coords_layout.addWidget(self.lat_input)
        
        self.lon_input = QDoubleSpinBox()
        self.lon_input.setRange(-180.0, 180.0)
        self.lon_input.setDecimals(4)
        self.lon_input.setValue(35.2137)
        self.lon_input.setPrefix("Lon: ")
        coords_layout.addWidget(self.lon_input)
        loc_layout.addLayout(coords_layout)
        
        input_layout.addWidget(loc_group)
        
        # Calculate button
        btn_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("📂 Load Chart")
        self.load_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
                border: 1px solid #cbd5e1;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.load_btn.clicked.connect(self._load_chart)
        btn_layout.addWidget(self.load_btn)

        self.calc_btn = QPushButton("⚡ Calculate")
        self.calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        self.calc_btn.clicked.connect(self._calculate)
        btn_layout.addWidget(self.calc_btn)
        
        input_layout.addLayout(btn_layout)
        
        main_layout.addWidget(input_frame)
        
        # Results Table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "Planet", "Zodiacal Position", "Degree", "Difference", "Ditrune", "Contrune", "Calendar Date"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8fafc;
                gridline-color: #e2e8f0;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #1e293b;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 6px;
            }
        """)
        
        # Enable context menu
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self._show_context_menu)
        
        main_layout.addWidget(self.results_table, 1)
        
        # Status
        self.status_label = QLabel("Enter birth information and click Calculate")
        self.status_label.setStyleSheet("color: #64748b; font-style: italic;")
        main_layout.addWidget(self.status_label)
    
    def _search_location(self) -> None:
        """Search for a location by name using the LocationLookupService."""
        query, accepted = QInputDialog.getText(
            self, "Search City", 
            "Enter a city or place name:",
            text=self.location_name.text()
        )
        if not accepted or not query.strip():
            return
        
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            results = self._location_service.search(query)
        except LocationLookupError as exc:
            QMessageBox.information(self, "No Results", str(exc))
            return
        except Exception as exc:
            QMessageBox.critical(self, "Lookup Failed", str(exc))
            return
        finally:
            QApplication.restoreOverrideCursor()
        
        if not results:
            QMessageBox.information(self, "No Results", f"No locations found for '{query}'")
            return
        
        # Select from multiple results
        selection = self._select_location(results)
        if selection:
            self._apply_location(selection)
            self.status_label.setText(f"Location set to: {selection.label}")
    
    def _select_location(self, results: List[LocationResult]) -> Optional[LocationResult]:
        """Let user choose from multiple location results."""
        if len(results) == 1:
            return results[0]
        
        options = [
            f"{item.label} ({item.latitude:.2f}, {item.longitude:.2f})"
            for item in results
        ]
        choice, accepted = QInputDialog.getItem(
            self, "Select Location",
            "Multiple matches found. Choose the correct one:",
            options, 0, False
        )
        if not accepted or not choice:
            return None
        return results[options.index(choice)]
    
    def _apply_location(self, result: LocationResult) -> None:
        """Apply a selected location to the input fields."""
        self.location_name.setText(result.label)
        self.lat_input.setValue(result.latitude)
        self.lon_input.setValue(result.longitude)
    
    def _load_chart(self) -> None:
        """Load a saved chart into the inputs."""
        if not self._storage_service:
            QMessageBox.warning(self, "Unavailable", "Chart storage is not available.")
            return

        picker = ChartPickerDialog(self._storage_service, self)
        # Use simple exec check like NatalChartWindow
        if picker.exec() != 1 or picker.selected is None: # 1 is Accepted
            return

        chosen = picker.selected
        loaded = self._storage_service.load_chart(chosen.chart_id)
        
        if loaded is None:
            QMessageBox.warning(self, "Missing", "The selected chart could not be loaded.")
            return

        # Populate inputs from request
        req = loaded.request
        event = req.primary_event
        
        if event.timestamp:
            self.date_edit.setDate(event.timestamp.date())
            self.time_edit.setTime(event.timestamp.time())
        
        if event.location:
            self.location_name.setText(event.location.name)
            self.lat_input.setValue(event.location.latitude)
            self.lon_input.setValue(event.location.longitude)
            
        self.status_label.setText(f"Loaded chart: {event.name}")
        
        # Auto-calculate
        self._calculate()
    
    def _calculate(self) -> None:
        """Calculate planetary positions and map to Conrune pairs."""
        if self._openastro_service is None:
            QMessageBox.warning(self, "Unavailable", "OpenAstro2 is not available.")
            return
        
        # Build the request
        try:
            date = self.date_edit.date()
            time = self.time_edit.time()
            
            dt = datetime(
                date.year(), date.month(), date.day(),
                time.hour(), time.minute()
            )
            
            lat = self.lat_input.value()
            lon = self.lon_input.value()
            
            location = GeoLocation(
                name=self.location_name.text() or "Unknown",
                latitude=lat, 
                longitude=lon
            )
            event = AstrologyEvent(
                name="Differential Chart",
                timestamp=dt,
                location=location
            )
            request = ChartRequest(primary_event=event, include_svg=False)
            
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return
        
        # Calculate chart
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
        try:
            result = self._openastro_service.generate_chart(request)
        except ChartComputationError as e:
            QMessageBox.critical(self, "Calculation Error", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return
        finally:
            QApplication.restoreOverrideCursor()
        
        # Process results
        self._populate_table(result)
        self.status_label.setText(f"Calculated for {dt.strftime('%Y-%m-%d %H:%M')} at {self.location_name.text()}")
    
    def _populate_table(self, result) -> None:
        """Populate the results table with planetary data."""
        self.results_table.setRowCount(0)
        
        # Reset totals
        self._planet_differences = []
        self._planet_ditrunes = []
        self._planet_contrunes = []
        
        for position in result.planet_positions:
            # Only show Classic 7
            if position.name not in CLASSIC_PLANETS:
                continue
            
            degree = position.degree
            
            # Get zodiacal string (DD° Sign MM')
            zodiacal = self._degree_to_zodiacal(degree)
            
            # Map degree to Conrune pair
            diff = self._calendar_service.zodiac_degree_to_difference(degree)
            if diff:
                pair = self._calendar_service.get_pair_by_difference(diff)
            else:
                pair = None
            
            # Add row
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            # Planet with symbol
            symbol = PLANET_SYMBOLS.get(position.name, "")
            planet_item = QTableWidgetItem(f"{symbol} {position.name.title()}")
            planet_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            self.results_table.setItem(row, 0, planet_item)
            
            # Zodiacal position
            self.results_table.setItem(row, 1, QTableWidgetItem(zodiacal))
            
            # Raw degree
            self.results_table.setItem(row, 2, QTableWidgetItem(f"{degree:.2f}°"))
            
            if pair:
                # Track values for totals
                self._planet_differences.append(pair.difference)
                self._planet_ditrunes.append(pair.ditrune)
                self._planet_contrunes.append(pair.contrune)
                
                # Difference
                diff_item = QTableWidgetItem(str(pair.difference))
                diff_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.results_table.setItem(row, 3, diff_item)
                
                # Ditrune
                ditrune_item = QTableWidgetItem(str(pair.ditrune))
                ditrune_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.results_table.setItem(row, 4, ditrune_item)
                
                # Contrune
                contrune_item = QTableWidgetItem(str(pair.contrune))
                contrune_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.results_table.setItem(row, 5, contrune_item)
                
                # Calendar date
                self.results_table.setItem(row, 6, QTableWidgetItem(pair.gregorian_date))
            else:
                for col in range(3, 7):
                    self.results_table.setItem(row, col, QTableWidgetItem("—"))
        
        # Add totals row
        self._total_difference = sum(self._planet_differences)
        self._total_ditrune = sum(self._planet_ditrunes)
        self._total_contrune = sum(self._planet_contrunes)
        
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Bold "TOTAL" label
        total_item = QTableWidgetItem("Σ TOTAL")
        total_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        total_item.setForeground(Qt.GlobalColor.darkMagenta)
        self.results_table.setItem(row, 0, total_item)
        
        # Empty cells for non-summed columns
        for col in range(1, 3):
            self.results_table.setItem(row, col, QTableWidgetItem(""))
        
        # Totals
        for col, total in [(3, self._total_difference), (4, self._total_ditrune), (5, self._total_contrune)]:
            item = QTableWidgetItem(str(total))
            item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setForeground(Qt.GlobalColor.darkMagenta)
            self.results_table.setItem(row, col, item)
        
        self.results_table.setItem(row, 6, QTableWidgetItem(""))
    
    def _degree_to_zodiacal(self, degree: float) -> str:
        """Convert absolute degree to zodiacal string."""
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        sign_idx = int(degree // 30)
        sign_degree = degree % 30
        return f"{int(sign_degree)}° {signs[sign_idx]}"
    
    def _show_context_menu(self, position) -> None:
        """Show context menu on table right-click."""
        if not self._planet_differences:
            return
        
        menu = QMenu(self)
        
        # Send to Quadset Analysis
        quadset_action = QAction("Send Total to Quadset Analysis", menu)
        quadset_action.triggered.connect(self._send_to_quadset)
        menu.addAction(quadset_action)
        
        # Look up in Database
        lookup_action = QAction("Look up Total in Database", menu)
        lookup_action.triggered.connect(self._lookup_in_database)
        menu.addAction(lookup_action)
        
        menu.addSeparator()
        
        # Send to Heptagon Transitions (special - 7 planets!)
        heptagon_action = QAction("🔷 Send to Heptagon Transitions", menu)
        heptagon_action.triggered.connect(self._send_to_heptagon)
        menu.addAction(heptagon_action)
        
        menu.exec(self.results_table.viewport().mapToGlobal(position))
    
    def _send_to_quadset(self) -> None:
        """Send total Difference to Quadset Analysis."""
        if not self.window_manager:
            QMessageBox.warning(self, "Unavailable", "Window manager not available.")
            return
        
        from pillars.tq.ui.quadset_analysis_window import QuadsetAnalysisWindow
        
        window = self.window_manager.open_window(
            "tq_quadset_analysis",
            QuadsetAnalysisWindow,
            allow_multiple=False,
            window_manager=self.window_manager,
        )
        if window and hasattr(window, "input_field"):
            window.input_field.setText(str(self._total_difference))
            window.raise_()
            window.activateWindow()
    
    def _lookup_in_database(self) -> None:
        """Look up total Difference in the Saved Calculations database."""
        if not self.window_manager:
            QMessageBox.warning(self, "Unavailable", "Window manager not available.")
            return
        
        from pillars.gematria.ui.saved_calculations_window import SavedCalculationsWindow
        
        window = self.window_manager.open_window(
            "saved_calculations",
            SavedCalculationsWindow,
            allow_multiple=False,
            window_manager=self.window_manager,
        )
        if window:
            value_field = getattr(window, "value_input", None)
            if value_field is not None:
                value_field.setText(str(self._total_difference))
            
            search_method = getattr(window, "_search", None)
            if callable(search_method):
                search_method()
                
            window.raise_()
            window.activateWindow()
    
    def _send_to_heptagon(self) -> None:
        """Send 7 planetary Differences to Geometric Transitions as a Heptagon."""
        if not self.window_manager:
            QMessageBox.warning(self, "Unavailable", "Window manager not available.")
            return
        
        if len(self._planet_differences) != 7:
            QMessageBox.warning(self, "Incomplete Data", "Need all 7 planetary values.")
            return
        
        from pillars.tq.ui.geometric_transitions_window import GeometricTransitionsWindow
        
        window = self.window_manager.open_window(
            "tq_geometric_transitions",
            GeometricTransitionsWindow,
            allow_multiple=False,
            window_manager=self.window_manager,
        )
        
        if window:
            # Set to Heptagon (7 sides)
            for i in range(window.shape_combo.count()):
                if window.shape_combo.itemData(i) == 7:
                    window.shape_combo.setCurrentIndex(i)
                    break
            
            # Populate the 7 value inputs
            window._refresh_value_inputs()
            for i, val in enumerate(self._planet_differences):
                if i < len(window.value_inputs):
                    window.value_inputs[i].setText(str(val))
            
            # Raise the window so user can click Generate
            window.raise_()
            window.activateWindow()

