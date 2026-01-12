"""
Mermaid Feature for Rich Text Editor.
Handles Mermaid diagram insertion, rendering, and management.
"""
import qtawesome as qta
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QIcon, QTextImageFormat, QTextDocument, QTextCursor
from PyQt6.QtWidgets import QMenu, QMessageBox, QTextEdit

from .mermaid_editor_dialog import MermaidEditorDialog

from .webview_mermaid_renderer import WebViewMermaidRenderer as MermaidRenderer
import uuid

class MermaidFeature:
    """
    Manages Mermaid diagram operations in the editor.
    """
    
    MERMAID_PREFIX = "MERMAID:"
    
    def __init__(self, editor: QTextEdit, parent):
        self.editor = editor # SafeTextEdit
        self.parent = parent # RichTextEditor
        self._setup_actions()
        
    def _setup_actions(self):
        """Initialize actions."""
        self.action_insert_mermaid = QAction("Insert Diagram", self.parent)
        self.action_insert_mermaid.setIcon(qta.icon("fa5s.project-diagram", color="#1e293b"))
        self.action_insert_mermaid.setToolTip("Insert Mermaid Diagram")
        self.action_insert_mermaid.triggered.connect(self.insert_mermaid_dialog)
        
        self.action_render_doc = QAction("Render All Diagrams", self.parent)
        self.action_render_doc.setIcon(qta.icon("fa5s.magic", color="#1e293b"))
        self.action_render_doc.setToolTip("Find and render all ```mermaid...``` blocks")
        self.action_render_doc.triggered.connect(self.render_all_mermaid)

    def insert_mermaid_dialog(self):
        """Show the Mermaid Editor dialog for new diagram."""
        dialog = MermaidEditorDialog(self.parent)
        if dialog.exec():
            code = dialog.get_code()
            if code:
                # Use standard flow: get image from renderer (dialog returns rendered image)
                image = dialog.get_image()
                if image:
                    self._insert_rendered_image(image, code)
                else:
                    self.insert_mermaid(code)

    def edit_mermaid_at_cursor(self):
        cursor = self.editor.textCursor()
        # If the cursor is just to the right of the image (common after clicking it)
        if not cursor.charFormat().isImageFormat():
            cursor.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.KeepAnchor)
        
        fmt = cursor.charFormat()
        if fmt.isImageFormat():
            alt = fmt.property(QTextImageFormat.Property.ImageAltText)
            if alt and alt.startswith(self.MERMAID_PREFIX):
                code = alt[len(self.MERMAID_PREFIX):]
                dialog = MermaidEditorDialog(self.parent, initial_code=code)
                if dialog.exec():
                    new_code = dialog.get_code()
                    if new_code:
                        # The cursor now has the image selected. 
                        # Calling insert_mermaid will overwrite the selected image.
                        self.editor.setTextCursor(cursor)
                        
                        image = dialog.get_image()
                        if image:
                            self._insert_rendered_image(image, new_code)
                        else:
                            self.insert_mermaid(new_code)

    def insert_mermaid(self, code: str):
        """Render and insert mermaid image at cursor."""
        # Show a "rendering..." status or just block? 
        # Since it's network request, blocking UI for 100-200ms is "okay" but 5s is bad.
        # Ideally threading, but for MVP keep it simple (synchronous).
        
        try:
             # Basic validity check (very loose)
            if not code.strip():
                return

            image = MermaidRenderer.render_mermaid(code)
            
            if image:
                self._insert_rendered_image(image, code)
            else:
                QMessageBox.warning(self.parent, "Rendering Error", 
                                  "Could not render Mermaid diagram.\nCheck your internet connection and syntax.")
        except Exception as e:
             QMessageBox.critical(self.parent, "Error", str(e))

    def _insert_rendered_image(self, image, code: str):
        """Insert the QImage into the document."""
        # Generate unique URL for the resource
        img_id = str(uuid.uuid4())
        url_str = f"docimg://mermaid/{img_id}"
        
        # Add to document resources
        doc = self.editor.document()
        doc.addResource(QTextDocument.ResourceType.ImageResource, QUrl(url_str), image)
        
        # Create format
        fmt = QTextImageFormat()
        fmt.setName(url_str)
        fmt.setWidth(image.width())
        fmt.setHeight(image.height())
        # Store original code in AltText for editing
        fmt.setProperty(QTextImageFormat.Property.ImageAltText, f"{self.MERMAID_PREFIX}{code}")
        # Build-in vertical alignment property for inline images (Qt 6)
        fmt.setVerticalAlignment(QTextImageFormat.VerticalAlignment.AlignMiddle)
        
        # Insert
        cursor = self.editor.textCursor()
        cursor.insertImage(fmt)

    def render_all_mermaid(self, silent: bool = False):
        """
        Scan document for ```mermaid ... ``` blocks and replace them with rendered images.

        Args:
            silent: If True, suppress dialog messages (for auto-render)
        """
        doc_text = self.editor.toPlainText()

        import re
        # Pattern 1: Standard Markdown ```mermaid ... ```
        # Pattern 2: Bare Start Keywords (e.g. "graph TD") until double newline?
        # A bit risky to auto-detect bare text, but user requested it.
        # Let's support:
        # 1. ```mermaid ... ```
        # 2. ``` ... ``` where content starts with standard mermaid keywords?
        # 3. Just `graph TD...` is hard to delimit end without knowing context.

        # User screenshot shows:
        # graph TD
        # A[...] --> B[...]

        # We can try to match blocks that start with known keywords and end with double newline.
        # Keywords: graph, sequenceDiagram, classDiagram, stateDiagram, erDiagram, pie, gantt

        # Keywords: graph, sequenceDiagram, classDiagram, stateDiagram, erDiagram, pie, gantt

        keywords = r'(?:graph|sequenceDiagram|classDiagram|stateDiagram(?:-v2)?|erDiagram|pie|gantt|mindmap|timeline)'

        # Updated to be Case-Sensitive to avoid matching English prose like "Graph Traversal"
        keywords = r'(?:graph|flowchart|sequenceDiagram|classDiagram|stateDiagram(?:-v2)?|erDiagram|pie|gantt|mindmap|timeline|gitGraph|c4Context)'

        # Refined Bare Block Logic:
        # Match a line starting with keyword, then subsequent non-empty lines.
        # Stops at first empty line.

        # Refined Bare Block Pattern
        # 1. Start with a keyword (graph, flow, etc.)
        # 2. Match content, allowing single newlines.
        # 3. Stop at double newline OR start of prose (Capitalized word).

        pattern = re.compile(
            r'(```mermaid(.*?)```)'                   # Group 1 & 2: Explicit
            r'|'
            r'(```\s*(' + keywords + r'.*?)```)'      # Group 3 & 4: Generic Fence
            r'|'
            # Group 5: Bare Block
            # Starts with new line or start of string.
            # Optional indentation [ \t]*.
            # Keyword word boundary.
            # Match characters sparingly until positive lookahead.
            r'((?:^|\n)[ \t]*(?:' + keywords + r')\b'
            r'(?:(?!\n\n).)*?)'                       # Match everything UNTIL a double newline
            r'(?=\n\n|\n[A-Z][a-z]+|\Z)',             # Stop at double-nl, capitalized sentence, or EOF
            re.DOTALL | re.MULTILINE
            # REMOVED re.IGNORECASE to prevent matching "Graph" vs "graph"
        )



        matches = []
        for match in pattern.finditer(doc_text):
            matches.append(match)

        if not matches:
            if not silent:
                QMessageBox.information(self.parent, "Mermaid Render", "No mermaid blocks found (```mermaid ... ```).")
            return

        cursor = self.editor.textCursor()
        # Process in reverse order to preserve indices
        count = 0
        for match in reversed(matches):
            code = ""
            # Determine which group matched
            # Group 2 (Standard Content)
            if match.group(2): 
                code = match.group(2).strip()
            # Group 4 (Generic Fence Content)
            elif match.group(4):
                code = match.group(4).strip()
            # Group 5 (Bare Block Content)
            elif match.group(5):
                code = match.group(5).strip()
            else:
                continue

            if not code:
                continue
            
            start = match.start()
            end = match.end()
            
            # For bare blocks, if they start with newline (Group 5), start++ to not eat the previous newline
            # Re-implement start shift logic safely
            if match.group(5) and match.group(5).startswith('\n'):
                 start += 1
            
            # Render
            image = MermaidRenderer.render_mermaid(code)
            
            if image:
                # Select the text range
                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.MoveMode.KeepAnchor)
                
                # Insert
                self._insert_rendered_image_at_cursor(image, code, cursor)
                count += 1
        
        if not silent:
            if count > 0:
                QMessageBox.information(self.parent, "Mermaid Render", f"Rendered {count} diagrams.")
            else:
                QMessageBox.warning(self.parent, "Mermaid Render", "Found blocks but failed to render them.")

    def _insert_rendered_image_at_cursor(self, image, code: str, cursor: QTextCursor):
        """Helper to insert image at specific cursor."""
        # Generate unique URL for the resource
        img_id = str(uuid.uuid4())
        url_str = f"docimg://mermaid/{img_id}"
        
        # Add to document resources
        doc = self.editor.document()
        doc.addResource(QTextDocument.ResourceType.ImageResource, QUrl(url_str), image)
        
        # Create format
        fmt = QTextImageFormat()
        fmt.setName(url_str)
        fmt.setWidth(image.width())
        fmt.setHeight(image.height())
        # Store original code in AltText for editing
        fmt.setProperty(QTextImageFormat.Property.ImageAltText, f"{self.MERMAID_PREFIX}{code}")
        fmt.setVerticalAlignment(QTextImageFormat.VerticalAlignment.AlignMiddle)
        
        # Insert
        cursor.insertImage(fmt)


    def extend_context_menu(self, menu: QMenu):
        """Add actions to context menu."""
        
        # Check if cursor is on a mermaid image
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
            if alt and isinstance(alt, str) and alt.startswith(self.MERMAID_PREFIX):
                menu.addSeparator()
                menu.addAction(qta.icon("fa5s.edit", color="#1e293b"), "Edit Diagram", self.edit_mermaid_at_cursor)


