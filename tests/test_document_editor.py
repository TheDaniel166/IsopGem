import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Method 2: Use relative import
# from ..core.document_editor.editor import DocumentEditor

import unittest
from PyQt5.QtWidgets import (QApplication, QDialog, QColorDialog)
from PyQt5.QtCore import Qt, QPoint, QTimer, QEvent, QUrl, QMimeData
from PyQt5.QtGui import QTextCursor, QColor, QFont, QTextListFormat, QMouseEvent, QTextCharFormat, QImage, QDropEvent
from PyQt5.QtTest import QTest
from core.document_editor import DocumentEditor, StyleInspector
import tempfile

class DocumentEditorTestBase(unittest.TestCase):
    """Base class for document editor tests"""
    
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
            
    def setUp(self):
        self.editor = DocumentEditor()
        self.temp_dir = tempfile.mkdtemp()
        QTest.qWaitForWindowExposed(self.editor)
        
    def tearDown(self):
            self.editor.close()
        # Cleanup temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)

class TestBasicFunctionality(DocumentEditorTestBase):
    """Test basic editor functionality"""
    
    def test_initial_state(self):
        """Test initial editor state"""
        self.assertIsNone(self.editor.current_file)
        self.assertFalse(self.editor.editor.document().isModified())
        self.assertTrue(hasattr(self.editor, 'editor'))
        self.assertTrue(hasattr(self.editor, 'status_bar'))
        self.assertEqual(self.editor.editor.toPlainText(), "")

    def test_undo_redo(self):
        """Test undo/redo functionality"""
        QApplication.processEvents()
        
        # Clear document and undo stack
        self.editor.editor.clear()
        self.editor.editor.document().clearUndoRedoStacks()
        QApplication.processEvents()
        
        # Insert text
        cursor = self.editor.editor.textCursor()
        cursor.insertText("Test text")
        QApplication.processEvents()
        
        # Verify undo is available
        self.assertTrue(self.editor.editor.document().isUndoAvailable())
        
        # Test undo
        self.editor.editor.undo()
        QApplication.processEvents()
        self.assertEqual(self.editor.editor.toPlainText(), "")
        
        # Test redo
        self.assertTrue(self.editor.editor.document().isRedoAvailable())
        self.editor.editor.redo()
        QApplication.processEvents()
        self.assertEqual(self.editor.editor.toPlainText(), "Test text")

class TestFormatting(DocumentEditorTestBase):
    """Test text formatting functionality"""
    
    def setUp(self):
        super().setUp()
        self.editor.editor.setText("Test text")
        QApplication.processEvents()
        cursor = self.editor.editor.textCursor()
        cursor.select(QTextCursor.Document)
        self.editor.editor.setTextCursor(cursor)

    def test_basic_formatting(self):
        """Test basic text formatting"""
        QApplication.processEvents()
        
        # Select text
        cursor = self.editor.editor.textCursor()
        cursor.select(QTextCursor.Document)
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        # Test bold
        self.editor.format_handler.toggle_bold(True)
        QApplication.processEvents()
        cursor = self.editor.editor.textCursor()
        self.assertEqual(cursor.charFormat().font().weight(), QFont.Bold)
        print("PASS: Bold formatting")
        
        # Test italic
        self.editor.format_handler.toggle_italic(True)
        QApplication.processEvents()
        cursor = self.editor.editor.textCursor()
        self.assertTrue(cursor.charFormat().font().italic())
        print("PASS: Italic formatting")
        
        # Test underline
        self.editor.format_handler.toggle_underline(True)
        QApplication.processEvents()
        cursor = self.editor.editor.textCursor()
        self.assertTrue(cursor.charFormat().font().underline())
        print("PASS: Underline formatting")

