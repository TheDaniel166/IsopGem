"""
Search and Replace features for RichTextEditor.
Encapsulates logic for finding text and managing the search UI.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QCheckBox, QMessageBox,
    QWidget, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextDocument, QTextCursor

class SearchDialog(QDialog):
    """
    Non-modal dialog for Find and Replace operations.
    Stays on top of the editor.
    """
    find_next_requested = pyqtSignal(str, bool, bool) # text, case_sensitive, whole_words
    find_all_requested = pyqtSignal(str, bool, bool) # text, case_sensitive, whole_words
    replace_requested = pyqtSignal(str, str, bool, bool) # text, replace_text, case, whole
    replace_all_requested = pyqtSignal(str, str, bool, bool) # text, replace_text, case, whole
    navigate_requested = pyqtSignal(int) # position

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find & Replace")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint) 
        # Make it non-modal so user can interact with editor
        self.setModal(False)
        self.resize(400, 300) # Slightly larger for list
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # input rows
        input_layout = QVBoxLayout()
        
        # Find
        find_row = QHBoxLayout()
        find_row.addWidget(QLabel("Find what:"))
        self.find_input = QLineEdit()
        self.find_input.textChanged.connect(self._reset_status)
        find_row.addWidget(self.find_input)
        input_layout.addLayout(find_row)
        
        # Replace
        replace_row = QHBoxLayout()
        replace_row.addWidget(QLabel("Replace with:"))
        self.replace_input = QLineEdit()
        replace_row.addWidget(self.replace_input)
        input_layout.addLayout(replace_row)
        
        layout.addLayout(input_layout)
        
        # Options
        opts_row = QHBoxLayout()
        self.case_check = QCheckBox("Match case")
        self.words_check = QCheckBox("Whole words")
        opts_row.addWidget(self.case_check)
        opts_row.addWidget(self.words_check)
        opts_row.addStretch()
        layout.addLayout(opts_row)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_find = QPushButton("Find Next")
        self.btn_find.setDefault(True)
        self.btn_find.clicked.connect(self._on_find_next)
        
        self.btn_find_all = QPushButton("Find All")
        self.btn_find_all.clicked.connect(self._on_find_all)
        
        self.btn_replace = QPushButton("Replace")
        self.btn_replace.clicked.connect(self._on_replace)
        
        self.btn_replace_all = QPushButton("Replace All")
        self.btn_replace_all.clicked.connect(self._on_replace_all)
        
        btn_layout.addWidget(self.btn_find)
        btn_layout.addWidget(self.btn_find_all)
        btn_layout.addWidget(self.btn_replace)
        btn_layout.addWidget(self.btn_replace_all)
        
        layout.addLayout(btn_layout)
        
        # Results List
        self.lbl_results = QLabel("Results:")
        self.lbl_results.setVisible(False)
        layout.addWidget(self.lbl_results)
        
        self.results_list = QListWidget()
        self.results_list.setVisible(False)
        self.results_list.itemClicked.connect(self._on_result_clicked)
        # Style for snippets
        self.results_list.setStyleSheet("font-family: monospace;")
        layout.addWidget(self.results_list)
        
        # Close button at very bottom? Or in btn layout?
        # Let's add a close button separately or keep it window based
        # Usually X is enough, but "Close" is nice.
        close_row = QHBoxLayout()
        close_row.addStretch()
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        close_row.addWidget(self.btn_close)
        layout.addLayout(close_row)

    def _on_find_next(self):
        text = self.find_input.text()
        if not text:
            return
        self.find_next_requested.emit(
            text, 
            self.case_check.isChecked(), 
            self.words_check.isChecked()
        )

    def _on_find_all(self):
        text = self.find_input.text()
        if not text:
            return
        self.find_all_requested.emit(
            text, 
            self.case_check.isChecked(), 
            self.words_check.isChecked()
        )

    def _on_replace(self):
        text = self.find_input.text()
        if not text:
            return
        self.replace_requested.emit(
            text,
            self.replace_input.text(),
            self.case_check.isChecked(),
            self.words_check.isChecked()
        )

    def _on_replace_all(self):
        text = self.find_input.text()
        if not text:
            return
        self.replace_all_requested.emit(
            text,
            self.replace_input.text(),
            self.case_check.isChecked(),
            self.words_check.isChecked()
        )
        
    def _on_result_clicked(self, item: QListWidgetItem):
        pos = item.data(Qt.ItemDataRole.UserRole)
        if pos is not None:
            self.navigate_requested.emit(pos)
        
    def _reset_status(self):
        # Clear any error styling
        self.find_input.setStyleSheet("")

    def set_not_found_state(self):
        # Visually indicate text not found (e.g. red border)
        self.find_input.setStyleSheet("border: 1px solid red;")

    def show_results(self, results: list[tuple[int, str]]):
        """
        Display list of results.
        results: list of (position, snippet)
        """
        self.results_list.clear()
        if not results:
            self.lbl_results.setText("No results found.")
            self.lbl_results.setVisible(True)
            self.results_list.setVisible(False)
            return

        self.lbl_results.setText(f"Found {len(results)} matches:")
        self.lbl_results.setVisible(True)
        self.results_list.setVisible(True)
        
        for pos, snippet in results:
            # Replace newlines in snippet to keep one line per item
            display_text = snippet.replace("\n", " ").replace("\r", " ")
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, pos)
            self.results_list.addItem(item)

class SearchReplaceFeature:
    """
    Logic for Search & Replace operations.
    Manages the SearchDialog and interacts with the editor cursor.
    """
    def __init__(self, editor, parent_widget=None):
        self.editor = editor # QTextEdit
        self.parent = parent_widget # Usually the RichTextEditor instance
        self._dialog = None

    def show_search_dialog(self):
        """Open (and create if needed) the search dialog."""
        if self._dialog is None:
            self._dialog = SearchDialog(self.parent)
            self._dialog.find_next_requested.connect(self.find_next)
            self._dialog.find_all_requested.connect(self.find_all)
            self._dialog.replace_requested.connect(self.replace_current)
            self._dialog.replace_all_requested.connect(self.replace_all)
            self._dialog.navigate_requested.connect(self.navigate_to)
        
        self._dialog.show()
        self._dialog.raise_()
        self._dialog.activateWindow()
        
        # If text is selected in editor, pre-fill find box
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            # Safety check for massive selections
            if len(selected) < 100:
                self._dialog.find_input.setText(selected)
                self._dialog.find_input.selectAll()
        
        self._dialog.find_input.setFocus()

    def find_next(self, text: str, case_sensitive: bool, whole_words: bool) -> bool:
        """Find next occurrence of text."""
        flags = QTextDocument.FindFlag(0)
        if case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if whole_words:
            flags |= QTextDocument.FindFlag.FindWholeWords
            
        found = self.editor.find(text, flags)
        
        if not found:
            # Wrap around search?
            # Save current cursor
            original_cursor = self.editor.textCursor()
            # Move to start
            self.editor.moveCursor(QTextCursor.MoveOperation.Start)
            # Try find again
            found = self.editor.find(text, flags)
            
            if not found:
                # Still not found, restore cursor (though find() usually doesn't move if fails)
                self.editor.setTextCursor(original_cursor)
                if self._dialog:
                    self._dialog.set_not_found_state()
                return False
        
        return True

    def find_all(self, text: str, case_sensitive: bool, whole_words: bool):
        """Find all occurrences and populate results list."""
        flags = QTextDocument.FindFlag(0)
        if case_sensitive:
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if whole_words:
            flags |= QTextDocument.FindFlag.FindWholeWords
            
        # We need to manually iterate
        doc = self.editor.document()
        results = []
        
        # Start from beginning
        cursor = QTextCursor(doc)
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        while True:
            cursor = doc.find(text, cursor, flags)
            if cursor.isNull():
                break
                
            # Extract snippet
            # Let's get context around the match
            # Match is at cursor.selectionStart() to cursor.selectionEnd()
            
            # create a temp cursor for extraction
            # context: 20 chars before, 20 after
            start_pos = cursor.selectionStart()
            end_pos = cursor.selectionEnd()
            
            ctx_start = max(0, start_pos - 20)
            ctx_end = min(doc.characterCount(), end_pos + 40) # + 40 to account for match len + after
            
            snippet_cursor = QTextCursor(doc)
            snippet_cursor.setPosition(ctx_start)
            snippet_cursor.setPosition(ctx_end, QTextCursor.MoveMode.KeepAnchor)
            
            raw_snippet = snippet_cursor.selectedText()
            
            # Highlight the match inside the snippet? 
            # Ideally we have HTML or strict bolding, but simple text is easier for QListWidget
            # We can use "..." ellipsis
            
            # Let's refine snippet logic simply
            # We can't bold easily in standard QListWidgetItem without valid HTML handling or delegates
            # We'll just provide the text.
            
            prefix = "..." if ctx_start > 0 else ""
            suffix = "..." if ctx_end < doc.characterCount() else ""
            
            results.append((start_pos, f"{prefix}{raw_snippet}{suffix}"))
            
        if self._dialog:
            self._dialog.show_results(results)

    def navigate_to(self, position: int):
        """Jump cursor to specific position."""
        cursor = self.editor.textCursor()
        cursor.setPosition(position)
        self.editor.setTextCursor(cursor)
        self.editor.ensureCursorVisible()
        self.editor.setFocus()

    def replace_current(self, text: str, new_text: str, case_sensitive: bool, whole_words: bool):
        """Replace current selection if it matches, then find next."""
        cursor = self.editor.textCursor()
        
        # Check if current selection matches 'text'
        # normalized comparison
        current_selection = cursor.selectedText()
        match = False
        
        if case_sensitive:
            match = current_selection == text
        else:
            match = current_selection.lower() == text.lower()
            
        if match:
            # Replace
            cursor.insertText(new_text)
            # find next immediately
            self.find_next(text, case_sensitive, whole_words)
        else:
            # Current selection isn't the text (or empty), so just find first
            self.find_next(text, case_sensitive, whole_words)

    def replace_all(self, text: str, new_text: str, case_sensitive: bool, whole_words: bool):
        """Replace all occurrences."""
        # Visual freeze
        if hasattr(self.editor, "setUpdatesEnabled"):
             self.editor.setUpdatesEnabled(False)
             
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        
        # Move to start
        self.editor.moveCursor(QTextCursor.MoveOperation.Start)
        
        count = 0
        while self.find_next(text, case_sensitive, whole_words):
            current_cursor = self.editor.textCursor()
            current_cursor.insertText(new_text)
            count += 1
            
        cursor.endEditBlock()
        if hasattr(self.editor, "setUpdatesEnabled"):
             self.editor.setUpdatesEnabled(True)
             
        if self._dialog:
             QMessageBox.information(self._dialog, "Replace All", f"Replaced {count} occurrences.")
             # Clear results list if any as they are now invalid
             self._dialog.show_results([])

