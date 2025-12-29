"""Repository for accessing chart interpretation data."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from ..models.interpretation_models import RichInterpretationContent

logger = logging.getLogger(__name__)

class InterpretationRepository:
    """Manages access to interpretation texts stored in JSON files."""

    def __init__(self, data_dir: Optional[Path] = None):
        """
          init   logic.
        
        Args:
            data_dir: Description of data_dir.
        
        """
        if data_dir is None:
            # Default to src/pillars/astrology/data/interpretations
            current_file = Path(__file__)
            # Adjust path: repositories/ -> data/interpretations/
            self.data_dir = current_file.parent.parent / "data" / "interpretations"
        else:
            self.data_dir = data_dir
        
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        """Ensure the data directory exists."""
        if not self.data_dir.exists():
            logger.warning(f"Interpretation data directory not found: {self.data_dir}")
            # We don't raise here, to allow for graceful degradation (empty reports)

    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load a JSON file from the data directory, with caching."""
        if filename in self._cache:
            return self._cache[filename]

        file_path = self.data_dir / filename
        if not file_path.exists():
            logger.warning(f"Interpretation file missing: {file_path}")
            return {}

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._cache[filename] = data
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode {filename}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return {}


    def _parse_content(self, raw: Any) -> Optional[RichInterpretationContent]:
        """Convert raw JSON data into RichInterpretationContent."""
        if not raw:
            return None
        
        if isinstance(raw, str):
            return RichInterpretationContent(text=raw)
            
        if isinstance(raw, dict):
            # Safe extraction with defaults
            return RichInterpretationContent(
                text=raw.get("text", "") or raw.get("body", "") or raw.get("essence", "No text available."),
                archetype=raw.get("archetype"),
                essence=raw.get("essence"),
                shadow=raw.get("shadow"),
                gift=raw.get("gift"),
                alchemical_process=raw.get("alchemical_process"),
                keywords=raw.get("keywords", [])
            )
            
        return None

    def get_planet_sign_text(self, planet: str, sign: str) -> Optional[RichInterpretationContent]:
        """Get text for a planet in a sign."""
        data = self._load_json("planets_in_signs.json")
        planet_data = data.get(planet, {})
        return self._parse_content(planet_data.get(sign))

    def get_planet_house_text(self, planet: str, house: int) -> Optional[RichInterpretationContent]:
        """Get text for a planet in a house."""
        data = self._load_json("planets_in_houses.json")
        planet_data = data.get(planet, {})
        return self._parse_content(planet_data.get(str(house)))

    def get_planet_sign_house_text(self, planet: str, sign: str, house: int) -> Optional[RichInterpretationContent]:
        """Get text for the combinatorial triad (Planet + Sign + House)."""
        data = self._load_json("combinatorial.json")
        try:
            raw = data.get(planet, {}).get(sign, {}).get(str(house))
            return self._parse_content(raw)
        except (AttributeError, TypeError):
            return None

    def get_aspect_text(self, planet_a: str, planet_b: str, aspect_name: str) -> Optional[RichInterpretationContent]:
        """Get text for an aspect between two planets."""
        data = self._load_json("aspects.json")
        aspect_key = aspect_name.lower().replace(" ", "_")
        aspect_data = data.get(aspect_key, {})
        
        # Try A -> B
        if raw := aspect_data.get(planet_a, {}).get(planet_b):
            return self._parse_content(raw)
            
        # Try B -> A
        if raw := aspect_data.get(planet_b, {}).get(planet_a):
            return self._parse_content(raw)
            
        return None

    def get_transit_text(self, transiting_planet: str, natal_planet: str, aspect_name: str) -> Optional[RichInterpretationContent]:
        """
        Get text for a transiting planet aspecting a natal planet.
        """
        data = self._load_json("transits.json")
        key = f"{transiting_planet}:{aspect_name}:{natal_planet}".lower().replace(" ", "_")
        # Structure is usually key-value or nested. 
        # For simplicity in Phase 3, we try nested: transiting -> aspect -> natal
        # Or flattened key. Let's try nested.
        try:
             raw = data.get(transiting_planet.lower(), {}).get(aspect_name.lower(), {}).get(natal_planet.lower())
             return self._parse_content(raw)
        except (AttributeError, TypeError):
             return None

    def get_synastry_text(self, planet_a: str, planet_b: str, aspect_name: str) -> Optional[RichInterpretationContent]:
        """
        Get text for synastry aspect (Inter-aspects).
        """
        data = self._load_json("synastry.json")
        # Synastry is usually symmetric conceptually, but text might differ based on who is A and who is B.
        # "Your Sun aspecting their Moon"
        try:
            raw = data.get(planet_a.lower(), {}).get(aspect_name.lower(), {}).get(planet_b.lower())
            return self._parse_content(raw)
        except (AttributeError, TypeError):
            return None