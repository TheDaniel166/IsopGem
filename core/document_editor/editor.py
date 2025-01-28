from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QToolBar, 
                            QTextEdit, QComboBox, QSpinBox, QColorDialog, 
                            QFontComboBox, QPushButton, QMenu, QAction,
                            QStatusBar, QFrame, QDialog, QDialogButtonBox,
                            QFileDialog, QMessageBox, QFormLayout, QGroupBox,
                            QGridLayout, QLabel, QTabWidget, QRadioButton,
                            QButtonGroup, QCheckBox, QGraphicsBlurEffect,
                            QGraphicsScene, QGraphicsPixmapItem, QDoubleSpinBox,
                            QTreeWidget, QTreeWidgetItem, QDockWidget)
from PyQt5.QtGui import (QTextCharFormat, QColor, QTextCursor, QTextListFormat,
                        QTextTableFormat, QImage, QTextFrameFormat, QFont,
                        QTextBlockFormat, QPainter, QTextImageFormat, QTextFormat,
                        QTransform, QPen, QPixmap)
from PyQt5.QtCore import Qt, QSizeF, QRect, QSize, QTimer
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from PyQt5.QtWidgets import QApplication
import os
import math
from datetime import datetime
from PyQt5.QtCore import QSettings
from zlib import compress, decompress  # Add to imports
from .style_inspector import StyleInspector

