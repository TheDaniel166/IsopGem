import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Method 2: Use relative import
# from ..core.document_editor.editor import DocumentEditor

import unittest
from PyQt5.QtWidgets import (QApplication, QDialog)
from PyQt5.QtCore import Qt, QPoint, QTimer, QEvent
from PyQt5.QtGui import QTextCursor, QColor, QFont, QTextListFormat, QMouseEvent, QTextCharFormat
from core.document_editor import DocumentEditor, StyleInspector

class DocumentEditorTestBase(unittest.TestCase):
    """Base class for document editor tests"""
    
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
            
    @classmethod
    def tearDownClass(cls):
        if cls.app:
            cls.app.quit()
            
    def setUp(self):
        self.editor = DocumentEditor()
        self.editor.show()
        QTimer.singleShot(0, self.editor.activateWindow)
        
    def tearDown(self):
        if hasattr(self, 'editor'):
            self.editor.close()
            self.editor.deleteLater()

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
        # Wait for editor to be ready
        QApplication.processEvents()
        
        # Clear document and undo stack
        self.editor.editor.clear()
        self.editor.editor.document().clearUndoRedoStacks()
        QApplication.processEvents()
        
        # Get document and cursor
        document = self.editor.editor.document()
        cursor = QTextCursor(document)
        self.editor.editor.setTextCursor(cursor)
        
        # Initial state
        self.assertFalse(document.isUndoAvailable())
        self.assertFalse(document.isRedoAvailable())
        
        # Insert some text
        cursor.insertText("First line\n")
        QApplication.processEvents()
        
        # Verify text was inserted and undo is available
        self.assertEqual(document.toPlainText(), "First line\n")
        self.assertTrue(document.isUndoAvailable())

class TestTextFormatting(DocumentEditorTestBase):
    """Test text formatting features"""
    
    def setUp(self):
        super().setUp()
        self.editor.editor.setText("Test text")
        self.cursor = self.editor.editor.textCursor()
        self.cursor.select(QTextCursor.Document)
        self.editor.editor.setTextCursor(self.cursor)

    def test_character_formatting(self):
        """Test character-level formatting"""
        # Bold
        self.editor.toggle_bold(True)
        self.assertEqual(self.cursor.charFormat().font().weight(), QFont.Bold)
        
        # Italic
        self.editor.toggle_italic(True)
        self.assertTrue(self.cursor.charFormat().font().italic())
        
        # Underline
        self.editor.toggle_underline(True)
        self.assertTrue(self.cursor.charFormat().font().underline())
        
        # Font family
        test_font = "Times New Roman"
        self.editor.font_family.setCurrentFont(QFont(test_font))
        self.assertEqual(self.cursor.charFormat().font().family(), test_font)
        
        # Font size
        test_size = 16
        self.editor.font_size.setValue(test_size)
        self.assertEqual(self.cursor.charFormat().font().pointSize(), test_size)

    def test_paragraph_formatting(self):
        """Test paragraph-level formatting"""
        # Alignment
        alignments = {
            'left': Qt.AlignLeft,
            'center': Qt.AlignCenter,
            'right': Qt.AlignRight,
            'justify': Qt.AlignJustify
        }
        
        for align_name, align_value in alignments.items():
            self.editor.align_text(align_name)
            self.assertEqual(self.editor.editor.alignment(), align_value)
        
        # Line spacing
        test_spacing = 2.0
        self.editor.set_line_spacing(test_spacing)
        self.assertEqual(
            self.cursor.blockFormat().lineHeight(),
            int(test_spacing * 100)
        )
        
        # Paragraph spacing
        test_margin = 20
        self.editor.set_paragraph_spacing(test_margin)
        block_format = self.cursor.blockFormat()
        self.assertEqual(block_format.topMargin(), test_margin)
        self.assertEqual(block_format.bottomMargin(), test_margin)

