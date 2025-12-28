"""
Chart Picker Dialog - The Saved Chart Selector.
Modal dialog for browsing, filtering, and loading previously saved astrology charts.
"""
from typing import Optional, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QWidget
)
from ..services import ChartStorageService, SavedChartSummary

class ChartPickerDialog(QDialog):
    """Modal selector for saved charts with text, category, and tag filters."""

    def __init__(self, storage: ChartStorageService, parent: Optional[QWidget] = None):
        """
          init   logic.
        
        Args:
            storage: Description of storage.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.storage = storage
        self.selected: Optional[SavedChartSummary] = None
        self._matches: List[SavedChartSummary] = []
        self.setWindowTitle("Select Saved Chart")
        self.resize(720, 540)
        self._build_ui()
        self._refresh_results()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Filters
        filter_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search text (name or location)")
        self.categories_input = QLineEdit()
        self.categories_input.setPlaceholderText("Categories (comma separated)")
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("Tags (comma separated)")
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._refresh_results)

        filter_row.addWidget(self.search_input, 2)
        filter_row.addWidget(self.categories_input, 2)
        filter_row.addWidget(self.tags_input, 2)
        filter_row.addWidget(self.refresh_button, 0)
        layout.addLayout(filter_row)

        # Results table
        self.table = QTableWidget(0, 6)
        headers = ["Name", "Date/Time", "Location", "Categories", "Tags", "Type"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self._accept_selection)
        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            for idx in range(1, 6):
                header.setSectionResizeMode(idx, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table, stretch=1)

        # Action buttons
        button_row = QHBoxLayout()
        button_row.addStretch()
        ok_btn = QPushButton("Load")
        ok_btn.clicked.connect(self._accept_selection)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_row.addWidget(ok_btn)
        button_row.addWidget(cancel_btn)
        layout.addLayout(button_row)

    def _accept_selection(self) -> None:
        row = self.table.currentRow()
        if row < 0 or row >= len(self._matches):
            return
        self.selected = self._matches[row]
        self.accept()

    def _refresh_results(self) -> None:
        text = self.search_input.text().strip()
        categories = self._split_terms(self.categories_input.text())
        tags = self._split_terms(self.tags_input.text())

        if not text and not categories and not tags:
            self._matches = self.storage.list_recent(limit=50)
        else:
            self._matches = self.storage.search(text=text or None, categories=categories or None, tags=tags or None)

        self._populate_table()

    def _populate_table(self) -> None:
        self.table.setRowCount(len(self._matches))
        for row, item in enumerate(self._matches):
            self.table.setItem(row, 0, QTableWidgetItem(item.name))
            self.table.setItem(row, 1, QTableWidgetItem(item.event_timestamp.strftime("%Y-%m-%d %H:%M")))
            self.table.setItem(row, 2, QTableWidgetItem(item.location_label))
            self.table.setItem(row, 3, QTableWidgetItem(", ".join(item.categories)))
            self.table.setItem(row, 4, QTableWidgetItem(", ".join(item.tags)))
            self.table.setItem(row, 5, QTableWidgetItem(item.chart_type))
        self.table.resizeRowsToContents()
        if self._matches:
            self.table.selectRow(0)

    @staticmethod
    def _split_terms(text: str) -> List[str]:
        return [part.strip() for part in text.split(",") if part.strip()]