from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from core.calendar.calendar_base import CalendarBase
from core.calendar.dance_of_days import DanceOfDays
from PyQt5.QtCore import QDate
from datetime import date

class CalendarPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.initialize_dance_of_days()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.calendar = CalendarBase()
        layout.addWidget(self.calendar)
        self.setLayout(layout)
        
        # Connect to calendar page changes
        self.calendar.currentPageChanged.connect(self.update_cycle_markers)
        
    def initialize_dance_of_days(self):
        """Initialize Dance of Days cycle markers"""
        self.update_cycle_markers()
        
    def update_cycle_markers(self):
        """Update cycle markers for visible month"""
        self.calendar.clear_cycle_markers()
        
        # Get current month's date range
        current_page = self.calendar.selectedDate()
        start_date = QDate(current_page.year(), current_page.month(), 1)
        end_date = QDate(current_page.year(), current_page.month(), start_date.daysInMonth())
        
        # Mark each day in the month with its cycle info
        current = start_date
        while current <= end_date:
            py_date = date(current.year(), current.month(), current.day())
            cycle_info = DanceOfDays.get_cycle_info(py_date)
            self.calendar.mark_cycle_date(current, cycle_info)
            current = current.addDays(1) 