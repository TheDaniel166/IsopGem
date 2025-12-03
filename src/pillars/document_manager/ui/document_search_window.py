"""Document Search Window."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal
from pillars.document_manager.services.document_service import document_service_context

class DocumentSearchWindow(QMainWindow):
    """Window for advanced document search with highlighting."""
    
    document_opened = pyqtSignal(int, str) # Emits (Document ID, Search Query)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Document Search")
        self.resize(900, 700)
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self._setup_ui()
        
        # Initial focus
        self.search_input.setFocus()

    def _setup_ui(self):
        layout = QVBoxLayout(self.central_widget)
        
        # Search Bar
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search terms...")
        self.search_input.returnPressed.connect(self._perform_search)
        search_layout.addWidget(self.search_input)
        
        self.btn_search = QPushButton("Search")
        self.btn_search.clicked.connect(self._perform_search)
        search_layout.addWidget(self.btn_search)
        
        layout.addLayout(search_layout)
        
        # Help Text
        help_label = QLabel(
            "Tip: Use '*' for wildcards (e.g. 'gem*'), 'AND/OR' for logic, and quotes for phrases."
        )
        help_label.setStyleSheet("color: #666; font-style: italic; font-size: 10pt;")
        layout.addWidget(help_label)
        
        # Results Label
        self.lbl_status = QLabel("Ready")
        layout.addWidget(self.lbl_status)
        
        # Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Title", "Snippet", "Created"])
        
        header = self.table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)
        
        # Enable HTML rendering in cells (via delegate or just setting text format? 
        # QTableWidgetItem doesn't support HTML directly easily without a delegate, 
        # but we can use a QLabel as a cell widget for the snippet)
        
        layout.addWidget(self.table)

    def _perform_search(self):
        query = self.search_input.text().strip()
        if not query:
            return
            
        self.lbl_status.setText("Searching...")
        self.table.setRowCount(0)
        
        try:
            with document_service_context() as service:
                results = service.search_documents_with_highlights(query)
            
            self.lbl_status.setText(f"Found {len(results)} results.")
            
            for r in results:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # Title
                title_item = QTableWidgetItem(r['title'])
                title_item.setData(Qt.ItemDataRole.UserRole, r['id'])
                self.table.setItem(row, 0, title_item)
                
                # Snippet (using QLabel for HTML support)
                snippet_label = QLabel(f"<html><body>{r['highlights']}</body></html>")
                snippet_label.setWordWrap(True)
                snippet_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
                snippet_label.setStyleSheet("padding: 5px;")
                self.table.setCellWidget(row, 1, snippet_label)
                
                # Created
                created_item = QTableWidgetItem(str(r['created_at']))
                self.table.setItem(row, 2, created_item)
                
            self.table.resizeRowsToContents()
            
        except Exception as e:
            self.lbl_status.setText(f"Error: {str(e)}")

    def _on_row_double_clicked(self, row, col):
        item = self.table.item(row, 0)
        if item is None:
            return
        
        doc_id = item.data(Qt.ItemDataRole.UserRole)
        query = self.search_input.text().strip()
        self.document_opened.emit(doc_id, query)
