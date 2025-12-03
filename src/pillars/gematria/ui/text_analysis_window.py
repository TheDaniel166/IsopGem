"""Text Analysis Window - Analyze documents with Gematria."""
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QTextEdit, QComboBox, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox, QGroupBox,
    QMenu, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor, QFont, QAction
from typing import List, Dict, Optional, Tuple
from PyQt6.QtWidgets import QSpinBox
from pillars.document_manager.services.document_service import document_service_context

from ..services.base_calculator import GematriaCalculator
from ..services import CalculationService
from pillars.document_manager.models.document import Document


class TextAnalysisWindow(QDialog):
    """Window for analyzing document text with Gematria."""
    
    def __init__(self, calculators: List[GematriaCalculator], parent=None):
        """
        Initialize the text analysis window.
        
        Args:
            calculators: List of available gematria calculators
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.calculators: Dict[str, GematriaCalculator] = {
            calc.name: calc for calc in calculators
        }
        self.current_calculator: GematriaCalculator = calculators[0]
        self.calculation_service = CalculationService()
        
        # Current state
        self.current_document: Optional[Document] = None
        self.highlighted_matches: List[Tuple[int, int]] = []  # List of (start, end) positions
        
        self.setWindowTitle("Gematria Text Analysis")
        self.setMinimumSize(1200, 800)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.setModal(False)
        
        self._setup_ui()
        self._load_documents()
    
    def _setup_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)
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
        toolbar_layout.addWidget(self.calculator_combo)
        
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
        
        search_layout.addLayout(action_layout)
        
        right_layout.addWidget(search_group)
        
        # Save current selection (no breakdown display)
        save_current_btn = QPushButton("💾 Save Current Selection")
        save_current_btn.clicked.connect(self._save_current_calculation)
        save_current_btn.setMinimumHeight(32)
        save_current_btn.setStyleSheet("""
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
        right_layout.addWidget(save_current_btn)
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
                documents = service.get_all_documents()
            
            self.document_combo.clear()
            self.document_combo.addItem("-- Select a document --", None)
            
            for doc in documents:
                self.document_combo.addItem(f"{doc.title} ({doc.id})", doc.id)
            
            if len(documents) == 0:
                self.status_label.setText("No documents found in database")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load documents:\n{str(e)}")
    
    def _on_document_selected(self, index: int):
        """Handle document selection."""
        doc_id = self.document_combo.currentData()
        
        if doc_id is None:
            self.text_display.clear()
            self.current_document = None
            self.status_label.setText("Ready - Select a document to begin")
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
                
                self.status_label.setText(f"Loaded: {self.current_document.title}")
            else:
                QMessageBox.warning(self, "Not Found", "Document not found in database.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load document:\n{str(e)}")
    
    def _on_calculator_changed(self, calc_name: str):
        """Handle calculator selection change."""
        if calc_name in self.calculators:
            self.current_calculator = self.calculators[calc_name]
            # Clear highlights when changing calculator
            self._clear_highlights()
            self.results_list.clear()
            self.results_info_label.setText("Calculator changed - search again to update")
    
    def _on_selection_changed(self):
        """Handle text selection change."""
        cursor = self.text_display.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            self.calc_selection_btn.setEnabled(True)
            self.selection_info_label.setText(f"Selected: {len(selected_text)} characters")
        else:
            self.calc_selection_btn.setEnabled(False)
            self.selection_info_label.setText("Select text to calculate its gematria value")
    
    def _calculate_selection(self):
        """Calculate gematria value for selected text."""
        cursor = self.text_display.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text:
            return
        
        try:
            # Calculate value
            value = self.current_calculator.calculate(selected_text)
            
            # Store for saving
            self._current_selection = {
                'text': selected_text,
                'value': value,
                'breakdown': []
            }
            
            self.status_label.setText(f"Calculated: {selected_text} = {value}")
            
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
        """Save the current calculation from the selection."""
        if not hasattr(self, '_current_selection'):
            QMessageBox.information(self, "No Calculation", "Calculate a selection first.")
            return
        
        sel = self._current_selection
        
        try:
            # Prompt for notes
            notes, ok = QInputDialog.getMultiLineText(
                self,
                "Save Calculation",
                f"Saving: {sel['text']} = {sel['value']}\n\nNotes (optional):",
                ""
            )
            
            if ok:
                record = self.calculation_service.save_calculation(
                    text=sel['text'],
                    value=sel['value'],
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
