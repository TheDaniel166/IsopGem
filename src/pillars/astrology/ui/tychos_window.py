"""Tychos/Skyfield planetary snapshot viewer."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QDateTimeEdit,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..services import (
    TychosSkyfieldComputationError,
    TychosSkyfieldNotAvailableError,
    TychosSkyfieldService,
)


class TychosWindow(QMainWindow):
    """Simple viewer for Tychos RA/Dec results."""

    def __init__(self, *_, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Tychos Skyfield Viewer")
        self.resize(900, 640)

        self._service: Optional[TychosSkyfieldService] = None
        self._service_error: Optional[str] = None
        self._body_checks: List[QCheckBox] = []

        self._init_service()
        self._build_ui()

    # ------------------------------------------------------------------
    def _init_service(self) -> None:
        try:
            self._service = TychosSkyfieldService()
        except (TychosSkyfieldNotAvailableError, TychosSkyfieldComputationError) as exc:
            self._service_error = str(exc)
            self._service = None

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Tychos Solar System Snapshot")
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        layout.addWidget(self._build_time_group())
        layout.addWidget(self._build_bodies_group())
        layout.addLayout(self._build_action_row())
        layout.addWidget(self._build_table(), stretch=1)

        self.status_label = QLabel(self._service_error or "Ready")
        layout.addWidget(self.status_label)

        if self._service_error:
            self.generate_button.setEnabled(False)

    def _build_time_group(self) -> QGroupBox:
        group = QGroupBox("Moment (UTC)")
        row = QHBoxLayout(group)
        self.datetime_input = QDateTimeEdit(QDateTime.currentDateTimeUtc())
        self.datetime_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.datetime_input.setCalendarPopup(True)
        row.addWidget(QLabel("Timestamp"))
        row.addWidget(self.datetime_input, stretch=1)
        return group

    def _build_bodies_group(self) -> QGroupBox:
        group = QGroupBox("Bodies")
        grid = QGridLayout(group)
        bodies = self._service.list_bodies() if self._service else []
        if not bodies:
            info = QLabel("No bodies available (service unavailable).")
            grid.addWidget(info, 0, 0)
            return group

        for idx, name in enumerate(bodies):
            check = QCheckBox(name)
            check.setChecked(True)
            self._body_checks.append(check)
            row, col = divmod(idx, 4)
            grid.addWidget(check, row, col)

        button_row = QHBoxLayout()
        select_all = QPushButton("Select All")
        select_all.clicked.connect(lambda: self._set_checks(True))
        button_row.addWidget(select_all)
        clear_all = QPushButton("Clear")
        clear_all.clicked.connect(lambda: self._set_checks(False))
        button_row.addWidget(clear_all)
        button_row.addStretch()

        wrapper = QWidget()
        wrapper.setLayout(button_row)
        grid.addWidget(wrapper, (len(bodies) // 4) + 1, 0, 1, 4)
        return group

    def _build_action_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.addStretch()
        self.generate_button = QPushButton("Compute Positions")
        self.generate_button.clicked.connect(self._generate)
        row.addWidget(self.generate_button)
        return row

    def _build_table(self) -> QTableWidget:
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Body", "RA (HMS)", "Dec (DMS)", "Distance (AU)"])
        header = self.table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
        return self.table

    # ------------------------------------------------------------------
    def _set_checks(self, checked: bool) -> None:
        for box in self._body_checks:
            box.setChecked(checked)

    def _generate(self) -> None:
        if not self._service:
            QMessageBox.warning(self, "Unavailable", self._service_error or "Tychos service is unavailable.")
            return

        selected = [box.text() for box in self._body_checks if box.isChecked()]
        if not selected:
            QMessageBox.information(self, "Select Bodies", "Choose at least one body to compute.")
            return

        moment = self.datetime_input.dateTime().toPyDateTime()
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)

        try:
            snapshot = self._service.compute_positions(moment, selected)
        except TychosSkyfieldComputationError as exc:
            QMessageBox.critical(self, "Computation Failed", str(exc))
            self._set_status(str(exc))
            return
        except Exception as exc:  # pragma: no cover - defensive guard
            QMessageBox.critical(self, "Unexpected Error", str(exc))
            self._set_status("Unexpected failure while computing positions.")
            return

        self._populate_table(snapshot)
        self._set_status(f"Computed {len(snapshot.positions)} positions at {snapshot.timestamp.isoformat()}")

    def _populate_table(self, snapshot) -> None:
        self.table.setRowCount(0)
        for entry in snapshot.positions:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(entry.name))
            self.table.setItem(row_idx, 1, QTableWidgetItem(entry.ra_hms))
            self.table.setItem(row_idx, 2, QTableWidgetItem(entry.dec_dms))
            self.table.setItem(row_idx, 3, QTableWidgetItem(f"{entry.distance_au:.4f}"))
        self.table.resizeColumnsToContents()

    def _set_status(self, text: str) -> None:
        self.status_label.setText(text)
