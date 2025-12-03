"""Unit tests for pyramid frustum solid services and calculators."""
import math

import pytest

from src.pillars.geometry.services import (
    SquarePyramidFrustumSolidService,
    SquarePyramidFrustumSolidCalculator,
    PentagonalPyramidFrustumSolidService,
    PentagonalPyramidFrustumSolidCalculator,
    HexagonalPyramidFrustumSolidService,
    HexagonalPyramidFrustumSolidCalculator,
)


def test_square_pyramid_frustum_metrics_are_consistent():
    base_edge = 6.0
    top_edge = 2.0
    height = 5.0
    result = SquarePyramidFrustumSolidService.build(base_edge=base_edge, top_edge=top_edge, height=height)
    payload = result.payload
    assert len(payload.vertices) == 8
    assert len(payload.edges) == 12
    assert len(payload.faces) == 6

    metrics = result.metrics
    expected_slant = math.sqrt(height ** 2 + ((base_edge - top_edge) / 2.0) ** 2)
    expected_volume = (height / 3.0) * (base_edge ** 2 + base_edge * top_edge + top_edge ** 2)
    expected_lateral = 2.0 * (base_edge + top_edge) * expected_slant
    assert metrics.slant_height == pytest.approx(expected_slant)
    assert metrics.volume == pytest.approx(expected_volume)
    assert metrics.lateral_area == pytest.approx(expected_lateral)
    assert metrics.surface_area == pytest.approx(metrics.lateral_area + metrics.base_area + metrics.top_area)


def test_square_pyramid_frustum_calculator_accepts_area_and_slant_inputs():
    calc = SquarePyramidFrustumSolidCalculator(base_edge=5.0, top_edge=3.0, height=4.0)

    assert calc.set_property('top_area', 16.0)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['top_edge'] == pytest.approx(4.0)

    slant_height = 6.0
    assert calc.set_property('slant_height', slant_height)
    props = {prop.key: prop.value for prop in calc.properties()}
    base_edge_val = props['base_edge']
    top_edge_val = props['top_edge']
    height_val = props['height']
    assert base_edge_val is not None and top_edge_val is not None and height_val is not None
    diff = abs(base_edge_val - top_edge_val) / 2.0
    expected_height = math.sqrt(slant_height ** 2 - diff ** 2)
    assert height_val == pytest.approx(expected_height)

    expected_volume = (height_val / 3.0) * (
        base_edge_val ** 2 + base_edge_val * top_edge_val + top_edge_val ** 2
    )
    assert calc.set_property('volume', expected_volume)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['volume'] == pytest.approx(expected_volume)

    payload = calc.payload()
    assert payload is not None
    assert len(payload.vertices) == 8


def test_pentagonal_pyramid_frustum_metrics_follow_closed_forms():
    base_edge = 8.0
    top_edge = 4.0
    height = 6.0
    result = PentagonalPyramidFrustumSolidService.build(base_edge=base_edge, top_edge=top_edge, height=height)
    metrics = result.metrics

    def n_area(edge: float) -> float:
        return (5.0 * edge ** 2) / (4.0 * math.tan(math.pi / 5.0))

    base_area = n_area(base_edge)
    top_area = n_area(top_edge)
    base_apothem = base_edge / (2.0 * math.tan(math.pi / 5.0))
    top_apothem = top_edge / (2.0 * math.tan(math.pi / 5.0))
    expected_slant = math.sqrt(height ** 2 + (base_apothem - top_apothem) ** 2)
    expected_lateral = 0.5 * (5.0 * base_edge + 5.0 * top_edge) * expected_slant
    expected_volume = (height / 3.0) * (base_area + math.sqrt(base_area * top_area) + top_area)

    assert metrics.base_area == pytest.approx(base_area)
    assert metrics.top_area == pytest.approx(top_area)
    assert metrics.slant_height == pytest.approx(expected_slant)
    assert metrics.lateral_area == pytest.approx(expected_lateral)
    assert metrics.volume == pytest.approx(expected_volume)


def test_pentagonal_pyramid_frustum_calculator_volume_and_area_inputs():
    calc = PentagonalPyramidFrustumSolidCalculator(base_edge=7.0, top_edge=3.5, height=5.0)
    top_area = (5.0 * 3.5 ** 2) / (4.0 * math.tan(math.pi / 5.0))
    assert calc.set_property('top_area', top_area)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['top_edge'] == pytest.approx(3.5)

    base_area = (5.0 * 7.5 ** 2) / (4.0 * math.tan(math.pi / 5.0))
    assert calc.set_property('base_area', base_area)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['base_edge'] == pytest.approx(7.5)

    base_edge_val = props['base_edge']
    top_edge_val = props['top_edge']
    height_val = props['height']
    assert base_edge_val is not None and top_edge_val is not None and height_val is not None
    current_base_area = (5.0 * base_edge_val ** 2) / (4.0 * math.tan(math.pi / 5.0))
    current_top_area = (5.0 * top_edge_val ** 2) / (4.0 * math.tan(math.pi / 5.0))
    target_volume = (height_val / 3.0) * (
        current_base_area + math.sqrt(current_base_area * current_top_area) + current_top_area
    )
    assert calc.set_property('volume', target_volume)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['volume'] == pytest.approx(target_volume)

    payload = calc.payload()
    assert payload is not None
    assert len(payload.vertices) == 10


def test_hexagonal_pyramid_frustum_metrics_and_calculator():
    base_edge = 9.0
    top_edge = 4.5
    height = 7.0
    result = HexagonalPyramidFrustumSolidService.build(base_edge=base_edge, top_edge=top_edge, height=height)
    metrics = result.metrics

    def hex_area(edge: float) -> float:
        return (3.0 * math.sqrt(3.0) / 2.0) * edge ** 2

    base_area = hex_area(base_edge)
    top_area = hex_area(top_edge)
    base_apothem = base_edge / (2.0 * math.tan(math.pi / 6.0))
    top_apothem = top_edge / (2.0 * math.tan(math.pi / 6.0))
    expected_slant = math.sqrt(height ** 2 + (base_apothem - top_apothem) ** 2)
    expected_lateral = 0.5 * (6.0 * base_edge + 6.0 * top_edge) * expected_slant
    expected_volume = (height / 3.0) * (base_area + math.sqrt(base_area * top_area) + top_area)

    assert metrics.base_area == pytest.approx(base_area)
    assert metrics.top_area == pytest.approx(top_area)
    assert metrics.slant_height == pytest.approx(expected_slant)
    assert metrics.lateral_area == pytest.approx(expected_lateral)
    assert metrics.volume == pytest.approx(expected_volume)

    calc = HexagonalPyramidFrustumSolidCalculator(base_edge=base_edge, top_edge=top_edge, height=height)
    assert calc.set_property('base_area', base_area)
    assert calc.set_property('top_area', top_area)
    props = {prop.key: prop.value for prop in calc.properties()}
    base_edge_val = props['base_edge']
    top_edge_val = props['top_edge']
    volume_val = props['volume']
    assert base_edge_val is not None and top_edge_val is not None and volume_val is not None
    assert base_edge_val == pytest.approx(base_edge)
    assert top_edge_val == pytest.approx(top_edge)
    assert volume_val == pytest.approx(metrics.volume)
