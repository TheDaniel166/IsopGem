"""Document Manager pillar hub - launcher interface for document tools."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from shared.ui import WindowManager
from shared.database import get_db
from pillars.document_manager.services.document_service import DocumentService
from .document_editor_window import DocumentEditorWindow
from .document_library import DocumentLibrary
from .document_search_window import DocumentSearchWindow
from .graph_view import GraphWindow


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
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Document Manager Pillar")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Analysis and organization of texts and documents"
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_font = QFont()
        desc_font.setPointSize(12)
        desc_label.setFont(desc_font)
        desc_label.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(desc_label)
        
        # Tools Section
        tools_layout = QVBoxLayout()
        tools_layout.setSpacing(15)
        
        # Document Editor Button
        editor_btn = QPushButton("New Document")
        editor_btn.setMinimumHeight(50)
        editor_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        editor_btn.clicked.connect(self._open_document_editor)
        tools_layout.addWidget(editor_btn)
        
        # Document Library Button
        lib_btn = QPushButton("Document Library")
        lib_btn.setMinimumHeight(50)
        lib_btn.setStyleSheet("""
            QPushButton {
                background-color: #059669;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #047857;
            }
        """)
        lib_btn.clicked.connect(self._open_document_library)
        tools_layout.addWidget(lib_btn)
        
        # Search Button
        search_btn = QPushButton("Search Documents")
        search_btn.setMinimumHeight(50)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #7c3aed;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #6d28d9;
            }
        """)
        search_btn.clicked.connect(self._open_document_search)
        tools_layout.addWidget(search_btn)

        # Graph View Button
        graph_btn = QPushButton("Knowledge Graph")
        graph_btn.setMinimumHeight(50)
        graph_btn.setStyleSheet("""
            QPushButton {
                background-color: #db2777;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #be185d;
            }
        """)
        graph_btn.clicked.connect(self._open_graph_view)
        tools_layout.addWidget(graph_btn)
        
        layout.addLayout(tools_layout)
        
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
                window.document_opened.disconnect(self._open_document_from_library)
            except TypeError:
                pass
            window.document_opened.connect(self._open_document_from_library)
        
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

    def _open_graph_view(self):
        """Open the knowledge graph window."""
        window = self.window_manager.open_window(
            "knowledge_graph",
            GraphWindow,
            allow_multiple=False
        )
        
        if isinstance(window, GraphWindow):
            try:
                window.document_opened.disconnect(self._open_document_by_id)
            except TypeError:
                pass
            window.document_opened.connect(self._open_document_by_id)

    def _open_document_from_library(self, doc, search_term=None):
        """Open a document from the library in the editor."""
        window = self.window_manager.open_window(
            "document_editor",
            DocumentEditorWindow
        )
        if isinstance(window, DocumentEditorWindow):
            window.load_document_model(doc, search_term)

    def _open_document_by_id(self, doc_id, search_term=None):
        """Open a document by ID in the editor."""
        try:
            db = next(get_db())
            service = DocumentService(db)
            doc = service.get_document(doc_id)
            if doc:
                self._open_document_from_library(doc, search_term)
        except Exception as e:
            print(f"Error opening document {doc_id}: {e}")

