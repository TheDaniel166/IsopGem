"""
Common panel implementations
"""
from pathlib import Path
from typing import Optional, Dict, Type

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget,
                          QPushButton, QLabel, QFrame)
from PyQt6.QtCore import Qt

from ..documents.viewer.base import DocumentViewer
from ..documents.viewer.text import TextViewer
from ..documents.processor import DocumentProcessor


class PropertiesPanel(QWidget):
    """Properties panel implementation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup properties panel UI"""
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Properties Panel"))


class CombinedViewer(QWidget):
    """
    Combined document viewer with tabs for different content types
    
    Features:
    - Text view
    - Table view (coming soon)
    - Image view (coming soon)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.processor = DocumentProcessor()
        self._setup_ui()
        
    def _setup_ui(self):
        """Create the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tab widget for different views
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)  # Modern look
        layout.addWidget(self.tabs)
        
        # Add viewers
        self.text_viewer = TextViewer()
        self.tabs.addTab(self.text_viewer, "Text")
        
        # Table and image viewers coming soon
        # self.table_viewer = TableViewer()
        # self.image_viewer = ImageViewer()
        # self.tabs.addTab(self.table_viewer, "Tables")
        # self.tabs.addTab(self.image_viewer, "Images")
        
    async def load_file(self, file_path: Path):
        """Load and process a file"""
        try:
            # Process the file
            output = await self.processor.process(
                file_path,
                extract_types=['text'],  # Add 'tables', 'images' later
                export_format='json'
            )
            
            # Load the content into viewers
            if self.text_viewer and output:
                content = await self.processor.load_content(output)
                self.text_viewer.load_content(content)
                
        except Exception as e:
            # Show error in text viewer
            if self.text_viewer:
                self.text_viewer.show_error(f"Error loading file: {str(e)}")
                
    def _show_loading(self, show: bool = True):
        """Show/hide loading indicator"""
        # TODO: Add loading indicator
        pass
