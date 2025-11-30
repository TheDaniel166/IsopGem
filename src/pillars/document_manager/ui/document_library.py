"""Document Library UI."""
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QFileDialog, QMessageBox, QAbstractItemView,
    QProgressDialog, QMenu, QTreeWidget, QTreeWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from shared.database import get_db
from pillars.document_manager.services.document_service import DocumentService
from .document_properties_dialog import DocumentPropertiesDialog
from .import_options_dialog import ImportOptionsDialog

class DocumentLibrary(QMainWindow):
    """Window for managing and searching the document database."""
    
    document_opened = pyqtSignal(object) # Emits Document object
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Document Library")
        self.resize(800, 600)
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self._setup_ui()
        self._load_documents()

    def _setup_ui(self):
        layout = QVBoxLayout(self.central_widget)
        
        # Top Bar
        top_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search documents...")
        self.search_input.textChanged.connect(self._search_documents)
        top_layout.addWidget(self.search_input)
        
        self.btn_import = QPushButton("Import Document")
        self.btn_import.clicked.connect(self._import_document)
        top_layout.addWidget(self.btn_import)
        
        self.btn_batch = QPushButton("Batch Import")
        self.btn_batch.clicked.connect(self._show_batch_menu)
        top_layout.addWidget(self.btn_batch)
        
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self._delete_document)
        top_layout.addWidget(self.btn_delete)
        
        self.btn_purge = QPushButton("Purge All")
        self.btn_purge.setStyleSheet("background-color: #ffcccc; color: #cc0000;") # Light red warning style
        self.btn_purge.clicked.connect(self._purge_database)
        top_layout.addWidget(self.btn_purge)
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.clicked.connect(self._load_documents)
        top_layout.addWidget(self.btn_refresh)
        
        layout.addLayout(top_layout)
        
        # Main Content (Splitter)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left: Collections Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Collections")
        self.tree.setMinimumWidth(200)
        self.tree.itemClicked.connect(self._on_collection_selected)
        splitter.addWidget(self.tree)
        
        # Right: Document Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Title", "Type", "Tags", "Created"])
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)
        
        # Context Menu
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        
        splitter.addWidget(self.table)
        
        # Set initial splitter sizes
        splitter.setSizes([200, 600])

    def _get_service(self):
        # Helper to get service with a fresh session
        # In a real app, we might manage session lifecycle differently
        db = next(get_db())
        return DocumentService(db)

    def _load_documents(self):
        service = self._get_service()
        # Use metadata-only fetch for performance
        self.all_docs = service.get_all_documents_metadata()
        self._populate_tree(self.all_docs)
        self._populate_table(self.all_docs)

    def _populate_tree(self, docs):
        self.tree.clear()
        
        # All Documents item
        all_item = QTreeWidgetItem(["All Documents"])
        all_item.setData(0, Qt.ItemDataRole.UserRole, None) # None means all
        self.tree.addTopLevelItem(all_item)
        
        # Collect unique collections
        collections = set()
        for doc in docs:
            if doc.collection is not None:
                collections.add(doc.collection)
        
        # Add collection items
        for collection in sorted(collections):
            item = QTreeWidgetItem([collection])
            item.setData(0, Qt.ItemDataRole.UserRole, collection)
            self.tree.addTopLevelItem(item)
            
        all_item.setSelected(True)

    def _on_collection_selected(self, item, column):
        collection = item.data(0, Qt.ItemDataRole.UserRole)
        if collection is None:
            self._populate_table(self.all_docs)
        else:
            filtered = [d for d in self.all_docs if d.collection == collection]
            self._populate_table(filtered)

    def _search_documents(self, text):
        service = self._get_service()
        if text:
            # Search hits DB, so we update all_docs? 
            # Or just display results?
            # Let's just display results and clear tree selection
            docs = service.search_documents(text, limit=50)
            self._populate_table(docs)
            self.tree.clearSelection()
        else:
            self._load_documents()

    def _populate_table(self, docs):
        self.table.setRowCount(0)
        for doc in docs:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            id_item = QTableWidgetItem(str(doc.id))
            id_item.setData(Qt.ItemDataRole.UserRole, doc)
            self.table.setItem(row, 0, id_item)
            
            self.table.setItem(row, 1, QTableWidgetItem(doc.title))
            self.table.setItem(row, 2, QTableWidgetItem(doc.file_type))
            self.table.setItem(row, 3, QTableWidgetItem(doc.tags or ""))
            self.table.setItem(row, 4, QTableWidgetItem(str(doc.created_at)))

    def _show_context_menu(self, position):
        menu = QMenu()
        edit_action = menu.addAction("Properties")
        add_tags_action = menu.addAction("Add Tags...")
        delete_action = menu.addAction("Delete")
        
        menu.addSeparator()
        
        # Add to Collection submenu
        collection_menu = menu.addMenu("Move to Collection")
        new_coll_action = None
        
        if collection_menu:
            new_coll_action = collection_menu.addAction("New Collection...")
            collection_menu.addSeparator()
            
            # Get existing collections
            collections = sorted({d.collection for d in self.all_docs if d.collection is not None})
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
        elif action == add_tags_action:
            self._add_tags_to_selection()
        elif action == delete_action:
            self._delete_document()
        elif new_coll_action and action == new_coll_action:
            self._move_to_new_collection()
        elif collection_menu and action and action.parent() == collection_menu:
            self._move_to_collection(action.data())

    def _add_tags_to_selection(self):
        selection_model = self.table.selectionModel()
        if not selection_model:
            return
        selected_rows = selection_model.selectedRows()
        if not selected_rows:
            return

        from PyQt6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, "Add Tags", "Tags (comma separated):")
        if ok and text:
            new_tags = [t.strip() for t in text.split(',') if t.strip()]
            if not new_tags:
                return

            service = self._get_service()
            for row_idx in selected_rows:
                item = self.table.item(row_idx.row(), 0)
                if item is None:
                    continue
                doc = item.data(Qt.ItemDataRole.UserRole)
                
                current_tags = set()
                if doc.tags:
                    current_tags = {t.strip() for t in doc.tags.split(',') if t.strip()}
                
                current_tags.update(new_tags)
                updated_tags_str = ", ".join(sorted(current_tags))
                
                try:
                    service.update_document(doc.id, tags=updated_tags_str)
                except Exception as e:
                    print(f"Error updating tags for doc {doc.id}: {e}")
            
            self._load_documents()

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

            service = self._get_service()
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
                service = self._get_service()
                
                # Prepare update args (filter out None)
                update_args = {k: v for k, v in data.items() if v is not None}
                
                if not update_args:
                    return

                for doc in docs:
                    service.update_document(doc.id, **update_args)
                    
                self._load_documents() # Refresh view
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update properties: {str(e)}")

    def _import_document(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Import Document", 
            "", 
            "Documents (*.txt *.html *.docx *.pdf *.rtf)"
        )
        
        if file_path:
            # Get existing collections for the dialog
            collections = sorted({d.collection for d in self.all_docs if d.collection is not None})
            dialog = ImportOptionsDialog(collections, self)
            
            if dialog.exec():
                options = dialog.get_data()
                try:
                    service = self._get_service()
                    service.import_document(
                        file_path, 
                        tags=options['tags'] or '', 
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
                service = self._get_service()
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
        
        service = self._get_service()
        succeeded = 0
        failed = 0
        errors = []
        
        for i, file_path in enumerate(file_paths):
            if progress.wasCanceled():
                break
                
            progress.setValue(i)
            progress.setLabelText(f"Importing {Path(file_path).name}...")
            
            try:
                service.import_document(
                    file_path,
                    tags=options['tags'] if options and options['tags'] else '',
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
                service = self._get_service()
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
                    service = self._get_service()
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
        
        service = self._get_service()
        doc = service.get_document(doc_id)
        
        if doc:
            self.document_opened.emit(doc)
