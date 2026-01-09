from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from src.shared.utils.measure_conversion import convert_between_units


def load_calc_module():
    repo_root = Path(__file__).resolve().parents[1]
    module_path = repo_root / "src" / "pillars" / "geometry" / "ui" / "advanced_scientific_calculator_window.py"
    spec = importlib.util.spec_from_file_location("advanced_scientific_calculator_window", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load calculator module for tests")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_calc_module = load_calc_module()
TIME_UNITS = _calc_module.TIME_UNITS


def _unit(name: str) -> dict:
    for u in TIME_UNITS:
        if u.get("name") == name and u.get("category") == "time":
            return u
    raise KeyError(name)


def test_time_units_include_basic_si():
    assert _unit("Second")["to_si"] == pytest.approx(1.0)
    assert _unit("Minute")["to_si"] == pytest.approx(60.0)
    assert _unit("Hour")["to_si"] == pytest.approx(3600.0)
    assert _unit("Day")["to_si"] == pytest.approx(86400.0)


def test_convert_seconds_to_minutes():
    second = _unit("Second")
    minute = _unit("Minute")
    result = convert_between_units(120.0, second, minute)
    assert result.converted_value == pytest.approx(2.0)


def test_convert_days_to_hours():
    day = _unit("Day")
    hour = _unit("Hour")
    result = convert_between_units(2.0, day, hour)
    assert result.converted_value == pytest.approx(48.0)


def test_julian_year_seconds_is_exact_by_definition():
    jy = _unit("Julian Year (astronomy)")
    assert float(jy["to_si"]) == pytest.approx(365.25 * 86400.0)
