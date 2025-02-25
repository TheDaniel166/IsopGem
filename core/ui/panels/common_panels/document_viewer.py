"""
Enhanced document viewer panel with advanced features
"""
from PyQt6.QtWidgets import (QTextEdit, QVBoxLayout, QFileDialog, QToolBar, 
                          QWidget, QLineEdit, QLabel, QSpinBox, QHBoxLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QTextDocument, QTextCursor, QTextCharFormat, QColor
from pathlib import Path
from ..base.panel import BasePanel
from ..registry import get_registry
from ....documents.base import DocumentContent, ExtractedContent
from ....base.config import ConfigManager
import logging

logger = logging.getLogger(__name__)

class DocumentViewer(BasePanel):
    """Enhanced document viewer panel with zoom, search, and rich content support"""
    def __init__(self, parent=None):
        super().__init__(parent, title="Document Viewer")
        self.current_content = None
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
        self.search_highlights = []
        self.current_search_index = -1
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the viewer interface"""
        # Guard against multiple initialization
        if hasattr(self, 'toolbar') and self.toolbar:
            logger.debug("DocumentViewer UI already set up, skipping initialization")
            return
            
        # Create toolbar
        self.toolbar = QToolBar()
        self.content_layout.insertWidget(0, self.toolbar)
        
        # Add save action to toolbar
        self.save_action = QAction("Save Document", self)
        self.save_action.setEnabled(False)
        self.save_action.triggered.connect(self._save_document)
        self.toolbar.addAction(self.save_action)
        
        self.toolbar.addSeparator()
        
        # Add zoom controls
        zoom_widget = QWidget()
        zoom_layout = QHBoxLayout(zoom_widget)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        
        zoom_label = QLabel("Zoom:")
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(25, 500)
        self.zoom_spin.setSuffix("%")
        self.zoom_spin.setValue(100)
        self.zoom_spin.valueChanged.connect(self._update_zoom)
        
        zoom_layout.addWidget(zoom_label)
        zoom_layout.addWidget(self.zoom_spin)
        
        self.toolbar.addWidget(zoom_widget)
        self.toolbar.addSeparator()
        
        # Add search controls
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.textChanged.connect(self._schedule_search)
        
        self.search_label = QLabel("0/0")
        
        self.prev_match = QAction("↑", self)
        self.prev_match.triggered.connect(lambda: self._navigate_search(False))
        self.prev_match.setEnabled(False)
        
        self.next_match = QAction("↓", self)
        self.next_match.triggered.connect(lambda: self._navigate_search(True))
        self.next_match.setEnabled(False)
        
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_label)
        
        self.toolbar.addWidget(search_widget)
        self.toolbar.addAction(self.prev_match)
        self.toolbar.addAction(self.next_match)
        
        # Text viewer
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.content_layout.addWidget(self.text_edit)
        
    def _update_zoom(self, value):
        """Update the zoom level of the text display"""
        self.text_edit.setZoomFactor(value / 100.0)
        
    def _schedule_search(self):
        """Schedule a search after brief typing delay"""
        self.search_timer.start(300)  # 300ms delay
        
    def _perform_search(self):
        """Perform the actual search operation"""
        search_text = self.search_edit.text()
        
        # Clear previous highlights
        for highlight in self.search_highlights:
            cursor = QTextCursor(highlight)
            format = cursor.charFormat()
            format.setBackground(QColor("transparent"))
            cursor.setCharFormat(format)
        self.search_highlights.clear()
        
        if not search_text:
            self.search_label.setText("0/0")
            self.prev_match.setEnabled(False)
            self.next_match.setEnabled(False)
            self.current_search_index = -1
            return
            
        # Find all matches
        cursor = self.text_edit.document().find(search_text)
        while not cursor.isNull():
            format = cursor.charFormat()
            format.setBackground(QColor("yellow"))
            cursor.setCharFormat(format)
            self.search_highlights.append(cursor)
            cursor = self.text_edit.document().find(search_text, cursor)
        
        # Update search navigation
        count = len(self.search_highlights)
        self.current_search_index = 0 if count > 0 else -1
        self.search_label.setText(f"1/{count}" if count > 0 else "0/0")
        self.prev_match.setEnabled(count > 0)
        self.next_match.setEnabled(count > 0)
        
        # Highlight first match
        if self.current_search_index >= 0:
            self._highlight_current_match()
            
    def _navigate_search(self, forward=True):
        """Navigate between search matches"""
        if not self.search_highlights:
            return
            
        # Update current index
        if forward:
            self.current_search_index = (self.current_search_index + 1) % len(self.search_highlights)
        else:
            self.current_search_index = (self.current_search_index - 1) % len(self.search_highlights)
            
        self._highlight_current_match()
        
    def _highlight_current_match(self):
        """Highlight the current search match"""
        # Update all highlights to yellow
        for highlight in self.search_highlights:
            cursor = QTextCursor(highlight)
            format = cursor.charFormat()
            format.setBackground(QColor("yellow"))
            cursor.setCharFormat(format)
            
        # Set current match to orange
        cursor = QTextCursor(self.search_highlights[self.current_search_index])
        format = cursor.charFormat()
        format.setBackground(QColor("orange"))
        cursor.setCharFormat(format)
        
        # Ensure visible
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()
        
        # Update counter
        self.search_label.setText(f"{self.current_search_index + 1}/{len(self.search_highlights)}")
        
    def initialize(self, **kwargs):
        """Initialize with content from kwargs"""
        if content := kwargs.get('content'):
            self.display_content(content)
            
    def display_content(self, content: ExtractedContent):
        """Display extracted document content"""
        self.current_content = content
        if content and content.text:
            # Update window title to show document type
            doc_type = content.source.file_type.upper() if content.source and content.source.file_type else "Document"
            self.setWindowTitle(f"{doc_type} Viewer - {Path(content.source.file_path).name if content.source else ''}")
            
            # Display content with proper formatting
            if hasattr(content, 'rich_text') and content.rich_text:
                # Use rich text formatting
                doc = content.rich_text.to_qt_document()
                self.text_edit.setDocument(doc)
            else:
                # Fallback to plain text
                self.text_edit.setText(content.text)
            
            self.save_action.setEnabled(True)
            
            # Log successful display
            logger.debug(f"Displayed {doc_type} content from {content.source.file_path if content.source else 'unknown source'}")
        else:
            self.text_edit.setText("No text content to display")
            self.save_action.setEnabled(False)
            logger.warning("Attempted to display empty content")
            
    def _save_document(self):
        """Save the extracted text content"""
        if not self.current_content or not self.current_content.text:
            logger.warning("No text content to save")
            return
            
        # Get default save directory from config
        docs_dir = ConfigManager.get_instance().get_documents_dir()
            
        # Get source info for filename suggestion
        source = self.current_content.source
        if source and source.file_path:
            suggested_name = f"{Path(source.file_path).stem}_extracted"
        else:
            suggested_name = "extracted_text"
        
        # Create full default path
        default_path = docs_dir / f"{suggested_name}.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Extracted Text",
            str(default_path),
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.current_content.text)
                logger.info(f"Successfully saved extracted text to {file_path}")
            except Exception as e:
                logger.error(f"Failed to save extracted text: {e}")

# Register panel factory
get_registry().register("Document Viewer", lambda: DocumentViewer())
