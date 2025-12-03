"""Unit tests for the rectangular prism solid service and calculator."""
import math

import pytest

from src.pillars.geometry.services import (
    RectangularPrismSolidService,
    RectangularPrismSolidCalculator,
)


def test_rectangular_prism_metrics_match_closed_form():
    result = RectangularPrismSolidService.build(length=6.0, width=4.0, height=3.0)
    payload = result.payload
    assert len(payload.vertices) == 8
    assert len(payload.edges) == 12
    assert len(payload.faces) == 6

    metrics = result.metrics
    assert metrics.base_area == pytest.approx(24.0)
    assert metrics.base_perimeter == pytest.approx(20.0)
    assert metrics.lateral_area == pytest.approx(60.0)
    assert metrics.surface_area == pytest.approx(108.0)
    assert metrics.volume == pytest.approx(72.0)
    assert metrics.face_diagonal_length == pytest.approx(math.hypot(6.0, 3.0))
    assert metrics.face_diagonal_width == pytest.approx(math.hypot(4.0, 3.0))
    assert metrics.space_diagonal == pytest.approx(math.sqrt(6.0 ** 2 + 4.0 ** 2 + 3.0 ** 2))

    metadata = payload.metadata
    assert metadata['volume'] == pytest.approx(metrics.volume)
    assert metadata['space_diagonal'] == pytest.approx(metrics.space_diagonal)


def test_rectangular_prism_calculator_updates_from_volume():
    calc = RectangularPrismSolidCalculator(length=5.0, width=4.0, height=2.0)

    assert calc.set_property('volume', 400.0)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['height'] == pytest.approx(400.0 / (5.0 * 4.0))
    assert props['volume'] == pytest.approx(400.0)

    assert calc.set_property('height', 10.0)
    props = {prop.key: prop.value for prop in calc.properties()}
    assert props['volume'] == pytest.approx(5.0 * 4.0 * 10.0)

    payload = calc.payload()
    assert payload is not None
    assert len(payload.vertices) == 8
