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
MEASURE_UNITS = _calc_module.MEASURE_UNITS


def _unit(name: str, category: str) -> dict:
    for u in MEASURE_UNITS:
        if u.get("name") == name and u.get("category") == category:
            return u
    raise KeyError(name)


def test_egyptian_length_derivations_are_consistent():
    cubit = _unit("Egyptian Royal Cubit", "length")
    palm = _unit("Egyptian Palm", "length")
    digit = _unit("Egyptian Digit", "length")
    remen = _unit("Egyptian Remen", "length")

    assert float(palm["to_si"]) == pytest.approx(float(cubit["to_si"]) / 7.0)
    assert float(digit["to_si"]) == pytest.approx(float(cubit["to_si"]) / 28.0)
    assert float(remen["to_si"]) == pytest.approx(float(cubit["to_si"]) * 5.0 / 7.0)


def test_egyptian_kite_is_tenth_deben():
    deben = _unit("Egyptian Deben", "mass")
    kite = _unit("Egyptian Kite (Qedet)", "mass")
    assert float(kite["to_si"]) == pytest.approx(float(deben["to_si"]) / 10.0)


def test_egyptian_hinu_is_tenth_hekat():
    hekat = _unit("Egyptian Hekat", "volume")
    hinu = _unit("Egyptian Hinu", "volume")
    assert float(hinu["to_si"]) == pytest.approx(float(hekat["to_si"]) / 10.0)


def test_convert_1_cubit_to_palms():
    cubit = _unit("Egyptian Royal Cubit", "length")
    palm = _unit("Egyptian Palm", "length")
    result = convert_between_units(1.0, cubit, palm)
    assert result.converted_value == pytest.approx(7.0)