class TestTable(DocumentEditorTestBase):
    """Test comprehensive table functionality"""
    
    def setUp(self):
        super().setUp()
        self.setup_test_table()
        
    def setup_test_table(self):
        """Create a test table with content"""
        cursor = self.editor.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        # Create initial table
        self.table = self.editor.table_handler.insert_table(3, 3)
        QApplication.processEvents()
        
        # Add content to cells
        if self.table:
            for row in range(3):
                for col in range(3):
                    cell = self.table.cellAt(row, col)
                    cursor = cell.firstCursorPosition()
                    cursor.insertText(f"Cell {row},{col}")
            QApplication.processEvents()

    def test_table_creation(self):
        """Test table creation and initial state"""
        self.assertIsNotNone(self.table, "Table creation failed")
        self.assertEqual(self.table.rows(), 3, "Wrong number of rows")
        self.assertEqual(self.table.columns(), 3, "Wrong number of columns")
        
        # Check cell content
        cell = self.table.cellAt(0, 0)
        cursor = cell.firstCursorPosition()
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        self.assertEqual(cursor.selectedText(), "Cell 0,0", "Cell content incorrect")
        print("PASS: Table creation and content")

    def test_row_operations(self):
        """Test row operations"""
        # Test insert row above
        initial_rows = self.table.rows()
        
        # Move cursor to first cell of table
        first_cell = self.table.cellAt(0, 0)
        cursor = first_cell.firstCursorPosition()
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        # Verify we're in the table
        cursor = self.editor.editor.textCursor()
        table = cursor.currentTable()
        self.assertIsNotNone(table, "Not in table before operation")
        
        # Get updated table reference after operation
        self.table = self.editor.table_handler.insert_row_above()
        QApplication.processEvents()
        
        self.assertIsNotNone(self.table, "Lost table reference")
        self.assertEqual(self.table.rows(), initial_rows + 1, "Row insertion above failed")
        print("PASS: Insert row above")
        
        # Test insert row below
        self.table = self.editor.table_handler.insert_row_below()
        QApplication.processEvents()
        
        self.assertEqual(self.table.rows(), initial_rows + 2, "Row insertion below failed")
        print("PASS: Insert row below")

    def test_column_operations(self):
        """Test column operations"""
        # Test insert column left
        initial_cols = self.table.columns()
        
        # Move cursor to first cell of table
        first_cell = self.table.cellAt(0, 0)
        cursor = first_cell.firstCursorPosition()
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        # Verify we're in the table
        cursor = self.editor.editor.textCursor()
        table = cursor.currentTable()
        self.assertIsNotNone(table, "Not in table before operation")
        
        # Get updated table reference after operation
        self.table = self.editor.table_handler.insert_column_left()
        QApplication.processEvents()
        
        self.assertIsNotNone(self.table, "Lost table reference")
        self.assertEqual(self.table.columns(), initial_cols + 1, "Column insertion left failed")
        print("PASS: Insert column left")
        
        # Test insert column right
        self.table = self.editor.table_handler.insert_column_right()
        QApplication.processEvents()
        
        self.assertEqual(self.table.columns(), initial_cols + 2, "Column insertion right failed")
        print("PASS: Insert column right")

    def test_cell_operations(self):
        """Test cell operations"""
        # Test cell merging
        cursor = self.editor.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        # Select two cells
        cell = self.table.cellAt(0, 0)
        cursor = cell.firstCursorPosition()
        cursor.movePosition(QTextCursor.NextCell)
        cursor.movePosition(QTextCursor.PreviousCell, QTextCursor.KeepAnchor)
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        self.editor.table_handler.merge_selected_cells()
        QApplication.processEvents()
        
        merged_cell = self.table.cellAt(0, 0)
        self.assertTrue(merged_cell.columnSpan() > 1, "Cell merge failed")
        print("PASS: Cell merge")
        
        # Test cell splitting
        self.editor.table_handler.split_cell()
        QApplication.processEvents()
        
        split_cell = self.table.cellAt(0, 0)
        self.assertEqual(split_cell.columnSpan(), 1, "Cell split failed")
        print("PASS: Cell split")

    def test_table_formatting(self):
        """Test table formatting"""
        cursor = self.editor.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        # Get current format
        table_format = self.table.format()
        
        # Test border settings
        table_format.setBorder(2)
        self.table.setFormat(table_format)
        QApplication.processEvents()
        
        updated_format = self.table.format()
        self.assertEqual(updated_format.border(), 2, "Border setting failed")
        print("PASS: Table border formatting")
        
        # Test alignment
        table_format.setAlignment(Qt.AlignCenter)
        self.table.setFormat(table_format)
        QApplication.processEvents()
        
        updated_format = self.table.format()
        self.assertEqual(updated_format.alignment(), Qt.AlignCenter, "Alignment setting failed")
        print("PASS: Table alignment formatting")

