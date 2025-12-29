from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QWidget,
    QScrollArea,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QSizePolicy
)
from shared.ui.theme import COLORS

class ScrollableTabBar(QWidget):
    """
    A scrollable horizontal tab bar using QScrollArea.
    Replaces QTabWidget's arrow-based scrolling with a smooth scrollbar.
    """
    
    currentChanged = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70) # Increased to fit scrollbar + buttons
        
        # Main Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        # Always show horizontal scrollbar to ensure it doesn't jump in/out
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Style the scrollbar to be slim and themed
        # Using 'stone' for handle to be neutral, and slightly wider for visibility
        scrollbar_handle = COLORS.get('stone', '#334155')
        scrollbar_bg = "#0f0f13"  # Darker track
        
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: {scrollbar_bg};
                height: 12px;
                margin: 0px 0px 0px 0px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background: {scrollbar_handle};
                min-width: 20px;
                border-radius: 6px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
                border: none;
                background: none;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """)
        
        # Content Container
        self.content_widget = QWidget()
        self.content_widget.setObjectName("tab_container")
        self.content_widget.setStyleSheet("QWidget#tab_container { background: transparent; }")
        
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(2)
        # Removed addStretch to allow buttons to take space, relying on scroll
        # self.content_layout.addStretch() 
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)
        
        # State
        self.buttons = []
        self._current_index = -1
        
    def add_tab(self, text: str) -> int:
        """Add a new tab button."""
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # Adaptive Width: Let the button size to its text content + padding
        # We remove the fixed min-width so short labels are short and long labels are long.
        btn.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        btn.setFont(QFont("Roboto", 11, QFont.Weight.Medium))
        
        index = len(self.buttons)
        btn.clicked.connect(lambda checked, idx=index: self.set_current_index(idx))
        
        self.content_layout.addWidget(btn)
        self.buttons.append(btn)
        
        if self._current_index == -1:
            self.set_current_index(0)
        
        # Ensure new button is styled correctly immediately
        self._update_styles()
            
        return index
        
    def set_current_index(self, index: int):
        """Set the active tab index."""
        if 0 <= index < len(self.buttons):
            if self._current_index != index:
                self._current_index = index
                self._update_styles()
                self.currentChanged.emit(index)
                self._ensure_visible(index)
                
    def current_index(self) -> int:
        return self._current_index
        
    def count(self) -> int:
        return len(self.buttons)
        
    def _update_styles(self):
        """Update button styles based on active state."""
        # Using 'seeker' (Gold) for active state to match Celestia theme
        active_color = COLORS.get('seeker', '#f59e0b') 
        text_active = "#ffffff"
        text_dim = "#aaaaaa"
        bg_hover = "rgba(255, 255, 255, 0.05)"
        
        for i, btn in enumerate(self.buttons):
            is_active = (i == self._current_index)
            
            if is_active:
                style = f"""
                    QPushButton {{
                        color: {text_active};
                        background-color: transparent;
                        border: none;
                        border-bottom: 2px solid {active_color};
                        padding: 8px 16px;
                        font-weight: bold;
                    }}
                """
            else:
                style = f"""
                    QPushButton {{
                        color: {text_dim};
                        background-color: transparent;
                        border: none;
                        border-bottom: 2px solid transparent;
                        padding: 8px 16px;
                    }}
                    QPushButton:hover {{
                        color: {text_active};
                        background-color: {bg_hover};
                    }}
                """
            btn.setStyleSheet(style)

    def _ensure_visible(self, index: int):
        """Scroll to ensure the selected tab is visible."""
        if 0 <= index < len(self.buttons):
            btn = self.buttons[index]
            self.scroll_area.ensureWidgetVisible(btn)
