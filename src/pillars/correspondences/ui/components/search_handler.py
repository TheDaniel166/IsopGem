from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
import logging
from ...services.formula_helper import cell_address

logger = logging.getLogger(__name__)

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

    def _find_matching_indexes(self, text, options, start_from=None, reverse=False):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """Helper to iterate grid and yield matches."""
        case_sensitive = options.get("case_sensitive", False)
        match_entire = options.get("match_entire", False)
        target = text if case_sensitive else text.lower()
        
        rows = self.model.rowCount()  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        cols = self.model.columnCount()  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        
        all_indexes = []
        for r in range(rows):
            for c in range(cols):
                all_indexes.append(self.model.index(r, c))  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
                
        if start_from and start_from.isValid():
            try:
                start_idx = (start_from.row() * cols) + start_from.column()  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
                all_indexes = all_indexes[start_idx+1:] + all_indexes[:start_idx+1]
            except (AttributeError, TypeError, ValueError) as e:
                logger.debug(
                    "SearchHandler: unable to compute start index (%s): %s",
                    type(e).__name__,
                    e,
                )
                 
        for idx in all_indexes:
            val = self.model.data(idx, Qt.ItemDataRole.DisplayRole)  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
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

    def _on_find_next(self, text, options):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        current = self.view.currentIndex()  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        gen = self._find_matching_indexes(text, options, start_from=current)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
        try:
            next_idx = next(gen)
            self.view.setCurrentIndex(next_idx)
            self.view.scrollTo(next_idx)
        except StopIteration:
            QMessageBox.information(self.window, "Find", f"Cannot find '{text}'.")

    def _on_find_all(self, text, options):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        gen = self._find_matching_indexes(text, options, start_from=None)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
        matches = list(gen)
        
        results_data = []
        
        for idx in matches:
            addr = cell_address(idx.row(), idx.column())  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            val = str(self.model.data(idx, Qt.ItemDataRole.DisplayRole) or "")  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            display = f"{addr}: {val}"
            results_data.append((display, idx))
            
        if self._find_dialog:
            self._find_dialog.show_results(results_data)

        if not matches:
             QMessageBox.information(self.window, "Find", f"Cannot find '{text}'.")
             return
             
        selection = self.view.selectionModel()  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        selection.clearSelection()
        
        from PyQt6.QtCore import QItemSelection
        qt_selection = QItemSelection()
        for idx in matches:
            qt_selection.select(idx, idx)
            
        selection.select(qt_selection, selection.SelectionFlag.Select)  # type: ignore[reportUnknownMemberType]
        
        # Use component status bar wrapper
        if hasattr(self.status_bar, 'show_message'):
            self.status_bar.show_message(f"Found {len(matches)} occurrences.", 5000)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        else:
             # Fallback if window passed statusbar widget vs component
             if hasattr(self.status_bar, 'showMessage'):
                 self.status_bar.showMessage(f"Found {len(matches)} occurrences.", 5000)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]

    def _on_replace(self, text, replacement, options):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        current = self.view.currentIndex()  # type: ignore[reportUnknownMemberType, reportUnknownVariableType]
        
        matches_current = False
        if current.isValid():
             case_sensitive = options.get("case_sensitive", False)
             match_entire = options.get("match_entire", False)
             val = str(self.model.data(current, Qt.ItemDataRole.DisplayRole) or "")  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
             target = text if case_sensitive else text.lower()
             check = val if case_sensitive else val.lower()
             
             if match_entire: matches_current = (check == target)
             else: matches_current = (target in check)
        
        if matches_current:
            val = str(self.model.data(current, Qt.ItemDataRole.DisplayRole) or "")  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
            
            if match_entire:
                new_val = replacement
            else:
                if not options.get("case_sensitive"):
                    import re
                    pattern = re.compile(re.escape(text), re.IGNORECASE)  # type: ignore[reportUnknownArgumentType, reportUnknownVariableType]
                    new_val = pattern.sub(replacement, val)
                else:
                    new_val = val.replace(text, replacement)
            
            self.model.setData(current, new_val, Qt.ItemDataRole.EditRole)
            
        self._on_find_next(text, options)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]

    def _on_replace_all(self, text, replacement, options):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        gen = self._find_matching_indexes(text, options, start_from=None)  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
        matches = list(gen)
        
        if not matches:
            QMessageBox.information(self.window, "Replace", f"Cannot find '{text}'.")
            return
            
        self.model.undo_stack.beginMacro("Replace All")  # type: ignore[reportUnknownMemberType]
        count = 0
        try:
            import re
            pattern = re.compile(re.escape(text), re.IGNORECASE) if not options.get("case_sensitive") else None  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType, reportUnknownVariableType]
            
            for idx in matches:
                val = str(self.model.data(idx, Qt.ItemDataRole.DisplayRole) or "")  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
                
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
            self.model.undo_stack.endMacro()  # type: ignore[reportUnknownMemberType]
            
        if hasattr(self.status_bar, 'show_message'):
             self.status_bar.show_message(f"Replaced {count} occurrences.", 5000)
