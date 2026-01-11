"""
Test style key shifting during row/column operations.

These tests verify that cell styles maintain correct cell associations
when rows or columns are inserted or deleted.
"""

import pytest
from unittest.mock import Mock
from PyQt6.QtCore import Qt, QModelIndex

# We need to import the actual SpreadsheetModel to test with
import sys
sys.path.insert(0, '/home/burkettdaniel927/projects/isopgem/src')

from pillars.correspondences.ui.spreadsheet_view import SpreadsheetModel
from pillars.correspondences.services.undo_commands import (
    InsertRowsCommand, RemoveRowsCommand,
    InsertColumnsCommand, RemoveColumnsCommand
)


def create_test_model():
    """Create a simple 5x5 model for testing."""
    data = {
        "columns": ["A", "B", "C", "D", "E"],
        "data": [
            ["R0C0", "R0C1", "R0C2", "R0C3", "R0C4"],
            ["R1C0", "R1C1", "R1C2", "R1C3", "R1C4"],
            ["R2C0", "R2C1", "R2C2", "R2C3", "R2C4"],
            ["R3C0", "R3C1", "R3C2", "R3C3", "R3C4"],
            ["R4C0", "R4C1", "R4C2", "R4C3", "R4C4"],
        ],
        "styles": {}
    }
    return SpreadsheetModel(data)


class TestInsertRowsStyleShift:
    """Test that inserting rows shifts style keys correctly."""
    
    def test_insert_rows_shifts_styles_down(self):
        """Inserting rows should shift all styles below insertion point down."""
        model = create_test_model()
        
        # Set styles at various positions
        model._styles[(0, 0)] = {"bg": "#FF0000"}  # Row 0 - should stay
        model._styles[(1, 1)] = {"bg": "#00FF00"}  # Row 1 - should move to row 3
        model._styles[(2, 2)] = {"bg": "#0000FF"}  # Row 2 - should move to row 4
        
        # Insert 2 rows at position 1
        cmd = InsertRowsCommand(model, position=1, rows=2)
        cmd.redo()
        
        # Verify shifts
        assert (0, 0) in model._styles  # Stayed at row 0
        assert model._styles[(0, 0)]["bg"] == "#FF0000"
        
        assert (1, 1) not in model._styles  # Old position gone
        assert (3, 1) in model._styles  # Moved down by 2
        assert model._styles[(3, 1)]["bg"] == "#00FF00"
        
        assert (2, 2) not in model._styles  # Old position gone
        assert (4, 2) in model._styles  # Moved down by 2
        assert model._styles[(4, 2)]["bg"] == "#0000FF"
    
    def test_insert_rows_undo_restores_positions(self):
        """Undoing row insertion should restore original style positions."""
        model = create_test_model()
        model._styles[(1, 1)] = {"bg": "#00FF00"}
        model._styles[(2, 2)] = {"bg": "#0000FF"}
        
        cmd = InsertRowsCommand(model, position=1, rows=2)
        cmd.redo()
        cmd.undo()
        
        # Should be back to original positions
        assert (1, 1) in model._styles
        assert (2, 2) in model._styles
        assert (3, 1) not in model._styles
        assert (4, 2) not in model._styles


class TestRemoveRowsStyleShift:
    """Test that removing rows shifts style keys correctly."""
    
    def test_remove_rows_shifts_styles_up(self):
        """Removing rows should shift all styles below deletion point up."""
        model = create_test_model()
        
        # Set styles
        model._styles[(0, 0)] = {"bg": "#FF0000"}  # Row 0 - should stay
        model._styles[(1, 1)] = {"bg": "#00FF00"}  # Row 1 - will be deleted
        model._styles[(2, 2)] = {"bg": "#0000FF"}  # Row 2 - will be deleted
        model._styles[(3, 3)] = {"bg": "#FFFF00"}  # Row 3 - should move to row 1
        model._styles[(4, 4)] = {"bg": "#FF00FF"}  # Row 4 - should move to row 2
        
        # Remove 2 rows starting at position 1
        cmd = RemoveRowsCommand(model, position=1, rows=2)
        cmd.redo()
        
        # Verify shifts
        assert (0, 0) in model._styles  # Stayed
        assert (1, 1) not in model._styles  # Deleted
        assert (2, 2) not in model._styles  # Deleted
        assert (1, 3) in model._styles  # Moved up from row 3
        assert (2, 4) in model._styles  # Moved up from row 4
        assert model._styles[(1, 3)]["bg"] == "#FFFF00"
        assert model._styles[(2, 4)]["bg"] == "#FF00FF"
    
    def test_remove_rows_undo_restores_deleted_styles(self):
        """Undoing row removal should restore deleted styles."""
        model = create_test_model()
        model._styles[(1, 1)] = {"bg": "#00FF00"}
        model._styles[(2, 2)] = {"bg": "#0000FF"}
        model._styles[(3, 3)] = {"bg": "#FFFF00"}
        
        cmd = RemoveRowsCommand(model, position=1, rows=2)
        cmd.redo()
        cmd.undo()
        
        # All original styles should be restored
        assert (1, 1) in model._styles
        assert (2, 2) in model._styles
        assert (3, 3) in model._styles
        assert model._styles[(1, 1)]["bg"] == "#00FF00"
        assert model._styles[(2, 2)]["bg"] == "#0000FF"


