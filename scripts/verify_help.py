
import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_help")

# Add src to path
project_root = '/home/burkettdaniel927/projects/isopgem'
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from PyQt6.QtWidgets import QApplication

def test_help_system():
    print("Testing Help System...")
    
    # 1. Test Librarian (Service)
    try:
        from shared.services.help_service import HelpService
        service = HelpService()
        print(f"Librarian initialized with root: {service.root_path}")
        
        service.index_content()
        toc = service.get_toc()
        print(f"TOC generated with {len(toc)} root topics.")
        
        # Verify manual index is there
        manual_found = False
        for topic in toc:
            print(f"- {topic.title} ({topic.id})")
            if "manual" in topic.id or "Manual" in topic.title:
                manual_found = True
                
        if manual_found:
            print("[PASS] Manual section found in TOC.")
        else:
            print("[WARN] Manual section NOT found in TOC (Result might be empty if wiki structure is flat/complex).")

        # Test Search
        results = service.search("Gematria")
        print(f"Search for 'Gematria' found {len(results)} results.")
        
    except Exception as e:
        print(f"[FAIL] Librarian Service failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # 2. Test Akaschic Archive (Window)
    try:
        app = QApplication(sys.argv)
        from shared.ui.help_window import HelpWindow
        
        window = HelpWindow()
        print("HelpWindow instantiated successfully.")
        
        # Check title
        if "Akaschic Archive" in window.windowTitle():
            print("[PASS] Window title correct.")
            
        # Check loading topic
        window._load_topic("manual/index.md")
        print("Loaded 'manual/index.md' into viewer.")
        
        # window.show()
        # sys.exit(app.exec())
        
    except Exception as e:
        print(f"[FAIL] Help Window failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_help_system()
