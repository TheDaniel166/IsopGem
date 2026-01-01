# The Grimoire of Thelema

<!-- Last Verified: 2026-01-01 -->

> *"Every man and every woman is a star."*

The **Thelemic Calendar** is a fixed solar calendar that maps the 365-day year onto a perfect 360° Zodiacal Circle + 5 Intercalary Days (The Prime Ditrune Gates).

## I. The Structure of the Year

### The 364 Days
The core calendar consists of 364 days, arranged as 52 weeks of 7 days.
- **Structure**: 52 Weeks × 7 Days = 364 Days.
- **Conrune Pairs**: Each day is a pair of numbers: **Ditrune** (Day) and **Contrune** (Night).

### The Prime Ditrune Gates
The 4 Cardinal Points (Equinoxes and Solstices) are the **Prime Gates**.
- These are "Days out of Time".
- They anchor the calendar to the solar cycle.

---

## II. The Zodiacal Circle

**Location**: `src/pillars/time_mechanics/ui/zodiacal_circle_window.py`

The primary visualization of the Thelemic Calendar is the **Zodiacal Circle**.

### The Mechanism
1.  **Ditrune & Contrune**: Every day has a Day Value and Night Value.
2.  **The Difference**: `abs(Ditrune - Contrune)` determines the **Degree** on the wheel.
3.  **Visualization**:
    - **Outer Ring**: The 12 Zodiac Signs (Aries - Pisces).
    - **Inner Ring**: The Difference Values (0-360).
    - **Aspects**: Geometric lines connecting days with harmonic relationships (Trine, Square, Opposition).

### The Astronomicon Font
The interface renders Zodiac glyphs using the sacred `Astronomicon` font. Fallback is Arial if the font is missing.

---

## III. Integration

The Thelemic Calendar serves as the bridge between:
- **Gregorian Dates** (Civil Time)
- **Zodiacal Degrees** (Astrological Time)
- **Conrune Values** (Symbolic/Mathematical Time)

> *"Love is the law, love under will."*
