from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                            QTextEdit, QComboBox, QLabel, QPushButton,
                            QSpinBox, QFileDialog, QCheckBox, QSplitter,
                            QLineEdit, QGroupBox, QToolTip, QMessageBox)
from PyQt5.QtCore import (Qt, QPropertyAnimation, QParallelAnimationGroup,
                         pyqtProperty, QPoint, QPointF, QSequentialAnimationGroup,
                         QEasingCurve, QStandardPaths)
from PyQt5.QtGui import (QTextCharFormat, QColor, QTextCursor, QPalette,
                        QBrush, QLinearGradient, QRadialGradient,
                        QSyntaxHighlighter, QPainter)
from core.gematria.calculator import GematriaCalculator
import random
import re
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QEvent
import os

class ToggleSwitch(QWidget):
    clicked = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        self._is_checked = False
        self._position = 5  # Initialize position
        
        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    @pyqtProperty(int)
    def position(self):
        return self._position
    
    @position.setter
    def position(self, pos):
        self._position = pos
        self.update()
        
    def is_checked(self):
        return self._is_checked
    
    def mousePressEvent(self, event):
        self._is_checked = not self._is_checked
        
        # Set animation start and end positions
        start = self._position
        end = 35 if self._is_checked else 5
        
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)
        self.animation.start()
        
        self.update()
        self.clicked.emit(self._is_checked)


    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        brush = QBrush(QColor("#777777") if not self._is_checked else QColor("#2196F3"))
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        
        painter.setBrush(QBrush(Qt.white))
        x = 35 if self._is_checked else 5
        painter.drawEllipse(x, 5, 20, 20)

        
    
class AnimatedHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.matches = []
        self._alpha = 255  # Full opacity for highlights

    def highlightBlock(self, text):
        block_position = self.currentBlock().position()
        
        for match in self.matches:
            start = match['start_index'] - block_position
            length = match['end_index'] - match['start_index']
            
            # Only highlight if the match is in this block
            if start >= 0 and start + length <= len(text):
                fmt = QTextCharFormat()
                # Create a semi-transparent yellow highlight
                highlight_color = QColor(255, 255, 0, 100)  # RGBA
                fmt.setBackground(QBrush(highlight_color))
                # Add a tooltip with match information
                fmt.setToolTip(f"Value: {match['value']} ({match['cipher_type']})")
                self.setFormat(start, length, fmt)

