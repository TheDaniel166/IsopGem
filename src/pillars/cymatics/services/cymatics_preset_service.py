"""Preset management service for cymatics configurations.

Saves and loads cymatics parameter presets as JSON files in the
user's config directory (~/.config/isopgem/cymatics_presets/).
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, fields
from pathlib import Path
from typing import List, Optional

from shared.config import get_config

from ..models import (
    ColorGradient,
    CymaticsPreset,
    PlateShape,
    SimulationParams,
)


class CymaticsPresetService:
    """Manages saving and loading of cymatics parameter presets.

    Presets are stored as JSON files in ~/.config/isopgem/cymatics_presets/
    with versioning for future migration support.
    """

    PRESET_VERSION = 1

    def __init__(self, preset_dir: Path | None = None):
        """Initialize preset service.

        Args:
            preset_dir: Optional custom preset directory. If None,
                       uses default XDG config path.
        """
        if preset_dir is None:
            config = get_config()
            self._preset_dir = Path(config.paths.user_config) / "cymatics_presets"
        else:
            self._preset_dir = preset_dir

        self._preset_dir.mkdir(parents=True, exist_ok=True)

    def save_preset(self, preset: CymaticsPreset) -> Path:
        """Save preset to JSON file.

        Args:
            preset: Preset to save

        Returns:
            Path to saved preset file
        """
        # Update metadata
        preset.created_at = time.time()
        preset.version = self.PRESET_VERSION

        filename = f"{self._sanitize_name(preset.name)}.json"
        path = self._preset_dir / filename

        # Convert to dict, handling enums
        data = self._preset_to_dict(preset)

        # Atomic write via temp file
        tmp_path = path.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        tmp_path.replace(path)

        return path

    def load_preset(self, name: str) -> Optional[CymaticsPreset]:
        """Load preset from JSON file.

        Args:
            name: Preset name (without .json extension)

        Returns:
            Loaded preset or None if not found
        """
        filename = f"{self._sanitize_name(name)}.json"
        path = self._preset_dir / filename

        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return self._dict_to_preset(data)
        except (json.JSONDecodeError, KeyError, ValueError):
            return None

    def list_presets(self) -> List[str]:
        """List all available preset names.

        Returns:
            List of preset names (without extension)
        """
        return sorted([p.stem for p in self._preset_dir.glob("*.json")])

    def delete_preset(self, name: str) -> bool:
        """Delete a preset file.

        Args:
            name: Preset name to delete

        Returns:
            True if deleted, False if not found
        """
        filename = f"{self._sanitize_name(name)}.json"
        path = self._preset_dir / filename

        if path.exists():
            path.unlink()
            return True
        return False

    def get_preset_info(self, name: str) -> Optional[dict]:
        """Get preset metadata without fully loading it.

        Args:
            name: Preset name

        Returns:
            Dictionary with name, description, created_at, tags
        """
        preset = self.load_preset(name)
        if preset is None:
            return None

        return {
            "name": preset.name,
            "description": preset.description,
            "created_at": preset.created_at,
            "tags": preset.tags,
            "plate_shape": preset.params.plate_shape.name,
        }

    def _sanitize_name(self, name: str) -> str:
        """Sanitize preset name for filesystem.

        Replaces problematic characters with underscores.
        """
        return "".join(
            c if c.isalnum() or c in "-_ " else "_" for c in name
        ).strip()

    def _preset_to_dict(self, preset: CymaticsPreset) -> dict:
        """Convert preset to JSON-serializable dictionary."""
        params_dict = {}

        # Get all fields from SimulationParams
        for field in fields(preset.params):
            value = getattr(preset.params, field.name)

            # Convert enums to strings
            if isinstance(value, PlateShape):
                params_dict[field.name] = value.name
            elif isinstance(value, ColorGradient):
                params_dict[field.name] = value.name
            else:
                params_dict[field.name] = value

        return {
            "version": preset.version,
            "name": preset.name,
            "description": preset.description,
            "created_at": preset.created_at,
            "tags": preset.tags,
            "params": params_dict,
        }

    def _dict_to_preset(self, data: dict) -> CymaticsPreset:
        """Convert dictionary to CymaticsPreset."""
        params_data = data.get("params", {})

        # Convert enum strings back to enums
        if "plate_shape" in params_data:
            params_data["plate_shape"] = PlateShape[params_data["plate_shape"]]
        if "color_gradient" in params_data:
            params_data["color_gradient"] = ColorGradient[params_data["color_gradient"]]

        # Build SimulationParams, ignoring unknown fields
        valid_fields = {f.name for f in fields(SimulationParams)}
        filtered_params = {k: v for k, v in params_data.items() if k in valid_fields}
        params = SimulationParams(**filtered_params)

        return CymaticsPreset(
            name=data.get("name", "Unnamed"),
            params=params,
            description=data.get("description", ""),
            version=data.get("version", 1),
            created_at=data.get("created_at", 0.0),
            tags=data.get("tags", []),
        )


# Built-in preset definitions
BUILTIN_PRESETS = [
    CymaticsPreset(
        name="Classic Chladni",
        description="Traditional circular plate Chladni pattern",
        params=SimulationParams(
            grid_size=220,
            mode_m=3,
            mode_n=2,
            secondary_m=4,
            secondary_n=3,
            mix=0.25,
            damping=0.5,
            plate_shape=PlateShape.CIRCULAR,
            color_gradient=ColorGradient.GRAYSCALE,
        ),
        tags=["classic", "circular"],
    ),
    CymaticsPreset(
        name="Hexagonal Harmony",
        description="Three-fold symmetric hexagonal plate pattern",
        params=SimulationParams(
            grid_size=200,
            mode_m=4,
            mode_n=4,
            secondary_m=2,
            secondary_n=2,
            mix=0.3,
            damping=0.0,
            plate_shape=PlateShape.HEXAGONAL,
            color_gradient=ColorGradient.PLASMA,
        ),
        tags=["hexagonal", "symmetric"],
    ),
    CymaticsPreset(
        name="High Frequency",
        description="Complex high-mode interference pattern",
        params=SimulationParams(
            grid_size=280,
            mode_m=8,
            mode_n=7,
            secondary_m=9,
            secondary_n=8,
            mix=0.4,
            damping=0.3,
            plate_shape=PlateShape.RECTANGULAR,
            color_gradient=ColorGradient.VIRIDIS,
        ),
        tags=["complex", "high-frequency"],
    ),
    CymaticsPreset(
        name="Ocean Waves",
        description="Low-frequency ocean-themed pattern",
        params=SimulationParams(
            grid_size=180,
            mode_m=2,
            mode_n=3,
            secondary_m=3,
            secondary_n=2,
            mix=0.5,
            damping=1.0,
            plate_shape=PlateShape.CIRCULAR,
            color_gradient=ColorGradient.OCEAN,
        ),
        tags=["simple", "ocean"],
    ),
]
