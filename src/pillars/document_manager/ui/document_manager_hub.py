"""Document Manager pillar hub - launcher interface for document tools."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QGridLayout, QGraphicsDropShadowEffect, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from shared.ui import WindowManager
from pillars.document_manager.services.document_service import document_service_context
from .document_editor_window import DocumentEditorWindow
from .document_library import DocumentLibrary
from .document_search_window import DocumentSearchWindow
from .mindscape_window import MindscapeWindow
from .database_manager import DatabaseManagerWindow


class DocumentManagerHub(QWidget):
    """Hub widget for Document Manager pillar - displays available tools."""
    
    def __init__(self, window_manager: WindowManager):
        """
        Initialize the Document Manager hub.
        
        Args:
            window_manager: Shared window manager instance
        """
        super().__init__()
        self.window_manager = window_manager
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the hub interface."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 32, 40, 40)

        # Header section
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Documents")
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 32pt;
                font-weight: 700;
                letter-spacing: -1px;
            }
        """)
        header_layout.addWidget(title_label)

        desc_label = QLabel("Create, organize, and analyze your texts and manuscripts")
        desc_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12pt;
            }
        """)
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header)

        # Tools grid
        tools = [
            ("📝", "New Document", "Create a new rich text document", "#3b82f6", self._open_document_editor),
            ("📚", "The Akaschic Record", "Browse and manage your documents", "#10b981", self._open_document_library),
            ("🔍", "Search", "Full-text search across all documents", "#8b5cf6", self._open_document_search),
            ("🧠", "Mindscape", "The Living Graph - visual connections", "#06b6d4", self._open_mindscape),
            ("🛠️", "Database Admin", "Stats, maintenance, and cleanup", "#f59e0b", self._open_database_manager),
        ]

        grid = QGridLayout()
        grid.setSpacing(16)
        
        for i, (icon, title, desc, color, callback) in enumerate(tools):
            card = self._create_tool_card(icon, title, desc, color, callback)
            grid.addWidget(card, i // 2, i % 2)
        
        layout.addLayout(grid)
        
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _create_tool_card(self, icon: str, title: str, description: str, accent_color: str, callback) -> QFrame:
        """Create a modern tool card."""
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 0;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f5f9);
                border-color: {accent_color};
            }}
        """)
        card.setMinimumSize(240, 150)
        card.setMaximumHeight(180)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 25))
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(8)
        
        icon_container = QLabel(icon)
        icon_container.setFixedSize(48, 48)
        icon_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.setStyleSheet(f"""
            QLabel {{
                background: {accent_color}20;
                border-radius: 10px;
                font-size: 22pt;
            }}
        """)
        card_layout.addWidget(icon_container)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 14pt;
                font-weight: 600;
                background: transparent;
            }
        """)
        card_layout.addWidget(title_label)
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 9pt;
                background: transparent;
            }
        """)
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)
        
        card_layout.addStretch()
        
        card.mousePressEvent = lambda e: callback()
        
        return card
        
    def _open_document_library(self):
        """Open the document library window."""
        window = self.window_manager.open_window(
            "document_library",
            DocumentLibrary,
            allow_multiple=False
        )
        
        # Connect signal safely
        if isinstance(window, DocumentLibrary):
            try:
                window.document_opened.disconnect(self._on_library_document_opened)
            except TypeError:
                pass
            window.document_opened.connect(self._on_library_document_opened)
        
    def _open_document_editor(self):
        """Open the document editor window."""
        self.window_manager.open_window(
            "document_editor",
            DocumentEditorWindow
        )

    def _open_document_search(self):
        """Open the document search window."""
        window = self.window_manager.open_window(
            "document_search",
            DocumentSearchWindow,
            allow_multiple=False
        )
        
        if isinstance(window, DocumentSearchWindow):
            try:
                window.document_opened.disconnect(self._open_document_by_id)
            except TypeError:
                pass
            window.document_opened.connect(self._open_document_by_id)

    def _open_mindscape(self):
        """Open the mindscape window."""
        self.window_manager.open_window(
            "mindscape",
            MindscapeWindow,
            allow_multiple=False
        )
    def _open_database_manager(self):
        """Open the database manager window."""
        self.window_manager.open_window(
            "database_manager",
            DatabaseManagerWindow,
            allow_multiple=False
        )



    def _open_document_from_library(self, doc, search_term=None, restored_html=None, read_only=False):
        """Open a document from the library in the editor."""
        window = self.window_manager.open_window(
            "document_editor",
            DocumentEditorWindow
        )
        if isinstance(window, DocumentEditorWindow):
            window.load_document_model(doc, search_term, restored_html, read_only)

    def _on_library_document_opened(self, doc, restored_html):
        """Handle document_opened signal from library (doc, restored_html)."""
        # From library = edit mode (read_only=False)
        self._open_document_from_library(doc, None, restored_html, read_only=False)

    def _open_document_by_id(self, doc_id, search_term=None):
        """Open a document by ID in the editor."""
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Attempting to open document ID: {doc_id}")
        
        try:
            with document_service_context() as service:
                # Use the new method that restores images
                result = service.get_document_with_images(doc_id)
                
                if result:
                    doc, restored_html = result
                    logger.debug(f"Document loaded: '{doc.title}', html_len={len(restored_html)}")
                    # Open the document from search = read-only mode
                    self._open_document_from_library(doc, search_term, restored_html, read_only=True)
                else:
                    # Document not found in DB - might be stale search index
                    from PyQt6.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        None,
                        "Document Not Found",
                        f"Document ID {doc_id} was not found in the database.\n\n"
                        "The search index may be out of sync. Try rebuilding it from the Library."
                    )
                    logger.warning(f"Document {doc_id} not found - search index may be stale")
        except Exception as e:
            import traceback
            logger.error(f"Error opening document {doc_id}: {e}")
            traceback.print_exc()

