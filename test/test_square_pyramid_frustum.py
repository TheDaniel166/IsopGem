"""Unit tests for the square pyramid frustum solid service and calculator."""
import math

import pytest

from src.pillars.geometry.services import (
    SquarePyramidFrustumSolidService,
    SquarePyramidFrustumSolidCalculator,
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

    # Adjust using top area (should set top edge accordingly)
    assert calc.set_property('top_area', 16.0)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['top_edge'] == pytest.approx(4.0)

    # Adjust height via slant height input
    slant_height = 6.0
    assert calc.set_property('slant_height', slant_height)
    props = {prop.key: prop.value for prop in calc.properties()}
    diff = abs(props['base_edge'] - props['top_edge']) / 2.0
    expected_height = math.sqrt(slant_height ** 2 - diff ** 2)
    assert props['height'] == pytest.approx(expected_height)

    # Apply volume constraint
    expected_volume = (props['height'] / 3.0) * (
        props['base_edge'] ** 2 + props['base_edge'] * props['top_edge'] + props['top_edge'] ** 2
    )
    assert calc.set_property('volume', expected_volume)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['volume'] == pytest.approx(expected_volume)

    payload = calc.payload()
    assert payload is not None
    assert len(payload.vertices) == 8
