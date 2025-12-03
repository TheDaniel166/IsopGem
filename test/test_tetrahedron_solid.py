"""Unit tests for the tetrahedron solid service and calculator."""
import math

import pytest

from src.pillars.geometry.services.tetrahedron_solid import (
    TetrahedronSolidCalculator,
    TetrahedronSolidService,
)


def test_metrics_match_closed_form():
    result = TetrahedronSolidService.build(edge_length=2.0)

    assert len(result.payload.vertices) == 4
    assert len(result.payload.edges) == 6
    assert len(result.payload.faces) == 4

    expected_volume = 8.0 / (6.0 * math.sqrt(2.0))
    expected_height = math.sqrt(2.0 / 3.0) * 2.0
    expected_face_area = (math.sqrt(3.0) / 4.0) * 4.0
    expected_midradius = 2.0 * math.sqrt(2.0) / 4.0
    expected_circum = 2.0 * math.pi * result.metrics.circumradius

    assert result.metrics.volume == pytest.approx(expected_volume)
    assert result.metrics.height == pytest.approx(expected_height)
    assert result.metrics.face_area == pytest.approx(expected_face_area)
    assert result.metrics.midradius == pytest.approx(expected_midradius)
    assert result.metrics.circumcircle_circumference == pytest.approx(expected_circum)


def test_rejects_non_positive_edge_length():
    with pytest.raises(ValueError):
        TetrahedronSolidService.build(edge_length=0.0)
    with pytest.raises(ValueError):
        TetrahedronSolidService.build(edge_length=-2.5)


def test_calculator_updates_from_surface_area():
    calc = TetrahedronSolidCalculator()
    surface_area = math.sqrt(3.0) * 4.0  # edge length 2
    assert calc.set_property('surface_area', surface_area)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['edge_length'] == pytest.approx(2.0)
    assert props['volume'] == pytest.approx(TetrahedronSolidService.build(2.0).metrics.volume)
    assert props['midradius'] == pytest.approx(2.0 * math.sqrt(2.0) / 4.0)


def test_calculator_updates_from_volume():
    target_edge = 3.5
    volume = target_edge ** 3 / (6.0 * math.sqrt(2.0))
    calc = TetrahedronSolidCalculator()
    assert calc.set_property('volume', volume)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['edge_length'] == pytest.approx(target_edge)
    assert calc.payload() is not None


def test_calculator_rejects_invalid_inputs():
    calc = TetrahedronSolidCalculator()
    assert not calc.set_property('edge_length', -1.0)
    assert not calc.set_property('surface_area', 0.0)


def test_calculator_accepts_circumference_inputs():
    target_edge = 1.25
    result = TetrahedronSolidService.build(target_edge)
    calc = TetrahedronSolidCalculator()
    assert calc.set_property('incircle_circumference', result.metrics.incircle_circumference)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['edge_length'] == pytest.approx(target_edge)
