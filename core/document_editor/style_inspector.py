from PyQt5.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class StyleInspector(QDockWidget):
    def __init__(self, editor):
        super().__init__("Style Inspector")  # Add title
        self.editor = editor
        self.setup_ui()
        
        # Connect to editor's cursor position change signal
        self.editor.editor.cursorPositionChanged.connect(self.update_properties)
        self.update_properties()
        
    def setup_ui(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create properties view
        self.properties = QTreeWidget()
        self.properties.setHeaderLabels(["Property", "Value"])
        self.properties.setAlternatingRowColors(True)
        self.properties.setColumnWidth(0, 150)  # Set width for property column
        
        layout.addWidget(self.properties)
        self.setWidget(widget)
        
    def update_properties(self):
        """Update displayed properties"""
        cursor = self.editor.editor.textCursor()
        char_format = cursor.charFormat()
        block_format = cursor.blockFormat()
        
        # Clear existing items
        self.properties.clear()
        
        # Add character format properties
        char_item = QTreeWidgetItem(["Character Format"])
        self.properties.addTopLevelItem(char_item)
        char_item.setExpanded(True)  # Expand by default
        
        # Font properties
        font = char_format.font()
        self.add_property(char_item, "Font Family", font.family())
        self.add_property(char_item, "Font Size", f"{font.pointSize()}pt")
        self.add_property(char_item, "Font Weight", self.get_weight_name(font.weight()))
        self.add_property(char_item, "Italic", str(font.italic()))
        self.add_property(char_item, "Underline", str(font.underline()))
        
        # Color properties
        color = char_format.foreground().color()
        self.add_property(char_item, "Text Color", color.name())
        
        # Background color
        bg_color = char_format.background().color()
        if bg_color.alpha() > 0:
            self.add_property(char_item, "Background", bg_color.name())
        
        # Paragraph formatting
        para_root = QTreeWidgetItem(["Paragraph Format"])
        self.properties.addTopLevelItem(para_root)
        
        self.add_property(para_root, "Alignment", self.get_alignment_name(block_format.alignment()))
        self.add_property(para_root, "Line Height", f"{block_format.lineHeight()}%")
        self.add_property(para_root, "Top Margin", f"{block_format.topMargin()}pt")
        self.add_property(para_root, "Bottom Margin", f"{block_format.bottomMargin()}pt")
        
    def add_property(self, parent, name, value):
        QTreeWidgetItem(parent, [name, str(value)])
        
    def get_weight_name(self, weight):
        weights = {
            QFont.Light: "Light",
            QFont.Normal: "Normal",
            QFont.DemiBold: "DemiBold",
            QFont.Bold: "Bold",
            QFont.Black: "Black"
        }
        return weights.get(weight, "Normal")
        
    def get_alignment_name(self, alignment):
        alignments = {
            Qt.AlignLeft: "Left",
            Qt.AlignRight: "Right",
            Qt.AlignCenter: "Center",
            Qt.AlignJustify: "Justify"
        }
        return alignments.get(alignment, "Left") 