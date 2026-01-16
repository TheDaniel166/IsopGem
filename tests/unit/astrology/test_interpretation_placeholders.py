"""Tests for placeholder messages when interpretation data is missing."""
from __future__ import annotations

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))

from pillars.astrology.models.chart_models import ChartResult
from pillars.astrology.models.interpretation_models import RichInterpretationContent
from pillars.astrology.services.aspects_service import AspectDefinition, CalculatedAspect
from pillars.astrology.services.interpretation_service import InterpretationService


class DummyRepo:
    def __init__(self, transit_content=None, synastry_content=None):
        self._transit_content = transit_content
        self._synastry_content = synastry_content

    def get_transit_text(self, *args, **kwargs):
        return self._transit_content

    def get_synastry_text(self, *args, **kwargs):
        return self._synastry_content


def _sample_aspects() -> list[CalculatedAspect]:
    aspect = AspectDefinition("Conjunction", 0, 8.0, "*", True)
    return [CalculatedAspect("Sun", "Moon", aspect, 1.0, True)]


def test_transit_placeholder_when_missing_data():
    service = InterpretationService(repository=DummyRepo())
    report = service.interpret_transits(
        ChartResult(chart_type="Radix"),
        ChartResult(chart_type="Radix"),
        _sample_aspects(),
    )

    assert report.segments
    assert "Interpretation Unavailable" in report.segments[0].title
    assert "transits.json" in report.segments[0].content.text


def test_synastry_placeholder_when_missing_data():
    service = InterpretationService(repository=DummyRepo())
    report = service.interpret_synastry(
        ChartResult(chart_type="Radix"),
        ChartResult(chart_type="Radix"),
        _sample_aspects(),
    )

    assert report.segments
    assert "Interpretation Unavailable" in report.segments[0].title
    assert "synastry.json" in report.segments[0].content.text


def test_placeholder_skipped_when_content_exists():
    content = RichInterpretationContent(text="Sample text")
    service = InterpretationService(repository=DummyRepo(transit_content=content))
    report = service.interpret_transits(
        ChartResult(chart_type="Radix"),
        ChartResult(chart_type="Radix"),
        _sample_aspects(),
    )

    assert report.segments
    assert report.segments[0].content.text == "Sample text"
