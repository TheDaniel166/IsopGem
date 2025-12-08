from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QComboBox, QCheckBox, QStackedWidget,
    QMessageBox, QInputDialog, QTabWidget, QFileDialog
)
from PyQt6.QtCore import Qt
from typing import List, Optional, Any, Dict

from ...services.base_calculator import GematriaCalculator
from ...services import CalculationService
from ...services.text_analysis_service import TextAnalysisService
from pillars.document_manager.services.document_service import document_service_context
from pillars.document_manager.models.document import Document

# Components
from .search_panel import SearchPanel
from .document_tab import DocumentTab
from .stats_panel import StatsPanel
from .smart_filter_dialog import SmartFilterDialog
from ..holy_book_teacher_window import HolyBookTeacherWindow

import logging

class TextAnalysisWindow(QMainWindow):
    """
    MDI Text Analysis Window using Tabs.
    """
    
    def __init__(self, calculators: List[GematriaCalculator], parent=None):
        super().__init__(parent)
        self.calculators = {c.name: c for c in calculators}
        self.current_calculator = calculators[0]
        # Default to English TQ if available
        eng_tq = next((c for c in calculators if "English TQ" in c.name), None)
        tq = next((c for c in calculators if "TQ" in c.name), None)
        eng = next((c for c in calculators if "English" in c.name), None)
        
        if eng_tq:
            self.current_calculator = eng_tq
        elif tq:
            self.current_calculator = tq
        elif eng:
            self.current_calculator = eng
                
        self.calc_service = CalculationService()
        self.analysis_service = TextAnalysisService()
        
        self._setup_ui()
        self._load_documents()
        
    def _setup_ui(self):
        self.setWindowTitle("Gematria Text Analysis")
        self.resize(1200, 800)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # --- Toolbar ---
        toolbar = QHBoxLayout()
        
        # Document Selector
        toolbar.addWidget(QLabel("Add Document:"))
        self.doc_combo = QComboBox()
        self.doc_combo.setMinimumWidth(250)
        toolbar.addWidget(self.doc_combo)
        
        open_btn = QPushButton("Open Tab")
        open_btn.clicked.connect(self._on_open_document)
        toolbar.addWidget(open_btn)
        
        toolbar.addSpacing(15)
        
        # Method Selector
        toolbar.addWidget(QLabel("Method:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(list(self.calculators.keys()))
        self.method_combo.setCurrentText(self.current_calculator.name)
        self.method_combo.currentTextChanged.connect(self._on_method_changed)
        toolbar.addWidget(self.method_combo)
        
        # Options
        self.holy_view_chk = QCheckBox("Holy Book View")
        self.holy_view_chk.toggled.connect(self._on_view_mode_toggled)
        toolbar.addWidget(self.holy_view_chk)
        
        self.strict_verse_chk = QCheckBox("Strict Parsing")
        self.strict_verse_chk.setChecked(True)
        self.strict_verse_chk.toggled.connect(self._on_options_changed)
        toolbar.addWidget(self.strict_verse_chk)
        
        self.include_nums_chk = QCheckBox("Include Numbers")
        self.include_nums_chk.stateChanged.connect(self._on_options_changed)
        toolbar.addWidget(self.include_nums_chk)
        
        self.teach_btn = QPushButton("Teach Parser")
        self.teach_btn.setEnabled(False) # Enable if tab active
        self.teach_btn.clicked.connect(self._open_teacher)
        toolbar.addWidget(self.teach_btn)
        
        toolbar.addStretch()
        main_layout.addLayout(toolbar)
        
        # --- Main Splitter ---
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Tabs for Documents
        self.doc_tabs = QTabWidget()
        self.doc_tabs.setTabsClosable(True)
        self.doc_tabs.tabCloseRequested.connect(self._on_tab_close)
        self.doc_tabs.currentChanged.connect(self._on_tab_changed)
        
        splitter.addWidget(self.doc_tabs)
        
        # Right: Tools (Tabs)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tools_tabs = QTabWidget()
        
        # Search Tab
        self.search_panel = SearchPanel()
        self.search_panel.search_requested.connect(self._on_search)
        self.search_panel.result_selected.connect(self._on_search_result_selected)
        self.search_panel.clear_requested.connect(self._on_clear_search)
        self.search_panel.save_matches_requested.connect(self._on_save_matches)
        self.search_panel.export_requested.connect(self._on_export_results)
        self.search_panel.smart_filter_requested.connect(self._on_smart_filter)
        self.tools_tabs.addTab(self.search_panel, "Search")
        
        # Stats Tab
        self.stats_panel = StatsPanel()
        self.tools_tabs.addTab(self.stats_panel, "Stats")
        
        right_layout.addWidget(self.tools_tabs)
        splitter.addWidget(right_widget)
        
        splitter.setSizes([800, 400])
        main_layout.addWidget(splitter)
        
        # Status Bar
        self.status = QLabel("Ready")
        main_layout.addWidget(self.status)
        
    def _load_documents(self):
        try:
            with document_service_context() as service:
                docs = service.get_all_documents()
                self.doc_combo.clear()
                self.doc_combo.addItem("-- Select Document to Open --", None)
                for d in docs:
                    collection = (d.collection or "").lower()
                    tags = (str(d.tags) if d.tags else "").lower()
                    if "holy" in collection or "holy" in tags:
                        self.doc_combo.addItem(f"{d.title}", d.id)
        except Exception as e:
            self.status.setText(f"Error loading docs: {e}")
            
    def _on_open_document(self):
        doc_id = self.doc_combo.currentData()
        if not doc_id:
            return
            
        # Check if already open
        for i in range(self.doc_tabs.count()):
            tab = self.doc_tabs.widget(i)
            if isinstance(tab, DocumentTab) and tab.document.id == doc_id:
                self.doc_tabs.setCurrentIndex(i)
                return
        
        # Load document
        try:
            with document_service_context() as service:
                document = service.get_document(doc_id)
            if not document:
                return
                
            tab = DocumentTab(document, self.analysis_service)
            # Connect signals
            tab.save_verse_requested.connect(self._on_save_verse)
            tab.save_all_requested.connect(self._on_save_all_verses)
            # Init settings
            tab.update_settings(
                self.current_calculator,
                self.strict_verse_chk.isChecked(),
                self.include_nums_chk.isChecked()
            )
            # If global "Holy Book View" is checked, set it
            tab.set_view_mode(self.holy_view_chk.isChecked())
            
            index = self.doc_tabs.addTab(tab, document.title)
            self.doc_tabs.setCurrentIndex(index)
            self.status.setText(f"Opened: {document.title}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open document: {e}")
            
    def _on_tab_close(self, index):
        self.doc_tabs.removeTab(index)
        
    def _on_tab_changed(self, index):
        tab = self.doc_tabs.widget(index)
        if isinstance(tab, DocumentTab):
            self.teach_btn.setEnabled(True)
            self._update_stats_for_tab(tab)
        else:
            self.teach_btn.setEnabled(False)
            
        # Update Search Panel with active tab index
        self.search_panel.set_active_tab(index)
            
    def _on_method_changed(self, name):
        if name in self.calculators:
            self.current_calculator = self.calculators[name]
            self._propagate_settings()
            
    def _on_options_changed(self):
        self._propagate_settings()
        
    def _propagate_settings(self):
        strict = self.strict_verse_chk.isChecked()
        nums = self.include_nums_chk.isChecked()
        
        for i in range(self.doc_tabs.count()):
            tab = self.doc_tabs.widget(i)
            if isinstance(tab, DocumentTab):
                tab.update_settings(self.current_calculator, strict, nums)
                
        # Update stats for current tab
        current = self.doc_tabs.currentWidget()
        if isinstance(current, DocumentTab):
            self._update_stats_for_tab(current)

    def _on_view_mode_toggled(self, checked):
        # Apply to current tab or all tabs? 
        # Requirement says "Tab per document", view mode could be per tab or global.
        # User toggles toolbar checkbox -> applies to ACTIVE tab usually, or all?
        # Let's apply to ACTIVE tab for flexibility, but wait, the toolbar is global.
        # Let's apply to ALL tabs to keep it consistent with the global toolbar state.
        for i in range(self.doc_tabs.count()):
            tab = self.doc_tabs.widget(i)
            if isinstance(tab, DocumentTab):
                tab.set_view_mode(checked)

    def _update_stats_for_tab(self, tab: DocumentTab):
        text = tab.get_text()
        stats = self.analysis_service.calculate_stats(text, self.current_calculator)
        self.stats_panel.update_stats(stats)
        
    # --- Search ---
    
    def _on_search(self, val, max_words, is_global):
        tabs_to_search = []
        if is_global:
            for i in range(self.doc_tabs.count()):
                widget = self.doc_tabs.widget(i)
                if isinstance(widget, DocumentTab):
                    tabs_to_search.append((i, widget))
        else:
            current = self.doc_tabs.currentIndex()
            widget = self.doc_tabs.widget(current)
            if isinstance(widget, DocumentTab):
                tabs_to_search.append((current, widget))
                
        if not tabs_to_search:
            return
            
        all_matches = []
        include_nums = self.include_nums_chk.isChecked()
        
        for index, tab in tabs_to_search:
            text = tab.get_text()
            matches = self.analysis_service.find_value_matches(
                text, val, self.current_calculator, include_nums, max_words
            )
            # Augment with doc info
            # Format: (text, start, end, doc_title, tab_index)
            for m_text, start, end in matches:
                all_matches.append((m_text, start, end, tab.document.title, index))
                
        self.search_panel.set_results(all_matches)
        
        # Ensure panel knows current tab
        current_idx = self.doc_tabs.currentIndex()
        self.search_panel.set_active_tab(current_idx)
        
        # Highlight matches in CURRENT tab only to avoid confusion / perf cost
        # Or highlight all if global?
        # Let's highlight current tab results
        self.doc_tabs.currentWidget().clear_highlights()
        if not is_global and tabs_to_search:
            ranges = [(m[1], m[2]) for m in all_matches]
            self.doc_tabs.currentWidget().highlight_ranges(ranges)
            
    def _on_search_result_selected(self, start, end, tab_index):
        # Switch to tab
        if tab_index >= 0 and tab_index < self.doc_tabs.count():
            self.doc_tabs.setCurrentIndex(tab_index)
            # Ensure text mode
            self.holy_view_chk.setChecked(False) # triggers signal to switch view mode
            
            tab = self.doc_tabs.widget(tab_index)
            if isinstance(tab, DocumentTab):
                tab.set_view_mode(False) # Force local Update
                tab.doc_viewer.select_range(start, end)
                
    def _on_clear_search(self):
        self.search_panel.clear_results()
        # Clear highlights in all tabs
        for i in range(self.doc_tabs.count()):
            tab = self.doc_tabs.widget(i)
            if isinstance(tab, DocumentTab):
                tab.clear_highlights()

    def _on_export_results(self):
        # We need the matches. The search panel has them? No, it just has display items.
        # We should probably re-run search or store last results.
        # Storing last results in SearchPanel is cleaner but accessing private data is meh.
        # Let's re-run search. Fast scan is cheap.
        val_str = self.search_panel.value_input.text()
        if not val_str.isdigit():
            QMessageBox.warning(self, "Invalid Value", "Please enter a numeric value to search first.")
            return
            
        path, _ = QFileDialog.getSaveFileName(self, "Export Results", "search_results.txt", "Text Files (*.txt);;CSV Files (*.csv)")
        if not path:
            return
            
        val = int(val_str)
        is_global = self.search_panel.global_chk.isChecked()
        max_words = self.search_panel.max_words.value()
        
        # Re-run logic (copy-paste from _on_search essentially, should refactor if time permits)
        tabs_to_search = []
        if is_global:
            for i in range(self.doc_tabs.count()):
                widget = self.doc_tabs.widget(i)
                if isinstance(widget, DocumentTab):
                    tabs_to_search.append(widget)
        else:
            current = self.doc_tabs.currentWidget()
            if isinstance(current, DocumentTab):
                tabs_to_search.append(current)
        
        include_nums = self.include_nums_chk.isChecked()
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"Search Results for Value: {val}\n")
                f.write(f"Calculator: {self.current_calculator.name}\n")
                f.write("-" * 40 + "\n")
                
                count = 0
                for tab in tabs_to_search:
                    text = tab.get_text()
                    matches = self.analysis_service.find_value_matches(
                        text, val, self.current_calculator, include_nums, max_words
                    )
                    for m_text, start, end in matches:
                        f.write(f"[{tab.document.title}] {m_text}\n")
                        count += 1
                
                f.write("-" * 40 + "\n")
                f.write(f"Total Matches: {count}\n")
                
            QMessageBox.information(self, "Exported", f"Exported {count} matches to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")

    def _on_smart_filter(self):
        # We need the full match list from the search panel
        matches = self.search_panel.all_matches
        if not matches:
            QMessageBox.information(self, "Info", "No matches to filter. Run a search first.")
            return
            
        dlg = SmartFilterDialog(matches, self)
        dlg.exec()

    # --- Saving / Teacher ---
    
    def _open_teacher(self):
        current = self.doc_tabs.currentWidget()
        if not isinstance(current, DocumentTab):
            return
            
        dlg = HolyBookTeacherWindow(
            document_id=current.document.id,
            document_title=current.document.title,
            allow_inline=not self.strict_verse_chk.isChecked(),
            parent=self
        )
        # On save, refresh current tab
        dlg.verses_saved.connect(current.refresh_verse_list)
        dlg.show()
        
    def _on_save_verse(self, verse):
        self._save_record(verse['text'], f"Verse {verse['number']}")

    def _on_save_all_verses(self, verses):
        count = 0 
        for v in verses:
            self._save_record(v['text'], None, silent=True)
            count += 1
        QMessageBox.information(self, "Saved", f"Saved {count} records.")

    def _on_save_matches(self):
        # Re-run search mostly
        val_str = self.search_panel.value_input.text()
        if not val_str.isdigit(): return
        val = int(val_str)
        is_global = self.search_panel.global_chk.isChecked()
        max_words = self.search_panel.max_words.value()
        
        tabs_to_search = []
        if is_global:
            for i in range(self.doc_tabs.count()):
                widget = self.doc_tabs.widget(i)
                if isinstance(widget, DocumentTab):
                    tabs_to_search.append(widget)
        else:
            current = self.doc_tabs.currentWidget()
            if isinstance(current, DocumentTab):
                tabs_to_search.append(current)
                
        count = 0
        include_nums = self.include_nums_chk.isChecked()
        for tab in tabs_to_search:
            text = tab.get_text()
            matches = self.analysis_service.find_value_matches(
                text, val, self.current_calculator, include_nums, max_words
            )
            for m_text, _, _ in matches:
                self._save_record(m_text, None, silent=True)
                count += 1
        
        QMessageBox.information(self, "Saved", f"Saved {count} matches.")

    def _save_record(self, text, default_note=None, silent=False):
        try:
            val = self.analysis_service.calculate_text(text, self.current_calculator, self.include_nums_chk.isChecked())
            notes = default_note or ""
            if not silent:
                notes, ok = QInputDialog.getMultiLineText(self, "Save", f"Save: {text} = {val}", notes)
                if not ok: return
            
            # Source should rely on current document?
            # If search results, we lose exact document context in this helper unless passed.
            # Simplified: Use current active tab as source, or "Search Result" if MDI ambiguity?
            # Ideally each match should carry source info.
            # For now, use "Gematria Tool Match".
            
            self.calc_service.save_calculation(
                text=text,
                value=val,
                calculator=self.current_calculator,
                breakdown=[],
                notes=notes,
                source="Analysis Tool"
            )
        except Exception as e:
            if not silent:
                QMessageBox.critical(self, "Error", str(e))
