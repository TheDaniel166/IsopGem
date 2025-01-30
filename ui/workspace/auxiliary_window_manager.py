from PyQt5.QtWidgets import (QDockWidget, QWidget, QMenu, QPushButton, 
                            QLabel, QHBoxLayout, QColorDialog, QFontDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette

class AuxiliaryWindowManager:
    """Manages auxiliary windows like visualizations that spawn from main panels"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.windows = {}  # Store active windows
        self.default_size = (400, 400)
        
        # Themes for auxiliary windows
        self.window_themes = {
            'dark': {
                'background': '#2b2b2b',
                'border': '#3498db',
                'text': '#ffffff',
                'title': '#4a90e2'
            },
            'light': {
                'background': '#f5f5f5',
                'border': '#2980b9',
                'text': '#2c3e50',
                'title': '#3498db'
            },
            'contrast': {
                'background': '#000000',
                'border': '#00ff00',
                'text': '#00ff00',
                'title': '#00ff00'
            }
        }
        self.current_theme = 'dark'
    
    def create_window(self, name, window_type, **params):
        """Create a new auxiliary window with customization features"""
        dock = QDockWidget(name, self.main_window)
        
        # Set dock widget features
        dock.setFeatures(
            QDockWidget.DockWidgetFloatable |
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetClosable
        )
        
        # Set floating by default
        dock.setFloating(True)
        
        # Create title bar
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(5, 2, 5, 2)
        
        # Left side - Customization
        customize_widget = QWidget()
        customize_layout = QHBoxLayout(customize_widget)
        customize_layout.setContentsMargins(0, 0, 0, 0)
        customize_layout.setSpacing(2)
        
        theme_btn = QPushButton("🎨")  # Theme
        font_btn = QPushButton("A")    # Font
        color_btn = QPushButton("◢")   # Color
        
        for btn in [theme_btn, font_btn, color_btn]:
            btn.setMaximumWidth(24)
            btn.setStyleSheet("""
                QPushButton { 
                    border: none;
                    padding: 2px;
                    border-radius: 2px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
            """)
            customize_layout.addWidget(btn)
        
        # Center - Title
        title_label = QLabel(name)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Right side - Window controls
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(2)
        
        minimize_btn = QPushButton("─")
        maximize_btn = QPushButton("□")
        close_btn = QPushButton("✕")
        
        # Store reference to manager in the buttons
        minimize_btn.manager = self
        maximize_btn.manager = self
        
        # Connect buttons to manager methods
        minimize_btn.clicked.connect(lambda: self._minimize_window(dock))
        maximize_btn.clicked.connect(lambda: self._toggle_maximize_window(dock))
        close_btn.clicked.connect(dock.close)
        
        for btn in [minimize_btn, maximize_btn, close_btn]:
            btn.setMaximumWidth(24)
            btn.setStyleSheet("""
                QPushButton { 
                    border: none;
                    padding: 2px;
                    border-radius: 2px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QPushButton#close_btn:hover {
                    background-color: #e81123;
                    color: white;
                }
            """)
            controls_layout.addWidget(btn)
        
        close_btn.setObjectName("close_btn")  # For specific hover style
        
        # Add all sections to title layout
        title_layout.addWidget(customize_widget)
        title_layout.addStretch()
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(controls_widget)
        
        dock.setTitleBarWidget(title_bar)
        
        # Create content
        content = self._create_window_content(window_type, **params)
        if content:
            dock.setWidget(content)
            dock.resize(*self.default_size)
            
            # Set up customization handlers
            theme_btn.clicked.connect(lambda: self._show_theme_menu(dock))
            font_btn.clicked.connect(lambda: self._choose_font(dock))
            color_btn.clicked.connect(lambda: self._choose_color(dock))
            
            # Store original geometry for minimize/maximize
            dock.original_geometry = None
            
            # Generate unique ID and store window
            window_id = f"{window_type}_{len(self.windows)}"
            self.windows[window_id] = dock
            
            # Apply current theme
            self._apply_theme(dock, self.current_theme)
            
            # Set up window behavior
            self._setup_window_customization(dock, window_type)
            
            # Add dock widget to main window but keep floating
            self.main_window.addDockWidget(Qt.RightDockWidgetArea, dock)
            dock.setFloating(True)
            
            # Position new window
            self._position_window(dock)
            
            # Connect dock state changes
            dock.topLevelChanged.connect(lambda floating: self._handle_floating_change(dock, floating))
            
            return dock
        return None
    
    def _create_window_content(self, window_type, **params):
        """Create content for auxiliary windows."""
        if window_type == "geometry_visualizer":
            from .tq_operations.geometry.visualizer import GeometryVisualizer
            visualizer = GeometryVisualizer()
            
            # Handle different visualization types
            if params.get('visualization_type') == 'polygonal':
                visualizer.create_polygonal_number(params['sides'], params['n'])
            elif 'sides' in params and 'layers' in params:
                visualizer.create_centered_polygon(params['sides'], params['layers'])
            elif 'sides' in params:
                visualizer.create_centered_polygon(params['sides'], 1)
                
            return visualizer
        # Add other window types here
        return None
    
    def _setup_window_customization(self, dock, window_type):
        """Set up window-specific behaviors"""
        # Allow closing
        dock.setFeatures(QDockWidget.DockWidgetClosable | 
                        QDockWidget.DockWidgetFloatable)
        
        # Handle window closure
        dock.closeEvent = lambda e: self._handle_window_close(dock, e)
    
    def _position_window(self, dock):
        """Position new window relative to existing ones"""
        offset = 30 * len(self.windows)
        dock.move(100 + offset, 100 + offset)
    
    def _handle_window_close(self, dock, event):
        """Clean up when window is closed"""
        # Remove from tracked windows
        window_id = next((k for k, v in self.windows.items() if v == dock), None)
        if window_id:
            del self.windows[window_id]
        event.accept()
    
    def close_all_windows(self):
        """Close all auxiliary windows"""
        for dock in list(self.windows.values()):
            dock.close()
    
    def _show_theme_menu(self, dock):
        """Show theme selection menu"""
        menu = QMenu()
        for theme_name in self.window_themes.keys():
            action = menu.addAction(theme_name.title())
            action.triggered.connect(lambda checked, t=theme_name: self._apply_theme(dock, t))
        menu.exec_(dock.mapToGlobal(dock.rect().topRight()))
    
    def _apply_theme(self, dock, theme_name):
        """Apply theme to window"""
        theme = self.window_themes[theme_name]
        style = f"""
            QDockWidget {{
                background-color: {theme['background']};
                border: 2px solid {theme['border']};
            }}
            QLabel {{
                color: {theme['text']};
            }}
            QWidget {{
                background-color: {theme['background']};
                color: {theme['text']};
            }}
            QPushButton {{
                background-color: {theme['background']};
                color: {theme['text']};
            }}
        """
        dock.setStyleSheet(style)
        self.current_theme = theme_name
    
    def _choose_font(self, dock):
        """Open font selection dialog"""
        font, ok = QFontDialog.getFont()
        if ok:
            dock.widget().setFont(font)
    
    def _choose_color(self, dock):
        """Open color selection dialog"""
        color = QColorDialog.getColor()
        if color.isValid():
            style = dock.styleSheet()
            style += f"\nQWidget {{ background-color: {color.name()}; }}"
            dock.setStyleSheet(style)
    
    def _minimize_window(self, dock):
        """Minimize the window to just its title bar"""
        if not hasattr(dock, 'minimized'):
            dock.minimized = False
            
        if not dock.minimized:
            print(f"Minimizing window from height {dock.height()}")
            dock.original_height = dock.height()
            title_height = dock.titleBarWidget().height()
            print(f"Title bar height: {title_height}")
            dock.resize(dock.width(), title_height + 2)  # Added small margin
            dock.minimized = True
            print(f"New height after minimize: {dock.height()}")
        else:
            print(f"Restoring window to height {dock.original_height}")
            dock.resize(dock.width(), dock.original_height)
            dock.minimized = False
            print(f"New height after restore: {dock.height()}")

    def _toggle_maximize_window(self, dock):
        """Toggle between maximized and normal size"""
        if not dock.original_geometry:
            # Store current geometry and maximize
            dock.original_geometry = dock.geometry()
            dock.setGeometry(self.main_window.geometry())
        else:
            # Restore original geometry
            dock.setGeometry(dock.original_geometry)
            dock.original_geometry = None 

    def _handle_floating_change(self, dock, floating):
        """Handle changes between docked and floating states"""
        if floating:
            # Restore size when becoming floating
            if hasattr(dock, 'docked_size'):
                dock.resize(dock.docked_size)
        else:
            # Store size before docking
            dock.docked_size = dock.size() 