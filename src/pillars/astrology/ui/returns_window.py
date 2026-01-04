"""
Sovereign Window for Planetary Returns (Solar/Lunar).
"""
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QDateTimeEdit, QComboBox, 
    QPushButton, QGroupBox, QSpinBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt, QThreadPool

from shared.ui.theme import COLORS
from shared.ui.worker import BackgroundWorker
from ..models.chart_models import ChartRequest, AstrologyEvent, GeoLocation, ChartResult
from ..services.openastro_service import OpenAstroService
from ..services.returns_service import ReturnsService
from .chart_canvas import ChartCanvas

class ReturnsWindow(QMainWindow):
    """
    Focused window for Solar/Lunar Returns.
    """
    
    def __init__(self, service: OpenAstroService, parent: QWidget | None = None):
        super().__init__(parent)
        self._service = service # For chart generation
        self._returns_service = ReturnsService() # For calculating the time
        
        self.setWindowTitle("Planetary Returns")
        self.resize(1100, 800)
        
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self._layout = QHBoxLayout(self.main_widget)
        self._layout.setSpacing(0)
        self._layout.setContentsMargins(0, 0, 0, 0)
        
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
        
        # Return Settings
        self.group_ret = QGroupBox("Return Settings")
        self.form_ret = QVBoxLayout(self.group_ret)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Solar Return", "Lunar Return"])
        self.form_ret.addWidget(QLabel("Return Type:"))
        self.form_ret.addWidget(self.type_combo)
        
        self.year_spin = QSpinBox()
        self.year_spin.setRange(1000, 3000)
        self.year_spin.setValue(datetime.now().year)
        self.form_ret.addWidget(QLabel("Target Year:"))
        self.form_ret.addWidget(self.year_spin)
        
        self.relocate_cb = QCheckBox("Relocate Chart")
        self.relocate_cb.stateChanged.connect(self._toggle_relocation)
        self.form_ret.addWidget(self.relocate_cb)
        
        self.loc_r = QLineEdit("Current Location"); self.loc_r.setEnabled(False)
        self.lat_r = QLineEdit("0.0"); self.lat_r.setEnabled(False)
        self.lon_r = QLineEdit("0.0"); self.lon_r.setEnabled(False)
        self.form_ret.addWidget(self.loc_r)
        self.form_ret.addWidget(self.lat_r) 
        self.form_ret.addWidget(self.lon_r)
        
        self.side_layout.addWidget(self.group_ret)
        
        # Action
        self.calc_btn = QPushButton("Calculate Return")
        self.calc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.calc_btn.setProperty("archetype", "magus")
        self.calc_btn.clicked.connect(self._on_calculate)
        self.side_layout.addWidget(self.calc_btn)
        self.side_layout.addStretch()
        
        # 2. Main Canvas
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.canvas = ChartCanvas()
        self.content_layout.addWidget(self.canvas)
        
        self._layout.addWidget(self.sidebar)
        self._layout.addWidget(self.content)

    def _toggle_relocation(self, state: int) -> None:
        enabled = state == Qt.CheckState.Checked.value
        self.loc_r.setEnabled(enabled)
        self.lat_r.setEnabled(enabled)
        self.lon_r.setEnabled(enabled)
        if enabled:
            self.loc_r.setFocus()

    def _on_calculate(self) -> None:
        try:
            natal_event = self._build_natal_event()
            
            # Resolve Return Location
            if self.relocate_cb.isChecked():
                try:
                    rlat = float(self.lat_r.text())
                    rlon = float(self.lon_r.text())
                    rloc = GeoLocation(self.loc_r.text(), rlat, rlon)
                except ValueError:
                     raise ValueError("Invalid Relocation Coordinates")
            else:
                rloc = natal_event.location
                
            target_year = self.year_spin.value()
            rtype = "sun" if "Solar" in self.type_combo.currentText() else "moon"
            
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", str(e))
            return

        self.calc_btn.setEnabled(False)
        self.calc_btn.setText("Solving...")
        
        worker = BackgroundWorker(self._perform_return, natal_event, target_year, rtype, rloc)
        worker.signals.result.connect(self._on_result)
        worker.signals.error.connect(self._on_error)
        worker.signals.finished.connect(self._on_finished)
        pool = QThreadPool.globalInstance()
        if pool is not None:
            pool.start(worker)

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

    def _perform_return(self, natal: AstrologyEvent, year: int, body: str, loc: GeoLocation) -> ChartResult:
        # 1. Solve Exact Time
        # Note: calculate_return takes natal_event and returns the Event of the return
        return_event = self._returns_service.calculate_return(natal, year, body_name=body)
        
        # 2. Update Location (Relocation)
        # return_event location defaults to natal in service (usually). We override it.
        # But wait, class is immutable dataclass? slots=True.
        # We can construct new event or modify if mutable? Dataclass is mutable by default unless frozen=True.
        # chart_models.py: @dataclass(slots=True) -> mutable.
        return_event.location = loc
        return_event.name = f"{body.title()} Return {year} for {natal.name}"
        
        # 3. Generate Chart
        req = ChartRequest(return_event, chart_type="Radix") # Returns are just radix charts at a specific time
        return self._service.generate_chart(req)

    def _on_result(self, result: ChartResult) -> None:
        self.canvas.set_data(result.planet_positions, result.house_positions)
        
    def _on_error(self, err: tuple[object, object, object]) -> None:
        # err is (exctype, value, traceback_str)
        value = err[1]
        QMessageBox.critical(self, "Calculation Error", str(value))

    def _on_finished(self) -> None:
        self.calc_btn.setText("Calculate Return")
        self.calc_btn.setEnabled(True)
