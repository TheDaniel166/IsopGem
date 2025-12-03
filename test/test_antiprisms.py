"""Unit tests for regular antiprism services and calculators."""
import math

import pytest

from src.pillars.geometry.services import (
    TriangularAntiprismSolidService,
    SquareAntiprismSolidCalculator,
    HeptagonalAntiprismSolidService,
)


def test_triangular_antiprism_metrics_and_payload():
    result = TriangularAntiprismSolidService.build(base_edge=3.0, height=4.0)
    payload = result.payload
    metrics = result.metrics

    assert len(payload.vertices) == 6
    assert len(payload.edges) == 12
    assert len(payload.faces) == 8

    base_area = (math.sqrt(3.0) / 4.0) * (3.0 ** 2)
    assert metrics.base_area == pytest.approx(base_area)
    assert metrics.base_perimeter == pytest.approx(9.0)

    lateral_chord = 2.0 * metrics.base_circumradius * math.sin(math.pi / (2.0 * metrics.sides))
    expected_lateral = math.sqrt(4.0 ** 2 + lateral_chord ** 2)
    assert metrics.lateral_edge_length == pytest.approx(expected_lateral)

    assert payload.metadata['surface_area'] == pytest.approx(metrics.surface_area)
    assert payload.metadata['volume'] == pytest.approx(metrics.volume)


def test_square_antiprism_calculator_handles_lateral_edge_and_volume():
    calc = SquareAntiprismSolidCalculator(base_edge=2.5, height=3.5)

    chord = 2.5 / (2.0 * math.sin(math.pi / 4.0)) * 2.0 * math.sin(math.pi / 8.0)
    target_lateral = math.sqrt(5.0 ** 2 + chord ** 2)
    assert calc.set_property('lateral_edge_length', target_lateral)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['height'] == pytest.approx(5.0)
    assert props['lateral_edge_length'] == pytest.approx(target_lateral)

    current_volume = props['volume']
    target_volume = current_volume * 1.5
    assert calc.set_property('volume', target_volume)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['volume'] == pytest.approx(target_volume)
    assert props['height'] == pytest.approx(5.0 * 1.5)

    payload = calc.payload()
    assert payload is not None
    assert len(payload.vertices) == 8


def test_heptagonal_antiprism_payload_counts():
    result = HeptagonalAntiprismSolidService.build(base_edge=2.0, height=3.0)
    payload = result.payload
    metrics = result.metrics

    assert len(payload.vertices) == 14
    assert len(payload.edges) == 28
    assert len(payload.faces) == 16
    assert metrics.base_area == pytest.approx((7 * 2.0 ** 2) / (4 * math.tan(math.pi / 7)))
    assert metrics.volume == pytest.approx(payload.metadata['volume'])
