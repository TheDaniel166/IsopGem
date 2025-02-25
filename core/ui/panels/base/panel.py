"""
Base panel implementation with modern styling and animations
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPalette, QColor

class BasePanel(QWidget):
    """Modern base panel with animations and effects"""
    
    def __init__(self, parent=None, title="Panel"):
        super().__init__(parent)
        self.title = title
        
        # Create main layout first
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Create content widget to hold effects
        self.content = QWidget(self)
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        self.main_layout.addWidget(self.content)
        
        # Make background slightly transparent
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.content.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
        
        # Set up effects and let child implement UI
        self.setup_effects()
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the panel UI - to be implemented by child classes"""
        pass
        
    def setup_effects(self):
        """Set up visual effects and animations"""
        # Opacity effect
        self.opacity_effect = QGraphicsOpacityEffect(self.content)
        self.opacity_effect.setOpacity(1.0)
        self.content.setGraphicsEffect(self.opacity_effect)
        
        # Set up animations
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.opacity_anim.setDuration(150)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def get_preferred_area(self):
        """Get the preferred dock area for this panel"""
        return Qt.DockWidgetArea.RightDockWidgetArea
        
    def on_show(self):
        """Called when panel becomes visible"""
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.start()
        
    def on_hide(self):
        """Called when panel becomes hidden"""
        self.opacity_anim.setStartValue(1.0)
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.start()
        
    def on_float(self):
        """Called when panel becomes floating"""
        pass
        
    def on_dock(self):
        """Called when panel becomes docked"""
        pass
        
    def enterEvent(self, event):
        """Handle mouse enter events for hover effects"""
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave events for hover effects"""
        super().leaveEvent(event)
