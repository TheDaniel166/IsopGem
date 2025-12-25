import sys
import os

# Add src to path
project_root = '/home/burkettdaniel927/projects/isopgem'
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from PyQt6.QtWidgets import QApplication

def test_import():
    try:
        print(f"Attempting to import DocumentEditorWindow from pillars.document_manager.ui.document_editor_window")
        from pillars.document_manager.ui.document_editor_window import DocumentEditorWindow
        print("Import successful")
        
        # Also try to instantiate it (headless)
        app = QApplication(sys.argv)
        try:
            win = DocumentEditorWindow(parent=None)
            print("Instantiation successful")
        except Exception as e:
            print(f"Instantiation failed: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"Import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_import()
