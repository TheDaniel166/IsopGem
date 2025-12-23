"""Chain Search Results Window - Non-modal window for displaying chain search results."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QLabel, QSpinBox, QComboBox, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Optional, Callable
import logging

from ..services.els_service import ELSSearchService
from ..services import TQGematriaCalculator
from ..models.els_models import ChainResult, ChainSearchSummary

logger = logging.getLogger(__name__)


class ChainResultsWindow(QMainWindow):
    """Non-modal window displaying chain search results with filtering and sorting."""
    
    result_selected = pyqtSignal(list)  # Emits positions for highlighting
    
    def __init__(self, summary: ChainSearchSummary, parent=None):
        super().__init__(parent)
        self._summary = summary
        self._filtered_results: List[ChainResult] = list(summary.results)
        self._calc = TQGematriaCalculator()
        self._term = summary.term
        
        # Calculate gematria for all results
        self._calculate_gematria()
        
        self.setWindowTitle(f"🔗 Chain Search: {summary.term} ({len(summary.results)} paths)")
        self.setMinimumSize(900, 500)
        self.resize(1100, 600)
        
        self._setup_ui()
        self._populate_table()
    
    def _calculate_gematria(self):
        """Calculate gematria for all intervening letters."""
        for result in self._summary.results:
            for step in result.steps:
                if step.intervening_letters:
                    step.intervening_gematria = self._calc.calculate(step.intervening_letters)
    
    def _get_segment_headers(self) -> List[str]:
        """Generate segment column headers like 'A→M', 'M→U', etc."""
        if not self._term or len(self._term) < 2:
            return []
        headers = []
        for i in range(len(self._term) - 1):
            headers.append(f"{self._term[i]}→{self._term[i+1]}")
        return headers
    
    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # === Filter/Sort Controls ===
        controls_group = QGroupBox("🎛️ Filter & Sort")
        controls_layout = QHBoxLayout(controls_group)
        
        # Sort by
        controls_layout.addWidget(QLabel("Sort by:"))
        self._sort_combo = QComboBox()
        self._sort_combo.addItems([
            "Path Length (asc)", "Path Length (desc)",
            "Total Gematria (asc)", "Total Gematria (desc)",
            "Start Position (asc)", "Start Position (desc)"
        ])
        self._sort_combo.currentIndexChanged.connect(self._apply_filters)
        controls_layout.addWidget(self._sort_combo)
        
        controls_layout.addSpacing(20)
        
        # Max path length filter
        controls_layout.addWidget(QLabel("Max Length:"))
        self._max_length_spin = QSpinBox()
        self._max_length_spin.setRange(0, 100000)
        self._max_length_spin.setValue(100000)
        self._max_length_spin.valueChanged.connect(self._apply_filters)
        controls_layout.addWidget(self._max_length_spin)
        
        controls_layout.addStretch()
        
        # Results count
        self._count_label = QLabel(f"Showing: {len(self._filtered_results)}")
        self._count_label.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(self._count_label)
        
        layout.addWidget(controls_group)
        
        # === Results Table ===
        segment_headers = self._get_segment_headers()
        base_headers = ["Start", "Length", "Total Gem"]
        all_headers = base_headers + segment_headers + ["Path"]
        
        self._table = QTableWidget()
        self._table.setColumnCount(len(all_headers))
        self._table.setHorizontalHeaderLabels(all_headers)
        
        # Resize modes
        header = self._table.horizontalHeader()
        for i in range(len(all_headers)):
            if i < 3:  # Start, Length, Total Gem
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            elif i < len(all_headers) - 1:  # Segment columns
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            else:  # Path column
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.cellClicked.connect(self._on_row_clicked)
        layout.addWidget(self._table)
        
        # === Actions ===
        btn_layout = QHBoxLayout()
        
        self._btn_export = QPushButton("📄 Export to Editor")
        self._btn_export.clicked.connect(self._on_export)
        btn_layout.addWidget(self._btn_export)
        
        btn_layout.addStretch()
        
        self._btn_close = QPushButton("Close")
        self._btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self._btn_close)
        
        layout.addLayout(btn_layout)
    
    def _apply_filters(self):
        """Apply filters and sorting to results."""
        max_length = self._max_length_spin.value()
        
        # Filter
        self._filtered_results = [
            r for r in self._summary.results
            if r.total_length <= max_length
        ]
        
        # Sort
        sort_idx = self._sort_combo.currentIndex()
        if sort_idx == 0:  # Path Length asc
            self._filtered_results.sort(key=lambda r: r.total_length)
        elif sort_idx == 1:  # Path Length desc
            self._filtered_results.sort(key=lambda r: r.total_length, reverse=True)
        elif sort_idx == 2:  # Gematria asc
            self._filtered_results.sort(key=lambda r: r.total_gematria)
        elif sort_idx == 3:  # Gematria desc
            self._filtered_results.sort(key=lambda r: r.total_gematria, reverse=True)
        elif sort_idx == 4:  # Start asc
            self._filtered_results.sort(key=lambda r: r.steps[0].position if r.steps else 0)
        elif sort_idx == 5:  # Start desc
            self._filtered_results.sort(key=lambda r: r.steps[0].position if r.steps else 0, reverse=True)
        
        self._populate_table()
    
    def _populate_table(self):
        """Fill table with filtered results."""
        self._table.setRowCount(len(self._filtered_results))
        segment_count = len(self._term) - 1 if self._term else 0
        
        for i, result in enumerate(self._filtered_results):
            col = 0
            
            # Start position
            start_pos = result.steps[0].position if result.steps else 0
            self._table.setItem(i, col, QTableWidgetItem(str(start_pos)))
            col += 1
            
            # Total length
            self._table.setItem(i, col, QTableWidgetItem(str(result.total_length)))
            col += 1
            
            # Total gematria
            self._table.setItem(i, col, QTableWidgetItem(str(result.total_gematria)))
            col += 1
            
            # Segment gematria values
            for j in range(segment_count):
                if j + 1 < len(result.steps):
                    step = result.steps[j + 1]  # +1 because step 0 has no interval
                    self._table.setItem(i, col, QTableWidgetItem(str(step.intervening_gematria)))
                else:
                    self._table.setItem(i, col, QTableWidgetItem("-"))
                col += 1
            
            # Path preview
            path_preview = "".join(s.letter for s in result.steps)
            self._table.setItem(i, col, QTableWidgetItem(path_preview))
        
        self._count_label.setText(f"Showing: {len(self._filtered_results)}")
    
    def _on_row_clicked(self, row: int, col: int):
        """Emit selected result's positions for highlighting."""
        if 0 <= row < len(self._filtered_results):
            result = self._filtered_results[row]
            self.result_selected.emit(result.positions)
    
    def _on_export(self):
        """Export results to Document Editor."""
        # TODO: Implement export
        pass
    
    def set_highlight_callback(self, callback: Callable[[List[int]], None]):
        """Set callback for when a result is selected."""
        self.result_selected.connect(callback)

