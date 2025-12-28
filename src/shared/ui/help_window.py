"""
The Akaschic Archive (Help Window).

A dual-pane documentation viewer resembling classic compiled help (.chm).
"""
import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTextBrowser, QLineEdit,
    QPushButton, QTabWidget, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction, QKeySequence

from ..services.help_service import HelpService, HelpTopic

logger = logging.getLogger(__name__)

class HelpWindow(QMainWindow):
    """The Akaschic Archive: Central Documentation Viewer."""
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Akaschic Archive")
        self.resize(1000, 700)
        
        # Initialize Librarian
        self.service = HelpService()
        self.service.index_content()
        
        # UI Setup
        self._setup_ui()
        self._load_toc()
        
        # Load home page if available
        self._load_topic("manual/index.md")

    def _setup_ui(self):
        """Build the dual-pane layout."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Toolbar
        toolbar = self._create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Splitter (The Book Binding)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background: #cbd5e1; }")
        
        # Left Pane: Navigation
        self.nav_pane = QTabWidget()
        self.nav_pane.setStyleSheet("""
            QTabWidget::pane { border: none; border-right: 1px solid #e2e8f0; }
            QTabBar::tab { padding: 8px 12px; }
        """)
        
        # Tab 1: Contents
        self.toc_tree = QTreeWidget()
        self.toc_tree.setHeaderHidden(True)
        self.toc_tree.itemClicked.connect(self._on_topic_clicked)
        self.nav_pane.addTab(self.toc_tree, "Contents")
        
        # Tab 2: Search
        search_widget = QWidget()
        search_layout = QVBoxLayout(search_widget)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search the archives...")
        self.search_input.returnPressed.connect(self._on_search)
        search_layout.addWidget(self.search_input)
        
        self.search_results = QTreeWidget()
        self.search_results.setHeaderHidden(True)
        self.search_results.itemClicked.connect(self._on_search_result_clicked)
        search_layout.addWidget(self.search_results)
        
        self.nav_pane.addTab(search_widget, "Search")
        
        splitter.addWidget(self.nav_pane)
        
        # Right Pane: The Reader
        self.viewer = QTextBrowser()
        self.viewer.setOpenExternalLinks(False)
        self.viewer.anchorClicked.connect(self._on_anchor_clicked)
        self.viewer.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                color: #1e293b;
                padding: 24px;
                border: none;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        splitter.addWidget(self.viewer)
        
        # Set initial sizes
        splitter.setSizes([300, 700])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        
        main_layout.addWidget(splitter)

    def _create_toolbar(self) -> QFrame:
        """Create navigation toolbar."""
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet("background: #f8fafc; border-bottom: 1px solid #e2e8f0;")
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(12, 0, 12, 0)
        
        title = QLabel("✦ Akaschic Guidance")
        title.setStyleSheet("font-weight: bold; color: #475569;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Simple Back/Forward could be implemented here
        
        return toolbar

    def _load_toc(self):
        """Populate the table of contents."""
        self.toc_tree.clear()
        
        def add_nodes(topics, parent_item):
            """
            Add nodes logic.
            
            Args:
                topics: Description of topics.
                parent_item: Description of parent_item.
            
            """
            for topic in topics:
                item = QTreeWidgetItem(parent_item)
                item.setText(0, topic.title)
                item.setData(0, Qt.ItemDataRole.UserRole, topic.id)
                
                # Icon
                if topic.is_category:
                    item.setIcon(0, QIcon.fromTheme("folder"))
                else:
                    item.setIcon(0, QIcon.fromTheme("text-x-generic"))
                
                if topic.children:
                    add_nodes(topic.children, item)
                    
        root_topics = self.service.get_toc()
        add_nodes(root_topics, self.toc_tree)
        self.toc_tree.expandToDepth(0)

    def _on_topic_clicked(self, item, column):
        """Handle TOC selection."""
        topic_id = item.data(0, Qt.ItemDataRole.UserRole)
        if topic_id:
            logger.debug(f"Loading topic: {topic_id}")
            self._load_topic(topic_id)
            
    def _load_topic(self, relative_path: str):
        """Render markdown content to the viewer."""
        raw_md = self.service.get_content(relative_path)
        
        # Use native Qt Markdown rendering
        self.viewer.setMarkdown(raw_md)
        
        # Note: Qt's markdown parser is basic but sufficient for now.
        # It respects the widget's styleSheet for fonts and colors.

    def _on_search(self):
        """Execute search."""
        query = self.search_input.text().strip()
        if not query:
            return
            
        self.search_results.clear()
        results = self.service.search(query)
        
        for title, path, snippet in results:
            item = QTreeWidgetItem(self.search_results)
            item.setText(0, title)
            item.setToolTip(0, snippet)
            item.setData(0, Qt.ItemDataRole.UserRole, path)
            
    def _on_search_result_clicked(self, item, column):
        """Load search result."""
        path = item.data(0, Qt.ItemDataRole.UserRole)
        if path:
            self._load_topic(path)
            
    def _on_anchor_clicked(self, url):
        """Handle internal links."""
        # Simple handling for now
        path = url.toString()
        if not path.startswith("http"):
             self._load_topic(path)