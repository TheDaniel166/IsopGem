
import sys
import os
import importlib.util
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication

# Mock dependencies
sys.modules["qtawesome"] = MagicMock()

# Ensure we can import from src
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src"))
sys.path.insert(0, SRC_PATH)

def import_dialog():
    file_path = os.path.join(SRC_PATH, "pillars/document_manager/ui/dialogs/special_characters_dialog.py")
    spec = importlib.util.spec_from_file_location("SpecialCharDialogModule", file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["SpecialCharDialogModule"] = module
    spec.loader.exec_module(module)
    return module.SpecialCharactersDialog

SpecialCharactersDialog = import_dialog()

def rite_of_special_chars():
    """
    Rite of Verification for the Special Characters Dialog.
    """
    print("Initiating Rite of Special Characters...")
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        dialog = SpecialCharactersDialog()
        print("[✓] Saturn: Dialog instantiated successfully.")
        
        # Check title
        if dialog.windowTitle() == "Insert Special Character":
            print("[✓] Sun: Title is correct.")
        else:
            print(f"[X] Sun: Title mismatch: '{dialog.windowTitle()}'")
            return False
            
        # Check sidebar exist
        # tab_count = dialog.tabs.count() -> Changed to category_list
        item_count = dialog.category_list.count()
        if item_count > 5:
            print(f"[✓] Venus: Categories loaded in Sidebar ({item_count} items).")
        else:
            print(f"[X] Venus: Too few categories ({item_count}).")
            return False
            
        # Check stylesheet applied (basic check)
        if "void slate" in dialog.styleSheet().lower() or "#0f172a" in dialog.styleSheet():
             print("[✓] Mars: Dark theme stylesheet detected.")
        else:
             print("[X] Mars: Stylesheet does not appear to contain dark theme colors.")
             # print(dialog.styleSheet())
             return False
             
        print("The Seals are Broken. The Dialog is operational.")
        return True
        
    except Exception as e:
        print(f"[X] Saturn: Verification failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = rite_of_special_chars()
    sys.exit(0 if success else 1)