class TestImage(DocumentEditorTestBase):
    """Test image functionality"""
    
    def setUp(self):
        super().setUp()
        # Create test image
        self.test_image = os.path.join(self.temp_dir, "test.png")
        image = QImage(100, 100, QImage.Format_RGB32)
        image.fill(QColor(Qt.red))
        image.save(self.test_image)

    def test_image_operations(self):
        """Test basic image operations"""
        # Insert image
        self.editor.image_handler.insert_image_from_file(self.test_image)
        QApplication.processEvents()
        
        cursor = self.editor.editor.textCursor()
        self.assertTrue(cursor.charFormat().isImageFormat())
        print("PASS: Image insertion")
        
        # Test rotation
        self.editor.image_handler.rotate_image(90)
        QApplication.processEvents()
        
        # Get updated cursor and format
        cursor = self.editor.editor.textCursor()
        format = cursor.charFormat().toImageFormat()
        rotation = format.property(3)
        
        self.assertEqual(rotation, 90)
        print("PASS: Image rotation")

class TestDocumentStructure(DocumentEditorTestBase):
    """Test document structure and state"""
    
    def test_document_state(self):
        """Test document state management"""
        # Test initial state
        self.assertFalse(self.editor.editor.document().isModified())
        print("PASS: Initial state")
        
        # Test modification state
        self.editor.editor.textCursor().insertText("Test")
        QApplication.processEvents()
        self.assertTrue(self.editor.editor.document().isModified())
        print("PASS: Modification detection")
        
        # Test clear operation
        self.editor.editor.clear()
        QApplication.processEvents()
        self.assertEqual(self.editor.editor.toPlainText(), "")
        print("PASS: Clear operation")

