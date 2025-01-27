from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QLineEdit, QPushButton, QComboBox, QCheckBox,
                            QDialogButtonBox, QFileDialog)
from PyQt5.QtCore import pyqtSignal

class ImportDialog(QDialog):
    importRequested = pyqtSignal(str, str, bool)  # file_path, category, open_after

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Import Document")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # File selection
        file_group = QGroupBox("Import File")
        file_layout = QHBoxLayout()
        self.file_path = QLineEdit()
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(self.file_path)
        file_layout.addWidget(browse_btn)
        file_group.setLayout(file_layout)
        
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
        
        # Open after import option
        self.open_checkbox = QCheckBox("Open document after import")
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add all to layout
        layout.addWidget(file_group)
        layout.addWidget(category_group)
        layout.addWidget(self.open_checkbox)
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

