import sys
import os
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from pillars.gematria.ui.batch_calculator_window import BatchCalculatorWindow

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
    # Mock calculators list
    window = BatchCalculatorWindow(calculators=[], window_manager=mock_wm)
    
    # Simulate Import
    window.imported_data = [
        {"word": "Test1", "tags": "tag1", "notes": "note1"},
        {"word": "Test2", "tags": "tag2", "notes": "note2"}
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
    
    assert "Batch_Import" in name
    assert data["columns"] == ["Word", "Tags", "Notes"]
    assert data["data"][0][0] == "Test1"
    assert data["data"][0][2] == "note1"
    
    print("SUCCESS: Batch send verification passed!")

if __name__ == "__main__":
    test_send_to_emerald()
