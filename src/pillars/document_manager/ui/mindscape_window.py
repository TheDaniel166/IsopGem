"""
Mindscape Window - The Knowledge Tree.
OneNote-style main window with tree navigation and page editor in a split layout.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout, QLineEdit, 
    QStackedWidget, QListWidget, QListWidgetItem, QHBoxLayout,
    QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QTimer
import qtawesome as qta
from .mindscape_tree import MindscapeTreeWidget
from .mindscape_page import MindscapePageWidget
from typing import Optional
from ..services.notebook_service import notebook_service_context

class SearchResultWidget(QWidget):
    """
    Custom widget for rendering a search result with distinct styling.
    Title (Blue/Bold)
    Path (Slate/Small)
    Snippet (Gray/Monospace)
    """
    def __init__(self, title: str, path: str, snippet: str, parent=None):
        """
          init   logic.
        
        Args:
            title: Description of title.
            path: Description of path.
            snippet: Description of snippet.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        # Transparent background to allow QListWidget selection highlight to show through?
        # QListWidget typically paints selection on the item background.
        # If this widget is opaque, it covers it.
        # We set transparent background.
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True) # Pass clicks to Item
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # Title
        lbl_title = QLabel(title)
        # Tailwind-like colors: Blue-400
        lbl_title.setStyleSheet("color: #60a5fa; font-weight: bold; font-size: 13px; background: transparent;")
        layout.addWidget(lbl_title)
        
        # Path
        lbl_path = QLabel(path)
        # Slate-400
        lbl_path.setStyleSheet("color: #94a3b8; font-size: 11px; background: transparent;")
        layout.addWidget(lbl_path)
        
        # Snippet
        lbl_snippet = QLabel(snippet)
        # Slate-300, monospace
        lbl_snippet.setStyleSheet("color: #cbd5e1; font-family: monospace; font-size: 12px; background: transparent;")
        lbl_snippet.setWordWrap(True)
        lbl_snippet.setMaximumHeight(60) # Limit height (approx 3 lines) -> ellide handling is manual usually but wrap is ok
        layout.addWidget(lbl_snippet)

class MindscapeWindow(QMainWindow):
    """
    Revised Mindscape Window (OneNote Style).
    Splitter: [Sidebar (Search + Tree)] | [Page Editor]
    """
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        Returns:
            Result of __init__ operation.
        """
        super().__init__(parent)
        self.setWindowTitle("Mindscape: The Knowledge Tree")
        self.resize(1200, 800)
        
        # Central Widget & Layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self.splitter)
        
        # --- Sidebar Container ---
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setMinimumWidth(250)
        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # 1. Search Bar
        search_container = QWidget()
        search_container.setObjectName("SearchContainer")
        # Apply some styling
        search_container.setStyleSheet("""
            #SearchContainer {
                background-color: #1e293b;
                border-bottom: 1px solid #334155;
            }
            QLineEdit {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 4px;
                padding: 4px;
                color: #e2e8f0;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(8, 8, 8, 8)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Notebooks...")
        self.search_input.setClearButtonEnabled(True)
        search_layout.addWidget(self.search_input)
        
        sidebar_layout.addWidget(search_container)
        
        # 2. Stacked Content (Tree vs Results)
        self.sidebar_stack = QStackedWidget()
        sidebar_layout.addWidget(self.sidebar_stack)
        
        # View 0: Tree
        self.tree = MindscapeTreeWidget()
        self.sidebar_stack.addWidget(self.tree)
        
        # View 1: Search Results
        self.results_widget = QWidget()
        res_layout = QVBoxLayout(self.results_widget)
        res_layout.setContentsMargins(0, 0, 0, 0)
        
        self.results_header = QLabel("Search Results")
        self.results_header.setStyleSheet("padding: 4px; font-weight: bold; color: #94a3b8;")
        res_layout.addWidget(self.results_header)
        
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                border: none;
                background-color: #0f172a;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #1e293b;
            }
            QListWidget::item:selected {
                background-color: #1e293b;
            }
        """)
        res_layout.addWidget(self.results_list)
        
        self.sidebar_stack.addWidget(self.results_widget)
        
        # Add sidebar to splitter
        self.splitter.addWidget(self.sidebar_widget)
        
        # Right: Page
        self.page = MindscapePageWidget()
        self.splitter.addWidget(self.page)
        
        # Setup Splitter Ratios
        self.splitter.setCollapsible(0, False)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([350, 850])
        
        # --- Logic Connections ---
        self.tree.page_selected.connect(self.page.load_node)
        
        # Search Logic
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(300) # Debounce 300ms
        
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_timer.timeout.connect(self._perform_search)
        self.results_list.itemClicked.connect(self._on_result_clicked)
        
        # Initial State
        self.page.clear()

    def _on_search_text_changed(self, text: str) -> None:
        if not text:
            # Show Tree
            self.sidebar_stack.setCurrentIndex(0)
            return
            
        # Reset timer
        self.search_timer.start()

    def _perform_search(self) -> None:
        text = self.search_input.text()
        if len(text) < 2:
            return
            
        self.sidebar_stack.setCurrentIndex(1) # Show Results
        self.results_list.clear()
        self.results_header.setText("Searching...")
        
        try:
            with notebook_service_context() as svc:
                results = svc.search_global(text)
                
            self.results_header.setText(f"Found {len(results)} matches")
            
            for res in results:
                item = QListWidgetItem()
                
                # Custom widget for rendering
                widget = SearchResultWidget(
                    res.title, 
                    f"{res.notebook_name} > {res.section_name}", 
                    res.snippet
                )
                
                # Must set size hint for the item to accommodate the widget
                item.setSizeHint(widget.sizeHint())
                
                # Store data on item
                item.setData(Qt.ItemDataRole.UserRole, res.page_id)
                item.setData(Qt.ItemDataRole.UserRole + 1, text) 
                
                self.results_list.addItem(item)
                self.results_list.setItemWidget(item, widget)
                
        except Exception as e:
            self.results_header.setText(f"Error: {e}")

    def _on_result_clicked(self, item: QListWidgetItem) -> None:
        page_id = item.data(Qt.ItemDataRole.UserRole)
        query = item.data(Qt.ItemDataRole.UserRole + 1)
        
        if page_id:
            # Load page, but do NOT reset scroll (let highlight handle it)
            self.page.load_node(page_id, reset_scroll=False)
            
            # Trigger highlight
            # We need to wait for load to finish. mindscape_page.load_node is synchronous (mostly),
            # but setting HTML might take a moment to be indexable.
            # Ideally we add a method to MindscapePageWidget to find_and_highlight
            if hasattr(self.page, "highlight_search_term"):
                self.page.highlight_search_term(query)
            elif hasattr(self.page, "active_editor") and self.page.active_editor:
                 # Fallback direct access if method not yet added
                 wrapper = self.page._get_active_wrapper()
                 if wrapper and wrapper.editor:
                     # Use our robust search feature
                     wrapper.editor.search_feature.find_next(query, False, False)