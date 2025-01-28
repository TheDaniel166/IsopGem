from core.document_editor.editor import DocumentEditor
from core.import_system.import_manager import ImportManager
from PyQt5.QtWidgets import (QMainWindow, QToolBar, QAction, QFileDialog, 
                            QMessageBox, QTreeView, QListWidget)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
import os
from ..import_dialog import ImportDialog
from datetime import datetime

class DocumentActions:
    def __init__(self, parent):
        self.parent = parent
        self.editor_windows = []
        self.import_manager = ImportManager()
        self.documents_root = "documents"  # Root folder for all documents
        self.ensure_document_structure()
        
    def ensure_document_structure(self):
        """Ensure the documents folder structure exists"""
        if not os.path.exists(self.documents_root):
            os.makedirs(self.documents_root)
            os.makedirs(os.path.join(self.documents_root, "uncategorized"))

    def create_new_document(self):
        """Create a new document editor window"""
        editor_window = QMainWindow()
        editor_window.setWindowTitle("New Document")
        editor_window.resize(800, 600)
        
        editor = DocumentEditor()
        editor_window.setCentralWidget(editor)
        
        # Add toolbar with actions
        toolbar = QToolBar()
        save_action = QAction("Save", editor_window)
        save_action.triggered.connect(lambda: self.save_document(editor))
        
        toolbar.addAction(save_action)
        editor_window.addToolBar(toolbar)
        
        self.editor_windows.append(editor_window)
        editor_window.show()
        return editor_window

    def show_import_dialog(self):
        """Show import dialog and handle import process"""
        dialog = ImportDialog(self.parent)
        if dialog.exec_():
            file_path = dialog.selected_file
            category = dialog.selected_category
            open_after = dialog.open_after_import
            preserve_format = dialog.preserve_formatting
            
            if file_path:
                try:
                    # Import the document
                    result = self.import_manager.import_document(file_path, category)
                    
                    # Store the document
                    stored_path = self.store_document(result['content'], result['metadata'], preserve_format)
                    
                    # Open document if requested
                    if open_after:
                        self.open_document(stored_path)
                    
                    # Update both tree view and recent documents
                    if hasattr(self.parent, 'update_document_views'):
                        self.parent.update_document_views()
                    
                    QMessageBox.information(self.parent, "Success", 
                                          f"Document imported successfully to category: {category}")
                    
                except Exception as e:
                    QMessageBox.critical(self.parent, "Import Error", 
                                       f"Could not import file: {str(e)}")

    def save_document(self, editor):
        """Save the current document"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self.parent,
                "Save Document",
                self.documents_root,
                "Text Files (*.txt);;All Files (*.*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(editor.editor.toPlainText())
                QMessageBox.information(self.parent, "Success", "Document saved successfully")
                
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", f"Could not save document: {str(e)}")

    def store_document(self, content, metadata, preserve_format):
        """Store the imported document in RTF format"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_name = os.path.splitext(os.path.basename(metadata['original_file']))[0]
            new_filename = f"{base_name}_{timestamp}.rtf"  # Changed extension to .rtf
            
            category = metadata.get('category', 'uncategorized')
            category_path = os.path.join(self.documents_root, category)
            os.makedirs(category_path, exist_ok=True)
            
            file_path = os.path.join(category_path, new_filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)  # Content is now in RTF format
            
            self.update_recent_documents(file_path, metadata)
            return file_path
            
        except Exception as e:
            raise Exception(f"Failed to store document: {str(e)}")

    def update_recent_documents(self, file_path, metadata):
        """Update the list of recent documents"""
        # This will be implemented when we add the storage system
        pass

    def get_all_documents(self):
        """Return a model for the TreeView showing all documents"""
        model = QStandardItemModel()
        root = model.invisibleRootItem()
        
        for category in os.listdir(self.documents_root):
            category_path = os.path.join(self.documents_root, category)
            if os.path.isdir(category_path):
                category_item = QStandardItem(category)
                
                for doc in os.listdir(category_path):
                    if doc.endswith(('.rtf', '.txt')):  # Added .rtf
                        doc_item = QStandardItem(doc)
                        doc_item.setData(os.path.join(category_path, doc))
                        category_item.appendRow(doc_item)
                
                root.appendRow(category_item)
        
        return model

    def get_recent_documents(self, limit=10):
        """Return list of recent documents"""
        recent_docs = []
        for root, _, files in os.walk(self.documents_root):
            for file in files:
                if file.endswith(('.rtf', '.txt')):  # Added .rtf
                    file_path = os.path.join(root, file)
                    recent_docs.append({
                        'path': file_path,
                        'name': file,
                        'modified': os.path.getmtime(file_path)
                    })
        
        recent_docs.sort(key=lambda x: x['modified'], reverse=True)
        return recent_docs[:limit]

    def open_document(self, file_path):
        """Open a document in the editor"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            editor_window = self.create_new_document()
            editor = editor_window.centralWidget()
            editor.editor.setText(content)
            editor_window.setWindowTitle(os.path.basename(file_path))
            
        except Exception as e:
            QMessageBox.critical(self.parent, "Error", 
                               f"Could not open document: {str(e)}")
