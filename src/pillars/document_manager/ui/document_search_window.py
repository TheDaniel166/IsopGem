"""Document Search Window."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QLabel, QMessageBox, QProgressDialog,
    QComboBox, QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QCoreApplication, QSettings
from PyQt6.QtGui import QFont
from pillars.document_manager.services.document_service import document_service_context

MAX_HISTORY = 10

class DocumentSearchWindow(QMainWindow):
    """Window for advanced document search with highlighting."""
    
    document_opened = pyqtSignal(int, str) # Emits (Document ID, Search Query)
    
    def __init__(self, parent=None):
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
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self._setup_ui()
        
        # Initial focus
        self.search_combo.setFocus()

    def _setup_ui(self):
        layout = QVBoxLayout(self.central_widget)
        
        # Search Bar
        search_layout = QHBoxLayout()
        
        # Editable combo box for search with history dropdown
        self.search_combo = QComboBox()
        self.search_combo.setEditable(True)
        self.search_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.search_combo.setMaxCount(MAX_HISTORY)
        self.search_combo.lineEdit().setPlaceholderText("Enter search terms...")
        self.search_combo.lineEdit().returnPressed.connect(self._perform_search)
        self.search_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.search_combo.setMinimumWidth(300)
        
        # Populate with history
        for term in self.search_history:
            self.search_combo.addItem(term)
        
        search_layout.addWidget(self.search_combo, stretch=1)
        
        self.btn_search = QPushButton("Search")
        self.btn_search.clicked.connect(self._perform_search)
        search_layout.addWidget(self.btn_search)
        
        self.btn_clear_history = QPushButton("Clear History")
        self.btn_clear_history.setToolTip("Clear search history")
        self.btn_clear_history.clicked.connect(self._clear_history)
        search_layout.addWidget(self.btn_clear_history)
        
        self.btn_rebuild = QPushButton("🔧 Rebuild Index")
        self.btn_rebuild.setToolTip("Rebuild search index if results are out of sync")
        self.btn_rebuild.clicked.connect(self._rebuild_index)
        search_layout.addWidget(self.btn_rebuild)
        
        layout.addLayout(search_layout)
        
        # Filter & Sort Row
        filter_sort_layout = QHBoxLayout()
        
        # Filter chips container (scrollable)
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet("font-weight: bold;")
        filter_sort_layout.addWidget(filter_label)
        
        self.filter_scroll = QScrollArea()
        self.filter_scroll.setWidgetResizable(True)
        self.filter_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.filter_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.filter_scroll.setFixedHeight(36)
        self.filter_scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        self.filter_container = QWidget()
        self.filter_chips_layout = QHBoxLayout(self.filter_container)
        self.filter_chips_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_chips_layout.setSpacing(4)
        self.filter_chips_layout.addStretch()
        
        self.filter_scroll.setWidget(self.filter_container)
        filter_sort_layout.addWidget(self.filter_scroll, stretch=1)
        
        # Sort dropdown
        sort_label = QLabel("Sort:")
        sort_label.setStyleSheet("font-weight: bold;")
        filter_sort_layout.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Relevance",
            "Date (Newest)",
            "Date (Oldest)", 
            "Title A-Z",
            "Title Z-A"
        ])
        self.sort_combo.currentIndexChanged.connect(self._apply_sort)
        self.sort_combo.setMinimumWidth(120)
        filter_sort_layout.addWidget(self.sort_combo)
        
        layout.addLayout(filter_sort_layout)
        
        # Help Text
        help_label = QLabel(
            "Tip: Use '*' for wildcards (e.g. 'gem*'), 'AND/OR' for logic, and quotes for phrases."
        )
        help_label.setStyleSheet("color: #666; font-style: italic; font-size: 10pt;")
        layout.addWidget(help_label)
        
        # Results Label (more prominent)
        self.lbl_status = QLabel("Ready")
        status_font = QFont()
        status_font.setPointSize(11)
        status_font.setBold(True)
        self.lbl_status.setFont(status_font)
        self.lbl_status.setStyleSheet("color: #333; padding: 4px;")
        layout.addWidget(self.lbl_status)
        
        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Title", "Snippet", "Created"])
        
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)
        
        # Enable HTML rendering in cells (via delegate or just setting text format? 
        # QTableWidgetItem doesn't support HTML directly easily without a delegate, 
        # but we can use a QLabel as a cell widget for the snippet)
        
        layout.addWidget(self.table)

    def _create_filter_chip(self, text: str, filter_type: str, value: str, is_active: bool = False) -> QPushButton:
        """Create a filter chip button."""
        chip = QPushButton(text)
        chip.setCheckable(True)
        chip.setChecked(is_active)
        chip.setStyleSheet("""
            QPushButton {
                border: 1px solid #ccc;
                border-radius: 12px;
                padding: 4px 10px;
                background: #f5f5f5;
                font-size: 10pt;
            }
            QPushButton:checked {
                background: #4a90d9;
                color: white;
                border-color: #3a7bc8;
            }
            QPushButton:hover {
                background: #e0e0e0;
            }
            QPushButton:checked:hover {
                background: #5a9fe9;
            }
        """)
        chip.clicked.connect(lambda checked, t=filter_type, v=value: self._on_filter_clicked(t, v, checked))
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
            filtered = [r for r in filtered if r.get('collection') == self.active_collection_filter]
        if self.active_type_filter:
            filtered = [r for r in filtered if r.get('file_type') == self.active_type_filter]
        
        # Sort
        sort_idx = self.sort_combo.currentIndex()
        if sort_idx == 0:  # Relevance - keep original order
            pass
        elif sort_idx == 1:  # Date Newest
            filtered.sort(key=lambda r: r.get('created_at') or '', reverse=True)
        elif sort_idx == 2:  # Date Oldest
            filtered.sort(key=lambda r: r.get('created_at') or '')
        elif sort_idx == 3:  # Title A-Z
            filtered.sort(key=lambda r: (r.get('title') or '').lower())
        elif sort_idx == 4:  # Title Z-A
            filtered.sort(key=lambda r: (r.get('title') or '').lower(), reverse=True)
        
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
            snippet_label = QLabel(f"<html><body>{r.get('highlights', '')}</body></html>")
            snippet_label.setWordWrap(True)
            snippet_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            snippet_label.setStyleSheet("padding: 5px;")
            self.table.setCellWidget(row, 1, snippet_label)
            
            # Created
            created_item = QTableWidgetItem(str(r.get('created_at', '')))
            self.table.setItem(row, 2, created_item)
        
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
        query = self.search_combo.currentText().strip()
        if not query:
            return
        
        # Add to history
        self._add_to_history(query)
        
        # Reset filters
        self.active_collection_filter = None
        self.active_type_filter = None
        self.sort_combo.setCurrentIndex(0)  # Reset to relevance
            
        self.lbl_status.setText("Searching...")
        self.table.setRowCount(0)
        
        try:
            with document_service_context() as service:
                results = service.search_documents_with_highlights(query)
            
            # Store results for filtering/sorting
            self.current_results = results
            
            # Update filter chips
            self._update_filter_chips(results)
            
            # Display results
            self._display_results(results)
            
        except Exception as e:
            self.lbl_status.setText(f"Error: {str(e)}")

    def _on_row_double_clicked(self, row, col):
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
