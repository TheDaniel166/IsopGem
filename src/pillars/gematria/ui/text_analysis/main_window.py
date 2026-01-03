
"""
Exegesis Main Window - The Scriptural Inquiry.
Main window for text analysis with multi-document tabs, search, and verse parsing.
"""
import logging

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QPushButton, QLabel, QCheckBox, QMessageBox, QTabWidget,
    QSplitter, QFileDialog, QFrame, QGraphicsDropShadowEffect,
    QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from typing import List
from pathlib import Path

from ...services.base_calculator import GematriaCalculator
from ...services import CalculationService
from ...services.text_analysis_service import TextAnalysisService
from shared.services.document_manager.document_service import document_service_context


# Components
from .search_panel import SearchPanel
from .document_tab import DocumentTab
from .stats_panel import StatsPanel
from .smart_filter_dialog import SmartFilterDialog
from ..holy_book_teacher_window import HolyBookTeacherWindow

logger = logging.getLogger(__name__)



class ExegesisWindow(QMainWindow):
    """
    The Exegesis: A window for scriptural inquiry and numerological frequency analysis.
    Formerly TextAnalysisWindow.
    """
    
    def __init__(self, calculators: List[GematriaCalculator], window_manager=None, parent=None):
        """
          init   logic.
        
        Args:
            calculators: Description of calculators.
            window_manager: Description of window_manager.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.window_manager = window_manager
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
        self.setWindowTitle("The Exegesis")
        self.resize(1200, 800)
        
        # Level 0: The Background (Thematic Texture)
        # Level 0: The Background (Thematic Texture)
        
        possible_paths = [
            Path("src/assets/patterns/exegesis_bg_pattern.png"),
            Path("assets/patterns/exegesis_bg_pattern.png"),
            Path(__file__).parent.parent.parent.parent.parent / "assets/patterns/exegesis_bg_pattern.png"
        ]
        
        bg_path = None
        for p in possible_paths:
            if p.exists():
                bg_path = p
                break
        
        central = QWidget()
        central.setObjectName("CentralContainer")
        self.setCentralWidget(central)
        
        if bg_path:
            logger.debug("Found background pattern at: %s", bg_path)
            # Use absolute path for CSS
            abs_path = bg_path.absolute().as_posix()
            central.setStyleSheet(f"""
                QWidget#CentralContainer {{
                    border-image: url("{abs_path}") 0 0 0 0 stretch stretch;
                    border: none;
                    background-color: #fdfbf7;
                }}
            """)
        else:
             logger.warning("Background pattern not found; using fallback color")
             central.setStyleSheet("QWidget#CentralContainer { background-color: #fdfbf7; }")
        
        # Main Layout with Padding for Floating Panels
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)
        
        # --- Toolbar (Level 1: Floating Header) ---
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("FloatingHeader")
        toolbar_frame.setStyleSheet("""
            QFrame#FloatingHeader {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid #d4c4a8; /* Ancient Gold/Tan border */
                border-radius: 16px;
            }
            QLabel { font-family: 'Inter'; font-weight: 600; color: #44403c; }
            QComboBox { 
                background: white; border: 1px solid #d6d3d1; padding: 4px; border-radius: 6px; 
            }
            QPushButton {
                background-color: white; border: 1px solid #d6d3d1; border-radius: 6px; padding: 6px 12px; font-weight: 600; color: #57534e;
            }
            QPushButton:hover { background-color: #fafaf9; border-color: #a8a29e; }
        """)
        header_shadow = QGraphicsDropShadowEffect()
        header_shadow.setBlurRadius(12)
        header_shadow.setColor(QColor(0,0,0,30))
        header_shadow.setOffset(0, 2)
        toolbar_frame.setGraphicsEffect(header_shadow)
        
        toolbar = QHBoxLayout(toolbar_frame)
        toolbar.setContentsMargins(16, 12, 16, 12)
        
        # Document Selector
        toolbar.addWidget(QLabel("Select Text:"))
        self.doc_combo = QComboBox()
        self.doc_combo.setMinimumWidth(250)
        toolbar.addWidget(self.doc_combo)
        
        open_btn = QPushButton("Open Scroll")
        open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        open_btn.setProperty("archetype", "seeker")
        open_btn.clicked.connect(self._on_open_document)
        toolbar.addWidget(open_btn)
        
        toolbar.addSpacing(24)
        
        # Method Selector
        toolbar.addWidget(QLabel("Cipher:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(list(self.calculators.keys()))
        self.method_combo.setCurrentText(self.current_calculator.name)
        self.method_combo.currentTextChanged.connect(self._on_method_changed)
        toolbar.addWidget(self.method_combo)
        
        # Options
        self.holy_view_chk = QCheckBox("Holy Scansion")
        self.holy_view_chk.toggled.connect(self._on_view_mode_toggled)
        toolbar.addWidget(self.holy_view_chk)
        
        self.interlinear_chk = QCheckBox("Interlinear")
        self.interlinear_chk.setToolTip("Show word-level TQ values and concordance links")
        self.interlinear_chk.toggled.connect(self._on_view_mode_toggled)
        self.interlinear_chk.setEnabled(False)  # Only enabled when Holy Scansion is checked
        toolbar.addWidget(self.interlinear_chk)
        
        self.strict_verse_chk = QCheckBox("Strict Parsing")
        self.strict_verse_chk.setChecked(True)
        self.strict_verse_chk.toggled.connect(self._on_options_changed)
        toolbar.addWidget(self.strict_verse_chk)
        
        self.include_nums_chk = QCheckBox("Include Numerals")
        self.include_nums_chk.stateChanged.connect(self._on_options_changed)
        toolbar.addWidget(self.include_nums_chk)
        
        self.curated_format_chk = QCheckBox("Curated Format")
        self.curated_format_chk.setToolTip("Display text with curated verse structure (one verse per line)")
        self.curated_format_chk.toggled.connect(self._on_curated_format_toggled)
        toolbar.addWidget(self.curated_format_chk)
        
        self.teach_btn = QPushButton("Train Scribe")
        self.teach_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.teach_btn.setEnabled(False) # Enable if tab active
        self.teach_btn.setProperty("archetype", "scribe")
        self.teach_btn.clicked.connect(self._open_teacher)
        toolbar.addWidget(self.teach_btn)
        
        # Concordance button - unified parse + index workflow
        self.concordance_btn = QPushButton("📚 Concordance")
        self.concordance_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.concordance_btn.setToolTip("Open Holy Book Concordance - parse and index documents")
        self.concordance_btn.setProperty("archetype", "navigator")
        self.concordance_btn.clicked.connect(self._open_concordance)
        toolbar.addWidget(self.concordance_btn)
        
        toolbar.addStretch()
        main_layout.addWidget(toolbar_frame)
        
        # --- Main Content Area (Splitter) ---
        # We wrap the splitter in nothing or just let it float?
        # Splitter handles often look bad on transparent backgrounds. 
        # But the children (TabWidgets) will be the Floating Panels.
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(8)
        
        # Left: Tabs for Documents (Floating Panel 1)
        # We need to wrap QTabWidget in a styled QFrame to give it the card look?
        # Or style QTabWidget directly. Styling QTabWidget pane is easier.
        
        self.doc_tabs = QTabWidget()
        self.doc_tabs.setTabsClosable(True)
        self.doc_tabs.tabCloseRequested.connect(self._on_tab_close)
        self.doc_tabs.currentChanged.connect(self._on_tab_changed)
        self.doc_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #d4c4a8;
                border-radius: 12px;
                background: rgba(255, 255, 255, 0.95);
                top: -1px; /* Overlap tab bottom border */
            }
            QTabBar::tab {
                background: rgba(240, 237, 230, 0.8);
                border: 1px solid #e7e5e4;
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                color: #57534e;
            }
            QTabBar::tab:selected {
                background: white;
                border-color: #d4c4a8;
                border-bottom-color: white;
                font-weight: bold;
                color: #0f172a;
            }
        """)
        
        splitter.addWidget(self.doc_tabs)
        
        # Right: Tools (Floating Panel 2)
        self.tools_tabs = QTabWidget()
        self.tools_tabs.setStyleSheet(self.doc_tabs.styleSheet()) # Shared style
        
        # Search Tab -> Scriptural Inquiry
        self.search_panel = SearchPanel()
        self.search_panel.search_requested.connect(self._on_search)
        self.search_panel.result_selected.connect(self._on_search_result_selected)
        self.search_panel.clear_requested.connect(self._on_clear_search)
        self.search_panel.save_matches_requested.connect(self._on_save_matches)
        self.search_panel.export_requested.connect(self._on_export_results)
        self.search_panel.smart_filter_requested.connect(self._on_smart_filter)
        self.search_panel.send_to_tablet_requested.connect(self._on_send_search_to_emerald)
        self.tools_tabs.addTab(self.search_panel, "Scriptural Inquiry")
        
        # Stats Tab -> Numerological Frequency
        self.stats_panel = StatsPanel()
        self.tools_tabs.addTab(self.stats_panel, "Numerological Frequency")
        
        splitter.addWidget(self.tools_tabs)
        
        splitter.setSizes([800, 400])
        main_layout.addWidget(splitter, 1)
        
        # Status Bar (Integrated into window or floating?)
        # Let's keep a simple label at bottom, maybe less obtrusive
        self.status = QLabel("Ready for Exegesis")
        self.status.setStyleSheet("color: #78716c; font-style: italic; margin-left: 8px;")
        main_layout.addWidget(self.status)
        
    def _load_documents(self):
        """Load holy book documents into the dropdown with curation status indicators.
        
        Uses a single batch query to fetch all curated document IDs upfront,
        then uses O(1) set membership checks during iteration for efficiency.
        """
        try:
            from shared.services.document_manager.verse_teacher_service import verse_teacher_service_context
            
            # Batch query: get all document IDs with curated verses in ONE query
            curated_doc_ids: set = set()
            try:
                with verse_teacher_service_context() as verse_service:
                    curated_doc_ids = verse_service.get_documents_with_curated_verses()
            except Exception:
                # Graceful fallback - all documents show as uncurated
                curated_doc_ids = set()
            
            with document_service_context() as service:
                docs = service.get_all_documents()
                self.doc_combo.clear()
                self.doc_combo.addItem("-- Select Sacred Text --", None)
                
                for d in docs:
                    collection = (d.collection or "").lower()
                    if "holy" in collection:
                        # O(1) set membership check instead of N+1 database queries
                        has_curated = d.id in curated_doc_ids
                        
                        if has_curated:
                            # Curated indicator: ✓
                            display_text = f"✓ {d.title}"
                        else:
                            display_text = f"  {d.title}"  # Align with curated ones
                        
                        self.doc_combo.addItem(display_text, d.id)
                        
        except Exception as e:
            self.status.setText(f"Error loading texts: {e}")
    
    def _check_document_curated(self, document_id: int) -> bool:
        """Check if a single document has curated verses.
        
        Note: For bulk checks, use get_documents_with_curated_verses() instead
        to avoid N+1 query patterns.
        
        Args:
            document_id: The document ID to check
            
        Returns:
            True if curated verses exist (excluding ignored)
        """
        try:
            from shared.services.document_manager.verse_teacher_service import verse_teacher_service_context
            
            with verse_teacher_service_context() as service:
                curated_ids = service.get_documents_with_curated_verses()
                return document_id in curated_ids
        except Exception:
            return False
            
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
            tab.save_text_requested.connect(self._on_save_text_selection)
            tab.open_quadset_requested.connect(self._on_open_quadset)
            # Init settings
            tab.update_settings(
                self.current_calculator,
                self.strict_verse_chk.isChecked(),
                self.include_nums_chk.isChecked()
            )
            # If global "Holy Book View" is checked, set it
            tab.set_view_mode(
                self.holy_view_chk.isChecked(),
                interlinear=self.interlinear_chk.isChecked()
            )
            
            index = self.doc_tabs.addTab(tab, document.title)
            self.doc_tabs.setCurrentIndex(index)
            self.status.setText(f"Opened Scroll: {document.title}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open scroll: {e}")
            
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
        # Enable/disable interlinear checkbox based on Holy Scansion
        if self.sender() == self.holy_view_chk:
            self.interlinear_chk.setEnabled(checked)
            if not checked:
                self.interlinear_chk.setChecked(False)
        
        holy_mode = self.holy_view_chk.isChecked()
        interlinear_mode = self.interlinear_chk.isChecked()
        
        # When Holy Scansion is enabled, auto-check Curated Format if curated verses exist
        if holy_mode and self.sender() == self.holy_view_chk:
            current_tab = self.doc_tabs.currentWidget()
            if isinstance(current_tab, DocumentTab) and current_tab.has_curated_verses():
                self.curated_format_chk.setChecked(True)
        
        for i in range(self.doc_tabs.count()):
            tab = self.doc_tabs.widget(i)
            if isinstance(tab, DocumentTab):
                tab.set_view_mode(holy_mode, interlinear=interlinear_mode)
    
    def _on_curated_format_toggled(self, checked):
        """Toggle between raw document text and curated verse format."""
        for i in range(self.doc_tabs.count()):
            tab = self.doc_tabs.widget(i)
            if isinstance(tab, DocumentTab):
                tab.toggle_formatted_view(checked)
        
        if checked:
            self.status.setText("Viewing curated verse structure")
        else:
            self.status.setText("Viewing raw document text")

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
            for m_text, start, end in matches:
                all_matches.append((m_text, start, end, tab.document.title, index))
                
        self.search_panel.set_results(all_matches)
        
        # Ensure panel knows current tab
        current_idx = self.doc_tabs.currentIndex()
        self.search_panel.set_active_tab(current_idx)
        
        # Highlight matches in CURRENT tab only
        # Highlight matches in CURRENT tab only
        current_widget = self.doc_tabs.currentWidget()
        if isinstance(current_widget, DocumentTab):
            current_widget.clear_highlights()
            if not is_global and tabs_to_search:
                ranges = [(m[1], m[2]) for m in all_matches]
                current_widget.highlight_ranges(ranges)
            
    def _on_search_result_selected(self, start, end, tab_index):
        if tab_index >= 0 and tab_index < self.doc_tabs.count():
            self.doc_tabs.setCurrentIndex(tab_index)
            # Ensure text mode
            self.holy_view_chk.setChecked(False) 
            
            tab = self.doc_tabs.widget(tab_index)
            if isinstance(tab, DocumentTab):
                tab.set_view_mode(False) 
                tab.doc_viewer.select_range(start, end)
                
    def _on_clear_search(self):
        self.search_panel.clear_results()
        for i in range(self.doc_tabs.count()):
            tab = self.doc_tabs.widget(i)
            if isinstance(tab, DocumentTab):
                tab.clear_highlights()

    def _on_export_results(self):
        val_str = self.search_panel.value_input.text()
        if not val_str.isdigit():
            QMessageBox.warning(self, "Invalid Value", "Please enter a numeric value to search first.")
            return
            
        path, _ = QFileDialog.getSaveFileName(self, "Export Inquiry", "exegesis_results.txt", "Text Files (*.txt);;CSV Files (*.csv)")
        if not path:
            return
            
        val = int(val_str)
        is_global = self.search_panel.global_chk.isChecked()
        max_words = 9999
        
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
                f.write(f"Exegesis Inquiry for Value: {val}\n")
                f.write(f"Cipher: {self.current_calculator.name}\n")
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
        matches = self.search_panel.all_matches
        if not matches:
            QMessageBox.information(self, "Info", "No matches to filter. Run an inquiry first.")
            return
            
        dlg = SmartFilterDialog(matches, self)
        dlg.exec()

    # --- Saving / Teacher / Concordance ---
    
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
        dlg.verses_saved.connect(current.refresh_verse_list)
        dlg.show()
    
    def _open_concordance(self):
        """Open the unified TQ Lexicon Workflow window."""
        try:
            # Focus existing window if open
            if hasattr(self, 'concordance_window') and self.concordance_window and self.concordance_window.isVisible():
                self.concordance_window.raise_()
                self.concordance_window.activateWindow()
                return

            # Use navigation bus to request the sovereign window
            from shared.signals.navigation_bus import navigation_bus
            if self.window_manager:
                navigation_bus.request_window.emit(
                    "lexicon_manager",
                    {"window_manager": self.window_manager}
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Lexicon:\n{e}")
        
    def _open_lexicon(self):
        """Launch the Holy Key Lexicon Manager."""
        from shared.signals.navigation_bus import navigation_bus
        if self.window_manager:
            navigation_bus.request_window.emit(
                "lexicon_manager",
                {"window_manager": self.window_manager}
            )
        
    def _on_save_verse(self, verse):
        self._save_record(verse['text'], f"Verse {verse['number']}")

    def _on_save_all_verses(self, verses):
        count = 0 
        for v in verses:
            self._save_record(v['text'], None, silent=True)
            count += 1
        QMessageBox.information(self, "Saved", f"Saved {count} records to Karnak.")

    def _on_save_matches(self):
        val_str = self.search_panel.value_input.text()
        if not val_str.isdigit(): return
        val = int(val_str)
        is_global = self.search_panel.global_chk.isChecked()
        max_words = 9999
        
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
        
        QMessageBox.information(self, "Saved", f"Saved {count} matches to Karnak.")

    def _on_save_text_selection(self, text):
        self._save_record(text, "Selection")

    def _on_open_quadset(self, value: int):
        from shared.signals.navigation_bus import navigation_bus
        
        if self.window_manager:
            navigation_bus.request_window.emit(
                "quadset_analysis", 
                {"window_manager": self.window_manager, "initial_value": value}
            )
        else:
            # Fallback (shouldn't happen in standard flow)
            pass

    def _save_record(self, text, default_note=None, silent=False):
        try:
            val = self.analysis_service.calculate_text(text, self.current_calculator, self.include_nums_chk.isChecked())
            notes = default_note or ""
            if not silent:
                notes, ok = QInputDialog.getMultiLineText(self, "Save to Karnak", f"Save: {text} = {val}", notes)
                if not ok: return
            
            self.calc_service.save_calculation(
                text=text,
                value=val,
                calculator=self.current_calculator,
                breakdown=[],
                notes=notes,
                source="Exegesis Tool"
            )
        except Exception as e:
            if not silent:
                QMessageBox.critical(self, "Error", str(e))

    def _on_send_search_to_emerald(self, matches):
        if not self.window_manager or not matches:
             return
             
        from shared.signals.navigation_bus import navigation_bus
        
        target_val = self.search_panel.value_input.text()
        
        columns = ["Text", "Document", "Start", "End", "Target Value"]
        rows = []
        for m in matches:
            rows.append([m[0], m[3], str(m[1]), str(m[2]), target_val])
            
        data = {
            "columns": columns,
            "data": rows,
            "styles": {}
        }
        
        navigation_bus.request_window.emit(
            "emerald_tablet",
            {"allow_multiple": False, "window_manager": self.window_manager}
        )
        
        hub = self.window_manager.get_active_windows().get("emerald_tablet")
        
        if hasattr(hub, "receive_import"):
            name = f"Inquiry_{target_val}"
            hub.receive_import(name, data)
            QMessageBox.information(self, "Sent", f"Sent {len(rows)} matches to Emerald Tablet.")