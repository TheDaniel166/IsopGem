"""
Time Mechanics Hub - The Keeper of Time.
Entry point for temporal tools including Tzolkin calculator and Dynamis visualization.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class TimeMechanicsHub(QWidget):
    """
    The Diplomat (Hub) for the Time Mechanics Pillar.
    Serves as the entry point for all temporal tools.
    """
    def __init__(self, window_manager=None):
        super().__init__()
        self.window_manager = window_manager
        self.setWindowTitle("Time Mechanics")
        self.resize(800, 600)
        
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Header
        self.header = QLabel("Time Mechanics Pillar")
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        self.layout.addWidget(self.header)
        
        # Tools Placeholder
        self.info_label = QLabel("The Keeper of Time")
        self.info_label.setStyleSheet("font-size: 16px; color: #888;")
        self.layout.addWidget(self.info_label)
        
        # --- Launch Pad ---
        self.grid_layout = QVBoxLayout()
        self.layout.addLayout(self.grid_layout)
        
        self.tzolkin_btn = QPushButton("⏳ Thelemic Tzolkin Calculator")
        self.tzolkin_btn.setFixedHeight(50)
        self.tzolkin_btn.clicked.connect(self.launch_tzolkin)
        self.grid_layout.addWidget(self.tzolkin_btn)
        
        self.dynamis_btn = QPushButton("⚡ Tzolkin Dynamis (Circulation of Energies)")
        self.dynamis_btn.setFixedHeight(50)
        self.dynamis_btn.clicked.connect(self.launch_dynamis)
        self.grid_layout.addWidget(self.dynamis_btn)
        
        self.zodiacal_btn = QPushButton("🔮 Zodiacal Circle (Trigrammic Time)")
        self.zodiacal_btn.setFixedHeight(50)
        self.zodiacal_btn.clicked.connect(self.launch_zodiacal_circle)
        self.grid_layout.addWidget(self.zodiacal_btn)

    def launch(self):
        """
        The method invoked by the WindowManager to show this sovereign domain.
        """
        self.show()

    def launch_tzolkin(self):
        from .tzolkin_window import TzolkinCalculatorWindow
        # Use window manager if available, otherwise just show (fallback)
        if self.window_manager:
            self.window_manager.open_window(
                "tzolkin_calculator",
                TzolkinCalculatorWindow
            )
        else:
            self.calc = TzolkinCalculatorWindow()
            self.calc.show()

    def launch_dynamis(self):
        from .dynamis_window import TzolkinDynamisWindow
        # Use window manager if available
        if self.window_manager:
            self.window_manager.open_window(
                "tzolkin_dynamis",
                TzolkinDynamisWindow
            )
        else:
            self.dynamis = TzolkinDynamisWindow()
            self.dynamis.show()

    def launch_zodiacal_circle(self):
        from .zodiacal_circle_window import ZodiacalCircleWindow
        # Use window manager if available
        if self.window_manager:
            self.window_manager.open_window(
                "zodiacal_circle",
                ZodiacalCircleWindow,
                window_manager=self.window_manager
            )
        else:
            self.zodiacal = ZodiacalCircleWindow()
            self.zodiacal.show()
