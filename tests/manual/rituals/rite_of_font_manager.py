
import sys
import os
import importlib.util
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication

# Ensure we can import from src
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
sys.path.insert(0, SRC_PATH)

from shared.ui import font_loader

# Dynamically import FontManagerWindow to bypass package __init__ dependencies
def import_font_manager_window():
    file_path = os.path.join(SRC_PATH, "pillars/document_manager/ui/font_manager_window.py")
    spec = importlib.util.spec_from_file_location("FontManagerWindowModule", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["FontManagerWindowModule"] = module
    spec.loader.exec_module(module)
    return module.FontManagerWindow

FontManagerWindow = import_font_manager_window()

def rite_of_font_manager():
    """
    Rite of Verification for the Font Manager Utility.
    """
    print("Initiating Rite of Font Manager...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Mercury: Load Fonts
    print("[*] Mercury: Loading fonts...")
    font_loader.load_custom_fonts()
    if font_loader.LOADED_FONTS:
        print(f"[✓] Mercury: Loaded {len(font_loader.LOADED_FONTS)} fonts: {font_loader.LOADED_FONTS}")
    else:
        print("[!] Mercury: No fonts loaded (check assets directory).")
        
    # Saturn: Instantiate Window
    try:
        window = FontManagerWindow()
        print("[✓] Saturn: FontManagerWindow instantiated successfully.")
    except Exception as e:
        print(f"[X] Saturn: Failed to instantiate window: {e}")
        return False
        
    # Venus: Check UI Elements
    if window.font_list.count() == len(font_loader.LOADED_FONTS) or (not font_loader.LOADED_FONTS and window.font_list.count() == 1):
        print(f"[✓] Venus: Font list populated correctly ({window.font_list.count()} items).")
    else:
        print(f"[X] Venus: Font list count mismatch. Expected {len(font_loader.LOADED_FONTS)}, got {window.font_list.count()}.")
        return False
        
    # Sun: Check Preview logic
    if font_loader.LOADED_FONTS:
        target_font = font_loader.LOADED_FONTS[0]
        window._render_preview(target_font)
        html = window.preview_area.toHtml()
        if target_font in html:
            print("[✓] Sun: Preview generated successfully containing font name.")
        else:
            print("[X] Sun: Preview HTML does not contain target font name.")
            return False
            
    print("The Seals are Broken. The Font Manager is operational.")
    return True

if __name__ == "__main__":
    success = rite_of_font_manager()
    sys.exit(0 if success else 1)
