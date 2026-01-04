"""
Import Options Dialog - The Collection Selector.
Dialog for configuring import settings including target collection selection.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QComboBox, QDialogButtonBox
)

class ImportOptionsDialog(QDialog):
    """
    Import Options Dialog class definition.
    
    Attributes:
        existing_collections: Description of existing_collections.
    
    """
    def __init__(self, existing_collections=None, parent=None):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """
          init   logic.
        
        Args:
            existing_collections: Description of existing_collections.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Import Options")
        self.existing_collections = existing_collections or []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Collection
        self.collection_combo = QComboBox()
        self.collection_combo.setEditable(True)
        self.collection_combo.setPlaceholderText("Select or type new collection...")
        self.collection_combo.addItem("") # Empty option
        for coll in sorted(self.existing_collections):  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
            self.collection_combo.addItem(coll)
        form.addRow("Collection:", self.collection_combo)

        layout.addLayout(form)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        """
        Retrieve data logic.
        
        Returns:
            Result of get_data operation.
        """
        return {
            'collection': self.collection_combo.currentText().strip() or None,
        }