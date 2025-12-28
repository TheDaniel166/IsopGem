"""Wall Analytics Window - 3D table view with summation analysis."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QMenu,
    QHeaderView,
)

from ..services.frustum_color_service import FrustumColorService


WALL_NAMES = ["Sun", "Mercury", "Moon", "Venus", "Jupiter", "Mars", "Saturn"]
WALL_FILES = [
    "sun_wall.csv",
    "mercury_wall.csv",
    "luna_wall.csv",
    "venus_wall.csv",
    "jupiter_wall.csv",
    "mars_wall.csv",
    "saturn_wall.csv",
]


class WallAnalyticsWindow(QMainWindow):
    """Analytics window showing wall data with row, column, and z-axis sums."""

    def __init__(self, window_manager=None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.window_manager = window_manager
        self.wall_data: List[List[List[int]]] = []  # 7 walls × 8 rows × 13 cols
        
        self._load_all_walls()
        self._setup_ui()

    def _load_all_walls(self) -> None:
        """Load data from all 7 wall CSV files."""
        service = FrustumColorService()
        for wall_idx in range(7):
            data = service.get_wall_decimals(wall_idx)
            self.wall_data.append(data)

    def _setup_ui(self) -> None:
        """Set up the UI with tabbed interface."""
        self.setWindowTitle("Wall Analytics - 3D Data Cube")
        self.setMinimumSize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("Wall Analytics")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Add individual wall tabs
        for wall_idx, name in enumerate(WALL_NAMES):
            tab = self._create_wall_tab(wall_idx)
            self.tabs.addTab(tab, name)

        # Add Z-Axis Sums tab
        z_tab = self._create_zaxis_tab()
        self.tabs.addTab(z_tab, "Z-Axis Sums")

        # Add Cross-Wall Rows tab
        cross_tab = self._create_cross_wall_rows_tab()
        self.tabs.addTab(cross_tab, "Cross-Wall Rows")

        # Add Wall Totals tab
        totals_tab = self._create_wall_totals_tab()
        self.tabs.addTab(totals_tab, "Wall Totals")

    def _create_wall_tab(self, wall_idx: int) -> QWidget:
        """Create a tab showing one wall's 8×13 grid with row/column sums."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 8 rows × 13 cols + 1 sum column + 1 sum row = 9×14 table
        table = QTableWidget(9, 14)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(
            lambda pos, t=table: self._show_context_menu(t, pos)
        )

        # Headers
        col_headers = [f"C{i+1}" for i in range(13)] + ["Row Sum"]
        row_headers = [f"R{i+1}" for i in range(8)] + ["Col Sum"]
        table.setHorizontalHeaderLabels(col_headers)
        table.setVerticalHeaderLabels(row_headers)

        data = self.wall_data[wall_idx]
        
        # Fill data and calculate row sums
        for row_idx in range(8):
            row_sum = 0
            for col_idx in range(13):
                val = data[row_idx][col_idx] if row_idx < len(data) and col_idx < len(data[row_idx]) else 0
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row_idx, col_idx, item)
                row_sum += val
            # Row sum
            sum_item = QTableWidgetItem(str(row_sum))
            sum_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            sum_item.setBackground(Qt.GlobalColor.lightGray)
            table.setItem(row_idx, 13, sum_item)

        # Calculate and fill column sums
        for col_idx in range(13):
            col_sum = sum(data[r][col_idx] for r in range(8) if r < len(data) and col_idx < len(data[r]))
            item = QTableWidgetItem(str(col_sum))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setBackground(Qt.GlobalColor.lightGray)
            table.setItem(8, col_idx, item)

        # Grand total (sum of all)
        grand_total = sum(sum(row) for row in data)
        total_item = QTableWidgetItem(str(grand_total))
        total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        total_item.setBackground(Qt.GlobalColor.darkGray)
        total_item.setForeground(Qt.GlobalColor.white)
        table.setItem(8, 13, total_item)

        # Resize columns
        header = table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(table)
        return tab

    def _create_zaxis_tab(self) -> QWidget:
        """Create tab showing sum of each position across all 7 walls."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        desc = QLabel("Sum of each (row, col) position across all 7 walls")
        desc.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc)

        table = QTableWidget(8, 13)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(
            lambda pos, t=table: self._show_context_menu(t, pos)
        )

        col_headers = [f"C{i+1}" for i in range(13)]
        row_headers = [f"R{i+1}" for i in range(8)]
        table.setHorizontalHeaderLabels(col_headers)
        table.setVerticalHeaderLabels(row_headers)

        for row_idx in range(8):
            for col_idx in range(13):
                z_sum = sum(
                    self.wall_data[w][row_idx][col_idx]
                    for w in range(7)
                    if row_idx < len(self.wall_data[w]) and col_idx < len(self.wall_data[w][row_idx])
                )
                item = QTableWidgetItem(str(z_sum))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row_idx, col_idx, item)

        header = table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(table)
        return tab

    def _create_cross_wall_rows_tab(self) -> QWidget:
        """Create tab showing sum of each row across all 7 walls."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        desc = QLabel("Sum of each row (1-8) across all 7 walls")
        desc.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc)

        # 8 rows × 7 walls + total column
        table = QTableWidget(8, 8)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(
            lambda pos, t=table: self._show_context_menu(t, pos)
        )

        col_headers = WALL_NAMES + ["Total"]
        row_headers = [f"Row {i+1}" for i in range(8)]
        table.setHorizontalHeaderLabels(col_headers)
        table.setVerticalHeaderLabels(row_headers)

        for row_idx in range(8):
            row_total = 0
            for wall_idx in range(7):
                row_sum = sum(self.wall_data[wall_idx][row_idx]) if row_idx < len(self.wall_data[wall_idx]) else 0
                item = QTableWidgetItem(str(row_sum))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row_idx, wall_idx, item)
                row_total += row_sum
            
            # Total across all walls for this row
            total_item = QTableWidgetItem(str(row_total))
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            total_item.setBackground(Qt.GlobalColor.lightGray)
            table.setItem(row_idx, 7, total_item)

        header = table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(table)
        return tab

    def _create_wall_totals_tab(self) -> QWidget:
        """Create tab showing grand totals per wall."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        desc = QLabel("Grand total of all values per wall")
        desc.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(desc)

        table = QTableWidget(7, 2)
        table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(
            lambda pos, t=table: self._show_context_menu(t, pos)
        )

        table.setHorizontalHeaderLabels(["Wall", "Total"])
        table.verticalHeader().setVisible(False)

        grand_total = 0
        for wall_idx, name in enumerate(WALL_NAMES):
            wall_total = sum(sum(row) for row in self.wall_data[wall_idx])
            grand_total += wall_total

            name_item = QTableWidgetItem(name)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(wall_idx, 0, name_item)

            total_item = QTableWidgetItem(str(wall_total))
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(wall_idx, 1, total_item)

        # Add grand total row
        table.setRowCount(8)
        grand_name = QTableWidgetItem("GRAND TOTAL")
        grand_name.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        grand_name.setBackground(Qt.GlobalColor.darkGray)
        grand_name.setForeground(Qt.GlobalColor.white)
        table.setItem(7, 0, grand_name)

        grand_val = QTableWidgetItem(str(grand_total))
        grand_val.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        grand_val.setBackground(Qt.GlobalColor.darkGray)
        grand_val.setForeground(Qt.GlobalColor.white)
        table.setItem(7, 1, grand_val)

        header = table.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(table)
        return tab

    def _show_context_menu(self, table: QTableWidget, position) -> None:
        """Show right-click context menu with Send to Quadset option."""
        item = table.itemAt(position)
        if not item:
            return

        try:
            value = int(item.text())
        except ValueError:
            return

        menu = QMenu(table)
        menu.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                color: #0f172a;
                border: 1px solid #cbd5e1;
                padding: 4px 0px;
            }
            QMenu::item {
                padding: 6px 16px;
            }
            QMenu::item:selected {
                background-color: #e0e7ff;
                color: #1d4ed8;
            }
        """)

        send_action = QAction("Send to Quadset Analysis", menu)
        send_action.triggered.connect(lambda: self._send_to_quadset(value))
        if not self.window_manager:
            send_action.setEnabled(False)
        menu.addAction(send_action)

        viewport = table.viewport()
        if viewport:
            menu.exec(viewport.mapToGlobal(position))

    def _send_to_quadset(self, value: int) -> None:
        """Open Quadset Analysis window with the given value."""
        if not self.window_manager:
            return

        from shared.signals.navigation_bus import navigation_bus
        
        # Open via NavigationBus with initial value
        navigation_bus.request_window.emit(
            "tq_quadset_analysis",
            {"window_manager": self.window_manager, "initial_value": value}
        )
