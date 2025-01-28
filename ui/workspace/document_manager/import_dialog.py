from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLineEdit, QPushButton, QComboBox, QCheckBox,
                            QDialogButtonBox, QFileDialog, QTextEdit, QLabel)
from PyQt5.QtCore import pyqtSignal
from core.import_system.import_manager import ImportManager

class ImportDialog(QDialog):
    importRequested = pyqtSignal(str, str, bool)  # file_path, category, open_after

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Document")
        self.selected_file = None
        self.selected_category = None
        self.import_manager = ImportManager()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # File selection
        file_group = QGroupBox("Import File")
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        self.file_path.textChanged.connect(self.update_preview)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(browse_btn)
        file_group.setLayout(file_layout)
        
        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(200)
        preview_layout.addWidget(self.preview_text)
        preview_group.setLayout(preview_layout)
        
        # Category selection
        category_group = QGroupBox("Select Category")
        category_layout = QVBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            'Class A', 'Class B', 'Class C', 
            'Class D', 'Class E', 'Class F',
            'Notes', 'Screenshots', 
            'Astrology Charts', 'TQ Operations'
        ])
        category_layout.addWidget(self.category_combo)
        category_group.setLayout(category_layout)
        
        # Import options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout()
        self.open_checkbox = QCheckBox("Open document after import")
        self.preserve_format = QCheckBox("Preserve original formatting")
        options_layout.addWidget(self.open_checkbox)
        options_layout.addWidget(self.preserve_format)
        options_group.setLayout(options_layout)
        
        # Status/Validation
        self.status_label = QLabel("")
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add all to layout
        layout.addWidget(file_group)
        layout.addWidget(preview_group)
        layout.addWidget(category_group)
        layout.addWidget(options_group)
        layout.addWidget(self.status_label)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def browse_file(self):
        file_types = "Text files (*.txt);;RTF files (*.rtf);;Word files (*.doc *.docx);;PDF files (*.pdf);;All files (*.*)"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File to Import",
            "",
            file_types
        )
        
        if file_path:
            self.file_path.setText(file_path)
            self.selected_file = file_path
            self.update_preview()

    def update_preview(self):
        try:
            if self.file_path.text():
                preview = self.import_manager.preview_document(self.file_path.text())
                self.preview_text.setText(preview)
                self.status_label.setText("Ready to import")
                self.status_label.setStyleSheet("color: green")
        except Exception as e:
            self.preview_text.setText("")
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet("color: red")

    def accept(self):
        if not self.file_path.text():
            self.status_label.setText("Please select a file")
            self.status_label.setStyleSheet("color: red")
            return
            
        self.selected_category = self.category_combo.currentText()
        self.open_after_import = self.open_checkbox.isChecked()
        self.preserve_formatting = self.preserve_format.isChecked()
        super().accept()

