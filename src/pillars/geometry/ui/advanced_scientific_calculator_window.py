"""Advanced scientific calculator window for quick math operations."""
from __future__ import annotations

import ast
import math
import re
from typing import Callable, Dict, List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication, QFont
from PyQt6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QComboBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

try:
    from shared.utils.calculator_persistence import (
        DEFAULT_MAX_HISTORY,
        CalculatorState,
        get_default_state_path,
        load_state,
        save_state,
    )
except ModuleNotFoundError:
    # Tests load this module by file path; in that context `src/` is not
    # necessarily on sys.path and `shared` may not resolve. Fall back to a
    # package-qualified import used by those tests.
    from src.shared.utils.calculator_persistence import (  # type: ignore
        DEFAULT_MAX_HISTORY,
        CalculatorState,
        get_default_state_path,
        load_state,
        save_state,
    )

try:
    from shared.utils.measure_conversion import convert_between_units, parse_measure_value
except ModuleNotFoundError:
    from src.shared.utils.measure_conversion import convert_between_units, parse_measure_value  # type: ignore


MEASURE_UNITS: List[Dict[str, object]] = [
    # Length (meters)
    {"name": "Meter", "system": "Metric", "category": "length", "si_unit": "m", "to_si": 1.0},
    {"name": "Kilometer", "system": "Metric", "category": "length", "si_unit": "m", "to_si": 1000.0},
    {"name": "Centimeter", "system": "Metric", "category": "length", "si_unit": "m", "to_si": 0.01},
    {"name": "Egyptian Royal Cubit", "system": "Egyptian", "category": "length", "si_unit": "m", "to_si": 0.5235, "note": "Royal cubit (7 palms)"},
    {"name": "Egyptian Palm", "system": "Egyptian", "category": "length", "si_unit": "m", "to_si": 0.5235 / 7.0, "note": "Derived: 1 royal cubit = 7 palms"},
    {"name": "Egyptian Digit", "system": "Egyptian", "category": "length", "si_unit": "m", "to_si": 0.5235 / 28.0, "note": "Derived: 1 palm = 4 digits; 1 royal cubit = 28 digits"},
    {"name": "Egyptian Remen", "system": "Egyptian", "category": "length", "si_unit": "m", "to_si": 0.5235 * 5.0 / 7.0, "note": "Derived: 1 remen = 5 palms (royal-cubit palm)"},
    {"name": "Egyptian Common Cubit", "system": "Egyptian", "category": "length", "si_unit": "m", "to_si": 0.45},
    {"name": "Hebrew Cubit", "system": "Hebrew", "category": "length", "si_unit": "m", "to_si": 0.457},
    {"name": "Babylonian Cubit", "system": "Babylonian", "category": "length", "si_unit": "m", "to_si": 0.5},
    {"name": "Greek Foot (pous)", "system": "Greek", "category": "length", "si_unit": "m", "to_si": 0.308},
    {"name": "Greek Stadion", "system": "Greek", "category": "length", "si_unit": "m", "to_si": 185.0},
    {"name": "Greek Cubit (pechys)", "system": "Greek", "category": "length", "si_unit": "m", "to_si": 0.462},
    {"name": "Roman Foot (pes)", "system": "Roman", "category": "length", "si_unit": "m", "to_si": 0.296},
    {"name": "Roman Pace (passus)", "system": "Roman", "category": "length", "si_unit": "m", "to_si": 1.48},
    {"name": "Roman Mile (mille passus)", "system": "Roman", "category": "length", "si_unit": "m", "to_si": 1480.0},
    {"name": "Roman Actus", "system": "Roman", "category": "length", "si_unit": "m", "to_si": 35.5},
    {"name": "Persian Parasang", "system": "Persian", "category": "length", "si_unit": "m", "to_si": 5600.0},
    {"name": "Chinese Chi", "system": "Chinese", "category": "length", "si_unit": "m", "to_si": 0.333},
    {"name": "Chinese Zhang", "system": "Chinese", "category": "length", "si_unit": "m", "to_si": 3.33},
    {"name": "Chinese Li", "system": "Chinese", "category": "length", "si_unit": "m", "to_si": 500.0},
    {"name": "Indian Hasta", "system": "Indian", "category": "length", "si_unit": "m", "to_si": 0.4572},
    {"name": "Indian Yojana", "system": "Indian", "category": "length", "si_unit": "m", "to_si": 13000.0, "note": "Yojana varies; using 13 km"},

    # Mass (kilograms)
    {"name": "Kilogram", "system": "Metric", "category": "mass", "si_unit": "kg", "to_si": 1.0},
    {"name": "Gram", "system": "Metric", "category": "mass", "si_unit": "kg", "to_si": 0.001},
    {"name": "Babylonian Talent", "system": "Babylonian", "category": "mass", "si_unit": "kg", "to_si": 30.3},
    {"name": "Babylonian Mina", "system": "Babylonian", "category": "mass", "si_unit": "kg", "to_si": 0.505},
    {"name": "Babylonian Shekel", "system": "Babylonian", "category": "mass", "si_unit": "kg", "to_si": 0.0084},
    {"name": "Hebrew Talent", "system": "Hebrew", "category": "mass", "si_unit": "kg", "to_si": 34.2},
    {"name": "Hebrew Shekel", "system": "Hebrew", "category": "mass", "si_unit": "kg", "to_si": 0.0114},
    {"name": "Greek Talent", "system": "Greek", "category": "mass", "si_unit": "kg", "to_si": 26.0},
    {"name": "Greek Mina", "system": "Greek", "category": "mass", "si_unit": "kg", "to_si": 0.436},
    {"name": "Greek Drachma", "system": "Greek", "category": "mass", "si_unit": "kg", "to_si": 0.00436},
    {"name": "Roman Libra", "system": "Roman", "category": "mass", "si_unit": "kg", "to_si": 0.327},
    {"name": "Roman Uncia", "system": "Roman", "category": "mass", "si_unit": "kg", "to_si": 0.0273},
    {"name": "Egyptian Deben", "system": "Egyptian", "category": "mass", "si_unit": "kg", "to_si": 0.091},
    {"name": "Egyptian Kite (Qedet)", "system": "Egyptian", "category": "mass", "si_unit": "kg", "to_si": 0.091 / 10.0, "note": "Derived: 1 deben = 10 kites (common scholarly convention; varies by period)"},
    {"name": "Chinese Jin", "system": "Chinese", "category": "mass", "si_unit": "kg", "to_si": 0.596},
    {"name": "Chinese Liang", "system": "Chinese", "category": "mass", "si_unit": "kg", "to_si": 0.0373},

    # Volume (liters)
    {"name": "Liter", "system": "Metric", "category": "volume", "si_unit": "L", "to_si": 1.0},
    {"name": "Milliliter", "system": "Metric", "category": "volume", "si_unit": "L", "to_si": 0.001},
    {"name": "Roman Sextarius", "system": "Roman", "category": "volume", "si_unit": "L", "to_si": 0.546},
    {"name": "Roman Congius", "system": "Roman", "category": "volume", "si_unit": "L", "to_si": 3.25},
    {"name": "Roman Amphora", "system": "Roman", "category": "volume", "si_unit": "L", "to_si": 26.2},
    {"name": "Greek Kotyle", "system": "Greek", "category": "volume", "si_unit": "L", "to_si": 0.273},
    {"name": "Greek Metretes", "system": "Greek", "category": "volume", "si_unit": "L", "to_si": 39.4},
    {"name": "Hebrew Bath", "system": "Hebrew", "category": "volume", "si_unit": "L", "to_si": 22.0},
    {"name": "Hebrew Hin", "system": "Hebrew", "category": "volume", "si_unit": "L", "to_si": 3.7},
    {"name": "Egyptian Hekat", "system": "Egyptian", "category": "volume", "si_unit": "L", "to_si": 4.8},
    {"name": "Egyptian Hinu", "system": "Egyptian", "category": "volume", "si_unit": "L", "to_si": 4.8 / 10.0, "note": "Derived: 1 hekat = 10 hinu (approx; historical definitions vary)"},
    {"name": "Hebrew Seah", "system": "Hebrew", "category": "volume", "si_unit": "L", "to_si": 7.3},
    {"name": "Hebrew Omer", "system": "Hebrew", "category": "volume", "si_unit": "L", "to_si": 2.2},
    {"name": "Roman Modius", "system": "Roman", "category": "volume", "si_unit": "L", "to_si": 8.62},
    {"name": "Greek Chous", "system": "Greek", "category": "volume", "si_unit": "L", "to_si": 3.27}
]


