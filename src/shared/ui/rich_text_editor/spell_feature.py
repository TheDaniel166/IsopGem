"""
Spell Check Feature for Document Manager.
Provides real-time spell checking with red underlines and right-click suggestions.
"""
import re
import qtawesome as qta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QDialog, QMenu, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import (
    QAction, QTextCursor, QSyntaxHighlighter, 
    QTextCharFormat, QColor, QTextDocument
)

from shared.services.document_manager.spell_service import get_spell_service
import logging

logger = logging.getLogger(__name__)


class SpellHighlighter(QSyntaxHighlighter):
    """
    Syntax highlighter that underlines misspelled words with red wavy lines.
    """
    
    def __init__(self, document: QTextDocument, enabled: bool = True):
        super().__init__(document)
        self._spell_service = get_spell_service()
        self._enabled = enabled
        
        # Format for misspelled words
        self._error_format = QTextCharFormat()
        self._error_format.setUnderlineColor(QColor(Qt.GlobalColor.red))
        self._error_format.setUnderlineStyle(
            QTextCharFormat.UnderlineStyle.SpellCheckUnderline
        )
        
        # Word pattern - letters only (handles most cases)
        self._word_pattern = re.compile(r'\b[a-zA-Z]{2,}\b')
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
        self.rehighlight()
    
    def highlightBlock(self, text: str):
        """Called for each text block to apply highlighting."""
        if not self._enabled or not self._spell_service.is_enabled:
            return
        
        for match in self._word_pattern.finditer(text):
            word = match.group()
            if not self._spell_service.check(word):
                self.setFormat(
                    match.start(),
                    len(word),
                    self._error_format
                )


class SpellCheckDialog(QDialog):
    """
    Dialog for navigating through spelling errors (F7).
    Similar to Microsoft Word's spell check dialog.
    """
    
    def __init__(self, editor: QTextEdit, parent=None):
        super().__init__(parent)
        self.editor = editor
        self._spell_service = get_spell_service()
        self._current_word = ""
        self._current_cursor: QTextCursor = None
        
        self.setWindowTitle("Spelling")
        self.setMinimumSize(400, 300)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Current word display
        word_layout = QHBoxLayout()
        word_layout.addWidget(QLabel("Not in Dictionary:"))
        self.lbl_word = QLabel("")
        self.lbl_word.setStyleSheet("font-weight: bold; color: #dc2626; font-size: 14pt;")
        word_layout.addWidget(self.lbl_word)
        word_layout.addStretch()
        layout.addLayout(word_layout)
        
        # Suggestions list
        layout.addWidget(QLabel("Suggestions:"))
        self.list_suggestions = QListWidget()
        self.list_suggestions.itemDoubleClicked.connect(self._on_change)
        layout.addWidget(self.list_suggestions)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_ignore = QPushButton("Ignore")
        self.btn_ignore.clicked.connect(self._on_ignore)
        btn_layout.addWidget(self.btn_ignore)
        
        self.btn_ignore_all = QPushButton("Ignore All")
        self.btn_ignore_all.clicked.connect(self._on_ignore_all)
        btn_layout.addWidget(self.btn_ignore_all)
        
        self.btn_add = QPushButton("Add to Dictionary")
        self.btn_add.clicked.connect(self._on_add)
        btn_layout.addWidget(self.btn_add)
        
        layout.addLayout(btn_layout)
        
        btn_layout2 = QHBoxLayout()
        
        self.btn_change = QPushButton("Change")
        self.btn_change.setIcon(qta.icon("fa5s.check", color="#22c55e"))
        self.btn_change.clicked.connect(self._on_change)
        btn_layout2.addWidget(self.btn_change)
        
        self.btn_change_all = QPushButton("Change All")
        self.btn_change_all.clicked.connect(self._on_change_all)
        btn_layout2.addWidget(self.btn_change_all)
        
        btn_layout2.addStretch()
        
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        btn_layout2.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout2)
    
    def start_check(self):
        """Start checking from the beginning of the document."""
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.editor.setTextCursor(cursor)
        self._find_next()
        self.show()
    
    def _find_next(self):
        """Find the next misspelled word."""
        cursor = self.editor.textCursor()
        document = self.editor.document()
        text = document.toPlainText()
        start_pos = cursor.position()
        
        # Find words from current position
        word_pattern = re.compile(r'\b[a-zA-Z]{2,}\b')
        
        for match in word_pattern.finditer(text, start_pos):
            word = match.group()
            if not self._spell_service.check(word):
                # Found misspelled word
                self._current_word = word
                
                # Select the word in editor
                cursor.setPosition(match.start())
                cursor.setPosition(match.end(), QTextCursor.MoveMode.KeepAnchor)
                self.editor.setTextCursor(cursor)
                self._current_cursor = cursor
                
                # Update dialog
                self.lbl_word.setText(word)
                self.list_suggestions.clear()
                suggestions = self._spell_service.suggest(word)
                for s in suggestions:
                    self.list_suggestions.addItem(s)
                if suggestions:
                    self.list_suggestions.setCurrentRow(0)
                
                return True
        
        # No more errors
        self.lbl_word.setText("(No more errors)")
        self.list_suggestions.clear()
        self._current_word = ""
        return False
    
    def _on_ignore(self):
        """Ignore this occurrence."""
        self._find_next()
    
    def _on_ignore_all(self):
        """Ignore all occurrences of this word."""
        if self._current_word:
            self._spell_service.ignore_all(self._current_word)
        self._find_next()
    
    def _on_add(self):
        """Add word to custom dictionary."""
        if self._current_word:
            self._spell_service.add_to_dictionary(self._current_word)
        self._find_next()
    
    def _on_change(self):
        """Replace with selected suggestion."""
        selected = self.list_suggestions.currentItem()
        if selected and self._current_cursor:
            replacement = selected.text()
            self._current_cursor.insertText(replacement)
        self._find_next()
    
    def _on_change_all(self):
        """Replace all occurrences with selected suggestion."""
        selected = self.list_suggestions.currentItem()
        if not selected or not self._current_word:
            return
        
        replacement = selected.text()
        cursor = self.editor.textCursor()
        
        # Find and replace all
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        while True:
            cursor = self.editor.document().find(
                self._current_word, 
                cursor,
                QTextDocument.FindFlag.FindWholeWords
            )
            if cursor.isNull():
                break
            cursor.insertText(replacement)
        
        cursor.endEditBlock()
        self._find_next()


