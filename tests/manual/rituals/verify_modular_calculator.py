import sys
import os
from PyQt6.QtWidgets import QApplication

# Ensure src is in pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from pillars.geometry.ui.calculator.calculator_window import GeometryCalculatorWindow
from pillars.geometry.services import CircleShape

def verify_modular_ui():
    print("🔮 Initializing QApplication...")
    app = QApplication(sys.path)
    
    print("📐 Creating Circle Shape...")
    shape = CircleShape()
    
    print("🏛️ Initializing Modular GeometryCalculatorWindow...")
    try:
        window = GeometryCalculatorWindow(shape)
        window.show()
        print(f"✅ Window Title: {window.windowTitle()}")
        
        # Check if ViewModel is initialized
        if not window.view_model:
            print("❌ ViewModel missing!")
            return 1
            
        print("✅ ViewModel verified.")
        
        # Check Panes
        if not (window.input_pane and window.viewport_pane and window.controls_pane):
            print("❌ One or more panes failed to initialize.")
            return 1
            
        print("✅ All Panes (Trinity) Initialized.")
        
        # Check Property Card creation (Input Pane logic)
        card_count = len(window.input_pane.cards)
        print(f"✅ Input Pane generated {card_count} Property Cards.")
        if card_count == 0:
            print("❌ Warning: No property cards generated.")
            
        print("✨ Verification Successful: The Schism is complete.")
        return 0
    except Exception as e:
        print(f"❌ Failed to initialize modular window: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(verify_modular_ui())
