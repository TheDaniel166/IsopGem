from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, 
    QComboBox, QDialogButtonBox, QLabel
)

class ImportOptionsDialog(QDialog):
    def __init__(self, existing_collections=None, parent=None):
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
        for coll in sorted(self.existing_collections):
            self.collection_combo.addItem(coll)
        form.addRow("Collection:", self.collection_combo)

        # Tags
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("tag1, tag2, tag3")
        form.addRow("Tags:", self.tags_edit)

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
        return {
            'collection': self.collection_combo.currentText().strip() or None,
            'tags': self.tags_edit.text().strip() or None
        }
