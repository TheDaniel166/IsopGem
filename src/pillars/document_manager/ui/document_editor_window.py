"""
Document Editor Window - The Scribe's Sanctum.
Main window for rich text document editing with file I/O, printing, and search capabilities.
"""
import os
from typing import Optional, Any
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
    QMessageBox, QMenuBar, QDialog, QListWidget, 
    QLineEdit, QDialogButtonBox, QListWidgetItem, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence, QCloseEvent
from PyQt6.QtPrintSupport import QPrinter
from .rich_text_editor import RichTextEditor
from pillars.document_manager.services.document_service import document_service_context
from pillars.document_manager.models.document import Document

class DocumentEditorWindow(QMainWindow):
    """Window for editing documents using the RichTextEditor."""
    
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        Returns:
            Result of __init__ operation.
        """
        super().__init__(parent)
        self.setWindowTitle("Document Editor")
        self.resize(1000, 800)
        
        # State
        self.current_file = None
        self.current_doc_model = None # Database model if loaded from DB
        self.is_modified = False
        
        # Setup Save Directory
        # Assuming app is run from project root, create 'saved_documents' there
        self.save_dir = Path(os.getcwd()) / "saved_documents"
        self.save_dir.mkdir(exist_ok=True)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # ═══════════════════════════════════════════════════════════════════════
        # Match Navigator Bar (hidden by default)
        # ═══════════════════════════════════════════════════════════════════════
        self.match_nav_bar = QFrame()
        self.match_nav_bar.setObjectName("MatchNavBar")
        self.match_nav_bar.setStyleSheet("""
            QFrame#MatchNavBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fef3c7, stop:1 #fcd34d);
                border-bottom: 2px solid #f59e0b;
                padding: 8px 16px;
            }
        """)
        self.match_nav_bar.hide()
        
        nav_layout = QHBoxLayout(self.match_nav_bar)
        nav_layout.setContentsMargins(16, 8, 16, 8)
        nav_layout.setSpacing(12)
        
        self.nav_search_label = QLabel("")
        self.nav_search_label.setStyleSheet("font-weight: bold; color: #92400e; font-size: 11pt;")
        nav_layout.addWidget(self.nav_search_label)
        
        self.nav_counter_label = QLabel("0 of 0")
        self.nav_counter_label.setStyleSheet("color: #78350f; font-size: 11pt;")
        nav_layout.addWidget(self.nav_counter_label)
        
        nav_layout.addStretch()
        
        # Navigator style (Void Slate)
        nav_btn_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #64748b, stop:1 #475569);
                border: 1px solid #334155;
                color: white;
                font-size: 10pt;
                font-weight: 600;
                border-radius: 6px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #94a3b8, stop:1 #64748b);
            }
            QPushButton:pressed {
                background: #475569;
            }
        """
        
        self.btn_prev_match = QPushButton("◀ Prev")
        self.btn_prev_match.setStyleSheet(nav_btn_style)
        self.btn_prev_match.setShortcut("Shift+F3")
        self.btn_prev_match.clicked.connect(self._on_prev_match)
        nav_layout.addWidget(self.btn_prev_match)
        
        self.btn_next_match = QPushButton("Next ▶")
        self.btn_next_match.setStyleSheet(nav_btn_style)
        self.btn_next_match.setShortcut("F3")
        self.btn_next_match.clicked.connect(self._on_next_match)
        nav_layout.addWidget(self.btn_next_match)
        
        btn_close_nav = QPushButton("✕")
        btn_close_nav.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #92400e;
                font-size: 14pt;
                font-weight: bold;
                padding: 4px 8px;
            }
            QPushButton:hover {
                color: #dc2626;
            }
        """)
        btn_close_nav.clicked.connect(self._hide_match_navigator)
        nav_layout.addWidget(btn_close_nav)
        
        layout.addWidget(self.match_nav_bar)
        
        # ═══════════════════════════════════════════════════════════════════════
        # Mode Toggle Bar (View/Edit mode indicator)
        # ═══════════════════════════════════════════════════════════════════════
        self.is_read_only = False
        
        self.mode_bar = QFrame()
        self.mode_bar.setObjectName("ModeBar")
        self.mode_bar.hide()  # Only shown when document loaded in read-only
        
        mode_layout = QHBoxLayout(self.mode_bar)
        mode_layout.setContentsMargins(16, 8, 16, 8)
        mode_layout.setSpacing(12)
        
        self.mode_icon_label = QLabel("🔒")
        self.mode_icon_label.setStyleSheet("font-size: 16pt;")
        mode_layout.addWidget(self.mode_icon_label)
        
        self.mode_text_label = QLabel("View Mode")
        self.mode_text_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        mode_layout.addWidget(self.mode_text_label)
        
        mode_layout.addStretch()
        
        self.btn_toggle_mode = QPushButton("✏️ Enable Editing")
        self.btn_toggle_mode.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
                border: 1px solid #1d4ed8;
                color: white;
                font-size: 10pt;
                font-weight: 600;
                border-radius: 6px;
                padding: 6px 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #60a5fa, stop:1 #3b82f6);
            }
            QPushButton:pressed {
                background: #2563eb;
            }
        """)
        self.btn_toggle_mode.clicked.connect(self._toggle_edit_mode)
        mode_layout.addWidget(self.btn_toggle_mode)
        
        self._update_mode_bar_style()
        layout.addWidget(self.mode_bar)
        
        # Rich Text Editor
        self.editor = RichTextEditor()
        self.editor.text_changed.connect(self._on_text_changed)
        self.editor.wiki_link_requested.connect(self._show_wiki_link_selector)
        layout.addWidget(self.editor)
        
        self._init_file_menu()
        self._update_title()

    def _show_wiki_link_selector(self) -> None:
        """Show a dialog to select a document to link."""
        try:
            with document_service_context() as service:
                docs = service.get_all_documents_metadata()
        except Exception as e:
            print(f"Error fetching docs: {e}")
            return

        # Create a simple selection dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Insert Link")
        dialog.resize(400, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Filter
        filter_input = QLineEdit()
        filter_input.setPlaceholderText("Search documents...")
        layout.addWidget(filter_input)
        
        # List
        list_widget = QListWidget()
        for doc in docs:
            item = QListWidgetItem(f"{doc.title} (ID: {doc.id})")
            item.setData(Qt.ItemDataRole.UserRole, doc)
            list_widget.addItem(item)
        layout.addWidget(list_widget)
        
        # Filter logic
        def filter_items(text):
            """
            Filter items logic.
            
            Args:
                text: Description of text.
            
            """
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                item.setHidden(text.lower() not in item.text().lower())
        
        filter_input.textChanged.connect(filter_items)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        # Handle selection
        def on_item_double_clicked(item):
            """
            Handle item double clicked logic.
            
            Args:
                item: Description of item.
            
            """
            dialog.accept()
            
        list_widget.itemDoubleClicked.connect(on_item_double_clicked)
        
        if dialog.exec():
            selected_items = list_widget.selectedItems()
            if selected_items:
                doc = selected_items[0].data(Qt.ItemDataRole.UserRole)
                self._insert_wiki_link(doc)

    def _insert_wiki_link(self, doc: Document) -> None:
        """Insert the wiki link into the editor."""
        # The editor cursor is currently after '[[', so we just append the title and ']]'
        self.editor.editor.insertPlainText(f"{doc.title}]]")

    def _init_file_menu(self) -> None:
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        # New
        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_document)
        file_menu.addAction(new_action)
        
        # Open
        open_action = QAction("Open...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_document)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Save
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_document)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_as_document)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # Export PDF
        export_pdf_action = QAction("Export PDF...", self)
        export_pdf_action.triggered.connect(self.export_pdf)
        file_menu.addAction(export_pdf_action)

    def _on_text_changed(self) -> None:
        if not self.is_modified:
            self.is_modified = True
            self._update_title()

    def _update_title(self) -> None:
        title = "Document Editor"
        if self.current_file:
            title += f" - {self.current_file.name}"
        elif self.current_doc_model:
            title += f" - {self.current_doc_model.title} (DB)"
        else:
            title += " - Untitled"
            
        if self.is_modified:
            title += "*"
            
        self.setWindowTitle(title)

    def load_document_model(self, doc: Document, search_term: Optional[str] = None, restored_html: Optional[str] = None, read_only: bool = False) -> None:
        """Load a document from the database model.
        
        Args:
            doc: Document model object
            search_term: Optional search term to highlight
            restored_html: Optional pre-restored HTML with images (from get_document_with_images)
            read_only: If True, open in read-only view mode
        """
        if not self._check_unsaved_changes():
            return

        self.current_doc_model = doc
        self.current_file = None
        
        # Use restored_html if provided (has images restored from docimg:// references)
        # Otherwise fall back to raw_content or content
        if restored_html:
            content = restored_html
        else:
            content = doc.raw_content if doc.raw_content else doc.content
        
        # If we have raw content, it's likely HTML (from our parser)
        # or if the file type is explicitly HTML
        if restored_html or doc.raw_content or doc.file_type == 'html':
            self.editor.set_html(content or '')
        else:
            self.editor.set_text(content or '')
            
        self.is_modified = False
        self._update_title()
        
        # Show Match Navigator if search term provided
        if search_term:
            match_count = self.editor.find_all_matches(search_term)
            if match_count > 0:
                self.nav_search_label.setText(f'"{search_term}"')
                self._update_match_counter()
                self.match_nav_bar.show()
            else:
                self.match_nav_bar.hide()
        else:
            self.match_nav_bar.hide()
        
        # Apply read-only mode if requested
        if read_only:
            self._set_read_only_mode(True)
        else:
            self._set_read_only_mode(False)
            self.mode_bar.hide()
    
    def _set_read_only_mode(self, read_only: bool) -> None:
        """Set the editor to read-only or edit mode."""
        self.is_read_only = read_only
        self.editor.editor.setReadOnly(read_only)
        
        if read_only:
            self.mode_icon_label.setText("🔒")
            self.mode_text_label.setText("View Mode")
            self.btn_toggle_mode.setText("✏️ Enable Editing")
            self.mode_bar.setStyleSheet("""
                QFrame#ModeBar {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e0e7ff, stop:1 #c7d2fe);
                    border-bottom: 2px solid #6366f1;
                }
            """)
            self.mode_text_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #3730a3;")
        else:
            self.mode_icon_label.setText("✏️")
            self.mode_text_label.setText("Edit Mode")
            self.btn_toggle_mode.setText("🔒 View Only")
            self.mode_bar.setStyleSheet("""
                QFrame#ModeBar {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #dcfce7, stop:1 #bbf7d0);
                    border-bottom: 2px solid #22c55e;
                }
            """)
            self.mode_text_label.setStyleSheet("font-weight: bold; font-size: 11pt; color: #166534;")
        
        self.mode_bar.show()
        self._update_mode_bar_style()
    
    def _toggle_edit_mode(self) -> None:
        """Toggle between read-only and edit modes."""
        self._set_read_only_mode(not self.is_read_only)
    
    def _update_mode_bar_style(self) -> None:
        """Update mode bar button style based on current mode."""
        if self.is_read_only:
            self.btn_toggle_mode.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
                    border: 1px solid #1d4ed8;
                    color: white;
                    font-size: 10pt;
                    font-weight: 600;
                    border-radius: 6px;
                    padding: 6px 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #60a5fa, stop:1 #3b82f6);
                }
            """)
        else:
            self.btn_toggle_mode.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #64748b, stop:1 #475569);
                    border: 1px solid #334155;
                    color: white;
                    font-size: 10pt;
                    font-weight: 600;
                    border-radius: 6px;
                    padding: 6px 14px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #94a3b8, stop:1 #64748b);
                }
            """)
    
    def _on_prev_match(self) -> None:
        """Navigate to previous match."""
        self.editor.find_previous()
        self._update_match_counter()
    
    def _on_next_match(self) -> None:
        """Navigate to next match."""
        self.editor.find_next()
        self._update_match_counter()
    
    def _update_match_counter(self) -> None:
        """Update the match counter label."""
        current, total = self.editor.get_match_info()
        self.nav_counter_label.setText(f"{current} of {total}")
    
    def _hide_match_navigator(self) -> None:
        """Hide the match navigator and clear search."""
        self.match_nav_bar.hide()
        self.editor.clear_search()

    def _check_unsaved_changes(self) -> bool:
        # In read-only mode, no changes are possible - skip dialog
        if self.is_read_only:
            return True
            
        if self.is_modified:
            reply = QMessageBox.question(
                self, 
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                return self.save_document()
            elif reply == QMessageBox.StandardButton.Cancel:
                return False
        return True

    def new_document(self) -> None:
        """
        New document logic.
        
        Returns:
            Result of new_document operation.
        """
        if not self._check_unsaved_changes():
            return
            
        self.editor.clear()
        self.current_file = None
        self.is_modified = False
        self._update_title()

    def open_document(self) -> None:
        """
        Open document logic.
        
        Returns:
            Result of open_document operation.
        """
        if not self._check_unsaved_changes():
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            str(self.save_dir),
            "Markdown (*.md);;HTML Files (*.html);;Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            path = Path(file_path)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if path.suffix == '.html':
                    self.editor.set_html(content)
                elif path.suffix == '.md':
                    self.editor.set_markdown(content)
                else:
                    self.editor.set_text(content)
                    
                self.current_file = path
                self.is_modified = False
                self._update_title()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")

    def save_document(self) -> bool:
        """
        Save document logic.
        
        Returns:
            Result of save_document operation.
        """
        if self.current_doc_model:
            try:
                with document_service_context() as service:
                    # Update content
                    # Note: We are saving HTML as raw_content. 
                    # We should ideally strip tags for 'content' (searchable text)
                    html_content = self.editor.get_html()
                    plain_text = self.editor.get_text()
                    
                    service.update_document(
                        self.current_doc_model.id,
                        content=plain_text,
                        raw_content=html_content
                    )
                
                self.is_modified = False
                self._update_title()
                QMessageBox.information(self, "Success", "Document saved to database.")
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save to database: {str(e)}")
                return False

        if not self.current_file:
            return self.save_as_document()
            
        try:
            if self.current_file.suffix == '.md':
                content = self.editor.get_markdown()
            elif self.current_file.suffix == '.html':
                content = self.editor.get_html()
            else:
                content = self.editor.get_text()

            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.is_modified = False
            self._update_title()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
            return False

    def save_as_document(self) -> bool:
        """
        Save as document logic.
        
        Returns:
            Result of save_as_document operation.
        """
        file_path, filter_used = QFileDialog.getSaveFileName(
            self,
            "Save Document As",
            str(self.save_dir),
            "Markdown (*.md);;HTML Files (*.html);;All Files (*)"
        )
        
        if file_path:
            # Ensure extension
            valid_exts = ['.html', '.md']
            if not any(file_path.endswith(ext) for ext in valid_exts):
                # Default to whatever matches the filter or just md if unsure
                if "Markdown" in filter_used:
                    file_path += '.md'
                else:
                    file_path += '.html'
                
            self.current_file = Path(file_path)
            return self.save_document()
        return False

    def export_pdf(self) -> None:
        """Export the current document to PDF."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export PDF",
            str(self.save_dir),
            "PDF Files (*.pdf)"
        )

        if file_path:
            if not file_path.endswith('.pdf'):
                file_path += '.pdf'

            try:
                printer = QPrinter(QPrinter.PrinterMode.HighResolution)
                printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                printer.setOutputFileName(file_path)
                
                # Print the content of the editor to the printer (PDF)
                self.editor.editor.print(printer)
                
                QMessageBox.information(self, "Success", f"Document exported successfully to:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export PDF: {str(e)}")

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Closeevent logic.
        
        Args:
            event: Description of event.
        
        Returns:
            Result of closeEvent operation.
        """
        if not self._check_unsaved_changes():
            event.ignore()
        else:
            event.accept()