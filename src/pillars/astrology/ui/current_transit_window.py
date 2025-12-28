"""Current transit viewer window."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import pytz
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
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
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..models import AstrologyEvent, ChartRequest, ChartResult, GeoLocation
from ..services import (
    ChartComputationError,
    LocationLookupError,
    LocationLookupService,
    OpenAstroService,
)
from ..utils import AstrologyPreferences, DefaultLocation
from ..utils.conversions import to_zodiacal_string


class CurrentTransitWindow(QMainWindow):
    """Displays a "now" chart using the saved default location."""

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
        self.setWindowTitle("Current Transit Viewer")
        self.resize(1100, 720)

        self._service: Optional[OpenAstroService] = None
        self._service_error: Optional[str] = None
        self._last_svg: Optional[str] = None
        self._temp_svg_files: List[str] = []
        self._location_lookup = LocationLookupService()
        self._preferences = AstrologyPreferences()
        self._default_location: Optional[DefaultLocation] = None
        self._current_timezone_id: Optional[str] = None
        self._last_generated: Optional[datetime] = None

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

        header = QLabel("Current Transit Overview")
        header_font = QFont()
        header_font.setPointSize(20)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        self.subtitle_label = QLabel("Not generated yet")
        self.subtitle_label.setStyleSheet("color: #666")
        layout.addWidget(self.subtitle_label)

        layout.addWidget(self._build_input_group())
        layout.addLayout(self._build_action_row())
        layout.addWidget(self._build_results_splitter(), stretch=1)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        if self._service_error:
            self._set_status(self._service_error)

    def _build_input_group(self) -> QGroupBox:
        group = QGroupBox("Location")
        form = QFormLayout(group)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.location_name_input = QLineEdit("Default Location")
        form.addRow("Label", self.location_name_input)

        self.latitude_input = QDoubleSpinBox()
        self.latitude_input.setRange(-90.0, 90.0)
        self.latitude_input.setDecimals(6)
        form.addRow("Latitude", self.latitude_input)

        self.longitude_input = QDoubleSpinBox()
        self.longitude_input.setRange(-180.0, 180.0)
        self.longitude_input.setDecimals(6)
        form.addRow("Longitude", self.longitude_input)

        self.elevation_input = QSpinBox()
        self.elevation_input.setRange(-500, 9000)
        form.addRow("Elevation (m)", self.elevation_input)

        self.timezone_input = QDoubleSpinBox()
        self.timezone_input.setRange(-14.0, 14.0)
        self.timezone_input.setDecimals(2)
        self.timezone_input.setSingleStep(0.25)
        form.addRow("Time Zone Offset", self.timezone_input)

        button_row = QHBoxLayout()
        self.search_button = QPushButton("Search City...")
        self.search_button.clicked.connect(self._search_location)
        button_row.addWidget(self.search_button)
        self.use_default_button = QPushButton("Use Default")
        self.use_default_button.clicked.connect(self._apply_default)
        button_row.addWidget(self.use_default_button)
        self.save_default_button = QPushButton("Save as Default")
        self.save_default_button.clicked.connect(self._save_default)
        button_row.addWidget(self.save_default_button)
        button_row.addStretch()
        search_widget = QWidget()
        search_widget.setLayout(button_row)
        form.addRow("", search_widget)

        return group

    def _build_action_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addStretch()

        self.include_svg_checkbox = QCheckBox("Include SVG")
        self.include_svg_checkbox.setChecked(True)
        row.addWidget(self.include_svg_checkbox)

        self.refresh_button = QPushButton("Generate Transit Now")
        self.refresh_button.clicked.connect(self._generate_transit)
        row.addWidget(self.refresh_button)

        self.export_button = QPushButton("Export SVG")
        self.export_button.clicked.connect(self._export_svg)
        self.export_button.setEnabled(False)
        row.addWidget(self.export_button)

        self.browser_button = QPushButton("Open in Browser")
        self.browser_button.clicked.connect(self._open_in_browser)
        self.browser_button.setEnabled(False)
        row.addWidget(self.browser_button)

        return row

    def _build_results_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_planet_group())
        splitter.addWidget(self._build_misc_group())
        splitter.setSizes([600, 400])
        return splitter

    def _build_planet_group(self) -> QGroupBox:
        group = QGroupBox("Planets")
        layout = QVBoxLayout(group)
        self.planets_table = QTableWidget(0, 2)
        self.planets_table.setHorizontalHeaderLabels(["Body", "Position"])
        layout.addWidget(self.planets_table)
        return group
    
    # ... existing code ...

    def _render_planets(self, result: ChartResult) -> None:
        self.planets_table.setRowCount(0)
        for position in result.planet_positions:
            row = self.planets_table.rowCount()
            self.planets_table.insertRow(row)
            self.planets_table.setItem(row, 0, QTableWidgetItem(position.name))
            
            formatted_pos = to_zodiacal_string(position.degree)
            self.planets_table.setItem(row, 1, QTableWidgetItem(formatted_pos))

    def _render_houses(self, result: ChartResult) -> None:
        self.houses_table.setRowCount(0)
        for house in result.house_positions:
            row = self.houses_table.rowCount()
            self.houses_table.insertRow(row)
            self.houses_table.setItem(row, 0, QTableWidgetItem(str(house.number)))
            
            formatted_pos = to_zodiacal_string(house.degree)
            self.houses_table.setItem(row, 1, QTableWidgetItem(formatted_pos))

    def _build_misc_group(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(10)

        houses_group = QGroupBox("Houses")
        houses_layout = QVBoxLayout(houses_group)
        self.houses_table = QTableWidget(0, 2)
        self.houses_table.setHorizontalHeaderLabels(["House", "Degree"])
        houses_layout.addWidget(self.houses_table)
        layout.addWidget(houses_group)

        aspects_group = QGroupBox("Aspects / Raw Data")
        aspects_layout = QVBoxLayout(aspects_group)
        self.aspects_text = QPlainTextEdit()
        self.aspects_text.setReadOnly(True)
        aspects_layout.addWidget(self.aspects_text)
        layout.addWidget(aspects_group, stretch=1)

        return container

    # ------------------------------------------------------------------
    def _load_preferences(self) -> None:
        self._default_location = self._preferences.load_default_location()
        self.use_default_button.setEnabled(self._default_location is not None)
        if self._default_location:
            self._apply_location(self._default_location)

    # ------------------------------------------------------------------
    def _generate_transit(self) -> None:
        if self._service is None:
            QMessageBox.warning(self, "Unavailable", "OpenAstro2 is not available.")
            return

        event = self._build_event()
        settings = self._service.default_settings() if self._service else {}
        request = ChartRequest(
            primary_event=event,
            include_svg=self.include_svg_checkbox.isChecked(),
            settings=settings,
        )
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
        try:
            result = self._service.generate_chart(request)
        except ChartComputationError as exc:
            QMessageBox.critical(self, "Calculation Error", str(exc))
            self._set_status(str(exc))
        except Exception as exc:  # pragma: no cover - upstream safety
            QMessageBox.critical(self, "Unexpected Error", str(exc))
            self._set_status("Unexpected error generating transit")
        else:
            self._render_result(result)
            self._last_generated = datetime.now(timezone.utc)
            self.subtitle_label.setText(
                f"Generated at {self._last_generated.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}"
            )
            self._set_status("Transit generated")
        finally:
            QApplication.restoreOverrideCursor()

    def _build_event(self) -> AstrologyEvent:
        now = datetime.now(timezone.utc)
        location = GeoLocation(
            name=self.location_name_input.text().strip() or "Transit Location",
            latitude=self.latitude_input.value(),
            longitude=self.longitude_input.value(),
            elevation=float(self.elevation_input.value()),
        )
        return AstrologyEvent(
            name="Current Transit",
            timestamp=now,
            location=location,
            timezone_offset=self.timezone_input.value(),
        )

    def _render_result(self, result: ChartResult) -> None:
        self._render_planets(result)
        self._render_houses(result)
        self._render_aspects(result)
        self._handle_svg(result)

    def _render_planets(self, result: ChartResult) -> None:
        self.planets_table.setRowCount(0)
        for position in result.planet_positions:
            row = self.planets_table.rowCount()
            self.planets_table.insertRow(row)
            self.planets_table.setItem(row, 0, QTableWidgetItem(position.name))
            
            formatted_pos = to_zodiacal_string(position.degree)
            self.planets_table.setItem(row, 1, QTableWidgetItem(formatted_pos))

    def _render_houses(self, result: ChartResult) -> None:
        self.houses_table.setRowCount(0)
        for house in result.house_positions:
            row = self.houses_table.rowCount()
            self.houses_table.insertRow(row)
            self.houses_table.setItem(row, 0, QTableWidgetItem(str(house.number)))
            
            formatted_pos = to_zodiacal_string(house.degree)
            self.houses_table.setItem(row, 1, QTableWidgetItem(formatted_pos))

    def _render_aspects(self, result: ChartResult) -> None:
        pretty = json.dumps(result.aspect_summary or result.raw_payload, indent=2)
        self.aspects_text.setPlainText(pretty)

    def _handle_svg(self, result: ChartResult) -> None:
        self._last_svg = result.svg_document
        enabled = bool(result.svg_document)
        self.export_button.setEnabled(enabled)
        self.browser_button.setEnabled(enabled)

    # ------------------------------------------------------------------
    def _search_location(self) -> None:
        query, accepted = QInputDialog.getText(self, "Search City", "Enter a city or place name:")
        if not accepted or not query.strip():
            return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            results = self._location_lookup.search(query)
        except LocationLookupError as exc:
            QMessageBox.information(self, "No Results", str(exc))
            return
        except Exception as exc:  # pragma: no cover
            QMessageBox.critical(self, "Lookup Failed", str(exc))
            return
        finally:
            QApplication.restoreOverrideCursor()
        selection = self._select_result(results)
        if selection is None:
            return
        offset = self._calculate_offset(selection.timezone_id)
        self._apply_location(
            DefaultLocation(
                name=selection.label,
                latitude=selection.latitude,
                longitude=selection.longitude,
                elevation=float(selection.elevation or 0.0),
                timezone_offset=offset if offset is not None else self.timezone_input.value(),
                timezone_id=selection.timezone_id,
            )
        )

    def _select_result(self, results):
        if len(results) == 1:
            return results[0]
        options = [f"{entry.label} ({entry.latitude:.2f}, {entry.longitude:.2f})" for entry in results]
        choice, accepted = QInputDialog.getItem(
            self,
            "Select Location",
            "Multiple matches found. Choose one:",
            options,
            0,
            False,
        )
        if not accepted or not choice:
            return None
        return results[options.index(choice)]

    def _apply_location(self, location: DefaultLocation) -> None:
        self.location_name_input.setText(location.name)
        self.latitude_input.setValue(location.latitude)
        self.longitude_input.setValue(location.longitude)
        self.elevation_input.setValue(int(location.elevation))
        self._current_timezone_id = location.timezone_id
        offset = self._calculate_offset(location.timezone_id)
        self.timezone_input.setValue(offset if offset is not None else location.timezone_offset)

    def _calculate_offset(self, timezone_id: Optional[str]) -> Optional[float]:
        if not timezone_id:
            return None
        try:
            tz = pytz.timezone(timezone_id)
            now = datetime.now(timezone.utc)
            localized = now.astimezone(tz)
            offset = localized.utcoffset()
        except (pytz.UnknownTimeZoneError, Exception):
            return None
        if offset is None:
            return None
        return round(offset.total_seconds() / 3600.0, 2)

    def _apply_default(self) -> None:
        if not self._default_location:
            QMessageBox.information(self, "No Default", "Save a default location first.")
            return
        self._apply_location(self._default_location)
        self._set_status("Default location applied.")

    def _save_default(self) -> None:
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
        except OSError as exc:  # pragma: no cover
            QMessageBox.critical(self, "Save Failed", str(exc))
            return
        self._default_location = location
        self.use_default_button.setEnabled(True)
        self._set_status("Default location saved.")

    # ------------------------------------------------------------------
    def _export_svg(self) -> None:
        if not self._last_svg:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save SVG", "transit.svg", "SVG Files (*.svg)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(self._last_svg)
        except OSError as exc:
            QMessageBox.critical(self, "Save Failed", str(exc))
        else:
            self._set_status(f"SVG saved to {path}")

    def _open_in_browser(self) -> None:
        if not self._last_svg:
            QMessageBox.information(self, "SVG Unavailable", "Generate a transit first.")
            return
        tmp_path: Optional[str] = None
        try:
            tmp_handle = tempfile.NamedTemporaryFile("w", suffix=".svg", prefix="transit_chart_", delete=False, encoding="utf-8")
            tmp_handle.write(self._last_svg)
            tmp_handle.close()
            tmp_path = tmp_handle.name
            self._temp_svg_files.append(tmp_path)
        except OSError as exc:
            QMessageBox.critical(self, "Temp File Error", str(exc))
            return
        chrome_path = self._find_chrome_binary()
        if chrome_path and self._launch_chrome(chrome_path, tmp_path):
            return
        if self._launch_default_browser(tmp_path):
            return
        QMessageBox.warning(self, "Browser Launch Failed", "Could not open the SVG in any browser.")

    def _find_chrome_binary(self) -> Optional[str]:
        for candidate in ("google-chrome", "google-chrome-stable", "chrome", "chromium-browser", "chromium"):
            chrome_path = shutil.which(candidate)
            if chrome_path:
                return chrome_path
        return None

    def _launch_chrome(self, chrome_path: str, svg_path: str) -> bool:
        try:
            # Removed Wayland/Ozone flags to improve compatibility
            subprocess.Popen([chrome_path, "--new-tab", svg_path])
        except OSError as exc:
            QMessageBox.critical(self, "Chrome Launch Failed", str(exc))
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

    def _cleanup_temp_files(self) -> None:
        while self._temp_svg_files:
            path = self._temp_svg_files.pop()
            try:
                if path and os.path.exists(path):
                    os.unlink(path)
            except OSError:
                continue

    def _set_status(self, message: str) -> None:
        if hasattr(self, "status_label"):
            self.status_label.setText(message)

    def _sign_label(self, index: Optional[int]) -> str:
        if index is None or index < 0 or index >= len(self.ZODIAC_SIGNS):
            return "Unknown"
        return self.ZODIAC_SIGNS[index]

    def closeEvent(self, a0: Optional[QCloseEvent]) -> None:  # noqa: N802
        """
        Closeevent logic.
        
        Args:
            a0: Description of a0.
        
        Returns:
            Result of closeEvent operation.
        """
        self._cleanup_temp_files()
        super().closeEvent(a0)