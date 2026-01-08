"""
The Esoteric Wisdom Window (The Temple of Sacred Forms).

A dedicated window for browsing and searching the esoteric meanings
of geometric forms, following the Visual Liturgy principles.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTreeWidget, QTreeWidgetItem, QScrollArea, QLineEdit,
    QSplitter, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont

from shared.ui import WindowManager
from ..services.esoteric_wisdom_service import get_esoteric_wisdom_service


class EsotericWisdomWindow(QWidget):
    """Window for browsing the Esoteric Wisdom of Sacred Geometry."""
    
    def __init__(self, window_manager: WindowManager = None, **kwargs):  # type: ignore[reportArgumentType, reportMissingParameterType, reportUnknownParameterType]
        """
          init   logic.
        
        Args:
            window_manager: Description of window_manager.
        
        """
        super().__init__()
        self.window_manager = window_manager
        self.service = get_esoteric_wisdom_service()
        self._setup_ui()
        self._populate_toc()
    
    def _setup_ui(self):
        """Set up the window interface."""
        self.setWindowTitle("The Esoteric Wisdom • Sacred Geometry Oracle")
        self.setMinimumSize(1000, 700)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        main_layout.addWidget(header)
        
        # Content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #e2e8f0; width: 1px; }")
        
        # Left panel - TOC
        left_panel = self._create_toc_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Content
        right_panel = self._create_content_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([300, 700])
        main_layout.addWidget(splitter)
    
    def _create_header(self) -> QWidget:
        """Create the header with title and search."""
        header = QFrame()
        header.setMaximumHeight(56)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1b4b, stop:1 #312e81);
                border-bottom: 1px solid #4c1d95;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(16)
        
        title = QLabel("The Esoteric Wisdom")
        title.setStyleSheet("""
            QLabel {
                color: #f8fafc;
                font-size: 16pt;
                font-weight: 700;
                font-family: 'Cinzel', serif;
                background: transparent;
            }
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search the sacred scrolls...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #a78bfa;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 10pt;
                color: #0f172a;
            }
            QLineEdit:focus {
                border-color: #8b5cf6;
            }
        """)
        self.search_input.returnPressed.connect(self._on_search)
        layout.addWidget(self.search_input)
        
        search_btn = QPushButton("🔮 Seek")
        search_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        search_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #8b5cf6, stop:1 #7c3aed);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 7px 14px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #a78bfa, stop:1 #8b5cf6);
            }
        """)
        search_btn.clicked.connect(self._on_search)
        layout.addWidget(search_btn)
        
        return header
    
    def _create_toc_panel(self) -> QWidget:
        """Create the Table of Contents panel."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-right: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # TOC Header
        toc_header = QLabel("📜 Sacred Forms")
        toc_header.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 13pt;
                font-weight: 700;
                padding: 16px;
                background: #f1f5f9;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        layout.addWidget(toc_header)
        
        # Tree widget
        self.toc_tree = QTreeWidget()
        self.toc_tree.setHeaderHidden(True)
        self.toc_tree.setStyleSheet("""
            QTreeWidget {
                background: transparent;
                border: none;
                font-size: 10pt;
            }
            QTreeWidget::item {
                padding: 6px 8px;
                border-radius: 6px;
                margin: 2px 8px;
            }
            QTreeWidget::item:selected {
                background: #8b5cf620;
                color: #5b21b6;
            }
            QTreeWidget::item:hover {
                background: #f1f5f9;
            }
            QTreeWidget::branch {
                background: transparent;
            }
        """)
        self.toc_tree.itemClicked.connect(self._on_topic_selected)
        layout.addWidget(self.toc_tree)
        
        return panel
    
    def _create_content_panel(self) -> QWidget:
        """Create the content display panel."""
        panel = QFrame()
        panel.setStyleSheet("QFrame { background-color: #ffffff; }")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        # Content container
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: #ffffff;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(32, 24, 32, 32)
        self.content_layout.setSpacing(20)
        
        # Welcome message
        welcome = QLabel("Select a sacred form to reveal its wisdom...")
        welcome.setStyleSheet("""
            QLabel {
                color: #94a3b8;
                font-size: 14pt;
                font-style: italic;
                padding: 60px;
            }
        """)
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(welcome)
        self.content_layout.addStretch()
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
        
        return panel
    
    def _populate_toc(self):
        """Populate the Table of Contents tree."""
        self.toc_tree.clear()
        
        toc = self.service.get_toc()
        
        for category_name, topics in toc:
            # Category item
            cat_item = QTreeWidgetItem([f"📁 {category_name}"])
            cat_item.setData(0, Qt.ItemDataRole.UserRole, None)  # No direct content
            cat_item.setExpanded(True)
            
            font = cat_item.font(0)
            font.setBold(True)
            cat_item.setFont(0, font)
            
            for topic in topics:
                # Topic item
                icon = "⭐" if topic.has_stellations else "◆"
                topic_item = QTreeWidgetItem([f"{icon} {topic.id}"])
                topic_item.setData(0, Qt.ItemDataRole.UserRole, topic.id)
                topic_item.setToolTip(0, topic.title)
                cat_item.addChild(topic_item)
            
            self.toc_tree.addTopLevelItem(cat_item)
    
    def _on_topic_selected(self, item: QTreeWidgetItem, column: int):
        """Handle topic selection."""
        shape_name = item.data(0, Qt.ItemDataRole.UserRole)
        if shape_name:
            self._display_content(shape_name)
    
    def _on_search(self):
        """Handle search."""
        query = self.search_input.text().strip()
        if not query:
            return
        
        results = self.service.search(query)
        self._display_search_results(query, results)
    
    def _display_search_results(self, query: str, results: list):
        """Display search results."""
        self._clear_content()
        
        # Header
        header = QLabel(f"Search Results for '{query}'")
        header.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 18pt;
                font-weight: 700;
                padding-bottom: 16px;
                border-bottom: 2px solid #8b5cf6;
            }
        """)
        self.content_layout.addWidget(header)
        
        if not results:
            empty = QLabel("No wisdom found for this query.")
            empty.setStyleSheet("color: #94a3b8; font-size: 12pt; font-style: italic;")
            self.content_layout.addWidget(empty)
        else:
            for shape_name, title, snippet in results:  # type: ignore[reportUnknownVariableType]
                result_card = self._create_result_card(shape_name, title, snippet)  # type: ignore[reportUnknownArgumentType]
                self.content_layout.addWidget(result_card)
        
        self.content_layout.addStretch()
    
    def _create_result_card(self, shape_name: str, title: str, snippet: str) -> QFrame:
        """Create a search result card."""
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 16px;
            }
            QFrame:hover {
                border-color: #8b5cf6;
                background: #faf5ff;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        
        name_label = QLabel(shape_name)
        name_label.setStyleSheet("color: #5b21b6; font-size: 13pt; font-weight: 700;")
        layout.addWidget(name_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #7c3aed; font-size: 11pt; font-style: italic;")
        layout.addWidget(title_label)
        
        snippet_label = QLabel(snippet)
        snippet_label.setWordWrap(True)
        snippet_label.setStyleSheet("color: #64748b; font-size: 10pt;")
        layout.addWidget(snippet_label)
        
        card.mousePressEvent = lambda e: self._display_content(shape_name)
        
        return card
    
    def _display_content(self, shape_name: str):
        """Display the full content for a shape."""
        content = self.service.get_content(shape_name)
        if not content:
            return
        
        self._clear_content()
        
        # Title
        title = content.get('title', shape_name)
        title_label = QLabel(f"◆ {shape_name}")
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 24pt;
                font-weight: 900;
                font-family: 'Cinzel', serif;
            }
        """)
        self.content_layout.addWidget(title_label)
        
        # Esoteric title
        esoteric_title = QLabel(title)
        esoteric_title.setStyleSheet("""
            QLabel {
                color: #7c3aed;
                font-size: 14pt;
                font-style: italic;
                padding-bottom: 16px;
                border-bottom: 1px solid #e2e8f0;
            }
        """)
        self.content_layout.addWidget(esoteric_title)
        
        # Summary
        summary = content.get('summary', '')
        if summary:
            summary_label = QLabel(summary)
            summary_label.setWordWrap(True)
            summary_label.setStyleSheet("""
                QLabel {
                    color: #334155;
                    font-size: 12pt;
                    line-height: 1.6;
                    padding: 16px 0;
                }
            """)
            self.content_layout.addWidget(summary_label)
        
        # Keywords
        keywords = content.get('keywords', [])
        if keywords:
            self._add_section("Keywords", " · ".join(keywords))
        
        # Correspondences
        correspondences = content.get('correspondences', {})
        if correspondences:
            corr_text = "\n".join([f"• {k}: {v}" for k, v in correspondences.items()])
            self._add_section("Correspondences", corr_text)
        
        # Attributes
        attributes = content.get('attributes', {})
        if attributes:
            attr_text = "\n".join([f"• {k}: {v}" for k, v in attributes.items()])
            self._add_section("Geometric Attributes", attr_text)
        
        # Stellations
        stellations = content.get('stellations', {})
        if stellations:
            for key, stell in stellations.items():
                if isinstance(stell, dict):
                    stell_name = stell.get('name', key)
                    stell_desc = stell.get('description', '')
                    stell_magic = stell.get('magical_function', '')
                    stell_text = f"{stell_desc}"
                    if stell_magic:
                        stell_text += f"\n\n🔮 Magical Function: {stell_magic}"
                    self._add_section(f"⭐ {key} — {stell_name}", stell_text, accent="#f59e0b")
        
        # Meditation
        meditation = content.get('meditation', '')
        if meditation:
            self._add_meditation(meditation)
        
        self.content_layout.addStretch()
    
    def _add_section(self, title: str, content: str, accent: str = "#8b5cf6"):
        """Add a content section."""
        section = QFrame()
        section.setStyleSheet(f"""
            QFrame {{
                background: #f8fafc;
                border-left: 4px solid {accent};
                border-radius: 8px;
                padding: 16px;
                margin-top: 8px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setSpacing(8)
        
        header = QLabel(title)
        header.setStyleSheet(f"color: {accent}; font-size: 11pt; font-weight: 700;")
        layout.addWidget(header)
        
        body = QLabel(content)
        body.setWordWrap(True)
        body.setStyleSheet("color: #475569; font-size: 10pt;")
        layout.addWidget(body)
        
        self.content_layout.addWidget(section)
    
    def _add_meditation(self, meditation: str):
        """Add the meditation section with special styling."""
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #faf5ff, stop:1 #f3e8ff);
                border: 1px solid #d8b4fe;
                border-radius: 16px;
                padding: 20px;
                margin-top: 16px;
            }
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(139, 92, 246, 40))
        section.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(section)
        layout.setSpacing(12)
        
        header = QLabel("🕯️ Meditation")
        header.setStyleSheet("""
            QLabel {
                color: #7c3aed;
                font-size: 12pt;
                font-weight: 700;
            }
        """)
        layout.addWidget(header)
        
        body = QLabel(meditation)
        body.setWordWrap(True)
        body.setStyleSheet("""
            QLabel {
                color: #581c87;
                font-size: 11pt;
                font-style: italic;
                line-height: 1.5;
            }
        """)
        layout.addWidget(body)
        
        self.content_layout.addWidget(section)
    
    def _clear_content(self):
        """Clear the content panel."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()