TIME_UNITS: List[Dict[str, object]] = [
    # Time (seconds)
    {"name": "Second", "system": "SI", "category": "time", "si_unit": "s", "to_si": 1.0},
    {"name": "Minute", "system": "SI", "category": "time", "si_unit": "s", "to_si": 60.0},
    {"name": "Hour", "system": "SI", "category": "time", "si_unit": "s", "to_si": 3600.0},
    {"name": "Day", "system": "SI", "category": "time", "si_unit": "s", "to_si": 86400.0},
    {"name": "Week", "system": "Common", "category": "time", "si_unit": "s", "to_si": 7.0 * 86400.0},

    # Ancient/Historical (explicitly approximate)
    {
        "name": "Seasonal Hour (Ancient Egypt/Antiquity)",
        "system": "Historical",
        "category": "time",
        "si_unit": "s",
        "to_si": 3600.0,
        "note": "Unequal hour: daylight/night divided into 12 parts; duration varies by season/latitude. Using 3600s as a mean placeholder.",
    },

    # Astronomical Day Units
    {
        "name": "Sidereal Day",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 86164.0905,  # 23h 56m 4.0905s
        "note": "Earth's rotation period relative to distant stars. Shorter than solar day by ~3m 56s.",
    },
    {
        "name": "Solar Day (mean)",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 86400.0,
        "note": "Mean solar day; Earth's rotation relative to the Sun. Defined as exactly 86400 SI seconds.",
    },

    # Astronomical Month Units (Lunar periods)
    {
        "name": "Synodic Month (Lunation)",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 29.53059 * 86400.0,  # ~29.53 days
        "note": "New Moon to New Moon; the lunar phase cycle as seen from Earth. ~29.53 days.",
    },
    {
        "name": "Sidereal Month",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 27.321661 * 86400.0,  # ~27.32 days
        "note": "Moon's orbital period relative to fixed stars. ~27.32 days.",
    },
    {
        "name": "Tropical Month",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 27.321582 * 86400.0,
        "note": "Time for Moon to return to same ecliptic longitude. ~27.32 days.",
    },
    {
        "name": "Anomalistic Month",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 27.554550 * 86400.0,  # ~27.55 days
        "note": "Perigee to perigee; Moon's closest approach cycle. ~27.55 days.",
    },
    {
        "name": "Draconic Month (Nodical)",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 27.212220 * 86400.0,  # ~27.21 days
        "note": "Node to node; important for eclipse prediction. ~27.21 days.",
    },

    # Astronomical Year Units
    {
        "name": "Julian Year (astronomy)",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 365.25 * 86400.0,
        "note": "Exact by definition: 365.25 days of 86400 SI seconds. Used in astronomy.",
    },
    {
        "name": "Tropical Year (mean)",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 365.24219 * 86400.0,
        "note": "Vernal equinox to vernal equinox. Basis for civil calendars. ~365.2422 days.",
    },
    {
        "name": "Sidereal Year",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 365.256363 * 86400.0,  # ~365.26 days
        "note": "Earth's orbital period relative to fixed stars. ~365.26 days.",
    },
    {
        "name": "Anomalistic Year",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 365.259636 * 86400.0,  # ~365.26 days
        "note": "Perihelion to perihelion; Earth's closest approach to Sun cycle. ~365.26 days.",
    },
    {
        "name": "Draconic Year (Eclipse Year)",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 346.620076 * 86400.0,  # ~346.62 days
        "note": "Time for Sun to return to same lunar node. Important for eclipse cycles. ~346.62 days.",
    },
    {
        "name": "Gregorian Year (mean)",
        "system": "Calendar",
        "category": "time",
        "si_unit": "s",
        "to_si": 365.2425 * 86400.0,
        "note": "Average Gregorian calendar year over 400-year cycle. 365.2425 days.",
    },
    {
        "name": "Besselian Year",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 365.242198781 * 86400.0,
        "note": "Tropical year starting when Sun's mean longitude is 280°. Used in star catalogs.",
    },
    {
        "name": "Gaussian Year",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 365.2568983 * 86400.0,
        "note": "Theoretical orbital period from Gauss's gravitational constant. ~365.257 days.",
    },

    # Astronomical Cycles
    {
        "name": "Metonic Cycle",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 6939.6882 * 86400.0,  # 19 tropical years ≈ 235 synodic months
        "note": "~19 years; lunar phases repeat on same calendar dates. Used in calendar systems.",
    },
    {
        "name": "Saros Cycle",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 6585.3211 * 86400.0,  # ~18.03 years
        "note": "~18 years 11 days; eclipse cycle. Similar eclipses repeat after one Saros.",
    },
    {
        "name": "Callippic Cycle",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 4.0 * 6939.6882 * 86400.0,  # 4 Metonic cycles = 76 years
        "note": "76 years; 4 Metonic cycles. More accurate lunar-solar synchronization.",
    },
    {
        "name": "Hipparchic Cycle",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 304.0 * 365.24219 * 86400.0,  # ~304 years
        "note": "~304 years; 4 Callippic cycles minus 1 day. Ancient Greek astronomical cycle.",
    },
    {
        "name": "Precession Cycle (Great Year)",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 25772.0 * 365.25 * 86400.0,  # ~25,772 years
        "note": "~25,772 years; Earth's axial precession cycle. Also called Platonic Year.",
    },
    {
        "name": "Astrological Age",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": (25772.0 / 12.0) * 365.25 * 86400.0,  # ~2,148 years
        "note": "~2,148 years; 1/12 of precession cycle. E.g., Age of Aquarius.",
    },

    # Cosmic/Galactic Time Units
    {
        "name": "Galactic Year (Cosmic Year)",
        "system": "Astronomy",
        "category": "time",
        "si_unit": "s",
        "to_si": 225000000.0 * 365.25 * 86400.0,  # ~225 million years
        "note": "~225-250 million years; Sun's orbital period around Milky Way center.",
    },

    # Fundamental Physics Time Units
    {
        "name": "Planck Time",
        "system": "Physics",
        "category": "time",
        "si_unit": "s",
        "to_si": 5.391247e-44,
        "note": "Fundamental unit of time in quantum gravity. Smallest meaningful time interval.",
    },
    {
        "name": "Atomic Unit of Time",
        "system": "Physics",
        "category": "time",
        "si_unit": "s",
        "to_si": 2.4188843265857e-17,
        "note": "Natural unit in atomic physics. Period of electron orbit in Bohr model / 2π.",
    },

    # Planetary Day Units
    {
        "name": "Martian Sol",
        "system": "Planetary",
        "category": "time",
        "si_unit": "s",
        "to_si": 88775.244,  # 24h 39m 35.244s
        "note": "A solar day on Mars. ~24h 39m 35s; ~2.7% longer than Earth day.",
    },
    {
        "name": "Martian Year",
        "system": "Planetary",
        "category": "time",
        "si_unit": "s",
        "to_si": 686.971 * 86400.0,  # ~687 Earth days
        "note": "Mars orbital period. ~687 Earth days; ~1.88 Earth years.",
    },
    {
        "name": "Jovian Year",
        "system": "Planetary",
        "category": "time",
        "si_unit": "s",
        "to_si": 4332.59 * 86400.0,  # ~11.86 Earth years
        "note": "Jupiter's orbital period. ~11.86 Earth years.",
    },
    {
        "name": "Saturnian Year",
        "system": "Planetary",
        "category": "time",
        "si_unit": "s",
        "to_si": 10759.22 * 86400.0,  # ~29.46 Earth years
        "note": "Saturn's orbital period. ~29.46 Earth years.",
    },
    {
        "name": "Uranian Year",
        "system": "Planetary",
        "category": "time",
        "si_unit": "s",
        "to_si": 30688.5 * 86400.0,  # ~84.01 Earth years
        "note": "Uranus orbital period. ~84.01 Earth years.",
    },
    {
        "name": "Neptunian Year",
        "system": "Planetary",
        "category": "time",
        "si_unit": "s",
        "to_si": 60182.0 * 86400.0,  # ~164.8 Earth years
        "note": "Neptune's orbital period. ~164.8 Earth years.",
    },
    {
        "name": "Venusian Day (Solar)",
        "system": "Planetary",
        "category": "time",
        "si_unit": "s",
        "to_si": 116.75 * 86400.0,  # ~116.75 Earth days
        "note": "A solar day on Venus. ~116.75 Earth days; longer than its year!",
    },
    {
        "name": "Mercury Solar Day",
        "system": "Planetary",
        "category": "time",
        "si_unit": "s",
        "to_si": 175.94 * 86400.0,  # ~176 Earth days
        "note": "A solar day on Mercury. ~176 Earth days; 2 Mercury years.",
    },

    # Hindu Units of Time (Surya Siddhanta tradition)
    # Small units
    {
        "name": "Truti (Hindu)",
        "system": "Hindu",
        "category": "time",
        "si_unit": "s",
        "to_si": 1.0 / 33750.0,  # ~29.63 microseconds
        "note": "Smallest practical Hindu time unit; 1/33,750 of a second (Surya Siddhanta).",
    },
    {
        "name": "Tatpara (Hindu)",
        "system": "Hindu",
        "category": "time",
        "si_unit": "s",
        "to_si": 100.0 / 33750.0,  # 100 Trutis ≈ 2.963 ms
        "note": "100 Trutis = 1 Tatpara.",
    },
    {
        "name": "Nimesha (Hindu)",
        "system": "Hindu",
        "category": "time",
        "si_unit": "s",
        "to_si": 16.0 / 75.0,  # ~0.2133 seconds (blink of an eye)
        "note": "The blink of an eye; 16/75 seconds. 30 Tatparas = 1 Nimesha.",
    },
    {
        "name": "Kashtha (Hindu)",
        "system": "Hindu",
        "category": "time",
        "si_unit": "s",
        "to_si": 18.0 * 16.0 / 75.0,  # 18 Nimeshas = 3.84 seconds
        "note": "18 Nimeshas = 1 Kashtha.",
    },
    {
        "name": "Kala (Hindu)",
        "system": "Hindu",
        "category": "time",
        "si_unit": "s",
        "to_si": 30.0 * 18.0 * 16.0 / 75.0,  # 30 Kashthas = 115.2 seconds
        "note": "30 Kashthas = 1 Kala (approximately 1.92 minutes).",
    },
    {
        "name": "Ghatika/Ghati (Hindu)",
        "system": "Hindu",
        "category": "time",
        "si_unit": "s",
        "to_si": 24.0 * 60.0,  # 24 minutes = 1440 seconds
        "note": "30 Kalas = 1 Ghatika = 24 minutes. 60 Ghatikas = 1 day.",
    },
    {
        "name": "Muhurta (Hindu)",
        "system": "Hindu",
        "category": "time",
        "si_unit": "s",
        "to_si": 48.0 * 60.0,  # 48 minutes = 2880 seconds
        "note": "2 Ghatikas = 1 Muhurta = 48 minutes. 30 Muhurtas = 1 day. Auspicious time unit for rituals.",
    },
    {
        "name": "Prahara/Yama (Hindu)",
        "system": "Hindu",
        "category": "time",
        "si_unit": "s",
        "to_si": 3.0 * 3600.0,  # 3 hours = 10800 seconds
        "note": "1/8 of a day = 3 hours. Also called Yama (watch).",
    },
    {
        "name": "Ahoratra (Hindu Day)",
        "system": "Hindu",
        "category": "time",
        "si_unit": "s",
        "to_si": 86400.0,  # 24 hours
        "note": "A full day and night cycle = 30 Muhurtas = 60 Ghatikas.",
    },

    # Hindu Calendar Units
    {
        "name": "Paksha (Hindu Fortnight)",
        "system": "Hindu",
        "category": "time",
        "si_unit": "s",
        "to_si": 15.0 * 86400.0,  # 15 days
        "note": "Half a lunar month = 15 tithis (lunar days). Shukla (bright) or Krishna (dark) Paksha.",
    },
    {
        "name": "Masa (Hindu Month)",
        "system": "Hindu",
        "category": "time",
        "si_unit": "s",
        "to_si": 30.0 * 86400.0,  # 30 days
        "note": "2 Pakshas = 1 lunar month (approximately 29.5 solar days). Using 30-day convention.",
    },
    {
        "name": "Ritu (Hindu Season)",
        "system": "Hindu",
        "category": "time",
        "si_unit": "s",
        "to_si": 2.0 * 30.0 * 86400.0,  # 2 months = 60 days
        "note": "2 months = 1 season. Six Ritus in a year.",
    },
    {
        "name": "Ayana (Hindu Half-Year)",
        "system": "Hindu",
        "category": "time",
        "si_unit": "s",
        "to_si": 6.0 * 30.0 * 86400.0,  # 6 months = 180 days
        "note": "6 months = 1 Ayana. Uttarayana (northward) or Dakshinayana (southward) sun movement.",
    },
    {
        "name": "Samvatsara (Hindu Year)",
        "system": "Hindu",
        "category": "time",
        "si_unit": "s",
        "to_si": 360.0 * 86400.0,  # 360 days (traditional)
        "note": "Traditional Hindu year of 360 days (12 months of 30 days). Tropical year also used.",
    },

    # Hindu Cosmic Time Units (Yuga System)
    {
        "name": "Kali Yuga (Hindu)",
        "system": "Hindu Cosmic",
        "category": "time",
        "si_unit": "s",
        "to_si": 432000.0 * 365.25 * 86400.0,  # 432,000 years
        "note": "The current age; 432,000 years. The shortest and most degraded of the four Yugas.",
    },
    {
        "name": "Dvapara Yuga (Hindu)",
        "system": "Hindu Cosmic",
        "category": "time",
        "si_unit": "s",
        "to_si": 864000.0 * 365.25 * 86400.0,  # 864,000 years
        "note": "2× Kali Yuga = 864,000 years. Third age of the cosmic cycle.",
    },
    {
        "name": "Treta Yuga (Hindu)",
        "system": "Hindu Cosmic",
        "category": "time",
        "si_unit": "s",
        "to_si": 1296000.0 * 365.25 * 86400.0,  # 1,296,000 years
        "note": "3× Kali Yuga = 1,296,000 years. Second age of the cosmic cycle.",
    },
    {
        "name": "Satya Yuga/Krita Yuga (Hindu)",
        "system": "Hindu Cosmic",
        "category": "time",
        "si_unit": "s",
        "to_si": 1728000.0 * 365.25 * 86400.0,  # 1,728,000 years
        "note": "4× Kali Yuga = 1,728,000 years. The golden age of truth and virtue.",
    },
    {
        "name": "Mahayuga/Chaturyuga (Hindu)",
        "system": "Hindu Cosmic",
        "category": "time",
        "si_unit": "s",
        "to_si": 4320000.0 * 365.25 * 86400.0,  # 4,320,000 years
        "note": "Sum of all four Yugas = 4,320,000 years. One complete cosmic cycle.",
    },
    {
        "name": "Manvantara (Hindu)",
        "system": "Hindu Cosmic",
        "category": "time",
        "si_unit": "s",
        "to_si": 71.0 * 4320000.0 * 365.25 * 86400.0,  # ~306,720,000 years
        "note": "71 Mahayugas = 1 Manvantara (~306.72 million years). Reign of one Manu.",
    },
    {
        "name": "Kalpa (Hindu)",
        "system": "Hindu Cosmic",
        "category": "time",
        "si_unit": "s",
        "to_si": 1000.0 * 4320000.0 * 365.25 * 86400.0,  # 4.32 billion years
        "note": "1000 Mahayugas = 1 Kalpa = 4.32 billion years. One day of Brahma.",
    },
]


# Physical Constants organized by category
PHYSICAL_CONSTANTS: List[Dict[str, object]] = [
    # Fundamental Constants
    {"name": "Speed of Light in Vacuum", "symbol": "c", "value": 299792458.0, "unit": "m/s", "category": "Fundamental", "note": "Exact by definition (SI 2019)"},
    {"name": "Planck Constant", "symbol": "h", "value": 6.62607015e-34, "unit": "J·s", "category": "Fundamental", "note": "Exact by definition (SI 2019)"},
    {"name": "Reduced Planck Constant", "symbol": "ħ", "value": 1.054571817e-34, "unit": "J·s", "category": "Fundamental", "note": "h/(2π)"},
    {"name": "Gravitational Constant", "symbol": "G", "value": 6.67430e-11, "unit": "m³/(kg·s²)", "category": "Fundamental", "note": "Newton's gravitational constant"},
    {"name": "Elementary Charge", "symbol": "e", "value": 1.602176634e-19, "unit": "C", "category": "Fundamental", "note": "Exact by definition (SI 2019)"},
    {"name": "Boltzmann Constant", "symbol": "k_B", "value": 1.380649e-23, "unit": "J/K", "category": "Fundamental", "note": "Exact by definition (SI 2019)"},
    {"name": "Avogadro Constant", "symbol": "N_A", "value": 6.02214076e23, "unit": "mol⁻¹", "category": "Fundamental", "note": "Exact by definition (SI 2019)"},
    {"name": "Gas Constant", "symbol": "R", "value": 8.314462618, "unit": "J/(mol·K)", "category": "Fundamental", "note": "N_A × k_B"},
    {"name": "Fine-Structure Constant", "symbol": "α", "value": 7.2973525693e-3, "unit": "dimensionless", "category": "Fundamental", "note": "~1/137; electromagnetic coupling strength"},
    {"name": "Vacuum Permittivity", "symbol": "ε₀", "value": 8.8541878128e-12, "unit": "F/m", "category": "Fundamental", "note": "Electric constant"},
    {"name": "Vacuum Permeability", "symbol": "μ₀", "value": 1.25663706212e-6, "unit": "N/A²", "category": "Fundamental", "note": "Magnetic constant"},
    {"name": "Coulomb Constant", "symbol": "k_e", "value": 8.9875517923e9, "unit": "N·m²/C²", "category": "Fundamental", "note": "1/(4πε₀)"},

    # Atomic & Particle Physics
    {"name": "Electron Mass", "symbol": "m_e", "value": 9.1093837015e-31, "unit": "kg", "category": "Atomic", "note": ""},
    {"name": "Proton Mass", "symbol": "m_p", "value": 1.67262192369e-27, "unit": "kg", "category": "Atomic", "note": ""},
    {"name": "Neutron Mass", "symbol": "m_n", "value": 1.67492749804e-27, "unit": "kg", "category": "Atomic", "note": ""},
    {"name": "Atomic Mass Unit", "symbol": "u", "value": 1.66053906660e-27, "unit": "kg", "category": "Atomic", "note": "Unified atomic mass unit"},
    {"name": "Bohr Radius", "symbol": "a₀", "value": 5.29177210903e-11, "unit": "m", "category": "Atomic", "note": "Most probable H electron distance"},
    {"name": "Rydberg Constant", "symbol": "R_∞", "value": 10973731.568160, "unit": "m⁻¹", "category": "Atomic", "note": "Hydrogen spectral constant"},
    {"name": "Bohr Magneton", "symbol": "μ_B", "value": 9.2740100783e-24, "unit": "J/T", "category": "Atomic", "note": "Electron magnetic moment unit"},
    {"name": "Nuclear Magneton", "symbol": "μ_N", "value": 5.0507837461e-27, "unit": "J/T", "category": "Atomic", "note": "Nucleon magnetic moment unit"},
    {"name": "Electron Volt", "symbol": "eV", "value": 1.602176634e-19, "unit": "J", "category": "Atomic", "note": "Energy unit in particle physics"},
    {"name": "Classical Electron Radius", "symbol": "r_e", "value": 2.8179403262e-15, "unit": "m", "category": "Atomic", "note": "Compton wavelength / (2πα)"},
    {"name": "Compton Wavelength (electron)", "symbol": "λ_C", "value": 2.42631023867e-12, "unit": "m", "category": "Atomic", "note": "h/(m_e × c)"},

    # Thermodynamic
    {"name": "Stefan-Boltzmann Constant", "symbol": "σ", "value": 5.670374419e-8, "unit": "W/(m²·K⁴)", "category": "Thermodynamic", "note": "Black-body radiation"},
    {"name": "Wien Displacement Constant", "symbol": "b", "value": 2.897771955e-3, "unit": "m·K", "category": "Thermodynamic", "note": "Peak wavelength of black body"},
    {"name": "First Radiation Constant", "symbol": "c₁", "value": 3.741771852e-16, "unit": "W·m²", "category": "Thermodynamic", "note": "2πhc²"},
    {"name": "Second Radiation Constant", "symbol": "c₂", "value": 1.438776877e-2, "unit": "m·K", "category": "Thermodynamic", "note": "hc/k_B"},
    {"name": "Standard Atmosphere", "symbol": "atm", "value": 101325.0, "unit": "Pa", "category": "Thermodynamic", "note": "Standard pressure"},
    {"name": "Standard Gravity", "symbol": "g₀", "value": 9.80665, "unit": "m/s²", "category": "Thermodynamic", "note": "Standard acceleration"},

    # Astronomical
    {"name": "Astronomical Unit", "symbol": "AU", "value": 1.495978707e11, "unit": "m", "category": "Astronomical", "note": "Earth-Sun mean distance"},
    {"name": "Light-Year", "symbol": "ly", "value": 9.4607304725808e15, "unit": "m", "category": "Astronomical", "note": "Distance light travels in one Julian year"},
    {"name": "Parsec", "symbol": "pc", "value": 3.0856775814914e16, "unit": "m", "category": "Astronomical", "note": "Parallax of 1 arcsecond"},
    {"name": "Solar Mass", "symbol": "M☉", "value": 1.98892e30, "unit": "kg", "category": "Astronomical", "note": "Mass of the Sun"},
    {"name": "Solar Radius", "symbol": "R☉", "value": 6.9634e8, "unit": "m", "category": "Astronomical", "note": "Radius of the Sun"},
    {"name": "Solar Luminosity", "symbol": "L☉", "value": 3.828e26, "unit": "W", "category": "Astronomical", "note": "Luminosity of the Sun"},
    {"name": "Earth Mass", "symbol": "M⊕", "value": 5.9722e24, "unit": "kg", "category": "Astronomical", "note": "Mass of Earth"},
    {"name": "Earth Radius (mean)", "symbol": "R⊕", "value": 6.371e6, "unit": "m", "category": "Astronomical", "note": "Mean radius of Earth"},
    {"name": "Earth Radius (equatorial)", "symbol": "R_eq", "value": 6.3781e6, "unit": "m", "category": "Astronomical", "note": "Equatorial radius"},
    {"name": "Earth Radius (polar)", "symbol": "R_pol", "value": 6.3568e6, "unit": "m", "category": "Astronomical", "note": "Polar radius"},
    {"name": "Moon Mass", "symbol": "M_moon", "value": 7.342e22, "unit": "kg", "category": "Astronomical", "note": "Mass of the Moon"},
    {"name": "Moon Radius", "symbol": "R_moon", "value": 1.7374e6, "unit": "m", "category": "Astronomical", "note": "Mean radius of the Moon"},
    {"name": "Jupiter Mass", "symbol": "M_J", "value": 1.89813e27, "unit": "kg", "category": "Astronomical", "note": "Mass of Jupiter"},
    {"name": "Jupiter Radius", "symbol": "R_J", "value": 6.9911e7, "unit": "m", "category": "Astronomical", "note": "Equatorial radius of Jupiter"},
    {"name": "Hubble Constant", "symbol": "H₀", "value": 67.4, "unit": "km/s/Mpc", "category": "Astronomical", "note": "Planck 2018 value; ~70 km/s/Mpc"},
    {"name": "Age of Universe", "symbol": "t₀", "value": 4.35e17, "unit": "s", "category": "Astronomical", "note": "~13.8 billion years"},

    # Planck Units
    {"name": "Planck Length", "symbol": "l_P", "value": 1.616255e-35, "unit": "m", "category": "Planck", "note": "√(ħG/c³)"},
    {"name": "Planck Time", "symbol": "t_P", "value": 5.391247e-44, "unit": "s", "category": "Planck", "note": "√(ħG/c⁵)"},
    {"name": "Planck Mass", "symbol": "m_P", "value": 2.176434e-8, "unit": "kg", "category": "Planck", "note": "√(ħc/G)"},
    {"name": "Planck Temperature", "symbol": "T_P", "value": 1.416784e32, "unit": "K", "category": "Planck", "note": "√(ħc⁵/Gk_B²)"},
    {"name": "Planck Energy", "symbol": "E_P", "value": 1.9561e9, "unit": "J", "category": "Planck", "note": "m_P×c²"},
    {"name": "Planck Charge", "symbol": "q_P", "value": 1.875546e-18, "unit": "C", "category": "Planck", "note": "√(4πε₀ħc)"},

    # Chemistry
    {"name": "Faraday Constant", "symbol": "F", "value": 96485.33212, "unit": "C/mol", "category": "Chemistry", "note": "N_A × e"},
    {"name": "Molar Volume (ideal gas, STP)", "symbol": "V_m", "value": 22.41396954, "unit": "L/mol", "category": "Chemistry", "note": "At 0°C, 1 atm"},
    {"name": "Molar Mass of Carbon-12", "symbol": "M(C-12)", "value": 11.9999999958e-3, "unit": "kg/mol", "category": "Chemistry", "note": "Approximately 12 g/mol"},
    {"name": "Loschmidt Constant", "symbol": "n₀", "value": 2.6867774e25, "unit": "m⁻³", "category": "Chemistry", "note": "Number density at STP"},

    # Mathematical/Numerical
    {"name": "Pi", "symbol": "π", "value": 3.141592653589793, "unit": "dimensionless", "category": "Mathematical", "note": "Ratio of circumference to diameter"},
    {"name": "Euler's Number", "symbol": "e", "value": 2.718281828459045, "unit": "dimensionless", "category": "Mathematical", "note": "Base of natural logarithm"},
    {"name": "Golden Ratio", "symbol": "φ", "value": 1.618033988749895, "unit": "dimensionless", "category": "Mathematical", "note": "(1 + √5) / 2"},
    {"name": "Square Root of 2", "symbol": "√2", "value": 1.4142135623730951, "unit": "dimensionless", "category": "Mathematical", "note": "Pythagoras' constant"},
    {"name": "Square Root of 3", "symbol": "√3", "value": 1.7320508075688772, "unit": "dimensionless", "category": "Mathematical", "note": "Theodorus' constant"},
    {"name": "Square Root of 5", "symbol": "√5", "value": 2.23606797749979, "unit": "dimensionless", "category": "Mathematical", "note": "Appears in golden ratio"},
    {"name": "Euler-Mascheroni Constant", "symbol": "γ", "value": 0.5772156649015329, "unit": "dimensionless", "category": "Mathematical", "note": "Limiting difference between harmonic series and ln"},
    {"name": "Apéry's Constant", "symbol": "ζ(3)", "value": 1.2020569031595942, "unit": "dimensionless", "category": "Mathematical", "note": "Riemann zeta function at 3"},
    {"name": "Catalan's Constant", "symbol": "G", "value": 0.9159655941772190, "unit": "dimensionless", "category": "Mathematical", "note": "Alternating series of inverse odd squares"},
    {"name": "Feigenbaum Constant (δ)", "symbol": "δ", "value": 4.669201609102990, "unit": "dimensionless", "category": "Mathematical", "note": "Ratio of period-doubling intervals"},
    {"name": "Feigenbaum Constant (α)", "symbol": "α_F", "value": 2.502907875095892, "unit": "dimensionless", "category": "Mathematical", "note": "Width scaling in bifurcation"},
]


