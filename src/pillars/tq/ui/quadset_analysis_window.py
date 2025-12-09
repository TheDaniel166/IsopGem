"""Quadset Analysis tool window."""
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QGroupBox, QTabWidget, QWidget,
    QTextEdit, QScrollArea, QGridLayout, QFrame,
    QSizePolicy, QMenu, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt, QPointF, QSize
from PyQt6.QtGui import QFont, QPainter, QPen, QColor, QAction, QTextCursor

from ..services.quadset_engine import QuadsetEngine
from ..models import QuadsetResult, QuadsetMember
from shared.ui import WindowManager
from shared.database import get_db_session
from pillars.gematria.models.calculation_entity import CalculationEntity


def get_super(x):
    normal = "0123456789"
    super_s = "⁰¹²³⁴⁵⁶⁷⁸⁹"
    res = x.maketrans(''.join(normal), ''.join(super_s))
    return x.translate(res)


class CardTextEdit(QTextEdit):
    """QTextEdit that delegates context menu events."""
    def __init__(self, text, parent=None, context_menu_handler=None):
        super().__init__(text, parent)
        self.context_menu_handler = context_menu_handler

    def contextMenuEvent(self, event):
        if self.context_menu_handler:
            self.context_menu_handler(event, self)
        else:
            super().contextMenuEvent(event)


class QuadsetGlyph(QWidget):
    """Visualize ternary strings as Taoist line glyphs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ternary = ""
    def sizeHint(self):
        return QSize(80, 100)

    def minimumSizeHint(self):
        return QSize(60, 80)

    def set_ternary(self, ternary: str) -> None:
        """Update the glyph with a ternary string and repaint."""
        self._ternary = ternary or ""
        self.update()

    def _normalized_digits(self) -> list[str]:
        digits = [d for d in self._ternary if d in {"0", "1", "2"}]
        return digits or ["0"]

    def paintEvent(self, _event):  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(255, 255, 255, 0))

        digits = self._normalized_digits()

        total = len(digits)
        height = self.height()
        width = self.width()
        width = self.width()
        MAX_LINE_WIDTH = 120
        line_length = min(width * 0.8, MAX_LINE_WIDTH) 
        margin_x = (width - line_length) / 2
        
        # Tighter vertical spacing
        # Reduce max line height to 12, min to 4
        # Denominator adjust for tighter packing
        line_height = max(min(height / (total + 0.5), 18), 6)
        base_pen = QPen(QColor("#111827"), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)

        for idx, digit in enumerate(reversed(digits)):
            y = height - ((idx + 0.5) * line_height)
            if digit == "0":
                painter.setPen(base_pen)
                radius = line_height * 0.18
                painter.drawEllipse(
                    int(width / 2 - radius),
                    int(y - radius),
                    int(radius * 2),
                    int(radius * 2),
                )
            elif digit == "1":
                painter.setPen(base_pen)
                painter.drawLine(
                    QPointF(margin_x, y),
                    QPointF(margin_x + line_length, y),
                )
            else:  # digit == "2"
                painter.setPen(base_pen)
                golden_ratio = 1.618
                gap = line_length / (2 * golden_ratio + 1)
                segment = (line_length - gap) / 2
                painter.drawLine(
                    QPointF(margin_x, y),
                    QPointF(margin_x + segment, y),
                )
                painter.drawLine(
                    QPointF(margin_x + segment + gap, y),
                    QPointF(margin_x + line_length, y),
                )


class PropertyCard(QFrame):
    """A card entry for displaying a specific property."""
    
    def __init__(self, title: str, content: str = "", parent=None, context_menu_handler=None):
        super().__init__(parent)
        self.setObjectName("propertyCard")
        self.setStyleSheet("""
            QFrame#propertyCard {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #64748b; font-size: 10pt; font-weight: 600; text-transform: uppercase;")
        layout.addWidget(self.title_label)
        
        self.content_edit = CardTextEdit("", context_menu_handler=context_menu_handler)
        self.content_edit.setPlainText(content)
        self.content_edit.setReadOnly(True)
        self.content_edit.setStyleSheet("""
            QTextEdit {
                color: #0f172a; 
                font-size: 11pt; 
                font-family: 'Segoe UI', sans-serif;
                background-color: transparent;
                border: none;
            }
        """)
        # Adjust height based on content approx (optional, but helpful to not be too huge default)
        # For now let layout handle it, but maybe minimum height
        self.content_edit.setFrameStyle(QFrame.Shape.NoFrame)
        self.content_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # Fit height logic or simpler:
        # Just use it. The card will expand in the VBox of the scrollarea.
        # But QTextEdit might be greedy. We want it to adapt.
        # A simple fix is to use QLabel for short text, but user complained about "all factors".
        # Let's use a dynamic approach or just a read-only text edit with a reasonable max/min height.
        # Actually, standard Label with WordWrap should grow. 
        # IF the text is super long, it might be pushing off screen?
        # The user said "not showing ALL", implying cut off. 
        # If I use TextEdit, it needs to be careful not to trap scroll if nested.
        
        # New approach for this component:
        self.content_edit.setFixedHeight(int(min(self.content_edit.document().size().height() + 10, 200)) if len(content) > 100 else 40)
        self.content_edit.textChanged.connect(self._adjust_height)

        layout.addWidget(self.content_edit)

    def _adjust_height(self):
        doc_height = self.content_edit.document().size().height()
        self.content_edit.setFixedHeight(int(min(max(doc_height + 10, 40), 250)))

    def set_content(self, text: str):
        self.content_edit.setPlainText(text)
        self._adjust_height()


