"""
Thelemic Date Window - Era Legis Calendar Display.

Window for displaying the current Thelemic date with options to:
- Copy the date as formatted text
- Export the display as an image
"""
from datetime import date, datetime, timezone
from pathlib import Path
import time

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QDateEdit, QFrame, QApplication,
    QFileDialog, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QPixmap

from ..services.thelemic_date_service import ThelemicDateService
from ..models.thelemic_date_models import ThelemicDate


class ThelemicDateCard(QFrame):
    """
    A styled card widget displaying the Thelemic date.
    This widget can be captured as an image.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thelemic_date: ThelemicDate | None = None
        self._setup_ui()

    def _setup_ui(self):
        """Set up the card UI."""
        self.setObjectName("ThelemicDateCard")
        self.setStyleSheet("""
            QFrame#ThelemicDateCard {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e,
                    stop:0.5 #16213e,
                    stop:1 #0f3460
                );
                border: 2px solid #d4af37;
                border-radius: 16px;
            }
        """)
        self.setMinimumSize(500, 400)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header: "Era Legis"
        self.header_label = QLabel("ERA LEGIS")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setStyleSheet("""
            color: #d4af37;
            font-size: 12pt;
            font-weight: bold;
            letter-spacing: 0.3em;
        """)
        layout.addWidget(self.header_label)

        # Main Anno display
        self.anno_label = QLabel("Anno V:x")
        self.anno_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        anno_font = QFont()
        anno_font.setPointSize(36)
        anno_font.setBold(True)
        self.anno_label.setFont(anno_font)
        self.anno_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(self.anno_label)

        # Tarot correspondence
        self.tarot_label = QLabel("The docosade of The Hierophant, and the year of Fortune")
        self.tarot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tarot_label.setWordWrap(True)
        self.tarot_label.setStyleSheet("""
            color: #a0a0c0;
            font-size: 11pt;
            font-style: italic;
        """)
        layout.addWidget(self.tarot_label)

        layout.addSpacing(10)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #d4af37; max-height: 1px;")
        layout.addWidget(divider)

        layout.addSpacing(10)

        # Sol position
        self.sol_label = QLabel("Sol in 27° Capricorni")
        self.sol_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sol_label.setStyleSheet("""
            color: #ffd700;
            font-size: 14pt;
            font-weight: bold;
        """)
        layout.addWidget(self.sol_label)

        # Luna position
        self.luna_label = QLabel("Luna in 15° Leonis")
        self.luna_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.luna_label.setStyleSheet("""
            color: #c0c0c0;
            font-size: 14pt;
            font-weight: bold;
        """)
        layout.addWidget(self.luna_label)

        layout.addSpacing(10)

        # Day of week (Latin)
        self.dies_label = QLabel("Dies Jovis")
        self.dies_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dies_label.setStyleSheet("""
            color: #8080a0;
            font-size: 12pt;
        """)
        layout.addWidget(self.dies_label)

        layout.addSpacing(10)

        # Divider
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setStyleSheet("background-color: #404060; max-height: 1px;")
        layout.addWidget(divider2)

        layout.addSpacing(5)

        # Gregorian date (smaller, for reference)
        self.gregorian_label = QLabel("16 January 2026 e.v.")
        self.gregorian_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gregorian_label.setStyleSheet("""
            color: #606080;
            font-size: 10pt;
        """)
        layout.addWidget(self.gregorian_label)

        layout.addStretch()

    def set_thelemic_date(self, td: ThelemicDate) -> None:
        """Update the card with a new Thelemic date."""
        self._thelemic_date = td

        # Update Anno
        self.anno_label.setText(f"Anno {td.anno}")

        # Update Tarot
        self.tarot_label.setText(td.format_tarot())

        # Update Sol
        self.sol_label.setText(f"Sol in {td.sol_degree}° {td.sol_sign[1]}")

        # Update Luna
        self.luna_label.setText(f"Luna in {td.luna_degree}° {td.luna_sign[1]}")

        # Update Dies
        self.dies_label.setText(td.dies_latin)

        # Update Gregorian
        greg_str = td.gregorian_date.strftime("%d %B %Y e.v.")
        self.gregorian_label.setText(greg_str)

    def get_full_format(self) -> str:
        """Return just the full format line for copying."""
        if self._thelemic_date is None:
            return ""
        return self._thelemic_date.format_full()

    def get_formatted_text(self) -> str:
        """Return the Thelemic date as formatted text for copying."""
        if self._thelemic_date is None:
            return ""

        td = self._thelemic_date
        lines = [
            "ERA LEGIS",
            "",
            f"Anno {td.anno}",
            td.format_tarot(),
            "",
            f"Sol in {td.sol_degree}° {td.sol_sign[1]}",
            f"Luna in {td.luna_degree}° {td.luna_sign[1]}",
            "",
            td.dies_latin,
            "",
            f"{td.gregorian_date.strftime('%d %B %Y')} e.v.",
            "",
            "---",
            f"Full format: {td.format_full()}",
        ]
        return "\n".join(lines)


class ThelemicDateWindow(QWidget):
    """
    Window for displaying and interacting with the Thelemic Date.

    Features:
    - Display current Thelemic date with astronomical positions
    - Navigate to different dates
    - Copy date as text
    - Export display as image
    """

    def __init__(self, window_manager=None, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager
        self.service = ThelemicDateService()
        self.current_date = date.today()

        self._setup_ui()
        self._refresh_display()

    def _setup_ui(self):
        """Set up the window UI."""
        self.setWindowTitle("Thelemic Date - Era Legis")
        self.setMinimumSize(600, 600)
        self.resize(650, 700)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Header ---
        header_layout = QHBoxLayout()

        header_label = QLabel("Thelemic Date")
        header_font = QFont()
        header_font.setPointSize(18)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        # Date navigation
        self.prev_btn = QPushButton("<")
        self.prev_btn.setFixedWidth(30)
        self.prev_btn.setToolTip("Previous day")
        self.prev_btn.clicked.connect(self._prev_day)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.dateChanged.connect(self._on_date_changed)
        self.date_edit.setFixedWidth(130)

        self.next_btn = QPushButton(">")
        self.next_btn.setFixedWidth(30)
        self.next_btn.setToolTip("Next day")
        self.next_btn.clicked.connect(self._next_day)

        self.today_btn = QPushButton("Today")
        self.today_btn.setToolTip("Go to today")
        self.today_btn.clicked.connect(self._go_today)

        header_layout.addWidget(self.prev_btn)
        header_layout.addWidget(self.date_edit)
        header_layout.addWidget(self.next_btn)
        header_layout.addWidget(self.today_btn)

        layout.addLayout(header_layout)

        # --- Main Date Card ---
        self.date_card = ThelemicDateCard()
        layout.addWidget(self.date_card, 1)

        # --- Action Buttons ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.copy_full_btn = QPushButton("Copy Full Format")
        self.copy_full_btn.setStyleSheet("""
            QPushButton {
                background-color: #7c3aed;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #6d28d9;
            }
            QPushButton:pressed {
                background-color: #5b21b6;
            }
        """)
        self.copy_full_btn.setToolTip("Copy just the full format line (e.g., 'Dies Veneris : Sol in 27° Capricorni : ...')")
        self.copy_full_btn.clicked.connect(self._copy_full_format)

        self.copy_btn = QPushButton("Copy All Details")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        self.copy_btn.setToolTip("Copy all date details to clipboard")
        self.copy_btn.clicked.connect(self._copy_text)

        self.export_btn = QPushButton("Export Image")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #047857;
            }
            QPushButton:pressed {
                background-color: #065f46;
            }
        """)
        self.export_btn.setToolTip("Export date card as image")
        self.export_btn.clicked.connect(self._export_image)

        button_layout.addStretch()
        button_layout.addWidget(self.copy_full_btn)
        button_layout.addWidget(self.copy_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def _refresh_display(self):
        """Refresh the display with the current date."""
        # Get Thelemic date for the current selection
        calc_time = datetime(
            self.current_date.year,
            self.current_date.month,
            self.current_date.day,
            12, 0, 0,
            tzinfo=timezone.utc
        )
        thelemic_date = self.service.from_gregorian(self.current_date, calc_time)

        # Update the card
        self.date_card.set_thelemic_date(thelemic_date)

        # Update date picker
        self.date_edit.blockSignals(True)
        self.date_edit.setDate(QDate(
            self.current_date.year,
            self.current_date.month,
            self.current_date.day
        ))
        self.date_edit.blockSignals(False)

    def _on_date_changed(self, qdate: QDate):
        """Handle date picker change."""
        self.current_date = qdate.toPyDate()
        self._refresh_display()

    def _prev_day(self):
        """Go to previous day."""
        from datetime import timedelta
        self.current_date = self.current_date - timedelta(days=1)
        self._refresh_display()

    def _next_day(self):
        """Go to next day."""
        from datetime import timedelta
        self.current_date = self.current_date + timedelta(days=1)
        self._refresh_display()

    def _go_today(self):
        """Go to today."""
        self.current_date = date.today()
        self._refresh_display()

    def _copy_full_format(self):
        """Copy just the full format line to clipboard."""
        text = self.date_card.get_full_format()
        if not text:
            return

        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text)

            # Show brief feedback
            original_text = self.copy_full_btn.text()
            self.copy_full_btn.setText("Copied!")
            self.copy_full_btn.setEnabled(False)
            QTimer.singleShot(1500, lambda: self._reset_copy_full_button(original_text))

    def _reset_copy_full_button(self, text: str):
        """Reset copy full format button after feedback."""
        self.copy_full_btn.setText(text)
        self.copy_full_btn.setEnabled(True)

    def _copy_text(self):
        """Copy the Thelemic date to clipboard as text."""
        text = self.date_card.get_formatted_text()
        if not text:
            return

        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text)

            # Show brief feedback
            original_text = self.copy_btn.text()
            self.copy_btn.setText("Copied!")
            self.copy_btn.setEnabled(False)
            QTimer.singleShot(1500, lambda: self._reset_copy_button(original_text))

    def _reset_copy_button(self, text: str):
        """Reset copy button after feedback."""
        self.copy_btn.setText(text)
        self.copy_btn.setEnabled(True)

    def _export_image(self):
        """Export the date card as an image."""
        # Generate default filename
        timestamp = int(time.time())
        default_name = f"thelemic_date_{timestamp}.png"

        # Show save dialog
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Save Thelemic Date Image",
            str(Path.home() / default_name),
            "PNG Image (*.png);;JPEG Image (*.jpg)"
        )

        if not path_str:
            return

        path = Path(path_str)

        # Capture the card widget as a pixmap
        pixmap = self.date_card.grab()

        # Determine format
        ext = path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            fmt = "JPEG"
        else:
            fmt = "PNG"
            if not path.suffix:
                path = path.with_suffix(".png")

        # Save the image
        success = pixmap.save(str(path), fmt)

        if success:
            # Show brief feedback
            original_text = self.export_btn.text()
            self.export_btn.setText("Saved!")
            self.export_btn.setEnabled(False)
            QTimer.singleShot(1500, lambda: self._reset_export_button(original_text))
        else:
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Failed to save image to:\n{path}"
            )

    def _reset_export_button(self, text: str):
        """Reset export button after feedback."""
        self.export_btn.setText(text)
        self.export_btn.setEnabled(True)
