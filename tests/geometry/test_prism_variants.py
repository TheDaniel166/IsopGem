"""Unit tests covering oblique and truncated prism variants."""
import math

import pytest

from src.pillars.geometry.services import (
    ObliquePrismSolidService,
    ObliquePrismSolidCalculator,
    PrismaticFrustumSolidService,
    PrismaticFrustumSolidCalculator,
)


def test_oblique_prism_service_metrics_match_geometry_helpers():
    skew_x = 0.8
    skew_y = -0.6
    height = 5.0
    result = ObliquePrismSolidService.build(base_edge=2.5, height=height, skew_x=skew_x, skew_y=skew_y)
    payload = result.payload
    metrics = result.metrics

    assert len(payload.vertices) == 12  # 2 * SIDES (6)
    assert len(payload.edges) == 18
    assert len(payload.faces) == 8

    skew_mag = math.hypot(skew_x, skew_y)
    assert metrics.skew_magnitude == pytest.approx(skew_mag)
    assert metrics.lateral_edge_length == pytest.approx(math.sqrt(height ** 2 + skew_mag ** 2))

    base_area = metrics.base_area
    assert metrics.volume == pytest.approx(base_area * height)
    assert payload.metadata['surface_area'] == pytest.approx(metrics.surface_area)


def test_oblique_prism_calculator_handles_skew_and_volume():
    calc = ObliquePrismSolidCalculator(base_edge=2.0, height=4.0, skew_x=0.5, skew_y=0.25)

    assert calc.set_property('skew_x', 1.1)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['skew_x'] == pytest.approx(1.1)
    assert props['skew_magnitude'] == pytest.approx(math.hypot(1.1, 0.25))

    props = {prop.key: prop.value for prop in calc.properties()}
    base_area = props['base_area']
    assert base_area is not None
    target_volume = base_area * 7.0
    assert calc.set_property('volume', target_volume)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['height'] == pytest.approx(7.0)
    assert props['volume'] == pytest.approx(target_volume)


def test_prismatic_frustum_service_metrics():
    result = PrismaticFrustumSolidService.build(bottom_edge=4.0, top_edge=2.0, height=3.0)
    payload = result.payload
    metrics = result.metrics

    assert len(payload.vertices) == 12
    assert len(payload.faces) == 8

    assert metrics.bottom_edge == pytest.approx(4.0)
    assert metrics.top_edge == pytest.approx(2.0)
    assert metrics.bottom_area > metrics.top_area

    # Volume should match classical frustum formula
    base_bottom = metrics.bottom_area
    base_top = metrics.top_area
    expected_volume = (metrics.height / 3.0) * (base_bottom + base_top + math.sqrt(base_bottom * base_top))
    assert metrics.volume == pytest.approx(expected_volume)


def test_prismatic_frustum_calculator_volume_update():
    calc = PrismaticFrustumSolidCalculator(bottom_edge=3.5, top_edge=2.5, height=4.0)

    props = {prop.key: prop.value for prop in calc.properties()}
    base_bottom = props['bottom_area']
    base_top = props['top_area']
    assert base_bottom is not None
    assert base_top is not None
    target_volume = (6.0 / 3.0) * (base_bottom + base_top + math.sqrt(base_bottom * base_top))
    assert calc.set_property('volume', target_volume)

    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['height'] == pytest.approx(6.0)
    assert props['volume'] == pytest.approx(target_volume)

    payload = calc.payload()
    assert payload is not None
    assert len(payload.vertices) == 12
