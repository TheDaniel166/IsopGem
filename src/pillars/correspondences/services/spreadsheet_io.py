import csv
import json
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import Qt

class SpreadsheetIO:
    """
    Service for handling Spreadsheet Import/Export operations.
    Moved from SpreadsheetWindow to reduce complexity.
    """
    
    @staticmethod
    def export_csv(window, model):
        """Export grid to CSV."""
        path, _ = QFileDialog.getSaveFileName(window, "Export CSV", "", "CSV Files (*.csv)")
        if not path: return

        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                rows = model.rowCount()
                cols = model.columnCount()
                
                for r in range(rows):
                    row_data = []
                    for c in range(cols):
                        idx = model.index(r, c)
                        val = model.data(idx, Qt.ItemDataRole.EditRole)
                        row_data.append(val if val is not None else "")
                    writer.writerow(row_data)
                    
            QMessageBox.information(window, "Export Successful", f"Saved to {path}")
        except Exception as e:
            QMessageBox.critical(window, "Export Failed", str(e))

    @staticmethod
    def export_json(window, model):
        """Export grid to JSON."""
        path, _ = QFileDialog.getSaveFileName(window, "Export JSON", "", "JSON Files (*.json)")
        if not path: return
        
        try:
            # model.to_json() should exist on the model
            data = model.to_json()
            data['name'] = getattr(model, "scroll_name", "Sheet")

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            QMessageBox.information(window, "Export Successful", f"Saved to {path}")
        except Exception as e:
            QMessageBox.critical(window, "Export Failed", str(e))

    @staticmethod
    def export_image(window, view):
        """Export visible grid to PNG."""
        path, _ = QFileDialog.getSaveFileName(window, "Export Image", "", "PNG Files (*.png)")
        if not path: return
        
        try:
            pixmap = view.grab()
            pixmap.save(path)
            QMessageBox.information(window, "Export Successful", f"Saved to {path}")
        except Exception as e:
            QMessageBox.critical(window, "Export Failed", str(e))

    @staticmethod
    def import_csv(window, model):
        """Import CSV to grid (Resizes grid to fit)."""
        path, _ = QFileDialog.getOpenFileName(window, "Import CSV", "", "CSV Files (*.csv)")
        if not path: return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                data = list(reader)
                
            if not data: return
            
            r_count = len(data)
            c_count = max(len(row) for row in data)
            
            # Resize model if needed
            if r_count > model.rowCount():
                model.setRowCount(r_count)
            if c_count > model.columnCount():
                model.setColumnCount(c_count)
                
            for r, row in enumerate(data):
                for c, val in enumerate(row):
                    model.setData(model.index(r, c), val, Qt.ItemDataRole.EditRole)
                    
            QMessageBox.information(window, "Import Successful", f"Loaded {r_count}x{c_count} grid.")
            
        except Exception as e:
            QMessageBox.critical(window, "Import Failed", str(e))
