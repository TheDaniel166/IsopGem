from core.document_editor.editor import DocumentEditor
from PyQt5.QtWidgets import QMainWindow, QToolBar, QAction, QFileDialog, QMessageBox
import os
from ..import_dialog import ImportDialog

class DocumentActions:
    def __init__(self, parent):
        self.parent = parent
        self.editor_windows = []  # List to store editor windows
        
    def create_new_document(self):
        # Create editor window
        editor_window = QMainWindow()
        editor_window.setWindowTitle("New Document")
        editor_window.resize(800, 600)
        
        # Create and set editor as central widget
        editor = DocumentEditor()
        editor_window.setCentralWidget(editor)
        
        # Add toolbar with actions
        toolbar = QToolBar()
        save_action = QAction("Save", editor_window)
        import_action = QAction("Import", editor_window)
        
        toolbar.addAction(save_action)
        toolbar.addAction(import_action)
        
        # Connect actions
        import_action.triggered.connect(lambda: self.import_document(editor))
        
        editor_window.addToolBar(toolbar)
        
        # Store reference to prevent garbage collection
        self.editor_windows.append(editor_window)
        
        editor_window.show()
        
    def import_document(self, editor):
        dialog = ImportDialog(self.parent)
        if dialog.exec_():
            file_path = dialog.selected_file
            category = dialog.selected_category
            
            if file_path:
                try:
                    ext = os.path.splitext(file_path)[1].lower()
                    editor.import_document(file_path)
                except Exception as e:
                    QMessageBox.critical(self.parent, "Import Error", 
                                       f"Could not import file: {str(e)}")

    def show_import_dialog(self):
        dialog = ImportDialog(self.parent)
        if dialog.exec_():
            file_path = dialog.selected_file
            category = dialog.selected_category
            open_after = dialog.open_after_import
            
            if file_path and open_after:
                self.create_new_document()
                # Get the most recently created editor window
                editor = self.editor_windows[-1].centralWidget()
                self.import_document(editor)
