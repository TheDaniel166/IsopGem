"""
Collapsible dock widget with minimize/maximize functionality
"""
from enum import Enum
from PyQt6.QtWidgets import (QDockWidget, QWidget, QPushButton, QStyle, 
                              QHBoxLayout, QLabel, QFrame)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from ..theme.manager import ThemeManager

class PanelState(Enum):
    """Panel collapse states"""
    EXPANDED = 0    # Full size
    TITLEBAR = 1    # Only title bar showing
    TAB = 2         # Collapsed to tab

class CollapsibleDockWidget(QDockWidget):
    """A dock widget that can collapse to titlebar or tab"""
    
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.state = PanelState.EXPANDED
        self.theme_manager = ThemeManager.get_instance()
        self._original_size = None
        self._title_bar_height = 24  # Default title bar height
        self._setup_ui()
        self._setup_animations()
        
        # Connect to theme changed signal
        self.theme_manager.theme_changed.connect(self._update_theme)
        
    def _setup_ui(self):
        """Setup the UI elements"""
        # Create custom title bar
        title_bar = QFrame(self)
        title_bar.setObjectName("dockWidgetTitleBar")
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(2)
        
        # Get current theme colors
        colors = self.theme_manager.get_theme_colors()
        
        # Style title bar
        title_bar.setStyleSheet(f"""
            QFrame#dockWidgetTitleBar {{
                background: {colors["window"]};
                border: none;
                height: 24px;
            }}
            QLabel#dockWidgetTitleLabel {{
                color: {colors["windowText"]};
                font-size: 12px;
            }}
            QPushButton {{
                background: transparent;
                border: none;
                padding: 2px;
            }}
            QPushButton:hover {{
                background: {colors["highlight"]};
                border-radius: 2px;
            }}
            #dockWidgetCloseButton:hover {{
                background: #c42b1c;
            }}
        """)
        
        # Add title label
        title_label = QLabel(self.windowTitle(), title_bar)
        title_label.setObjectName("dockWidgetTitleLabel")
        layout.addWidget(title_label)
        
        # Add stretch to push buttons to the right
        layout.addStretch()
        
        # Add minimize button
        self.minimize_button = QPushButton(title_bar)
        self.minimize_button.setObjectName("dockWidgetMinButton")
        self.minimize_button.setFixedSize(16, 16)
        self.minimize_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMinButton))
        self.minimize_button.clicked.connect(self._toggle_collapse)
        layout.addWidget(self.minimize_button)
        
        # Add maximize button
        self.maximize_button = QPushButton(title_bar)
        self.maximize_button.setObjectName("dockWidgetMaxButton")
        self.maximize_button.setFixedSize(16, 16)
        self.maximize_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton))
        self.maximize_button.clicked.connect(self.expand)
        self.maximize_button.hide()  # Hidden initially since we start expanded
        layout.addWidget(self.maximize_button)
        
        # Add close button
        close_button = QPushButton(title_bar)
        close_button.setObjectName("dockWidgetCloseButton")
        close_button.setFixedSize(16, 16)
        close_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton))
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        # Set custom title bar widget
        self.setTitleBarWidget(title_bar)
        
        # Set features
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable |
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        
    def _setup_animations(self):
        """Setup the animations"""
        self.size_animation = QPropertyAnimation(self, b"size")
        self.size_animation.setDuration(200)  # 200ms
        self.size_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def _toggle_collapse(self):
        """Toggle between states: Expanded -> TitleBar -> Tab"""
        if self.state == PanelState.EXPANDED:
            self.collapse_to_titlebar()
        elif self.state == PanelState.TITLEBAR:
            self.collapse_to_tab()
        else:
            self.expand()
            
    def collapse_to_titlebar(self):
        """Collapse to show only titlebar"""
        if self.state == PanelState.EXPANDED:
            title_bar = self.titleBarWidget()
            if title_bar:
                self._title_bar_height = title_bar.height()
            self._animate_size(QSize(self.width(), self._title_bar_height))
            self.state = PanelState.TITLEBAR
            self.maximize_button.show()
            
    def collapse_to_tab(self):
        """Collapse to tab mode"""
        if self.state == PanelState.TITLEBAR:
            # Calculate tab size based on dock area
            if self.isFloating():
                return  # Don't collapse floating windows to tabs
                
            area = self.parent().dockWidgetArea(self) if self.parent() else Qt.DockWidgetArea.RightDockWidgetArea
            if area in (Qt.DockWidgetArea.LeftDockWidgetArea, Qt.DockWidgetArea.RightDockWidgetArea):
                tab_size = QSize(30, self.height())  # Vertical tab
            else:
                tab_size = QSize(self.width(), 30)  # Horizontal tab
                
            self._animate_size(tab_size)
            self.state = PanelState.TAB
            
    def expand(self):
        """Expand to full size"""
        if self.state != PanelState.EXPANDED:
            # Restore original size
            if self._original_size:
                self._animate_size(self._original_size)
            else:
                self._animate_size(QSize(200, 200))  # Default size if none saved
            self.state = PanelState.EXPANDED
            self.maximize_button.hide()
            
    def _animate_size(self, new_size: QSize):
        """Animate to a new size"""
        if self.state == PanelState.EXPANDED:
            self._original_size = self.size()
            
        self.size_animation.setStartValue(self.size())
        self.size_animation.setEndValue(new_size)
        self.size_animation.start()
        
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        if self.state == PanelState.EXPANDED:
            self._original_size = event.size()

    def _update_theme(self):
        """Update colors when theme changes"""
        colors = self.theme_manager.get_theme_colors()
        title_bar = self.titleBarWidget()
        if title_bar:
            title_bar.setStyleSheet(f"""
                QFrame#dockWidgetTitleBar {{
                    background: {colors["window"]};
                    border: none;
                    height: 24px;
                }}
                QLabel#dockWidgetTitleLabel {{
                    color: {colors["windowText"]};
                    font-size: 12px;
                }}
                QPushButton {{
                    background: transparent;
                    border: none;
                    padding: 2px;
                }}
                QPushButton:hover {{
                    background: {colors["highlight"]};
                    border-radius: 2px;
                }}
                #dockWidgetCloseButton:hover {{
                    background: #c42b1c;
                }}
            """)
