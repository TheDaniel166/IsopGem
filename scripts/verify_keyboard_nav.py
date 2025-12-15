
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QEvent, QPoint
from PyQt6.QtGui import QMouseEvent, QKeyEvent

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.ui.spreadsheet_window import SpreadsheetWindow

def verify_keyboard_nav():
    app = QApplication(sys.argv)
    
    # Mock Data (using corrected dict format)
    content = {
        "columns": [f"Col{i}" for i in range(5)],
        "data": [["" for _ in range(5)] for _ in range(5)],
        "styles": {}
    }
    repo = None
    
    window = SpreadsheetWindow(1, "Test Table", content, repo)
    window.show()
    
    view = window.view
    model = window.model
    
    print("[1] Opening Inline Editor on A1...")
    idx_a1 = model.index(0, 0)
    view.setCurrentIndex(idx_a1)
    view.edit(idx_a1)
    editor = view.active_editor
    if not editor:
        print("FAIL: Editor not open.")
        return
    print("PASS: Editor opened.")

    # 1. Test Operator Logic
    print("[2] Typing '=' -> Should Enable Ref Mode")
    editor.setText("=")
    editor.setCursorPosition(1) # Ensure cursor is at end
    if not window._ref_mode:
        print("FAIL: Ref Mode not enabled by '='.")
    else:
        print("PASS: Ref Mode enabled.")

    # 2. Test Arrow Navigation
    print("[3] Pressing RIGHT Arrow -> Should select B1 (0,1)")
    # Since we can't easily simulate physical key press going through Qt event loop without QTest,
    # we manually send the event to the window (which is the event filter).
    
    key_event = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Right, Qt.KeyboardModifier.NoModifier)
    
    # The event usually goes to editor, and window intercepts it.
    # So we send to editor.
    res = QApplication.sendEvent(editor, key_event)
    
    current = view.currentIndex()
    # Phantom Cursor Logic: Selection should NOT move (stays at A1), but text updates.
    if current.row() == 0 and current.column() == 0:
        print("PASS: Selection stayed at A1 (0,0) [Phantom Mode].")
    else:
        print(f"FAIL: Selection moved to {current.row()},{current.column()} (Expected 0,0)")
        
    if editor.text() == "=B1":
        print("PASS: Text updated to '=B1'.")
    else:
        print(f"FAIL: Text is '{editor.text()}'")

    # 3. Test Toggle (Ctrl+E)
    print("[4] Pressing Ctrl+E -> Should Disable Ref Mode")
    ctrl_e = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_E, Qt.KeyboardModifier.ControlModifier)
    QApplication.sendEvent(editor, ctrl_e)
    
    if not window._ref_mode:
        print("PASS: Ref Mode disabled.")
    else:
        print("FAIL: Ref Mode NOT disabled.")
        
    # 4. Test Mouse Click Reset (Click inside Editor)
    print("[5] Re-enabling Ref Mode manually, then Clicking Editor -> Should Disable")
    window._ref_mode = True
    
    # Send click to Editor
    click_event = QMouseEvent(QEvent.Type.MouseButtonPress, QPoint(5,5).toPointF(), Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier)
    QApplication.sendEvent(editor, click_event)
    
    if not window._ref_mode:
        print("PASS: Ref Mode disabled by click.")
    else:
        print("FAIL: Ref Mode NOT disabled by click.")

    app.quit()

if __name__ == "__main__":
    verify_keyboard_nav()
