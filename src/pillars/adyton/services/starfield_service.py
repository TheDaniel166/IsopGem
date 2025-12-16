"""
Starfield Service: loads bright stars and planets via Skyfield, outputs direction vectors and brightness.
"""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Tuple

from skyfield.api import Loader, Star, load
from skyfield.data import hipparcos

# Rough Galactic Center equatorial (J2000): RA 17h45m40s, Dec -29°00'28"
GC_RA_HOURS = 17 + 45/60 + 40/3600
GC_DEC_DEG = -29.0078

@dataclass
class StarPoint:
    direction: Tuple[float, float, float]
    magnitude: float
    color: Tuple[float, float, float]

class StarfieldService:
    def __init__(self):
        self.load = Loader('/tmp/skyfield')
        self.ts = self.load.timescale()
        self.planets = load('de421.bsp')

    @lru_cache(maxsize=1)
    def load_bright_stars(self, mag_limit: float = 5.0) -> List[StarPoint]:
        with self.load.open(hipparcos.URL) as f:
            df = hipparcos.load_dataframe(f)
        df = df[df['magnitude'] <= mag_limit]
        stars: List[StarPoint] = []
        t = self.ts.utc(2025, 12, 16)
        earth = self.planets['earth']
        for row in df.itertuples():
            star = Star(ra_hours=row.ra_hours, dec_degrees=row.dec_degrees)
            astrometric = earth.at(t).observe(star)
            ra, dec, _ = astrometric.radec()
            direction = self._radec_to_unit(ra.hours, dec.degrees)
            # simple bluish-white color based on magnitude
            b = max(0.4, 1.0 - (row.magnitude / mag_limit))
            col = (0.8 * b, 0.85 * b, 1.0)
            stars.append(StarPoint(direction=direction, magnitude=row.magnitude, color=col))
        return stars

    def planet_points(self) -> List[StarPoint]:
        t = self.ts.now()
        earth = self.planets['earth']
        bodies = ['mercury', 'venus', 'mars', 'jupiter barycenter', 'saturn barycenter']
        pts: List[StarPoint] = []
        for name in bodies:
            astrometric = earth.at(t).observe(self.planets[name])
            ra, dec, _ = astrometric.radec()
            direction = self._radec_to_unit(ra.hours, dec.degrees)
            pts.append(StarPoint(direction=direction, magnitude=-1.0, color=(1.0, 0.8, 0.4)))
        return pts

    def rotated_samples(self, mag_limit: float = 5.0) -> List[StarPoint]:
        """Stars+planets rotated so the Galactic Center points to +Z."""
        rot = self._rotation_from_vec_to_vec(self.galactic_center_unit(), (0.0, 0.0, 1.0))
        samples = []
        for s in self.load_bright_stars(mag_limit):
            dx, dy, dz = self._apply_rotation(rot, s.direction)
            samples.append(StarPoint((dx, dy, dz), s.magnitude, s.color))
        for p in self.planet_points():
            dx, dy, dz = self._apply_rotation(rot, p.direction)
            samples.append(StarPoint((dx, dy, dz), p.magnitude, p.color))
        return samples

    def _radec_to_unit(self, ra_hours: float, dec_deg: float) -> Tuple[float, float, float]:
        import math
        ra_rad = math.radians(ra_hours * 15.0)
        dec_rad = math.radians(dec_deg)
        x = math.cos(dec_rad) * math.cos(ra_rad)
        y = math.cos(dec_rad) * math.sin(ra_rad)
        z = math.sin(dec_rad)
        return (x, y, z)

    def galactic_center_unit(self) -> Tuple[float, float, float]:
        return self._radec_to_unit(GC_RA_HOURS, GC_DEC_DEG)

    def _rotation_from_vec_to_vec(self, src, dst):
        sx, sy, sz = src
        dx, dy, dz = dst
        import math
        vx, vy, vz = (sy * dz - sz * dy, sz * dx - sx * dz, sx * dy - sy * dx)
        c = sx * dx + sy * dy + sz * dz
        if c < -0.9999:
            # 180-degree rotation around any orthogonal axis
            ax = 1.0 if abs(sx) < 0.9 else 0.0
            ay = 1.0 if ax == 0.0 else 0.0
            az = 0.0
            vx, vy, vz = ay * sz - az * sy, az * sx - ax * sz, ax * sy - ay * sx
            c = -1.0
        k = 1.0 / (1.0 + c)
        return (
            1 + k * (vx * vx - 1), k * vx * vy - vz, k * vx * vz + vy,
            k * vy * vx + vz, 1 + k * (vy * vy - 1), k * vy * vz - vx,
            k * vz * vx - vy, k * vz * vy + vx, 1 + k * (vz * vz - 1),
        )

    def _apply_rotation(self, rot, vec):
        m00, m01, m02, m10, m11, m12, m20, m21, m22 = rot
        x, y, z = vec
        return (
            m00 * x + m01 * y + m02 * z,
            m10 * x + m11 * y + m12 * z,
            m20 * x + m21 * y + m22 * z,
        )
