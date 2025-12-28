"""
Formula Helper - The Wizard's Apprentice.
Services for discovering, searching, and validating spreadsheet formulas.
"""
from typing import List, Dict, Optional
from .formula_engine import FormulaRegistry, FormulaMetadata

class FormulaHelperService:
    """
    The Wizard's Apprentice.
    Provides services for discovering and constructing formulas.
    """

    @staticmethod
    def get_all_definitions() -> List[FormulaMetadata]:
        """Returns all registered formulas."""
        return FormulaRegistry.get_all_metadata()

    @staticmethod
    def get_categories() -> List[str]:
        """Returns unique list of categories (e.g. Math, Esoteric)."""
        defs = FormulaRegistry.get_all_metadata()
        return sorted(list(set(d.category for d in defs)))

    @staticmethod
    def search(query: str) -> List[FormulaMetadata]:
        """
        Search for formulas by name or description.
        Case-insensitive partial match.
        """
        if not query:
            return FormulaRegistry.get_all_metadata()
            
        q = query.upper()
        results = []
        for meta in FormulaRegistry.get_all_metadata():
            if q in meta.name or q in meta.description.upper():
                results.append(meta)
        return results

    @staticmethod
    def validate_syntax(formula: str) -> bool:
        """
        Basic syntax check.
        Returns True if superficially valid (balanced parens, starts with =).
        """
        if not formula.startswith("="):
            return False
        
        # Check parenthesis balance
        balance = 0
        for char in formula:
            if char == "(":
                balance += 1
            elif char == ")":
                balance -= 1
            if balance < 0:
                return False
        return balance == 0
