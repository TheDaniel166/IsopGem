"""
Spreadsheet Data Validation

Validates JSON data structures before they enter the SpreadsheetModel.
Prevents malformed data from corrupting the spreadsheet state.

The Law of the Shield: Corrupt data must not reach the Model.
"""

import logging
from typing import Any, Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when spreadsheet data fails validation."""
    pass


class SpreadsheetValidator:
    """
    Validates spreadsheet JSON data structures.
    
    Expected Schema:
    {
        "columns": ["A", "B", "C", ...],  # List of strings
        "data": [["cell", "cell", ...], ...],  # List of rows (list of lists)
        "styles": {"0,1": {"bg": "#hex", ...}, ...}  # Optional: Dict of style objects
    }
    
    Or Multi-Sheet Format:
    {
        "scrolls": [
            {"name": "Sheet1", "columns": [...], "data": [...], "styles": {...}},
            ...
        ],
        "active_scroll_index": 0  # Optional: Default sheet index
    }
    """
    
    @staticmethod
    def validate(data: Any) -> Dict[str, Any]:
        """
        Validate and sanitize spreadsheet data.
        
        Args:
            data: The incoming JSON data (dict expected)
            
        Returns:
            Sanitized data dictionary
            
        Raises:
            ValidationError: If data is malformed beyond repair
        """
        if not isinstance(data, dict):
            raise ValidationError(f"Expected dict, got {type(data).__name__}")
        
        # Detect format
        if "scrolls" in data:
            return SpreadsheetValidator._validate_multi_sheet(data)
        else:
            return SpreadsheetValidator._validate_single_sheet(data)
    
    @staticmethod
    def _validate_multi_sheet(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate multi-sheet format."""
        scrolls = data.get("scrolls")
        if not isinstance(scrolls, list):
            raise ValidationError("'scrolls' must be a list")
        
        if not scrolls:
            logger.warning("Empty scrolls list, creating default sheet")
            scrolls = [{
                "name": "Sheet1",
                "columns": [],
                "data": []
            }]
        
        # Validate each scroll
        validated_scrolls = []
        for i, scroll in enumerate(scrolls):
            if not isinstance(scroll, dict):
                logger.error(f"Scroll {i} is not a dict, skipping")
                continue
            
            try:
                validated = SpreadsheetValidator._validate_single_sheet(scroll)
                # Ensure name exists
                if "name" not in validated:
                    validated["name"] = f"Sheet{i+1}"
                validated_scrolls.append(validated)
            except ValidationError as e:
                logger.error(f"Scroll {i} validation failed: {e}, skipping")
        
        if not validated_scrolls:
            raise ValidationError("No valid scrolls after validation")
        
        # Validate active index
        active_index = data.get("active_scroll_index", 0)
        if not isinstance(active_index, int) or active_index < 0:
            logger.warning(f"Invalid active_scroll_index {active_index}, defaulting to 0")
            active_index = 0
        if active_index >= len(validated_scrolls):
            active_index = 0
        
        return {
            "scrolls": validated_scrolls,
            "active_scroll_index": active_index
        }
    
    @staticmethod
    def _validate_single_sheet(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate single sheet format."""
        result = {}
        
        # 1. Validate columns
        columns = data.get("columns", [])
        if not isinstance(columns, list):
            logger.warning(f"'columns' must be a list, got {type(columns).__name__}, using []")
            columns = []
        
        # Ensure all columns are strings
        validated_columns = []
        for i, col in enumerate(columns):
            if isinstance(col, str):
                validated_columns.append(col)
            else:
                logger.warning(f"Column {i} is not a string ({type(col).__name__}), converting")
                validated_columns.append(str(col))
        
        result["columns"] = validated_columns
        
        # 2. Validate data (rows)
        data_rows = data.get("data") or data.get("rows", [])
        if not isinstance(data_rows, list):
            logger.warning(f"'data' must be a list, got {type(data_rows).__name__}, using []")
            data_rows = []
        
        # Ensure all rows are lists
        validated_rows = []
        expected_width = len(validated_columns) if validated_columns else 0
        
        for r, row in enumerate(data_rows):
            if not isinstance(row, list):
                logger.warning(f"Row {r} is not a list, converting to list")
                row = [row] if row is not None else [""]
            
            # Validate each cell
            validated_row = []
            for c, cell in enumerate(row):
                validated_cell = SpreadsheetValidator._validate_cell_value(cell, r, c)
                validated_row.append(validated_cell)
            
            # Pad or trim to expected width if we have column info
            if expected_width > 0:
                if len(validated_row) < expected_width:
                    validated_row.extend([""] * (expected_width - len(validated_row)))
                elif len(validated_row) > expected_width:
                    logger.debug(f"Row {r} has {len(validated_row)} cells, trimming to {expected_width}")
                    validated_row = validated_row[:expected_width]
            
            validated_rows.append(validated_row)
        
        result["data"] = validated_rows
        
        # 3. Validate styles (optional)
        styles = data.get("styles", {})
        if not isinstance(styles, dict):
            logger.warning(f"'styles' must be a dict, got {type(styles).__name__}, using {{}}")
            styles = {}
        
        validated_styles = SpreadsheetValidator._validate_styles(styles)
        result["styles"] = validated_styles
        
        # 4. Preserve name if present (for scrolls)
        if "name" in data:
            result["name"] = str(data["name"])
        
        return result
    
    @staticmethod
    def _validate_cell_value(value: Any, row: int, col: int) -> Any:
        """
        Validate and sanitize a cell value.
        
        Allowed types: str, int, float, bool, None
        Everything else gets stringified.
        """
        if value is None:
            return ""
        
        if isinstance(value, (str, int, float, bool)):
            return value
        
        # Lists/dicts should not be in cells
        if isinstance(value, (list, dict)):
            logger.warning(
                f"Cell ({row},{col}) contains {type(value).__name__}, "
                "converting to string"
            )
            return str(value)
        
        # Unknown types
        logger.debug(f"Cell ({row},{col}) has type {type(value).__name__}, converting to string")
        return str(value)
    
    @staticmethod
    def _validate_styles(styles: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate style dictionary.
        
        Expected format:
        {
            "row,col": {
                "bg": "#hex",
                "fg": "#hex",
                "bold": bool,
                "italic": bool,
                "underline": bool,
                "borders": {"top": bool, "bottom": bool, "left": bool, "right": bool}
            }
        }
        """
        validated = {}
        
        for key, style_dict in styles.items():
            # Validate key format
            if not isinstance(key, str):
                logger.warning(f"Style key must be string, got {type(key).__name__}, skipping")
                continue
            
            # Check if key is "row,col" format
            try:
                parts = key.split(",")
                if len(parts) != 2:
                    raise ValueError("Must be 'row,col'")
                int(parts[0])
                int(parts[1])
            except (ValueError, AttributeError) as e:
                logger.warning(f"Invalid style key '{key}': {e}, skipping")
                continue
            
            # Validate style dict
            if not isinstance(style_dict, dict):
                logger.warning(f"Style for {key} must be dict, got {type(style_dict).__name__}, skipping")
                continue
            
            # Validate style properties
            validated_style = {}
            
            # Color properties
            for color_key in ["bg", "fg"]:
                if color_key in style_dict:
                    val = style_dict[color_key]
                    if isinstance(val, str) and (val.startswith("#") or val.lower() in ["transparent", "none"]):
                        validated_style[color_key] = val
                    else:
                        logger.debug(f"Invalid color '{val}' for {key}.{color_key}, skipping")
            
            # Boolean properties
            for bool_key in ["bold", "italic", "underline"]:
                if bool_key in style_dict:
                    val = style_dict[bool_key]
                    if isinstance(val, bool):
                        validated_style[bool_key] = val
                    else:
                        logger.debug(f"Property {bool_key} must be bool, got {type(val).__name__}, skipping")
            
            # Font size
            if "font_size" in style_dict:
                val = style_dict["font_size"]
                if isinstance(val, (int, float)) and val > 0:
                    validated_style["font_size"] = val
                else:
                    logger.debug(f"Invalid font_size '{val}' for {key}, skipping")
            
            # Borders
            if "borders" in style_dict:
                borders = style_dict["borders"]
                if isinstance(borders, dict):
                    validated_borders = {}
                    for side in ["top", "bottom", "left", "right"]:
                        if side in borders and isinstance(borders[side], bool):
                            validated_borders[side] = borders[side]
                    if validated_borders:
                        validated_style["borders"] = validated_borders
            
            # Text alignment
            if "align" in style_dict:
                val = style_dict["align"]
                if val in ["left", "center", "right"]:
                    validated_style["align"] = val
            
            if validated_style:
                validated[key] = validated_style
        
        return validated


def validate_spreadsheet_data(data: Any) -> Dict[str, Any]:
    """
    Convenience function for validating spreadsheet data.
    
    Args:
        data: The data to validate
        
    Returns:
        Validated and sanitized data
        
    Raises:
        ValidationError: If data is malformed
    """
    return SpreadsheetValidator.validate(data)
