
import sys
import os
from PyQt6.QtWidgets import QApplication, QMenu
from PyQt6.QtCore import Qt, QPoint

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.ui.spreadsheet_window import SpreadsheetWindow

def verify_context_menu():
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

    # Monkey patch QMenu.exec to capture actions instead of blocking
    original_exec = QMenu.exec
    
    found_actions = []

    def mocked_exec(self, pos=None):
        nonlocal found_actions
        for action in self.actions():
            found_actions.append(action.text())
        return None # mimic cancellation

    QMenu.exec = mocked_exec
    
    print("[1] Triggering Cell Context Menu...")
    # Trigger menu at 10, 10
    view._show_cell_menu(QPoint(10, 10))
    
    print(f"DEBUG: Found Actions: {found_actions}")
    
    if "Copy" in found_actions and "Paste" in found_actions:
        print("PASS: Copy and Paste actions found in menu.")
    else:
        print("FAIL: Copy/Paste actions missing.")

    app.quit()

if __name__ == "__main__":
    verify_context_menu()
