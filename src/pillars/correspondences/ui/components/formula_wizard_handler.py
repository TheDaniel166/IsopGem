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
        self.model = window.model
        self.view = window.view
        self.formula_bar = window.formula_bar_widget # Access via component

    def launch(self):
        """Launches the Function Wizard."""
        try:
            # Lazy import to avoid circular dependencies if any
            from ..formula_wizard import FormulaWizardDialog
            
            wizard = FormulaWizardDialog(self.window)
            wizard.formula_selected.connect(self._commit_wizard_formula)
            # wizard.selection_requested.connect(...) # If wizard supports point-click selection
            
            # If we wanted live preview/selection we would need to connect
            # wizard.selection_changed -> self._on_wizard_selection_change
            
            wizard.exec()
        except ImportError:
            QMessageBox.warning(self.window, "Wizard Error", "Function Wizard component not found.")
        except Exception as e:
            QMessageBox.critical(self.window, "Wizard Error", str(e))

    def _commit_wizard_formula(self, formula_text):
        """
        Receives formula from Wizard (e.g. "=SUM(A1:B2)") and inserts it.
        """
        # If we just replace pure text:
        self.formula_bar.setText(formula_text)
        self.window._on_formula_return() # Trigger commit logic in window
        
    def _on_wizard_selection_change(self, selected, deselected):
        """
        Future expansion: If wizard allows selecting ranges while open.
        This logic was partly present in monolith but unused? 
        The Wizard was modal with exec(), so live selection requires non-modal or specific handling.
        For now, we preserve the placeholder structure.
        """
        pass
