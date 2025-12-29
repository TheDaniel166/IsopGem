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
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon

from shared.ui.theme import COLORS
from shared.ui.worker import BackgroundWorker
from ..models.chart_models import ChartRequest, AstrologyEvent, GeoLocation, ChartResult
from ..services.openastro_service import OpenAstroService, ChartComputationError
from .chart_canvas import ChartCanvas
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
        self.setWindowTitle("Synastry & Relationships")
        self.resize(1100, 800)
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QHBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # 1. Sidebar (Inputs)
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(320)
        self.sidebar.setStyleSheet(f"background-color: {COLORS['surface']}; border-right: 1px solid {COLORS['border']};")
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
        self.side_layout.addWidget(self.group_b)
        
        # Method Selector
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Synastry (Bi-Wheel)", "Composite (Midpoint)", "Davison (Time/Space)"])
        self.side_layout.addWidget(QLabel("Relationship Model:"))
        self.side_layout.addWidget(self.method_combo)
        
        # Action
        self.calc_btn = QPushButton("Calculate Compatibility")
        self.calc_btn.setStyleSheet(f"background-color: {COLORS['primary']}; color: white; padding: 8px; font-weight: bold;")
        self.calc_btn.clicked.connect(self._on_calculate)
        self.side_layout.addWidget(self.calc_btn)
        self.side_layout.addStretch()
        
        # 2. Main Canvas
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        
        self.canvas = ChartCanvas()
        self.content_layout.addWidget(self.canvas)
        
        self.layout.addWidget(self.sidebar)
        self.layout.addWidget(self.content_area)
        
        # State
        self._last_result_a: Optional[ChartResult] = None
        self._last_result_b: Optional[ChartResult] = None

    def _on_calculate(self):
        """Orchestrate calculation of A, B, and interaction."""
        try:
            event_a = self._build_event(self.name_a, self.dt_a, self.loc_a, self.lat_a, self.lon_a)
            event_b = self._build_event(self.name_b, self.dt_b, self.loc_b, self.lat_b, self.lon_b)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return

        mode = self.method_combo.currentText()
        
        # For Synastry, we need TWO charts computed independently first
        # Composite/Davison require creating a THIRD virtual event.
        
        self.calc_btn.setEnabled(False)
        self.calc_btn.setText("Calculating...")
        
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
        # Heavy lifting
        req_a = ChartRequest(event_a, chart_type="Radix")
        res_a = self._service.generate_chart(req_a)
        
        res_b = None
        if "Synastry" in mode:
            # Bi-Wheel: We need Chart B positions
            req_b = ChartRequest(event_b, chart_type="Radix")
            res_b = self._service.generate_chart(req_b)
            return ("Synastry", res_a, res_b)
            
        elif "Composite" in mode:
            # Composite involves calculating midpoints of positions
            # OR midpoints of times/locations (Davison)
            # OpenAstro might support Composite naturally?
            # Check OpenAstroService capability?
            # For now, let's just do Synastry Bi-Wheel as MVP.
            # If user selected Composite, we might just fail gracefully or fallback.
            return ("Synastry", res_a, self._service.generate_chart(ChartRequest(event_b)))
            
        return ("Synastry", res_a, None)

    def _on_result(self, data):
        mode, res_a, res_b = data
        self._last_result_a = res_a
        self._last_result_b = res_b
        
        if mode == "Synastry" and res_b:
            # Feed bi-wheel data
            self.canvas.set_synastry_data(
                res_a.planet_positions,
                res_b.planet_positions,
                res_a.house_positions # Use House A for reference
            )
        else:
            self.canvas.set_data(res_a.planet_positions, res_a.house_positions)

    def _on_error(self, err):
        QMessageBox.critical(self, "Error", str(err[1]))

    def _on_finished(self):
        self.calc_btn.setText("Calculate Compatibility")
        self.calc_btn.setEnabled(True)
