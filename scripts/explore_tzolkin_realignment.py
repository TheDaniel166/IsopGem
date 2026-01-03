"""Explore calendar realignment hypotheses for the Tzolkin mapping.

Goal
----
When you suspect an N-year "realignment" (e.g., 16 years) with possible subcycles
(4/8 years), the quickest way to rediscover the rule is to compare how the
Tzolkin index advances under different day-counting policies.

This script compares:
- gregorian: advance on every Gregorian day (current app behavior)
- leap_intercalary: Feb 29 exists but does NOT advance the Tzolkin index
- leap_double: Feb 29 advances the index an extra step (advances twice total)

It prints a compact table for a chosen anchor month/day across years, plus a
summary of the 4/8/16-year deltas.

Usage
-----
  .venv/bin/python scripts/explore_tzolkin_realignment.py --years 40
  .venv/bin/python scripts/explore_tzolkin_realignment.py --anchor 01-12 --years 80 --report Docs/time_mechanics/REALIGNMENT_DISCOVERY.md

Notes
-----
- "Include the leap day" is satisfied for leap_intercalary: Feb 29 exists as a
  date, but it's treated as an intercalary day (index does not advance).
- This script is non-UI and does not modify app behavior.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Literal

# Ensure `src/` import root
REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pillars.time_mechanics.services.tzolkin_service import TzolkinService


Mode = Literal["gregorian", "leap_intercalary", "leap_double"]


@dataclass(frozen=True)
class MappingResult:
    mode: Mode
    target_date: date
    epoch: date
    delta_days: int
    effective_delta: int
    kin: int
    tone: int
    sign: int
    sign_row_color_group: int  # matches UI ring coloring: row % 4


def _parse_ymd(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def _parse_mmdd(s: str) -> tuple[int, int]:
    mm, dd = s.split("-")
    return int(mm), int(dd)


def _is_leap_year(y: int) -> bool:
    return (y % 4 == 0) and (y % 100 != 0 or y % 400 == 0)


def _count_leap_days_between_exclusive(start: date, end: date) -> int:
    """Count Feb 29 dates with start < feb29 <= end."""
    if end <= start:
        start, end = end, start

    count = 0
    for y in range(start.year, end.year + 1):
        if not _is_leap_year(y):
            continue
        d = date(y, 2, 29)
        if start < d <= end:
            count += 1
    return count


def _effective_delta(epoch: date, target: date, mode: Mode) -> tuple[int, int]:
    """Return (delta_days, effective_delta_days) under a counting mode."""
    delta = (target - epoch).days

    if mode == "gregorian":
        return delta, delta

    leap_days = _count_leap_days_between_exclusive(epoch, target)

    if mode == "leap_intercalary":
        # Feb 29 exists in civil time, but is intercalary for the Tzolkin count.
        # Each leap day removes one advancement.
        return delta, delta - leap_days

    if mode == "leap_double":
        # Feb 29 advances twice total: an extra advancement per leap day.
        return delta, delta + leap_days

    raise ValueError(f"Unknown mode: {mode}")


def map_date(epoch: date, target: date, mode: Mode) -> MappingResult:
    delta, eff = _effective_delta(epoch, target, mode)
    kin_index = eff % 260

    kin = kin_index + 1
    tone = (kin_index % 13) + 1
    sign = (kin_index % 20) + 1

    # UI ring colors are currently by row (sign_idx) mod 4.
    sign_row_color_group = (sign - 1) % 4

    return MappingResult(
        mode=mode,
        target_date=target,
        epoch=epoch,
        delta_days=delta,
        effective_delta=eff,
        kin=kin,
        tone=tone,
        sign=sign,
        sign_row_color_group=sign_row_color_group,
    )


def _safe_date(y: int, mm: int, dd: int) -> date | None:
    try:
        return date(y, mm, dd)
    except ValueError:
        return None


def _summarize_jump(epoch: date, mm: int, dd: int, years: int, modes: Iterable[Mode]) -> list[str]:
    """Lines describing the mapping after a +years jump to same MM-DD."""
    d0 = _safe_date(epoch.year, mm, dd)
    d1 = _safe_date(epoch.year + years, mm, dd)
    if d0 is None or d1 is None:
        return [f"{years:>2}y: (invalid date for MM-DD {mm:02d}-{dd:02d})"]

    lines: list[str] = [f"{years:>2}y jump: {d0.isoformat()} -> {d1.isoformat()} (civil delta={(d1 - d0).days})"]
    for mode in modes:
        a = map_date(epoch, d0, mode)
        b = map_date(epoch, d1, mode)
        kin_shift = ((b.kin - a.kin) + 260) % 260
        sign_shift = ((b.sign - a.sign) + 20) % 20
        tone_shift = ((b.tone - a.tone) + 13) % 13
        lines.append(
            f"  - {mode:15} kin={b.kin:3d} (Δ{kin_shift:3d})  sign={b.sign:2d} (Δ{sign_shift:2d})  tone={b.tone:2d} (Δ{tone_shift:2d})"
        )
    return lines


def _detect_period(years: list[int], values: list[int]) -> int | None:
    """Find smallest period p where values[i]==values[i+p] for all possible i."""
    n = len(values)
    for p in range(1, min(64, n)):
        ok = True
        for i in range(0, n - p):
            if values[i] != values[i + p]:
                ok = False
                break
        if ok:
            return p
    return None


def _render_report(
    *,
    epoch: date,
    anchor_mm: int,
    anchor_dd: int,
    start_year: int,
    years: int,
    modes: list[Mode],
    series_by_mode: dict[Mode, list[MappingResult]],
) -> str:
    lines: list[str] = []

    lines.append("# Tzolkin Calendar Realignment Discovery")
    lines.append("")
    lines.append("This document is generated by `scripts/explore_tzolkin_realignment.py`.")
    lines.append("")
    lines.append("## Settings")
    lines.append("")
    lines.append(f"- Epoch: `{epoch.isoformat()}` (Kin 1 in current implementation)")
    lines.append(f"- Anchor MM-DD: `{anchor_mm:02d}-{anchor_dd:02d}`")
    lines.append(f"- Year range: `{start_year}` … `{start_year + years}`")
    lines.append(f"- Modes: `{', '.join(modes)}`")
    lines.append("")

    lines.append("## Key jumps")
    lines.append("")
    for yjump in (4, 8, 16):
        for l in _summarize_jump(epoch, anchor_mm, anchor_dd, yjump, modes):
            lines.append(l)
        lines.append("")

    lines.append("## Subcycle hints")
    lines.append("")
    lines.append("We look for repeating patterns across years on the same civil date (same MM-DD):")
    lines.append("- `sign_row_color_group` matches the Tzolkin UI row ring coloring (`(sign-1) % 4`).")
    lines.append("- If a mode yields short periods for sign/group/tone, it’s a candidate for your remembered ‘subcycles’. ")
    lines.append("")

    for mode in modes:
        series = series_by_mode[mode]
        yrs = [r.target_date.year for r in series]
        kin_vals = [r.kin for r in series]
        sign_vals = [r.sign for r in series]
        tone_vals = [r.tone for r in series]
        group_vals = [r.sign_row_color_group for r in series]

        p_kin = _detect_period(yrs, kin_vals)
        p_sign = _detect_period(yrs, sign_vals)
        p_tone = _detect_period(yrs, tone_vals)
        p_group = _detect_period(yrs, group_vals)

        lines.append(f"### Mode: `{mode}`")
        lines.append("")
        lines.append(f"- Period(kin): `{p_kin}` years" if p_kin else "- Period(kin): (no short period detected)")
        lines.append(f"- Period(sign): `{p_sign}` years" if p_sign else "- Period(sign): (no short period detected)")
        lines.append(f"- Period(tone): `{p_tone}` years" if p_tone else "- Period(tone): (no short period detected)")
        lines.append(f"- Period(row-color group): `{p_group}` years" if p_group else "- Period(row-color group): (no short period detected)")
        lines.append("")

    lines.append("## How to use this")
    lines.append("")
    lines.append("1) Run the script and inspect the 4/8/16-year jump deltas.")
    lines.append("2) If one mode keeps the feature you care about stable (e.g., sign row / color group), that’s your likely rule.")
    lines.append("3) If needed, we can implement that policy as an optional calendar mode in `TzolkinService` (without touching UI logic).")
    lines.append("")

    return "\n".join(lines)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Explore Tzolkin calendar realignment hypotheses")
    p.add_argument("--epoch", default="2020-01-12", help="Epoch date (YYYY-MM-DD), default matches current app")
    p.add_argument("--anchor", default="01-12", help="Anchor month-day to compare across years (MM-DD)")
    p.add_argument("--start-year", type=int, default=2020, help="Start year for the anchor series")
    p.add_argument("--years", type=int, default=40, help="How many years forward to include")
    p.add_argument(
        "--modes",
        default="gregorian,leap_intercalary,leap_double",
        help="Comma-separated modes: gregorian, leap_intercalary, leap_double",
    )
    p.add_argument("--report", help="Optional path to write a markdown report")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)

    epoch = _parse_ymd(args.epoch)
    anchor_mm, anchor_dd = _parse_mmdd(args.anchor)
    start_year = int(args.start_year)
    years = int(args.years)

    modes: list[Mode] = [m.strip() for m in str(args.modes).split(",") if m.strip()]  # type: ignore[assignment]

    # Basic sanity: verify current service agrees with gregorian mode at epoch.
    # (Non-fatal: just an informative print.)
    try:
        svc = TzolkinService()
        tz_epoch = svc.from_gregorian(epoch)
        greg_epoch = map_date(epoch, epoch, "gregorian")
        if tz_epoch.kin != greg_epoch.kin:
            print(f"[WARN] Service epoch kin={tz_epoch.kin} differs from computed={greg_epoch.kin}")
    except Exception as e:
        print(f"[WARN] Could not instantiate TzolkinService for sanity check: {e}")

    # Build the year series for the anchor MM-DD.
    series_by_mode: dict[Mode, list[MappingResult]] = {m: [] for m in modes}

    anchor_dates: list[date] = []
    for y in range(start_year, start_year + years + 1):
        d = _safe_date(y, anchor_mm, anchor_dd)
        if d is not None:
            anchor_dates.append(d)

    print(",".join(
        [
            "year",
            "date",
            "mode",
            "delta_days",
            "effective_delta",
            "kin",
            "tone",
            "sign",
            "sign_row_color_group",
        ]
    ))

    for d in anchor_dates:
        for mode in modes:
            r = map_date(epoch, d, mode)
            series_by_mode[mode].append(r)
            print(",".join(
                [
                    str(d.year),
                    d.isoformat(),
                    mode,
                    str(r.delta_days),
                    str(r.effective_delta),
                    str(r.kin),
                    str(r.tone),
                    str(r.sign),
                    str(r.sign_row_color_group),
                ]
            ))

    print("\n# Key jumps (same MM-DD)")
    for yjump in (4, 8, 16):
        for l in _summarize_jump(epoch, anchor_mm, anchor_dd, yjump, modes):
            print(l)

    # Period hints
    print("\n# Subcycle period hints (years)")
    for mode in modes:
        series = series_by_mode[mode]
        if not series:
            continue

        yrs = [r.target_date.year for r in series]
        kin_vals = [r.kin for r in series]
        sign_vals = [r.sign for r in series]
        tone_vals = [r.tone for r in series]
        group_vals = [r.sign_row_color_group for r in series]

        p_kin = _detect_period(yrs, kin_vals)
        p_sign = _detect_period(yrs, sign_vals)
        p_tone = _detect_period(yrs, tone_vals)
        p_group = _detect_period(yrs, group_vals)

        print(f"{mode}:")
        print(f"  period(kin)   = {p_kin}" if p_kin else "  period(kin)   = (none <=64y)")
        print(f"  period(sign)  = {p_sign}" if p_sign else "  period(sign)  = (none <=64y)")
        print(f"  period(tone)  = {p_tone}" if p_tone else "  period(tone)  = (none <=64y)")
        print(f"  period(group) = {p_group}" if p_group else "  period(group) = (none <=64y)")

    if args.report:
        report_path = Path(args.report)
        report_text = _render_report(
            epoch=epoch,
            anchor_mm=anchor_mm,
            anchor_dd=anchor_dd,
            start_year=start_year,
            years=years,
            modes=modes,
            series_by_mode=series_by_mode,
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_text, encoding="utf-8")
        print(f"\n[WROTE] {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