class QuadsetAnalysisWindow(QMainWindow):
    """Window for Quadset Analysis with detailed property tabs."""
    
    def __init__(self, window_manager: WindowManager = None, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager
        self.setWindowTitle("Quadset Analysis")
        self.resize(1000, 800)
        
        # Engine for calculations
        self.engine = QuadsetEngine()
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Quadset Analysis")
        self.setMinimumSize(900, 700)
        
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Quadset Analysis")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Input Section
        input_layout = QHBoxLayout()
        input_label = QLabel("Input Decimal:")
        input_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter a number...")
        self.input_field.setStyleSheet("font-size: 14pt; padding: 8px;")
        self.input_field.textChanged.connect(self._on_input_changed)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_field)
        layout.addLayout(input_layout)
        
        # Tabs Section
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e5e7eb;
                border-radius: 4px;
                background: white;
            }
            QTabBar::tab {
                background: #f3f4f6;
                border: 1px solid #e5e7eb;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-size: 11pt;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
                font-weight: bold;
                color: #2563eb;
            }
        """)
        
        # Create tabs
        self.tab_overview = self._create_overview_tab()
        self.tab_original = self._create_detail_tab("Original")
        self.tab_conrune = self._create_detail_tab("Conrune")
        self.tab_reversal = self._create_detail_tab("Reversal")
        self.tab_conrune_rev = self._create_detail_tab("Conrune of Reversal")
        self.tab_upper_diff = self._create_detail_tab("Upper Difference")
        self.tab_lower_diff = self._create_detail_tab("Lower Difference")
        self.tab_advanced = self._create_advanced_tab()
        self.tab_gematria = self._create_gematria_tab()
        
        self.tabs.addTab(self.tab_overview, "Quadset Overview")
        self.tabs.addTab(self.tab_original, "Original")
        self.tabs.addTab(self.tab_conrune, "Conrune")
        self.tabs.addTab(self.tab_reversal, "Reversal")
        self.tabs.addTab(self.tab_conrune_rev, "Conrune Reversal")
        self.tabs.addTab(self.tab_upper_diff, "Upper Diff")
        self.tabs.addTab(self.tab_lower_diff, "Lower Diff")
        self.tabs.addTab(self.tab_advanced, "Advanced")
        self.tabs.addTab(self.tab_gematria, "Gematria") # Add Gematria tab
        
        layout.addWidget(self.tabs)
        
    def _create_overview_tab(self) -> QWidget:
        """Create the overview tab with the 2x2 grid and differences."""
        # Main tab widget is now a scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Container for content
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Grid Section
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # Create the 4 panels
        self.panel_original = self._create_panel("Original (Upper Left)")
        self.panel_conrune = self._create_panel("Conrune (Upper Right)")
        self.panel_reversal = self._create_panel("Reversal (Lower Left)")
        self.panel_conrune_rev = self._create_panel("Conrune of Reversal (Lower Right)")
        
        # Add to grid
        grid.addWidget(self.panel_original, 0, 0)
        grid.addWidget(self.panel_conrune, 0, 1)
        grid.addWidget(self.panel_reversal, 1, 0)
        grid.addWidget(self.panel_conrune_rev, 1, 1)
        
        layout.addLayout(grid)
        
        # Differences Section
        diff_layout = QHBoxLayout()
        diff_layout.setSpacing(20)
        
        self.panel_upper_diff = self._create_panel("Upper Difference (|Orig - Conrune|)")
        self.panel_lower_diff = self._create_panel("Lower Difference (|Rev - Conrune Rev|)")
        
        diff_layout.addWidget(self.panel_upper_diff)
        diff_layout.addWidget(self.panel_lower_diff)
        
        layout.addLayout(diff_layout)
        
        # Set content to scroll area
        scroll.setWidget(content)
        
        return scroll

    def _create_panel(self, title: str) -> QGroupBox:
        """Create a standardized panel for the grid."""
        group = QGroupBox(title)
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12pt;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 12px;
                background-color: #f9fafb;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Decimal Value Label
        dec_label = QLabel("Decimal:")
        dec_label.setStyleSheet("color: #6b7280; font-size: 10pt;")
        layout.addWidget(dec_label)
        
        val_label = QLabel("-")
        val_label.setObjectName("decimal_val")
        val_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #111827;")
        val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(val_label)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)
        
        # Ternary Value Label
        tern_label = QLabel("Ternary:")
        tern_label.setStyleSheet("color: #6b7280; font-size: 10pt;")
        layout.addWidget(tern_label)

        t_val_label = QLabel("-")
        t_val_label.setObjectName("ternary_val")
        t_val_label.setStyleSheet("font-size: 18pt; font-family: monospace; color: #2563eb;")
        t_val_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(t_val_label)

        glyph = QuadsetGlyph()
        glyph.setObjectName("ternary_glyph")
        layout.addWidget(glyph)
        
        group.setLayout(layout)
        return group

    def _update_panel(self, panel: QGroupBox, member: QuadsetMember):
        """Update the values in a panel."""
        dec_lbl = panel.findChild(QLabel, "decimal_val")
        tern_lbl = panel.findChild(QLabel, "ternary_val")
        glyph = panel.findChild(QuadsetGlyph, "ternary_glyph")
        
        if dec_lbl:
            dec_lbl.setText(f"{member.decimal:,}")
        if tern_lbl:
            tern_lbl.setText(member.ternary)
        if glyph:
            glyph.set_ternary(member.ternary)

    def _create_detail_tab(self, title: str) -> QWidget:
        """Create a tab widget for number details."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header Section (Values)
        header_group = QGroupBox(f"{title} Values")
        header_layout = QVBoxLayout()
        
        # Decimal Display
        dec_layout = QHBoxLayout()
        dec_label = QLabel("Decimal:")
        dec_label.setStyleSheet("font-size: 12pt; color: #6b7280;")
        dec_val = QLabel("-")
        dec_val.setObjectName("decimal_val")
        dec_val.setStyleSheet("font-size: 24pt; font-weight: bold; color: #111827;")
        dec_layout.addWidget(dec_label)
        dec_layout.addWidget(dec_val)
        dec_layout.addStretch()
        header_layout.addLayout(dec_layout)
        
        # Ternary Display
        tern_layout = QHBoxLayout()
        tern_label = QLabel("Ternary:")
        tern_label.setStyleSheet("font-size: 12pt; color: #6b7280;")
        tern_val = QLabel("-")
        tern_val.setObjectName("ternary_val")
        tern_val.setStyleSheet("font-size: 18pt; font-family: monospace; color: #2563eb;")
        tern_layout.addWidget(tern_label)
        tern_layout.addWidget(tern_val)
        tern_layout.addStretch()
        header_layout.addLayout(tern_layout)

        glyph = QuadsetGlyph()
        glyph.setObjectName("ternary_glyph")
        header_layout.addWidget(glyph)
        
        header_group.setLayout(header_layout)
        layout.addWidget(header_group)
        
        # Properties Section
        props_label = QLabel("Number Properties")
        props_label.setStyleSheet("font-size: 12pt; font-weight: bold; margin-top: 10px;")
        layout.addWidget(props_label)
        
        # Scroll Area for Cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        cards_container = QWidget()
        cards_container.setObjectName("cardsContainer")
        # Store for retrieval
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setSpacing(12)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        cards_layout.addStretch() # Push up
        
        scroll.setWidget(cards_container)
        layout.addWidget(scroll)
        
        return tab

    def _create_advanced_tab(self) -> QWidget:
        """Create the advanced tab with quadset summary info."""
        # Main Tab Wrapper (Scroll Area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        # Content Widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        sum_box = QGroupBox("Quadset Totals")
        sum_layout = QHBoxLayout()
        sum_label = QLabel("Quadset Sum:")
        sum_label.setStyleSheet("font-size: 12pt; color: #6b7280;")
        sum_value = QLabel("-")
        sum_value.setObjectName("advanced_sum")
        sum_value.setStyleSheet("font-size: 24pt; font-weight: bold; color: #111827;")
        sum_layout.addWidget(sum_label)
        sum_layout.addWidget(sum_value)
        sum_layout.addStretch()
        sum_box.setLayout(sum_layout)
        layout.addWidget(sum_box)

        septad_box = QGroupBox("Septad")
        septad_layout = QHBoxLayout()
        septad_label = QLabel("Septad Total:")
        septad_label.setStyleSheet("font-size: 12pt; color: #6b7280;")
        septad_value = QLabel("-")
        septad_value.setObjectName("advanced_septad")
        septad_value.setStyleSheet("font-size: 20pt; font-weight: bold; color: #0f172a;")
        septad_layout.addWidget(septad_label)
        septad_layout.addWidget(septad_value)
        septad_layout.addStretch()
        septad_box.setLayout(septad_layout)
        layout.addWidget(septad_box)

        # Transgram Section (Manual Frame instead of GroupBox to fix layout)
        trans_header = QLabel("Differential Transgram")
        trans_header.setStyleSheet("font-size: 12pt; font-weight: bold; margin-top: 10px; color: #111827;")
        layout.addWidget(trans_header)

        trans_frame = QFrame()
        trans_frame.setStyleSheet("""
            QFrame {
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
            }
        """)
        trans_layout = QVBoxLayout(trans_frame)
        trans_layout.setSpacing(12) 
        trans_layout.setContentsMargins(16, 16, 16, 16)
        
        # Row 1: Differentials
        diff_row = QHBoxLayout()
        
        # Upper
        upper_frame = QFrame()
        upper_frame.setStyleSheet("border: none; background: transparent;")
        upper_layout = QVBoxLayout(upper_frame)
        upper_layout.setContentsMargins(0,0,0,0)
        upper_layout.addWidget(QLabel("Upper Differential:"))
        uv = QLabel("-")
        uv.setObjectName("advanced_upper_diff")
        uv.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        upper_layout.addWidget(uv)
        
        # Lower
        lower_frame = QFrame()
        lower_frame.setStyleSheet("border: none; background: transparent;")
        lower_layout = QVBoxLayout(lower_frame)
        lower_layout.setContentsMargins(0,0,0,0)
        lower_layout.addWidget(QLabel("Lower Differential:"))
        lv = QLabel("-")
        lv.setObjectName("advanced_lower_diff")
        lv.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        lower_layout.addWidget(lv)
        
        diff_row.addWidget(upper_frame)
        diff_row.addSpacing(40)
        diff_row.addWidget(lower_frame)
        diff_row.addStretch()
        
        trans_layout.addLayout(diff_row)
        
        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("border: none; background: #e5e7eb; max-height: 1px;")
        trans_layout.addWidget(line)

        # Row 2: Transgram Ternary
        t_label = QLabel("Transgram (Ternary):")
        t_label.setStyleSheet("font-size: 11pt; color: #6b7280; border: none;")
        t_val = QLabel("-")
        t_val.setObjectName("advanced_transgram")
        t_val.setStyleSheet("font-size: 16pt; font-family: monospace; color: #2563eb; border: none;")
        
        trans_layout.addWidget(t_label)
        trans_layout.addWidget(t_val)

        # Row 3: Transgram Decimal
        d_label = QLabel("Transgram (Decimal):")
        d_label.setStyleSheet("font-size: 11pt; color: #6b7280; border: none;")
        d_val = QLabel("-")
        d_val.setObjectName("advanced_transgram_dec")
        d_val.setStyleSheet("font-size: 14pt; font-weight: bold; color: #111827; border: none;")

        trans_layout.addWidget(d_label)
        trans_layout.addWidget(d_val)

        layout.addWidget(trans_frame)

        patterns_box = QGroupBox("Pattern Summary")
        patterns_layout = QVBoxLayout()
        patterns_text = QTextEdit()
        patterns_text.setObjectName("advanced_patterns")
        patterns_text.setReadOnly(True)
        patterns_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 11pt;
                background-color: #f8fafc;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        patterns_layout.addWidget(patterns_text)
        patterns_box.setLayout(patterns_layout)
        layout.addWidget(patterns_box)

        layout.addStretch()
        
        scroll.setWidget(content)
        return scroll

    def _handle_geometry_menu(self, event, text_edit):
        """Handle context menu for geometry properties."""
        cursor = text_edit.cursorForPosition(event.pos())
        text_edit.setTextCursor(cursor) # Move cursor to click
        line_text = cursor.block().text().strip()
        
        # Parse: "• {Type} (Index: {N})"
        if not line_text.startswith("• "):
            return
            
        import re
        match = re.search(r"• (.*?) \(Index: (\d+)\)", line_text)
        if not match:
            return
            
        full_name = match.group(1)
        index_str = match.group(2)
        try:
            index = int(index_str)
        except ValueError:
            return

        # Determine mode and sides
        mode = "polygonal"
        sides = 3
        
        if "Star Number" in full_name:
            mode = "star"
            sides = 12 # Not strictly used by visualizer for Star but good default
        elif "Centered" in full_name:
            mode = "centered"
            # Map name to sides
            name_lower = full_name.lower()
            if "triangle" in name_lower: sides = 3
            elif "square" in name_lower: sides = 4
            elif "pentagonal" in name_lower: sides = 5
            elif "hexagonal" in name_lower: sides = 6
            elif "heptagonal" in name_lower: sides = 7
            elif "octagonal" in name_lower: sides = 8
            elif "nonagonal" in name_lower: sides = 9
            elif "decagonal" in name_lower: sides = 10
            elif "hendecagonal" in name_lower: sides = 11
            elif "dodecagonal" in name_lower: sides = 12
        else:
            mode = "polygonal"
            name_lower = full_name.lower()
            if "triangle" in name_lower: sides = 3
            elif "square" in name_lower: sides = 4
            elif "pentagonal" in name_lower: sides = 5
            elif "hexagonal" in name_lower: sides = 6
            elif "heptagonal" in name_lower: sides = 7
            elif "octagonal" in name_lower: sides = 8
            elif "nonagonal" in name_lower: sides = 9
            elif "decagonal" in name_lower: sides = 10
            elif "hendecagonal" in name_lower: sides = 11
            elif "dodecagonal" in name_lower: sides = 12

        menu = QMenu(self)
        action = QAction(f"Visualize {full_name}...", self)
        action.triggered.connect(lambda: self._open_geometry_window(sides, index, mode))
        menu.addAction(action)
        menu.exec(event.globalPos())

    def _open_geometry_window(self, sides: int, index: int, mode: str):
        """Open the geometry visualizer with pre-filled values."""
        from pillars.geometry.ui.polygonal_number_window import PolygonalNumberWindow
        
        if not self.window_manager:
            print("No window manager found, cannot open visualizer")
            return

        win_id = "geometry_window_shared"
        # Open logic: If already open, it returns the instance.
        win = self.window_manager.open_window(win_id, PolygonalNumberWindow, window_manager=self.window_manager)
        
        if win:
            # Set values programmatically
            # Block signals to prevent redundant renders if desired, or let it render
            if win.mode_combo:
                idx = win.mode_combo.findData(mode)
                if idx >= 0: win.mode_combo.setCurrentIndex(idx)
            
            if win.sides_spin: win.sides_spin.setValue(sides)
            if win.index_spin: win.index_spin.setValue(index)
            
            # Force a re-render/update if needed by calling private method (hacky but effective)
            # Or rely on valueChanged signals which should have fired
            
            win.raise_()
            win.activateWindow()


    def _update_tab(self, tab: QWidget, member: QuadsetMember):
        """Update a tab with a member's values and properties."""
        # Update Header Values
        dec_lbl = tab.findChild(QLabel, "decimal_val")
        tern_lbl = tab.findChild(QLabel, "ternary_val")
        glyph = tab.findChild(QuadsetGlyph, "ternary_glyph")
        
        if dec_lbl:
            dec_lbl.setText(f"{member.decimal:,}")
        if tern_lbl:
            tern_lbl.setText(member.ternary)
        if glyph:
            glyph.set_ternary(member.ternary)
            
        # Get Properties from model
        props = member.properties
        if not props:
            return  # Should not happen for calculated members
        
        # Rebuild Cards
        container = tab.findChild(QWidget, "cardsContainer")
        if not container:
            return
            
        layout = container.layout()
        # Clear existing
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 1. Type Card
        checks = []
        if props.get('is_prime'): 
            checks.append(f"PRIME (Ordinal: {props.get('prime_ordinal')})")
        if props.get('is_square'): checks.append("PERFECT SQUARE")
        if props.get('is_cube'): checks.append("PERFECT CUBE")
        if props.get('is_fibonacci'): checks.append("FIBONACCI")
        
        type_str = ", ".join(checks) if checks else "Composite / Regular"
        layout.addWidget(PropertyCard("Number Type", type_str))
        
        # 2. Factorization Card
        pf = props.get('prime_factors', [])
        if pf:
            pf_str = " × ".join([f"{p}{get_super(str(e))}" if e > 1 else str(p) for p, e in pf])
            layout.addWidget(PropertyCard("Prime Factorization", pf_str))
        
        # 3. Factors Detail Card
        factors = props.get('factors', [])
        count = len(factors)
        f_sum = props.get('sum_factors', 0)
        ali_sum = props.get('aliquot_sum', 0)
        
        detail_lines = [
            f"Count: {count}",
            f"Sum: {f_sum:,}",
            f"Aliquot Sum: {ali_sum:,}"
        ]
        
        abundance = props.get('abundance_status', '')
        if abundance:
            diff = props.get('abundance_diff', 0)
            status_line = f"Status: {abundance}"
            if diff: status_line += f" (by {diff:,})"
            detail_lines.append(status_line)
            
        layout.addWidget(PropertyCard("Factors Analysis", "\n".join(detail_lines)))
        layout.addWidget(PropertyCard("All Factors", str(factors)))

        # 4. Geometry Card
        polys = props.get('polygonal_info', [])
        centered = props.get('centered_polygonal_info', [])
        if polys or centered:
            poly_text = ""
            if polys:
                poly_text += "Polygonal:\n" + "\n".join([f"• {p}" for p in polys])
            if centered:
                if poly_text: poly_text += "\n\n"
                poly_text += "Centered:\n" + "\n".join([f"• {c}" for c in centered])
            layout.addWidget(PropertyCard("Geometric Properties", poly_text, context_menu_handler=self._handle_geometry_menu))
            
        # 5. Digits Card
        d_sum = props.get('digit_sum', 0)
        layout.addWidget(PropertyCard("Digit Sum", str(d_sum)))
        
        layout.addStretch()
        
    def _create_gematria_tab(self) -> QWidget:
        """Create the Gematria Database tab with sub-tabs for each number."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Sub-tabs for each number type
        self.gem_tabs = QTabWidget()
        
        # We need keys: 'original', 'conrune', 'reverse', 'reciprocal', 'upper_diff', 'lower_diff'
        # Let's verify standard keys. QuadsetResult has members.
        # We will create tabs dynamically or statically?
        # Ideally statically so we can access them.
        
        self.gem_tables = {} # Map 'key' -> QTableWidget
        
        keys = [
            ("Original", "original"),
            ("Conrune", "conrune"),
            ("Reverse", "reverse"),
            ("Reciprocal", "reciprocal"),
            ("Upper Diff", "upper_diff"),
            ("Lower Diff", "lower_diff")
        ]
        
        for label, key in keys:
             sub_tab = QWidget()
             sub_layout = QVBoxLayout(sub_tab)
             sub_layout.setContentsMargins(0, 0, 0, 0)
             
             table = QTableWidget()
             table.setColumnCount(4)
             table.setHorizontalHeaderLabels(["Word", "Method", "Tags", "Notes"])
             table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
             table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
             table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
             table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
             table.setAlternatingRowColors(True)
             table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
             table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
             table.setWordWrap(True)
             
             sub_layout.addWidget(table)
             self.gem_tabs.addTab(sub_tab, label)
             self.gem_tables[key] = table
             
        layout.addWidget(self.gem_tabs)
        return tab

    def _update_gematria_tab(self, result: QuadsetResult):
        """Query database and update tables for each number."""
        # Map result members to keys
        # original, conrune, reverse, reciprocal are in result.members
        # upper/lower diff are separate attributes
        
        tasks = []
        
        # Members (first 4)
        if len(result.members) >= 4:
            tasks.append(("original", result.members[0].decimal))
            tasks.append(("conrune", result.members[1].decimal))
            tasks.append(("reverse", result.members[2].decimal))
            tasks.append(("reciprocal", result.members[3].decimal))
            
        # Diffs
        tasks.append(("upper_diff", result.upper_diff.decimal))
        tasks.append(("lower_diff", result.lower_diff.decimal))
        
        for key, value in tasks:
            table = self.gem_tables.get(key)
            if table:
                self._populate_gematria_table(table, value)

    def _populate_gematria_table(self, table: QTableWidget, value: int):
        """Fetch rows from DB where value matches and populate table."""
        table.setRowCount(0)
        
        try:
            with get_db_session() as db:
                # Query CalculationEntity
                # We want entries where value == value
                entries = db.query(CalculationEntity).filter(CalculationEntity.value == value).limit(100).all()
                
                table.setRowCount(len(entries))
                for row, entry in enumerate(entries):
                    # Word
                    table.setItem(row, 0, QTableWidgetItem(entry.text))
                    # Method
                    table.setItem(row, 1, QTableWidgetItem(entry.method))
                    # Tags
                    tags_str = entry.tags
                    # Clean up json string display if needed, or just show raw string if user wants quick view
                    # Usually tags is '["tag1", "tag2"]'
                    try:
                        import json
                        tags_list = json.loads(tags_str)
                        if isinstance(tags_list, list):
                            tags_display = ", ".join(tags_list)
                        else:
                            tags_display = str(tags_str)
                    except:
                        tags_display = str(tags_str)

                    table.setItem(row, 2, QTableWidgetItem(tags_display))
                    # Notes
                    table.setItem(row, 3, QTableWidgetItem(entry.notes))
                
                table.resizeRowsToContents()
                    
        except Exception as e:
            print(f"Error fetching gematria for {value}: {e}")
            pass # Fail gracefully

    def _update_advanced_tab(self, result: QuadsetResult):
        """Update the advanced tab values from the result object."""
        def _set_label(name: str, value: str):
            label = self.tab_advanced.findChild(QLabel, name)
            if label:
                label.setText(value)

        _set_label("advanced_sum", f"{result.quadset_sum:,}")
        _set_label("advanced_septad", f"{result.septad_total:,}")
        _set_label("advanced_upper_diff", f"{result.upper_diff.decimal:,}")
        _set_label("advanced_lower_diff", f"{result.lower_diff.decimal:,}")
        _set_label("advanced_transgram", result.transgram.ternary)
        _set_label("advanced_transgram_dec", f"{result.transgram.decimal:,}")

        patterns_area = self.tab_advanced.findChild(QTextEdit, "advanced_patterns")
        if patterns_area:
            patterns_area.setPlainText(result.pattern_summary)

    def _clear_tabs(self):
        """Clear all tabs."""
        # This implementation remains largely same but could be simplified if we created an "EmptyQuadsetResult"
        # For now, manual clearing is fine.
        for panel in [self.panel_original, self.panel_conrune, 
                     self.panel_reversal, self.panel_conrune_rev,
                     self.panel_upper_diff, self.panel_lower_diff]:
             panel.findChild(QLabel, "decimal_val").setText("-")
             panel.findChild(QLabel, "ternary_val").setText("-")
             glyph = panel.findChild(QuadsetGlyph, "ternary_glyph")
             if glyph: glyph.set_ternary("")

        for tab in [self.tab_original, self.tab_conrune, 
                   self.tab_reversal, self.tab_conrune_rev,
                   self.tab_upper_diff, self.tab_lower_diff]:
            tab.findChild(QLabel, "decimal_val").setText("-")
            tab.findChild(QLabel, "ternary_val").setText("-")
            container = tab.findChild(QWidget, "cardsContainer")
            if container:
                l = container.layout()
                while l.count():
                    c = l.takeAt(0)
                    if c.widget(): c.widget().deleteLater()
            
            glyph = tab.findChild(QuadsetGlyph, "ternary_glyph")
            if glyph: glyph.set_ternary("")

        if hasattr(self, "tab_advanced"):
            for name in ["advanced_sum", "advanced_septad", "advanced_upper_diff", 
                         "advanced_lower_diff", "advanced_transgram", "advanced_transgram_dec"]:
                label = self.tab_advanced.findChild(QLabel, name)
                if label: label.setText("-")
            patterns_area = self.tab_advanced.findChild(QTextEdit, "advanced_patterns")
            if patterns_area: patterns_area.clear()

        # Clear Gematria tables
        if hasattr(self, "gem_tables"):
            for key in self.gem_tables:
                self.gem_tables[key].setRowCount(0)

    def _on_input_changed(self, text: str):
        """Handle input change, delegate calculation to engine."""
        if not text:
            self._clear_tabs()
            return
            
        try:
            decimal_val = int(text)
            result = self.engine.calculate(decimal_val)
            self._display_results(result)
        except ValueError:
            # Optionally clear or indicate error, for now just ignore incomplete input
            pass

    def _display_results(self, result: QuadsetResult):
        """Distribute the QuadsetResult to the UI components."""
        # 1. Update Grid Panels
        self._update_panel(self.panel_original, result.original)
        self._update_panel(self.panel_conrune, result.conrune)
        self._update_panel(self.panel_reversal, result.reversal)
        self._update_panel(self.panel_conrune_rev, result.conrune_reversal)
        self._update_panel(self.panel_upper_diff, result.upper_diff)
        self._update_panel(self.panel_lower_diff, result.lower_diff)
        
        # 2. Update Detail Tabs
        self._update_tab(self.tab_original, result.original)
        self._update_tab(self.tab_conrune, result.conrune)
        self._update_tab(self.tab_reversal, result.reversal)
        self._update_tab(self.tab_conrune_rev, result.conrune_reversal)
        self._update_tab(self.tab_upper_diff, result.upper_diff)
        self._update_tab(self.tab_lower_diff, result.lower_diff)
        
        # 3. Update Advanced Tab
        self._update_advanced_tab(result)

        # 4. Update Gematria Tab
        self._update_gematria_tab(result)