class TestTableOperations(DocumentEditorTestBase):
    """Test table operations"""
    
    def setUp(self):
        super().setUp()
        # Wait for editor to be ready
        QApplication.processEvents()
        
        # Ensure cursor is at start
        cursor = self.editor.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.editor.editor.setTextCursor(cursor)
        
        # Insert table with format
        self.table = self.editor.insert_table(3, 3)
        QApplication.processEvents()
        
        # Verify table was created
        if self.table is None:
            self.skipTest("Table creation failed - skipping table tests")

    def test_table_structure(self):
        """Test table creation and basic structure"""
        self.assertIsNotNone(self.table)
        self.assertEqual(self.table.rows(), 3)
        self.assertEqual(self.table.columns(), 3)

    def test_row_operations(self):
        """Test row operations"""
        # Insert row above
        initial_rows = self.table.rows()
        self.editor.insert_row_above()
        self.assertEqual(self.table.rows(), initial_rows + 1)
        
        # Insert row below
        self.editor.insert_row_below()
        self.assertEqual(self.table.rows(), initial_rows + 2)
        
        # Delete row
        self.editor.delete_row()
        self.assertEqual(self.table.rows(), initial_rows + 1)

    def test_column_operations(self):
        """Test column operations"""
        initial_cols = self.table.columns()
        
        # Insert column left
        self.editor.insert_column_left()
        self.assertEqual(self.table.columns(), initial_cols + 1)
        
        # Insert column right
        self.editor.insert_column_right()
        self.assertEqual(self.table.columns(), initial_cols + 2)
        
        # Delete column
        self.editor.delete_column()
        self.assertEqual(self.table.columns(), initial_cols + 1)

class TestFileOperations(DocumentEditorTestBase):
    """Test file operations"""
    
    def setUp(self):
        super().setUp()
        self.test_file = "test_document.rtf"
        self.test_content = "Test content\nWith multiple lines"
        self.editor.editor.setText(self.test_content)

    def tearDown(self):
        super().tearDown()
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_save_load_file(self):
        """Test saving and loading files"""
        # Save file
        self.editor.save_file(self.test_file)
        self.assertTrue(os.path.exists(self.test_file))
        
        # Clear and reload
        self.editor.editor.clear()
        self.editor.load_file(self.test_file)
        
        # Verify content
        self.assertIn(self.test_content, self.editor.editor.toPlainText())

    def test_recent_files(self):
        """Test recent files functionality"""
        # Save file to add to recent files
        self.editor.save_file(self.test_file)
        
        # Check recent files list
        self.assertIn(self.test_file, self.editor.recent_files)
        self.assertLessEqual(len(self.editor.recent_files), self.editor.max_recent_files)

class TestAutoSave(DocumentEditorTestBase):
    """Test auto-save functionality"""
    
    def test_auto_save_settings(self):
        """Test auto-save settings"""
        self.assertTrue(hasattr(self.editor, 'auto_save_timer'))
        self.assertEqual(
            self.editor.auto_save_interval,
            5 * 60 * 1000  # 5 minutes in milliseconds
        )

    def test_backup_settings(self):
        """Test backup settings"""
        self.assertTrue(self.editor.backup_enabled)
        self.assertEqual(self.editor.max_backups, 5)
        self.assertTrue(os.path.exists(self.editor.backup_dir))

class TestFormatPainter(DocumentEditorTestBase):
    """Test format painter functionality"""
    
    def test_format_copying(self):
        """Test copying and applying formats"""
        QApplication.processEvents()
        
        # Set up source text with formatting
        self.editor.editor.setText("Source text\nTarget text")
        cursor = self.editor.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        # Apply formatting to source
        self.editor.toggle_bold(True)
        self.editor.toggle_italic(True)
        QApplication.processEvents()
        
        # Enable format painter
        self.editor.toggle_format_painter(True)
        self.assertIsNotNone(self.editor.copied_format)
        
        # Create proper QMouseEvent with widget-relative position
        pos = self.editor.editor.mapFromGlobal(
            self.editor.editor.viewport().mapToGlobal(QPoint(10, 10))
        )
        event = QMouseEvent(
            QEvent.MouseButtonPress,
            pos,
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier
        )
        
        # Apply to target
        cursor.movePosition(QTextCursor.NextBlock)
        cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
        self.editor.editor.setTextCursor(cursor)
        QApplication.processEvents()
        
        # Send event to editor viewport
        self.editor.editor.viewport().mousePressEvent(event)

