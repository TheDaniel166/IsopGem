"""
Quick test of spreadsheet validator.
Run: python -m pytest tests/manual/test_validator.py -v
"""

import pytest
from src.pillars.correspondences.services.spreadsheet_validator import (
    SpreadsheetValidator, ValidationError, validate_spreadsheet_data
)


def test_valid_single_sheet():
    """Valid single-sheet data should pass through."""
    data = {
        "columns": ["A", "B", "C"],
        "data": [["1", "2", "3"], ["4", "5", "6"]],
        "styles": {"0,0": {"bg": "#FF0000"}}
    }
    result = validate_spreadsheet_data(data)
    assert result["columns"] == ["A", "B", "C"]
    assert len(result["data"]) == 2
    assert "0,0" in result["styles"]


def test_valid_multi_sheet():
    """Valid multi-sheet format."""
    data = {
        "scrolls": [
            {"name": "Sheet1", "columns": ["A"], "data": [["1"]]},
            {"name": "Sheet2", "columns": ["B"], "data": [["2"]]}
        ],
        "active_scroll_index": 1
    }
    result = validate_spreadsheet_data(data)
    assert len(result["scrolls"]) == 2
    assert result["active_scroll_index"] == 1


def test_empty_data():
    """Empty dict should not crash."""
    data = {}
    result = validate_spreadsheet_data(data)
    assert result["columns"] == []
    assert result["data"] == []


def test_malformed_columns():
    """Non-list columns should be corrected."""
    data = {"columns": "ABC", "data": []}
    result = validate_spreadsheet_data(data)
    assert result["columns"] == []


def test_malformed_rows():
    """Non-list data should be corrected."""
    data = {"columns": ["A"], "data": "not a list"}
    result = validate_spreadsheet_data(data)
    assert result["data"] == []


def test_malformed_cell_values():
    """Complex types in cells should be stringified."""
    data = {
        "columns": ["A", "B", "C"],
        "data": [
            [1, "text", 3.14],
            [None, {"key": "val"}, ["list", "item"]]
        ]
    }
    result = validate_spreadsheet_data(data)
    assert result["data"][0] == [1, "text", 3.14]
    assert result["data"][1][0] == ""
    assert isinstance(result["data"][1][1], str)
    assert isinstance(result["data"][1][2], str)


def test_malformed_styles():
    """Invalid style keys should be skipped."""
    data = {
        "columns": ["A"],
        "data": [["1"]],
        "styles": {
            "0,0": {"bg": "#FF0000"},  # Valid
            "not_valid": {"bg": "#00FF00"},  # Invalid key format
            "1,1": {"bg": "not_a_color"},  # Invalid color
            "2,2": {"bg": "#0000FF", "bold": "yes"}  # Invalid bold type
        }
    }
    result = validate_spreadsheet_data(data)
    assert "0,0" in result["styles"]
    assert "not_valid" not in result["styles"]
    assert result["styles"]["2,2"]["bg"] == "#0000FF"
    assert "bold" not in result["styles"]["2,2"]


def test_non_dict_input():
    """Non-dict input should raise ValidationError."""
    with pytest.raises(ValidationError):
        validate_spreadsheet_data([1, 2, 3])


def test_scrolls_not_list():
    """Scrolls that aren't a list should raise error."""
    data = {"scrolls": "not a list"}
    with pytest.raises(ValidationError):
        validate_spreadsheet_data(data)


def test_invalid_active_index():
    """Out-of-range active index should be corrected to 0."""
    data = {
        "scrolls": [
            {"name": "Sheet1", "columns": ["A"], "data": [["1"]]}
        ],
        "active_scroll_index": 99
    }
    result = validate_spreadsheet_data(data)
    assert result["active_scroll_index"] == 0


def test_row_padding():
    """Rows should be padded to match column count."""
    data = {
        "columns": ["A", "B", "C"],
        "data": [["1"], ["2", "3"]]
    }
    result = validate_spreadsheet_data(data)
    assert len(result["data"][0]) == 3
    assert result["data"][0] == ["1", "", ""]
    assert len(result["data"][1]) == 3
    assert result["data"][1] == ["2", "3", ""]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
