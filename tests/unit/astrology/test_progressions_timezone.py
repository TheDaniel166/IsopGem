"""Tests for progressions and return timezone handling."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from pillars.astrology.models.chart_models import (
    AstrologyEvent,
    ChartRequest,
    ChartResult,
    GeoLocation,
    HousePosition,
    PlanetPosition,
)
from pillars.astrology.services import progressions_service
from pillars.astrology.services.progressions_service import ProgressionsService
from pillars.astrology.services import returns_service
from pillars.astrology.services.returns_service import ReturnsService


class DummyEphemeris:
    def get_geocentric_ecliptic_position(self, body_name: str, dt: datetime) -> float:
        return 100.0

    def get_extended_data(self, body_name: str, dt: datetime) -> dict:
        return {"geo_speed": 1.0}


class DummyEphemerisProvider:
    @classmethod
    def get_instance(cls) -> DummyEphemeris:
        return DummyEphemeris()


class DummyOpenAstro:
    def __init__(self, natal_chart: ChartResult, progressed_chart: ChartResult):
        self._natal = natal_chart
        self._progressed = progressed_chart
        self.last_request: ChartRequest | None = None

    def generate_chart(self, request: ChartRequest) -> ChartResult:
        self.last_request = request
        if request.chart_type == "Progressed":
            return self._progressed
        return self._natal


def _chart_with_sun(degree: float) -> ChartResult:
    planets = [PlanetPosition(name="Sun", degree=degree, sign_index=int(degree // 30))]
    houses = [HousePosition(number=i + 1, degree=i * 30.0) for i in range(12)]
    return ChartResult(chart_type="Radix", planet_positions=planets, house_positions=houses)


def test_solar_arc_shifts_houses(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(progressions_service, "EphemerisProvider", DummyEphemerisProvider)
    natal_chart = _chart_with_sun(10.0)
    progressed_chart = _chart_with_sun(40.0)
    openastro = DummyOpenAstro(natal_chart, progressed_chart)
    service = ProgressionsService(openastro)

    event = AstrologyEvent(
        name="Natal",
        timestamp=datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc),
        location=GeoLocation(name="Test", latitude=0.0, longitude=0.0, elevation=0.0),
    )
    request = ChartRequest(primary_event=event)

    result = service.calculate_solar_arc(request, datetime(2025, 1, 1, tzinfo=timezone.utc))

    assert result.house_positions[0].degree == pytest.approx(30.0)
    assert result.house_positions[1].degree == pytest.approx(60.0)


def test_secondary_progression_accepts_naive_target_date(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(progressions_service, "EphemerisProvider", DummyEphemerisProvider)
    openastro = DummyOpenAstro(_chart_with_sun(10.0), _chart_with_sun(20.0))
    service = ProgressionsService(openastro)

    event = AstrologyEvent(
        name="Natal",
        timestamp=datetime(2000, 1, 1, 12, 0, tzinfo=timezone.utc),
        location=GeoLocation(name="Test", latitude=0.0, longitude=0.0, elevation=0.0),
    )
    request = ChartRequest(primary_event=event)

    service.calculate_secondary_progression(request, datetime(2025, 1, 1))

    assert openastro.last_request is not None
    assert openastro.last_request.primary_event.timestamp.tzinfo is not None


def test_return_preserves_timezone_offset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(returns_service, "EphemerisProvider", DummyEphemerisProvider)
    service = ReturnsService()

    event = AstrologyEvent(
        name="Natal",
        timestamp=datetime(2000, 1, 1, 12, 0),
        location=GeoLocation(name="Test", latitude=0.0, longitude=0.0, elevation=0.0),
        timezone_offset=-5.0,
    )

    result = service.calculate_return(event, 2025)

    assert result.timezone_offset == -5.0
    assert result.timestamp.tzinfo is not None
    assert result.timestamp.utcoffset() == timedelta(hours=-5)
