
import pytest
from PyQt6.QtWidgets import QApplication
from pillars.document_manager.ui.mindscape_items import MindscapeNodeItem

# Basic Qt App needed for GraphicsObjects
app = QApplication([])

def test_node_tooltip():
    # 1. Create Item with Content
    content = "This is a secret snippet."
    item = MindscapeNodeItem(1, "Test Node", content=content)
    
    # 2. Verify Tooltip
    assert item.toolTip() == content
    
def test_node_tooltip_empty():
    item = MindscapeNodeItem(2, "Empty Node")
    assert item.toolTip() == ""
