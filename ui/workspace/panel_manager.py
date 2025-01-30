from PyQt5.QtWidgets import (QDockWidget, QWidget, QMenu, QPushButton, 
                            QLabel, QHBoxLayout, QSizePolicy, QTabWidget,
                            QColorDialog, QFontDialog, QSpinBox, QWidgetAction)
from PyQt5.QtCore import Qt, QSettings, QSize
from PyQt5.QtGui import QIcon, QCursor, QColor, QPalette

# Panel imports
from .gematria.text_analysis_panel import TextAnalysisPanel
from .gematria.calculator_panel import CalculatorPanel
from .gematria.history_panel import HistoryPanel
from .gematria.reverse_panel import ReversePanel
from .gematria.suggestions_panel import SuggestionsPanel
# from .gematria.search_panel import SearchPanel  # Comment out or remove this line
from .gematria.saved_panel import SavedPanel
from .gematria.search_results_panel import SearchResultsPanel
from .gematria.analysis_results_panel import AnalysisResultsPanel
from ui.workspace.gematria.grid.grid_config_dialog import GridConfigDialog
from ui.workspace.document_manager.categories.category_panel import CategoryPanel
from .gematria.create_cipher_panel import CreateCipherPanel
from .tq_operations.quadset_analysis_panel import QuadsetAnalysisPanel
from .tq_operations.converse_analysis_panel import ConverseAnalysisPanel
from .tq_operations.pair_transitions_panel import PairTransitionsPanel
from .tq_operations.series_transitions_panel import SeriesTransitionsPanel
from .tq_operations.geometric_transitions_panel import GeometricTransitionsPanel
from .tq_operations.dance_of_days_panel import DanceOfDaysPanel
from .tq_operations.thelemic_haad_panel import ThelemicHaadPanel
from .tq_operations.zodiacal_heptagons_panel import ZodiacalHeptagonsPanel
from .tq_operations.kamea_maut_panel import KameaMautPanel
from .tq_operations.kamea_bafomet_panel import KameaBafometPanel
from .tq_operations.kamea_creator_panel import KameaCreatorPanel
from .document_manager.calendar_panel import CalendarPanel



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
        
        # Enhanced customization features
        self.panel_themes = {
            'dark': {
                'background': '#2b2b2b',
                'border': '#333333',
                'text': '#ffffff',
                'button': '#3d3d3d',
                'button_hover': '#4d4d4d'
            },
            'light': {
                'background': '#f0f0f0',
                'border': '#cccccc',
                'text': '#000000',
                'button': '#e0e0e0',
                'button_hover': '#d0d0d0'
            },
            'blue': {
                'background': '#1e2433',
                'border': '#3498db',
                'text': '#ffffff',
                'button': '#2c3e50',
                'button_hover': '#34495e'
            }
        }
        
        # Load saved customizations
        self.current_theme = self.settings.value('panel_theme', 'dark')

    def create_panel(self, panel_type):
        print(f"DEBUG: Creating panel of type {panel_type}")  # Debug print
        panel = self._create_new_panel(panel_type.title(), panel_type)
        if panel:
            print("DEBUG: Panel created successfully")  # Debug print
            panel_id = f"{panel_type}_{len(self.panels)}"
            self.panels[panel_id] = panel
            
            # Set panel properties
            panel.setFeatures(QDockWidget.DockWidgetClosable | 
                             QDockWidget.DockWidgetMovable | 
                             QDockWidget.DockWidgetFloatable)
            panel.setAllowedAreas(Qt.AllDockWidgetAreas)
            
            # Setup customization
            self._setup_panel_customization(panel, panel_type)
            
            # Add to main window with proper tab position
            self.main_window.setTabPosition(Qt.RightDockWidgetArea, QTabWidget.North)
            self.main_window.addDockWidget(Qt.RightDockWidgetArea, panel)
            panel.setFloating(True)
            
            self._position_panel(panel, panel_type)
            panel.show()
            panel.raise_()
            return panel
        else:
            print("DEBUG: Failed to create panel")  # Debug print
            return None

    def _create_panel_content(self, panel_type):
        panel_classes = {
            'calculator': CalculatorPanel,
            'history': HistoryPanel,
            'reverse': ReversePanel,
            'suggestions': SuggestionsPanel,
            'saved': SavedPanel,
            'search_results': SearchResultsPanel,
            'analysis_results': AnalysisResultsPanel,
            'text_analysis': TextAnalysisPanel,
            'grid_analysis': GridConfigDialog,
            'create_cipher': CreateCipherPanel,
            'import': self._handle_import,
            'categories': CategoryPanel,
            'quadset_analysis': lambda: QuadsetAnalysisPanel(self.main_window),
            'converse_analysis': ConverseAnalysisPanel,
            'pair_transitions': PairTransitionsPanel,
            'series_transitions': SeriesTransitionsPanel,
            'geometric_transitions': GeometricTransitionsPanel,
            'dance_of_days': DanceOfDaysPanel,
            'thelemic_haad': ThelemicHaadPanel,
            'zodiacal_heptagons': ZodiacalHeptagonsPanel,
            'kamea_of_maut': KameaMautPanel,
            'kamea_of_bafomet': KameaBafometPanel,
            'kamea_creator': KameaCreatorPanel,
            'calendar': CalendarPanel
        }
        
        if panel_type.lower() in panel_classes:
            if panel_type.lower() == 'search_results':
                return SearchResultsPanel(self.main_window.search_results)
            elif panel_type.lower() == 'analysis_results':
                return AnalysisResultsPanel(self.main_window.analysis_results)
            elif panel_type.lower() == 'import':
                return panel_classes[panel_type.lower()]()
            return panel_classes[panel_type.lower()]()
        return None


    def _create_new_panel(self, name, panel_type):
        dock = QDockWidget(name, self.main_window)
        dock.setFloating(True)
        
        # Initialize geometry tracking
        dock.original_geometry = None
        
        # Create content
        content = self._create_panel_content(panel_type)
        if content:
            dock.setWidget(content)
            dock.resize(self.default_size)
            
            if panel_type == "pair_transitions":
                # Connect to existing quadset panel if it exists
                quadset_panel = None
                quadset_dock = None
                
                # First check existing panels
                for existing_panel in self.panels.values():
                    if isinstance(existing_panel.widget(), QuadsetAnalysisPanel):
                        quadset_panel = existing_panel.widget()
                        quadset_dock = existing_panel
                        break
                
                # If no quadset panel exists, create one directly
                if not quadset_panel:
                    print("Creating new QuadsetAnalysisPanel")
                    quadset_dock = QDockWidget("Quadset Analysis", self.main_window)
                    quadset_dock.setFloating(True)
                    quadset_panel = QuadsetAnalysisPanel(self.main_window)
                    quadset_dock.setWidget(quadset_panel)
                    quadset_dock.resize(self.default_size)
                    
                    # Add to panels dictionary
                    panel_id = f"quadset_analysis_{len(self.panels)}"
                    self.panels[panel_id] = quadset_dock
                    
                    # Setup and show the quadset panel
                    self._setup_panel_customization(quadset_dock, "quadset_analysis")
                    self.main_window.addDockWidget(Qt.RightDockWidgetArea, quadset_dock)
                    quadset_dock.setFloating(True)
                    self._position_panel(quadset_dock, "quadset_analysis")
                    quadset_dock.show()
                    quadset_dock.raise_()
                
                # Connect the signal - first disconnect any existing connections
                if quadset_panel:
                    try:
                        content.send_to_quadset.disconnect()  # Disconnect any existing connections
                    except TypeError:
                        pass  # No existing connections
                        
                    def update_quadset(value):
                        quadset_panel.number_input.setText(str(value))
                        quadset_panel.perform_analysis()
                        quadset_dock.show()
                        quadset_dock.raise_()
                    
                    content.send_to_quadset.connect(update_quadset)
            
            return dock
        return None


    def _setup_panel_customization(self, dock, panel_type):
        title_bar = QWidget()
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Theme selector button
        theme_btn = QPushButton()
        theme_btn.setIcon(QIcon("assets/icons/settings.png"))
        theme_btn.setToolTip("Change Theme")
        theme_btn.clicked.connect(lambda: self._show_theme_menu(dock))
        
        # Customize button
        customize_btn = QPushButton()
        customize_btn.setIcon(QIcon("assets/icons/settings.png"))  # Using settings icon for now
        customize_btn.setToolTip("Customize Panel")
        customize_btn.clicked.connect(lambda: self._show_customization_menu(dock))
        
        # Window controls with icons (using text for now until we have icons)
        minimize_btn = QPushButton("-")
        maximize_btn = QPushButton("□")
        close_btn = QPushButton("×")
        
        # Connect controls
        minimize_btn.clicked.connect(lambda: self._minimize_panel(dock))
        maximize_btn.clicked.connect(lambda: self._maximize_panel(dock))
        close_btn.clicked.connect(dock.close)
        
        # Add elements to layout
        layout.addWidget(theme_btn)
        layout.addWidget(customize_btn)
        layout.addStretch()
        layout.addWidget(QLabel(panel_type.title()))
        layout.addStretch()
        layout.addWidget(minimize_btn)
        layout.addWidget(maximize_btn)
        layout.addWidget(close_btn)
        
        dock.setTitleBarWidget(title_bar)
        self._apply_theme(dock, self.current_theme)

    def _show_theme_menu(self, dock):
        menu = QMenu()
        
        for theme_name in self.panel_themes.keys():
            action = menu.addAction(theme_name.title())
            action.triggered.connect(
                lambda checked, t=theme_name: self._apply_theme(dock, t))
        
        menu.addSeparator()
        menu.addAction("Custom Theme", lambda: self._create_custom_theme(dock))
        
        menu.exec_(QCursor.pos())

    def _show_customization_menu(self, dock):
        menu = QMenu()
        
        # Opacity control
        opacity_menu = menu.addMenu("Opacity")
        opacity_widget = QWidget()
        opacity_layout = QHBoxLayout(opacity_widget)
        
        opacity_spin = QSpinBox()
        opacity_spin.setRange(20, 100)
        opacity_spin.setValue(int(dock.windowOpacity() * 100))
        opacity_spin.valueChanged.connect(
            lambda v: dock.setWindowOpacity(v / 100))
        
        opacity_layout.addWidget(QLabel("Opacity:"))
        opacity_layout.addWidget(opacity_spin)
        opacity_layout.setContentsMargins(8, 4, 8, 4)
        
        # Create a QWidgetAction to hold the opacity controls
        opacity_action = QWidgetAction(opacity_menu)
        opacity_action.setDefaultWidget(opacity_widget)
        opacity_menu.addAction(opacity_action)
        
        # Border customization
        menu.addAction("Change Border Color", 
                      lambda: self._choose_border_color(dock))
        
        # Font customization
        menu.addAction("Change Font", 
                      lambda: self._choose_font(dock))
        
        # Background customization
        menu.addAction("Change Background", 
                      lambda: self._choose_background(dock))
        
        # Reset option
        menu.addSeparator()
        menu.addAction("Reset to Default", 
                      lambda: self._apply_theme(dock, self.current_theme))
        
        menu.exec_(QCursor.pos())

    def _apply_theme(self, dock, theme_name):
        theme = self.panel_themes[theme_name]
        
        style = f"""
            QDockWidget {{
                border: 2px solid {theme['border']};
                background-color: {theme['background']};
            }}
            QWidget {{
                background-color: {theme['background']};
                color: {theme['text']};
            }}
            QPushButton {{
                background-color: {theme['button']};
                border: none;
                padding: 4px;
                min-width: 20px;
                border-radius: 2px;
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
            QLabel {{
                color: {theme['text']};
            }}
        """
        
        dock.setStyleSheet(style)
        self.current_theme = theme_name
        self.settings.setValue('panel_theme', theme_name)

    def _choose_border_color(self, dock):
        color = QColorDialog.getColor()
        if color.isValid():
            self._set_panel_border(dock, color.name())

    def _choose_font(self, dock):
        font, ok = QFontDialog.getFont()
        if ok:
            dock.widget().setFont(font)

    def _choose_background(self, dock):
        color = QColorDialog.getColor()
        if color.isValid():
            style = dock.styleSheet()
            style += f"\nQWidget {{ background-color: {color.name()}; }}"
            dock.setStyleSheet(style)

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

    def _position_panel(self, panel, panel_type):
        # Calculate offset based on existing panels
        x_offset = 20 * len(self.panels)
        y_offset = 20 * len(self.panels)
        base_x = 200
        base_y = 200
        
        # Position the panel
        panel.move(base_x + x_offset, base_y + y_offset)
        self.panel_positions[panel_type] = (base_x + x_offset, base_y + y_offset)

    def _handle_import(self):
        # Get document actions from main window
        doc_actions = self.main_window.document_actions
        # Show import dialog
        doc_actions.show_import_dialog()