class TestFormatHandler(DocumentEditorTestBase):
    """Test format handler functionality"""
    
    def setUp(self):
        super().setUp()
        self.editor.editor.setText("Test text")
        cursor = self.editor.editor.textCursor()
        cursor.select(QTextCursor.Document)
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()

    def test_text_formatting(self):
        """Test text formatting operations"""
        # Test font family
        font_family = "Arial"
        format = QTextCharFormat()
        format.setFontFamily(font_family)
        self.editor.format_handler.merge_format(format)
        QApplication.processEvents()
        
        cursor = self.editor.editor.textCursor()
        self.assertEqual(cursor.charFormat().font().family(), font_family)
        print("PASS: Font family")
        
        # Test font size
        font_size = 16
        format = QTextCharFormat()
        format.setFontPointSize(font_size)
        self.editor.format_handler.merge_format(format)
        QApplication.processEvents()
        
        cursor = self.editor.editor.textCursor()
        self.assertEqual(int(cursor.charFormat().font().pointSize()), font_size)
        print("PASS: Font size")
        
        # Test text color
        color = QColor(Qt.red)
        format = QTextCharFormat()
        format.setForeground(color)
        self.editor.format_handler.merge_format(format)
        QApplication.processEvents()
        
        cursor = self.editor.editor.textCursor()
        self.assertEqual(cursor.charFormat().foreground().color(), color)
        print("PASS: Text color")

    def test_paragraph_formatting(self):
        """Test paragraph formatting"""
        # Test alignment
        alignments = {
            'left': Qt.AlignLeft,
            'center': Qt.AlignCenter,
            'right': Qt.AlignRight,
            'justify': Qt.AlignJustify
        }
        
        for name, align in alignments.items():
            self.editor.format_handler.align_text(name)
            QApplication.processEvents()
            
            cursor = self.editor.editor.textCursor()
            self.assertEqual(cursor.blockFormat().alignment(), align)
            print(f"PASS: {name.capitalize()} alignment")

    def test_style_application(self):
        """Test style application"""
        styles = ["Normal", "Title", "Subtitle", "Heading 1", "Heading 2"]
        
        for style in styles:
            self.editor.format_handler.apply_text_style(style)
            QApplication.processEvents()
            
            cursor = self.editor.editor.textCursor()
            if style == "Normal":
                self.assertEqual(cursor.charFormat().font().weight(), QFont.Normal)
            elif style in ["Title", "Heading 1", "Heading 2"]:
                self.assertEqual(cursor.charFormat().font().weight(), QFont.Bold)
            print(f"PASS: {style} style")

    def test_color_operations(self):
        """Test color operations"""
        # Setup test text
        self.editor.editor.setText("Test text")
        cursor = self.editor.editor.textCursor()
        cursor.select(QTextCursor.Document)
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        # Test text color
        test_color = QColor(Qt.red)
        format = QTextCharFormat()
        format.setForeground(test_color)
        self.editor.format_handler.merge_format(format)
        QApplication.processEvents()
        
        cursor = self.editor.editor.textCursor()
        self.assertEqual(
            cursor.charFormat().foreground().color(),
            test_color,
            "Text color not applied correctly"
        )
        print("PASS: Text color")
        
        # Test highlight color
        highlight_color = QColor(Qt.yellow)
        format = QTextCharFormat()
        format.setBackground(highlight_color)
        self.editor.format_handler.merge_format(format)
        QApplication.processEvents()
        
        cursor = self.editor.editor.textCursor()
        self.assertEqual(
            cursor.charFormat().background().color(),
            highlight_color,
            "Highlight color not applied correctly"
        )
        print("PASS: Highlight color")

    def test_color_dialog_operations(self):
        """Test color dialog operations"""
        # Setup test text
        self.editor.editor.setText("Test text")
        cursor = self.editor.editor.textCursor()
        cursor.select(QTextCursor.Document)
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        # Mock color dialog
        def mock_get_color(*args, **kwargs):
            return QColor(Qt.red)
        
        original_get_color = QColorDialog.getColor
        QColorDialog.getColor = mock_get_color
        
        try:
            # Test text color
            self.editor.format_handler.text_color()
            QApplication.processEvents()
            
            cursor = self.editor.editor.textCursor()
            self.assertEqual(
                cursor.charFormat().foreground().color(),
                QColor(Qt.red),
                "Text color not applied correctly"
            )
            print("PASS: Text color dialog")
            
            # Test highlight color
            QColorDialog.getColor = lambda *args, **kwargs: QColor(Qt.yellow)
            self.editor.format_handler.highlight_color()
            QApplication.processEvents()
            
            cursor = self.editor.editor.textCursor()
            self.assertEqual(
                cursor.charFormat().background().color(),
                QColor(Qt.yellow),
                "Highlight color not applied correctly"
            )
            print("PASS: Highlight color dialog")
            
        finally:
            # Restore original color dialog
            QColorDialog.getColor = original_get_color

class TestImageHandler(DocumentEditorTestBase):
    """Test image handler functionality"""
    
    def setUp(self):
        super().setUp()
        # Create test images
        self.test_images = {}
        for format in ['png', 'jpg', 'gif']:
            path = os.path.join(self.temp_dir, f"test.{format}")
            image = QImage(100, 100, QImage.Format_RGB32)
            image.fill(QColor(Qt.red))
            image.save(path)
            self.test_images[format] = path

    def test_image_insertion(self):
        """Test image insertion for different formats"""
        for format, path in self.test_images.items():
            self.editor.editor.clear()
            QApplication.processEvents()
            
            self.editor.image_handler.insert_image_from_file(path)
            QApplication.processEvents()
            
            cursor = self.editor.editor.textCursor()
            self.assertTrue(cursor.charFormat().isImageFormat())
            print(f"PASS: {format.upper()} image insertion")

    def test_image_manipulation(self):
        """Test image manipulation operations"""
        self.editor.image_handler.insert_image_from_file(self.test_images['png'])
        QApplication.processEvents()
        
        # Test rotation
        angles = [90, 180, 270]
        for angle in angles:
            self.editor.image_handler.rotate_image(angle)
            QApplication.processEvents()
            
            cursor = self.editor.editor.textCursor()
            format = cursor.charFormat().toImageFormat()
            self.assertEqual(format.property(3), angle)
            print(f"PASS: {angle}° rotation")
        
        # Test flipping
        self.editor.image_handler.flip_image_horizontal()
        QApplication.processEvents()
        print("PASS: Horizontal flip")
        
        self.editor.image_handler.flip_image_vertical()
        QApplication.processEvents()
        print("PASS: Vertical flip")

