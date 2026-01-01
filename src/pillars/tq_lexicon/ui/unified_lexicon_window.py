"""
Unified TQ Lexicon Workflow Window.

Consolidates the entire Holy Book → Concordance workflow into a single tabbed interface:
1. Import & Parse - Select and parse holy books
2. Candidates - Process word candidates from the imported document
3. Concordance - View word occurrences and context
4. Master Key - Full word database view
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import qtawesome as qta
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QLineEdit, QSplitter, QTableWidget,
    QTableWidgetItem, QCheckBox, QPlainTextEdit, QMessageBox,
    QHeaderView, QListWidget, QListWidgetItem, QComboBox, QFrame,
    QTreeWidget, QTreeWidgetItem, QProgressBar, QGroupBox, QTextEdit,
)
from PyQt6.QtGui import QColor, QFont

from ..services.holy_key_service import HolyKeyService
from ..services.enrichment_service import EnrichmentService
from ..services.concordance_indexer_service import ConcordanceIndexerService

logger = logging.getLogger(__name__)


class ParseAndIndexWorker(QThread):
    """Background worker for parse + index."""
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, document_id: int, options: dict):
        super().__init__()
        self.document_id = document_id
        self.options = options

    def run(self):
        try:
            indexer = ConcordanceIndexerService()
            result = indexer.parse_and_index(
                document_id=self.document_id,
                allow_inline=self.options.get('allow_inline', True),
                apply_rules=self.options.get('apply_rules', True),
                auto_save=self.options.get('auto_save', True),
                reindex=self.options.get('reindex', False),
                progress_callback=self._emit_progress,
            )
            self.finished.emit(result)
        except Exception as e:
            logger.exception("Parse and index failed")
            self.error.emit(str(e))

    def _emit_progress(self, current: int, total: int, message: str):
        self.progress.emit(current, total, message)


class EnrichmentWorker(QThread):
    """Worker thread for running the batch enrichment process."""
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal()
    
    def __init__(self, service: HolyKeyService):
        super().__init__()
        self.service = service
        self.enricher = EnrichmentService(service)
        self._is_running = True
        
    def run(self):
        self.enricher.enrich_batch(self._emit_progress)
        self.finished.emit()
        
    def _emit_progress(self, current, total, status):
        if self._is_running:
            self.progress.emit(current, total, status)
            
    def stop(self):
        self._is_running = False

class SuggestionWorker(QThread):
    """Worker for fetching suggestions for a single word."""
    finished = pyqtSignal(list)
    
    def __init__(self, service: HolyKeyService, word: str):
        super().__init__()
        self.service = service
        self.word = word
        self.enricher = EnrichmentService(service)
        
    def run(self):
        suggestions = self.enricher.get_suggestions(self.word)
        self.finished.emit(suggestions)


class UnifiedLexiconWindow(QMainWindow):
    """
    Unified window for the complete TQ Lexicon workflow.
    
    Tabs:
    1. Import & Parse - Select document and parse into verses
    2. Candidates - Process word candidates from the active document
    3. Concordance - View word occurrences across documents
    4. Master Key - Full word database with definitions
    """

    def __init__(self, window_manager=None, parent=None, **kwargs):
        super().__init__(parent)
        self.window_manager = window_manager
        self.setWindowTitle("TQ Lexicon Workflow")
        self.resize(1100, 750)

        # State
        self._active_document: Optional[Dict[str, Any]] = None
        self._documents: List[Dict[str, Any]] = []
        self._worker: Optional[ParseAndIndexWorker] = None

        # Services
        self.service = HolyKeyService()
        self.indexer = ConcordanceIndexerService()

        self._build_ui()
        self._load_documents()

    def _build_ui(self):
        """Build the main UI with tabs."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(8, 8, 8, 8)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tabs)

        # Build each tab
        self._build_import_tab()
        self._build_candidates_tab()
        self._build_concordance_tab()
        self._build_master_key_tab()

        # Status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
        self.statusBar().showMessage("Ready")

    # =========================================================================
    # TAB 1: IMPORT & PARSE
    # =========================================================================

    def _build_import_tab(self):
        """Tab 1: Document import and parsing."""
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # Left: Document list
        left_panel = QGroupBox("Holy Books")
        left_layout = QVBoxLayout(left_panel)

        # Filter
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter:"))
        self.cmb_import_filter = QComboBox()
        self.cmb_import_filter.addItems(["All", "Not Indexed", "Indexed"])
        self.cmb_import_filter.currentTextChanged.connect(self._apply_doc_filter)
        filter_row.addWidget(self.cmb_import_filter, 1)
        left_layout.addLayout(filter_row)

        # Document table
        self.tbl_documents = QTableWidget(0, 4)
        self.tbl_documents.setHorizontalHeaderLabels(["Title", "Verses", "Indexed", "Words"])
        self.tbl_documents.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tbl_documents.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tbl_documents.itemSelectionChanged.connect(self._on_doc_selected)
        header = self.tbl_documents.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        left_layout.addWidget(self.tbl_documents)

        layout.addWidget(left_panel)

        # Right: Details and actions
        right_panel = QGroupBox("Document Details")
        right_layout = QVBoxLayout(right_panel)

        # Document info
        self.lbl_doc_title = QLabel("Select a document")
        self.lbl_doc_title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        right_layout.addWidget(self.lbl_doc_title)

        self.lbl_doc_status = QLabel("")
        self.lbl_doc_status.setStyleSheet("color: #64748b;")
        right_layout.addWidget(self.lbl_doc_status)

        # Options
        options_group = QGroupBox("Parse & Index Options")
        options_layout = QVBoxLayout(options_group)

        self.chk_inline = QCheckBox("Allow inline verse markers")
        self.chk_inline.setChecked(True)
        options_layout.addWidget(self.chk_inline)

        self.chk_rules = QCheckBox("Apply parsing rules")
        self.chk_rules.setChecked(True)
        options_layout.addWidget(self.chk_rules)

        self.chk_autosave = QCheckBox("Auto-save verses as curated")
        self.chk_autosave.setChecked(True)
        options_layout.addWidget(self.chk_autosave)

        self.chk_reindex = QCheckBox("Force re-index (clear existing)")
        self.chk_reindex.setChecked(False)
        options_layout.addWidget(self.chk_reindex)

        right_layout.addWidget(options_group)

        # Results
        results_group = QGroupBox("Results Preview")
        results_layout = QVBoxLayout(results_group)
        self.txt_import_results = QTextEdit()
        self.txt_import_results.setReadOnly(True)
        self.txt_import_results.setPlaceholderText("Results will appear here after processing...")
        results_layout.addWidget(self.txt_import_results)
        right_layout.addWidget(results_group, 1)

        # Actions
        btn_row = QHBoxLayout()

        self.btn_parse_index = QPushButton("🚀 Parse && Index")
        self.btn_parse_index.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
                color: white; border: 1px solid #1e40af; border-radius: 4px;
                padding: 8px 16px; font-weight: 600; font-size: 12pt;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1d4ed8, stop:1 #2563eb); }
            QPushButton:disabled { background: #94a3b8; }
        """)
        self.btn_parse_index.clicked.connect(self._on_parse_and_index)
        self.btn_parse_index.setEnabled(False)
        btn_row.addWidget(self.btn_parse_index)

        btn_row.addStretch()

        btn_refresh = QPushButton("↻ Refresh")
        btn_refresh.clicked.connect(self._load_documents)
        btn_row.addWidget(btn_refresh)
        
        # Advanced (Teacher) Button - Ported from HolyBookConcordanceWindow
        self.btn_teacher = QPushButton("⚙️ Teacher")
        self.btn_teacher.setToolTip("Open detailed verse editor for manual curation")
        self.btn_teacher.clicked.connect(self._open_teacher_window)
        self.btn_teacher.setEnabled(False) 
        btn_row.addWidget(self.btn_teacher)
        
        right_layout.addLayout(btn_row)

        layout.addWidget(right_panel)

        self.tabs.addTab(tab, "📥 Import & Parse")

    # =========================================================================
    # TAB 2: CANDIDATES (Simplified - works with active document only)
    # =========================================================================

    def _build_candidates_tab(self):
        """Tab 2: Simplified candidate processing for active document."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Header showing active document
        header = QHBoxLayout()
        self.lbl_cand_doc = QLabel("No document selected")
        self.lbl_cand_doc.setStyleSheet("font-size: 14pt; font-weight: bold; color: #7c3aed;")
        header.addWidget(self.lbl_cand_doc)
        header.addStretch()

        self.btn_scan_doc = QPushButton("🔍 Scan Document for Candidates")
        self.btn_scan_doc.setEnabled(False)
        self.btn_scan_doc.clicked.connect(self._scan_active_document)
        header.addWidget(self.btn_scan_doc)

        layout.addLayout(header)

        # Candidates list
        lbl = QLabel("Candidates (Uncheck to Exclude/Ignore)")
        lbl.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(lbl)

        self.list_candidates = QListWidget()
        self.list_candidates.setAlternatingRowColors(True)
        layout.addWidget(self.list_candidates, 1)

        # Actions
        action_row = QHBoxLayout()

        self.btn_process_cand = QPushButton("✓ Process Candidates")
        self.btn_process_cand.setIcon(qta.icon("fa5s.check-circle", color="#16a34a"))
        self.btn_process_cand.clicked.connect(self._process_candidates)
        action_row.addWidget(self.btn_process_cand)

        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self.list_candidates.clear)
        action_row.addWidget(btn_clear)

        action_row.addStretch()

        # Status
        self.lbl_cand_status = QLabel("")
        action_row.addWidget(self.lbl_cand_status)

        layout.addLayout(action_row)

        self.tabs.addTab(tab, "📝 Candidates")

    # =========================================================================
    # TAB 3: CONCORDANCE
    # =========================================================================

    def _build_concordance_tab(self):
        """Tab 3: Concordance view."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Header
        header = QHBoxLayout()

        self.lbl_conc_stats = QLabel("Concordance: 0 words | 0 occurrences | 0 documents")
        self.lbl_conc_stats.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(self.lbl_conc_stats)

        header.addStretch()

        header.addWidget(QLabel("Sort by:"))
        self.cmb_conc_sort = QComboBox()
        self.cmb_conc_sort.addItems([
            "Frequency (High→Low)", "Frequency (Low→High)",
            "TQ Value (High→Low)", "TQ Value (Low→High)",
            "Alphabetical (A→Z)", "Alphabetical (Z→A)"
        ])
        self.cmb_conc_sort.currentIndexChanged.connect(self._load_concordance)
        header.addWidget(self.cmb_conc_sort)

        header.addWidget(QLabel("Document:"))
        self.cmb_conc_doc = QComboBox()
        self.cmb_conc_doc.addItem("All Documents", None)
        self.cmb_conc_doc.currentIndexChanged.connect(self._load_concordance)
        header.addWidget(self.cmb_conc_doc)

        layout.addLayout(header)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: Word list
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.txt_conc_filter = QLineEdit()
        self.txt_conc_filter.setPlaceholderText("Filter words...")
        self.txt_conc_filter.textChanged.connect(self._filter_concordance)
        left_layout.addWidget(self.txt_conc_filter)

        self.tree_concordance = QTreeWidget()
        self.tree_concordance.setHeaderLabels(["Word", "Freq", "TQ"])
        self.tree_concordance.setColumnWidth(0, 180)
        self.tree_concordance.setColumnWidth(1, 50)
        self.tree_concordance.setColumnWidth(2, 60)
        self.tree_concordance.itemClicked.connect(self._on_conc_word_selected)
        self.tree_concordance.setAlternatingRowColors(True)
        left_layout.addWidget(self.tree_concordance)

        splitter.addWidget(left)

        # Right: Occurrences
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_occ_word = QLabel("Select a word to view occurrences")
        self.lbl_occ_word.setStyleSheet("font-weight: bold; font-size: 16px; color: #7c3aed;")
        right_layout.addWidget(self.lbl_occ_word)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        right_layout.addWidget(line)

        self.lbl_occ_defs = QLabel("")
        self.lbl_occ_defs.setWordWrap(True)
        self.lbl_occ_defs.setStyleSheet("color: #4b5563; padding: 5px; background: #f3f4f6; border-radius: 4px;")
        right_layout.addWidget(self.lbl_occ_defs)

        self.list_occurrences = QListWidget()
        self.list_occurrences.setAlternatingRowColors(True)
        right_layout.addWidget(self.list_occurrences)

        splitter.addWidget(right)
        splitter.setSizes([350, 500])

        layout.addWidget(splitter)

        self.tabs.addTab(tab, "📖 Concordance")

    # =========================================================================
    # TAB 4: MASTER KEY
    # =========================================================================

    def _build_master_key_tab(self):
        """Tab 4: Master Key database view."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Filter bar
        filter_row = QHBoxLayout()

        self.txt_mk_search = QLineEdit()
        self.txt_mk_search.setPlaceholderText("Search Key...")
        self.txt_mk_search.textChanged.connect(self._search_master_key)
        filter_row.addWidget(self.txt_mk_search)

        filter_row.addWidget(QLabel("Sort:"))
        self.cmb_mk_sort = QComboBox()
        self.cmb_mk_sort.addItems(["Alphabetical", "TQ Value", "Frequency", "Recently Added"])
        self.cmb_mk_sort.currentIndexChanged.connect(lambda: self._search_master_key(self.txt_mk_search.text()))
        filter_row.addWidget(self.cmb_mk_sort)

        layout.addLayout(filter_row)

        # Table
        self.tbl_master_key = QTableWidget()
        self.tbl_master_key.setColumnCount(4)
        self.tbl_master_key.setHorizontalHeaderLabels(["ID", "Word", "TQ Value", "Freq"])
        self.tbl_master_key.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tbl_master_key.setColumnWidth(0, 60)
        self.tbl_master_key.setColumnWidth(2, 80)
        self.tbl_master_key.setColumnWidth(3, 60)
        self.tbl_master_key.setAlternatingRowColors(True)
        self.tbl_master_key.setSortingEnabled(True)
        self.tbl_master_key.itemDoubleClicked.connect(self._on_mk_double_click)
        layout.addWidget(self.tbl_master_key)

        # Bottom buttons
        btn_row = QHBoxLayout()

        btn_enrich = QPushButton("✨ Auto-Enrich Definitions")
        btn_enrich.setIcon(qta.icon("fa5s.magic", color="#8b5cf6"))
        btn_enrich.clicked.connect(self._start_enrichment)
        btn_row.addWidget(btn_enrich)

        btn_row.addStretch()

        # Pagination
        self.btn_mk_prev = QPushButton("<")
        self.btn_mk_prev.setMaximumWidth(30)
        self.btn_mk_prev.clicked.connect(self._mk_prev_page)
        btn_row.addWidget(self.btn_mk_prev)

        self.lbl_mk_page = QLabel("Page 1 / 1")
        self.lbl_mk_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_row.addWidget(self.lbl_mk_page)

        self.btn_mk_next = QPushButton(">")
        self.btn_mk_next.setMaximumWidth(30)
        self.btn_mk_next.clicked.connect(self._mk_next_page)
        btn_row.addWidget(self.btn_mk_next)

        btn_row.addStretch()

        btn_reset = QPushButton("Reset Database")
        btn_reset.setStyleSheet("background-color: #ef4444; color: white; border-radius: 4px; padding: 5px;")
        btn_reset.clicked.connect(self._reset_database)
        btn_row.addWidget(btn_reset)

        layout.addLayout(btn_row)

        self.tabs.addTab(tab, "🔑 Master Key")

        # Pagination state
        self._mk_page = 1
        self._mk_page_size = 500
        self._mk_total_pages = 1

    # =========================================================================
    # DOCUMENT LOADING (Tab 1)
    # =========================================================================

    def _load_documents(self):
        """Load documents for the import tab (filtered to Holy Books only)."""
        try:
            from shared.database import get_db_session
            from shared.repositories.document_manager.document_repository import DocumentRepository

            # Sacred collection markers
            SACRED_MARKERS = ["holy", "class a", "class f"]

            with get_db_session() as db:
                doc_repo = DocumentRepository(db)
                all_documents = doc_repo.get_all()

            self._documents = []
            for doc in all_documents:
                # Filter to only sacred texts
                collection_lower = (doc.collection or "").lower()
                if not any(marker in collection_lower for marker in SACRED_MARKERS):
                    continue

                status = self.indexer.get_document_status(doc.id)
                self._documents.append({
                    'id': doc.id,
                    'title': doc.title,
                    'verse_count': status['verse_count'],
                    'is_indexed': status['is_indexed'],
                    'occurrence_count': status['occurrence_count'],
                    'has_curated': status['has_curated_verses'],
                })

            self._populate_doc_table()
            self._update_stats()

            # Show helpful message if no sacred texts found
            if not self._documents:
                self.statusBar().showMessage(
                    "No Holy Books found. Add documents to 'Holy', 'Class A', or 'Class F' collections."
                )

        except Exception as e:
            logger.exception("Failed to load documents")
            QMessageBox.critical(self, "Error", f"Failed to load documents:\n{e}")

    def _populate_doc_table(self, docs: Optional[List[Dict]] = None):
        """Populate the document table."""
        if docs is None:
            docs = self._documents

        self.tbl_documents.setRowCount(len(docs))

        for row, doc in enumerate(docs):
            # Title
            title_item = QTableWidgetItem(doc['title'])
            title_item.setData(Qt.ItemDataRole.UserRole, doc)
            self.tbl_documents.setItem(row, 0, title_item)

            # Verses
            verse_item = QTableWidgetItem(str(doc['verse_count']) if doc['verse_count'] else "-")
            verse_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tbl_documents.setItem(row, 1, verse_item)

            # Indexed
            status = "✓" if doc['is_indexed'] else ("○" if doc['has_curated'] else "—")
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tbl_documents.setItem(row, 2, status_item)

            # Words
            word_item = QTableWidgetItem(str(doc['occurrence_count']) if doc['occurrence_count'] else "-")
            word_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tbl_documents.setItem(row, 3, word_item)

    def _apply_doc_filter(self, filter_text: str):
        """Apply filter to document list."""
        if filter_text == "All":
            filtered = self._documents
        elif filter_text == "Not Indexed":
            filtered = [d for d in self._documents if not d['is_indexed']]
        elif filter_text == "Indexed":
            filtered = [d for d in self._documents if d['is_indexed']]
        else:
            filtered = self._documents
        self._populate_doc_table(filtered)

    def _on_doc_selected(self):
        """Handle document selection."""
        rows = self.tbl_documents.selectionModel().selectedRows()
        if not rows:
            self._active_document = None
            self.lbl_doc_title.setText("Select a document")
            self.lbl_doc_status.setText("")
            self.btn_parse_index.setEnabled(False)
            self._update_candidates_header()
            return

        row = rows[0].row()
        item = self.tbl_documents.item(row, 0)
        if item:
            self._active_document = item.data(Qt.ItemDataRole.UserRole)
            self._update_doc_details()
            self._update_candidates_header()

    def _update_doc_details(self):
        """Update document details panel."""
        if not self._active_document:
            return

        doc = self._active_document
        self.lbl_doc_title.setText(doc['title'])

        status_parts = []
        if doc['has_curated']:
            status_parts.append(f"📝 {doc['verse_count']} curated verses")
        else:
            status_parts.append("📄 Not yet parsed")

        if doc['is_indexed']:
            status_parts.append(f"📚 {doc['occurrence_count']} word occurrences indexed")
        else:
            status_parts.append("🔍 Not indexed")

        self.lbl_doc_status.setText(" · ".join(status_parts))
        self.btn_parse_index.setEnabled(True)
        self.chk_reindex.setChecked(doc['is_indexed'])

    def _on_parse_and_index(self):
        """Run parse and index on selected document."""
        if not self._active_document:
            return

        doc = self._active_document

        if doc['is_indexed'] and self.chk_reindex.isChecked():
            reply = QMessageBox.question(
                self, "Re-index Document",
                f"'{doc['title']}' is already indexed.\n\nThis will clear existing data. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self._set_processing(True)
        self.txt_import_results.clear()

        self._worker = ParseAndIndexWorker(
            document_id=doc['id'],
            options={
                'allow_inline': self.chk_inline.isChecked(),
                'apply_rules': self.chk_rules.isChecked(),
                'auto_save': self.chk_autosave.isChecked(),
                'reindex': self.chk_reindex.isChecked(),
            }
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_parse_finished)
        self._worker.error.connect(self._on_parse_error)
        self._worker.start()

    def _on_progress(self, current: int, total: int, message: str):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.statusBar().showMessage(message)

    def _on_parse_finished(self, result):
        self._set_processing(False)
        self._worker = None

        lines = [
            f"✓ Completed: '{result.document_title}'",
            "=" * 40,
            "\n📝 PARSING:",
            f"  Verses: {len(result.verses)}",
            f"  Source: {result.source}",
            "\n📚 INDEXING:",
            f"  Words: {result.total_words}",
            f"  New keys: {result.new_keys_added}",
            f"  Occurrences: {result.occurrences_added}",
        ]
        if result.errors:
            lines.append(f"\n⚠️ Errors: {len(result.errors)}")

        self.txt_import_results.setPlainText("\n".join(lines))
        self._load_documents()
        self._update_stats()

        QMessageBox.information(
            self, "Complete",
            f"'{result.document_title}' processed.\n\n"
            f"• {len(result.verses)} verses\n"
            f"• {result.occurrences_added} word occurrences"
        )

    def _on_parse_error(self, error_msg: str):
        self._set_processing(False)
        self._worker = None
        self.txt_import_results.setPlainText(f"❌ Error:\n{error_msg}")
        QMessageBox.critical(self, "Error", f"Processing failed:\n{error_msg}")

    def _set_processing(self, processing: bool):
        self.progress_bar.setVisible(processing)
        self.btn_parse_index.setEnabled(not processing)
        self.tbl_documents.setEnabled(not processing)

    # =========================================================================
    # CANDIDATES (Tab 2)
    # =========================================================================

    def _update_candidates_header(self):
        """Update candidates tab header based on active document."""
        if self._active_document:
            self.lbl_cand_doc.setText(f"📄 {self._active_document['title']}")
            self.btn_scan_doc.setEnabled(True)
        else:
            self.lbl_cand_doc.setText("No document selected - Go to Import tab first")
            self.btn_scan_doc.setEnabled(False)

    def _scan_active_document(self):
        """Scan the active document for word candidates."""
        if not self._active_document:
            return

        try:
            from shared.database import get_db_session
            from shared.repositories.document_manager.document_repository import DocumentRepository

            with get_db_session() as db:
                doc_repo = DocumentRepository(db)
                doc = doc_repo.get(self._active_document['id'])

                if not doc or not doc.content:
                    QMessageBox.warning(self, "No Content", "Document has no text content.")
                    return

                candidates = self.service.scan_text(doc.content)

            self.list_candidates.clear()
            for word in candidates:
                item = QListWidgetItem(word)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked)
                self.list_candidates.addItem(item)

            self.lbl_cand_status.setText(f"Found {len(candidates)} candidates")

        except Exception as e:
            logger.exception("Scan failed")
            QMessageBox.critical(self, "Error", f"Scan failed:\n{e}")

    def _process_candidates(self):
        """Process candidates - add checked to master key, unchecked to ignore."""
        approved = []
        ignored = []

        for i in range(self.list_candidates.count()):
            item = self.list_candidates.item(i)
            word = item.text()
            if item.checkState() == Qt.CheckState.Checked:
                approved.append(word)
            else:
                ignored.append(word)

        source = self._active_document['title'] if self._active_document else "Manual"
        added, already = self.service.process_batch(approved, source)
        self.service.bulk_ignore(ignored)

        self.list_candidates.clear()
        self.lbl_cand_status.setText(f"Added {added}, {already} existed, {len(ignored)} ignored")
        self.statusBar().showMessage(f"Processed: {added} added, {len(ignored)} ignored (Source: {source}).")

        # Refresh master key
        self._search_master_key("")

    # =========================================================================
    # CONCORDANCE (Tab 3)
    # =========================================================================

    def _load_concordance(self):
        """Load concordance data."""
        stats = self.service.db.get_concordance_stats()

        self.lbl_conc_stats.setText(
            f"Concordance: {stats.get('total_indexed_words', 0):,} words | "
            f"{stats.get('total_occurrences', 0):,} occurrences | "
            f"{stats.get('indexed_documents', 0)} documents"
        )

        # Update document dropdown
        current_doc = self.cmb_conc_doc.currentData()
        self.cmb_conc_doc.blockSignals(True)
        self.cmb_conc_doc.clear()
        self.cmb_conc_doc.addItem("All Documents", None)
        for doc_id, title in stats.get('documents', []):
            self.cmb_conc_doc.addItem(title, doc_id)
        if current_doc:
            idx = self.cmb_conc_doc.findData(current_doc)
            if idx >= 0:
                self.cmb_conc_doc.setCurrentIndex(idx)
        self.cmb_conc_doc.blockSignals(False)

        # Sort options
        sort_idx = self.cmb_conc_sort.currentIndex()
        sort_options = [
            ('frequency', True), ('frequency', False),
            ('tq_value', True), ('tq_value', False),
            ('word', False), ('word', True),
        ]
        sort_by, desc = sort_options[sort_idx] if sort_idx < len(sort_options) else ('frequency', True)

        words_data = self.service.db.get_concordance_words(
            document_id=self.cmb_conc_doc.currentData(),
            sort_by=sort_by,
            descending=desc,
            limit=2000
        )

        self.tree_concordance.clear()
        self._concordance_data = words_data

        for word, freq, tq_value, key_id in words_data:
            item = QTreeWidgetItem([word, str(freq), str(tq_value)])
            item.setData(0, Qt.ItemDataRole.UserRole, key_id)
            if freq >= 10:
                item.setForeground(0, QColor("#7c3aed"))
            elif freq >= 5:
                item.setForeground(0, QColor("#2563eb"))
            self.tree_concordance.addTopLevelItem(item)

    def _filter_concordance(self, text: str):
        """Filter concordance tree."""
        text = text.lower()
        for i in range(self.tree_concordance.topLevelItemCount()):
            item = self.tree_concordance.topLevelItem(i)
            item.setHidden(text not in item.text(0).lower())

    def _on_conc_word_selected(self, item: QTreeWidgetItem, column: int):
        """Show occurrences for selected word."""
        key_id = item.data(0, Qt.ItemDataRole.UserRole)
        word = item.text(0)
        tq_value = item.text(2)

        self.lbl_occ_word.setText(f"{word}  (TQ: {tq_value})")

        definitions = self.service.db.get_definitions(key_id)
        if definitions:
            def_text = "\n".join([f"• [{d.type}] {d.content[:100]}..." if len(d.content) > 100
                                  else f"• [{d.type}] {d.content}" for d in definitions[:3]])
            self.lbl_occ_defs.setText(def_text)
        else:
            self.lbl_occ_defs.setText("No definitions recorded")

        occurrences = self.service.db.get_word_occurrences(key_id)
        self.list_occurrences.clear()
        for occ in occurrences:
            text = f"📖 {occ.document_title} — Verse {occ.verse_number}"
            if occ.context_snippet:
                text += f"\n   \"{occ.context_snippet}\""
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, occ)
            self.list_occurrences.addItem(item)

    # =========================================================================
    # TEACHER / ADVANCED WORKFLOW
    # =========================================================================

    def _open_teacher_window(self):
        """Open the detailed verse teacher window for advanced curation."""
        if not self._active_document:
            return
            
        try:
            from pillars.gematria.ui.holy_book_teacher_window import HolyBookTeacherWindow
            
            doc = self._active_document
            self.teacher_window = HolyBookTeacherWindow(
                document_id=doc['id'],
                document_title=doc['title'],
                allow_inline=self.chk_inline.isChecked(),
                parent=self,
            )
            self.teacher_window.verses_saved.connect(self._load_documents)
            self.teacher_window.show()
        except Exception as e:
            logger.exception("Failed to open Teacher window")
            QMessageBox.critical(self, "Error", f"Failed to open Teacher window:\n{e}")

    # =========================================================================
    # DETAILED VIEW & ENRICHMENT
    # =========================================================================

    def _on_mk_double_click(self, item: QTableWidgetItem):
        """Handle double-click in Master Key table."""
        row = item.row()
        self._open_key_details(row)

    def _open_key_details(self, row):
        """Open detailed view for a Master Key with enrichment & concordance."""
        # Get data from table
        id_item = self.tbl_master_key.item(row, 0)
        word_item = self.tbl_master_key.item(row, 1)
        tq_item = self.tbl_master_key.item(row, 2)
        
        if not id_item or not word_item:
            return
            
        key_id = int(id_item.text())
        word = word_item.text()
        tq_value = tq_item.text() if tq_item else "?"
        
        from PyQt6.QtWidgets import QDialog, QFormLayout, QTextEdit, QComboBox, QGroupBox
        
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Key Details: {word} (TQ: {tq_value})")
        dlg.resize(700, 700)
        layout = QVBoxLayout(dlg)
        
        # Header
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_word = QLabel(f"<h2>{word}</h2>")
        lbl_word.setStyleSheet("color: #7c3aed;")
        header_layout.addWidget(lbl_word)
        
        lbl_tq = QLabel(f"TQ Value: <b>{tq_value}</b>")
        lbl_tq.setStyleSheet("font-size: 14px; padding: 5px 10px; background: #ede9fe; border-radius: 4px;")
        header_layout.addWidget(lbl_tq)
        header_layout.addStretch()
        layout.addWidget(header_widget)
        
        # Tabs
        detail_tabs = QTabWidget()
        layout.addWidget(detail_tabs)
        
        # === Tab 1: Definitions ===
        def_tab = QWidget()
        def_layout = QVBoxLayout(def_tab)
        
        # List of existing definitions
        def_list = QListWidget()
        def_list.setAlternatingRowColors(True)
        definitions = self.service.db.get_definitions(key_id)
        
        for d in definitions:
            src_text = f" ({d.source})" if d.source else ""
            item = QListWidgetItem(f"[{d.type}] {d.content}{src_text}")
            item.setData(Qt.ItemDataRole.UserRole, d)
            def_list.addItem(item)
            
        if not definitions:
            def_list.addItem(QListWidgetItem("No definitions recorded. Use 'Fetch Suggestions' to add."))
            
        def_layout.addWidget(def_list)
        
        # Add Definition Section
        group_add = QGroupBox("Add New Definition")
        def_layout.addWidget(group_add)
        add_layout = QVBoxLayout(group_add)
        
        # Auto-fetch button (no dropdown)
        box_auto = QHBoxLayout()
        btn_fetch = QPushButton("✨ Fetch & Add All")
        btn_fetch.setIcon(qta.icon("fa5s.magic", color="#8b5cf6"))
        btn_fetch.setStyleSheet("background-color: #8b5cf6; color: white; font-weight: bold; padding: 8px 16px;")
        box_auto.addWidget(btn_fetch)
        box_auto.addStretch()
        add_layout.addLayout(box_auto)
        
        # Status label for fetch results
        lbl_fetch_status = QLabel("")
        lbl_fetch_status.setStyleSheet("color: #64748b; font-style: italic;")
        add_layout.addWidget(lbl_fetch_status)
        
        # Separator
        add_layout.addWidget(QLabel("— or add manually —"))
        
        # Manual Form
        form_layout = QFormLayout()
        cmb_type = QComboBox()
        cmb_type.addItems(['Etymology', 'Standard', 'Alchemical', 'Botanical', 'Occult', 'Divinatory', 'Mythological'])
        
        txt_content = QTextEdit()
        txt_content.setMaximumHeight(80)
        
        txt_source = QLineEdit()
        txt_source.setPlaceholderText("Citation / Authority")
        
        form_layout.addRow("Type:", cmb_type)
        form_layout.addRow("Meaning:", txt_content)
        form_layout.addRow("Citation:", txt_source)
        add_layout.addLayout(form_layout)
        
        btn_add = QPushButton("Add Definition")
        btn_add.setStyleSheet("background-color: #7c3aed; color: white; font-weight: bold;")
        add_layout.addWidget(btn_add)
        
        detail_tabs.addTab(def_tab, f"Definitions ({len(definitions)})")
        
        # Logic for auto-fetch and add
        def fetch_and_add_all():
            btn_fetch.setText("Fetching...")
            btn_fetch.setEnabled(False)
            lbl_fetch_status.setText("Querying sources...")
            self.sugg_worker = SuggestionWorker(self.service, word)
            self.sugg_worker.finished.connect(on_auto_add_complete)
            self.sugg_worker.start()
            
        def on_auto_add_complete(suggestions):
            btn_fetch.setText("✨ Fetch & Add All")
            btn_fetch.setEnabled(True)
            
            if not suggestions:
                lbl_fetch_status.setText("No definitions found from any source.")
                return
                
            # Track what types we add to avoid duplicates
            added_types = set()
            added_count = 0
            
            # Principle of Apocalypsis: ALL revelation, no veils
            for s in suggestions:
                self.service.db.add_definition(key_id, s.type, s.content, s.source)
                added_count += 1
            
            # Refresh the list
            def_list.clear()
            new_defs = self.service.db.get_definitions(key_id)
            for d in new_defs:
                src_text = f" ({d.source})" if d.source else ""
                item = QListWidgetItem(f"[{d.type}] {d.content}{src_text}")
                item.setData(Qt.ItemDataRole.UserRole, d)
                def_list.addItem(item)
                
            detail_tabs.setTabText(0, f"Definitions ({len(new_defs)})")
            lbl_fetch_status.setText(f"Added {added_count} definitions from {len(added_types)} categories.")
            
            # Emit signal
            try:
                from shared.signals.navigation_bus import navigation_bus
                navigation_bus.lexicon_updated.emit(key_id, word)
            except Exception as e:
                logger.error(f"Signal emit failed: {e}")
                
            QMessageBox.information(dlg, "Enriched", f"Added {added_count} definitions.")

        def add_definition():
            """Manual definition add."""
            content = txt_content.toPlainText().strip()
            dtype = cmb_type.currentText()
            source = txt_source.text().strip()
            
            if not content:
                QMessageBox.warning(dlg, "Missing Content", "Please enter a meaning.")
                return
                
            self.service.db.add_definition(key_id, dtype, content, source)
            
            # Refresh list
            def_list.clear()
            new_defs = self.service.db.get_definitions(key_id)
            for d in new_defs:
                src_text = f" ({d.source})" if d.source else ""
                item = QListWidgetItem(f"[{d.type}] {d.content}{src_text}")
                item.setData(Qt.ItemDataRole.UserRole, d)
                def_list.addItem(item)
            
            detail_tabs.setTabText(0, f"Definitions ({len(new_defs)})")
            txt_content.clear()
            
            # Emit Signal
            try:
                from shared.signals.navigation_bus import navigation_bus
                navigation_bus.lexicon_updated.emit(key_id, word)
            except Exception as e:
                logger.error(f"Signal emit failed: {e}")
                
            QMessageBox.information(dlg, "Added", "Definition added successfully.")

        btn_fetch.clicked.connect(fetch_and_add_all)
        btn_add.clicked.connect(add_definition)
        
        # === Tab 2: Concordance ===
        conc_tab = QWidget()
        conc_layout = QVBoxLayout(conc_tab)
        
        occ_list = QListWidget()
        occ_list.setAlternatingRowColors(True)
        occurrences = self.service.db.get_word_occurrences(key_id)
        
        for occ in occurrences:
             text = f"📖 {occ.document_title} — Verse {occ.verse_number}\n   \"{occ.context_snippet}\""
             occ_list.addItem(text)
             
        conc_layout.addWidget(occ_list)
        detail_tabs.addTab(conc_tab, f"Occurrences ({len(occurrences)})")
        
        dlg.exec()

    # =========================================================================
    # MASTER KEY (Tab 4)
    # =========================================================================

    def _search_master_key(self, query: str = ""):
        """Search and display master key entries."""
        sort_map = {0: 'word', 1: 'tq_value', 2: 'frequency', 3: 'id'}
        sort_by = sort_map.get(self.cmb_mk_sort.currentIndex(), 'word')
        desc = sort_by in ('frequency', 'id')

        results, total = self.service.db.search_keys(
            query, page=self._mk_page, page_size=self._mk_page_size,
            sort_by=sort_by, descending=desc
        )

        self._mk_total_pages = max(1, (total + self._mk_page_size - 1) // self._mk_page_size)
        self.lbl_mk_page.setText(f"Page {self._mk_page} / {self._mk_total_pages}")

        self.tbl_master_key.setRowCount(len(results))
        for row, key in enumerate(results):
            self.tbl_master_key.setItem(row, 0, QTableWidgetItem(str(key.id)))
            self.tbl_master_key.setItem(row, 1, QTableWidgetItem(key.word))
            self.tbl_master_key.setItem(row, 2, QTableWidgetItem(str(key.tq_value)))
            self.tbl_master_key.setItem(row, 3, QTableWidgetItem(str(key.frequency)))

    def _mk_prev_page(self):
        if self._mk_page > 1:
            self._mk_page -= 1
            self._search_master_key(self.txt_mk_search.text())

    def _mk_next_page(self):
        if self._mk_page < self._mk_total_pages:
            self._mk_page += 1
            self._search_master_key(self.txt_mk_search.text())



    def _start_enrichment(self):
        """Start auto-enrichment of definitions."""
        targets = self.service.get_undefined_keys()
        if not targets:
            QMessageBox.information(self, "Enrichment", "All keys already have definitions!")
            return
            
        count = len(targets)
        reply = QMessageBox.question(
            self, "Confirm Enrichment",
            f"Found {count} keys without definitions.\nFetch meanings automatically?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._enrich_worker = EnrichmentWorker(self.service)
            self._enrich_worker.progress.connect(self._on_enrich_progress)
            self._enrich_worker.finished.connect(self._on_enrich_finished)
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(count)
            self.statusBar().showMessage(f"Enrichment started ({count} keys)...")
            self._enrich_worker.start()

    def _reset_database(self):
        """Reset the entire database."""
        reply = QMessageBox.warning(
            self, "Reset Database",
            "This will DELETE all words, definitions, and occurrences.\n\nAre you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.service.db.reset_database()
            self._search_master_key("")
            self._load_concordance()
            self._load_documents()
            self.statusBar().showMessage("Database reset.")

    def _on_enrich_progress(self, current: int, total: int, status: str):
        """Handle enrichment progress updates."""
        self.progress_bar.setValue(current)
        self.statusBar().showMessage(status)

    def _on_enrich_finished(self):
        """Handle enrichment completion."""
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Enrichment complete!")
        self._search_master_key("")  # Refresh the list

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def _on_tab_changed(self, index: int):
        """Handle tab changes."""
        tab_text = self.tabs.tabText(index)
        if "Concordance" in tab_text:
            self._load_concordance()
        elif "Master Key" in tab_text:
            self._search_master_key("")
        elif "Candidates" in tab_text:
            self._update_candidates_header()

    def _update_stats(self):
        """Update status bar with stats."""
        stats = self.service.db.get_concordance_stats()
        indexed = sum(1 for d in self._documents if d['is_indexed'])
        self.statusBar().showMessage(
            f"Keys: {stats['total_keys']} | Indexed: {indexed}/{len(self._documents)} docs | "
            f"Occurrences: {stats['total_occurrences']}"
        )
