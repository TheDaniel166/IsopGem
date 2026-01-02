"""
Quadset Analysis Window - The Ternary Transformation Explorer.
A comprehensive UI for analyzing the Quadset (Original, Conrune, Reversal, ConrReversal) and its mathematical properties.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QGroupBox, QTabWidget, QWidget,
    QTextEdit, QScrollArea, QGridLayout, QFrame,
    QSizePolicy, QMenu, QTableWidget, QTableWidgetItem, QHeaderView,
    QStackedWidget, QListWidget, QListWidgetItem, QGraphicsDropShadowEffect,
    QComboBox
)
from PyQt6.QtCore import Qt, QPointF, QSize, QRect
from PyQt6.QtGui import QFont, QPainter, QPen, QColor, QAction, QTextCursor, QPixmap, QBrush

from ..services.quadset_engine import QuadsetEngine
from ..models import QuadsetResult, QuadsetMember
from shared.ui import WindowManager
from shared.database import get_db_session
from shared.signals.navigation_bus import navigation_bus
from shared.models.gematria import CalculationEntity
from shared.ui.theme import COLORS, get_card_style, get_app_stylesheet



from shared.ui.substrate_widget import SubstrateWidget

def get_super(x):
    """
    Retrieve super logic.
    
    Args:
        x: Description of x.
    
    Returns:
        Result of get_super operation.
    """
    normal = "0123456789"
    super_s = "⁰¹²³⁴⁵⁶⁷⁸⁹"
    res = x.maketrans(''.join(normal), ''.join(super_s))
    return x.translate(res)


class CardTextEdit(QTextEdit):
    """QTextEdit that delegates context menu events."""
    def __init__(self, text, parent=None, context_menu_handler=None):
        """
          init   logic.
        
        Args:
            text: Description of text.
            parent: Description of parent.
            context_menu_handler: Description of context_menu_handler.
        
        """
        super().__init__(text, parent)
        self.context_menu_handler = context_menu_handler

    def contextMenuEvent(self, event):
        """
        Contextmenuevent logic.
        
        Args:
            event: Description of event.
        
        """
        if self.context_menu_handler:
            self.context_menu_handler(event, self)
        else:
            super().contextMenuEvent(event)


class QuadsetGlyph(QWidget):
    """Visualize ternary strings as Taoist line glyphs."""

    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self._ternary = ""
    def sizeHint(self):
        """
        Sizehint logic.
        
        """
        return QSize(80, 100)

    def minimumSizeHint(self):
        """
        Minimumsizehint logic.
        
        """
        return QSize(60, 80)

    def set_ternary(self, ternary: str) -> None:
        """Update the glyph with a ternary string and repaint."""
        self._ternary = ternary or ""
        self.update()

    def _normalized_digits(self) -> list[str]:
        digits = [d for d in self._ternary if d in {"0", "1", "2"}]
        return digits or ["0"]

    def paintEvent(self, _event):  # noqa: N802
        """
        Paintevent logic.
        
        Args:
            _event: Description of _event.
        
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(255, 255, 255, 0))

        digits = self._normalized_digits()

        total = len(digits)
        height = self.height()
        width = self.width()
        
        # INCREASED visual dominance
        MAX_LINE_WIDTH = 250 
        line_length = min(width * 0.9, MAX_LINE_WIDTH) 
        margin_x = (width - line_length) / 2
        
        # Tighter vertical spacing
        # Reduce max line height to 12, min to 4
        # Denominator adjust for tighter packing
        line_height = max(min(height / (total + 0.5), 24), 8) # slightly larger max
        base_pen = QPen(QColor(COLORS['text_primary']), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)

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
    
    def __init__(self, title: str, content: str = "", parent=None, link_handler=None):
        """
          init   logic.
        
        Args:
            title: Description of title.
            content: Description of content.
            parent: Description of parent.
            link_handler: Description of link_handler.
        
        """
        super().__init__(parent)
        self.setObjectName("propertyCard")
        self.setStyleSheet(get_card_style() + f"background-color: {COLORS['surface']};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #64748b; font-size: 10pt; font-weight: 600; text-transform: uppercase;")
        layout.addWidget(self.title_label)
        
        self.content_label = QLabel(content)
        self.content_label.setWordWrap(True)
        self.content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.content_label.setOpenExternalLinks(False) # We handle internally
        
        if link_handler:
            self.content_label.linkActivated.connect(link_handler)
            
        self.content_label.setStyleSheet("""
            QLabel {
                color: #0f172a; 
                font-size: 11pt; 
                font-family: 'Segoe UI', sans-serif;
                background-color: transparent;
                border: none;
            }
        """)
        
        layout.addWidget(self.content_label)

    def set_content(self, text: str):
        """
        Configure content logic.
        
        Args:
            text: Description of text.
        
        """
        self.content_label.setText(text)





