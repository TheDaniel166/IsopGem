"""Tests for the tesseract (hypercube) solid service and calculator."""
import math

import pytest

from src.pillars.geometry.services import TesseractSolidService, TesseractSolidCalculator


def test_tesseract_counts_and_faces():
    result = TesseractSolidService.build(edge_length=2.0)
    payload = result.payload
    metrics = result.metrics

    assert len(payload.vertices) == 16
    assert len(payload.edges) == len(set(payload.edges))
    assert len(payload.faces) == 24
    assert metrics.face_count == 24
    assert metrics.vertex_count == 16
    assert metrics.edge_length == pytest.approx(2.0)
    assert metrics.face_sides == {4: 24}

    # All faces should be quads with constant edge length
    first_face = payload.faces[0]
    v0 = payload.vertices[first_face[0]]
    v1 = payload.vertices[first_face[1]]
    measured = math.dist(v0, v1)
    assert measured == pytest.approx(2.0)


def test_tesseract_calculator_scaling_volume_and_area():
    calc = TesseractSolidCalculator(edge_length=1.5)
    props = {prop.key: prop.value for prop in calc.properties()}
    base_volume = props['volume']
    assert base_volume is not None and base_volume > 0
    target_volume = base_volume * 2.5
    assert calc.set_property('volume', target_volume)

    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['volume'] == pytest.approx(target_volume)
    expected_edge = 1.5 * (2.5 ** (1.0 / 3.0))
    assert props['edge_length'] == pytest.approx(expected_edge)

    base_area = props['surface_area']
    assert base_area is not None and base_area > 0
    target_area = base_area * 0.4
    assert calc.set_property('surface_area', target_area)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['surface_area'] == pytest.approx(target_area)
    assert props['edge_length'] == pytest.approx(expected_edge * math.sqrt(0.4))