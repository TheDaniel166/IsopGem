"""
Font Manager Window - The Glyph Atlas.
Utility window for inspecting, installing, and previewing custom Magickal fonts.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QListWidget, QTextEdit, QLabel, QSplitter, QFrame,
    QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QAction, QIcon

from shared.ui.font_loader import LOADED_FONTS, install_new_font

class FontManagerWindow(QMainWindow):
    """
    Utility window to inspect loaded Magickal Fonts.
    Shows a list of active custom fonts and a character map preview.
    """
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Font Manager")
        self.resize(900, 600)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a; /* Void Slate */
            }
            QListWidget {
                background-color: #1e293b; /* Stone */
                color: #f8fafc; /* Cloud */
                border: 1px solid #334155;
                font-family: 'Inter';
                font-size: 11pt;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #3b82f6; /* Electric Blue */
                color: white;
            }
            QTextEdit {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                padding: 12px;
            }
            QLabel {
                color: #94a3b8; /* Mist */
                font-family: 'Inter';
                font-weight: 600;
                margin-bottom: 4px;
            }
        """)
        
        self._setup_ui()
        self._load_fonts()
        
    def _setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Splitter for adjustable panes
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # LEFT PANE: Font List
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0,0,0,0)
        
        left_label = QLabel("Active Magickal Fonts")
        self.font_list = QListWidget()
        self.font_list.currentItemChanged.connect(self._on_font_selected)
        
        # Install Button (v2.5.1)
        self.install_btn = QPushButton("Install New Font...")
        self.install_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.install_btn.setStyleSheet("""
            QPushButton {
                background-color: #334155; 
                color: #f8fafc;
                border: 1px solid #475569;
                border-radius: 6px;
                padding: 8px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        self.install_btn.clicked.connect(self._on_install_click)
        
        left_layout.addWidget(left_label)
        left_layout.addWidget(self.font_list)
        left_layout.addWidget(self.install_btn)
        
        # RIGHT PANE: Preview
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0,0,0,0)
        
        right_label = QLabel("Character Key")
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        
        right_layout.addWidget(right_label)
        right_layout.addWidget(self.preview_area)
        
        splitter.addWidget(left_container)
        splitter.addWidget(right_container)
        splitter.setStretchFactor(1, 2) # Give more space to preview
        
        main_layout.addWidget(splitter)
        
    def _load_fonts(self):
        self.font_list.clear()
        
        # If no custom fonts loaded (or run incorrectly), show fallback
        if not LOADED_FONTS:
            self.font_list.addItem("No custom fonts loaded.")
            return

        for font in LOADED_FONTS:
            self.font_list.addItem(font)
            
        # Select first by default
        if self.font_list.count() > 0:
            self.font_list.setCurrentRow(0)
            
    def _on_font_selected(self, current, previous):
        if not current:
            return
            
        font_family = current.text()
        if font_family == "No custom fonts loaded.":
            return
            
        self._render_preview(font_family)
        
    def _on_install_click(self):
        """Handle font installation."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Install Custom Font",
            "",
            "Font Files (*.ttf *.otf);;All Files (*)"
        )
        
        if not file_path:
            return
            
        family = install_new_font(file_path)
        if family:
            QMessageBox.information(
                self, 
                "Font Installed", 
                f"Successfully installed and loaded '{family}'."
            )
            # Refresh list
            self._load_fonts()
            
            # Select the new font
            items = self.font_list.findItems(family, Qt.MatchFlag.MatchExactly)
            if items:
                self.font_list.setCurrentItem(items[0])
        else:
            QMessageBox.critical(
                self,
                "Installation Failed",
                "Could not install or load the selected font file."
            )

    def _render_preview(self, font_family):
        """Generates the HTML preview for the selected font."""
        
        # 1. Sample Text
        html = f"""
        <div style="font-family: 'Inter'; color: #94a3b8; font-size: 10pt; margin-bottom: 10px;">
            FONT FAMILY: <span style="color: white; font-weight: bold;">{font_family}</span>
        </div>
        
        <div style="font-family: '{font_family}'; font-size: 32pt; margin-bottom: 20px;">
            The Quick Brown Fox Jumps Over The Lazy Dog.<br>
            0 1 2 3 4 5 6 7 8 9
        </div>
        <hr style="border: 1px solid #334155;">
        
        <div style="font-family: 'Inter'; color: #94a3b8; font-size: 10pt; margin-top: 10px; margin-bottom: 10px;">
             CHARACTER MAP (A-Z)
        </div>
        
        <table style="width: 100%; border-collapse: collapse;">
        """
        
        # 2. Character Grid (A-Z, a-z)
        # We'll create a simple grid showing the char and its glyph
        chars = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz"
            "0123456789"
            "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        )
        
        # Grid logic
        columns = 8
        count = 0
        html += "<tr>"
        
        for char in chars:
            if count > 0 and count % columns == 0:
                html += "</tr><tr>"
                
            # Each cell: Small label (Inter) + Large Glyph (Custom Font)
            html += f"""
            <td style="border: 1px solid #334155; padding: 10px; text-align: center;">
                <div style="font-family: 'Inter'; font-size: 10px; color: #64748b;">'{char}'</div>
                <div style="font-family: '{font_family}'; font-size: 24pt;">{char}</div>
            </td>
            """
            count += 1
            
        html += "</tr></table>"
        
        self.preview_area.setHtml(html)