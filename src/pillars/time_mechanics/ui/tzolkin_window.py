"""
Tzolkin Calculator Window - The Harmonic Grid.
Window for calculating and navigating Tzolkin dates with interactive 13x20 grid.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QDateEdit, QFrame, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QStyledItemDelegate, QStyle, QScrollArea
)
from PyQt6.QtCore import Qt, QDate, QThread, pyqtSignal, QRectF, QSize, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QFontMetrics
from datetime import date, timedelta
from ..services.tzolkin_service import TzolkinService
from ..models.tzolkin_models import TzolkinDate
from ..services.venus_tzolkin_overlay_service import VenusTzolkinOverlayService


class _VenusOverlayWorker(QThread):
    result_ready = pyqtSignal(object)  # list[VenusTzolkinOverlayEvent]
    error = pyqtSignal(str)

    def __init__(self, start_date: date, end_date: date, parent=None):
        super().__init__(parent)
        self._start_date = start_date
        self._end_date = end_date

    def run(self):
        try:
            service = VenusTzolkinOverlayService()
            events = service.get_overlay_events_for_range(self._start_date, self._end_date)
            self.result_ready.emit(events)
        except Exception as e:
            self.error.emit(str(e))


class _CartoucheGrid(QWidget):
    """Fully custom-painted 20x13 grid of cartouche tiles."""

    cell_clicked = pyqtSignal(int, int)  # row, col

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

        self._rows = 20
        self._cols = 13

        # Default tile geometry: golden mean cartouches (vertical oblong).
        # 157/97 ≈ 1.618
        self._tile_w = 97
        self._tile_h = 157
        self._gap_x = 14
        self._gap_y = 14
        self._margin = 12

        self._base_text: list[list[str]] = [["-" for _ in range(self._cols)] for _ in range(self._rows)]
        self._marker_text: dict[tuple[int, int], str] = {}
        self._tooltip_text: dict[tuple[int, int], str] = {}

        self._selected_row = 0
        self._selected_col = 0
        self._hover_cell: tuple[int, int] | None = None

    def sizeHint(self) -> QSize:
        w = self._margin * 2 + self._cols * self._tile_w + (self._cols - 1) * self._gap_x
        h = self._margin * 2 + self._rows * self._tile_h + (self._rows - 1) * self._gap_y
        return QSize(w, h)

    def set_tile_size(self, w: int, h: int) -> None:
        self._tile_w = int(w)
        self._tile_h = int(h)
        self.updateGeometry()
        self.update()

    def set_base_text(self, row: int, col: int, text: str) -> None:
        self._base_text[row][col] = text

    def clear_markers(self) -> None:
        self._marker_text.clear()
        self._tooltip_text.clear()
        self.update()

    def set_cell_marker(self, row: int, col: int, marker: str, tooltip: str) -> None:
        if marker:
            self._marker_text[(row, col)] = marker
        else:
            self._marker_text.pop((row, col), None)
        if tooltip:
            self._tooltip_text[(row, col)] = tooltip
        else:
            self._tooltip_text.pop((row, col), None)
        self.update()

    def set_current_cell(self, row: int, col: int) -> None:
        self._selected_row = max(0, min(self._rows - 1, int(row)))
        self._selected_col = max(0, min(self._cols - 1, int(col)))
        self.update()

    def _cell_rect(self, row: int, col: int) -> QRectF:
        x = self._margin + col * (self._tile_w + self._gap_x)
        y = self._margin + row * (self._tile_h + self._gap_y)
        return QRectF(x, y, self._tile_w, self._tile_h)

    def _hit_test(self, x: float, y: float) -> tuple[int, int] | None:
        # Fast grid-based hit test; then confirm point is in the tile rect.
        x0 = x - self._margin
        y0 = y - self._margin
        if x0 < 0 or y0 < 0:
            return None
        step_x = self._tile_w + self._gap_x
        step_y = self._tile_h + self._gap_y
        col = int(x0 // step_x)
        row = int(y0 // step_y)
        if not (0 <= row < self._rows and 0 <= col < self._cols):
            return None
        r = self._cell_rect(row, col)
        if not r.contains(x, y):
            return None
        return row, col

    def mousePressEvent(self, event):
        hit = self._hit_test(event.position().x(), event.position().y())
        if hit is not None:
            row, col = hit
            self.set_current_cell(row, col)
            self.cell_clicked.emit(row, col)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        hit = self._hit_test(event.position().x(), event.position().y())
        if hit != self._hover_cell:
            self._hover_cell = hit
            if hit is None:
                self.setToolTip("")
            else:
                self.setToolTip(self._tooltip_text.get(hit, ""))
        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # Reuse the palette already present in this window (no new tokens).
        stone_fill = QColor("#f1f5f9")
        stone_border = QColor("#cbd5e1")
        stone_inner_fill = QColor("#f8fafc")
        stone_inner_shadow = QColor("#94a3b8")
        selected_fill = QColor("#3b82f6")

        base_font = QFont(self.font())
        base_font.setBold(True)
        base_font.setPointSize(max(10, base_font.pointSize() - 1))

        marker_font = QFont(self.font())
        marker_font.setBold(True)
        marker_font.setPointSize(max(8, marker_font.pointSize() - 4))

        # Ring colors by row: Red, Green, Blue, White repeating.
        ring_colors = [QColor("red"), QColor("green"), QColor("blue"), QColor("white")]

        for row in range(self._rows):
            for col in range(self._cols):
                r = self._cell_rect(row, col)

                is_selected = (row == self._selected_row and col == self._selected_col)
                fill = selected_fill if is_selected else stone_fill
                text_color = QColor("white") if is_selected else QColor("#0f172a")
                marker_color = QColor("white") if is_selected else QColor("#64748b")

                outer = QRectF(r)
                # Less-rounded corners (avoid capsule look): pick a modest radius based on width.
                radius = max(10.0, min(22.0, outer.width() / 3.6))

                # Outer fill
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(fill)
                painter.drawRoundedRect(outer, radius, radius)

                # Outer border
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QPen(stone_border if not is_selected else text_color, 2))
                painter.drawRoundedRect(outer, radius, radius)

                # Colored ring between outer and inner borders
                ring_outer = outer.adjusted(3.0, 3.0, -3.0, -3.0)
                ring_inner = outer.adjusted(8.0, 8.0, -8.0, -8.0)
                ring_radius_outer = max(9.0, min(21.0, ring_outer.width() / 3.6))
                ring_radius_inner = max(8.0, min(20.0, ring_inner.width() / 3.6))

                ring_color = ring_colors[row % 4]
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(ring_color)
                painter.drawRoundedRect(ring_outer, ring_radius_outer, ring_radius_outer)

                # Inner fill
                painter.setBrush(fill if is_selected else stone_inner_fill)
                painter.drawRoundedRect(ring_inner, ring_radius_inner, ring_radius_inner)

                # Inner border/shadow
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(QPen(stone_inner_shadow if not is_selected else text_color, 1))
                painter.drawRoundedRect(ring_inner, ring_radius_inner, ring_radius_inner)

                painter.setPen(text_color)
                painter.setFont(base_font)
                base_text = self._base_text[row][col]
                # Push the decimal number toward the top of the cartouche.
                base_rect = ring_inner.adjusted(6.0, 10.0, -6.0, -32.0).toRect()
                painter.drawText(base_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, base_text)

                marker = self._marker_text.get((row, col), "")
                if marker:
                    painter.setPen(marker_color)
                    painter.setFont(marker_font)
                    marker_rect = ring_inner.adjusted(6.0, 6.0, -6.0, -10.0).toRect()
                    painter.drawText(marker_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom, marker)

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

        # Map between Kin (1-260) and the source-of-truth grid layout:
        # rows = Sign (0-19), cols = Tone (0-12).
        self._kin_by_sign_tone: dict[tuple[int, int], int] = {}
        for kin in range(1, 261):
            kin_index = kin - 1
            sign_idx = kin_index % 20
            tone_idx = kin_index % 13
            self._kin_by_sign_tone[(sign_idx, tone_idx)] = kin

        self._venus_overlay_cycle = None
        self._venus_overlay_request_id = 0
        self._venus_overlay_worker: _VenusOverlayWorker | None = None
        
        self._setup_ui()
        self._populate_grid()
        self._refresh_display()

        # Ensure the main label is fitted after the first layout pass.
        QTimer.singleShot(0, self._refit_main_label)

    def _kin_to_cell(self, kin: int) -> tuple[int, int]:
        """Map Kin (1-260) to a cell in the source-of-truth grid layout.

        The window grid matches Docs/time_mechanics/Tzolkin Cycle.csv:
        - rows = Sign (0-19)
        - cols = Tone (0-12)
        """
        kin_index = (kin - 1) % 260
        row = kin_index % 20
        col = kin_index % 13
        return row, col

    def _cell_to_kin(self, row: int, col: int) -> int:
        # Invert (sign_idx=row, tone_idx=col) -> unique Kin (CRT since 20 and 13 are coprime).
        return int(self._kin_by_sign_tone.get((int(row), int(col)), 1))

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
        # Font size is auto-fitted in code to prevent overflow for long Greek tokens.
        self.main_label.setStyleSheet("color: #0f172a; font-weight: bold; background: transparent; border: none;")
        # Always single-line: shrink-to-fit only.
        self.main_label.setWordWrap(False)
        self._main_label_max_point_size = 24
        # Allow smaller fonts to avoid truncation for long, space-free tokens.
        self._main_label_min_point_size = 6
        self._main_label_max_lines = 1
        self._main_label_full_text = ""
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
        
        # Right: Fully custom-painted cartouche grid.
        self.grid = _CartoucheGrid()
        self.grid.cell_clicked.connect(self._on_cell_clicked)

        # Wrap the grid in a scroll area so we can later add more integrated info
        # below/around it without redesigning the main layout.
        grid_container = QWidget()
        grid_container_layout = QVBoxLayout(grid_container)
        grid_container_layout.setContentsMargins(10, 10, 10, 10)
        # Ensure the scroll area can actually scroll (don't let the container shrink to the viewport).
        self.grid.set_tile_size(97, 157)
        self.grid.setMinimumSize(self.grid.sizeHint())
        grid_container.setMinimumSize(self.grid.sizeHint())
        grid_container_layout.addWidget(self.grid)

        self.grid_scroll = QScrollArea()
        # If widgetResizable=True, Qt will stretch the grid to fit the viewport,
        # which prevents scrollbars from ever appearing.
        self.grid_scroll.setWidgetResizable(False)
        self.grid_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.grid_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.grid_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.grid_scroll.setWidget(grid_container)

        content_layout.addWidget(self.grid_scroll)

    def _populate_grid(self):
        """Populate the 20x13 grid with Ditrune values matching Tzolkin Cycle.csv."""

        if not self.service._decimal_grid:
            for row in range(20):
                for col in range(13):
                    self.grid.set_base_text(row, col, "-")
            self.grid.clear_markers()
            self.grid.update()
            return

        for sign_idx in range(20):
            for tone_idx in range(13):
                try:
                    val = self.service._decimal_grid[sign_idx][tone_idx]
                    text = str(val)
                except Exception:
                    text = "?"

                self.grid.set_base_text(sign_idx, tone_idx, text)

        self.grid.clear_markers()
        self.grid.update()

    def _clear_venus_markers(self):
        self.grid.clear_markers()

    def _format_venus_kind(self, kind: str) -> str:
        mapping = {
            "inferior_conjunction": "IC",
            "superior_conjunction": "SC",
            "greatest_elongation_east": "GE→",
            "greatest_elongation_west": "GE←",
            "invisible_start": "INV+",
            "invisible_end": "INV-",
        }
        return mapping.get(kind, kind)

    def _apply_venus_overlay(self, request_id: int, events: list):
        if request_id != self._venus_overlay_request_id:
            return

        self._clear_venus_markers()

        events_by_cell: dict[tuple[int, int], list] = {}
        for e in events:
            tz = getattr(e, "tzolkin", None)
            if tz is None:
                continue
            kin = int(getattr(tz, "kin", 0))
            if not (1 <= kin <= 260):
                continue
            row, col = self._kin_to_cell(kin)
            events_by_cell.setdefault((row, col), []).append(e)

        for (row, col), cell_events in events_by_cell.items():
            marker_codes = [self._format_venus_kind(getattr(e, "kind", "")) for e in cell_events]
            marker_text = " ".join(marker_codes)

            tooltip_lines: list[str] = []
            for e in sorted(cell_events, key=lambda x: getattr(x, "dt_utc", None) or 0):
                dt_utc = getattr(e, "dt_utc", None)
                kind = getattr(e, "kind", "")
                elong = getattr(e, "elongation_deg", None)
                illum = getattr(e, "illumination_fraction", None)
                if dt_utc is not None and elong is not None and illum is not None:
                    tooltip_lines.append(f"{dt_utc.isoformat()}  {kind}  elong={float(elong):.3f}°  illum={float(illum):.4f}")
                elif dt_utc is not None:
                    tooltip_lines.append(f"{dt_utc.isoformat()}  {kind}")
                else:
                    tooltip_lines.append(str(kind))
            self.grid.set_cell_marker(row, col, marker_text, "\n".join(tooltip_lines))

    def _refresh_venus_overlay_for_cycle(self, cycle: int):
        cycle_start = self.service.EPOCH + timedelta(days=(cycle - 1) * 260)
        cycle_end = cycle_start + timedelta(days=259)

        self._venus_overlay_request_id += 1
        request_id = self._venus_overlay_request_id
        self._venus_overlay_cycle = cycle

        if self._venus_overlay_worker is not None:
            try:
                self._venus_overlay_worker.result_ready.disconnect()
                self._venus_overlay_worker.error.disconnect()
            except Exception:
                pass
            self._venus_overlay_worker = None

        worker = _VenusOverlayWorker(cycle_start, cycle_end, parent=self)
        worker.result_ready.connect(lambda evts: self._apply_venus_overlay(request_id, evts))
        worker.error.connect(lambda _msg: None)
        worker.start()
        self._venus_overlay_worker = worker

    def _refresh_display(self):
        tz_date: TzolkinDate = self.service.from_gregorian(self.current_date)

        if tz_date.cycle != self._venus_overlay_cycle:
            self._refresh_venus_overlay_for_cycle(tz_date.cycle)
        
        # Update Info Card
        self.kin_label.setText(f"Kin {tz_date.kin}")
        greek_name = self.service.get_true_token_for_kin(tz_date.kin)
        self._set_main_label_text(greek_name or f"{tz_date.tone} {tz_date.sign_name}")
        self.cycle_label.setText(f"Cycle {tz_date.cycle}\n(Since Epoch 2020-01-12)")
        self.ditrune_label.setText(
            f"Ditrune: {tz_date.ditrune_decimal}\n[{tz_date.ditrune_ternary}]"
        )
        
        # Update Date Picker logic
        self.date_edit.blockSignals(True)
        self.date_edit.setDate(QDate(self.current_date.year, self.current_date.month, self.current_date.day))
        self.date_edit.blockSignals(False)
        
        # Highlight Grid Cell
        row, col = self._kin_to_cell(tz_date.kin)

        self.grid.set_current_cell(row, col)

    def _set_main_label_text(self, text: str) -> None:
        """Set the primary name line and fit its font to the card width."""
        self._main_label_full_text = text
        # Keep the full token available even if we later elide it.
        self.main_label.setToolTip(text)
        self.main_label.setText(text)
        # Defer fitting until Qt has computed final label geometry.
        QTimer.singleShot(0, self._refit_main_label)

    def _refit_main_label(self) -> None:
        full_text = getattr(self, "_main_label_full_text", "") or self.main_label.text()
        self._fit_label_font(
            label=self.main_label,
            text=full_text,
            max_point_size=self._main_label_max_point_size,
            min_point_size=self._main_label_min_point_size,
            max_lines=self._main_label_max_lines,
        )

    def _fit_label_font(
        self,
        label: QLabel,
        text: str,
        max_point_size: int,
        min_point_size: int,
        max_lines: int,
    ) -> None:
        """Reduce font size until the text fits.

        Policy: single line, shrink-to-fit only (no elision).
        """

        # contentsRect() can be 0 before layout; fall back to current widget width.
        available_width = max(1, label.contentsRect().width(), label.width() - 2)

        base_font = QFont(label.font())
        base_font.setBold(True)

        # Single-line fit: keep reducing point size until width fits.
        for pt in range(int(max_point_size), int(min_point_size) - 1, -1):
            base_font.setPointSize(pt)
            fm = QFontMetrics(base_font)
            if fm.horizontalAdvance(text) <= available_width:
                label.setFont(base_font)
                label.setText(text)
                return

        # If it still doesn't fit at the minimum font, keep the full text anyway.
        base_font.setPointSize(int(min_point_size))
        label.setFont(base_font)
        label.setText(text)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Refit the main label when the window/card width changes.
        self._refit_main_label()

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
        Logic: target Kin comes directly from the clicked cell (Kin-order layout).
        """
        target_kin = self._cell_to_kin(row, col)
            
        # Get current date details to know which cycle we are in
        current_tz = self.service.from_gregorian(self.current_date)
        current_kin = current_tz.kin
        
        # Calculate diff
        diff = target_kin - current_kin
        
        # Apply diff
        new_date = self.current_date + timedelta(days=diff)
        self.current_date = new_date
        self._refresh_display()