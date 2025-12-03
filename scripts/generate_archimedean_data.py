"""Fetch canonical Archimedean solid data from dmccooey.com and emit Python module."""
from __future__ import annotations

import math
import pathlib
from typing import Dict, List, Tuple

import requests

BASE_URL = "https://dmccooey.com/polyhedra/{name}.txt"
HEADERS = {"User-Agent": "Mozilla/5.0 (GeometryHub)"}

SOLIDS = {
    "cuboctahedron": {
        "remote": "Cuboctahedron",
        "name": "Cuboctahedron",
    },
    "truncated_tetrahedron": {
        "remote": "TruncatedTetrahedron",
        "name": "Truncated Tetrahedron",
    },
    "truncated_cube": {
        "remote": "TruncatedCube",
        "name": "Truncated Cube",
    },
    "truncated_octahedron": {
        "remote": "TruncatedOctahedron",
        "name": "Truncated Octahedron",
    },
    "rhombicuboctahedron": {
        "remote": "Rhombicuboctahedron",
        "name": "Rhombicuboctahedron",
    },
    "truncated_cuboctahedron": {
        "remote": "TruncatedCuboctahedron",
        "name": "Truncated Cuboctahedron",
    },
    "icosidodecahedron": {
        "remote": "Icosidodecahedron",
        "name": "Icosidodecahedron",
    },
    "truncated_dodecahedron": {
        "remote": "TruncatedDodecahedron",
        "name": "Truncated Dodecahedron",
    },
    "truncated_icosahedron": {
        "remote": "TruncatedIcosahedron",
        "name": "Truncated Icosahedron",
    },
    "rhombicosidodecahedron": {
        "remote": "Rhombicosidodecahedron",
        "name": "Rhombicosidodecahedron",
    },
    "truncated_icosidodecahedron": {
        "remote": "TruncatedIcosidodecahedron",
        "name": "Truncated Icosidodecahedron",
    },
    "snub_cube": {
        "remote": "LsnubCube",
        "name": "Snub Cube",
    },
    "snub_dodecahedron": {
        "remote": "LsnubDodecahedron",
        "name": "Snub Dodecahedron",
    },
}

SAFE_GLOBALS = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
DEFAULT_CONSTS = {
    'phi': (1.0 + math.sqrt(5.0)) / 2.0,
    'Phi': (1.0 + math.sqrt(5.0)) / 2.0,
}


def _eval(expr: str, consts: Dict[str, float]) -> float:
    expr = expr.strip()
    return float(eval(expr, {"__builtins__": {}}, {**SAFE_GLOBALS, **consts}))


def parse_solid(text: str) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, ...]]]:
    consts: Dict[str, float] = dict(DEFAULT_CONSTS)
    vertices: List[Tuple[float, float, float]] = []
    faces: List[Tuple[int, ...]] = []
    in_faces = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("Faces"):
            in_faces = True
            continue
        if not in_faces and line.startswith("C") and "=" in line:
            left, _, rest = line.partition("=")
            name = left.strip()
            rhs = rest.strip()
            if "=" in rhs:
                rhs = rhs.split("=")[-1]
            if name in consts:
                continue
            consts[name] = _eval(rhs, consts)
            continue
        if not in_faces and line.startswith("V"):
            name, _, rhs = line.partition("=")
            rhs = rhs.strip().lstrip("(").rstrip(")")
            parts = [p.strip() for p in rhs.split(",")]
            coords = tuple(_eval(part, consts) for part in parts)
            if len(coords) != 3:
                raise ValueError(f"Unexpected vertex coords: {raw_line}")
            vertices.append(coords)  # type: ignore[arg-type]
            continue
        if in_faces and line.startswith("{"):
            body = line.strip("{} ")
            ints = tuple(int(token.strip()) for token in body.split(","))
            faces.append(ints)
    if not vertices or not faces:
        raise ValueError("Failed to parse solid")
    return vertices, faces


def main() -> None:
    data = {}
    for key, meta in SOLIDS.items():
        url = BASE_URL.format(name=meta["remote"])
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        vertices, faces = parse_solid(resp.text)
        data[key] = {
            "name": meta["name"],
            "vertices": vertices,
            "faces": faces,
        }
        print(f"Fetched {key}: {len(vertices)} vertices, {len(faces)} faces")
    target = pathlib.Path(__file__).resolve().parents[1] / "src" / "pillars" / "geometry" / "services" / "archimedean_data.py"
    header = (
        '"""Canonical Archimedean solid datasets auto-generated from dmccooey.com.\n'
        'Do not edit by hand; run scripts/generate_archimedean_data.py instead."""'
    )
    lines = [header]
    lines.append("ARCHIMEDEAN_DATA = {")
    for key, entry in sorted(data.items()):
        lines.append(f"    '{key}': {{")
        lines.append(f"        'name': '{entry['name']}',")
        lines.append("        'vertices': [")
        for vx, vy, vz in entry["vertices"]:
            lines.append(f"            ({vx:.12f}, {vy:.12f}, {vz:.12f}),")
        lines.append("        ],")
        lines.append("        'faces': [")
        for face in entry["faces"]:
            lines.append(f"            {tuple(face)},")
        lines.append("        ],")
        lines.append("    },")
    lines.append("}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {target}")


if __name__ == '__main__':
    main()