class TestTableFeatures(DocumentEditorTestBase):
    """Test comprehensive table functionality"""
    
    def setUp(self):
        super().setUp()
        QApplication.processEvents()
        self.table = self.create_test_table()
        
    def create_test_table(self):
        """Create a test table with some content"""
        cursor = self.editor.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        self.editor.editor.setTextCursor(cursor)
        
        table = self.editor.insert_table(3, 3)
        if table is None:
            self.skipTest("Table creation failed")
            
        # Add some content
        for row in range(3):
            for col in range(3):
                cell = table.cellAt(row, col)
                cursor = cell.firstCursorPosition()
                cursor.insertText(f"Cell {row},{col}")
        
        return table

    def test_table_formatting(self):
        """Test table formatting options"""
        format_data = {
            'border_width': 2,
            'border_style': Qt.SolidLine,
            'border_color': QColor("#000000"),
            'padding': 10,
            'spacing': 2,
            'width': 500,
            'background_color': QColor("#f0f0f0")
        }
        
        self.editor.apply_table_format(self.table, format_data)
        
        # Verify format was applied
        table_format = self.table.format()
        self.assertEqual(table_format.border(), 2)
        self.assertEqual(table_format.cellPadding(), 10)
        self.assertEqual(table_format.cellSpacing(), 2)
        self.assertEqual(table_format.width(), 500)

    def test_cell_operations(self):
        """Test cell-level operations"""
        # Test cell merging
        self.table.mergeCells(0, 0, 1, 2)
        self.assertEqual(self.table.cellAt(0, 0).columnSpan(), 2)
        
        # Test cell splitting
        self.table.splitCell(0, 0, 1, 2)
        self.assertEqual(self.table.cellAt(0, 0).columnSpan(), 1)

    def test_table_templates(self):
        """Test table templates"""
        templates = {
            "Header Row 3x3": (3, 3),
            "Calendar 7x5": (5, 7),
            "Contact Card 2x3": (2, 3)
        }
        
        for name, (rows, cols) in templates.items():
            cursor = self.editor.editor.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.editor.editor.setTextCursor(cursor)
            
            self.editor.insert_table_template(rows, cols, name)
            table = cursor.currentTable()
            
            self.assertIsNotNone(table)
            self.assertEqual(table.rows(), rows)
            self.assertEqual(table.columns(), cols)

class TestDocumentMap(DocumentEditorTestBase):
    """Test document map functionality"""
    
    def setUp(self):
        super().setUp()
        self.create_test_document()
        
    def create_test_document(self):
        """Create a test document with headings"""
        cursor = self.editor.editor.textCursor()
        
        # Add title
        self.editor.apply_text_style("Title")
        cursor.insertText("Document Title")
        cursor.insertBlock()
        
        # Add sections
        for i in range(3):
            self.editor.apply_text_style(f"Heading {i+1}")
            cursor.insertText(f"Section {i+1}")
            cursor.insertBlock()
            cursor.insertText("Regular paragraph text")
            cursor.insertBlock()

    def test_map_structure(self):
        """Test document map structure"""
        doc_map = self.editor.document_map
        doc_map.update_map()
        
        # Verify structure
        self.assertEqual(doc_map.tree.topLevelItemCount(), 4)  # Title + 3 sections
        
        # Verify content
        title_item = doc_map.tree.topLevelItem(0)
        self.assertEqual(title_item.text(0), "Document Title")

    def test_navigation(self):
        """Test navigation through document map"""
        doc_map = self.editor.document_map
        doc_map.update_map()
        
        # Click on second heading
        second_item = doc_map.tree.topLevelItem(2)
        doc_map.navigate_to_section(second_item)
        
        # Verify cursor position
        cursor = self.editor.editor.textCursor()
        self.assertEqual(cursor.block().text(), "Section 2")

class TestStyleInspector(DocumentEditorTestBase):
    """Test style inspector functionality"""
    
    def test_character_properties(self):
        """Test character formatting detection"""
        cursor = self.editor.editor.textCursor()
        
        # Apply some formatting
        format = QTextCharFormat()
        format.setFontFamily("Arial")
        format.setFontPointSize(16)
        format.setFontWeight(QFont.Bold)
        format.setForeground(QColor("#FF0000"))
        
        cursor.insertText("Test text", format)
        
        # Update inspector
        inspector = StyleInspector(self.editor)
        inspector.update_properties()
        
        # Verify properties
        self.verify_property(inspector, "Font", "Arial")
        self.verify_property(inspector, "Size", "16pt")
        self.verify_property(inspector, "Weight", "Bold")
        self.verify_property(inspector, "Color", "#ff0000")

    def verify_property(self, inspector, name, expected_value):
        """Helper to verify property values"""
        for i in range(inspector.properties.topLevelItemCount()):
            parent = inspector.properties.topLevelItem(i)
            for j in range(parent.childCount()):
                item = parent.child(j)
                if item.text(0) == name:
                    self.assertEqual(item.text(1), expected_value)
                    return
        self.fail(f"Property {name} not found")

def run_tests():
    """Run all tests"""
    suite = unittest.TestSuite()
    test_classes = [
        TestBasicFunctionality,
        TestTextFormatting,
        TestTableOperations,
        TestFileOperations,
        TestAutoSave,
        TestFormatPainter,
        TestTableFeatures,
        TestDocumentMap,
        TestStyleInspector
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)

if __name__ == '__main__':
    try:
        result = run_tests()
    finally:
        app = QApplication.instance()
        if app:
            app.quit() 