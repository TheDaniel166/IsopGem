
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.ui.spreadsheet_window import SpreadsheetWindow

def verify_sorting():
    app = QApplication(sys.argv)
    
    # Mock Data
    # Col 0: Numbers (unsorted)
    # Col 1: Strings (unsorted)
    content = {
        "columns": ["Num", "Str"],
        "data": [
            [10, "Z"],
            [2, "A"],
            [5, "M"],
            [100, "C"],
            [1, "B"]
        ],
        "styles": {}
    }
    
    window = SpreadsheetWindow(1, "TestSort", content, None)
    model = window.model
    
    # 1. Sort Column 0 (Num) Ascending
    print("Sorting Col 0 Ascending...")
    model.sort_range(0, 0, 4, 1, 0, ascending=True)
    
    # Check Result (Col 0 should be 1, 2, 5, 10, 100)
    data = [model.data(model.index(r, 0), Qt.ItemDataRole.EditRole) for r in range(5)]
    print(f"Col 0 Data: {data}")
    expected = ['1', '2', '5', '10', '100']
    
    if list(map(str, data)) == expected:
        print("PASS: Numeric Sort Ascending")
    else:
        print(f"FAIL: Expected {expected}, got {data}")
        
    # Check Col 1 Moved with it?
    # Original: 1->B, 2->A, 5->M, 10->Z, 100->C
    data_c1 = [model.data(model.index(r, 1), Qt.ItemDataRole.EditRole) for r in range(5)]
    print(f"Col 1 Data: {data_c1}")
    expected_c1 = ["B", "A", "M", "Z", "C"]
    if data_c1 == expected_c1:
        print("PASS: Row integrity maintained")
    else:
        print(f"FAIL: Row integrity broken. Got {data_c1}")

    # 2. Sort Column 1 (Str) Descending
    print("Sorting Col 1 Descending...")
    model.sort_range(0, 0, 4, 1, 1, ascending=False)
    
    # Expected: Z, M, C, B, A
    data_c1 = [model.data(model.index(r, 1), Qt.ItemDataRole.EditRole) for r in range(5)]
    print(f"Col 1 Data: {data_c1}")
    expected_desc = ["Z", "M", "C", "B", "A"]
    if data_c1 == expected_desc:
        print("PASS: String Sort Descending")
    else:
        print(f"FAIL: Expected {expected_desc}, got {data_c1}")
        
    # 3. Undo
    print("Testing Undo...")
    model.undo_stack.undo()
    # Should revert to previous state (Sorted by Num Asc)
    data_c1 = [model.data(model.index(r, 1), Qt.ItemDataRole.EditRole) for r in range(5)]
    if data_c1 == expected_c1:
        print("PASS: Undo worked")
    else:
        print(f"FAIL: Undo failed. Got {data_c1}")
        
    app.quit()

if __name__ == "__main__":
    verify_sorting()
