import logging
import qtawesome as qta
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QLineEdit, QSplitter, QTableWidget, 
    QTableWidgetItem, QCheckBox, QPlainTextEdit, QMessageBox,
    QHeaderView, QListWidget, QListWidgetItem, QMenu, QProgressBar,
    QTreeWidget, QTreeWidgetItem, QComboBox, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QFont, QColor

from ..services.holy_key_service import HolyKeyService
from ..services.enrichment_service import EnrichmentService

logger = logging.getLogger(__name__)

class EnrichmentWorker(QThread):
    """Worker thread for running the enrichment process."""
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

class LexiconManagerWindow(QMainWindow):
    """
    Sovereign Interface for managing the Holy Book Key.
    """
    
    def __init__(self, window_manager=None, parent=None, **kwargs):
        super().__init__(parent)
        self.window_manager = window_manager
        self.setWindowTitle("Holy Key Lexicon")
        self.resize(1000, 700)
        
        # Initialize Service
        self.service = HolyKeyService()
        self.worker = None
        
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Init Tabs
        self._init_staging_tab()
        self._init_master_key_tab()
        self._init_concordance_tab()
        
        # Status Bar & Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar)
        self.statusBar().showMessage("Lexicon loaded.")
        self._update_stats()

    def _init_staging_tab(self):
        """Tab 1: Staging & Curation."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Top: Input Area
        input_layout = QHBoxLayout()
        self.txt_input = QPlainTextEdit()
        self.txt_input.setPlaceholderText("Paste text here to scan for new candidates...")
        input_layout.addWidget(self.txt_input, 3)
        
        btn_scan = QPushButton("Scan Text")
        btn_scan.setIcon(qta.icon("fa5s.search", color="#2563eb"))
        btn_scan.clicked.connect(self._scan_text)
        btn_scan.setMinimumHeight(40)
        
        btn_import = QPushButton("Import File")
        btn_import.setIcon(qta.icon("fa5s.file-upload", color="#d97706"))
        btn_import.clicked.connect(self._import_file)
        btn_import.setMinimumHeight(40)

        # Button Layout
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(btn_scan)
        btn_layout.addWidget(btn_import)
        
        input_layout.addWidget(self.txt_input, 1)
        input_layout.addLayout(btn_layout, 0)
        
        layout.addLayout(input_layout, 1)
        
        # Middle: Candidates List (Opt-out)
        lbl_candidates = QLabel("Candidates (Uncheck to Exclude/Ignore)")
        lbl_candidates.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(lbl_candidates)
        
        self.list_candidates = QListWidget()
        layout.addWidget(self.list_candidates, 3)
        
        # Source Input (Batch)
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Source for Approval:"))
        self.txt_batch_source = QLineEdit()
        self.txt_batch_source.setPlaceholderText("e.g. Liber LUXORAT (Auto-filled on import)")
        self.txt_batch_source.setText("Magus") # Default fallback
        source_layout.addWidget(self.txt_batch_source)
        layout.addLayout(source_layout)
        
        # Bottom: Actions
        action_layout = QHBoxLayout()
        
        btn_process = QPushButton("Process Candidates")
        btn_process.setToolTip("Add Checked to Master Key, Unchecked to Ignore List")
        btn_process.setIcon(qta.icon("fa5s.check-circle", color="#16a34a"))
        btn_process.clicked.connect(self._process_candidates)
        
        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self.list_candidates.clear)
        
        action_layout.addWidget(btn_process)
        action_layout.addWidget(btn_clear)
        layout.addLayout(action_layout)
        
        self.tabs.addTab(tab, "Staging & Curation")

    def _init_master_key_tab(self):
        """Tab 2: Master Key Database."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Filter Bar
        filter_layout = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Search Key...")
        self.txt_search.textChanged.connect(self._search_keys)
        filter_layout.addWidget(self.txt_search)
        
        # Sort options
        filter_layout.addWidget(QLabel("Sort:"))
        self.cmb_mk_sort = QComboBox()
        self.cmb_mk_sort.addItems(["Alphabetical", "TQ Value", "Frequency", "Recently Added"])
        self.cmb_mk_sort.currentIndexChanged.connect(lambda: self._search_keys(self.txt_search.text()))
        filter_layout.addWidget(self.cmb_mk_sort)
        
        layout.addLayout(filter_layout)
        
        # Table with 4 columns now
        self.table_keys = QTableWidget()
        self.table_keys.setColumnCount(4)
        self.table_keys.setHorizontalHeaderLabels(["ID", "Word", "TQ Value", "Freq"])
        self.table_keys.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_keys.setColumnWidth(0, 60)
        self.table_keys.setColumnWidth(2, 80)
        self.table_keys.setColumnWidth(3, 60)
        self.table_keys.setAlternatingRowColors(True)
        self.table_keys.setSortingEnabled(True)
        layout.addWidget(self.table_keys)
        
        # Bottom Buttons
        btn_layout = QHBoxLayout()
        
        # Enrich Button
        btn_enrich = QPushButton("Auto-Enrich Definitions")
        btn_enrich.setIcon(qta.icon("fa5s.magic", color="#8b5cf6"))
        btn_enrich.setToolTip("Fetch definitions for words with no meanings")
        btn_enrich.clicked.connect(self._start_enrichment)
        btn_layout.addWidget(btn_enrich)
        
        btn_layout.addStretch()

        # Pagination Controls
        self.btn_prev = QPushButton("<") 
        self.btn_prev.setMaximumWidth(30)
        self.btn_prev.clicked.connect(self._prev_page)
        
        self.lbl_page = QLabel("Page 1 / ?")
        self.lbl_page.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_page.setMinimumWidth(80)
        
        self.btn_next = QPushButton(">")
        self.btn_next.setMaximumWidth(30)
        self.btn_next.clicked.connect(self._next_page)
        
        btn_layout.addWidget(self.btn_prev)
        btn_layout.addWidget(self.lbl_page)
        btn_layout.addWidget(self.btn_next)
        
        btn_layout.addStretch()
        
        # Reset Database Button
        btn_reset = QPushButton("Reset Database")
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #ef4444; 
                color: white; 
                border-radius: 4px; 
                padding: 5px;
            }
            QPushButton:hover { background-color: #dc2626; }
        """)
        btn_reset.clicked.connect(self._reset_database)
        btn_layout.addWidget(btn_reset)
        
        layout.addLayout(btn_layout)
        
        self.tabs.addTab(tab, "Master Key")
        
        # Initial Load
        self.current_page = 1
        self.page_size = 500
        self.total_pages = 1
        self._search_keys("")
    
    def _init_concordance_tab(self):
        """Tab 3: Concordance View - Word occurrences by document/verse."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header with stats
        header_layout = QHBoxLayout()
        
        self.lbl_concordance_stats = QLabel("Concordance: Loading...")
        self.lbl_concordance_stats.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.lbl_concordance_stats)
        
        header_layout.addStretch()
        
        # Sort options
        header_layout.addWidget(QLabel("Sort by:"))
        self.cmb_conc_sort = QComboBox()
        self.cmb_conc_sort.addItems(["Frequency (High→Low)", "Frequency (Low→High)", 
                                     "TQ Value (High→Low)", "TQ Value (Low→High)",
                                     "Alphabetical (A→Z)", "Alphabetical (Z→A)"])
        self.cmb_conc_sort.currentIndexChanged.connect(self._load_concordance)
        header_layout.addWidget(self.cmb_conc_sort)
        
        # Filter by document
        header_layout.addWidget(QLabel("Document:"))
        self.cmb_conc_doc = QComboBox()
        self.cmb_conc_doc.addItem("All Documents", None)
        self.cmb_conc_doc.currentIndexChanged.connect(self._load_concordance)
        header_layout.addWidget(self.cmb_conc_doc)
        
        layout.addLayout(header_layout)
        
        # Splitter: Word list | Occurrences detail
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Word list with frequency and TQ
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search filter
        self.txt_conc_search = QLineEdit()
        self.txt_conc_search.setPlaceholderText("Filter words...")
        self.txt_conc_search.textChanged.connect(self._filter_concordance)
        left_layout.addWidget(self.txt_conc_search)
        
        self.tree_concordance = QTreeWidget()
        self.tree_concordance.setHeaderLabels(["Word", "Freq", "TQ"])
        self.tree_concordance.setColumnWidth(0, 180)
        self.tree_concordance.setColumnWidth(1, 50)
        self.tree_concordance.setColumnWidth(2, 60)
        self.tree_concordance.itemClicked.connect(self._on_concordance_word_selected)
        self.tree_concordance.setAlternatingRowColors(True)
        left_layout.addWidget(self.tree_concordance)
        
        splitter.addWidget(left_widget)
        
        # Right: Occurrence details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_occ_word = QLabel("Select a word to view occurrences")
        self.lbl_occ_word.setStyleSheet("font-weight: bold; font-size: 16px; color: #7c3aed;")
        right_layout.addWidget(self.lbl_occ_word)
        
        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #e5e7eb;")
        right_layout.addWidget(line)
        
        # Definitions section (collapsible)
        self.lbl_occ_definitions = QLabel("")
        self.lbl_occ_definitions.setWordWrap(True)
        self.lbl_occ_definitions.setStyleSheet("color: #4b5563; padding: 5px; background: #f3f4f6; border-radius: 4px;")
        right_layout.addWidget(self.lbl_occ_definitions)
        
        # Occurrences list with verse context
        self.list_occurrences = QListWidget()
        self.list_occurrences.setAlternatingRowColors(True)
        self.list_occurrences.setStyleSheet("""
            QListWidget::item { 
                padding: 8px; 
                border-bottom: 1px solid #e5e7eb;
            }
            QListWidget::item:hover {
                background-color: #ede9fe;
            }
        """)
        self.list_occurrences.itemDoubleClicked.connect(self._on_occurrence_double_clicked)
        right_layout.addWidget(self.list_occurrences)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter)
        
        self.tabs.addTab(tab, "📖 Concordance")
        
        # Load on tab change
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
    def _on_tab_changed(self, index):
        """Handle tab changes to load data lazily."""
        if self.tabs.tabText(index).startswith("📖"):
            self._load_concordance()
            
    def _load_concordance(self):
        """Load concordance data with current sort/filter settings."""
        # Get concordance stats
        stats = self.service.db.get_concordance_stats()
        
        total_words = stats.get('total_indexed_words', 0)
        total_occurrences = stats.get('total_occurrences', 0)
        doc_count = stats.get('indexed_documents', 0)
        
        self.lbl_concordance_stats.setText(
            f"Concordance: {total_words:,} words | {total_occurrences:,} occurrences | {doc_count} documents"
        )
        
        # Update document filter dropdown
        current_doc = self.cmb_conc_doc.currentData()
        self.cmb_conc_doc.blockSignals(True)
        self.cmb_conc_doc.clear()
        self.cmb_conc_doc.addItem("All Documents", None)
        
        for doc_id, title in stats.get('documents', []):
            self.cmb_conc_doc.addItem(title, doc_id)
        
        # Restore selection
        if current_doc:
            idx = self.cmb_conc_doc.findData(current_doc)
            if idx >= 0:
                self.cmb_conc_doc.setCurrentIndex(idx)
        self.cmb_conc_doc.blockSignals(False)
        
        # Determine sort order
        sort_idx = self.cmb_conc_sort.currentIndex()
        sort_options = [
            ('frequency', True),   # Freq high→low
            ('frequency', False),  # Freq low→high
            ('tq_value', True),    # TQ high→low
            ('tq_value', False),   # TQ low→high
            ('word', False),       # A→Z
            ('word', True),        # Z→A
        ]
        sort_by, desc = sort_options[sort_idx] if sort_idx < len(sort_options) else ('frequency', True)
        
        # Get document filter
        doc_filter = self.cmb_conc_doc.currentData()
        
        # Fetch words with occurrence counts
        words_data = self.service.db.get_concordance_words(
            document_id=doc_filter,
            sort_by=sort_by,
            descending=desc,
            limit=2000
        )
        
        # Populate tree
        self.tree_concordance.clear()
        self._concordance_data = words_data  # Cache for filtering
        
        for word, freq, tq_value, key_id in words_data:
            item = QTreeWidgetItem([word, str(freq), str(tq_value)])
            item.setData(0, Qt.ItemDataRole.UserRole, key_id)
            
            # Color-code by frequency
            if freq >= 10:
                item.setForeground(0, QColor("#7c3aed"))  # Purple for common
            elif freq >= 5:
                item.setForeground(0, QColor("#2563eb"))  # Blue for moderate
                
            self.tree_concordance.addTopLevelItem(item)
            
    def _filter_concordance(self, text):
        """Filter concordance tree by search text."""
        text = text.lower()
        for i in range(self.tree_concordance.topLevelItemCount()):
            item = self.tree_concordance.topLevelItem(i)
            word = item.text(0).lower()
            item.setHidden(text not in word)
            
    def _on_concordance_word_selected(self, item: QTreeWidgetItem, column: int):
        """Show occurrences for selected word."""
        key_id = item.data(0, Qt.ItemDataRole.UserRole)
        word = item.text(0)
        tq_value = item.text(2)
        
        self.lbl_occ_word.setText(f"{word}  (TQ: {tq_value})")
        
        # Get definitions
        definitions = self.service.db.get_definitions(key_id)
        if definitions:
            def_text = "\n".join([f"• [{d.type}] {d.content[:100]}..." if len(d.content) > 100 
                                  else f"• [{d.type}] {d.content}" for d in definitions[:3]])
            self.lbl_occ_definitions.setText(def_text)
            self.lbl_occ_definitions.setVisible(True)
        else:
            self.lbl_occ_definitions.setText("No definitions recorded")
            
        # Get occurrences
        occurrences = self.service.db.get_word_occurrences(key_id)
        
        self.list_occurrences.clear()
        for occ in occurrences:
            # Format: Document Title - Verse X: "...context..."
            verse_ref = f"Verse {occ.verse_number}" if occ.verse_number else "(prose)"
            display = f"{occ.document_title} — {verse_ref}\n   \"{occ.context_snippet}\""
            
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, occ)
            self.list_occurrences.addItem(item)
            
        if not occurrences:
            self.list_occurrences.addItem(QListWidgetItem("No verse occurrences recorded."))
            
    def _on_occurrence_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on occurrence to open source document."""
        occ = item.data(Qt.ItemDataRole.UserRole)
        if not occ:
            return
            
        # TODO: Open document in ExegesisWindow at specific verse
        QMessageBox.information(
            self, "Navigate to Verse",
            f"Document: {occ.document_title}\nVerse: {occ.verse_number}\n\n"
            f"Navigation to source document will be available in a future update."
        )

    # --- Enrichment Logic ---
    
    def _start_enrichment(self):
        """Start the background enrichment process."""
        if self.worker and self.worker.isRunning():
            return
            
        targets = self.service.get_undefined_keys()
        if not targets:
            QMessageBox.information(self, "Enrichment", "All keys already have definitions!")
            return
            
        count = len(targets)
        reply = QMessageBox.question(
            self, "Confirm Enrichment",
            f"Found {count} keys without definitions.\n"
            "Fetch meanings from external dictionaries?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.worker = EnrichmentWorker(self.service)
            self.worker.progress.connect(self._on_enrich_progress)
            self.worker.finished.connect(self._on_enrich_finished)
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_bar.setMaximum(count)
            self.statusBar().showMessage(f"Enrichment started ({count} keys)...")
            
            self.worker.start()
            
    def _on_enrich_progress(self, current, total, status):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.statusBar().showMessage(status)
        
    def _on_enrich_finished(self):
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Enrichment complete.")
        self._search_keys(self.txt_search.text())  # Refresh table
        QMessageBox.information(self, "Enrichment", "Lexicon enrichment completed successfully.")

    # --- Logic: Staging ---

    def _scan_text(self):
        text = self.txt_input.toPlainText()
        if not text.strip():
            return
            
        candidates = self.service.scan_text(text)
        self.list_candidates.clear()
        
        for word in candidates:
            item = QListWidgetItem(word)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked)  # Checked = Include (Opt-out workflow)
            self.list_candidates.addItem(item)
            
        self.statusBar().showMessage(f"Found {len(candidates)} candidates.")

    def _process_candidates(self):
        count = self.list_candidates.count()
        if count == 0:
            return
            
        added = 0
        ignored = 0
        source = self.txt_batch_source.text().strip() or "Magus"
        
        for i in range(count):
            item = self.list_candidates.item(i)
            word = item.text()
            
            if item.checkState() == Qt.CheckState.Checked:
                # Approve -> Master Key
                try:
                    self.service.approve_candidate(word, source=source)
                    added += 1
                except Exception as e:
                    logger.error(f"Error adding {word}: {e}")
            else:
                # Unchecked -> Ignore List
                self.service.ignore_candidate(word)
                ignored += 1
                
        self.statusBar().showMessage(f"Processed: {added} added, {ignored} ignored (Source: {source}).")
        self.list_candidates.clear()
        self.txt_input.clear()
        self._search_keys("")  # Refresh table
        self._update_stats()

    def _import_file(self):
        """Import text from a file with robust encoding handling."""
        from PyQt6.QtWidgets import QFileDialog
        from pathlib import Path
        
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Text", "", "Text Files (*.txt *.md *.doc *.docx);;All Files (*)"
        )
        if not path:
            return

        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']
        content = None
        used_encoding = None

        # Try to read with different encodings
        for enc in encodings:
            try:
                with open(path, 'r', encoding=enc) as f:
                    content = f.read()
                    used_encoding = enc
                    break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Read error ({enc}): {e}")
                return

        if content is not None:
            self.txt_input.setPlainText(content)
            
            # Auto-set source from filename (no extension)
            p = Path(path)
            clean_source = p.stem.replace("_", " ").title()
            self.txt_batch_source.setText(clean_source)
            
            self.statusBar().showMessage(f"Imported: {p.name} ({used_encoding})")
        else:
            QMessageBox.critical(
                self, 
                "Import Failed", 
                f"Could not decode file with standard encodings: {', '.join(encodings)}"
            )

    # --- Logic: Master Key ---
    
    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._search_keys(self.txt_search.text())
            
    def _next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._search_keys(self.txt_search.text())

    def _search_keys(self, query):
        if hasattr(self, 'txt_search') and self.txt_search.text() != query:
            # If search changed, reset to page 1
            self.current_page = 1
        
        # Determine sort order from combo box
        sort_by = 'word'  # default
        descending = False
        if hasattr(self, 'cmb_mk_sort'):
            sort_idx = self.cmb_mk_sort.currentIndex()
            sort_options = [
                ('word', False),       # Alphabetical
                ('tq_value', True),    # TQ Value (high first)
                ('frequency', True),   # Frequency (high first)
                ('id', True),          # Recently Added (high ID first)
            ]
            if sort_idx < len(sort_options):
                sort_by, descending = sort_options[sort_idx]
            
        keys, total_count = self.service.db.search_keys(
            query, 
            page=self.current_page, 
            page_size=self.page_size,
            sort_by=sort_by,
            descending=descending
        )
        
        # Update Pagination UI
        import math
        self.total_pages = math.ceil(total_count / self.page_size) if total_count > 0 else 1
        self.lbl_page.setText(f"Page {self.current_page} / {self.total_pages}")
        
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < self.total_pages)
        
        # Populate Table - temporarily disable sorting during population
        self.table_keys.setSortingEnabled(False)
        self.table_keys.setRowCount(0)
        self.table_keys.blockSignals(True)
        
        for row, key in enumerate(keys):
            self.table_keys.insertRow(row)
            
            # ID column
            id_item = QTableWidgetItem()
            id_item.setData(Qt.ItemDataRole.EditRole, key.id)
            self.table_keys.setItem(row, 0, id_item)
            
            # Word column
            self.table_keys.setItem(row, 1, QTableWidgetItem(key.word))
            
            # TQ Value column
            tq_item = QTableWidgetItem()
            tq_item.setData(Qt.ItemDataRole.EditRole, key.tq_value)
            self.table_keys.setItem(row, 2, tq_item)
            
            # Frequency column
            freq_item = QTableWidgetItem()
            freq_item.setData(Qt.ItemDataRole.EditRole, key.frequency)
            self.table_keys.setItem(row, 3, freq_item)
            
            # Store key_id for details lookup
            self.table_keys.item(row, 0).setData(Qt.ItemDataRole.UserRole, key.id)

        self.table_keys.blockSignals(False)
        self.table_keys.setSortingEnabled(True)
        
        # Connect double click (idempotent check)
        try:
            self.table_keys.cellDoubleClicked.disconnect()
        except TypeError:
            pass 
        self.table_keys.cellDoubleClicked.connect(self._open_key_details)

    def _update_stats(self):
        stats = self.service.get_lexicon_stats()
        self.tabs.setTabText(1, f"Master Key ({stats['total_keys']})")

    def _open_key_details(self, row, col):
        """Open detailed view for a Master Key with concordance data."""
        id_item = self.table_keys.item(row, 0)
        word_item = self.table_keys.item(row, 1)
        tq_item = self.table_keys.item(row, 2)
        
        if not id_item or not word_item:
            return
            
        key_id = int(id_item.text())
        word = word_item.text()
        tq_value = tq_item.text() if tq_item else "?"
        
        from PyQt6.QtWidgets import QDialog, QFormLayout, QTextEdit, QComboBox, QGroupBox, QTabWidget
        
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Key Details: {word} (TQ: {tq_value})")
        dlg.resize(700, 700)
        layout = QVBoxLayout(dlg)
        
        # Header with word info
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
        
        # Tabbed content: Definitions | Concordance
        detail_tabs = QTabWidget()
        layout.addWidget(detail_tabs)
        
        # === Tab 1: Definitions ===
        def_tab = QWidget()
        def_layout = QVBoxLayout(def_tab)
        
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
        
        # Add Definition Group
        group_add = QGroupBox("Add New Definition")
        def_layout.addWidget(group_add)
        add_layout = QVBoxLayout(group_add)
        
        # Fetch suggestions row
        box_suggestions = QHBoxLayout()
        btn_fetch = QPushButton("Fetch Suggestions")
        btn_fetch.setIcon(qta.icon("fa5s.cloud-download-alt", color="#2563eb"))
        
        cmb_suggestions = QComboBox()
        cmb_suggestions.setPlaceholderText("Select a suggestion to auto-fill...")
        cmb_suggestions.setEnabled(False)
        
        box_suggestions.addWidget(btn_fetch)
        box_suggestions.addWidget(cmb_suggestions, 1)
        add_layout.addLayout(box_suggestions)
        
        # Manual form
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
        
        # === Tab 2: Concordance (Verse References) ===
        conc_tab = QWidget()
        conc_layout = QVBoxLayout(conc_tab)
        
        # Get word occurrences from concordance
        word_occurrences = self.service.db.get_word_occurrences(key_id)
        
        lbl_occ_header = QLabel(f"Found in {len(word_occurrences)} verse(s):")
        lbl_occ_header.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        conc_layout.addWidget(lbl_occ_header)
        
        occ_list = QListWidget()
        occ_list.setAlternatingRowColors(True)
        occ_list.setStyleSheet("""
            QListWidget::item { 
                padding: 8px; 
                border-bottom: 1px solid #e5e7eb;
            }
        """)
        
        for occ in word_occurrences:
            verse_ref = f"Verse {occ.verse_number}" if occ.verse_number else "(prose)"
            display = f"{occ.document_title} — {verse_ref}"
            if occ.context_snippet:
                display += f"\n   \"{occ.context_snippet}\""
            
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, occ)
            occ_list.addItem(item)
            
        if not word_occurrences:
            occ_list.addItem(QListWidgetItem("No verse occurrences recorded.\n\nIndex a document from Holy Book Teacher to populate."))
            
        conc_layout.addWidget(occ_list)
        
        # Document frequency summary
        doc_freq = self.service.db.get_occurrences_by_document(key_id)
        if doc_freq:
            freq_text = "  |  ".join([f"{doc}: {count}" for doc, count in doc_freq.items()])
            lbl_freq = QLabel(f"<small>By document: {freq_text}</small>")
            lbl_freq.setStyleSheet("color: #6b7280; padding: 5px;")
            conc_layout.addWidget(lbl_freq)
        
        detail_tabs.addTab(conc_tab, f"Concordance ({len(word_occurrences)})")
        
        # === Fetch Suggestions Logic ===
        def fetch_suggs():
            btn_fetch.setText("Fetching...")
            btn_fetch.setEnabled(False)
            self.sugg_worker = SuggestionWorker(self.service, word)
            self.sugg_worker.finished.connect(on_fetch_done)
            self.sugg_worker.start()
            
        def on_fetch_done(suggestions):
            btn_fetch.setText("Fetch Suggestions")
            btn_fetch.setEnabled(True)
            cmb_suggestions.clear()
            cmb_suggestions.setEnabled(True)
            cmb_suggestions.addItem("--- Select a Suggestion ---")
            
            if not suggestions:
                QMessageBox.information(dlg, "Enrichment", "No external suggestions found.")
                return
                
            for s in suggestions:
                label = f"[{s.type}] {s.content[:60]}... ({s.source})"
                cmb_suggestions.addItem(label, s)
                
        def on_suggestion_selected(index):
            if index <= 0: return
            s = cmb_suggestions.itemData(index)
            if s:
                # Map suggestion type to combo
                type_map = {
                    'Etymology': 'Etymology',
                    'Standard': 'Standard',
                    'Alchemical': 'Alchemical',
                    'Botanical': 'Botanical',
                    'Occult': 'Occult',
                    'Divinatory': 'Divinatory',
                }
                mapped_type = type_map.get(s.type, 'Standard')
                cmb_type.setCurrentText(mapped_type)
                txt_content.setText(s.content)
                txt_source.setText(s.source)
        
        btn_fetch.clicked.connect(fetch_suggs)
        cmb_suggestions.currentIndexChanged.connect(on_suggestion_selected)
        
        # === Add Definition Logic ===
        def add_def():
            d_type = cmb_type.currentText()
            content = txt_content.toPlainText().strip()
            source = txt_source.text().strip()
            
            if not content:
                QMessageBox.warning(dlg, "Error", "Definition content cannot be empty.")
                return
                
            self.service.db.add_definition(key_id, d_type, content, source)
            
            # Refresh definitions list
            def_list.clear()
            updated_defs = self.service.db.get_definitions(key_id)
            for d in updated_defs:
                src_text = f" ({d.source})" if d.source else ""
                item = QListWidgetItem(f"[{d.type}] {d.content}{src_text}")
                item.setData(Qt.ItemDataRole.UserRole, d)
                def_list.addItem(item)
            
            # Update tab label
            detail_tabs.setTabText(0, f"Definitions ({len(updated_defs)})")
                
            txt_content.clear()
            txt_source.clear()
            QMessageBox.information(dlg, "Success", "Definition added.")
            self._update_stats()
            
        btn_add.clicked.connect(add_def)
        
        dlg.exec()

    def _reset_database(self):
        """Reset the Holy Key database."""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to delete ALL keys, definitions, and stats?\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.service.db.reset_database()
            self.statusBar().showMessage("Database reset complete.")
            self._search_keys("")
            self._update_stats()
            # Clear staging areas too if needed, though they are independent widgets
            self.list_candidates.clear()
