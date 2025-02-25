"""
Theme management system for IsopGem
"""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import QObject, pyqtSignal, QSettings, Qt
import json
from typing import Dict, Any

class ThemeManager(QObject):
    """Manages application themes and styling"""
    
    # Signals
    theme_changed = pyqtSignal(str)
    mode_changed = pyqtSignal(str)
    custom_theme_updated = pyqtSignal(dict)
    
    # Default colors for themes
    DEFAULT_LIGHT_THEME = {
        "window": "#ffffff",
        "windowText": "#000000",
        "base": "#ffffff",
        "alternateBase": "#f7f7f7",
        "text": "#000000",
        "button": "#f0f0f0",
        "buttonText": "#000000",
        "highlight": "#308cc6",
        "highlightedText": "#ffffff",
        "link": "#0000ff"
    }
    
    DEFAULT_DARK_THEME = {
        "window": "#2d2d2d",
        "windowText": "#ffffff",
        "base": "#353535",
        "alternateBase": "#3d3d3d",
        "text": "#ffffff",
        "button": "#454545",
        "buttonText": "#ffffff",
        "highlight": "#2a82da",
        "highlightedText": "#ffffff",
        "link": "#56c8ff"
    }
    
    # Singleton instance
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance
    
    def __init__(self):
        """Initialize theme manager"""
        if ThemeManager._instance is not None:
            raise RuntimeError("Use ThemeManager.get_instance()")
            
        super().__init__()
        
        # Load settings
        self.settings = QSettings("IsopGem", "Theme")
        
        # Load custom themes
        themes_json = self.settings.value("theme/custom_themes", "{}")
        self._custom_themes = json.loads(themes_json)
        
        # Load current theme and custom colors
        self._current_theme = self.settings.value("theme/current", "light")
        custom_colors = self.settings.value("theme/custom", "{}")
        self._current_custom_colors = json.loads(custom_colors) if isinstance(custom_colors, str) else custom_colors
        
        # Load current mode
        self._current_mode = self.settings.value("theme/mode", "light")
        
        # Apply initial theme
        self.apply_theme(self._current_theme)
    
    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self._current_theme
    
    def get_current_mode(self) -> str:
        """Get current theme mode (light/dark)"""
        return self._current_mode
    
    def set_mode(self, mode: str):
        """Set the theme mode (light/dark) and apply its default colors"""
        if mode not in ["light", "dark"]:
            raise ValueError(f"Invalid mode: {mode}")
        
        # Update mode
        self._current_mode = mode
        self.settings.setValue("theme/mode", mode)
        
        # Clear any custom colors and theme
        self._current_custom_colors = {}
        self._current_theme = mode  # Reset to base theme
        self.settings.setValue("theme/custom", "{}")
        self.settings.setValue("theme/current", mode)
        
        # Apply default colors for this mode
        colors = self.get_theme_colors()
        palette = self._create_palette(colors)
        QApplication.instance().setPalette(palette)
        
        # Apply theme stylesheet
        stylesheet = self._create_stylesheet(colors)
        QApplication.instance().setStyleSheet(stylesheet)
        
        # Emit signals
        self.mode_changed.emit(mode)
        self.theme_changed.emit(mode)
        self.custom_theme_updated.emit({})

    def get_theme_colors(self) -> dict:
        """Get current theme colors"""
        # Get base theme colors based on mode
        if self._current_mode == "light":
            colors = self.DEFAULT_LIGHT_THEME.copy()
        else:
            colors = self.DEFAULT_DARK_THEME.copy()
            
        # Apply custom theme colors if any
        if self._current_theme and self._current_theme in self._custom_themes:
            custom_colors = self._custom_themes[self._current_theme]["colors"]
            colors.update(custom_colors)
        
        # Apply any current custom colors
        if self._current_custom_colors:
            colors.update(self._current_custom_colors)
            
        return colors
    
    def apply_theme(self, theme_name: str):
        """Apply a theme, respecting its base mode"""
        # Update current theme
        self._current_theme = theme_name
        self.settings.setValue("theme/current", theme_name)
        
        if theme_name in self._custom_themes:
            # For custom theme: first set mode, then apply custom colors
            theme_data = self._custom_themes[theme_name]
            self._current_mode = theme_data["mode"]
            self._current_custom_colors = theme_data["colors"].copy()
        else:
            # For base themes (light/dark): just set the mode
            self._current_mode = theme_name
            self._current_custom_colors = {}
        
        # Apply colors
        colors = self.get_theme_colors()
        palette = self._create_palette(colors)
        QApplication.instance().setPalette(palette)
        
        # Apply stylesheet
        stylesheet = self._create_stylesheet(colors)
        QApplication.instance().setStyleSheet(stylesheet)
        
        # Save settings
        self.settings.setValue("theme/mode", self._current_mode)
        self.settings.setValue("theme/custom", json.dumps(self._current_custom_colors))
        
        # Emit signals
        self.theme_changed.emit(theme_name)
        self.mode_changed.emit(self._current_mode)
        self.custom_theme_updated.emit(self._current_custom_colors)
    
    def update_custom_colors(self, colors: Dict[str, Any]):
        """Update custom color overrides"""
        # Update custom theme
        self._current_custom_colors.update(colors)
        self.settings.setValue("theme/custom", json.dumps(self._current_custom_colors))
        
        # Get theme colors
        colors = self.get_theme_colors()
        
        # Create and apply palette
        palette = self._create_palette(colors)
        QApplication.instance().setPalette(palette)
        
        # Apply theme stylesheet
        stylesheet = self._create_stylesheet(colors)
        QApplication.instance().setStyleSheet(stylesheet)
        
        # Emit update signal
        self.custom_theme_updated.emit(self._current_custom_colors)
    
    def reset_custom_colors(self):
        """Reset all custom colors"""
        self._current_custom_colors = {}
        self.settings.setValue("theme/custom", "{}")
        self.apply_theme(self._current_theme)
        self.custom_theme_updated.emit({})
    
    def save_custom_theme(self, name: str):
        """Save current theme as custom theme"""
        # Store theme data
        theme_data = {
            "mode": self._current_mode,
            "colors": self._current_custom_colors.copy()
        }
        
        # Save theme
        self._custom_themes[name] = theme_data
        self._save_custom_themes()
        
        # Update current theme
        self._current_theme = name
        self.settings.setValue("theme/current", name)
        self.theme_changed.emit(name)
    
    def delete_custom_theme(self, name: str):
        """Delete a custom theme"""
        if name not in self._custom_themes:
            return
            
        # Get current mode before deletion
        current_mode = self._current_mode
        
        # Delete theme
        del self._custom_themes[name]
        self._save_custom_themes()
        
        # If current theme was deleted, switch to mode theme
        if self._current_theme == name:
            self._current_theme = current_mode
            self.settings.setValue("theme/current", current_mode)
            self.theme_changed.emit(current_mode)
    
    def get_custom_themes(self) -> list:
        """Get list of custom theme names"""
        return list(self._custom_themes.keys())
    
    def get_custom_theme_data(self, name: str) -> dict:
        """Get data for a custom theme"""
        if name not in self._custom_themes:
            raise ValueError(f"Theme not found: {name}")
        return self._custom_themes[name]
    
    def _create_palette(self, colors: dict) -> QPalette:
        """Create a palette from theme colors"""
        palette = QPalette()
        
        # Color groups
        groups = [
            QPalette.ColorGroup.Normal,
            QPalette.ColorGroup.Disabled,
            QPalette.ColorGroup.Inactive
        ]
        
        for group in groups:
            # Window colors
            palette.setColor(group, QPalette.ColorRole.Window, QColor(colors["window"]))
            palette.setColor(group, QPalette.ColorRole.WindowText, QColor(colors["windowText"]))
            
            # Widget colors
            palette.setColor(group, QPalette.ColorRole.Base, QColor(colors["base"]))
            palette.setColor(group, QPalette.ColorRole.AlternateBase, QColor(colors["alternateBase"]))
            palette.setColor(group, QPalette.ColorRole.Text, QColor(colors["text"]))
            
            # Button colors
            palette.setColor(group, QPalette.ColorRole.Button, QColor(colors["button"]))
            palette.setColor(group, QPalette.ColorRole.ButtonText, QColor(colors["buttonText"]))
            
            # Selection colors
            palette.setColor(group, QPalette.ColorRole.Highlight, QColor(colors["highlight"]))
            palette.setColor(group, QPalette.ColorRole.HighlightedText, QColor(colors["highlightedText"]))
            
            # Link color
            palette.setColor(group, QPalette.ColorRole.Link, QColor(colors["link"]))
        
        return palette
    
    def _create_stylesheet(self, colors: dict) -> str:
        """Create stylesheet from theme colors"""
        return f"""
            QWidget {{
                background-color: {colors["window"]};
                color: {colors["windowText"]};
            }}
            
            QFrame {{
                border: 1px solid {colors["button"]};
                border-radius: 4px;
            }}
            
            QPushButton {{
                background-color: {colors["button"]};
                color: {colors["buttonText"]};
                border: 1px solid {colors["button"]};
                border-radius: 4px;
                padding: 5px 10px;
            }}
            
            QPushButton:hover {{
                background-color: {colors["highlight"]};
                color: {colors["highlightedText"]};
                border-color: {colors["highlight"]};
            }}
            
            QLineEdit {{
                background-color: {colors["base"]};
                color: {colors["text"]};
                border: 1px solid {colors["button"]};
                border-radius: 4px;
                padding: 5px;
            }}
            
            QLabel[header=true] {{
                font-weight: bold;
                font-size: 14px;
                color: {colors["highlight"]};
            }}
        """
    
    def _save_custom_themes(self):
        """Save custom themes to settings"""
        self.settings.setValue("theme/custom_themes", json.dumps(self._custom_themes))
