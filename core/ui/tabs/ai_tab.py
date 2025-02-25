"""
AI Tools Tab implementation with Karnak, the spiritual guide
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QPushButton, QToolBar,
                            QFileDialog, QLabel, QFrame, QGridLayout, QStyle,
                            QProgressBar, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
import shutil
from qasync import asyncSlot
import logging
from typing import List, Optional

from .base_tab import BaseTab
from ..panels.common_panels import PropertiesPanel, DocumentViewer
from ..panels.ai_panels.console_panel import ConsolePanel
from ..panels.ai_panels.test_panel import AITestPanel
from ..panels.registry import get_registry
from ...documents.parsers import get_parser
from ...documents.base import DocumentContent, ExtractedContent
from ...documents.extractors.text import TextExtractor
from ...documents.analysis.analyzer import (
    analyze_document_structure,
    find_cross_document_relationships
)
from ...base.config import ConfigManager
from ...ai.rag_manager import RAGManager

logger = logging.getLogger(__name__)

class AIToolsTab(BaseTab):
    """Tab containing AI-related tools and interfaces, including Karnak the spiritual guide"""
    
    # Tab metadata
    tab_name = "AI Tools"
    tab_order = 1  # After home tab
    
    # Signals
    chat_started = pyqtSignal()
    chat_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_batch = []  # Track current batch of documents
        
        # Initialize panels
        self.test_panel = None
        self.console = None
        self.properties = None
        
        # Initialize Karnak
        self.rag = RAGManager()
        
    def setup_ui(self):
        """Set up the AI tools interface"""
        super().setup_ui()
        
        # Create progress bar (hidden by default)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.layout.addWidget(self.progress_bar)
        
        # Create status label
        self.status_label = QLabel(self)
        self.status_label.setVisible(False)
        self.layout.addWidget(self.status_label)
        
        # Main horizontal layout
        main_layout = QHBoxLayout()
        self.layout.addLayout(main_layout)
        
        # Left side - Chat Interface (1/3)
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(4, 4, 4, 4)
        self.setup_chat_interface(chat_layout)
        
        # Add a vertical line separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        
        # Right side - Panel Buttons (2/3)
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(4, 4, 4, 4)
        self.setup_buttons_interface(buttons_layout)
        
        # Add widgets to main layout with proper sizing
        main_layout.addWidget(chat_widget, 1)  # 1/3 width
        main_layout.addWidget(line)
        main_layout.addWidget(buttons_widget, 2)  # 2/3 width
    
    def setup_chat_interface(self, parent_layout):
        """Set up the chat interface components"""
        # Title with Karnak
        title_bar = QToolBar()
        title = QLabel("Karnak - Spiritual Guide")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_bar.addWidget(title)
        parent_layout.addWidget(title_bar)
        
        # Chat history with welcome message
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        parent_layout.addWidget(self.chat_history)
        
        # Welcome message
        self.chat_history.append(
            "Welcome, seeker of wisdom. I am Karnak, named after the ancient temple "
            "of spiritual knowledge. How may I guide you today?"
        )
        
        # Input area
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(60)
        self.chat_input.setPlaceholderText("Ask Karnak for guidance...")
        self.chat_input.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        self.send_button = QPushButton("Ask")
        self.send_button.setFixedWidth(60)
        self.send_button.clicked.connect(self._on_send_clicked)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        
        # Connect return key to send
        self.chat_input.textChanged.connect(self._on_input_changed)
        
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(self.send_button)
        
        parent_layout.addWidget(input_container)
        
    def _on_input_changed(self):
        """Handle input changes and allow Ctrl+Enter to send"""
        cursor = self.chat_input.textCursor()
        if cursor.position() > 0:
            # Check if Ctrl+Enter was pressed
            if (self.chat_input.toPlainText()[-1] == '\n' and 
                Qt.KeyboardModifier.ControlModifier in QApplication.keyboardModifiers()):
                # Remove the newline and send
                text = self.chat_input.toPlainText()[:-1]
                self.chat_input.setPlainText(text)
                self._on_send_clicked()
                
    @asyncSlot()
    async def _on_send_clicked(self):
        """Handle send button click"""
        try:
            query = self.chat_input.toPlainText().strip()
            if not query:
                return
                
            # Clear input and disable button
            self.chat_input.clear()
            self.send_button.setEnabled(False)
            self.chat_started.emit()
            
            # Show user message
            self.chat_history.append(f"\nYou: {query}")
            
            # Get Karnak's response
            results = await self.rag.search(query)
            
            # Format response
            if not results:
                response = (
                    "I apologize, but I don't find any specific wisdom in our texts about that. "
                    "Perhaps you could rephrase your question, or we could explore a related topic?"
                )
            else:
                # Build context from results
                context = []
                for result in results:
                    context.append(
                        f"From {result['source']} (Section {result['chunk_index'] + 1} of {result['total_chunks']}):\n"
                        f"{result['content']}"
                    )
                
                # Format response with context
                response = (
                    "Drawing upon the ancient wisdom, I can share this understanding:\n\n"
                    f"{' '.join(context)}\n\n"
                    "Is there a specific aspect of this teaching you'd like to explore further?"
                )
            
            # Show response
            self.chat_history.append(f"\nKarnak: {response}\n")
            
            # Scroll to bottom
            self.chat_history.verticalScrollBar().setValue(
                self.chat_history.verticalScrollBar().maximum()
            )
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            self.chat_history.append(
                "\nKarnak: I apologize, but I am unable to access the wisdom "
                "at this moment. Please try again."
            )
        finally:
            self.send_button.setEnabled(True)
            self.chat_finished.emit()

    def setup_buttons_interface(self, parent_layout):
        """Set up the buttons interface"""
        # Document Management Group
        doc_group = QFrame()
        doc_group.setFrameStyle(QFrame.Shape.StyledPanel)
        doc_layout = QVBoxLayout(doc_group)
        doc_layout.setSpacing(8)
        
        # Title
        title = QLabel("Document Management")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        doc_layout.addWidget(title)
        
        # Buttons grid
        grid = QGridLayout()
        grid.setSpacing(6)
        
        # Import Document
        import_btn = QPushButton("Import Document")
        import_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))
        import_btn.clicked.connect(self._show_import_dialog)
        grid.addWidget(import_btn, 0, 0)
        
        # View Saved Documents
        view_btn = QPushButton("View Documents")
        view_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView))
        view_btn.clicked.connect(self._show_view_dialog)
        grid.addWidget(view_btn, 0, 1)
        
        # Properties Panel
        prop_btn = QPushButton("Properties")
        prop_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView))
        prop_btn.clicked.connect(self._show_properties_panel)
        grid.addWidget(prop_btn, 1, 0)
        
        # Console Panel
        console_btn = QPushButton("Console")
        console_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_CommandLink))
        console_btn.clicked.connect(self._show_console_panel)
        grid.addWidget(console_btn, 1, 1)
        
        # Test Panel
        test_btn = QPushButton("AI Test")
        test_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        test_btn.clicked.connect(self._show_test_panel)
        grid.addWidget(test_btn, 2, 0)
        
        doc_layout.addLayout(grid)
        parent_layout.addWidget(doc_group)
        parent_layout.addStretch()
        
    def _show_test_panel(self):
        """Show test panel"""
        window = self.get_main_window()
        if window:
            if not self.test_panel:
                self.test_panel = AITestPanel()
            window.create_panel(panel=self.test_panel, name="AI Test")
            
    def _show_properties_panel(self):
        """Show the properties panel"""
        if window := self.window():
            if not self.properties:
                registry = get_registry()
                self.properties = registry.create_panel("Properties")
            window.create_panel(panel=self.properties, name="Properties")
        
    def _show_console_panel(self):
        """Show the console panel"""
        if window := self.window():
            if not self.console:
                registry = get_registry()
                self.console = registry.create_panel("Console")
            window.create_panel(panel=self.console, name="Console")

    def _connect_progress_tracking(self, progress):
        """Connect progress tracking signals"""
        progress.started.connect(self._on_processing_started)
        progress.progress.connect(self._on_processing_progress)
        progress.status.connect(self._on_processing_status)
        progress.finished.connect(self._on_processing_finished)
        progress.error.connect(self._on_processing_error)
    
    def _on_processing_started(self, description: str):
        """Handle processing started"""
        self.progress_bar.setVisible(True)
        self.status_label.setVisible(True)
        self.status_label.setText(description)
        self.progress_bar.setValue(0)
    
    def _on_processing_progress(self, current: int, total: int):
        """Handle processing progress"""
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
        else:
            # Show busy indicator if total is unknown
            self.progress_bar.setMaximum(0)
    
    def _on_processing_status(self, status: str):
        """Handle processing status update"""
        self.status_label.setText(status)
    
    def _on_processing_finished(self):
        """Handle processing finished"""
        self.progress_bar.setVisible(False)
        self.status_label.setVisible(False)
    
    def _on_processing_error(self, message: str):
        """Handle processing error"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {message}")
        self.status_label.setStyleSheet("color: red")
        self.status_label.setVisible(True)
    
    @asyncSlot()
    async def _show_import_dialog(self):
        """Show file dialog and import selected document for AI processing"""
        # Get default documents directory
        docs_dir = ConfigManager.get_instance().get_documents_dir()
        logger.debug(f"Opening document import dialog with default dir: {docs_dir}")
        
        # Allow multiple file selection
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Import Documents for AI",
            str(docs_dir),
            "Documents (*.pdf *.docx);;PDF Files (*.pdf);;Word Documents (*.docx)"
        )
        
        if file_paths:
            try:
                # Group files by type and get appropriate parsers
                docx_files = []
                pdf_files = []
                
                for file_path in file_paths:
                    if file_path.lower().endswith('.docx'):
                        docx_files.append(file_path)
                    elif file_path.lower().endswith('.pdf'):
                        pdf_files.append(file_path)
                
                # Process DOCX files
                if docx_files:
                    parser = get_parser(docx_files[0])  # Get DOCX parser
                    if parser:
                        self._connect_progress_tracking(parser.progress)
                        contents = await parser.parse_batch(docx_files)
                        
                        # Show each document in viewer
                        await self._process_document_batch(contents)
                
                # Process PDF files
                if pdf_files:
                    parser = get_parser(pdf_files[0])  # Get PDF parser
                    if parser:
                        self._connect_progress_tracking(parser.progress)
                        contents = await parser.parse_batch(pdf_files) if hasattr(parser, 'parse_batch') else [await parser.parse(f) for f in pdf_files]
                        
                        # Show each document in viewer
                        await self._process_document_batch(contents)
                
                logger.info(f"Successfully processed {len(file_paths)} documents")
                
            except Exception as e:
                logger.error(f"Failed to import documents: {e}")
                self._on_processing_error(str(e))

    async def _process_document_batch(self, contents: List[DocumentContent]) -> None:
        """Process a batch of documents with analysis"""
        try:
            # Analyze each document
            for content in contents:
                if not content:
                    continue
                    
                # Analyze document structure
                analysis = analyze_document_structure(content)
                
                # Create extracted content with analysis
                extracted = ExtractedContent(
                    text=content.raw_content if isinstance(content.raw_content, str) else None,
                    source=content,
                    structure=getattr(content, 'structure', None),
                    metadata={
                        **content.metadata,
                        'analysis': analysis
                    }
                )
                
                # Show in viewer
                panel_type = "Document Viewer"
                panel_id = f"document_viewer_{content.file_path.stem}"
                if get_registry().ensure_panel_exists(self.window(), panel_type, panel_id):
                    viewer = self.window().panel_manager.panels[panel_id]
                    viewer.display_content(extracted)
                
                # Add to current batch
                self.current_batch.append(content)
            
            # Find relationships if we have multiple documents
            if len(self.current_batch) > 1:
                relationships = find_cross_document_relationships(self.current_batch)
                if relationships:
                    logger.info(f"Found {len(relationships)} relationships between documents")
                    # TODO: Display relationships in UI
        
        except Exception as e:
            logger.error(f"Error processing document batch: {e}")
            self._on_processing_error(str(e))

    @asyncSlot()
    async def _show_view_dialog(self):
        """Show dialog to view saved documents"""
        docs_dir = ConfigManager.get_instance().get_documents_dir()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "View Document",
            str(docs_dir),
            "Text Files (*.txt)"
        )
        
        if file_path:
            logger.debug(f"Selected file to view: {file_path}")
            path = Path(file_path)
            text = path.read_text(encoding='utf-8')
            logger.debug(f"Read text content, length: {len(text)}")
            
            # Create extracted content with source info
            source = DocumentContent(
                raw_content=text,
                file_type="txt",
                file_path=path
            )
            
            extracted = ExtractedContent(
                text=text,
                metadata={'file_path': str(path)},
                source=source
            )
            
            # Create or get existing viewer through registry
            panel_id = f"document_viewer_{path.stem}"
            logger.debug(f"Creating/getting viewer with ID: {panel_id}")
            
            if window := self.window():
                viewer = get_registry().create_panel(
                    panel_type="Document Viewer",
                    panel_id=panel_id,
                    content=extracted
                )
                
                if viewer:
                    window.create_panel(panel=viewer, name="Document Viewer")
                else:
                    logger.error("Failed to create document viewer panel")
            else:
                logger.error("No window available for panel creation")

# Register panel factories
registry = get_registry()
registry.register("Properties", lambda: PropertiesPanel())
registry.register("Console", lambda: ConsolePanel())