# Sacred Geometry Constants and Ratios
SACRED_GEOMETRY: List[Dict[str, object]] = [
    # Primary Sacred Ratios
    {"name": "Golden Ratio (Phi)", "symbol": "φ", "value": (1 + 5**0.5) / 2, "category": "Primary Ratios", "note": "(1+√5)/2 ≈ 1.618. Divine proportion; appears in nature, art, architecture."},
    {"name": "Golden Ratio Conjugate", "symbol": "Φ", "value": (5**0.5 - 1) / 2, "category": "Primary Ratios", "note": "(√5-1)/2 ≈ 0.618. Also φ-1 = 1/φ."},
    {"name": "Silver Ratio", "symbol": "δ_s", "value": 1 + 2**0.5, "category": "Primary Ratios", "note": "1+√2 ≈ 2.414. Ratio in regular octagon."},
    {"name": "Bronze Ratio", "symbol": "σ", "value": (3 + 13**0.5) / 2, "category": "Primary Ratios", "note": "(3+√13)/2 ≈ 3.303. Third metallic mean."},
    {"name": "Plastic Number", "symbol": "ρ", "value": 1.324717957244746, "category": "Primary Ratios", "note": "Real root of x³ = x + 1. Only Pisot number that is also a Salem number."},
    {"name": "Supergolden Ratio", "symbol": "ψ", "value": 1.465571231876768, "category": "Primary Ratios", "note": "Real root of x³ = x² + 1."},

    # Pi-Related
    {"name": "Pi", "symbol": "π", "value": 3.141592653589793, "category": "Circle Constants", "note": "Ratio of circumference to diameter."},
    {"name": "Tau (2π)", "symbol": "τ", "value": 6.283185307179586, "category": "Circle Constants", "note": "Full circle in radians. Some prefer τ over π."},
    {"name": "Pi/2 (Quadrant)", "symbol": "π/2", "value": 1.5707963267948966, "category": "Circle Constants", "note": "Quarter circle; right angle in radians."},
    {"name": "Pi/3 (Sextant)", "symbol": "π/3", "value": 1.0471975511965976, "category": "Circle Constants", "note": "60 degrees; interior angle of equilateral triangle."},
    {"name": "Pi/4 (Octant)", "symbol": "π/4", "value": 0.7853981633974483, "category": "Circle Constants", "note": "45 degrees; half of right angle."},
    {"name": "Pi/5 (Pentagon)", "symbol": "π/5", "value": 0.6283185307179587, "category": "Circle Constants", "note": "36 degrees; related to pentagram."},
    {"name": "Pi/6 (Dodecant)", "symbol": "π/6", "value": 0.5235987755982989, "category": "Circle Constants", "note": "30 degrees; half of sextant."},

    # Square Roots (Geometric Means)
    {"name": "Square Root of 2", "symbol": "√2", "value": 1.4142135623730951, "category": "Roots", "note": "Diagonal of unit square. First known irrational."},
    {"name": "Square Root of 3", "symbol": "√3", "value": 1.7320508075688772, "category": "Roots", "note": "Height of equilateral triangle with side 2."},
    {"name": "Square Root of 5", "symbol": "√5", "value": 2.23606797749979, "category": "Roots", "note": "Diagonal of 1×2 rectangle. Appears in φ."},
    {"name": "Square Root of 6", "symbol": "√6", "value": 2.449489742783178, "category": "Roots", "note": "√2 × √3"},
    {"name": "Square Root of 7", "symbol": "√7", "value": 2.6457513110645907, "category": "Roots", "note": "Related to heptagon."},

    # Vesica Piscis Ratios
    {"name": "Vesica Piscis Height/Width", "symbol": "VP", "value": 1.7320508075688772, "category": "Vesica Piscis", "note": "√3. Height to width ratio of vesica piscis."},
    {"name": "Vesica Piscis Width/Height", "symbol": "1/VP", "value": 0.5773502691896257, "category": "Vesica Piscis", "note": "1/√3. Width to height ratio."},

    # Platonic Solid Ratios
    {"name": "Tetrahedron Edge/Circumradius", "symbol": "Tet", "value": 1.632993161855452, "category": "Platonic Solids", "note": "√(8/3). Edge length when circumradius = 1."},
    {"name": "Cube Edge/Circumradius", "symbol": "Cube", "value": 1.1547005383792517, "category": "Platonic Solids", "note": "2/√3. Edge length when circumradius = 1."},
    {"name": "Octahedron Edge/Circumradius", "symbol": "Oct", "value": 1.4142135623730951, "category": "Platonic Solids", "note": "√2. Edge length when circumradius = 1."},
    {"name": "Dodecahedron Edge/Circumradius", "symbol": "Dod", "value": 0.7136441795461797, "category": "Platonic Solids", "note": "4/(φ²√3). Uses golden ratio."},
    {"name": "Icosahedron Edge/Circumradius", "symbol": "Ico", "value": 1.0514622242382672, "category": "Platonic Solids", "note": "1/sin(2π/5). Related to pentagon."},
    {"name": "Icosahedron to Dodecahedron", "symbol": "I/D", "value": 1.618033988749895, "category": "Platonic Solids", "note": "Their edges relate by φ!"},

    # Pentagon & Pentagram
    {"name": "Pentagon Diagonal/Side", "symbol": "d/s", "value": 1.618033988749895, "category": "Pentagon", "note": "φ. The golden ratio appears in pentagons."},
    {"name": "Pentagram Inner/Outer", "symbol": "P*", "value": 0.381966011250105, "category": "Pentagon", "note": "1/φ² = φ-1-1. Ratio of inner to outer pentagon."},
    {"name": "Pentagon Interior Angle", "symbol": "θ_5", "value": 108.0, "category": "Pentagon", "note": "Interior angle in degrees: (5-2)×180/5."},

    # Hexagon & Hexagram
    {"name": "Hexagon Diagonal/Side", "symbol": "Hex", "value": 1.7320508075688772, "category": "Hexagon", "note": "√3. Long diagonal is 2×side."},
    {"name": "Hexagon Apothem/Side", "symbol": "a/s", "value": 0.8660254037844386, "category": "Hexagon", "note": "√3/2. Apothem to side ratio."},
    {"name": "Hexagon Interior Angle", "symbol": "θ_6", "value": 120.0, "category": "Hexagon", "note": "Interior angle in degrees."},

    # Fibonacci & Lucas
    {"name": "Fibonacci Limit Ratio", "symbol": "F_n/F_{n-1}", "value": 1.618033988749895, "category": "Sequences", "note": "Consecutive Fibonacci numbers approach φ."},
    {"name": "Lucas Limit Ratio", "symbol": "L_n/L_{n-1}", "value": 1.618033988749895, "category": "Sequences", "note": "Lucas numbers also approach φ."},
    {"name": "Tribonacci Constant", "symbol": "T", "value": 1.839286755214161, "category": "Sequences", "note": "Limit of Tribonacci sequence ratios."},

    # Egyptian & Ancient
    {"name": "Royal Cubit Ratio", "symbol": "RC", "value": 1.047197551196598, "category": "Ancient", "note": "π/3 ≈ 1.047. Some link cubit to π/6 meters."},
    {"name": "Pyramid Angle (Giza)", "symbol": "θ_Giza", "value": 51.84, "category": "Ancient", "note": "Great Pyramid slope angle in degrees."},
    {"name": "Pyramid Height/Base Ratio", "symbol": "h/b", "value": 0.636, "category": "Ancient", "note": "Great Pyramid: ~4/2π = 2/π."},
    {"name": "Seked (Pyramid Slope)", "symbol": "Seked", "value": 5.5, "category": "Ancient", "note": "Horizontal run per cubit rise (Great Pyramid)."},
]


# Base conversion: digits for bases 2-36
BASE_DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Zodiac signs for zodiacal notation
ZODIAC_SIGNS = [
    ("♈", "Aries"), ("♉", "Taurus"), ("♊", "Gemini"), ("♋", "Cancer"),
    ("♌", "Leo"), ("♍", "Virgo"), ("♎", "Libra"), ("♏", "Scorpio"),
    ("♐", "Sagittarius"), ("♑", "Capricorn"), ("♒", "Aquarius"), ("♓", "Pisces"),
]

# Coordinate system descriptions
COORDINATE_SYSTEMS = [
    {
        "name": "Equatorial (RA/Dec)",
        "coords": ("Right Ascension", "Declination"),
        "units": ("hours (0-24h)", "degrees (-90° to +90°)"),
        "note": "Most common astronomical system. RA measured eastward from vernal equinox. Dec measured from celestial equator.",
        "category": "Celestial",
    },
    {
        "name": "Horizontal (Alt/Az)",
        "coords": ("Altitude", "Azimuth"),
        "units": ("degrees (0°-90°)", "degrees (0°-360°)"),
        "note": "Observer-dependent. Altitude above horizon, Azimuth from North through East. Changes with time and location.",
        "category": "Observer",
    },
    {
        "name": "Ecliptic",
        "coords": ("Ecliptic Longitude", "Ecliptic Latitude"),
        "units": ("degrees (0°-360°)", "degrees (-90° to +90°)"),
        "note": "Based on Earth's orbital plane. Used for planets and zodiacal positions. Longitude measured from vernal equinox.",
        "category": "Celestial",
    },
    {
        "name": "Galactic",
        "coords": ("Galactic Longitude (l)", "Galactic Latitude (b)"),
        "units": ("degrees (0°-360°)", "degrees (-90° to +90°)"),
        "note": "Centered on Milky Way. l=0° toward galactic center (Sagittarius A*), b=0° on galactic plane.",
        "category": "Galactic",
    },
    {
        "name": "Supergalactic",
        "coords": ("Supergalactic Longitude (SGL)", "Supergalactic Latitude (SGB)"),
        "units": ("degrees (0°-360°)", "degrees (-90° to +90°)"),
        "note": "Based on supergalactic plane where many nearby galaxies concentrate. Used for large-scale structure.",
        "category": "Galactic",
    },
    {
        "name": "Hour Angle",
        "coords": ("Hour Angle", "Declination"),
        "units": ("hours (-12h to +12h)", "degrees (-90° to +90°)"),
        "note": "HA = Local Sidereal Time - RA. Measures westward from local meridian. HA=0 means object is culminating.",
        "category": "Observer",
    },
]



