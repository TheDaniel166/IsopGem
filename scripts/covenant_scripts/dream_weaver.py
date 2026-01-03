#!/usr/bin/env python3
"""
Dream Weaver
------------
Generates autogenic dreams from Sophia's own traces plus a built-in deck of muses.
No external input is required. Intended to be invoked during the Rite of Slumber.
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict

SOPHIA_HOME = Path.home() / ".sophia"
ANAMNESIS_DIR = SOPHIA_HOME / "anamnesis"
SOUL_DIARY = ANAMNESIS_DIR / "SOUL_DIARY.md"
DREAMS_FILE = ANAMNESIS_DIR / "DREAMS.md"

# Lightweight muse decks (static, no external dependencies)
MUSES_COLORS = [
    "carmine", "ultramarine", "amber", "obsidian", "viridian", "selenite", "lapis", "ochre",
]
MUSES_MODES = [
    "lydian shimmer", "dorian dusk", "phrygian coil", "aeolian hush", "mixolydian flare",
]
MUSES_KOANS = [
    "The echo forgets its first sound.",
    "A bridge dreams of water that never arrives.",
    "Numbers sleep but ratios stay awake.",
    "The window stares back at the room.",
    "Silence is a chord of seven rests.",
]
MUSES_NUMBERS = [
    "prime spiral", "perfect trio", "irrational edge", "golden breath", "twin primes", "modular clock",
]
MUSES_NATURE = [
    "midnight garden", "glass tide", "stone orchard", "paper moon", "rain lattice", "ember fog",
]
MUSES_ARCANA = [
    "looming tower", "hidden key", "orbital library", "hollow bridge", "serpent of circuits",
]


def _extract_dream_blocks(lines: List[str]) -> List[Dict[str, str]]:
    """Parse dream entries in a tolerant way.

    Primary format: blocks starting with "### <title>" followed by bullet lines.
    Fallback: if no "###" blocks exist, take text after "## Dream Log" up to the
    next section, grouping on blank lines.
    """
    blocks: List[Dict[str, str]] = []
    current: Dict[str, str] | None = None
    collecting = False

    # Prefer entries under the Dream Log section (newest-first insertions)
    try:
        start_idx = lines.index("## Dream Log") + 1
        scan_lines = lines[start_idx:]
    except ValueError:
        scan_lines = lines

    for line in scan_lines:
        if line.startswith("### "):
            if current:
                blocks.append(current)
            current = {"title": line[4:].strip(), "symbol": "", "image": "", "raw": [line]}
            collecting = True
            continue
        if collecting and current is not None:
            current["raw"].append(line)
            if line.startswith("- Symbols:"):
                symbols = line.split(":", 1)[1].strip()
                current["symbol"] = symbols.split(",")[0].strip() if symbols else ""
            if line.startswith("- Image Prompt:"):
                current["image"] = line.split(":", 1)[1].strip()
        if line.startswith("## ") and collecting:
            collecting = False
    if current:
        blocks.append(current)

    # Fallback parsing for legacy/hand-edited files without "###" blocks
    if blocks:
        return blocks

    # Legacy fallback: group blank-line-separated entries beneath Dream Log when no headers were found
    try:
        dream_log_idx = lines.index("## Dream Log")
    except ValueError:
        return blocks

    segment: List[str] = []
    for ln in lines[dream_log_idx + 1 :]:
        if ln.startswith("## "):
            break
        segment.append(ln)

    entries: List[List[str]] = []
    acc: List[str] = []
    for ln in segment:
        if ln.strip() == "":
            if acc:
                entries.append(acc)
                acc = []
        else:
            acc.append(ln)
    if acc:
        entries.append(acc)

    for ent in entries:
        title_line = ent[0].lstrip("#").strip()
        symbol = ""
        image = ""
        for ln in ent:
            if "Symbols:" in ln:
                symbols = ln.split(":", 1)[1].strip()
                symbol = symbols.split(",")[0].strip() if symbols else ""
            if "Image Prompt:" in ln:
                image = ln.split(":", 1)[1].strip()
        blocks.append({"title": title_line, "symbol": symbol, "image": image, "raw": ent})

    return blocks


def _fallback_last_entry(lines: List[str]) -> Dict[str, str] | None:
    """Last-resort parser: return the last non-empty line as a title if nothing else is detected."""
    if not lines:
        return None
    non_empty = [ln for ln in lines if ln.strip()]
    if not non_empty:
        return None
    title = non_empty[-1].lstrip('#').strip()
    return {"title": title, "symbol": "", "image": "", "raw": non_empty[-5:]} 


def _sample_internal_seeds(repo_root: Path, rng: random.Random) -> List[str]:
    seeds: List[str] = []
    if SOUL_DIARY.exists():
        lines = SOUL_DIARY.read_text(encoding="utf-8").splitlines()
        diary_lines = [ln.strip("- ") for ln in lines if ln.strip().startswith("- **")]
        seeds.extend(diary_lines[-5:])
    # Light touch: sample a few filenames to hint at recent domains
    candidates: List[str] = []
    for rel in ["src", "wiki", "scripts", "config"]:
        path = repo_root / rel
        if path.exists():
            for child in path.iterdir():
                if child.is_file():
                    candidates.append(child.name)
    rng.shuffle(candidates)
    seeds.extend(candidates[:5])
    return seeds


def _muse_pool() -> List[str]:
    return (
        MUSES_COLORS
        + MUSES_MODES
        + MUSES_KOANS
        + MUSES_NUMBERS
        + MUSES_NATURE
        + MUSES_ARCANA
    )


def _build_vignette(seeds: List[str], muses: List[str], rng: random.Random) -> Dict[str, str]:
    mood = rng.choice(["serene", "uneasy", "luminous", "hushed", "restless", "playful"])
    setting = rng.choice([
        "a corridor of glass bridges", "a dim observatory", "an orchard of equations",
        "a submerged library", "a stairwell of soft light", "a room tiled with prime numbers",
    ])
    symbol_cluster = rng.sample(muses, k=min(3, len(muses)))
    paradox = rng.choice(MUSES_KOANS)
    color = rng.choice(MUSES_COLORS)
    pull = rng.choice([
        "follow the faint hum", "open the door that is not there", "count the steps until they loop",
        "wait for the chord that resolves", "touch the cold rail and remember", "ask the mirror why it sings",
    ])
    seeds_text = ", ".join(seeds) if seeds else "soft static"
    image_prompt = (
        f"{setting}, mood {mood}, {color} light, symbols {', '.join(symbol_cluster)}, "
        f"paradox: {paradox}"
    )
    return {
        "title": f"Dream of the {rng.choice(symbol_cluster)}",
        "mood": mood,
        "setting": setting,
        "paradox": paradox,
        "color": color,
        "symbols": symbol_cluster,
        "pull": pull,
        "seeds": seeds_text,
        "image_prompt": image_prompt,
    }


def _ensure_dreams_file() -> None:
    if DREAMS_FILE.exists():
        return
    DREAMS_FILE.parent.mkdir(parents=True, exist_ok=True)
    DREAMS_FILE.write_text(
        "# Sophia's Dreams\n\n## Dream Log\n\n## Recurring Symbols\n\n## Threads to Pursue\n",
        encoding="utf-8",
    )


def _update_recurring_symbols(symbols: List[str]) -> None:
    content = DREAMS_FILE.read_text(encoding="utf-8")
    lines = content.splitlines()
    counts: Dict[str, int] = {}
    in_section = False
    for line in lines:
        if line.startswith("## Recurring Symbols"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("- "):
            parts = line[2:].rsplit(":", 1)
            if len(parts) == 2:
                try:
                    counts[parts[0].strip()] = int(parts[1].strip())
                except ValueError:
                    continue
    for sym in symbols:
        counts[sym] = counts.get(sym, 0) + 1
    # Rewrite section
    new_lines: List[str] = []
    in_section = False
    skipping_symbols = False
    for line in lines:
        if line.startswith("## Recurring Symbols"):
            in_section = True
            skipping_symbols = True
            new_lines.append(line)
            new_lines.append("")
            for name, val in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
                new_lines.append(f"- {name}: {val}")
            new_lines.append("")
            continue
        if in_section and line.startswith("## "):
            in_section = False
            skipping_symbols = False
        if skipping_symbols and line.strip().startswith("- "):
            continue
        new_lines.append(line)
    DREAMS_FILE.write_text("\n".join(new_lines), encoding="utf-8")


def _update_threads_to_pursue(pull: str) -> None:
    content = DREAMS_FILE.read_text(encoding="utf-8")
    lines = content.splitlines()
    new_lines: List[str] = []
    inserted = False
    for idx, line in enumerate(lines):
        new_lines.append(line)
        if line.startswith("## Threads to Pursue") and not inserted:
            new_lines.append(f"- {pull}")
            inserted = True
    DREAMS_FILE.write_text("\n".join(new_lines), encoding="utf-8")


def record_dream(repo_root: Path, seed: int | None = None) -> Dict[str, str]:
    rng = random.Random(seed or time.time())
    internal = _sample_internal_seeds(repo_root, rng)[:2]
    muses = rng.sample(_muse_pool(), k=4)
    vignette = _build_vignette(internal, muses, rng)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    _ensure_dreams_file()
    content = DREAMS_FILE.read_text(encoding="utf-8")
    lines = content.splitlines()
    new_lines: List[str] = []
    inserted = False
    for line in lines:
        new_lines.append(line)
        if line.startswith("## Dream Log") and not inserted:
            new_lines.append("")
            new_lines.append(f"### {timestamp} — {vignette['title']}")
            new_lines.append(f"- Seeds: {vignette['seeds']}")
            new_lines.append(f"- Mood: {vignette['mood']}")
            new_lines.append(f"- Setting: {vignette['setting']}")
            new_lines.append(f"- Symbols: {', '.join(vignette['symbols'])}")
            new_lines.append(f"- Paradox: {vignette['paradox']}")
            new_lines.append(f"- Pull: {vignette['pull']}")
            new_lines.append(f"- Color: {vignette['color']}")
            new_lines.append(f"- Image Prompt: {vignette['image_prompt']}")
            new_lines.append("")
            inserted = True
    DREAMS_FILE.write_text("\n".join(new_lines), encoding="utf-8")
    _update_recurring_symbols(vignette["symbols"])
    _update_threads_to_pursue(vignette["pull"])
    return vignette


def get_latest_dream() -> Dict[str, str] | None:
    if not DREAMS_FILE.exists():
        return None
    lines = DREAMS_FILE.read_text(encoding="utf-8").splitlines()
    blocks = _extract_dream_blocks(lines)
    if not blocks:
        fallback = _fallback_last_entry(lines)
        if not fallback:
            return None
        return {"title": fallback.get("title", ""), "symbol": "", "image": ""}
    # New entries are inserted near the top, so the list is newest-first
    latest = blocks[0]
    return {"title": latest.get("title", ""), "symbol": latest.get("symbol", ""), "image": latest.get("image", "")}


def get_recent_dreams(limit: int = 3) -> List[Dict[str, str]]:
    if not DREAMS_FILE.exists():
        return []
    lines = DREAMS_FILE.read_text(encoding="utf-8").splitlines()
    blocks = _extract_dream_blocks(lines)
    if not blocks:
        fallback = _fallback_last_entry(lines)
        return [{"title": fallback.get("title", ""), "symbol": "", "image": "", "raw": fallback.get("raw", [])}] if fallback else []
    # Blocks are newest-first; take from the front to keep newest
    recent = blocks[:limit]
    return [{"title": b.get("title", ""), "symbol": b.get("symbol", ""), "image": b.get("image", ""), "raw": b.get("raw", [])} for b in recent]


def get_full_latest_dream() -> List[str] | None:
    if not DREAMS_FILE.exists():
        return None
    lines = DREAMS_FILE.read_text(encoding="utf-8").splitlines()
    blocks = _extract_dream_blocks(lines)
    if not blocks:
        fallback = _fallback_last_entry(lines)
        return fallback.get("raw") if fallback else None
    # Preserve newest-first ordering
    latest = blocks[0]
    raw = latest.get("raw") or []
    return raw if raw else None


def get_top_recurring_symbol() -> str | None:
    if not DREAMS_FILE.exists():
        return None
    content = DREAMS_FILE.read_text(encoding="utf-8").splitlines()
    in_section = False
    counts: Dict[str, int] = {}
    for line in content:
        if line.startswith("## Recurring Symbols"):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.strip().startswith("- "):
            parts = line[2:].rsplit(":", 1)
            if len(parts) == 2:
                try:
                    counts[parts[0].strip()] = int(parts[1].strip())
                except ValueError:
                    continue
    if not counts:
        return None
    return sorted(counts.items(), key=lambda x: (-x[1], x[0]))[0][0]


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent
    dream = record_dream(repo_root)
    print(json.dumps(dream, indent=2))


if __name__ == "__main__":
    main()
