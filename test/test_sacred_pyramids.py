"""Tests for golden and step pyramid services/calculators."""
import math

import pytest

from src.pillars.geometry.services import (
    GoldenPyramidSolidService,
    GoldenPyramidSolidCalculator,
    StepPyramidSolidService,
    StepPyramidSolidCalculator,
)


def test_golden_pyramid_metrics_follow_phi_ratio():
    base_edge = 440.0
    result = GoldenPyramidSolidService.build(base_edge=base_edge)
    metrics = result.metrics
    half_base = base_edge / 2.0
    assert metrics.slant_height / half_base == pytest.approx((1.0 + math.sqrt(5.0)) / 2.0)
    expected_height = half_base * math.sqrt(((1.0 + math.sqrt(5.0)) / 2.0) ** 2 - 1.0)
    assert metrics.height == pytest.approx(expected_height)
    assert metrics.volume == pytest.approx((base_edge ** 2 * expected_height) / 3.0)


def test_golden_pyramid_calculator_accepts_height_and_volume():
    calc = GoldenPyramidSolidCalculator(base_edge=300.0)
    target_height = 200.0
    assert calc.set_property('height', target_height)
    props = {prop.key: prop.value for prop in calc.properties()}
    base_edge_val = props['base_edge']
    slant_height_val = props['slant_height']
    volume_val = props['volume']
    assert base_edge_val is not None and slant_height_val is not None and volume_val is not None
    half_base = base_edge_val / 2.0
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    assert slant_height_val == pytest.approx(phi * half_base)

    new_volume = volume_val * 1.5
    assert calc.set_property('volume', new_volume)
    props = {prop.key: prop.value for prop in calc.properties()}
    base_edge_val = props['base_edge']
    height_val = props['height']
    assert base_edge_val is not None and height_val is not None
    computed_volume = (base_edge_val ** 2 * height_val) / 3.0
    assert computed_volume == pytest.approx(new_volume)


def test_step_pyramid_metrics_sum_layer_volumes():
    base_edge = 200.0
    top_edge = 80.0
    height = 120.0
    tiers = 4
    result = StepPyramidSolidService.build(base_edge=base_edge, top_edge=top_edge, height=height, tiers=tiers)
    metrics = result.metrics
    step_height = height / tiers
    edge_sizes = [base_edge - (base_edge - top_edge) * (i / tiers) for i in range(tiers)]
    expected_volume = step_height * sum(edge ** 2 for edge in edge_sizes)
    assert metrics.volume == pytest.approx(expected_volume)
    expected_lateral = 4.0 * step_height * sum(edge_sizes)
    assert metrics.lateral_area == pytest.approx(expected_lateral)
    assert metrics.step_height == pytest.approx(step_height)


def test_step_pyramid_calculator_updates_tiers():
    calc = StepPyramidSolidCalculator(base_edge=180.0, top_edge=60.0, height=90.0, tiers=3)
    assert calc.set_property('tiers', 6)
    props = {prop.key: prop.value for prop in calc.properties()}
    tiers_val = props['tiers']
    step_height_val = props['step_height']
    assert tiers_val is not None and step_height_val is not None
    assert tiers_val == pytest.approx(6.0)
    assert step_height_val == pytest.approx(90.0 / 6.0)
    assert calc.set_property('base_edge', 150.0)
    props = {prop.key: prop.value for prop in calc.properties()}
    base_edge_val = props['base_edge']
    assert base_edge_val is not None
    assert base_edge_val == pytest.approx(150.0)
    payload = calc.payload()
    assert payload is not None
    assert len(payload.vertices) == (6 + 1) * 4