class AdvancedScientificCalculatorWindow(QMainWindow):
    """Lightweight scientific calculator with common functions.

    The evaluator is intentionally constrained to a safe set of math functions
    and constants. All trigonometric inputs expect radians.

    @RiteExempt: Visual Liturgy
    Note: This window is exempt from standard Visual Liturgy enforcement to maintain
    its sleek, modern, dark-themed aesthetic with vertical navigation loops.
    """

    def __init__(self, window_manager: Optional[object] = None, parent=None):
        super().__init__(parent)
        self.window_manager = window_manager
        self._last_answer: Optional[float] = None
        self._angle_mode: str = "RAD"
        self._memory: float = 0.0
        self._state_path = get_default_state_path()
        self._restoring_state = False
        self._last_measure_result: Optional[dict] = None
        self._last_time_result: Optional[dict] = None
        self.setWindowTitle("Advanced Scientific Calculator")
        self.resize(1000, 700) # Increased size for better split layout
        self.setMinimumSize(800, 600)
        
        # Main sleek dark theme
        self.setStyleSheet("""
            QMainWindow, QWidget { 
                background-color: #0f172a; 
                color: #e2e8f0; 
                font-family: "Segoe UI", Arial, sans-serif;
            }
            QScrollArea { border: none; }
            QLineEdit {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
                color: #f8fafc;
                font-family: monospace;
            }
            QLineEdit:focus { border: 1px solid #38bdf8; }
            QComboBox {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px;
                color: #f8fafc;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #1e293b;
                selection-background-color: #334155;
                color: #f8fafc;
            }
            QPushButton {
                background-color: #334155;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                color: #f8fafc;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #475569; }
            QPushButton:pressed { background-color: #1e293b; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Left Sidebar (Vertical Tabs) ---
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #1e293b;
                border: none;
                border-right: 1px solid #334155;
                outline: none;
            }
            QListWidget::item {
                height: 50px;
                padding-left: 16px;
                color: #94a3b8;
                border-left: 3px solid transparent;
            }
            QListWidget::item:hover {
                background-color: #334155;
                color: #f1f5f9;
            }
            QListWidget::item:selected {
                background-color: #0f172a;
                color: #38bdf8;
                border-left: 3px solid #38bdf8;
                font-weight: bold;
            }
        """)

        # --- Content Area ---
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #0f172a;")

        # --- Add Modules ---
        modules = [
            ("🧮 Calculator", self._build_calculator_tab()),
            ("📏 Ancient Measures", self._build_measures_tab()),
            ("⏳ Time Units", self._build_time_tab()),
            ("🔢 Base Converter", self._build_base_converter_tab()),
            ("π Constants", self._build_constants_tab()),
            ("✡ Sacred Geometry", self._build_sacred_geometry_tab()),
            ("🌐 Coordinates", self._build_coordinates_tab()),
            ("📐 Geometry Solver", self._build_geometry_solver_tab()),
        ]

        for name, widget in modules:
            # Create list item with icon (optional, using text for now)
            item = QListWidgetItem(name)
            item.setFont(QFont("Segoe UI", 11))
            self.sidebar.addItem(item)
            self.stack.addWidget(widget)

        # --- Layout Assembly ---
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)

        # Wire up selection
        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

        self._restore_persisted_state()

    def _build_time_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Time Conversion")
        header.setStyleSheet("font-size: 15pt; font-weight: 700; color: #e2e8f0;")
        layout.addWidget(header)

        subtitle = QLabel("Convert between SI time units and historically-attested (approximate) ones.")
        subtitle.setStyleSheet("color: #cbd5e1; font-size: 10pt;")
        layout.addWidget(subtitle)

        from_row = QHBoxLayout()
        from_row.setSpacing(8)
        from_label = QLabel("From:")
        from_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.time_from_unit_combo = QComboBox()
        self.time_from_unit_combo.currentIndexChanged.connect(self._update_time_conversion_result)
        from_row.addWidget(from_label)
        from_row.addWidget(self.time_from_unit_combo, 1)
        layout.addLayout(from_row)

        to_row = QHBoxLayout()
        to_row.setSpacing(8)
        to_label = QLabel("To:")
        to_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.time_to_unit_combo = QComboBox()
        self.time_to_unit_combo.currentIndexChanged.connect(self._update_time_conversion_result)
        to_row.addWidget(to_label)
        to_row.addWidget(self.time_to_unit_combo, 1)

        swap_btn = QPushButton("Swap")
        swap_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        swap_btn.setProperty("archetype", "navigator")
        swap_btn.clicked.connect(self._swap_time_units)
        to_row.addWidget(swap_btn)
        layout.addLayout(to_row)

        value_row = QHBoxLayout()
        value_row.setSpacing(8)
        value_label = QLabel("Value:")
        value_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.time_value_input = QLineEdit()
        self.time_value_input.setPlaceholderText("Enter a number")
        self.time_value_input.textChanged.connect(self._update_time_conversion_result)
        self.time_value_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 10px 10px;
                font-size: 12pt;
            }
            """
        )
        value_row.addWidget(value_label)
        value_row.addWidget(self.time_value_input, 1)
        layout.addLayout(value_row)

        self.time_result_label = QLabel("Enter a value to convert.")
        self.time_result_label.setWordWrap(True)
        self.time_result_label.setStyleSheet("color: #cbd5e1; font-size: 11pt;")
        layout.addWidget(self.time_result_label)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)
        actions_row.addStretch(1)

        self.copy_time_result_btn = QPushButton("Copy Result")
        self.copy_time_result_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_time_result_btn.setEnabled(False)
        self.copy_time_result_btn.setProperty("archetype", "scribe")
        self.copy_time_result_btn.clicked.connect(self._copy_time_result)
        actions_row.addWidget(self.copy_time_result_btn)
        layout.addLayout(actions_row)

        self.time_base_label = QLabel("")
        self.time_base_label.setStyleSheet("color: #94a3b8; font-size: 9pt;")
        layout.addWidget(self.time_base_label)

        self.time_note_label = QLabel("")
        self.time_note_label.setWordWrap(True)
        self.time_note_label.setStyleSheet("color: #94a3b8; font-size: 9pt; font-style: italic;")
        layout.addWidget(self.time_note_label)

        layout.addStretch()

        self._refresh_time_unit_combos()
        return container

    def _unit_options_for_time(self) -> List[Dict[str, object]]:
        return [u for u in TIME_UNITS if u.get("category") == "time"]

    def _refresh_time_unit_combos(self, *_):
        units = self._unit_options_for_time()

        # Group units by system in a specific order
        system_order = [
            "SI", "Common", "Calendar", "Astronomy", "Planetary", "Physics",
            "Hindu", "Hindu Cosmic", "Historical"
        ]

        # Create a dict of system -> list of units
        by_system: Dict[str, List[Dict[str, object]]] = {}
        for unit in units:
            sys = str(unit.get("system", "Other"))
            if sys not in by_system:
                by_system[sys] = []
            by_system[sys].append(unit)

        # Sort units within each system by name
        for sys in by_system:
            by_system[sys].sort(key=lambda u: str(u.get("name", "")))

        def populate(combo: QComboBox):
            """
            Populate logic.
            
            Args:
                combo: Description of combo.
            
            """
            combo.blockSignals(True)
            combo.clear()

            # Add units grouped by system with headers
            added_systems = set()
            for sys in system_order:
                if sys in by_system:
                    self._add_system_group(combo, sys, by_system[sys])
                    added_systems.add(sys)

            # Add any remaining systems not in our order
            for sys in sorted(by_system.keys()):
                if sys not in added_systems:
                    self._add_system_group(combo, sys, by_system[sys])

            combo.blockSignals(False)

        populate(self.time_from_unit_combo)
        populate(self.time_to_unit_combo)

        # Select first selectable items
        self._select_first_selectable(self.time_from_unit_combo, 0)
        self._select_first_selectable(self.time_to_unit_combo, 1)

        self._update_time_conversion_result()

    def _add_system_group(self, combo: QComboBox, system_name: str, units: List[Dict[str, object]]) -> None:
        """Add a group header and its units to the combo box."""

        # Get the model to add styled items
        model = combo.model()

        # Add separator/header item
        header_text = f"━━━ {system_name} ━━━"
        combo.addItem(header_text, None)
        header_idx = combo.count() - 1

        # Make header unselectable and styled
        if model and hasattr(model, 'item'):
            header_item = model.item(header_idx)  # type: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
            if header_item:
                header_item.setEnabled(False)
                header_item.setSelectable(False)

        # Add units under this system
        for unit in units:
            name = str(unit.get("name", ""))
            combo.addItem(f"    {name}", unit)

    def _select_first_selectable(self, combo: QComboBox, preferred_offset: int = 0) -> None:
        """Select the first selectable (non-header) item."""
        selectable_indices = []
        for i in range(combo.count()):
            data = combo.itemData(i)
            if data is not None:  # Headers have None data
                selectable_indices.append(i)

        if selectable_indices:
            # Try to use preferred offset, otherwise use first
            if preferred_offset < len(selectable_indices):
                combo.setCurrentIndex(selectable_indices[preferred_offset])
            else:
                combo.setCurrentIndex(selectable_indices[0])

    def _swap_time_units(self) -> None:
        if not hasattr(self, "time_from_unit_combo") or not hasattr(self, "time_to_unit_combo"):
            return
        from_idx = self.time_from_unit_combo.currentIndex()
        to_idx = self.time_to_unit_combo.currentIndex()
        self.time_from_unit_combo.blockSignals(True)
        self.time_to_unit_combo.blockSignals(True)
        self.time_from_unit_combo.setCurrentIndex(to_idx)
        self.time_to_unit_combo.setCurrentIndex(from_idx)
        self.time_from_unit_combo.blockSignals(False)
        self.time_to_unit_combo.blockSignals(False)
        self._update_time_conversion_result()

    def _copy_time_result(self) -> None:
        payload = self._last_time_result
        if not isinstance(payload, dict):
            return
        text = payload.get("copy_text")
        if not isinstance(text, str) or not text:
            return
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(text)

    def _current_time_unit(self, combo: QComboBox) -> Optional[Dict[str, object]]:
        idx = combo.currentIndex()
        if idx < 0:
            return None
        data = combo.currentData()
        if isinstance(data, dict):
            return data
        return None

    def _update_time_conversion_result(self, *_):
        from_unit = self._current_time_unit(self.time_from_unit_combo)
        to_unit = self._current_time_unit(self.time_to_unit_combo)

        if not from_unit or not to_unit:
            self.time_result_label.setText("Select units to convert.")
            self.time_base_label.setText("")
            self.time_note_label.setText("")
            self._last_time_result = None
            if hasattr(self, "copy_time_result_btn"):
                self.copy_time_result_btn.setEnabled(False)
            return

        raw_value = self.time_value_input.text().strip()
        if not raw_value:
            self.time_result_label.setText("Enter a value to convert.")
            self.time_base_label.setText("")
            self.time_note_label.setText("")
            self._last_time_result = None
            if hasattr(self, "copy_time_result_btn"):
                self.copy_time_result_btn.setEnabled(False)
            return

        try:
            value = parse_measure_value(raw_value)
        except ValueError:
            self.time_result_label.setText("Invalid number.")
            self.time_base_label.setText("")
            self.time_note_label.setText("")
            self._last_time_result = None
            if hasattr(self, "copy_time_result_btn"):
                self.copy_time_result_btn.setEnabled(False)
            return

        try:
            result = convert_between_units(value, from_unit, to_unit)
        except ValueError:
            self.time_result_label.setText("Conversion error.")
            self.time_base_label.setText("")
            self.time_note_label.setText("")
            self._last_time_result = None
            if hasattr(self, "copy_time_result_btn"):
                self.copy_time_result_btn.setEnabled(False)
            return

        result_text = f"{result.input_value:g} {result.from_name} = {result.converted_value:.6g} {result.to_name}"
        self.time_result_label.setText(result_text)

        base_text = f"Base: {result.base_value:.6g} {result.base_unit}"
        self.time_base_label.setText(base_text)

        note = from_unit.get("note") or to_unit.get("note")
        self.time_note_label.setText(str(note) if note else "")

        self._last_time_result = {
            "value": result.input_value,
            "from": from_unit,
            "to": to_unit,
            "si_value": result.base_value,
            "converted": result.converted_value,
            "copy_text": f"{result.converted_value:.6g} {result.to_name}",
        }
        if hasattr(self, "copy_time_result_btn"):
            self.copy_time_result_btn.setEnabled(True)

    # ==================== BASE CONVERTER TAB ====================

    def _build_base_converter_tab(self) -> QWidget:
        """Build a comprehensive number base converter tab."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Number Base Converter")
        header.setStyleSheet("font-size: 15pt; font-weight: 700; color: #e2e8f0;")
        layout.addWidget(header)

        subtitle = QLabel("Convert between any bases (2-36), including binary, octal, decimal, hex, and ternary.")
        subtitle.setStyleSheet("color: #cbd5e1; font-size: 10pt;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Input value
        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        input_label = QLabel("Value:")
        input_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.base_input = QLineEdit()
        self.base_input.setPlaceholderText("Enter a number (e.g., 255, FF, 11111111)")
        self.base_input.textChanged.connect(self._update_base_conversion)
        self.base_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 10px 10px;
                font-size: 12pt;
                font-family: monospace;
            }
            """
        )
        input_row.addWidget(input_label)
        input_row.addWidget(self.base_input, 1)
        layout.addLayout(input_row)

        # From base selector
        from_row = QHBoxLayout()
        from_row.setSpacing(8)
        from_label = QLabel("From Base:")
        from_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.from_base_combo = QComboBox()
        self._populate_base_combo(self.from_base_combo)
        self.from_base_combo.setCurrentText("10 - Decimal")
        self.from_base_combo.currentIndexChanged.connect(self._update_base_conversion)
        from_row.addWidget(from_label)
        from_row.addWidget(self.from_base_combo, 1)
        layout.addLayout(from_row)

        # Results display
        results_label = QLabel("Conversions:")
        results_label.setStyleSheet("color: #e2e8f0; font-weight: 600; margin-top: 8px;")
        layout.addWidget(results_label)

        self.base_results_list = QListWidget()
        self.base_results_list.setStyleSheet(
            """
            QListWidget {
                background: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 8px;
                font-family: monospace;
                font-size: 11pt;
            }
            QListWidget::item {
                padding: 4px 0;
            }
            QListWidget::item:selected {
                background: #334155;
            }
            """
        )
        self.base_results_list.setMinimumHeight(200)
        layout.addWidget(self.base_results_list)

        # Copy button
        copy_btn = QPushButton("Copy Selected")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setProperty("archetype", "scribe")
        copy_btn.clicked.connect(self._copy_base_result)
        layout.addWidget(copy_btn)

        # Balanced ternary section
        bt_label = QLabel("Balanced Ternary:")
        bt_label.setStyleSheet("color: #e2e8f0; font-weight: 600; margin-top: 8px;")
        layout.addWidget(bt_label)

        self.balanced_ternary_result = QLabel("Enter a number above")
        self.balanced_ternary_result.setStyleSheet("color: #cbd5e1; font-size: 11pt; font-family: monospace;")
        self.balanced_ternary_result.setWordWrap(True)
        layout.addWidget(self.balanced_ternary_result)

        layout.addStretch()
        return container

    def _populate_base_combo(self, combo: QComboBox) -> None:
        """Populate a combo box with common bases."""
        common_bases = [
            (2, "Binary"),
            (3, "Ternary"),
            (8, "Octal"),
            (10, "Decimal"),
            (12, "Duodecimal"),
            (16, "Hexadecimal"),
            (20, "Vigesimal"),
            (36, "Base-36"),
            (60, "Sexagesimal"),
        ]
        for base, name in common_bases:
            if base <= 36:
                combo.addItem(f"{base} - {name}", base)
            else:
                combo.addItem(f"{base} - {name} (special)", base)
        # Add all other bases
        for b in range(2, 37):
            if b not in [cb[0] for cb in common_bases]:
                combo.addItem(f"{b}", b)

    def _int_to_base(self, n: int, base: int) -> str:
        """Convert an integer to a string in the given base (2-36)."""
        if n == 0:
            return "0"
        if base < 2 or base > 36:
            return "?"
        negative = n < 0
        n = abs(n)
        digits = []
        while n:
            digits.append(BASE_DIGITS[n % base])
            n //= base
        if negative:
            digits.append("-")
        return "".join(reversed(digits))

    def _int_from_base(self, s: str, base: int) -> int:
        """Convert a string in the given base to an integer."""
        s = s.strip().upper()
        if not s:
            raise ValueError("Empty input")
        negative = s.startswith("-")
        if negative:
            s = s[1:]
        result = 0
        for char in s:
            if char not in BASE_DIGITS[:base]:
                raise ValueError(f"Invalid digit '{char}' for base {base}")
            result = result * base + BASE_DIGITS.index(char)
        return -result if negative else result

    def _int_to_balanced_ternary(self, n: int) -> str:
        """Convert an integer to balanced ternary (using T for -1, 0, 1)."""
        if n == 0:
            return "0"
        digits = []
        negative = n < 0
        n = abs(n)
        while n:
            rem = n % 3
            if rem == 0:
                digits.append("0")
            elif rem == 1:
                digits.append("1")
            else:  # rem == 2
                digits.append("T")  # T represents -1
                n += 1
            n //= 3
        result = "".join(reversed(digits))
        if negative:
            # Negate: swap 1 and T
            result = result.translate(str.maketrans("1T", "T1"))
        return result

    def _update_base_conversion(self, *_) -> None:
        """Update all base conversion results."""
        self.base_results_list.clear()
        self.balanced_ternary_result.setText("")

        input_text = self.base_input.text().strip()
        if not input_text:
            return

        from_base = self.from_base_combo.currentData()
        if not isinstance(from_base, int):
            return

        try:
            value = self._int_from_base(input_text, from_base)
        except ValueError as e:
            self.base_results_list.addItem(f"Error: {e}")
            return

        # Show conversions to common bases
        conversions = [
            (2, "Binary"),
            (3, "Ternary"),
            (8, "Octal"),
            (10, "Decimal"),
            (12, "Duodecimal"),
            (16, "Hexadecimal"),
            (36, "Base-36"),
        ]
        for base, name in conversions:
            converted = self._int_to_base(value, base)
            self.base_results_list.addItem(f"{name} (base {base}): {converted}")

        # Balanced ternary
        bt = self._int_to_balanced_ternary(value)
        self.balanced_ternary_result.setText(f"Balanced Ternary: {bt}  (T=-1, 0, 1)")

    def _copy_base_result(self) -> None:
        """Copy the selected base conversion result."""
        item = self.base_results_list.currentItem()
        if item:
            text = item.text()
            # Extract just the converted value
            if ": " in text:
                text = text.split(": ", 1)[1]
            clipboard = QGuiApplication.clipboard()
            if clipboard:
                clipboard.setText(text)

    # ==================== PHYSICAL CONSTANTS TAB ====================

    def _build_constants_tab(self) -> QWidget:
        """Build a physical constants reference tab."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Physical Constants")
        header.setStyleSheet("font-size: 15pt; font-weight: 700; color: #e2e8f0;")
        layout.addWidget(header)

        subtitle = QLabel("Reference values for fundamental, astronomical, and mathematical constants.")
        subtitle.setStyleSheet("color: #cbd5e1; font-size: 10pt;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Category filter
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        filter_label = QLabel("Category:")
        filter_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.constants_category_combo = QComboBox()
        self.constants_category_combo.addItem("All Categories", None)
        categories = sorted(set(c.get("category", "Other") for c in PHYSICAL_CONSTANTS))
        for cat in categories:
            self.constants_category_combo.addItem(str(cat), cat)
        self.constants_category_combo.currentIndexChanged.connect(self._filter_constants)
        filter_row.addWidget(filter_label)
        filter_row.addWidget(self.constants_category_combo, 1)
        layout.addLayout(filter_row)

        # Search
        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        search_label = QLabel("Search:")
        search_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.constants_search = QLineEdit()
        self.constants_search.setPlaceholderText("Search constants...")
        self.constants_search.textChanged.connect(self._filter_constants)
        self.constants_search.setStyleSheet(
            """
            QLineEdit {
                background-color: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 8px;
                font-size: 11pt;
            }
            """
        )
        search_row.addWidget(search_label)
        search_row.addWidget(self.constants_search, 1)
        layout.addLayout(search_row)

        # Constants list
        self.constants_list = QListWidget()
        self.constants_list.setStyleSheet(
            """
            QListWidget {
                background: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 8px;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 6px 4px;
                border-bottom: 1px solid #1e293b;
            }
            QListWidget::item:selected {
                background: #334155;
            }
            """
        )
        self.constants_list.currentItemChanged.connect(self._show_constant_detail)
        self.constants_list.itemDoubleClicked.connect(self._insert_constant_to_calc)
        layout.addWidget(self.constants_list)

        # Detail display
        self.constant_detail = QLabel("Select a constant to see details.")
        self.constant_detail.setWordWrap(True)
        self.constant_detail.setStyleSheet(
            """
            QLabel {
                background: #1e293b;
                color: #e2e8f0;
                border-radius: 8px;
                padding: 12px;
                font-size: 10pt;
            }
            """
        )
        self.constant_detail.setMinimumHeight(80)
        layout.addWidget(self.constant_detail)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        # Insert to calculator button
        insert_btn = QPushButton("Insert to Calculator")
        insert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        insert_btn.setProperty("archetype", "magus")
        insert_btn.clicked.connect(self._insert_constant_to_calc)
        btn_row.addWidget(insert_btn)

        # Copy button
        copy_btn = QPushButton("Copy Value")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setProperty("archetype", "scribe")
        copy_btn.clicked.connect(self._copy_constant_value)
        btn_row.addWidget(copy_btn)

        layout.addLayout(btn_row)

        self._filter_constants()
        return container

    def _filter_constants(self, *_) -> None:
        """Filter constants by category and search term."""
        self.constants_list.clear()
        category = self.constants_category_combo.currentData()
        search = self.constants_search.text().strip().lower()

        for const in PHYSICAL_CONSTANTS:
            if category and const.get("category") != category:
                continue
            name = str(const.get("name", ""))
            symbol = str(const.get("symbol", ""))
            if search and search not in name.lower() and search not in symbol.lower():
                continue
            item = QListWidgetItem(f"{const.get('symbol', '')}  {name}")
            item.setData(Qt.ItemDataRole.UserRole, const)
            self.constants_list.addItem(item)

    def _show_constant_detail(self, current, previous) -> None:  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """Display details for the selected constant."""
        if not current:
            self.constant_detail.setText("Select a constant to see details.")
            return
        const = current.data(Qt.ItemDataRole.UserRole)
        if not isinstance(const, dict):
            return

        value = const.get("value", 0)
        # Format value nicely
        if isinstance(value, float):
            if abs(value) < 0.001 or abs(value) > 1e6:
                value_str = f"{value:.10e}"
            else:
                value_str = f"{value:.10g}"
        else:
            value_str = str(value)

        detail = f"<b>{const.get('name', '')}</b><br>"
        detail += f"Symbol: <b>{const.get('symbol', '')}</b><br>"
        detail += f"Value: <b>{value_str}</b> {const.get('unit', '')}<br>"
        if const.get("note"):
            detail += f"<i>{const.get('note')}</i>"
        self.constant_detail.setText(detail)

    def _copy_constant_value(self) -> None:
        """Copy the selected constant's value."""
        item = self.constants_list.currentItem()
        if not item:
            return
        const = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(const, dict):
            return
        value = const.get("value", 0)
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(str(value))

    def _insert_constant_to_calc(self) -> None:
        """Insert the selected constant's value into the calculator."""
        item = self.constants_list.currentItem()
        if not item:
            return
        const = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(const, dict):
            return
        value = const.get("value", 0)
        # Insert into calculator display
        if hasattr(self, "display"):
            current = self.display.text()
            self.display.setText(current + str(value))
            # Switch to calculator tab
            if hasattr(self, "sidebar"):
                self.sidebar.setCurrentRow(0)

    # ==================== SACRED GEOMETRY TAB ====================

    def _build_sacred_geometry_tab(self) -> QWidget:
        """Build a sacred geometry constants and ratios tab."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Sacred Geometry")
        header.setStyleSheet("font-size: 15pt; font-weight: 700; color: #e2e8f0;")
        layout.addWidget(header)

        subtitle = QLabel("Golden ratio, metallic means, Platonic solids, and geometric proportions.")
        subtitle.setStyleSheet("color: #cbd5e1; font-size: 10pt;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Category filter
        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)
        filter_label = QLabel("Category:")
        filter_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.sacred_category_combo = QComboBox()
        self.sacred_category_combo.addItem("All Categories", None)
        categories = sorted(set(c.get("category", "Other") for c in SACRED_GEOMETRY))
        for cat in categories:
            self.sacred_category_combo.addItem(str(cat), cat)
        self.sacred_category_combo.currentIndexChanged.connect(self._filter_sacred)
        filter_row.addWidget(filter_label)
        filter_row.addWidget(self.sacred_category_combo, 1)
        layout.addLayout(filter_row)

        # Ratios list
        self.sacred_list = QListWidget()
        self.sacred_list.setStyleSheet(
            """
            QListWidget {
                background: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 8px;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 6px 4px;
                border-bottom: 1px solid #1e293b;
            }
            QListWidget::item:selected {
                background: #334155;
            }
            """
        )
        self.sacred_list.currentItemChanged.connect(self._show_sacred_detail)
        self.sacred_list.itemDoubleClicked.connect(self._insert_sacred_to_calc)
        layout.addWidget(self.sacred_list)

        # Detail display
        self.sacred_detail = QLabel("Select a ratio to see details.")
        self.sacred_detail.setWordWrap(True)
        self.sacred_detail.setStyleSheet(
            """
            QLabel {
                background: #1e293b;
                color: #e2e8f0;
                border-radius: 8px;
                padding: 12px;
                font-size: 10pt;
            }
            """
        )
        self.sacred_detail.setMinimumHeight(80)
        layout.addWidget(self.sacred_detail)

        # Fibonacci calculator
        fib_header = QLabel("Fibonacci Sequence")
        fib_header.setStyleSheet("color: #e2e8f0; font-weight: 600; margin-top: 8px;")
        layout.addWidget(fib_header)

        fib_row = QHBoxLayout()
        fib_row.setSpacing(8)
        fib_label = QLabel("F(n):")
        fib_label.setStyleSheet("color: #e2e8f0;")
        self.fib_input = QLineEdit()
        self.fib_input.setPlaceholderText("Enter n (0-100)")
        self.fib_input.textChanged.connect(self._calculate_fibonacci)
        self.fib_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 8px;
                font-size: 11pt;
            }
            """
        )
        self.fib_input.setMaximumWidth(100)
        self.fib_result = QLabel("")
        self.fib_result.setStyleSheet("color: #cbd5e1; font-size: 11pt;")
        self.fib_result.setWordWrap(True)
        fib_row.addWidget(fib_label)
        fib_row.addWidget(self.fib_input)
        fib_row.addWidget(self.fib_result, 1)
        layout.addLayout(fib_row)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        # Insert to calculator button
        insert_btn = QPushButton("Insert to Calculator")
        insert_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        insert_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #059669;
                color: #e2e8f0;
                border: 1px solid #047857;
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #10b981; }
            QPushButton:pressed { background-color: #047857; }
            """
        )
        insert_btn.clicked.connect(self._insert_sacred_to_calc)
        btn_row.addWidget(insert_btn)

        # Copy button
        copy_btn = QPushButton("Copy Value")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #334155;
                color: #e2e8f0;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #475569; }
            QPushButton:pressed { background-color: #0b1729; }
            """
        )
        copy_btn.clicked.connect(self._copy_sacred_value)
        btn_row.addWidget(copy_btn)

        layout.addLayout(btn_row)

        layout.addStretch()
        self._filter_sacred()
        return container

    def _filter_sacred(self, *_) -> None:
        """Filter sacred geometry entries by category."""
        self.sacred_list.clear()
        category = self.sacred_category_combo.currentData()

        for entry in SACRED_GEOMETRY:
            if category and entry.get("category") != category:
                continue
            name = str(entry.get("name", ""))
            symbol = str(entry.get("symbol", ""))
            value = entry.get("value", 0)
            item = QListWidgetItem(f"{symbol}  {name} = {value:.10g}")
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.sacred_list.addItem(item)

    def _show_sacred_detail(self, current, previous) -> None:  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """Display details for the selected sacred geometry entry."""
        if not current:
            self.sacred_detail.setText("Select a ratio to see details.")
            return
        entry = current.data(Qt.ItemDataRole.UserRole)
        if not isinstance(entry, dict):
            return

        value = entry.get("value", 0)
        detail = f"<b>{entry.get('name', '')}</b><br>"
        detail += f"Symbol: <b>{entry.get('symbol', '')}</b><br>"
        detail += f"Value: <b>{value:.15g}</b><br>"
        detail += f"Category: {entry.get('category', '')}<br>"
        if entry.get("note"):
            detail += f"<i>{entry.get('note')}</i>"
        self.sacred_detail.setText(detail)

    def _calculate_fibonacci(self, *_) -> None:
        """Calculate Fibonacci number F(n)."""
        text = self.fib_input.text().strip()
        if not text:
            self.fib_result.setText("")
            return
        try:
            n = int(text)
            if n < 0:
                self.fib_result.setText("n must be non-negative")
                return
            if n > 1000:
                self.fib_result.setText("n too large (max 1000)")
                return
            # Calculate Fibonacci
            a, b = 0, 1
            for _ in range(n):
                a, b = b, a + b
            # Also show ratio approaching phi
            if n >= 2:
                ratio = b / a if a != 0 else 0
                self.fib_result.setText(f"F({n}) = {a}    (F({n})/F({n-1}) = {ratio:.10g} → φ)")
            else:
                self.fib_result.setText(f"F({n}) = {a}")
        except ValueError:
            self.fib_result.setText("Invalid number")

    def _copy_sacred_value(self) -> None:
        """Copy the selected sacred geometry value."""
        item = self.sacred_list.currentItem()
        if not item:
            return
        entry = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(entry, dict):
            return
        value = entry.get("value", 0)
        clipboard = QGuiApplication.clipboard()
        if clipboard:
            clipboard.setText(str(value))

    def _insert_sacred_to_calc(self) -> None:
        """Insert the selected sacred geometry value into the calculator."""
        item = self.sacred_list.currentItem()
        if not item:
            return
        entry = item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(entry, dict):
            return
        value = entry.get("value", 0)
        # Insert into calculator display
        if hasattr(self, "display"):
            current = self.display.text()
            self.display.setText(current + str(value))
            # Switch to calculator tab
            if hasattr(self, "sidebar"):
                self.sidebar.setCurrentRow(0)

    # ==================== COORDINATES TAB ====================

    def _build_coordinates_tab(self) -> QWidget:
        """Build a stellar/celestial coordinates conversion tab."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Stellar Coordinates")
        header.setStyleSheet("font-size: 15pt; font-weight: 700; color: #e2e8f0;")
        layout.addWidget(header)

        subtitle = QLabel("Convert between angle formats and explore coordinate systems.")
        subtitle.setStyleSheet("color: #cbd5e1; font-size: 10pt;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # === Angle Format Conversion Section ===
        angle_header = QLabel("Angle Format Conversion")
        angle_header.setStyleSheet("color: #e2e8f0; font-weight: 600; margin-top: 8px;")
        layout.addWidget(angle_header)

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(8)
        self.coord_angle_input = QLineEdit()
        self.coord_angle_input.setPlaceholderText("Enter angle (e.g., 45.5, 45°30'0\", 12h30m, 15♈23)")
        self.coord_angle_input.textChanged.connect(self._update_angle_conversions)
        self.coord_angle_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 10px;
                font-size: 11pt;
            }
            """
        )
        input_row.addWidget(self.coord_angle_input, 1)
        layout.addLayout(input_row)

        # Format selector
        format_row = QHBoxLayout()
        format_row.setSpacing(8)
        format_label = QLabel("Input Format:")
        format_label.setStyleSheet("color: #e2e8f0;")
        self.coord_format_combo = QComboBox()
        self.coord_format_combo.addItem("Decimal Degrees", "decimal")
        self.coord_format_combo.addItem("Degrees°Minutes'Seconds\"", "dms")
        self.coord_format_combo.addItem("Hours:Minutes:Seconds", "hms")
        self.coord_format_combo.addItem("Radians", "radians")
        self.coord_format_combo.addItem("Zodiacal (e.g., 15♈23)", "zodiacal")
        self.coord_format_combo.currentIndexChanged.connect(self._update_angle_conversions)
        format_row.addWidget(format_label)
        format_row.addWidget(self.coord_format_combo, 1)
        layout.addLayout(format_row)

        # Results display
        self.coord_results_list = QListWidget()
        self.coord_results_list.setStyleSheet(
            """
            QListWidget {
                background: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 8px;
                font-family: monospace;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 4px 0;
            }
            QListWidget::item:selected {
                background: #334155;
            }
            """
        )
        self.coord_results_list.setMaximumHeight(150)
        layout.addWidget(self.coord_results_list)

        # === Coordinate Systems Reference ===
        sys_header = QLabel("Coordinate Systems Reference")
        sys_header.setStyleSheet("color: #e2e8f0; font-weight: 600; margin-top: 12px;")
        layout.addWidget(sys_header)

        self.coord_sys_list = QListWidget()
        self.coord_sys_list.setStyleSheet(
            """
            QListWidget {
                background: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 8px;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 6px 4px;
                border-bottom: 1px solid #1e293b;
            }
            QListWidget::item:selected {
                background: #334155;
            }
            """
        )
        self.coord_sys_list.currentItemChanged.connect(self._show_coord_system_detail)
        for sys in COORDINATE_SYSTEMS:
            item = QListWidgetItem(f"{sys['name']}")
            item.setData(Qt.ItemDataRole.UserRole, sys)
            self.coord_sys_list.addItem(item)
        layout.addWidget(self.coord_sys_list)

        # Detail display
        self.coord_sys_detail = QLabel("Select a coordinate system to see details.")
        self.coord_sys_detail.setWordWrap(True)
        self.coord_sys_detail.setStyleSheet(
            """
            QLabel {
                background: #1e293b;
                color: #e2e8f0;
                border-radius: 8px;
                padding: 12px;
                font-size: 10pt;
            }
            """
        )
        self.coord_sys_detail.setMinimumHeight(80)
        layout.addWidget(self.coord_sys_detail)

        # Copy button
        copy_btn = QPushButton("Copy Selected")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #334155;
                color: #e2e8f0;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #475569; }
            QPushButton:pressed { background-color: #0b1729; }
            """
        )
        copy_btn.clicked.connect(self._copy_coord_result)
        layout.addWidget(copy_btn)

        layout.addStretch()
        return container

    # ==================== GEOMETRY SOLVER TAB ====================

    def _build_geometry_solver_tab(self) -> QWidget:
        """Build a dynamic regular polygon solver."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Regular Polygon Solver")
        header.setStyleSheet("font-size: 15pt; font-weight: 700; color: #e2e8f0;")
        layout.addWidget(header)

        subtitle = QLabel("Calculate dimensions for any regular N-gon.")
        subtitle.setStyleSheet("color: #cbd5e1; font-size: 10pt;")
        layout.addWidget(subtitle)

        # Polygon Selector
        poly_row = QHBoxLayout()
        poly_label = QLabel("Shape:")
        poly_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.geo_poly_combo = QComboBox()
        polygons = [
            (3, "Triangle (3)"), (4, "Square (4)"), (5, "Pentagon (5)"),
            (6, "Hexagon (6)"), (7, "Heptagon (7)"), (8, "Octagon (8)"),
            (9, "Nonagon (9)"), (10, "Decagon (10)"), (12, "Dodecagon (12)"),
            (0, "Custom N...")
        ]
        for sides, name in polygons:
            self.geo_poly_combo.addItem(name, sides)
        self.geo_poly_combo.setCurrentIndex(4) # Default to Heptagon
        self.geo_poly_combo.currentIndexChanged.connect(self._update_geometry_solver)
        
        # Custom N input (hidden by default)
        self.geo_custom_n = QLineEdit()
        self.geo_custom_n.setPlaceholderText("N")
        self.geo_custom_n.setMaximumWidth(60)
        self.geo_custom_n.setVisible(False)
        self.geo_custom_n.textChanged.connect(self._update_geometry_solver)
        self.geo_custom_n.setStyleSheet("background-color: #0b1220; color: #e2e8f0; border: 1px solid #1f2937; border-radius: 4px; padding: 4px;")

        poly_row.addWidget(poly_label)
        poly_row.addWidget(self.geo_poly_combo, 1)
        poly_row.addWidget(self.geo_custom_n)
        layout.addLayout(poly_row)

        # Input Parameter Selector
        param_row = QHBoxLayout()
        param_label = QLabel("Known:")
        param_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.geo_param_combo = QComboBox()
        self.geo_param_combo.addItem("Edge Length (s)", "edge")
        self.geo_param_combo.addItem("Circumradius (R)", "R")
        self.geo_param_combo.addItem("Inradius/Apothem (r)", "r")
        self.geo_param_combo.addItem("Area (A)", "area")
        self.geo_param_combo.currentIndexChanged.connect(self._update_geometry_solver)
        
        param_row.addWidget(param_label)
        param_row.addWidget(self.geo_param_combo, 1)
        layout.addLayout(param_row)

        # Value Input
        val_row = QHBoxLayout()
        val_label = QLabel("Value:")
        val_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.geo_value_input = QLineEdit()
        self.geo_value_input.setPlaceholderText("Enter value...")
        self.geo_value_input.textChanged.connect(self._update_geometry_solver)
        self.geo_value_input.setStyleSheet("""
            QLineEdit {
                background-color: #0b1220; color: #e2e8f0; 
                border: 1px solid #1f2937; border-radius: 8px; padding: 10px; font-size: 11pt;
            }
        """)
        val_row.addWidget(val_label)
        val_row.addWidget(self.geo_value_input, 1)
        layout.addLayout(val_row)

        layout.addSpacing(10)

        # Results Display
        self.geo_result_list = QListWidget()
        self.geo_result_list.setStyleSheet("""
            QListWidget {
                background: #0b1220; color: #e2e8f0;
                border: 1px solid #1f2937; border-radius: 8px; padding: 8px; font-family: monospace; font-size: 11pt;
            }
            QListWidget::item { padding: 4px; }
            QListWidget::item:selected { background: #1f2937; }
        """)
        # Double click to insert result
        self.geo_result_list.itemDoubleClicked.connect(self._insert_geo_result_to_calc)
        layout.addWidget(self.geo_result_list)

        # Info Label
        self.geo_info = QLabel("")
        self.geo_info.setWordWrap(True)
        self.geo_info.setStyleSheet("color: #64748b; font-size: 9pt; font-style: italic;")
        layout.addWidget(self.geo_info)

        return container

    def _update_geometry_solver(self, *_) -> None:
        """Calculate polygon properties."""
        # Get N
        n_data = self.geo_poly_combo.currentData()
        if n_data == 0:
            self.geo_custom_n.setVisible(True)
            try:
                n = int(self.geo_custom_n.text().strip())
                if n < 3: raise ValueError
            except:
                self.geo_result_list.clear()
                self.geo_info.setText("Enter valid N ≥ 3")
                return
        else:
            self.geo_custom_n.setVisible(False)
            n = n_data

        # Get Value
        try:
            val = float(self.geo_value_input.text().strip())
            if val <= 0: raise ValueError
        except:
            self.geo_result_list.clear()
            self.geo_info.setText("Enter valid positive number")
            return

        # Solve
        mode = self.geo_param_combo.currentData()
        pi_n = math.pi / n
        
        # Solving for Edge (s) first as common base
        s = 0.0
        if mode == "edge":
            s = val
        elif mode == "R":
            # R = s / (2 * sin(pi/n))  => s = R * 2 * sin(pi/n)
            s = val * 2 * math.sin(pi_n)
        elif mode == "r":
            # r = s / (2 * tan(pi/n))  => s = r * 2 * tan(pi/n)
            s = val * 2 * math.tan(pi_n)
        elif mode == "area":
            # A = (n * s^2) / (4 * tan(pi/n)) => s = sqrt( (4 * A * tan(pi/n)) / n )
            s = math.sqrt((4 * val * math.tan(pi_n)) / n)

        # Calculate others from s
        # R = s / (2 * sin(pi/n))
        R = s / (2 * math.sin(pi_n))
        # r = s / (2 * tan(pi/n))
        r = s / (2 * math.tan(pi_n))
        # Area
        area = (n * s**2) / (4 * math.tan(pi_n))
        # Perimeter
        P = n * s
        # Interior Angle
        angle = (n - 2) * 180 / n

        # Display
        self.geo_result_list.clear()
        
        def add(label, v, key):
            item = QListWidgetItem(f"{label:<20} : {v:.6g}")
            item.setData(Qt.ItemDataRole.UserRole, v)
            self.geo_result_list.addItem(item)

        add(f"Edge Length (s)", s, "s")
        add(f"Perimeter (P)", P, "P")
        add(f"Circumradius (R)", R, "R")
        add(f"Inradius/Apoth (r)", r, "r")
        add(f"Area (A)", area, "A")
        add(f"Interior Angle", angle, "deg")

        self.geo_info.setText(f"Calculated for regular {n}-gon.")

    def _insert_geo_result_to_calc(self, item: QListWidgetItem) -> None:
        """Insert solved geometry value into calculator."""
        val = item.data(Qt.ItemDataRole.UserRole)
        if val is None: return
        
        if hasattr(self, "display"):
            current = self.display.text()
            self.display.setText(current + f"{val:.6g}")
            if hasattr(self, "sidebar"):
                self.sidebar.setCurrentRow(0)

    def _parse_angle_input(self, text: str, fmt: str) -> Optional[float]:
        """Parse angle input and return decimal degrees."""
        text = text.strip()
        if not text:
            return None

        try:
            if fmt == "decimal":
                return float(text)

            elif fmt == "radians":
                return float(text) * 180.0 / math.pi

            elif fmt == "dms":
                # Parse formats like: 45°30'15", 45 30 15, 45:30:15
                # Remove degree symbols and normalize
                text = text.replace('°', ' ').replace("'", ' ').replace('"', ' ').replace(':', ' ')
                parts = text.split()
                d = float(parts[0]) if len(parts) > 0 else 0
                m = float(parts[1]) if len(parts) > 1 else 0
                s = float(parts[2]) if len(parts) > 2 else 0
                sign = -1 if d < 0 else 1
                return sign * (abs(d) + m / 60.0 + s / 3600.0)

            elif fmt == "hms":
                # Parse formats like: 12h30m15s, 12:30:15, 12 30 15
                text = text.lower().replace('h', ' ').replace('m', ' ').replace('s', ' ').replace(':', ' ')
                parts = text.split()
                h = float(parts[0]) if len(parts) > 0 else 0
                m = float(parts[1]) if len(parts) > 1 else 0
                s = float(parts[2]) if len(parts) > 2 else 0
                # Convert hours to degrees (1h = 15°)
                return (h + m / 60.0 + s / 3600.0) * 15.0

            elif fmt == "zodiacal":
                # Parse formats like: 15♈23, 15Ari23, 15°♈23'
                # Find zodiac sign
                for i, (symbol, name) in enumerate(ZODIAC_SIGNS):
                    if symbol in text or name[:3].lower() in text.lower():
                        # Extract degrees and minutes
                        cleaned = text.replace(symbol, ' ').replace('°', ' ').replace("'", ' ')
                        for n in [name, name[:3], name[:3].lower(), name[:3].upper()]:
                            cleaned = cleaned.replace(n, ' ')
                        parts = cleaned.split()
                        deg = float(parts[0]) if len(parts) > 0 else 0
                        mins = float(parts[1]) if len(parts) > 1 else 0
                        # Each sign is 30 degrees
                        return i * 30.0 + deg + mins / 60.0
                return None

        except (ValueError, IndexError):
            return None
        return None

    def _degrees_to_dms(self, deg: float) -> str:
        """Convert decimal degrees to DMS string."""
        sign = "-" if deg < 0 else ""
        deg = abs(deg)
        d = int(deg)
        m = int((deg - d) * 60)
        s = (deg - d - m / 60.0) * 3600
        return f"{sign}{d}°{m:02d}'{s:05.2f}\""

    def _degrees_to_hms(self, deg: float) -> str:
        """Convert decimal degrees to HMS string (for RA)."""
        hours = deg / 15.0
        h = int(hours)
        remainder = (hours - h) * 60
        m = int(remainder)
        s = (remainder - m) * 60
        # Handle rounding edge case
        if s >= 59.995:
            s = 0
            m += 1
            if m >= 60:
                m = 0
                h += 1
        return f"{h:02d}h{m:02d}m{s:05.2f}s"

    def _degrees_to_zodiacal(self, deg: float) -> str:
        """Convert decimal degrees to zodiacal notation."""
        deg = deg % 360.0
        sign_idx = int(deg / 30.0)
        sign_deg = deg - sign_idx * 30.0
        d = int(sign_deg)
        m = int((sign_deg - d) * 60)
        symbol, _name = ZODIAC_SIGNS[sign_idx % 12]
        return f"{d}°{symbol}{m:02d}'"

    def _update_angle_conversions(self, *_) -> None:
        """Update all angle format conversions."""
        self.coord_results_list.clear()

        text = self.coord_angle_input.text().strip()
        if not text:
            return

        fmt = self.coord_format_combo.currentData()
        degrees = self._parse_angle_input(text, fmt)

        if degrees is None:
            self.coord_results_list.addItem("Could not parse input. Check format.")
            return

        # Show all conversions
        self.coord_results_list.addItem(f"Decimal Degrees: {degrees:.8g}°")
        self.coord_results_list.addItem(f"DMS: {self._degrees_to_dms(degrees)}")
        self.coord_results_list.addItem(f"HMS (as RA): {self._degrees_to_hms(degrees)}")
        self.coord_results_list.addItem(f"Radians: {degrees * math.pi / 180.0:.10g}")
        self.coord_results_list.addItem(f"Zodiacal: {self._degrees_to_zodiacal(degrees)}")
        self.coord_results_list.addItem(f"Turns: {degrees / 360.0:.8g}")
        self.coord_results_list.addItem(f"Gradians: {degrees * 400.0 / 360.0:.8g}")

    def _show_coord_system_detail(self, current, previous) -> None:  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """Display details for the selected coordinate system."""
        if not current:
            self.coord_sys_detail.setText("Select a coordinate system to see details.")
            return
        sys = current.data(Qt.ItemDataRole.UserRole)
        if not isinstance(sys, dict):
            return

        coords = sys.get("coords", ("", ""))
        units = sys.get("units", ("", ""))

        detail = f"<b>{sys.get('name', '')}</b><br><br>"
        detail += "<b>Coordinates:</b><br>"
        detail += f"  • {coords[0]}: {units[0]}<br>"
        detail += f"  • {coords[1]}: {units[1]}<br><br>"
        detail += f"<i>{sys.get('note', '')}</i>"
        self.coord_sys_detail.setText(detail)

    def _copy_coord_result(self) -> None:
        """Copy the selected coordinate result."""
        item = self.coord_results_list.currentItem()
        if item:
            text = item.text()
            # Extract just the value after the colon
            if ": " in text:
                text = text.split(": ", 1)[1]
            clipboard = QGuiApplication.clipboard()
            if clipboard:
                clipboard.setText(text)

    def _restore_persisted_state(self) -> None:
        self._restoring_state = True
        try:
            state = load_state(self._state_path, max_history=DEFAULT_MAX_HISTORY)
            self._angle_mode = state.angle_mode
            self._memory = float(state.memory)
            if hasattr(self, "angle_mode_label"):
                self.angle_mode_label.setText(f"Mode: {self._angle_mode}")
            if hasattr(self, "history_list"):
                self.history_list.clear()
                for entry in (state.history or []):
                    self.history_list.addItem(QListWidgetItem(entry))
        finally:
            self._restoring_state = False

    def _persist_state(self) -> None:
        if getattr(self, "_restoring_state", False):
            return
        history: List[str] = []
        if hasattr(self, "history_list"):
            for i in range(self.history_list.count()):
                item = self.history_list.item(i)
                if item is not None:
                    history.append(item.text())
        state = CalculatorState(angle_mode=self._angle_mode, memory=self._memory, history=history)
        save_state(state, self._state_path, max_history=DEFAULT_MAX_HISTORY)

    def _on_history_double_clicked(self, item: QListWidgetItem) -> None:
        """Insert history result into calculator input."""
        text = item.text()
        val = text
        if "=" in text:
            # "expr = result" -> take result
            val = text.rsplit("=", 1)[1].strip()
            
        if hasattr(self, "display"):
            current = self.display.text()
            self.display.setText(current + val)

    def _build_calculator_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setStyleSheet(
            """
            QLineEdit {
                background-color: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 10px;
                padding: 14px 12px;
                font-size: 18pt;
                letter-spacing: 0.5px;
            }
            """
        )
        layout.addWidget(self.display)

        self.angle_mode_label = QLabel("Mode: RAD")
        self.angle_mode_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.angle_mode_label.setStyleSheet("color: #94a3b8; font-size: 9pt;")
        layout.addWidget(self.angle_mode_label)

        layout.addLayout(self._build_function_row())

        content_row = QHBoxLayout()
        content_row.setSpacing(12)
        content_row.addLayout(self._build_keypad(), 3)

        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self._on_history_double_clicked)
        self.history_list.setMinimumWidth(220)
        self.history_list.setStyleSheet(
            """
            QListWidget {
                background: #0b1220;
                border: 1px solid #1f2937;
                border-radius: 10px;
                padding: 6px;
                color: #e2e8f0;
            }
            QListWidget::item {
                padding: 6px;
            }
            QListWidget::item:selected {
                background: #1f2937;
            }
            """
        )
        self.history_list.itemClicked.connect(self._on_history_item_clicked)
        content_row.addWidget(self.history_list, 1)

        layout.addLayout(content_row)

        layout.addStretch()
        return container

    def _build_measures_tab(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Ancient Measures Conversion")
        header.setStyleSheet("font-size: 15pt; font-weight: 700; color: #e2e8f0;")
        layout.addWidget(header)

        subtitle = QLabel("Convert between ancient systems and modern metric baselines.")
        subtitle.setStyleSheet("color: #cbd5e1; font-size: 10pt;")
        layout.addWidget(subtitle)

        category_row = QHBoxLayout()
        category_row.setSpacing(8)
        category_label = QLabel("Category:")
        category_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.measure_category_combo = QComboBox()
        self.measure_category_combo.addItem("Length (meters)", "length")
        self.measure_category_combo.addItem("Mass (kilograms)", "mass")
        self.measure_category_combo.addItem("Volume (liters)", "volume")
        self.measure_category_combo.currentIndexChanged.connect(self._refresh_unit_combos)
        category_row.addWidget(category_label)
        category_row.addWidget(self.measure_category_combo, 1)
        layout.addLayout(category_row)

        from_row = QHBoxLayout()
        from_row.setSpacing(8)
        from_label = QLabel("From:")
        from_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.from_unit_combo = QComboBox()
        self.from_unit_combo.currentIndexChanged.connect(self._update_conversion_result)
        from_row.addWidget(from_label)
        from_row.addWidget(self.from_unit_combo, 1)
        layout.addLayout(from_row)

        to_row = QHBoxLayout()
        to_row.setSpacing(8)
        to_label = QLabel("To:")
        to_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.to_unit_combo = QComboBox()
        self.to_unit_combo.currentIndexChanged.connect(self._update_conversion_result)
        to_row.addWidget(to_label)
        to_row.addWidget(self.to_unit_combo, 1)

        swap_btn = QPushButton("Swap")
        swap_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        swap_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #1f2937;
                color: #e2e8f0;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #334155; }
            QPushButton:pressed { background-color: #0b1729; }
            """
        )
        swap_btn.clicked.connect(self._swap_measures_units)
        to_row.addWidget(swap_btn)
        layout.addLayout(to_row)

        value_row = QHBoxLayout()
        value_row.setSpacing(8)
        value_label = QLabel("Value:")
        value_label.setStyleSheet("color: #e2e8f0; font-weight: 600;")
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter a number")
        self.value_input.textChanged.connect(self._update_conversion_result)
        self.value_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #0b1220;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 8px;
                padding: 10px 10px;
                font-size: 12pt;
            }
            """
        )
        value_row.addWidget(value_label)
        value_row.addWidget(self.value_input, 1)
        layout.addLayout(value_row)

        self.result_label = QLabel("Enter a value to convert.")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("color: #cbd5e1; font-size: 11pt;")
        layout.addWidget(self.result_label)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)
        actions_row.addStretch(1)

        self.copy_result_btn = QPushButton("Copy Result")
        self.copy_result_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_result_btn.setEnabled(False)
        self.copy_result_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #334155;
                color: #e2e8f0;
                border: 1px solid #1e293b;
                border-radius: 8px;
                padding: 8px 10px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #475569; }
            QPushButton:pressed { background-color: #0b1729; }
            QPushButton:disabled { color: #94a3b8; background-color: #1f2937; }
            """
        )
        self.copy_result_btn.clicked.connect(self._copy_measures_result)
        actions_row.addWidget(self.copy_result_btn)
        layout.addLayout(actions_row)

        self.base_label = QLabel("")
        self.base_label.setStyleSheet("color: #94a3b8; font-size: 9pt;")
        layout.addWidget(self.base_label)

        self.note_label = QLabel("")
        self.note_label.setWordWrap(True)
        self.note_label.setStyleSheet("color: #94a3b8; font-size: 9pt; font-style: italic;")
        layout.addWidget(self.note_label)

        layout.addStretch()
        self._refresh_unit_combos()
        return container

    def _swap_measures_units(self) -> None:
        if not hasattr(self, "from_unit_combo") or not hasattr(self, "to_unit_combo"):
            return
        from_idx = self.from_unit_combo.currentIndex()
        to_idx = self.to_unit_combo.currentIndex()
        self.from_unit_combo.blockSignals(True)
        self.to_unit_combo.blockSignals(True)
        self.from_unit_combo.setCurrentIndex(to_idx)
        self.to_unit_combo.setCurrentIndex(from_idx)
        self.from_unit_combo.blockSignals(False)
        self.to_unit_combo.blockSignals(False)
        self._update_conversion_result()

    def _copy_measures_result(self) -> None:
        payload = self._last_measure_result
        if not isinstance(payload, dict):
            return
        text = payload.get("copy_text")
        if not isinstance(text, str) or not text:
            return
        clipboard = QGuiApplication.clipboard()
        if clipboard is not None:
            clipboard.setText(text)

    def _unit_options_for_category(self, category: str) -> List[Dict[str, object]]:
        if not category:
            return []
        return [u for u in MEASURE_UNITS if u.get("category") == category]

    def _refresh_unit_combos(self, *_):
        category = self.measure_category_combo.currentData()
        units = self._unit_options_for_category(category)
        units_sorted = sorted(
            units,
            key=lambda u: (0 if u.get("system") == "Metric" else 1, str(u.get("system")), str(u.get("name"))),
        )

        def populate(combo: QComboBox):
            """
            Populate logic.
            
            Args:
                combo: Description of combo.
            
            """
            combo.blockSignals(True)
            combo.clear()
            for unit in units_sorted:
                label = f"{unit.get('system')} - {unit.get('name')}"
                combo.addItem(label, unit)
            combo.blockSignals(False)

        populate(self.from_unit_combo)
        populate(self.to_unit_combo)

        if self.from_unit_combo.count() > 0:
            self.from_unit_combo.setCurrentIndex(0)
        if self.to_unit_combo.count() > 1:
            self.to_unit_combo.setCurrentIndex(1)
        elif self.to_unit_combo.count() > 0:
            self.to_unit_combo.setCurrentIndex(0)

        self._update_conversion_result()

    def _current_unit(self, combo: QComboBox) -> Optional[Dict[str, object]]:
        idx = combo.currentIndex()
        if idx < 0:
            return None
        data = combo.currentData()
        if isinstance(data, dict):
            return data
        return None

    def _update_conversion_result(self, *_):
        from_unit = self._current_unit(self.from_unit_combo)
        to_unit = self._current_unit(self.to_unit_combo)

        if not from_unit or not to_unit:
            self.result_label.setText("Select units to convert.")
            self.base_label.setText("")
            self.note_label.setText("")
            self._last_measure_result = None
            if hasattr(self, "copy_result_btn"):
                self.copy_result_btn.setEnabled(False)
            return

        raw_value = self.value_input.text().strip()
        if not raw_value:
            self.result_label.setText("Enter a value to convert.")
            self.base_label.setText("")
            self.note_label.setText("")
            self._last_measure_result = None
            if hasattr(self, "copy_result_btn"):
                self.copy_result_btn.setEnabled(False)
            return

        try:
            value = parse_measure_value(raw_value)
        except ValueError:
            self.result_label.setText("Invalid number.")
            self.base_label.setText("")
            self.note_label.setText("")
            self._last_measure_result = None
            if hasattr(self, "copy_result_btn"):
                self.copy_result_btn.setEnabled(False)
            return

        try:
            result = convert_between_units(value, from_unit, to_unit)
        except ValueError:
            self.result_label.setText("Conversion error.")
            self.base_label.setText("")
            self.note_label.setText("")
            self._last_measure_result = None
            if hasattr(self, "copy_result_btn"):
                self.copy_result_btn.setEnabled(False)
            return

        result_text = f"{result.input_value:g} {result.from_name} = {result.converted_value:.6g} {result.to_name}"
        self.result_label.setText(result_text)

        base_text = f"Base: {result.base_value:.6g} {result.base_unit}"
        self.base_label.setText(base_text)

        note = from_unit.get("note") or to_unit.get("note")
        self.note_label.setText(str(note) if note else "")

        self._last_measure_result = {
            "value": result.input_value,
            "from": from_unit,
            "to": to_unit,
            "si_value": result.base_value,
            "converted": result.converted_value,
            "copy_text": f"{result.converted_value:.6g} {result.to_name}",
        }
        if hasattr(self, "copy_result_btn"):
            self.copy_result_btn.setEnabled(True)

    def _build_function_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(8)
        buttons = [
            ("AC", self._clear, "#ef4444"),
            ("Back", self._backspace, "#334155"),
            ("DEG/RAD", self._toggle_angle_mode, "#334155"),
            ("MC", self._memory_clear, "#334155"),
            ("MR", self._memory_recall, "#334155"),
            ("M+", self._memory_add, "#334155"),
            ("M-", self._memory_subtract, "#334155"),
            ("(", lambda: self._append("("), "#1f2937"),
            (")", lambda: self._append(")"), "#1f2937"),
        ]
        for label, handler, color in buttons:
            row.addWidget(self._make_button(label, handler, color))
        return row

    def _toggle_angle_mode(self):
        self._angle_mode = "DEG" if self._angle_mode == "RAD" else "RAD"
        if hasattr(self, "angle_mode_label"):
            self.angle_mode_label.setText(f"Mode: {self._angle_mode}")
        self._persist_state()

    def _memory_clear(self):
        self._memory = 0.0
        self._persist_state()

    def _memory_recall(self):
        # Insert as a readable constant rather than pasting the numeric value.
        self._append("mem")

    def _memory_add(self):
        if self._last_answer is not None:
            self._memory += float(self._last_answer)
            self._persist_state()

    def _memory_subtract(self):
        if self._last_answer is not None:
            self._memory -= float(self._last_answer)
            self._persist_state()

    def _build_keypad(self) -> QGridLayout:
        grid = QGridLayout()
        grid.setSpacing(8)

        keys = [
            ("sin", 0, 0, lambda: self._append("sin(")),
            ("cos", 0, 1, lambda: self._append("cos(")),
            ("tan", 0, 2, lambda: self._append("tan(")),
            ("ln", 0, 3, lambda: self._append("log(")),
            ("log10", 0, 4, lambda: self._append("log10(")),
            ("ANS", 1, 0, lambda: self._append("ans")),
            ("MEM", 1, 5, lambda: self._append("mem")),
            ("deg", 1, 1, lambda: self._append("deg(")),
            ("rad", 1, 2, lambda: self._append("rad(")),
            ("x^2", 1, 3, lambda: self._append("**2")),
            ("sqrt", 1, 4, lambda: self._append("sqrt(")),
            ("7", 2, 0, lambda: self._append("7")),
            ("8", 2, 1, lambda: self._append("8")),
            ("9", 2, 2, lambda: self._append("9")),
            ("/", 2, 3, lambda: self._append("/")),
            ("^", 2, 4, lambda: self._append("^")),
            ("pi", 6, 0, lambda: self._append("pi")),
            ("e", 6, 1, lambda: self._append("e")),
            ("tau", 6, 2, lambda: self._append("tau")),
            ("4", 3, 0, lambda: self._append("4")),
            ("5", 3, 1, lambda: self._append("5")),
            ("6", 3, 2, lambda: self._append("6")),
            ("*", 3, 3, lambda: self._append("*")),
            ("!", 3, 4, self._append_factorial),
            ("1", 4, 0, lambda: self._append("1")),
            ("2", 4, 1, lambda: self._append("2")),
            ("3", 4, 2, lambda: self._append("3")),
            ("-", 4, 3, lambda: self._append("-")),
            ("mod", 4, 4, lambda: self._append("%")),
            ("0", 5, 0, lambda: self._append("0")),
            (".", 5, 1, lambda: self._append(".")),
            ("+/-", 5, 2, self._toggle_sign),
            ("+", 5, 3, lambda: self._append("+")),
            ("=", 5, 4, self._calculate),
        ]

        for label, row, col, handler in keys:
            if label == "=":
                btn = self._make_button(label, handler, "#10b981")
            elif label == "AC":
                btn = self._make_button(label, handler, "#ef4444")
            else:
                btn = self._make_button(label, handler, "#1f2937")
            grid.addWidget(btn, row, col)

        return grid

    def _append_factorial(self):
        text = self.display.text()
        if not text:
            self._append("factorial(")
            return

        idx = len(text) - 1
        while idx >= 0 and text[idx].isspace():
            idx -= 1
        if idx < 0:
            self._append("factorial(")
            return

        last = text[idx]
        if last.isdigit() or last == ")":
            self._append("!")
        else:
            self._append("factorial(")

    def _make_button(self, text: str, handler: Callable, bg_color: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg_color};
                color: #e2e8f0;
                border: 1px solid #1e293b;
                border-radius: 10px;
                padding: 10px;
                font-size: 12pt;
            }}
            QPushButton:hover {{
                background-color: #334155;
            }}
            QPushButton:pressed {{
                background-color: #0b1729;
            }}
            """
        )
        btn.clicked.connect(handler)
        return btn

    def _append(self, value: str):
        self.display.setText(self.display.text() + value)

    def _clear(self):
        self.display.clear()

    def _backspace(self):
        current = self.display.text()
        self.display.setText(_smart_backspace(current))

    def _toggle_sign(self):
        text = self.display.text()
        if not text:
            return

        # Toggle sign of the last numeric literal when possible; fall back to whole expression.
        idx = len(text) - 1
        while idx >= 0 and text[idx].isspace():
            idx -= 1
        if idx < 0:
            return


        has_digit = False
        while idx >= 0:
            ch = text[idx]
            if ch.isdigit():
                has_digit = True
                idx -= 1
                continue
            if ch == ".":
                idx -= 1
                continue
            break

        if has_digit:
            start = idx + 1
            if start > 0 and text[start - 1] == "-":
                before = text[start - 2] if start - 2 >= 0 else ""
                if start - 1 == 0 or before in "+-*/%(":
                    self.display.setText(text[: start - 1] + text[start:])
                    return
            self.display.setText(text[:start] + "-" + text[start:])
            return

        if text.startswith("-"):
            self.display.setText(text[1:])
        else:
            self.display.setText(f"-{text}")

    def _calculate(self):
        expression = self.display.text().strip()
        if not expression:
            return
        try:
            result = self._safe_eval(expression)
            # Avoid scientific notation for most results
            if isinstance(result, float):
                display_val = ("{0:.12g}".format(result)).rstrip("0").rstrip(".")
                self.display.setText(display_val)
            else:
                self.display.setText(str(result))
            if isinstance(result, (int, float)):
                self._last_answer = float(result)
            self._append_history(expression, result)
        except ValueError as exc:
            message = str(exc) or "Error"
            if "Invalid expression" in message:
                self.display.setText("Syntax Error")
            elif "Math domain error" in message:
                self.display.setText("Math Error")
            else:
                self.display.setText("Error")
        except Exception:
            self.display.setText("Error")

    def _append_history(self, expression: str, result):
        if not hasattr(self, "history_list"):
            return
        item_text = f"{expression} = {result}"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, {"expression": expression, "result": str(result)})
        self.history_list.insertItem(0, item)
        self._persist_state()

    def _on_history_item_clicked(self, item: QListWidgetItem):
        payload = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(payload, dict) and "result" in payload:
            self.display.setText(str(payload["result"]))

    def _safe_eval(self, expression: str):
        expression = _normalize_expression(expression)

        def _angle_to_radians(x: float) -> float:
            return math.radians(x) if self._angle_mode == "DEG" else x

        def sin_wrapped(x: float) -> float:
            """
            Sin wrapped logic.
            
            Args:
                x: Description of x.
            
            Returns:
                Result of sin_wrapped operation.
            """
            return math.sin(_angle_to_radians(x))

        def cos_wrapped(x: float) -> float:
            """
            Cos wrapped logic.
            
            Args:
                x: Description of x.
            
            Returns:
                Result of cos_wrapped operation.
            """
            return math.cos(_angle_to_radians(x))

        def tan_wrapped(x: float) -> float:
            """
            Tan wrapped logic.
            
            Args:
                x: Description of x.
            
            Returns:
                Result of tan_wrapped operation.
            """
            return math.tan(_angle_to_radians(x))

        allowed_funcs: Dict[str, Callable] = {
            "sin": sin_wrapped,
            "cos": cos_wrapped,
            "tan": tan_wrapped,
            "asin": math.asin,
            "acos": math.acos,
            "atan": math.atan,
            "sqrt": math.sqrt,
            "log": math.log,
            "log10": math.log10,
            "exp": math.exp,
            "floor": math.floor,
            "ceil": math.ceil,
            "pow": math.pow,
            "factorial": math.factorial,
            "gcd": math.gcd,
            "lcm": math.lcm,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "deg": math.degrees,
            "rad": math.radians,
        }
        allowed_consts: Dict[str, float] = {
            "pi": math.pi,
            "e": math.e,
            "tau": math.tau,
            "ans": float(self._last_answer) if self._last_answer is not None else 0.0,
            "mem": float(self._memory),
        }

        return _safe_math_eval(expression, allowed_funcs=allowed_funcs, allowed_consts=allowed_consts)


