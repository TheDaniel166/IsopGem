"""Document Editor Window."""
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QFileDialog, 
    QMessageBox, QMenuBar, QDialog, QListWidget, 
    QLineEdit, QDialogButtonBox, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from .rich_text_editor import RichTextEditor
from shared.database import get_db
from pillars.document_manager.services.document_service import DocumentService

class DocumentEditorWindow(QMainWindow):
    """Window for editing documents using the RichTextEditor."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Document Editor")
        self.resize(1000, 800)
        
        # State
        self.current_file = None
        self.current_doc_model = None # Database model if loaded from DB
        self.is_modified = False
        
        # Setup Save Directory
        # Assuming app is run from project root, create 'saved_documents' there
        self.save_dir = Path(os.getcwd()) / "saved_documents"
        self.save_dir.mkdir(exist_ok=True)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Rich Text Editor
        self.editor = RichTextEditor()
        self.editor.text_changed.connect(self._on_text_changed)
        self.editor.wiki_link_requested.connect(self._show_wiki_link_selector)
        layout.addWidget(self.editor)
        
        self._init_file_menu()
        self._update_title()

    def _show_wiki_link_selector(self):
        """Show a dialog to select a document to link."""
        try:
            db = next(get_db())
            service = DocumentService(db)
            docs = service.get_all_documents_metadata()
        except Exception as e:
            print(f"Error fetching docs: {e}")
            return

        # Create a simple selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Insert Link")
        dialog.resize(400, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Filter
        filter_input = QLineEdit()
        filter_input.setPlaceholderText("Search documents...")
        layout.addWidget(filter_input)
        
        # List
        list_widget = QListWidget()
        for doc in docs:
            item = QListWidgetItem(f"{doc.title} (ID: {doc.id})")
            item.setData(Qt.ItemDataRole.UserRole, doc)
            list_widget.addItem(item)
        layout.addWidget(list_widget)
        
        # Filter logic
        def filter_items(text):
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                item.setHidden(text.lower() not in item.text().lower())
        
        filter_input.textChanged.connect(filter_items)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        # Handle selection
        def on_item_double_clicked(item):
            dialog.accept()
            
        list_widget.itemDoubleClicked.connect(on_item_double_clicked)
        
        if dialog.exec():
            selected_items = list_widget.selectedItems()
            if selected_items:
                doc = selected_items[0].data(Qt.ItemDataRole.UserRole)
                self._insert_wiki_link(doc)

    def _insert_wiki_link(self, doc):
        """Insert the wiki link into the editor."""
        # The editor cursor is currently after '[[', so we just append the title and ']]'
        self.editor.editor.insertPlainText(f"{doc.title}]]")

    def _init_file_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        # New
        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_document)
        file_menu.addAction(new_action)
        
        # Open
        open_action = QAction("Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_document)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Save
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_document)
        file_menu.addAction(save_action)
        
        # Save As
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_as_document)
        file_menu.addAction(save_as_action)

    def _on_text_changed(self):
        if not self.is_modified:
            self.is_modified = True
            self._update_title()

    def _update_title(self):
        title = "Document Editor"
        if self.current_file:
            title += f" - {self.current_file.name}"
        elif self.current_doc_model:
            title += f" - {self.current_doc_model.title} (DB)"
        else:
            title += " - Untitled"
            
        if self.is_modified:
            title += "*"
            
        self.setWindowTitle(title)

    def load_document_model(self, doc, search_term=None):
        """Load a document from the database model."""
        if not self._check_unsaved_changes():
            return

        self.current_doc_model = doc
        self.current_file = None
        
        # Prefer raw content (HTML/RTF) if available, else plain content
        content = doc.raw_content if doc.raw_content else doc.content
        
        # If we have raw content, it's likely HTML (from our parser)
        # or if the file type is explicitly HTML
        if doc.raw_content or doc.file_type == 'html':
            self.editor.set_html(content)
        else:
            self.editor.set_text(content)
            
        self.is_modified = False
        self._update_title()
        
        # Highlight search term if provided
        if search_term:
            self.editor.find_text(search_term)

    def _check_unsaved_changes(self):
        if self.is_modified:
            reply = QMessageBox.question(
                self, 
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                return self.save_document()
            elif reply == QMessageBox.StandardButton.Cancel:
                return False
        return True

    def new_document(self):
        if not self._check_unsaved_changes():
            return
            
        self.editor.clear()
        self.current_file = None
        self.is_modified = False
        self._update_title()

    def open_document(self):
        if not self._check_unsaved_changes():
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            str(self.save_dir),
            "HTML Files (*.html);;Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            path = Path(file_path)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if path.suffix == '.html':
                    self.editor.set_html(content)
                else:
                    self.editor.set_text(content)
                    
                self.current_file = path
                self.is_modified = False
                self._update_title()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def save_document(self):
        if self.current_doc_model:
            try:
                db = next(get_db())
                service = DocumentService(db)
                
                # Update content
                # Note: We are saving HTML as raw_content. 
                # We should ideally strip tags for 'content' (searchable text)
                html_content = self.editor.get_html()
                plain_text = self.editor.get_text()
                
                service.update_document(
                    self.current_doc_model.id,
                    content=plain_text,
                    raw_content=html_content
                )
                
                self.is_modified = False
                self._update_title()
                QMessageBox.information(self, "Success", "Document saved to database.")
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save to database: {str(e)}")
                return False

        if not self.current_file:
            return self.save_as_document()
            
        try:
            content = self.editor.get_html()
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.is_modified = False
            self._update_title()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
            return False

    def save_as_document(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Document As",
            str(self.save_dir),
            "HTML Files (*.html);;All Files (*)"
        )
        
        if file_path:
            # Ensure extension
            if not file_path.endswith('.html'):
                file_path += '.html'
                
            self.current_file = Path(file_path)
            return self.save_document()
        return False

    def closeEvent(self, event):
        if not self._check_unsaved_changes():
            event.ignore()
        else:
            event.accept()
