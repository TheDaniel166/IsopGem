"""Unit tests for the square pyramid solid service and calculator."""
import math

import pytest

from src.pillars.geometry.services import (
    SquarePyramidSolidService,
    SquarePyramidSolidCalculator,
)


def test_square_pyramid_metrics_match_closed_form():
    result = SquarePyramidSolidService.build(base_edge=6.0, height=4.0)
    payload = result.payload
    assert len(payload.vertices) == 5
    assert len(payload.edges) == 8
    assert len(payload.faces) == 5

    metrics = result.metrics
    assert metrics.slant_height == pytest.approx(5.0)
    assert metrics.base_apothem == pytest.approx(3.0)
    assert metrics.base_area == pytest.approx(36.0)
    assert metrics.lateral_area == pytest.approx(60.0)
    assert metrics.surface_area == pytest.approx(96.0)
    assert metrics.volume == pytest.approx(48.0)
    assert metrics.lateral_edge == pytest.approx(math.sqrt(34.0))


def test_square_pyramid_calculator_handles_slant_height_and_volume():
    calc = SquarePyramidSolidCalculator(base_edge=4.0, height=3.0)

    assert calc.set_property('slant_height', 5.0)
    props = {prop.key: prop.value for prop in calc.properties()}
    half_edge = props['base_edge'] / 2.0
    expected_height = math.sqrt(5.0 ** 2 - half_edge ** 2)
    assert props['height'] == pytest.approx(expected_height)
    assert props['volume'] == pytest.approx((props['base_edge'] ** 2 * expected_height) / 3.0)

    assert calc.set_property('volume', 120.0)
    props = {prop.key: prop.value for prop in calc.properties()}
    expected_height = (3.0 * 120.0) / (props['base_edge'] ** 2)
    assert props['height'] == pytest.approx(expected_height)
    assert props['volume'] == pytest.approx(120.0)

    payload = calc.payload()
    assert payload is not None
    assert len(payload.vertices) == 5
