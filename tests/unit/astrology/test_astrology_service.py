"""Integration coverage for the Astrology pillar's OpenAstro2 wiring."""
from datetime import datetime, timezone

import pytest

from src.pillars.astrology.models import AstrologyEvent, ChartRequest, GeoLocation
from src.pillars.astrology.services import OpenAstroNotAvailableError, OpenAstroService


@pytest.mark.integration
def test_openastro_service_generates_chart_payload():
    """Ensure OpenAstro2 can compute a basic natal chart via the service wrapper."""
    try:
        service = OpenAstroService()
    except OpenAstroNotAvailableError as exc:  # pragma: no cover - environmental skip
        pytest.skip(f"OpenAstro2 unavailable: {exc}")

    location = GeoLocation(name="Jerusalem", latitude=31.7683, longitude=35.2137, elevation=754)
    event = AstrologyEvent(
        name="Baseline",
        timestamp=datetime(1990, 1, 1, 12, 0, tzinfo=timezone.utc),
        location=location,
        timezone_offset=0.0,
    )
    request = ChartRequest(primary_event=event, include_svg=False)

    result = service.generate_chart(request)

    assert result.planet_positions, "Expected planet positions in chart output"
    assert result.house_positions, "Expected house cusps to be populated"
    assert isinstance(result.raw_payload, dict)


@pytest.mark.integration
def test_default_settings_returns_independent_copy():
    try:
        service = OpenAstroService()
    except OpenAstroNotAvailableError as exc:  # pragma: no cover - environmental skip
        pytest.skip(f"OpenAstro2 unavailable: {exc}")

    first = service.default_settings()
    second = service.default_settings()

    assert first == second
    first.setdefault("astrocfg", {})["houses_system"] = "W"
    assert second.get("astrocfg", {}).get("houses_system") != "W"