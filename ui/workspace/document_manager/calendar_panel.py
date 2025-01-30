from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from core.calendar.calendar_base import CalendarBase
from PyQt5.QtCore import QDate, QSize
from datetime import date
from core.calendar.dance_of_days import DanceOfDays
from core.calendar.astronomical_events import AstronomicalEvents

class CalendarPanel(QWidget):
    """Calendar panel for document management"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.astronomical_events = AstronomicalEvents()  # Initialize astronomical events
        self.setup_ui()
        self.initialize_dance_of_days()
        self.update_astronomical_events()  # Add this line to initialize astronomical events
        
    def setup_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Calendar")
        header.setObjectName("panelHeader")
        layout.addWidget(header)
        
        # Calendar widget
        self.calendar = CalendarBase()
        
        # Set size policies
        self.calendar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.calendar.setMinimumSize(QSize(600, 400))  # Set minimum size
        
        # Set current date to today
        today = QDate.currentDate()
        self.calendar.setSelectedDate(today)
        self.calendar.showToday()  # Ensure today is visible
        
        # Connect signals
        self.calendar.currentPageChanged.connect(self.update_cycle_markers)  # Month change
        self.calendar.selectionChanged.connect(self.update_cycle_markers)    # Date selection
        self.calendar.currentPageChanged.connect(self.update_astronomical_events)  # Month change
        
        layout.addWidget(self.calendar)
        
        # Set panel size policies
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(QSize(650, 500))  # Set minimum panel size
        
        self.setLayout(layout)
        
    def initialize_dance_of_days(self):
        """Initialize Dance of Days cycle markers"""
        self.update_cycle_markers()
        
    def update_cycle_markers(self):
        """Update cycle markers for visible month"""
        self.calendar.clear_cycle_markers()
        
        # Get visible month's date range
        current_month = self.calendar.monthShown()
        current_year = self.calendar.yearShown()
        start_date = QDate(current_year, current_month, 1)
        end_date = QDate(current_year, current_month, start_date.daysInMonth())
        
        # Mark each day in the month with its cycle info
        current = start_date
        while current <= end_date:
            py_date = date(current.year(), current.month(), current.day())
            cycle_info = DanceOfDays.get_cycle_info(py_date)
            self.calendar.mark_cycle_date(current, cycle_info)
            current = current.addDays(1)

    def update_astronomical_events(self):
        """Update astronomical events for current month"""
        current_year = self.calendar.yearShown()
        current_month = self.calendar.monthShown()
        
        # Clear previous astronomical events
        self.calendar.astronomical_events.clear()
        if hasattr(self.calendar, 'event_tooltips'):
            self.calendar.event_tooltips.clear()
        
        # Get events for current month
        events = self.astronomical_events.get_events_for_month(current_year, current_month)
        
        # Mark events on calendar with tooltips
        for event_date, event_type, tooltip in events:
            qdate = QDate(event_date.year, event_date.month, event_date.day)
            self.calendar.mark_astronomical_event(qdate, event_type, tooltip)
        
        # Force update of calendar display
        self.calendar.updateCells() 