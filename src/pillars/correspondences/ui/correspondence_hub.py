from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QFileDialog, 
    QMessageBox, QInputDialog, QMenu, QDialog, QDialogButtonBox, QFormLayout, 
    QLineEdit, QSpinBox, QLabel, QFrame, QPushButton, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint, QThread, QObject, pyqtSignal
from PyQt6.QtGui import QAction, QColor
from pillars.correspondences.ui.spreadsheet_window import SpreadsheetWindow
from pillars.correspondences.services.ingestion_service import IngestionService
from pillars.correspondences.services.table_service import TableService
from shared.database import get_db_session, SessionLocal


class _ImportWorker(QObject):
    """Background file ingestion to keep the UI responsive."""

    finished = pyqtSignal(str, dict)
    failed = pyqtSignal(str)

    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.path = path

    def run(self):
        import os
        try:
            data = IngestionService.ingest_file(self.path)
            name = os.path.splitext(os.path.basename(self.path))[0]
            self.finished.emit(name, data)
        except Exception as exc:
            self.failed.emit(str(exc))


class _NewTableDialog(QDialog):
    """Collect name and grid size for a new table."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Tablet")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background: #f8fafc;
            }
            QLabel {
                color: #1e293b;
                font-size: 10pt;
            }
            QLineEdit, QSpinBox {
                padding: 8px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background: white;
                font-size: 10pt;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #3b82f6;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 10pt;
                font-weight: 600;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title
        title = QLabel("✨ Create New Tablet")
        title.setStyleSheet("font-size: 16pt; font-weight: 700; color: #1e293b;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(12)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name of the new work")
        form.addRow("Name", self.name_input)

        self.rows_input = QSpinBox()
        self.rows_input.setRange(1, 1000)
        self.rows_input.setSingleStep(10)
        self.rows_input.setValue(100)
        form.addRow("Rows", self.rows_input)

        self.cols_input = QSpinBox()
        self.cols_input.setRange(1, 1000)
        self.cols_input.setSingleStep(10)
        self.cols_input.setValue(50)
        form.addRow("Columns", self.cols_input)

        layout.addLayout(form)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #64748b;
                border: 1px solid #e2e8f0;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton("Create Tablet")
        create_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        create_btn.clicked.connect(self.accept)
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)

    def get_values(self):
        return self.name_input.text().strip(), self.rows_input.value(), self.cols_input.value()


class CorrespondenceHub(QWidget):
    """
    The Emerald Tablet Hub.
    The Library of Correspondences. Launches Spreadsheet Windows.
    """
    def __init__(self, window_manager, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager
        self.open_windows = []
        self._setup_ui()
        self._load_tables()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 32, 40, 40)
        
        # Header
        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setSpacing(8)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("Emerald Tablet")
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 32pt;
                font-weight: 700;
                letter-spacing: -1px;
            }
        """)
        header_layout.addWidget(title_label)

        desc_label = QLabel("Library of Correspondences - Scrolls and Tablets")
        desc_label.setStyleSheet("""
            QLabel {
                color: #64748b;
                font-size: 12pt;
            }
        """)
        header_layout.addWidget(desc_label)
        
        layout.addWidget(header)
        
        # Action cards
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(16)
        
        new_card = self._create_action_card(
            "📜", "New Scroll", "Create a blank tablet", "#3b82f6", self._new_table
        )
        actions_layout.addWidget(new_card)
        
        import_card = self._create_action_card(
            "📥", "Import", "Import Excel/CSV file", "#10b981", self._import_table
        )
        actions_layout.addWidget(import_card)
        
        refresh_card = self._create_action_card(
            "🔄", "Refresh", "Reload library", "#8b5cf6", self._load_tables
        )
        actions_layout.addWidget(refresh_card)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Library section
        library_header = QLabel("Your Tablets")
        library_header.setStyleSheet("""
            QLabel {
                color: #475569;
                font-size: 14pt;
                font-weight: 600;
                margin-top: 8px;
            }
        """)
        layout.addWidget(library_header)
        
        # Library List with modern styling
        self.table_list = QListWidget()
        self.table_list.setStyleSheet("""
            QListWidget {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 8px;
                font-size: 11pt;
            }
            QListWidget::item {
                padding: 12px 16px;
                border-radius: 8px;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background: #f1f5f9;
            }
            QListWidget::item:selected {
                background: #dbeafe;
                color: #1d4ed8;
            }
        """)
        self.table_list.itemDoubleClicked.connect(self._on_table_double_click)
        self.table_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_list.customContextMenuRequested.connect(self._show_context_menu)
        
        # Add shadow to list
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 25))
        self.table_list.setGraphicsEffect(shadow)
        
        layout.addWidget(self.table_list)
    
    def _create_action_card(self, icon: str, title: str, desc: str, color: str, callback) -> QFrame:
        """Create a compact action card."""
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border: 1px solid #e2e8f0;
                border-radius: 10px;
            }}
            QFrame:hover {{
                border-color: {color};
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f1f5f9);
            }}
        """)
        card.setFixedSize(140, 100)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setOffset(0, 1)
        shadow.setColor(QColor(0, 0, 0, 20))
        card.setGraphicsEffect(shadow)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(4)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 20pt;
                background: transparent;
            }}
        """)
        card_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #1e293b;
                font-size: 10pt;
                font-weight: 600;
                background: transparent;
            }
        """)
        card_layout.addWidget(title_label)
        
        card_layout.addStretch()
        
        card.mousePressEvent = lambda e: callback()
        
        return card

    def _load_tables(self):
        """Load existing tables from DB."""
        self.table_list.clear()
        with get_db_session() as session:
            service = TableService(session)
            tables = service.list_tables()
            for table in tables:
                # Clean Display
                item = QListWidgetItem(table.name)
                item.setData(100, table.id)
                # Tooltip with Metadata
                c_time = table.created_at.strftime("%Y-%m-%d %H:%M") if table.created_at else "?"
                u_time = table.updated_at.strftime("%Y-%m-%d %H:%M") if table.updated_at else "?"
                tooltip = f"Name: {table.name}\nCreated: {c_time}\nUpdated: {u_time}\nID: {table.id}"
                item.setToolTip(tooltip)
                # Store full meta in custom role for easy properties access
                item.setData(101, tooltip)
                self.table_list.addItem(item)

    def _new_table(self):
        dlg = _NewTableDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            name, rows, cols = dlg.get_values()
            if not name:
                QMessageBox.warning(self, "Name required", "Please enter a name for the new table.")
                return
            empty_data = IngestionService.create_empty(rows=rows, cols=cols)
            self.receive_import(name, empty_data)

    def _import_table(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Scroll", "", "Spreadsheets (*.csv *.xlsx *.xls)")
        if not path:
            return

        # Spawn worker thread to avoid blocking UI during ingestion
        self._import_thread = QThread(self)
        self._import_worker = _ImportWorker(path)
        self._import_worker.moveToThread(self._import_thread)

        self._import_thread.started.connect(self._import_worker.run)
        self._import_worker.finished.connect(self._on_import_finished)
        self._import_worker.failed.connect(self._on_import_failed)

        # Ensure cleanup
        self._import_worker.finished.connect(self._import_thread.quit)
        self._import_worker.failed.connect(self._import_thread.quit)
        self._import_thread.finished.connect(self._import_worker.deleteLater)
        self._import_thread.finished.connect(self._import_thread.deleteLater)

        self._import_thread.start()

    def receive_import(self, name, data):
        """
        Public API: specific import method for other pillars.
        Creates a new table and launches it.
        """
        with get_db_session() as session:
            service = TableService(session)
            table = service.create_table(name, data)
            # We must refresh the list to see it
            self._load_tables()
            # Launch it
            self._launch_window(table.id, table.name, data)
            
            # Hide the Hub (Library) as we are now focusing on the specific Tablet (Scroll)
            self.hide()

    def _on_import_finished(self, name: str, data: dict):
        self.receive_import(name, data)

    def _on_import_failed(self, message: str):
        QMessageBox.critical(self, "Import Failed", message)



    def _show_context_menu(self, pos: QPoint):
        item = self.table_list.itemAt(pos)
        if not item: return
        
        menu = QMenu(self)
        act_rename = QAction("Rename", self)
        act_rename.triggered.connect(lambda: self._rename_table(item))
        menu.addAction(act_rename)
        
        act_delete = QAction("Delete", self)
        act_delete.triggered.connect(lambda: self._delete_table(item))
        menu.addAction(act_delete)
        
        menu.addSeparator()
        
        act_props = QAction("Properties", self)
        act_props.triggered.connect(lambda: self._show_properties(item))
        menu.addAction(act_props)
        
        menu.exec(self.table_list.mapToGlobal(pos))

    def _show_properties(self, item):
        meta = item.data(101)
        QMessageBox.information(self, "Scroll Properties", meta)

    def _rename_table(self, item):
        table_id = item.data(100)
        current_text = item.text()
        
        new_name, ok = QInputDialog.getText(self, "Rename Scroll", "New Name:", text=current_text)
        if ok and new_name:
            with get_db_session() as session:
                service = TableService(session)
                service.rename_table(table_id, new_name)
            self._load_tables()
            
    def _delete_table(self, item):
        table_id = item.data(100)
        name = item.text()
        
        reply = QMessageBox.question(
            self, "Delete Scroll", 
            f"Are you sure you want to destroy '{name}'?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            with get_db_session() as session:
                service = TableService(session)
                service.destoy_table(table_id)
            self._load_tables()

    def _on_table_double_click(self, item):
        table_id = item.data(100)
        
        # Fetch fresh data
        with get_db_session() as session:
            service = TableService(session)
            table = service.get_table(table_id)
            if table:
                self._launch_window(table.id, table.name, table.content)

    def _launch_window(self, table_id, name, content):
        # We need a persistent session for the window's repository interactions.
        # using get_db_session() context manager is not appropriate for long-lived objects.
        # We create a raw session using the factory.
        
        session = SessionLocal()
        service = TableService(session)
        
        win = SpreadsheetWindow(table_id, name, content, service)
        win._db_session = session # Keep alive reference
        
        # Clean up on close - session objects have a .close() method
        win.destroyed.connect(lambda: session.close())
        win.destroyed.connect(lambda: self.open_windows.remove(win) if win in self.open_windows else None)
        
        win.show()
        self.open_windows.append(win)
