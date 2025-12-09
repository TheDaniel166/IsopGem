
import sys
import unittest
from PyQt6.QtWidgets import QApplication

# Mock dependnecies if needed, but integration test is better
# We just want to check if NatalChartWindow instantiates without error

def test_instantiation():
    app = QApplication(sys.argv)
    try:
        from pillars.astrology.ui.natal_chart_window import NatalChartWindow
        print("Import successful.")
        
        window = NatalChartWindow()
        print("Instantiation successful.")
        
        if not hasattr(window, '_init_service'):
            print("FAILURE: _init_service missing!")
            return False
            
        print("Verification passed.")
        return True
    except Exception as e:
        print(f"FAILURE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import os
    sys.path.append(os.path.join(os.getcwd(), "src"))
    success = test_instantiation()
    sys.exit(0 if success else 1)
