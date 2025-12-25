"""Unit tests for additional platonic solid services and calculators."""
import math

import pytest

from src.pillars.geometry.services import (
    CubeSolidService,
    CubeSolidCalculator,
    OctahedronSolidService,
    OctahedronSolidCalculator,
    DodecahedronSolidService,
    DodecahedronSolidCalculator,
    IcosahedronSolidService,
    IcosahedronSolidCalculator,
)


def test_cube_metrics_match_closed_form():
    result = CubeSolidService.build(edge_length=2.0)
    assert len(result.payload.vertices) == 8
    assert len(result.payload.edges) == 12
    assert len(result.payload.faces) == 6
    assert result.metrics.volume == pytest.approx(8.0)
    assert result.metrics.surface_area == pytest.approx(24.0)
    assert result.metrics.face_diagonal == pytest.approx(2.0 * math.sqrt(2.0))
    assert result.metrics.space_diagonal == pytest.approx(2.0 * math.sqrt(3.0))
    assert result.metrics.inradius == pytest.approx(1.0)
    assert result.metrics.midradius == pytest.approx(math.sqrt(2.0))
    assert result.metrics.circumradius == pytest.approx(math.sqrt(3.0))


def test_cube_calculator_from_surface_area():
    calc = CubeSolidCalculator()
    assert calc.set_property('surface_area', 54.0)  # edge length should be 3
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['edge_length'] == pytest.approx(3.0)
    assert props['volume'] == pytest.approx(27.0)


def test_octahedron_metrics_against_formulas():
    edge = 2.5
    result = OctahedronSolidService.build(edge)
    assert len(result.payload.vertices) == 6
    assert len(result.payload.edges) == 12
    assert len(result.payload.faces) == 8
    expected_area = 2.0 * math.sqrt(3.0) * edge ** 2
    expected_volume = (math.sqrt(2.0) / 3.0) * edge ** 3
    expected_inradius = (math.sqrt(6.0) / 6.0) * edge
    expected_midradius = 0.5 * edge
    expected_circumradius = (math.sqrt(2.0) / 2.0) * edge
    assert result.metrics.surface_area == pytest.approx(expected_area)
    assert result.metrics.volume == pytest.approx(expected_volume)
    assert result.metrics.inradius == pytest.approx(expected_inradius)
    assert result.metrics.midradius == pytest.approx(expected_midradius)
    assert result.metrics.circumradius == pytest.approx(expected_circumradius)


def test_octahedron_calculator_from_volume():
    edge = 1.75
    volume = (math.sqrt(2.0) / 3.0) * edge ** 3
    calc = OctahedronSolidCalculator()
    assert calc.set_property('volume', volume)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['edge_length'] == pytest.approx(edge)
def test_dodecahedron_metrics_match_closed_form():
    edge = 1.2
    result = DodecahedronSolidService.build(edge)
    expected_area = 3.0 * math.sqrt(25.0 + 10.0 * math.sqrt(5.0)) * edge ** 2
    expected_volume = ((15.0 + 7.0 * math.sqrt(5.0)) / 4.0) * edge ** 3
    assert result.metrics.surface_area == pytest.approx(expected_area)
    assert result.metrics.volume == pytest.approx(expected_volume)


def test_dodecahedron_calculator_from_surface_area():
    edge = 2.0
    area = 3.0 * math.sqrt(25.0 + 10.0 * math.sqrt(5.0)) * edge ** 2
    calc = DodecahedronSolidCalculator()
    assert calc.set_property('surface_area', area)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['edge_length'] == pytest.approx(edge)


def test_icosahedron_metrics_match_closed_form():
    edge = 1.7
    result = IcosahedronSolidService.build(edge)
    expected_area = 5.0 * math.sqrt(3.0) * edge ** 2
    expected_volume = (5.0 * (3.0 + math.sqrt(5.0)) / 12.0) * edge ** 3
    assert result.metrics.surface_area == pytest.approx(expected_area)
    assert result.metrics.volume == pytest.approx(expected_volume)


def test_icosahedron_calculator_from_volume():
    edge = 0.95
    volume = (5.0 * (3.0 + math.sqrt(5.0)) / 12.0) * edge ** 3
    calc = IcosahedronSolidCalculator()
    assert calc.set_property('volume', volume)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['edge_length'] == pytest.approx(edge)