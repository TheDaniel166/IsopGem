"""PDF export dialog for Rich Text Editor."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox, QGroupBox,
    QDialogButtonBox, QFileDialog
)
from PyQt6.QtGui import QPageSize, QPageLayout
from PyQt6.QtCore import QMarginsF
from .page_setup_dialog import PageSetupDialog


class ExportPdfDialog(QDialog):
    """Dialog for PDF export options."""
    
    PAGE_SIZES = PageSetupDialog.PAGE_SIZES
    MARGIN_PRESETS = PageSetupDialog.MARGIN_PRESETS
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export to PDF")
        self.setMinimumWidth(400)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        file_group = QGroupBox("Output File")
        file_layout = QHBoxLayout()
        
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Select output file...")
        file_layout.addWidget(self.file_input)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(browse_btn)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        page_group = QGroupBox("Page Setup")
        page_layout = QFormLayout()
        
        self.size_combo = QComboBox()
        for name, _ in self.PAGE_SIZES:
            self.size_combo.addItem(name)
        self.size_combo.setCurrentIndex(2)
        page_layout.addRow("Paper size:", self.size_combo)
        
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["Portrait", "Landscape"])
        page_layout.addRow("Orientation:", self.orientation_combo)
        
        self.margins_combo = QComboBox()
        for name, *_ in self.MARGIN_PRESETS:
            self.margins_combo.addItem(name)
        page_layout.addRow("Margins:", self.margins_combo)
        
        page_group.setLayout(page_layout)
        layout.addWidget(page_group)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Export")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _browse_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", "", "PDF Files (*.pdf)"
        )
        if path:
            if not path.endswith('.pdf'):
                path += '.pdf'
            self.file_input.setText(path)
    
    def get_file_path(self) -> str:
        return self.file_input.text()
    
    def get_page_size(self) -> QPageSize:
        idx = self.size_combo.currentIndex()
        _, size_id = self.PAGE_SIZES[idx]
        return QPageSize(size_id)
    
    def get_orientation(self) -> QPageLayout.Orientation:
        if self.orientation_combo.currentText() == "Landscape":
            return QPageLayout.Orientation.Landscape
        return QPageLayout.Orientation.Portrait
    
    def get_margins(self) -> QMarginsF:
        idx = self.margins_combo.currentIndex()
        _, left, top, right, bottom = self.MARGIN_PRESETS[idx]
        return QMarginsF(left, top, right, bottom)
