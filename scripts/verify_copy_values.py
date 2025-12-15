
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QItemSelectionModel
from PyQt6.QtGui import QClipboard

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.ui.spreadsheet_window import SpreadsheetWindow

def verify_copy_values():
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
    
    # 1. Setup Data: A1="=10+20"
    idx_a1 = model.index(0, 0)
    model.setData(idx_a1, "=10+20", Qt.ItemDataRole.EditRole)
    
    # Verify DisplayRole is evaluated
    display_val = model.data(idx_a1, Qt.ItemDataRole.DisplayRole)
    print(f"[1] A1 Edit: '=10+20' | Display: '{display_val}'")
    
    print("[2] Selecting A1...")
    selection = view.selectionModel()
    selection.select(idx_a1, QItemSelectionModel.SelectionFlag.Select)
    
    # 2. Test Normal Copy (Should be Formula)
    print("[3] Executing Standard Copy...")
    view._copy_selection()
    clip_std = QApplication.clipboard().text()
    if "=10+20" in clip_std:
        print(f"PASS: Standard Copy got formula: '{clip_std}'")
    else:
        print(f"FAIL: Standard Copy mismatch: '{clip_std}'")

    # 3. Test Copy Values (Should be Result)
    print("[4] Executing Copy Values...")
    view._copy_selection_values()
    clip_val = QApplication.clipboard().text()
    
    # Check if result (30) is in clipboard
    # Note: Formula result depends on engine. Assuming '30' or '30.0'
    if "30" in clip_val and "=" not in clip_val:
        print(f"PASS: Copy Values got result: '{clip_val}'")
    else:
        print(f"FAIL: Copy Values mismatch: '{clip_val}'")

    app.quit()

if __name__ == "__main__":
    verify_copy_values()
