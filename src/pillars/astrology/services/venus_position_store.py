"""Venus/Earth positional cache (SQLite).

Purpose
- Provide fast, repeatable access to heliocentric (Sun-centered) ecliptic positions
  at a fixed cadence (default 30 minutes).
- Keep ephemeris-heavy computation out of the UI thread.

This module intentionally contains NO PyQt imports.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional


DEFAULT_DB_PATH = Path("data") / "venus_positions.db"
DEFAULT_CADENCE_MINUTES = 30
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class HeliocentricPosition:
    """Heliocentric ecliptic position projected to the ecliptic plane."""

    dt_utc: datetime
    body: str  # 'earth' or 'venus'
    lon_deg: float
    lat_deg: float
    distance_au: float


class VenusPositionStore:
    """SQLite-backed store for cached heliocentric positions."""

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH):
        self._db_path = Path(db_path)

    @property
    def db_path(self) -> Path:
        return self._db_path

    def is_built(self) -> bool:
        return self._db_path.exists()

    def connect(self) -> sqlite3.Connection:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def ensure_schema(self, conn: sqlite3.Connection) -> None:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS heliocentric_positions (
                dt_utc TEXT NOT NULL,
                body TEXT NOT NULL,
                lon_deg REAL NOT NULL,
                lat_deg REAL NOT NULL,
                distance_au REAL NOT NULL,
                PRIMARY KEY (dt_utc, body)
            )
            """
        )
        cur.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)",
            ("schema_version", str(SCHEMA_VERSION)),
        )
        conn.commit()

    @staticmethod
    def round_dt_to_cadence(dt: datetime, cadence_minutes: int = DEFAULT_CADENCE_MINUTES) -> datetime:
        """Round a datetime to the nearest cadence bucket in UTC."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)

        cadence_seconds = cadence_minutes * 60
        epoch = int(dt.timestamp())
        rounded = int((epoch + cadence_seconds / 2) // cadence_seconds * cadence_seconds)
        return datetime.fromtimestamp(rounded, tz=timezone.utc)

    @staticmethod
    def to_dt_key(dt: datetime) -> str:
        """Storage key format (UTC)."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def get_heliocentric_position(
        self,
        dt: datetime,
        body: str,
        cadence_minutes: int = DEFAULT_CADENCE_MINUTES,
        conn: Optional[sqlite3.Connection] = None,
    ) -> Optional[HeliocentricPosition]:
        """Fetch nearest cached heliocentric position for a body."""
        # Critical: do not create an empty DB as a side-effect of a read.
        # If the cache doesn't exist yet, caller should fall back to live ephemeris.
        if conn is None and not self._db_path.exists():
            return None

        rounded_dt = self.round_dt_to_cadence(dt, cadence_minutes=cadence_minutes)
        dt_key = self.to_dt_key(rounded_dt)

        close_conn = False
        if conn is None:
            conn = self.connect()
            close_conn = True

        try:
            self.ensure_schema(conn)
            row = conn.execute(
                """
                SELECT dt_utc, body, lon_deg, lat_deg, distance_au
                FROM heliocentric_positions
                WHERE dt_utc = ? AND body = ?
                """,
                (dt_key, body.lower()),
            ).fetchone()
            if row is None:
                return None

            return HeliocentricPosition(
                dt_utc=datetime.strptime(row["dt_utc"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
                body=row["body"],
                lon_deg=float(row["lon_deg"]),
                lat_deg=float(row["lat_deg"]),
                distance_au=float(row["distance_au"]),
            )
        finally:
            if close_conn:
                conn.close()

    def upsert_heliocentric_position(
        self,
        conn: sqlite3.Connection,
        pos: HeliocentricPosition,
    ) -> None:
        conn.execute(
            """
            INSERT OR REPLACE INTO heliocentric_positions(
                dt_utc, body, lon_deg, lat_deg, distance_au
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (
                self.to_dt_key(pos.dt_utc),
                pos.body.lower(),
                pos.lon_deg,
                pos.lat_deg,
                pos.distance_au,
            ),
        )


def add_years(dt: datetime, years: int) -> datetime:
    """Add years safely (approx, Feb 29 handled by clamping to Feb 28)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    try:
        return dt.replace(year=dt.year + years)
    except ValueError:
        # Likely Feb 29
        return dt.replace(month=2, day=28, year=dt.year + years)


def iter_time_range(start_dt: datetime, end_dt: datetime, cadence_minutes: int):
    """Yield UTC datetimes from start to end inclusive at cadence."""
    if start_dt.tzinfo is None:
        start_dt = start_dt.replace(tzinfo=timezone.utc)
    else:
        start_dt = start_dt.astimezone(timezone.utc)

    if end_dt.tzinfo is None:
        end_dt = end_dt.replace(tzinfo=timezone.utc)
    else:
        end_dt = end_dt.astimezone(timezone.utc)

    step = timedelta(minutes=cadence_minutes)
    t = start_dt
    while t <= end_dt:
        yield t
        t += step
