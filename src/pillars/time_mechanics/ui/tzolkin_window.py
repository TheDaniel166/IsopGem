"""
Tzolkin Calculator Window - The Harmonic Grid.
Window for calculating and navigating Tzolkin dates with interactive 13x20 grid.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QDateEdit, QFrame, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
from datetime import date, timedelta
from ..services.tzolkin_service import TzolkinService
from ..models.tzolkin_models import TzolkinDate

class TzolkinCalculatorWindow(QWidget):
    """
    Window for calculating and displaying Tzolkin dates.
    Allows navigation through the harmonic cycles via Grid or Buttons.
    """
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Tzolkin Calculator")
        self.resize(1600, 1000)
        
        self.service = TzolkinService()
        self.current_date = date.today()
        
        # Precompute Kin Map: (Tone, Sign) -> (Kin, Ditrune)
        # We need this to quickly find which date to jump to when a cell is clicked.
        self._kin_map = {} # (tone, sign) -> kin
        for k in range(1, 261):
            t = (k - 1) % 13 + 1
            s = (k - 1) % 20 + 1
            self._kin_map[(t, s)] = k
        
        self._setup_ui()
        self._populate_grid()
        self._refresh_display()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # --- Header ---
        header_layout = QHBoxLayout()
        header_label = QLabel("Thelemic Tzolkin Calculator")
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        # Date Nav
        self.prev_btn = QPushButton("◀")
        self.prev_btn.setFixedWidth(30)
        self.prev_btn.clicked.connect(self._prev_day)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.dateChanged.connect(self._on_date_changed)
        self.date_edit.setFixedWidth(120)
        
        self.next_btn = QPushButton("▶")
        self.next_btn.setFixedWidth(30)
        self.next_btn.clicked.connect(self._next_day)
        
        self.today_btn = QPushButton("Today")
        self.today_btn.clicked.connect(self._go_today)
        
        header_layout.addWidget(self.prev_btn)
        header_layout.addWidget(self.date_edit)
        header_layout.addWidget(self.next_btn)
        header_layout.addWidget(self.today_btn)
        
        layout.addLayout(header_layout)
        
        # --- Main Content Split ---
        content_layout = QHBoxLayout()
        layout.addLayout(content_layout)
        
        # Left: Info Card
        self.card_frame = QFrame()
        self.card_frame.setFixedWidth(400)
        self.card_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 10px;
                border: 1px solid #e2e8f0;
            }
        """)
        card_layout = QVBoxLayout(self.card_frame)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(15)
        
        # Kin Number
        self.kin_label = QLabel("Kin 1")
        self.kin_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.kin_label.setStyleSheet("font-size: 14pt; color: #64748b; font-weight: bold; background: transparent; border: none;")
        card_layout.addWidget(self.kin_label)
        
        # Tone & Sign
        self.main_label = QLabel("1 Imix")
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_label.setStyleSheet("font-size: 24pt; color: #0f172a; font-weight: bold; background: transparent; border: none;")
        self.main_label.setWordWrap(True)
        card_layout.addWidget(self.main_label)
        
        # Cycle Information
        self.cycle_label = QLabel("Cycle 1")
        self.cycle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cycle_label.setStyleSheet("font-size: 11pt; color: #94a3b8; background: transparent; border: none;")
        self.cycle_label.setWordWrap(True)
        card_layout.addWidget(self.cycle_label)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #cbd5e1; border: none;")
        card_layout.addWidget(line)
        
        # Ditrune Info
        self.ditrune_label = QLabel("Ditrune: 49\n(001211)")
        self.ditrune_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ditrune_label.setStyleSheet("font-size: 14pt; color: #3b82f6; font-family: monospace; background: transparent; border: none;")
        card_layout.addWidget(self.ditrune_label)
        
        card_layout.addStretch()
        content_layout.addWidget(self.card_frame)
        
        # Right: The 20x13 Grid
        # Rows = Signs (1-20), Cols = Tones (1-13)
        self.grid_table = QTableWidget(20, 13)
        self.grid_table.horizontalHeader().setVisible(False)
        self.grid_table.verticalHeader().setVisible(False)
        self.grid_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.grid_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.grid_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.grid_table.cellClicked.connect(self._on_cell_clicked)
        
        # Custom Style for Grid
        self.grid_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                gridline-color: #f1f5f9;
                background-color: white;
            }
            QTableWidget::item {
                border: none;
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3b82f6;
                color: white;
            }
        """)
        
        content_layout.addWidget(self.grid_table)

    def _populate_grid(self):
        """Populate the 20x13 grid with Ditrune values."""
        # Row = Sign (0-19), Col = Tone (0-12)
        
        # Font for cells
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        
        # We need the service's internal grid.
        # Logic: service._decimal_grid[sign_idx][tone_idx]
        # Our UI Grid: item(row=sign_idx, col=tone_idx)
        
        for sign_idx in range(20):
            for tone_idx in range(13):
                # Retrieve value from Service logic (Sign x Tone)
                if self.service._decimal_grid:
                    try:
                        val = self.service._decimal_grid[sign_idx][tone_idx]
                        text = str(val)
                    except IndexError:
                        text = "?"
                else:
                    text = "-"
                
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFont(font)
                # Store (tone, sign) in data to help navigation
                item.setData(Qt.ItemDataRole.UserRole, (tone_idx + 1, sign_idx + 1))
                self.grid_table.setItem(sign_idx, tone_idx, item)

    def _refresh_display(self):
        tz_date: TzolkinDate = self.service.from_gregorian(self.current_date)
        
        # Update Info Card
        self.kin_label.setText(f"Kin {tz_date.kin}")
        self.main_label.setText(f"{tz_date.tone} {tz_date.sign_name}")
        self.cycle_label.setText(f"Cycle {tz_date.cycle}\n(Since Epoch 2020-01-12)")
        self.ditrune_label.setText(
            f"Ditrune: {tz_date.ditrune_decimal}\n[{tz_date.ditrune_ternary}]"
        )
        
        # Update Date Picker logic
        self.date_edit.blockSignals(True)
        self.date_edit.setDate(QDate(self.current_date.year, self.current_date.month, self.current_date.day))
        self.date_edit.blockSignals(False)
        
        # Highlight Grid Cell
        # Row = Sign-1, Col = Tone-1
        row = tz_date.sign - 1
        col = tz_date.tone - 1
        
        self.grid_table.blockSignals(True) # Prevent cellClick trigger
        self.grid_table.setCurrentCell(row, col)
        self.grid_table.blockSignals(False)

    def _on_date_changed(self, qdate: QDate):
        self.current_date = qdate.toPyDate()
        self._refresh_display()

    def _prev_day(self):
        self.current_date = self.current_date - timedelta(days=1)
        self._refresh_display()

    def _next_day(self):
        self.current_date = self.current_date + timedelta(days=1)
        self._refresh_display()
        
    def _go_today(self):
        self.current_date = date.today()
        self._refresh_display()

    def _on_cell_clicked(self, row, col):
        """
        When a grid cell is clicked, jump to that Kin.
        Logic: Calculate target Kin, find difference from current Kin, apply delta days.
        """
        # Row = Sign, Col = Tone
        sign = row + 1
        tone = col + 1
        
        # Find target Kin
        target_kin = self._kin_map.get((tone, sign))
        if not target_kin:
            return # Should not happen
            
        # Get current date details to know which cycle we are in
        current_tz = self.service.from_gregorian(self.current_date)
        current_kin = current_tz.kin
        
        # Calculate diff
        diff = target_kin - current_kin
        
        # Apply diff
        new_date = self.current_date + timedelta(days=diff)
        self.current_date = new_date
        self._refresh_display()