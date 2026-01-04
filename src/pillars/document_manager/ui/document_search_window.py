"""Document Search Window."""
import os
import re
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QLabel, QMessageBox, QProgressDialog,
    QComboBox, QFrame, QScrollArea, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QCoreApplication, QSettings, QRunnable, QThreadPool, QObject, pyqtSlot
from PyQt6.QtGui import QFont, QColor
from pillars.document_manager.services.document_service import document_service_context
from shared.ui.catalyst_styles import (
    get_seeker_style, get_navigator_style, get_scribe_style, get_filter_chip_style
)

logger = logging.getLogger(__name__)

MAX_HISTORY = 10


class SearchWorkerSignals(QObject):
    """Signals for SearchWorker to communicate with main thread."""
    finished = pyqtSignal(list)  # Emits search results
    error = pyqtSignal(str)      # Emits error message


class SearchWorker(QRunnable):
    """Background worker for document search to prevent UI freezing."""
    
    def __init__(self, query: str):
        """
          init   logic.
        
        Args:
            query: Description of query.
        
        """
        super().__init__()
        self.query = query
        self.signals = SearchWorkerSignals()
    
    @pyqtSlot()
    def run(self):
        """Execute the search in background thread."""
        try:
            logger.debug(f"SearchWorker: Communing with Archives for '{self.query}'...")
            with document_service_context() as service:
                results = service.search_documents_with_highlights(self.query)
            logger.info(f"SearchWorker: Found {len(results)} documents for '{self.query}'")
            self.signals.finished.emit(results)
        except Exception as e:
            logger.error(f"SearchWorker: Error searching for '{self.query}': {e}")
            self.signals.error.emit(str(e))
