"""Gematria pillar hub - launcher interface for gematria tools."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QGridLayout, QFrame
)
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
        # Set white background for better contrast
        self.setStyleSheet("background-color: #ffffff;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title section
        title_label = QLabel("📖 Gematria")
        title_label.setStyleSheet("""
            color: #000000;
            font-size: 32pt;
            font-weight: 700;
            letter-spacing: -1px;
            background-color: transparent;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Numerical analysis across Hebrew, Greek, and English systems"
        )
        desc_label.setStyleSheet("""
            color: #374151;
            font-size: 13pt;
            margin-top: 4px;
            margin-bottom: 16px;
            background-color: transparent;
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        layout.addSpacing(20)
        
        # Tools section
        tools_label = QLabel("Tools")
        tools_label.setStyleSheet("""
            color: #000000;
            font-size: 18pt;
            font-weight: 700;
            margin-bottom: 12px;
            background-color: transparent;
        """)
        layout.addWidget(tools_label)
        
        # Tool buttons grid
        tools_grid = QGridLayout()
        tools_grid.setSpacing(16)
        tools_grid.setContentsMargins(0, 0, 0, 0)
        
        # Gematria Calculator button
        calc_button = self._create_tool_button(
            "📖 Gematria Calculator",
            "Calculate Hebrew, Greek, and English gematria values",
            self._open_calculator
        )
        tools_grid.addWidget(calc_button, 0, 0)
        
        # Saved Calculations button
        saved_button = self._create_tool_button(
            "💾 Saved Calculations",
            "Browse and manage your saved calculations",
            self._open_saved_calculations
        )
        tools_grid.addWidget(saved_button, 0, 1)
        
        # Batch Calculator button
        batch_button = self._create_tool_button(
            "📝 Batch Calculator",
            "Import and process spreadsheets of words",
            self._open_batch_calculator
        )
        tools_grid.addWidget(batch_button, 1, 0)
        
        # Database Tools button
        db_tools_button = self._create_tool_button(
            "🛠️ Database Tools",
            "Clean, optimize, and manage your database",
            self._open_database_tools
        )
        tools_grid.addWidget(db_tools_button, 1, 1)
        
        # Text Analysis button
        text_analysis_button = self._create_tool_button(
            "📊 Text Analysis",
            "Analyze documents with gematria highlighting",
            self._open_text_analysis
        )
        tools_grid.addWidget(text_analysis_button, 2, 0)
        
        # Methods Reference button
        methods_button = self._create_tool_button(
            "📚 Gemetria Methods",
            "Reference for all gematria calculation systems",
            self._open_methods_reference
        )
        tools_grid.addWidget(methods_button, 2, 1)

        # Future tools (placeholders)
        future_tools = [
            ("🔢 Number Analysis", "Analyze numerical patterns and relationships"),
            ("📈 Comparison Tool", "Compare gematria across multiple systems"),
        ]
        
        row, col = 3, 0  # Start below existing buttons
        for title, description in future_tools:
            btn = self._create_tool_button(title, description, None, enabled=False)
            tools_grid.addWidget(btn, row, col)
            col += 1
            if col > 1:  # 2 columns
                col = 0
                row += 1
        
        layout.addLayout(tools_grid)
        
        # Spacer to push everything to top
        layout.addStretch()
        
        # Status bar at bottom
        status_label = QLabel("Ready • lots of calculator systems available")
        status_label.setStyleSheet("""
            color: #64748b;
            font-size: 10pt;
            font-style: italic;
            background-color: transparent;
        """)
        layout.addWidget(status_label)
    
    def _create_tool_button(
        self, 
        title: str, 
        description: str, 
        callback, 
        enabled: bool = True
    ) -> QWidget:
        """
        Create a tool launcher button.
        
        Args:
            title: Tool title
            description: Tool description
            callback: Function to call when clicked
            enabled: Whether button is enabled
            
        Returns:
            Widget containing the button
        """
        # Container frame
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)
        
        if enabled:
            frame.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 2px solid #cbd5e1;
                    border-radius: 8px;
                }
                QFrame:hover {
                    border-color: #2563eb;
                    background-color: #f8fafc;
                }
            """)
        else:
            frame.setStyleSheet("""
                QFrame {
                    background-color: #f1f5f9;
                    border: 2px solid #cbd5e1;
                    border-radius: 8px;
                }
            """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title_label = QLabel()
        title_label.setText(title)
        title_label.setStyleSheet("color: #000000; font-size: 13pt; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel()
        desc_label.setText(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #374151; font-size: 10pt;")
        desc_label.setMaximumHeight(40)
        layout.addWidget(desc_label)
        
        # Spacer
        layout.addStretch()
        
        # Launch button
        button = QPushButton("Open Tool" if enabled else "Coming Soon")
        button.setEnabled(enabled)
        button.setMinimumHeight(36)
        if enabled and callback:
            button.clicked.connect(callback)
        
        if enabled:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 11pt;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #1d4ed8;
                }
                QPushButton:pressed {
                    background-color: #1e40af;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #e5e7eb;
                    color: #9ca3af;
                    border: none;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 11pt;
                }
            """)
        
        layout.addWidget(button)
        
        frame.setMinimumHeight(130)
        frame.setMaximumHeight(150)
        
        return frame
    
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
            calculators=calculators
        )
    
    def _open_saved_calculations(self):
        """Open the Saved Calculations browser window."""
        # Open through window manager - single instance only
        self.window_manager.open_window(
            window_type="saved_calculations",
            window_class=SavedCalculationsWindow,
            allow_multiple=False,  # Only one browser window at a time
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
            calculators=calculators
        )
    
    def _open_database_tools(self):
        """Open the Database Tools window."""
        # Open through window manager
        self.window_manager.open_window(
            window_type="database_tools",
            window_class=DatabaseToolsWindow,
            allow_multiple=False,  # Only one database tools window at a time
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
        
        # Need to get database session for document access
        from shared.database import get_db
        db = next(get_db())
        
        # Open through window manager
        self.window_manager.open_window(
            window_type="text_analysis",
            window_class=TextAnalysisWindow,
            allow_multiple=False,  # Only one text analysis window at a time
            calculators=calculators,
            db_session=db
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