class TestInsertColumnsStyleShift:
    """Test that inserting columns shifts style keys correctly."""
    
    def test_insert_columns_shifts_styles_right(self):
        """Inserting columns should shift all styles right of insertion point."""
        model = create_test_model()
        
        # Set styles
        model._styles[(0, 0)] = {"bg": "#FF0000"}  # Col 0 - should stay
        model._styles[(1, 1)] = {"bg": "#00FF00"}  # Col 1 - should move to col 3
        model._styles[(2, 2)] = {"bg": "#0000FF"}  # Col 2 - should move to col 4
        
        # Insert 2 columns at position 1
        cmd = InsertColumnsCommand(model, position=1, columns=2)
        cmd.redo()
        
        # Verify shifts
        assert (0, 0) in model._styles  # Stayed at col 0
        assert (1, 1) not in model._styles  # Old position gone
        assert (1, 3) in model._styles  # Moved right by 2
        assert (2, 2) not in model._styles  # Old position gone
        assert (2, 4) in model._styles  # Moved right by 2
        assert model._styles[(1, 3)]["bg"] == "#00FF00"
    
    def test_insert_columns_undo_restores_positions(self):
        """Undoing column insertion should restore original positions."""
        model = create_test_model()
        model._styles[(1, 1)] = {"bg": "#00FF00"}
        model._styles[(2, 2)] = {"bg": "#0000FF"}
        
        cmd = InsertColumnsCommand(model, position=1, columns=2)
        cmd.redo()
        cmd.undo()
        
        # Should be back to original
        assert (1, 1) in model._styles
        assert (2, 2) in model._styles
        assert model._styles[(1, 1)]["bg"] == "#00FF00"


class TestRemoveColumnsStyleShift:
    """Test that removing columns shifts style keys correctly."""
    
    def test_remove_columns_shifts_styles_left(self):
        """Removing columns should shift all styles left of deletion point."""
        model = create_test_model()
        
        # Set styles
        model._styles[(0, 0)] = {"bg": "#FF0000"}  # Col 0 - should stay
        model._styles[(1, 1)] = {"bg": "#00FF00"}  # Col 1 - will be deleted
        model._styles[(2, 2)] = {"bg": "#0000FF"}  # Col 2 - will be deleted
        model._styles[(3, 3)] = {"bg": "#FFFF00"}  # Col 3 - should move to col 1
        model._styles[(4, 4)] = {"bg": "#FF00FF"}  # Col 4 - should move to col 2
        
        # Remove 2 columns starting at position 1
        cmd = RemoveColumnsCommand(model, position=1, columns=2)
        cmd.redo()
        
        # Verify shifts
        assert (0, 0) in model._styles  # Stayed
        assert (1, 1) not in model._styles  # Deleted
        assert (2, 2) not in model._styles  # Deleted
        assert (3, 1) in model._styles  # Moved left from col 3
        assert (4, 2) in model._styles  # Moved left from col 4
        assert model._styles[(3, 1)]["bg"] == "#FFFF00"
        assert model._styles[(4, 2)]["bg"] == "#FF00FF"
    
    def test_remove_columns_undo_restores_deleted_styles(self):
        """Undoing column removal should restore deleted styles."""
        model = create_test_model()
        model._styles[(1, 1)] = {"bg": "#00FF00"}
        model._styles[(2, 2)] = {"bg": "#0000FF"}
        model._styles[(3, 3)] = {"bg": "#FFFF00"}
        
        cmd = RemoveColumnsCommand(model, position=1, columns=2)
        cmd.redo()
        cmd.undo()
        
        # All original styles should be restored
        assert (1, 1) in model._styles
        assert (2, 2) in model._styles
        assert (3, 3) in model._styles
        assert model._styles[(1, 1)]["bg"] == "#00FF00"


class TestComplexStyleOperations:
    """Test complex sequences of operations."""
    
    def test_multiple_insertions_compound(self):
        """Multiple insertions should compound correctly."""
        model = create_test_model()
        model._styles[(2, 2)] = {"bg": "#0000FF"}
        
        # Insert 1 row at position 1
        cmd1 = InsertRowsCommand(model, position=1, rows=1)
        cmd1.redo()
        assert (3, 2) in model._styles  # Moved from 2 to 3
        
        # Insert another row at position 0
        cmd2 = InsertRowsCommand(model, position=0, rows=1)
        cmd2.redo()
        assert (4, 2) in model._styles  # Moved from 3 to 4
    
    def test_insert_then_remove_same_position(self):
        """Inserting then removing at same position should restore state."""
        model = create_test_model()
        model._styles[(2, 2)] = {"bg": "#0000FF"}
        
        cmd_insert = InsertRowsCommand(model, position=1, rows=2)
        cmd_insert.redo()
        assert (4, 2) in model._styles
        
        cmd_remove = RemoveRowsCommand(model, position=1, rows=2)
        cmd_remove.redo()
        assert (2, 2) in model._styles
        assert model._styles[(2, 2)]["bg"] == "#0000FF"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