class DocumentSearchWindow(QMainWindow):
    """Window for advanced document search with highlighting."""
    
    document_opened = pyqtSignal(int, str) # Emits (Document ID, Search Query)
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Document Search")
        self.resize(900, 700)
        
        # Settings for persistent history
        self.settings = QSettings("IsopGem", "DocumentSearch")
        self.search_history = self.settings.value("search_history", [], type=list)
        
        # Store current results for filtering/sorting
        self.current_results = []
        self.active_collection_filter = None
        self.active_type_filter = None
        
        # Thread pool for background operations
        self.thread_pool = QThreadPool()
        logger.debug(f"DocumentSearchWindow: Thread pool max threads = {self.thread_pool.maxThreadCount()}")
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self._setup_ui()
        
        # Initial focus
        self.search_combo.setFocus()

    def _setup_ui(self):
        """Initialize UI components by delegating to focused sub-methods."""
        self.main_layout = self._setup_substrate()
        self.panel, self.panel_layout = self._setup_floating_panel()  # type: ignore[reportUnknownMemberType]
        self.main_layout.addWidget(self.panel)
        
        self._setup_header(self.panel_layout)
        self._setup_search_bar(self.panel_layout)
        self._setup_filters_and_sort(self.panel_layout)
        self._setup_help_and_status(self.panel_layout)
        self._setup_results_table(self.panel_layout)
    
    def _setup_substrate(self) -> QVBoxLayout:
        # ═══════════════════════════════════════════════════════════════════════
        # Level 0: The Substrate (Visual Liturgy §1)
        # ═══════════════════════════════════════════════════════════════════════
        """Setup the background substrate."""
        bg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../assets/patterns/document_bg.png"))
        bg_path = bg_path.replace("\\", "/")
        
        self.central_widget.setObjectName("SearchSubstrate")
        self.central_widget.setStyleSheet(f"""
            QWidget#SearchSubstrate {{
                border-image: url("{bg_path}") 0 0 0 0 stretch stretch;
                border: none;
            }}
        """)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        return main_layout
    
    def _setup_floating_panel(self) -> tuple:
        # ═══════════════════════════════════════════════════════════════════════
        # Level 1: The Floating Panel (Visual Liturgy §1)
        # ═══════════════════════════════════════════════════════════════════════
        """Setup the floating panel with shadow effect."""
        panel = QFrame()
        panel.setObjectName("FloatingPanel")
        panel.setStyleSheet("""
            QFrame#FloatingPanel {
                background-color: #f1f5f9; /* Marble */
                border: 1px solid #cbd5e1; /* Ash */
                border-radius: 24px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 25))
        panel.setGraphicsEffect(shadow)
        
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(32, 32, 32, 32)
        panel_layout.setSpacing(24)
        
        return panel, panel_layout
    
    def _setup_header(self, parent_layout: QVBoxLayout):
        # ═══════════════════════════════════════════════════════════════════════
        # The Header
        # ═══════════════════════════════════════════════════════════════════════
        """Setup the header with title."""
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Document Search")
        title_label.setStyleSheet("""
            font-size: 22pt;
            font-weight: 800;
            color: #0f172a; /* Void */
            border: none;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)
    
    def _setup_search_bar(self, parent_layout: QVBoxLayout):
        # ═══════════════════════════════════════════════════════════════════════
        # The Vessel (Search Bar)
        # ═══════════════════════════════════════════════════════════════════════
        """Setup the search input and action buttons."""
        search_layout = QHBoxLayout()
        search_layout.setSpacing(16)
        
        # Editable combo box for search with history dropdown
        self.search_combo = QComboBox()
        self.search_combo.setEditable(True)
        self.search_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.search_combo.setMaxCount(MAX_HISTORY)
        self.search_combo.lineEdit().setPlaceholderText("Search the Archives...")
        self.search_combo.lineEdit().returnPressed.connect(self._perform_search)
        self.search_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.search_combo.setMinimumWidth(400)
        self.search_combo.setStyleSheet("""
            QComboBox {
                font-size: 15pt;
                min-height: 50px;
                padding: 0px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                background-color: #ffffff;
                color: #0f172a;
            }
            QComboBox:focus {
                border: 2px solid #3b82f6;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 16px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #64748b;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                selection-background-color: #ede9fe;
                selection-color: #8b5cf6;
            }
        """)
        
        # Populate with history
        for term in self.search_history:
            self.search_combo.addItem(term)
        
        search_layout.addWidget(self.search_combo, stretch=1)
        
        # Action buttons (using shared Catalyst styles)
        height_override = "min-height: 50px;"
        
        self.btn_search = QPushButton("🔍 Search")
        self.btn_search.setObjectName("SeekerButton")
        self.btn_search.setStyleSheet(get_seeker_style().replace("min-height: 48px;", height_override))
        self.btn_search.clicked.connect(self._perform_search)
        search_layout.addWidget(self.btn_search)
        
        self.btn_clear_history = QPushButton("Clear History")
        self.btn_clear_history.setObjectName("NavigatorButton")
        self.btn_clear_history.setStyleSheet(get_navigator_style().replace("min-height: 48px;", height_override))
        self.btn_clear_history.setToolTip("Clear search history")
        self.btn_clear_history.clicked.connect(self._clear_history)
        search_layout.addWidget(self.btn_clear_history)
        
        self.btn_rebuild = QPushButton("🔧 Rebuild Index")
        self.btn_rebuild.setObjectName("ScribeButton")
        self.btn_rebuild.setStyleSheet(get_scribe_style().replace("min-height: 48px;", height_override))
        self.btn_rebuild.setToolTip("Rebuild search index if results are out of sync")
        self.btn_rebuild.clicked.connect(self._rebuild_index)
        search_layout.addWidget(self.btn_rebuild)
        
        parent_layout.addLayout(search_layout)
    
    def _setup_filters_and_sort(self, parent_layout: QVBoxLayout):
        # ═══════════════════════════════════════════════════════════════════════
        # Filter & Sort Row
        # ═══════════════════════════════════════════════════════════════════════
        """Setup the filter chips area and sort dropdown."""
        filter_sort_layout = QHBoxLayout()
        
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet("font-weight: bold; color: #334155;")
        filter_sort_layout.addWidget(filter_label)
        
        self.filter_scroll = QScrollArea()
        self.filter_scroll.setWidgetResizable(True)
        self.filter_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.filter_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.filter_scroll.setFixedHeight(52)
        self.filter_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.filter_scroll.setStyleSheet("background: transparent;")
        
        self.filter_container = QWidget()
        self.filter_chips_layout = QHBoxLayout(self.filter_container)
        self.filter_chips_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_chips_layout.setSpacing(8)
        self.filter_chips_layout.addStretch()
        
        self.filter_scroll.setWidget(self.filter_container)
        filter_sort_layout.addWidget(self.filter_scroll, stretch=1)
        
        # Sort dropdown
        sort_label = QLabel("Sort:")
        sort_label.setStyleSheet("font-weight: bold; color: #334155;")
        filter_sort_layout.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Relevance",
            "Date (Newest)",
            "Date (Oldest)", 
            "Title A-Z",
            "Title Z-A"
        ])
        self.sort_combo.setStyleSheet("""
            QComboBox {
                font-size: 11pt;
                min-height: 36px;
                padding: 0px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                background-color: #ffffff;
                color: #0f172a;
            }
            QComboBox:focus {
                border: 2px solid #3b82f6;
            }
        """)
        self.sort_combo.currentIndexChanged.connect(self._apply_sort)
        self.sort_combo.setMinimumWidth(140)
        filter_sort_layout.addWidget(self.sort_combo)
        
        parent_layout.addLayout(filter_sort_layout)
    
    def _setup_help_and_status(self, parent_layout: QVBoxLayout):
        # ═══════════════════════════════════════════════════════════════════════
        # The Whisper (Help & Status)
        # ═══════════════════════════════════════════════════════════════════════
        """Setup help text and status label."""
        help_label = QLabel(
            "Tip: Use '*' for wildcards (e.g. 'gem*'), 'AND/OR' for logic, and quotes for phrases."
        )
        help_label.setStyleSheet("color: #64748b; font-style: italic; font-size: 10pt;")
        parent_layout.addWidget(help_label)
        
        self.lbl_status = QLabel("Awaiting your intent, Magus.")
        status_font = QFont()
        status_font.setPointSize(11)
        status_font.setBold(True)
        self.lbl_status.setFont(status_font)
        self.lbl_status.setStyleSheet("color: #475569; padding: 4px 0;")
        parent_layout.addWidget(self.lbl_status)
    
    def _setup_results_table(self, parent_layout: QVBoxLayout):
        # ═══════════════════════════════════════════════════════════════════════
        # The Results Table
        # ═══════════════════════════════════════════════════════════════════════
        """Setup the results table with columns and styling."""
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Title", "Snippet", "Hits", "Created"])
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
                font-size: 11pt;
                background-color: #ffffff;
            }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: 700;
                color: #475569;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f5f9;
            }
            QTableWidget::item:selected {
                background-color: #ede9fe;
                color: #6d28d9;
            }
        """)
        
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Title
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)            # Snippet
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Hits
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Created
            
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)
        
        parent_layout.addWidget(self.table)

    def _create_filter_chip(self, text: str, filter_type: str, value: str, is_active: bool = False) -> QPushButton:
        """Create a filter chip button."""
        chip = QPushButton(text)
        chip.setCheckable(True)
        chip.setChecked(is_active)
        chip.setStyleSheet(get_filter_chip_style())
        chip.clicked.connect(lambda checked, t=filter_type, v=value: self._on_filter_clicked(t, v, checked))  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
        return chip
    
    def _update_filter_chips(self, results: list):
        """Update filter chips based on available collections and file types in results."""
        # Clear existing chips
        while self.filter_chips_layout.count() > 1:  # Keep the stretch
            item = self.filter_chips_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not results:
            return
        
        # Collect unique collections and file types
        collections = set()
        file_types = set()
        for r in results:
            if r.get('collection'):
                collections.add(r['collection'])
            if r.get('file_type'):
                file_types.add(r['file_type'])
        
        # Add "All" chip first
        all_chip = self._create_filter_chip(
            "All", "all", "all", 
            self.active_collection_filter is None and self.active_type_filter is None
        )
        self.filter_chips_layout.insertWidget(0, all_chip)
        
        idx = 1
        
        # Add collection chips
        for coll in sorted(collections):
            chip = self._create_filter_chip(
                f"📁 {coll}", "collection", coll,
                self.active_collection_filter == coll
            )
            self.filter_chips_layout.insertWidget(idx, chip)
            idx += 1
        
        # Add file type chips  
        for ft in sorted(file_types):
            chip = self._create_filter_chip(
                f"📄 {ft.upper()}", "type", ft,
                self.active_type_filter == ft
            )
            self.filter_chips_layout.insertWidget(idx, chip)
            idx += 1
    
    def _on_filter_clicked(self, filter_type: str, value: str, checked: bool):
        """Handle filter chip click."""
        if filter_type == "all":
            self.active_collection_filter = None
            self.active_type_filter = None
        elif filter_type == "collection":
            self.active_collection_filter = value if checked else None
            self.active_type_filter = None  # Clear other filter
        elif filter_type == "type":
            self.active_type_filter = value if checked else None
            self.active_collection_filter = None  # Clear other filter
        
        self._apply_filters_and_sort()
    
    def _apply_sort(self):
        """Apply current sort option."""
        self._apply_filters_and_sort()
    
    def _apply_filters_and_sort(self):
        """Apply current filters and sort to results."""
        if not self.current_results:
            return
        
        # Filter
        filtered = self.current_results[:]
        if self.active_collection_filter:
            filtered = [r for r in filtered if r.get('collection') == self.active_collection_filter]  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        if self.active_type_filter:
            filtered = [r for r in filtered if r.get('file_type') == self.active_type_filter]  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        
        # Sort
        sort_idx = self.sort_combo.currentIndex()
        if sort_idx == 0:  # Relevance - keep original order
            pass
        elif sort_idx == 1:  # Date Newest
            filtered.sort(key=lambda r: r.get('created_at') or '', reverse=True)  # type: ignore[reportUnknownLambdaType, reportUnknownMemberType]
        elif sort_idx == 2:  # Date Oldest
            filtered.sort(key=lambda r: r.get('created_at') or '')  # type: ignore[reportUnknownLambdaType, reportUnknownMemberType]
        elif sort_idx == 3:  # Title A-Z
            filtered.sort(key=lambda r: (r.get('title') or '').lower())  # type: ignore[reportUnknownLambdaType, reportUnknownMemberType]
        elif sort_idx == 4:  # Title Z-A
            filtered.sort(key=lambda r: (r.get('title') or '').lower(), reverse=True)  # type: ignore[reportUnknownLambdaType, reportUnknownMemberType]
        
        # Update display
        self._display_results(filtered)
        
        # Update filter chips to reflect current state
        self._update_filter_chips(self.current_results)
    
    def _display_results(self, results: list):
        """Display results in the table."""
        self.table.setRowCount(0)
        
        for r in results:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Title
            title_item = QTableWidgetItem(r['title'])
            title_item.setData(Qt.ItemDataRole.UserRole, r['id'])
            self.table.setItem(row, 0, title_item)
            
            # Snippet (using QLabel for HTML support)
            highlights = r.get('highlights', '')
            snippet_label = QLabel(f"<html><body>{highlights}</body></html>")
            snippet_label.setWordWrap(True)
            snippet_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            snippet_label.setStyleSheet("padding: 5px;")
            self.table.setCellWidget(row, 1, snippet_label)
            
            # Hits - use pre-calculated hit_count from search repository (counts full document)
            hit_count = r.get('hit_count', 0)
            
            if hit_count > 0:
                hits_label = QLabel(f"<span style='background:#fef3c7; color:#92400e; padding:2px 8px; border-radius:10px; font-weight:600;'>{hit_count}</span>")
                hits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setCellWidget(row, 2, hits_label)
            else:
                self.table.setItem(row, 2, QTableWidgetItem(""))
            
            # Created (shifted to column 3)
            created_item = QTableWidgetItem(str(r.get('created_at', '')))
            self.table.setItem(row, 3, created_item)
        
        self.table.resizeRowsToContents()
        
        # Update status with count
        total = len(self.current_results)
        showing = len(results)
        if showing == total:
            self.lbl_status.setText(f"Found {total} document{'s' if total != 1 else ''}")
        else:
            self.lbl_status.setText(f"Showing {showing} of {total} document{'s' if total != 1 else ''}")

    def _add_to_history(self, term: str):
        """Add a search term to history (most recent first, max 10)."""
        # Remove if already exists (to move it to front)
        if term in self.search_history:
            self.search_history.remove(term)
        
        # Insert at front
        self.search_history.insert(0, term)
        
        # Limit to MAX_HISTORY
        self.search_history = self.search_history[:MAX_HISTORY]
        
        # Update combo box
        self.search_combo.clear()
        for t in self.search_history:
            self.search_combo.addItem(t)
        
        # Save to settings
        self.settings.setValue("search_history", self.search_history)
    
    def _clear_history(self):
        """Clear the search history."""
        self.search_history = []
        self.search_combo.clear()
        self.settings.setValue("search_history", [])
        self.lbl_status.setText("Search history cleared.")

    def _perform_search(self):
        """Initiate search operation in background thread."""
        query = self.search_combo.currentText().strip()
        if not query:
            return
        
        # Add to history
        self._add_to_history(query)
        
        # Reset filters
        self.active_collection_filter = None
        self.active_type_filter = None
        self.sort_combo.setCurrentIndex(0)  # Reset to relevance
        
        # Update UI for search in progress
        self.lbl_status.setText("Communing with the Archives...")
        self.table.setRowCount(0)
        self.btn_search.setEnabled(False)  # Prevent double-clicks
        
        # Dispatch to background thread
        worker = SearchWorker(query)
        worker.signals.finished.connect(self._on_search_complete)
        worker.signals.error.connect(self._on_search_error)
        self.thread_pool.start(worker)
        logger.debug(f"_perform_search: Dispatched worker for '{query}'")
    
    def _on_search_complete(self, results: list):
        """Handle search completion from worker thread."""
        self.btn_search.setEnabled(True)
        
        # Store results for filtering/sorting
        self.current_results = results
        
        # Update filter chips
        self._update_filter_chips(results)
        
        # Display results
        self._display_results(results)
        
        logger.info(f"_on_search_complete: Displayed {len(results)} results")
    
    def _on_search_error(self, error_message: str):
        """Handle search error from worker thread."""
        self.btn_search.setEnabled(True)
        self.lbl_status.setText(f"The Archives remain silent: {error_message}")
        logger.error(f"_on_search_error: {error_message}")

    def _on_row_double_clicked(self, row, col):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        item = self.table.item(row, 0)
        if item is None:
            return
        
        doc_id = item.data(Qt.ItemDataRole.UserRole)
        query = self.search_combo.currentText().strip()
        self.document_opened.emit(doc_id, query)

    def _rebuild_index(self):
        """Rebuild the search index from database."""
        reply = QMessageBox.question(
            self,
            "Rebuild Index",
            "This will rebuild the search index from the database.\n"
            "This fixes issues where search results don't match actual documents.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        progress = QProgressDialog("Rebuilding search index...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        QCoreApplication.processEvents()
        
        try:
            with document_service_context() as service:
                service.rebuild_search_index()
            progress.close()
            QMessageBox.information(self, "Success", "Search index rebuilt successfully.")
            # Clear current results
            self.table.setRowCount(0)
            self.lbl_status.setText("Index rebuilt. Search again.")
        except Exception as e:
            progress.close()
            QMessageBox.critical(self, "Error", f"Failed to rebuild index: {str(e)}")