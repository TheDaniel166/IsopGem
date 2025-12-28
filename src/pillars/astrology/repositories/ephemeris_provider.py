"""
Ephemeris Provider - The Celestial Engine.
Singleton interface to Skyfield for calculating geocentric/heliocentric planetary positions and lunar nodes.
"""
from datetime import datetime, timezone, timedelta
import math
import os
from skyfield.api import load
from skyfield.framelib import ecliptic_frame

import threading

class EphemerisNotLoadedError(Exception):
    pass

class EphemerisProvider:
    _instance = None
    _planets = None
    _ts = None
    _loaded = False
    _loading_thread = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = EphemerisProvider()
        return cls._instance

    def __init__(self):
        if EphemerisProvider._instance is not None:
            raise Exception("This class is a singleton!")
        
        self._loaded = False
        self._loading_thread = threading.Thread(target=self._load_data, daemon=True)
        self._loading_thread.start()

    def is_loaded(self) -> bool:
        return self._loaded

    def _load_data(self):
        # Look for de421.bsp in likely locations
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
        candidates = [
            "de441.bsp",
            "data/de441.bsp",
            os.path.join(base_dir, "de441.bsp"),
            os.path.join(base_dir, "data/de441.bsp"),
            # Check IsopGem build directory
            os.path.expanduser("~/IsopGem/_internal/assets/ephemeris/de441.bsp"),
            "de421.bsp",
            "data/de421.bsp",
            os.path.join(base_dir, "de421.bsp"),
            os.path.join(base_dir, "data/de421.bsp")
        ]
        
        file_path = "de421.bsp" # Default fall back (small)
        found = False
        for c in candidates:
            if os.path.exists(c):
                file_path = c
                found = True
                break
        
        if not found:
            # Prefer big file for new installs or updates
            file_path = "de441.bsp"
            
        print(f"Loading ephemeris from: {file_path}")
        self._ts = load.timescale()
        self._planets = load(file_path) # This will download if missing
        self._loaded = True
        print("Ephemeris loaded successfully.")

    def get_osculating_north_node(self, dt: datetime) -> float:
        """
        Calculates the Geocentric Osculating North Node (True Node) of the Moon.
        Defined as the intersection of the Moon's instantaneous orbital plane with the Ecliptic.
        """
        if not self._loaded:
            raise EphemerisNotLoadedError("Ephemeris data is still loading.")

        t = self._ts.from_datetime(dt)
        earth = self._planets['earth']
        moon = self._planets['moon']
        
        # 1. Get Moon's Geocentric Position and Velocity
        # Note: 'true' parameter provides GCRS position/velocity
        astrometric = earth.at(t).observe(moon)
        pos = astrometric.position.au
        vel = astrometric.velocity.au_per_d
        
        # 2. Calculate Angular Momentum Vector L = r x v
        # This vector is perpendicular to the orbital plane
        Lx = pos[1]*vel[2] - pos[2]*vel[1]
        Ly = pos[2]*vel[0] - pos[0]*vel[2]
        Lz = pos[0]*vel[1] - pos[1]*vel[0]
        
        # 3. Calculate Node Longitude
        # The line of nodes is the intersection of orbital plane and ecliptic plane (z=0)
        # Vector pointing to ascending node is N = k x L (where k is z-axis unit vector)
        # N = (-Ly, Lx, 0)
        # Longitude = atan2(Ny, Nx) = atan2(Lx, -Ly)
        
        node_rad = math.atan2(Lx, -Ly)
        node_deg = math.degrees(node_rad)
        
        return node_deg % 360.0

    def get_geocentric_ecliptic_position(self, body_name: str, dt: datetime) -> float:
        """
        Returns the Geocentric Ecliptic Longitude (0-360) for a given body.
        body_name: 'venus', 'mars', 'sun', etc.
        """

        if not self._loaded:
            raise EphemerisNotLoadedError("Ephemeris data is still loading.")
        
        t = self._ts.from_datetime(dt)
        earth = self._planets['earth']
        body = self._planets[body_name]
        
        # Geocentric observation
        astrometric = earth.at(t).observe(body)
        
        # Project to Ecliptic
        lat, lon, distance = astrometric.ecliptic_latlon()
        
        return lon.degrees

    def get_heliocentric_ecliptic_position(self, body_name: str, dt: datetime) -> float:
        """
        Returns the Heliocentric Ecliptic Longitude (0-360) for a given body.
        Observer is the Sun.
        """

        if not self._loaded:
            raise EphemerisNotLoadedError("Ephemeris data is still loading.")
        
        t = self._ts.from_datetime(dt)
        sun = self._planets['sun']
        body = self._planets[body_name]
        
        # Heliocentric observation
        astrometric = sun.at(t).observe(body)
        
        # Project to Ecliptic
        lat, lon, distance = astrometric.ecliptic_latlon()
        
        return lon.degrees

    def get_extended_data(self, body_name: str, dt: datetime) -> dict:
        """
        Returns a dictionary of extended orbital data:
        - helio_lon: Heliocentric Longitude (deg)
        - helio_lat: Heliocentric Latitude (deg)
        - helio_speed: Heliocentric Speed (deg/day)
        - elongation: Geocentric Elongation (deg)
        - is_retrograde: Geocentric Retrograde Status (bool)
        """

        if not self._loaded:
            raise EphemerisNotLoadedError("Ephemeris data is still loading.")
        
        t = self._ts.from_datetime(dt)
        sun = self._planets['sun']
        earth = self._planets['earth']
        body = self._planets[body_name]
        
        # 1. Heliocentric Data (Sun -> Body)
        # Position at T
        ast_h = sun.at(t).observe(body)
        lat_h, lon_h, dist_h = ast_h.ecliptic_latlon()
        
        # Speed (Velocity at T, estimate via delta)
        # 1 hour delta
        delta_h = 1.0 / 24.0
        t_plus = self._ts.from_datetime(dt + timedelta(hours=1))
        ast_h_plus = sun.at(t_plus).observe(body)
        _, lon_h_plus, _ = ast_h_plus.ecliptic_latlon()
        
        diff_h = (lon_h_plus.degrees - lon_h.degrees)
        # Handle wraparound
        if diff_h < -300: diff_h += 360
        elif diff_h > 300: diff_h -= 360
        
        speed_deg_per_day = diff_h * 24.0
        
        # 2. Geocentric Data (Earth -> Body) & Retrograde
        ast_g = earth.at(t).observe(body)
        _, lon_g, _ = ast_g.ecliptic_latlon()
        
        ast_g_plus = earth.at(t_plus).observe(body)
        _, lon_g_plus, _ = ast_g_plus.ecliptic_latlon()
        
        diff_g = (lon_g_plus.degrees - lon_g.degrees)
        if diff_g < -300: diff_g += 360
        elif diff_g > 300: diff_g -= 360
        
        # Retrograde if Geocentric Longitude is decreasing
        is_retrograde = diff_g < 0
        
        # 3. Elongation (Angle between Sun and Body as seen from Earth)
        # Separation returns an Angle object
        # Note: separation_from() calculates angular distance between two observation vectors
        # Vector 1: Earth->Sun
        # Vector 2: Earth->Body
        elongation_angle = earth.at(t).observe(sun).separation_from(earth.at(t).observe(body))
        
        return {
            "helio_lon": lon_h.degrees,
            "helio_lat": lat_h.degrees,
            "helio_speed": speed_deg_per_day,
            "elongation": elongation_angle.degrees,
            "is_retrograde": is_retrograde,
            "geo_speed": diff_g * 24.0 # Optional context
        }
