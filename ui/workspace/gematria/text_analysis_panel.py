from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QTextEdit, QComboBox, QLabel, QPushButton,
                              QSpinBox, QFileDialog, QCheckBox, QSplitter,
                              QLineEdit, QGroupBox)
from PySide6.QtCore import (Qt, QPropertyAnimation, QParallelAnimationGroup, 
                           Property, QPoint, QPointF, QSequentialAnimationGroup,
                           QEasingCurve)
from PySide6.QtGui import (QTextCharFormat, QColor, QTextCursor, QPalette, 
                          QBrush, QLinearGradient, QRadialGradient,
                          QSyntaxHighlighter, QPainter)
from core.gematria.calculator import GematriaCalculator
import random
import re
from PySide6.QtCore import Signal

class ToggleSwitch(QWidget):
    clicked = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 30)
        self._is_checked = False
        
        self.animation = QPropertyAnimation(self, b"position")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self._position = 0
        
    @Property(int)  
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
        self._alpha = 0
        self.matches = []
        self.smart_matches = []
        self.hover_index = -1
        
        self.fade_animation = QPropertyAnimation(self, b'alpha')
        self.fade_animation.setDuration(400)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.gradients = {
            'raw': self.create_gradient(QColor(255, 255, 0)),
            'smart': self.create_gradient(QColor(0, 255, 0)),
            'hover': self.create_gradient(QColor(255, 165, 0))
        }

    def create_gradient(self, base_color):
        gradient = QLinearGradient(QPoint(0, 0), QPoint(0, 30))
        gradient.setColorAt(0, QColor(base_color.red(),
                                    base_color.green(),
                                    base_color.blue(),
                                    self._alpha))
        gradient.setColorAt(1, QColor(base_color.red(),
                                    base_color.green(),
                                    base_color.blue(),
                                    int(self._alpha * 0.7)))
        return gradient
    @Property(int)
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self._alpha = value
        self.update_gradients()
        self.rehighlight()
        
    def highlightBlock(self, text):
        block_position = self.currentBlock().position()
        
        for match in self.matches:
            start = match['start_index'] - block_position
            length = match['end_index'] - match['start_index']
            if start >= 0 and start + length <= len(text):
                fmt = QTextCharFormat()
                fmt.setBackground(QBrush(self.gradients['raw']))
                self.setFormat(start, length, fmt)
        
        for match in self.smart_matches:
            start = match['start_index'] - block_position
            length = match['end_index'] - match['start_index']
            if start >= 0 and start + length <= len(text):
                fmt = QTextCharFormat()
                fmt.setBackground(QBrush(self.gradients['smart']))
                self.setFormat(start, length, fmt)
                
class TextAnalysisPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.calculator = GematriaCalculator()
        self.current_results = []
        self.current_text = ""
        self.init_ui()
        self.connect_signals()
        self.highlighter = AnimatedHighlighter(self.source_text.document())

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Text Input Section
        input_group = QGroupBox("Text Input")
        input_layout = QVBoxLayout()
        
        # Control buttons
        control_layout = QHBoxLayout()
        self.import_button = QPushButton("Import Text File")
        self.clear_button = QPushButton("Clear Text")
        self.search_button = QPushButton("Search")
        self.export_button = QPushButton("Export Results")
        
        control_layout.addWidget(self.import_button)
        control_layout.addWidget(self.clear_button)
        control_layout.addWidget(self.search_button)
        control_layout.addWidget(self.export_button)
        
        # Value and Cipher Selection
        value_layout = QHBoxLayout()
        self.value_input = QSpinBox()
        self.value_input.setRange(1, 99999)
        self.cipher_select = QComboBox()
        self.cipher_select.addItems(['TQ English', 'Hebrew Standard', 'Hebrew Gadol', 'Greek'])
        
        value_layout.addWidget(QLabel("Target Value:"))
        value_layout.addWidget(self.value_input)
        value_layout.addWidget(self.cipher_select)
        
        # Filter Controls
        filter_layout = QHBoxLayout()
        self.any_length = QCheckBox("Any Length")
        self.phrase_length = QSpinBox()
        self.phrase_length.setRange(1, 100)
        self.pattern_input = QLineEdit()
        self.regex_checkbox = QCheckBox("Use Regex")
        self.category_select = QComboBox()
        self.category_select.addItems(['All', 'Names', 'Places', 'Phrases', 'Custom'])
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Enter a filter")
        
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(self.any_length)
        filter_layout.addWidget(self.phrase_length)
        filter_layout.addWidget(self.pattern_input)
        filter_layout.addWidget(self.regex_checkbox)
        filter_layout.addWidget(self.category_select)
        
        # Text areas
        self.source_text = QTextEdit()
        self.results_text = QTextEdit()
        self.stats_label = QLabel("Found: 0 matches")
        
        # Result type toggle
        result_type_layout = QHBoxLayout()
        self.result_toggle = ToggleSwitch()
        result_type_layout.addWidget(QLabel("Raw Results"))
        result_type_layout.addWidget(self.result_toggle)
        result_type_layout.addWidget(QLabel("Valid Phrases"))
        
        # Add all layouts to main layout
        input_layout.addLayout(control_layout)
        input_layout.addLayout(value_layout)
        input_layout.addLayout(filter_layout)
        input_layout.addWidget(self.source_text)
        input_layout.addWidget(self.results_text)
        input_layout.addWidget(self.stats_label)
        input_layout.addLayout(result_type_layout)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        self.setLayout(layout)

    def connect_signals(self):
        self.import_button.clicked.connect(self.import_text)
        self.clear_button.clicked.connect(self.clear_text)
        self.search_button.clicked.connect(self.perform_search)
        self.export_button.clicked.connect(self.export_results)
        self.filter_input.textChanged.connect(self.filter_results)
        self.result_toggle.clicked.connect(self.update_results_display)
        
        # New connections
        self.value_input.valueChanged.connect(self.perform_search)
        self.cipher_select.currentIndexChanged.connect(self.perform_search)
        self.any_length.stateChanged.connect(lambda state: self.phrase_length.setEnabled(not state))
        self.phrase_length.valueChanged.connect(self.filter_results)
        self.pattern_input.textChanged.connect(self.filter_results)
        self.regex_checkbox.stateChanged.connect(self.filter_results)
        self.category_select.currentIndexChanged.connect(self.filter_results)

    def import_text(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Text File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.source_text.setPlainText(file.read())

    def find_raw_combinations(self, text, target_value, cipher):
        words = text.split()
        combinations = []
        
        for i in range(len(words)):
            current_sum = 0
            current_words = []
            start_position = text.find(words[i])
            
            for j in range(i, len(words)):
                word = words[j]
                value = self.calculator.calculate(word, cipher)
                current_sum += value
                current_words.append(word)
                
                if current_sum == target_value:
                    phrase = ' '.join(current_words)
                    end_position = text.find(words[j], start_position) + len(words[j])
                    combinations.append({
                        'phrase': phrase,
                        'start_index': start_position,
                        'end_index': end_position
                    })
                elif current_sum > target_value:
                    break
        
        return combinations

    def find_smart_combinations(self, raw_combinations):
        smart_results = []
        for combo in raw_combinations:
            words = combo['phrase'].split()
            if self.is_valid_phrase(words):
                smart_results.append(combo)
        return smart_results

    def is_valid_phrase(self, words):
        if len(words) <= 3:
            return True
            
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
        
        basic_structure = (has_article or has_preposition or has_conjunction or
                          has_pronoun or has_auxiliary)
        advanced_structure = (starts_capitalized or ends_with_punctuation or
                             has_valid_ending or has_verb_pattern)
        
        return basic_structure or advanced_structure

    def analyze_text(self, text):
        if not text:
            return
            
        target_value = self.value_input.value()
        cipher = self.cipher_select.currentText()
        
        raw_combinations = self.find_raw_combinations(text, target_value, cipher)
        smart_combinations = []
        
        is_smart_mode = self.result_toggle.is_checked()
        
        if is_smart_mode:
            smart_combinations = self.find_smart_combinations(raw_combinations)
            filtered_results = self.apply_filters(smart_combinations)
        else:
            filtered_results = self.apply_filters(raw_combinations)
        
        self.current_results = filtered_results
        total_matches = len(filtered_results)
        self.stats_label.setText(f"Found: {total_matches} matches")
        
        self.display_results(filtered_results if not is_smart_mode else [],
                           filtered_results if is_smart_mode else [])
        self.highlight_matches(filtered_results if not is_smart_mode else [],
                             filtered_results if is_smart_mode else [])

    def apply_filters(self, results):
        filtered = results.copy()
        
        if not self.any_length.isChecked():
            target_length = self.phrase_length.value()
            filtered = [r for r in filtered if len(r['phrase'].split()) == target_length]
        
        pattern = self.pattern_input.text()
        if pattern:
            if self.regex_checkbox.isChecked():
                regex = re.compile(pattern, re.IGNORECASE)
                filtered = [r for r in filtered if regex.search(r['phrase'])]
            else:
                pattern = pattern.lower()
                filtered = [r for r in filtered if pattern in r['phrase'].lower()]
        
        category = self.category_select.currentText()
        if category != 'All':
            filtered = [r for r in filtered if self.check_category(r['phrase'], category)]
        
        return filtered

    def display_results(self, raw_results, smart_results):
        self.results_text.clear()
        if raw_results:
            self.results_text.append("Raw Combinations:")
            for result in raw_results:
                self.results_text.append(f"• {result['phrase']}")
            self.results_text.append("")
        
        if smart_results:
            self.results_text.append("Valid Phrases:")
            for result in smart_results:
                self.results_text.append(f"• {result['phrase']}")

    def highlight_matches(self, raw_matches, smart_matches):
        self.highlighter.set_matches(raw_matches, smart_matches)


    def clear_text(self):
        self.source_text.clear()
        self.results_text.clear()
        self.current_text = ""
        self.stats_label.setText("Found: 0 matches")
        self.highlighter.set_matches([], [])

    def perform_search(self):
        text = self.source_text.toPlainText()
        if not text:
            return
        self.current_text = text
        self.analyze_text(text)

    def export_results(self):
        if not self.results_text.toPlainText():
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Results", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.results_text.toPlainText())

    def filter_results(self):
        if self.current_text:
            self.analyze_text(self.current_text)

    def update_results_display(self):
        if self.current_text:
            is_smart_mode = self.result_toggle.is_checked()
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

