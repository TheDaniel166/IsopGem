from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QToolBar, QFileDialog, QMessageBox, QInputDialog, QMenu,
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QSpinBox
)
from PyQt6.QtCore import Qt, QPoint, QThread, QObject, pyqtSignal
from PyQt6.QtGui import QAction
from pillars.correspondences.ui.spreadsheet_window import SpreadsheetWindow
from pillars.correspondences.services.ingestion_service import IngestionService
from pillars.correspondences.repos.table_repository import TableRepository
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

        layout = QFormLayout(self)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name of the new work")
        layout.addRow("Name", self.name_input)

        self.rows_input = QSpinBox()
        self.rows_input.setRange(1, 1000)
        self.rows_input.setSingleStep(10)
        self.rows_input.setValue(100)
        layout.addRow("Rows", self.rows_input)

        self.cols_input = QSpinBox()
        self.cols_input.setRange(1, 1000)
        self.cols_input.setSingleStep(10)
        self.cols_input.setValue(50)
        layout.addRow("Columns", self.cols_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

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
        self.open_windows = [] # Keep references to prevent GC
        self._setup_ui()
        self._load_tables()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Toolbar
        self.toolbar = QToolBar()
        layout.addWidget(self.toolbar)
        
        act_new = QAction("New Scroll", self)
        act_new.triggered.connect(self._new_table)
        self.toolbar.addAction(act_new)
        
        act_import = QAction("Import (Excel/CSV)", self)
        act_import.triggered.connect(self._import_table)
        self.toolbar.addAction(act_import)
        
        act_refresh = QAction("Refresh Library", self)
        act_refresh.triggered.connect(self._load_tables)
        self.toolbar.addAction(act_refresh)
        
        # Library List
        self.table_list = QListWidget()
        self.table_list.itemDoubleClicked.connect(self._on_table_double_click)
        self.table_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.table_list)

    def _load_tables(self):
        """Load existing tables from DB."""
        self.table_list.clear()
        with get_db_session() as session:
            repo = TableRepository(session)
            tables = repo.get_all()
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
            repo = TableRepository(session)
            table = repo.create(name, data)
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
                repo = TableRepository(session)
                repo.update_name(table_id, new_name)
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
                repo = TableRepository(session)
                repo.delete(table_id)
            self._load_tables()

    def _on_table_double_click(self, item):
        table_id = item.data(100)
        
        # Fetch fresh data
        with get_db_session() as session:
            repo = TableRepository(session)
            table = repo.get_by_id(table_id)
            if table:
                self._launch_window(table.id, table.name, table.content)

    def _launch_window(self, table_id, name, content):
        # We need a persistent session for the window's repository interactions.
        # using get_db_session() context manager is not appropriate for long-lived objects.
        # We create a raw session using the factory.
        
        session = SessionLocal()
        repo = TableRepository(session)
        
        win = SpreadsheetWindow(table_id, name, content, repo)
        win._db_session = session # Keep alive reference
        
        # Clean up on close - session objects have a .close() method
        win.destroyed.connect(lambda: session.close())
        win.destroyed.connect(lambda: self.open_windows.remove(win) if win in self.open_windows else None)
        
        win.show()
        self.open_windows.append(win)