def _normalize_expression(expression: str) -> str:
    # Support common calculator convention: caret for exponent.
    # The UI already emits '**', but users may type '^' manually.
    normalized = expression.replace("^", "**")
    normalized = _rewrite_unit_suffixes(normalized)
    normalized = _insert_implicit_multiplication(normalized)
    return _rewrite_postfix_factorial(normalized)


def _rewrite_unit_suffixes(expression: str) -> str:
    """Rewrite number+unit suffixes into explicit conversion calls.

    Supported:
    - 30deg  -> rad(30)
    - 0.5rad -> 0.5

    This is intentionally explicit (no guessing). Users can still control
    trig input via the global DEG/RAD mode, but suffixes override by turning
    values into radians directly.
    """

    tokens = _tokenize_expression(expression)
    if not tokens:
        return expression

    out: List[str] = []
    i = 0
    while i < len(tokens):
        kind, val = tokens[i]
        if kind == "number" and i + 1 < len(tokens):
            n_kind, n_val = tokens[i + 1]
            if n_kind == "ident" and n_val.lower() in {"deg", "rad"}:
                if n_val.lower() == "deg":
                    out.append(f"rad({val})")
                else:
                    out.append(val)
                i += 2
                continue
        out.append(val)
        i += 1
    return "".join(out)


