import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QMouseEvent
from pillars.document_manager.ui.canvas.infinite_canvas import InfiniteCanvasView
import logging

logging.basicConfig(level=logging.INFO)

def RiteOfCanvas():
    app = QApplication(sys.argv)
    
    view = InfiniteCanvasView()
    view.resize(800, 600)
    view.show()
    
    print("Testing Canvas Click...")
    
    # Simulate Double Click at 100, 100
    pos = QPointF(100.0, 100.0)
    event = QMouseEvent(
        QMouseEvent.Type.MouseButtonDblClick,
        pos,
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    
    view.mouseDoubleClickEvent(event)
    
    # Check if item added
    items = view.scene.items()
    print(f"Items in scene: {len(items)}")
    
    if len(items) > 0:
        print("Success: Item created.")
    else:
        print("Failure: No item created.")
        
    # sys.exit(app.exec()) # Don't actually run loop in headless test

if __name__ == "__main__":
    RiteOfCanvas()
