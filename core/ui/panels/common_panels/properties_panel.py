"""
Properties Panel implementation
"""
from PyQt6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from ..base import BasePanel

class PropertiesPanel(BasePanel):
    """Panel for displaying and editing object properties"""
    
    property_changed = pyqtSignal(str, object)  # Property name, new value
    
    def __init__(self, parent=None):
        self.current_object = None
        super().__init__(parent, title="Properties")
        
    def setup_ui(self):
        """Set up the properties panel UI"""
        # Create tree widget
        self.tree = QTreeWidget(self)
        self.tree.setHeaderLabels(["Property", "Value"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setColumnWidth(0, 150)
        self.tree.itemChanged.connect(self._on_item_changed)
        
        # Add to content layout
        self.content_layout.addWidget(self.tree)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_properties)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        
        self.content_layout.addLayout(controls_layout)
    
    def set_object(self, obj):
        """Set the object whose properties to display"""
        self.current_object = obj
        self.refresh_properties()
        
    def refresh_properties(self):
        """Refresh the properties display"""
        self.tree.clear()
        
        if not self.current_object:
            return
            
        # Add properties
        for name, value in vars(self.current_object).items():
            if not name.startswith('_'):  # Skip private attributes
                item = QTreeWidgetItem([name, str(value)])
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
                self.tree.addTopLevelItem(item)
    
    def _on_item_changed(self, item, column):
        """Handle property value changes"""
        if column == 1:  # Value column
            prop_name = item.text(0)
            new_value = item.text(1)
            self.property_changed.emit(prop_name, new_value)
    
    def get_preferred_area(self) -> Qt.DockWidgetArea:
        return Qt.DockWidgetArea.RightDockWidgetArea
    
    def get_preferred_size(self) -> tuple:
        return (300, 500)
