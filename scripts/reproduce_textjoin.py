
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.ui.spreadsheet_window import SpreadsheetWindow

def reproduce_textjoin():
    app = QApplication(sys.argv)
    
    # Mock Data
    content = {
        "columns": [f"Col{i}" for i in range(5)],
        "data": [["" for _ in range(5)] for _ in range(5)],
        "styles": {}
    }
    repo = None
    
    window = SpreadsheetWindow(1, "Test Table", content, repo)
    model = window.model
    
    # Setup B4, C4 (Indices: Row 3, Cols 1, 2)
    # B4 = "sgadfgsf"
    model.setData(model.index(3, 1), "sgadfgsf", Qt.ItemDataRole.EditRole)
    # C4 = "sgadf"
    model.setData(model.index(3, 2), "sgadf", Qt.ItemDataRole.EditRole)
    
    # Setup D4 Formula: =TEXTJOIN(and, B4, C4)
    # Note: 'and' is unquoted.
    formula = "=TEXTJOIN(and, B4, C4)"
    idx_d4 = model.index(3, 3)
    model.setData(idx_d4, formula, Qt.ItemDataRole.EditRole)
    
    # Check Result
    result = model.data(idx_d4, Qt.ItemDataRole.DisplayRole)
    print(f"Formula: '{formula}'")
    print(f"Result: '{result}'")
    
    # Check what happens if we join to make a formula string
    # E4 = "="
    # F4 = "SUM(1,1)"
    model.setData(model.index(3, 4), "=", Qt.ItemDataRole.EditRole)
    model.setData(model.index(3, 5), "SUM(1,1)", Qt.ItemDataRole.EditRole)
    
    # G4 = TEXTJOIN("", 1, E4, F4) -> "=SUM(1,1)"
    formula_g4 = '=TEXTJOIN("", 1, E4, F4)'
    idx_g4 = model.index(3, 6) # G4 (Row 3, Col 6) - wait, col count is 5 (0-4). Need resize.
    model.insertColumns(5, 5)
    
    idx_g4 = model.index(3, 6)
    model.setData(idx_g4, formula_g4, Qt.ItemDataRole.EditRole)
    
    res_g4 = model.data(idx_g4, Qt.ItemDataRole.DisplayRole)
    print(f"Formula G4: '{formula_g4}'")
    print(f"Result G4: '{res_g4}'")
    
    app.quit()

if __name__ == "__main__":
    reproduce_textjoin()
