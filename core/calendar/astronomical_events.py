from datetime import date, datetime, timedelta
from enum import Enum
from skyfield.api import load, utc
from skyfield.almanac import find_discrete, risings_and_settings
from skyfield.almanac import moon_phases, seasons
from skyfield.units import Angle
from numpy import pi, cos, degrees
import pytz

class AstronomicalEvents:
    """Handles astronomical events and cycles with high precision"""
    
    class EventType(Enum):
        NEW_MOON = "New Moon"
        FULL_MOON = "Full Moon"
        EQUINOX = "Equinox"
        SOLSTICE = "Solstice"
        
    def __init__(self):
        # Load required astronomical data
        self.eph = load('de421.bsp')  # JPL ephemeris
        self.ts = load.timescale()
        self.earth = self.eph['earth']
        self.sun = self.eph['sun']
        self.moon = self.eph['moon']
        self.timezone = pytz.timezone('US/Eastern')
        
    def get_zodiacal_position(self, body, time):
        """Get zodiacal position of a celestial body"""
        earth = self.earth.at(time)
        pos = earth.observe(body).apparent()
        lat, lon, _ = pos.ecliptic_latlon()
        
        # Convert longitude to degrees
        degrees_total = degrees(lon.radians)
        if degrees_total < 0:
            degrees_total += 360
            
        # Calculate zodiac sign
        zodiac_signs = [
            "Aries", "Taurus", "Gemini", "Cancer",
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        sign_num = int(degrees_total / 30)
        sign = zodiac_signs[sign_num]
        
        # Calculate degrees within sign
        deg_in_sign = degrees_total % 30
        
        return f"{sign} {deg_in_sign:.2f}°"

    def get_events_for_month(self, year, month):
        """Get precise astronomical events for month with zodiacal positions"""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
            
        # Convert to UTC datetime with timezone
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.min.time())
        start_dt = self.timezone.localize(start_dt).astimezone(pytz.UTC)
        end_dt = self.timezone.localize(end_dt).astimezone(pytz.UTC)
        
        t0 = self.ts.from_datetime(start_dt)
        t1 = self.ts.from_datetime(end_dt)
        
        events = []
        
        # Moon phases with positions
        t, phase = find_discrete(t0, t1, moon_phases(self.eph))
        for ti, ph in zip(t, phase):
            # event_time_utc already has UTC timezone
            event_time_utc = ti.utc_datetime()
            # Convert directly to local timezone since it's already UTC
            event_time_local = event_time_utc.astimezone(self.timezone)
            event_date = event_time_local.date()
            
            if ph == 0:  # New Moon
                event_type = self.EventType.NEW_MOON
                event_name = "New Moon"
                sun_pos = self.get_zodiacal_position(self.sun, ti)
                time_str = event_time_local.strftime("%Y-%m-%d %H:%M:%S %Z")
                tooltip = f"{event_name}: {time_str}\nPosition: {sun_pos}"
                events.append((event_date, event_type, tooltip))
                
            elif ph == 2:  # Full Moon
                event_type = self.EventType.FULL_MOON
                event_name = "Full Moon"
                sun_pos = self.get_zodiacal_position(self.sun, ti)
                moon_pos = self.get_zodiacal_position(self.moon, ti)
                time_str = event_time_local.strftime("%Y-%m-%d %H:%M:%S %Z")
                tooltip = f"{event_name}: {time_str}\nSun: {sun_pos}\nMoon: {moon_pos}"
                events.append((event_date, event_type, tooltip))
            
        # Equinoxes and solstices with sun position
        t, season = find_discrete(t0, t1, seasons(self.eph))
        for ti, si in zip(t, season):
            event_time_utc = ti.utc_datetime()
            # Convert directly to local timezone
            event_time_local = event_time_utc.astimezone(self.timezone)
            event_date = event_time_local.date()
            
            sun_pos = self.get_zodiacal_position(self.sun, ti)
            
            if si == 0:  # Spring equinox
                event_type = self.EventType.EQUINOX
                event_name = "Spring Equinox"
            elif si == 1:  # Summer solstice
                event_type = self.EventType.SOLSTICE
                event_name = "Summer Solstice"
            elif si == 2:  # Autumn equinox
                event_type = self.EventType.EQUINOX
                event_name = "Autumn Equinox"
            elif si == 3:  # Winter solstice
                event_type = self.EventType.SOLSTICE
                event_name = "Winter Solstice"
                
            time_str = event_time_local.strftime("%Y-%m-%d %H:%M:%S %Z")
            tooltip = f"{event_name}: {time_str}\nSun: {sun_pos}"
            events.append((event_date, event_type, tooltip))
            
        return sorted(events, key=lambda x: x[0]) 