from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


STATE_VERSION = 1
DEFAULT_MAX_HISTORY = 200


@dataclass(frozen=True)
class CalculatorState:
    version: int = STATE_VERSION
    angle_mode: str = "RAD"  # "RAD" or "DEG"
    memory: float = 0.0
    history: Optional[List[str]] = None  # list of rendered entries "expr = result"

    def __post_init__(self):
        object.__setattr__(self, "history", list(self.history or []))


def default_state() -> CalculatorState:
    return CalculatorState(history=[])


def get_default_state_path(app_name: str = "isopgem") -> Path:
    """Return user-specific state path using XDG base directory.

    Linux target:
    - $XDG_STATE_HOME/<app_name>/calculator_state.json
    - fallback: ~/.local/state/<app_name>/calculator_state.json
    """

    xdg_state_home = os.environ.get("XDG_STATE_HOME")
    base = Path(xdg_state_home) if xdg_state_home else (Path.home() / ".local" / "state")
    return base / app_name / "calculator_state.json"


def _ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _coerce_angle_mode(value: Any) -> str:
    if str(value).upper() == "DEG":
        return "DEG"
    return "RAD"


def _coerce_float(value: Any, *, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _coerce_history(value: Any, *, max_items: int) -> List[str]:
    if not isinstance(value, list):
        return []
    out: List[str] = []
    for item in value:
        if isinstance(item, str):
            out.append(item)
    return out[:max_items]


def load_state(path: Path, *, max_history: int = DEFAULT_MAX_HISTORY) -> CalculatorState:
    """Load state from JSON.

    Returns default state if missing/corrupt/unexpected.
    """

    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return default_state()
    except OSError:
        return default_state()

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return default_state()

    if not isinstance(payload, dict):
        return default_state()

    version = payload.get("version", STATE_VERSION)
    try:
        version_i = int(version)
    except Exception:
        version_i = STATE_VERSION

    # For now, v1 is the only supported shape; tolerate future keys.
    angle_mode = _coerce_angle_mode(payload.get("angle_mode", "RAD"))
    memory = _coerce_float(payload.get("memory", 0.0), default=0.0)
    history = _coerce_history(payload.get("history", []), max_items=max_history)

    return CalculatorState(version=version_i, angle_mode=angle_mode, memory=memory, history=history)


def save_state(state: CalculatorState, path: Path, *, max_history: int = DEFAULT_MAX_HISTORY) -> None:
    """Persist state to JSON.

    Writes atomically (via .tmp + replace) when possible.
    """

    _ensure_parent_dir(path)

    payload: Dict[str, Any] = {
        "version": int(state.version),
        "angle_mode": _coerce_angle_mode(state.angle_mode),
        "memory": float(state.memory),
        "history": list((state.history or [])[:max_history]),
    }

    tmp = path.with_suffix(path.suffix + ".tmp")
    data = json.dumps(payload, indent=2, sort_keys=True)
    tmp.write_text(data + "\n", encoding="utf-8")
    tmp.replace(path)