class QuadsetAnalysisWindow(QMainWindow):
    """Window for Quadset Analysis with detailed property tabs."""
    
    def __init__(self, window_manager: WindowManager = None, parent=None, initial_value=None, **kwargs):
        """
          init   logic.
        
        Args:
            window_manager: Description of window_manager.
            parent: Description of parent.
            initial_value: Description of initial_value.
        
        """
        super().__init__(parent)
        self.window_manager = window_manager
        self.setWindowTitle("Quadset Analysis")
        self.resize(1000, 800)
        
        # Engine for calculations
        self.engine = QuadsetEngine()
        
        self._setup_ui()
        
        if initial_value is not None:
            self.input_field.setText(str(initial_value))
        
    def _setup_ui(self):
        """Set up the user interface with vertical sidebar navigation."""
        self.setWindowTitle("Quadset Analysis")
        self.setMinimumSize(1200, 850)
        
        # Level 0: The Substrate (Thematic background for Quadset Analysis)
        import os
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        bg_path = os.path.join(base_path, "assets", "textures", "quadset_substrate.png")
        
        central = SubstrateWidget(bg_path)
        self.setCentralWidget(central)

        # Main Layout (Horizontal split)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. Sidebar (Navigation)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setFrameShape(QFrame.Shape.NoFrame)
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['surface']};
                border-right: 1px solid {COLORS['border']};
                outline: none;
                padding-top: 20px;
            }}
            QListWidget::item {{
                height: 60px;
                padding-left: 16px;
                color: {COLORS['text_secondary']};
                border-left: 4px solid transparent;
            }}
            QListWidget::item:selected {{
                color: {COLORS['text_primary']};
                background-color: {COLORS['background_alt']};
                border-left: 4px solid {COLORS['primary']};
                font-weight: bold;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        
        # 2. Content Area
        content_container = QWidget()
        content_container.setStyleSheet("background-color: transparent;")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(24)
        
        # Title & Input (Global Header)
        header_layout = QVBoxLayout()
        header_layout.setSpacing(16)
        
        title_label = QLabel("Quadset Analysis")
        title_label.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            font-size: 32pt;
            font-weight: 700;
            letter-spacing: -1px;
        """)
        header_layout.addWidget(title_label)
        
        # Input Section
        input_frame = QFrame()
        input_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(16, 12, 16, 12)
        
        input_label = QLabel("Input:")
        input_label.setStyleSheet(f"font-size: 14pt; font-weight: 600; color: {COLORS['text_secondary']};")
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter decimal...")
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                font-size: 16pt; 
                padding: 4px;
                background: transparent;
                border: none;
                color: {COLORS['text_primary']};
            }}
        """)
        self.input_field.textChanged.connect(self._on_input_changed)
        
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_field)
        header_layout.addWidget(input_frame)
        
        content_layout.addLayout(header_layout)
        
        # Stacked Pages
        self.stack = QStackedWidget()
        self.tab_overview = self._create_overview_tab()
        self.tab_original = self._create_detail_tab("Original")
        self.tab_conrune = self._create_detail_tab("Conrune")
        self.tab_reversal = self._create_detail_tab("Reune")
        self.tab_conrune_rev = self._create_detail_tab("ConReune")
        self.tab_upper_diff = self._create_detail_tab("A - B")
        self.tab_lower_diff = self._create_detail_tab("C - D")
        self.tab_advanced = self._create_advanced_tab()
        self.tab_gematria = self._create_gematria_tab()
        
        self.pages = [
            self.tab_overview,
            self.tab_original, self.tab_conrune, self.tab_reversal, self.tab_conrune_rev,
            self.tab_upper_diff, self.tab_lower_diff,
            self.tab_advanced, self.tab_gematria
        ]
        
        for page in self.pages:
            self.stack.addWidget(page)
            
        content_layout.addWidget(self.stack)
        
        # Populate Sidebar
        self.nav_items = [
            "Overview",
            "Original", "Conrune", "Reune", "ConReune",
            "A - B", "C - D",
            "Advanced", "Gematria"
        ]
        self.sidebar.addItems(self.nav_items)
        self.sidebar.item(0).setSelected(True)
        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(content_container)

    def _update_sidebar_labels(self, result: QuadsetResult):
        """Update sidebar items with calculated values."""
        members = [
            result.original, result.conrune, result.reversal, result.conrune_reversal,
            result.upper_diff, result.lower_diff
        ]
        roles = [
            "Original", "Conrune", "Reune", "ConReune",
            "A - B", "C - D"
        ]
        for i, member in enumerate(members):
            item = self.sidebar.item(i + 1)
            if member and member.decimal is not None:
                item.setText(f"{member.decimal}\n{roles[i]}")
            else:
                item.setText(roles[i])
        
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
        self.panel_original = self._create_panel("ORIGINAL")
        self.panel_conrune = self._create_panel("CONRUNE")
        self.panel_reversal = self._create_panel("REUNE")
        self.panel_conrune_rev = self._create_panel("CONREUNE")
        
        # Add to grid
        grid.addWidget(self.panel_original, 0, 0)
        grid.addWidget(self.panel_conrune, 0, 1)
        grid.addWidget(self.panel_reversal, 1, 0)
        grid.addWidget(self.panel_conrune_rev, 1, 1)
        
        layout.addLayout(grid)
        
        # Differences Section
        diff_layout = QHBoxLayout()
        diff_layout.setSpacing(20)
        
        self.panel_upper_diff = self._create_panel("A - B")
        self.panel_lower_diff = self._create_panel("C - D")
        
        diff_layout.addWidget(self.panel_upper_diff)
        diff_layout.addWidget(self.panel_lower_diff)
        
        layout.addLayout(diff_layout)
        
        # Set content to scroll area
        scroll.setWidget(content)
        
        return scroll

    def _create_panel(self, title: str) -> QFrame:
        """Create a standardized panel using 'The Canvas' layout with centered text and tint."""
        group = QFrame()
        # Custom tinted surface color
        tint_color = "#1e293b" # Slate-800, standard surface
        # Let's try a slightly lighter/bluer tint for 'professional' look? 
        # Actually sticking to surface is safer for consistency, but maybe opacity?
        # User asked for different tint. Let's try a subtle gradient or just the border.
        # I'll use a slightly different background color.
        
        group.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']}; 
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 40))
        group.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 24, 20, 24)
        
        # 1. Title (Top)
        title_lbl = QLabel(title)
        title_lbl.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        title_lbl.setStyleSheet(f"font-weight: 800; font-size: 11pt; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 1.5px;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter) # Centered
        layout.addWidget(title_lbl)
        
        # 2. Glyph (Center - The Star)
        glyph = QuadsetGlyph()
        glyph.setObjectName("ternary_glyph")
        glyph.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        glyph.setMinimumHeight(120)
        layout.addWidget(glyph)
        
        # 3. Footer (Bottom - Just Values)
        # Use a grid or horizontal layout where items are centered
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(0) 
        
        # Decimal Wrapper (Left Half)
        dec_wrapper = QFrame()
        dec_layout_inner = QVBoxLayout(dec_wrapper)
        dec_layout_inner.setContentsMargins(0,0,0,0)
        
        dec_val = QLabel("-")
        dec_val.setObjectName("decimal_val")
        dec_val.setStyleSheet(f"font-size: 32pt; font-weight: 700; color: {COLORS['text_primary']};")
        dec_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dec_layout_inner.addWidget(dec_val)
        
        footer_layout.addWidget(dec_wrapper)
        
        # Ternary Wrapper (Right Half)
        tern_wrapper = QFrame()
        tern_layout_inner = QVBoxLayout(tern_wrapper)
        tern_layout_inner.setContentsMargins(0,0,0,0)

        tern_val = QLabel("-")
        tern_val.setObjectName("ternary_val")
        tern_val.setStyleSheet(f"font-size: 18pt; font-family: 'Courier New', monospace; font-weight: bold; color: {COLORS['primary']};")
        tern_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tern_layout_inner.addWidget(tern_val)
        
        footer_layout.addWidget(tern_wrapper)
        
        layout.addLayout(footer_layout)
        
        # Force Glyph to take all available space
        layout.setStretch(0, 0)
        layout.setStretch(1, 1) # Glyph
        layout.setStretch(2, 0)
        
        return group

    def _update_panel(self, panel: QWidget, member: QuadsetMember):
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
        """Create a tab widget for number details with Hero Card style (Adaptive Layout)."""
        # Main Tab Wrapper (Scroll Area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        # Content Widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(12)
        layout.setContentsMargins(40, 10, 40, 10)
        
        # 1. Hero Card
        hero_card = QFrame()
        hero_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']}; 
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 40))
        hero_card.setGraphicsEffect(shadow)
        
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setSpacing(12)
        hero_layout.setContentsMargins(20, 16, 20, 16)
        
        # Title
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet(f"font-weight: 800; font-size: 12pt; color: {COLORS['text_secondary']}; letter-spacing: 2px;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(title_lbl)

        # Glyph
        glyph = QuadsetGlyph()
        glyph.setObjectName("ternary_glyph")
        glyph.setMinimumHeight(100) 
        hero_layout.addWidget(glyph)

        # Footer (Values)
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(0)
        
        # Decimal Wrapper
        dec_wrapper = QFrame()
        dec_layout_inner = QVBoxLayout(dec_wrapper)
        dec_layout_inner.setContentsMargins(0,0,0,0)
        
        dec_val = QLabel("-")
        dec_val.setObjectName("decimal_val")
        dec_val.setStyleSheet(f"font-size: 32pt; font-weight: 700; color: {COLORS['text_primary']};")
        dec_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dec_layout_inner.addWidget(dec_val)
        
        footer_layout.addWidget(dec_wrapper)
        
        # Ternary Wrapper
        tern_wrapper = QFrame()
        tern_layout_inner = QVBoxLayout(tern_wrapper)
        tern_layout_inner.setContentsMargins(0,0,0,0)

        tern_val = QLabel("-")
        tern_val.setObjectName("ternary_val")
        tern_val.setStyleSheet(f"font-size: 16pt; font-family: 'Courier New', monospace; font-weight: bold; color: {COLORS['primary']};")
        tern_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tern_layout_inner.addWidget(tern_val)
        
        footer_layout.addWidget(tern_wrapper)
        
        hero_layout.addLayout(footer_layout)
        hero_layout.setStretch(1, 1) # Glyph grows
        
        layout.addWidget(hero_card)
        
        # 2. Properties Section
        props_label = QLabel("PROPERTIES")
        props_label.setStyleSheet(f"font-weight: 700; font-size: 11pt; color: {COLORS['text_secondary']}; letter-spacing: 1px; margin-top: 10px;")
        layout.addWidget(props_label)
        
        # Properties Container (Adaptive)
        cards_container = QWidget()
        cards_container.setObjectName("cardsContainer")
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setSpacing(12)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addWidget(cards_container)
        layout.addStretch()
        
        scroll.setWidget(content)
        return scroll

    def _create_advanced_tab(self) -> QWidget:
        """Create the advanced tab with quadset summary info using tinted cards."""
        # Main Tab Wrapper (Scroll Area)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")

        # Content Widget
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 20, 40, 20)

        # Helper to create a card
        def create_card():
            """
            Create card logic.
            
            """
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {COLORS['surface']}; 
                    border: 1px solid {COLORS['border']};
                    border-radius: 12px;
                }}
            """)
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(24)
            shadow.setOffset(0, 8)
            shadow.setColor(QColor(0, 0, 0, 40))
            card.setGraphicsEffect(shadow)
            return card

        # 1. Totals Card
        totals_card = create_card()
        totals_layout = QVBoxLayout(totals_card)
        totals_layout.setContentsMargins(24, 24, 24, 24)
        totals_layout.setSpacing(16)
        
        totals_header = QLabel("QUADSET TOTALS")
        totals_header.setStyleSheet(f"font-weight: 800; font-size: 11pt; color: {COLORS['text_secondary']}; letter-spacing: 2px;")
        totals_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        totals_layout.addWidget(totals_header)
        
        # Grid for Sum/Septad
        t_grid = QHBoxLayout()
        
        # Sum
        sum_container = QVBoxLayout()
        sum_lbl = QLabel("SUM")
        sum_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10pt; font-weight: bold;")
        sum_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sum_val = QLabel("-")
        sum_val.setObjectName("advanced_sum")
        sum_val.setStyleSheet(f"font-size: 28pt; font-weight: 700; color: {COLORS['text_primary']};")
        sum_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sum_container.addWidget(sum_lbl)
        sum_container.addWidget(sum_val)
        
        # Septad
        sept_container = QVBoxLayout()
        sept_lbl = QLabel("SEPTAD")
        sept_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10pt; font-weight: bold;")
        sept_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sept_val = QLabel("-")
        sept_val.setObjectName("advanced_septad")
        sept_val.setStyleSheet(f"font-size: 28pt; font-weight: 700; color: {COLORS['text_primary']};")
        sept_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sept_container.addWidget(sept_lbl)
        sept_container.addWidget(sept_val)
        
        t_grid.addLayout(sum_container)
        t_grid.addLayout(sept_container)
        totals_layout.addLayout(t_grid)
        layout.addWidget(totals_card)

        # 2. Transgram Card
        trans_card = create_card()
        trans_layout = QVBoxLayout(trans_card)
        trans_layout.setContentsMargins(24, 24, 24, 24)
        trans_layout.setSpacing(20)
        
        trans_header = QLabel("DIFFERENTIAL TRANSGRAM")
        trans_header.setStyleSheet(f"font-weight: 800; font-size: 11pt; color: {COLORS['text_secondary']}; letter-spacing: 2px;")
        trans_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trans_layout.addWidget(trans_header)
        
        # Diffs Row
        diff_row = QHBoxLayout()
        
        # Upper
        ud_layout = QVBoxLayout()
        ud_lbl = QLabel("A - B")
        ud_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10pt;")
        ud_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ud_val = QLabel("-")
        ud_val.setObjectName("advanced_upper_diff")
        ud_val.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {COLORS['text_primary']};")
        ud_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ud_layout.addWidget(ud_lbl)
        ud_layout.addWidget(ud_val)
        
        # Lower
        ld_layout = QVBoxLayout()
        ld_lbl = QLabel("C - D")
        ld_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10pt;")
        ld_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ld_val = QLabel("-")
        ld_val.setObjectName("advanced_lower_diff")
        ld_val.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {COLORS['text_primary']};")
        ld_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ld_layout.addWidget(ld_lbl)
        ld_layout.addWidget(ld_val)
        
        diff_row.addLayout(ud_layout)
        diff_row.addLayout(ld_layout)
        trans_layout.addLayout(diff_row)
        
        # Transgram Result
        tg_layout = QVBoxLayout()
        tg_layout.setSpacing(8)
        
        tg_lbl = QLabel("TRANSGRAM VALUE")
        tg_lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 10pt; font-weight: bold; margin-top: 10px;")
        tg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        tg_dec = QLabel("-")
        tg_dec.setObjectName("advanced_transgram_dec")
        tg_dec.setStyleSheet(f"font-size: 32pt; font-weight: 700; color: {COLORS['text_primary']};")
        tg_dec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        tg_tern = QLabel("-")
        tg_tern.setObjectName("advanced_transgram")
        tg_tern.setStyleSheet(f"font-size: 20pt; font-family: 'Courier New', monospace; font-weight: bold; color: {COLORS['primary']};")
        tg_tern.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        tg_layout.addWidget(tg_lbl)
        tg_layout.addWidget(tg_dec)
        tg_layout.addWidget(tg_tern)
        trans_layout.addLayout(tg_layout)
        
        layout.addWidget(trans_card)

        # 3. Pattern Summary Card
        pat_card = create_card()
        pat_layout = QVBoxLayout(pat_card)
        pat_layout.setContentsMargins(24, 24, 24, 24)
        
        pat_header = QLabel("PATTERN SUMMARY")
        pat_header.setStyleSheet(f"font-weight: 800; font-size: 11pt; color: {COLORS['text_secondary']}; letter-spacing: 2px;")
        pat_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pat_layout.addWidget(pat_header)
        
        # Use simple label for pattern if it fits, or text edit if long. 
        # Existing used QTextEdit. Let's stick to QTextEdit but styled minimally matching the theme.
        patterns_text = QTextEdit()
        patterns_text.setObjectName("advanced_patterns")
        patterns_text.setReadOnly(True)
        patterns_text.setStyleSheet(f"""
            QTextEdit {{
                font-family: 'Courier New', monospace;
                font-size: 11pt;
                background-color: {COLORS['background_alt']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 12px;
                color: {COLORS['text_primary']};
            }}
        """)
        pat_layout.addWidget(patterns_text)
        
        layout.addWidget(pat_card)

        layout.addStretch()
        
        scroll.setWidget(content)
        return scroll

    def _handle_link_activation(self, link: str):
        """Handle execution of geometry visualization links."""
        if link.startswith("geo3d:"):
            # 3D Figurate: geo3d:shape_type:index
            try:
                _, shape_type, index_str = link.split(":")
                index = int(index_str)
                self._open_figurate_3d_window(shape_type, index)
            except ValueError:
                print(f"Invalid 3D geometry link: {link}")
            return
            
        if not link.startswith("geo:"):
            return
            
        try:
            _, mode, sides_str, index_str = link.split(":")
            sides = int(sides_str)
            index = int(index_str)
            self._open_geometry_window(sides, index, mode)
        except ValueError:
            print(f"Invalid geometry link: {link}")

    def _open_figurate_3d_window(self, shape_type: str, index: int):
        """Open the 3D figurate visualizer with pre-filled values."""
    def _open_figurate_3d_window(self, shape_type: str, index: int):
        """Open the 3D figurate visualizer with pre-filled values."""
        if not self.window_manager:
            print("No window manager found, cannot open visualizer")
            return

        # Use signal bus
        navigation_bus.request_window.emit(
            "figurate_3d", 
            {
                "window_manager": self.window_manager,
                # We can't pass shape_type/index directly to init if the class doesn't support it,
                # but we can try to find it after opening if single instance or just rely on manual interaction for now.
                # However, looking at Figurate3DWindow, it might not take these in init yet.
                # Let's emit, then try to find and set.
            }
        )
        
        # Attempt to find the window we just requested (likely the most recent or unique one)
        # This relies on the window ID convention or allows multiple if supported.
        # But wait, Figurate3D key is "figurate_3d" and allow_multiple=True.
        # ID is "figurate_3d_N".
        # This is tricky for "allow_multiple".
        # Creating a dedicated navigation param would be better long term.
        # For now, we iterate active windows to find one.
        
        # WORKAROUND: Iterate active windows to find the one we likely just opened (or reusing)
        # OR: Modify Figurate3DWindow to accept these in __init__.
        # Getting the window instance via get_active_windows is the safest "no-code-change" way for target.
        
        # Actually, let's just attempt to get "figurate_3d_1" or scan.
        # Simpler: we just opened it.
        pass # The previous code returned 'win'.
        
        # We need to set the values.
        # Let's try to get the latest window of this type.
        start_count = self.window_manager._window_counters.get("figurate_3d", 0)
        win_id = f"figurate_3d_{start_count}" # Rough guess
        win = self.window_manager.get_window(win_id)
        if not win:
             # Fallback scan
             for w in self.window_manager.get_active_windows().values():
                 if w.property("window_type") == "figurate_3d":
                     win = w
                     break # Take any
        
        if win:
            # Map shape_type to combo index
            shape_map = {
                "tetrahedral": 0,
                "pyramidal": 1,
                "octahedral": 2,
                "cubic": 3,
            }
            combo_idx = shape_map.get(shape_type.lower(), 0)
            
            if hasattr(win, "shape_combo") and win.shape_combo:
                win.shape_combo.setCurrentIndex(combo_idx)
            if hasattr(win, "index_spin") and win.index_spin:
                win.index_spin.setValue(index)

    def _open_geometry_window(self, sides: int, index: int, mode: str):
        """Open the geometry visualizer with pre-filled values."""
    def _open_geometry_window(self, sides: int, index: int, mode: str):
        """Open the geometry visualizer with pre-filled values."""
        if not self.window_manager:
            print("No window manager found, cannot open visualizer")
            return

        navigation_bus.request_window.emit(
            "polygonal_number", 
            {"window_manager": self.window_manager}
        )
        
        # Similar logic to find the window instance
        win = None
        # Try to find generic or specific
        start_count = self.window_manager._window_counters.get("polygonal_number", 0)
        win_id = f"polygonal_number_{start_count}"
        win = self.window_manager.get_window(win_id)
        
        if not win:
             for w in self.window_manager.get_active_windows().values():
                 if w.property("window_type") == "polygonal_number":
                     win = w
                     break

        if win:
            # Set values programmatically
            if hasattr(win, "mode_combo") and win.mode_combo:
                idx = win.mode_combo.findData(mode)
                if idx >= 0: win.mode_combo.setCurrentIndex(idx)
            
            if hasattr(win, "sides_spin") and win.sides_spin: 
                win.sides_spin.setValue(sides)
            if hasattr(win, "index_spin") and win.index_spin: 
                win.index_spin.setValue(index)
            
            win.raise_()
            win.activateWindow()


    def _update_detail_tab(self, tab: QWidget, member: QuadsetMember):
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
            import re
            poly_text = ""
            if polys:
                poly_text += "<b>Polygonal:</b><br>" 
                for p in polys:
                    # Parse: "{Name} (Index: {N})"
                    match = re.search(r"(.*?) \(Index: (\d+)\)", p)
                    if match:
                        full_name = match.group(1)
                        index = match.group(2)
                        # Determine sides
                        mode = "polygonal"
                        sides = 3
                        # Helper for sides
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
                        
                        link = f"geo:{mode}:{sides}:{index}"
                        poly_text += f"<a href='{link}' style='text-decoration:none; color:#3b82f6;'>• {p}</a><br>"
                    else:
                        poly_text += f"• {p}<br>"

            if centered:
                if poly_text: poly_text += "<br>"
                poly_text += "<b>Centered:</b><br>"
                for c in centered:
                    match = re.search(r"(.*?) \(Index: (\d+)\)", c)
                    if match:
                        full_name = match.group(1)
                        index = match.group(2)
                        mode = "centered"
                        sides = 3
                        if "star" in full_name.lower(): mode = "star"; sides = 12 
                        
                        # Helper for sides (simplified repetition)
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
                        
                        link = f"geo:{mode}:{sides}:{index}"
                        poly_text += f"<a href='{link}' style='text-decoration:none; color:#3b82f6;'>• {c}</a><br>"
                    else:
                        poly_text += f"• {c}<br>"
                        
            layout.addWidget(PropertyCard("Geometric Properties", poly_text, link_handler=self._handle_link_activation))

        # 5. 3D Figurate Numbers Card
        figurate_3d = props.get('figurate_3d_info', [])
        if figurate_3d:
            import re
            fig3d_text = ""
            for f in figurate_3d:
                # Parse: "{Type} (Index: {N})"
                match = re.search(r"(.*?) \(Index: (\d+)\)", f)
                if match:
                    full_name = match.group(1)
                    index = match.group(2)
                    # Map name to shape_type
                    shape_type = "tetrahedral"  # default
                    name_lower = full_name.lower()
                    if "tetrahedral" in name_lower:
                        shape_type = "tetrahedral"
                    elif "pyramidal" in name_lower or "square pyramidal" in name_lower:
                        shape_type = "pyramidal"
                    elif "octahedral" in name_lower:
                        shape_type = "octahedral"
                    elif "cubic" in name_lower:
                        shape_type = "cubic"
                    
                    link = f"geo3d:{shape_type}:{index}"
                    fig3d_text += f"<a href='{link}' style='text-decoration:none; color:#3b82f6;'>• {f}</a><br>"
                else:
                    fig3d_text += f"• {f}<br>"
            layout.addWidget(PropertyCard("3D Figurate Numbers", fig3d_text, link_handler=self._handle_link_activation))

        # 6. Pronic Card (if applicable)
        if props.get('is_pronic'):
            pronic_idx = props.get('pronic_index', -1)
            pronic_text = f"{pronic_idx} × {pronic_idx + 1} = {pronic_idx * (pronic_idx + 1)}"
            layout.addWidget(PropertyCard("Pronic Number", f"Index: {pronic_idx}<br>{pronic_text}"))

        # 7. Happy/Sad Number Card
        is_happy = props.get('is_happy', False)
        happy_iters = props.get('happy_iterations', -1)
        happy_chain = props.get('happy_chain', [])
        
        # Format chain as: n → n → n → ...
        chain_str = " → ".join(str(x) for x in happy_chain)
        
        if is_happy:
            happy_text = f"😊 <b>Happy Number</b><br>Reached 1 in {happy_iters} iterations<br><br><b>Chain:</b><br>{chain_str}"
            layout.addWidget(PropertyCard("Happy Number", happy_text))
        else:
            # Show the chain leading into the cycle
            happy_text = f"😢 <b>Sad Number</b><br>Enters a cycle and never reaches 1<br><br><b>Chain:</b><br>{chain_str}<br>(cycle detected)"
            layout.addWidget(PropertyCard("Sad Number", happy_text))
            
        layout.addStretch()
        
    def _create_gematria_tab(self) -> QWidget:
        """Create the Gematria Database tab with vertical side tabs for each number."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(40, 20, 40, 20)
        
        # Tablet Container
        tablet = QFrame()
        tablet.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']}; 
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 40))
        tablet.setGraphicsEffect(shadow)
        
        tablet_layout = QVBoxLayout(tablet)
        tablet_layout.setSpacing(16)
        tablet_layout.setContentsMargins(20, 24, 20, 24)
        
        # Title
        title_lbl = QLabel("GEMATRIA DATABASE")
        title_lbl.setStyleSheet(f"font-weight: 800; font-size: 14pt; color: {COLORS['text_secondary']}; letter-spacing: 2px;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tablet_layout.addWidget(title_lbl)
        
        # Horizontal layout for side tabs + content
        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        
        # Side navigation list
        self.gem_sidebar = QListWidget()
        self.gem_sidebar.setFixedWidth(140)
        self.gem_sidebar.setFrameShape(QFrame.Shape.NoFrame)
        self.gem_sidebar.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['background_alt']};
                border-right: 1px solid {COLORS['border']};
                outline: none;
                padding-top: 8px;
            }}
            QListWidget::item {{
                height: 48px;
                padding-left: 12px;
                color: {COLORS['text_secondary']};
                border-left: 3px solid transparent;
            }}
            QListWidget::item:selected {{
                color: {COLORS['text_primary']};
                background-color: {COLORS['surface']};
                border-left: 3px solid {COLORS['primary']};
                font-weight: bold;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {COLORS['surface_hover']};
            }}
        """)
        
        # Stacked widget for content pages
        self.gem_stack = QStackedWidget()
        self.gem_stack.setStyleSheet(f"background-color: {COLORS['background_alt']};")
        
        # Define keys - labels will be updated dynamically with actual values
        self.gem_keys = [
            ("original", "Original"),
            ("conrune", "Conrune"),
            ("reverse", "Reune"),
            ("reciprocal", "ConReune"),
            ("upper_diff", "A - B"),
            ("lower_diff", "C - D")
        ]
        
        self.gem_tables = {}
        self.gem_list_items = {}  # Store list items for dynamic label updates
        
        for key, default_label in self.gem_keys:
            # Add item to sidebar
            item = QListWidgetItem(default_label)
            item.setData(Qt.ItemDataRole.UserRole, key)
            self.gem_sidebar.addItem(item)
            self.gem_list_items[key] = item
            
            # Create page with filters and table
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setContentsMargins(12, 12, 12, 12)
            page_layout.setSpacing(8)
            
            # Filter row
            filter_row = QHBoxLayout()
            filter_row.setSpacing(12)
            
            # Language filter
            lang_label = QLabel("Language:")
            lang_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 600;")
            filter_row.addWidget(lang_label)
            
            lang_combo = QComboBox()
            lang_combo.addItem("All Languages", "")
            lang_combo.setMinimumWidth(140)
            lang_combo.setStyleSheet(f"""
                QComboBox {{
                    background-color: {COLORS['surface']};
                    border: 1px solid {COLORS['border']};
                    border-radius: 6px;
                    padding: 6px 10px;
                }}
                QComboBox:focus {{
                    border-color: {COLORS['primary']};
                }}
            """)
            filter_row.addWidget(lang_combo)
            
            # Method filter
            method_label = QLabel("Method:")
            method_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-weight: 600;")
            filter_row.addWidget(method_label)
            
            method_combo = QComboBox()
            method_combo.addItem("All Methods", "")
            method_combo.setMinimumWidth(160)
            method_combo.setStyleSheet(lang_combo.styleSheet())
            filter_row.addWidget(method_combo)
            
            filter_row.addStretch()
            page_layout.addLayout(filter_row)
            
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
            table.setSortingEnabled(True)
            table.setStyleSheet(f"""
                QTableWidget {{
                    background-color: transparent;
                    gridline-color: {COLORS['border']};
                    border: none;
                }}
                QHeaderView::section {{
                    background-color: {COLORS['surface']};
                    color: {COLORS['text_secondary']};
                    border: none;
                    padding: 4px;
                }}
            """)
            
            # Connect filters to table filtering
            lang_combo.currentIndexChanged.connect(
                lambda _, t=table, lc=lang_combo, mc=method_combo: self._apply_gematria_filters(t, lc, mc)
            )
            method_combo.currentIndexChanged.connect(
                lambda _, t=table, lc=lang_combo, mc=method_combo: self._apply_gematria_filters(t, lc, mc)
            )
            
            page_layout.addWidget(table)
            self.gem_stack.addWidget(page)
            self.gem_tables[key] = table
            
            # Store combo references for dynamic population
            if not hasattr(self, 'gem_filter_combos'):
                self.gem_filter_combos = {}
            self.gem_filter_combos[key] = {'language': lang_combo, 'method': method_combo}
        
        # Connect sidebar selection to stack
        self.gem_sidebar.currentRowChanged.connect(self.gem_stack.setCurrentIndex)
        self.gem_sidebar.setCurrentRow(0)
        
        content_layout.addWidget(self.gem_sidebar)
        content_layout.addWidget(self.gem_stack, 1)
        
        tablet_layout.addLayout(content_layout)
        layout.addWidget(tablet)
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
            # Update sidebar label to show actual number
            if hasattr(self, 'gem_list_items') and key in self.gem_list_items:
                self.gem_list_items[key].setText(str(value))
            
            # Populate the table
            table = self.gem_tables.get(key)
            if table:
                self._populate_gematria_table(table, value, key)

    def _populate_gematria_table(self, table: QTableWidget, value: int, key: str = ""):
        """Fetch rows from DB where value matches and populate table."""
        table.setRowCount(0)
        
        # Track unique languages and methods for filter population
        languages = set()
        methods = set()
        
        try:
            with get_db_session() as db:
                entries = db.query(CalculationEntity).filter(CalculationEntity.value == value).limit(100).all()
                
                # Need 5 columns: Word, Method, Tags, Notes, Language (hidden)
                table.setColumnCount(5)
                table.setHorizontalHeaderLabels(["Word", "Method", "Tags", "Notes", "Language"])
                table.setColumnHidden(4, True)  # Hide language column
                
                table.setRowCount(len(entries))
                for row, entry in enumerate(entries):
                    # Word
                    table.setItem(row, 0, QTableWidgetItem(entry.text))
                    # Method
                    table.setItem(row, 1, QTableWidgetItem(entry.method))
                    methods.add(entry.method)
                    # Tags
                    tags_str = entry.tags
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
                    # Language (hidden column for filtering) - extract from language field
                    # Handle both "Hebrew" and "Hebrew (Standard)" formats
                    lang_raw = entry.language or ""
                    if "(" in lang_raw:
                        lang_parsed = lang_raw.split("(")[0].strip()
                    else:
                        lang_parsed = lang_raw.strip()
                    table.setItem(row, 4, QTableWidgetItem(lang_parsed))
                    languages.add(lang_parsed)
                    
                    # Track method separately
                    methods.add(entry.method)
                
                table.resizeRowsToContents()
                
                # Update filter combo boxes
                if hasattr(self, 'gem_filter_combos') and key in self.gem_filter_combos:
                    combos = self.gem_filter_combos[key]
                    
                    # Update language combo
                    lang_combo = combos['language']
                    lang_combo.blockSignals(True)
                    lang_combo.clear()
                    lang_combo.addItem("All Languages", "")
                    for lang in sorted(languages):
                        if lang:
                            lang_combo.addItem(lang, lang)
                    lang_combo.blockSignals(False)
                    
                    # Update method combo
                    method_combo = combos['method']
                    method_combo.blockSignals(True)
                    method_combo.clear()
                    method_combo.addItem("All Methods", "")
                    for method in sorted(methods):
                        if method:
                            method_combo.addItem(method, method)
                    method_combo.blockSignals(False)
                    
        except Exception as e:
            print(f"Error fetching gematria for {value}: {e}")
            pass # Fail gracefully

    def _apply_gematria_filters(self, table: QTableWidget, lang_combo: QComboBox, method_combo: QComboBox):
        """Filter table rows based on language and method selections."""
        selected_lang = lang_combo.currentData() or ""
        selected_method = method_combo.currentData() or ""
        
        for row in range(table.rowCount()):
            should_show = True
            
            # Check language (column 4, hidden)
            if selected_lang:
                lang_item = table.item(row, 4)
                if lang_item and lang_item.text() != selected_lang:
                    should_show = False
            
            # Check method (column 1)
            if should_show and selected_method:
                method_item = table.item(row, 1)
                if method_item and method_item.text() != selected_method:
                    should_show = False
            
            table.setRowHidden(row, not should_show)

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
        """Display the results in the UI."""
        # Update Outline/Overview Panels
        self._update_panel(self.panel_original, result.original)
        self._update_panel(self.panel_conrune, result.conrune)
        self._update_panel(self.panel_reversal, result.reversal)
        self._update_panel(self.panel_conrune_rev, result.conrune_reversal)
        
        self._update_panel(self.panel_upper_diff, result.upper_diff)
        self._update_panel(self.panel_lower_diff, result.lower_diff)

        # Update Detail Tabs
        self._update_detail_tab(self.tab_original, result.original)
        self._update_detail_tab(self.tab_conrune, result.conrune)
        self._update_detail_tab(self.tab_reversal, result.reversal)
        self._update_detail_tab(self.tab_conrune_rev, result.conrune_reversal)
        self._update_detail_tab(self.tab_upper_diff, result.upper_diff)
        self._update_detail_tab(self.tab_lower_diff, result.lower_diff)
        
        # Update Advanced Tab
        self._update_advanced_tab(result)
        
        # Update Gematria Tab
        if result.original and result.original.decimal:
             self._update_gematria_tab(result)

        # Update Sidebar
        self._update_sidebar_labels(result)

    def _clear_all(self):
        """Clear all outputs."""
        # Reset panels
        empty_member = QuadsetMember(name="Empty", decimal=0, ternary="", properties={})
        empty_result = QuadsetResult(
            original=empty_member, conrune=empty_member,
            reversal=empty_member, conrune_reversal=empty_member,
            upper_diff=empty_member, lower_diff=empty_member,
            transgram=empty_member,
            quadset_sum=0, septad_total=0,
            pattern_summary=""
        )
        
        self._display_results(empty_result)
        
        # Clear sidebar manually to remove numbers
        roles = [
            "Original", "Conrune", "Reune", "ConReune",
            "A - B", "C - D"
        ]
        for i, role in enumerate(roles):
            self.sidebar.item(i + 1).setText(role)
            
        # Clear Gematria
        if hasattr(self, "gem_tables"):
            for key in self.gem_tables:
                self.gem_tables[key].setRowCount(0)