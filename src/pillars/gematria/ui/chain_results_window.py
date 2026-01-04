"""Chain Search Results Window - Non-modal window for displaying chain search results."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QLabel, QSpinBox, QComboBox, QGroupBox, QLineEdit, QDialog, QTextBrowser
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
    
    def __init__(self, summary: ChainSearchSummary, window_manager=None, parent=None):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """
          init   logic.
        
        Args:
            summary: Description of summary.
            window_manager: Description of window_manager.
            parent: Description of parent.
        
        """
        super().__init__(None) # Independent window
        self.window_manager = window_manager
        self._summary = summary
        self._filtered_results: List[ChainResult] = list(summary.results)
        self._calc = TQGematriaCalculator()
        self._term = summary.term
        
        # Pagination
        self._page_size = 200
        self._current_page = 0
        
        # Calculate gematria for all results
        self._calculate_gematria()
        
        self.setWindowTitle(f"🔗 Chain Search: {summary.term} ({len(summary.results)} paths)")
        self.setMinimumSize(900, 500)
        self.resize(1100, 600)
        
        self._setup_ui()
        self._populate_table()
    
    def _calculate_gematria(self):
        """Calculate gematria for all intervening letters and pre-compute row data."""
        segment_count = len(self._term) - 1 if self._term else 0
        
        for result in self._summary.results:
            # Calculate gematria
            for step in result.steps:
                if step.intervening_letters:
                    step.intervening_gematria = self._calc.calculate(step.intervening_letters)
            
            # Pre-compute display row (tuple of strings for fast table population)
            start_pos = result.steps[0].position if result.steps else 0
            row_data = [str(start_pos), str(result.total_length), str(result.total_gematria)]
            
            for j in range(segment_count):
                if j + 1 < len(result.steps):
                    row_data.append(str(result.steps[j + 1].intervening_gematria))
                else:
                    row_data.append("-")
            
            row_data.append("".join(s.letter for s in result.steps))
            result._row_data = tuple(row_data)  # Cache for fast access
    
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
        
        # Gematria filter
        controls_layout.addSpacing(10)
        controls_layout.addWidget(QLabel("Gematria:"))
        self._gematria_filter = QLineEdit()
        self._gematria_filter.setPlaceholderText("e.g. 93")
        self._gematria_filter.setFixedWidth(60)
        self._gematria_filter.textChanged.connect(self._apply_filters)
        controls_layout.addWidget(self._gematria_filter)
        
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
        
        # === Pagination Controls ===
        page_layout = QHBoxLayout()
        
        self._btn_prev = QPushButton("◀ Prev")
        self._btn_prev.clicked.connect(self._prev_page)
        page_layout.addWidget(self._btn_prev)
        
        self._page_label = QLabel("Page 1 of 1")
        self._page_label.setStyleSheet("font-weight: bold; padding: 0 10px;")
        page_layout.addWidget(self._page_label)
        
        self._btn_next = QPushButton("Next ▶")
        self._btn_next.clicked.connect(self._next_page)
        page_layout.addWidget(self._btn_next)
        
        page_layout.addStretch()
        layout.addLayout(page_layout)
        
        # === Actions ===
        btn_layout = QHBoxLayout()
        
        self._btn_export = QPushButton("📄 Export to Editor")
        self._btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_export.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
                color: white;
                border: 1px solid #059669;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #047857);
            }
        """)
        self._btn_export.clicked.connect(self._on_export)
        btn_layout.addWidget(self._btn_export)
        
        self._btn_stats = QPushButton("📊 Statistics")
        self._btn_stats.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_stats.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
                color: white;
                border: 1px solid #d97706;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #b45309);
            }
        """)
        self._btn_stats.clicked.connect(self._on_show_statistics)
        btn_layout.addWidget(self._btn_stats)
        
        btn_layout.addStretch()
        
        self._btn_close = QPushButton("Close")
        self._btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_close.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #e2e8f0;
                color: #334155;
            }
        """)
        self._btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self._btn_close)
        
        layout.addLayout(btn_layout)
    
    def _prev_page(self):
        if self._current_page > 0:
            self._current_page -= 1
            self._populate_table()
    
    def _next_page(self):
        total_pages = max(1, (len(self._filtered_results) + self._page_size - 1) // self._page_size)
        if self._current_page < total_pages - 1:
            self._current_page += 1
            self._populate_table()
    def _apply_filters(self):
        """Apply filters and sorting to results."""
        max_length = self._max_length_spin.value()
        
        # Parse gematria filter
        gematria_target = None
        gematria_text = self._gematria_filter.text().strip()
        if gematria_text:
            try:
                gematria_target = int(gematria_text)
            except ValueError:
                pass  # Invalid input, ignore filter
        
        # Filter by max length
        self._filtered_results = [
            r for r in self._summary.results
            if r.total_length <= max_length
        ]
        
        # Filter by gematria if specified
        if gematria_target is not None:
            self._filtered_results = [
                r for r in self._filtered_results
                if r.total_gematria == gematria_target
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
        
        # Reset to first page on filter/sort change
        self._current_page = 0
        self._populate_table()
        
    def _populate_table(self):
        """Fill table with current page of results using pre-cached row data."""
        # Calculate pagination
        total_results = len(self._filtered_results)
        total_pages = max(1, (total_results + self._page_size - 1) // self._page_size)
        start_idx = self._current_page * self._page_size
        end_idx = min(start_idx + self._page_size, total_results)
        page_results = self._filtered_results[start_idx:end_idx]
        
        # Disable all updates and signals for speed
        self._table.blockSignals(True)
        self._table.setUpdatesEnabled(False)
        self._table.setSortingEnabled(False)
        
        try:
            # Clear and resize to page size only
            self._table.clearContents()
            self._table.setRowCount(len(page_results))
            
            # Use pre-computed row data for speed
            for i, result in enumerate(page_results):
                if hasattr(result, '_row_data'):
                    for col, value in enumerate(result._row_data):  # type: ignore  # 4 errors
                        self._table.setItem(i, col, QTableWidgetItem(value))
                else:
                    # Fallback for any results without cached data
                    start_pos = result.steps[0].position if result.steps else 0
                    self._table.setItem(i, 0, QTableWidgetItem(str(start_pos)))
                    self._table.setItem(i, 1, QTableWidgetItem(str(result.total_length)))
                    self._table.setItem(i, 2, QTableWidgetItem(str(result.total_gematria)))
        finally:
            self._table.setUpdatesEnabled(True)
            self._table.blockSignals(False)
        
        # Update labels
        self._count_label.setText(f"Total: {total_results} | Showing: {start_idx + 1}-{end_idx}")
        self._page_label.setText(f"Page {self._current_page + 1} of {total_pages}")
        
        # Update button states
        self._btn_prev.setEnabled(self._current_page > 0)
        self._btn_next.setEnabled(self._current_page < total_pages - 1)
    
    def _on_row_clicked(self, row: int, col: int):
        """Emit selected result's positions for highlighting."""
        # Convert page row to filtered results index
        idx = self._current_page * self._page_size + row
        if 0 <= idx < len(self._filtered_results):
            result = self._filtered_results[idx]
            self.result_selected.emit(result.positions)
    
    def _on_export(self):
        """Export results to Document Editor."""
        if not self.window_manager:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Window Manager not available.")
            return

        # Generate HTML report
        html = f"""
        <h1>🔗 Chain Search Report</h1>
        <h2>Term: {self._term}</h2>
        <p><b>Found:</b> {len(self._filtered_results)} paths</p>
        <hr>
        <table border='1' cellspacing='0' cellpadding='5' style='border-collapse: collapse; width: 100%;'>
            <thead>
                <tr style='background-color: #f2f2f2;'>
                    <th>Start</th>
                    <th>Length</th>
                    <th>Total Gem</th>
                    <th>Path Steps & Intervening Intervals</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for result in self._filtered_results:
            path_desc = ""
            for i, step in enumerate(result.steps):
                path_desc += f"<b>{step.letter}</b>" 
                if i < len(result.steps) - 1:
                    next_step = result.steps[i+1]
                    interval = abs(next_step.position - step.position)
                    path_desc += f" --({interval})--> "
            
            start_pos = result.steps[0].position if result.steps else 0
            
            html += f"""
            <tr>
                <td>{start_pos}</td>
                <td>{result.total_length}</td>
                <td>{result.total_gematria}</td>
                <td>{path_desc}</td>
            </tr>
            """
            
        html += """
            </tbody>
        </table>
        """

        from shared.signals.navigation_bus import navigation_bus
        
        # Requests editor via bus
        navigation_bus.request_window.emit(
            "document_editor", 
            {"allow_multiple": True, "window_manager": self.window_manager}
        )
        
        # Finding the window we just opened is tricky with allow_multiple=True
        # because the ID is generated.
        # However, for document editor, we usually want to passing content via params 
        # is cleaner if the target supports it. 
        # But DocumentEditorWindow constructor signature: __init__(self, window_manager=None, parent=None)
        # So we have to find it.
        
        # Strategy: Get the most highly numbered document_editor window
        count = self.window_manager._window_counters.get("document_editor", 0)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        win_id = f"document_editor_{count}"
        editor_window = self.window_manager.get_window(win_id)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        
        if editor_window and hasattr(editor_window, 'editor'):
            editor_window.setWindowTitle(f"chain Report - {self._term}")
            editor_window.editor.set_html(html)
            editor_window.is_modified = True
            editor_window.show()
    
    def _on_show_statistics(self):
        """Show statistical analysis dialog."""
        results = self._filtered_results if self._filtered_results else self._summary.results
        
        if not results:
            return
        
        # Calculate statistics
        total_count = len(results)
        
        # Path length stats
        lengths = [r.total_length for r in results]
        min_len = min(lengths)
        max_len = max(lengths)
        avg_len = sum(lengths) / len(lengths)
        
        # Gematria stats
        gematria_values = [r.total_gematria for r in results]
        min_gem = min(gematria_values)
        max_gem = max(gematria_values)
        avg_gem = sum(gematria_values) / len(gematria_values)
        
        # Gematria frequency distribution (top 10)
        gem_freq = {}
        for g in gematria_values:
            gem_freq[g] = gem_freq.get(g, 0) + 1
        top_gematria = sorted(gem_freq.items(), key=lambda x: -x[1])[:10]  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType, reportUnknownVariableType]
        
        # Interval analysis - first intervals
        first_intervals = [r.steps[1].interval for r in results if len(r.steps) > 1]
        if first_intervals:
            avg_first_interval = sum(first_intervals) / len(first_intervals)
            min_first = min(first_intervals)
            max_first = max(first_intervals)
        else:
            avg_first_interval = min_first = max_first = 0
        
        # Build HTML report
        html = f"""
        <h2>📊 Chain Search Statistics</h2>
        <h3>Term: {self._term}</h3>
        <hr>
        
        <h4>📈 Summary</h4>
        <table border='1' cellpadding='5'>
        <tr><td>Total Paths</td><td><b>{total_count}</b></td></tr>
        </table>
        
        <h4>📏 Path Length</h4>
        <table border='1' cellpadding='5'>
        <tr><td>Minimum</td><td>{min_len}</td></tr>
        <tr><td>Maximum</td><td>{max_len}</td></tr>
        <tr><td>Average</td><td>{avg_len:.1f}</td></tr>
        </table>
        
        <h4>🔢 Gematria Values</h4>
        <table border='1' cellpadding='5'>
        <tr><td>Minimum</td><td>{min_gem}</td></tr>
        <tr><td>Maximum</td><td>{max_gem}</td></tr>
        <tr><td>Average</td><td>{avg_gem:.1f}</td></tr>
        </table>
        
        <h4>⚡ First Interval ({self._term[0]}→{self._term[1] if len(self._term) > 1 else '-'})</h4>
        <table border='1' cellpadding='5'>
        <tr><td>Minimum</td><td>{min_first}</td></tr>
        <tr><td>Maximum</td><td>{max_first}</td></tr>
        <tr><td>Average</td><td>{avg_first_interval:.1f}</td></tr>
        </table>
        
        <h4>🎯 Most Common Gematria Values</h4>
        <table border='1' cellpadding='5'>
        <tr><th>Value</th><th>Count</th></tr>
        """
        for val, count in top_gematria:
            html += f"<tr><td>{val}</td><td>{count}</td></tr>"
        html += "</table>"
        
        # Show dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("📊 Statistics")
        dialog.resize(400, 500)
        
        layout = QVBoxLayout(dialog)
        browser = QTextBrowser()
        browser.setHtml(html)
        layout.addWidget(browser)
        
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dialog.close)
        layout.addWidget(btn_close)
        
        dialog.exec()
    
    def set_highlight_callback(self, callback: Callable[[List[int]], None]):
        """Set callback for when a result is selected."""
        self.result_selected.connect(callback)
