"""
Find Replace Dialog - The Seeker's Lens.
Non-modal dialog for searching and replacing text in spreadsheet cells.
"""
from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QCheckBox, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QGroupBox, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal

class FindReplaceDialog(QDialog):
    """
    Non-modal dialog for searching and replacing text in the spreadsheet.
    """
    find_next_requested = pyqtSignal(str, dict) # text, options
    find_all_requested = pyqtSignal(str, dict)
    replace_requested = pyqtSignal(str, str, dict) # find, replace, options
    replace_all_requested = pyqtSignal(str, str, dict) # find, replace, options
    
    navigation_requested = pyqtSignal(object) # raw_index (opaque)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find & Replace")
        self.setWindowFlags(Qt.WindowType.Window) # Independent window behavior (stays on top if configured)
        self.resize(350, 400) # Taller for results
        
        layout = QVBoxLayout(self)
        
        # Inputs
        grid = QGridLayout()
        
        grid.addWidget(QLabel("Find what:"), 0, 0)
        self.input_find = QLineEdit()
        grid.addWidget(self.input_find, 0, 1)
        
        grid.addWidget(QLabel("Replace with:"), 1, 0)
        self.input_replace = QLineEdit()
        grid.addWidget(self.input_replace, 1, 1)
        
        layout.addLayout(grid)
        
        # Options
        opt_group = QGroupBox("Options")
        opt_layout = QVBoxLayout(opt_group)
        self.chk_case = QCheckBox("Match case")
        self.chk_entire = QCheckBox("Match entire cell contents")
        opt_layout.addWidget(self.chk_case)
        opt_layout.addWidget(self.chk_entire)
        layout.addWidget(opt_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.btn_find_next = QPushButton("Find Next")
        self.btn_find_next.setDefault(True)
        self.btn_find_next.clicked.connect(self._on_find_next)
        
        self.btn_find_all = QPushButton("Find All")
        self.btn_find_all.clicked.connect(self._on_find_all)
        
        self.btn_replace = QPushButton("Replace")
        self.btn_replace.clicked.connect(self._on_replace)
        
        self.btn_replace_all = QPushButton("Replace All")
        self.btn_replace_all.clicked.connect(self._on_replace_all)
        
        btn_layout.addWidget(self.btn_find_next)
        btn_layout.addWidget(self.btn_find_all)
        btn_layout.addWidget(self.btn_replace)
        btn_layout.addWidget(self.btn_replace_all)
        
        layout.addLayout(btn_layout)
        
        # Results List (Initially Hidden?)
        # Let's keep it visible but empty
        self.lbl_results = QLabel("Results:")
        self.lbl_results.hide()
        layout.addWidget(self.lbl_results)
        
        self.result_list = QListWidget()
        self.result_list.hide()
        self.result_list.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.result_list)
        
    def show_find_mode(self):
        """Focus Find input."""
        self.input_find.setFocus()
        self.input_find.selectAll()
        self.show()
        
    def show_replace_mode(self):
        """Focus Replace input (but usually Find is first)."""
        self.input_replace.setFocus()
        self.input_replace.selectAll()
        self.show()

    def get_options(self):
        return {
            "case_sensitive": self.chk_case.isChecked(),
            "match_entire": self.chk_entire.isChecked()
        }
    
    def show_results(self, matches):
        """
        Populate the list widget.
        Matches: list of tuples (display_text, user_data)
        """
        self.result_list.clear()
        if matches:
            self.lbl_results.show()
            self.result_list.show()
            self.lbl_results.setText(f"Found {len(matches)} results:")
            
            for display_text, user_data in matches:
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, user_data)
                self.result_list.addItem(item)
        else:
            self.lbl_results.show()
            self.lbl_results.setText("No results found.")
            self.result_list.hide()

    def _on_find_next(self):
        text = self.input_find.text()
        if not text: return
        self.find_next_requested.emit(text, self.get_options())
        
    def _on_find_all(self):
        text = self.input_find.text()
        if not text: return
        self.find_all_requested.emit(text, self.get_options())
        
    def _on_replace(self):
        text = self.input_find.text()
        repl = self.input_replace.text()
        if not text: return
        self.replace_requested.emit(text, repl, self.get_options())
        
    def _on_replace_all(self):
        text = self.input_find.text()
        repl = self.input_replace.text()
        if not text: return
        self.replace_all_requested.emit(text, repl, self.get_options())
        
    def _on_item_clicked(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            self.navigation_requested.emit(data)
