"""Dialog for editing document metadata."""
from typing import List, Optional, Union, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFormLayout, QCheckBox
)
from pillars.document_manager.models.document import Document
from pillars.document_manager.models.dtos import DocumentMetadataDTO

class DocumentPropertiesDialog(QDialog):
    def __init__(self, documents: List[Union[Document, DocumentMetadataDTO]], parent=None):
        super().__init__(parent)
        self.documents = documents
        
        if len(documents) == 1:
            self.setWindowTitle(f"Properties: {documents[0].title}")
        else:
            self.setWindowTitle(f"Properties: {len(documents)} Documents")
            
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Helper to determine common value
        def get_common_value(attr):
            values = {getattr(d, attr) or "" for d in self.documents}
            return values.pop() if len(values) == 1 else None

        # Title
        self.title_edit = QLineEdit()
        if len(self.documents) == 1:
            self.title_edit.setText(str(self.documents[0].title))
        else:
            self.title_edit.setPlaceholderText("<Multiple Values> - Editing Disabled")
            self.title_edit.setEnabled(False)
        form.addRow("Title:", self.title_edit)
        
        # Author
        self.author_edit = QLineEdit()
        common_author = get_common_value("author")
        if common_author is not None:
            self.author_edit.setText(common_author)
        else:
            self.author_edit.setPlaceholderText("<Multiple Values> - Leave blank to keep")
        form.addRow("Author:", self.author_edit)
        
        # Collection
        self.collection_edit = QLineEdit()
        common_collection = get_common_value("collection")
        if common_collection is not None:
            self.collection_edit.setText(common_collection)
        else:
            self.collection_edit.setPlaceholderText("<Multiple Values> - Leave blank to keep")
        form.addRow("Collection:", self.collection_edit)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)

    def get_data(self):
        """Returns dict of fields to update. None value means no change."""
        data = {}
        
        # Title (only if single doc)
        if len(self.documents) == 1:
            data['title'] = self.title_edit.text()
            
        # For other fields, if text is empty and placeholder indicates multiple, 
        # we assume no change.
        # If text is empty and placeholder is NOT multiple (meaning it was empty or common empty),
        # then it's an empty string update.
        
        def get_update_value(edit_widget, attr):
            text = edit_widget.text()
            # If user typed something, use it
            if text:
                return text
            
            # If text is empty
            # Check if it was originally multiple
            values = {getattr(d, attr) or "" for d in self.documents}
            is_multiple = len(values) > 1
            
            if is_multiple:
                return None # No change
            else:
                return "" # User cleared it or it was already empty
        
        data['author'] = get_update_value(self.author_edit, 'author')
        data['collection'] = get_update_value(self.collection_edit, 'collection')
        
        return data
