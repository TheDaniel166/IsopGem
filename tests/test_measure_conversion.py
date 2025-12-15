from __future__ import annotations

import math

import pytest

from src.shared.utils.measure_conversion import convert_between_units, parse_measure_value


def test_parse_measure_value_plain_float():
    assert parse_measure_value("12.5") == 12.5


def test_parse_measure_value_commas():
    assert parse_measure_value("1,234.5") == 1234.5


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("3/4", 0.75),
        ("-5/2", -2.5),
        ("  10 / 4 ", 2.5),
    ],
)
def test_parse_measure_value_fraction(raw, expected):
    assert parse_measure_value(raw) == expected


def test_parse_measure_value_invalid():
    with pytest.raises(ValueError):
        parse_measure_value("abc")
    with pytest.raises(ValueError):
        parse_measure_value("1/0")
    with pytest.raises(ValueError):
        parse_measure_value("1/2/3")


def test_convert_between_units_length_round_trip():
    meter = {"name": "Meter", "si_unit": "m", "to_si": 1.0}
    cm = {"name": "Centimeter", "si_unit": "m", "to_si": 0.01}
    result = convert_between_units(2.0, meter, cm)
    assert result.base_unit == "m"
    assert result.base_value == 2.0
    assert result.converted_value == pytest.approx(200.0)


def test_convert_between_units_mass():
    kg = {"name": "Kilogram", "si_unit": "kg", "to_si": 1.0}
    g = {"name": "Gram", "si_unit": "kg", "to_si": 0.001}
    result = convert_between_units(3.0, kg, g)
    assert result.converted_value == pytest.approx(3000.0)


def test_convert_between_units_uses_string_factor():
    meter = {"name": "Meter", "si_unit": "m", "to_si": "1.0"}
    km = {"name": "Kilometer", "si_unit": "m", "to_si": "1000.0"}
    result = convert_between_units(2.0, km, meter)
    assert result.converted_value == pytest.approx(2000.0)


def test_convert_between_units_rejects_invalid_unit():
    with pytest.raises(ValueError):
        convert_between_units(1.0, {"to_si": 1.0}, {"to_si": 0.0})
