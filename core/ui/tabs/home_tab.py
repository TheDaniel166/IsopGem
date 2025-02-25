"""
Home tab implementation with theme customization
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QFrame, QFileDialog, QMessageBox, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
import os
from .base_tab import BaseTab
from ..theme.manager import ThemeManager
from ..panels.theme_panel import ThemePanel

class HomeTab(BaseTab):
    """Home tab with theme and UI customization"""
    
    tab_name = "Home"
    tab_order = 0  # First tab
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Create layouts directory if it doesn't exist
        self.layouts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "layouts")
        os.makedirs(self.layouts_dir, exist_ok=True)
    
    def setup_ui(self):
        """Set up the home tab UI"""
        # Create main content layout
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Left side - Layout Management
        left_layout = QVBoxLayout()
        
        # Layout Management group
        layout_group = QFrame()
        layout_group.setFrameStyle(QFrame.Shape.StyledPanel)
        layout_layout = QVBoxLayout(layout_group)
        layout_layout.setSpacing(10)
        
        # Header
        layout_header = QLabel("Layout Management")
        layout_header.setProperty("header", True)
        layout_layout.addWidget(layout_header)
        
        # Buttons in horizontal layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        save_btn = QPushButton("Save Layout")
        save_btn.setToolTip("Save current panel layout")
        save_btn.clicked.connect(self._save_state)
        button_layout.addWidget(save_btn)
        
        load_btn = QPushButton("Load Layout") 
        load_btn.setToolTip("Load saved panel layout")
        load_btn.clicked.connect(self._load_state)
        button_layout.addWidget(load_btn)
        
        delete_btn = QPushButton("Delete Layout")
        delete_btn.setToolTip("Delete saved panel layout")
        delete_btn.clicked.connect(self._delete_state)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        layout_layout.addLayout(button_layout)
        
        left_layout.addWidget(layout_group)
        left_layout.addStretch()
        content_layout.addLayout(left_layout)
        
        # Right side - Theme
        right_layout = QVBoxLayout()
        
        # Theme group
        theme_group = QFrame()
        theme_group.setFrameStyle(QFrame.Shape.StyledPanel)
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setSpacing(10)
        
        # Theme header
        theme_header = QLabel("Theme")
        theme_header.setProperty("header", True)
        theme_layout.addWidget(theme_header)
        
        # Theme buttons in horizontal layout
        theme_buttons = QHBoxLayout()
        theme_buttons.setSpacing(10)
        
        self.light_btn = QPushButton("Light Mode")
        self.light_btn.setCheckable(True)
        self.light_btn.clicked.connect(self._set_light_mode)
        theme_buttons.addWidget(self.light_btn)
        
        self.dark_btn = QPushButton("Dark Mode")
        self.dark_btn.setCheckable(True)
        self.dark_btn.clicked.connect(self._set_dark_mode)
        theme_buttons.addWidget(self.dark_btn)
        
        customize_btn = QPushButton("Customize Theme...")
        customize_btn.clicked.connect(self._show_theme_panel)
        theme_buttons.addWidget(customize_btn)
        
        theme_buttons.addStretch()
        theme_layout.addLayout(theme_buttons)
        
        right_layout.addWidget(theme_group)
        right_layout.addStretch()
        content_layout.addLayout(right_layout)
        
        self.layout.addWidget(content)
        
        # Set initial button state based on current theme
        theme_manager = ThemeManager.get_instance()
        current_theme = theme_manager.get_current_theme()
        self.light_btn.setChecked(current_theme == "light")
        self.dark_btn.setChecked(current_theme == "dark")
        
        # Connect to theme changes
        theme_manager.theme_changed.connect(self._on_theme_changed)
    
    def _save_state(self):
        """Save current panel state"""
        if window := self.window():
            name, ok = QFileDialog.getSaveFileName(
                self, "Save Layout",
                self.layouts_dir,
                "Layout Files (*.layout)"
            )
            if ok and name:
                # Ensure .layout extension
                if not name.endswith('.layout'):
                    name += '.layout'
                window.panel_manager.save_state(name)
                QMessageBox.information(self, "Success", "Layout saved successfully!")
            
    def _load_state(self):
        """Load saved panel state"""
        if window := self.window():
            name, ok = QFileDialog.getOpenFileName(
                self, "Load Layout",
                self.layouts_dir,
                "Layout Files (*.layout)"
            )
            if ok and name:
                window.panel_manager.load_state(name)
                QMessageBox.information(self, "Success", "Layout loaded successfully!")
            
    def _delete_state(self):
        """Delete saved panel state"""
        if window := self.window():
            name, ok = QFileDialog.getOpenFileName(
                self, "Delete Layout",
                self.layouts_dir,
                "Layout Files (*.layout)"
            )
            if ok and name:
                reply = QMessageBox.question(
                    self, "Confirm Delete",
                    f"Are you sure you want to delete this layout?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    os.remove(name)
                    QMessageBox.information(self, "Success", "Layout deleted successfully!")
    
    def _set_light_mode(self):
        """Switch to light mode"""
        if not self.light_btn.isChecked():
            self.light_btn.setChecked(True)
            return
            
        self.dark_btn.setChecked(False)
        ThemeManager.get_instance().apply_theme("light")
    
    def _set_dark_mode(self):
        """Switch to dark mode"""
        if not self.dark_btn.isChecked():
            self.dark_btn.setChecked(True)
            return
            
        self.light_btn.setChecked(False)
        ThemeManager.get_instance().apply_theme("dark")
    
    def _show_theme_panel(self):
        """Show the theme customization panel"""
        panel = ThemePanel()
        self.window().create_panel(panel=panel, name="Theme Customization")
    
    def _on_theme_changed(self, theme_name: str):
        """Handle theme changes"""
        self.light_btn.setChecked(theme_name == "light")
        self.dark_btn.setChecked(theme_name == "dark")
