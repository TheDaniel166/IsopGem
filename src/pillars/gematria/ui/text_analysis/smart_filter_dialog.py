from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QProgressBar, QMessageBox, QSplitter, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from ...services.smart_filter_service import SmartFilterService

class FilterWorker(QThread):
    finished = pyqtSignal(list)
    
    def __init__(self, matches):
        super().__init__()
        self.matches = matches
        
    def run(self):
        service = SmartFilterService()
        valid = service.filter_phrases(self.matches)
        self.finished.emit(valid)

class SmartFilterDialog(QDialog):
    def __init__(self, matches, parent=None):
        super().__init__(parent)
        self.raw_matches = matches
        self.filtered_matches = []
        self.setWindowTitle("Smart Filter Results")
        self.resize(900, 600)
        self._setup_ui()
        self._start_filtering()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        self.status_lbl = QLabel("Initializing Spacy Model... (This may take a moment first time)")
        layout.addWidget(self.status_lbl)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0) # Indeterminate
        layout.addWidget(self.progress)
        
        # Splitter for Before/After
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Original
        original_widget = QWidget()
        l_layout = QVBoxLayout(original_widget)
        l_layout.addWidget(QLabel(f"Original Matches ({len(self.raw_matches)})"))
        self.list_original = QListWidget()
        # Populate original immediately (limit if huge?)
        for m in self.raw_matches[:1000]: # Cap preview
            self.list_original.addItem(m[0])
        if len(self.raw_matches) > 1000:
             self.list_original.addItem(f"... and {len(self.raw_matches)-1000} more")
        l_layout.addWidget(self.list_original)
        splitter.addWidget(original_widget)
        
        # Right: Filtered
        filtered_widget = QWidget()
        r_layout = QVBoxLayout(filtered_widget)
        self.lbl_filtered = QLabel("Filtered Matches (Waiting...)")
        r_layout.addWidget(self.lbl_filtered)
        self.list_filtered = QListWidget()
        r_layout.addWidget(self.list_filtered)
        splitter.addWidget(filtered_widget)
        
        layout.addWidget(splitter)
        
        # Footer
        btn_layout = QHBoxLayout()
        export_btn = QPushButton("Export Filtered")
        export_btn.clicked.connect(self._export_filtered)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(export_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
    def _start_filtering(self):
        self.worker = FilterWorker(self.raw_matches)
        self.worker.finished.connect(self._on_filtering_done)
        self.worker.start()
        
    def _on_filtering_done(self, valid_matches):
        self.filtered_matches = valid_matches
        self.progress.hide()
        self.status_lbl.setText("Filtering Complete.")
        
        count = len(valid_matches)
        removed = len(self.raw_matches) - count
        self.lbl_filtered.setText(f"Filtered Matches ({count}) - Removed {removed} rubbish")
        
        self.list_filtered.clear()
        for m in valid_matches:
            # m: (text, start, end, doc_title, tab_index)
            label = f"{m[0]} [{m[3]}]"
            self.list_filtered.addItem(label)
            
    def _export_filtered(self):
        if not self.filtered_matches:
            return
            
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Export Smart Results", "smart_results.txt", "Text Files (*.txt)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(f"Smart Filter Results\n")
                    f.write(f"Original Count: {len(self.raw_matches)}\n")
                    f.write(f"Filtered Count: {len(self.filtered_matches)}\n")
                    f.write("-" * 40 + "\n")
                    for m in self.filtered_matches:
                        f.write(f"[{m[3]}] {m[0]}\n")
                QMessageBox.information(self, "Exported", f"Saved to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))
