"""Interactive UI for generating natal charts through OpenAstro2."""
from __future__ import annotations

import json
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
from PyQt6.QtGui import QCloseEvent, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
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
    ChartStorageService,
    LocationLookupError,
    LocationResult,
    LocationLookupService,
    OpenAstroNotAvailableError,
    OpenAstroService,
    SavedChartSummary,
)
from ..utils import AstrologyPreferences, DefaultLocation


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
        self._last_request: Optional[ChartRequest] = None
        self._last_result: Optional[ChartResult] = None
        self._preferences = AstrologyPreferences()
        self._default_location: Optional[DefaultLocation] = None
        self._current_timezone_id: Optional[str] = None

        self._init_service()
        self._build_ui()
        self._initialize_preferences()

    # ------------------------------------------------------------------
    # UI assembly
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        title = QLabel("Generate Natal Charts with OpenAstro2")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addWidget(self._build_input_group())
        layout.addLayout(self._build_action_row())
        layout.addWidget(self._build_results_splitter(), stretch=1)

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
        self.include_svg_checkbox.setChecked(False)
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

        if self._service is None:
            self.generate_button.setEnabled(False)

        return row

    def _build_results_splitter(self) -> QSplitter:
        splitter = QSplitter(Qt.Orientation.Horizontal)

        splitter.addWidget(self._build_planet_group())
        splitter.addWidget(self._build_misc_group())

        splitter.setSizes([650, 450])
        return splitter

    def _build_planet_group(self) -> QGroupBox:
        group = QGroupBox("Planetary Positions")
        layout = QVBoxLayout(group)

        self.planets_table = QTableWidget(0, 3)
        self.planets_table.setHorizontalHeaderLabels(["Body", "Degree", "Sign"])
        header = self.planets_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
        layout.addWidget(self.planets_table)
        return group

    def _build_misc_group(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(10)

        houses_group = QGroupBox("House Cusps")
        houses_layout = QVBoxLayout(houses_group)
        self.houses_table = QTableWidget(0, 2)
        self.houses_table.setHorizontalHeaderLabels(["House", "Degree"])
        houses_header = self.houses_table.horizontalHeader()
        if houses_header:
            houses_header.setStretchLastSection(True)
        houses_layout.addWidget(self.houses_table)
        layout.addWidget(houses_group)

        aspects_group = QGroupBox("Aspect / Raw Data")
        aspects_layout = QVBoxLayout(aspects_group)
        self.aspects_text = QPlainTextEdit()
        self.aspects_text.setReadOnly(True)
        aspects_layout.addWidget(self.aspects_text)
        layout.addWidget(aspects_group, stretch=1)

        svg_group = QGroupBox("SVG Output")
        svg_layout = QVBoxLayout(svg_group)
        self.svg_label = QLabel("No SVG rendered.")
        svg_layout.addWidget(self.svg_label)
        self.save_svg_button = QPushButton("Export SVG...")
        self.save_svg_button.clicked.connect(self._export_svg)
        self.save_svg_button.setEnabled(False)
        svg_layout.addWidget(self.save_svg_button, alignment=Qt.AlignmentFlag.AlignLeft)

        self.open_chrome_button = QPushButton("Open in Browser")
        self.open_chrome_button.clicked.connect(self._open_in_browser)
        self.open_chrome_button.setEnabled(False)
        svg_layout.addWidget(self.open_chrome_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(svg_group)

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

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _generate_chart(self) -> None:
        if self._service is None:
            QMessageBox.warning(self, "Unavailable", "OpenAstro2 is not available in this environment.")
            return

        request = self._build_request()
        QApplication.setOverrideCursor(Qt.CursorShape.BusyCursor)
        try:
            result = self._service.generate_chart(request)
        except ChartComputationError as exc:
            self._set_status(str(exc))
            QMessageBox.critical(self, "Calculation Error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive UI handling
            self._set_status("Unexpected failure while computing chart")
            QMessageBox.critical(self, "Unexpected Error", str(exc))
        else:
            self._render_result(result)
            self._set_status("Chart generated successfully.")
            self._last_request = request
            self._last_result = result
            self.save_chart_button.setEnabled(True)
        finally:
            QApplication.restoreOverrideCursor()

    def _clear_results(self) -> None:
        self.planets_table.setRowCount(0)
        self.houses_table.setRowCount(0)
        self.aspects_text.clear()
        self.svg_label.setText("No SVG rendered.")
        self.save_svg_button.setEnabled(False)
        self.open_chrome_button.setEnabled(False)
        self._last_svg = None
        self._last_result = None
        self.save_chart_button.setEnabled(False)
        self._set_status("Results cleared.")

    def _export_svg(self) -> None:
        if not self._last_svg:
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save SVG", "chart.svg", "SVG Files (*.svg)")
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as handle:
                handle.write(self._last_svg)
        except OSError as exc:
            QMessageBox.critical(self, "Save Failed", str(exc))
        else:
            self._set_status(f"SVG saved to {file_path}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _build_request(self) -> ChartRequest:
        qdatetime = self.datetime_input.dateTime()
        py_dt: datetime = qdatetime.toPyDateTime()
        if py_dt.tzinfo is None:
            py_dt = py_dt.replace(tzinfo=timezone.utc)

        location = GeoLocation(
            name=self.location_name_input.text().strip() or "Unknown",
            latitude=self.latitude_input.value(),
            longitude=self.longitude_input.value(),
            elevation=float(self.elevation_input.value()),
        )

        primary_event = AstrologyEvent(
            name=self.name_input.text().strip() or "Primary Event",
            timestamp=py_dt,
            location=location,
            timezone_offset=self.timezone_input.value(),
        )

        settings = self._service.default_settings() if self._service else {}
        cfg = settings.setdefault("astrocfg", {})
        cfg["houses_system"] = self.house_system_combo.currentData() or "P"

        return ChartRequest(
            primary_event=primary_event,
            include_svg=self.include_svg_checkbox.isChecked(),
            settings=settings,
        )

    def _render_result(self, result) -> None:
        self._render_planets(result)
        self._render_houses(result)
        self._render_aspects(result)
        self._handle_svg(result)

    def _render_planets(self, result) -> None:
        self.planets_table.setRowCount(0)
        for position in result.planet_positions:
            row = self.planets_table.rowCount()
            self.planets_table.insertRow(row)
            self.planets_table.setItem(row, 0, QTableWidgetItem(position.name))
            self.planets_table.setItem(row, 1, QTableWidgetItem(f"{position.degree:.2f}°"))
            self.planets_table.setItem(row, 2, QTableWidgetItem(self._sign_label(position.sign_index)))

    def _render_houses(self, result) -> None:
        self.houses_table.setRowCount(0)
        for house in result.house_positions:
            row = self.houses_table.rowCount()
            self.houses_table.insertRow(row)
            self.houses_table.setItem(row, 0, QTableWidgetItem(str(house.number)))
            self.houses_table.setItem(row, 1, QTableWidgetItem(f"{house.degree:.2f}°"))

    def _render_aspects(self, result) -> None:
        pretty = json.dumps(result.aspect_summary or result.raw_payload, indent=2)
        self.aspects_text.setPlainText(pretty)

    def _handle_svg(self, result) -> None:
        self._last_svg = result.svg_document
        if result.svg_document:
            self.svg_label.setText(f"SVG generated ({len(result.svg_document)} chars)")
            self.save_svg_button.setEnabled(True)
            self.open_chrome_button.setEnabled(True)
        else:
            self.svg_label.setText("SVG generation disabled for this chart.")
            self.save_svg_button.setEnabled(False)
            self.open_chrome_button.setEnabled(False)

    def _sign_label(self, index: Optional[int]) -> str:
        if index is None or index < 0 or index >= len(self.ZODIAC_SIGNS):
            return "Unknown"
        return self.ZODIAC_SIGNS[index]

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

        query, accepted = QInputDialog.getText(self, "Find Chart", "Enter search text (or leave blank for recent):")
        if not accepted:
            return

        matches = self._storage_service.search(text=query.strip()) if query.strip() else self._storage_service.list_recent()
        if not matches:
            QMessageBox.information(self, "No Results", "No charts matched your search.")
            return

        chosen = self._prompt_for_chart_choice(matches)
        if chosen is None:
            return

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

    def _prompt_for_chart_choice(self, matches: List[SavedChartSummary]) -> Optional[SavedChartSummary]:
        if len(matches) == 1:
            return matches[0]

        options = [
            f"{item.name} – {item.location_label} ({item.event_timestamp:%Y-%m-%d %H:%M})"
            for item in matches
        ]
        choice, accepted = QInputDialog.getItem(
            self,
            "Select Chart",
            "Multiple charts found. Choose one:",
            options,
            0,
            False,
        )
        if not accepted or not choice:
            return None
        return matches[options.index(choice)]

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
        self._cleanup_temp_files()
        super().closeEvent(a0)

 