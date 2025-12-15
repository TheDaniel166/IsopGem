
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QItemSelectionModel
from PyQt6.QtGui import QKeyEvent

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.ui.spreadsheet_window import SpreadsheetWindow

def verify_delete_key():
    app = QApplication(sys.argv)
    
    # Mock Data
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
    
    # 1. Setup Data: A1="Delete Me"
    idx_a1 = model.index(0, 0)
    model.setData(idx_a1, "Delete Me", Qt.ItemDataRole.EditRole)
    
    print(f"[1] A1 Content: '{model.data(idx_a1, Qt.ItemDataRole.EditRole)}'")
    
    print("[2] Selecting A1...")
    selection = view.selectionModel()
    selection.select(idx_a1, QItemSelectionModel.SelectionFlag.Select)
    
    # 2. Simulate Delete Key
    print("[3] Pressing Delete Key...")
    event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Delete, Qt.KeyboardModifier.NoModifier)
    view.keyPressEvent(event)
    
    # Check if empty
    val_after = model.data(idx_a1, Qt.ItemDataRole.EditRole)
    if val_after == "" or val_after is None:
        print("PASS: Cell cleared.")
    else:
        print(f"FAIL: Cell content is '{val_after}'")
        return

    # 3. Simulate Undo
    print("[4] Executing Undo...")
    model.undo_stack.undo()
    
    val_undo = model.data(idx_a1, Qt.ItemDataRole.EditRole)
    if val_undo == "Delete Me":
        print("PASS: Undo successful.")
    else:
        print(f"FAIL: Undo content is '{val_undo}'")
        
    app.quit()

if __name__ == "__main__":
    verify_delete_key()
