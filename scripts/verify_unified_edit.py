
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QEvent, QPoint
from PyQt6.QtGui import QMouseEvent

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.ui.spreadsheet_window import SpreadsheetWindow

def verify_unified_edit():
    app = QApplication(sys.argv)
    
    # Mock Data
    content = {
        "columns": [f"Col{i}" for i in range(5)],
        "data": [["" for _ in range(5)] for _ in range(5)],
        "styles": {}
    }
    repo = None # Mock repo
    
    window = SpreadsheetWindow(1, "Test Table", content, repo)
    window.show()
    
    view = window.view
    model = window.model
    
    print("[1] Opening Inline Editor on A1...")
    # Select A1
    idx_a1 = model.index(0, 0)
    view.setCurrentIndex(idx_a1)
    
    # Trigger Edit
    view.edit(idx_a1)
    
    editor = view.active_editor
    if not editor:
        print("FAIL: Editor did not open.")
        return
    print("PASS: Editor opened.")
    
    print("[2] Typing '=' to trigger Reference Mode...")
    # Simulate typing
    editor.setText("=")
    # Signal should have fired
    # Check window state
    if not window._is_editing_formula:
        print("FAIL: Formula Mode NOT triggered.")
        return
    print("PASS: Formula Mode triggered.")
    
    print("[3] Clicking B2 (1,1) to insert reference...")
    idx_b2 = model.index(1, 1)
    rect = view.visualRect(idx_b2)
    click_pos = rect.center()
    
    # Create Mouse Event on Viewport
    # QMouseEvent(type, pos, button, buttons, modifiers)
    # Note: pos is relative to receiver (viewport)
    event = QMouseEvent(QEvent.Type.MouseButtonPress, 
                        click_pos.toPointF(), 
                        Qt.MouseButton.LeftButton, 
                        Qt.MouseButton.LeftButton, 
                        Qt.KeyboardModifier.NoModifier)
    
    # Send Event
    # Logic in SpreadsheetWindow.eventFilter should intercept this
    handled = QApplication.sendEvent(view.viewport(), event)
    
    # Check results
    current_text = editor.text()
    print(f"Editor Text: '{current_text}'")
    
    if current_text == "=B2":
        print("PASS: Reference inserted correctly.")
    else:
        print(f"FAIL: Expected '=B2', got '{current_text}'")
        
    # Check if editor is still open (active_editor ref matches focused widget?)
    # Or just check if view.active_editor is still set
    if view.active_editor and view.active_editor.isVisible():
        print("PASS: Editor remained open.")
    else:
        print("FAIL: Editor closed unexpectedly.")
        
    app.quit()

if __name__ == "__main__":
    verify_unified_edit()
