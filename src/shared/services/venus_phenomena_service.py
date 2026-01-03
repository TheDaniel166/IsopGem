"""Venus phenomena computation (events + states).

This module exists to support *Time Mechanics* use-cases:
- Dates of greatest elongations (east/west)
- Conjunctions (inferior/superior)
- Visibility/"occulted" windows (elongation below a threshold)
- Phase/illumination estimates

Design goals
- No large precomputed databases.
- Fast via in-memory caching and coarse-to-fine refinement.
- No pillar-to-pillar imports (shared service).

Notes
- Uses `EphemerisProvider` (Skyfield + JPL kernels) for accurate geometry.
- Phase/illumination is computed from heliocentric ecliptic lat/lon/dist using vector math.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Iterable, Literal, Sequence

from shared.services.ephemeris_provider import EphemerisProvider


EventKind = Literal[
    "inferior_conjunction",
    "superior_conjunction",
    "greatest_elongation_east",
    "greatest_elongation_west",
    "invisible_start",
    "invisible_end",
]


@dataclass(frozen=True)
class VenusState:
    dt_utc: datetime
    elongation_deg: float
    geo_lon_venus_deg: float
    geo_lon_sun_deg: float
    is_retrograde: bool
    phase_angle_deg: float
    illumination_fraction: float


@dataclass(frozen=True)
class VenusEvent:
    dt_utc: datetime
    kind: EventKind
    elongation_deg: float
    illumination_fraction: float


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _dt_from_ts(ts: float) -> datetime:
    # Round to whole seconds to avoid microsecond noise from float timestamps.
    return datetime.fromtimestamp(int(round(ts)), tz=timezone.utc)


def _wrap180(deg: float) -> float:
    v = (deg + 180.0) % 360.0 - 180.0
    return v


def _sph_to_cart(lat_deg: float, lon_deg: float, r: float) -> tuple[float, float, float]:
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    x = r * math.cos(lat) * math.cos(lon)
    y = r * math.cos(lat) * math.sin(lon)
    z = r * math.sin(lat)
    return x, y, z


def _angle_between(u: tuple[float, float, float], v: tuple[float, float, float]) -> float:
    ux, uy, uz = u
    vx, vy, vz = v
    dot = ux * vx + uy * vy + uz * vz
    nu = math.sqrt(ux * ux + uy * uy + uz * uz)
    nv = math.sqrt(vx * vx + vy * vy + vz * vz)
    if nu == 0 or nv == 0:
        return 0.0
    cosang = max(-1.0, min(1.0, dot / (nu * nv)))
    return math.degrees(math.acos(cosang))


class VenusPhenomenaService:
    """Computes Venus phenomena for ranges and provides cached state queries."""

    def __init__(self, cache_minutes: int = 30):
        self._cache_minutes = cache_minutes
        self._provider = EphemerisProvider.get_instance()

    def _bucket_key(self, dt: datetime) -> int:
        dt = _to_utc(dt)
        bucket_s = self._cache_minutes * 60
        return int(dt.timestamp()) // bucket_s

    @lru_cache(maxsize=200_000)
    def _state_by_bucket(self, bucket: int) -> VenusState:
        bucket_s = self._cache_minutes * 60
        dt = datetime.fromtimestamp(bucket * bucket_s, tz=timezone.utc)
        return self._compute_state(dt)

    def get_state(self, dt: datetime) -> VenusState:
        return self._state_by_bucket(self._bucket_key(dt))

    def _compute_state(self, dt: datetime) -> VenusState:
        dt = _to_utc(dt)

        # Fast accurate elongation + retrograde via provider.
        ext = self._provider.get_extended_data("venus", dt)
        elong = float(ext["elongation"])
        is_retro = bool(ext["is_retrograde"])

        geo_lon_v = float(self._provider.get_geocentric_ecliptic_position("venus", dt)) % 360.0
        geo_lon_s = float(self._provider.get_geocentric_ecliptic_position("sun", dt)) % 360.0

        # Phase / illumination from heliocentric vectors (ecliptic frame).
        e_lat, e_lon, e_dist = self._provider.get_heliocentric_ecliptic_latlon_distance("earth", dt)
        v_lat, v_lon, v_dist = self._provider.get_heliocentric_ecliptic_latlon_distance("venus", dt)

        rE = _sph_to_cart(e_lat, e_lon, e_dist)
        rV = _sph_to_cart(v_lat, v_lon, v_dist)

        # V->S is -rV, V->E is rE-rV
        v_to_s = (-rV[0], -rV[1], -rV[2])
        v_to_e = (rE[0] - rV[0], rE[1] - rV[1], rE[2] - rV[2])

        phase_angle = _angle_between(v_to_s, v_to_e)
        illum = (1.0 + math.cos(math.radians(phase_angle))) / 2.0

        return VenusState(
            dt_utc=dt,
            elongation_deg=elong,
            geo_lon_venus_deg=geo_lon_v,
            geo_lon_sun_deg=geo_lon_s,
            is_retrograde=is_retro,
            phase_angle_deg=phase_angle,
            illumination_fraction=illum,
        )

    def compute_visibility_windows(
        self,
        start_dt: datetime,
        end_dt: datetime,
        threshold_deg: float = 10.0,
        sample_step: timedelta = timedelta(hours=6),
    ) -> list[tuple[datetime, datetime]]:
        """Return intervals where elongation < threshold ("occulted" by solar glare).

        The threshold is a pragmatic visibility proxy. Tune per your tradition.
        """
        start_dt = _to_utc(start_dt)
        end_dt = _to_utc(end_dt)

        def f(t: datetime) -> float:
            return self.get_state(t).elongation_deg - threshold_deg

        windows: list[tuple[datetime, datetime]] = []
        t = start_dt
        prev_t = t
        prev_v = f(t)
        in_window = prev_v < 0
        window_start = t if in_window else None

        t += sample_step
        while t <= end_dt:
            cur_v = f(t)
            cur_in = cur_v < 0

            if not in_window and cur_in:
                # entering: bracket crossing
                enter = self._bisect_crossing(prev_t, t, threshold_deg)
                window_start = enter
            elif in_window and not cur_in:
                # exiting
                exit_t = self._bisect_crossing(prev_t, t, threshold_deg)
                if window_start is not None:
                    windows.append((window_start, exit_t))
                window_start = None

            in_window = cur_in
            prev_t, prev_v = t, cur_v
            t += sample_step

        # If still inside at end
        if in_window and window_start is not None:
            windows.append((window_start, end_dt))

        return windows

    def _bisect_crossing(self, a: datetime, b: datetime, threshold_deg: float) -> datetime:
        """Bisection on elongation-threshold across [a,b] (assumes a bracket)."""
        a = _to_utc(a)
        b = _to_utc(b)

        def f(t: datetime) -> float:
            return self.get_state(t).elongation_deg - threshold_deg

        fa = f(a)
        fb = f(b)
        if fa == 0:
            return a.replace(microsecond=0)
        if fb == 0:
            return b.replace(microsecond=0)

        # If not bracketed, return the closer end.
        if (fa < 0) == (fb < 0):
            return (a if abs(fa) < abs(fb) else b).replace(microsecond=0)

        lo_ts = a.timestamp()
        hi_ts = b.timestamp()
        for _ in range(40):
            mid_ts = (lo_ts + hi_ts) / 2.0
            mid = datetime.fromtimestamp(mid_ts, tz=timezone.utc)
            fm = f(mid)
            if fm == 0:
                return mid.replace(microsecond=0)
            if (fa < 0) == (fm < 0):
                lo_ts = mid_ts
                fa = fm
            else:
                hi_ts = mid_ts
                fb = fm
        return _dt_from_ts((lo_ts + hi_ts) / 2.0)

    def compute_greatest_elongations(
        self,
        start_dt: datetime,
        end_dt: datetime,
        sample_step: timedelta = timedelta(hours=6),
        refine_half_window: timedelta = timedelta(days=2),
    ) -> list[VenusEvent]:
        """Find local maxima of elongation and classify east/west."""
        start_dt = _to_utc(start_dt)
        end_dt = _to_utc(end_dt)

        samples: list[tuple[datetime, float]] = []
        t = start_dt
        while t <= end_dt:
            samples.append((t, self.get_state(t).elongation_deg))
            t += sample_step

        events: list[VenusEvent] = []
        for i in range(1, len(samples) - 1):
            t0, e0 = samples[i - 1]
            t1, e1 = samples[i]
            t2, e2 = samples[i + 1]
            if e1 > e0 and e1 > e2:
                # refine maximum near t1
                lo = max(start_dt, t1 - refine_half_window)
                hi = min(end_dt, t1 + refine_half_window)
                t_max = self._maximize_elongation(lo, hi)
                s = self.get_state(t_max)

                # East vs West: sign of (Venus_lon - Sun_lon) in [-180,180]
                delta = _wrap180(s.geo_lon_venus_deg - s.geo_lon_sun_deg)
                kind: EventKind = "greatest_elongation_east" if delta > 0 else "greatest_elongation_west"
                events.append(VenusEvent(t_max, kind, s.elongation_deg, s.illumination_fraction))

        # Deduplicate near-duplicates (coarse sampling can detect same peak multiple times)
        events.sort(key=lambda e: e.dt_utc)
        deduped: list[VenusEvent] = []
        for evt in events:
            if not deduped:
                deduped.append(evt)
                continue
            if abs((evt.dt_utc - deduped[-1].dt_utc).total_seconds()) < 36 * 3600:
                # keep the stronger elongation
                if evt.elongation_deg > deduped[-1].elongation_deg:
                    deduped[-1] = evt
            else:
                deduped.append(evt)

        return deduped

    def compute_conjunctions(
        self,
        start_dt: datetime,
        end_dt: datetime,
        sample_step: timedelta = timedelta(hours=6),
        refine_half_window: timedelta = timedelta(days=2),
    ) -> list[VenusEvent]:
        """Find local minima of elongation and classify inferior vs superior.

        Classification heuristic:
        - inferior conjunction ≈ illumination near 0 (new)
        - superior conjunction ≈ illumination near 1 (full)
        """
        start_dt = _to_utc(start_dt)
        end_dt = _to_utc(end_dt)

        samples: list[tuple[datetime, float]] = []
        t = start_dt
        while t <= end_dt:
            samples.append((t, self.get_state(t).elongation_deg))
            t += sample_step

        events: list[VenusEvent] = []
        for i in range(1, len(samples) - 1):
            t0, e0 = samples[i - 1]
            t1, e1 = samples[i]
            t2, e2 = samples[i + 1]
            if e1 < e0 and e1 < e2:
                lo = max(start_dt, t1 - refine_half_window)
                hi = min(end_dt, t1 + refine_half_window)
                t_min = self._minimize_elongation(lo, hi)
                s = self.get_state(t_min)

                kind: EventKind = "inferior_conjunction" if s.illumination_fraction < 0.5 else "superior_conjunction"
                events.append(VenusEvent(t_min, kind, s.elongation_deg, s.illumination_fraction))

        events.sort(key=lambda e: e.dt_utc)
        deduped: list[VenusEvent] = []
        for evt in events:
            if not deduped:
                deduped.append(evt)
                continue
            if abs((evt.dt_utc - deduped[-1].dt_utc).total_seconds()) < 48 * 3600:
                # keep the deeper minimum
                if evt.elongation_deg < deduped[-1].elongation_deg:
                    deduped[-1] = evt
            else:
                deduped.append(evt)

        return deduped

    def _minimize_elongation(self, lo: datetime, hi: datetime) -> datetime:
        """Golden-section search to minimize elongation over [lo,hi]."""
        lo = _to_utc(lo)
        hi = _to_utc(hi)

        def g(t: datetime) -> float:
            return self.get_state(t).elongation_deg

        phi = (1 + 5 ** 0.5) / 2
        invphi = 1 / phi

        a_ts = lo.timestamp()
        b_ts = hi.timestamp()

        c_ts = b_ts - (b_ts - a_ts) * invphi
        d_ts = a_ts + (b_ts - a_ts) * invphi

        c = datetime.fromtimestamp(c_ts, tz=timezone.utc)
        d = datetime.fromtimestamp(d_ts, tz=timezone.utc)
        fc = g(c)
        fd = g(d)

        for _ in range(45):
            if fc > fd:
                a_ts = c_ts
                c_ts = d_ts
                fc = fd
                d_ts = a_ts + (b_ts - a_ts) * invphi
                d = datetime.fromtimestamp(d_ts, tz=timezone.utc)
                fd = g(d)
            else:
                b_ts = d_ts
                d_ts = c_ts
                fd = fc
                c_ts = b_ts - (b_ts - a_ts) * invphi
                c = datetime.fromtimestamp(c_ts, tz=timezone.utc)
                fc = g(c)

        best_ts = c_ts if fc < fd else d_ts
        return datetime.fromtimestamp(best_ts, tz=timezone.utc).replace(microsecond=0)

    def _maximize_elongation(self, lo: datetime, hi: datetime) -> datetime:
        """Golden-section search to maximize elongation over [lo,hi]."""
        lo = _to_utc(lo)
        hi = _to_utc(hi)

        def g(t: datetime) -> float:
            return self.get_state(t).elongation_deg

        phi = (1 + 5 ** 0.5) / 2
        invphi = 1 / phi

        a_ts = lo.timestamp()
        b_ts = hi.timestamp()

        c_ts = b_ts - (b_ts - a_ts) * invphi
        d_ts = a_ts + (b_ts - a_ts) * invphi

        c = datetime.fromtimestamp(c_ts, tz=timezone.utc)
        d = datetime.fromtimestamp(d_ts, tz=timezone.utc)
        fc = g(c)
        fd = g(d)

        for _ in range(45):
            if fc < fd:
                a_ts = c_ts
                c_ts = d_ts
                fc = fd
                d_ts = a_ts + (b_ts - a_ts) * invphi
                d = datetime.fromtimestamp(d_ts, tz=timezone.utc)
                fd = g(d)
            else:
                b_ts = d_ts
                d_ts = c_ts
                fd = fc
                c_ts = b_ts - (b_ts - a_ts) * invphi
                c = datetime.fromtimestamp(c_ts, tz=timezone.utc)
                fc = g(c)

        best_ts = c_ts if fc > fd else d_ts
        return datetime.fromtimestamp(best_ts, tz=timezone.utc).replace(microsecond=0)