class DocumentEditor(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize instance variables first
        self.current_file = None
        self.resize_handles_visible = False
        self.current_handle = None
        self.handle_rects = {}  # Store handle rectangles
        
        # Auto-save settings
        self.auto_save_interval = 5 * 60 * 1000  # 5 minutes in milliseconds
        
        # Recent files list
        self.max_recent_files = 10
        self.recent_files = []
        
        # Backup settings
        self.backup_enabled = True
        self.max_backups = 5
        self.backup_dir = os.path.join(os.path.expanduser('~'), '.document_backups')
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

        # Then setup UI and connections
        self.setup_ui()
        self.setup_editor()
        self.setup_toolbars()
        self.setup_status_bar()
        self.setup_connections()
        
        # Finally, setup features that depend on UI elements
        self.setup_auto_save()
        self.load_recent_files()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        
        # Main toolbar
        self.main_toolbar = QToolBar()
        self.format_toolbar = QToolBar()
        self.insert_toolbar = QToolBar()
        
        # Editor
        self.editor = QTextEdit()
        
        # Status bar
        self.status_bar = QStatusBar()
        
        # Add to layout
        self.layout.addWidget(self.main_toolbar)
        self.layout.addWidget(self.format_toolbar)
        self.layout.addWidget(self.insert_toolbar)
        self.layout.addWidget(self.editor)
        self.layout.addWidget(self.status_bar)
        
        self.setLayout(self.layout)

    def setup_editor(self):
        # Editor settings
        self.editor.setAcceptRichText(True)
        self.editor.setAutoFormatting(QTextEdit.AutoAll)
        
        # Default font
        font = QFont("Arial", 11)
        self.editor.setFont(font)
        
        # Document settings
        doc = self.editor.document()
        doc.setDocumentMargin(20)
        
        # Clear undo stack and set initial state
        doc.clearUndoRedoStacks()
        doc.setModified(False)
        
        # Enable drag and drop
        self.editor.setAcceptDrops(True)

    def setup_toolbars(self):
        # Main Toolbar - File Operations
        self.setup_file_toolbar()
        
        # Format Toolbar - Text Formatting
        self.setup_format_toolbar()
        
        # Insert Toolbar - Tables, Images, etc.
        self.setup_insert_toolbar()

    def setup_file_toolbar(self):
        # File operations
        new_action = self.create_action("New", self.new_document, "Ctrl+N")
        open_action = self.create_action("Open", self.open_document, "Ctrl+O")
        save_action = self.create_action("Save", self.save_document, "Ctrl+S")
        print_action = self.create_action("Print", self.print_document, "Ctrl+P")
        preview_action = self.create_action("Print Preview", self.print_preview)
        
        # Add undo/redo actions
        self.undo_action = self.create_action("Undo", self.editor.undo, "Ctrl+Z")
        self.redo_action = self.create_action("Redo", self.editor.redo, "Ctrl+Shift+Z")
        
        # Update undo/redo availability
        self.undo_action.setEnabled(False)
        self.redo_action.setEnabled(False)
        
        # Add to toolbar
        self.main_toolbar.addAction(new_action)
        self.main_toolbar.addAction(open_action)
        self.main_toolbar.addAction(save_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.undo_action)
        self.main_toolbar.addAction(self.redo_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(print_action)
        self.main_toolbar.addAction(preview_action)
        
        # Add settings action
        settings_action = self.create_action("Settings", self.show_auto_save_settings)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(settings_action)

    def setup_format_toolbar(self):
        # Font family
        self.font_family = QFontComboBox()
        self.font_family.setMinimumWidth(150)
        
        # Font size
        self.font_size = QSpinBox()
        self.font_size.setMinimum(6)
        self.font_size.setMaximum(72)
        self.font_size.setValue(11)
        
        # Text formatting
        bold_action = self.create_action("Bold", self.toggle_bold, "Ctrl+B", checkable=True)
        italic_action = self.create_action("Italic", self.toggle_italic, "Ctrl+I", checkable=True)
        underline_action = self.create_action("Underline", self.toggle_underline, "Ctrl+U", checkable=True)
        
        # Text alignment
        align_left = self.create_action("Left", lambda: self.align_text('left'))
        align_center = self.create_action("Center", lambda: self.align_text('center'))
        align_right = self.create_action("Right", lambda: self.align_text('right'))
        align_justify = self.create_action("Justify", lambda: self.align_text('justify'))
        
        # Colors
        text_color_action = self.create_action("Text Color", self.text_color)
        highlight_action = self.create_action("Highlight", self.highlight_color)
        
        # Add text styles
        self.style_combo = QComboBox()
        self.style_combo.setMinimumWidth(120)
        self.style_combo.addItems([
            "Normal",
            "Heading 1",
            "Heading 2",
            "Heading 3",
            "Heading 4",
            "Title",
            "Subtitle"
        ])
        self.style_combo.currentTextChanged.connect(self.apply_text_style)
        
        # Line spacing
        line_spacing_menu = QMenu("Line Spacing", self)
        for spacing in [1.0, 1.15, 1.5, 2.0]:
            action = QAction(f"{spacing:.2f}", self)
            action.setData(spacing)
            action.triggered.connect(lambda checked, s=spacing: self.set_line_spacing(s))
            line_spacing_menu.addAction(action)
        
        # Add custom line spacing option
        line_spacing_menu.addSeparator()
        custom_line_action = QAction("Custom...", self)
        custom_line_action.triggered.connect(self.show_custom_line_spacing)
        line_spacing_menu.addAction(custom_line_action)
        
        line_spacing_button = QPushButton("Line Spacing")
        line_spacing_button.setMenu(line_spacing_menu)
        
        # Paragraph spacing
        para_spacing_menu = QMenu("Paragraph Spacing", self)
        for spacing in [0, 6, 12, 18, 24]:
            action = QAction(f"{spacing}pt", self)
            action.setData(spacing)
            action.triggered.connect(lambda checked, s=spacing: self.set_paragraph_spacing(s))
            para_spacing_menu.addAction(action)
            
        # Add custom paragraph spacing option
        para_spacing_menu.addSeparator()
        custom_para_action = QAction("Custom...", self)
        custom_para_action.triggered.connect(self.show_custom_paragraph_spacing)
        para_spacing_menu.addAction(custom_para_action)
        
        para_spacing_button = QPushButton("Paragraph Spacing")
        para_spacing_button.setMenu(para_spacing_menu)
        
        # Add to toolbar
        self.format_toolbar.addWidget(self.font_family)
        self.format_toolbar.addWidget(self.font_size)
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(bold_action)
        self.format_toolbar.addAction(italic_action)
        self.format_toolbar.addAction(underline_action)
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(align_left)
        self.format_toolbar.addAction(align_center)
        self.format_toolbar.addAction(align_right)
        self.format_toolbar.addAction(align_justify)
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(text_color_action)
        self.format_toolbar.addAction(highlight_action)
        self.format_toolbar.addWidget(self.style_combo)
        self.format_toolbar.addWidget(line_spacing_button)
        self.format_toolbar.addWidget(para_spacing_button)
        self.format_toolbar.addSeparator()
        
        # Add format painter
        self.format_painter = self.create_action(
            "Format Painter", 
            self.toggle_format_painter,
            checkable=True
        )
        self.format_toolbar.addAction(self.format_painter)
        
        # Store copied format
        self.copied_format = None

    def setup_insert_toolbar(self):
        # Create table button and menu
        table_button = QPushButton("Table")
        table_menu = QMenu()
        table_button.setMenu(table_menu)
        
        # Table insertion submenu
        insert_submenu = QMenu("Insert", self)
        insert_table_action = self.create_action("Custom Table...", self.show_table_dialog)
        insert_submenu.addAction(insert_table_action)
        
        # Add table templates
        insert_submenu.addSeparator()
        templates = {
            "Simple 2x2": (2, 2),
            "Header Row 3x3": (3, 3),
            "Calendar 7x5": (5, 7),
            "Contact Card 2x3": (2, 3)
        }
        for name, (rows, cols) in templates.items():
            action = QAction(name, self)
            action.triggered.connect(lambda checked, r=rows, c=cols, n=name: 
                                  self.insert_table_template(r, c, n))
            insert_submenu.addAction(action)
        
        table_menu.addMenu(insert_submenu)
        table_menu.addSeparator()
        
        # Row/Column operations
        row_menu = QMenu("Row", self)
        row_menu.addAction(self.create_action("Insert Row Above", self.insert_row_above))
        row_menu.addAction(self.create_action("Insert Row Below", self.insert_row_below))
        row_menu.addAction(self.create_action("Delete Row", self.delete_row))
        table_menu.addMenu(row_menu)
        
        col_menu = QMenu("Column", self)
        col_menu.addAction(self.create_action("Insert Column Left", self.insert_column_left))
        col_menu.addAction(self.create_action("Insert Column Right", self.insert_column_right))
        col_menu.addAction(self.create_action("Delete Column", self.delete_column))
        table_menu.addMenu(col_menu)
        
        table_menu.addSeparator()
        
        # Table formatting
        format_menu = QMenu("Format", self)
        format_menu.addAction(self.create_action("Table Properties...", self.show_table_format_dialog))
        format_menu.addAction(self.create_action("Cell Properties...", self.show_cell_format_dialog))
        
        # Border presets submenu
        border_presets = QMenu("Border Presets", self)
        border_presets.addAction(self.create_action("No Borders", lambda: self.apply_border_preset("none")))
        border_presets.addAction(self.create_action("All Borders", lambda: self.apply_border_preset("all")))
        border_presets.addAction(self.create_action("Outside Borders", lambda: self.apply_border_preset("outside")))
        border_presets.addAction(self.create_action("Inside Borders", lambda: self.apply_border_preset("inside")))
        format_menu.addMenu(border_presets)
        
        table_menu.addMenu(format_menu)
        
        # Add to toolbar
        self.insert_toolbar.addWidget(table_button)
        
        # Add other insert toolbar items (images, lists, etc.)
        # ... rest of your existing insert toolbar setup ...

    def setup_status_bar(self):
        """Setup the status bar with document information"""
        # Create permanent widgets for the status bar
        self.word_count_label = QLabel("Words: 0")
        self.char_count_label = QLabel("Characters: 0")
        self.paragraph_count_label = QLabel("Paragraphs: 0")
        self.page_count_label = QLabel("Pages: 0")
        self.cursor_pos_label = QLabel("Line: 1, Column: 1")
        self.zoom_label = QLabel("100%")
        self.file_info_label = QLabel()
        
        # Add widgets to status bar
        self.status_bar.addPermanentWidget(self.word_count_label)
        self.status_bar.addPermanentWidget(QLabel("|"))
        self.status_bar.addPermanentWidget(self.char_count_label)
        self.status_bar.addPermanentWidget(QLabel("|"))
        self.status_bar.addPermanentWidget(self.paragraph_count_label)
        self.status_bar.addPermanentWidget(QLabel("|"))
        self.status_bar.addPermanentWidget(self.page_count_label)
        self.status_bar.addPermanentWidget(QLabel("|"))
        self.status_bar.addPermanentWidget(self.cursor_pos_label)
        self.status_bar.addPermanentWidget(QLabel("|"))
        self.status_bar.addPermanentWidget(self.zoom_label)
        self.status_bar.addPermanentWidget(QLabel("|"))
        self.status_bar.addPermanentWidget(self.file_info_label)
        
        # Initial update
        self.update_status_bar()

    def update_status_bar(self):
        """Update all status bar information"""
        # Get text statistics
        text = self.editor.toPlainText()
        char_count = len(text)
        word_count = len(text.split()) if text else 0
        
        # Count paragraphs (non-empty lines)
        paragraphs = [p for p in text.split('\n') if p.strip()]
        paragraph_count = len(paragraphs)
        
        # Estimate page count (roughly 250 words per page)
        page_count = max(1, math.ceil(word_count / 250))
        
        # Update statistics labels
        self.word_count_label.setText(f"Words: {word_count}")
        self.char_count_label.setText(f"Characters: {char_count}")
        self.paragraph_count_label.setText(f"Paragraphs: {paragraph_count}")
        self.page_count_label.setText(f"Pages: {page_count}")
        
        # Get cursor position
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.cursor_pos_label.setText(f"Line: {line}, Column: {column}")
        
        # Update file information
        self.update_file_info()
        
        # Get selection info
        if cursor.hasSelection():
            selection = cursor.selectedText()
            sel_chars = len(selection)
            sel_words = len(selection.split()) if selection else 0
            self.status_bar.showMessage(
                f"Selected: {sel_words} words, {sel_chars} characters", 
                2000
            )

    def update_file_info(self):
        """Update file information in status bar"""
        if self.current_file:
            try:
                # Get file stats
                stats = os.stat(self.current_file)
                size = self.format_file_size(stats.st_size)
                modified = datetime.fromtimestamp(stats.st_mtime)
                modified_str = modified.strftime("%Y-%m-%d %H:%M")
                
                # Get file type
                file_type = os.path.splitext(self.current_file)[1].upper()[1:]
                if not file_type:
                    file_type = "TXT"
                
                # Update label
                self.file_info_label.setText(
                    f"{file_type} | {size} | Modified: {modified_str}"
                )
            except Exception:
                self.file_info_label.setText("No file information available")
        else:
            self.file_info_label.setText("New Document")

    def format_file_size(self, size_in_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.1f} {unit}"
            size_in_bytes /= 1024
        return f"{size_in_bytes:.1f} TB"

    def save_file(self, file_name):
        """Save document to file"""
        try:
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(self.editor.toHtml())
            self.current_file = file_name
            self.editor.document().setModified(False)
            self.status_bar.showMessage(f"Saved {file_name}")
            self.update_file_info()
            
            # Add to recent files and create backup
            self.add_to_recent_files(file_name)
            self.create_backup()
            return True
        except Exception as e:
            self.status_bar.showMessage(f"Failed to save {file_name}: {str(e)}")
            return False

    def text_changed(self):
        """Handle text changes"""
        self.status_bar.showMessage("Document modified")
        self.update_edit_status()
        self.update_status_bar()  # Update statistics when text changes

    def cursor_position_changed(self):
        """Update UI based on cursor position"""
        cursor = self.editor.textCursor()
        
        # Update format buttons
        format = cursor.charFormat()
        self.update_format_buttons(format)
        
        # Update style combo based on current block format
        self.update_style_combo(cursor)
        
        # Update status bar
        self.update_status_bar()

    def selection_changed(self):
        """Handle selection changes"""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selection = cursor.selectedText()
            sel_chars = len(selection)
            sel_words = len(selection.split()) if selection else 0
            self.status_bar.showMessage(
                f"Selected: {sel_words} words, {sel_chars} characters",
                2000
            )
        else:
            self.status_bar.clearMessage()

    def update_format_buttons(self, format):
        """Update format button states"""
        font = format.font()
        self.font_family.setCurrentFont(font)
        self.font_size.setValue(int(font.pointSize()))
        
        # Update formatting buttons
        bold_action = self.format_toolbar.actions()[3]  # Bold action
        italic_action = self.format_toolbar.actions()[4]  # Italic action
        underline_action = self.format_toolbar.actions()[5]  # Underline action
        
        bold_action.setChecked(font.bold())
        italic_action.setChecked(font.italic())
        underline_action.setChecked(font.underline())

    def toggle_bold(self, checked):
        """Toggle bold formatting"""
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if checked else QFont.Normal)
        self.merge_format(fmt)

    def toggle_italic(self, checked):
        """Toggle italic formatting"""
        fmt = QTextCharFormat()
        fmt.setFontItalic(checked)
        self.merge_format(fmt)

    def toggle_underline(self, checked):
        """Toggle underline formatting"""
        fmt = QTextCharFormat()
        fmt.setFontUnderline(checked)
        self.merge_format(fmt)

    def text_color(self):
        """Change text color"""
        color = QColorDialog.getColor(self.editor.textColor(), self)
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            self.merge_format(fmt)

    def highlight_color(self):
        """Change text background color"""
        color = QColorDialog.getColor(self.editor.textBackgroundColor(), self)
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setBackground(color)
            self.merge_format(fmt)

    def align_text(self, alignment):
        """Set text alignment"""
        if alignment == 'left':
            self.editor.setAlignment(Qt.AlignLeft)
        elif alignment == 'center':
            self.editor.setAlignment(Qt.AlignCenter)
        elif alignment == 'right':
            self.editor.setAlignment(Qt.AlignRight)
        elif alignment == 'justify':
            self.editor.setAlignment(Qt.AlignJustify)

    def merge_format(self, format):
        """Apply the given format to the selected text or at cursor position"""
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(format)
        self.editor.mergeCurrentCharFormat(format)

    def create_action(self, text, slot, shortcut=None, checkable=False):
        """Create a QAction with the given parameters"""
        action = QAction(text, self)
        action.triggered.connect(slot)
        if shortcut:
            action.setShortcut(shortcut)
        if checkable:
            action.setCheckable(True)
        return action

    def show_table_dialog(self):
        """Show dialog for table insertion"""
        dialog = TableDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            rows = dialog.rows_spin.value()
            cols = dialog.cols_spin.value()
            self.insert_table(rows, cols)

    def insert_table(self, rows, cols):
        """Insert table at current cursor position"""
        cursor = self.editor.textCursor()
        table_format = QTextTableFormat()
        table_format.setCellPadding(5)
        table_format.setCellSpacing(0)
        table_format.setBorder(1)
        
        # Create table
        table = cursor.insertTable(rows, cols, table_format)
        QApplication.processEvents()
        
        return table

    def merge_table_cells(self):
        """Merge selected table cells"""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            table = cursor.currentTable()
            if table:
                cell = table.cellAt(cursor)
                if cell.isValid():
                    table.mergeCells(cursor)

    def split_table_cells(self):
        """Split merged table cells"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            if cell.isValid():
                table.splitCell(cell.row(), cell.column(), 1, 1)

    def insert_image(self):
        """Insert an image at cursor position"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Insert Image", "",
            "Images (*.png *.jpg *.bmp *.gif)"
        )
        if file_name:
            image = QImage(file_name)
            if not image.isNull():
                cursor = self.editor.textCursor()
                image_format = QTextImageFormat()
                image_format.setName(file_name)
                # Scale image if too large
                if image.width() > 800:
                    image = image.scaledToWidth(800, Qt.SmoothTransformation)
                image_format.setWidth(image.width())
                image_format.setHeight(image.height())
                cursor.insertImage(image_format)

    def insert_list(self, list_style):
        """Insert a list with the specified style"""
        cursor = self.editor.textCursor()
        list_format = QTextListFormat()
        list_format.setStyle(list_style)
        cursor.createList(list_format)

    def show_table_format_dialog(self):
        """Show dialog for table formatting"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            dialog = TableFormatDialog(self, table)
            if dialog.exec_() == QDialog.Accepted:
                self.apply_table_format(table, dialog.get_format())

    def apply_table_format(self, table, format_data):
        """Apply formatting to table"""
        table_format = table.format()
        
        # Convert Qt.PenStyle to QTextFrameFormat.BorderStyle
        border_style_map = {
            Qt.NoPen: QTextFrameFormat.BorderStyle_None,
            Qt.SolidLine: QTextFrameFormat.BorderStyle_Solid,
            Qt.DashLine: QTextFrameFormat.BorderStyle_Dashed,
            Qt.DotLine: QTextFrameFormat.BorderStyle_Dotted,
            Qt.DashDotLine: QTextFrameFormat.BorderStyle_Dot_Dash,
            Qt.DashDotDotLine: QTextFrameFormat.BorderStyle_Dot_Dot_Dash
        }
        
        # Apply formatting
        table_format.setBorder(format_data['border_width'])
        table_format.setBorderStyle(border_style_map.get(format_data['border_style'], QTextFrameFormat.BorderStyle_Solid))
        table_format.setBorderBrush(format_data['border_color'])
        table_format.setCellPadding(format_data['padding'])
        table_format.setCellSpacing(format_data['spacing'])
        table_format.setWidth(format_data['width'])
        
        if format_data['background_color']:
            table_format.setBackground(format_data['background_color'])
            
        table.setFormat(table_format)

    def show_image_resize_dialog(self):
        """Show dialog for image resizing"""
        cursor = self.editor.textCursor()
        image_format = cursor.charFormat().toImageFormat()
        if image_format.isValid():
            dialog = ImageResizeDialog(self, image_format)
            if dialog.exec_() == QDialog.Accepted:
                self.apply_image_format(cursor, dialog.get_format())

    def align_image(self, alignment):
        """Align the selected image"""
        cursor = self.editor.textCursor()
        image_format = cursor.charFormat().toImageFormat()
        if image_format.isValid():
            block_format = QTextBlockFormat()
            if alignment == 'left':
                block_format.setAlignment(Qt.AlignLeft)
            elif alignment == 'center':
                block_format.setAlignment(Qt.AlignCenter)
            elif alignment == 'right':
                block_format.setAlignment(Qt.AlignRight)
            cursor.mergeBlockFormat(block_format)

    def apply_image_format(self, cursor, format_data):
        """Apply formatting to image"""
        image_format = cursor.charFormat().toImageFormat()
        if image_format.isValid():
            image_format.setWidth(format_data['width'])
            image_format.setHeight(format_data['height'])
            cursor.mergeCharFormat(image_format)

    def show_cell_format_dialog(self):
        """Show dialog for cell formatting"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            if cell.isValid():
                dialog = TableCellFormatDialog(self, cell)
                if dialog.exec_() == QDialog.Accepted:
                    self.apply_cell_format(cell, dialog.get_format())

    def apply_cell_format(self, cell, format_data):
        """Apply formatting to specific cell"""
        cursor = cell.firstCursorPosition()
        block_format = cursor.blockFormat()
        
        # Background color
        block_format.setBackground(QColor(format_data['background_color']))
        
        # Borders
        block_format.setProperty(QTextFormat.TableCellBorderStyle, format_data['border_style'])
        block_format.setProperty(QTextFormat.TableCellBorderWidth, format_data['border_width'])
        block_format.setProperty(QTextFormat.TableCellBorderColor, QColor(format_data['border_color']))
        
        # Alignment
        block_format.setAlignment(format_data['alignment'])
        
        cursor.setBlockFormat(block_format)

    def rotate_image(self, degrees):
        """Rotate the selected image"""
        cursor = self.editor.textCursor()
        image_format = cursor.charFormat().toImageFormat()
        if image_format.isValid():
            image = QImage(image_format.name())
            transform = QTransform().rotate(degrees)
            rotated_image = image.transformed(transform, Qt.SmoothTransformation)
            
            # Save rotated image to temp file
            temp_path = f"{image_format.name()}_rotated.png"
            rotated_image.save(temp_path)
            
            # Update image in document
            new_format = QTextImageFormat()
            new_format.setName(temp_path)
            new_format.setWidth(rotated_image.width())
            new_format.setHeight(rotated_image.height())
            cursor.insertImage(new_format)

    def apply_image_filter(self, filter_type):
        """Apply filter to the selected image"""
        cursor = self.editor.textCursor()
        image_format = cursor.charFormat().toImageFormat()
        if image_format.isValid():
            image = QImage(image_format.name())
            
            if filter_type == 'grayscale':
                filtered = image.convertToFormat(QImage.Format_Grayscale8)
            elif filter_type == 'sepia':
                filtered = self.apply_sepia_filter(image)
            elif filter_type == 'blur':
                # New blur implementation
                pixmap = QPixmap.fromImage(image)
                scene = QGraphicsScene()
                item = QGraphicsPixmapItem(pixmap)
                blur = QGraphicsBlurEffect()
                blur.setBlurRadius(5)
                item.setGraphicsEffect(blur)
                scene.addItem(item)
                
                # Render the blurred result
                filtered = QImage(image.size(), QImage.Format_ARGB32)
                filtered.fill(Qt.transparent)
                painter = QPainter(filtered)
                scene.render(painter, filtered.rect(), scene.sceneRect())
                painter.end()
            
            # Save filtered image
            temp_path = f"{image_format.name()}_{filter_type}.png"
            filtered.save(temp_path)
            
            # Update image in document
            new_format = QTextImageFormat()
            new_format.setName(temp_path)
            new_format.setWidth(filtered.width())
            new_format.setHeight(filtered.height())
            cursor.insertImage(new_format)

    def apply_sepia_filter(self, image):
        """Apply sepia filter to image"""
        for y in range(image.height()):
            for x in range(image.width()):
                color = QColor(image.pixel(x, y))
                r, g, b = color.red(), color.green(), color.blue()
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                image.setPixel(x, y, QColor(
                    min(tr, 255),
                    min(tg, 255),
                    min(tb, 255)
                ).rgb())
        return image

    def paintEvent(self, event):
        """Override paint event to draw resize handles"""
        super().paintEvent(event)
        if self.resize_handles_visible:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw handles
            for position, rect in self.handle_rects.items():
                if position == self.current_handle:
                    # Highlight active handle
                    painter.setBrush(QColor(0, 120, 215))  # Blue when active
                    painter.setPen(QPen(QColor(255, 255, 255), 1))
                else:
                    # Normal handle appearance
                    painter.setBrush(QColor(255, 255, 255))  # White
                    painter.setPen(QPen(QColor(0, 120, 215), 1))  # Blue border
                
                painter.drawRect(rect)

    def mousePressEvent(self, event):
        """Handle mouse press events for resize handles"""
        if event.button() == Qt.LeftButton:
            cursor = self.editor.cursorForPosition(event.pos())
            image_format = cursor.charFormat().toImageFormat()
            if image_format.isValid():
                # Get image rectangle
                image_rect = self.editor.document().documentLayout().blockBoundingRect(cursor.block())
                handle_size = 8  # Size of resize handles
                
                # Create handle rectangles
                self.handle_rects = {
                    'top-left': QRect(
                        image_rect.left() - handle_size//2,
                        image_rect.top() - handle_size//2,
                        handle_size, handle_size
                    ),
                    'top-right': QRect(
                        image_rect.right() - handle_size//2,
                        image_rect.top() - handle_size//2,
                        handle_size, handle_size
                    ),
                    'bottom-left': QRect(
                        image_rect.left() - handle_size//2,
                        image_rect.bottom() - handle_size//2,
                        handle_size, handle_size
                    ),
                    'bottom-right': QRect(
                        image_rect.right() - handle_size//2,
                        image_rect.bottom() - handle_size//2,
                        handle_size, handle_size
                    )
                }
                
                # Check if click is on any handle
                for position, rect in self.handle_rects.items():
                    if rect.contains(event.pos()):
                        self.resizing_image = True
                        self.resize_start_pos = event.pos()
                        self.original_size = QSize(image_format.width(), image_format.height())
                        self.current_handle = position
                        self.setCursor(self.get_resize_cursor(position))
                        event.accept()
                        self.update()  # Redraw handles
                        return
                
                # Show handles when clicking on image
                self.resize_handles_visible = True
                self.update()  # Redraw to show handles

        if self.format_painter.isChecked() and self.copied_format:
            cursor = self.editor.cursorForPosition(event.pos())
            if event.modifiers() & Qt.ShiftModifier:
                # Apply to whole paragraph
                cursor.movePosition(QTextCursor.StartOfBlock)
                cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            else:
                # Apply to word
                cursor.select(QTextCursor.WordUnderCursor)
            
            cursor.mergeCharFormat(self.copied_format['char'])
            cursor.mergeBlockFormat(self.copied_format['block'])
            
            # Turn off format painter unless Ctrl is held
            if not (event.modifiers() & Qt.ControlModifier):
                self.format_painter.setChecked(False)
                self.copied_format = None
                self.editor.viewport().setCursor(Qt.IBeamCursor)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move events for image resizing"""
        if hasattr(self, 'resizing_image') and self.resizing_image:
            cursor = self.editor.textCursor()
            image_format = cursor.charFormat().toImageFormat()
            if image_format.isValid():
                delta = event.pos() - self.resize_start_pos
                new_size = self.calculate_new_size(delta)
                
                # Update image size
                image_format.setWidth(max(10, new_size.width()))
                image_format.setHeight(max(10, new_size.height()))
                cursor.mergeCharFormat(image_format)
                
                # Update handle positions
                self.update_handle_positions(event.pos())
        else:
            # Update cursor shape on hover
            for position, rect in self.handle_rects.items():
                if rect.contains(event.pos()):
                    self.setCursor(self.get_resize_cursor(position))
                    self.current_handle = position
                    self.update()  # Redraw handles
                    return
            self.setCursor(Qt.ArrowCursor)
            self.current_handle = None
            self.update()  # Redraw handles

    def calculate_new_size(self, delta):
        """Calculate new size based on resize handle and delta"""
        new_width = self.original_size.width()
        new_height = self.original_size.height()
        
        if self.current_handle in ['top-right', 'bottom-right']:
            new_width += delta.x()
        if self.current_handle in ['bottom-left', 'bottom-right']:
            new_height += delta.y()
        if self.current_handle in ['top-left', 'bottom-left']:
            new_width -= delta.x()
        if self.current_handle in ['top-left', 'top-right']:
            new_height -= delta.y()
        
        # Maintain aspect ratio if Shift is pressed
        if QApplication.keyboardModifiers() & Qt.ShiftModifier:
            ratio = self.original_size.width() / self.original_size.height()
            if abs(delta.x()) > abs(delta.y()):
                new_height = new_width / ratio
            else:
                new_width = new_height * ratio
        
        return QSize(new_width, new_height)

    def get_resize_cursor(self, position):
        """Get appropriate cursor shape for resize handle"""
        if position in ['top-left', 'bottom-right']:
            return Qt.SizeFDiagCursor
        elif position in ['top-right', 'bottom-left']:
            return Qt.SizeBDiagCursor
        return Qt.ArrowCursor

    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        super().mouseReleaseEvent(event)
        if hasattr(self, 'resizing_image'):
            self.resizing_image = False
            self.current_handle = None
            self.setCursor(Qt.ArrowCursor)
            self.update()  # Redraw handles

    def leaveEvent(self, event):
        """Handle mouse leave events"""
        super().leaveEvent(event)
        self.resize_handles_visible = False
        self.current_handle = None
        self.update()  # Remove handles

    def update_edit_status(self):
        """Update edit status information in status bar"""
        undo_available = self.editor.document().isUndoAvailable()
        redo_available = self.editor.document().isRedoAvailable()
        
        # Create status message
        status_parts = []
        if undo_available:
            status_parts.append("Undo available")
        if redo_available:
            status_parts.append("Redo available")
        
        if status_parts:
            status = " | ".join(status_parts)
        else:
            status = "No changes"
        
        # Add to permanent status bar widget
        if not hasattr(self, 'edit_status_label'):
            self.edit_status_label = QLabel()
            self.status_bar.addPermanentWidget(self.edit_status_label)
        
        self.edit_status_label.setText(status)

    def clear_undo_stack(self):
        """Clear the undo stack when loading a new document"""
        self.editor.document().clearUndoRedoStacks()
        self.update_edit_status()

    def setup_connections(self):
        """Setup signal connections"""
        # Existing connections
        self.font_family.currentFontChanged.connect(self.font_family_changed)
        self.font_size.valueChanged.connect(self.font_size_changed)
        self.editor.cursorPositionChanged.connect(self.cursor_position_changed)
        self.editor.textChanged.connect(self.text_changed)
        
        # Add undo/redo connections
        document = self.editor.document()
        document.undoAvailable.connect(self.undo_action.setEnabled)
        document.redoAvailable.connect(self.redo_action.setEnabled)
        
        # Clear undo stack when loading new document
        document.clearUndoRedoStacks()

    def setup_auto_save(self):
        """Setup auto-save timer"""
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(self.auto_save_interval)

    def auto_save(self):
        """Perform auto-save if document is modified"""
        if self.editor.document().isModified() and self.current_file:
            self.save_file(self.current_file)
            self.status_bar.showMessage("Auto-saved", 2000)

    def load_recent_files(self):
        """Load recent files list from settings"""
        settings = QSettings('YourCompany', 'YourApp')
        self.recent_files = settings.value('recent_files', [], str)
        self.update_recent_files_menu()

    def save_recent_files(self):
        """Save recent files list to settings"""
        settings = QSettings('YourCompany', 'YourApp')
        settings.setValue('recent_files', self.recent_files)

    def add_to_recent_files(self, file_path):
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        while len(self.recent_files) > self.max_recent_files:
            self.recent_files.pop()
        self.save_recent_files()
        self.update_recent_files_menu()

    def update_recent_files_menu(self):
        """Update recent files menu"""
        if not hasattr(self, 'recent_files_menu'):
            self.recent_files_menu = QMenu("Recent Files", self)
            # Create action for the menu
            recent_files_action = QAction("Recent Files", self)
            recent_files_action.setMenu(self.recent_files_menu)
            # Insert after New action
            self.main_toolbar.insertAction(self.main_toolbar.actions()[1], recent_files_action)
        
        self.recent_files_menu.clear()
        for file_path in self.recent_files:
            if os.path.exists(file_path):
                action = QAction(os.path.basename(file_path), self)
                action.setData(file_path)
                action.setStatusTip(file_path)
                action.triggered.connect(lambda checked, f=file_path: self.open_recent_file(f))
                self.recent_files_menu.addAction(action)

    def open_recent_file(self, file_path):
        """Open a file from recent files list"""
        if os.path.exists(file_path):
            self.load_file(file_path)
        else:
            QMessageBox.warning(
                self, "File Not Found",
                f"The file {file_path} no longer exists."
            )
            self.recent_files.remove(file_path)
            self.save_recent_files()
            self.update_recent_files_menu()

    def show_auto_save_settings(self):
        """Show auto-save settings dialog"""
        dialog = AutoSaveSettingsDialog(self)
        dialog.exec_()

    def apply_auto_save_settings(self):
        """Apply auto-save settings from QSettings"""
        settings = QSettings('YourCompany', 'YourApp')
        
        # Update auto-save settings
        auto_save_enabled = settings.value('auto_save/enabled', True, bool)
        interval_minutes = settings.value('auto_save/interval', 5, int)
        
        if auto_save_enabled:
            self.auto_save_interval = interval_minutes * 60 * 1000  # Convert to milliseconds
            self.auto_save_timer.start(self.auto_save_interval)
        else:
            self.auto_save_timer.stop()

    def create_backup(self):
        """Create backup of current file with optional compression"""
        if not self.backup_enabled or not self.current_file:
            return
            
        file_name = os.path.basename(self.current_file)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        settings = QSettings('YourCompany', 'YourApp')
        use_compression = settings.value('backup/compress', True, bool)
        
        if use_compression:
            backup_name = f"{file_name}.{timestamp}.bak.gz"
        else:
            backup_name = f"{file_name}.{timestamp}.bak"
            
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            content = self.editor.toHtml().encode('utf-8')
            
            if use_compression:
                content = compress(content)
            
            with open(backup_path, 'wb') as file:
                file.write(content)
            
            # Clean old backups
            self.clean_old_backups()
            
        except Exception as e:
            self.status_bar.showMessage(f"Backup failed: {str(e)}", 3000)

    def clean_old_backups(self):
        """Remove old backups exceeding max_backups"""
        if not self.current_file:
            return
            
        file_name = os.path.basename(self.current_file)
        backups = []
        
        # Get all backups for current file
        for backup in os.listdir(self.backup_dir):
            if backup.startswith(file_name) and backup.endswith('.bak'):
                backup_path = os.path.join(self.backup_dir, backup)
                backups.append((
                    backup_path,
                    os.path.getmtime(backup_path)
                ))
        
        # Sort by modification time (newest first)
        backups.sort(key=lambda x: x[1], reverse=True)
        
        # Remove excess backups
        for backup_path, _ in backups[self.max_backups:]:
            try:
                os.remove(backup_path)
            except Exception:
                pass

    def new_document(self):
        """Create a new document"""
        if self.maybe_save():
            self.editor.clear()
            self.current_file = None
            self.editor.document().setModified(False)
            self.clear_undo_stack()
            self.status_bar.showMessage("New document created")

    def maybe_save(self):
        """Check if document needs saving before closing"""
        if not self.editor.document().isModified():
            return True

        ret = QMessageBox.warning(
            self, "Application",
            "The document has been modified.\nDo you want to save your changes?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )

        if ret == QMessageBox.Save:
            return self.save_document()
        elif ret == QMessageBox.Cancel:
            return False
        return True

    def save_document(self):
        """Save the current document"""
        if not self.current_file:
            return self.save_document_as()
        return self.save_file(self.current_file)

    def save_document_as(self):
        """Save the current document with a new name"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Document", "",
            "Rich Text Files (*.rtf);;All Files (*.*)"
        )
        if file_name:
            return self.save_file(file_name)
        return False

    def open_document(self):
        """Open an existing document"""
        if self.maybe_save():
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Open Document", "",
                "Rich Text Files (*.rtf);;All Files (*.*)"
            )
            if file_name:
                self.load_file(file_name)

    def load_file(self, file_name):
        """Load a document from file"""
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                self.editor.setHtml(file.read())
            self.current_file = file_name
            self.editor.document().setModified(False)
            self.clear_undo_stack()
            self.status_bar.showMessage(f"Loaded {file_name}")
            
            # Add to recent files
            self.add_to_recent_files(file_name)
            return True
        except Exception as e:
            self.status_bar.showMessage(f"Failed to load {file_name}: {str(e)}")
            return False

    def print_document(self):
        """Print the current document"""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            self.editor.print_(printer)

    def print_preview(self):
        """Show print preview dialog"""
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: self.editor.print_(p))
        preview.exec_()

    def font_family_changed(self, font):
        """Handle font family change"""
        self.editor.setFontFamily(font.family())

    def font_size_changed(self, size):
        """Handle font size change"""
        self.editor.setFontPointSize(size)

    def closeEvent(self, event):
        """Handle window close event"""
        if self.maybe_save():
            # Save settings before closing
            self.save_recent_files()
            event.accept()
        else:
            event.ignore()

    def update_handle_positions(self, pos):
        """Update resize handle positions during image resize"""
        if hasattr(self, 'handle_rects'):
            cursor = self.editor.textCursor()
            image_format = cursor.charFormat().toImageFormat()
            if image_format.isValid():
                image_rect = self.editor.document().documentLayout().blockBoundingRect(cursor.block())
                handle_size = 8
                
                # Update handle positions based on new image size
                self.handle_rects['top-left'] = QRect(
                    image_rect.left() - handle_size//2,
                    image_rect.top() - handle_size//2,
                    handle_size, handle_size
                )
                self.handle_rects['top-right'] = QRect(
                    image_rect.right() - handle_size//2,
                    image_rect.top() - handle_size//2,
                    handle_size, handle_size
                )
                self.handle_rects['bottom-left'] = QRect(
                    image_rect.left() - handle_size//2,
                    image_rect.bottom() - handle_size//2,
                    handle_size, handle_size
                )
                self.handle_rects['bottom-right'] = QRect(
                    image_rect.right() - handle_size//2,
                    image_rect.bottom() - handle_size//2,
                    handle_size, handle_size
                )
                self.update()  # Redraw handles

    def apply_text_style(self, style_name):
        """Apply the selected text style"""
        cursor = self.editor.textCursor()
        block_format = QTextBlockFormat()
        char_format = QTextCharFormat()
        
        # Reset to base format
        char_format.setFontWeight(QFont.Normal)
        char_format.setFontPointSize(11)
        block_format.setAlignment(Qt.AlignLeft)
        
        # Apply style-specific formatting
        if style_name == "Normal":
            pass  # Use base format
        elif style_name.startswith("Heading"):
            level = int(style_name[-1])
            char_format.setFontWeight(QFont.Bold)
            char_format.setFontPointSize(18 - (level * 2))  # Size decreases with level
            block_format.setTopMargin(20)
            block_format.setBottomMargin(10)
        elif style_name == "Title":
            char_format.setFontWeight(QFont.Bold)
            char_format.setFontPointSize(24)
            block_format.setAlignment(Qt.AlignCenter)
            block_format.setTopMargin(30)
            block_format.setBottomMargin(20)
        elif style_name == "Subtitle":
            char_format.setFontWeight(QFont.Bold)
            char_format.setFontPointSize(18)
            char_format.setFontItalic(True)
            block_format.setAlignment(Qt.AlignCenter)
            block_format.setTopMargin(10)
            block_format.setBottomMargin(20)
        
        # Apply the formatting
        cursor.mergeBlockFormat(block_format)
        cursor.mergeCharFormat(char_format)
        self.editor.setCurrentCharFormat(char_format)

    def set_line_spacing(self, spacing):
        """Set line spacing for selected paragraphs"""
        cursor = self.editor.textCursor()
        block_format = cursor.blockFormat()
        block_format.setLineHeight(
            int(spacing * 100),
            QTextBlockFormat.ProportionalHeight
        )
        cursor.mergeBlockFormat(block_format)

    def set_paragraph_spacing(self, spacing):
        """Set spacing before and after paragraphs"""
        cursor = self.editor.textCursor()
        block_format = cursor.blockFormat()
        block_format.setTopMargin(spacing)
        block_format.setBottomMargin(spacing)
        cursor.mergeBlockFormat(block_format)

    def update_style_combo(self, cursor):
        """Update style combo box based on current paragraph style"""
        block_format = cursor.blockFormat()
        char_format = cursor.charFormat()
        
        # Determine current style based on formatting
        if char_format.fontPointSize() >= 24:
            self.style_combo.setCurrentText("Title")
        elif char_format.fontPointSize() >= 18 and char_format.fontItalic():
            self.style_combo.setCurrentText("Subtitle")
        elif char_format.fontWeight() >= QFont.Bold:
            size = char_format.fontPointSize()
            if size >= 16:
                self.style_combo.setCurrentText("Heading 1")
            elif size >= 14:
                self.style_combo.setCurrentText("Heading 2")
            elif size >= 12:
                self.style_combo.setCurrentText("Heading 3")
            elif size >= 11:
                self.style_combo.setCurrentText("Heading 4")
        else:
            self.style_combo.setCurrentText("Normal")

    def show_custom_line_spacing(self):
        """Show dialog for custom line spacing"""
        cursor = self.editor.textCursor()
        current_spacing = cursor.blockFormat().lineHeight() / 100
        if current_spacing == 0:
            current_spacing = 1.0
            
        dialog = CustomSpacingDialog(
            self, 
            spacing_type="line",
            current_value=current_spacing
        )
        
        if dialog.exec_() == QDialog.Accepted:
            self.set_line_spacing(dialog.get_value())

    def show_custom_paragraph_spacing(self):
        """Show dialog for custom paragraph spacing"""
        cursor = self.editor.textCursor()
        current_spacing = cursor.blockFormat().topMargin()
        
        dialog = CustomSpacingDialog(
            self, 
            spacing_type="paragraph",
            current_value=current_spacing
        )
        
        if dialog.exec_() == QDialog.Accepted:
            self.set_paragraph_spacing(dialog.get_value())

    def insert_table_template(self, rows, cols, template_name):
        """Insert a predefined table template"""
        cursor = self.editor.textCursor()
        table_format = QTextTableFormat()
        
        # Basic formatting
        table_format.setAlignment(Qt.AlignLeft)
        table_format.setBorder(1)
        table_format.setCellPadding(5)
        table_format.setCellSpacing(0)
        
        # Create table
        table = cursor.insertTable(rows, cols, table_format)
        
        # Apply template-specific formatting
        if template_name == "Header Row 3x3":
            # Format header row
            for col in range(cols):
                cell = table.cellAt(0, col)
                cursor = cell.firstCursorPosition()
                format = QTextCharFormat()
                format.setBackground(QColor("#e0e0e0"))
                format.setFontWeight(QFont.Bold)
                cursor.mergeCharFormat(format)
        
        elif template_name == "Calendar 7x5":
            # Format day headers
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for col, day in enumerate(days):
                cell = table.cellAt(0, col)
                cursor = cell.firstCursorPosition()
                cursor.insertText(day)
                format = QTextCharFormat()
                format.setBackground(QColor("#e0e0e0"))
                cursor.mergeCharFormat(format)
        
        elif template_name == "Contact Card 2x3":
            # Add labels
            labels = ["Name:", "Email:", "Phone:", "Address:", "Company:", "Notes:"]
            for row in range(2):
                for col in range(3):
                    cell = table.cellAt(row, col)
                    cursor = cell.firstCursorPosition()
                    cursor.insertText(labels[row * 3 + col])
                    format = QTextCharFormat()
                    format.setFontWeight(QFont.Bold)
                    cursor.mergeCharFormat(format)

    def insert_row_above(self):
        """Insert a new row above the current row"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            table.insertRows(cell.row(), 1)

    def insert_row_below(self):
        """Insert a new row below the current row"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            table.insertRows(cell.row() + 1, 1)

    def delete_row(self):
        """Delete the current row"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            table.removeRows(cell.row(), 1)

    def insert_column_left(self):
        """Insert a new column to the left"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            table.insertColumns(cell.column(), 1)

    def insert_column_right(self):
        """Insert a new column to the right"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            table.insertColumns(cell.column() + 1, 1)

    def delete_column(self):
        """Delete the current column"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table:
            cell = table.cellAt(cursor)
            table.removeColumns(cell.column(), 1)

    def apply_border_preset(self, preset):
        """Apply a border preset to the current table"""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if not table:
            return
            
        format = table.format()
        
        if preset == "none":
            format.setBorder(0)
        elif preset == "all":
            format.setBorder(1)
        elif preset == "outside":
            format.setBorder(1)
            format.setProperty(QTextFormat.TableCellSpacing, 0)
            # Set inner borders to 0 for all cells
            for row in range(table.rows()):
                for col in range(table.columns()):
                    cell = table.cellAt(row, col)
                    cell_format = cell.format()
                    cell_format.setProperty(QTextFormat.TableCellBorderStyle, Qt.NoPen)
                    cell.setFormat(cell_format)
        elif preset == "inside":
            format.setBorder(0)
            # Set inner borders for all cells
            for row in range(table.rows()):
                for col in range(table.columns()):
                    cell = table.cellAt(row, col)
                    cell_format = cell.format()
                    cell_format.setProperty(QTextFormat.TableCellBorderStyle, Qt.SolidLine)
                    cell_format.setProperty(QTextFormat.TableCellBorderWidth, 1)
                    cell.setFormat(cell_format)
        
        table.setFormat(format)

    def toggle_format_painter(self, checked):
        if checked:
            cursor = self.editor.textCursor()
            self.copied_format = {
                'char': cursor.charFormat(),
                'block': cursor.blockFormat()
            }
            self.editor.viewport().setCursor(Qt.CrossCursor)
        else:
            self.copied_format = None
            self.editor.viewport().setCursor(Qt.IBeamCursor)

    def mousePressEvent(self, event):
        if self.format_painter.isChecked() and self.copied_format:
            cursor = self.editor.cursorForPosition(event.pos())
            if event.modifiers() & Qt.ShiftModifier:
                # Apply to whole paragraph
                cursor.movePosition(QTextCursor.StartOfBlock)
                cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
            else:
                # Apply to word
                cursor.select(QTextCursor.WordUnderCursor)
            
            cursor.mergeCharFormat(self.copied_format['char'])
            cursor.mergeBlockFormat(self.copied_format['block'])
            
            # Turn off format painter unless Ctrl is held
            if not (event.modifiers() & Qt.ControlModifier):
                self.format_painter.setChecked(False)
                self.copied_format = None
                self.editor.viewport().setCursor(Qt.IBeamCursor)
        else:
            super().mousePressEvent(event)

