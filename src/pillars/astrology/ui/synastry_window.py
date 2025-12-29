"""
Sovereign Window for Synastry Analysis.
Allows entering two chart profiles and generating Bi-Wheel, Composite, or Davison charts.
"""
from datetime import datetime
from typing import Optional, List, Any

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QDateTimeEdit, QComboBox, 
    QPushButton, QGroupBox, QSplitter, QMessageBox,
    QStackedWidget
)
from shared.ui.scrollable_tab_bar import ScrollableTabBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from shared.ui.theme import COLORS
from shared.ui.worker import BackgroundWorker
from ..models.chart_models import ChartRequest, AstrologyEvent, GeoLocation, ChartResult
from ..services.openastro_service import OpenAstroService, ChartComputationError
from ..services.chart_storage_service import ChartStorageService
from ..services.synastry_service import SynastryService, CompositeResult, DavisonResult
from .chart_canvas import ChartCanvas
from .chart_picker_dialog import ChartPickerDialog
from .synastry_aspects_widget import SynastryAspectsWidget
from .synastry_midpoints_widget import SynastryMidpointsWidget
from .synastry_davison_widget import SynastryDavisonWidget
from .advanced_analysis_panel import AdvancedAnalysisPanel
from .conversions import to_zodiacal_string

class SynastryWindow(QMainWindow):
    """
    Focused window for Synastry and Relationship Astrology.
    Input: Chart A (Inner), Chart B (Outer).
    Output: Bi-Wheel or Composite Chart.
    """
    
    def __init__(self, service: OpenAstroService, parent=None):
        super().__init__(parent)
        self._service = service
        self._synastry_service = SynastryService(service)  # Purified service for calculations
        self._storage = ChartStorageService()  # For loading saved charts
        self.setWindowTitle("Synastry & Relationships")
        self.resize(1100, 800)
        # Remove global white text that breaks inputs
        # self.setStyleSheet(f"background-color: {COLORS['void']}; color: white;")
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QHBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 1. Sidebar (Inputs)
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        # Removed FixedWidth in favor of Golden Splitter
        # self.sidebar.setFixedWidth(320)
        # Explicitly set text color for sidebar inputs to be visible against light surface
        self.sidebar.setStyleSheet(f"""
            QWidget#sidebar {{
                background-color: {COLORS['surface']}; 
                border-right: 1px solid {COLORS['border']};
                color: {COLORS['text_primary']};
            }}
            QLineEdit, QComboBox, QDateTimeEdit {{
                color: {COLORS['text_primary']};
                background-color: {COLORS['light']};
                font-size: 12pt;
                padding: 4px;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
            QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus {{
                border: 2px solid #3b82f6;
            }}
        """)
        self.side_layout = QVBoxLayout(self.sidebar)
        
        # Chart A
        self.group_a = QGroupBox("Person A (Inner)")
        self.form_a = QVBoxLayout(self.group_a)
        self.name_a = QLineEdit("Person A"); self.name_a.setPlaceholderText("Name")
        self.dt_a = QDateTimeEdit(datetime.now()); self.dt_a.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.loc_a = QLineEdit("London"); self.loc_a.setPlaceholderText("Location")
        self.lat_a = QLineEdit("51.5"); self.lat_a.setPlaceholderText("Lat")
        self.lon_a = QLineEdit("-0.12"); self.lon_a.setPlaceholderText("Lon")
        
        for w in [self.name_a, self.dt_a, self.loc_a, self.lat_a, self.lon_a]: self.form_a.addWidget(w)
        
        # Load Saved Button for A
        # Load Saved Button for A
        self.load_a_btn = QPushButton("Load Saved Chart...")
        self.load_a_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.load_a_btn.setProperty("archetype", "seeker")
        self.load_a_btn.clicked.connect(lambda: self._load_saved_chart('A'))
        self.form_a.addWidget(self.load_a_btn)
        
        self.side_layout.addWidget(self.group_a)
        
        # Chart B
        self.group_b = QGroupBox("Person B (Outer)")
        self.form_b = QVBoxLayout(self.group_b)
        self.name_b = QLineEdit("Person B"); self.name_b.setPlaceholderText("Name")
        self.dt_b = QDateTimeEdit(datetime.now()); self.dt_b.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.loc_b = QLineEdit("New York"); self.loc_b.setPlaceholderText("Location")
        self.lat_b = QLineEdit("40.7"); self.lat_b.setPlaceholderText("Lat")
        self.lon_b = QLineEdit("-74.0"); self.lon_b.setPlaceholderText("Lon")
        
        for w in [self.name_b, self.dt_b, self.loc_b, self.lat_b, self.lon_b]: self.form_b.addWidget(w)
        
        # Load Saved Button for B
        # Load Saved Button for B
        self.load_b_btn = QPushButton("Load Saved Chart...")
        self.load_b_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.load_b_btn.setProperty("archetype", "seeker")
        self.load_b_btn.clicked.connect(lambda: self._load_saved_chart('B'))
        self.form_b.addWidget(self.load_b_btn)
        
        self.side_layout.addWidget(self.group_b)
        
        # Method Selector
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Synastry (Bi-Wheel)", "Composite (Midpoint)", "Davison (Time/Space)"])
        self.side_layout.addWidget(QLabel("Relationship Model:"))
        self.side_layout.addWidget(self.method_combo)
        
        # Action
        # Action
        self.calc_btn = QPushButton("Reveal Compatibility")
        self.calc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.calc_btn.setProperty("archetype", "seeker") # Seeking Connection
        self.calc_btn.clicked.connect(self._on_calculate)
        self.side_layout.addWidget(self.calc_btn)
        self.side_layout.addStretch()
        
        # 2. Main Content Area (Tabbed)
        self.content_area = QWidget()
        self.content_area.setObjectName("content_area")
        # Set dark theme for the main analysis area
        self.content_area.setStyleSheet(f"""
            QWidget#content_area {{
                background-color: {COLORS['void']};
                color: white;
            }}
        """)
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab Widget Replacement
        self.tab_bar = ScrollableTabBar()
        self.content_stack = QStackedWidget()
        
        # Connect navigation
        self.tab_bar.currentChanged.connect(self.content_stack.setCurrentIndex)
        
        # Tab 1: Chart View
        self.canvas = ChartCanvas()
        self.tab_bar.add_tab("Chart")
        self.content_stack.addWidget(self.canvas)
        
        # Tab 2: Aspects
        self.aspects_widget = SynastryAspectsWidget()
        self.tab_bar.add_tab("Aspects")
        self.content_stack.addWidget(self.aspects_widget)
        
        # Tab 3: Midpoints (cross-chart planet-to-planet midpoints)
        self.midpoints_widget = SynastryMidpointsWidget()
        self.tab_bar.add_tab("Cross-Chart Midpoints")
        self.content_stack.addWidget(self.midpoints_widget)
        
        # Tab 4: Davison Info
        self.davison_widget = SynastryDavisonWidget()
        self.tab_bar.add_tab("Davison Info")
        self.content_stack.addWidget(self.davison_widget)
        
        # Tab 5: Composite Analysis (full chart analysis of composite positions)
        self.composite_analysis = AdvancedAnalysisPanel()
        self.tab_bar.add_tab("Composite Analysis")
        self.content_stack.addWidget(self.composite_analysis)
        
        # Tab 6: Davison Analysis (full chart analysis of Davison chart)
        self.davison_analysis = AdvancedAnalysisPanel()
        self.tab_bar.add_tab("Davison Analysis")
        self.content_stack.addWidget(self.davison_analysis)
        
        self.content_layout.addWidget(self.tab_bar)
        self.content_layout.addWidget(self.content_stack)
        
        # Golden Ratio Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.content_area)
        # The Divine Proportion: ~38.2% Input, ~61.8% Content
        self.splitter.setStretchFactor(0, 382) 
        self.splitter.setStretchFactor(1, 618)
        self.splitter.setHandleWidth(2)
        
        self.layout.addWidget(self.splitter)
        
        # State
        self._last_result_a: Optional[ChartResult] = None
        self._last_result_b: Optional[ChartResult] = None

    def _on_calculate(self):
        """Orchestrate calculation of A, B, and interaction."""
        try:
            event_a = self._build_event(self.name_a, self.dt_a, self.loc_a, self.lat_a, self.lon_a)
            event_b = self._build_event(self.name_b, self.dt_b, self.loc_b, self.lat_b, self.lon_b)
        except ValueError as e:
            QMessageBox.warning(self, "Input Dissonance", str(e))
            return

        mode = self.method_combo.currentText()
        
        # For Synastry, we need TWO charts computed independently first
        # Composite/Davison require creating a THIRD virtual event.
        
        self.calc_btn.setEnabled(False)
        self.calc_btn.setText("Communing with the Stars...")
        
        # Using simple synchronous logic first to verify, then worker if slow.
        # But Phase 5 says we should be using workers.
        # Since we might need multiple calls (Chart A, then Chart B), chaining workers is annoying.
        # Or we loop inside one worker.
        
        from PyQt6.QtCore import QThreadPool
        worker = BackgroundWorker(self._perform_synastry, event_a, event_b, mode)
        worker.signals.result.connect(self._on_result)
        worker.signals.error.connect(self._on_error)
        worker.signals.finished.connect(self._on_finished)
        QThreadPool.globalInstance().start(worker)

    def _build_event(self, name_w, dt_w, loc_w, lat_w, lon_w) -> AstrologyEvent:
        try:
            lat = float(lat_w.text())
            lon = float(lon_w.text())
        except ValueError:
            raise ValueError(f"Invalid Coordinates for {name_w.text()}")
            
        return AstrologyEvent(
            name=name_w.text(),
            timestamp=dt_w.dateTime().toPyDateTime(),
            location=GeoLocation(loc_w.text(), lat, lon)
        )

    def _perform_synastry(self, event_a, event_b, mode):
        """Generate charts for all modes. Delegates to SynastryService."""
        # Generate both base charts
        res_a = self._synastry_service.generate_chart(event_a)
        res_b = self._synastry_service.generate_chart(event_b)
        
        # Always calculate Composite and Davison for analysis panels
        composite_result = self._synastry_service.calculate_composite(res_a, res_b)
        davison_result = self._synastry_service.calculate_davison(event_a, event_b)
        
        return (mode, res_a, res_b, composite_result, davison_result)

    def _on_result(self, data):
        mode, res_a, res_b, composite_result, davison_result = data
        self._last_result_a = res_a
        self._last_result_b = res_b
        
        # Always populate cross-chart tabs with base charts
        if res_b:
            self.aspects_widget.set_data(res_a.planet_positions, res_b.planet_positions)
            self.midpoints_widget.set_data(
                res_a.planet_positions, res_b.planet_positions,
                res_a.house_positions, res_b.house_positions
            )
        
        # Always populate Composite Analysis panel
        self.composite_analysis.set_data(
            composite_result.planets, 
            composite_result.houses,
            julian_day=composite_result.julian_day
        )
        
        # Always populate Davison Analysis panel and Davison Info
        davison_info = {
            "midpoint_time": davison_result.info.midpoint_time,
            "midpoint_lat": davison_result.info.midpoint_latitude,
            "midpoint_lon": davison_result.info.midpoint_longitude,
        }
        self.davison_widget.set_data(davison_info)
        self.davison_analysis.set_data(
            davison_result.chart.planet_positions,
            davison_result.chart.house_positions,
            julian_day=davison_result.chart.julian_day
        )
        
        # Chart tab display depends on selected mode
        if "Synastry" in mode:
            # Bi-wheel: Person A inner, Person B outer
            self.canvas.set_synastry_data(
                res_a.planet_positions,
                res_b.planet_positions,
                res_a.house_positions
            )
            
        elif "Composite" in mode:
            # Display the composite (midpoint) chart as a single wheel
            self.canvas.set_data(composite_result.planets, composite_result.houses)
            
        elif "Davison" in mode:
            # Display the Davison chart (cast for midpoint time/space)
            self.canvas.set_data(
                davison_result.chart.planet_positions,
                davison_result.chart.house_positions
            )
            
        else:
            self.canvas.set_data(res_a.planet_positions, res_a.house_positions)

    def _on_error(self, err):
        QMessageBox.critical(self, "The Archives are Silent", str(err[1]))

    def _on_finished(self):
        self.calc_btn.setText("Reveal Compatibility")
        self.calc_btn.setEnabled(True)

    def _load_saved_chart(self, target: str) -> None:
        """Open the chart picker dialog and populate form fields for Person A or B."""
        dialog = ChartPickerDialog(self._storage, parent=self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        
        selected = dialog.selected
        if not selected:
            return
        
        # Load the full chart data
        loaded = self._storage.load_chart(selected.chart_id)
        if not loaded:
            QMessageBox.warning(self, "Load Failed", f"Could not load chart ID {selected.chart_id}")
            return
        
        # Extract event data from the loaded request
        event = loaded.request.primary_event
        
        # Populate the appropriate form
        if target == 'A':
            self.name_a.setText(event.name)
            self.dt_a.setDateTime(event.timestamp)
            self.loc_a.setText(event.location.name)
            self.lat_a.setText(str(event.location.latitude))
            self.lon_a.setText(str(event.location.longitude))
        else:  # B
            self.name_b.setText(event.name)
            self.dt_b.setDateTime(event.timestamp)
            self.loc_b.setText(event.location.name)
            self.lat_b.setText(str(event.location.latitude))
            self.lon_b.setText(str(event.location.longitude))

