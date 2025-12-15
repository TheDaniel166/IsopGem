
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QItemSelectionModel
from PyQt6.QtGui import QClipboard

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.ui.spreadsheet_window import SpreadsheetWindow

def verify_copy_paste():
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
    
    # 1. Setup Data: A1="Hello", B1="World"
    model.setData(model.index(0, 0), "Hello", Qt.ItemDataRole.EditRole)
    model.setData(model.index(0, 1), "World", Qt.ItemDataRole.EditRole)
    
    print("[1] Selecting A1:B1...")
    # Select Range
    selection = view.selectionModel()
    idx_a1 = model.index(0, 0)
    idx_b1 = model.index(0, 1)
    # Using Select | Rows causes full row selection, just select items
    # selection.select(idx_a1, QItemSelectionModel.SelectionFlag.Select)
    # selection.select(idx_b1, QItemSelectionModel.SelectionFlag.Select)
    
    # Correct way to select range programmatically?
    # view.setSelection(rect, flags) logic is internal.
    # manually using selection model
    selection.select(idx_a1, QItemSelectionModel.SelectionFlag.Select)
    selection.select(idx_b1, QItemSelectionModel.SelectionFlag.Select)
    
    print("[2] Executing Copy...")
    view._copy_selection()
    
    # Check Clipboard
    clipboard_text = QApplication.clipboard().text()
    expected = "Hello\tWorld"
    # Note: Might vary due to OS newlines, typically \n or \r\n
    # Strip helps, but tab check is key
    if expected in clipboard_text.replace('\r', ''):
        print(f"PASS: Clipboard content correct: {repr(clipboard_text)}")
    else:
        print(f"FAIL: Clipboard content mismatch: {repr(clipboard_text)}")
        return

    print("[3] Selecting A2 (Paste Target)...")
    idx_a2 = model.index(1, 0)
    view.setCurrentIndex(idx_a2)
    
    print("[4] Executing Paste...")
    view._paste_from_clipboard()
    
    # Check Data
    val_a2 = model.data(idx_a2, Qt.ItemDataRole.EditRole)
    val_b2 = model.data(model.index(1, 1), Qt.ItemDataRole.EditRole)
    
    if val_a2 == "Hello" and val_b2 == "World":
        print("PASS: Paste successful.")
    else:
        print(f"FAIL: Data Mismatch. A2='{val_a2}', B2='{val_b2}'")
        
    print("[5] Executing Undo...")
    model.undo_stack.undo()
    
    val_a2_undo = model.data(idx_a2, Qt.ItemDataRole.EditRole)
    if val_a2_undo in [None, ""]:
        print("PASS: Undo successful.")
    else:
        print(f"FAIL: Undo failed. A2='{val_a2_undo}'")
        
    app.quit()

if __name__ == "__main__":
    verify_copy_paste()
