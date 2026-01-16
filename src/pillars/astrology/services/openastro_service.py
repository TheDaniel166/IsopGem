"""Wrapper service that integrates OpenAstro2 with IsopGem."""
from __future__ import annotations

import copy
import logging
from typing import Any, Dict, List, Optional

from ..models import (
    AstrologyEvent,
    ChartRequest,
    ChartResult,
    GeoLocation,
    HousePosition,
    PlanetPosition,
)

try:  # pragma: no cover - import guard only hits when dependency missing
    from openastro2.openastro2 import openAstro  # type: ignore
except ImportError:  # pragma: no cover - handled at runtime
    openAstro = None  # type: ignore

try:
    import swisseph as swe
except ImportError:
    swe = None


class OpenAstroNotAvailableError(RuntimeError):
    """Raised when openastro2 is not available in the current environment."""


class ChartComputationError(RuntimeError):
    """Wrap low-level exceptions that occur during chart generation."""


class OpenAstroService:
    """High-level orchestration layer for OpenAstro2 usage.

    The service isolates direct dependencies on openastro2, making testing
    easier while giving the UI a clean API surface.
    """

    # Minimal subset of well-known house systems for quick validation
    HOUSE_SYSTEM_LABELS: Dict[str, str] = {
        "A": "Equal",
        "E": "Equal (alternate)",
        "G": "Gauquelin",
        "H": "Horizontal",
        "K": "Koch",
        "O": "Porphyry",
        "P": "Placidus",
        "R": "Regiomontanus",
        "C": "Campanus",
        "W": "Whole Sign",
    }

    def __init__(self, default_settings: Optional[Dict[str, Any]] = None) -> None:
        """
          init   logic.
        
        Args:
            default_settings: Description of default_settings.
        
        Returns:
            Result of __init__ operation.
        """
        if openAstro is None:
            raise OpenAstroNotAvailableError(
                "openastro2 is not installed. Ensure 'pip install openastro2' "
                "has been run on this system."
            )
        self._logger = logging.getLogger(self.__class__.__name__)
        # Initialize default settings (copied from template if not provided)
        # Note: self._default_settings is defined in class body but we want instance copy if creating new.
        # Actually in previous edit I moved definition to init but `_build_default_settings` call remained.
        
        base_defaults = {
            "astrocfg": {
                "language": "en",
                "houses_system": "P", 
                "zodiactype": "tropical",
                "postype": "geo",
                "planet_in_one_house": 0,
                "round_aspects": 0,
            }
        }
        self._default_settings = default_settings or base_defaults
        self._cache: Dict[str, ChartResult] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_chart(self, request: ChartRequest) -> ChartResult:
        """Generate a chart with OpenAstro2 based on the supplied request."""
        primary = self._to_openastro_event(request.primary_event)
        secondary = (
            self._to_openastro_event(request.reference_event)
            if request.reference_event
            else None
        )

        # Merge request settings on top of defaults
        chart_settings = self.default_settings()
        if request.settings:
            # Deep merge logic for 'astrocfg' etc
            for key, val in request.settings.items():
                if isinstance(val, dict) and key in chart_settings:
                    chart_settings[key].update(val)
                else:
                    chart_settings[key] = val
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug("Generating chart", extra={
                "chart_type": request.chart_type,
                "has_secondary": bool(secondary),
            })
            
        # Check Cache
        # Serialize request for key (naive but functional)
        # We assume ChartRequest is dataclass so repr is stable-ish, but let's use a specific key method
        cache_key = f"{request}" # Dataclass repr includes all fields
        if cache_key in self._cache:
             self._logger.info("Serving chart from cache.")
             return self._cache[cache_key]

        try:
            # Validate inputs before calling external lib
            self._validate_request(request)

            chart_args: List[Any] = [primary]
            if secondary is not None:
                chart_args.append(secondary)
            chart = openAstro(*chart_args, type=request.chart_type, settings=chart_settings)
            self._prime_chart(chart)
        except Exception as exc:  # pragma: no cover - wraps upstream errors
            self._logger.exception("OpenAstro2 raised an error")
            raise ChartComputationError("OpenAstro2 failed to compute the chart") from exc
        
        result = self._build_chart_result(chart, request)
        self._cache[cache_key] = result
        return result

    def _validate_request(self, request: ChartRequest) -> None:
        """Validate request parameters before calling OpenAstro."""
        if not request.primary_event.location:
             raise ValueError("Location is required")
        # Add more validation if needed

    def list_house_systems(self) -> Dict[str, str]:
        """Return a dictionary of supported house systems and their labels."""
        return self.HOUSE_SYSTEM_LABELS.copy()

    def default_settings(self) -> Dict[str, Any]:
        """Expose a safe copy of the default OpenAstro settings template."""
        return copy.deepcopy(self._default_settings)
    
    def configure_defaults(self, new_defaults: Dict[str, Any]) -> None:
        """Update the base default settings for the service instance."""
        # Deep merge new settings into existing defaults
        for section, values in new_defaults.items():
            if section not in self._default_settings:
                self._default_settings[section] = {}
            if isinstance(values, dict):
                self._default_settings[section].update(values)
            else:
                self._default_settings[section] = values

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _check_availability(self) -> None:
        """
        Checks if openastro2 is available and raises an error if not.
        
        Raises:
            OpenAstroNotAvailableError: If openastro cannot be imported.
        """
        if openAstro is None:
            raise OpenAstroNotAvailableError(
                "openastro2 is not installed. Ensure 'pip install openastro2' "
                "has been run on this system."
            )

    def _to_openastro_event(self, event: AstrologyEvent) -> Dict[str, Any]:
        """Convert an AstrologyEvent into kwargs for openAstro.event()."""
        payload = event.to_openastro_kwargs()
        return openAstro.event(**payload)

    def _build_chart_result(self, chart: Any, request: ChartRequest) -> ChartResult:
        planet_data = self._planet_data(chart)
        planets = self._extract_planet_positions(chart, planet_data)
        houses = self._extract_house_positions(chart)
        aspects = self._extract_aspects(chart)
        svg_data = self._maybe_render_svg(chart, request.include_svg)
        raw_payload = self._extract_raw_payload(chart, planet_data)
        raw_payload = self._extract_raw_payload(chart, planet_data)
        
        # Try to get JD from chart, or calculate it manually
        julian_day = getattr(chart, "julian_day_ut", None)
        if julian_day is None and swe is not None:
             # Calculate from request event (assumed UTC normalized by to_openastro_kwargs logic)
             # But request.primary_event.timestamp is the source of truth
             dt = request.primary_event.timestamp
             # Convert to UTC
             from datetime import timezone
             if dt.tzinfo is None:
                 dt = dt.replace(tzinfo=timezone.utc)
             else:
                 dt = dt.astimezone(timezone.utc)
                 
             hour_dec = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
             try:
                 julian_day = swe.julday(dt.year, dt.month, dt.day, hour_dec)
             except Exception:
                 self._logger.warning("Failed to calculate manual Julian Day via swisseph")
        if julian_day is None:
             self._logger.warning(f"Julian Day missing. Chart attributes: {dir(chart)}")

        return ChartResult(
            chart_type=request.chart_type,
            planet_positions=planets,
            house_positions=houses,
            aspect_summary=aspects,
            svg_document=svg_data,
            raw_payload=raw_payload,
            julian_day=julian_day,
        )

    def _prime_chart(self, chart: Any) -> None:
        """Ensure OpenAstro2 populates computed attributes before extraction."""
        calc_method = getattr(chart, "calcAstro", None)
        if not callable(calc_method):
            self._logger.warning("OpenAstro2 chart is missing calcAstro()")
            return
        try:
            calc_method()
        except Exception as exc:  # pragma: no cover - relies on third party
            self._logger.exception("OpenAstro2.calcAstro failed")
            raise ChartComputationError("OpenAstro2 failed to finalize the chart") from exc

    def _planet_data(self, chart: Any) -> Dict[str, Dict[str, Any]]:
        dict_method = getattr(chart, "makePlanetDict", None)
        if callable(dict_method):
            try:
                data = dict_method()
                if isinstance(data, dict):
                    return data
            except Exception:  # pragma: no cover - defensive logging only
                self._logger.debug("OpenAstro2.makePlanetDict failed", exc_info=True)
        return {}

    def _extract_planet_positions(self, chart: Any, planet_data: Dict[str, Dict[str, Any]]) -> List[PlanetPosition]:
        positions: List[PlanetPosition] = []

        # Get retrograde list from chart (indexed by planet order)
        retrograde_list = getattr(chart, "planets_retrograde", [])
        speed_list = getattr(chart, "planet_lon_speed", [])

        if planet_data:
            for idx, (fallback_name, payload) in enumerate(planet_data.items()):
                try:
                    degree_val = float(payload.get("planets_degree_ut", 0.0)) % 360
                except (TypeError, ValueError):
                    continue
                sign_idx = payload.get("planets_sign")
                raw_name = payload.get("planets_name") or fallback_name
                name = raw_name.title() if raw_name else "Unknown"

                # Extract retrograde status
                is_retro = None
                if idx < len(retrograde_list):
                    is_retro = bool(retrograde_list[idx])

                # Extract speed
                speed = None
                if idx < len(speed_list):
                    try:
                        speed = float(speed_list[idx])
                    except (TypeError, ValueError):
                        pass

                positions.append(
                    PlanetPosition(
                        name=name,
                        degree=degree_val,
                        sign_index=int(sign_idx) if isinstance(sign_idx, (int, float)) else None,
                        speed=speed,
                        _retrograde=is_retro,
                    )
                )
        if positions:
            return positions

        # Fallback: extract from chart attributes directly
        names = getattr(chart, "planets_name", [])
        degrees = getattr(chart, "planets_degree_ut", [])
        signs = getattr(chart, "planets_sign", [])

        for idx, degree in enumerate(degrees):
            name = names[idx] if idx < len(names) else f"Planet {idx}"
            sign_idx = signs[idx] if idx < len(signs) else None
            try:
                degree_val = float(degree)
            except (TypeError, ValueError):
                continue

            # Extract retrograde status
            is_retro = None
            if idx < len(retrograde_list):
                is_retro = bool(retrograde_list[idx])

            # Extract speed
            speed = None
            if idx < len(speed_list):
                try:
                    speed = float(speed_list[idx])
                except (TypeError, ValueError):
                    pass

            positions.append(
                PlanetPosition(
                    name=name,
                    degree=degree_val % 360,
                    sign_index=int(sign_idx) if sign_idx is not None else None,
                    speed=speed,
                    _retrograde=is_retro,
                )
            )
        return positions

    def _extract_house_positions(self, chart: Any) -> List[HousePosition]:
        houses = getattr(chart, "houses_degree_ut", [])
        house_positions: List[HousePosition] = []
        for idx, degree in enumerate(houses):
            try:
                degree_val = float(degree)
            except (TypeError, ValueError):
                continue
            house_positions.append(HousePosition(number=idx + 1, degree=degree_val % 360))
        return house_positions

    def _extract_aspects(self, chart: Any) -> Dict[str, Any]:
        aspect_data = getattr(chart, "planets_aspects_list", None)
        if aspect_data:
            return {"planets_aspects": aspect_data}
        raw_aspects = getattr(chart, "planets_aspects", None)
        if raw_aspects:
            return {"planets_aspects": raw_aspects}
        aspect_text = getattr(chart, "aspect_all_str", None)
        if aspect_text:
            return {"aspect_text": aspect_text}
        return {}

    def _maybe_render_svg(self, chart: Any, include_svg: bool) -> Optional[str]:
        if not include_svg:
            return None
        render_method = getattr(chart, "makeSVG2", None)
        if callable(render_method):
            try:
                return str(render_method())
            except Exception:
                self._logger.exception("Failed to render SVG via OpenAstro2")
        return None

    def _extract_raw_payload(self, chart: Any, planet_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        keys = (
            "planets_degree_ut",
            "planets_sign",
            "planets_retrograde",
            "houses_degree_ut",
            "houses_sign",
            "lunar_phase",
        )
        payload: Dict[str, Any] = {}
        for key in keys:
            value = getattr(chart, key, None)
            if value is not None:
                payload[key] = value
        if planet_data:
            payload["planets_detail"] = planet_data
        return payload