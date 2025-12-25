
import sys
import os
from PyQt6.QtWidgets import QApplication

# Ensure src is in pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from pillars.geometry.ui.geometry_calculator_window import GeometryCalculatorWindow
from pillars.geometry.services import GeometricShape, CircleShape

def verify_ui():
    print("Initializing QApplication...")
    app = QApplication(sys.path)
    
    print("Creating Shape...")
    shape = CircleShape()
    
    print("Initializing GeometryCalculatorWindow...")
    try:
        window = GeometryCalculatorWindow(shape)
        window.show()
        print(f"Window Title: {window.windowTitle()}")
        
        # Verify basic styling presence (simple check)
        style = window.styleSheet()
        # The window background is set via logic, usually empty string on widget unless set explicitly
        # But we can check if it crashed.
        
        print("✅ Window initialized successfully.")
        return 0
    except Exception as e:
        print(f"❌ Failed to initialize window: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(verify_ui())
