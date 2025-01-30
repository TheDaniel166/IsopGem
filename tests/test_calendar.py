import sys
import os
from pathlib import Path

# Add virtual environment site-packages to Python path
venv_site_packages = Path(__file__).parent.parent / "venv" / "Lib" / "site-packages"
if venv_site_packages.exists():
    sys.path.insert(0, str(venv_site_packages))

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.workspace.document_manager.calendar_panel import CalendarPanel

class CalendarTest:
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        # Create and show calendar
        self.calendar_panel = CalendarPanel()
        
        # Add debug output for astronomical events
        current_year = self.calendar_panel.calendar.yearShown()
        current_month = self.calendar_panel.calendar.monthShown()
        events = self.calendar_panel.astronomical_events.get_events_for_month(current_year, current_month)
        
        print("\nAstronomical Events for current month:")
        for event_date, event_type, tooltip in events:
            print(f"Date: {event_date}, Type: {event_type.value}")
            print(f"Tooltip: {tooltip}\n")
        
        # Show calendar
        self.calendar_panel.show()
        self.calendar_panel.setWindowTitle("Calendar Test")
        self.calendar_panel.resize(800, 600)
        
    def run(self):
        return self.app.exec_()

def main():
    # Enable High DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # Create and run test
    test = CalendarTest()
    sys.exit(test.run())

if __name__ == "__main__":
    main() 