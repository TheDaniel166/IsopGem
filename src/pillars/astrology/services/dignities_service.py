"""Planetary Dignities calculation service.

Calculates essential dignities (domicile, exaltation, detriment, fall)
and accidental dignities (house placement, retrograde, combustion, mutual reception)
for the Classic 7 planets.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# Classic 7 planets
CLASSIC_7 = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}

# Zodiac signs in order (0-indexed by 30-degree sectors)
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Essential Dignities Table
# Format: planet -> {dignity_type: [signs]}
DOMICILE: Dict[str, List[str]] = {
    "Sun": ["Leo"],
    "Moon": ["Cancer"],
    "Mercury": ["Gemini", "Virgo"],
    "Venus": ["Taurus", "Libra"],
    "Mars": ["Aries", "Scorpio"],
    "Jupiter": ["Sagittarius", "Pisces"],
    "Saturn": ["Capricorn", "Aquarius"],
}

EXALTATION: Dict[str, List[str]] = {
    "Sun": ["Aries"],
    "Moon": ["Taurus"],
    "Mercury": ["Virgo"],
    "Venus": ["Pisces"],
    "Mars": ["Capricorn"],
    "Jupiter": ["Cancer"],
    "Saturn": ["Libra"],
}

DETRIMENT: Dict[str, List[str]] = {
    "Sun": ["Aquarius"],
    "Moon": ["Capricorn"],
    "Mercury": ["Sagittarius", "Pisces"],
    "Venus": ["Scorpio", "Aries"],
    "Mars": ["Libra", "Taurus"],
    "Jupiter": ["Gemini", "Virgo"],
    "Saturn": ["Cancer", "Leo"],
}

FALL: Dict[str, List[str]] = {
    "Sun": ["Libra"],
    "Moon": ["Scorpio"],
    "Mercury": ["Pisces"],
    "Venus": ["Virgo"],
    "Mars": ["Cancer"],
    "Jupiter": ["Capricorn"],
    "Saturn": ["Aries"],
}

# Scoring values
SCORE_DOMICILE = 5
SCORE_EXALTATION = 4
SCORE_DETRIMENT = -5
SCORE_FALL = -4
SCORE_PEREGRINE = 0

# Accidental dignity scores
SCORE_ANGULAR = 4       # Houses 1, 4, 7, 10
SCORE_SUCCEDENT = 2     # Houses 2, 5, 8, 11
SCORE_CADENT = -2       # Houses 3, 6, 9, 12
SCORE_DIRECT = 2
SCORE_RETROGRADE = -5
SCORE_CAZIMI = 5        # Within 17' of Sun
SCORE_COMBUST = -5      # Within 8 degrees of Sun
SCORE_UNDER_SUNBEAMS = -4  # 8-17 degrees of Sun
SCORE_MUTUAL_RECEPTION_DOMICILE = 5
SCORE_MUTUAL_RECEPTION_EXALTATION = 4

# House classifications
ANGULAR_HOUSES = {1, 4, 7, 10}
SUCCEDENT_HOUSES = {2, 5, 8, 11}
CADENT_HOUSES = {3, 6, 9, 12}


@dataclass(slots=True)
class PlanetaryDignity:
    """Calculated dignity state for a planet."""
    planet: str
    sign: str
    degree: float
    house: int
    essential_dignity: str  # "Domicile", "Exaltation", "Detriment", "Fall", "Peregrine"
    essential_score: int
    accidental_dignities: List[str] = field(default_factory=list)
    accidental_score: int = 0
    total_score: int = 0
    is_retrograde: bool = False


class DignitiesService:
    """Service for calculating planetary dignities."""

    def calculate_dignities(
        self,
        planet_positions: List[Dict],
        house_positions: List[Dict],
    ) -> List[PlanetaryDignity]:
        """
        Calculate dignities for all Classic 7 planets.

        Args:
            planet_positions: List of planet position dicts with keys:
                - name: str
                - degree: float (ecliptic longitude 0-360)
                - is_retrograde: bool (optional)
            house_positions: List of house position dicts with keys:
                - number: int (1-12)
                - degree: float (cusp longitude)

        Returns:
            List of PlanetaryDignity objects for each Classic 7 planet found
        """
        # Build house cusp lookup
        house_cusps = self._build_house_cusps(house_positions)

        # Build planet longitude lookup for mutual reception and combustion
        planet_lons: Dict[str, float] = {}
        planet_signs: Dict[str, str] = {}
        planet_retro: Dict[str, bool] = {}

        for pos in planet_positions:
            name = pos.get("name", "").strip().title()
            degree = pos.get("degree", 0.0)
            is_retro = pos.get("is_retrograde", False)

            planet_lons[name] = degree
            planet_signs[name] = self._get_sign(degree)
            planet_retro[name] = is_retro

        # Get Sun longitude for combustion calculations
        sun_lon = planet_lons.get("Sun", 0.0)

        # Calculate mutual receptions
        mutual_receptions = self._find_mutual_receptions(planet_signs)

        results: List[PlanetaryDignity] = []

        for planet in CLASSIC_7:
            if planet not in planet_lons:
                continue

            degree = planet_lons[planet]
            sign = planet_signs[planet]
            is_retro = planet_retro.get(planet, False)
            house = self._get_house(degree, house_cusps)

            # Essential dignity
            essential, essential_score = self._get_essential_dignity(planet, sign)

            # Accidental dignities
            accidental_list, accidental_score = self._get_accidental_dignities(
                planet=planet,
                house=house,
                is_retrograde=is_retro,
                planet_lon=degree,
                sun_lon=sun_lon,
                mutual_receptions=mutual_receptions,
            )

            total = essential_score + accidental_score

            results.append(PlanetaryDignity(
                planet=planet,
                sign=sign,
                degree=degree,
                house=house,
                essential_dignity=essential,
                essential_score=essential_score,
                accidental_dignities=accidental_list,
                accidental_score=accidental_score,
                total_score=total,
                is_retrograde=is_retro,
            ))

        # Sort by traditional planet order
        order = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        results.sort(key=lambda d: order.index(d.planet) if d.planet in order else 99)

        return results

    def _get_sign(self, degree: float) -> str:
        """Get zodiac sign from ecliptic longitude."""
        idx = int(degree // 30) % 12
        return ZODIAC_SIGNS[idx]

    def _get_essential_dignity(self, planet: str, sign: str) -> Tuple[str, int]:
        """
        Determine essential dignity for a planet in a sign.

        Returns:
            Tuple of (dignity_name, score)
        """
        if sign in DOMICILE.get(planet, []):
            return ("Domicile", SCORE_DOMICILE)
        if sign in EXALTATION.get(planet, []):
            return ("Exaltation", SCORE_EXALTATION)
        if sign in DETRIMENT.get(planet, []):
            return ("Detriment", SCORE_DETRIMENT)
        if sign in FALL.get(planet, []):
            return ("Fall", SCORE_FALL)
        return ("Peregrine", SCORE_PEREGRINE)

    def _get_accidental_dignities(
        self,
        planet: str,
        house: int,
        is_retrograde: bool,
        planet_lon: float,
        sun_lon: float,
        mutual_receptions: Dict[str, List[Tuple[str, str]]],
    ) -> Tuple[List[str], int]:
        """
        Calculate accidental dignities for a planet.

        Returns:
            Tuple of (list of dignity descriptions, total score)
        """
        dignities: List[str] = []
        score = 0

        # House placement
        if house in ANGULAR_HOUSES:
            dignities.append(f"Angular ({house})")
            score += SCORE_ANGULAR
        elif house in SUCCEDENT_HOUSES:
            dignities.append(f"Succedent ({house})")
            score += SCORE_SUCCEDENT
        elif house in CADENT_HOUSES:
            dignities.append(f"Cadent ({house})")
            score += SCORE_CADENT

        # Motion (retrograde vs direct)
        if is_retrograde:
            dignities.append("Retrograde")
            score += SCORE_RETROGRADE
        else:
            dignities.append("Direct")
            score += SCORE_DIRECT

        # Sun proximity (not applicable to Sun or Moon)
        if planet not in ("Sun", "Moon"):
            sun_distance = self._angular_distance(planet_lon, sun_lon)

            # Cazimi: within 17 arcminutes (0.283 degrees)
            if sun_distance <= 0.283:
                dignities.append("Cazimi")
                score += SCORE_CAZIMI
            # Combust: within 8 degrees
            elif sun_distance <= 8.0:
                dignities.append("Combust")
                score += SCORE_COMBUST
            # Under the Sunbeams: 8-17 degrees
            elif sun_distance <= 17.0:
                dignities.append("Under Sunbeams")
                score += SCORE_UNDER_SUNBEAMS

        # Mutual reception
        if planet in mutual_receptions:
            for other_planet, reception_type in mutual_receptions[planet]:
                if reception_type == "domicile":
                    dignities.append(f"Mutual Reception ({other_planet})")
                    score += SCORE_MUTUAL_RECEPTION_DOMICILE
                elif reception_type == "exaltation":
                    dignities.append(f"Mutual Exalt. ({other_planet})")
                    score += SCORE_MUTUAL_RECEPTION_EXALTATION

        return dignities, score

    def _find_mutual_receptions(
        self, planet_signs: Dict[str, str]
    ) -> Dict[str, List[Tuple[str, str]]]:
        """
        Find mutual receptions between planets.

        A mutual reception occurs when two planets are each in a sign
        ruled by the other (domicile) or exalted by the other (exaltation).

        Returns:
            Dict mapping planet name to list of (other_planet, reception_type) tuples
        """
        receptions: Dict[str, List[Tuple[str, str]]] = {}

        planets = list(planet_signs.keys())

        for i, planet_a in enumerate(planets):
            if planet_a not in CLASSIC_7:
                continue
            sign_a = planet_signs[planet_a]

            for planet_b in planets[i + 1:]:
                if planet_b not in CLASSIC_7:
                    continue
                sign_b = planet_signs[planet_b]

                # Check domicile mutual reception
                # Planet A is in a sign ruled by Planet B AND
                # Planet B is in a sign ruled by Planet A
                a_in_b_domicile = sign_a in DOMICILE.get(planet_b, [])
                b_in_a_domicile = sign_b in DOMICILE.get(planet_a, [])

                if a_in_b_domicile and b_in_a_domicile:
                    if planet_a not in receptions:
                        receptions[planet_a] = []
                    if planet_b not in receptions:
                        receptions[planet_b] = []
                    receptions[planet_a].append((planet_b, "domicile"))
                    receptions[planet_b].append((planet_a, "domicile"))
                    continue  # Skip exaltation check if domicile reception exists

                # Check exaltation mutual reception
                a_in_b_exalt = sign_a in EXALTATION.get(planet_b, [])
                b_in_a_exalt = sign_b in EXALTATION.get(planet_a, [])

                if a_in_b_exalt and b_in_a_exalt:
                    if planet_a not in receptions:
                        receptions[planet_a] = []
                    if planet_b not in receptions:
                        receptions[planet_b] = []
                    receptions[planet_a].append((planet_b, "exaltation"))
                    receptions[planet_b].append((planet_a, "exaltation"))

        return receptions

    def _build_house_cusps(self, house_positions: List[Dict]) -> List[float]:
        """
        Build ordered list of house cusps (12 values, index 0 = house 1).
        """
        cusps = [0.0] * 12
        for pos in house_positions:
            num = pos.get("number", 0)
            degree = pos.get("degree", 0.0)
            if 1 <= num <= 12:
                cusps[num - 1] = degree
        return cusps

    def _get_house(self, degree: float, cusps: List[float]) -> int:
        """
        Determine which house a degree falls in.

        Uses whole sign-aware logic: planet is in a house if its degree
        falls between that house's cusp and the next house's cusp.
        """
        degree = degree % 360

        for i in range(12):
            cusp_start = cusps[i]
            cusp_end = cusps[(i + 1) % 12]

            # Handle wrap-around at 0/360
            if cusp_start <= cusp_end:
                if cusp_start <= degree < cusp_end:
                    return i + 1
            else:
                # Wraps around 360
                if degree >= cusp_start or degree < cusp_end:
                    return i + 1

        return 1  # Fallback

    @staticmethod
    def _angular_distance(lon1: float, lon2: float) -> float:
        """Calculate the shortest angular distance between two longitudes."""
        diff = abs((lon1 % 360) - (lon2 % 360))
        return min(diff, 360 - diff)
