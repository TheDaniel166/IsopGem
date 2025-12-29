"""
Sovereign Window for Progressions and Directions.
"""
from datetime import datetime
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QDateTimeEdit, QComboBox, 
    QPushButton, QGroupBox, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QThreadPool

from shared.ui.theme import COLORS
from shared.ui.worker import BackgroundWorker
from ..models.chart_models import ChartRequest, AstrologyEvent, GeoLocation, ChartResult
from ..services.openastro_service import OpenAstroService
from ..services.progressions_service import ProgressionsService
from .chart_canvas import ChartCanvas

class ProgressionsWindow(QMainWindow):
    """
    Focused window for Secondary Progressions & Solar Arc.
    Displays Bi-Wheel (Natal vs Progressed).
    """
    
    def __init__(self, service: OpenAstroService, parent=None):
        super().__init__(parent)
        self._service = service
        self._prog_service = ProgressionsService(service)
        
        self.setWindowTitle("Progressions & Directions")
        self.resize(1100, 800)
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QHBoxLayout(self.main_widget)
        self.layout.setSpacing(0); self.layout.setContentsMargins(0,0,0,0)
        
        # 1. Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(320)
        self.sidebar.setStyleSheet(f"background-color: {COLORS['surface']}; border-right: 1px solid {COLORS['border']};")
        self.side_layout = QVBoxLayout(self.sidebar)
        
        # Natal Input
        self.group_natal = QGroupBox("Radix (Natal Chart)")
        self.form_natal = QVBoxLayout(self.group_natal)
        self.name_n = QLineEdit("Native"); self.name_n.setPlaceholderText("Name")
        self.dt_n = QDateTimeEdit(datetime.now()); self.dt_n.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.loc_n = QLineEdit("London"); self.loc_n.setPlaceholderText("Location")
        self.lat_n = QLineEdit("51.5"); self.lat_n.setPlaceholderText("Lat")
        self.lon_n = QLineEdit("-0.12"); self.lon_n.setPlaceholderText("Lon")
        
        for w in [self.name_n, self.dt_n, self.loc_n, self.lat_n, self.lon_n]: self.form_natal.addWidget(w)
        self.side_layout.addWidget(self.group_natal)
        
        # Method Settings
        self.group_meth = QGroupBox("Prediction Settings")
        self.form_meth = QVBoxLayout(self.group_meth)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Secondary Progressions", "Solar Arc Directions"])
        self.form_meth.addWidget(QLabel("Method:"))
        self.form_meth.addWidget(self.method_combo)
        
        self.target_dt = QDateTimeEdit(datetime.now())
        self.target_dt.setDisplayFormat("yyyy-MM-dd")
        self.target_dt.setCalendarPopup(True)
        self.form_meth.addWidget(QLabel("Target Date:"))
        self.form_meth.addWidget(self.target_dt)
        
        self.biwheel_cb = QCheckBox("Show as Bi-Wheel (vs Natal)")
        self.biwheel_cb.setChecked(True)
        self.form_meth.addWidget(self.biwheel_cb)
        
        self.side_layout.addWidget(self.group_meth)
        
        # Action
        self.calc_btn = QPushButton("Calculate Forecast")
        self.calc_btn.setStyleSheet(f"background-color: {COLORS['primary']}; color: white; padding: 8px;")
        self.calc_btn.clicked.connect(self._on_calculate)
        self.side_layout.addWidget(self.calc_btn)
        self.side_layout.addStretch()
        
        # 2. Main Canvas
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.canvas = ChartCanvas()
        self.content_layout.addWidget(self.canvas)
        
        self.layout.addWidget(self.sidebar)
        self.layout.addWidget(self.content)
        
        self._last_natal_res: Optional[ChartResult] = None

    def _on_calculate(self):
        try:
            natal_event = self._build_natal_event()
            target_date = self.target_dt.dateTime().toPyDateTime()
            method = self.method_combo.currentText()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return

        self.calc_btn.setEnabled(False)
        self.calc_btn.setText("Predicting...")
        
        worker = BackgroundWorker(self._perform_progression, natal_event, target_date, method)
        worker.signals.result.connect(self._on_result)
        worker.signals.error.connect(self._on_error)
        worker.signals.finished.connect(self._on_finished)
        QThreadPool.globalInstance().start(worker)

    def _build_natal_event(self) -> AstrologyEvent:
        try:
            lat = float(self.lat_n.text())
            lon = float(self.lon_n.text())
        except ValueError:
            raise ValueError("Invalid Coordinates")
        return AstrologyEvent(
            self.name_n.text(),
            self.dt_n.dateTime().toPyDateTime(),
            GeoLocation(self.loc_n.text(), lat, lon)
        )

    def _perform_progression(self, natal: AstrologyEvent, target: datetime, method: str):
        # 1. Base Natal Chart (needed for Bi-wheel reference or calculation)
        natal_req = ChartRequest(natal, chart_type="Radix")
        # Optimization: We could reuse valid cache inside service, but here we just request it.
        natal_res = self._service.generate_chart(natal_req)
        
        # 2. Progressed Chart
        if "Secondary" in method:
            prog_res = self._prog_service.calculate_secondary_progression(natal_req, target)
        else: # Solar Arc
            prog_res = self._prog_service.calculate_solar_arc(natal_req, target)
            
        return (natal_res, prog_res)

    def _on_result(self, results):
        natal_res, prog_res = results
        self._last_natal_res = natal_res
        
        if self.biwheel_cb.isChecked():
            self.canvas.set_synastry_data(
                natal_res.planet_positions,
                prog_res.planet_positions,
                natal_res.house_positions # Keep Natal Houses as frame of reference usually
            )
        else:
            self.canvas.set_data(prog_res.planet_positions, prog_res.house_positions)
        
    def _on_error(self, err):
        QMessageBox.critical(self, "Error", str(err[1]))

    def _on_finished(self):
        self.calc_btn.setText("Calculate Forecast")
        self.calc_btn.setEnabled(True)
