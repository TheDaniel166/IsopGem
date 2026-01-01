from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject

class FormulaWizardHandler(QObject):
    """
    Handles interactions with the Formula Wizard Dialog.
    Extracted from SpreadsheetWindow.
    """
    def __init__(self, window):
        super().__init__(window)
        self.window = window

    @property
    def model(self):
        """Get current model from window (avoids stale reference)."""
        return self.window.model

    @property
    def view(self):
        """Get view from window."""
        return self.window.view

    @property
    def formula_bar(self):
        """Get formula bar widget from window."""
        return self.window.formula_bar_widget

    def launch(self):
        """Launches the Function Wizard (two-stage flow)."""
        try:
            # Lazy import to avoid circular dependencies
            from ..formula_wizard import FormulaWizardDialog, FormulaArgumentDialog
            
            # Get engine from current model
            engine = getattr(self.model, 'formula_engine', None)
            
            # Stage 1: Function Selection
            wizard = FormulaWizardDialog(engine=engine, parent=self.window)
            if wizard.exec():
                # User accepted Stage 1
                selected_meta = wizard.get_selected_formula()
                if selected_meta:
                    # Stage 2: Argument Entry
                    arg_dialog = FormulaArgumentDialog(
                        metadata=selected_meta,
                        engine=engine,
                        parent=self.window
                    )
                    if arg_dialog.exec():
                        # Get final formula and commit
                        formula_text = arg_dialog.get_formula_text()
                        self._commit_wizard_formula(formula_text)
                        
        except ImportError as e:
            QMessageBox.warning(self.window, "Wizard Error", f"Formula Wizard component not found: {e}")
        except Exception as e:
            QMessageBox.critical(self.window, "Wizard Error", str(e))

    def _commit_wizard_formula(self, formula_text):
        """
        Receives formula from Wizard (e.g. "=SUM(A1:B2)") and inserts it.
        """
        # Set formula text in the formula bar
        self.formula_bar.setText(formula_text)
        # Trigger commit logic in window (writes to cell)
        self.window._on_formula_return()
        
    def _on_wizard_selection_change(self, selected, deselected):
        """
        Future expansion: If wizard allows selecting ranges while open.
        This logic was partly present in monolith but unused? 
        The Wizard was modal with exec(), so live selection requires non-modal or specific handling.
        For now, we preserve the placeholder structure.
        """
        pass
