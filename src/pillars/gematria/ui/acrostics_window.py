"""Window for the Acrostic Discovery Tool."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QCheckBox, QComboBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QListWidgetItem,
                             QDialog, QListWidget, QLineEdit)
from PyQt6.QtCore import Qt
from pillars.gematria.services.acrostic_service import AcrosticService
from pillars.gematria.services.corpus_dictionary_service import CorpusDictionaryService
from pillars.gematria.ui.document_selector import DocumentSelectorDialog

class AcrosticsWindow(QWidget):
    """
    Acrostics Window class definition.
    
    Attributes:
        service: Description of service.
        dict_service: Description of dict_service.
    
    """
    def __init__(self, window_manager=None, parent=None):
        """
          init   logic.
        
        Args:
            window_manager: Description of window_manager.
            parent: Description of parent.
        
        """
        super().__init__(parent=parent)
        self.setWindowTitle("Acrostic Discovery Tool")
        self.resize(800, 600)
        
        self.service = AcrosticService()
        self.dict_service = CorpusDictionaryService()
        
        self.setup_ui()
        
    def setup_ui(self):
        """
        Setup ui logic.
        
        """
        layout = QVBoxLayout(self)
        
        # --- Top Control Panel ---
        controls_layout = QHBoxLayout()
        
        # Mode Selection
        controls_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Line", "Word"])
        controls_layout.addWidget(self.mode_combo)
        
        # Checkboxes
        self.check_first = QCheckBox("First Letter")
        self.check_first.setChecked(True)
        controls_layout.addWidget(self.check_first)
        
        self.check_last = QCheckBox("Last Letter")
        self.check_last.setChecked(True)
        controls_layout.addWidget(self.check_last)
        
        # Load Dictionary Button
        self.btn_load_dict = QPushButton("Load Corpus Dictionary")
        self.btn_load_dict.clicked.connect(self.load_dictionary)
        controls_layout.addWidget(self.btn_load_dict)
        
        self.lbl_dict_status = QLabel("Dictionary: Not Loaded")
        controls_layout.addWidget(self.lbl_dict_status)
        
        self.btn_view_dict = QPushButton("👁️")
        self.btn_view_dict.setToolTip("View loaded words")
        self.btn_view_dict.setFixedWidth(30)
        self.btn_view_dict.clicked.connect(self.view_dictionary)
        controls_layout.addWidget(self.btn_view_dict)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # --- Input Area ---
        layout.addWidget(QLabel("Input Text:"))
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Paste text here...")
        layout.addWidget(self.input_text)
        
        # Action Button
        action_layout = QHBoxLayout()
        
        self.btn_load_doc = QPushButton("📂 Load Document")
        self.btn_load_doc.setToolTip("Import text from a document in the database")
        self.btn_load_doc.clicked.connect(self.load_document_dialog)
        action_layout.addWidget(self.btn_load_doc)
        
        self.btn_search = QPushButton("Discover Acrostics")
        self.btn_search.clicked.connect(self.run_search)
        action_layout.addWidget(self.btn_search)
        
        layout.addLayout(action_layout)
        
        # --- Results Area ---
        # --- Results Area ---
        layout.addWidget(QLabel("Results:"))
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "Method", "Found Word", "Word Value", "Valid?", 
            "Source Text", "Source Total", "Indices"
        ])
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        # Connect double click
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.cellDoubleClicked.connect(self.on_result_double_clicked)

        layout.addWidget(self.results_table)

    def on_result_double_clicked(self, row, col):
        """Opens the highlight dialog for the selected result."""
        if row < 0:
            return
            
        if hasattr(self, 'current_results') and row < len(self.current_results):
            res = self.current_results[row]
            dialog = AcrosticHighlightDialog(res.source_text_units, res.method, self)
            dialog.exec()

    def load_dictionary(self):
        """Loads the dictionary from the 'Holy' corpus."""
        try:
            count = self.dict_service.load_dictionary("Holy")
            self.lbl_dict_status.setText(f"Dictionary: {count} words loaded")
            QMessageBox.information(self, "Dictionary Loaded", f"Loaded {count} words from 'Holy' documents.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load dictionary: {str(e)}")

    def view_dictionary(self):
        """
        View dictionary logic.
        
        """
        if self.dict_service.word_count == 0:
            QMessageBox.warning(self, "Empty", "Dictionary is empty. Load it first.")
            return
        
        words = self.dict_service.get_words()
        dialog = DictionaryViewerDialog(words, self)
        dialog.exec()

    def load_document_dialog(self):
        """
        Load document dialog logic.
        
        """
        dialog = DocumentSelectorDialog(self)
        if dialog.exec():
            doc_id = dialog.get_selected_doc_id()
            if doc_id:
                self.load_document_text(doc_id)

    def load_document_text(self, doc_id):
        """
        Load document text logic.
        
        Args:
            doc_id: Description of doc_id.
        
        """
        from shared.repositories.document_manager.document_repository import DocumentRepository
        from shared.database import get_db
        
        try:
            db = next(get_db())
            repo = DocumentRepository(db)
            doc = repo.get(doc_id)
            if doc and doc.content:
                self.input_text.setText(doc.content)
                QMessageBox.information(self, "Loaded", f"Loaded text from '{doc.title}'")
            else:
                QMessageBox.warning(self, "Warning", "Document has no content.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load document: {str(e)}")

    def calculate_gematria(self, text: str) -> int:
        """Simple TQ Cipher (A=1, B=2...) calculation."""
        # This could use TQGematriaCalculator, but for a simple total strict A=1 is safer here.
        # Or we can reuse TQGematriaCalculator().calculate(text) if available.
        # Let's do a simple inline calculation for now to avoid complexity, TQ is A=1..Z=26
        total = 0
        for char in text.upper():
            if 'A' <= char <= 'Z':
                total += ord(char) - ord('A') + 1
        return total

    def run_search(self):
        """
        Execute search logic.
        
        """
        text = self.input_text.toPlainText()
        if not text:
            return

        mode = self.mode_combo.currentText()
        first = self.check_first.isChecked()
        last = self.check_last.isChecked()
        
        results = self.service.find_acrostics(text, first, last, mode)
        self.current_results = results # Store for interaction
        
        self.results_table.setRowCount(0)
        for row, res in enumerate(results):
            self.results_table.insertRow(row)
            
            # 0: Method
            self.results_table.setItem(row, 0, QTableWidgetItem(res.method))
            
            # 1: Found Word
            self.results_table.setItem(row, 1, QTableWidgetItem(res.found_word))
            
            # 2: Word Value
            word_val = self.calculate_gematria(res.found_word)
            self.results_table.setItem(row, 2, QTableWidgetItem(str(word_val)))
            
            # 3: Valid?
            valid_item = QTableWidgetItem("YES" if res.is_valid_word else "NO")
            if res.is_valid_word:
                valid_item.setBackground(Qt.GlobalColor.green)
            self.results_table.setItem(row, 3, valid_item)
            
            # 4: Source Text
            source_str = " ".join(res.source_text_units)
            self.results_table.setItem(row, 4, QTableWidgetItem(source_str))
            
            # 5: Source Total
            source_val = self.calculate_gematria(source_str)
            self.results_table.setItem(row, 5, QTableWidgetItem(str(source_val)))
            
            # 6: Indices
            indices_str = f"{min(res.source_indices)}-{max(res.source_indices)}" if res.source_indices else ""
            self.results_table.setItem(row, 6, QTableWidgetItem(indices_str))



class DictionaryViewerDialog(QDialog):
    """Dialog to view all words in the loaded dictionary."""
    def __init__(self, words: list[str], parent=None):
        """
          init   logic.
        
        Args:
            words: Description of words.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle(f"Corpus Dictionary ({len(words)} words)")
        self.resize(400, 600)
        
        layout = QVBoxLayout(self)
        
        # Search
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Search words...")
        self.filter_edit.textChanged.connect(self.filter_list)
        layout.addWidget(self.filter_edit)
        
        # List
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        # Close button
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        
        self.all_words = words
        self.update_list(self.all_words)
        
    def update_list(self, words):
        """
        Update list logic.
        
        Args:
            words: Description of words.
        
        """
        self.list_widget.clear()
        # Limit display for performance if huge? 
        # But 7000 words is fine for QListWidget.
        for w in words[:2000]: # Cap visual at 2000 to prevent lag if dictionary is massive
            self.list_widget.addItem(w)
        
        if len(words) > 2000:
            self.list_widget.addItem(f"... and {len(words)-2000} more (filter to see)")
            
    def filter_list(self, text):
        """
        Filter list logic.
        
        Args:
            text: Description of text.
        
        """
        text = text.upper()
        if not text:
            self.update_list(self.all_words)
            return
            
        filtered = [w for w in self.all_words if text in w]
        self.update_list(filtered)

