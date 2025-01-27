from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                           QToolBar, QAction, QFontComboBox, QComboBox,
                           QFileDialog, QMessageBox)
from PyQt5.Qsci import QsciScintilla
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

class DocumentEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_editor()
        self.setup_toolbar()
        self.connect_toolbar_actions()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.toolbar = QToolBar()
        layout.addWidget(self.toolbar)
        self.editor = QsciScintilla()
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def setup_editor(self):
        # Basic editor settings
        self.editor.setWrapMode(QsciScintilla.WrapWord)
        self.editor.setMarginWidth(0, 0)
        
        # Font and colors
        self.editor.setFont(QFont("Arial", 11))
        self.editor.setPaper(QColor("white"))
        self.editor.setColor(QColor("black"))
        
        # Writing aids
        self.editor.setCaretLineVisible(True)
        self.editor.setCaretLineBackgroundColor(QColor("#f0f0f0"))
        
        # Document interaction
        self.editor.setAcceptDrops(True)
        self.editor.setReadOnly(False)
        
        # Selection settings
        self.editor.setSelectionBackgroundColor(QColor("#c0d8f0"))
        self.editor.setSelectionForegroundColor(QColor("black"))

    def setup_toolbar(self):
        # File Operations
        self.new_action = QAction("New", self)
        self.open_action = QAction("Open", self)
        self.save_action = QAction("Save", self)
        self.print_action = QAction("Print", self)
        
        # Edit Operations
        self.cut_action = QAction("Cut", self)
        self.copy_action = QAction("Copy", self)
        self.paste_action = QAction("Paste", self)
        self.undo_action = QAction("Undo", self)
        self.redo_action = QAction("Redo", self)
        
        # Text Formatting
        self.font_family = QFontComboBox()
        self.font_size = QComboBox()
        self.font_size.addItems([str(size) for size in range(8, 49, 2)])
        
        self.bold_action = QAction("Bold", self)
        self.bold_action.setCheckable(True)
        self.italic_action = QAction("Italic", self)
        self.italic_action.setCheckable(True)
        self.underline_action = QAction("Underline", self)
        self.underline_action.setCheckable(True)
        
        #superscript and subscript
        self.superscript_action = QAction("Superscript", self)
        self.superscript_action.setCheckable(True)
        self.subscript_action = QAction("Subscript", self)
        self.subscript_action.setCheckable(True)
        
        # Paragraph Formatting
        self.align_left = QAction("Align Left", self)
        self.align_center = QAction("Center", self)
        self.align_right = QAction("Align Right", self)
        self.align_justify = QAction("Justify", self)
        
        # Search Operations
        self.find_action = QAction("Find", self)
        self.replace_action = QAction("Replace", self)
        
        # Add to Toolbar with Separators
        self.toolbar.addAction(self.new_action)
        self.toolbar.addAction(self.open_action)
        self.toolbar.addAction(self.save_action)
        self.toolbar.addAction(self.print_action)
        self.toolbar.addSeparator()
        
        self.toolbar.addAction(self.cut_action)
        self.toolbar.addAction(self.copy_action)
        self.toolbar.addAction(self.paste_action)
        self.toolbar.addSeparator()
        
        self.toolbar.addAction(self.undo_action)
        self.toolbar.addAction(self.redo_action)
        self.toolbar.addSeparator()
        
        self.toolbar.addWidget(self.font_family)
        self.toolbar.addWidget(self.font_size)
        self.toolbar.addSeparator()
        
        self.toolbar.addAction(self.bold_action)
        self.toolbar.addAction(self.italic_action)
        self.toolbar.addAction(self.underline_action)
        self.toolbar.addSeparator()
        
        self.toolbar.addAction(self.align_left)
        self.toolbar.addAction(self.align_center)
        self.toolbar.addAction(self.align_right)
        self.toolbar.addAction(self.align_justify)
        self.toolbar.addSeparator()
        
        self.toolbar.addAction(self.find_action)
        self.toolbar.addAction(self.replace_action)
        
        self.toolbar.addAction(self.superscript_action)
        self.toolbar.addAction(self.subscript_action)        

    def connect_toolbar_actions(self):
        # File Operations
        self.new_action.triggered.connect(self.new_document)
        self.open_action.triggered.connect(self.open_document)
        self.save_action.triggered.connect(self.save_document)
        self.print_action.triggered.connect(self.print_document)
        
        # Edit Operations
        self.cut_action.triggered.connect(self.editor.cut)
        self.copy_action.triggered.connect(self.editor.copy)
        self.paste_action.triggered.connect(self.editor.paste)
        self.undo_action.triggered.connect(self.editor.undo)
        self.redo_action.triggered.connect(self.editor.redo)
        
        # Text Formatting
        self.font_family.currentFontChanged.connect(self.change_font_family)
        self.font_size.currentTextChanged.connect(self.change_font_size)
        self.bold_action.triggered.connect(self.toggle_bold)
        self.italic_action.triggered.connect(self.toggle_italic)
        self.underline_action.triggered.connect(self.toggle_underline)
        
        # Paragraph Formatting
        self.align_left.triggered.connect(lambda: self.align_text('left'))
        self.align_center.triggered.connect(lambda: self.align_text('center'))
        self.align_right.triggered.connect(lambda: self.align_text('right'))
        self.align_justify.triggered.connect(lambda: self.align_text('justify'))
        
        # Search Operations
        self.find_action.triggered.connect(self.show_find)
        self.replace_action.triggered.connect(self.show_replace)

        self.superscript_action.triggered.connect(self.toggle_superscript)
        self.subscript_action.triggered.connect(self.toggle_subscript)        
        

    def new_document(self):
        self.editor.clear()

    def open_document(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
        if filename:
            try:
                with open(filename, 'r') as file:
                    self.editor.setText(file.read())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def save_document(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt);;All Files (*)")
        if filename:
            try:
                with open(filename, 'w') as file:
                    file.write(self.editor.text())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")

    def align_text(self, alignment):
        # Implementation depends on QScintilla's capabilities
        pass

    def change_font_family(self, font):
        self.editor.setFont(font)
        
    def change_font_size(self, size):
        font = self.editor.font()
        font.setPointSize(int(size))
        self.editor.setFont(font)
        
    def toggle_bold(self, checked):
        font = self.editor.font()
        font.setBold(checked)
        self.editor.setFont(font)
        
    def toggle_italic(self, checked):
        font = self.editor.font()
        font.setItalic(checked)
        self.editor.setFont(font)
        
    def toggle_underline(self, checked):
        font = self.editor.font()
        font.setUnderline(checked)
        self.editor.setFont(font)
        
    def print_document(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QPrintDialog.Accepted:
            # Implement printing logic
            pass
            
    def show_find(self):
        self.editor.findFirst(
            "text to find",  # Replace with dialog input
            False,  # Regular expression
            True,   # Case sensitive
            True,   # Whole words only
            True,   # Wrap around document
            True    # Forward search
        )
        
    def show_replace(self):
        # Implement replace dialog and logic
        pass

    def toggle_superscript(self, checked):
        current_font = self.editor.font()
        current_size = current_font.pointSizeF()  # Use pointSizeF() for floating point precision
        
        if checked:
            new_size = max(6.0, current_size * 0.7)
            current_font.setPointSizeF(new_size)
            self.editor.setFont(current_font)
        else:
            original_size = current_size / 0.7
            current_font.setPointSizeF(original_size)
            self.editor.setFont(current_font)

    def toggle_subscript(self, checked):
        current_font = self.editor.font()
        current_size = current_font.pointSizeF()  # Use pointSizeF() for floating point precision
        
        if checked:
            new_size = max(6.0, current_size * 0.7)
            current_font.setPointSizeF(new_size)
            self.editor.setFont(current_font)
        else:
            original_size = current_size / 0.7
            current_font.setPointSizeF(original_size)
            self.editor.setFont(current_font)
