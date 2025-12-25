
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPoint, QPointF
from PyQt6.QtGui import QMouseEvent
from pillars.document_manager.ui.mindscape_view import MindscapeView
from pillars.document_manager.ui.mindscape_items import MindscapeNodeItem

# App instance needed for GraphicsView
app = QApplication([])

def test_view_click_propagation():
    """
    Verify that clicking a node in the view emits node_selected.
    Using qtbot-like logic manually since we might not have pytest-qt installed fully configured,
    or just standard event sending.
    """
    view = MindscapeView()
    view.resize(800, 600)
    view.show()
    
    # 1. Add a dummy node manually to bypassing Service/DB for pure UI test
    # (We need to trick the view logic or just insert item directly)
    node_id = 999
    item = MindscapeNodeItem(node_id, "Test Node")
    item.setPos(100, 100) # Center-ish?
    view.scene.addItem(item)
    view._items[node_id] = item # Register in view map
    
    # CRITICAL: Wire the internal signal (normally done in load_graph)
    item.clicked.connect(view._on_node_clicked)
    
    # 2. Setup Signal Spy
    received_signals = []
    view.node_selected.connect(lambda nid: received_signals.append(nid))
    
    # 3. Simulate Click
    # Map item center to viewport coordinates
    # We must ensure the scene rect is set so the centerOn works or mapFromScene works
    view.setSceneRect(0, 0, 1000, 1000)
    
    # Get center of item in SCENE coords
    scene_pos = item.sceneBoundingRect().center()
    
    # Map to VIEWPORT coords
    viewport_pos = view.mapFromScene(scene_pos)
    
    # Assert item is actually there
    found_item = view.itemAt(viewport_pos)
    assert isinstance(found_item, MindscapeNodeItem), f"Expected NodeItem, got {found_item} at {viewport_pos}"
    
    # Send Press
    press_event = QMouseEvent(
        QMouseEvent.Type.MouseButtonPress,
        viewport_pos.toPointF(),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    view.mousePressEvent(press_event)
    
    # Send Release (optional for click logic, but good practice)
    release_event = QMouseEvent(
        QMouseEvent.Type.MouseButtonRelease,
        viewport_pos.toPointF(),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    view.mouseReleaseEvent(release_event)
    
    # 4. Verify
    assert len(received_signals) > 0, "node_selected signal was not emitted!"
    assert received_signals[0] == node_id
