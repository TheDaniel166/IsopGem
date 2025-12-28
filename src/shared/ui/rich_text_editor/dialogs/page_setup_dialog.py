"""Page setup dialog for Rich Text Editor."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QComboBox,
    QGroupBox, QDialogButtonBox
)
from PyQt6.QtGui import QPageSize, QPageLayout
from PyQt6.QtCore import QMarginsF


class PageSetupDialog(QDialog):
    """Dialog for page setup options."""
    
    PAGE_SIZES = [
        ("Letter (8.5 x 11 in)", QPageSize.PageSizeId.Letter),
        ("Legal (8.5 x 14 in)", QPageSize.PageSizeId.Legal),
        ("A4 (210 x 297 mm)", QPageSize.PageSizeId.A4),
        ("A3 (297 x 420 mm)", QPageSize.PageSizeId.A3),
        ("A5 (148 x 210 mm)", QPageSize.PageSizeId.A5),
        ("B5 (176 x 250 mm)", QPageSize.PageSizeId.B5),
        ("Executive (7.25 x 10.5 in)", QPageSize.PageSizeId.Executive),
        ("Tabloid (11 x 17 in)", QPageSize.PageSizeId.Tabloid),
    ]
    
    # Margin presets: (name, left, top, right, bottom) in mm
    MARGIN_PRESETS = [
        ("Normal (1 inch)", 25.4, 25.4, 25.4, 25.4),
        ("Narrow (0.5 inch)", 12.7, 12.7, 12.7, 12.7),
        ("Moderate", 19.1, 25.4, 19.1, 25.4),
        ("Wide", 50.8, 25.4, 50.8, 25.4),
    ]
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Page Setup")
        self.setMinimumWidth(350)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        size_group = QGroupBox("Paper")
        size_layout = QFormLayout()
        
        self.size_combo = QComboBox()
        for name, _ in self.PAGE_SIZES:
            self.size_combo.addItem(name)
        self.size_combo.setCurrentIndex(2)
        size_layout.addRow("Paper size:", self.size_combo)
        
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["Portrait", "Landscape"])
        size_layout.addRow("Orientation:", self.orientation_combo)
        
        self.margins_combo = QComboBox()
        for name, *_ in self.MARGIN_PRESETS:
            self.margins_combo.addItem(name)
        size_layout.addRow("Margins:", self.margins_combo)
        
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_page_size(self) -> QPageSize:
        """
        Retrieve page size logic.
        
        Returns:
            Result of get_page_size operation.
        """
        idx = self.size_combo.currentIndex()
        _, size_id = self.PAGE_SIZES[idx]
        return QPageSize(size_id)
    
    def get_orientation(self) -> QPageLayout.Orientation:
        """
        Retrieve orientation logic.
        
        Returns:
            Result of get_orientation operation.
        """
        if self.orientation_combo.currentText() == "Landscape":
            return QPageLayout.Orientation.Landscape
        return QPageLayout.Orientation.Portrait
    
    def get_margins(self) -> QMarginsF:
        """
        Retrieve margins logic.
        
        Returns:
            Result of get_margins operation.
        """
        idx = self.margins_combo.currentIndex()
        _, left, top, right, bottom = self.MARGIN_PRESETS[idx]
        return QMarginsF(left, top, right, bottom)