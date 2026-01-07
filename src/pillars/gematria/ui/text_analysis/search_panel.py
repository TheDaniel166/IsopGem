"""
Search Panel - The Value Finder.
Widget for searching text by gematria value with match list and export support.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QPushButton, QListWidget, QListWidgetItem, 
    QGroupBox, QMenu, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from shared.ui.theme import COLORS, get_exegesis_group_style, set_archetype

class SearchPanel(QWidget):
    """
    Widget for searching text by gematria value and displaying results.
    """
    search_requested = pyqtSignal(int, int, bool)  # value, max_words, is_global
    result_selected = pyqtSignal(int, int, int)   # start, end, doc_index (optional)
    save_matches_requested = pyqtSignal()
    export_requested = pyqtSignal()
    smart_filter_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        """
          init   logic.
        
        Args:
            parent: Description of parent.
        
        """
        super().__init__(parent)
        self.all_matches = []
        self.current_tab_index = -1
        self._setup_ui()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = QGroupBox("Search by Value")
        group.setStyleSheet(get_exegesis_group_style())
        group_layout = QVBoxLayout(group)
        
        # Inputs
        input_layout = QHBoxLayout()
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter value...")
        self.value_input.returnPressed.connect(self._on_search)
        
        self.max_words = QSpinBox()
        self.max_words.setRange(1, 9999)
        self.max_words.setValue(8)
        self.max_words.setToolTip("Max words in a phrase (1-9999)")
        
        search_btn = QPushButton("🔍 Find")
        search_btn.clicked.connect(self._on_search)
        set_archetype(search_btn, "seeker")
        
        input_layout.addWidget(QLabel("Value:"))
        input_layout.addWidget(self.value_input)
        input_layout.addWidget(search_btn)
        
        # Global Search Checkbox
        self.global_chk = QCheckBox("All Docs")
        self.global_chk.setToolTip("Search in all open documents")
        input_layout.addWidget(self.global_chk)
        
        group_layout.addLayout(input_layout)
        
        # Info label
        self.info_label = QLabel("Enter a value to search.")
        self.info_label.setStyleSheet(f"color: {COLORS['stone']}; font-size: 9pt;")
        group_layout.addWidget(self.info_label)
        
        # Results List
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self._on_item_clicked)
        group_layout.addWidget(self.results_list)
        
        # Actions
        actions_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_requested.emit)
        set_archetype(clear_btn, "destroyer")
        
        save_btn = QPushButton("💾 Save Matches")
        save_btn.clicked.connect(self.save_matches_requested.emit)
        set_archetype(save_btn, "scribe")
        
        export_btn = QPushButton("📤 Export")
        export_btn.clicked.connect(self._on_export)
        set_archetype(export_btn, "navigator")
        
        smart_btn = QPushButton("✨ Smart Filter")
        smart_btn.clicked.connect(self._on_smart_filter)
        set_archetype(smart_btn, "magus")
        
        actions_layout.addWidget(clear_btn)
        actions_layout.addWidget(save_btn)
        actions_layout.addWidget(export_btn)
        actions_layout.addWidget(smart_btn)
        group_layout.addLayout(actions_layout)
        
        layout.addWidget(group)
        
    def _on_search(self):
        val_str = self.value_input.text().strip()
        if not val_str or not val_str.isdigit():
            return
        # Hardcoded to 9999 as requested by user
        self.search_requested.emit(int(val_str), 9999, self.global_chk.isChecked())
        
    def _on_export(self):
        self.export_requested.emit()
        
    def _on_smart_filter(self):
        self.smart_filter_requested.emit()

    def set_active_tab(self, index: int):
        """
        Configure active tab logic.
        
        Args:
            index: Description of index.
        
        """
        self.current_tab_index = index
        self._refresh_results()

    def set_results(self, matches):
        """
        Set matches and refresh display.
        Args:
            matches: List of tuples (text, start, end, doc_title, tab_index)
        """
        self.all_matches = matches
        self._refresh_results()
        
    def _refresh_results(self):
        self.results_list.clear()
        
        # Filter by active tab
        if self.current_tab_index == -1:
            filtered = [] # No tab active? or show all? 
            # If no tab active, maybe show nothing.
        else:
            filtered = [m for m in self.all_matches if m[4] == self.current_tab_index]  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        
        total_count = len(self.all_matches)
        local_count = len(filtered)
        target_val = self.value_input.text()
        
        if not self.all_matches:
            self.info_label.setText("No matches found.")
        else:
            self.info_label.setText(f"Found {total_count} total ({local_count} in current tab)")
        
        if not filtered and total_count > 0:
            # Maybe show a helper item?
            pass
            
        for item_data in filtered:
            # item_data: (text, start, end, doc_title, tab_index)
            text, start, end, _doc_title, tab_index = item_data  # type: ignore[reportUnknownVariableType, reportUnusedVariable]
            
            label = f"{text} = {target_val}"
            # Doc title is redundant if we only show current tab, but kept for clarity if needed?
            # User said "only the active tab", so doc_title is implicitly the active doc.
            # We can remove it to clean up UI.
            # label += f" [{doc_title}]" 
                
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, (start, end, tab_index))
            self.results_list.addItem(item)
            
    def clear_results(self):
        """
        Clear results logic.
        
        """
        self.all_matches = []
        self.results_list.clear()
        self.info_label.setText("")
        
    send_to_tablet_requested = pyqtSignal(list)

    def _on_item_clicked(self, item):
        data = item.data(Qt.ItemDataRole.UserRole)
        if data:
            start, end, tab_index = data  # type: ignore[reportUnknownVariableType]
            self.result_selected.emit(start, end, tab_index)

    def contextMenuEvent(self, event):  # type: ignore[reportIncompatibleMethodOverride, reportMissingParameterType, reportUnknownParameterType]
        """Context menu for results."""
        if not self.results_list.itemAt(event.pos()):
            return
            
        menu = QMenu(self)
        send_action = QAction("Send Results to Emerald Tablet", self)
        send_action.triggered.connect(self._on_send_results)
        menu.addAction(send_action)
        menu.exec(event.globalPos())
        
    def _on_send_results(self):
        """Emit signal to send current filtered results to Tablet."""
        # Filter matches by current tab if needed, similar to display
        if self.current_tab_index == -1:
             # If no tab active, maybe send nothing or all? Logic in refresh uses all if -1?
             # refresh_results logic: if -1, filtered = [].
             # Let's use visible items from list widget to be true to WYSIWYG
             pass
        
        # Actually easier to just send self.all_matches filtered by current_tab_index
        filtered = []
        if self.current_tab_index != -1:
            filtered = [m for m in self.all_matches if m[4] == self.current_tab_index]  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
            
        if filtered:
            self.send_to_tablet_requested.emit(filtered)
            

