"""Venus ↔ Tzolkin overlay service.

This is the "ready to wire" integration point for the Time Mechanics calendar.
It does NOT touch UI. It only returns DTOs that a calendar view can render later.

Sovereignty rules:
- Time Mechanics may import shared services.
- Shared services must not import pillar code.
"""

from __future__ import annotations

import time
from datetime import date, datetime, time as dtime, timedelta, timezone
from typing import Iterable, Sequence

from shared.services.ephemeris_provider import EphemerisProvider
from shared.services.venus_phenomena_service import VenusPhenomenaService, VenusEvent

from ..models.venus_tzolkin_models import VenusOverlayKind, VenusTzolkinOverlayEvent
from .tzolkin_service import TzolkinService


def _as_utc_datetime(d: date, at: dtime = dtime(0, 0)) -> datetime:
    return datetime.combine(d, at).replace(tzinfo=timezone.utc)


class VenusTzolkinOverlayService:
    """Build Venus phenomena overlays for the Tzolkin calendar."""

    def __init__(
        self,
        tzolkin_service: TzolkinService | None = None,
        venus_service: VenusPhenomenaService | None = None,
    ):
        self._tzolkin = tzolkin_service or TzolkinService()
        self._venus = venus_service or VenusPhenomenaService(cache_minutes=30)
        self._ephemeris = EphemerisProvider.get_instance()

    def wait_for_ephemeris(self, timeout_s: float = 30.0, poll_s: float = 0.1) -> bool:
        """Block until ephemeris is ready, or timeout.

        Returns:
            True if loaded, False if timed out.
        """
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            if self._ephemeris.is_loaded():
                return True
            time.sleep(poll_s)
        return self._ephemeris.is_loaded()

    def get_overlay_events_for_range(
        self,
        start_date: date,
        end_date: date,
        *,
        visibility_threshold_deg: float = 10.0,
        sample_step: timedelta = timedelta(hours=6),
        include: Sequence[str] = ("conjunctions", "elongations", "visibility"),
    ) -> list[VenusTzolkinOverlayEvent]:
        """Compute Venus events in [start_date, end_date] and map each to a Tzolkin day.

        Note: mapping uses the UTC date of the event timestamp.
        """
        if end_date < start_date:
            start_date, end_date = end_date, start_date

        # Expand to full-day UTC range.
        start_dt = _as_utc_datetime(start_date, dtime(0, 0))
        # End is inclusive; sample/refine may land inside the last day.
        end_dt = _as_utc_datetime(end_date, dtime(23, 59, 59))

        if not self.wait_for_ephemeris():
            raise RuntimeError("Ephemeris not loaded (timeout).")

        venus_events: list[VenusEvent] = []

        include_set = set(include)
        if "visibility" in include_set:
            windows = self._venus.compute_visibility_windows(
                start_dt,
                end_dt,
                threshold_deg=visibility_threshold_deg,
                sample_step=sample_step,
            )
            for w_start, w_end in windows:
                s0 = self._venus.get_state(w_start)
                s1 = self._venus.get_state(w_end)
                venus_events.append(VenusEvent(w_start, "invisible_start", s0.elongation_deg, s0.illumination_fraction))
                venus_events.append(VenusEvent(w_end, "invisible_end", s1.elongation_deg, s1.illumination_fraction))

        if "elongations" in include_set:
            venus_events.extend(
                self._venus.compute_greatest_elongations(
                    start_dt,
                    end_dt,
                    sample_step=sample_step,
                )
            )

        if "conjunctions" in include_set:
            venus_events.extend(
                self._venus.compute_conjunctions(
                    start_dt,
                    end_dt,
                    sample_step=sample_step,
                )
            )

        # Convert to Time Mechanics DTOs.
        out: list[VenusTzolkinOverlayEvent] = []
        for evt in sorted(venus_events, key=lambda e: e.dt_utc):
            evt_date = evt.dt_utc.astimezone(timezone.utc).date()
            tz = self._tzolkin.from_gregorian(evt_date)
            out.append(
                VenusTzolkinOverlayEvent(
                    dt_utc=evt.dt_utc,
                    kind=evt.kind,  # type: ignore[assignment]
                    tzolkin=tz,
                    elongation_deg=evt.elongation_deg,
                    illumination_fraction=evt.illumination_fraction,
                )
            )

        # Deduplicate identical timestamps/kinds (can happen when range boundaries clip a window).
        deduped: list[VenusTzolkinOverlayEvent] = []
        seen: set[tuple[str, str]] = set()
        for e in out:
            key = (e.dt_utc.isoformat(), e.kind)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(e)

        return deduped

    def group_by_kin(
        self, events: Iterable[VenusTzolkinOverlayEvent]
    ) -> dict[int, list[VenusTzolkinOverlayEvent]]:
        """Convenience for calendar wiring: kin -> events on that kin day."""
        grouped: dict[int, list[VenusTzolkinOverlayEvent]] = {}
        for e in events:
            grouped.setdefault(e.tzolkin.kin, []).append(e)
        for k in grouped:
            grouped[k].sort(key=lambda x: x.dt_utc)
        return grouped
