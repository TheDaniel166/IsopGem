"""
Search Results Panel - The Librarian's List.
Side panel displaying search results with add-to-graph and open-document actions.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
    QLabel, QPushButton, QHBoxLayout, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QBrush

class SearchResultsPanel(QWidget):
    """
    Side panel to display search results stored in a concept node.
    Allows user to selectively add documents to the graph.
    """
    add_to_graph_requested = pyqtSignal(dict) # Emits the result dict
    open_document_requested = pyqtSignal(int) # Emits doc_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        self.header = QLabel("Search Results")
        self.header.setStyleSheet("font-size: 14px; font-weight: bold; color: #cbd5e1; padding: 10px;")
        self.layout.addWidget(self.header)
        
        # List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #1e293b;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background-color: #334155;
                color: #e2e8f0;
                padding: 10px;
                margin: 5px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #475569;
                border: 1px solid #64748b;
            }
            QListWidget::item:hover {
                background-color: #475569;
            }
        """)
        self.list_widget.setWordWrap(True)
        self.list_widget.itemDoubleClicked.connect(self._on_double_click)
        self.layout.addWidget(self.list_widget)
        
        # Context Menu
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        
        self._current_results = []

    def load_results(self, results: list, term: str = None):
        """
        Populate the list with search results.
        results: List of dicts {'id', 'title', 'highlights', ...}
        """
        self.list_widget.clear()
        self._current_results = results
        self.header.setText(f"Search Results ({len(results)})")
        
        if not results:
            self.list_widget.addItem("No results found.")
            return

        for res in results:
            item = QListWidgetItem()
            
            # Create Custom Widget container
            widget = QWidget()
            w_layout = QVBoxLayout(widget)
            w_layout.setContentsMargins(5, 5, 5, 5)
            w_layout.setSpacing(2)
            
            # Title Label
            title_text = res.get('title', 'Untitled')
            title_label = QLabel(title_text)
            title_label.setStyleSheet("font-weight: bold; color: #e2e8f0; font-size: 14px;")
            w_layout.addWidget(title_label)
            
            # Snippet Label (Rich Text)
            raw_snippet = res.get('highlights', 'No preview available.')
            
            # Cleanse snippet logic:
            # 1. Replace the specific whoosh class with standard bold
            import re
            # Regex to catch <b class="match term0"> etc and replace with <b>
            clean_snippet = re.sub(r'<b class="[^"]+">', '<b>', raw_snippet)
            
            snippet_label = QLabel(clean_snippet)
            snippet_label.setWordWrap(True)
            snippet_label.setTextFormat(Qt.TextFormat.RichText)
            snippet_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
            w_layout.addWidget(snippet_label)
            
            # Set size hint for item
            # We need to ensure the item has enough height. 
            # Since WordWrap is dynamic, this is tricky in QListWidget.
            # But setItemWidget usually handles it if the list resize mode is Adjust.
            
            item.setSizeHint(widget.sizeHint())
            
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            
            # Inject term for downstream use
            if term:
                res['search_term'] = term
            item.setData(Qt.ItemDataRole.UserRole, res)

    def _on_double_click(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.add_to_graph_requested.emit(data)

    def _show_context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item: return
        
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data: return
        
        menu = QMenu(self)
        add_action = menu.addAction("Add to Mindscape")
        open_action = menu.addAction("Open Document")
        
        action = menu.exec(self.list_widget.mapToGlobal(pos))
        
        if action == add_action:
            self.add_to_graph_requested.emit(data)
        elif action == open_action:
            self.open_document_requested.emit(data['id'])