class TestStyleInspector(DocumentEditorTestBase):
    """Test style inspector functionality"""
    
    def test_format_inspection(self):
        """Test format inspection"""
        # Apply some formatting
        self.editor.editor.setText("Test text")
        cursor = self.editor.editor.textCursor()
        cursor.select(QTextCursor.Document)
        
        format = QTextCharFormat()
        format.setFontFamily("Arial")
        format.setFontPointSize(16)
        format.setFontWeight(QFont.Bold)
        format.setForeground(QColor("#FF0000"))
        
        cursor.mergeCharFormat(format)
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        # Test inspector
        inspector = StyleInspector(self.editor)
        inspector.update_properties()
        
        # Verify properties
        self.verify_inspector_property(inspector, "Font Family", "Arial")
        self.verify_inspector_property(inspector, "Font Size", "16pt")
        self.verify_inspector_property(inspector, "Font Weight", "Bold")
        self.verify_inspector_property(inspector, "Text Color", "#ff0000")
        print("PASS: Style inspection")

    def verify_inspector_property(self, inspector, name, expected):
        """Helper to verify inspector properties"""
        found = False
        for i in range(inspector.properties.topLevelItemCount()):
            parent = inspector.properties.topLevelItem(i)
            for j in range(parent.childCount()):
                item = parent.child(j)
                if item.text(0) == name:
                    self.assertEqual(item.text(1), expected, 
                                   f"Property {name} value mismatch: expected {expected}, got {item.text(1)}")
                    found = True
                    print(f"PASS: {name} property inspection")
                    break
            if found:
                break
        
        if not found:
            self.fail(f"Property {name} not found in inspector")

class TestFileOperations(DocumentEditorTestBase):
    """Test file operations"""
    
    def setUp(self):
        super().setUp()
        self.test_file = os.path.join(self.temp_dir, "test_document.txt")
        self.test_html = os.path.join(self.temp_dir, "test_document.html")
    
    def test_save_load_operations(self):
        """Test saving and loading documents"""
        # Create test content with formatting
        self.editor.editor.clear()
        cursor = self.editor.editor.textCursor()
        
        # Add formatted text
        format = QTextCharFormat()
        format.setFontWeight(QFont.Bold)
        format.setForeground(QColor(Qt.red))
        cursor.insertText("Test Document", format)
        cursor.insertBlock()
        
        format.setFontWeight(QFont.Normal)
        format.setForeground(QColor(Qt.black))
        cursor.insertText("Normal text")
        QApplication.processEvents()
        
        # Test plain text save/load
        self.editor.save_document_as(self.test_file)
        QApplication.processEvents()
        
        self.assertTrue(os.path.exists(self.test_file), "File not saved")
        
        self.editor.editor.clear()
        self.editor.load_document(self.test_file)
        QApplication.processEvents()
        
        self.assertIn("Test Document", self.editor.editor.toPlainText())
        print("PASS: Plain text save/load")
        
        # Test HTML save/load
        self.editor.save_document_as(self.test_html)
        QApplication.processEvents()
        
        self.assertTrue(os.path.exists(self.test_html), "HTML file not saved")
        
        self.editor.editor.clear()
        self.editor.load_document(self.test_html)
        QApplication.processEvents()
        
        cursor = self.editor.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.EndOfWord, QTextCursor.KeepAnchor)
        self.assertEqual(cursor.charFormat().fontWeight(), QFont.Bold)
        print("PASS: HTML save/load with formatting")

    def test_auto_save(self):
        """Test auto-save functionality"""
        # Enable auto-save with shorter interval for testing
        self.editor.auto_save_interval = 1000  # 1 second
        self.editor.setup_auto_save()
        
        # Make changes and set current file
        self.editor.editor.setText("Auto-save test")
        self.editor.current_file = self.test_file
        self.editor.editor.document().setModified(True)  # Mark as modified
        QApplication.processEvents()
        
        # Force auto-save
        self.editor._auto_save()
        QApplication.processEvents()
        
        # Verify file was created and contains correct content
        self.assertTrue(os.path.exists(self.test_file), "Auto-save file not created")
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("Auto-save test", content)
        print("PASS: Auto-save")

