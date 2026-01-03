"""Analyze Venus greatest elongation cycles and map them to Tzolkin.

This script focuses on ONE phenomenon: greatest elongation.
You can choose:
- east-only (one per synodic cycle)
- west-only
- both (east+west)

It computes:
- event list (UTC timestamps, elongation, illumination)
- Tzolkin mapping for the UTC date of the event
- interval statistics (days between events)
- modular deltas (Kin mod 260, Sign mod 20, Tone mod 13, Row-color group mod 4)
- an N-step recurrence check (default: 5 steps for east-only ≈ 8-year resonance)

Usage
-----
  .venv/bin/python scripts/analyze_venus_elongation_cycles.py --start 2000-01-01 --end 2050-01-01 --which east --csv Docs/time_mechanics/venus_elong_east_2000_2050.csv --md Docs/time_mechanics/VENUS_ELONG_EAST_2000_2050.md

Notes
-----
- Requires ephemeris to be loaded (waits for EphemerisProvider).
- No UI; safe to run headless.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Iterable, Literal

# Ensure `src/` import root
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from shared.services.ephemeris_provider import EphemerisProvider
from shared.services.venus_phenomena_service import VenusPhenomenaService, VenusEvent
from pillars.time_mechanics.services.tzolkin_service import TzolkinService


Which = Literal["east", "west", "both"]


@dataclass(frozen=True)
class Row:
    idx: int
    dt_utc: datetime
    kind: str
    elongation_deg: float
    illumination_fraction: float
    utc_date: date
    kin: int
    tone: int
    sign: int
    row_color_group: int


def _parse_ymd(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def _to_dt_noon_utc(d: date) -> datetime:
    # Use noon UTC as a stable sampling anchor for the range.
    return datetime(d.year, d.month, d.day, 12, 0, tzinfo=timezone.utc)


def _wait_for_ephemeris(timeout_s: float = 60.0, poll_s: float = 0.25) -> None:
    provider = EphemerisProvider.get_instance()
    deadline = time.monotonic() + timeout_s
    while not provider.is_loaded():
        if time.monotonic() > deadline:
            raise RuntimeError("Ephemeris not loaded (timeout)")
        time.sleep(poll_s)


def _filter_events(events: Iterable[VenusEvent], which: Which) -> list[VenusEvent]:
    if which == "both":
        return list(events)
    want = "greatest_elongation_east" if which == "east" else "greatest_elongation_west"
    return [e for e in events if e.kind == want]


def _mod_delta(a: int, b: int, m: int) -> int:
    return (b - a) % m


def _interval_days(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds() / 86400.0


def _summ_stats(vals: list[float]) -> dict[str, float]:
    if not vals:
        return {"count": 0.0, "mean": float("nan"), "std": float("nan"), "min": float("nan"), "max": float("nan")}
    return {
        "count": float(len(vals)),
        "mean": float(mean(vals)),
        "std": float(pstdev(vals)) if len(vals) > 1 else 0.0,
        "min": float(min(vals)),
        "max": float(max(vals)),
    }


def _render_md(
    *,
    which: Which,
    start_d: date,
    end_d: date,
    sample_hours: float,
    step_n: int,
    rows: list[Row],
    consec_days: list[float],
    step_days: list[float],
    kin_deltas: list[int],
    sign_deltas: list[int],
    tone_deltas: list[int],
    group_deltas: list[int],
) -> str:
    lines: list[str] = []
    lines.append("# Venus Greatest Elongation Cycle Analysis")
    lines.append("")
    lines.append("One phenomenon: **greatest elongation**.")
    lines.append("")
    lines.append("## Settings")
    lines.append("")
    lines.append(f"- Which: `{which}`")
    lines.append(f"- Range: `{start_d.isoformat()}` … `{end_d.isoformat()}`")
    lines.append(f"- Sampling step: `{sample_hours}h` (coarse-to-fine refinement in service)")
    lines.append(f"- N-step recurrence: `{step_n}`")
    lines.append("")

    lines.append("## Counts")
    lines.append("")
    lines.append(f"- Events: `{len(rows)}`")
    lines.append("")

    s_consec = _summ_stats(consec_days)
    s_step = _summ_stats(step_days)

    lines.append("## Interval stats")
    lines.append("")
    lines.append(f"- Consecutive Δdays: mean `{s_consec['mean']:.3f}`, std `{s_consec['std']:.3f}`, min `{s_consec['min']:.3f}`, max `{s_consec['max']:.3f}`")
    lines.append(f"- {step_n}-step Δdays: mean `{s_step['mean']:.3f}`, std `{s_step['std']:.3f}`, min `{s_step['min']:.3f}`, max `{s_step['max']:.3f}`")
    lines.append("")

    lines.append("## Modular deltas (N-step)")
    lines.append("")
    if kin_deltas:
        lines.append(f"- Kin Δ mod 260: most common = `{_mode(kin_deltas)}`")
    if sign_deltas:
        lines.append(f"- Sign Δ mod 20: most common = `{_mode(sign_deltas)}`")
    if tone_deltas:
        lines.append(f"- Tone Δ mod 13: most common = `{_mode(tone_deltas)}`")
    if group_deltas:
        lines.append(f"- Row-color group Δ mod 4: most common = `{_mode(group_deltas)}`")
    lines.append("")

    lines.append("## Sample events")
    lines.append("")
    lines.append("| idx | dt_utc | kind | elong° | illum | UTC date | Kin | Tone | Sign | group |")
    lines.append("|---:|---|---|---:|---:|---|---:|---:|---:|---:|")
    for r in rows[:12]:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(r.idx),
                    r.dt_utc.isoformat(),
                    r.kind,
                    f"{r.elongation_deg:.3f}",
                    f"{r.illumination_fraction:.4f}",
                    r.utc_date.isoformat(),
                    str(r.kin),
                    str(r.tone),
                    str(r.sign),
                    str(r.row_color_group),
                ]
            )
            + " |"
        )

    lines.append("")
    return "\n".join(lines)


def _mode(vals: list[int]) -> str:
    # small manual mode (deterministic: pick smallest among ties)
    counts: dict[int, int] = {}
    for v in vals:
        counts[v] = counts.get(v, 0) + 1
    best = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    return f"{best[0]} (count={best[1]})"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze Venus greatest elongation cycles mapped to Tzolkin")
    p.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    p.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    p.add_argument("--which", choices=["east", "west", "both"], default="east", help="Which elongations")
    p.add_argument("--sample-hours", type=float, default=6.0, help="Coarse sampling step in hours")
    p.add_argument("--step-n", type=int, default=5, help="N-step recurrence check (east-only: 5 ≈ 8-year resonance)")
    p.add_argument("--csv", help="Optional CSV output path")
    p.add_argument("--md", help="Optional markdown summary output path")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)

    start_d = _parse_ymd(args.start)
    end_d = _parse_ymd(args.end)
    if end_d < start_d:
        start_d, end_d = end_d, start_d

    which: Which = args.which
    sample_hours = float(args.sample_hours)
    sample_step = timedelta(hours=sample_hours)
    step_n = int(args.step_n)

    _wait_for_ephemeris()

    tz = TzolkinService()
    venus = VenusPhenomenaService(cache_minutes=30)

    start_dt = _to_dt_noon_utc(start_d)
    end_dt = _to_dt_noon_utc(end_d)

    events = venus.compute_greatest_elongations(start_dt, end_dt, sample_step=sample_step)
    events = _filter_events(events, which)
    events.sort(key=lambda e: e.dt_utc)

    rows: list[Row] = []
    for i, e in enumerate(events):
        d = e.dt_utc.astimezone(timezone.utc).date()
        tz_d = tz.from_gregorian(d)
        rows.append(
            Row(
                idx=i,
                dt_utc=e.dt_utc,
                kind=str(e.kind),
                elongation_deg=float(e.elongation_deg),
                illumination_fraction=float(e.illumination_fraction),
                utc_date=d,
                kin=int(tz_d.kin),
                tone=int(tz_d.tone),
                sign=int(tz_d.sign),
                row_color_group=(int(tz_d.sign) - 1) % 4,
            )
        )

    # Consecutive intervals
    consec_days: list[float] = []
    for a, b in zip(rows, rows[1:]):
        consec_days.append(_interval_days(a.dt_utc, b.dt_utc))

    # N-step recurrence intervals + modular deltas
    step_days: list[float] = []
    kin_deltas: list[int] = []
    sign_deltas: list[int] = []
    tone_deltas: list[int] = []
    group_deltas: list[int] = []

    for i in range(0, len(rows) - step_n):
        a = rows[i]
        b = rows[i + step_n]
        step_days.append(_interval_days(a.dt_utc, b.dt_utc))
        kin_deltas.append(_mod_delta(a.kin, b.kin, 260))
        sign_deltas.append(_mod_delta(a.sign, b.sign, 20))
        tone_deltas.append(_mod_delta(a.tone, b.tone, 13))
        group_deltas.append(_mod_delta(a.row_color_group, b.row_color_group, 4))

    # Optional CSV output
    if args.csv:
        out_path = Path(args.csv)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "idx",
                    "dt_utc",
                    "kind",
                    "elongation_deg",
                    "illumination_fraction",
                    "utc_date",
                    "kin",
                    "tone",
                    "sign",
                    "row_color_group",
                ]
            )
            for r in rows:
                w.writerow(
                    [
                        r.idx,
                        r.dt_utc.isoformat(),
                        r.kind,
                        f"{r.elongation_deg:.6f}",
                        f"{r.illumination_fraction:.6f}",
                        r.utc_date.isoformat(),
                        r.kin,
                        r.tone,
                        r.sign,
                        r.row_color_group,
                    ]
                )

    # Optional markdown summary
    if args.md:
        md_path = Path(args.md)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_text = _render_md(
            which=which,
            start_d=start_d,
            end_d=end_d,
            sample_hours=sample_hours,
            step_n=step_n,
            rows=rows,
            consec_days=consec_days,
            step_days=step_days,
            kin_deltas=kin_deltas,
            sign_deltas=sign_deltas,
            tone_deltas=tone_deltas,
            group_deltas=group_deltas,
        )
        md_path.write_text(md_text, encoding="utf-8")

    # Console summary
    s_consec = _summ_stats(consec_days)
    s_step = _summ_stats(step_days)

    print(f"events={len(rows)} which={which} range={start_d.isoformat()}..{end_d.isoformat()}")
    if consec_days:
        print(
            "consecutive_days: "
            + f"mean={s_consec['mean']:.3f} std={s_consec['std']:.3f} min={s_consec['min']:.3f} max={s_consec['max']:.3f}"
        )
    if step_days:
        print(
            f"step{step_n}_days: "
            + f"mean={s_step['mean']:.3f} std={s_step['std']:.3f} min={s_step['min']:.3f} max={s_step['max']:.3f}"
        )

    if kin_deltas:
        print(f"step{step_n} kin Δ mod260: {_mode(kin_deltas)}")
    if sign_deltas:
        print(f"step{step_n} sign Δ mod20: {_mode(sign_deltas)}")
    if tone_deltas:
        print(f"step{step_n} tone Δ mod13: {_mode(tone_deltas)}")
    if group_deltas:
        print(f"step{step_n} group Δ mod4: {_mode(group_deltas)}")

    if args.csv:
        print(f"wrote csv: {args.csv}")
    if args.md:
        print(f"wrote md: {args.md}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