class SpellFeature:
    """
    Controller that integrates spell checking into the editor.
    """
    
    def __init__(self, main_editor):
        self.main = main_editor
        self.editor = main_editor.editor
        self._spell_service = get_spell_service()
        
        # Create highlighter
        self._highlighter = SpellHighlighter(self.editor.document())
        
        # Dialog (lazy created)
        self._dialog = None
        
        # Debounce timer for rehighlighting
        self._rehighlight_timer = QTimer()
        self._rehighlight_timer.setSingleShot(True)
        self._rehighlight_timer.timeout.connect(self._on_rehighlight)
        
        # Connect signals
        self.editor.textChanged.connect(self._schedule_rehighlight)
    
    def _schedule_rehighlight(self):
        """Schedule a rehighlight after a short delay (debounce)."""
        self._rehighlight_timer.start(500)  # 500ms delay
    
    def _on_rehighlight(self):
        """Rehighlight the document."""
        self._safe_rehighlight()
    
    @property
    def enabled(self) -> bool:
        return self._highlighter.enabled
    
    @enabled.setter
    def enabled(self, value: bool):
        self._highlighter.enabled = value
    
    def toggle(self):
        """Toggle spell checking on/off."""
        self.enabled = not self.enabled
        return self.enabled
    
    def create_ribbon_action(self, parent) -> QAction:
        """Create action for the ribbon."""
        action = QAction("Spelling", parent)
        action.setToolTip("Check Spelling (F7)")
        action.setIcon(qta.icon("fa5s.spell-check", color="#1e293b"))
        action.triggered.connect(self.show_dialog)
        return action
    
    def create_toggle_action(self, parent) -> QAction:
        """Create toggle action for enabling/disabling spell check."""
        action = QAction("Toggle Spell Check", parent)
        action.setCheckable(True)
        action.setChecked(self.enabled)
        action.setToolTip("Enable/Disable Spell Check")
        action.setIcon(qta.icon("fa5s.underline", color="#1e293b"))
        action.triggered.connect(lambda checked: setattr(self, 'enabled', checked))
        return action
    
    def show_dialog(self):
        """Show the spell check dialog."""
        if self._dialog is None:
            self._dialog = SpellCheckDialog(self.editor, parent=self.main)
        self._dialog.start_check()
    
    def extend_context_menu(self, menu: QMenu, pos):
        """
        Add spelling suggestions to context menu if cursor is on misspelled word.
        """
        if not self._spell_service.is_enabled:
            return
        
        cursor = self.editor.cursorForPosition(pos)
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        
        if not word or len(word) < 2:
            return
        
        # Check if word is misspelled
        if self._spell_service.check(word):
            return  # Word is correct
        
        # Add suggestions at the top of the menu
        suggestions = self._spell_service.suggest(word, max_suggestions=5)
        
        if suggestions:
            # Insert before first action
            first_action = menu.actions()[0] if menu.actions() else None
            
            for suggestion in suggestions:
                action = QAction(suggestion, menu)
                action.setFont(action.font())
                action.triggered.connect(
                    lambda checked, s=suggestion, c=cursor: self._replace_word(c, s)
                )
                if first_action:
                    menu.insertAction(first_action, action)
                else:
                    menu.addAction(action)
            
            # Add separator and dictionary options
            sep = menu.insertSeparator(first_action) if first_action else menu.addSeparator()
            
            ignore_action = QAction(qta.icon("fa5s.minus-circle", color="#6b7280"), "Ignore", menu)
            ignore_action.triggered.connect(lambda: self._ignore_word(word))
            menu.insertAction(first_action, ignore_action) if first_action else menu.addAction(ignore_action)
            
            add_action = QAction(qta.icon("fa5s.plus-circle", color="#22c55e"), "Add to Dictionary", menu)
            add_action.triggered.connect(lambda: self._add_word(word))
            menu.insertAction(first_action, add_action) if first_action else menu.addAction(add_action)
            
            menu.insertSeparator(first_action) if first_action else menu.addSeparator()
    
    def _replace_word(self, cursor: QTextCursor, replacement: str):
        """Replace word at cursor with replacement."""
        cursor.insertText(replacement)
        self._safe_rehighlight()
    
    def _ignore_word(self, word: str):
        """Ignore word for this session."""
        self._spell_service.ignore(word)
        self._safe_rehighlight()
    
    def _add_word(self, word: str):
        """Add word to custom dictionary."""
        self._spell_service.add_to_dictionary(word)
        self._safe_rehighlight()
    
    def _safe_rehighlight(self):
        """Safely rehighlight, handling case where C++ object is deleted."""
        try:
            if self._highlighter is not None and self._highlighter.document() is not None:
                self._highlighter.rehighlight()
        except RuntimeError:
            pass
