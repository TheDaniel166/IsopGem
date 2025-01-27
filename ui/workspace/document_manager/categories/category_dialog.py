from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, 
                            QDialogButtonBox, QLabel)

class CategoryDialog(QDialog):
    def __init__(self, parent=None, category_name=None):
        super().__init__(parent)
        self.category_name = category_name
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Name input
        layout.addWidget(QLabel("Category Name:"))
        self.name_input = QLineEdit()
        if self.category_name:
            self.name_input.setText(self.category_name)
        layout.addWidget(self.name_input)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
