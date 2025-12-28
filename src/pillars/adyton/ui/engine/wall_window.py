"""Dedicated viewer for a single Adyton wall with data grid and CSV export."""
from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QFileDialog,
    QHeaderView,
    QSplitter,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from .opengl_viewport import AdytonGLViewport
from pillars.adyton.services.frustum_color_service import FrustumColorService
from pillars.adyton.ui.frustum_popup import FrustumDetailPopup


PLANET_NAMES = [
    "Sun",
    "Mercury",
    "Moon",
    "Venus",
    "Jupiter",
    "Mars",
    "Saturn",
]


class AdytonWallWindow(QWidget):
    """Displays one wall in isolation with data grid and 3D viewport."""

    def __init__(self, wall_index: int, parent: Optional[QWidget] = None):
        """
          init   logic.
        
        Args:
            wall_index: Description of wall_index.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.wall_index = wall_index
        self.frustum_service: FrustumColorService = FrustumColorService()
        self.table: QTableWidget
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Title
        title = QLabel(self._title_text())
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Splitter for data grid and viewport
        splitter = QSplitter(Qt.Orientation.Vertical)

        # --- Data Grid Section ---
        grid_container = QWidget()
        grid_layout = QVBoxLayout(grid_container)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(4)

        # Button row
        button_row = QHBoxLayout()
        button_row.addStretch()

        export_btn = QPushButton("Export CSV")
        export_btn.setFixedWidth(120)
        export_btn.clicked.connect(self._export_csv)
        button_row.addWidget(export_btn)

        grid_layout.addLayout(button_row)

        # Table widget for decimal values (8 rows × 13 cols)
        self.table = QTableWidget()
        self.table.setRowCount(8)
        self.table.setColumnCount(13)

        # Column headers (1-13)
        self.table.setHorizontalHeaderLabels([str(i + 1) for i in range(13)])
        # Row headers (Row 1-8, bottom to top for visual match)
        self.table.setVerticalHeaderLabels([f"Row {8 - i}" for i in range(8)])

        # Style the table with header guards for type checkers
        h_header = self.table.horizontalHeader()
        v_header = self.table.verticalHeader()
        if h_header is not None:
            h_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        if v_header is not None:
            v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
            v_header.setDefaultSectionSize(28)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ContiguousSelection)

        # Load data
        self._load_data()

        # Connect cell click to popup
        self.table.cellClicked.connect(self._on_cell_clicked)

        grid_layout.addWidget(self.table)
        splitter.addWidget(grid_container)

        # --- 3D Viewport Section ---
        viewport = AdytonGLViewport(wall_index=self.wall_index)
        splitter.addWidget(viewport)

        # Set initial splitter sizes (grid smaller than viewport)
        splitter.setSizes([250, 500])

        layout.addWidget(splitter)

        self.setWindowTitle(self._title_text())
        self.resize(1024, 768)

    def _load_data(self) -> None:
        """Load decimal values from the frustum service into the table."""
        decimals: Optional[List[List[int]]] = self.frustum_service.get_wall_decimals(self.wall_index)

        if not decimals:
            return

        # Display data in same order as source CSV (Row 1 at top)
        for row in range(min(8, len(decimals))):
            row_data = decimals[row]
            for col in range(min(13, len(row_data))):
                item = QTableWidgetItem(str(row_data[col]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)

    def _on_cell_clicked(self, table_row: int, col: int) -> None:
        """Open frustum detail popup when a cell is clicked."""
        # Table row now matches data row directly (no reversal)
        row = table_row

        # Get decimal value from table
        item = self.table.item(table_row, col)
        if item is None:
            return

        try:
            decimal_value = int(item.text())
        except ValueError:
            return

        # Open popup (non-modal)
        popup = FrustumDetailPopup(
            self.wall_index,
            row,
            col,
            decimal_value,
            parent=self,
        )
        popup.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        popup.show()

    def _export_csv(self) -> None:
        """Export the table data to a CSV file."""
        planet = PLANET_NAMES[self.wall_index % len(PLANET_NAMES)]
        default_name = f"wall_{self.wall_index + 1}_{planet.lower()}.csv"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Wall Data",
            default_name,
            "CSV Files (*.csv);;All Files (*)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                # Header row
                f.write(",".join([f"Col {i + 1}" for i in range(13)]) + "\n")

                # Data rows (reversed back to original order for export)
                for table_row in range(8):
                    row_values = []
                    for col in range(13):
                        item = self.table.item(table_row, col)
                        row_values.append(item.text() if item else "0")
                    f.write(",".join(row_values) + "\n")

            QMessageBox.information(
                self,
                "Export Successful",
                f"Wall data exported to:\n{file_path}",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export data:\n{str(e)}",
            )

    def _title_text(self) -> str:
        planet = PLANET_NAMES[self.wall_index % len(PLANET_NAMES)]
        return f"Adyton Wall {self.wall_index + 1} - {planet}"