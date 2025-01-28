from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                            QTreeWidgetItem, QPushButton, QMenu, QInputDialog)
from .category_manager import CategoryManager
from ui.workspace.document_manager.categories.category_manager import CategoryManager
from .category_dialog import CategoryDialog
class CategoryPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.category_manager = CategoryManager()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("Add Category")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.edit_btn)
        toolbar.addWidget(self.delete_btn)
        
        # Category Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Categories")
        
        # Create root items
        self.predefined_root = QTreeWidgetItem(["Predefined Categories"])
        self.custom_root = QTreeWidgetItem(["Custom Categories"])
        
        self.tree.addTopLevelItem(self.predefined_root)
        self.tree.addTopLevelItem(self.custom_root)
        
        # Populate categories
        self.refresh_categories()
        
        # Connect signals
        self.add_btn.clicked.connect(self.add_category)
        self.edit_btn.clicked.connect(self.edit_category)
        self.delete_btn.clicked.connect(self.delete_category)
        
        # Add to layout
        layout.addLayout(toolbar)
        layout.addWidget(self.tree)
        self.setLayout(layout)

    def add_category(self):
        dialog = CategoryDialog(self)
        if dialog.exec_():
            new_category = dialog.name_input.text().strip()
            if new_category:
                self.category_manager.add_custom_category(new_category)
                self.refresh_categories()

    def edit_category(self):
        current_item = self.tree.currentItem()
        if current_item and current_item.parent():  # Ensure it's a category, not a root
            old_name = current_item.text(0)
            dialog = CategoryDialog(self, old_name)
            if dialog.exec_():
                new_name = dialog.name_input.text().strip()
                if new_name and new_name != old_name:
                    # Update in category manager
                    if old_name in self.category_manager.custom_categories:
                        self.category_manager.custom_categories.remove(old_name)
                        self.category_manager.add_custom_category(new_name)
                        self.refresh_categories()

    def delete_category(self):
        current_item = self.tree.currentItem()
        if current_item and current_item.parent() == self.custom_root:
            category = current_item.text(0)
            self.category_manager.remove_custom_category(category)
            self.refresh_categories()
        
    def refresh_categories(self):
        # Clear existing items
        self.predefined_root.takeChildren()
        self.custom_root.takeChildren()
        
        # Add predefined categories
        for category in self.category_manager.predefined_categories:
            item = QTreeWidgetItem([category])
            self.predefined_root.addChild(item)
        
        # Add custom categories
        for category in self.category_manager.custom_categories:
            item = QTreeWidgetItem([category])
            self.custom_root.addChild(item)
        
        # Expand roots to show categories
        self.tree.expandAll()