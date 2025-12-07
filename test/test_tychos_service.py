"""Integration smoke tests for the Tychos/Skyfield service."""
from datetime import datetime, timezone

import pytest

from src.pillars.astrology.services import (
    TychosSkyfieldComputationError,
    TychosSkyfieldNotAvailableError,
    TychosSkyfieldService,
)


@pytest.mark.integration
def test_tychos_service_computes_positions():
    try:
        service = TychosSkyfieldService()
    except TychosSkyfieldNotAvailableError as exc:  # pragma: no cover - environment guard
        pytest.skip(f"Tychos service unavailable: {exc}")
    except TychosSkyfieldComputationError as exc:  # pragma: no cover - missing ephemeris
        pytest.skip(f"Tychos ephemeris unavailable: {exc}")

    snapshot = service.compute_positions(
        datetime(2020, 6, 21, 12, 0, tzinfo=timezone.utc),
        bodies=["Jupiter"],
    )

    assert snapshot.positions, "Expected at least one body in the result"
    entry = snapshot.positions[0]
    assert entry.ra_hms
    assert entry.dec_dms
    assert isinstance(entry.distance_au, float)


@pytest.mark.integration
def test_tychos_service_lists_bodies():
    try:
        service = TychosSkyfieldService()
    except (TychosSkyfieldNotAvailableError, TychosSkyfieldComputationError) as exc:  # pragma: no cover
        pytest.skip(f"Tychos service unavailable: {exc}")

    bodies = service.list_bodies()
    assert bodies, "Expected observable bodies to be returned"
