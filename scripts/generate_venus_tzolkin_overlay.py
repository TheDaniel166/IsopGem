"""Generate Venus phenomena events and map them onto the 260-day Tzolkin calendar.

This is a bridge script (no UI). It produces a CSV-like table printed to stdout.

Outputs:
- Greatest elongations (east/west)
- Visibility ("occulted") windows based on elongation threshold

You can redirect output to a file and later import into the Time Mechanics pillar.

Usage:
  /home/burkettdaniel927/projects/isopgem/.venv/bin/python scripts/generate_venus_tzolkin_overlay.py --days 260
  /home/burkettdaniel927/projects/isopgem/.venv/bin/python scripts/generate_venus_tzolkin_overlay.py --start 2026-01-01 --end 2026-09-18
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# Ensure `src/` import root
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from shared.services.venus_phenomena_service import VenusPhenomenaService
from shared.services.ephemeris_provider import EphemerisProvider
from pillars.time_mechanics.services.tzolkin_service import TzolkinService


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Venus phenomena mapped to Tzolkin")
    p.add_argument("--start", help="Start date (YYYY-MM-DD)")
    p.add_argument("--end", help="End date (YYYY-MM-DD)")
    p.add_argument("--days", type=int, default=260, help="If start not provided, range is [today, today+days]")
    p.add_argument("--occult-threshold", type=float, default=10.0, help="Elongation degrees below which Venus is 'occulted'")
    return p.parse_args(argv)


def _to_dt(d: date) -> datetime:
    return datetime(d.year, d.month, d.day, 12, 0, tzinfo=timezone.utc)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)

    if args.start:
        start_d = datetime.strptime(args.start, "%Y-%m-%d").date()
    else:
        start_d = date.today()

    if args.end:
        end_d = datetime.strptime(args.end, "%Y-%m-%d").date()
    else:
        end_d = start_d + timedelta(days=int(args.days))

    start_dt = _to_dt(start_d)
    end_dt = _to_dt(end_d)

    tz = TzolkinService()
    venus = VenusPhenomenaService(cache_minutes=30)

    provider = EphemerisProvider.get_instance()
    while not provider.is_loaded():
        time.sleep(0.25)

    events = venus.compute_greatest_elongations(start_dt, end_dt)
    events += venus.compute_conjunctions(start_dt, end_dt)
    events.sort(key=lambda e: e.dt_utc)
    windows = venus.compute_visibility_windows(start_dt, end_dt, threshold_deg=float(args.occult_threshold))

    print(",".join(
        [
            "dt_utc",
            "event",
            "elongation_deg",
            "illum_frac",
            "tzolkin_kin",
            "tzolkin_tone",
            "tzolkin_sign",
            "tzolkin_sign_name",
        ]
    ))

    for evt in events:
        d = evt.dt_utc.date()
        tz_date = tz.from_gregorian(d)
        print(",".join(
            [
                evt.dt_utc.isoformat(),
                evt.kind,
                f"{evt.elongation_deg:.3f}",
                f"{evt.illumination_fraction:.4f}",
                str(tz_date.kin),
                str(tz_date.tone),
                str(tz_date.sign),
                tz_date.sign_name,
            ]
        ))

    for start_w, end_w in windows:
        for kind, dtw in (("invisible_start", start_w), ("invisible_end", end_w)):
            d = dtw.date()
            tz_date = tz.from_gregorian(d)
            s = venus.get_state(dtw)
            print(",".join(
                [
                    dtw.isoformat(),
                    kind,
                    f"{s.elongation_deg:.3f}",
                    f"{s.illumination_fraction:.4f}",
                    str(tz_date.kin),
                    str(tz_date.tone),
                    str(tz_date.sign),
                    tz_date.sign_name,
                ]
            ))

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
