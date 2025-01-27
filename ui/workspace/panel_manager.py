from PyQt5.QtWidgets import (QDockWidget, QWidget, QMenu, QPushButton, 
                            QLabel, QHBoxLayout, QSizePolicy)
from PyQt5.QtCore import Qt, QSettings, QSize
from PyQt5.QtGui import QIcon, QCursor

# Panel imports
from .gematria.text_analysis_panel import TextAnalysisPanel
from .gematria.calculator_panel import CalculatorPanel
from .gematria.history_panel import HistoryPanel
from .gematria.reverse_panel import ReversePanel
from .gematria.suggestions_panel import SuggestionsPanel
from .gematria.search_panel import SearchPanel
from .gematria.saved_panel import SavedPanel
from ui.workspace.gematria.grid.grid_config_dialog import GridConfigDialog




class PanelManager:
    def __init__(self, main_window):
        # Existing initialization
        self.main_window = main_window
        self.settings = QSettings('Sourcegraph', 'IsopGem')
        self.panels = {}
        self.panel_positions = {}
        self.panel_counters = {}
        self.default_size = QSize(400, 300)
        self.min_size = QSize(200, 100)
        self.max_size = QSize(1920, 1080)
        
        # New customization features
        self.panel_styles = {}
        self.opacity_levels = {}
        self.custom_borders = {}

    def create_panel(self, panel_type):
        # Create new panel instance
        panel = self._create_new_panel(panel_type.title(), panel_type)
        if panel:
            # Generate unique ID
            panel_id = f"{panel_type}_{len(self.panels)}"
            self.panels[panel_id] = panel
            self._position_panel(panel, panel_id)
            panel.show()
            panel.raise_()
            return panel

    def _create_panel_content(self, panel_type):
        panel_classes = {
            'calculator': CalculatorPanel,
            'history': HistoryPanel,
            'reverse': ReversePanel,
            'suggestions': SuggestionsPanel,
            'search': SearchPanel,
            'saved': SavedPanel,
            'text_analysis': TextAnalysisPanel,
            'grid_analysis': GridConfigDialog
        }
        
        if panel_type.lower() in panel_classes:
            return panel_classes[panel_type.lower()]()
        return None



    def _create_new_panel(self, name, panel_type):
        dock = QDockWidget(name, self.main_window)
        
        # Set floating state first for proper styling
        dock.setFloating(True)
        
        # Set features and constraints
        dock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        dock.setAllowedAreas(Qt.NoDockWidgetArea)
        
        # Apply initial border style
        self._set_panel_border(dock, "#333333")
        
        # Add customization features
        self._setup_panel_customization(dock, panel_type)
        
        # Set content
        content = self._create_panel_content(panel_type)
        if content:
            dock.setWidget(content)
            dock.resize(self.default_size)
            return dock
        return None


    def _setup_panel_customization(self, dock, panel_type):
        # Create custom title bar
        title_bar = QWidget()
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Settings button
        settings_btn = QPushButton()
        settings_btn.setIcon(QIcon("assets/settings.png"))
        settings_btn.clicked.connect(lambda: self._show_panel_settings(dock, panel_type))
        
        # Window control buttons
        minimize_btn = QPushButton("-")
        maximize_btn = QPushButton("□")
        close_btn = QPushButton("×")
        
        # Store original geometry for minimize/maximize
        dock.original_geometry = None
        
        # Connect window controls
        minimize_btn.clicked.connect(lambda: self._minimize_panel(dock))
        maximize_btn.clicked.connect(lambda: self._maximize_panel(dock))
        close_btn.clicked.connect(dock.close)
        
        # Add all elements to layout
        layout.addWidget(settings_btn)
        layout.addStretch()
        layout.addWidget(QLabel(panel_type.title()))
        layout.addStretch()
        layout.addWidget(minimize_btn)
        layout.addWidget(maximize_btn)
        layout.addWidget(close_btn)
        
        # Set initial border style
        self._set_panel_border(dock, "#333333")
        
        dock.setTitleBarWidget(title_bar)

    def _minimize_panel(self, dock):
        if not dock.original_geometry:
            dock.original_geometry = dock.geometry()
            dock.resize(dock.width(), dock.titleBarWidget().height())
        else:
            dock.setGeometry(dock.original_geometry)
            dock.original_geometry = None

    def _maximize_panel(self, dock):
        if not dock.original_geometry:
            dock.original_geometry = dock.geometry()
            dock.setGeometry(self.main_window.geometry())
        else:
            dock.setGeometry(dock.original_geometry)
            dock.original_geometry = None

    def _set_panel_border(self, dock, color):
        style = f"""
            QDockWidget {{
                border: 2px solid {color};
                background-color: #2b2b2b;
            }}
            QWidget {{
                background-color: #2b2b2b;
            }}
            QPushButton {{
                background-color: #3d3d3d;
                border: none;
                padding: 4px;
                min-width: 20px;
            }}
            QPushButton:hover {{
                background-color: #4d4d4d;
            }}
            QLabel {{
                color: white;
            }}
        """
        dock.setStyleSheet(style)

    def _show_panel_settings(self, dock, panel_type):
        menu = QMenu()
        
        # Opacity submenu
        opacity_menu = menu.addMenu("Opacity")
        for opacity in [25, 50, 75, 100]:
            action = opacity_menu.addAction(f"{opacity}%")
            action.triggered.connect(
                lambda checked, o=opacity: self._set_panel_opacity(dock, o/100))
        
        # Border customization
        border_menu = menu.addMenu("Border")
        colors = {"Default": "#333", "Blue": "#00f", "Red": "#f00"}
        for name, color in colors.items():
            action = border_menu.addAction(name)
            action.triggered.connect(
                lambda checked, c=color: self._set_panel_border(dock, c))
        
        menu.exec_(QCursor.pos())

    def _set_panel_opacity(self, dock, value):
        dock.setWindowOpacity(value)
        self.opacity_levels[dock] = value

    def _set_panel_border(self, dock, color):
        dock.setStyleSheet(f"QDockWidget {{ border: 2px solid {color}; }}")
        self.custom_borders[dock] = color

    def _position_panel(self, panel, panel_type):
        # Calculate offset based on existing panels
        x_offset = 20 * len(self.panels)
        y_offset = 20 * len(self.panels)
        base_x = 200
        base_y = 200
        
        # Position the panel
        panel.move(base_x + x_offset, base_y + y_offset)
        self.panel_positions[panel_type] = (base_x + x_offset, base_y + y_offset)


