"""Tests for the astrology chart storage service."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared.database import Base

from src.pillars.astrology.models import AstrologyEvent, ChartRequest, ChartResult, GeoLocation
from src.pillars.astrology.services.chart_storage_service import ChartStorageService


def _build_service() -> ChartStorageService:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)

    @contextmanager
    def session_scope():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    return ChartStorageService(session_factory=session_scope)


def _sample_request(name: str) -> ChartRequest:
    location = GeoLocation(name="Testville", latitude=35.0, longitude=-90.0, elevation=100.0)
    event = AstrologyEvent(
        name=name,
        timestamp=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
        location=location,
        timezone_offset=0.0,
    )
    settings = {"astrocfg": {"houses_system": "P"}}
    return ChartRequest(primary_event=event, settings=settings)


def _sample_result() -> ChartResult:
    return ChartResult(chart_type="Radix")


def test_save_and_load_chart_round_trip():
    service = _build_service()
    request = _sample_request("Client A")
    result = _sample_result()

    chart_id = service.save_chart(
        name="Client A",
        request=request,
        result=result,
        categories=["Clients"],
        tags=["natal", "first"],
        description="Initial session",
    )

    summaries = service.search(text="client")
    assert summaries
    assert summaries[0].chart_id == chart_id

    loaded = service.load_chart(chart_id)
    assert loaded is not None
    assert loaded.request.primary_event.location.latitude == request.primary_event.location.latitude
    assert "Clients" in loaded.categories
    assert "natal" in loaded.tags
    assert loaded.description == "Initial session"


def test_search_filters_by_category():
    service = _build_service()
    service.save_chart(
        name="Family",
        request=_sample_request("Family"),
        result=_sample_result(),
        categories=["Family"],
        tags=[],
    )
    service.save_chart(
        name="Work",
        request=_sample_request("Work"),
        result=_sample_result(),
        categories=["Clients"],
        tags=[],
    )

    only_family = service.search(categories=["family"])
    assert len(only_family) == 1
    assert only_family[0].name == "Family"