"""Tychos/Skyfield integration helpers for the astrology pillar."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Sequence


class TychosSkyfieldNotAvailableError(RuntimeError):
    """Raised when tychos_skyfield or Skyfield are missing."""


class TychosSkyfieldComputationError(RuntimeError):
    """Raised when a Tychos calculation fails."""


@dataclass(slots=True)
class TychosBodyPosition:
    name: str
    ra_hours: float
    dec_degrees: float
    distance_au: float
    ra_hms: str
    dec_dms: str


@dataclass(slots=True)
class TychosSnapshot:
    timestamp: datetime
    positions: List[TychosBodyPosition]


class TychosSkyfieldService:
    """Facade around tychos_skyfield that returns normalized RA/Dec payloads."""

    DEFAULT_BODIES: Sequence[str] = (
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
    )

    def __init__(
        self,
        *,
        data_dir: Optional[Path] = None,
        ephemeris_file: str = "de421.bsp",
    ) -> None:
        try:
            from skyfield.api import Loader, load
            from tychos_skyfield import skyfieldlib as TS
        except ImportError as exc:  # pragma: no cover - environmental guard
            raise TychosSkyfieldNotAvailableError(
                "tychos_skyfield or skyfield is not installed. "
                "Run 'pip install tychos_skyfield skyfield'."
            ) from exc

        self._tychos = TS
        self._loader = Loader(str(data_dir)) if data_dir else load
        self._timescale = self._loader.timescale()

        try:
            self._ephemeris = self._loader(ephemeris_file)
        except Exception as exc:  # pragma: no cover - relies on network/file
            raise TychosSkyfieldComputationError(
                f"Failed to load ephemeris '{ephemeris_file}'."
            ) from exc

        try:
            self._earth_sf = self._ephemeris["Earth"]
            self._earth_ref = TS.ReferencePlanet("Earth", self._ephemeris)
        except Exception as exc:  # pragma: no cover - defensive guard
            raise TychosSkyfieldComputationError("Failed to initialize Earth reference.") from exc

    def list_bodies(self) -> List[str]:
        """Return observable object labels, falling back to defaults."""
        try:
            return list(self._tychos.TychosSkyfield.get_observable_objects())
        except Exception:
            return list(self.DEFAULT_BODIES)

    def compute_positions(
        self,
        when: datetime,
        bodies: Optional[Sequence[str]] = None,
    ) -> TychosSnapshot:
        moment = self._normalize_datetime(when)
        sf_time = self._timescale.from_datetime(moment)
        targets = tuple(bodies) if bodies else tuple(self.DEFAULT_BODIES)

        positions: List[TychosBodyPosition] = []
        for body in targets:
            try:
                tychos_obj = self._tychos.TychosSkyfield(body, self._earth_ref)
                astrometric = self._earth_sf.at(sf_time).observe(tychos_obj).apparent()
                ra_angle, dec_angle, distance = astrometric.radec()
            except Exception as exc:  # pragma: no cover - upstream safety
                raise TychosSkyfieldComputationError(
                    f"Tychos failed to calculate positions for '{body}'."
                ) from exc

            positions.append(
                TychosBodyPosition(
                    name=body,
                    ra_hours=float(ra_angle.hours),
                    dec_degrees=float(dec_angle.degrees),
                    distance_au=float(distance.au),
                    ra_hms=ra_angle.hstr(),
                    dec_dms=dec_angle.dstr(),
                )
            )

        return TychosSnapshot(timestamp=moment, positions=positions)

    @staticmethod
    def _normalize_datetime(moment: datetime) -> datetime:
        if moment.tzinfo is None:
            return moment.replace(tzinfo=timezone.utc)
        return moment.astimezone(timezone.utc)
