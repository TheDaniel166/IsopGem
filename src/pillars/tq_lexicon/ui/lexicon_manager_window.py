import logging
import qtawesome as qta
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QPushButton, QLineEdit, QSplitter, QTableWidget, 
    QTableWidgetItem, QCheckBox, QPlainTextEdit, QMessageBox,
    QHeaderView, QListWidget, QListWidgetItem, QMenu
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction

from ..services.holy_key_service import HolyKeyService

logger = logging.getLogger(__name__)

class LexiconManagerWindow(QMainWindow):
    """
    Sovereign Interface for managing the Holy Book Key.
    Allows the Magus to:
    1. Scan texts and curate candidates (Opt-out workflow)
    2. Manage the Master Key database
    """
    
    
    def __init__(self, window_manager=None, parent=None, **kwargs):
        super().__init__(parent)
        self.window_manager = window_manager
        self.setWindowTitle("Holy Key Lexicon")
        self.resize(1000, 700)
        
        # Initialize Service
        self.service = HolyKeyService()
        
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
        
        # Status Bar
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
        layout.addLayout(filter_layout)
        
        # Table
        self.table_keys = QTableWidget()
        self.table_keys.setColumnCount(3)
        self.table_keys.setHorizontalHeaderLabels(["ID", "Word", "TQ Value"])
        self.table_keys.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_keys)
        
        self.tabs.addTab(tab, "Master Key")
        
        # Initial Load
        self._search_keys("")

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
        
        for i in range(count):
            item = self.list_candidates.item(i)
            word = item.text()
            
            if item.checkState() == Qt.CheckState.Checked:
                # Approve -> Master Key
                try:
                    self.service.approve_candidate(word)
                    added += 1
                except Exception as e:
                    logger.error(f"Error adding {word}: {e}")
            else:
                # Unchecked -> Ignore List
                self.service.ignore_candidate(word)
                ignored += 1
                
        self.statusBar().showMessage(f"Processed: {added} added, {ignored} ignored.")
        self.list_candidates.clear()
        self.txt_input.clear()
        self._search_keys("")  # Refresh table
        self._update_stats()

    def _import_file(self):
        """Import text from a file with robust encoding handling."""
        from PyQt6.QtWidgets import QFileDialog
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
            self.statusBar().showMessage(f"Imported: {path} ({used_encoding})")
        else:
            QMessageBox.critical(
                self, 
                "Import Failed", 
                f"Could not decode file with standard encodings: {', '.join(encodings)}"
            )

    # --- Logic: Master Key ---

    def _search_keys(self, query):
        keys = self.service.db.search_keys(query)
        self.table_keys.setRowCount(0)
        self.table_keys.blockSignals(True)
        
        for row, key in enumerate(keys):
            self.table_keys.insertRow(row)
            self.table_keys.setItem(row, 0, QTableWidgetItem(str(key.id)))
            self.table_keys.setItem(row, 1, QTableWidgetItem(key.word))
            self.table_keys.setItem(row, 2, QTableWidgetItem(str(key.tq_value)))
            
            # Allow opening details on double click
            self.table_keys.item(row, 0).setData(Qt.ItemDataRole.UserRole, key.id)

        self.table_keys.blockSignals(False)
        # Connect double click if not already connected (check connection logic elsewhere or here idempotent)
        try:
            self.table_keys.cellDoubleClicked.disconnect()
        except TypeError:
            pass # Not connected
        self.table_keys.cellDoubleClicked.connect(self._open_key_details)

    def _update_stats(self):
        stats = self.service.get_lexicon_stats()
        self.tabs.setTabText(1, f"Master Key ({stats['total_keys']})")

    def _open_key_details(self, row, col):
        """Open a dialog to view/edit definitions and source."""
        key_id = self.table_keys.item(row, 0).data(Qt.ItemDataRole.UserRole)
        word = self.table_keys.item(row, 1).text()
        
        from PyQt6.QtWidgets import QDialog, QFormLayout, QTextEdit, QComboBox
        
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Key Details: {word}")
        dlg.resize(600, 500)
        layout = QVBoxLayout(dlg)
        
        # Definitions List
        def_list = QListWidget()
        definitions = self.service.db.get_definitions(key_id)
        
        for d in definitions:
            item = QListWidgetItem(f"[{d.type}] {d.content[:50]}... ({d.source})")
            item.setData(Qt.ItemDataRole.UserRole, d)
            def_list.addItem(item)
            
        layout.addWidget(QLabel("Definitions & Meanings:"))
        layout.addWidget(def_list)
        
        # Add New Definition Area
        form_layout = QFormLayout()
        
        cmb_type = QComboBox()
        cmb_type.addItems(['Etymology', 'Standard', 'Alchemical', 'Occult', 'Mythological'])
        
        txt_content = QTextEdit()
        txt_content.setMaximumHeight(100)
        
        txt_source = QLineEdit()
        txt_source.setPlaceholderText("e.g. Liber LUXORAT, Wikipedia, User Curation")
        txt_source.setText("Magus") # Default
        
        form_layout.addRow("Type:", cmb_type)
        form_layout.addRow("Meaning:", txt_content)
        form_layout.addRow("Source:", txt_source)
        
        layout.addLayout(form_layout)
        
        # Save Button
        btn_add = QPushButton("Add Definition")
        def add_def():
            content = txt_content.toPlainText().strip()
            source = txt_source.text().strip()
            if not content: return
            
            self.service.db.add_definition(key_id, cmb_type.currentText(), content, source)
            
            # Refresh list
            def_list.clear()
            new_defs = self.service.db.get_definitions(key_id)
            for d in new_defs:
                item = QListWidgetItem(f"[{d.type}] {d.content[:50]}... ({d.source})")
                item.setData(Qt.ItemDataRole.UserRole, d)
                def_list.addItem(item)
            
            txt_content.clear()
            
        btn_add.clicked.connect(add_def)
        layout.addWidget(btn_add)
        
        dlg.exec()