class TestDocumentStatistics(DocumentEditorTestBase):
    """Test document statistics functionality"""
    
    def test_word_count(self):
        """Test word count calculation"""
        test_text = "This is a test document.\nIt has multiple lines.\nAnd some numbers: 123."
        self.editor.editor.setText(test_text)
        QApplication.processEvents()
        
        stats = self.editor.get_document_statistics()
        expected_words = len([word for word in test_text.split() if word.strip()])  # Count actual words
        self.assertEqual(stats['words'], expected_words, 
                        f"Word count mismatch. Expected {expected_words}, got {stats['words']}")
        self.assertEqual(stats['characters'], len(test_text))
        self.assertEqual(stats['lines'], 3)
        print("PASS: Word count")

class TestDragDrop(DocumentEditorTestBase):
    """Test drag and drop functionality"""
    
    def setUp(self):
        super().setUp()
        # Create test files
        self.text_file = os.path.join(self.temp_dir, "drag_test.txt")
        with open(self.text_file, 'w') as f:
            f.write("Dragged text")
        
        self.image_file = os.path.join(self.temp_dir, "drag_test.png")
        image = QImage(100, 100, QImage.Format_RGB32)
        image.fill(QColor(Qt.red))
        image.save(self.image_file)
    
    def test_drag_drop_text(self):
        """Test text file drag and drop"""
        # Create mime data
        mime_data = QMimeData()
        url = QUrl.fromLocalFile(self.text_file)
        mime_data.setUrls([url])
        
        # Create drop event
        event = QDropEvent(
            QPoint(10, 10),
            Qt.CopyAction,
            mime_data,
            Qt.LeftButton,
            Qt.NoModifier
        )
        
        # Process drop
        self.editor.editor.dropEvent(event)
        QApplication.processEvents()
        
        self.assertIn("Dragged text", self.editor.editor.toPlainText())
        print("PASS: Text drag and drop")
    
    def test_drag_drop_image(self):
        """Test image drag and drop"""
        # Create mime data
        mime_data = QMimeData()
        url = QUrl.fromLocalFile(self.image_file)
        mime_data.setUrls([url])
        
        # Create drop event
        event = QDropEvent(
            QPoint(10, 10),
            Qt.CopyAction,
            mime_data,
            Qt.LeftButton,
            Qt.NoModifier
        )
        
        # Process drop
        self.editor.editor.dropEvent(event)
        QApplication.processEvents()
        
        cursor = self.editor.editor.textCursor()
        self.assertTrue(cursor.charFormat().isImageFormat())
        print("PASS: Image drag and drop")

