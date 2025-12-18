from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import Optional

from .document_viewer import DocumentViewer
from .verse_list import VerseList
from pillars.document_manager.models.document import Document
from ...services.text_analysis_service import TextAnalysisService

class DocumentTab(QWidget):
    """
    A single document tab containing viewer, verse list, and controls.
    """
    # Signals to propagate up to main window
    text_selected = pyqtSignal(bool) # has_selection
    save_verse_requested = pyqtSignal(dict)
    save_all_requested = pyqtSignal(list)
    save_text_requested = pyqtSignal(str)
    open_quadset_requested = pyqtSignal(int)
    teach_requested = pyqtSignal()
    
    def __init__(self, document: Document, analysis_service: TextAnalysisService, parent=None):
        super().__init__(parent)
        self.document = document
        self.analysis_service = analysis_service
        self.current_calculator = None
        self.strict_parsing = True
        self.include_numbers = False
        
        self._setup_ui()
        self._load_document_content()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header / Toolbar specific to this tab (optional, or rely on main window toolbar)
        # We'll stick to the layout from main_window: Header with "Document Text" and "Calculate Selection"
        
        header = QHBoxLayout()
        self.viewer_label = QLabel("Document Text")
        self.viewer_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        header.addWidget(self.viewer_label)
        header.addStretch()
        
        self.calc_sel_btn = QPushButton("Calculate Selection")
        self.calc_sel_btn.clicked.connect(self._on_calculate_selection)
        self.calc_sel_btn.setEnabled(False)
        header.addWidget(self.calc_sel_btn)

        self.save_sel_btn = QPushButton("Save Selection")
        self.save_sel_btn.clicked.connect(self._on_save_selection)
        self.save_sel_btn.setEnabled(False)
        header.addWidget(self.save_sel_btn)
        layout.addLayout(header)
        
        # Stack
        self.stack = QStackedWidget()
        
        self.doc_viewer = DocumentViewer()
        self.doc_viewer.text_selected.connect(self._on_text_selection_changed)
        self.doc_viewer.save_requested.connect(self._on_viewer_save)
        self.doc_viewer.calculate_requested.connect(self._on_viewer_calculate)
        self.doc_viewer.send_to_quadset_requested.connect(self._on_viewer_quadset)
        self.stack.addWidget(self.doc_viewer)
        
        self.verse_list = VerseList()
        self.verse_list.verse_jump_requested.connect(self._on_verse_jump)
        self.verse_list.verse_save_requested.connect(self.save_verse_requested.emit)
        self.verse_list.save_all_requested.connect(self.save_all_requested.emit)
        self.stack.addWidget(self.verse_list)
        
        layout.addWidget(self.stack)
        
        # Selection Result Label
        self.sel_result_lbl = QLabel("")
        self.sel_result_lbl.setStyleSheet("color: #2563eb; font-weight: bold;")
        layout.addWidget(self.sel_result_lbl)
        
    def _load_document_content(self):
        if not self.document:
            return
            
        from PyQt6.QtGui import QTextDocument
        td = QTextDocument()
        td.setHtml(str(self.document.content or ""))
        plain = td.toPlainText()
        
        self.doc_viewer.set_text(plain)
        
    def set_view_mode(self, verse_mode: bool):
        if verse_mode:
            self.stack.setCurrentWidget(self.verse_list)
            self.viewer_label.setText("Verse List")
            self.refresh_verse_list()
        else:
            self.stack.setCurrentWidget(self.doc_viewer)
            self.viewer_label.setText("Document Text")
            
    def refresh_verse_list(self):
        if not self.document or not self.current_calculator:
            return
            
        text = self.doc_viewer.get_text()
        result = self.analysis_service.parse_verses(
            text, 
            self.document.id, 
            allow_inline=not self.strict_parsing
        )
        verses = result.get('verses', [])
        source = result.get('source', '')
        
        self.verse_list.render_verses(verses, self.current_calculator, self.include_numbers, f"Source: {source}")

    def update_settings(self, calculator, strict_parsing: bool, include_numbers: bool):
        self.current_calculator = calculator
        self.strict_parsing = strict_parsing
        self.include_numbers = include_numbers
        
        # If in verse mode, refresh
        if self.stack.currentWidget() == self.verse_list:
            self.refresh_verse_list()
            
    def get_text(self) -> str:
        return self.doc_viewer.get_text()
        
    def highlight_ranges(self, ranges):
        self.doc_viewer.highlight_ranges(ranges)
        
    def clear_highlights(self):
        self.doc_viewer.clear_highlights()
        
    def _on_text_selection_changed(self):
        txt = self.doc_viewer.get_selected_text()
        has_sel = bool(txt)
        has_sel = bool(txt)
        self.calc_sel_btn.setEnabled(has_sel)
        self.save_sel_btn.setEnabled(has_sel)
        self.text_selected.emit(has_sel)
        if not txt:
            self.sel_result_lbl.setText("")
            
    def _on_calculate_selection(self):
        txt = self.doc_viewer.get_selected_text()
        if not txt or not self.current_calculator:
            return
        val = self.analysis_service.calculate_text(txt, self.current_calculator, self.include_numbers)
        self.sel_result_lbl.setText(f"Value: {val}")
        
    def _on_verse_jump(self, start, end):
        # Switch to text view and highlight
        # We need to tell parent to switch toggle? Or just switch locally?
        # Creating a seamless experience implies switching locally but sync might be needed.
        # For now, switch locally.
        self.set_view_mode(False) 
        # But wait, the checkbox in main window needs to update. 
        # We might need a signal 'view_mode_changed'.
        self.doc_viewer.select_range(start, end)

    def _on_save_selection(self):
        txt = self.doc_viewer.get_selected_text()
        if txt:
            self.save_text_requested.emit(txt)

    def _on_viewer_save(self, text):
        self.save_text_requested.emit(text)

    def _on_viewer_calculate(self, text):
        # We can just run the calculation logic
        if not text or not self.current_calculator:
            return
        val = self.analysis_service.calculate_text(text, self.current_calculator, self.include_numbers)
        self.sel_result_lbl.setText(f"Value: {val}")

    def _on_viewer_quadset(self, text):
        if not text or not self.current_calculator:
            return
        val = self.analysis_service.calculate_text(text, self.current_calculator, self.include_numbers)
        self.open_quadset_requested.emit(val)