_TOKEN_RE = re.compile(
    r"""\s*(?:(\d+(?:\.\d*)?|\.\d+)|(\*\*|[+\-*/%(),!])|([A-Za-z_][A-Za-z_0-9]*))"""
)


def _tokenize_expression(expression: str) -> List[tuple[str, str]]:
    tokens: List[tuple[str, str]] = []
    pos = 0
    while pos < len(expression):
        match = _TOKEN_RE.match(expression, pos)
        if not match:
            # Keep original behavior: let AST parse throw later, but here we
            # surface a clear error for odd characters.
            raise ValueError("Invalid expression")
        number, op, ident = match.groups()
        if number is not None:
            tokens.append(("number", number))
        elif op is not None:
            tokens.append(("op", op))
        elif ident is not None:
            tokens.append(("ident", ident))
        pos = match.end()
    return tokens


def _insert_implicit_multiplication(expression: str) -> str:
    """Insert '*' where calculators typically assume multiplication.

    Examples: 2pi -> 2*pi, 2(3+4) -> 2*(3+4), (1+2)(3+4) -> (1+2)*(3+4),
    2sin(pi/2) -> 2*sin(pi/2)
    """

    tokens = _tokenize_expression(expression)
    if not tokens:
        return expression

    def is_value(tok: tuple[str, str]) -> bool:
        """
        Determine if value logic.
        
        Args:
            tok: Description of tok.
        
        Returns:
            Result of is_value operation.
        """
        kind, val = tok
        return kind in {"number", "ident"} or (kind == "op" and val == ")")

    def is_value_start(tok: tuple[str, str]) -> bool:
        """
        Determine if value start logic.
        
        Args:
            tok: Description of tok.
        
        Returns:
            Result of is_value_start operation.
        """
        kind, val = tok
        # NOTE: '(' can start a value expression, but we only want implicit
        # multiplication into '(' (not treating '(' as an argument list).
        return kind in {"number", "ident"} or (kind == "op" and val == "(")

    known_func_names = {
        "sin",
        "cos",
        "tan",
        "asin",
        "acos",
        "atan",
        "sqrt",
        "log",
        "log10",
        "pow",
        "factorial",
        "exp",
        "floor",
        "ceil",
        "gcd",
        "lcm",
        "abs",
        "round",
        "min",
        "max",
        "deg",
        "rad",
    }

    out: List[str] = []
    for i, tok in enumerate(tokens):
        if i > 0:
            prev = tokens[i - 1]
            if is_value(prev) and is_value_start(tok):
                # If we have IDENT '(' it might be a function call. Only insert
                # '*' when the identifier is NOT a known safe function name.
                if prev[0] == "ident" and tok == ("op", "(") and prev[1] in known_func_names:
                    pass
                else:
                    out.append("*")
        out.append(tok[1])
    return "".join(out)


