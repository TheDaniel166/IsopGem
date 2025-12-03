"""TQ pillar hub - launcher interface for TQ tools."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shared.ui import WindowManager
from .ternary_converter_window import TernaryConverterWindow
from .quadset_analysis_window import QuadsetAnalysisWindow
from .transitions_window import TransitionsWindow
from .geometric_transitions_window import GeometricTransitionsWindow
from .conrune_pair_finder_window import ConrunePairFinderWindow


class TQHub(QWidget):
    """Hub widget for TQ pillar - displays available tools."""
    
    def __init__(self, window_manager: WindowManager):
        """
        Initialize the TQ hub.
        
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
        
        # Title
        title_label = QLabel("TQ Pillar")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Trigrammaton QBLH integration and pattern analysis"
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_font = QFont()
        desc_font.setPointSize(12)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(desc_label)
        
        # Tools Section
        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(15)
        
        # Ternary Converter Button
        converter_btn = QPushButton("Ternary Converter")
        converter_btn.setMinimumHeight(50)
        converter_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        converter_btn.clicked.connect(self._open_ternary_converter)
        tools_layout.addWidget(converter_btn)

        # Quadset Analysis Button
        quadset_btn = QPushButton("Quadset Analysis")
        quadset_btn.setMinimumHeight(50)
        quadset_btn.setStyleSheet("""
            QPushButton {
                background-color: #7c3aed;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #6d28d9;
            }
        """)
        quadset_btn.clicked.connect(self._open_quadset_analysis)
        tools_layout.addWidget(quadset_btn)

        # Transitions Button
        transitions_btn = QPushButton("Ternary Transitions")
        transitions_btn.setMinimumHeight(50)
        transitions_btn.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #047857;
            }
        """)
        transitions_btn.clicked.connect(self._open_transitions)
        tools_layout.addWidget(transitions_btn)

        # Geometric Transitions Button
        geometric_btn = QPushButton("Geometric Transitions")
        geometric_btn.setMinimumHeight(50)
        geometric_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
        """)
        geometric_btn.clicked.connect(self._open_geometric_transitions)
        tools_layout.addWidget(geometric_btn)

        conrune_btn = QPushButton("Conrune Pair Finder")
        conrune_btn.setMinimumHeight(50)
        conrune_btn.setStyleSheet("""
            QPushButton {
                background-color: #f97316;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #ea580c;
            }
        """)
        conrune_btn.clicked.connect(self._open_conrune_pair_finder)
        tools_layout.addWidget(conrune_btn)
        
        layout.addLayout(tools_layout)
        
        # Future Tools Placeholder
        future_label = QLabel(
            "\nComing Soon:\n"
            "• Trigrammaton Mapper\n"
            "• QBLH Pattern Analyzer\n"
            "• Symbol Correlation Tool"
        )
        future_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        future_label.setStyleSheet("color: #9ca3af; margin-top: 30px;")
        layout.addWidget(future_label)
        
        layout.addStretch()

    def _open_ternary_converter(self):
        """Open the ternary converter window."""
        self.window_manager.open_window(
            "ternary_converter",
            TernaryConverterWindow
        )

    def _open_quadset_analysis(self):
        """Open the quadset analysis window."""
        self.window_manager.open_window(
            "quadset_analysis",
            QuadsetAnalysisWindow
        )

    def _open_transitions(self):
        """Open the transitions window."""
        self.window_manager.open_window(
            "transitions",
            TransitionsWindow,
            window_manager=self.window_manager
        )

    def _open_geometric_transitions(self):
        """Open the geometric transitions window."""
        self.window_manager.open_window(
            "geometric_transitions",
            GeometricTransitionsWindow,
            window_manager=self.window_manager
        )

    def _open_conrune_pair_finder(self):
        """Open the Conrune Pair Finder window."""
        self.window_manager.open_window(
            "conrune_pair_finder",
            ConrunePairFinderWindow,
            window_manager=self.window_manager
        )
