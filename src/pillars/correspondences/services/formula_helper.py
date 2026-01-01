"""
Formula Helper - The Wizard's Apprentice.
Services for discovering, searching, and validating spreadsheet formulas.
"""
import re
from typing import List, Dict, Optional, Tuple, NamedTuple
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


# --- Cell Address Utilities ---

def col_to_letter(col_idx: int) -> str:
    """Convert zero-based column index to letter (0 -> 'A', 26 -> 'AA')."""
    result = ""
    while col_idx >= 0:
        result = chr((col_idx % 26) + 65) + result
        col_idx = (col_idx // 26) - 1
    return result


def letter_to_col(letters: str) -> int:
    """Convert column letters to zero-based index ('A' -> 0, 'AA' -> 26)."""
    col_idx = 0
    for char in letters.upper():
        col_idx = col_idx * 26 + (ord(char) - ord('A') + 1)
    return col_idx - 1


def cell_address(row: int, col: int) -> str:
    """Convert row/col (0-based) to cell address (e.g., 0,0 -> 'A1')."""
    return f"{col_to_letter(col)}{row + 1}"


# --- Reference Extraction for Color-Coding ---

class CellReference(NamedTuple):
    """A parsed cell reference with its position in the formula string."""
    text: str          # The reference text (e.g., "A1", "B2:C5")
    start: int         # Start position in formula string
    end: int           # End position in formula string
    row: int           # Zero-based row (for single cell or start of range)
    col: int           # Zero-based column (for single cell or start of range)
    end_row: Optional[int] = None  # For ranges: end row
    end_col: Optional[int] = None  # For ranges: end column
    is_range: bool = False


# Excel-style reference colors (matches RichTextDelegate.SELECTION_COLORS)
REFERENCE_COLORS = [
    "#3B82F6",  # Blue
    "#10B981",  # Emerald
    "#F59E0B",  # Amber
    "#8B5CF6",  # Violet
    "#EC4899",  # Pink
    "#14B8A6",  # Teal
    "#F97316",  # Orange
    "#6366F1",  # Indigo
    "#84CC16",  # Lime
    "#EF4444",  # Red
]


def extract_references(formula: str) -> List[CellReference]:
    """
    Extract all cell references from a formula with their positions.
    
    Supports:
    - Single cells: A1, $A$1, A$1, $A1
    - Ranges: A1:B5, $A$1:$B$5
    
    Returns list of CellReference tuples with position info.
    """
    if not formula or not formula.startswith("="):
        return []
    
    # Pattern matches: optional $, letters, optional $, digits, optional :same
    # Cell pattern: (\$?[A-Z]+\$?\d+)
    # Range pattern: cell:cell
    pattern = r'(\$?[A-Z]+\$?\d+)(?::(\$?[A-Z]+\$?\d+))?'
    
    references = []
    
    for match in re.finditer(pattern, formula, re.IGNORECASE):
        start_ref = match.group(1)
        end_ref = match.group(2)  # May be None for single cells
        
        # Parse start cell
        start_row, start_col = _parse_cell_ref(start_ref)
        if start_row is None:
            continue
        
        if end_ref:
            # It's a range
            end_row, end_col = _parse_cell_ref(end_ref)
            references.append(CellReference(
                text=match.group(0),
                start=match.start(),
                end=match.end(),
                row=start_row,
                col=start_col,
                end_row=end_row,
                end_col=end_col,
                is_range=True
            ))
        else:
            # Single cell
            references.append(CellReference(
                text=start_ref,
                start=match.start(),
                end=match.end(),
                row=start_row,
                col=start_col,
                is_range=False
            ))
    
    return references


def _parse_cell_ref(ref: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse a cell reference like 'A1' or '$B$2' into (row, col) zero-based."""
    match = re.match(r'^\$?([A-Z]+)\$?(\d+)$', ref, re.IGNORECASE)
    if not match:
        return None, None
    
    col_str, row_str = match.groups()
    col = letter_to_col(col_str)
    row = int(row_str) - 1
    return row, col


def colorize_formula(formula: str) -> str:
    """
    Convert a formula to HTML with color-coded references.
    
    Each reference gets a unique color from REFERENCE_COLORS palette.
    Returns HTML string suitable for display in a rich text widget.
    """
    if not formula or not formula.startswith("="):
        return formula
    
    refs = extract_references(formula)
    if not refs:
        return formula
    
    # Sort by position (reverse order for safe replacement)
    refs_sorted = sorted(refs, key=lambda r: r.start, reverse=True)
    
    result = formula
    for i, ref in enumerate(reversed(refs_sorted)):  # Reverse back for color assignment
        color_idx = len(refs_sorted) - 1 - i
        color = REFERENCE_COLORS[color_idx % len(REFERENCE_COLORS)]
        
        # Find actual position (refs_sorted is reversed)
        actual_ref = refs_sorted[len(refs_sorted) - 1 - i]
        colored = f'<span style="color:{color}; font-weight:bold;">{actual_ref.text}</span>'
        result = result[:actual_ref.start] + colored + result[actual_ref.end:]
    
    return result


def get_reference_cells(formula: str) -> List[Tuple[int, int, int, int, str]]:
    """
    Get all cells that should be highlighted with their colors.
    
    Returns list of (row, col, end_row, end_col, color) tuples.
    For single cells, end_row and end_col equal row and col.
    """
    refs = extract_references(formula)
    result = []
    
    for i, ref in enumerate(refs):
        color = REFERENCE_COLORS[i % len(REFERENCE_COLORS)]
        if ref.is_range:
            result.append((ref.row, ref.col, ref.end_row, ref.end_col, color))
        else:
            result.append((ref.row, ref.col, ref.row, ref.col, color))
    
    return result