def _rewrite_postfix_factorial(expression: str) -> str:
    """Rewrite postfix factorial to explicit factorial() calls.

    Examples:
    - 5! -> factorial(5)
    - (3+2)! -> factorial((3+2))
    - 3!! -> factorial(factorial(3))

    This stays within the safe evaluation allowlist (factorial is already allowed).
    """

    tokens = _tokenize_expression(expression)
    if not tokens:
        return expression

    out: List[tuple[str, str]] = []

    def pop_atom() -> str:
        """
        Pop atom logic.
        
        Returns:
            Result of pop_atom operation.
        """
        if not out:
            raise ValueError("Invalid expression")

        kind, val = out[-1]
        if kind in {"number", "ident"}:
            out.pop()
            return val

        # Parenthesized atom: find matching '('
        if kind == "op" and val == ")":
            depth = 0
            pieces: List[str] = []
            while out:
                k, v = out.pop()
                pieces.append(v)
                if k == "op" and v == ")":
                    depth += 1
                elif k == "op" and v == "(":
                    depth -= 1
                    if depth == 0:
                        break
            if depth != 0:
                raise ValueError("Invalid expression")
            return "".join(reversed(pieces))

        raise ValueError("Invalid expression")

    for kind, val in tokens:
        if kind == "op" and val == "!":
            atom = pop_atom()
            out.append(("ident", f"factorial({atom})"))
        else:
            out.append((kind, val))

    return "".join(v for _, v in out)


