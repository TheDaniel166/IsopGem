"""
Unified Holy Book Concordance Window.

Combines document parsing and concordance indexing into a single streamlined interface.
Documents are parsed and indexed in one cohesive operation.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTextEdit,
    QProgressBar,
    QSplitter,
    QComboBox,
    QCheckBox,
    QMessageBox,
    QFrame,
)

logger = logging.getLogger(__name__)


class ParseAndIndexWorker(QThread):
    """Background worker for unified parse + index operation."""
    
    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(object)  # ParseAndIndexResult
    error = pyqtSignal(str)
    
    def __init__(
        self,
        document_id: int,
        allow_inline: bool = True,
        apply_rules: bool = True,
        auto_save: bool = True,
        reindex: bool = False,
    ):
        super().__init__()
        self.document_id = document_id
        self.allow_inline = allow_inline
        self.apply_rules = apply_rules
        self.auto_save = auto_save
        self.reindex = reindex
        
    def run(self):
        try:
            from shared.services.lexicon.concordance_indexer_service import (
                ConcordanceIndexerService,
            )
            
            indexer = ConcordanceIndexerService()
            result = indexer.parse_and_index(
                document_id=self.document_id,
                allow_inline=self.allow_inline,
                apply_rules=self.apply_rules,
                auto_save=self.auto_save,
                reindex=self.reindex,
                progress_callback=self._emit_progress,
            )
            self.finished.emit(result)
        except Exception as e:
            logger.exception("Parse and index failed")
            self.error.emit(str(e))
            
    def _emit_progress(self, current: int, total: int, message: str):
        self.progress.emit(current, total, message)


class HolyBookConcordanceWindow(QMainWindow):
    """
    Unified window for parsing holy books and indexing to the concordance.
    
    This window combines what was previously two separate workflows:
    1. Parse document into verses (HolyBookTeacherWindow)
    2. Index verses to concordance (ConcordanceIndexerService)
    
    Into a single streamlined interface where documents are parsed AND indexed
    in one cohesive operation.
    """
    
    documents_updated = pyqtSignal()  # Emitted when indexing changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Holy Book Concordance [DEPRECATED - Use Unified Window]")
        self.resize(1100, 750)
        
        from shared.services.lexicon.holy_key_service import HolyKeyService
        from shared.services.document_manager.document_service import DocumentService

        self.service = HolyKeyService()
        self.document_service = DocumentService()
        self._documents: List[Dict[str, Any]] = []
        self._current_worker: Optional[ParseAndIndexWorker] = None
        
        self._build_ui()
        self._load_documents()
        
    def _build_ui(self):
        """Build the main UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)
        
        # Header
        header = self._build_header()
        layout.addWidget(header)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Document list
        doc_panel = self._build_document_panel()
        splitter.addWidget(doc_panel)
        
        # Right: Details and results
        details_panel = self._build_details_panel()
        splitter.addWidget(details_panel)
        
        splitter.setSizes([400, 700])
        layout.addWidget(splitter, 1)
        
        # Bottom: Progress and actions
        bottom = self._build_bottom_panel()
        layout.addWidget(bottom)
        
    def _build_header(self) -> QWidget:
        """Build header with title and stats."""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("📚 Holy Book Concordance")
        title.setStyleSheet("font-size: 18pt; font-weight: 600; color: #1e293b;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Quick stats
        self.stats_label = QLabel("Loading...")
        self.stats_label.setStyleSheet("color: #64748b; font-size: 10pt;")
        layout.addWidget(self.stats_label)
        
        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.clicked.connect(self._load_documents)
        layout.addWidget(refresh_btn)
        
        return header
        
    def _build_document_panel(self) -> QWidget:
        """Build left panel with document list."""
        panel = QGroupBox("Holy Books")
        layout = QVBoxLayout(panel)
        
        # Filter row
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Filter:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Not Indexed", "Indexed", "Needs Update"])
        self.filter_combo.currentTextChanged.connect(self._apply_filter)
        filter_row.addWidget(self.filter_combo, 1)
        layout.addLayout(filter_row)
        
        # Document table
        self.doc_table = QTableWidget(0, 4)
        self.doc_table.setHorizontalHeaderLabels(["Title", "Verses", "Indexed", "Words"])
        self.doc_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.doc_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.doc_table.itemSelectionChanged.connect(self._on_doc_selected)
        self.doc_table.cellDoubleClicked.connect(self._on_doc_double_clicked)
        
        header = self.doc_table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            
        layout.addWidget(self.doc_table)
        
        return panel
        
    def _build_details_panel(self) -> QWidget:
        """Build right panel with document details."""
        panel = QGroupBox("Document Details")
        layout = QVBoxLayout(panel)
        
        # Document info
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        info_layout = QVBoxLayout(info_frame)
        
        self.doc_title_label = QLabel("Select a document")
        self.doc_title_label.setStyleSheet("font-size: 14pt; font-weight: 600;")
        info_layout.addWidget(self.doc_title_label)
        
        self.doc_status_label = QLabel("")
        self.doc_status_label.setStyleSheet("color: #64748b;")
        info_layout.addWidget(self.doc_status_label)
        
        layout.addWidget(info_frame)
        
        # Options
        options_group = QGroupBox("Parse & Index Options")
        options_layout = QVBoxLayout(options_group)
        
        self.inline_check = QCheckBox("Allow inline verse markers")
        self.inline_check.setChecked(True)
        self.inline_check.setToolTip("Detect verse markers within paragraphs (e.g., '1. ...', '2. ...')")
        options_layout.addWidget(self.inline_check)
        
        self.rules_check = QCheckBox("Apply parsing rules")
        self.rules_check.setChecked(True)
        self.rules_check.setToolTip("Apply any stored rules for this document")
        options_layout.addWidget(self.rules_check)
        
        self.autosave_check = QCheckBox("Auto-save verses as curated")
        self.autosave_check.setChecked(True)
        self.autosave_check.setToolTip("Automatically save parsed verses for future use")
        options_layout.addWidget(self.autosave_check)
        
        self.reindex_check = QCheckBox("Force re-index (clear existing)")
        self.reindex_check.setChecked(False)
        self.reindex_check.setToolTip("Clear and rebuild the index for this document")
        options_layout.addWidget(self.reindex_check)
        
        layout.addWidget(options_group)
        
        # Results preview
        results_group = QGroupBox("Results Preview")
        results_layout = QVBoxLayout(results_group)
        
        self.results_view = QTextEdit()
        self.results_view.setReadOnly(True)
        self.results_view.setStyleSheet("font-family: monospace; font-size: 10pt;")
        self.results_view.setPlaceholderText("Results will appear here after processing...")
        results_layout.addWidget(self.results_view)
        
        layout.addWidget(results_group, 1)
        
        return panel
        
    def _build_bottom_panel(self) -> QWidget:
        """Build bottom panel with progress and actions."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Progress bar
        progress_row = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_row.addWidget(self.progress_bar, 1)
        
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #64748b;")
        progress_row.addWidget(self.progress_label)
        layout.addLayout(progress_row)
        
        # Action buttons
        btn_row = QHBoxLayout()
        
        self.parse_only_btn = QPushButton("📝 Parse Only")
        self.parse_only_btn.setToolTip("Parse document into verses without indexing")
        self.parse_only_btn.clicked.connect(self._on_parse_only)
        self.parse_only_btn.setEnabled(False)
        btn_row.addWidget(self.parse_only_btn)
        
        self.parse_and_index_btn = QPushButton("🚀 Parse && Index")
        self.parse_and_index_btn.setToolTip("Parse document AND index all words to concordance")
        self.parse_and_index_btn.setProperty("archetype", "magus")
        self.parse_and_index_btn.clicked.connect(self._on_parse_and_index)
        self.parse_and_index_btn.setEnabled(False)
        btn_row.addWidget(self.parse_and_index_btn)
        
        btn_row.addStretch()
        
        self.view_lexicon_btn = QPushButton("📖 Open Lexicon Manager")
        self.view_lexicon_btn.clicked.connect(self._open_lexicon_manager)
        btn_row.addWidget(self.view_lexicon_btn)
        
        self.advanced_btn = QPushButton("⚙️ Advanced (Teacher)")
        self.advanced_btn.setToolTip("Open detailed verse editor for manual curation")
        self.advanced_btn.clicked.connect(self._open_teacher_window)
        self.advanced_btn.setEnabled(False)
        btn_row.addWidget(self.advanced_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_row.addWidget(close_btn)
        
        layout.addLayout(btn_row)
        
        return panel
        
    def _load_documents(self):
        """Load holy book documents and their status."""
        try:
            from shared.database import get_db_session
            from shared.repositories.document_manager.document_repository import DocumentRepository
            from shared.services.lexicon.concordance_indexer_service import ConcordanceIndexerService
            
            indexer = ConcordanceIndexerService()
            
            with get_db_session() as db:
                doc_repo = DocumentRepository(db)
                # Get documents tagged as holy books (or all documents for now)
                documents = doc_repo.get_all()
                
            self._documents = []
            for doc in documents:
                status = indexer.get_document_status(doc.id)
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
            
        except Exception as e:
            logger.exception("Failed to load documents")
            QMessageBox.critical(self, "Error", f"Failed to load documents:\n{e}")
            
    def _populate_doc_table(self, documents: Optional[List[Dict]] = None):
        """Populate the document table."""
        if documents is None:
            documents = self._documents
            
        self.doc_table.setRowCount(len(documents))
        
        for row, doc in enumerate(documents):
            # Title
            title_item = QTableWidgetItem(doc['title'])
            title_item.setData(Qt.ItemDataRole.UserRole, doc)
            self.doc_table.setItem(row, 0, title_item)
            
            # Verse count
            verse_item = QTableWidgetItem(str(doc['verse_count']) if doc['verse_count'] else "-")
            verse_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.doc_table.setItem(row, 1, verse_item)
            
            # Indexed status
            if doc['is_indexed']:
                status = "✓"
            elif doc['has_curated']:
                status = "○"
            else:
                status = "—"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setForeground(Qt.GlobalColor.darkGreen if doc['is_indexed'] else Qt.GlobalColor.gray)
            self.doc_table.setItem(row, 2, status_item)
            
            # Word count
            word_item = QTableWidgetItem(str(doc['occurrence_count']) if doc['occurrence_count'] else "-")
            word_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.doc_table.setItem(row, 3, word_item)
            
    def _apply_filter(self, filter_text: str):
        """Apply filter to document list."""
        if filter_text == "All":
            filtered = self._documents
        elif filter_text == "Not Indexed":
            filtered = [d for d in self._documents if not d['is_indexed']]
        elif filter_text == "Indexed":
            filtered = [d for d in self._documents if d['is_indexed']]
        elif filter_text == "Needs Update":
            filtered = [d for d in self._documents if d['has_curated'] and not d['is_indexed']]
        else:
            filtered = self._documents
            
        self._populate_doc_table(filtered)
        
    def _update_stats(self):
        """Update the stats label."""
        total = len(self._documents)
        indexed = sum(1 for d in self._documents if d['is_indexed'])
        self.stats_label.setText(f"{indexed}/{total} documents indexed")
        
    def _get_selected_document(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected document."""
        rows = self.doc_table.selectionModel().selectedRows()
        if not rows:
            return None
        row = rows[0].row()
        item = self.doc_table.item(row, 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None
        
    def _on_doc_selected(self):
        """Handle document selection change."""
        doc = self._get_selected_document()
        
        if not doc:
            self.doc_title_label.setText("Select a document")
            self.doc_status_label.setText("")
            self.parse_only_btn.setEnabled(False)
            self.parse_and_index_btn.setEnabled(False)
            self.advanced_btn.setEnabled(False)
            return
            
        self.doc_title_label.setText(doc['title'])
        
        # Build status text
        status_parts = []
        if doc['has_curated']:
            status_parts.append(f"📝 {doc['verse_count']} curated verses")
        else:
            status_parts.append("📄 Not yet parsed")
            
        if doc['is_indexed']:
            status_parts.append(f"📚 {doc['occurrence_count']} word occurrences indexed")
        else:
            status_parts.append("🔍 Not indexed")
            
        self.doc_status_label.setText(" · ".join(status_parts))
        
        # Enable buttons
        self.parse_only_btn.setEnabled(True)
        self.parse_and_index_btn.setEnabled(True)
        self.advanced_btn.setEnabled(True)
        
        # Auto-check reindex if already indexed
        self.reindex_check.setChecked(doc['is_indexed'])
        
    def _on_doc_double_clicked(self, row: int, _col: int):
        """Handle double-click on document row."""
        self._on_parse_and_index()
        
    def _on_parse_only(self):
        """Parse document without indexing."""
        doc = self._get_selected_document()
        if not doc:
            return
            
        try:
            from shared.services.lexicon.concordance_indexer_service import ConcordanceIndexerService
            
            self._set_processing(True)
            self.progress_label.setText("Parsing...")
            
            indexer = ConcordanceIndexerService()
            result = indexer.parse_document(
                document_id=doc['id'],
                allow_inline=self.inline_check.isChecked(),
                apply_rules=self.rules_check.isChecked(),
                force_reparse=True,
            )
            
            # Show results
            verses = result.get('verses', [])
            self.results_view.setPlainText(
                f"✓ Parsed '{doc['title']}'\n\n"
                f"Verses found: {len(verses)}\n"
                f"Source: {result.get('source', 'parser')}\n\n"
                f"Anomalies:\n{self._format_anomalies(result.get('anomalies', {}))}\n\n"
                f"First 5 verses:\n" + "\n".join(
                    f"  {v.get('number')}: {(v.get('text', '')[:80])}..."
                    for v in verses[:5]
                )
            )
            
            self._set_processing(False)
            self._load_documents()  # Refresh status
            
        except Exception as e:
            self._set_processing(False)
            logger.exception("Parse failed")
            QMessageBox.critical(self, "Error", f"Parse failed:\n{e}")
            
    def _on_parse_and_index(self):
        """Run unified parse + index operation."""
        doc = self._get_selected_document()
        if not doc:
            return
            
        # Confirm reindex if needed
        if doc['is_indexed'] and self.reindex_check.isChecked():
            reply = QMessageBox.question(
                self,
                "Re-index Document",
                f"'{doc['title']}' is already indexed.\n\n"
                "This will clear existing word occurrences and rebuild the index.\n\n"
                "Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
                
        # Start worker
        self._set_processing(True)
        self.results_view.clear()
        
        self._current_worker = ParseAndIndexWorker(
            document_id=doc['id'],
            allow_inline=self.inline_check.isChecked(),
            apply_rules=self.rules_check.isChecked(),
            auto_save=self.autosave_check.isChecked(),
            reindex=self.reindex_check.isChecked(),
        )
        self._current_worker.progress.connect(self._on_progress)
        self._current_worker.finished.connect(self._on_finished)
        self._current_worker.error.connect(self._on_error)
        self._current_worker.start()
        
    def _on_progress(self, current: int, total: int, message: str):
        """Handle progress updates."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_label.setText(message)
        
    def _on_finished(self, result):
        """Handle completion."""
        self._set_processing(False)
        self._current_worker = None
        
        # Format results
        lines = [
            f"✓ Completed: '{result.document_title}'\n",
            "=" * 40,
            "\n📝 PARSING:",
            f"  Verses found: {len(result.verses)}",
            f"  Source: {result.source}",
            f"  Verses saved: {'Yes' if result.verses_saved else 'No'}",
        ]
        
        if result.anomalies:
            lines.append(f"\n  Anomalies:\n{self._format_anomalies(result.anomalies)}")
            
        lines.extend([
            "\n📚 INDEXING:",
            f"  Words processed: {result.total_words}",
            f"  New keys added: {result.new_keys_added}",
            f"  Occurrences recorded: {result.occurrences_added}",
        ])
        
        if result.errors:
            lines.append(f"\n⚠️ Errors ({len(result.errors)}):")
            for err in result.errors[:5]:
                lines.append(f"  - {err}")
            if len(result.errors) > 5:
                lines.append(f"  ... and {len(result.errors) - 5} more")
                
        self.results_view.setPlainText("\n".join(lines))
        
        # Refresh document list
        self._load_documents()
        self.documents_updated.emit()
        
        QMessageBox.information(
            self,
            "Complete",
            f"'{result.document_title}' has been parsed and indexed.\n\n"
            f"• {len(result.verses)} verses\n"
            f"• {result.total_words} words processed\n"
            f"• {result.new_keys_added} new keys\n"
            f"• {result.occurrences_added} occurrences recorded",
        )
        
    def _on_error(self, error_msg: str):
        """Handle error."""
        self._set_processing(False)
        self._current_worker = None
        
        self.results_view.setPlainText(f"❌ Error:\n{error_msg}")
        QMessageBox.critical(self, "Error", f"Operation failed:\n{error_msg}")
        
    def _set_processing(self, processing: bool):
        """Enable/disable UI during processing."""
        self.progress_bar.setVisible(processing)
        self.parse_only_btn.setEnabled(not processing)
        self.parse_and_index_btn.setEnabled(not processing)
        self.advanced_btn.setEnabled(not processing)
        self.doc_table.setEnabled(not processing)
        
        if processing:
            self.progress_bar.setValue(0)
            self.progress_label.setText("Starting...")
        else:
            self.progress_label.setText("")
            
    def _format_anomalies(self, anomalies: Dict[str, Any]) -> str:
        """Format anomalies dict for display."""
        if not anomalies:
            return "  None detected"
            
        lines = []
        if anomalies.get('duplicates'):
            lines.append(f"    Duplicates: {anomalies['duplicates']}")
        if anomalies.get('missing_numbers'):
            lines.append(f"    Missing: {anomalies['missing_numbers']}")
        if anomalies.get('overlaps'):
            lines.append(f"    Overlaps: {len(anomalies['overlaps'])} found")
            
        return "\n".join(lines) if lines else "  None detected"
        
    def _open_lexicon_manager(self):
        """Open the Lexicon Manager window."""
        try:
            from shared.signals.navigation_bus import navigation_bus
            navigation_bus.request_window.emit("lexicon_manager", {})
        except Exception as e:
            logger.exception("Failed to open Lexicon Manager")
            QMessageBox.critical(self, "Error", f"Failed to open Lexicon Manager:\n{e}")

    def _open_teacher_window(self):
        """Open the detailed verse teacher window via NavigationBus."""
            
        doc = self._get_selected_document()
        if not doc:
            return
            
        try:
            from shared.signals.navigation_bus import navigation_bus
            
            navigation_bus.request_window.emit("holy_book_teacher", {
                "document_id": doc['id'],
                "document_title": doc['title'],
                "allow_inline": self.inline_check.isChecked()
            })
            
            # Note: We can't connect to signals easily via bus (yet), 
            # so autorefresh might need a general 'document_updated' signal on the bus later.
            # For now, user can click refresh.
            
        except Exception as e:
            logger.exception("Failed to request Teacher window")
            QMessageBox.critical(self, "Error", f"Failed to open Teacher window:\n{e}")
