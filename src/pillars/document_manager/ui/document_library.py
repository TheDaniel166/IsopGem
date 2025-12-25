"""Document Library UI."""
from pathlib import Path
import time
import logging
import zipfile
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QFileDialog, QMessageBox, QAbstractItemView,
    QProgressDialog, QMenu, QTreeWidget, QTreeWidgetItem, QSplitter,
    QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread
from pillars.document_manager.services.document_service import document_service_context
from .document_properties_dialog import DocumentPropertiesDialog
from .import_options_dialog import ImportOptionsDialog

logger = logging.getLogger(__name__)

class SearchWorker(QThread):
    """Background thread for searching documents."""
    results_ready = pyqtSignal(list)
    
    def __init__(self, query, parent=None):
        super().__init__(parent)
        self.query = query
        
    def run(self):
        try:
            with document_service_context() as service:
                # Limit results to 1000 to prevent Jupiter Overload
                docs = service.search_documents(self.query, limit=1000)
                self.results_ready.emit(docs)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            self.results_ready.emit([])

class SortableTableWidgetItem(QTableWidgetItem):
    """
    A QTableWidgetItem that sorts based on a custom key (e.g., number or timestamp)
    rather than the string representation.
    """
    def __init__(self, text, sort_key):
        super().__init__(text)
        self.sort_key = sort_key

    def __lt__(self, other):
        try:
            return self.sort_key < other.sort_key
        except (TypeError, AttributeError):
            # Fallback to standard string comparison if keys are incompatible
            return self.text() < other.text()

