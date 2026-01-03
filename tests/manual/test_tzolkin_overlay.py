
import sys
import os
from PyQt6.QtWidgets import QApplication

# Ensure project root is in path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

from src.pillars.time_mechanics.ui.tzolkin_window import TzolkinCalculatorWindow
from shared.services.ephemeris_provider import EphemerisProvider

def main():
    app = QApplication(sys.argv)
    
    # Pre-load ephemeris (mock or real)
    # For this test we assume EphemerisProvider works or fails gracefully
    try:
        provider = EphemerisProvider.get_instance()
        print("Ephemeris loaded:", provider.is_loaded())
    except Exception as e:
        print("Ephemeris load warn:", e)

    window = TzolkinCalculatorWindow()
    window.show()
    
    # Wait a bit to let threads finish
    # In a real manual test we'd just loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
