from __future__ import annotations

from pathlib import Path

from src.shared.utils.calculator_persistence import CalculatorState, load_state, save_state


def test_load_missing_returns_default(tmp_path: Path):
    state = load_state(tmp_path / "missing.json")
    assert state.angle_mode == "RAD"
    assert state.memory == 0.0
    assert state.history == []


def test_save_then_load_round_trip(tmp_path: Path):
    path = tmp_path / "state.json"
    original = CalculatorState(angle_mode="DEG", memory=12.5, history=["1+1 = 2", "sin(90deg) = 1"])
    save_state(original, path)
    loaded = load_state(path)
    assert loaded.angle_mode == "DEG"
    assert loaded.memory == 12.5
    assert loaded.history[:2] == original.history


def test_load_corrupt_json_falls_back(tmp_path: Path):
    path = tmp_path / "state.json"
    path.write_text("{not json}", encoding="utf-8")
    loaded = load_state(path)
    assert loaded.angle_mode == "RAD"
    assert loaded.memory == 0.0
    assert loaded.history == []


def test_history_is_capped(tmp_path: Path):
    path = tmp_path / "state.json"
    history = [f"{i}+{i} = {2*i}" for i in range(500)]
    save_state(CalculatorState(angle_mode="RAD", memory=0.0, history=history), path, max_history=50)
    loaded = load_state(path, max_history=50)
    assert len(loaded.history) == 50
