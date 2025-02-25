"""
Console Panel implementation
"""
from PyQt6.QtWidgets import (QTextEdit, QPushButton, QVBoxLayout, 
                           QHBoxLayout, QComboBox, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor, QColor, QTextCharFormat
from ..base import BasePanel

class ConsolePanel(BasePanel):
    """Interactive console panel"""
    
    command_executed = pyqtSignal(str)  # Command that was executed
    
    def __init__(self, parent=None):
        super().__init__(parent, title="Console")
        self.command_history = []
        self.history_index = 0
        
    def setup_ui(self):
        """Set up the console panel UI"""
        # Output area
        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.output.setStyleSheet("QTextEdit { background-color: #1e1e1e; color: #ffffff; }")
        self.content_layout.addWidget(self.output)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input = QTextEdit(self)
        self.input.setMaximumHeight(60)
        self.input.setStyleSheet("QTextEdit { background-color: #252526; color: #ffffff; }")
        self.input.setPlaceholderText("Enter command...")
        input_layout.addWidget(self.input)
        
        # Controls
        controls_layout = QVBoxLayout()
        
        self.run_btn = QPushButton("Run", self)
        self.run_btn.clicked.connect(self._execute_command)
        controls_layout.addWidget(self.run_btn)
        
        self.clear_btn = QPushButton("Clear", self)
        self.clear_btn.clicked.connect(self.clear_output)
        controls_layout.addWidget(self.clear_btn)
        
        input_layout.addLayout(controls_layout)
        self.content_layout.addLayout(input_layout)
        
        # Log level selector
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Log Level:"))
        
        self.level_combo = QComboBox(self)
        self.level_combo.addItems(["INFO", "DEBUG", "WARNING", "ERROR"])
        level_layout.addWidget(self.level_combo)
        
        level_layout.addStretch()
        self.content_layout.addLayout(level_layout)
    
    def _execute_command(self):
        """Execute the current command"""
        command = self.input.toPlainText().strip()
        if not command:
            return
            
        # Add to history
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # Show command
        self.write_output(f"\n> {command}\n", color="#00FF00")
        
        # Emit signal
        self.command_executed.emit(command)
        
        # Clear input
        self.input.clear()
    
    def write_output(self, text: str, color: str = None):
        """Write text to the output area"""
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        if color:
            format = QTextCharFormat()
            format.setForeground(QColor(color))
            cursor.setCharFormat(format)
            
        cursor.insertText(text)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()
    
    def clear_output(self):
        """Clear the output area"""
        self.output.clear()
    
    def get_preferred_area(self) -> Qt.DockWidgetArea:
        return Qt.DockWidgetArea.BottomDockWidgetArea
    
    def get_preferred_size(self) -> tuple:
        return (600, 300)
