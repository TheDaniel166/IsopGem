# Realignment discovery

This is a working note to rediscover an older “calendar realignment” rule (suspected 16‑year cycle with subcycles) starting from the current Tzolkin epoch.

## Canonical anchor (current implementation)

- Epoch: `2020-01-12` = **Kin 1**, Cycle 1
- Current mapping: advance the Tzolkin count on every Gregorian day (leap days included).

Note on leap years:
- Gregorian leap years are “every 4 years”, except century years are only leap years if divisible by 400.
- This matters for long-range periodicity checks: some 16-year intervals can contain **3** leap days instead of **4** when they end on a non-leap century (e.g., 2100), which can break the otherwise clean 4×4 → 16-year color-phase repetition for anchors after Feb 29.

## Tooling

Run the exploration script:

- Generate a year-series CSV (printed to stdout) and a markdown report:
  - `.venv/bin/python scripts/explore_tzolkin_realignment.py --anchor 01-12 --start-year 2020 --years 80 --report Docs/time_mechanics/REALIGNMENT_DISCOVERY.generated.md`

The script compares multiple counting modes:

- `gregorian` (current behavior)
- `leap_intercalary` (Feb 29 exists but does not advance the Tzolkin index)
- `leap_double` (Feb 29 advances twice total)

## What to look for

The output includes “key jumps” for +4/+8/+16 years (same MM‑DD). Use these to spot:

- **Which feature ‘realigns’**: full Kin, Sign (row), Tone (column), or just the row‑color group (`(sign-1) % 4`).
- Whether the subcycle is 4/8/16 years or something else.

Once we identify the exact behavior that matches your old rule, we can implement it as an optional calendar mode in the service layer (without mixing UI + logic).
