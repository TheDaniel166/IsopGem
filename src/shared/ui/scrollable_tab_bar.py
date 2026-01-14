"""
⚠️  GRANDFATHERED VIOLATION - Pre-existing before Law of Substrate (2026-01-13)

SHARED JUSTIFICATION:
- RATIONALE: GRANDFATHERED - Needs manual review
- USED BY: Astrology (1 references)
- CRITERION: Unknown - requires categorization

This module violates the Law of the Substrate but is documented as pre-existing.
Refactoring plan: See wiki/04_prophecies/shared_folder_audit_2026-01-13.md
"""


from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QScrollArea,
    QHBoxLayout,
    QPushButton,
    QFrame,
    QSizePolicy
)
from shared.ui.theme import (
    get_scrollable_tab_bar_style,
    get_scrollable_tab_button_style,
)

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
        self.scroll_area.setObjectName("scrollable_tab_area")
        self.scroll_area.setWidgetResizable(True)
        # Always show horizontal scrollbar to ensure it doesn't jump in/out
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setStyleSheet(get_scrollable_tab_bar_style())
        
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
        self.scroll_area.horizontalScrollBar().setObjectName("scrollable_tab_scrollbar")
        
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
        for i, btn in enumerate(self.buttons):
            is_active = (i == self._current_index)
            btn.setStyleSheet(get_scrollable_tab_button_style(is_active))

    def _ensure_visible(self, index: int):
        """Scroll to ensure the selected tab is visible."""
        if 0 <= index < len(self.buttons):
            btn = self.buttons[index]
            self.scroll_area.ensureWidgetVisible(btn)