class TableDialog(QDialog):
    """Dialog for table insertion"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Insert Table")
        layout = QVBoxLayout(self)

        # Rows and columns
        form_layout = QFormLayout()
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(1, 50)
        self.rows_spin.setValue(3)
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 50)
        self.cols_spin.setValue(3)

        form_layout.addRow("Rows:", self.rows_spin)
        form_layout.addRow("Columns:", self.cols_spin)
        layout.addLayout(form_layout)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_format(self):
        """Get the table format settings"""
        return {
            'border_width': self.border_width.value(),
            'border_style': self.border_style.currentData(),  # Returns Qt.PenStyle
            'border_color': self.border_color_button.color,
            'padding': self.cell_padding.value(),
            'spacing': self.cell_spacing.value(),
            'width': self.table_width.value(),
            'background_color': self.background_color_button.color if self.background_color_button.color else None
        }

class TableFormatDialog(QDialog):
    """Dialog for table formatting"""
    def __init__(self, parent=None, table=None):
        super().__init__(parent)
        self.table = table
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Format Table")
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Border width
        self.border_width = QSpinBox()
        self.border_width.setRange(0, 10)
        self.border_width.setValue(1)
        form_layout.addRow("Border Width:", self.border_width)

        # Border color
        self.border_color = QPushButton("Choose Color")
        self.border_color.clicked.connect(self.choose_border_color)
        self.border_color_value = "#000000"
        form_layout.addRow("Border Color:", self.border_color)

        # Background color
        self.bg_color = QPushButton("Choose Color")
        self.bg_color.clicked.connect(self.choose_bg_color)
        self.bg_color_value = "#ffffff"
        form_layout.addRow("Background:", self.bg_color)

        # Padding and spacing
        self.padding = QSpinBox()
        self.padding.setRange(0, 50)
        self.padding.setValue(5)
        form_layout.addRow("Cell Padding:", self.padding)

        self.spacing = QSpinBox()
        self.spacing.setRange(0, 50)
        self.spacing.setValue(0)
        form_layout.addRow("Cell Spacing:", self.spacing)

        layout.addLayout(form_layout)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def choose_border_color(self):
        color = QColorDialog.getColor(QColor(self.border_color_value), self)
        if color.isValid():
            self.border_color_value = color.name()
            self.border_color.setStyleSheet(f"background-color: {color.name()}")

    def choose_bg_color(self):
        color = QColorDialog.getColor(QColor(self.bg_color_value), self)
        if color.isValid():
            self.bg_color_value = color.name()
            self.bg_color.setStyleSheet(f"background-color: {color.name()}")

    def get_format(self):
        return {
            'border_width': self.border_width.value(),
            'border_style': Qt.SolidLine,
            'border_color': self.border_color_value,
            'background_color': self.bg_color_value,
            'padding': self.padding.value(),
            'spacing': self.spacing.value(),
            'alignment': Qt.AlignLeft
        }

class ImageResizeDialog(QDialog):
    """Dialog for image resizing"""
    def __init__(self, parent=None, image_format=None):
        super().__init__(parent)
        self.image_format = image_format
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Resize Image")
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Width
        self.width = QSpinBox()
        self.width.setRange(1, 2000)
        # Convert float to int for width
        self.width.setValue(int(self.image_format.width()))
        form_layout.addRow("Width:", self.width)

        # Height
        self.height = QSpinBox()
        self.height.setRange(1, 2000)
        # Convert float to int for height
        self.height.setValue(int(self.image_format.height()))
        form_layout.addRow("Height:", self.height)

        # Maintain aspect ratio
        self.aspect_ratio = QCheckBox("Maintain Aspect Ratio")
        self.aspect_ratio.setChecked(True)
        form_layout.addRow(self.aspect_ratio)

        layout.addLayout(form_layout)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        # Connect signals
        self.width.valueChanged.connect(self.width_changed)
        self.height.valueChanged.connect(self.height_changed)

    def width_changed(self, value):
        if self.aspect_ratio.isChecked():
            ratio = self.image_format.height() / self.image_format.width()
            self.height.setValue(int(value * ratio))

    def height_changed(self, value):
        if self.aspect_ratio.isChecked():
            ratio = self.image_format.width() / self.image_format.height()
            self.width.setValue(int(value * ratio))

    def get_format(self):
        return {
            'width': self.width.value(),
            'height': self.height.value()
        }

class TableCellFormatDialog(QDialog):
    """Dialog for cell formatting"""
    def __init__(self, parent=None, cell=None):
        super().__init__(parent)
        self.cell = cell
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Format Cell")
        layout = QVBoxLayout(self)
        
        # Create tab widget for better organization
        tab_widget = QTabWidget()
        
        # Background tab
        background_tab = QWidget()
        bg_layout = QFormLayout()
        
        # Background color with preview
        self.bg_color = QPushButton()
        self.bg_color.setFixedSize(80, 30)
        self.bg_color.clicked.connect(self.choose_bg_color)
        self.bg_color_value = "#ffffff"
        self.bg_color.setStyleSheet(f"background-color: {self.bg_color_value}")
        bg_layout.addRow("Background Color:", self.bg_color)
        
        background_tab.setLayout(bg_layout)
        
        # Borders tab
        borders_tab = QWidget()
        borders_layout = QVBoxLayout()
        
        # Border settings
        self.border_group = QGroupBox("Border Settings")
        border_layout = QGridLayout()
        
        # Border width for each side
        self.borders = {}
        for position in ['top', 'bottom', 'left', 'right']:
            group = QGroupBox(position.capitalize())
            group_layout = QVBoxLayout()
            
            # Width spinner
            width_spin = QSpinBox()
            width_spin.setRange(0, 10)
            group_layout.addWidget(QLabel("Width:"))
            group_layout.addWidget(width_spin)
            
            # Style combo
            style_combo = QComboBox()
            style_combo.addItems(['Solid', 'Dashed', 'Dotted'])
            group_layout.addWidget(QLabel("Style:"))
            group_layout.addWidget(style_combo)
            
            # Color button
            color_btn = QPushButton()
            color_btn.setFixedSize(60, 20)
            color_btn.setStyleSheet("background-color: black")
            group_layout.addWidget(QLabel("Color:"))
            group_layout.addWidget(color_btn)
            
            group.setLayout(group_layout)
            self.borders[position] = {
                'width': width_spin,
                'style': style_combo,
                'color': color_btn,
                'color_value': "#000000"
            }
            
            # Connect color button
            color_btn.clicked.connect(
                lambda checked, pos=position: self.choose_border_color(pos)
            )
            
        # Add border groups to layout
        border_layout.addWidget(self.borders['top']['group'], 0, 1)
        border_layout.addWidget(self.borders['left']['group'], 1, 0)
        border_layout.addWidget(self.borders['right']['group'], 1, 2)
        border_layout.addWidget(self.borders['bottom']['group'], 2, 1)
        
        self.border_group.setLayout(border_layout)
        borders_layout.addWidget(self.border_group)
        borders_tab.setLayout(borders_layout)
        
        # Alignment tab
        alignment_tab = QWidget()
        alignment_layout = QVBoxLayout()
        
        # Horizontal alignment
        h_group = QGroupBox("Horizontal Alignment")
        h_layout = QHBoxLayout()
        self.h_align_group = QButtonGroup()
        
        for align, text in [
            (Qt.AlignLeft, "Left"),
            (Qt.AlignHCenter, "Center"),
            (Qt.AlignRight, "Right"),
            (Qt.AlignJustify, "Justify")
        ]:
            btn = QRadioButton(text)
            self.h_align_group.addButton(btn, align)
            h_layout.addWidget(btn)
        h_group.setLayout(h_layout)
        
        # Vertical alignment
        v_group = QGroupBox("Vertical Alignment")
        v_layout = QHBoxLayout()
        self.v_align_group = QButtonGroup()
        
        for align, text in [
            (Qt.AlignTop, "Top"),
            (Qt.AlignVCenter, "Middle"),
            (Qt.AlignBottom, "Bottom")
        ]:
            btn = QRadioButton(text)
            self.v_align_group.addButton(btn, align)
            v_layout.addWidget(btn)
        v_group.setLayout(v_layout)
        
        alignment_layout.addWidget(h_group)
        alignment_layout.addWidget(v_group)
        alignment_tab.setLayout(alignment_layout)
        
        # Add tabs
        tab_widget.addTab(background_tab, "Background")
        tab_widget.addTab(borders_tab, "Borders")
        tab_widget.addTab(alignment_tab, "Alignment")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def choose_border_color(self, position):
        color = QColorDialog.getColor(
            QColor(self.borders[position]['color_value']), 
            self
        )
        if color.isValid():
            self.borders[position]['color_value'] = color.name()
            self.borders[position]['color'].setStyleSheet(
                f"background-color: {color.name()}"
            )

    def get_format(self):
        return {
            'background_color': self.bg_color_value,
            'borders': {
                pos: {
                    'width': data['width'].value(),
                    'style': self.get_border_style(data['style'].currentText()),
                    'color': data['color_value']
                }
                for pos, data in self.borders.items()
            },
            'h_alignment': self.h_align_group.checkedId(),
            'v_alignment': self.v_align_group.checkedId()
        }

    def get_border_style(self, style_text):
        return {
            'Solid': Qt.SolidLine,
            'Dashed': Qt.DashLine,
            'Dotted': Qt.DotLine
        }.get(style_text, Qt.SolidLine)

    def choose_bg_color(self):
        color = QColorDialog.getColor(QColor(self.bg_color_value), self)
        if color.isValid():
            self.bg_color_value = color.name()
            self.bg_color.setStyleSheet(f"background-color: {color.name()}")

class AutoSaveSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        self.setWindowTitle("Auto-Save Settings")
        layout = QVBoxLayout(self)

        # Enable auto-save
        self.auto_save_enabled = QCheckBox("Enable Auto-Save")
        layout.addWidget(self.auto_save_enabled)

        # Interval settings
        interval_group = QGroupBox("Auto-Save Interval")
        interval_layout = QHBoxLayout()
        
        self.interval_value = QSpinBox()
        self.interval_value.setRange(1, 60)
        self.interval_unit = QComboBox()
        self.interval_unit.addItems(["Minutes", "Hours"])
        
        interval_layout.addWidget(self.interval_value)
        interval_layout.addWidget(self.interval_unit)
        interval_group.setLayout(interval_layout)
        layout.addWidget(interval_group)

        # Backup settings
        backup_group = QGroupBox("Backup Settings")
        backup_layout = QFormLayout()
        
        self.backup_enabled = QCheckBox("Enable Backups")
        self.compress_backups = QCheckBox("Compress Backup Files")
        self.max_backups_spin = QSpinBox()
        self.max_backups_spin.setRange(1, 100)
        
        backup_layout.addRow(self.backup_enabled)
        backup_layout.addRow(self.compress_backups)
        backup_layout.addRow("Maximum backups:", self.max_backups_spin)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def load_settings(self):
        settings = QSettings('YourCompany', 'YourApp')
        
        # Auto-save settings
        self.auto_save_enabled.setChecked(
            settings.value('auto_save/enabled', True, bool)
        )
        interval_minutes = settings.value('auto_save/interval', 5, int)
        
        if interval_minutes >= 60:
            self.interval_value.setValue(interval_minutes // 60)
            self.interval_unit.setCurrentText("Hours")
        else:
            self.interval_value.setValue(interval_minutes)
            self.interval_unit.setCurrentText("Minutes")
        
        # Backup settings
        self.backup_enabled.setChecked(
            settings.value('backup/enabled', True, bool)
        )
        self.compress_backups.setChecked(
            settings.value('backup/compress', True, bool)
        )
        self.max_backups_spin.setValue(
            settings.value('backup/max_backups', 5, int)
        )

    def save_settings(self):
        settings = QSettings('YourCompany', 'YourApp')
        
        # Save auto-save settings
        settings.setValue('auto_save/enabled', self.auto_save_enabled.isChecked())
        
        interval = self.interval_value.value()
        if self.interval_unit.currentText() == "Hours":
            interval *= 60
        settings.setValue('auto_save/interval', interval)
        
        # Save backup settings
        settings.setValue('backup/enabled', self.backup_enabled.isChecked())
        settings.setValue('backup/compress', self.compress_backups.isChecked())
        settings.setValue('backup/max_backups', self.max_backups_spin.value())
        
        # Update parent settings
        if self.parent:
            self.parent.apply_auto_save_settings()
            self.parent.backup_enabled = self.backup_enabled.isChecked()
            self.parent.max_backups = self.max_backups_spin.value()
        
        self.accept()

class CustomSpacingDialog(QDialog):
    """Dialog for custom spacing settings"""
    def __init__(self, parent=None, spacing_type="line", current_value=1.0):
        super().__init__(parent)
        self.spacing_type = spacing_type
        self.current_value = current_value
        self.setup_ui()

    def setup_ui(self):
        title = "Line Spacing" if self.spacing_type == "line" else "Paragraph Spacing"
        self.setWindowTitle(f"Custom {title}")
        layout = QVBoxLayout(self)

        # Spacing value input
        form_layout = QFormLayout()
        
        if self.spacing_type == "line":
            self.spacing_value = QDoubleSpinBox()
            self.spacing_value.setRange(0.5, 5.0)
            self.spacing_value.setSingleStep(0.1)
            self.spacing_value.setValue(float(self.current_value))  # Convert to float
            self.spacing_value.setDecimals(2)
            label = "Line spacing:"
            unit = "lines"
        else:
            self.spacing_value = QSpinBox()
            self.spacing_value.setRange(0, 100)
            self.spacing_value.setSingleStep(1)
            self.spacing_value.setValue(int(self.current_value))  # Convert to int
            label = "Spacing:"
            unit = "points"

        # Create a horizontal layout for the input and unit label
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.spacing_value)
        input_layout.addWidget(QLabel(unit))
        
        form_layout.addRow(label, input_layout)
        layout.addLayout(form_layout)

        # Preview text
        if self.spacing_type == "line":
            preview = QTextEdit()
            preview.setReadOnly(True)
            preview.setMaximumHeight(100)
            preview.setText("This is a preview of the line spacing.\nYou can see how it looks here.\nAdjust the value to change spacing.")
            
            # Update preview when value changes
            self.spacing_value.valueChanged.connect(
                lambda v: self.update_preview(preview, v)
            )
            
            layout.addWidget(QLabel("Preview:"))
            layout.addWidget(preview)
            
            # Initial preview update
            self.update_preview(preview, self.current_value)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def update_preview(self, preview, value):
        """Update the preview text with current spacing"""
        cursor = preview.textCursor()
        block_format = QTextBlockFormat()
        block_format.setLineHeight(
            int(value * 100),
            QTextBlockFormat.ProportionalHeight
        )
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(block_format)

    def get_value(self):
        """Get the selected spacing value"""
        return self.spacing_value.value()

class DocumentRuler(QWidget):
    def __init__(self, orientation=Qt.Horizontal, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.scale = 1.0  # For zoom support
        self.margin = 20  # Document margin
        
        # Set fixed size based on orientation
        if orientation == Qt.Horizontal:
            self.setFixedHeight(20)
        else:
            self.setFixedWidth(20)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor("#f0f0f0"))
        
        # Draw ruler markings
        if self.orientation == Qt.Horizontal:
            self.draw_horizontal_ruler(painter)
        else:
            self.draw_vertical_ruler(painter)

    def draw_horizontal_ruler(self, painter):
        width = self.width()
        # Convert pixels to centimeters (assuming 96 DPI)
        pixels_per_cm = 96 / 2.54 * self.scale
        
        for pixel in range(self.margin, width, int(pixels_per_cm / 2)):
            if (pixel - self.margin) % int(pixels_per_cm) == 0:
                # Draw centimeter mark
                painter.drawLine(pixel, 15, pixel, self.height())
                # Draw number
                cm = (pixel - self.margin) / pixels_per_cm
                painter.drawText(pixel - 10, 0, 20, 15, Qt.AlignCenter, str(int(cm)))
            else:
                # Draw millimeter mark
                painter.drawLine(pixel, 18, pixel, self.height())

    def draw_vertical_ruler(self, painter):
        height = self.height()
        pixels_per_cm = 96 / 2.54 * self.scale
        
        for pixel in range(self.margin, height, int(pixels_per_cm / 2)):
            if (pixel - self.margin) % int(pixels_per_cm) == 0:
                painter.drawLine(15, pixel, self.width(), pixel)
                cm = (pixel - self.margin) / pixels_per_cm
                painter.save()
                painter.translate(0, pixel)
                painter.rotate(-90)
                painter.drawText(-15, 0, 15, 15, Qt.AlignCenter, str(int(cm)))
                painter.restore()
            else:
                painter.drawLine(18, pixel, self.width(), pixel)

    def set_scale(self, scale):
        self.scale = scale
        self.update()

class DocumentMap(QWidget):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setFixedWidth(150)
        
        layout = QVBoxLayout(self)
        
        # Create tree view for document structure
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Document Map")
        self.tree.itemClicked.connect(self.navigate_to_section)
        
        layout.addWidget(self.tree)
        
        # Update map when document changes
        self.editor.document().contentsChanged.connect(self.update_map)
        
    def update_map(self):
        self.tree.clear()
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        
        current_item = None
        while not cursor.atEnd():
            block = cursor.block()
            format = block.charFormat()
            
            # Check if block is a heading
            if format.fontWeight() == QFont.Bold and format.fontPointSize() > 11:
                level = self.get_heading_level(format.fontPointSize())
                text = block.text()
                
                item = QTreeWidgetItem([text])
                item.setData(0, Qt.UserRole, block.position())
                
                if level == 1 or current_item is None:
                    self.tree.addTopLevelItem(item)
                    current_item = item
                else:
                    current_item.addChild(item)
            
            cursor.movePosition(QTextCursor.NextBlock)
            
    def get_heading_level(self, size):
        if size >= 24:  # Title
            return 1
        elif size >= 18:  # Heading 1
            return 2
        elif size >= 14:  # Heading 2
            return 3
        else:  # Heading 3 or 4
            return 4
            
    def navigate_to_section(self, item):
        position = item.data(0, Qt.UserRole)
        cursor = self.editor.textCursor()
        cursor.setPosition(position)
        self.editor.setTextCursor(cursor)
        self.editor.ensureCursorVisible()

class StyleInspector(QDockWidget):
    def __init__(self, editor, parent=None):
        super().__init__("Style Inspector", parent)
        self.editor = editor
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Create properties view
        self.properties = QTreeWidget()
        self.properties.setHeaderLabels(["Property", "Value"])
        self.properties.setAlternatingRowColors(True)
        
        layout.addWidget(self.properties)
        self.setWidget(widget)
        
        # Update when cursor position changes
        self.editor.cursorPositionChanged.connect(self.update_properties)
        
    def update_properties(self):
        self.properties.clear()
        cursor = self.editor.textCursor()
        char_format = cursor.charFormat()
        block_format = cursor.blockFormat()
        
        # Character formatting
        char_root = QTreeWidgetItem(["Character Format"])
        self.properties.addTopLevelItem(char_root)
        
        self.add_property(char_root, "Font", char_format.font().family())
        self.add_property(char_root, "Size", f"{char_format.font().pointSize()}pt")
        self.add_property(char_root, "Weight", self.get_weight_name(char_format.font().weight()))
        self.add_property(char_root, "Color", char_format.foreground().color().name())
        
        # Paragraph formatting
        para_root = QTreeWidgetItem(["Paragraph Format"])
        self.properties.addTopLevelItem(para_root)
        
        self.add_property(para_root, "Alignment", self.get_alignment_name(block_format.alignment()))
        self.add_property(para_root, "Line Height", f"{block_format.lineHeight()}%")
        self.add_property(para_root, "Top Margin", f"{block_format.topMargin()}pt")
        self.add_property(para_root, "Bottom Margin", f"{block_format.bottomMargin()}pt")
        
    def add_property(self, parent, name, value):
        QTreeWidgetItem(parent, [name, str(value)])
        
    def get_weight_name(self, weight):
        weights = {
            QFont.Light: "Light",
            QFont.Normal: "Normal",
            QFont.DemiBold: "DemiBold",
            QFont.Bold: "Bold",
            QFont.Black: "Black"
        }
        return weights.get(weight, "Normal")
        
    def get_alignment_name(self, alignment):
        alignments = {
            Qt.AlignLeft: "Left",
            Qt.AlignRight: "Right",
            Qt.AlignCenter: "Center",
            Qt.AlignJustify: "Justify"
        }
        return alignments.get(alignment, "Left")

# TODO List:

# 1. Ruler Implementation
# - Add horizontal and vertical rulers to the editor
# - Implement ruler guides/snap functionality
# - Add ruler margin markers
# - Add support for different measurement units (inches, pixels)
# - Add zoom synchronization with rulers

# 2. Document Map/Navigation
# - Add collapsible section support
# - Implement search within document map
# - Add thumbnail preview for sections
# - Add drag-and-drop section reordering
# - Add section level customization
# - Add automatic section numbering

# 3. Style Inspector
# - Add more detailed formatting information
# - Add direct property editing in inspector
# - Add style inheritance visualization
# - Add style copying from inspector
# - Add custom property views
# - Add style comparison between selections

# 4. Format Painter
# - Add multiple format storage
# - Add format painter presets
# - Add selective format painting (only specific attributes)
# - Add format painter history
# - Add format painter preview
# - Add keyboard shortcuts for format painter operations

# 5. General Improvements
# - Add undo/redo for all operations
# - Improve performance for large documents
# - Add better error handling and user feedback
# - Add accessibility features
# - Add keyboard navigation for all features
# - Add configuration options for all features

# 6. Table Enhancements
# - Add table styles presets
# - Add cell merging/splitting improvements
# - Add table sorting capabilities
# - Add automatic row/column sizing
# - Add table conversion (table to text, text to table)
# - Add table templates management

# 7. Document Features
# - Add document sections
# - Add headers and footers
# - Add page numbering
# - Add footnotes and endnotes
# - Add table of contents generation
# - Add index generation

# 8. UI Improvements
# - Add customizable toolbars
# - Add dark mode support
# - Add status bar customization
# - Add context menus for all elements
# - Add toolbar configuration
# - Add dockable panels

# 9. File Operations
# - Add auto-recovery improvements
# - Add version control integration
# - Add cloud storage support
# - Add file comparison tools
# - Add batch processing capabilities
# - Add document statistics

# 10. Advanced Features
# - Add macro recording/playback
# - Add find/replace improvements
# - Add spell check/grammar check
# - Add language support
# - Add document collaboration features
# - Add document encryption

# Priority Levels:
# [HIGH] - Essential features needed for basic functionality
# [MEDIUM] - Important features for user experience
# [LOW] - Nice-to-have features for advanced users

# Next Steps:
# 1. Implement ruler system [HIGH]
# 2. Complete document map functionality [HIGH]
# 3. Enhance style inspector capabilities [MEDIUM]
# 4. Improve format painter functionality [MEDIUM]
# 5. Add basic table enhancements [HIGH]
