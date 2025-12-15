"""Gematria pillar hub - launcher interface for gematria tools."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shared.ui import WindowManager
from .gematria_calculator_window import GematriaCalculatorWindow
from .saved_calculations_window import SavedCalculationsWindow
from .batch_calculator_window import BatchCalculatorWindow
from .database_tools_window import DatabaseToolsWindow
from .text_analysis_window import TextAnalysisWindow
from .methods_reference_window import MethodsReferenceWindow
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
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title section to match other pillars
        title_label = QLabel("Gematria Pillar")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        desc_label = QLabel(
            "Numerical analysis across Hebrew, Greek, and English systems"
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_font = QFont()
        desc_font.setPointSize(12)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(desc_label)

        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(15)

        buttons = [
            ("Gematria Calculator", "#2563eb", "#1d4ed8", self._open_calculator),
            ("Saved Calculations", "#059669", "#047857", self._open_saved_calculations),
            ("Batch Calculator", "#7c3aed", "#6d28d9", self._open_batch_calculator),
            ("Text Analysis", "#db2777", "#be185d", self._open_text_analysis),
            ("Database Tools", "#f97316", "#ea580c", self._open_database_tools),
            ("Methods Reference", "#2563eb", "#1d4ed8", self._open_methods_reference),
        ]

        for label, base_color, hover_color, callback in buttons:
            tools_layout.addWidget(
                self._create_primary_button(label, base_color, hover_color, callback)
            )

        layout.addLayout(tools_layout)

        future_label = QLabel(
            "\nComing Soon:\n"
            "• Number Analysis\n"
            "• Comparison Tool"
        )
        future_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        future_label.setStyleSheet("color: #9ca3af; margin-top: 30px;")
        layout.addWidget(future_label)

        layout.addStretch()
    def _create_primary_button(self, label: str, base_color: str, hover_color: str, callback):
        """Create a pillar-style primary button with shared styling."""
        button = QPushButton(label)
        button.setMinimumHeight(50)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {base_color};
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
        button.clicked.connect(callback)
        return button
    
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
            window_class=BatchCalculatorWindow,
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
            window_class=TextAnalysisWindow,
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
