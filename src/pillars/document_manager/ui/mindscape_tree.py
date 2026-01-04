"""
Mindscape Tree - The Notebook Sidebar.
Hierarchical tree widget for Notebooks, Sections, and Pages navigation.
"""
from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog, QMessageBox,
    QAbstractItemView, QFileDialog, QProgressDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QObject, QRunnable, QThreadPool, pyqtSlot
from PyQt6.QtGui import QDropEvent
from ..services.notebook_service import notebook_service_context
from typing import Optional, Any
import logging
from ..services.document_service import document_service_context

logger = logging.getLogger(__name__)

class ImportWorkerSignals(QObject):
    """Signals for ImportWorker."""
    finished = pyqtSignal(int) # document_id
    error = pyqtSignal(str)

class ImportWorker(QRunnable):
    """Background worker for parsing documents."""
    def __init__(self, filepath: str):
        """
          init   logic.
        
        Args:
            filepath: Description of filepath.
        
        """
        super().__init__()
        self.filepath = filepath
        self.signals = ImportWorkerSignals()
        
    @pyqtSlot()
    def run(self):
        """
        Execute logic.
        
        """
        try:
            # Transmute via DocumentService (handles images, duplicates, indexing)
            with document_service_context() as svc:
                doc = svc.import_document(self.filepath)
                self.signals.finished.emit(doc.id)
        except Exception as e:
            self.signals.error.emit(str(e))