class DocumentLibrary(QMainWindow):
    """Window for managing and searching the document database."""
    
    document_opened = pyqtSignal(object, str) # Emits (Document object, restored_html)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("The Akaschic Record")
        self.resize(1000, 700)
        self.all_docs: list = []
        self.is_loading = False
        self._suppress_tree_signal = False
        self.search_worker = None
        
        # Level 0: The Background
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralContainer")
        
        # The Nano Banana Protocol
        import os
        bg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../assets/patterns/document_bg.png"))
        
        # Convert backslashes to forward slashes for CSS if on Windows (safe to do always for URLs)
        bg_path = bg_path.replace("\\", "/")
        
        self.central_widget.setStyleSheet(f"""
            QWidget#CentralContainer {{
                border-image: url("{bg_path}") 0 0 0 0 stretch stretch;
                border: none;
            }}
        """)
        self.setCentralWidget(self.central_widget)
        
        self._setup_ui()
        self.status_label.setText("Consulting the Oracle...")
        QTimer.singleShot(0, self._load_documents)

    def _setup_ui(self):
        # Main Layout (Level 0)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40) # Generous breath
        
        # Level 1: The Floating Panel
        self.panel = QFrame()
        self.panel.setObjectName("FloatingPanel")
        self.panel.setStyleSheet("""
            QFrame#FloatingPanel {
                background-color: #f1f5f9; /* Marble - The harshness of Pure White is banished */
                border: 1px solid #cbd5e1; /* Ash */
                border-radius: 24px;
            }
        """)
        
        # Shadow for Levitational Effect
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40)) # 15% opacity roughly
        self.panel.setGraphicsEffect(shadow)
        
        main_layout.addWidget(self.panel)
        
        # Panel Layout
        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(32, 32, 32, 32)
        panel_layout.setSpacing(24)
        
        # Header Section
        header_layout = QHBoxLayout()
        
        title_label = QLabel("The Akaschic Record")
        title_label.setStyleSheet("""
            font-size: 22pt;
            font-weight: 800;
            color: #0f172a; /* Void */
            border: none;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        panel_layout.addLayout(header_layout)

        # Control Bar
        top_layout = QHBoxLayout()
        top_layout.setSpacing(16)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search the Archives...")
        # The Vessel Style
        self.search_input.setStyleSheet("""
            QLineEdit {
                font-size: 15pt;
                min-height: 50px;
                padding: 0px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                background-color: #ffffff;
                color: #0f172a;
                selection-background-color: #bfdbfe;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)
        self.search_input.returnPressed.connect(self._search_documents)
        top_layout.addWidget(self.search_input, 2) # Give search more space
        
        # ═══════════════════════════════════════════════════════════════════════
        # The Catalyst Styles (Visual Liturgy v2.2 §10)
        # ═══════════════════════════════════════════════════════════════════════
        
        # The Seeker (Gold) — Reveals hidden knowledge
        style_seeker = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
                border: 1px solid #b45309;
                color: #0f172a; /* Void text for clarity */
                font-size: 11pt;
                font-weight: 700;
                border-radius: 8px;
                padding: 0 20px;
                min-height: 48px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fbbf24, stop:1 #f59e0b);
            }
            QPushButton:focus {
                outline: none;
                border: 2px solid #3b82f6; /* Azure focus ring */
            }
            QPushButton:pressed {
                background: #d97706;
            }
            QPushButton:disabled {
                background-color: #fef3c7;
                border: 1px solid #fcd34d;
                color: #92400e;
            }
        """
        
        # The Destroyer (Crimson) — Purges and banishes
        style_destroyer = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #b91c1c);
                border: 1px solid #991b1b;
                color: white;
                font-size: 11pt;
                font-weight: 600;
                border-radius: 8px;
                padding: 0 20px;
                min-height: 48px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f87171, stop:1 #ef4444);
            }
            QPushButton:focus {
                outline: none;
                border: 2px solid #3b82f6;
            }
            QPushButton:pressed {
                background: #b91c1c;
            }
            QPushButton:disabled {
                background-color: #fee2e2;
                border: 1px solid #fca5a5;
                color: #991b1b;
            }
        """
        
        # The Navigator (Void Slate) — Traverses and refreshes
        style_navigator = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #64748b, stop:1 #475569);
                border: 1px solid #334155;
                color: white;
                font-size: 11pt;
                font-weight: 600;
                border-radius: 8px;
                padding: 0 20px;
                min-height: 48px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #94a3b8, stop:1 #64748b);
            }
            QPushButton:focus {
                outline: none;
                border: 2px solid #3b82f6;
            }
            QPushButton:pressed {
                background: #475569;
            }
            QPushButton:disabled {
                background-color: #e2e8f0;
                border: 1px solid #cbd5e1;
                color: #64748b;
            }
        """

        # ═══════════════════════════════════════════════════════════════════════
        # The Catalyst Buttons
        # ═══════════════════════════════════════════════════════════════════════
        
        self.btn_import = QPushButton("Import Document")
        self.btn_import.setObjectName("SeekerButton")
        self.btn_import.setStyleSheet(style_seeker)
        self.btn_import.clicked.connect(self._import_document)
        top_layout.addWidget(self.btn_import)
        
        self.btn_batch = QPushButton("Batch Import")
        self.btn_batch.setObjectName("SeekerButton")
        self.btn_batch.setStyleSheet(style_seeker)
        self.btn_batch.clicked.connect(self._show_batch_menu)
        top_layout.addWidget(self.btn_batch)
        
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setObjectName("DestroyerButton")
        self.btn_delete.setStyleSheet(style_destroyer)
        self.btn_delete.clicked.connect(self._delete_document)
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setObjectName("NavigatorButton")
        self.btn_refresh.setStyleSheet(style_navigator)
        self.btn_refresh.clicked.connect(self._load_documents)
        top_layout.addWidget(self.btn_refresh)
        
        self.btn_purge = QPushButton("Purge")
        self.btn_purge.setObjectName("DestroyerButton")
        self.btn_purge.setStyleSheet(style_destroyer)
        self.btn_purge.clicked.connect(self._purge_database)
        
        panel_layout.addLayout(top_layout)
        
        # Action Bar (Secondary Actions)
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        action_layout.addWidget(self.btn_delete)
        action_layout.addWidget(self.btn_purge)
        panel_layout.addLayout(action_layout)
        
        # Content Area (Splitter)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e2e8f0;
                width: 1px;
            }
        """)
        panel_layout.addWidget(splitter)
        
        # Left: Collections Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Collections")
        self.tree.setMinimumWidth(220)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background-color: #f8fafc;
                font-size: 11pt;
            }
            QTreeWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #475569;
            }
        """)
        self.tree.itemClicked.connect(self._on_collection_selected)
        splitter.addWidget(self.tree)
        
        # Right: Document Table
        self.table = QTableWidget()
        self.table.setColumnCount(5) # ID, Title, Type, Author, Date
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Type", "Author", "Date"])
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                gridline-color: #f1f5f9;
                font-size: 11pt;
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
                background-color: #eff6ff;
                color: #1d4ed8;
            }
        """)
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            header.customContextMenuRequested.connect(self._show_header_menu)
            
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)
        
        # Hide ID column by default (it's internal)
        # self.table.setColumnHidden(0, True) # Keep visible for now per existing behavior
        
        # Context Menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        
        splitter.addWidget(self.table)
        
        # Set initial splitter sizes
        splitter.setSizes([250, 750])
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #64748b; font-size: 10pt; font-weight: 500;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        panel_layout.addWidget(self.status_label)

    def _load_documents(self):
        if self.is_loading:
            return
        self.is_loading = True
        self.status_label.setText("Loading documents...")
        start = time.perf_counter()
        with document_service_context() as service:
            logger.debug("DocumentLibrary: fetching metadata ...")
            # Use metadata-only fetch for performance
            self.all_docs = service.get_all_documents_metadata()
        logger.debug(
            "DocumentLibrary: fetched %s docs in %.1f ms",
            len(self.all_docs),
            (time.perf_counter() - start) * 1000,
        )
        self._populate_tree(self.all_docs)
        self.table.setRowCount(0)
        self.status_label.setText("Select a collection to display documents.")
        self.is_loading = False

    def _populate_tree(self, docs):
        start = time.perf_counter()
        self._suppress_tree_signal = True
        try:
            self.tree.clear()
            
            # All Documents item
            all_item = QTreeWidgetItem(["All Documents"])
            all_item.setData(0, Qt.ItemDataRole.UserRole, None) # None means all
            self.tree.addTopLevelItem(all_item)
            
            # Collect unique collections
            collections = set()
            for doc in docs:
                if doc.collection:
                    collections.add(doc.collection)
            
            # Add collection items
            for collection in sorted(collections):
                item = QTreeWidgetItem([collection])
                item.setData(0, Qt.ItemDataRole.UserRole, collection)
                self.tree.addTopLevelItem(item)
            
            self.tree.clearSelection()
        finally:
            self._suppress_tree_signal = False
        logger.debug(
            "DocumentLibrary: populated tree for %s docs in %.1f ms",
            len(docs),
            (time.perf_counter() - start) * 1000,
        )

    def _on_collection_selected(self, item, column):
        if self._suppress_tree_signal or self.is_loading:
            return
        collection = item.data(0, Qt.ItemDataRole.UserRole)
        if collection is None:
            docs = self.all_docs
        else:
            docs = [d for d in self.all_docs if d.collection == collection]
        self._populate_table(docs)
        self.status_label.setText(
            f"Showing {len(docs)} document(s)" if docs else "No documents in this collection."
        )

    def _search_documents(self, text):
        if text:
            # Search hits DB, so we update all_docs? 
            # Or just display results?
            # Let's just display results and clear tree selection
            start = time.perf_counter()
            with document_service_context() as service:
                docs = service.search_documents(text, limit=50)
            logger.debug(
                "DocumentLibrary: search '%s' returned %s results in %.1f ms",
                text,
                len(docs),
                (time.perf_counter() - start) * 1000,
            )
            self._populate_table(docs)
            self.status_label.setText(f"Search returned {len(docs)} result(s).")
            self.tree.clearSelection()
        else:
            self._load_documents()

    def _populate_table(self, docs):
        start = time.perf_counter()
        
        # Disable sorting during population to improve performance
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        
        # Sort docs by updated_at descending if available, else by id
        # This gives a better default view (newest first)
        try:
            docs.sort(key=lambda d: d.updated_at or datetime.min, reverse=True)
        except:
            pass # Fallback if no updated_at

        from datetime import datetime
        
        for idx, doc in enumerate(docs, start=1):
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # ID: Sort numerically
            id_item = SortableTableWidgetItem(str(doc.id), doc.id)
            id_item.setData(Qt.ItemDataRole.UserRole, doc)
            self.table.setItem(row, 0, id_item)
            
            # Title: Standard sort
            self.table.setItem(row, 1, QTableWidgetItem(doc.title))
            
            # Type: Standard sort
            self.table.setItem(row, 2, QTableWidgetItem(doc.file_type))
            
            # Author: Standard sort
            author_text = doc.author if doc.author else ""
            self.table.setItem(row, 3, QTableWidgetItem(author_text))
            
            # Date: Sort chronologically
            date_text = ""
            sort_val = 0.0
            if doc.updated_at:
                # Nice format: "Oct 12, 2025 14:30"
                date_text = doc.updated_at.strftime("%b %d, %Y %H:%M")
                sort_val = doc.updated_at.timestamp()
                
            date_item = SortableTableWidgetItem(date_text, sort_val)
            self.table.setItem(row, 4, date_item)
            
            if idx % 500 == 0:
                logger.debug(
                    "DocumentLibrary: inserted %s rows (%.1f ms so far)",
                    idx,
                    (time.perf_counter() - start) * 1000,
                )
                
        # Re-enable sorting
        self.table.setSortingEnabled(True)
        
        logger.debug(
            "DocumentLibrary: populated table with %s rows in %.1f ms",
            len(docs),
            (time.perf_counter() - start) * 1000,
        )

    def _show_header_menu(self, position):
        """Show context menu to toggle columns."""
        header = self.table.horizontalHeader()
        menu = QMenu(self)
        
        for col_idx in range(self.table.columnCount()):
            col_name = self.table.horizontalHeaderItem(col_idx).text()
            action = menu.addAction(col_name)
            action.setCheckable(True)
            action.setChecked(not self.table.isColumnHidden(col_idx))
            
            # Use closure to capture loop variable
            def toggle_col(checked, idx=col_idx):
                self.table.setColumnHidden(idx, not checked)
                
            action.triggered.connect(toggle_col)
            
        menu.exec(header.mapToGlobal(position))

    def _show_context_menu(self, position):
        menu = QMenu()
        edit_action = menu.addAction("Properties")
        delete_action = menu.addAction("Delete")
        export_action = menu.addAction("Export as Zip...")
        
        menu.addSeparator()
        
        # Move to Collection submenu
        collection_menu = menu.addMenu("Move to Collection")
        new_coll_action = None
        
        if collection_menu:
            new_coll_action = collection_menu.addAction("New Collection...")
            collection_menu.addSeparator()
            
            # Get existing collections
            collections = sorted({d.collection for d in self.all_docs if d.collection})
            for coll in collections:
                from PyQt6.QtGui import QAction
                action = QAction(str(coll), collection_menu)
                collection_menu.addAction(action)
                action.setData(coll)
        
        viewport = self.table.viewport()
        if viewport is None:
            return
        action = menu.exec(viewport.mapToGlobal(position))
        
        if action == edit_action:
            self._edit_properties()
        elif action == delete_action:
            self._delete_document()
        elif action == export_action:
            self._export_as_zip()
        elif new_coll_action and action == new_coll_action:
            self._move_to_new_collection()
        elif collection_menu and action and action.parent() == collection_menu:
            self._move_to_collection(action.data())

    def _move_to_collection(self, collection_name):
        try:
            selection_model = self.table.selectionModel()
            if not selection_model:
                return
            selected_rows = selection_model.selectedRows()
            if not selected_rows:
                return
            
            # Collect IDs
            doc_ids = []
            for row_idx in selected_rows:
                item = self.table.item(row_idx.row(), 0)
                if item is None:
                    continue
                doc = item.data(Qt.ItemDataRole.UserRole)
                doc_ids.append(doc.id)
            
            if not doc_ids:
                return

            # Show progress dialog for large batches
            if len(doc_ids) > 5:
                progress = QProgressDialog("Moving documents...", None, 0, 0, self)
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setMinimumDuration(0)
                progress.show()
                # Force UI update
                from PyQt6.QtWidgets import QApplication
                QApplication.processEvents()

            with document_service_context() as service:
                service.update_documents(doc_ids, collection=collection_name)
            
            self._load_documents()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to move to collection: {str(e)}")

    def _move_to_new_collection(self):
        try:
            from PyQt6.QtWidgets import QInputDialog
            name, ok = QInputDialog.getText(self, "New Collection", "Collection Name:")
            if ok and name:
                self._move_to_collection(name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create new collection: {str(e)}")

    def _export_as_zip(self):
        try:
            selection_model = self.table.selectionModel()
            if not selection_model:
                return
            selected_rows = selection_model.selectedRows()
            if not selected_rows:
                return
                
            # Collect IDs
            doc_ids = []
            for row_idx in selected_rows:
                item = self.table.item(row_idx.row(), 0)
                if item is None:
                    continue
                doc = item.data(Qt.ItemDataRole.UserRole)
                doc_ids.append(doc.id)
                
            if not doc_ids:
                return
                
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export as Zip", "documents.zip", "Zip Files (*.zip)"
            )
            
            if not file_path:
                return
                
            with document_service_context() as service:
                # Fetch full documents
                docs = service.repo.get_by_ids(doc_ids)
                
                with zipfile.ZipFile(file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for doc in docs:
                        # Construct filename: Title_ID.ext
                        ext = doc.file_type.lower().lstrip('.') if doc.file_type else "txt"
                        if not ext: ext = "txt"
                        
                        safe_title = "".join([c for c in doc.title if c.isalnum() or c in (' ', '-', '_')]).strip()
                        filename = f"{safe_title}_{doc.id}.{ext}"
                        
                        content = doc.raw_content or doc.content or ""
                        zf.writestr(filename, content)
                        
            QMessageBox.information(self, "Success", f"Exported {len(docs)} scrolls to {Path(file_path).name}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")

    def _edit_properties(self):
        selection_model = self.table.selectionModel()
        if not selection_model:
            return
        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return
            
        docs = []
        for row_idx in selected_rows:
            item = self.table.item(row_idx.row(), 0)
            if item is None:
                continue
            docs.append(item.data(Qt.ItemDataRole.UserRole))
        
        dialog = DocumentPropertiesDialog(docs, self)
        if dialog.exec():
            data = dialog.get_data()
            try:
                with document_service_context() as service:
                    # Prepare update args (filter out None)
                    update_args = {k: v for k, v in data.items() if v is not None}
                    
                    if not update_args:
                        return

                    for doc in docs:
                        service.update_document(doc.id, **update_args)
                    
                self._load_documents() # Refresh view
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update properties: {str(e)}")

    def _search_documents(self):
        query = self.search_input.text().strip()
        if not query:
            # If empty, reload all
            self._populate_table(self.all_docs)
            self.status_label.setText(f"Found {len(self.all_docs)} scrolls")
            return
            
        # Cancel existing search
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.terminate()
            self.search_worker.wait()
            
        self.status_label.setText("Searching the threads...")
        self.search_worker = SearchWorker(query)
        self.search_worker.results_ready.connect(self._on_search_results)
        self.search_worker.start()
        
    def _on_search_results(self, results):
        """Handle async search results."""
        self._populate_table(results)
        self.status_label.setText(f"Found {len(results)} matches")

    def _import_document(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Import Document", 
            "", 
            "Documents (*.txt *.html *.docx *.pdf *.rtf)"
        )
        
        if file_path:
            # Get existing collections for the dialog
            collections = sorted({d.collection for d in self.all_docs if d.collection})
            dialog = ImportOptionsDialog(collections, self)
            
            if dialog.exec():
                options = dialog.get_data()
                try:
                    with document_service_context() as service:
                        service.import_document(
                            file_path, 
                            collection=options['collection']
                        )
                    self._load_documents()
                    QMessageBox.information(self, "Success", "Document imported successfully.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Import failed: {str(e)}")

    def _rebuild_index(self):
        reply = QMessageBox.question(
            self,
            "Rebuild Index",
            "Are you sure you want to rebuild the search index? This may take some time.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with document_service_context() as service:
                    service.rebuild_search_index()
                QMessageBox.information(self, "Success", "Search index rebuilt successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to rebuild index: {str(e)}")

    def _show_batch_menu(self):
        menu = QMenu(self)
        
        action_files = menu.addAction("Import Multiple Files...")
        if action_files:
            action_files.triggered.connect(self._batch_import_files)
        
        action_folder = menu.addAction("Import Folder...")
        if action_folder:
            action_folder.triggered.connect(self._batch_import_folder)
            
        menu.addSeparator()
        
        action_rebuild = menu.addAction("Rebuild Search Index")
        if action_rebuild:
            action_rebuild.triggered.connect(self._rebuild_index)
        
        menu.exec(self.btn_batch.mapToGlobal(self.btn_batch.rect().bottomLeft()))

    def _batch_import_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select Documents", 
            "", 
            "Documents (*.txt *.html *.docx *.pdf *.rtf)"
        )
        if files:
            collections = sorted({d.collection for d in self.all_docs if d.collection is not None})
            dialog = ImportOptionsDialog(collections, self)
            if dialog.exec():
                options = dialog.get_data()
                self._process_batch(files, options)

    def _batch_import_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            # Recursively find supported files
            extensions = {'.txt', '.html', '.docx', '.pdf', '.rtf'}
            files = []
            for path in Path(folder).rglob('*'):
                if path.suffix.lower() in extensions:
                    files.append(str(path))
            
            if not files:
                QMessageBox.information(self, "No Files", "No supported documents found in this folder.")
                return
                
            collections = sorted({d.collection for d in self.all_docs if d.collection is not None})
            dialog = ImportOptionsDialog(collections, self)
            if dialog.exec():
                options = dialog.get_data()
                self._process_batch(files, options)

    def _process_batch(self, file_paths, options=None):
        progress = QProgressDialog("Importing documents...", "Cancel", 0, len(file_paths), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        
        succeeded = 0
        failed = 0
        errors = []
        
        with document_service_context() as service:
            for i, file_path in enumerate(file_paths):
                if progress.wasCanceled():
                    break
                    
                progress.setValue(i)
                progress.setLabelText(f"Importing {Path(file_path).name}...")
                
                try:
                    service.import_document(
                        file_path,
                        collection=options.get('collection') or '' if options else ''
                    )
                    succeeded += 1
                except Exception as e:
                    failed += 1
                    errors.append(f"{Path(file_path).name}: {str(e)}")
                
        progress.setValue(len(file_paths))
        
        self._load_documents()
        
        msg = f"Import completed.\nSucceeded: {succeeded}\nFailed: {failed}"
        if errors:
            msg += "\n\nErrors:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                msg += f"\n...and {len(errors)-5} more."
                
        if failed > 0:
            QMessageBox.warning(self, "Batch Import Result", msg)
        else:
            QMessageBox.information(self, "Batch Import Result", msg)

    def _delete_document(self):
        """Delete the currently selected document."""
        selection_model = self.table.selectionModel()
        if not selection_model:
            return
        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a document to delete.")
            return
            
        # Get document ID from the first column of the selected row
        row = selected_rows[0].row()
        item = self.table.item(row, 0)
        if not item:
            return
            
        doc_id = int(item.text())
        title_item = self.table.item(row, 1)
        if not title_item:
            return
        doc_title = title_item.text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{doc_title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                with document_service_context() as service:
                    service.delete_document(doc_id)
                self._load_documents()
                QMessageBox.information(self, "Success", "Document deleted successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete failed: {str(e)}")

    def _purge_database(self):
        """Delete ALL documents from the database."""
        # First confirmation
        reply = QMessageBox.warning(
            self,
            "PURGE DATABASE",
            "WARNING: This will delete ALL documents from the database.\n\nThis action cannot be undone.\n\nAre you absolutely sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Second confirmation
            reply2 = QMessageBox.warning(
                self,
                "FINAL CONFIRMATION",
                "Really delete everything? All data will be lost forever.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply2 == QMessageBox.StandardButton.Yes:
                try:
                    with document_service_context() as service:
                        count = service.delete_all_documents()
                    self._load_documents()
                    QMessageBox.information(self, "Purge Complete", f"Database purged. {count} documents deleted.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Purge failed: {str(e)}")

    def _on_row_double_clicked(self, row, col):
        item = self.table.item(row, 0)
        if item is None:
            return
        
        doc_id = int(item.text())
        
        with document_service_context() as service:
            # Use the new method that restores images
            result = service.get_document_with_images(doc_id)
            if result:
                doc, restored_html = result
                self.document_opened.emit(doc, restored_html)
            else:
                QMessageBox.warning(
                    self,
                    "Document Not Found",
                    f"Document ID {doc_id} was not found in the database."
                )
