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
                        QTransform, QPen, QPixmap, QIcon, QTextDocument)
from PyQt5.QtCore import (Qt, QSizeF, QRect, QSize, QTimer, QSettings, 
                         QRegularExpression)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

import os
import math
from datetime import datetime
from zlib import compress, decompress

# Change to absolute imports
from core.document_editor.style_inspector import StyleInspector
from core.document_editor.image_handler import ImageHandler
from core.document_editor.table_handler import TableHandler
from core.document_editor.format_handler import FormatHandler

class DocumentEditor(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize handlers
        self.image_handler = ImageHandler(self)
        self.table_handler = TableHandler(self)
        self.format_handler = FormatHandler(self)
        
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
        self.setup_connections()
        
        # Finally, setup features that depend on UI elements
        self.setup_auto_save()
        self.load_recent_files()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        
        # Create toolbars
        self.main_toolbar = QToolBar()
        self.format_toolbar = QToolBar()
        self.insert_toolbar = QToolBar()
        
        # Create editor first
        self.editor = QTextEdit()
        
        # Create status bar
        self.status_bar = QStatusBar()
        
        # Now setup toolbars after editor is created
        self.setup_file_toolbar()
        
        # Initialize handlers
        self.format_handler = FormatHandler(self)
        self.table_handler = TableHandler(self)
        self.image_handler = ImageHandler(self)
        
        # Get format actions and widgets
        format_items = self.format_handler.setup_format_actions()
        
        # Store references to frequently used widgets
        self.font_family = format_items['font_family']
        self.font_size = format_items['font_size']
        self.format_painter = format_items['format_painter']
        
        # Add format items to toolbar
        self.format_toolbar.addWidget(self.font_family)
        self.format_toolbar.addWidget(self.font_size)
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(format_items['bold'])
        self.format_toolbar.addAction(format_items['italic'])
        self.format_toolbar.addAction(format_items['underline'])
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(format_items['align_left'])
        self.format_toolbar.addAction(format_items['align_center'])
        self.format_toolbar.addAction(format_items['align_right'])
        self.format_toolbar.addAction(format_items['align_justify'])
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(format_items['text_color'])
        self.format_toolbar.addAction(format_items['highlight'])
        self.format_toolbar.addWidget(format_items['style_combo'])
        self.format_toolbar.addAction(self.format_painter)
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(format_items['bullet_list'])
        self.format_toolbar.addAction(format_items['numbered_list'])
        
        # Add table and image buttons
        self.insert_toolbar.addWidget(self.table_handler.setup_table_actions())
        self.insert_toolbar.addWidget(self.image_handler.setup_image_actions())
        
        # Add to layout
        self.layout.addWidget(self.main_toolbar)
        self.layout.addWidget(self.format_toolbar)
        self.layout.addWidget(self.insert_toolbar)
        self.layout.addWidget(self.editor)
        self.layout.addWidget(self.status_bar)
        
        self.setLayout(self.layout)

    def setup_connections(self):
        """Setup signal connections"""
        # Document change connections
        self.editor.document().contentsChanged.connect(self.text_changed)
        self.editor.cursorPositionChanged.connect(self.cursor_position_changed)
        
        # Add undo/redo connections
        document = self.editor.document()
        document.undoAvailable.connect(self.undo_action.setEnabled)
        document.redoAvailable.connect(self.redo_action.setEnabled)
        
        # Clear undo stack when loading new document
        document.clearUndoRedoStacks()

    def text_changed(self):
        """Handle text content changes"""
        # Update document modified state
        document = self.editor.document()
        document.setModified(True)
        
        # Update window title to show modified state
        window_title = self.window().windowTitle()
        if not window_title.startswith('*'):
            self.window().setWindowTitle(f'*{window_title}')
        
        # Trigger auto-save if enabled
        if hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.start()
        
        # Update status bar
        word_count = len(self.editor.toPlainText().split())
        char_count = len(self.editor.toPlainText())
        self.status_bar.showMessage(f'Words: {word_count} | Characters: {char_count}')

    def cursor_position_changed(self):
        """Handle cursor position changes"""
        cursor = self.editor.textCursor()
        
        # Update format toolbar states
        if hasattr(self, 'format_handler'):
            # Get current character format
            char_format = cursor.charFormat()
            
            # Update font family combo
            font = char_format.font()
            self.font_family.setCurrentFont(font)
            
            # Update font size spinner
            size = char_format.fontPointSize()
            if size > 0:
                self.font_size.setValue(int(size))
        
        # Update status bar position info
        block = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.status_bar.showMessage(f'Line: {block} | Column: {col}')

    def setup_auto_save(self):
        """Setup auto-save functionality"""
        self.auto_save_timer = QTimer(self)  # Make timer a child of editor
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.setInterval(self.auto_save_interval)
        self.auto_save_timer.start()

    def _auto_save(self):
        """Auto-save current document"""
        if self.current_file and self.editor.document().isModified():
            try:
                self.save_document_as(self.current_file)
                self.editor.document().setModified(False)  # Reset modified state
                print(f"Auto-saved to {self.current_file}")  # Debug info
            except Exception as e:
                print(f"Auto-save failed: {str(e)}")

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
        if not hasattr(self, 'recent_files'):
            self.recent_files = []
        
        # Remove if already exists
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        # Add to start of list
        self.recent_files.insert(0, file_path)
        
        # Keep only last 10 files
        while len(self.recent_files) > self.max_recent_files:
            self.recent_files.pop()
        
        # Update menu if it exists
        if hasattr(self, 'update_recent_files_menu'):
            self.update_recent_files_menu()

    def update_recent_files_menu(self):
        """Update the recent files menu"""
        if hasattr(self, 'recent_files_menu'):
            self.recent_files_menu.clear()
            
            for file_path in self.recent_files:
                if os.path.exists(file_path):
                    action = QAction(os.path.basename(file_path), self)
                    action.setData(file_path)
                    action.setStatusTip(file_path)
                    action.triggered.connect(
                        lambda checked, f=file_path: self.load_document(f))
                    self.recent_files_menu.addAction(action)

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
            self.auto_save_timer.setInterval(self.auto_save_interval)
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

    def resize_selected_image(self):
        """Show resize dialog for selected image"""
        cursor = self.editor.textCursor()
        if cursor.charFormat().isImageFormat():
            self.show_image_properties(cursor)

    def toggle_resize_handles(self, checked):
        """Toggle visibility of image resize handles"""
        self.resize_handles_visible = checked
        if not checked:
            self.clear_resize_handles()
        else:
            self.update_resize_handles()
        self.editor.viewport().update()

    def update_resize_handles(self):
        """Update resize handles for all images in the document"""
        if not self.resize_handles_visible:
            return
            
        self.handle_rects = {}
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        
        while not cursor.atEnd():
            format = cursor.charFormat()
            if format.isImageFormat():
                image_format = format.toImageFormat()
                rect = self.editor.document().documentLayout().blockBoundingRect(cursor.block())
                pos = rect.topLeft()
                size = QSizeF(image_format.width(), image_format.height())
                
                # Create handle rectangles
                handle_size = 8
                handles = {
                    'top-left': QRectF(pos.x(), pos.y(), handle_size, handle_size),
                    'top-right': QRectF(pos.x() + size.width() - handle_size, pos.y(), handle_size, handle_size),
                    'bottom-left': QRectF(pos.x(), pos.y() + size.height() - handle_size, handle_size, handle_size),
                    'bottom-right': QRectF(pos.x() + size.width() - handle_size, pos.y() + size.height() - handle_size, handle_size, handle_size)
                }
                self.handle_rects[cursor.position()] = handles
                
            cursor.movePosition(QTextCursor.NextCharacter)

    def clear_resize_handles(self):
        """Clear all resize handles"""
        self.handle_rects = {}
        self.current_handle = None
        self.editor.viewport().update()

    def mousePressEvent(self, event):
        """Handle mouse press for resize handles"""
        if self.resize_handles_visible:
            pos = event.pos()
            for position, handles in self.handle_rects.items():
                for handle_pos, rect in handles.items():
                    if rect.contains(pos):
                        self.current_handle = (position, handle_pos)
                        return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for image resizing"""
        if self.current_handle:
            position, handle_pos = self.current_handle
            cursor = self.editor.textCursor()
            cursor.setPosition(position)
            
            if cursor.charFormat().isImageFormat():
                image_format = cursor.charFormat().toImageFormat()
                rect = self.editor.document().documentLayout().blockBoundingRect(cursor.block())
                delta = event.pos() - rect.topLeft()
                
                # Calculate new size based on handle position and mouse movement
                new_width = image_format.width()
                new_height = image_format.height()
                
                if 'right' in handle_pos:
                    new_width = max(10, delta.x())
                if 'bottom' in handle_pos:
                    new_height = max(10, delta.y())
                    
                # Update image size
                new_format = QTextImageFormat()
                new_format.setName(image_format.name())
                new_format.setWidth(new_width)
                new_format.setHeight(new_height)
                cursor.mergeCharFormat(new_format)
                
                self.update_resize_handles()
                
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release for resize handles"""
        self.current_handle = None
        super().mouseReleaseEvent(event)

    def editor_drag_enter_event(self, event):
        """Delegate drag enter events to image handler"""
        self.image_handler.handle_drag_enter(event)

    def editor_drop_event(self, event):
        """Delegate drop events to image handler"""
        self.image_handler.handle_drop(event)

    def insert_image_at_position(self, file_path, pos):
        """Insert image at the specified position"""
        cursor = self.editor.cursorForPosition(pos)
        image = QImage(file_path)
        if not image.isNull():
            image_format = QTextImageFormat()
            image_format.setName(file_path)
            
            # Set reasonable default size
            max_width = 800
            if image.width() > max_width:
                image = image.scaledToWidth(max_width, Qt.SmoothTransformation)
            
            image_format.setWidth(image.width())
            image_format.setHeight(image.height())
            
            # Store original size and rotation
            image_format.setProperty(1, image.width())
            image_format.setProperty(2, image.height())
            image_format.setProperty(3, 0)  # Rotation angle
            
            cursor.insertImage(image_format)

    def rotate_image(self, angle):
        """Rotate the selected image"""
        cursor = self.editor.textCursor()
        if cursor.charFormat().isImageFormat():
            image_format = cursor.charFormat().toImageFormat()
            file_path = image_format.name()
            
            # Load and rotate image
            image = QImage(file_path)
            transform = QTransform().rotate(angle)
            rotated = image.transformed(transform, Qt.SmoothTransformation)
            
            # Save rotated image
            temp_path = f"{file_path}_rotated.png"
            rotated.save(temp_path)
            
            # Update format
            new_format = QTextImageFormat()
            new_format.setName(temp_path)
            new_format.setWidth(rotated.width())
            new_format.setHeight(rotated.height())
            
            # Update rotation property
            current_rotation = image_format.property(3) or 0
            new_rotation = (current_rotation + angle) % 360
            new_format.setProperty(3, new_rotation)
            
            cursor.mergeCharFormat(new_format)

    def flip_image_horizontal(self):
        """Flip image horizontally"""
        self._flip_image(True, False)

    def flip_image_vertical(self):
        """Flip image vertically"""
        self._flip_image(False, True)

    def _flip_image(self, horizontal, vertical):
        """Internal method to flip image"""
        cursor = self.editor.textCursor()
        if cursor.charFormat().isImageFormat():
            image_format = cursor.charFormat().toImageFormat()
            file_path = image_format.name()
            
            image = QImage(file_path)
            flipped = image.mirrored(horizontal, vertical)
            
            temp_path = f"{file_path}_flipped.png"
            flipped.save(temp_path)
            
            new_format = QTextImageFormat()
            new_format.setName(temp_path)
            new_format.setWidth(flipped.width())
            new_format.setHeight(flipped.height())
            
            cursor.mergeCharFormat(new_format)

    def add_image_border(self):
        """Add border to image"""
        cursor = self.editor.textCursor()
        if cursor.charFormat().isImageFormat():
            dialog = ImageBorderDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                border_settings = dialog.get_border_settings()
                self.apply_image_border(cursor, border_settings)

    def apply_image_border(self, cursor, settings):
        """Apply border to image"""
        image_format = cursor.charFormat().toImageFormat()
        file_path = image_format.name()
        
        image = QImage(file_path)
        
        # Create new image with border
        bordered = QImage(
            image.width() + 2 * settings['width'],
            image.height() + 2 * settings['width'],
            QImage.Format_ARGB32
        )
        bordered.fill(settings['color'])
        
        # Draw original image in center
        painter = QPainter(bordered)
        painter.drawImage(settings['width'], settings['width'], image)
        painter.end()
        
        # Save and update
        temp_path = f"{file_path}_bordered.png"
        bordered.save(temp_path)
        
        new_format = QTextImageFormat()
        new_format.setName(temp_path)
        new_format.setWidth(bordered.width())
        new_format.setHeight(bordered.height())
        
        cursor.mergeCharFormat(new_format)

    def crop_image(self):
        """Show image cropping dialog"""
        cursor = self.editor.textCursor()
        if cursor.charFormat().isImageFormat():
            dialog = ImageCropDialog(self, cursor.charFormat().toImageFormat())
            if dialog.exec_() == QDialog.Accepted:
                self.apply_image_crop(cursor, dialog.get_crop_rect())

    def reset_image_size(self):
        """Reset image to its original size"""
        cursor = self.editor.textCursor()
        if cursor.charFormat().isImageFormat():
            image_format = cursor.charFormat().toImageFormat()
            
            # Get original size from stored properties
            original_width = image_format.property(1)
            original_height = image_format.property(2)
            
            if original_width and original_height:
                # Create new format with original dimensions
                new_format = QTextImageFormat()
                new_format.setName(image_format.name())
                new_format.setWidth(original_width)
                new_format.setHeight(original_height)
                
                # Preserve other properties
                new_format.setProperty(1, original_width)
                new_format.setProperty(2, original_height)
                new_format.setProperty(3, image_format.property(3) or 0)  # Rotation
                
                cursor.mergeCharFormat(new_format)

    def setup_file_toolbar(self):
        """Setup file operations toolbar"""
        # File operations
        new_action = self.create_action("New", self.new_document, "Ctrl+N")
        open_action = self.create_action("Open", self.open_document, "Ctrl+O")
        save_action = self.create_action("Save", self.save_document, "Ctrl+S")
        save_as_action = self.create_action("Save As...", self.save_document_as)
        print_action = self.create_action("Print", self.print_document, "Ctrl+P")
        
        # Undo/Redo
        self.undo_action = self.create_action("Undo", self.editor.undo, "Ctrl+Z")
        self.redo_action = self.create_action("Redo", self.editor.redo, "Ctrl+Shift+Z")
        
        # Add to toolbar
        self.main_toolbar.addAction(new_action)
        self.main_toolbar.addAction(open_action)
        self.main_toolbar.addAction(save_action)
        self.main_toolbar.addAction(save_as_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(self.undo_action)
        self.main_toolbar.addAction(self.redo_action)
        self.main_toolbar.addSeparator()
        self.main_toolbar.addAction(print_action)

    def create_action(self, text, slot, shortcut=None, checkable=False):
        """Helper to create an action"""
        action = QAction(text, self)
        action.triggered.connect(slot)
        if shortcut:
            action.setShortcut(shortcut)
        if checkable:
            action.setCheckable(True)
        return action

    def new_document(self):
        """Create new document"""
        if self.maybe_save():
            self.editor.clear()
            self.current_file = None
            self.editor.document().setModified(False)
            self.window().setWindowTitle("New Document")

    def open_document(self):
        """Open document from file"""
        if self.maybe_save():
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Open Document", "",
                "All Files (*);;Text Files (*.txt);;HTML Files (*.html)"
            )
            if file_name:
                self.load_file(file_name)

    def save_document(self):
        """Save current document"""
        if not self.current_file:
            return self.save_document_as()
        return self.save_file(self.current_file)

    def save_document_as(self):
        """Save document with new name"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save As", "",
            "All Files (*);;Text Files (*.txt);;HTML Files (*.html)"
        )
        if file_name:
            return self.save_file(file_name)
        return False

    def open_document(self):
        """Open document from file"""
        if self.maybe_save():
            file_name, _ = QFileDialog.getOpenFileName(
                self, "Open Document", "",
                "All Files (*);;Text Files (*.txt);;HTML Files (*.html)"
            )
            if file_name:
                self.load_file(file_name)

    def save_file(self, file_name):
        """Save document to file"""
        try:
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(self.editor.toHtml() if file_name.endswith('.html') 
                          else self.editor.toPlainText())
            
            self.current_file = file_name
            self.editor.document().setModified(False)
            self.window().setWindowTitle(os.path.basename(file_name))
            self.add_to_recent_files(file_name)
            return True
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Failed to save file: {str(e)}")
            return False

    def print_document(self):
        """Print the current document"""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QDialog.Accepted:
            self.editor.print_(printer)

    def save_document_as(self, filepath):
        """Save document to specified path"""
        try:
            if filepath.endswith('.html'):
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toHtml())
            else:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.editor.toPlainText())
            self.current_file = filepath
            return True
        except Exception as e:
            print(f"Error saving document: {str(e)}")
            return False

    def load_document(self, filepath):
        """Load document from specified path"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                if filepath.endswith('.html'):
                    self.editor.setHtml(f.read())
                else:
                    self.editor.setPlainText(f.read())
            self.current_file = filepath
            return True
        except Exception as e:
            print(f"Error loading document: {str(e)}")
            return False

    def get_document_statistics(self):
        """Get document statistics"""
        text = self.editor.toPlainText()
        # Split by whitespace and filter out empty strings
        words = [word for word in text.split() if word.strip()]
        return {
            'words': len(words),
            'characters': len(text),
            'lines': len(text.splitlines()) or 1
        }

    def find_text(self, text, forward=True, use_regex=False):
        """Find text in document"""
        flags = QTextDocument.FindFlags()
        if not forward:
            flags |= QTextDocument.FindBackward
        
        if use_regex:
            # Use QRegularExpression instead of QRegExp
            regex = QRegularExpression(text)
            return self.editor.find(regex, flags)
        else:
            return self.editor.find(text, flags)

    def replace_text(self, find_text, replace_with):
        """Replace single occurrence of text"""
        cursor = self.editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == find_text:
            cursor.insertText(replace_with)
            return True
        return self.find_text(find_text)

    def replace_all(self, find_text, replace_with):
        """Replace all occurrences of text"""
        count = 0
        # Start from beginning
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.editor.setTextCursor(cursor)
        
        while self.find_text(find_text):
            cursor = self.editor.textCursor()
            cursor.insertText(replace_with)
            count += 1
        
        return count

    def get_font_size(self):
        """Get current font size"""
        cursor = self.textCursor()
        char_format = cursor.charFormat()
        size = char_format.fontPointSize()
        if size <= 0:  # If no explicit size set
            size = self.currentCharFormat().fontPointSize()
        return size

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
