import sys
import os
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from pillars.gematria.ui.gematria_calculator_window import GematriaCalculatorWindow
from pillars.gematria.services.base_calculator import GematriaCalculator

# Mock Calculator
class MockCalculator(GematriaCalculator):
    @property
    def name(self):
        return "MockCalc"
    
    def calculate(self, text):
        return 123
        
    def get_breakdown(self, text):
        return [("A", 1), ("B", 2), ("C", 3)]
        
    def normalize_text(self, text):
        return text

    def _initialize_mapping(self):
        pass

def test_send_to_emerald():
    app = QApplication(sys.argv)
    
    # Mock Window Manager
    mock_wm = MagicMock()
    mock_hub = MagicMock()
    
    # Setup open_window mock to return mock_hub
    def open_window_side_effect(window_type, window_class, **kwargs):
        print(f"Opening window: {window_type}")
        if window_type == "emerald_tablet":
            return mock_hub
        return MagicMock()
    
    mock_wm.open_window.side_effect = open_window_side_effect
    
    # Init Window
    calc = MockCalculator()
    window = GematriaCalculatorWindow([calc], window_manager=mock_wm)
    
    # Simulate Calculation
    print("Simulating calculation...")
    # Inject export data manually to simulate successful calculation
    window.last_export_data = {
        "name": "Test_Calc",
        "data": {
            "columns": ["Character", "Value"],
            "data": [["A", "1"], ["TOTAL", "123"]],
            "styles": {}
        }
    }
    
    # Simulate Click
    print("Simulating 'Send to Tablet' click...")
    window._send_to_tablet()
    
    # Verify Window Manager called
    mock_wm.open_window.assert_called()
    call_args = mock_wm.open_window.call_args
    print(f"WindowManager.open_window called with: {call_args}")
    
    assert call_args[0][0] == "emerald_tablet", "Should open emerald_tablet"
    assert call_args[1].get('window_manager') == mock_wm, "Should pass window_manager to hub"
    
    # Verify Hub receive_import called
    mock_hub.receive_import.assert_called()
    hub_args = mock_hub.receive_import.call_args
    print(f"Hub.receive_import called with: {hub_args}")
    
    name, data = hub_args[0]
    assert name == "Test_Calc"
    assert data["data"][0][0] == "A"
    
    print("SUCCESS: Gematria 'Send to Emerald Tablet' verification passed!")

if __name__ == "__main__":
    test_send_to_emerald()
