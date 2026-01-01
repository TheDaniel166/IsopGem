from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
from ...services.formula_helper import cell_address

try:
    from ..find_replace_dialog import FindReplaceDialog
except ImportError:
    # Handle relative import if moved differently or import directly
    from pillars.correspondences.ui.find_replace_dialog import FindReplaceDialog

class SearchHandler:
    """
    Handles internal search and replace logic for the Spreadsheet.
    Extracted from SpreadsheetWindow.
    """
    def __init__(self, window):
        self.window = window
        self._find_dialog = None

    @property
    def view(self):
        """Always fetch current view from window."""
        return self.window.view

    @property
    def model(self):
        """Always fetch current model from window."""
        return self.window.model

    @property
    def status_bar(self):
        """Always fetch status bar from window."""
        return self.window.status_bar

    def launch(self, mode="find"):
        if not self._find_dialog:
            self._find_dialog = FindReplaceDialog(self.window)
            self._find_dialog.find_next_requested.connect(self._on_find_next)
            self._find_dialog.find_all_requested.connect(self._on_find_all)
            self._find_dialog.replace_requested.connect(self._on_replace)
            self._find_dialog.replace_all_requested.connect(self._on_replace_all)
            self._find_dialog.navigation_requested.connect(self._on_navigate_to_result)
            
        if mode == "replace":
            self._find_dialog.show_replace_mode()
        else:
            self._find_dialog.show_find_mode()

    def _on_navigate_to_result(self, index):
        """Called when user clicks a result in the Find Dialog."""
        if index.isValid():
            self.view.setCurrentIndex(index)
            self.view.scrollTo(index)
            self.view.setFocus()

    def _find_matching_indexes(self, text, options, start_from=None, reverse=False):
        """Helper to iterate grid and yield matches."""
        case_sensitive = options.get("case_sensitive", False)
        match_entire = options.get("match_entire", False)
        target = text if case_sensitive else text.lower()
        
        rows = self.model.rowCount()
        cols = self.model.columnCount()
        
        all_indexes = []
        for r in range(rows):
            for c in range(cols):
                all_indexes.append(self.model.index(r, c))
                
        if start_from and start_from.isValid():
            try:
                start_idx = (start_from.row() * cols) + start_from.column()
                all_indexes = all_indexes[start_idx+1:] + all_indexes[:start_idx+1]
            except:
                pass
                 
        for idx in all_indexes:
            val = self.model.data(idx, Qt.ItemDataRole.DisplayRole)
            if val is None: val = ""
            val_str = str(val)
            check_val = val_str if case_sensitive else val_str.lower()
            
            match = False
            if match_entire:
                match = (check_val == target)
            else:
                match = (target in check_val)
                
            if match:
                yield idx

    def _on_find_next(self, text, options):
        current = self.view.currentIndex()
        gen = self._find_matching_indexes(text, options, start_from=current)
        try:
            next_idx = next(gen)
            self.view.setCurrentIndex(next_idx)
            self.view.scrollTo(next_idx)
        except StopIteration:
            QMessageBox.information(self.window, "Find", f"Cannot find '{text}'.")

    def _on_find_all(self, text, options):
        gen = self._find_matching_indexes(text, options, start_from=None)
        matches = list(gen)
        
        results_data = []
        
        for idx in matches:
            addr = cell_address(idx.row(), idx.column())
            val = str(self.model.data(idx, Qt.ItemDataRole.DisplayRole) or "")
            display = f"{addr}: {val}"
            results_data.append((display, idx))
            
        if self._find_dialog:
            self._find_dialog.show_results(results_data)

        if not matches:
             QMessageBox.information(self.window, "Find", f"Cannot find '{text}'.")
             return
             
        selection = self.view.selectionModel()
        selection.clearSelection()
        
        from PyQt6.QtCore import QItemSelection
        qt_selection = QItemSelection()
        for idx in matches:
            qt_selection.select(idx, idx)
            
        selection.select(qt_selection, selection.SelectionFlag.Select)
        
        # Use component status bar wrapper
        if hasattr(self.status_bar, 'show_message'):
            self.status_bar.show_message(f"Found {len(matches)} occurrences.", 5000)
        else:
             # Fallback if window passed statusbar widget vs component
             if hasattr(self.status_bar, 'showMessage'):
                 self.status_bar.showMessage(f"Found {len(matches)} occurrences.", 5000)

    def _on_replace(self, text, replacement, options):
        current = self.view.currentIndex()
        
        matches_current = False
        if current.isValid():
             case_sensitive = options.get("case_sensitive", False)
             match_entire = options.get("match_entire", False)
             val = str(self.model.data(current, Qt.ItemDataRole.DisplayRole) or "")
             target = text if case_sensitive else text.lower()
             check = val if case_sensitive else val.lower()
             
             if match_entire: matches_current = (check == target)
             else: matches_current = (target in check)
        
        if matches_current:
            val = str(self.model.data(current, Qt.ItemDataRole.DisplayRole) or "")
            
            if match_entire:
                new_val = replacement
            else:
                if not options.get("case_sensitive"):
                    import re
                    pattern = re.compile(re.escape(text), re.IGNORECASE)
                    new_val = pattern.sub(replacement, val)
                else:
                    new_val = val.replace(text, replacement)
            
            self.model.setData(current, new_val, Qt.ItemDataRole.EditRole)
            
        self._on_find_next(text, options)

    def _on_replace_all(self, text, replacement, options):
        gen = self._find_matching_indexes(text, options, start_from=None)
        matches = list(gen)
        
        if not matches:
            QMessageBox.information(self.window, "Replace", f"Cannot find '{text}'.")
            return
            
        self.model.undo_stack.beginMacro("Replace All")
        count = 0
        try:
            import re
            pattern = re.compile(re.escape(text), re.IGNORECASE) if not options.get("case_sensitive") else None
            
            for idx in matches:
                val = str(self.model.data(idx, Qt.ItemDataRole.DisplayRole) or "")
                
                if options.get("match_entire"):
                    new_val = replacement
                else:
                    if pattern:
                        new_val = pattern.sub(replacement, val)
                    else:
                        new_val = val.replace(text, replacement)
                        
                if val != new_val:
                    self.model.setData(idx, new_val, Qt.ItemDataRole.EditRole)
                    count += 1
        finally:
            self.model.undo_stack.endMacro()
            
        if hasattr(self.status_bar, 'show_message'):
             self.status_bar.show_message(f"Replaced {count} occurrences.", 5000)
