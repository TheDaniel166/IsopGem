
import sys
import os
import csv
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtCore import Qt

# Add src to path
sys.path.append(os.path.abspath("src"))

from pillars.correspondences.ui.spreadsheet_window import SpreadsheetWindow

def verify_csv_io():
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
    model = window.model
    
    # 1. Setup Data: A1="ExportMe", B1="=10+10"
    model.setData(model.index(0, 0), "ExportMe", Qt.ItemDataRole.EditRole)
    model.setData(model.index(0, 1), "=10+10", Qt.ItemDataRole.EditRole)
    
    temp_file = os.path.abspath("temp_verify_csv.csv")
    
    print("[1] Exporting to CSV...")
    # Mock QFileDialog.getSaveFileName
    with patch.object(QFileDialog, 'getSaveFileName', return_value=(temp_file, "CSV Files (*.csv)")):
        window._export_csv()
        
    # Verify Content on Disk
    if not os.path.exists(temp_file):
        print("FAIL: File not created.")
        return
        
    with open(temp_file, 'r', newline='') as f:
        content = f.read()
        print(f"DEBUG: File Content: {repr(content)}")
        if "ExportMe" in content and "=10+10" in content:
            print("PASS: Export contains correct data definitions.")
        else:
            print("FAIL: Export content mismatch.")
            return

    print("[2] Clearing Grid...")
    model.setData(model.index(0, 0), "", Qt.ItemDataRole.EditRole)
    model.setData(model.index(0, 1), "", Qt.ItemDataRole.EditRole)
    
    # Verify Clear
    if model.data(model.index(0, 0), Qt.ItemDataRole.EditRole) != "":
        print("FAIL: Failed to clear grid.")
        return
        
    print("[3] Importing CSV...")
    # Mock QFileDialog.getOpenFileName AND QMessageBox
    from PyQt6.QtWidgets import QMessageBox
    with patch.object(QFileDialog, 'getOpenFileName', return_value=(temp_file, "CSV Files (*.csv)")), \
         patch.object(QMessageBox, 'information') as mock_info:
        window._import_csv()
        
    # Verify Data Restored
    val_a1 = model.data(model.index(0, 0), Qt.ItemDataRole.EditRole)
    val_b1 = model.data(model.index(0, 1), Qt.ItemDataRole.EditRole)
    
    if val_a1 == "ExportMe" and val_b1 == "=10+10":
        print("PASS: Import Successful.")
    else:
        print(f"FAIL: Import Error. A1='{val_a1}', B1='{val_b1}'")
        
    # Cleanup
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    app.quit()

if __name__ == "__main__":
    verify_csv_io()
