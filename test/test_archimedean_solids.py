"""Unit tests for Archimedean solid services and calculators."""
from collections import Counter
import math

import pytest

from src.pillars.geometry.services import (
    CuboctahedronSolidService,
    CuboctahedronSolidCalculator,
    TruncatedTetrahedronSolidService,
    TruncatedTetrahedronSolidCalculator,
    TruncatedCubeSolidService,
    TruncatedCubeSolidCalculator,
    TruncatedOctahedronSolidService,
    TruncatedOctahedronSolidCalculator,
    RhombicuboctahedronSolidService,
    RhombicuboctahedronSolidCalculator,
    RhombicosidodecahedronSolidService,
    RhombicosidodecahedronSolidCalculator,
    TruncatedCuboctahedronSolidService,
    TruncatedCuboctahedronSolidCalculator,
    IcosidodecahedronSolidService,
    IcosidodecahedronSolidCalculator,
    TruncatedDodecahedronSolidService,
    TruncatedDodecahedronSolidCalculator,
    TruncatedIcosahedronSolidService,
    TruncatedIcosahedronSolidCalculator,
    TruncatedIcosidodecahedronSolidService,
    TruncatedIcosidodecahedronSolidCalculator,
    SnubCubeSolidService,
    SnubCubeSolidCalculator,
    SnubDodecahedronSolidService,
    SnubDodecahedronSolidCalculator,
)
from src.pillars.geometry.services.archimedean_data import ARCHIMEDEAN_DATA


SOLID_CASES = [
    ('cuboctahedron', CuboctahedronSolidService, CuboctahedronSolidCalculator),
    ('truncated_tetrahedron', TruncatedTetrahedronSolidService, TruncatedTetrahedronSolidCalculator),
    ('truncated_cube', TruncatedCubeSolidService, TruncatedCubeSolidCalculator),
    ('truncated_octahedron', TruncatedOctahedronSolidService, TruncatedOctahedronSolidCalculator),
    ('rhombicuboctahedron', RhombicuboctahedronSolidService, RhombicuboctahedronSolidCalculator),
    ('truncated_cuboctahedron', TruncatedCuboctahedronSolidService, TruncatedCuboctahedronSolidCalculator),
    ('snub_cube', SnubCubeSolidService, SnubCubeSolidCalculator),
    ('icosidodecahedron', IcosidodecahedronSolidService, IcosidodecahedronSolidCalculator),
    ('truncated_dodecahedron', TruncatedDodecahedronSolidService, TruncatedDodecahedronSolidCalculator),
    ('truncated_icosahedron', TruncatedIcosahedronSolidService, TruncatedIcosahedronSolidCalculator),
    ('rhombicosidodecahedron', RhombicosidodecahedronSolidService, RhombicosidodecahedronSolidCalculator),
    ('truncated_icosidodecahedron', TruncatedIcosidodecahedronSolidService, TruncatedIcosidodecahedronSolidCalculator),
    ('snub_dodecahedron', SnubDodecahedronSolidService, SnubDodecahedronSolidCalculator),
]


@pytest.mark.parametrize("key,service_cls,_", SOLID_CASES)
def test_archimedean_service_matches_dataset(key, service_cls, _):
    result = service_cls.build(edge_length=1.5)
    payload = result.payload
    metrics = result.metrics
    data = ARCHIMEDEAN_DATA[key]

    assert len(payload.vertices) == len(data['vertices'])
    assert len(payload.faces) == len(data['faces'])
    assert len(payload.edges) > 0
    assert payload.metadata['face_count'] == len(data['faces'])
    assert payload.metadata['vertex_count'] == len(data['vertices'])
    assert payload.metadata['edge_count'] == len(payload.edges)
    assert metrics.edge_length == pytest.approx(1.5)

    expected_face_sides = Counter(len(face) for face in data['faces'])
    assert metrics.face_sides == expected_face_sides
    assert math.isclose(sum(metrics.face_sides.values()), len(payload.faces))


@pytest.mark.parametrize("key,_,calculator_cls", SOLID_CASES)
def test_archimedean_calculator_scaling(key, _, calculator_cls):
    calc = calculator_cls(edge_length=1.0)
    props = {prop.key: prop.value for prop in calc.properties()}
    base_volume = props['volume']
    assert base_volume is not None and base_volume > 0
    target_volume = base_volume * 1.5
    assert calc.set_property('volume', target_volume)

    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['volume'] == pytest.approx(target_volume)
    assert props['edge_length'] == pytest.approx(1.0 * (target_volume / base_volume) ** (1.0 / 3.0))
    assert calc.payload() is not None

    calc_area = calculator_cls(edge_length=1.0)
    props = {prop.key: prop.value for prop in calc_area.properties()}
    base_area = props['surface_area']
    assert base_area is not None and base_area > 0
    target_area = base_area * 0.5
    assert calc_area.set_property('surface_area', target_area)

    props = {prop.key: prop.value for prop in calc_area.properties()}
    assert props['surface_area'] == pytest.approx(target_area)
    assert props['edge_length'] == pytest.approx(1.0 * math.sqrt(target_area / base_area))