class AcrosticHighlightDialog(QDialog):
    """
    Dialog to display the source text with the acrostic letters highlighted.
    """
    def __init__(self, source_units: list[str], method: str, parent=None):
        """
          init   logic.
        
        Args:
            source_units: Description of source_units.
            method: Description of method.
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.setWindowTitle("Acrostic Visualization")
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Explanation
        layout.addWidget(QLabel(f"<b>Method:</b> {method}"))
        
        # Text Display
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        # Apply a nice font size
        font = self.text_edit.font()
        font.setPointSize(12)
        self.text_edit.setFont(font)
        
        layout.addWidget(self.text_edit)
        
        # Render HTML
        html = self.generate_html(source_units, method)
        self.text_edit.setHtml(html)
        
        # Close button
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        
    def generate_html(self, units: list[str], method: str) -> str:
        """Generates HTML with red bolded letters for the acrostic."""
        html_lines = []
        
        # Determine which index to highlight based on method string
        # method is like "First Letter (Line)" or "Last Letter (Word)"
        is_first = "First Letter" in method
        is_last = "Last Letter" in method
        
        for unit in units:
            if not unit: 
                continue
                
            # We need to find the actual letter to highlight.
            # The acrostic logic strips non-alpha, but here we have the full unit (with punctuation).
            # We must be careful. If the user provided "Hello!", the logic used 'H'.
            # If "World!", the logic used 'W'.
            # If Last Letter of "Hello!", logic used 'o' (from Hello).
            
            # Let's try to robustly identify the char index.
            # We can walk from left or right to find the first alpha char.
            
            if is_first:
                # Highlight first alpha char
                for i, char in enumerate(unit):
                    if char.isalpha():
                        # Found it
                        formatted = (
                            unit[:i] + 
                            f"<b style='color:red; font-size:14pt'>{char}</b>" + 
                            unit[i+1:]
                        )
                        html_lines.append(formatted)
                        break
                else:
                    # No alpha found? Just append as is.
                    html_lines.append(unit)
                    
            elif is_last:
                # Highlight last alpha char
                # Walk backwards
                found_idx = -1
                for i in range(len(unit) - 1, -1, -1):
                    if unit[i].isalpha():
                        found_idx = i
                        break
                
                if found_idx != -1:
                    formatted = (
                        unit[:found_idx] + 
                        f"<b style='color:red; font-size:14pt'>{unit[found_idx]}</b>" + 
                        unit[found_idx+1:]
                    )
                    html_lines.append(formatted)
                else:
                    html_lines.append(unit)
            else:
                # Fallback if method is unknown
                html_lines.append(unit)
                
        # Join with breaks. If simple words, spaces might be better?
        # If "Line" mode, <br>. If "Word" mode, space?
        # Let's assume <br> for vertical clarity as requested by "Acrostic" nature usually.
        # But for "Word" mode, maybe they want to see the sentence flow?
        # "Acrostic" implies vertical reading. Let's stick to <br> to align the letters vertically.
        return "<br>".join(html_lines)
