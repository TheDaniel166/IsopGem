from PyQt5.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class StyleInspector(QDockWidget):
    def __init__(self, editor, parent=None):
        super().__init__("Style Inspector", parent)
        self.editor = editor
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create properties view
        self.properties = QTreeWidget()
        self.properties.setHeaderLabels(["Property", "Value"])
        self.properties.setAlternatingRowColors(True)
        
        layout.addWidget(self.properties)
        self.setWidget(widget)
        
        # Update when cursor position changes
        self.editor.cursorPositionChanged.connect(self.update_properties)
        
    def update_properties(self):
        self.properties.clear()
        cursor = self.editor.textCursor()
        char_format = cursor.charFormat()
        block_format = cursor.blockFormat()
        
        # Character formatting
        char_root = QTreeWidgetItem(["Character Format"])
        self.properties.addTopLevelItem(char_root)
        
        self.add_property(char_root, "Font", char_format.font().family())
        self.add_property(char_root, "Size", f"{char_format.font().pointSize()}pt")
        self.add_property(char_root, "Weight", self.get_weight_name(char_format.font().weight()))
        self.add_property(char_root, "Color", char_format.foreground().color().name())
        
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