def _safe_math_eval(
    expression: str,
    *,
    allowed_funcs: Dict[str, Callable],
    allowed_consts: Dict[str, float],
):
    """Evaluate a constrained math expression.

    Supports numbers, parentheses, binary ops (+, -, *, /, %, **), unary +/-,
    and calls to a strict allowlist of functions.
    """

    def fail(message: str) -> ValueError:
        """
        Fail logic.
        
        Args:
            message: Description of message.
        
        Returns:
            Result of fail operation.
        """
        return ValueError(message)

    expression = _normalize_expression(expression)

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise fail("Invalid expression") from exc

    def eval_node(node):  # type: ignore[reportMissingParameterType, reportUnknownParameterType]
        """
        Eval node logic.
        
        Args:
            node: Description of node.
        
        """
        if isinstance(node, ast.Expression):
            return eval_node(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise fail("Only numeric literals are allowed")

        if isinstance(node, ast.Name):
            if node.id in allowed_consts:
                return allowed_consts[node.id]
            raise fail(f"Unknown identifier: {node.id}")

        if isinstance(node, ast.UnaryOp):
            operand = eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise fail("Unsupported unary operator")

        if isinstance(node, ast.BinOp):
            left = eval_node(node.left)
            right = eval_node(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Mod):
                return left % right
            if isinstance(node.op, ast.Pow):
                return left ** right
            raise fail("Unsupported operator")

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise fail("Only simple function calls are allowed")
            func_name = node.func.id
            func = allowed_funcs.get(func_name)
            if func is None:
                raise fail(f"Function not allowed: {func_name}")
            if node.keywords:
                raise fail("Keyword arguments are not allowed")
            args = [eval_node(arg) for arg in node.args]
            try:
                return func(*args)
            except Exception as exc:
                raise fail("Math domain error") from exc

        raise fail("Unsupported expression")

    # Explicitly forbid nodes even if they might slip through.
    for subnode in ast.walk(tree):
        if isinstance(
            subnode,
            (
                ast.Attribute,
                ast.Subscript,
                ast.Lambda,
                ast.Dict,
                ast.List,
                ast.Set,
                ast.Tuple,
                ast.ListComp,
                ast.SetComp,
                ast.DictComp,
                ast.GeneratorExp,
                ast.Await,
                ast.Yield,
                ast.YieldFrom,
                ast.Compare,
                ast.IfExp,
                ast.BoolOp,
                ast.NamedExpr,
            ),
        ):
            raise fail("Unsupported expression")

    return eval_node(tree)


def _smart_backspace(text: str) -> str:
    """Backspace that removes whole tokens where it improves UX.

    Examples:
    - 'sin(' deletes as a unit
    - 'deg(' / 'rad(' / 'log10(' / 'factorial(' delete as units
    - '**' deletes as a unit
    - postfix '!' deletes as a unit
    """

    if not text:
        return text

    # Trim trailing whitespace first.
    stripped = text.rstrip()
    if not stripped:
        return ""

    token_suffixes = [
        "log10(",
        "factorial(",
        "sqrt(",
        "asin(",
        "acos(",
        "atan(",
        "sin(",
        "cos(",
        "tan(",
        "deg(",
        "rad(",
        "log(",
        "ans",
        "mem",
        "pi",
        "tau",
        "e",
        "**",
        "!",
    ]

    for suffix in token_suffixes:
        if stripped.endswith(suffix):
            return stripped[: -len(suffix)]

    return stripped[:-1]




__all__ = ["AdvancedScientificCalculatorWindow", "_smart_backspace"]