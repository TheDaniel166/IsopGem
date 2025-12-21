from PyQt6.QtWidgets import (
    QTreeWidget, QTreeWidgetItem, QMenu, QInputDialog, QMessageBox,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from ..services.notebook_service import notebook_service_context
import logging

logger = logging.getLogger(__name__)

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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("Notebooks")
        self.setColumnCount(1)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        
        # Drag and Drop (Allow moving Pages between sections)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        
        self.itemClicked.connect(self._on_item_clicked)
        self.itemExpanded.connect(self._on_item_expanded)
        
        self.load_tree()

    def load_tree(self):
        """Reload the entire tree structure."""
        self.clear()
        try:
            with notebook_service_context() as svc:
                notebooks = svc.get_notebooks_with_structure()
                for nb in notebooks:
                    self._add_notebook_item(nb)
        except Exception as e:
            logger.error(f"Error loading tree: {e}")

    def _add_notebook_item(self, nb):
        item = QTreeWidgetItem(self)
        item.setText(0, nb.title)
        item.setData(0, Qt.ItemDataRole.UserRole, nb.id)
        item.setData(0, Qt.ItemDataRole.UserRole + 1, self.TYPE_NOTEBOOK)
        item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_DirIcon)) # Folder Icon
        
        # Load Sections
        for section in nb.sections:
            self._add_section_item(item, section)
            
        item.setExpanded(True) # Expand Notebooks by default?

    def _add_section_item(self, parent_item, section):
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

    def _on_item_expanded(self, item: QTreeWidgetItem):
        item_type = item.data(0, Qt.ItemDataRole.UserRole + 1)
        if item_type == self.TYPE_SECTION:
            is_loaded = item.data(0, Qt.ItemDataRole.UserRole + 2)
            if not is_loaded:
                section_id = item.data(0, Qt.ItemDataRole.UserRole)
                self._load_pages(item, section_id)

    def _load_pages(self, section_item, section_id):
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

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        item_type = item.data(0, Qt.ItemDataRole.UserRole + 1)
        if item_type == self.TYPE_PAGE:
            doc_id = item.data(0, Qt.ItemDataRole.UserRole)
            self.page_selected.emit(doc_id)

    def _show_context_menu(self, pos):
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
                del_sec = menu.addAction("Delete Section")
                
                action = menu.exec(self.mapToGlobal(pos))
                if action == new_nb: self._create_notebook()
                elif action == rename: self._rename_item(item, "Section")
                elif action == new_page: self._create_page(item_id, item)
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

    def _create_notebook(self):
        text, ok = QInputDialog.getText(self, "New Notebook", "Title:")
        if ok and text:
            with notebook_service_context() as svc:
                nb = svc.create_notebook(text)
                self._add_notebook_item(nb)

    def _create_section(self, nb_id, nb_item):
        text, ok = QInputDialog.getText(self, "New Section", "Title:")
        if ok and text:
            with notebook_service_context() as svc:
                sec = svc.create_section(nb_id, text)
                self._add_section_item(nb_item, sec)
                nb_item.setExpanded(True)

    def _create_page(self, sec_id, sec_item):
        text, ok = QInputDialog.getText(self, "New Page", "Title:")
        if ok and text:
            with notebook_service_context() as svc:
                page = svc.create_page(sec_id, text)
                
                # Add visually
                p_item = QTreeWidgetItem(sec_item)
                p_item.setText(0, page.title)
                p_item.setData(0, Qt.ItemDataRole.UserRole, page.id)
                p_item.setData(0, Qt.ItemDataRole.UserRole + 1, self.TYPE_PAGE)
                p_item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
                
                sec_item.setExpanded(True)
                # Ensure marked loaded if we just added manually to avoid dupes on expand?
                # Actually if we add manually, we should ensure it was loaded first or just mark loaded.
                sec_item.setData(0, Qt.ItemDataRole.UserRole + 2, True)

    def _delete_item(self, item, type_str):
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


            (item.parent() or self.invisibleRootItem()).removeChild(item)


    def _rename_item(self, item, type_str):
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
    def dropEvent(self, event):
        # Only allow dropping Pages onto Sections
        # Or sorting pages within section
        super().dropEvent(event)
        # Handle logic... (Simplified for now)
