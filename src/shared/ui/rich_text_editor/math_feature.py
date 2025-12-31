"""
Math Feature for Rich Text Editor.
Handles LaTeX insertion, rendering, and management.
"""
import qtawesome as qta
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QIcon, QTextImageFormat, QTextDocument, QTextCursor
from PyQt6.QtWidgets import QMenu, QInputDialog, QMessageBox, QTextEdit

from .math_renderer import MathRenderer
import uuid

class MathFeature:
    """
    Manages Math/LaTeX operations in the editor.
    """
    
    LATEX_PREFIX = "LATEX:"
    
    def __init__(self, editor: QTextEdit, parent):
        self.editor = editor # SafeTextEdit
        self.parent = parent # RichTextEditor
        self._setup_actions()
        
    def _setup_actions(self):
        """Initialize actions."""
        self.action_insert_math = QAction("Insert Math", self.parent)
        self.action_insert_math.setIcon(qta.icon("fa5s.square-root-alt", color="#1e293b"))
        self.action_insert_math.setToolTip("Insert LaTeX Equation")
        self.action_insert_math.triggered.connect(self.insert_math_dialog)
        
        self.action_render_doc = QAction("Render All Math", self.parent)
        self.action_render_doc.setIcon(qta.icon("fa5s.magic", color="#1e293b"))
        self.action_render_doc.setToolTip("Find and render all $$...$$ equations")
        self.action_render_doc.triggered.connect(self.render_all_math)

    def insert_math_dialog(self):
        """Show input dialog for LaTeX."""
        # Use a larger dialog if possible, but inputDialog is simplest for now.
        text, ok = QInputDialog.getMultiLineText(
            self.parent, 
            "Insert Math", 
            "Enter LaTeX code (e.g. E = mc^2):",
            "E = mc^2"
        )
        if ok and text:
            self.insert_math(text)

    def insert_math(self, latex: str):
        """Render and insert math image at cursor."""
        image = MathRenderer.render_latex(latex, fontsize=14)
        if image:
            self._insert_rendered_image(image, latex)
        else:
            QMessageBox.warning(self.parent, "Rendering Error", "Could not render LaTeX. Please check syntax.")

    def _insert_rendered_image(self, image, latex: str):
        """Insert the QImage into the document."""
        # Generate unique URL for the resource
        img_id = str(uuid.uuid4())
        url_str = f"docimg://math/{img_id}"
        
        # Add to document resources
        doc = self.editor.document()
        doc.addResource(QTextDocument.ResourceType.ImageResource, QUrl(url_str), image)
        
        # Create format
        fmt = QTextImageFormat()
        fmt.setName(url_str)
        fmt.setWidth(image.width())
        fmt.setHeight(image.height())
        fmt.setProperty(QTextImageFormat.Property.ImageAltText, f"{self.LATEX_PREFIX}{latex}")
        # Build-in vertical alignment property for inline images (Qt 6)
        fmt.setVerticalAlignment(QTextImageFormat.VerticalAlignment.AlignMiddle)
        
        # Insert
        cursor = self.editor.textCursor()
        cursor.insertImage(fmt)

    def render_all_math(self):
        """
        Scan document for $$...$$ blocks and replace them with rendered images.
        """
        doc_text = self.editor.toPlainText()
        
        # Finding all occurrences of $$...$$
        # We must be careful about modifying text while iterating.
        # We'll collect all matches first (start, end, content), then apply from back to front.
        
        import re
        # Pattern 1: $$ content $$ (Display Math, priority)
        # Pattern 2: $ content $ (Inline Math, stricter)
        # We search for $$...$$ first, process matches, then search $...$ in remaining text? 
        # Better: Single pattern or iterate carefully.
        
        # Regex explanation:
        # (?<!\$)\$\$(.*?)\$\$(?!\$)  Matches $$...$$ not preceded or followed by another $
        # OR
        # (?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)Matches $...$ (strict single $)
        
        # Combined pattern is complex. Let's do two passes or use a unified regex.
        # Unified: (\$\$(.*?)\$\$)|((?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$))
        
        pattern = re.compile(r'(\$\$.*?\$\$)|((?<!\$)\$(?!\$).*?(?<!\$)\$(?!\$))', re.DOTALL)
        
        matches = []
        for match in pattern.finditer(doc_text):
            matches.append(match)
            
        if not matches:
            QMessageBox.information(self.parent, "Math Render", "No math blocks found ($$...$$ or $...$).")
            return

        cursor = self.editor.textCursor()
        doc = self.editor.document()
        
        # Process in reverse order to preserve indices
        count = 0
        for match in reversed(matches):
            full_match = match.group(0)
            # Group 1 is $$, Group 2 is $
            if match.group(1): # Display math $$...$$
                latex = match.group(1).replace('$$', '').strip()
            elif match.group(2): # Inline math $...$
                 latex = match.group(2).replace('$', '').strip()
            else:
                continue

            start = match.start()
            end = match.end()
            
            # Render first to ensure validity
            image = MathRenderer.render_latex(latex, fontsize=14)
            if image:
                # Select the text range
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
                
                # Delete text? Or just overwrite with insert image?
                # insertImage replaces selection.
                
                # Prepare resource
                img_id = str(uuid.uuid4())
                url_str = f"docimg://math/{img_id}"
                doc.addResource(QTextDocument.ResourceType.ImageResource, QUrl(url_str), image)
                
                fmt = QTextImageFormat()
                fmt.setName(url_str)
                fmt.setWidth(image.width())
                fmt.setHeight(image.height())
                fmt.setProperty(QTextImageFormat.Property.ImageAltText, f"{self.LATEX_PREFIX}{latex}")
                # Align inline math with text
                fmt.setVerticalAlignment(QTextImageFormat.VerticalAlignment.AlignMiddle)
                
                cursor.insertImage(fmt)
                count += 1
        
        if count > 0:
            QMessageBox.information(self.parent, "Math Render", f"Rendered {count} equations.")
        else:
            QMessageBox.warning(self.parent, "Math Render", "Found blocks but failed to render them.")

    def extend_context_menu(self, menu: QMenu):
        """Add actions to context menu."""
        menu.addSeparator()
        menu.addAction(self.action_insert_math)
        
        # Check if cursor is on a math image
        cursor = self.editor.textCursor()
        fmt = cursor.charFormat()
        
        # Try to find image if cursor is adjacent
        if not fmt.isImageFormat():
            # Check left
            test_cursor = QTextCursor(cursor)
            test_cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
            if test_cursor.charFormat().isImageFormat():
                fmt = test_cursor.charFormat()
            else:
                 # Check right
                test_cursor = QTextCursor(cursor)
                test_cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
                if test_cursor.charFormat().isImageFormat():
                    fmt = test_cursor.charFormat()

        if fmt.isImageFormat():
            alt = fmt.property(QTextImageFormat.Property.ImageAltText)
            if alt and isinstance(alt, str) and alt.startswith(self.LATEX_PREFIX):
                menu.addAction(qta.icon("fa5s.edit", color="#1e293b"), "Edit Math", self.edit_math_at_cursor)

    def edit_math_at_cursor(self):
        """Edit the latex of the selected math image."""
        cursor = self.editor.textCursor()
        fmt = cursor.charFormat()
        
        # Similar logic to find image
        has_selection = False
        if not fmt.isImageFormat():
             test_cursor = QTextCursor(cursor)
             test_cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
             if test_cursor.charFormat().isImageFormat():
                 cursor = test_cursor
                 fmt = cursor.charFormat()
                 has_selection = True
             else:
                 test_cursor = QTextCursor(cursor)
                 test_cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
                 if test_cursor.charFormat().isImageFormat():
                     cursor = test_cursor
                     fmt = cursor.charFormat()
                     has_selection = True
        
        if fmt.isImageFormat():
            alt = fmt.property(QTextImageFormat.Property.ImageAltText)
            if alt and isinstance(alt, str) and alt.startswith(self.LATEX_PREFIX):
                latex = alt[len(self.LATEX_PREFIX):]
                
                text, ok = QInputDialog.getMultiLineText(
                    self.parent, 
                    "Edit Math", 
                    "Edit LaTeX code:",
                    latex
                )
                
                if ok and text:
                    # Select the image if not already
                    if not has_selection and not cursor.hasSelection():
                         # We know where the cursor is relative to image from the check above, 
                         # but honestly replacing current selection is safer if we select it properly.
                         # Let's rely on _insert_rendered_image inserting at 'cursor'.
                         # If we move 'cursor' to select the image first, insertImage overwrites it.
                         
                         # If we are strictly ON the image (cursor pos is right after it, and char format is it? No)
                         # Qt rich text images are 1 char.
                         pass
                    
                    # More robust selection logic:
                    # Ideally we identify exactly where the image is and select it.
                    # For now, let's assume the user Right-Clicked -> Context Menu.
                    # The Context Menu logic above *found* the format.
                    # We need to make sure 'self.editor.textCursor()' targets that same position for replacement.
                    
                    # Let's re-find and select
                    cleanup_cursor = self.editor.textCursor()
                    f = cleanup_cursor.charFormat()
                    if not f.isImageFormat():
                         # Try left
                         cleanup_cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
                         if not cleanup_cursor.charFormat().isImageFormat():
                             # Try right
                             cleanup_cursor.movePosition(QTextCursor.MoveOperation.Right) # Undo left
                             cleanup_cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor)
                    
                    if cleanup_cursor.charFormat().isImageFormat():
                        self.editor.setTextCursor(cleanup_cursor)
                        self.insert_math(text) # This will overwrite selection

