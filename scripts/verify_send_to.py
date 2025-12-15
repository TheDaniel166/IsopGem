
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Add src to path
sys.path.append(os.path.abspath("src"))

from shared.ui.window_manager import WindowManager
from pillars.correspondences.ui.correspondence_hub import CorrespondenceHub
from shared.database import get_db_session
from pillars.correspondences.repos.table_repository import TableRepository

def verify_send_to():
    app = QApplication(sys.argv)
    
    # 1. Setup Window Manager
    wm = WindowManager()
    
    # 2. Simulate "Send to Emerald Tablet"
    # This acts as the sender code in another pillar
    print("Opening Hub...")
    hub = wm.open_window("emerald_tablet", CorrespondenceHub, allow_multiple=False, window_manager=wm)
    
    # 3. Simulate Data Transfer
    test_data = {
        "columns": ["Source", "Value"],
        "rows": [
            {"0": "External", "1": 123},
            {"0": "Signal", "1": 456}
        ],
        "styles": {}
    }
    
    print("Sending Data...")
    if hasattr(hub, "receive_import"):
        hub.receive_import("Test_Import_Signal", test_data)
        print("Data Sent.")
    else:
        print("FAIL: Hub does not have receive_import method.")
        return

    # 4. Verify DB Entry
    print("Verifying DB...")
    with get_db_session() as session:
        repo = TableRepository(session)
        # Find the table we just created
        tables = repo.get_all()
        found = False
        for t in tables:
            if t.name == "Test_Import_Signal":
                print(f"PASS: Found table '{t.name}' with ID {t.id}")
                # Verify Content
                if t.content['rows'][0]['1'] == 123:
                    print("PASS: Content verified.")
                else:
                    print(f"FAIL: Content mismatch. Got {t.content}")
                
                # Cleanup
                repo.delete(t.id)
                found = True
                break
        
        if not found:
            print("FAIL: Table not found in DB.")

    app.quit()

if __name__ == "__main__":
    verify_send_to()
