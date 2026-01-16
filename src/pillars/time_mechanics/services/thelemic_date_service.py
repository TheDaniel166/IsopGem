"""
Thelemic Date Service - Era Legis Calendar Calculator.

Calculates Thelemic dates based on the calendar system established by
Aleister Crowley following the reception of Liber AL vel Legis in 1904.

Key features:
- Docosade (22-year cycle) calculation with Tarot correspondences
- Solar and Lunar position calculation for date format
- Latin day-of-week names
- Full and abbreviated date formatting

Reference: https://oto-usa.org/thelema/calendar/
"""
from datetime import date, datetime, timezone
from typing import Optional
import logging

from ..models.thelemic_date_models import ThelemicDate

logger = logging.getLogger(__name__)


class ThelemicDateService:
    """
    Service for calculating and formatting Thelemic dates.

    The Thelemic calendar begins on March 20, 1904 (Vernal Equinox)
    when Aleister Crowley received The Book of the Law.

    Each Thelemic year runs from Vernal Equinox to Vernal Equinox.
    Years are counted in 22-year cycles (docosades) corresponding
    to the 22 Tarot Trumps.
    """

    # The Thelemic epoch: March 20, 1904 (Vernal Equinox)
    EPOCH = date(1904, 3, 20)

    # Approximate Vernal Equinox for year calculation
    # (We use March 20 as the standard date; precise calculation
    # would require astronomical computation)
    EQUINOX_MONTH = 3
    EQUINOX_DAY = 20

    def __init__(self):
        """Initialize the Thelemic Date Service."""
        self._ephemeris = None
        self._ephemeris_available = False
        self._init_ephemeris()

    def _init_ephemeris(self) -> None:
        """Lazily initialize ephemeris provider for astronomical calculations."""
        try:
            from shared.services.ephemeris_provider import EphemerisProvider
            self._ephemeris = EphemerisProvider.get_instance()
            self._ephemeris_available = True
        except ImportError:
            logger.warning("Ephemeris provider not available; using approximate positions")
            self._ephemeris_available = False
        except Exception as e:
            logger.warning("Failed to initialize ephemeris: %s", e)
            self._ephemeris_available = False

    def from_gregorian(
        self,
        gregorian_date: date,
        time_of_day: Optional[datetime] = None
    ) -> ThelemicDate:
        """
        Convert a Gregorian date to a Thelemic date.

        Args:
            gregorian_date: The Gregorian calendar date
            time_of_day: Optional datetime for precise Sol/Luna positions.
                        If None, uses noon UTC.

        Returns:
            ThelemicDate object with all calculated values
        """
        # Calculate Thelemic year
        thelemic_year = self._calculate_thelemic_year(gregorian_date)

        # Calculate docosade and year within docosade
        docosade = thelemic_year // 22
        year_in_docosade = thelemic_year % 22

        # Get datetime for astronomical calculations
        if time_of_day is not None:
            calc_datetime = time_of_day
        else:
            calc_datetime = datetime(
                gregorian_date.year,
                gregorian_date.month,
                gregorian_date.day,
                12, 0, 0,
                tzinfo=timezone.utc
            )

        # Calculate Sol and Luna positions
        sol_longitude = self._get_sun_longitude(calc_datetime)
        luna_longitude = self._get_moon_longitude(calc_datetime)

        # Get day of week (Python: Monday=0, Sunday=6)
        weekday = gregorian_date.weekday()

        return ThelemicDate(
            gregorian_date=gregorian_date,
            gregorian_time=calc_datetime,
            thelemic_year=thelemic_year,
            docosade=docosade,
            year_in_docosade=year_in_docosade,
            sol_longitude=sol_longitude,
            luna_longitude=luna_longitude,
            weekday=weekday,
        )

    def _calculate_thelemic_year(self, gregorian_date: date) -> int:
        """
        Calculate the Thelemic year number.

        The Thelemic year begins at the Vernal Equinox (approximately March 20).
        Year 0 ran from March 20, 1904 to March 19, 1905.

        Args:
            gregorian_date: The Gregorian date

        Returns:
            Thelemic year number (0-based from 1904)
        """
        year_diff = gregorian_date.year - self.EPOCH.year

        # Check if we're before the equinox in the given year
        equinox_this_year = date(gregorian_date.year, self.EQUINOX_MONTH, self.EQUINOX_DAY)

        if gregorian_date < equinox_this_year:
            # Before equinox: still in previous Thelemic year
            year_diff -= 1

        return max(0, year_diff)

    def _get_sun_longitude(self, dt: datetime) -> float:
        """
        Get the Sun's ecliptic longitude.

        Uses the ephemeris if available, otherwise calculates
        an approximate position based on the date.

        Args:
            dt: The datetime for calculation

        Returns:
            Ecliptic longitude in degrees (0-360)
        """
        if self._ephemeris_available and self._ephemeris and self._ephemeris.is_loaded():
            try:
                return self._ephemeris.get_geocentric_ecliptic_position("sun", dt)
            except Exception as e:
                logger.debug("Ephemeris calculation failed, using approximation: %s", e)

        # Approximate calculation based on date
        # The Sun moves approximately 1 degree per day through the zodiac
        # Vernal Equinox (0° Aries) is approximately March 20
        days_since_equinox = (dt.date() - date(dt.year, 3, 20)).days
        return (days_since_equinox * (360.0 / 365.25)) % 360.0

    def _get_moon_longitude(self, dt: datetime) -> float:
        """
        Get the Moon's ecliptic longitude.

        Uses the ephemeris if available, otherwise calculates
        a rough approximation.

        Args:
            dt: The datetime for calculation

        Returns:
            Ecliptic longitude in degrees (0-360)
        """
        if self._ephemeris_available and self._ephemeris and self._ephemeris.is_loaded():
            try:
                return self._ephemeris.get_geocentric_ecliptic_position("moon", dt)
            except Exception as e:
                logger.debug("Ephemeris calculation failed, using approximation: %s", e)

        # Very rough approximation (Moon moves ~13.2 degrees per day)
        # This is not accurate but provides a placeholder
        # Use a known Moon position as reference
        # Jan 1, 2000 at noon: Moon was approximately at 122° (Leo)
        ref_date = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        days_since_ref = (dt - ref_date).total_seconds() / 86400.0
        # Synodic month is ~29.53 days, Moon completes 360° in that time
        # But for ecliptic longitude, we use sidereal month (~27.32 days)
        degrees_per_day = 360.0 / 27.321661
        return (122.0 + days_since_ref * degrees_per_day) % 360.0

    def get_today(self, time_of_day: Optional[datetime] = None) -> ThelemicDate:
        """
        Get the Thelemic date for today.

        Args:
            time_of_day: Optional specific time. If None, uses current time.

        Returns:
            ThelemicDate for today
        """
        today = date.today()
        if time_of_day is None:
            time_of_day = datetime.now(timezone.utc)
        return self.from_gregorian(today, time_of_day)
