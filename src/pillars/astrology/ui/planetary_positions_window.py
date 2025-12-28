"""Ephemeris-style planetary positions viewer."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QDateTimeEdit,
    QSpinBox,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QCheckBox,
    QGridLayout,
    QDialog,
)

from ..models import AstrologyEvent, ChartRequest, GeoLocation
from ..services import OpenAstroNotAvailableError, OpenAstroService
from ..utils import AstrologyPreferences, DefaultLocation
from ..utils.conversions import to_zodiacal_string
from shared.ui.window_manager import WindowManager
from shared.ui.window_manager import WindowManager


PLANET_CHOICES: Sequence[str] = (
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
    "Chiron",
    "North Node",
    "South Node",
)

ZODIAC_SIGNS = (
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
)

MAX_TIMESTAMPS = 240  # safety valve for UI responsiveness


@dataclass(slots=True)
class EphemerisRow:
    """
    Ephemeris Row class definition.
    
    """
    timestamp: datetime
    body: str
    degree: float
    sign_label: str
    retrograde: Optional[bool]
    speed: Optional[float]


class EphemerisResultsDialog(QDialog):
    """Popup dialog used to display ephemeris matrices."""

    def __init__(self, parent: Optional[QWidget] = None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Ephemeris Results")
        self.resize(900, 600)
        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 0)
        layout.addWidget(self.table)

    def populate(
        self,
        timestamps: Sequence[datetime],
        planet_labels: Sequence[str],
        planet_keys: Sequence[str],
        matrix: Dict[datetime, Dict[str, EphemerisRow]],
        formatter,
    ) -> None:
        """
        Populate logic.
        
        Args:
            timestamps: Description of timestamps.
            planet_labels: Description of planet_labels.
            planet_keys: Description of planet_keys.
            matrix: Description of matrix.
            formatter: Description of formatter.
        
        Returns:
            Result of populate operation.
        """
        self.table.setRowCount(len(timestamps))
        self.table.setColumnCount(len(planet_labels) + 1)
        headers = ["Timestamp"] + list(planet_labels)
        self.table.setHorizontalHeaderLabels(headers)
        for row_idx, ts in enumerate(timestamps):
            self.table.setItem(row_idx, 0, QTableWidgetItem(ts.strftime("%Y-%m-%d %H:%M")))
            row_map = matrix.get(ts, {})
            for col_idx, key in enumerate(planet_keys, start=1):
                entry = row_map.get(key)
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(formatter(entry)))
        self.table.resizeColumnsToContents()


class PlanetaryPositionsWindow(QMainWindow):
    """Displays planetary positions over a configurable time range."""

    def __init__(self, *_, window_manager: Optional[WindowManager] = None, parent: Optional[QWidget] = None):
        """
          init   logic.
        
        """
        super().__init__(parent)
        self.window_manager = window_manager
        self.setWindowTitle("Planetary Positions")
        self.resize(1100, 720)

        self._service: Optional[OpenAstroService] = None
        self._service_error: Optional[str] = None
        self._preferences = AstrologyPreferences()
        self._default_location: Optional[DefaultLocation] = None
        self._results_dialog: Optional[EphemerisResultsDialog] = None
        self._latest_matrix: Dict[datetime, Dict[str, EphemerisRow]] = {}
        self._latest_planet_labels: List[str] = []
        self._latest_planet_keys: List[str] = []
        self._latest_timestamps: List[datetime] = []

        self._init_service()
        self._build_ui()
        self._load_preferences()

    # ------------------------------------------------------------------
    def _init_service(self) -> None:
        try:
            self._service = OpenAstroService()
        except OpenAstroNotAvailableError as exc:
            self._service_error = str(exc)
            self._service = None

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Planetary Positions Ephemeris")
        header_font = QFont()
        header_font.setPointSize(20)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        layout.addWidget(self._build_timeframe_group())
        layout.addWidget(self._build_planet_group())
        layout.addWidget(self._build_location_group())
        layout.addLayout(self._build_action_row())

        self.status_label = QLabel(self._service_error or "Ready")
        layout.addWidget(self.status_label)

    def _build_timeframe_group(self) -> QGroupBox:
        group = QGroupBox("Time Range")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        now = datetime.now()

        self.start_input = QDateTimeEdit(now)
        self.start_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.start_input.setCalendarPopup(True)
        form.addRow("Start", self.start_input)

        self.days_input = QSpinBox()
        self.days_input.setRange(1, 60)
        self.days_input.setValue(7)
        form.addRow("Days", self.days_input)

        self.step_hours_input = QSpinBox()
        self.step_hours_input.setRange(1, 24)
        self.step_hours_input.setValue(24)
        form.addRow("Step (hours)", self.step_hours_input)

        return group

    def _build_planet_group(self) -> QGroupBox:
        group = QGroupBox("Planets")
        grid = QGridLayout(group)
        self.planet_checks: List[QCheckBox] = []
        for idx, name in enumerate(PLANET_CHOICES):
            check = QCheckBox(name)
            check.setChecked(True)
            self.planet_checks.append(check)
            row, col = divmod(idx, 4)
            grid.addWidget(check, row, col)

        button_row = QHBoxLayout()
        select_all = QPushButton("Select All")
        select_all.clicked.connect(lambda: self._set_planet_checks(True))
        button_row.addWidget(select_all)
        clear_all = QPushButton("Clear")
        clear_all.clicked.connect(lambda: self._set_planet_checks(False))
        button_row.addWidget(clear_all)
        button_row.addStretch()
        wrapper = QWidget()
        wrapper.setLayout(button_row)
        grid.addWidget(wrapper, (len(PLANET_CHOICES) // 4) + 1, 0, 1, 4)
        return group

    def _build_location_group(self) -> QGroupBox:
        group = QGroupBox("Reference Location")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.location_name_input = QLineEdit("Default Location")
        form.addRow("Label", self.location_name_input)

        self.latitude_input = QDoubleSpinBox()
        self.latitude_input.setDecimals(4)
        self.latitude_input.setRange(-90.0, 90.0)
        self.latitude_input.setValue(0.0)
        form.addRow("Latitude", self.latitude_input)

        self.longitude_input = QDoubleSpinBox()
        self.longitude_input.setDecimals(4)
        self.longitude_input.setRange(-180.0, 180.0)
        self.longitude_input.setValue(0.0)
        form.addRow("Longitude", self.longitude_input)

        self.timezone_input = QDoubleSpinBox()
        self.timezone_input.setDecimals(2)
        self.timezone_input.setSingleStep(0.25)
        self.timezone_input.setRange(-14.0, 14.0)
        self.timezone_input.setValue(0.0)
        form.addRow("Timezone Offset", self.timezone_input)

        self.use_default_button = QPushButton("Use Default")
        self.use_default_button.clicked.connect(self._apply_default_location)
        form.addRow("", self.use_default_button)

        return group

    def _build_action_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addStretch()
        self.generate_button = QPushButton("Generate Table")
        self.generate_button.clicked.connect(self._generate_ephemeris)
        row.addWidget(self.generate_button)

        self.export_button = QPushButton("Export CSV")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._export_csv)
        row.addWidget(self.export_button)

        self.send_button = QPushButton("Send to Emerald Tablet")
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self._send_to_tablet)
        row.addWidget(self.send_button)
        return row

    # ------------------------------------------------------------------
    def _load_preferences(self) -> None:
        self._default_location = self._preferences.load_default_location()
        self.use_default_button.setEnabled(self._default_location is not None)
        if self._default_location:
            self._apply_location(self._default_location)

    def _apply_default_location(self) -> None:
        if not self._default_location:
            QMessageBox.information(self, "No Default", "Save a default location in the transit or natal view first.")
            return
        self._apply_location(self._default_location)
        self._set_status("Default location applied.")

    def _apply_location(self, location: DefaultLocation) -> None:
        self.location_name_input.setText(location.name)
        self.latitude_input.setValue(location.latitude)
        self.longitude_input.setValue(location.longitude)
        self.timezone_input.setValue(location.timezone_offset)

    # ------------------------------------------------------------------
    def _set_planet_checks(self, checked: bool) -> None:
        for box in self.planet_checks:
            box.setChecked(checked)

    def _generate_ephemeris(self) -> None:
        if not self._service:
            QMessageBox.warning(self, "Unavailable", self._service_error or "OpenAstro2 is unavailable.")
            return
        selections = [
            (self._canonical_name(box.text()), box.text())
            for box in self.planet_checks
            if box.isChecked()
        ]
        if not selections:
            QMessageBox.information(self, "Select Planets", "Choose at least one planet to display.")
            return
        planet_keys = [item[0] for item in selections]
        planet_labels = [item[1] for item in selections]

        start_dt = self.start_input.dateTime().toPyDateTime()
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        total_hours = self.days_input.value() * 24
        step_hours = self.step_hours_input.value()
        timestamps = [start_dt + timedelta(hours=i) for i in range(0, total_hours + 1, step_hours)]
        if len(timestamps) > MAX_TIMESTAMPS:
            QMessageBox.warning(self, "Range Too Large", f"Please reduce the range or step size (max {MAX_TIMESTAMPS} timestamps).")
            return

        location = GeoLocation(
            name=self.location_name_input.text().strip() or "Reference",
            latitude=float(self.latitude_input.value()),
            longitude=float(self.longitude_input.value()),
            elevation=0.0,
        )

        include_svg = False
        matrix: Dict[datetime, Dict[str, EphemerisRow]] = {}
        flattened: List[EphemerisRow] = []
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
        try:
            for ts in timestamps:
                settings = self._service.default_settings()
                event = AstrologyEvent(
                    name=f"Ephemeris {ts.isoformat()}",
                    timestamp=ts,
                    location=location,
                    timezone_offset=float(self.timezone_input.value()),
                )
                request = ChartRequest(primary_event=event, include_svg=include_svg, settings=settings)
                result = self._service.generate_chart(request)
                row_map = self._extract_rows(result, ts, planet_keys)
                matrix[ts] = row_map
                flattened.extend(row_map.values())
        except Exception as exc:  # pragma: no cover
            QMessageBox.critical(self, "Generation Failed", str(exc))
            self._set_status("Ephemeris generation failed.")
            return
        finally:
            QApplication.restoreOverrideCursor()

        self._latest_matrix = matrix
        self._latest_planet_labels = planet_labels
        self._latest_planet_keys = planet_keys
        self._latest_timestamps = timestamps
        self.export_button.setEnabled(bool(flattened))
        if hasattr(self, "send_button"):
            self.send_button.setEnabled(bool(flattened))
        self._set_status(f"Generated {len(flattened)} entries across {len(timestamps)} timestamps.")
        if flattened:
            self._show_results_dialog()
        else:
            QMessageBox.information(self, "No Data", "No planetary data returned for the selected range.")

    def _extract_rows(self, result, timestamp: datetime, selected: Sequence[str]) -> Dict[str, EphemerisRow]:
        selected_set = set(selected)
        retro_map = self._retrograde_map(result)
        speed_map = self._speed_map(result)
        rows: Dict[str, EphemerisRow] = {}
        for position in result.planet_positions:
            key = self._canonical_name(position.name)
            if key not in selected_set:
                continue
            rows[key] = EphemerisRow(
                timestamp=timestamp,
                body=position.name,
                degree=position.degree % 360,
                sign_label=self._sign_label(position.sign_index),
                retrograde=retro_map.get(key),
                speed=speed_map.get(key),
            )
        return rows

    def _retrograde_map(self, result) -> Dict[str, bool]:
        data: Dict[str, bool] = {}
        payload = result.raw_payload or {}
        retro_seq = payload.get("planets_retrograde")
        if isinstance(retro_seq, list):
            for idx, flag in enumerate(retro_seq):
                if idx < len(result.planet_positions):
                    key = self._canonical_name(result.planet_positions[idx].name)
                    data[key] = bool(flag)
        detail = payload.get("planets_detail") or {}
        for name, info in detail.items():
            flag = info.get("planets_retrograde")
            if flag is not None:
                data[self._canonical_name(name)] = bool(flag)
        return data

    def _speed_map(self, result) -> Dict[str, float]:
        payload = result.raw_payload or {}
        detail = payload.get("planets_detail") or {}
        speeds: Dict[str, float] = {}
        for name, info in detail.items():
            try:
                speeds[self._canonical_name(name)] = float(info.get("planets_speed"))
            except (TypeError, ValueError):
                continue
        return speeds

    def _export_csv(self) -> None:
        if not self._latest_matrix:
            QMessageBox.information(self, "No Data", "Generate an ephemeris first.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Ephemeris", "ephemeris.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["timestamp", *self._latest_planet_labels])
                for ts in self._latest_timestamps:
                    row_map = self._latest_matrix.get(ts, {})
                    row_cells = [self._format_cell(row_map.get(key)) for key in self._latest_planet_keys]
                    writer.writerow([ts.isoformat(), *row_cells])
        except OSError as exc:
            QMessageBox.critical(self, "Export Failed", str(exc))
        else:
            self._set_status(f"Exported {len(self._latest_timestamps)} rows to {Path(path).name}.")

    def _sign_label(self, index: Optional[int]) -> str:
        if index is None or index < 0 or index >= len(ZODIAC_SIGNS):
            return "Unknown"
        return ZODIAC_SIGNS[index]

    def _set_status(self, message: str) -> None:
        if hasattr(self, "status_label"):
            self.status_label.setText(message)

    def _show_results_dialog(self) -> None:
        if not self._latest_matrix:
            return
        if self._results_dialog is None:
            self._results_dialog = EphemerisResultsDialog(self)
        self._results_dialog.populate(
            self._latest_timestamps,
            self._latest_planet_labels,
            self._latest_planet_keys,
            self._latest_matrix,
            self._format_cell,
        )
        self._results_dialog.show()
        self._results_dialog.raise_()
        self._results_dialog.activateWindow()

    def _format_cell(self, row: Optional[EphemerisRow]) -> str:
        if row is None:
            return "--"
        text = to_zodiacal_string(row.degree)
        if row.retrograde:
            text += " (R)"
        if row.speed is not None:
            text += f"\n{row.speed:.3f}°/day"
        return text

    def _send_to_tablet(self) -> None:
        """Send current ephemeris data to Emerald Tablet."""
        if not self._latest_matrix:
            return
            
        if not self.window_manager:
            QMessageBox.warning(self, "Integration Error", "Window Manager not linked.")
            return

        # Format data for Hub
        columns = ["Timestamp"] + self._latest_planet_labels
        rows = []
        
        for ts in self._latest_timestamps:
            row_map = self._latest_matrix.get(ts, {})
            row_data = [ts.isoformat()]
            for key in self._latest_planet_keys:
                cell_text = self._format_cell(row_map.get(key))
                row_data.append(cell_text)
            rows.append(row_data)

        export_data = {
            "name": "Planetary Positions Ephemeris",
            "data": {
                "columns": columns,
                "data": rows,
                "styles": {}
            }
        }

        # Open Hub and Send via NavigationBus
        from shared.signals.navigation_bus import navigation_bus
        
        navigation_bus.request_window.emit(
            "emerald_tablet", 
            {"allow_multiple": False, "window_manager": self.window_manager}
        )
        
        hub = self.window_manager.get_active_windows().get("emerald_tablet")
        
        if hasattr(hub, "receive_import"):
            hub.receive_import(export_data["name"], export_data["data"])
            self._set_status("Sent data to Emerald Tablet.")

    def _canonical_name(self, name: str) -> str:
        normalized = "".join(ch for ch in name.lower() if ch.isalnum())
        alias_map = {
            "truenode": "northnode",
            "meannode": "southnode",
            "node": "northnode",
            "dragonhead": "northnode",
            "dragontail": "southnode",
        }
        return alias_map.get(normalized, normalized)