class MindscapeTreeWidget(QTreeWidget):
    """
    Hierarchical sidebar for Notebooks -> Sections -> Pages.
    Mimics OneNote structure.
    """
    page_selected = pyqtSignal(int)  # Emits document_id
    
    # Item Types
    TYPE_NOTEBOOK = 1
    TYPE_SECTION = 2
    TYPE_PAGE = 3
    
    def __init__(self, parent: Optional[Any] = None) -> None:
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        Returns:
            Result of __init__ operation.
        """
        super().__init__(parent)
        self.setHeaderLabel("Notebooks")
        self.setColumnCount(1)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        # Thread Pool for imports
        self.thread_pool = QThreadPool()
        self.progress_dialog = None
        
        # Drag and Drop (Allow moving Pages between sections)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        
        self.itemClicked.connect(self._on_item_clicked)
        self.itemExpanded.connect(self._on_item_expanded)
        
        self.load_tree()

    def load_tree(self) -> None:
        """Reload the entire tree structure."""
        self.clear()
        try:
            with notebook_service_context() as svc:
                notebooks = svc.get_notebooks_with_structure()
                for nb in notebooks:
                    self._add_notebook_item(nb)
        except Exception as e:
            logger.error(f"Error loading tree: {e}")

    def _add_notebook_item(self, nb: Any) -> QTreeWidgetItem:
        item = QTreeWidgetItem(self)
        item.setText(0, nb.title)
        item.setData(0, Qt.ItemDataRole.UserRole, nb.id)
        item.setData(0, Qt.ItemDataRole.UserRole + 1, self.TYPE_NOTEBOOK)
        item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_DirIcon)) # Folder Icon
        
        # Load Sections
        for section in nb.sections:
            self._add_section_item(item, section)
            
        item.setExpanded(True) # Expand Notebooks by default?
        return item

    def _add_section_item(self, parent_item: QTreeWidgetItem, section: Any) -> QTreeWidgetItem:
        item = QTreeWidgetItem(parent_item)
        item.setText(0, section.title)
        item.setData(0, Qt.ItemDataRole.UserRole, section.id)
        item.setData(0, Qt.ItemDataRole.UserRole + 1, self.TYPE_SECTION)
        # Tab/Section Icon
        
        # Lazy load pages? Or eager? 
        # Typically Sections have 10-50 pages. Eager is fine.
        # But we need to fetch them. The 'nb.sections' might not have eager loaded pages unless configured.
        # In 'get_notebooks_with_structure', we only options(joinedload(Notebook.sections)).
        # We didn't join pages.
        # We can lazy load on expand.
        item.setChildIndicatorPolicy(QTreeWidgetItem.ChildIndicatorPolicy.ShowIndicator)
        item.setData(0, Qt.ItemDataRole.UserRole + 2, False) # Pages Loaded?
        return item

    def _on_item_expanded(self, item: QTreeWidgetItem) -> None:
        item_type = item.data(0, Qt.ItemDataRole.UserRole + 1)
        if item_type == self.TYPE_SECTION:
            is_loaded = item.data(0, Qt.ItemDataRole.UserRole + 2)
            if not is_loaded:
                section_id = item.data(0, Qt.ItemDataRole.UserRole)
                self._load_pages(item, section_id)

    def _load_pages(self, section_item: QTreeWidgetItem, section_id: int) -> None:
        # Clear dummy children if any (none added yet)
        try:
            with notebook_service_context() as svc:
                pages = svc.get_section_pages(section_id)
                for p in pages:
                    p_item = QTreeWidgetItem(section_item)
                    p_item.setText(0, p.title)
                    p_item.setData(0, Qt.ItemDataRole.UserRole, p.id)
                    p_item.setData(0, Qt.ItemDataRole.UserRole + 1, self.TYPE_PAGE)
                    p_item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
                    
            section_item.setData(0, Qt.ItemDataRole.UserRole + 2, True)
        except Exception as e:
            logger.error(f"Error loading pages: {e}")

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        item_type = item.data(0, Qt.ItemDataRole.UserRole + 1)
        if item_type == self.TYPE_PAGE:
            doc_id = item.data(0, Qt.ItemDataRole.UserRole)
            self.page_selected.emit(doc_id)

    def _show_context_menu(self, pos: QPoint) -> None:
        item = self.itemAt(pos)
        menu = QMenu(self)
        
        # General Actions
        new_nb = menu.addAction("New Notebook")
        
        if item:
            item_type = item.data(0, Qt.ItemDataRole.UserRole + 1)
            item_id = item.data(0, Qt.ItemDataRole.UserRole)
            
            menu.addSeparator()
            
            if item_type == self.TYPE_NOTEBOOK:
                rename = menu.addAction("Rename Notebook")
                new_sec = menu.addAction("New Section")
                del_nb = menu.addAction("Delete Notebook")
                
                action = menu.exec(self.mapToGlobal(pos))
                if action == new_nb: self._create_notebook()
                elif action == rename: self._rename_item(item, "Notebook")
                elif action == new_sec: self._create_section(item_id, item)
                elif action == del_nb: self._delete_item(item, "notebook")
                
            elif item_type == self.TYPE_SECTION:
                rename = menu.addAction("Rename Section")
                new_page = menu.addAction("New Page")
                link_lib = menu.addAction("Link from Library...")
                import_page = menu.addAction("Import Page...")
                del_sec = menu.addAction("Delete Section")
                
                action = menu.exec(self.mapToGlobal(pos))
                if action == new_nb: self._create_notebook()
                elif action == rename: self._rename_item(item, "Section")
                elif action == new_page: self._create_page(item_id, item)
                elif action == link_lib: self._link_from_library(item_id, item)
                elif action == import_page: self._import_page(item_id, item)
                elif action == del_sec: self._delete_item(item, "section")
                
            elif item_type == self.TYPE_PAGE:
                rename = menu.addAction("Rename Page")
                del_page = menu.addAction("Delete Page")
                
                action = menu.exec(self.mapToGlobal(pos))
                if action == new_nb: self._create_notebook()
                elif action == rename: self._rename_item(item, "Page")
                elif action == del_page: self._delete_item(item, "page")
        else:
            # Blank space click
            action = menu.exec(self.mapToGlobal(pos))
            if action == new_nb: self._create_notebook()

    def _create_notebook(self) -> None:
        text, ok = QInputDialog.getText(self, "New Notebook", "Title:")
        if ok and text:
            with notebook_service_context() as svc:
                nb = svc.create_notebook(text)
                self._add_notebook_item(nb)

    def _create_section(self, nb_id: int, nb_item: QTreeWidgetItem) -> None:
        text, ok = QInputDialog.getText(self, "New Section", "Title:")
        if ok and text:
            with notebook_service_context() as svc:
                sec = svc.create_section(nb_id, text)
                self._add_section_item(nb_item, sec)
                nb_item.setExpanded(True)

    def _create_page(self, sec_id: int, sec_item: QTreeWidgetItem) -> None:
        text, ok = QInputDialog.getText(self, "New Page", "Title:")
        if ok and text:
            with notebook_service_context() as svc:
                page = svc.create_page(sec_id, text)
                
                # If pages weren't loaded yet, load them first (but exclude the new page
                # since it's about to be added manually)
                is_loaded = sec_item.data(0, Qt.ItemDataRole.UserRole + 2)
                if not is_loaded:
                    # Load existing pages (the new one is already in DB, so filter it out)
                    existing_pages = svc.get_section_pages(sec_id)
                    for p in existing_pages:
                        if p.id != page.id:  # Skip the page we just created
                            p_item = QTreeWidgetItem(sec_item)
                            p_item.setText(0, p.title)
                            p_item.setData(0, Qt.ItemDataRole.UserRole, p.id)
                            p_item.setData(0, Qt.ItemDataRole.UserRole + 1, self.TYPE_PAGE)
                            p_item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
                
                # Mark as loaded BEFORE expanding to prevent double loading
                sec_item.setData(0, Qt.ItemDataRole.UserRole + 2, True)
                
                # Add the new page visually
                p_item = QTreeWidgetItem(sec_item)
                p_item.setText(0, page.title)
                p_item.setData(0, Qt.ItemDataRole.UserRole, page.id)
                p_item.setData(0, Qt.ItemDataRole.UserRole + 1, self.TYPE_PAGE)
                p_item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
                
                sec_item.setExpanded(True)

    def _import_page(self, sec_id: int, sec_item: QTreeWidgetItem) -> None:
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Import Document", "", "Documents (*.txt *.md *.html *.pdf *.docx);;All Files (*)"
        )
        
        if not filepath:
            return
            
        # Show Progress Dialog
        self.progress_dialog = QProgressDialog("Transmuting Document...", None, 0, 0, self)
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.show()
        
        # Start Worker
        worker = ImportWorker(filepath)
        worker.signals.finished.connect(lambda doc_id: self._on_import_finished(doc_id, sec_id, sec_item))  # type: ignore[reportUnknownArgumentType, reportUnknownLambdaType]
        worker.signals.error.connect(self._on_import_error)
        self.thread_pool.start(worker)

    def _link_from_library(self, sec_id: int, sec_item: QTreeWidgetItem) -> None:
        """Open dialog to select un-filed documents to link to this section."""
        from PyQt6.QtWidgets import QDialog, QListWidget, QVBoxLayout, QDialogButtonBox, QLabel, QListWidgetItem
        
        # Use existing docs?
        dialog = QDialog(self)
        dialog.setWindowTitle("Link from Library")
        dialog.resize(500, 600)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Select document(s) to add to this section:"))
        
        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        layout.addWidget(list_widget)
        
        # Determine valid candidates: docs without section_id
        candidates = []
        try:
            with notebook_service_context() as svc:
                # Direct SQL query via session for orphans
                from pillars.document_manager.models.document import Document
                candidates = (
                    svc.db.query(Document)
                    .filter(Document.section_id == None)
                    .order_by(Document.updated_at.desc())
                    .all()
                )
                logger.debug(f"LinkFromLibrary: Found {len(candidates)} orphan documents.")
        except Exception as e:
            logger.error(f"LinkFromLibrary: Error fetching candidates: {e}")
            QMessageBox.warning(self, "Error", f"Could not fetch candidates: {str(e)}")
            return

        for doc in candidates:
            # Format: 'Title (ID: 123)' for clarity
            label = f"{doc.title} (ID: {doc.id})"
            item = QListWidgetItem(label)
            item.setToolTip(f"ID: {doc.id} | Type: {doc.file_type}\nPath: {doc.file_path}")
            item.setData(Qt.ItemDataRole.UserRole, doc.id)
            list_widget.addItem(item)
            
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec():
            selected_items = list_widget.selectedItems()
            logger.debug(f"LinkFromLibrary: User selected {len(selected_items)} items.")
            
            if not selected_items:
                return
            
            for item in selected_items:
                doc_id = item.data(Qt.ItemDataRole.UserRole)
                logger.debug(f"LinkFromLibrary: Adopting Doc ID {doc_id} into Section {sec_id}")
                self._on_import_finished(doc_id, sec_id, sec_item)

    def _on_import_finished(self, doc_id: int, sec_id: int, sec_item: QTreeWidgetItem) -> None:
        """Handle successful import on main thread."""
        if self.progress_dialog:
            self.progress_dialog.close()
            
        try:
            with notebook_service_context() as svc:
                # Adopt the document into the section
                # This wraps content in JSON if needed and updates linkage
                page = svc.adopt_document(doc_id, sec_id)
                
                # --- Visual Update Logic ---
                is_loaded = sec_item.data(0, Qt.ItemDataRole.UserRole + 2)
                if not is_loaded:
                    existing_pages = svc.get_section_pages(sec_id)
                    for p in existing_pages:
                        if p.id != page.id:
                            p_item = QTreeWidgetItem(sec_item)
                            p_item.setText(0, p.title)
                            p_item.setData(0, Qt.ItemDataRole.UserRole, p.id)
                            p_item.setData(0, Qt.ItemDataRole.UserRole + 1, self.TYPE_PAGE)
                            p_item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
                
                sec_item.setData(0, Qt.ItemDataRole.UserRole + 2, True)
                
                p_item = QTreeWidgetItem(sec_item)
                p_item.setText(0, page.title)
                p_item.setData(0, Qt.ItemDataRole.UserRole, page.id)
                p_item.setData(0, Qt.ItemDataRole.UserRole + 1, self.TYPE_PAGE)
                p_item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
                
                sec_item.setExpanded(True)
                
        except Exception as e:
            QMessageBox.critical(self, "Import Processing Error", str(e))

    def _on_import_error(self, error_msg: str) -> None:
        if self.progress_dialog:
            self.progress_dialog.close()
        QMessageBox.critical(self, "Import Error", f"Failed to ingest document: {error_msg}")

    def _delete_item(self, item: QTreeWidgetItem, type_str: str) -> None:
        item_id = item.data(0, Qt.ItemDataRole.UserRole)
        confirm = QMessageBox.question(self, "Delete", f"Delete this {type_str}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            with notebook_service_context() as svc:
                if type_str == "notebook": svc.delete_notebook(item_id)
                elif type_str == "section": svc.delete_section(item_id)
                elif type_str == "page": 
                    svc.delete_page(item_id)
            
            # Remove visual item
            (item.parent() or self.invisibleRootItem()).removeChild(item)



    def _rename_item(self, item: QTreeWidgetItem, type_str: str) -> None:
        current_name = item.text(0)
        item_id = item.data(0, Qt.ItemDataRole.UserRole)
        
        text, ok = QInputDialog.getText(self, f"Rename {type_str}", "New Title:", text=current_name)
        if ok and text and text != current_name:
            with notebook_service_context() as svc:
                if type_str == "Notebook":
                    svc.rename_notebook(item_id, text)
                elif type_str == "Section":
                    svc.rename_section(item_id, text)
                elif type_str == "Page":
                    svc.rename_page(item_id, text)
            
            # Update UI
            item.setText(0, text)

    # Drag Drop
    def dropEvent(self, event: QDropEvent) -> None:
        # Only allow dropping Pages onto Sections
        # Or sorting pages within section
        """
        Dropevent logic.
        
        Args:
            event: Description of event.
        
        Returns:
            Result of dropEvent operation.
        """
        super().dropEvent(event)
        # Handle logic... (Simplified for now)