class TextAnalysisPanel(QWidget):
    def __init__(self):
        super().__init__()
        # Get app's base directory
        self.app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.documents_dir = os.path.join(self.app_dir, 'documents')
        
        # Create documents directory if it doesn't exist
        if not os.path.exists(self.documents_dir):
            os.makedirs(self.documents_dir)
            
        self.calculator = GematriaCalculator()
        self.current_results = []
        self.current_text = ""
        self.init_ui()
        self.connect_signals()
        self.highlighter = AnimatedHighlighter(self.source_text.document())

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header Section
        header = QLabel("Text Analysis")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        layout.addWidget(header)
        
        # Control Section
        control_group = QGroupBox("Controls")
        control_layout = QVBoxLayout()
        
        # Button toolbar
        button_layout = QHBoxLayout()
        self.import_button = QPushButton("Import Text")
        self.clear_button = QPushButton("Clear")
        self.search_button = QPushButton("Search")
        self.export_button = QPushButton("Export")
        
        for btn in [self.import_button, self.clear_button, 
                   self.search_button, self.export_button]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 5px 15px;
                    border-radius: 3px;
                    background: #f8f9fa;
                    border: 1px solid #ddd;
                }
                QPushButton:hover {
                    background: #e9ecef;
                }
            """)
            button_layout.addWidget(btn)
        
        control_layout.addLayout(button_layout)
        
        # Search parameters
        params_layout = QHBoxLayout()
        self.value_input = QSpinBox()
        self.value_input.setRange(1, 99999)
        self.cipher_select = QComboBox()
        self.cipher_select.addItems(['TQ English', 'Hebrew Standard', 'Hebrew Gadol', 'Greek'])
        
        params_layout.addWidget(QLabel("Target Value:"))
        params_layout.addWidget(self.value_input)
        params_layout.addWidget(QLabel("Cipher:"))
        params_layout.addWidget(self.cipher_select)
        control_layout.addLayout(params_layout)
        
        # Filter Section
        filter_group = QGroupBox("Filters")
        filter_layout = QVBoxLayout()
        
        # Length filter
        length_layout = QHBoxLayout()
        self.any_length = QCheckBox("Any Word Count")
        self.any_length.setChecked(True)  # Set checked by default
        self.phrase_length = QSpinBox()
        self.phrase_length.setRange(1, 100)
        self.phrase_length.setValue(1)
        self.phrase_length.setEnabled(False)  # Disable since "Any Word Count" is checked
        length_layout.addWidget(self.any_length)
        length_layout.addWidget(QLabel("Number of Words:"))
        length_layout.addWidget(self.phrase_length)
        length_layout.addStretch()
        
        # Pattern filter
        pattern_layout = QHBoxLayout()
        self.pattern_input = QLineEdit()
        self.pattern_input.setPlaceholderText("Enter pattern to match...")
        self.regex_checkbox = QCheckBox("Use Regex")
        pattern_layout.addWidget(self.pattern_input)
        pattern_layout.addWidget(self.regex_checkbox)
        
        filter_layout.addLayout(length_layout)
        filter_layout.addLayout(pattern_layout)
        filter_group.setLayout(filter_layout)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        layout.addWidget(filter_group)
        
        # Text Areas
        text_group = QGroupBox("Text Analysis")
        text_layout = QVBoxLayout()
        
        self.source_text = QTextEdit()
        self.source_text.setPlaceholderText("Enter or paste text to analyze...")
        self.source_text.viewport().installEventFilter(self)
        
        # Results toggle
        toggle_layout = QHBoxLayout()
        self.result_toggle = ToggleSwitch()
        toggle_layout.addWidget(QLabel("Raw Results"))
        toggle_layout.addWidget(self.result_toggle)
        toggle_layout.addWidget(QLabel("Smart Phrases"))
        toggle_layout.addStretch()
        
        self.stats_label = QLabel("Found: 0 matches")
        self.stats_label.setStyleSheet("color: #666;")
        
        text_layout.addWidget(self.source_text)
        text_layout.addLayout(toggle_layout)
        text_layout.addWidget(self.stats_label)
        
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)
        
        self.setLayout(layout)

    def connect_signals(self):
        # Button connections
        self.import_button.clicked.connect(self.import_text)
        self.clear_button.clicked.connect(self.clear_text)
        self.search_button.clicked.connect(self.perform_search)
        self.export_button.clicked.connect(self.export_results)
        
        # Input field connections
        self.pattern_input.textChanged.connect(self.filter_results)
        self.result_toggle.clicked.connect(lambda checked: self.update_results_display(checked))
        
        # Filter connections
        self.any_length.stateChanged.connect(lambda state: self.phrase_length.setEnabled(not state))
        self.phrase_length.valueChanged.connect(self.filter_results)
        self.pattern_input.textChanged.connect(self.filter_results)
        self.regex_checkbox.stateChanged.connect(self.filter_results)

    def import_text(self):
        options = QFileDialog.Options()
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Text File",
            self.documents_dir,  # Use app's documents directory
            "Text Files (*.txt);;All Files (*)",
            options=options
        )
        
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.source_text.setPlainText(file.read())

    def find_raw_combinations(self, text, target_value, cipher):
        """Find combinations of words that sum to target value more efficiently"""
        # Pre-process text into words with their positions
        words_with_positions = []
        current_pos = 0
        text_words = text.split()
        
        for word in text_words:
            # Find actual position in original text
            pos = text.find(word, current_pos)
            words_with_positions.append({
                'word': word,
                'start': pos,
                'end': pos + len(word),
                'value': self.calculator.calculate(word, cipher)
            })
            current_pos = pos + len(word)

        combinations = []
        max_phrase_length = self.phrase_length.value() if not self.any_length.isChecked() else len(text_words)
        
        # Use sliding window approach
        for start_idx in range(len(words_with_positions)):
            current_sum = 0
            current_words = []
            
            for end_idx in range(start_idx, min(start_idx + max_phrase_length, len(words_with_positions))):
                word_info = words_with_positions[end_idx]
                current_sum += word_info['value']
                current_words.append(word_info)
                
                # Check if current combination matches criteria
                if current_sum == target_value:
                    if self.any_length.isChecked() or len(current_words) == self.phrase_length.value():
                        phrase = ' '.join(w['word'] for w in current_words)
                        combinations.append({
                            'phrase': phrase,
                            'start_index': current_words[0]['start'],
                            'end_index': current_words[-1]['end'],
                            'value': target_value,
                            'cipher_type': cipher
                        })
                elif current_sum > target_value:
                    # Early break if sum exceeds target
                    break

        return combinations

    def find_smart_combinations(self, raw_combinations):
        """Filter raw combinations to only include valid phrases"""
        smart_results = []
        for combo in raw_combinations:
            words = combo['phrase'].split()
            if self.is_valid_phrase(words):
                smart_results.append(combo)
        return smart_results

    def is_valid_phrase(self, words):
        """Check if a phrase is valid for smart search"""
        if len(words) <= 3:
            return True
            
        # Common word lists for checking phrase validity
        articles = {'a', 'an', 'the'}
        prepositions = {
            'in', 'on', 'at', 'by', 'for', 'with', 'to', 'of', 'from', 'into',
            'onto', 'upon', 'within', 'without', 'through', 'beyond', 'among',
            'between', 'amid', 'across'
        }
        conjunctions = {
            'and', 'or', 'but', 'nor', 'yet', 'so', 'for', 'because',
            'although', 'unless', 'since', 'while'
        }
        pronouns = {
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
            'mine', 'yours', 'hers', 'ours', 'theirs'
        }
        auxiliaries = {
            'am', 'is', 'are', 'was', 'were', 'be', 'being', 'been',
            'have', 'has', 'had', 'do', 'does', 'did',
            'can', 'could', 'may', 'might', 'must', 'shall', 'should', 'will', 'would'
        }
        
        # Check for various indicators of a valid phrase
        has_article = any(word.lower() in articles for word in words)
        has_preposition = any(word.lower() in prepositions for word in words)
        has_conjunction = any(word.lower() in conjunctions for word in words)
        has_pronoun = any(word.lower() in pronouns for word in words)
        has_auxiliary = any(word.lower() in auxiliaries for word in words)
        
        starts_capitalized = words[0][0].isupper() if words else False
        ends_with_punctuation = words[-1][-1] in {'.', '!', '?'} if words else False
        
        valid_endings = {'up', 'down', 'in', 'out', 'on', 'off', 'away', 'back'}
        has_valid_ending = words[-1].lower() in valid_endings if words else False
        
        has_verb_pattern = any(
            word.lower().endswith(('ing', 'ed', 's'))
            for word in words
        )
        
        # Combine checks for final decision
        basic_structure = (has_article or has_preposition or has_conjunction or
                          has_pronoun or has_auxiliary)
        advanced_structure = (starts_capitalized or ends_with_punctuation or
                             has_valid_ending or has_verb_pattern)
        
        return basic_structure or advanced_structure

    def analyze_text(self, text):
        """Analyze text with optimized filtering"""
        if not text:
            return
            
        target_value = self.value_input.value()
        cipher = self.cipher_select.currentText()
        
        # Cache the pattern if using regex
        pattern_text = self.pattern_input.text()
        pattern = None
        if pattern_text and self.regex_checkbox.isChecked():
            try:
                pattern = re.compile(pattern_text, re.IGNORECASE)
            except re.error:
                QMessageBox.warning(self, "Invalid Regex", "The regular expression pattern is invalid.")
                return
        
        # Get combinations with integrated length filtering
        raw_combinations = self.find_raw_combinations(text, target_value, cipher)
        
        # Apply pattern filtering if needed
        if pattern_text:
            if pattern:  # Regex
                raw_combinations = [r for r in raw_combinations if pattern.search(r['phrase'])]
            else:  # Plain text
                pattern_text = pattern_text.lower()
                raw_combinations = [r for r in raw_combinations if pattern_text in r['phrase'].lower()]
        
        # Apply smart filtering if needed
        if self.result_toggle.is_checked():
            filtered_results = self.find_smart_combinations(raw_combinations)
        else:
            filtered_results = raw_combinations
        
        self.current_results = filtered_results
        
        # Find main window
        main_window = None
        widget = self
        while widget.parent():
            widget = widget.parent()
            if hasattr(widget, 'panel_manager'):
                main_window = widget
                break

        if main_window:
            # Store results and create results panel
            main_window.analysis_results = {
                'results': filtered_results,
                'target_value': target_value,
                'cipher': cipher,
                'mode': 'Smart' if self.result_toggle.is_checked() else 'Raw'
            }
            main_window.panel_manager.create_panel('analysis_results')

    def display_results(self, raw_results, smart_results):
        """Update the stats label with current results"""
        total = len(raw_results) if raw_results else len(smart_results)
        mode = "Raw" if raw_results else "Smart"
        self.stats_label.setText(f"Found: {total} {mode} matches")

    def highlight_matches(self, raw_matches, smart_matches):
        self.highlighter.set_matches(raw_matches, smart_matches)


    def clear_text(self):
        """Clear all text and results"""
        self.source_text.clear()
        self.current_text = ""
        self.current_results = []
        self.stats_label.setText("Found: 0 matches")
        self.highlighter.matches = []
        self.highlighter.rehighlight()

    def perform_search(self):
        """Execute the search on current text"""
        text = self.source_text.toPlainText()
        if not text:
            return
        self.current_text = text
        self.analyze_text(text)

    def export_results(self):
        """Export current results to a file"""
        if not self.current_results:
            return
            
        # Create a default filename with timestamp
        from datetime import datetime
        default_filename = f"text_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        default_path = os.path.join(self.documents_dir, default_filename)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            default_path,
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(f"Text Analysis Results\n")
                    file.write(f"{'='*40}\n\n")
                    file.write(f"Target Value: {self.value_input.value()}\n")
                    file.write(f"Cipher: {self.cipher_select.currentText()}\n")
                    file.write(f"Total Matches: {len(self.current_results)}\n\n")
                    
                    for match in self.current_results:
                        file.write(f"Phrase: {match['phrase']}\n")
                        file.write(f"Value: {match['value']}\n")
                        file.write(f"Cipher: {match['cipher_type']}\n")
                        file.write(f"{'-'*40}\n\n")
                
                # Optional: Show success message
                QMessageBox.information(self, "Success", "Results exported successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to export results: {str(e)}")

    def filter_results(self):
        """Apply filters to current results without performing new search"""
        if not self.current_results:  # Only filter if we have results
            return
        
        # Apply current filters to existing results
        filtered = self.current_results.copy()
        
        # Apply pattern filter if exists
        pattern_text = self.pattern_input.text()
        if pattern_text:
            if self.regex_checkbox.isChecked():
                try:
                    pattern = re.compile(pattern_text, re.IGNORECASE)
                    filtered = [r for r in filtered if pattern.search(r['phrase'])]
                except re.error:
                    pass  # Invalid regex, skip filtering
            else:
                pattern_text = pattern_text.lower()
                filtered = [r for r in filtered if pattern_text in r['phrase'].lower()]
        
        # Update display with filtered results
        self.current_results = filtered
        self.display_results(filtered if not self.result_toggle.is_checked() else [],
                            filtered if self.result_toggle.is_checked() else [])

    def update_results_display(self, is_smart_mode):
        """Update results when toggling between raw and smart mode"""
        if self.current_text:
            self.analyze_text(self.current_text)

    def check_category(self, phrase, category):
        if category == 'Vowels':
            return all(char in 'aeiou' for char in phrase)
        elif category == 'Consonants':
            return all(char in 'bcdfghjklmnpqrstvwxyz' for char in phrase)
        elif category == 'Numbers':
            return all(char.isdigit() for char in phrase)
        elif category == 'Symbols':
            return all(char in '!@#$%^&*()_+-=[]{}|;:",.<>?/' for char in phrase)
        elif category == 'Special Characters':
            return all(char in '!@#$%^&*()_+-=[]{}|;:",.<>?/' for char in phrase)
        elif category == 'Letters':
            return all(char.isalpha() for char in phrase)
        elif category == 'Numbers and Letters':
            return all(char.isalnum() for char in phrase)
        elif category == 'Letters and Symbols':
            return all(char.isalnum() or char in '!@#$%^&*()_+-=[]{}|;:",.<>?/' for char in phrase)

    def eventFilter(self, obj, event):
        if obj == self.source_text.viewport():
            if event.type() == QEvent.MouseMove:
                # Get cursor position under mouse
                cursor = self.source_text.cursorForPosition(event.pos())
                position = cursor.position()
                
                # Check if position is within any match
                for match in self.current_results:
                    if match['start_index'] <= position <= match['end_index']:
                        # Show tooltip with match information
                        QToolTip.showText(
                            self.source_text.mapToGlobal(event.pos()),
                            f"Phrase: {match['phrase']}\n"
                            f"Value: {match['value']}\n"
                            f"Cipher: {match['cipher_type']}"
                        )
                        return True
                
                QToolTip.hideText()
        
        return super().eventFilter(obj, event)

# TODO: Future Improvements

# Search and History
# TODO: Implement search history dropdown
# TODO: Add ability to save favorite search configurations
# TODO: Add search presets for common gematria values
# TODO: Implement batch searching for multiple values

# Real-time Features
# TODO: Add real-time analysis option while typing
# TODO: Add live match counter
# TODO: Add performance optimizations for large texts
# TODO: Add auto-save feature for work in progress

# Advanced Filtering
# TODO: Add min/max value filters
# TODO: Add word category filters (nouns, verbs, etc.)
# TODO: Add case sensitivity option for pattern matching
# TODO: Add exclusion patterns
# TODO: Add custom cipher definition capability
# TODO: Add phrase structure filters (sentences, clauses, etc.)

# Results Enhancement
# TODO: Add sorting options (by value, length, position)
# TODO: Add result grouping by categories
# TODO: Add statistical analysis view
# TODO: Add cross-reference functionality between matches
# TODO: Add ability to annotate matches
# TODO: Add bookmarking system for important matches

# Visual Improvements
# TODO: Add color coding for different match types
# TODO: Add progress bar for long analyses
# TODO: Add results visualization (charts/graphs)
# TODO: Add dark/light theme support
# TODO: Add customizable highlighting colors
# TODO: Add mini-map for navigation in large texts

# Export and Import
# TODO: Add multiple export formats (CSV, JSON, PDF)
# TODO: Add export with highlighted context
# TODO: Add configuration save/load
# TODO: Add bulk import capability
# TODO: Add export templates
# TODO: Add automatic backup system

# Usability Features
# TODO: Add keyboard shortcuts
# TODO: Add right-click context menu
# TODO: Add drag-and-drop text import
# TODO: Add undo/redo functionality
# TODO: Add text formatting tools
# TODO: Add split view capability
# TODO: Add workspace sessions

# Integration Features
# TODO: Add API integration for external tools
# TODO: Add plugin system for custom analysis methods
# TODO: Add collaboration features
# TODO: Add cloud sync capability
# TODO: Add version control for texts and results

# Documentation and Help
# TODO: Add interactive tutorials
# TODO: Add tooltip help system
# TODO: Add example searches
# TODO: Add user manual
# TODO: Add FAQ section

# Performance Optimization
# TODO: Implement caching system for frequent searches
# TODO: Add batch processing for large texts
# TODO: Optimize memory usage for large datasets
# TODO: Add multi-threading support for complex analyses

# Accessibility
# TODO: Add screen reader support
# TODO: Add keyboard navigation
# TODO: Add font size controls
# TODO: Add high contrast mode
# TODO: Add voice input support

