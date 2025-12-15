import sys
import os
import signal
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Mock Database before importing pillars that use it
from unittest.mock import MagicMock
import shared.database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import Models so they are registered in Base.metadata
from pillars.correspondences.models.correspondence_models import CorrespondenceTable

# 1. Setup In-Memory DB
engine = create_engine('sqlite:///:memory:')
shared.database.Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

# Patch get_db_session and SessionLocal in shared.database
shared.database.SessionLocal = SessionLocal
shared.database.get_db_session = MagicMock()
# We need get_db_session to act as a context manager
class MockSessionContext:
    def __init__(self):
        self.session = SessionLocal()
    def __enter__(self):
        return self.session
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

shared.database.get_db_session.side_effect = MockSessionContext

# Now import real components
from pillars.correspondences.ui.correspondence_hub import CorrespondenceHub
from pillars.gematria.ui.batch_calculator_window import BatchCalculatorWindow

def run_integration_test():
    print("Starting Integration Test...")
    app = QApplication(sys.argv)
    
    # Mock Window Manager just enough
    mock_wm = MagicMock()
    
    # Create Hub (Real)
    hub = CorrespondenceHub(window_manager=mock_wm)
    # Patch window manager to return our hub
    mock_wm.open_window.side_effect = lambda *args, **kwargs: hub
    
    # 2. Simulate Batch Send
    print("Simulating Batch Send IO...")
    
    # Data to send
    columns = ["Word", "Tags", "Notes"]
    rows = [["TestWord", "Tag", "Note"]]
    data = {"columns": columns, "data": rows, "styles": {}}
    
    # Call receive_import directly
    try:
        print("Calling hub.receive_import...")
        hub.receive_import("Test Import", data)
        print("receive_import returned.")
        
        # Check if window was launched
        print(f"Open windows: {len(hub.open_windows)}")
        if len(hub.open_windows) > 0:
            win = hub.open_windows[0]
            print(f"Window Title: {win.windowTitle()}")
            win.show()
            
            # 3. Wait a bit to ensure paint events happen
            def close_and_exit():
                print("Closing window and exiting...")
                win.close()
                app.quit()
                
            QTimer.singleShot(2000, close_and_exit)
            
        else:
            print("ERROR: No window launched!")
            sys.exit(1)
            
    except Exception as e:
        print(f"CRASH CAUGHT: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    # Run Event Loop
    print("Entering Event Loop...")
    app.exec()
    print("Test Finished Successfully.")

if __name__ == "__main__":
    run_integration_test()
