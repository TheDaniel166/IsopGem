import sys
import os
import json
from unittest.mock import MagicMock
from datetime import datetime

# Mock pytz before imports
sys.modules["pytz"] = MagicMock()
sys.modules["requests"] = MagicMock()

from PyQt6.QtWidgets import QApplication

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from pillars.astrology.ui.planetary_positions_window import PlanetaryPositionsWindow, EphemerisRow
# We want to test if SpreadsheetModel crashes with the data
from pillars.correspondences.ui.spreadsheet_view import SpreadsheetModel

def test_send_to_emerald():
    app = QApplication(sys.argv)
    
    # Mock Window Manager and Hub
    mock_wm = MagicMock()
    mock_hub = MagicMock()
    
    def open_window_side_effect(window_type, window_class, **kwargs):
        if window_type == "emerald_tablet":
            return mock_hub
        return MagicMock()
    
    mock_wm.open_window.side_effect = open_window_side_effect
    
    # Initialize Window
    window = PlanetaryPositionsWindow(window_manager=mock_wm)
    
    # Simulate Data Generation
    ts = datetime(2025, 1, 1, 12, 0)
    window._latest_timestamps = [ts]
    window._latest_planet_labels = ["Sun", "Moon"]
    window._latest_planet_keys = ["sun", "moon"]
    window._latest_matrix = {
        ts: {
            "sun": EphemerisRow(ts, "Sun", 280.5, "Capricorn", False, 1.01),
            "moon": EphemerisRow(ts, "Moon", 15.2, "Aries", False, 13.2)
        }
    }
    
    # Trigger Send
    print("Simulating Send...")
    window._send_to_tablet()
    
    # Verify Hub Interaction
    mock_wm.open_window.assert_called()
    assert mock_wm.open_window.call_args[0][0] == "emerald_tablet"
    
    mock_hub.receive_import.assert_called()
    name, data = mock_hub.receive_import.call_args[0]
    
    print(f"Received Name: {name}")
    print(f"Received ID: {data['data'][0][0]}") # Should be timestamp
    print(f"Received Sun: {data['data'][0][1]}") # Should be formatted string
    
    # 1. Verify Structure
    assert name == "Planetary Positions Ephemeris"
    assert data["columns"] == ["Timestamp", "Sun", "Moon"]
    assert "2025-01-01" in data["data"][0][0]
    
    # 2. Verify JSON Serialization (Simulate DB Store)
    print("Verifying JSON serialization...")
    try:
        json_str = json.dumps(data)
        print("JSON Serialization OK")
    except Exception as e:
        print(f"FAILED JSON Serialization: {e}")
        raise e

    # 3. Verify SpreadsheetModel instantiation (Simulate Hub loading)
    print("Verifying SpreadsheetModel instantiation...")
    try:
        model = SpreadsheetModel(data)
        print(f"SpreadsheetModel initialized with {model.rowCount()} rows and {model.columnCount()} columns")
    except Exception as e:
        print(f"FAILED SpreadsheetModel init: {e}")
        raise e
    
    print("SUCCESS: Planetary send verification passed!")

from pillars.gematria.ui.batch_calculator_window import BatchCalculatorWindow

def test_batch_send():
    print("\n--- Testing Batch Calculator Send ---")
    app = QApplication.instance() or QApplication(sys.argv)
    
    mock_wm = MagicMock()
    mock_hub = MagicMock()
    
    def open_window_side_effect(window_type, window_class, **kwargs):
        if window_type == "emerald_tablet":
            return mock_hub
        return MagicMock()
    
    mock_wm.open_window.side_effect = open_window_side_effect
    
    # Initialize Windows
    # Calculators can be empty list for this test as we just import data
    window = BatchCalculatorWindow(calculators=[], window_manager=mock_wm)
    
    # Simulate Imported Data
    window.imported_data = [
        {"word": "test", "tags": "tag1", "notes": "note1"},
        {"word": "example", "tags": "", "notes": ""}
    ]
    
    # Trigger Send
    print("Simulating Batch Send...")
    window._send_to_emerald()
    
    # Verify Hub Interaction
    mock_wm.open_window.assert_called()
    assert mock_wm.open_window.call_args[0][0] == "emerald_tablet"
    
    mock_hub.receive_import.assert_called()
    name, data = mock_hub.receive_import.call_args[0]
    
    print(f"Received Name: {name}")
    print(f"Received Row 0: {data['data'][0]}")
    
    # Verify Structure
    assert "Batch_Import" in name
    assert data["columns"] == ["Word", "Tags", "Notes"]
    assert data["data"][0] == ["test", "tag1", "note1"]
    
    # Simulate 'rows' key mismatch (Regression Test)
    data["rows"] = data.pop("data")
    
    # Verify Model Init
    print("Verifying SpreadsheetModel instantiation for Batch data (with 'rows' key)...")
    try:
        model = SpreadsheetModel(data)
        print(f"SpreadsheetModel initialized with {model.rowCount()} rows")
        
        # Verify DisplayRole (Trigger Formula Engine)
        print("Verifying DisplayRole evaluation...")
        for r in range(min(5, model.rowCount())):
            for c in range(min(3, model.columnCount())):
                idx = model.index(r, c)
                val = model.data(idx, Qt.ItemDataRole.DisplayRole)
                # Just ensure it doesn't crash
    except Exception as e:
        print(f"FAILED SpreadsheetModel Evaluation: {e}")
        raise e
        
    print("SUCCESS: Batch send verification passed!")

if __name__ == "__main__":
    from PyQt6.QtCore import Qt # Import Qt for Role
    test_send_to_emerald()
    test_batch_send()
