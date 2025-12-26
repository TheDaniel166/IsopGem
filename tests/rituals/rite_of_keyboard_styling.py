import sys
import os
from PyQt6.QtWidgets import QApplication, QPushButton
from PyQt6.QtCore import Qt, QPoint

from PyQt6.QtGui import QFontDatabase

# Ensure we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../src")))
import shared.ui.font_loader # To trigger load
from shared.ui.virtual_keyboard import VirtualKeyboard

def rite_of_keyboard_styling():
    """
    Rite of Verification for the Virtual Keyboard Refactoring.
    """
    print("Initiating Rite of Keyboard Styling...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Load fonts Manually for Test
    shared.ui.font_loader.load_custom_fonts()
    
    # Check Fonts
    families = QFontDatabase.families()
    if "Trigrammaton" in families:
        print("[✓] Mercury: Trigrammaton font loaded.")
    else:
        print("[X] Mercury: Trigrammaton font NOT found.")
        
    if "Astronomicon" in families:
        print("[✓] Mercury: Astronomicon font loaded.")
    else:
        print("[X] Mercury: Astronomicon font NOT found.")
        
    try:
        # Saturn Trial: Structure & Boundaries
        keyboard = VirtualKeyboard()
        print("[✓] Saturn: Keyboard instantiated successfully.")
        
        # Verify Window Flags (The Floating Temple)
        flags = keyboard.windowFlags()
        if flags & Qt.WindowType.FramelessWindowHint:
            print("[✓] Saturn: FramelessWindowHint set (The Tablet).")
        else:
            print("[X] Saturn: FramelessWindowHint MISSING!")
            return False

        # Verify Stylesheet content
        style = keyboard.styleSheet()
        if "QFrame#MainTablet" in style and "#0f172a" in style:
            print("[✓] Venus: Stylesheet contains 'MainTablet' and Void Slate color.")
        else:
            print("[X] Venus: Stylesheet validation failed.")
            return False

        # Sun Trial: Button Creation (Happy Path)
        # Check if keys exist
        buttons = keyboard.findChildren(QPushButton)
        if len(buttons) > 10:
             print(f"[✓] Sun: {len(buttons)} keys detected.")
        else:
             print(f"[X] Sun: Too few keys detected ({len(buttons)}).")
             return False
             
        # Check specific Liturgy constraints
        # Key Buttons should use Inter font
        key_btn = next((b for b in buttons if b.property("class") == "keyButton"), None)
        if key_btn:
            font = key_btn.font()
            if "Inter" in font.family():
                print("[✓] Venus: Key font set to Inter.")
            else:
                 print(f"[!] Venus: Key font is {font.family()}, expected 'Inter'. (Warning only, fallback might be active)")
        
        print("The Seals are Broken. The Visual Liturgy is honored.")
        
        # Mercury Trial: Custom Font Logic
        if "Trigrammaton" in families:
             # Switch layout and mock a click
             keyboard._switch_layout("trigrammaton")
             # Verify internal state (hard to verify UI output headless, but can check if method runs)
             print("[✓] Mercury: Switched to Trigrammaton layout.")
             
        return True
        
    except Exception as e:
        print(f"[X] Mars: The Rite failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = rite_of_keyboard_styling()
    sys.exit(0 if success else 1)
