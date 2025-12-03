"""Unit tests for additional right regular pyramid services and calculators."""
import math

import pytest

from src.pillars.geometry.services import (
    RectangularPyramidSolidService,
    RectangularPyramidSolidCalculator,
    TriangularPyramidSolidService,
    TriangularPyramidSolidCalculator,
    PentagonalPyramidSolidService,
    PentagonalPyramidSolidCalculator,
    HexagonalPyramidSolidCalculator,
    HeptagonalPyramidSolidService,
    HeptagonalPyramidSolidCalculator,
)


def test_rectangular_pyramid_metrics_match_formulas():
    result = RectangularPyramidSolidService.build(base_length=10.0, base_width=6.0, height=8.0)
    payload = result.payload
    assert len(payload.vertices) == 5
    assert len(payload.edges) == 8
    assert len(payload.faces) == 5

    metrics = result.metrics
    assert metrics.base_area == pytest.approx(60.0)
    assert metrics.volume == pytest.approx(160.0)
    assert metrics.slant_length == pytest.approx(math.hypot(8.0, 3.0))
    assert metrics.slant_width == pytest.approx(math.hypot(8.0, 5.0))
    assert metrics.lateral_area == pytest.approx(10.0 * metrics.slant_length + 6.0 * metrics.slant_width)
    assert metrics.surface_area == pytest.approx(metrics.base_area + metrics.lateral_area)
    assert metrics.base_diagonal == pytest.approx(math.hypot(10.0, 6.0))
    assert metrics.lateral_edge == pytest.approx(math.hypot(8.0, math.hypot(10.0, 6.0) / 2.0))


def test_rectangular_pyramid_calculator_handles_slant_and_volume():
    calc = RectangularPyramidSolidCalculator(base_length=6.0, base_width=4.0, height=5.0)
    assert calc.set_property('slant_width', 6.0)  # updates height using base_length
    props = {prop.key: prop.value for prop in calc.properties()}
    expected_height = math.sqrt(6.0 ** 2 - (props['base_length'] / 2.0) ** 2)
    assert props['height'] == pytest.approx(expected_height)

    assert calc.set_property('volume', 200.0)
    props = {prop.key: prop.value for prop in calc.properties()}
    base_area = props['base_length'] * props['base_width']
    assert props['height'] == pytest.approx((3.0 * 200.0) / base_area)

    payload = calc.payload()
    assert payload is not None
    assert len(payload.vertices) == 5


def test_triangular_pyramid_metrics_match_regular_formulas():
    base_edge = 6.0
    height = 4.0
    result = TriangularPyramidSolidService.build(base_edge=base_edge, height=height)
    metrics = result.metrics
    expected_apothem = base_edge / (2.0 * math.tan(math.pi / 3.0))
    expected_area = (base_edge ** 2 * math.sqrt(3.0)) / 4.0
    expected_slant = math.sqrt(height ** 2 + expected_apothem ** 2)
    assert metrics.base_apothem == pytest.approx(expected_apothem)
    assert metrics.base_area == pytest.approx(expected_area)
    assert metrics.slant_height == pytest.approx(expected_slant)
    assert metrics.volume == pytest.approx(expected_area * height / 3.0)
    assert metrics.base_perimeter == pytest.approx(3.0 * base_edge)


def test_triangular_pyramid_calculator_from_base_area_and_volume():
    base_edge = 5.5
    height = 7.25
    area = (base_edge ** 2 * math.sqrt(3.0)) / 4.0
    volume = area * height / 3.0
    calc = TriangularPyramidSolidCalculator()
    assert calc.set_property('base_area', area)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['base_edge'] == pytest.approx(base_edge)

    assert calc.set_property('volume', volume)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['height'] == pytest.approx(height)


def test_pentagonal_pyramid_metrics_track_perimeter():
    base_edge = 4.0
    height = 5.0
    result = PentagonalPyramidSolidService.build(base_edge=base_edge, height=height)
    metrics = result.metrics
    expected_perimeter = 5.0 * base_edge
    expected_area = (5.0 * base_edge ** 2) / (4.0 * math.tan(math.pi / 5.0))
    assert metrics.base_perimeter == pytest.approx(expected_perimeter)
    assert metrics.base_area == pytest.approx(expected_area)
    assert metrics.volume == pytest.approx(expected_area * height / 3.0)


def test_hexagonal_pyramid_calculator_allows_apothem_input():
    calc = HexagonalPyramidSolidCalculator(base_edge=3.0, height=4.0)
    apothem = 2.5
    assert calc.set_property('base_apothem', apothem)
    props = {prop.key: prop.value for prop in calc.properties()}
    expected_edge = 2.0 * apothem * math.tan(math.pi / 6.0)
    assert props['base_edge'] == pytest.approx(expected_edge)
    payload = calc.payload()
    assert payload is not None


def test_heptagonal_pyramid_metrics_and_calculator():
    base_edge = 3.0
    height = 6.0
    result = HeptagonalPyramidSolidService.build(base_edge=base_edge, height=height)
    metrics = result.metrics
    expected_area = (7.0 * base_edge ** 2) / (4.0 * math.tan(math.pi / 7.0))
    expected_perimeter = 7.0 * base_edge
    assert metrics.base_area == pytest.approx(expected_area)
    assert metrics.base_perimeter == pytest.approx(expected_perimeter)
    assert metrics.volume == pytest.approx(expected_area * height / 3.0)

    calc = HeptagonalPyramidSolidCalculator()
    assert calc.set_property('base_area', expected_area)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['base_edge'] == pytest.approx(base_edge)
    assert calc.set_property('volume', expected_area * height / 3.0)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['height'] == pytest.approx(height)
