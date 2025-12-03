"""Quadset Analysis tool window."""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QGroupBox, QTabWidget, QWidget,
    QTextEdit, QScrollArea, QGridLayout, QFrame,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QPointF, QSize
from PyQt6.QtGui import QFont, QPainter, QPen, QColor

from ..services.ternary_service import TernaryService
from ..services.number_properties import NumberPropertiesService


class QuadsetGlyph(QWidget):
    """Visualize ternary strings as Taoist line glyphs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ternary = ""
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self.setMinimumSize(90, 100)

    def sizeHint(self):
        return QSize(140, 160)

    def minimumSizeHint(self):
        return QSize(90, 120)

    def set_ternary(self, value: str):
        self._ternary = value or ""
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
        margin_x = width * 0.1
        line_length = width - margin_x * 2
        line_height = max(min(height / (total + 0.3), 28), 12)
        base_pen = QPen(QColor("#111827"), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)

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
                gap = line_length * 0.2
                segment = (line_length - gap) / 2
                painter.drawLine(
                    QPointF(margin_x, y),
                    QPointF(margin_x + segment, y),
                )
                painter.drawLine(
                    QPointF(margin_x + segment + gap, y),
                    QPointF(margin_x + line_length, y),
                )


class QuadsetAnalysisWindow(QDialog):
    """Window for Quadset Analysis with detailed property tabs."""
    
    def __init__(self, parent=None):
        """Initialize the window."""
        super().__init__(parent)
        self.ternary_service = TernaryService()
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Quadset Analysis")
        self.setMinimumSize(900, 700)
        
        # Main layout
        layout = QVBoxLayout(self)
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
        self.input_field.textChanged.connect(self._calculate_quadset)
        
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
        
        self.tabs.addTab(self.tab_overview, "Quadset Overview")
        self.tabs.addTab(self.tab_original, "Original")
        self.tabs.addTab(self.tab_conrune, "Conrune")
        self.tabs.addTab(self.tab_reversal, "Reversal")
        self.tabs.addTab(self.tab_conrune_rev, "Conrune Reversal")
        self.tabs.addTab(self.tab_upper_diff, "Upper Diff")
        self.tabs.addTab(self.tab_lower_diff, "Lower Diff")
        
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

    def _update_panel(self, panel: QGroupBox, decimal: int, ternary: str):
        """Update the values in a panel."""
        dec_lbl = panel.findChild(QLabel, "decimal_val")
        tern_lbl = panel.findChild(QLabel, "ternary_val")
        glyph = panel.findChild(QuadsetGlyph, "ternary_glyph")
        
        if dec_lbl:
            dec_lbl.setText(f"{decimal:,}")
        if tern_lbl:
            tern_lbl.setText(ternary)
        if glyph:
            glyph.set_ternary(ternary)

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
        
        props_text = QTextEdit()
        props_text.setObjectName("properties_text")
        props_text.setReadOnly(True)
        props_text.setStyleSheet("""
            QTextEdit {
                font-family: 'Courier New', monospace;
                font-size: 11pt;
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                padding: 12px;
            }
        """)
        layout.addWidget(props_text)
        
        return tab

    def _update_tab(self, tab: QWidget, decimal: int, ternary: str):
        """Update a tab with new values and properties."""
        # Update Header Values
        dec_lbl = tab.findChild(QLabel, "decimal_val")
        tern_lbl = tab.findChild(QLabel, "ternary_val")
        glyph = tab.findChild(QuadsetGlyph, "ternary_glyph")
        
        if dec_lbl:
            dec_lbl.setText(f"{decimal:,}")
        if tern_lbl:
            tern_lbl.setText(ternary)
        if glyph:
            glyph.set_ternary(ternary)
            
        # Calculate Properties
        props = NumberPropertiesService.get_properties(decimal)
        
        # Format Properties Text
        lines = []
        
        # Basic Checks
        checks = []
        if props['is_prime']: 
            checks.append(f"PRIME (Ordinal: {props['prime_ordinal']})")
        if props['is_square']: checks.append("PERFECT SQUARE")
        if props['is_cube']: checks.append("PERFECT CUBE")
        if props['is_fibonacci']: checks.append("FIBONACCI")
        
        if checks:
            lines.append(f"Type: {', '.join(checks)}")
        else:
            lines.append("Type: Composite / Regular")
            
        lines.append("-" * 40)
        
        # Polygonal Info
        if props['polygonal_info']:
            lines.append("Polygonal Numbers:")
            for info in props['polygonal_info']:
                lines.append(f"  • {info}")
        
        if props['centered_polygonal_info']:
            lines.append("Centered Polygonal Numbers:")
            for info in props['centered_polygonal_info']:
                lines.append(f"  • {info}")
                
        if props['polygonal_info'] or props['centered_polygonal_info']:
            lines.append("-" * 40)
        
        # Digits
        lines.append(f"Digit Sum: {props['digit_sum']}")
        lines.append("-" * 40)
        
        # Factors & Abundance
        factors = props['factors']
        if len(factors) > 20:
            lines.append(f"Factors ({len(factors)}): {str(factors[:20])[:-1]}...]")
        else:
            lines.append(f"Factors ({len(factors)}): {factors}")
            
        lines.append(f"Sum of Factors: {props['sum_factors']}")
        lines.append(f"Aliquot Sum:    {props['aliquot_sum']}")
        
        abundance_msg = props['abundance_status']
        if props['abundance_status'] != "Perfect":
            abundance_msg += f" (by {props['abundance_diff']})"
        lines.append(f"Status:         {abundance_msg}")
        
        lines.append("-" * 40)
            
        # Prime Factorization
        pf = props['prime_factors']
        pf_str = " * ".join([f"{p}^{e}" if e > 1 else str(p) for p, e in pf])
        lines.append(f"Prime Factorization: {pf_str}")
        
        # Update Text Area
        text_area = tab.findChild(QTextEdit, "properties_text")
        if text_area:
            text_area.setPlainText("\n".join(lines))

    def _clear_tabs(self):
        """Clear all tabs."""
        # Clear overview panels
        for panel in [self.panel_original, self.panel_conrune, 
                     self.panel_reversal, self.panel_conrune_rev,
                     self.panel_upper_diff, self.panel_lower_diff]:
            self._update_panel(panel, 0, "-")
            panel.findChild(QLabel, "decimal_val").setText("-")

        # Clear detail tabs
        for tab in [self.tab_original, self.tab_conrune, 
                   self.tab_reversal, self.tab_conrune_rev,
                   self.tab_upper_diff, self.tab_lower_diff]:
            tab.findChild(QLabel, "decimal_val").setText("-")
            tab.findChild(QLabel, "ternary_val").setText("-")
            tab.findChild(QTextEdit, "properties_text").clear()
            glyph = tab.findChild(QuadsetGlyph, "ternary_glyph")
            if glyph:
                glyph.set_ternary("")

    def _calculate_quadset(self, text: str):
        """Perform the quadset calculations and update tabs."""
        if not text:
            self._clear_tabs()
            return
            
        try:
            # 1. Original
            decimal_orig = int(text)
            ternary_orig = self.ternary_service.decimal_to_ternary(decimal_orig)
            self._update_tab(self.tab_original, decimal_orig, ternary_orig)
            self._update_panel(self.panel_original, decimal_orig, ternary_orig)
            
            # 2. Conrune
            ternary_conrune = self.ternary_service.conrune_transform(ternary_orig)
            decimal_conrune = self.ternary_service.ternary_to_decimal(ternary_conrune)
            self._update_tab(self.tab_conrune, decimal_conrune, ternary_conrune)
            self._update_panel(self.panel_conrune, decimal_conrune, ternary_conrune)
            
            # 3. Reversal
            ternary_rev = self.ternary_service.reverse_ternary(ternary_orig)
            decimal_rev = self.ternary_service.ternary_to_decimal(ternary_rev)
            self._update_tab(self.tab_reversal, decimal_rev, ternary_rev)
            self._update_panel(self.panel_reversal, decimal_rev, ternary_rev)
            
            # 4. Conrune of Reversal
            ternary_conrune_rev = self.ternary_service.conrune_transform(ternary_rev)
            decimal_conrune_rev = self.ternary_service.ternary_to_decimal(ternary_conrune_rev)
            self._update_tab(self.tab_conrune_rev, decimal_conrune_rev, ternary_conrune_rev)
            self._update_panel(self.panel_conrune_rev, decimal_conrune_rev, ternary_conrune_rev)
            
            # 5. Differences
            diff_upper = abs(decimal_orig - decimal_conrune)
            ternary_upper_diff = self.ternary_service.decimal_to_ternary(diff_upper)
            self._update_tab(self.tab_upper_diff, diff_upper, ternary_upper_diff)
            self._update_panel(self.panel_upper_diff, diff_upper, ternary_upper_diff)
            
            diff_lower = abs(decimal_rev - decimal_conrune_rev)
            ternary_lower_diff = self.ternary_service.decimal_to_ternary(diff_lower)
            self._update_tab(self.tab_lower_diff, diff_lower, ternary_lower_diff)
            self._update_panel(self.panel_lower_diff, diff_lower, ternary_lower_diff)
            
        except ValueError:
            self._clear_tabs()
