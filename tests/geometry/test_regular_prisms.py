"""Unit tests for regular prism solid services and calculators."""
import math

import pytest

from src.pillars.geometry.services import (
    TriangularPrismSolidService,
    PentagonalPrismSolidCalculator,
    HeptagonalPrismSolidService,
)


def test_triangular_prism_service_generates_expected_metrics():
    result = TriangularPrismSolidService.build(base_edge=3.0, height=5.0)
    payload = result.payload
    assert len(payload.vertices) == 6
    assert len(payload.edges) == 9
    assert len(payload.faces) == 5

    metrics = result.metrics
    base_area = (math.sqrt(3.0) / 4.0) * (3.0 ** 2)
    assert metrics.base_area == pytest.approx(base_area)
    assert metrics.base_perimeter == pytest.approx(9.0)
    assert metrics.base_apothem == pytest.approx(3.0 / (2.0 * math.tan(math.pi / 3.0)))
    assert metrics.base_circumradius == pytest.approx(3.0 / (2.0 * math.sin(math.pi / 3.0)))
    assert metrics.lateral_area == pytest.approx(9.0 * 5.0)
    assert metrics.surface_area == pytest.approx(9.0 * 5.0 + 2.0 * base_area)
    assert metrics.volume == pytest.approx(base_area * 5.0)

    metadata = payload.metadata
    assert metadata['surface_area'] == pytest.approx(metrics.surface_area)
    assert metadata['volume'] == pytest.approx(metrics.volume)


def test_pentagonal_prism_calculator_handles_apothem_and_volume():
    calc = PentagonalPrismSolidCalculator(base_edge=2.0, height=4.0)

    target_apothem = 3.0
    assert calc.set_property('base_apothem', target_apothem)
    props = {prop.key: prop.value for prop in calc.properties()}
    expected_edge = 2.0 * target_apothem * math.tan(math.pi / 5.0)
    assert props['base_edge'] == pytest.approx(expected_edge)

    base_area = props['base_area']
    target_height = 7.5
    target_volume = base_area * target_height
    assert calc.set_property('volume', target_volume)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['height'] == pytest.approx(target_height)
    assert props['volume'] == pytest.approx(target_volume)

    payload = calc.payload()
    assert payload is not None
    assert len(payload.vertices) == 10


def test_heptagonal_prism_service_payload_structure():
    result = HeptagonalPrismSolidService.build(base_edge=2.5, height=6.0)
    payload = result.payload
    assert len(payload.vertices) == 14
    assert len(payload.edges) == 21
    assert len(payload.faces) == 9

    metrics = result.metrics
    perimeter = 7 * 2.5
    base_area = (7 * 2.5 ** 2) / (4 * math.tan(math.pi / 7))
    assert metrics.base_perimeter == pytest.approx(perimeter)
    assert metrics.base_area == pytest.approx(base_area)
    assert metrics.lateral_area == pytest.approx(perimeter * 6.0)
    assert metrics.volume == pytest.approx(base_area * 6.0)