class TestSearchReplace(DocumentEditorTestBase):
    """Test search and replace functionality"""
    
    def test_search_operations(self):
        """Test text search operations"""
        # Setup test content
        test_text = "This is a test. This is another test."
        self.editor.editor.setText(test_text)
        QApplication.processEvents()
        
        # Test find first occurrence
        found = self.editor.find_text("test")
        self.assertTrue(found, "Text search failed")
        
        # Verify selection
        cursor = self.editor.editor.textCursor()
        self.assertEqual(cursor.selectedText(), "test")
        print("PASS: Text search")
        
        # Test find next
        found = self.editor.find_text("test", forward=True)
        self.assertTrue(found, "Find next failed")
        cursor = self.editor.editor.textCursor()
        self.assertEqual(cursor.position(), test_text.rindex("test") + 4)
        print("PASS: Find next")
        
        # Test find with regex
        found = self.editor.find_text("t..t", use_regex=True)
        self.assertTrue(found, "Regex search failed")
        print("PASS: Regex search")

    def test_replace_operations(self):
        """Test text replace operations"""
        # Setup test content
        self.editor.editor.setText("test test test")
        QApplication.processEvents()
        
        # Test replace first occurrence
        replaced = self.editor.replace_text("test", "TEST")
        self.assertTrue(replaced, "Replace failed")
        self.assertEqual(self.editor.editor.toPlainText(), "TEST test test")
        print("PASS: Single replace")
        
        # Test replace all
        count = self.editor.replace_all("test", "TEST")
        self.assertEqual(count, 2, "Replace all count incorrect")
        self.assertEqual(self.editor.editor.toPlainText(), "TEST TEST TEST")
        print("PASS: Replace all")

class TestListFormatting(DocumentEditorTestBase):
    """Test list formatting functionality"""
    
    def test_bullet_list(self):
        """Test bullet list formatting"""
        # Create test content
        self.editor.editor.setText("Item 1\nItem 2\nItem 3")
        cursor = self.editor.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        # Apply bullet list
        self.editor.format_handler.toggle_bullet_list()
        QApplication.processEvents()
        
        # Verify list format
        cursor = self.editor.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.assertTrue(cursor.currentList() is not None)
        self.assertEqual(cursor.currentList().format().style(),
                        QTextListFormat.ListDisc)
        print("PASS: Bullet list")

    def test_numbered_list(self):
        """Test numbered list formatting"""
        # Create test content
        self.editor.editor.setText("Item 1\nItem 2\nItem 3")
        cursor = self.editor.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        # Apply numbered list
        self.editor.format_handler.toggle_numbered_list()
        QApplication.processEvents()
        
        # Verify list format
        cursor = self.editor.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.assertTrue(cursor.currentList() is not None)
        self.assertEqual(cursor.currentList().format().style(),
                        QTextListFormat.ListDecimal)
        print("PASS: Numbered list")

class TestDocumentHistory(DocumentEditorTestBase):
    """Test document history functionality"""
    
    def test_recent_files(self):
        """Test recent files management"""
        # Create test files
        test_files = []
        for i in range(3):
            path = os.path.join(self.temp_dir, f"test_{i}.txt")
            with open(path, 'w') as f:
                f.write(f"Test content {i}")
            test_files.append(path)
        
        # Add files to recent list
        for file in test_files:
            self.editor.add_to_recent_files(file)
        
        # Verify recent files list
        self.assertEqual(len(self.editor.recent_files), 3)
        self.assertEqual(self.editor.recent_files[0], test_files[-1])
        print("PASS: Recent files management")

def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    test_classes = [
        TestFileOperations,
        TestDocumentStatistics,
        TestSearchReplace,
        TestListFormatting,
        TestDocumentHistory
    ]
    
    for test_class in test_classes:
        try:
            tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
        except Exception as e:
            print(f"Error loading tests from {test_class.__name__}: {str(e)}")
    
    runner = unittest.TextTestRunner(verbosity=2)
    
    try:
        result = runner.run(suite)
        return result
    except Exception as e:
        print(f"\nTest execution failed: {str(e)}")
        return None

if __name__ == '__main__':
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        result = run_tests()
        
        if result is not None:
            print("\nTest Summary:")
            print(f"Ran {result.testsRun} tests")
            print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
            print(f"Failures: {len(result.failures)}")
            print(f"Errors: {len(result.errors)}")
            
            if result.wasSuccessful():
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            print("Test execution failed")
            sys.exit(2)
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        sys.exit(3)
    finally:
        if QApplication.instance():
            QApplication.instance().quit() 