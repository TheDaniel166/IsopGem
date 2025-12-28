"""
Document Selector - The Archive Picker.
Dialog for selecting documents from the repository with filter support.
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QListWidget, QListWidgetItem, QLineEdit)
from PyQt6.QtCore import Qt

class DocumentSelectorDialog(QDialog):
    """Simple dialog to select a document from the repository."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Document")
        self.resize(500, 400)
        
        self.layout = QVBoxLayout(self)
        
        # Search filter
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Filter documents...")
        self.filter_edit.textChanged.connect(self.filter_list)
        self.layout.addWidget(self.filter_edit)
        
        # List
        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_select = QPushButton("Select")
        self.btn_select.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_select)
        self.layout.addLayout(btn_layout)
        
        self.docs = []
        self.load_docs()
        
    def load_docs(self):
        from shared.repositories.document_manager.document_repository import DocumentRepository
        from shared.database import get_db
        
        db = next(get_db())
        repo = DocumentRepository(db)
        # Fetch metadata only to be lighter
        self.docs = repo.get_all_metadata()
        
        self.update_list(self.docs)
        
    def update_list(self, docs):
        self.list_widget.clear()
        for doc in docs:
            # Use title and collection in display
            display = f"{doc.title} ({doc.collection or 'Uncategorized'})"
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, doc.id)
            self.list_widget.addItem(item)
            
    def filter_list(self, text):
        text = text.lower()
        filtered = [
            d for d in self.docs 
            if text in d.title.lower() or (d.collection and text in d.collection.lower())
        ]
        self.update_list(filtered)
        
    def get_selected_doc_id(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None
