import sys
import os
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from pillars.gematria.ui.text_analysis.main_window import TextAnalysisWindow
from pillars.gematria.services.base_calculator import GematriaCalculator

def test_send_search_to_emerald():
    app = QApplication(sys.argv)
    
    # Mock Window Manager and Hub
    mock_wm = MagicMock()
    mock_hub = MagicMock()
    
    def open_window_side_effect(window_type, window_class, **kwargs):
        if window_type == "emerald_tablet":
            return mock_hub
        return MagicMock()
    
    mock_wm.open_window.side_effect = open_window_side_effect
    
    # Mock Calculator
    calc = MagicMock(spec=GematriaCalculator)
    calc.name = "Test Calculator"
    
    # Initialize Window
    window = TextAnalysisWindow(calculators=[calc], window_manager=mock_wm)
    
    # Set mock search value
    window.search_panel.value_input.setText("123")
    
    # Simulate matches
    # Format: (text, start, end, doc_title, tab_index)
    matches = [
        ("Test Match 1", 10, 20, "Doc A", 0),
        ("Test Match 2", 30, 40, "Doc B", 1)
    ]
    
    # Trigger Send
    print("Simulating Search Result Send...")
    window._on_send_search_to_emerald(matches)
    
    # Verify Hub Interaction
    mock_wm.open_window.assert_called()
    assert mock_wm.open_window.call_args[0][0] == "emerald_tablet"
    
    mock_hub.receive_import.assert_called()
    name, data = mock_hub.receive_import.call_args[0]
    
    print(f"Received Name: {name}")
    print(f"Received Row 0: {data['data'][0]}")
    
    assert "Search_Results_123" in name
    assert data["columns"] == ["Text", "Document", "Start", "End", "Target Value"]
    assert data["data"][0][0] == "Test Match 1"
    assert data["data"][0][1] == "Doc A"
    assert data["data"][0][4] == "123"
    
    print("SUCCESS: Text Analysis send verification passed!")

if __name__ == "__main__":
    test_send_search_to_emerald()
