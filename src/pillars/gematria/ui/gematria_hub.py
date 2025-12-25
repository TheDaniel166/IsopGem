"""Gematria pillar hub - launcher interface for gematria tools."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QGridLayout, QGraphicsDropShadowEffect, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from shared.ui import WindowManager
from .gematria_calculator_window import GematriaCalculatorWindow
from .saved_calculations_window import SavedCalculationsWindow
from .batch_calculator_window import GreatHarvestWindow
from .database_tools_window import DatabaseToolsWindow
from .text_analysis_window import ExegesisWindow
from .methods_reference_window import MethodsReferenceWindow
from .els_search_window import ELSSearchWindow
from .acrostics_window import AcrosticsWindow
from .chiastic_window import ChiasticWindow
from ..services import (
    HebrewGematriaCalculator,
    HebrewSofitCalculator,
    HebrewLetterValueCalculator,
    HebrewOrdinalCalculator,
    HebrewSmallValueCalculator,
    HebrewAtBashCalculator,
    HebrewKolelCalculator,
    HebrewSquareCalculator,
    HebrewCubeCalculator,
    HebrewTriangularCalculator,
    HebrewIntegralReducedCalculator,
    HebrewOrdinalSquareCalculator,
    HebrewFullValueCalculator,
    HebrewAlbamCalculator,
    GreekGematriaCalculator,
    GreekLetterValueCalculator,
    GreekOrdinalCalculator,
    GreekSmallValueCalculator,
    GreekKolelCalculator,
    GreekSquareCalculator,
    GreekCubeCalculator,
    GreekTriangularCalculator,
    GreekDigitalCalculator,
    GreekOrdinalSquareCalculator,
    GreekFullValueCalculator,
    GreekReverseSubstitutionCalculator,
    GreekPairMatchingCalculator,
    GreekNextLetterCalculator,
    TQGematriaCalculator,
    TQReducedCalculator,
    TQSquareCalculator,
    TQTriangularCalculator,
    TQPositionCalculator
)


class GematriaHub(QWidget):
    """Hub widget for Gematria pillar - displays available tools."""
    
    def __init__(self, window_manager: WindowManager):
        """
        Initialize the Gematria hub.
        
        Args:
            window_manager: Shared window manager instance
        """
        super().__init__()
        self.window_manager = window_manager
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the hub interface."""
        # Scroll area for the hub content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 32, 40, 40)

        # Header section
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Gematria")
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 32pt;
                font-weight: 700;
                letter-spacing: -1px;
            }
        """)
        header_layout.addWidget(title_label)

        desc_label = QLabel("Numerical analysis across Hebrew, Greek, and English systems")
        desc_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12pt;
            }
        """)
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header)

        # Tools grid
        tools = [
            ("🔢", "Logos Abacus", "Interactive gematria calculator", "#3b82f6", self._open_calculator),
            ("💾", "Records of Karnak", "Browse saved calculations", "#10b981", self._open_saved_calculations),
            ("🌾", "The Great Harvest", "Sow and reap calculations", "#8b5cf6", self._open_batch_calculator),
            ("🕯️", "The Exegesis", "Scriptural Inquiry & Analysis", "#ec4899", self._open_text_analysis),
            ("🔮", "The Resonant Chain", "Hidden letter sequences", "#7C3AED", self._open_els_search),
            ("🗝️", "Acrostic Discovery", "Find hidden messages in text", "#f43f5e", self._open_acrostics),
            ("⚖️", "Chiastic TQ Finder", "Find symmetrical Gematria patterns", "#E11D48", self._open_chiasmus),
            ("🗄️", "Database", "Manage calculation data", "#f97316", self._open_database_tools),
            ("📖", "Reference", "Method documentation", "#06b6d4", self._open_methods_reference),
        ]

        grid = QGridLayout()
        grid.setSpacing(16)
        
        for i, (icon, title, desc, color, callback) in enumerate(tools):
            card = self._create_tool_card(icon, title, desc, color, callback)
            grid.addWidget(card, i // 3, i % 3)
        
        layout.addLayout(grid)
        
        # Coming soon section
        coming_soon = QLabel("Coming Soon: Number Analysis • Comparison Tool")
        coming_soon.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 10pt;
                padding: 20px;
            }
        """)
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(coming_soon)
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _create_tool_card(self, icon: str, title: str, description: str, accent_color: str, callback) -> QFrame:
        """Create a modern tool card."""
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 0;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f5f9);
                border-color: {accent_color};
            }}
        """)
        card.setMinimumSize(200, 140)
        card.setMaximumHeight(160)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 25))
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        
        # Icon with accent background
        icon_container = QLabel(icon)
        icon_container.setFixedSize(48, 48)
        icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.setStyleSheet(f"""
            QLabel {{
                background: {accent_color}20;
                border-radius: 10px;
                font-size: 22pt;
            }}
        """)
        layout.addWidget(icon_container)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 13pt;
                font-weight: 600;
                background: transparent;
            }
        """)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 9pt;
                background: transparent;
            }
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # Click handler
        card.mousePressEvent = lambda e: callback()
        
        return card
    
    def _open_calculator(self):
        """Open the Gematria Calculator window."""
        # Prepare calculators
        calculators = [
            # Hebrew calculators
            HebrewGematriaCalculator(),
            HebrewSofitCalculator(),
            HebrewLetterValueCalculator(),
            HebrewOrdinalCalculator(),
            HebrewSmallValueCalculator(),
            HebrewAtBashCalculator(),
            HebrewAlbamCalculator(),
            HebrewKolelCalculator(),
            HebrewSquareCalculator(),
            HebrewCubeCalculator(),
            HebrewTriangularCalculator(),
            HebrewIntegralReducedCalculator(),
            HebrewOrdinalSquareCalculator(),
            HebrewFullValueCalculator(),
            # Greek calculators
            GreekGematriaCalculator(),
            GreekLetterValueCalculator(),
            GreekOrdinalCalculator(),
            GreekSmallValueCalculator(),
            GreekKolelCalculator(),
            GreekSquareCalculator(),
            GreekCubeCalculator(),
            GreekTriangularCalculator(),
            GreekDigitalCalculator(),
            GreekOrdinalSquareCalculator(),
            GreekFullValueCalculator(),
            GreekReverseSubstitutionCalculator(),
            GreekPairMatchingCalculator(),
            GreekNextLetterCalculator(),
            # English/TQ calculators
            TQGematriaCalculator(),
            TQReducedCalculator(),
            TQSquareCalculator(),
            TQTriangularCalculator(),
            TQPositionCalculator(),
        ]
        
        # Open through window manager - allow_multiple=True means each click creates a new window
        # Note: Don't pass 'parent' in kwargs - WindowManager will handle it
        self.window_manager.open_window(
            window_type="gematria_calculator",
            window_class=GematriaCalculatorWindow,
            allow_multiple=True,  # Allow multiple calculator windows
            calculators=calculators,
            window_manager=self.window_manager
        )
    
    def _open_saved_calculations(self):
        """Open the Saved Calculations browser window."""
        # Open through window manager - single instance only
        self.window_manager.open_window(
            window_type="saved_calculations",
            window_class=SavedCalculationsWindow,
            allow_multiple=False,  # Only one browser window at a time
            window_manager=self.window_manager
        )
    
    def _open_batch_calculator(self):
        """Open the Batch Calculator window."""
        # Prepare calculators (same as regular calculator)
        calculators = [
            # Hebrew calculators
            HebrewGematriaCalculator(),
            HebrewSofitCalculator(),
            HebrewLetterValueCalculator(),
            HebrewOrdinalCalculator(),
            HebrewSmallValueCalculator(),
            HebrewAtBashCalculator(),
            HebrewAlbamCalculator(),
            HebrewKolelCalculator(),
            HebrewSquareCalculator(),
            HebrewCubeCalculator(),
            HebrewTriangularCalculator(),
            HebrewIntegralReducedCalculator(),
            HebrewOrdinalSquareCalculator(),
            HebrewFullValueCalculator(),
            # Greek calculators
            GreekGematriaCalculator(),
            GreekLetterValueCalculator(),
            GreekOrdinalCalculator(),
            GreekSmallValueCalculator(),
            GreekKolelCalculator(),
            GreekSquareCalculator(),
            GreekCubeCalculator(),
            GreekTriangularCalculator(),
            GreekDigitalCalculator(),
            GreekOrdinalSquareCalculator(),
            GreekFullValueCalculator(),
            GreekReverseSubstitutionCalculator(),
            GreekPairMatchingCalculator(),
            GreekNextLetterCalculator(),
            # English/TQ calculators
            TQGematriaCalculator(),
            TQReducedCalculator(),
            TQSquareCalculator(),
            TQTriangularCalculator(),
            TQPositionCalculator(),
        ]
        
        # Open through window manager
        self.window_manager.open_window(
            window_type="batch_calculator",
            window_class=GreatHarvestWindow,
            allow_multiple=False,  # Only one batch calculator at a time
            calculators=calculators,
            window_manager=self.window_manager
        )
    
    def _open_database_tools(self):
        """Open the Database Tools window."""
        # Open through window manager
        self.window_manager.open_window(
            window_type="database_tools",
            window_class=DatabaseToolsWindow,
            allow_multiple=False,  # Only one database tools window at a time
            window_manager=self.window_manager
        )
    
    def _open_text_analysis(self):
        """Open the Text Analysis window."""
        # Prepare calculators (same as regular calculator)
        calculators = [
            # Hebrew calculators
            HebrewGematriaCalculator(),
            HebrewSofitCalculator(),
            HebrewLetterValueCalculator(),
            HebrewOrdinalCalculator(),
            HebrewSmallValueCalculator(),
            HebrewAtBashCalculator(),
            HebrewAlbamCalculator(),
            HebrewKolelCalculator(),
            HebrewSquareCalculator(),
            HebrewCubeCalculator(),
            HebrewTriangularCalculator(),
            HebrewIntegralReducedCalculator(),
            HebrewOrdinalSquareCalculator(),
            HebrewFullValueCalculator(),
            # Greek calculators
            GreekGematriaCalculator(),
            GreekLetterValueCalculator(),
            GreekOrdinalCalculator(),
            GreekSmallValueCalculator(),
            GreekKolelCalculator(),
            GreekSquareCalculator(),
            GreekCubeCalculator(),
            GreekTriangularCalculator(),
            GreekDigitalCalculator(),
            GreekOrdinalSquareCalculator(),
            GreekFullValueCalculator(),
            GreekReverseSubstitutionCalculator(),
            GreekPairMatchingCalculator(),
            GreekNextLetterCalculator(),
            # English/TQ calculators
            TQGematriaCalculator(),
            TQReducedCalculator(),
            TQSquareCalculator(),
            TQTriangularCalculator(),
            TQPositionCalculator(),
        ]
        
        # Open through window manager
        self.window_manager.open_window(
            window_type="text_analysis",
            window_class=ExegesisWindow,
            allow_multiple=False,  # Only one text analysis window at a time
            calculators=calculators,
            window_manager=self.window_manager
        )

    def _open_methods_reference(self):
        """Open the Gemetria Methods reference window."""
        calculators = [
            # Hebrew calculators
            HebrewGematriaCalculator(),
            HebrewSofitCalculator(),
            HebrewLetterValueCalculator(),
            HebrewOrdinalCalculator(),
            HebrewSmallValueCalculator(),
            HebrewAtBashCalculator(),
            HebrewAlbamCalculator(),
            HebrewKolelCalculator(),
            HebrewSquareCalculator(),
            HebrewCubeCalculator(),
            HebrewTriangularCalculator(),
            HebrewIntegralReducedCalculator(),
            HebrewOrdinalSquareCalculator(),
            HebrewFullValueCalculator(),
            # Greek calculators
            GreekGematriaCalculator(),
            GreekLetterValueCalculator(),
            GreekOrdinalCalculator(),
            GreekSmallValueCalculator(),
            GreekKolelCalculator(),
            GreekSquareCalculator(),
            GreekCubeCalculator(),
            GreekTriangularCalculator(),
            GreekDigitalCalculator(),
            GreekOrdinalSquareCalculator(),
            GreekFullValueCalculator(),
            GreekReverseSubstitutionCalculator(),
            GreekPairMatchingCalculator(),
            GreekNextLetterCalculator(),
            # English/TQ calculators
            TQGematriaCalculator(),
            TQReducedCalculator(),
            TQSquareCalculator(),
            TQTriangularCalculator(),
            TQPositionCalculator(),
        ]
        self.window_manager.open_window(
            window_type="methods_reference",
            window_class=MethodsReferenceWindow,
            allow_multiple=False,
            calculators=calculators
        )

    def _open_els_search(self):
        """Open the TQ Text Sequencer window."""
        self.window_manager.open_window(
            window_type="els_search",
            window_class=ELSSearchWindow,
            allow_multiple=False,
            window_manager=self.window_manager
        )


    def _open_acrostics(self):
        """Open the Acrostic Discovery window."""
        self.window_manager.open_window(
            window_type="acrostics",
            window_class=AcrosticsWindow,
            allow_multiple=False,
            window_manager=self.window_manager
        )

    def _open_chiasmus(self):
        """Open the Chiastic TQ Finder window."""
        self.window_manager.open_window(
            window_type="chiasmus",
            window_class=ChiasticWindow,
            allow_multiple=False,
            window_manager=self.window_manager
        )
