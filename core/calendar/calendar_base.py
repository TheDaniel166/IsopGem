from PyQt5.QtWidgets import QCalendarWidget, QToolTip
from PyQt5.QtCore import QDate, Qt, pyqtSignal, QRect, QPoint, QRectF
from PyQt5.QtGui import (QPainter, QColor, QTextCharFormat, QPen, QBrush, 
                        QLinearGradient, QPainterPath, QFont, QIcon)
from datetime import datetime, date
from core.calendar.astronomical_events import AstronomicalEvents
from pathlib import Path

class CalendarBase(QCalendarWidget):
    """
    Enhanced calendar widget with support for:
    - Custom date highlighting
    - Cycle overlays
    - Event tracking
    """
    date_clicked = pyqtSignal(QDate)  # Signal when date is clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
        self.initialize_formats()
        self.load_icons()
        
        # Track special dates and cycles
        self.highlighted_dates = {}      # date -> format
        self.cycle_markers = {}          # date -> cycle info
        self.astronomical_events = {}    # date -> event type
        
        # Modern styling
        self.setStyleSheet("""
            QCalendarWidget {
                background-color: #f5f5f5;
                color: #333333;
            }
            QCalendarWidget QToolButton {
                color: #333333;
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px;
                margin: 2px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
            }
            QCalendarWidget QMenu {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #e0e0e0;
            }
            QCalendarWidget QSpinBox {
                color: #333333;
                background-color: #ffffff;
                selection-background-color: #e0e0e0;
                selection-color: #333333;
            }
            QCalendarWidget QTableView {
                background-color: #ffffff;
                selection-background-color: #f0f0f0;
            }
        """)
        
        self.setMouseTracking(True)  # Enable mouse tracking
        self.mouse_pos = QPoint()
        self.hovered_date = None
        
    def setup_ui(self):
        """Initialize calendar UI"""
        self.setGridVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.setHorizontalHeaderFormat(QCalendarWidget.SingleLetterDayNames)
        self.setNavigationBarVisible(True)
        
        # Remove or adjust minimum date to allow navigation before 1904
        self.setMinimumDate(QDate(1, 1, 1))  # Allow dates back to year 1
        
    def setup_connections(self):
        """Setup signal connections"""
        self.clicked.connect(self.handle_date_click)
        self.currentPageChanged.connect(self.update_display)
        
    def initialize_formats(self):
        """Initialize text formats for different date types"""
        # Regular day format
        self.default_format = QTextCharFormat()
        
        # Cycle day format
        self.cycle_format = QTextCharFormat()
        self.cycle_format.setBackground(QColor(200, 230, 250))
        
        # Special day format
        self.special_format = QTextCharFormat()
        self.special_format.setBackground(QColor(250, 200, 200))
        
        # Add astronomical event formats
        self.new_moon_format = QTextCharFormat()
        self.new_moon_format.setBackground(QColor(0, 0, 0, 30))
        
        self.full_moon_format = QTextCharFormat()
        self.full_moon_format.setBackground(QColor(255, 255, 200, 30))
        
        self.solstice_format = QTextCharFormat()
        self.solstice_format.setBackground(QColor(255, 200, 0, 30))
        
        self.equinox_format = QTextCharFormat()
        self.equinox_format.setBackground(QColor(0, 255, 0, 30))
        
    def handle_date_click(self, date):
        """Handle date selection"""
        self.date_clicked.emit(date)
        
    def update_display(self):
        """Update calendar display when month/year changes"""
        self.updateCells()
        
    def paintCell(self, painter, rect, date):
        """Custom cell painting for dates"""
        painter.save()
        
        # Draw card-like background
        painter.setPen(QPen(QColor("#e0e0e0")))
        bg_rect = rect.adjusted(1, 1, -1, -1)
        painter.fillRect(bg_rect, QColor("#ffffff"))
        painter.drawRect(bg_rect)
        
        # Draw astronomical event if exists (as background)
        if date in self.astronomical_events:
            self.paint_astronomical_event(painter, rect, self.astronomical_events[date])
        
        # Date number in top-left
        painter.setPen(QColor("#333333"))
        date_font = painter.font()
        date_font.setPointSize(9)
        painter.setFont(date_font)
        date_rect = rect.adjusted(4, 2, 0, 0)
        painter.drawText(date_rect, Qt.AlignLeft | Qt.AlignTop, str(date.day()))
        
        # Draw detail button in top-right
        detail_rect = QRect(rect.right() - 20, rect.top() + 2, 16, 16)
        if self._is_mouse_over_detail_button(date):
            painter.fillRect(detail_rect, QColor("#e0e0e0"))
        painter.drawRect(detail_rect)
        painter.drawText(detail_rect, Qt.AlignCenter, "...")
        
        # Draw cycle info if exists
        if date in self.cycle_markers:
            cycle_info = self.cycle_markers[date]
            self.paint_cycle_marker(painter, rect, cycle_info)
        
        # Draw any additional info summary
        if date in self.highlighted_dates:
            self.paint_summary_info(painter, rect.adjusted(4, 24, -4, -4))
        
        painter.restore()
        
    def paint_cycle_marker(self, painter, rect, cycle_info):
        """Paint Dance of Days cycle marker"""
        if isinstance(cycle_info, tuple) and len(cycle_info) == 2:
            cycle_number, day_in_cycle = cycle_info
            
            # Create info box
            info_rect = rect.adjusted(4, rect.height() - 20, -4, -4)
            # Convert QRect to QRectF
            info_rectf = QRectF(info_rect)
            painter.setPen(Qt.NoPen)
            
            # Gradient background
            gradient = QLinearGradient(info_rect.topLeft(), info_rect.bottomRight())
            gradient.setColorAt(0, QColor(100, 149, 237, 50))  # Cornflower blue
            gradient.setColorAt(1, QColor(100, 149, 237, 30))
            
            # Draw rounded info box using QRectF
            path = QPainterPath()
            path.addRoundedRect(info_rectf, 3.0, 3.0)  # Use floating point values
            painter.fillPath(path, gradient)
            
            # Draw text
            painter.setPen(QColor("#333333"))
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            text = f"C{cycle_number}·D{day_in_cycle}"
            painter.drawText(info_rect, Qt.AlignCenter, text)

    def paint_summary_info(self, painter, rect):
        """Paint summary information for the day"""
        info = self.highlighted_dates[date].get('summary', '')
        if info:
            painter.setPen(QColor("#666666"))
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignLeft | Qt.TextWordWrap, info)
        
    def highlight_date(self, date, format=None):
        """Highlight specific date with given format"""
        if format is None:
            format = self.special_format
        self.highlighted_dates[date] = format
        self.updateCell(date)
        
    def clear_highlights(self):
        """Clear all date highlights"""
        self.highlighted_dates.clear()
        self.updateCells()
        
    def mark_cycle_date(self, date, cycle_info):
        """Mark date as part of a cycle"""
        self.cycle_markers[date] = cycle_info
        self.updateCell(date)
        
    def clear_cycle_markers(self):
        """Clear all cycle markers"""
        self.cycle_markers.clear()
        self.updateCells()
        
    def get_selected_date(self):
        """Get currently selected date as Python date object"""
        qdate = self.selectedDate()
        return date(qdate.year(), qdate.month(), qdate.day())
        
    def set_date(self, python_date):
        """Set date from Python date object"""
        qdate = QDate(python_date.year, python_date.month, python_date.day)
        self.setSelectedDate(qdate)
        
    def mouseMoveEvent(self, event):
        """Track mouse position for hover effects and show tooltips"""
        self.mouse_pos = event.pos()
        date = self.dateAt(event.pos())
        
        if date and date in self.astronomical_events:
            event_type = self.astronomical_events[date]
            if hasattr(self, 'event_tooltips') and date in self.event_tooltips:
                tooltip_text = self.event_tooltips[date]
                print(f"Showing tooltip for {date}: {tooltip_text}")  # Debug print
                rect = self.dateRectAt(date)
                if rect:
                    pos = self.mapToGlobal(QPoint(rect.center().x(), rect.top()))
                    QToolTip.showText(pos, tooltip_text, self, rect, 10000)
        elif QToolTip.isVisible():
            QToolTip.hideText()
        
        self.hovered_date = date
        self.updateCell(date)
        super().mouseMoveEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leaving widget"""
        if self.hovered_date:
            old_date = self.hovered_date
            self.hovered_date = None
            self.updateCell(old_date)
            QToolTip.hideText()
        super().leaveEvent(event)
        
    def _is_mouse_over_detail_button(self, date):
        """Check if mouse is over detail button of given date"""
        if date != self.hovered_date:
            return False
            
        # Get cell rect for the date
        rect = self.dateRectAt(date)
        if not rect:
            return False
            
        # Define detail button rect
        detail_rect = QRect(rect.right() - 20, rect.top() + 2, 16, 16)
        return detail_rect.contains(self.mouse_pos)
        
    def dateAt(self, pos):
        """Get date at given position"""
        for r in range(self.rowCount()):
            for c in range(self.columnCount()):
                cell_rect = self.cellRect(r, c)
                if cell_rect.contains(pos):
                    grid = self.monthGrid()
                    if 0 <= r < len(grid) and 0 <= c < 7:
                        return grid[r][c]
        return None
        
    def dateFromCell(self, row, col):
        """Get date from grid position"""
        grid = self.monthGrid()
        if 0 <= row < len(grid) and 0 <= col < 7:
            return grid[row][col]
        return None
        
    def monthGrid(self):
        """Get current month as grid of dates"""
        grid = []
        current = self.firstDayOfMonth()
        
        # Find first day of grid (might be in previous month)
        while current.dayOfWeek() != 1:  # Start with Monday
            current = current.addDays(-1)
            
        # Build 6-week grid
        for r in range(6):
            row = []
            for c in range(7):
                row.append(current)
                current = current.addDays(1)
            grid.append(row)
            
        return grid
        
    def firstDayOfMonth(self):
        """Get first day of current month"""
        return QDate(self.yearShown(), self.monthShown(), 1)
        
    def dateRectAt(self, date):
        """Get rectangle for given date"""
        if not date:
            return None
            
        grid = self.monthGrid()
        for r, row in enumerate(grid):
            for c, cell_date in enumerate(row):
                if cell_date == date:
                    return self.cellRect(r, c)
        return None
        
    def cellRect(self, row, col):
        """Get rectangle for grid cell"""
        width = self.width() / 7
        height = (self.height() - self.yearShown()) / 6  # Adjust for header
        
        x = col * width
        y = row * height + self.yearShown()  # Adjust for header
        
        return QRect(int(x), int(y), int(width), int(height))
        
    def rowCount(self):
        """Get number of rows in calendar grid"""
        return 6  # Standard calendar month view has 6 rows
        
    def columnCount(self):
        """Get number of columns in calendar grid"""
        return 7  # 7 days per week 

    def mark_astronomical_event(self, date, event_type, tooltip):
        """Mark date with astronomical event and tooltip"""
        self.astronomical_events[date] = event_type
        if not hasattr(self, 'event_tooltips'):
            self.event_tooltips = {}
        self.event_tooltips[date] = tooltip
        self.updateCell(date)

    def paint_astronomical_event(self, painter, rect, event_type):
        """Paint astronomical event as icon or fallback to shapes"""
        # Increase icon size
        icon_size = 24  # Increased from 16
        center_x = rect.center().x() - icon_size/2
        center_y = rect.center().y() - icon_size/2 - 10
        
        if hasattr(self, 'astro_icons') and event_type in self.astro_icons:
            icon = self.astro_icons[event_type]
            icon.paint(painter, int(center_x), int(center_y), icon_size, icon_size)
        else:
            # Fallback shapes (adjusted for larger size)
            center_x = rect.center().x()
            center_y = rect.center().y() - 10
            size = icon_size
            painter.setPen(Qt.NoPen)
            
            if event_type == AstronomicalEvents.EventType.NEW_MOON:
                painter.setBrush(QColor(0, 0, 0, 30))
                painter.drawEllipse(center_x - size/2, center_y - size/2, size, size)
            elif event_type == AstronomicalEvents.EventType.FULL_MOON:
                painter.setBrush(QColor(255, 255, 200, 30))
                painter.drawEllipse(center_x - size/2, center_y - size/2, size, size)
            elif event_type == AstronomicalEvents.EventType.EQUINOX:
                # Equinox - green diamond
                painter.setBrush(QColor(0, 255, 0, 30))
                path = QPainterPath()
                path.moveTo(center_x, center_y - size/2)
                path.lineTo(center_x + size/2, center_y)
                path.lineTo(center_x, center_y + size/2)
                path.lineTo(center_x - size/2, center_y)
                path.closeSubpath()
                painter.fillPath(path, painter.brush())
            
            elif event_type == AstronomicalEvents.EventType.SOLSTICE:
                # Solstice - orange square
                painter.setBrush(QColor(255, 200, 0, 30))
                painter.drawRect(center_x - size/2, center_y - size/2, size, size) 

    def load_icons(self):
        """Load astronomical event icons"""
        icon_path = Path("assets/icons/astronomy")
        
        # Ensure directory exists
        if not icon_path.exists():
            return
        
        # Try loading each icon with error handling
        self.astro_icons = {}
        icon_files = {
            AstronomicalEvents.EventType.NEW_MOON: "new_moon.png",
            AstronomicalEvents.EventType.FULL_MOON: "full_moon.png",
            AstronomicalEvents.EventType.EQUINOX: "equinox.png",
            AstronomicalEvents.EventType.SOLSTICE: "solstice.png"
        }
        
        for event_type, filename in icon_files.items():
            icon_file = icon_path / filename
            if icon_file.exists():
                icon = QIcon(str(icon_file))
                if not icon.isNull():
                    self.astro_icons[event_type] = icon 