"""
Theme customization widget
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QFrame, QSplitter, QGridLayout, QComboBox,
                           QInputDialog, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .color_picker import ColorPicker
from .theme_preview import ThemePreview
from ..theme.manager import ThemeManager

class ThemeCustomizer(QWidget):
    """Widget for customizing theme colors"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.get_instance()
        self._setup_ui()
        
        # Initialize with current colors
        self._update_color_pickers()
        
        # Connect to theme changes
        self.theme_manager.theme_changed.connect(self._on_theme_changed)
        self.theme_manager.mode_changed.connect(self._on_mode_changed_signal)
    
    def _setup_ui(self):
        """Set up the UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add title
        title = QLabel("Theme Colors")
        title.setProperty("header", True)
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        main_layout.addWidget(title)
        
        # Mode and theme selection
        controls_layout = QHBoxLayout()
        
        # Mode selector
        mode_label = QLabel("Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["light", "dark"])
        self.mode_combo.setCurrentText(self.theme_manager.get_current_mode())
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        controls_layout.addWidget(mode_label)
        controls_layout.addWidget(self.mode_combo)
        
        # Theme selector
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self._update_theme_combo()
        self.theme_combo.currentTextChanged.connect(self._on_theme_selected)
        controls_layout.addWidget(theme_label)
        controls_layout.addWidget(self.theme_combo)
        
        main_layout.addLayout(controls_layout)
        
        # Add theme management buttons
        theme_buttons = QHBoxLayout()
        
        save_theme = QPushButton("Save Theme")
        save_theme.clicked.connect(self._on_save_theme)
        theme_buttons.addWidget(save_theme)
        
        delete_theme = QPushButton("Delete Theme")
        delete_theme.clicked.connect(self._on_delete_theme)
        theme_buttons.addWidget(delete_theme)
        
        main_layout.addLayout(theme_buttons)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)  # Prevent collapsing sections
        main_layout.addWidget(splitter)
        
        # Create controls panel
        controls = QWidget()
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setSpacing(20)
        
        # Add color pickers in a grid
        colors_frame = QFrame()
        colors_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        colors_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        grid_layout = QGridLayout(colors_frame)
        grid_layout.setContentsMargins(15, 15, 15, 15)
        grid_layout.setSpacing(10)
        grid_layout.setColumnMinimumWidth(1, 150)  # Make color picker column wider
        
        def add_color_picker(row: int, label_text: str, color_key: str):
            """Add a color picker with label to the grid"""
            label = QLabel(label_text)
            grid_layout.addWidget(label, row, 0)
            
            picker = ColorPicker()
            grid_layout.addWidget(picker, row, 1)
            
            # Connect color change signal
            picker.color_changed.connect(lambda color: self._on_color_changed(color_key, color))
            
            return picker
        
        # Window colors
        row = 0
        self.window_picker = add_color_picker(row, "Window:", "window")
        row += 1
        self.window_text_picker = add_color_picker(row, "Window Text:", "windowText")
        
        # Add section separator
        row += 1
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        grid_layout.addWidget(separator, row, 0, 1, 2)
        
        # Base colors
        row += 1
        self.base_picker = add_color_picker(row, "Base:", "base")
        row += 1
        self.alt_base_picker = add_color_picker(row, "Alt Base:", "alternateBase")
        row += 1
        self.text_picker = add_color_picker(row, "Text:", "text")
        
        # Add section separator
        row += 1
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        grid_layout.addWidget(separator, row, 0, 1, 2)
        
        # Button colors
        row += 1
        self.button_picker = add_color_picker(row, "Button:", "button")
        row += 1
        self.button_text_picker = add_color_picker(row, "Button Text:", "buttonText")
        
        # Add section separator
        row += 1
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        grid_layout.addWidget(separator, row, 0, 1, 2)
        
        # Selection colors
        row += 1
        self.highlight_picker = add_color_picker(row, "Selection:", "highlight")
        row += 1
        self.highlight_text_picker = add_color_picker(row, "Selection Text:", "highlightedText")
        
        # Add section separator
        row += 1
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        grid_layout.addWidget(separator, row, 0, 1, 2)
        
        # Link colors
        row += 1
        self.link_picker = add_color_picker(row, "Link:", "link")
        
        # Add buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        reset_button = QPushButton("Reset Colors")
        reset_button.clicked.connect(self._on_reset_clicked)
        buttons_layout.addWidget(reset_button)
        
        load_button = QPushButton("Load Theme")
        load_button.clicked.connect(self._on_load_theme)
        buttons_layout.addWidget(load_button)
        
        save_button = QPushButton("Save Theme")
        save_button.clicked.connect(self._on_save_theme)
        buttons_layout.addWidget(save_button)
        
        delete_button = QPushButton("Delete Theme")
        delete_button.clicked.connect(self._on_delete_theme)
        buttons_layout.addWidget(delete_button)
        
        controls_layout.addWidget(colors_frame)
        controls_layout.addLayout(buttons_layout)
        controls_layout.addStretch()
        
        # Add controls to splitter
        splitter.addWidget(controls)
        
        # Create preview panel
        preview = ThemePreview()
        preview.setMinimumWidth(500)  # Set minimum width for preview
        splitter.addWidget(preview)
        
        # Set initial splitter sizes (40% controls, 60% preview)
        total_width = self.width()
        splitter.setSizes([int(total_width * 0.4), int(total_width * 0.6)])
    
    def _update_theme_combo(self):
        """Update theme combo box items"""
        current_theme = self.theme_manager.get_current_theme()
        self.theme_combo.clear()
        self.theme_combo.addItems(["light", "dark"] + self.theme_manager.get_custom_themes())
        self.theme_combo.setCurrentText(current_theme)
    
    def _on_mode_changed(self, mode: str):
        """Handle mode combo change - sets base mode"""
        self.theme_manager.set_mode(mode)
    
    def _on_mode_changed_signal(self, mode: str):
        """Handle mode change signal from theme manager"""
        self.mode_combo.blockSignals(True)
        self.mode_combo.setCurrentText(mode)
        self.mode_combo.blockSignals(False)
    
    def _on_theme_selected(self, theme_name: str):
        """Handle theme selection"""
        if theme_name != self.theme_manager.get_current_theme():
            self.theme_manager.apply_theme(theme_name)
    
    def _on_color_changed(self, color_key: str, color: str):
        """Handle color picker changes"""
        self.theme_manager.update_custom_colors({color_key: color})
    
    def _on_save_clicked(self):
        """Handle save button click"""
        # TODO: Add dialog to get theme name
        self.theme_manager.save_custom_theme("custom")
    
    def _on_reset_clicked(self):
        """Reset colors to default for current mode"""
        # Reset to default colors for current mode
        self.theme_manager.set_mode(self.theme_manager.get_current_mode())
        
    def _on_theme_changed(self, theme_name: str):
        """Handle theme change signal"""
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentText(theme_name)
        self.theme_combo.blockSignals(False)
        self._update_color_pickers()
    
    def _update_color_pickers(self):
        """Update color pickers with current theme colors"""
        colors = self.theme_manager.get_theme_colors()
        
        self.window_picker.set_color(colors["window"])
        self.window_text_picker.set_color(colors["windowText"])
        self.base_picker.set_color(colors["base"])
        self.alt_base_picker.set_color(colors["alternateBase"])
        self.text_picker.set_color(colors["text"])
        self.button_picker.set_color(colors["button"])
        self.button_text_picker.set_color(colors["buttonText"])
        self.highlight_picker.set_color(colors["highlight"])
        self.highlight_text_picker.set_color(colors["highlightedText"])
        self.link_picker.set_color(colors["link"])

    def _on_load_theme(self):
        """Load a saved theme"""
        themes = self.theme_manager.get_custom_themes()
        if not themes:
            QMessageBox.information(
                self,
                "No Custom Themes",
                "No custom themes available to load"
            )
            return
            
        theme, ok = QInputDialog.getItem(
            self,
            "Load Theme",
            "Select theme to load:",
            themes,
            0,  # Current index
            False  # Not editable
        )
        
        if ok and theme:
            self.theme_manager.apply_theme(theme)
            self.theme_combo.setCurrentText(theme)
    
    def _on_save_theme(self):
        """Save current theme"""
        current = self.theme_combo.currentText()
        name, ok = QInputDialog.getText(
            self, 
            "Save Theme",
            "Theme name:",
            QLineEdit.EchoMode.Normal,
            current if current not in ["light", "dark"] else ""
        )
        
        if ok and name:
            if name in ["light", "dark"]:
                QMessageBox.warning(
                    self,
                    "Invalid Name",
                    "Cannot use reserved names 'light' or 'dark'"
                )
                return
                
            if name in self.theme_manager.get_custom_themes():
                reply = QMessageBox.question(
                    self,
                    "Overwrite Theme",
                    f"Theme '{name}' already exists. Overwrite?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            self.theme_manager.save_custom_theme(name)
            self._update_theme_combo()
            self.theme_combo.setCurrentText(name)
    
    def _on_delete_theme(self):
        """Delete current theme"""
        current = self.theme_combo.currentText()
        
        if current in ["light", "dark"]:
            QMessageBox.warning(
                self,
                "Cannot Delete",
                "Cannot delete built-in themes"
            )
            return
            
        reply = QMessageBox.question(
            self,
            "Delete Theme",
            f"Delete theme '{current}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.theme_manager.delete_custom_theme(current)
            self._update_theme_combo()
            self.theme_combo.setCurrentText(self.theme_manager.get_current_mode())
