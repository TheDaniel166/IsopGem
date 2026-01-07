"""Window for the Acrostic Discovery Tool."""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QCheckBox, QComboBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QListWidgetItem,
                             QDialog, QListWidget, QLineEdit, QStatusBar, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
import logging
from pathlib import Path
from shared.ui import theme
from pillars.gematria.services.acrostic_service import AcrosticService
from pillars.gematria.services.corpus_dictionary_service import CorpusDictionaryService
from pillars.gematria.ui.document_selector import DocumentSelectorDialog

class AcrosticsWindow(QMainWindow):
    """
    Acrostics Window class definition.
    
    Attributes:
        service: Description of service.
        dict_service: Description of dict_service.
    
    """
    def __init__(self, window_manager=None, parent=None):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """
          init   logic.
        
        Args:
            window_manager: Description of window_manager.
            parent: Description of parent.
        
        """
        super().__init__(parent=parent)
        self.setWindowTitle("Acrostic Discovery Tool")
        self.resize(800, 600)
        
        # Level 0: The Ghost Layer (Nano Banana substrate)
        possible_paths = [
            Path("src/assets/patterns/acrostic_bg_pattern.png"),
            Path("src/assets/patterns/tq_bg_pattern.png"),
            Path("assets/patterns/tq_bg_pattern.png"),
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
            logging.debug("Found Ghost Layer pattern at: %s", bg_path)
            abs_path = bg_path.absolute().as_posix()
            central.setStyleSheet(f"""
                QWidget#CentralContainer {{
                    border-image: url("{abs_path}") 0 0 0 0 stretch stretch;
                    border: none;
                    background-color: {theme.COLORS['light']};
                }}
            """)
        else:
            logging.warning("Ghost Layer pattern not found; using fallback color")
            central.setStyleSheet(f"QWidget#CentralContainer {{ background-color: {theme.COLORS['light']}; }}")
        
        self.service = AcrosticService()
        self.dict_service = CorpusDictionaryService()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(theme.get_status_muted_style())
        
        self.setup_ui()
        
    def setup_ui(self):
        """
        Setup ui logic.
        
        """
        # Container_layout on the central widget
        container_layout = QVBoxLayout(self.centralWidget())
        container_layout.setContentsMargins(16, 16, 16, 16)
        container_layout.setSpacing(16)  # Visual Liturgy: spacing-md
        
        # --- Top Control Panel ---
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)  # Visual Liturgy: spacing-sm
        
        # Mode Selection
        mode_label = QLabel("Scan Mode:")
        mode_label.setStyleSheet(f"font-weight: 600; color: {theme.COLORS['text_primary']};")
        controls_layout.addWidget(mode_label)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Line", "Word"])
        self.mode_combo.setMinimumHeight(40)
        self.mode_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {theme.COLORS['light']};
                border: 2px solid {theme.COLORS['ash']};
                border-radius: 8px;
                padding: 8px;
                color: {theme.COLORS['void']};
                min-height: 40px;
            }}
            QComboBox:focus {{
                border-color: {theme.COLORS['focus']};
            }}
        """)
        controls_layout.addWidget(self.mode_combo)
        
        controls_layout.addSpacing(16)
        
        # Checkboxes
        self.check_first = QCheckBox("🄰 First Letter")
        self.check_first.setChecked(True)
        self.check_first.setStyleSheet(f"color: {theme.COLORS['text_primary']}; font-weight: 600;")
        controls_layout.addWidget(self.check_first)
        
        self.check_last = QCheckBox("🄱 Last Letter")
        self.check_last.setChecked(True)
        self.check_last.setStyleSheet(f"color: {theme.COLORS['text_primary']}; font-weight: 600;")
        controls_layout.addWidget(self.check_last)
        
        controls_layout.addSpacing(16)
        
        # Advanced Options
        from PyQt6.QtWidgets import QSpinBox
        
        length_label = QLabel("Min Length:")
        length_label.setStyleSheet(f"font-weight: 600; color: {theme.COLORS['text_primary']};")
        controls_layout.addWidget(length_label)
        self.spin_min_length = QSpinBox()
        self.spin_min_length.setRange(3, 10)
        self.spin_min_length.setValue(3)
        self.spin_min_length.setMinimumHeight(40)
        self.spin_min_length.setToolTip("Minimum word length to discover")
        self.spin_min_length.setStyleSheet(f"""
            QSpinBox {{
                background-color: {theme.COLORS['light']};
                border: 2px solid {theme.COLORS['ash']};
                border-radius: 8px;
                padding: 8px;
                color: {theme.COLORS['void']};
            }}
            QSpinBox:focus {{
                border-color: {theme.COLORS['focus']};
            }}
        """)
        controls_layout.addWidget(self.spin_min_length)
        
        skip_label = QLabel("Skip:")
        skip_label.setStyleSheet(f"font-weight: 600; color: {theme.COLORS['text_primary']};")
        skip_label.setToolTip("Letter extraction pattern")
        controls_layout.addWidget(skip_label)
        self.spin_skip = QSpinBox()
        self.spin_skip.setRange(1, 5)
        self.spin_skip.setValue(1)
        self.spin_skip.setMinimumHeight(40)
        self.spin_skip.setToolTip("1=consecutive, 2=every other, 3=every third, etc.")
        self.spin_skip.setStyleSheet(f"""
            QSpinBox {{
                background-color: {theme.COLORS['light']};
                border: 2px solid {theme.COLORS['ash']};
                border-radius: 8px;
                padding: 8px;
                color: {theme.COLORS['void']};
            }}
            QSpinBox:focus {{
                border-color: {theme.COLORS['focus']};
            }}
        """)
        controls_layout.addWidget(self.spin_skip)
        
        self.check_longest = QCheckBox("📏 Longest Only")
        self.check_longest.setToolTip("Keep only longest non-overlapping matches")
        self.check_longest.setStyleSheet(f"color: {theme.COLORS['text_primary']}; font-weight: 600;")
        controls_layout.addWidget(self.check_longest)
        
        self.check_stopwords = QCheckBox("🚫 Filter Stopwords")
        self.check_stopwords.setToolTip("Exclude common words (the, and, for, etc.)")
        self.check_stopwords.setStyleSheet(f"color: {theme.COLORS['text_primary']}; font-weight: 600;")
        controls_layout.addWidget(self.check_stopwords)
        
        controls_layout.addSpacing(16)
        
        # Load Dictionary Button
        self.btn_load_dict = QPushButton("📖 Load Corpus")
        self.btn_load_dict.setMinimumHeight(40)
        theme.set_archetype(self.btn_load_dict, "scribe")
        self.btn_load_dict.clicked.connect(self.load_dictionary)
        controls_layout.addWidget(self.btn_load_dict)
        
        self.lbl_dict_status = QLabel("No corpus loaded")
        self.lbl_dict_status.setStyleSheet(f"font-style: italic; color: {theme.COLORS['mist']};")
        controls_layout.addWidget(self.lbl_dict_status)
        
        self.btn_view_dict = QPushButton("👁️")
        self.btn_view_dict.setToolTip("View loaded words")
        self.btn_view_dict.setFixedSize(40, 40)
        theme.set_archetype(self.btn_view_dict, "ghost")
        self.btn_view_dict.clicked.connect(self.view_dictionary)
        controls_layout.addWidget(self.btn_view_dict)
        
        controls_layout.addStretch()
        container_layout.addLayout(controls_layout)
        
        # --- Input Area ---
        input_label = QLabel("📜 The Text to Scrutinize")
        input_label.setStyleSheet(theme.get_subtitle_style())
        container_layout.addWidget(input_label)
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Inscribe the text to scan for hidden vertical patterns...")
        self.input_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme.COLORS['light']};
                border: 2px solid {theme.COLORS['ash']};
                border-radius: 8px;
                padding: 12px;
                color: {theme.COLORS['void']};
                font-size: 11pt;
            }}
            QTextEdit:focus {{
                border-color: {theme.COLORS['focus']};
            }}
        """)
        container_layout.addWidget(self.input_text)
        
        # Action Button
        action_layout = QHBoxLayout()
        action_layout.setSpacing(8)
        
        self.btn_load_doc = QPushButton("📂 Load Document")
        self.btn_load_doc.setMinimumHeight(40)
        self.btn_load_doc.setToolTip("Import text from a document in the archives")
        theme.set_archetype(self.btn_load_doc, "navigator")
        self.btn_load_doc.clicked.connect(self.load_document_dialog)
        action_layout.addWidget(self.btn_load_doc)
        
        self.btn_search = QPushButton("✨ Discover Acrostics")
        self.btn_search.setMinimumHeight(40)
        theme.set_archetype(self.btn_search, "seeker")
        self.btn_search.clicked.connect(self.run_search)
        action_layout.addWidget(self.btn_search)
        
        container_layout.addLayout(action_layout)
        
        # --- Results Area ---
        results_label = QLabel("🔍 Revealed Patterns")
        results_label.setStyleSheet(theme.get_subtitle_style())
        container_layout.addWidget(results_label)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "Method", "Found Word", "Word Value", "Valid?", 
            "Source Text", "Source Total", "Indices"
        ])
        self.results_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {theme.COLORS['surface']};
                border: 1px solid {theme.COLORS['border']};
                border-radius: 8px;
                gridline-color: {theme.COLORS['border']};
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
            QTableWidget::item:selected {{
                background-color: {theme.COLORS['seeker_soft']};
                color: {theme.COLORS['void']};
            }}
            QHeaderView::section {{
                background-color: {theme.COLORS['marble']};
                color: {theme.COLORS['void']};
                font-weight: 700;
                border: 1px solid {theme.COLORS['border']};
                padding: 8px;
            }}
        """)
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        # Connect double click
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.cellDoubleClicked.connect(self.on_result_double_clicked)

        container_layout.addWidget(self.results_table)
        container_layout.addWidget(self.status_bar)
        
        # Initial status
        self.status_bar.showMessage("Ready to discover hidden acrostics...")

    def on_result_double_clicked(self, row, col):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """Opens the highlight dialog for the selected result."""
        if row < 0:
            return
            
        if hasattr(self, 'current_results') and row < len(self.current_results):
            res = self.current_results[row]
            dialog = AcrosticHighlightDialog(res.source_text_units, res.method, self)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            dialog.exec()

    def load_dictionary(self):
        """Loads the dictionary from the 'Holy' corpus."""
        from PyQt6.QtGui import QCursor
        from PyQt6.QtCore import Qt as QtCore
        from PyQt6.QtWidgets import QApplication
        
        self.setCursor(QCursor(QtCore.CursorShape.WaitCursor))
        self.status_bar.showMessage("Loading corpus dictionary from Holy texts...")
        QApplication.processEvents()
        
        try:
            count = self.dict_service.load_dictionary("Holy")
            self.lbl_dict_status.setText(f"{count} words")
            self.lbl_dict_status.setStyleSheet(f"font-weight: 700; color: {theme.COLORS['seeker']};")
            self.status_bar.showMessage(f"✨ Corpus loaded: {count} sacred words")
            QMessageBox.information(self, "The Lexicon Awakens", f"Loaded {count} words from Holy documents.")
        except Exception as e:
            QMessageBox.critical(self, "The Archive Resists", f"Failed to load dictionary:\n{str(e)}")
            self.status_bar.showMessage("Corpus loading failed.")
        finally:
            self.setCursor(QCursor(QtCore.CursorShape.ArrowCursor))

    def view_dictionary(self):
        """
        View dictionary logic.
        
        """
        if self.dict_service.word_count == 0:
            QMessageBox.warning(self, "The Lexicon Sleeps", "No corpus loaded. Load the dictionary first.")
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
        from pillars.gematria.services.document_service import DocumentService
        
        try:
            service = DocumentService()
            content = service.get_document_content(doc_id)
            if content:
                self.input_text.setText(content)
                self.status_bar.showMessage("✨ Document text loaded successfully")
                QMessageBox.information(self, "The Scroll Unfurls", "Text loaded from the archives.")
            else:
                QMessageBox.warning(self, "The Scroll is Empty", "This document contains no text.")
        except Exception as e:
            QMessageBox.critical(self, "The Archives Resist", f"Failed to retrieve document:\n{str(e)}")

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
        from PyQt6.QtGui import QCursor, QColor
        from PyQt6.QtCore import Qt as QtCore
        from PyQt6.QtWidgets import QApplication
        
        text = self.input_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "The Scroll is Blank", "Please provide text to scan for acrostics.")
            return

        mode = self.mode_combo.currentText()
        first = self.check_first.isChecked()
        last = self.check_last.isChecked()
        min_length = self.spin_min_length.value()
        skip_pattern = self.spin_skip.value()
        longest_only = self.check_longest.isChecked()
        filter_stopwords = self.check_stopwords.isChecked()
        
        if not first and not last:
            QMessageBox.warning(self, "No Method Selected", "Please select at least one letter position (First or Last).")
            return
        
        self.setCursor(QCursor(QtCore.CursorShape.WaitCursor))
        filters = []
        if longest_only: filters.append("longest-only")
        if filter_stopwords: filters.append("no-stopwords")
        if skip_pattern > 1: filters.append(f"skip-{skip_pattern}")
        filter_str = f" [{', '.join(filters)}]" if filters else ""
        self.status_bar.showMessage(f"Scanning for acrostics in {mode} mode{filter_str}...")
        QApplication.processEvents()
        
        try:
            results = self.service.find_acrostics(
                text, first, last, mode,
                min_length=min_length,
                longest_only=longest_only,
                filter_stopwords=filter_stopwords,
                skip_pattern=skip_pattern
            )
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
                    valid_item.setForeground(QColor(theme.COLORS['scribe']))
                    valid_item.setBackground(QColor(theme.COLORS['scribe_soft']))
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
            
            self.status_bar.showMessage(f"✨ {len(results)} acrostic pattern(s) discovered!")
            
        except Exception as e:
            QMessageBox.critical(self, "The Weave Unravels", f"Error during scan:\n{str(e)}")
            self.status_bar.showMessage("Scan failed.")
        finally:
            self.setCursor(QCursor(QtCore.CursorShape.ArrowCursor))



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
        self.setWindowTitle(f"📖 Corpus Lexicon ({len(words)} words)")
        self.resize(400, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Search
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("🔍 Search words...")
        self.filter_edit.setMinimumHeight(40)
        self.filter_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {theme.COLORS['light']};
                border: 2px solid {theme.COLORS['ash']};
                border-radius: 8px;
                padding: 8px;
                color: {theme.COLORS['void']};
            }}
            QLineEdit:focus {{
                border-color: {theme.COLORS['focus']};
            }}
        """)
        self.filter_edit.textChanged.connect(self.filter_list)
        layout.addWidget(self.filter_edit)
        
        # List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: {theme.COLORS['surface']};
                border: 1px solid {theme.COLORS['border']};
                border-radius: 8px;
                padding: 8px;
            }}
            QListWidget::item {{
                padding: 4px;
            }}
        """)
        layout.addWidget(self.list_widget)
        
        # Close button
        btn_close = QPushButton("Close")
        btn_close.setMinimumHeight(40)
        theme.set_archetype(btn_close, "ghost")
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
        self.setWindowTitle("✨ Acrostic Visualization")
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Explanation
        method_label = QLabel(f"<b>Method:</b> {method}")
        method_label.setStyleSheet(theme.get_subtitle_style())
        layout.addWidget(method_label)
        
        # Text Display
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                font-family: 'Courier New', monospace;
                font-size: 12pt;
                background-color: {theme.COLORS['void']};
                color: {theme.COLORS['light']};
                border: 1px solid {theme.COLORS['border']};
                border-radius: 8px;
                padding: 16px;
                line-height: 1.6;
            }}
        """)
        
        layout.addWidget(self.text_edit)
        
        # Render HTML
        html = self.generate_html(source_units, method)
        self.text_edit.setHtml(html)
        
        # Close button
        btn_close = QPushButton("Close")
        btn_close.setMinimumHeight(40)
        theme.set_archetype(btn_close, "ghost")
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
                            f"<b style='color:{theme.COLORS['destroyer']}; font-size:14pt'>{char}</b>" + 
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
                        f"<b style='color:{theme.COLORS['destroyer']}; font-size:14pt'>{unit[found_idx]}</b>" + 
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
