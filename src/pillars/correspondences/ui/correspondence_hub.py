from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QToolBar, QFileDialog, QMessageBox, QInputDialog
)
from PyQt6.QtGui import QAction
from pillars.correspondences.ui.spreadsheet_window import SpreadsheetWindow
from pillars.correspondences.services.ingestion_service import IngestionService
from pillars.correspondences.repos.table_repository import TableRepository
from shared.database import get_db_session, SessionLocal

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
        layout.addWidget(self.table_list)

    def _load_tables(self):
        """Load existing tables from DB."""
        self.table_list.clear()
        with get_db_session() as session:
            repo = TableRepository(session)
            tables = repo.get_all()
            for table in tables:
                item = QListWidgetItem(f"{table.name} (ID: {table.id})")
                item.setData(100, table.id) # Store ID in user role
                self.table_list.addItem(item)

    def _new_table(self):
        name, ok = QInputDialog.getText(self, "New Tablet", "Name of the new work:")
        if ok and name:
            empty_data = IngestionService.create_empty()
            self._create_and_launch(name, empty_data)

    def _import_table(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Scroll", "", "Spreadsheets (*.csv *.xlsx *.xls)")
        if not path:
            return
            
        try:
            data = IngestionService.ingest_file(path)
            import os
            name = os.path.splitext(os.path.basename(path))[0]
            self._create_and_launch(name, data)
        except Exception as e:
            QMessageBox.critical(self, "Import Failed", str(e))

    def _create_and_launch(self, name, data):
        with get_db_session() as session:
            repo = TableRepository(session)
            table = repo.create(name, data)
            # We must refresh the list to see it
            self._load_tables()
            # Launch it
            self._launch_window(table.id, table.name, data)

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
