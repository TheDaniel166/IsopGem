"""
Reusable dialog for saving gematria calculations.
Handles notes input, tags input, and saving to the calculation service.
"""
from PyQt6.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QWidget
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from pillars.gematria.services.calculation_service import CalculationService


class SaveCalculationDialog:
    """
    Reusable dialog for saving gematria calculations with notes and tags.
    
    This provides a consistent save experience across all windows
    (Gematria Calculator, Exegesis, etc.)
    """
    
    @staticmethod
    def save_calculation(
        parent: QWidget,
        text: str,
        value: int,
        calculator,
        breakdown: Optional[List[tuple[str, int]]] = None,
        source: str = "",
        default_notes: str = "",
        silent: bool = False
    ) -> bool:
        """
        Show dialogs to save a calculation to the database.
        
        Args:
            parent: Parent widget for dialogs
            text: The text that was calculated
            value: The calculated gematria value
            calculator: The calculator used (for method name)
            breakdown: Optional letter-by-letter breakdown
            source: Optional source description (e.g., "Exegesis Tool", "Book 1:1")
            default_notes: Pre-filled notes text
            silent: If True, save without showing dialogs (uses defaults)
            
        Returns:
            True if saved successfully, False if cancelled or error
        """
        if not text or calculator is None:
            return False
        
        # Import here to avoid circular dependency
        from pillars.gematria.services.calculation_service import CalculationService
        calculation_service = CalculationService()
        
        if silent:
            # Silent save with defaults
            try:
                calculation_service.save_calculation(
                    text=text,
                    value=value,
                    calculator=calculator,
                    breakdown=breakdown or [],
                    notes=default_notes,
                    tags=[],
                    source=source
                )
                return True
            except Exception:
                return False
        
        # Get notes from user
        notes, ok = QInputDialog.getMultiLineText(
            parent,
            "Save Calculation",
            f"Saving: {text} = {value}\n\nNotes (optional):",
            default_notes
        )
        
        if not ok:
            return False
        
        # Get tags from user
        tags_str, ok = QInputDialog.getText(
            parent,
            "Add Tags",
            "Tags (comma-separated, optional):",
            QLineEdit.EchoMode.Normal,
            ""
        )
        
        if not ok:
            tags_str = ""
        
        # Parse tags
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        
        # Save to database
        try:
            record = calculation_service.save_calculation(
                text=text,
                value=value,
                calculator=calculator,
                breakdown=breakdown or [],
                notes=notes,
                tags=tags,
                source=source
            )
            
            QMessageBox.information(
                parent,
                "Saved",
                f"Calculation saved successfully!\n\n{record.text} = {record.value}"
            )
            return True
            
        except Exception as e:
            QMessageBox.critical(
                parent,
                "Error",
                f"Failed to save calculation:\n{str(e)}"
            )
            return False
