import pytest
from PyQt6.QtWidgets import QApplication

from pillars.correspondences.ui.spreadsheet_view import SpreadsheetModel


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def build_model(data):
    return SpreadsheetModel({"columns": ["A", "B", "C"], "data": data})


def test_self_reference_reports_cycle(qapp):
    model = build_model([["=A1"]])
    assert model.evaluate_cell(0, 0) == "#CYCLE!"


def test_two_cell_cycle_reports_cycle_both_cells(qapp):
    model = build_model([["=B1", "=A1"]])
    assert model.evaluate_cell(0, 0) == "#CYCLE!"
    assert model.evaluate_cell(0, 1) == "#CYCLE!"


def test_non_cycle_evaluates_value(qapp):
    model = build_model([["=B1", "3"]])
    assert model.evaluate_cell(0, 0) == 3


def test_range_reference_with_self_cycle(qapp):
    model = build_model([["=SUM(A1:A1)"]])
    assert model.evaluate_cell(0, 0) == "#CYCLE!"
