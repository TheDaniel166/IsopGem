"""
Document Tab - The Text Analysis Container.
Tab widget combining document viewer with verse list and calculation controls.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget
)
from PyQt6.QtCore import pyqtSignal
from typing import Optional

from .document_viewer import DocumentViewer
from .verse_list import VerseList
from .interlinear_widget import InterlinearDocumentView
from shared.models.document_manager.document import Document
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
        """
          init   logic.
        
        Args:
            document: Description of document.
            analysis_service: Description of analysis_service.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.document = document
        self.analysis_service = analysis_service
        self.current_calculator = None
        self.strict_parsing = True
        self.include_numbers = False
        self._formatted_verse_mode = False  # Track formatted verse display
        self._is_stale = False # Track if content needs refresh due to lexicon updates
        
        self._setup_ui()
        self._load_document_content()

        # Connect signals
        self._navigation_bus = None
        try:
            from shared.signals.navigation_bus import navigation_bus
            self._navigation_bus = navigation_bus
            self._navigation_bus.lexicon_updated.connect(self._on_lexicon_updated)
        except ImportError:
            pass

    def closeEvent(self, a0):
        """Disconnect from navigation bus on close to prevent signals to destroyed objects."""
        if self._navigation_bus:
            try:
                self._navigation_bus.lexicon_updated.disconnect(self._on_lexicon_updated)
            except (TypeError, RuntimeError):
                pass  # Already disconnected or object deleted
        super().closeEvent(a0)
        
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
        
        # Interlinear view (TQ Concordance mode)
        self.interlinear_view = InterlinearDocumentView()
        self.stack.addWidget(self.interlinear_view)
        
        layout.addWidget(self.stack)
        
        # Selection Result Label
        self.sel_result_lbl = QLabel("")
        self.sel_result_lbl.setStyleSheet("color: #2563eb; font-weight: bold;")
        layout.addWidget(self.sel_result_lbl)
        
    def _load_document_content(self, use_curated_format: bool = False):
        """Load document content into the viewer.
        
        Args:
            use_curated_format: If True, format text with curated verse structure
                               (one verse per line with verse number prefix).
        """
        if not self.document:
            return
        
        self._formatted_verse_mode = use_curated_format
        
        if use_curated_format:
            # Load curated verses and format as structured text
            formatted_text = self._get_formatted_verse_text()
            if formatted_text:
                self.doc_viewer.set_text(formatted_text)
                return
            # Fall back to raw if no curated verses
            
        from PyQt6.QtGui import QTextDocument
        td = QTextDocument()
        td.setHtml(str(self.document.content or ""))
        plain = td.toPlainText()
        
        self.doc_viewer.set_text(plain)
    
    def _get_formatted_verse_text(self) -> Optional[str]:
        """Get document text formatted with curated verse structure.
        
        Returns:
            Formatted text with each verse on its own line, or None if no curated verses.
        """
        if not self.document:
            return None
            
        try:
            from shared.services.document_manager.verse_teacher_service import verse_teacher_service_context
            
            with verse_teacher_service_context() as service:
                result = service.get_or_parse_verses(
                    self.document.id,
                    allow_inline=True,
                    apply_rules=True
                )
                
            source = result.get('source', '')
            verses = result.get('verses', [])
            
            if not verses:
                return None
            
            # Filter out ignored verses
            active_verses = [
                v for v in verses 
                if v.get('status', 'auto') != 'ignored'
            ]
            
            if not active_verses:
                return None
            
            # Format each verse on its own line
            lines = []
            for v in active_verses:
                number = v.get('number') or v.get('verse_number', '')
                text = v.get('text', '').strip()
                if number:
                    lines.append(f"{number}. {text}")
                else:
                    lines.append(text)
            
            # Add source indicator at top
            header = f"[Source: {source} | {len(active_verses)} verses]\n" + "─" * 50 + "\n\n"
            
            return header + "\n\n".join(lines)
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to load formatted verses: {e}")
            return None
    
    def toggle_formatted_view(self, use_formatted: bool):
        """Toggle between raw document text and formatted curated verse view.
        
        Args:
            use_formatted: True to show curated verse format, False for raw text.
        """
        self._load_document_content(use_curated_format=use_formatted)
        if use_formatted:
            self.viewer_label.setText("Document Text (Curated Format)")
        else:
            self.viewer_label.setText("Document Text")
    
    def has_curated_verses(self) -> bool:
        """Check if this document has curated verses available.
        
        Returns:
            True if curated verses exist (excluding ignored ones).
        """
        if not self.document:
            return False
            
        try:
            from shared.services.document_manager.verse_teacher_service import verse_teacher_service_context
            
            with verse_teacher_service_context() as service:
                result = service.get_or_parse_verses(
                    self.document.id,
                    allow_inline=True,
                    apply_rules=True
                )
            
            source = result.get('source', '')
            if source != 'curated':
                return False
                
            verses = result.get('verses', [])
            # Check for non-ignored verses
            active_verses = [
                v for v in verses 
                if v.get('status', 'auto') != 'ignored'
            ]
            return len(active_verses) > 0
            
        except Exception:
            return False
        

            
    def refresh_verse_list(self):
        """Refresh the verse list with current settings."""
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
    
    def _refresh_interlinear_view(self):
        """Refresh the interlinear view with verses from the document."""
        if not self.document or not self.current_calculator:
            return
            
        # Get key service for concordance lookup
        try:
            from pillars.tq_lexicon.services.holy_key_service import HolyKeyService
            key_service = HolyKeyService()
        except ImportError:
            key_service = None
            
        # Set calculator and key service
        self.interlinear_view.calculator = self.current_calculator
        self.interlinear_view.key_service = key_service
        
        # Parse verses
        text = self.doc_viewer.get_text()
        result = self.analysis_service.parse_verses(
            text, 
            self.document.id, 
            allow_inline=not self.strict_parsing
        )
        raw_verses = result.get('verses', [])
        
        # Convert to format expected by interlinear view
        verses = []
        for i, verse in enumerate(raw_verses):
            if isinstance(verse, str):
                verses.append({'text': verse, 'verse_number': i + 1})
            elif isinstance(verse, dict):
                verses.append({
                    'text': verse.get('text', str(verse)),
                    'verse_number': verse.get('number', i + 1)
                })
            else:
                verses.append({'text': str(verse), 'verse_number': i + 1})
                
        self.interlinear_view.set_verses(verses)

    def update_settings(self, calculator, strict_parsing: bool, include_numbers: bool):
        """
        Update settings logic.
        
        Args:
            calculator: Description of calculator.
            strict_parsing: Description of strict_parsing.
            include_numbers: Description of include_numbers.
        
        """
        self.current_calculator = calculator
        self.strict_parsing = strict_parsing
        self.include_numbers = include_numbers
        
        # If in verse mode, refresh
        if self.stack.currentWidget() == self.verse_list:
            self.refresh_verse_list()
            
    def get_text(self) -> str:
        """
        Retrieve text logic.
        
        Returns:
            Result of get_text operation.
        """
        return self.doc_viewer.get_text()
        
    def highlight_ranges(self, ranges):
        """
        Highlight ranges logic.
        
        Args:
            ranges: Description of ranges.
        
        """
        self.doc_viewer.highlight_ranges(ranges)
        
    def clear_highlights(self):
        """
        Clear highlights logic.
        
        """
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

    # --- Signal Handling ---

    def _on_lexicon_updated(self, key_id: int, word: str):
        """Handle lexicon updates."""
        # Check if the word is relevant to this document
        current_text = self.doc_viewer.get_text().lower()
        if word.lower() in current_text:
            self._is_stale = True
            
            # Update label to show stale state
            current_label = self.viewer_label.text()
            if "(!)" not in current_label:
                self.viewer_label.setText(f"{current_label} (!)")
                self.viewer_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #d97706;")

            # If showing interlinear view, we can verify relevancy more deeply but "in text" is good proxy.
            
    def set_view_mode(self, verse_mode: bool, interlinear: bool = False, auto_curated: bool = True):
        """
        Configure view mode.
        
        Args:
            verse_mode: Show verse list instead of plain text (Holy Scansion)
            interlinear: Show interlinear concordance view (requires verse_mode)
            auto_curated: Automatically use curated format when verse_mode is True
                         and curated verses are available
        """
        # Auto-refresh if stale
        if self._is_stale:
            self._is_stale = False
            # Reset label style
            self.viewer_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
            # Force refresh of current views
            self.refresh_verse_list()
            self._refresh_interlinear_view()

        if interlinear and verse_mode:
            self.stack.setCurrentWidget(self.interlinear_view)
            self.viewer_label.setText("Interlinear Concordance")
            self._refresh_interlinear_view()
        elif verse_mode:
            self.stack.setCurrentWidget(self.verse_list)
            self.viewer_label.setText("Verse List")
            self.refresh_verse_list()
        else:
            self.stack.setCurrentWidget(self.doc_viewer)
            # When exiting verse mode, check if we should maintain curated format
            if self._formatted_verse_mode:
                self.viewer_label.setText("Document Text (Curated Format)")
            else:
                self.viewer_label.setText("Document Text")
        
        # Auto-apply curated format when Holy Scansion is enabled and curated verses exist
        if verse_mode and auto_curated and not self._formatted_verse_mode:
            if self.has_curated_verses():
                self._load_document_content(use_curated_format=True)