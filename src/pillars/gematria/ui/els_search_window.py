"""TQ Text Sequencer Window - Three-pane interface for ELS searching.

Left: Controls (text source, grid config, search params)
Center: Zoomable letter grid
Right: Clickable search results
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QLineEdit, QSpinBox, QPushButton, QComboBox, QRadioButton,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
    QFileDialog, QMessageBox, QButtonGroup, QFrame, QScrollArea, QTabWidget,
    QCheckBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import List, Optional
import logging

from .els_grid_view import ELSGridView
from ..services.els_service import ELSSearchService, ELSResult
from ..services import TQGematriaCalculator

logger = logging.getLogger(__name__)


# Local style helpers
def _button_style():
    return """
        QPushButton {
            background-color: #f1f5f9;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 8px 16px;
            color: #1e293b;
        }
        QPushButton:hover { background-color: #e2e8f0; }
        QPushButton:pressed { background-color: #cbd5e1; }
    """

def _input_style():
    return """
        QLineEdit, QSpinBox, QComboBox {
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 6px 10px;
            color: #1e293b;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
            border-color: #7C3AED;
        }
    """


class ELSSearchWindow(QMainWindow):
    """
    TQ Text Sequencer Window with 3-pane layout.
    
    - Left pane: Text source, grid configuration, search controls
    - Center pane: Zoomable/pannable letter grid (ELSGridView)
    - Right pane: Clickable search results
    """
    
    def __init__(self, window_manager=None, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager
        self._service = ELSSearchService()
        
        self._stripped_text = ""
        self._position_map = []
        self._current_results: List[ELSResult] = []
        
        self.setWindowTitle("🔮 The Resonant Chain")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Build the 3-pane interface."""
        central = QWidget()
        central.setObjectName("CentralContainer")
        self.setCentralWidget(central)
        
        # Level 0: Background
        import os
        bg_path = os.path.abspath("src/assets/patterns/tq_bg_pattern.png")
        central.setStyleSheet(f"""
            QWidget#CentralContainer {{
                border-image: url("{bg_path}") 0 0 0 0 stretch stretch;
                background-color: #fdfbf7;
            }}
        """)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Main horizontal splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # === LEFT PANE: Controls ===
        left_pane = self._create_left_pane()
        splitter.addWidget(left_pane)
        
        # === CENTER PANE: Grid View ===
        self._grid_view = ELSGridView()
        splitter.addWidget(self._grid_view)
        
        # === RIGHT PANE: Results ===
        right_pane = self._create_right_pane()
        splitter.addWidget(right_pane)
        
        # Set splitter proportions
        splitter.setSizes([280, 700, 320])
        splitter.setStretchFactor(0, 0)  # Left fixed
        splitter.setStretchFactor(1, 1)  # Center stretches
        splitter.setStretchFactor(2, 0)  # Right fixed
        
        main_layout.addWidget(splitter, 1)
        
        # Status bar
        self.statusBar().showMessage("Load a text to begin")
        self.statusBar().setStyleSheet("color: #64748b; font-style: italic;")
    
    def _create_left_pane(self) -> QWidget:
        """Create left control pane with tabs."""
        pane = QWidget()
        pane.setMaximumWidth(300)
        layout = QVBoxLayout(pane)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Style as floating card
        pane.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid #d4c4a8;
                border-radius: 16px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        pane.setGraphicsEffect(shadow)
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #e2e8f0; border-radius: 6px; }
            QTabBar::tab { padding: 8px 12px; margin-right: 2px; }
            QTabBar::tab:selected { background-color: #7C3AED; color: white; border-radius: 4px; }
        """)
        
        # === TAB 1: Source & Grid ===
        source_tab = QWidget()
        source_layout = QVBoxLayout(source_tab)
        source_layout.setSpacing(10)
        
        # Text Source section
        source_layout.addWidget(QLabel("📄 <b>Text Source</b>"))
        
        btn_layout = QHBoxLayout()
        self._btn_load = QPushButton("📁 File")
        self._btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_load.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
                color: white;
                border: 1px solid #b45309;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 700;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #f59e0b);
            }
        """)
        self._btn_load.clicked.connect(self._on_load_document)
        btn_layout.addWidget(self._btn_load)
        
        self._btn_paste = QPushButton("📋 Paste")
        self._btn_paste.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_paste.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
                color: white;
                border: 1px solid #b45309;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 700;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #f59e0b);
            }
        """)
        self._btn_paste.clicked.connect(self._on_paste_text)
        btn_layout.addWidget(self._btn_paste)
        source_layout.addLayout(btn_layout)
        
        self._btn_database = QPushButton("📚 Load from Database")
        self._btn_database.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_database.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
                color: white;
                border: 1px solid #b45309;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 700;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #f59e0b);
            }
        """)
        self._btn_database.clicked.connect(self._on_load_from_database)
        source_layout.addWidget(self._btn_database)
        
        self._letter_count_label = QLabel("Letters: 0")
        self._letter_count_label.setStyleSheet("font-weight: bold; color: #7C3AED;")
        source_layout.addWidget(self._letter_count_label)
        
        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        source_layout.addWidget(sep1)
        
        # Grid Configuration section
        source_layout.addWidget(QLabel("📐 <b>Grid Configuration</b>"))
        
        source_layout.addWidget(QLabel("Available Factors:"))
        self._factors_combo = QComboBox()
        self._factors_combo.setStyleSheet(_input_style())
        self._factors_combo.currentIndexChanged.connect(self._on_factor_selected)
        source_layout.addWidget(self._factors_combo)
        
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("Custom:"))
        self._cols_spin = QSpinBox()
        self._cols_spin.setRange(1, 10000)
        self._cols_spin.setValue(50)
        self._cols_spin.setStyleSheet(_input_style())
        custom_layout.addWidget(self._cols_spin)
        custom_layout.addWidget(QLabel("cols"))
        source_layout.addLayout(custom_layout)
        
        self._btn_apply_grid = QPushButton("Apply Grid")
        self._btn_apply_grid.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_apply_grid.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #7c3aed);
                color: white;
                border: 1px solid #6d28d9;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 700;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #8b5cf6);
            }
        """)
        self._btn_apply_grid.clicked.connect(self._on_apply_grid)
        source_layout.addWidget(self._btn_apply_grid)
        
        source_layout.addStretch()
        tabs.addTab(source_tab, "📄 Source")
        
        # === TAB 2: Search ===
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)
        search_layout.setSpacing(8)
        
        search_layout.addWidget(QLabel("Search Term:"))
        self._term_input = QLineEdit()
        self._term_input.setPlaceholderText("Enter letters to find...")
        self._term_input.setStyleSheet(_input_style())
        search_layout.addWidget(self._term_input)
        
        # Skip mode
        self._skip_group = QButtonGroup()
        
        skip_layout = QHBoxLayout()
        self._exact_radio = QRadioButton("Exact Skip:")
        self._exact_radio.setChecked(True)
        self._skip_group.addButton(self._exact_radio)
        skip_layout.addWidget(self._exact_radio)
        
        self._exact_skip_spin = QSpinBox()
        self._exact_skip_spin.setRange(1, 10000)
        self._exact_skip_spin.setValue(50)
        self._exact_skip_spin.setStyleSheet(_input_style())
        skip_layout.addWidget(self._exact_skip_spin)
        search_layout.addLayout(skip_layout)
        
        range_layout = QHBoxLayout()
        self._range_radio = QRadioButton("Range:")
        self._skip_group.addButton(self._range_radio)
        range_layout.addWidget(self._range_radio)
        
        self._min_skip_spin = QSpinBox()
        self._min_skip_spin.setRange(1, 1000)
        self._min_skip_spin.setValue(1)
        self._min_skip_spin.setStyleSheet(_input_style())
        self._min_skip_spin.setFixedWidth(60)
        range_layout.addWidget(self._min_skip_spin)
        
        range_layout.addWidget(QLabel("to"))
        
        self._max_skip_spin = QSpinBox()
        self._max_skip_spin.setRange(1, 10000)
        self._max_skip_spin.setValue(100)
        self._max_skip_spin.setStyleSheet(_input_style())
        self._max_skip_spin.setFixedWidth(70)
        range_layout.addWidget(self._max_skip_spin)
        search_layout.addLayout(range_layout)
        
        # Sequence mode
        seq_layout = QHBoxLayout()
        self._seq_radio = QRadioButton("Sequence:")
        self._skip_group.addButton(self._seq_radio)
        seq_layout.addWidget(self._seq_radio)
        
        self._seq_combo = QComboBox()
        self._seq_combo.addItems(["Triangular", "Square", "Fibonacci"])
        self._seq_combo.setStyleSheet(_input_style())
        seq_layout.addWidget(self._seq_combo)
        search_layout.addLayout(seq_layout)
        
        # Chain mode
        chain_layout = QHBoxLayout()
        self._chain_radio = QRadioButton("🔗 Chain")
        self._skip_group.addButton(self._chain_radio)
        chain_layout.addWidget(self._chain_radio)
        
        self._chain_reverse_check = QCheckBox("Reverse")
        self._chain_reverse_check.setToolTip("Search backwards for each letter")
        chain_layout.addWidget(self._chain_reverse_check)
        chain_layout.addStretch()
        search_layout.addLayout(chain_layout)
        
        # Direction
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Direction:"))
        self._dir_combo = QComboBox()
        self._dir_combo.addItems(["Both", "Forward", "Reverse"])
        self._dir_combo.setStyleSheet(_input_style())
        dir_layout.addWidget(self._dir_combo)
        search_layout.addLayout(dir_layout)
        
        self._btn_search = QPushButton("🔍 Search")
        self._btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_search.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #7c3aed);
                color: white;
                border: 1px solid #6d28d9;
                border-radius: 6px;
                padding: 10px;
                font-weight: 700;
                font-size: 11pt;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #8b5cf6);
            }
        """)
        self._btn_search.clicked.connect(self._on_search)
        search_layout.addWidget(self._btn_search)
        
        search_layout.addStretch()
        tabs.addTab(search_tab, "🔍 Search")
        
        layout.addWidget(tabs)
        
        # Zoom controls (always visible below tabs)
        zoom_group = QFrame()
        zoom_layout = QHBoxLayout(zoom_group)
        zoom_layout.setContentsMargins(0, 10, 0, 0)
        
        btn_zoom_out = QPushButton("−")
        btn_zoom_out.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_zoom_out.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #475569, stop:1 #334155);
                color: white;
                border: 1px solid #1e293b;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 700;
                min-width: 30px;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #334155, stop:1 #475569);
            }
        """)
        btn_zoom_out.clicked.connect(lambda: self._grid_view.zoom_out())
        zoom_layout.addWidget(btn_zoom_out)
        
        self._zoom_label = QLabel("100%")
        zoom_layout.addWidget(self._zoom_label)
        
        btn_zoom_in = QPushButton("+")
        btn_zoom_in.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_zoom_in.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #475569, stop:1 #334155);
                color: white;
                border: 1px solid #1e293b;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 700;
                min-width: 30px;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #334155, stop:1 #475569);
            }
        """)
        btn_zoom_in.clicked.connect(lambda: self._grid_view.zoom_in())
        zoom_layout.addWidget(btn_zoom_in)
        
        btn_zoom_reset = QPushButton("Reset")
        btn_zoom_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_zoom_reset.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #475569, stop:1 #334155);
                color: white;
                border: 1px solid #1e293b;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 700;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #334155, stop:1 #475569);
            }
        """)
        btn_zoom_reset.clicked.connect(lambda: self._grid_view.zoom_reset())
        zoom_layout.addWidget(btn_zoom_reset)
        
        layout.addWidget(zoom_group)
        
        return pane
    
    def _create_right_pane(self) -> QWidget:
        """Create right results pane with gematria breakdown."""
        pane = QWidget()
        pane.setMaximumWidth(400)
        layout = QVBoxLayout(pane)
        
        # Style as floating card
        pane.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid #d4c4a8;
                border-radius: 16px;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        pane.setGraphicsEffect(shadow)
        
        layout.addWidget(QLabel("📊 Search Results"))
        
        self._results_table = QTableWidget()
        self._results_table.setColumnCount(4)
        self._results_table.setHorizontalHeaderLabels(["Term", "Skip", "Pos", "Dir"])
        self._results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._results_table.cellClicked.connect(self._on_result_clicked)
        layout.addWidget(self._results_table)
        
        # Filter and count row
        filter_layout = QHBoxLayout()
        self._hits_label = QLabel("Total: 0 hits")
        self._hits_label.setStyleSheet("font-weight: bold;")
        filter_layout.addWidget(self._hits_label)
        
        filter_layout.addStretch()
        
        filter_layout.addWidget(QLabel("Gem:"))
        self._gematria_filter = QLineEdit()
        self._gematria_filter.setPlaceholderText("e.g. 93")
        self._gematria_filter.setFixedWidth(60)
        self._gematria_filter.textChanged.connect(self._apply_gematria_filter)
        filter_layout.addWidget(self._gematria_filter)
        
        layout.addLayout(filter_layout)
        
        # === Gematria Breakdown Section ===
        breakdown_group = QGroupBox("🔢 Gematria Breakdown")
        breakdown_layout = QVBoxLayout(breakdown_group)
        
        self._breakdown_text = QTextEdit()
        self._breakdown_text.setReadOnly(True)
        self._breakdown_text.setMaximumHeight(200)
        self._breakdown_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        breakdown_layout.addWidget(self._breakdown_text)
        
        layout.addWidget(breakdown_group)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        self._btn_export = QPushButton("Export")
        self._btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_export.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
                color: white;
                border: 1px solid #047857;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 700;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
            }
        """)
        self._btn_export.clicked.connect(self._on_export)
        btn_layout.addWidget(self._btn_export)
        
        self._btn_clear = QPushButton("Clear")
        self._btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_clear.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #b91c1c);
                color: white;
                border: 1px solid #b91c1c;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 700;
            }
            QPushButton:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b91c1c, stop:1 #ef4444);
            }
        """)
        self._btn_clear.clicked.connect(self._on_clear)
        btn_layout.addWidget(self._btn_clear)
        layout.addLayout(btn_layout)
        
        return pane
    
    # === Event Handlers ===
    
    def _on_load_document(self):
        """Load text from a file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Text File", "",
            "Text Files (*.txt);;All Files (*)"
        )
        if path:
            text = None
            # Try multiple encodings
            encodings = ['utf-8', 'utf-16', 'cp1252', 'latin-1', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(path, 'r', encoding=encoding) as f:
                        text = f.read()
                    logger.info(f"Loaded file with {encoding} encoding")
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if text is not None:
                self._load_text(text, source=path)
            else:
                QMessageBox.warning(self, "Error", "Failed to decode file with any supported encoding")
    
    def _on_paste_text(self):
        """Show dialog to paste raw text."""
        from PyQt6.QtWidgets import QDialog, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Paste Text")
        dialog.setMinimumSize(500, 400)
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Paste your text here...")
        layout.addWidget(text_edit)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec():
            text = text_edit.toPlainText()
            if text.strip():
                self._load_text(text, source="Pasted Text")
    
    def _on_load_from_database(self):
        """Load text from Document Manager database."""
        from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QListWidget, QListWidgetItem
        from pillars.document_manager.services.document_service import document_service_context
        
        # Fetch documents from database
        try:
            with document_service_context() as doc_service:
                docs = doc_service.get_all_documents_metadata()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load documents: {e}")
            return
        
        if not docs:
            QMessageBox.information(self, "No Documents", "No documents found in database")
            return
        
        # Create selector dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Document")
        dialog.setMinimumSize(500, 400)
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel(f"📚 {len(docs)} documents available:"))
        
        # Document list
        doc_list = QListWidget()
        doc_list.setStyleSheet("""
            QListWidget::item { padding: 8px; }
            QListWidget::item:selected { background-color: #7C3AED; color: white; }
        """)
        
        # Sort by title
        sorted_docs = sorted(docs, key=lambda d: d.title or "Untitled")
        for doc in sorted_docs:
            item = QListWidgetItem(f"{doc.title or 'Untitled'}")
            item.setData(Qt.ItemDataRole.UserRole, doc.id)
            doc_list.addItem(item)
        
        layout.addWidget(doc_list)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() and doc_list.currentItem():
            doc_id = doc_list.currentItem().data(Qt.ItemDataRole.UserRole)
            try:
                with document_service_context() as doc_service:
                    document = doc_service.get_document(doc_id)
                    if document and document.raw_content:
                        self._load_text(document.raw_content, source=document.title or "Database Document")
                    elif document and document.content:
                        # Strip HTML if raw_content not available
                        import re
                        text = re.sub(r'<[^>]+>', '', document.content)
                        self._load_text(text, source=document.title or "Database Document")
                    else:
                        QMessageBox.warning(self, "Error", "Document has no text content")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load document: {e}")
    
    def _load_text(self, text: str, source: str = ""):
        """Process and display text."""
        self._stripped_text, self._position_map = self._service.prepare_text(text)
        
        letter_count = len(self._stripped_text)
        self._letter_count_label.setText(f"Letters: {letter_count:,}")
        
        # Populate grid factors
        self._factors_combo.clear()
        factors = self._service.get_grid_factors(letter_count)
        for cols, rows in factors:
            self._factors_combo.addItem(f"{cols} × {rows}", cols)
        
        # Set initial grid
        if factors:
            initial_cols = factors[0][0]
            self._cols_spin.setValue(initial_cols)
            self._grid_view.set_grid(self._stripped_text, initial_cols)
        
            self._grid_view.set_grid(self._stripped_text, initial_cols)
        
        self.statusBar().showMessage(f"Loaded: {source} ({letter_count:,} letters)")
        logger.info(f"Loaded text: {letter_count} letters from {source}")
    
    def _on_factor_selected(self, index: int):
        """Apply selected factor as grid columns."""
        if index >= 0:
            cols = self._factors_combo.currentData()
            if cols:
                self._cols_spin.setValue(cols)
    
    def _on_apply_grid(self):
        """Apply custom grid configuration."""
        cols = self._cols_spin.value()
        if self._stripped_text:
            self._grid_view.clear_highlights()
        if self._stripped_text:
            self._grid_view.clear_highlights()
            self._grid_view.set_grid(self._stripped_text, cols)
            self.statusBar().showMessage(f"Grid: {cols} columns")
    
    def _on_search(self):
        """Execute ELS or sequence search."""
        term = self._term_input.text().strip()
        if not term:
            QMessageBox.warning(self, "Error", "Please enter a search term")
            return
        
        if not self._stripped_text:
            QMessageBox.warning(self, "Error", "Please load text first")
            return
        
        # Get search parameters
        direction = self._dir_combo.currentText().lower()
        
        if self._exact_radio.isChecked():
            skip = self._exact_skip_spin.value()
            summary = self._service.search_els(
                self._stripped_text, term, skip=skip, direction=direction
            )
        elif self._range_radio.isChecked():
            min_skip = self._min_skip_spin.value()
            max_skip = self._max_skip_spin.value()
            summary = self._service.search_els(
                self._stripped_text, term,
                min_skip=min_skip, max_skip=max_skip,
                direction=direction
            )
        elif self._seq_radio.isChecked():
            seq_type = self._seq_combo.currentText().lower()
            summary = self._service.search_sequence(
                self._stripped_text, term,
                sequence_type=seq_type, direction=direction
            )
        elif self._chain_radio.isChecked():
            # Chain search - opens separate results window
            reverse = self._chain_reverse_check.isChecked()
            chain_summary = self._service.search_chain(self._stripped_text, term, reverse=reverse)
            
            direction_str = "reverse" if reverse else "forward"
            self.statusBar().showMessage(f"Found {len(chain_summary.results)} chain paths ({direction_str}) for '{term}'")
            
            if chain_summary.results:
                from .chain_results_window import ChainResultsWindow
                # Pass window manager for export functionality
                self._chain_results_window = ChainResultsWindow(chain_summary, window_manager=self.window_manager)
                self._chain_results_window.result_selected.connect(self._on_chain_result_selected)
                self._chain_results_window.show()
            return  # Don't continue to normal results display
        
        self._all_results = summary.results
        self._current_results = summary.results
        self._current_results = summary.results
        self._gematria_filter.clear()  # Clear filter on new search
        self._display_results()
        
        self.statusBar().showMessage(f"Found {len(self._current_results)} matches for '{term}'")
    
    def _apply_gematria_filter(self):
        """Filter displayed results by gematria value."""
        if not hasattr(self, '_all_results'):
            return
        
        filter_text = self._gematria_filter.text().strip()
        
        if not filter_text:
            # Show all results
            self._current_results = self._all_results
        else:
            try:
                target_gematria = int(filter_text)
                # Calculate gematria for each result and filter
                calc = TQGematriaCalculator()
                filtered = []
                for result in self._all_results:
                    # Calculate total gematria for this result's intervening letters
                    result_gematria = 0
                    if self._stripped_text:
                        segments = self._service.extract_intervening_letters(
                            self._stripped_text.upper(),
                            result.letter_positions,
                            result.term
                        )
                        for seg in segments:
                            if seg.letters:
                                result_gematria += calc.calculate(seg.letters)
                    
                    term_gematria = calc.calculate(result.term)
                    total = term_gematria + result_gematria
                    
                    if total == target_gematria:
                        filtered.append(result)
                
                self._current_results = filtered
            except ValueError:
                # Invalid input, show all
                self._current_results = self._all_results
        
        self._display_results()
    
    def _display_results(self):
        """Populate results table."""
        self._results_table.setRowCount(len(self._current_results))
        
        for i, result in enumerate(self._current_results):
            self._results_table.setItem(i, 0, QTableWidgetItem(result.term))
            self._results_table.setItem(i, 1, QTableWidgetItem(str(result.skip)))
            self._results_table.setItem(i, 2, QTableWidgetItem(str(result.start_pos)))
            self._results_table.setItem(i, 3, QTableWidgetItem(result.direction[:3]))
        
        all_count = len(self._all_results) if hasattr(self, '_all_results') else len(self._current_results)
        if len(self._current_results) < all_count:
            self._hits_label.setText(f"Showing: {len(self._current_results)} / {all_count} hits")
        else:
            self._hits_label.setText(f"Total: {len(self._current_results)} hits")
        
        # Highlight all results on grid
        self._grid_view.clear_highlights()
        for i, result in enumerate(self._current_results):
            self._grid_view.highlight_sequence(result.letter_positions, i)
    
    def _on_result_clicked(self, row: int, col: int):
        """Center grid on clicked result and show gematria breakdown."""
        if 0 <= row < len(self._current_results):
            result = self._current_results[row]
            if result.letter_positions:
                self._grid_view.center_on_position(result.letter_positions[0])
                self._show_gematria_breakdown(result)
    
    def _on_chain_result_selected(self, positions: list):
        """Handle chain result selection - highlight path on grid."""
        self._grid_view.clear_highlights()
        self._grid_view.highlight_sequence(positions, 0)
        if positions:
            self._grid_view.center_on_position(positions[0])
    
    def _on_export(self):
        """Export results to Document Editor."""
        if not self._current_results:
            QMessageBox.information(self, "No Results", "No results to export")
            return
        
        # Build formatted HTML report
        calc = TQGematriaCalculator()
        lines = []
        
        # Header
        term = self._current_results[0].term if self._current_results else "ELS"
        term_gematria = calc.calculate(term)
        lines.append(f"<h1>🔮 ELS Search Report: {term}</h1>")
        lines.append(f"<p><strong>Term Gematria:</strong> {term_gematria}</p>")
        lines.append(f"<p><strong>Total Matches:</strong> {len(self._current_results)}</p>")
        lines.append("<hr>")
        
        # Each result with gematria breakdown
        for i, result in enumerate(self._current_results, 1):
            lines.append(f"<h2>Match {i}: Skip {result.skip}, Position {result.start_pos} ({result.direction})</h2>")
            
            # Extract segments and calculate gematria
            if self._stripped_text:
                segments = self._service.extract_intervening_letters(
                    self._stripped_text.upper(),
                    result.letter_positions,
                    result.term
                )
                
                term_value = calc.calculate(result.term)
                skip_total = 0
                
                lines.append("<table border='1' cellpadding='5'>")
                lines.append("<tr><th>Segment</th><th>Letters</th><th>Gematria</th></tr>")
                lines.append(f"<tr><td><strong>Term: {result.term}</strong></td><td>—</td><td><strong>{term_value}</strong></td></tr>")
                
                for seg in segments:
                    seg_value = calc.calculate(seg.letters) if seg.letters else 0
                    skip_total += seg_value
                    display_letters = seg.letters[:30] + "..." if len(seg.letters) > 30 else seg.letters
                    lines.append(f"<tr><td>{seg.from_letter} → {seg.to_letter}</td><td>{display_letters}</td><td>{seg_value}</td></tr>")
                
                lines.append(f"<tr><td><strong>Skip Total</strong></td><td>—</td><td><strong>{skip_total}</strong></td></tr>")
                lines.append(f"<tr><td><strong>TOTAL</strong></td><td>—</td><td><strong>{term_value + skip_total}</strong></td></tr>")
                lines.append("</table>")
                lines.append("<br>")
        
        html_content = "\n".join(lines)
        
        # Open in Document Editor
        if self.window_manager:
            from pillars.document_manager.ui.document_editor_window import DocumentEditorWindow
            
            # Use window manager to open window (prevents garbage collection)
            editor_window = self.window_manager.open_window(
                window_type="document_editor",
                window_class=DocumentEditorWindow,
                allow_multiple=True
            )
            
            editor_window.setWindowTitle(f"ELS Report - {term}")
            editor_window.editor.set_html(html_content)
            editor_window.is_modified = True  # Mark as needing save
            editor_window.show()
            
            self.statusBar().showMessage("Exported to Document Editor")
        else:
            QMessageBox.warning(self, "Error", "Window manager not available")
    
    def _on_clear(self):
        """Clear search results."""
        self._current_results.clear()
        self._results_table.setRowCount(0)
        self._hits_label.setText("Total: 0 hits")
        self._grid_view.clear_highlights()
        self._breakdown_text.clear()
    
    def _show_gematria_breakdown(self, result: ELSResult):
        """Display gematria breakdown for selected result."""
        if not self._stripped_text or not result.letter_positions:
            return
        
        calc = TQGematriaCalculator()
        lines = []
        
        # Calculate term gematria
        term_value = calc.calculate(result.term)
        lines.append(f"Search Term: {result.term}")
        lines.append(f"Term Gematria: {term_value}")
        lines.append("-" * 30)
        
        # Extract and calculate intervening segments
        segments = self._service.extract_intervening_letters(
            self._stripped_text.upper(),
            result.letter_positions,
            result.term
        )
        
        skip_total = 0
        for seg in segments:
            seg_value = calc.calculate(seg.letters) if seg.letters else 0
            skip_total += seg_value
            
            # Truncate long letter sequences for display
            display_letters = seg.letters[:20] + "..." if len(seg.letters) > 20 else seg.letters
            lines.append(f"{seg.from_letter} → {seg.to_letter}: {display_letters}")
            lines.append(f"  Value: {seg_value}")
        
        lines.append("-" * 30)
        lines.append(f"Skip Letters Total: {skip_total}")
        lines.append(f"Term + Skip: {term_value + skip_total}")
        
        self._breakdown_text.setText("\n".join(lines))

