"""Precompute Venus/Earth heliocentric positions into a local SQLite cache.

Default span: 200 years past + 200 years forward from now (UTC).
Default cadence: 30 minutes.

This is intentionally a standalone script (no PyQt), safe to run headless.

Usage examples:
  /home/burkettdaniel927/projects/isopgem/.venv/bin/python scripts/precompute_venus_positions.py
  /home/burkettdaniel927/projects/isopgem/.venv/bin/python scripts/precompute_venus_positions.py --cadence-minutes 30
  /home/burkettdaniel927/projects/isopgem/.venv/bin/python scripts/precompute_venus_positions.py --years-past 200 --years-future 200

Notes:
- The resulting DB can be large. With 400 years at 30-minute cadence, expect ~7.0M rows per body.
  Since we store BOTH Earth and Venus, that is ~14.0M rows.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Ensure `src/` is importable when running from repo root.
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from shared.services.ephemeris_provider import EphemerisProvider

from pillars.astrology.services.venus_position_store import (
    DEFAULT_CADENCE_MINUTES,
    DEFAULT_DB_PATH,
    HeliocentricPosition,
    VenusPositionStore,
    add_years,
    iter_time_range,
)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Precompute Venus/Earth heliocentric positions into SQLite")
    p.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="SQLite DB path (default: data/venus_positions.db)")
    p.add_argument("--cadence-minutes", type=int, default=DEFAULT_CADENCE_MINUTES)
    p.add_argument("--years-past", type=int, default=200)
    p.add_argument("--years-future", type=int, default=200)
    p.add_argument(
        "--resume",
        action="store_true",
        help="Resume from the last fully-written timestamp in the DB (both earth+venus).",
    )
    p.add_argument("--progress-every", type=int, default=5000, help="Print progress every N timestamps")
    p.add_argument(
        "--commit-every",
        type=int,
        default=2000,
        help="Commit batch size (timestamps). Each timestamp writes 2 rows (earth+venus).",
    )
    return p.parse_args(argv)


def _find_last_complete_timestamp(conn, dt_format: str = "%Y-%m-%d %H:%M:%S") -> datetime | None:
    """Return the latest dt_utc that has BOTH bodies present (earth+venus)."""
    row = conn.execute(
        """
        SELECT dt_utc
        FROM heliocentric_positions
        GROUP BY dt_utc
        HAVING
            SUM(CASE WHEN body = 'earth' THEN 1 ELSE 0 END) = 1
            AND SUM(CASE WHEN body = 'venus' THEN 1 ELSE 0 END) = 1
        ORDER BY dt_utc DESC
        LIMIT 1
        """
    ).fetchone()
    if row is None:
        return None
    return datetime.strptime(row[0], dt_format).replace(tzinfo=timezone.utc)


def _get_helio_lat_lon_dist(provider: EphemerisProvider, body_name: str, dt: datetime) -> tuple[float, float, float]:
    """Return (lat_deg, lon_deg, dist_au) for heliocentric observation."""
    if not provider.is_loaded():
        raise RuntimeError("EphemerisProvider not loaded yet")

    return provider.get_heliocentric_ecliptic_latlon_distance(body_name, dt)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)

    db_path = Path(args.db_path)
    cadence_minutes = int(args.cadence_minutes)

    now = datetime.now(timezone.utc)
    start_dt = add_years(now, -int(args.years_past)).replace(minute=0, second=0, microsecond=0)
    end_dt = add_years(now, int(args.years_future)).replace(minute=0, second=0, microsecond=0)

    store = VenusPositionStore(db_path)

    provider = EphemerisProvider.get_instance()
    print("Waiting for ephemeris load...")
    while not provider.is_loaded():
        time.sleep(0.25)

    with store.connect() as conn:
        store.ensure_schema(conn)

        # Speed pragmas for bulk load
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = OFF")
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA cache_size = -200000")  # ~200MB cache

        if args.resume:
            last_complete = _find_last_complete_timestamp(conn)
            if last_complete is not None:
                from datetime import timedelta
                resume_from = last_complete + timedelta(minutes=cadence_minutes)
                if resume_from > start_dt:
                    print(f"Resuming from {resume_from.isoformat()} (last complete {last_complete.isoformat()})")
                    start_dt = resume_from
            else:
                print("--resume requested, but DB has no complete timestamps; starting from range start.")

        if start_dt > end_dt:
            print("Nothing to do: start_dt is after end_dt.")
            return 0

        total_steps = int(((end_dt - start_dt).total_seconds() // 60) // cadence_minutes) + 1
        print(
            f"Range: {start_dt.isoformat()} -> {end_dt.isoformat()} | cadence={cadence_minutes}m | timestamps={total_steps:,} | rows={total_steps*2:,}")

        total = 0
        t0 = time.perf_counter()

        for idx, dt in enumerate(iter_time_range(start_dt, end_dt, cadence_minutes=cadence_minutes), start=1):
            # Earth
            e_lat, e_lon, e_dist = _get_helio_lat_lon_dist(provider, "earth", dt)
            store.upsert_heliocentric_position(
                conn,
                HeliocentricPosition(dt_utc=dt, body="earth", lon_deg=e_lon, lat_deg=e_lat, distance_au=e_dist),
            )

            # Venus
            v_lat, v_lon, v_dist = _get_helio_lat_lon_dist(provider, "venus", dt)
            store.upsert_heliocentric_position(
                conn,
                HeliocentricPosition(dt_utc=dt, body="venus", lon_deg=v_lon, lat_deg=v_lat, distance_au=v_dist),
            )

            total += 1

            if total % int(args.commit_every) == 0:
                conn.commit()

            if total % int(args.progress_every) == 0:
                elapsed = time.perf_counter() - t0
                rate = total / elapsed if elapsed > 0 else 0.0
                pct = (total / total_steps) * 100.0 if total_steps else 100.0
                remaining = (total_steps - total)
                eta_s = (remaining / rate) if rate > 0 else 0.0
                eta_m = eta_s / 60.0
                print(
                    f"{dt.isoformat()} | {pct:5.1f}% | timestamps={total:,}/{total_steps:,} | rows={total*2:,} | {rate:,.1f} ts/s | ETA={eta_m:,.1f}m | db={db_path}")

        conn.commit()

    print(f"Done. Wrote {total*2:,} rows into {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
