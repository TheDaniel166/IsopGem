"""Text Analysis Window - Analyze documents with Gematria."""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QTextEdit, QComboBox, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox, QGroupBox,
    QMenu, QInputDialog, QScrollArea, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont, QAction
from typing import List, Dict, Optional, Tuple, Any
from ..utils.verse_parser import parse_verses
from ..utils.numeric_utils import sum_numeric_face_values
import re
from PyQt6.QtWidgets import QSpinBox
from pillars.document_manager.services.document_service import document_service_context
from pillars.document_manager.services.verse_teacher_service import verse_teacher_service_context

from .holy_book_teacher_window import HolyBookTeacherWindow
import logging

from ..services.base_calculator import GematriaCalculator
from ..services import CalculationService
from pillars.document_manager.models.document import Document


logger = logging.getLogger(__name__)


class TextAnalysisWindow(QMainWindow):
    """Window for analyzing document text with Gematria."""
    HOLY_BOOKS_CATEGORY = "Holy Books"
    DEFAULT_CALCULATOR_NAME = "English (TQ)"
    
    def __init__(self, calculators: List[GematriaCalculator], parent=None):
        """
        Initialize the text analysis window.
        
        Args:
            calculators: List of available gematria calculators
            parent: Optional parent widget
        """
        super().__init__(parent)
        # UI readiness flag to prevent handlers running during construction
        self._ui_ready = False
        self.calculators: Dict[str, GematriaCalculator] = {
            calc.name: calc for calc in calculators
        }
        self.current_calculator: GematriaCalculator = self._select_default_calculator(calculators)
        self.calculation_service = CalculationService()
        
        # Current state
        self.current_document: Optional[Document] = None
        self.highlighted_matches: List[Tuple[int, int]] = []  # List of (start, end) positions
        self._current_selection: Optional[Dict[str, Any]] = None
        self._verse_run_metadata: Optional[Dict[str, Any]] = None
        
        self.setWindowTitle("Gematria Text Analysis")
        self.setMinimumSize(1200, 800)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)

        self._setup_ui()
        self._load_documents()
        # Mark UI ready after setup/load complete
        self._ui_ready = True

    def _select_default_calculator(self, calculators: List[GematriaCalculator]) -> GematriaCalculator:
        """Return preferred calculator, falling back to the first available."""
        if not calculators:
            raise ValueError("At least one calculator is required")

        preferred = self.DEFAULT_CALCULATOR_NAME.lower()
        for calc in calculators:
            if calc.name.lower() == preferred:
                return calc
        return calculators[0]
    
    def _setup_ui(self):
        """Set up the user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("📊 Gematria Text Analysis")
        title_label.setStyleSheet("""
            font-size: 22pt;
            font-weight: bold;
            color: #1e293b;
        """)
        main_layout.addWidget(title_label)
        
        # Toolbar section
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(12)
        
        # Document selector
        doc_label = QLabel("Document:")
        doc_label.setStyleSheet("font-weight: 500; font-size: 11pt;")
        toolbar_layout.addWidget(doc_label)
        
        self.document_combo = QComboBox()
        self.document_combo.setMinimumWidth(300)
        self.document_combo.setMinimumHeight(36)
        self.document_combo.currentIndexChanged.connect(self._on_document_selected)
        toolbar_layout.addWidget(self.document_combo)
        
        toolbar_layout.addSpacing(20)
        
        # Calculator selector
        calc_label = QLabel("Method:")
        calc_label.setStyleSheet("font-weight: 500; font-size: 11pt;")
        toolbar_layout.addWidget(calc_label)
        
        self.calculator_combo = QComboBox()
        self.calculator_combo.addItems(list(self.calculators.keys()))
        self.calculator_combo.setMinimumWidth(250)
        self.calculator_combo.setMinimumHeight(36)
        self.calculator_combo.currentTextChanged.connect(self._on_calculator_changed)
        default_index = self.calculator_combo.findText(self.current_calculator.name)
        if default_index >= 0:
            # Prevent triggering change handler while UI still building
            self.calculator_combo.blockSignals(True)
            self.calculator_combo.setCurrentIndex(default_index)
            self.calculator_combo.blockSignals(False)
        toolbar_layout.addWidget(self.calculator_combo)
        # Holy Book view toggle - when enabled, show verses parsed by verse number
        self.holy_view_toggle = QCheckBox("Holy Book View")
        self.holy_view_toggle.setToolTip("Parse document into verse boxes by leading verse numbers")
        self.holy_view_toggle.toggled.connect(self._on_holy_view_toggled)
        toolbar_layout.addWidget(self.holy_view_toggle)
        # Strict verse parsing toggles whether inline numbers are considered.
        self.strict_verse_toggle = QCheckBox("Strict Verse Parsing")
        self.strict_verse_toggle.setToolTip("When enabled, only numbers at the start of a line are treated as verse markers")
        self.strict_verse_toggle.setChecked(True)
        # Include numeric face values for totals
        self.include_numbers_checkbox = QCheckBox("Include numeric face values")
        self.include_numbers_checkbox.setToolTip("Include integer numbers found in text when summing totals")
        self.include_numbers_checkbox.setChecked(False)
        self.include_numbers_checkbox.stateChanged.connect(self._on_include_numbers_toggled)
        toolbar_layout.addWidget(self.include_numbers_checkbox)
        toolbar_layout.addWidget(self.strict_verse_toggle)
        self.teach_parser_btn = QPushButton("Teach Parser")
        self.teach_parser_btn.setMinimumHeight(32)
        self.teach_parser_btn.setEnabled(False)
        self.teach_parser_btn.setToolTip("Open the Holy Book Teacher workspace")
        self.teach_parser_btn.clicked.connect(self._open_teacher_window)
        toolbar_layout.addWidget(self.teach_parser_btn)
        
        toolbar_layout.addStretch()
        
        main_layout.addLayout(toolbar_layout)
        
        # Main content - splitter with text on left, tools on right
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Text display
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Text display header
        text_header_layout = QHBoxLayout()
        text_header_label = QLabel("Document Text")
        text_header_label.setStyleSheet("font-weight: 600; font-size: 12pt;")
        text_header_layout.addWidget(text_header_label)
        
        text_header_layout.addStretch()
        
        # Calculate selection button
        self.calc_selection_btn = QPushButton("Calculate Selection")
        self.calc_selection_btn.setMinimumHeight(32)
        self.calc_selection_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self.calc_selection_btn.clicked.connect(self._calculate_selection)
        self.calc_selection_btn.setEnabled(False)
        text_header_layout.addWidget(self.calc_selection_btn)
        
        left_layout.addLayout(text_header_layout)
        
        # Text display
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet("""
            QTextEdit {
                font-family: 'Georgia', 'Times New Roman', serif;
                font-size: 13pt;
                background-color: #ffffff;
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                padding: 16px;
                line-height: 1.6;
            }
        """)
        self.text_display.selectionChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self.text_display)
        
        # Selection info
        self.selection_info_label = QLabel("Select text to calculate its gematria value")
        self.selection_info_label.setStyleSheet("""
            color: #64748b;
            font-size: 10pt;
            padding: 4px;
        """)
        left_layout.addWidget(self.selection_info_label)
        # Value display for calculated selection (stays visible for long selections)
        self.calculated_value_label = QLabel("")
        self.calculated_value_label.setStyleSheet("""
            color: #2563eb;
            font-weight: 600;
            font-size: 10pt;
            padding: 4px;
        """)
        left_layout.addWidget(self.calculated_value_label)
        # Verses scroll area for Holy Book view (hidden by default)
        self.verses_scroll = QScrollArea()
        self.verses_container = QWidget()
        self.verses_layout = QVBoxLayout(self.verses_container)
        self.verses_layout.setContentsMargins(0, 0, 0, 0)
        self.verses_layout.setSpacing(8)
        self.verses_scroll.setWidget(self.verses_container)
        self.verses_scroll.setWidgetResizable(True)
        self.verses_scroll.hide()
        left_layout.addWidget(self.verses_scroll)
        self.verse_run_info_label = QLabel("")
        self.verse_run_info_label.setStyleSheet("color: #475569; font-size: 9pt; padding: 2px 0;")
        self.verse_run_info_label.hide()
        left_layout.addWidget(self.verse_run_info_label)
        
        splitter.addWidget(left_widget)
        
        # Right side - Analysis tools
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Value search section
        search_group = QGroupBox("Search by Value")
        search_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 11pt;
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
            }
        """)
        search_layout = QVBoxLayout(search_group)
        
        # Search input
        search_input_layout = QHBoxLayout()
        self.search_value_input = QLineEdit()
        self.search_value_input.setPlaceholderText("Enter gematria value...")
        self.search_value_input.setMinimumHeight(36)
        self.search_value_input.returnPressed.connect(self._search_by_value)
        search_input_layout.addWidget(self.search_value_input)
        
        # Max words spinbox
        max_label = QLabel("Max words:")
        max_label.setStyleSheet("color: #374151;")
        search_input_layout.addWidget(max_label)

        self.max_words_spin = QSpinBox()
        self.max_words_spin.setRange(1, 20)
        self.max_words_spin.setValue(8)
        self.max_words_spin.setMinimumHeight(36)
        search_input_layout.addWidget(self.max_words_spin)

        search_btn = QPushButton("🔍 Find")
        search_btn.setMinimumHeight(36)
        search_btn.setMinimumWidth(80)
        search_btn.clicked.connect(self._search_by_value)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        search_input_layout.addWidget(search_btn)
        search_layout.addLayout(search_input_layout)
        
        # Results info
        self.results_info_label = QLabel("No search performed")
        self.results_info_label.setStyleSheet("color: #64748b; font-size: 9pt;")
        search_layout.addWidget(self.results_info_label)
        
        # Results list
        results_list_label = QLabel("Matches:")
        results_list_label.setStyleSheet("font-weight: 600; margin-top: 8px;")
        search_layout.addWidget(results_list_label)
        
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                background-color: #f9fafb;
                font-family: monospace;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e5e7eb;
            }
            QListWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
            QListWidget::item:hover {
                background-color: #f0f9ff;
            }
        """)
        self.results_list.itemClicked.connect(self._on_result_clicked)
        self.results_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_list.customContextMenuRequested.connect(self._show_result_context_menu)
        search_layout.addWidget(self.results_list)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear Highlights")
        clear_btn.clicked.connect(self._clear_highlights)
        clear_btn.setMinimumHeight(32)
        action_layout.addWidget(clear_btn)
        
        save_matches_btn = QPushButton("💾 Save Matches")
        save_matches_btn.clicked.connect(self._save_matches)
        save_matches_btn.setMinimumHeight(32)
        save_matches_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        action_layout.addWidget(save_matches_btn)
        # Save verse totals button
        self.save_verses_btn = QPushButton("💾 Save Verse Totals")
        self.save_verses_btn.clicked.connect(self._save_verse_totals)
        self.save_verses_btn.setMinimumHeight(32)
        self.save_verses_btn.setStyleSheet("""
            QPushButton {
                background-color: #f97316;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #ea580c;
            }
        """)
        action_layout.addWidget(self.save_verses_btn)
        self.save_verses_btn.setEnabled(False)
        
        search_layout.addLayout(action_layout)
        
        right_layout.addWidget(search_group)
        
        # Save highlighted selection (mirrors manual calculations)
        self.save_selection_btn = QPushButton("💾 Save Highlight Calculation")
        self.save_selection_btn.clicked.connect(self._save_current_calculation)
        self.save_selection_btn.setMinimumHeight(32)
        self.save_selection_btn.setEnabled(False)
        self.save_selection_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:disabled {
                background-color: #cbd5e1;
                color: #94a3b8;
            }
        """)
        right_layout.addWidget(self.save_selection_btn)
        right_layout.addStretch()
        
        splitter.addWidget(right_widget)
        
        # Set initial splitter sizes (60% text, 40% tools)
        splitter.setSizes([720, 480])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_label = QLabel("Ready - Select a document to begin")
        self.status_label.setStyleSheet("color: #64748b; font-size: 10pt;")
        main_layout.addWidget(self.status_label)
    
    def _load_documents(self):
        """Load documents from the database into the combo box."""
        try:
            with document_service_context() as service:
                documents = [
                    doc for doc in service.get_all_documents()
                    if self._is_holy_books_document(doc)
                ]
            
            self.document_combo.clear()
            self.document_combo.addItem("-- Select a document --", None)
            
            for doc in documents:
                self.document_combo.addItem(f"{doc.title} ({doc.id})", doc.id)
            
            if len(documents) == 0:
                self.status_label.setText("No Holy Books documents found")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load documents:\n{str(e)}")

    def _is_holy_books_document(self, doc: Document) -> bool:
        """Return True if a document belongs to the Holy Books category/collection."""
        target = self.HOLY_BOOKS_CATEGORY.lower()
        candidates = [
            getattr(doc, "category", None),
            getattr(doc, "collection", None),
        ]

        tags = getattr(doc, "tags", None)
        if tags:
            # Tags are stored as comma-separated values; include them as potential categories.
            candidates.extend([t.strip() for t in str(tags).split(",") if t.strip()])

        for candidate in candidates:
            if candidate and str(candidate).strip().lower() == target:
                return True
        return False
    
    def _on_document_selected(self, index: int):
        """Handle document selection."""
        doc_id = self.document_combo.currentData()
        
        if doc_id is None:
            self.text_display.clear()
            self.current_document = None
            self._verse_run_metadata = None
            self.status_label.setText("Ready - Select a document to begin")
            if hasattr(self, 'teach_parser_btn'):
                self.teach_parser_btn.setEnabled(False)
            return
        
        try:
            with document_service_context() as service:
                self.current_document = service.get_document(doc_id)
            
            if self.current_document:
                # Extract plain text from HTML content
                from PyQt6.QtGui import QTextDocument
                doc = QTextDocument()
                content = str(self.current_document.content) if self.current_document.content is not None else ""
                doc.setHtml(content)
                plain_text = doc.toPlainText()
                
                self.text_display.setPlainText(plain_text)
                self._clear_highlights()
                self.results_list.clear()
                self.results_info_label.setText("No search performed")
                if hasattr(self, 'calculated_value_label'):
                    self.calculated_value_label.setText("")
                self._verse_run_metadata = None
                if hasattr(self, 'teach_parser_btn'):
                    self.teach_parser_btn.setEnabled(True)
                # Re-parse verses if holy view active
                if getattr(self, 'holy_view_toggle', None) and self.holy_view_toggle.isChecked():
                    allow_inline = not getattr(self, 'strict_verse_toggle', None) or not self.strict_verse_toggle.isChecked()
                    self._parse_and_render_verses(plain_text, allow_inline=allow_inline)
                
                self.status_label.setText(f"Loaded: {self.current_document.title}")
            else:
                QMessageBox.warning(self, "Not Found", "Document not found in database.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load document:\n{str(e)}")
    
    def _on_calculator_changed(self, calc_name: str):
        """Handle calculator selection change."""
        # Ignore early events before widgets are constructed
        if not getattr(self, '_ui_ready', False):
            return
        if calc_name in self.calculators:
            self.current_calculator = self.calculators[calc_name]
            # Clear highlights when changing calculator
            self._clear_highlights()
            self.results_list.clear()
            self.results_info_label.setText("Calculator changed - search again to update")
            # Refresh verse totals if holy view is active
            if getattr(self, 'holy_view_toggle', None) and self.holy_view_toggle.isChecked():
            # Recompute verse totals in the rendered view
                text = self.text_display.toPlainText()
                allow_inline = not getattr(self, 'strict_verse_toggle', None) or not self.strict_verse_toggle.isChecked()
                self._parse_and_render_verses(text, allow_inline=allow_inline)
            if hasattr(self, 'calculated_value_label'):
                self.calculated_value_label.setText("")
    
    def _on_selection_changed(self):
        """Handle text selection change."""
        cursor = self.text_display.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            self.calc_selection_btn.setEnabled(True)
            if hasattr(self, "save_selection_btn"):
                self.save_selection_btn.setEnabled(True)
            self.selection_info_label.setText(f"Selected: {len(selected_text)} characters")
            # Clear any previous calculated value until user clicks Calculate
            if hasattr(self, 'calculated_value_label'):
                self.calculated_value_label.setText("")
            # If holy view is on, compute the verse total for the verse the selection is in
            if getattr(self, 'holy_view_toggle', None) and self.holy_view_toggle.isChecked():
                # Get full plain text and compute verse selection's verse number
                text = self.text_display.toPlainText()
                if text:
                    verses = self._parse_verses(text)
                    cursor_pos = self.text_display.textCursor().selectionStart()
                    for v in verses:
                        if v['start'] <= cursor_pos < v['end']:
                            # Show verse total
                            total = self.current_calculator.calculate(v['text'])
                            if hasattr(self, 'calculated_value_label'):
                                self.calculated_value_label.setText(f"Verse {v['number']} Value: {total}")
                            break
        else:
            self.calc_selection_btn.setEnabled(False)
            if hasattr(self, "save_selection_btn"):
                self.save_selection_btn.setEnabled(False)
            self.selection_info_label.setText("Select text to calculate its gematria value")
            if hasattr(self, 'calculated_value_label'):
                self.calculated_value_label.setText("")
    
    def _calculate_selection(self):
        """Calculate gematria value for selected text."""
        cursor = self.text_display.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text:
            return
        
        try:
            # Calculate gematria value and optionally include numeric face values
            value = self.current_calculator.calculate(selected_text)
            if getattr(self, 'include_numbers_checkbox', None) and self.include_numbers_checkbox.isChecked():
                value += self._sum_numeric_face_values(selected_text)
            
            # Store for saving
            self._current_selection = {
                'text': selected_text,
                'value': value,
                'breakdown': []
            }
            
            # Update both status and a dedicated value label so long phrases still show their value
            self.status_label.setText(f"Calculated: {selected_text}")
            if hasattr(self, 'calculated_value_label'):
                self.calculated_value_label.setText(f"Value: {value}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to calculate:\n{str(e)}")
    
    def _search_by_value(self):
        """Search for text segments matching a gematria value."""
        value_str = self.search_value_input.text().strip()
        
        if not value_str:
            return
        
        try:
            target_value = int(value_str)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid integer value.")
            return
        
        if not self.current_document:
            QMessageBox.warning(self, "No Document", "Please select a document first.")
            return
        
        # Get plain text
        text = self.text_display.toPlainText()
        
        if not text:
            return
        
        # Search for matches
        matches = self._find_value_matches(text, target_value)
        
        # Clear previous highlights first
        self._clear_highlights()
        
        # Display results
        self.results_list.clear()
        self.highlighted_matches = []
        
        if matches:
            for match_text, start, end in matches:
                item = QListWidgetItem(f"{match_text} = {target_value}")
                item.setData(Qt.ItemDataRole.UserRole, (start, end))
                self.results_list.addItem(item)
                self.highlighted_matches.append((start, end))
            
            self.results_info_label.setText(f"Found {len(matches)} matches for value {target_value}")
            self.status_label.setText(f"Found {len(matches)} matches")
            
            # Highlight all matches
            self._highlight_all_matches()
        else:
            self.results_info_label.setText(f"No matches found for value {target_value}")
            self.status_label.setText("No matches found")

    def _on_holy_view_toggled(self, checked: bool):
        """Toggle the Holy Book verse view."""
        if checked:
            # Hide the plain text view, show verses scroll
            self.text_display.hide()
            self.verses_scroll.show()
            if hasattr(self, 'verse_run_info_label'):
                self.verse_run_info_label.show()
            # If there is a document loaded, parse and render verses
            if self.current_document:
                text = self.text_display.toPlainText()
                self._parse_and_render_verses(text)
        else:
            # Restore the plain text view
            self.verses_scroll.hide()
            self.text_display.show()
            if hasattr(self, 'verse_run_info_label'):
                self.verse_run_info_label.hide()

    def _open_teacher_window(self):
        if not self.current_document:
            QMessageBox.information(self, "No Document", "Select a document before teaching the parser.")
            return
        allow_inline = not getattr(self, 'strict_verse_toggle', None) or not self.strict_verse_toggle.isChecked()
        dialog = HolyBookTeacherWindow(
            document_id=self.current_document.id,
            document_title=self.current_document.title,
            allow_inline=allow_inline,
            parent=self,
        )
        dialog.verses_saved.connect(self._handle_teacher_save)
        dialog.exec()

    def _handle_teacher_save(self):
        if not self.current_document:
            return
        if getattr(self, 'holy_view_toggle', None) and self.holy_view_toggle.isChecked():
            allow_inline = not getattr(self, 'strict_verse_toggle', None) or not self.strict_verse_toggle.isChecked()
            text = self.text_display.toPlainText()
            self._parse_and_render_verses(text, allow_inline=allow_inline)
        self.status_label.setText("Holy Book Teacher: saved curated verses")

    def _on_include_numbers_toggled(self, state: int):
        """Handler when the include-numeric-face-values toggle changes.

        Update the calculated selection and re-render verse totals if the Holy Book View is enabled.
        """
        # Recompute selection value if there is a selection
        cursor = self.text_display.textCursor()
        selected_text = cursor.selectedText()
        if selected_text:
            # Recalculate selection value
            value = self.current_calculator.calculate(selected_text)
            if getattr(self, 'include_numbers_checkbox', None) and self.include_numbers_checkbox.isChecked():
                value += self._sum_numeric_face_values(selected_text)
            self._current_selection = {'text': selected_text, 'value': value, 'breakdown': []}
            if hasattr(self, 'calculated_value_label'):
                self.calculated_value_label.setText(f"Value: {value}")

        # Re-render verse view if active
        if getattr(self, 'holy_view_toggle', None) and self.holy_view_toggle.isChecked():
            text = self.text_display.toPlainText()
            allow_inline = not getattr(self, 'strict_verse_toggle', None) or not self.strict_verse_toggle.isChecked()
            self._parse_and_render_verses(text, allow_inline=allow_inline)
        # Re-run active search to reflect changes in numeric inclusion
        if getattr(self, 'search_value_input', None) and self.search_value_input.text().strip():
            self._search_by_value()

    def _parse_verses(self, text: str, allow_inline: bool = True) -> List[Dict[str, Any]]:
        metadata = self._load_verses_metadata(allow_inline)
        if metadata is not None:
            self._verse_run_metadata = metadata
            return metadata.get('verses', [])

        fallback = parse_verses(text, allow_inline=allow_inline)
        self._verse_run_metadata = {
            'document_id': self.current_document.id if self.current_document else None,
            'source': 'local-parser',
            'verses': fallback,
            'anomalies': {},
            'rules_applied': [],
        }
        self.status_label.setText(
            "Holy Book View: parser service unavailable, showing local parse"
        )
        return fallback

    def _load_verses_metadata(self, allow_inline: bool) -> Optional[Dict[str, Any]]:
        if not self.current_document:
            return None
        try:
            with verse_teacher_service_context() as teacher_service:
                return teacher_service.get_or_parse_verses(
                    self.current_document.id,
                    allow_inline=allow_inline,
                    apply_rules=True,
                )
        except Exception as exc:
            logger.exception("Verse teacher load failed", exc_info=exc)
            return None

    def _parse_and_render_verses(self, text: str, allow_inline: bool = True):
        """Parse the plain text for verses and render them in the verses view."""
        # Parse
        verses = self._parse_verses(text, allow_inline=allow_inline)
        self._parsed_verses = verses
        source = 'parser'
        if getattr(self, '_verse_run_metadata', None):
            source = self._verse_run_metadata.get('source', source)
        # Update status bar
        self.status_label.setText(
            f"Holy Book View ({source}): parsed {len(verses)} verses"
        )
        self._update_verse_run_info()
        # Render
        self._clear_verses_display()
        if not verses:
            notice = QLabel("No verses detected for Holy Book View.")
            notice.setStyleSheet("color: #64748b;")
            self.verses_layout.addWidget(notice)
            if hasattr(self, 'save_verses_btn'):
                self.save_verses_btn.setEnabled(False)
            return

        for v in verses:
            widget = self._create_verse_widget(v)
            self.verses_layout.addWidget(widget)
        # Add stretch to keep layout tidy
        self.verses_layout.addStretch()
        if hasattr(self, 'save_verses_btn'):
            self.save_verses_btn.setEnabled(True)

    def _update_verse_run_info(self):
        label = getattr(self, 'verse_run_info_label', None)
        if label is None:
            return
        if not getattr(self, 'holy_view_toggle', None) or not self.holy_view_toggle.isChecked():
            label.hide()
            label.setText("")
            return
        if not getattr(self, '_verse_run_metadata', None):
            label.hide()
            label.setText("")
            return
        data = self._verse_run_metadata
        anomalies = data.get('anomalies') or {}
        counts = []
        if anomalies.get('duplicates'):
            counts.append(f"duplicates: {len(anomalies['duplicates'])}")
        if anomalies.get('missing_numbers'):
            counts.append(f"missing: {len(anomalies['missing_numbers'])}")
        if anomalies.get('overlaps'):
            counts.append(f"overlaps: {len(anomalies['overlaps'])}")
        if data.get('rules_applied'):
            counts.append(f"rules: {len(data['rules_applied'])}")
        info = f"Source: {data.get('source', 'parser')}"
        if counts:
            info = info + " · " + ", ".join(counts)
        label.setText(info)
        label.show()

    def _clear_verses_display(self):
        """Clear verse widgets from the container."""
        while self.verses_layout.count():
            item = self.verses_layout.takeAt(0)
            if item:
                w = item.widget()
                if w:
                    w.deleteLater()

    def _create_verse_widget(self, verse: Dict[str, Any]) -> QWidget:
        """Build a small widget for a verse including text, calculated value and actions."""
        box = QGroupBox(f"Verse {verse['number']}")
        layout = QHBoxLayout(box)
        # Verse text; keep it compact
        text_label = QLabel(verse['text'])
        text_label.setWordWrap(True)
        text_label.setMinimumWidth(400)
        layout.addWidget(text_label, 3)

        # Value label
        value = 0
        try:
            value = self.current_calculator.calculate(verse['text'])
            # Add numeric face value if toggled
            if getattr(self, 'include_numbers_checkbox', None) and self.include_numbers_checkbox.isChecked():
                value += self._sum_numeric_face_values(verse['text'])
        except Exception:
            value = 0
        value_label = QLabel(f"Value: {value}")
        value_label.setStyleSheet("font-weight: 600; color: #2563eb;")
        layout.addWidget(value_label)

        action_layout = QVBoxLayout()
        jump_btn = QPushButton("Jump")
        jump_btn.setMaximumWidth(80)
        jump_btn.clicked.connect(lambda _, s=verse['start'], e=verse['end']: self._jump_to_range(s, e))
        action_layout.addWidget(jump_btn)

        save_btn = QPushButton("Save")
        save_btn.setMaximumWidth(80)
        save_btn.clicked.connect(lambda _, v=verse: self._save_single_verse(v))
        action_layout.addWidget(save_btn)

        layout.addLayout(action_layout)
        return box

    def _jump_to_range(self, start: int, end: int):
        """Select and focus the given character range in the main text display."""
        try:
            cursor = self.text_display.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            self.text_display.setTextCursor(cursor)
            self.text_display.setFocus()
        except Exception:
            pass

    def _sum_numeric_face_values(self, text: str) -> int:
        """Wrapper for numeric utils helper (keeps UI code simple)."""
        return sum_numeric_face_values(text)

    def _save_single_verse(self, verse: Dict[str, Any]):
        """Save a single verse as a calculation record."""
        try:
            val = self.current_calculator.calculate(verse['text'])
            if getattr(self, 'include_numbers_checkbox', None) and self.include_numbers_checkbox.isChecked():
                val += self._sum_numeric_face_values(verse['text'])
            notes, ok = QInputDialog.getMultiLineText(
                self,
                "Save Verse",
                f"Saving Verse {verse['number']}: {verse['text']} = {val}\n\nNotes (optional):",
                ""
            )
            if ok:
                self.calculation_service.save_calculation(
                    text=verse['text'],
                    value=val,
                    calculator=self.current_calculator,
                    breakdown=[],
                    notes=notes,
                    source=f"Document: {self.current_document.title if self.current_document else 'Unknown'}"
                )
                QMessageBox.information(self, "Saved", "Verse calculation saved!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save verse:\n{str(e)}")

    def _save_verse_totals(self):
        """Save all verse totals for the current parsed verses."""
        if not getattr(self, '_parsed_verses', None):
            QMessageBox.information(self, "No Verses", "No parsed verses to save.")
            return
        reply = QMessageBox.question(
            self,
            "Save All Verse Totals",
            f"Save all {len(self._parsed_verses)} verse totals as calculations?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            saved = 0
            for verse in self._parsed_verses:
                val = self.current_calculator.calculate(verse['text'])
                if getattr(self, 'include_numbers_checkbox', None) and self.include_numbers_checkbox.isChecked():
                    val += self._sum_numeric_face_values(verse['text'])
                self.calculation_service.save_calculation(
                    text=verse['text'],
                    value=val,
                    calculator=self.current_calculator,
                    breakdown=[],
                    source=f"Document: {self.current_document.title if self.current_document else 'Unknown'}"
                )
                saved += 1
            QMessageBox.information(self, "Saved", f"Saved {saved} verse calculations!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save verse totals:\n{str(e)}")
    
    def _find_value_matches(self, text: str, target_value: int) -> List[Tuple[str, int, int]]:
        """
        Find all text segments that match the target gematria value.
        
        Args:
            text: The text to search
            target_value: The target gematria value
            
        Returns:
            List of (match_text, start_pos, end_pos) tuples
        """
        matches = []
        words = []
        positions = []
        
        # Split text into words and track positions
        current_word = ""
        start_pos = 0
        
        for i, char in enumerate(text):
            # Treat common punctuation and whitespace as separators
            if char.isspace() or char in '.,;:!?()[]{}"\'–—-:':
                if current_word:
                    words.append(current_word)
                    positions.append((start_pos, i))
                    current_word = ""
            else:
                if not current_word:
                    start_pos = i
                current_word += char
        
        if current_word:
            words.append(current_word)
            positions.append((start_pos, len(text)))
        
        # Check individual words
        for word, (start, end) in zip(words, positions):
            try:
                value = self.current_calculator.calculate(word)
                if getattr(self, 'include_numbers_checkbox', None) and self.include_numbers_checkbox.isChecked():
                    value += self._sum_numeric_face_values(word)
                if value == target_value:
                    matches.append((word, start, end))
            except:
                pass
        
        # Sliding window over words up to max length
        max_words_widget = getattr(self, 'max_words_spin', None)
        max_len = max_words_widget.value() if max_words_widget is not None else 8
        n_words = len(words)
        for window_size in range(2, min(max_len, n_words) + 1):
            for i in range(n_words - window_size + 1):
                start = positions[i][0]
                end = positions[i + window_size - 1][1]
                phrase_text = text[start:end].strip()
                try:
                    value = self.current_calculator.calculate(phrase_text)
                    if getattr(self, 'include_numbers_checkbox', None) and self.include_numbers_checkbox.isChecked():
                        value += self._sum_numeric_face_values(phrase_text)
                    if value == target_value:
                        if not any(s <= start and e >= end for _, s, e in matches):
                            matches.append((phrase_text, start, end))
                except:
                    pass
        
        return matches
    
    def _highlight_all_matches(self):
        """Highlight all matched segments in the text."""
        # Don't clear first - we'll apply highlights on top
        
        # Create highlight format
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("#fef3c7"))  # Yellow highlight
        highlight_format.setForeground(QColor("#000000"))  # Black text
        highlight_format.setFontWeight(QFont.Weight.Normal)
        
        # Save current cursor position
        original_cursor = self.text_display.textCursor()
        original_position = original_cursor.position()
        
        cursor = self.text_display.textCursor()
        
        for start, end in self.highlighted_matches:
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(highlight_format)
        
        # Restore cursor position
        cursor.setPosition(original_position)
        self.text_display.setTextCursor(cursor)
    
    def _clear_highlights(self):
        """Clear all text highlights."""
        cursor = self.text_display.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        
        normal_format = QTextCharFormat()
        normal_format.setBackground(QColor("#ffffff"))
        normal_format.setForeground(QColor("#000000"))
        
        cursor.setCharFormat(normal_format)
        
        # Reset cursor
        cursor.setPosition(0)
        self.text_display.setTextCursor(cursor)
        
        self.highlighted_matches = []
        self.results_info_label.setText("Highlights cleared")
        if hasattr(self, 'calculated_value_label'):
            self.calculated_value_label.setText("")
    
    def _on_result_clicked(self, item: QListWidgetItem):
        """Handle clicking on a result item."""
        position_data = item.data(Qt.ItemDataRole.UserRole)
        
        if position_data:
            start, end = position_data
            
            # Scroll to and select the match
            cursor = self.text_display.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
            self.text_display.setTextCursor(cursor)
            self.text_display.setFocus()
    
    def _show_result_context_menu(self, position):
        """Show context menu for result items."""
        item = self.results_list.itemAt(position)
        if not item:
            return
        
        menu = QMenu(self)
        
        copy_action = QAction("Copy Text", self)
        copy_action.triggered.connect(lambda: self._copy_result_text(item))
        menu.addAction(copy_action)
        
        save_action = QAction("Save as Calculation", self)
        save_action.triggered.connect(lambda: self._save_result_as_calculation(item))
        menu.addAction(save_action)
        
        menu.exec(self.results_list.mapToGlobal(position))
    
    def _copy_result_text(self, item: QListWidgetItem):
        """Copy result text to clipboard."""
        from PyQt6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(item.text())
    
    def _save_result_as_calculation(self, item: QListWidgetItem):
        """Save a result as a calculation record."""
        # Extract text from item
        text = item.text().split(" = ")[0]
        
        try:
            value = self.current_calculator.calculate(text)
            
            # Prompt for notes
            notes, ok = QInputDialog.getMultiLineText(
                self,
                "Save Calculation",
                f"Saving: {text} = {value}\n\nNotes (optional):",
                ""
            )
            
            if ok:
                record = self.calculation_service.save_calculation(
                    text=text,
                    value=value,
                    calculator=self.current_calculator,
                    breakdown=[],
                    notes=notes,
                    source=f"Document: {self.current_document.title if self.current_document else 'Unknown'}"
                )
                
                QMessageBox.information(
                    self,
                    "Saved",
                    f"Calculation saved successfully!"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save:\n{str(e)}")
    
    def _save_matches(self):
        """Save all matched results as calculations."""
        if not self.highlighted_matches:
            QMessageBox.information(self, "No Matches", "No matches to save.")
            return
        
        reply = QMessageBox.question(
            self,
            "Save All Matches",
            f"Save all {len(self.highlighted_matches)} matches as calculations?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                saved = 0
                text = self.text_display.toPlainText()
                
                for start, end in self.highlighted_matches:
                    match_text = text[start:end]
                    value = self.current_calculator.calculate(match_text)
                    if getattr(self, 'include_numbers_checkbox', None) and self.include_numbers_checkbox.isChecked():
                        value += self._sum_numeric_face_values(match_text)
                    self.calculation_service.save_calculation(
                        text=match_text,
                        value=value,
                        calculator=self.current_calculator,
                        breakdown=[],
                        source=f"Document: {self.current_document.title if self.current_document else 'Unknown'}"
                    )
                    saved += 1
                
                QMessageBox.information(
                    self,
                    "Saved",
                    f"Successfully saved {saved} calculations!"
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save matches:\n{str(e)}")
    
    def _save_current_calculation(self):
        """Save the active highlight's calculation (auto-calculates if needed)."""
        cursor = self.text_display.textCursor()
        selected_text = cursor.selectedText()
        selection_data = None

        if selected_text:
            try:
                value = self.current_calculator.calculate(selected_text)
                if getattr(self, 'include_numbers_checkbox', None) and self.include_numbers_checkbox.isChecked():
                    value += self._sum_numeric_face_values(selected_text)
                selection_data = {
                    'text': selected_text,
                    'value': value,
                    'breakdown': []
                }
                self._current_selection = selection_data
                self.status_label.setText(f"Calculated: {selected_text} = {value}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to calculate selection:\n{str(e)}")
                return
        elif self._current_selection:
            # Recompute selection value using current setting if needed.
            selection_data = self._current_selection
            try:
                if getattr(self, 'include_numbers_checkbox', None) and self.include_numbers_checkbox.isChecked():
                    computed = self.current_calculator.calculate(selection_data['text']) + self._sum_numeric_face_values(selection_data['text'])
                    selection_data['value'] = computed
                else:
                    selection_data['value'] = self.current_calculator.calculate(selection_data['text'])
            except Exception:
                pass
        else:
            QMessageBox.information(self, "No Selection", "Highlight text to save its calculation.")
            return

        try:
            notes, ok = QInputDialog.getMultiLineText(
                self,
                "Save Calculation",
                f"Saving: {selection_data['text']} = {selection_data['value']}\n\nNotes (optional):",
                ""
            )

            if ok:
                # Cast values to primitive types to satisfy repository API typing
                text_val: str = str(selection_data['text'])
                value_val: int = int(selection_data['value'])
                breakdown_val: list = list(selection_data.get('breakdown', []))
                self.calculation_service.save_calculation(
                    text=text_val,
                    value=value_val,
                    calculator=self.current_calculator,
                    breakdown=breakdown_val,
                    notes=notes,
                    source=f"Document: {self.current_document.title if self.current_document else 'Unknown'}"
                )

                QMessageBox.information(
                    self,
                    "Saved",
                    "Calculation saved successfully!"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save:\n{str(e)}")
