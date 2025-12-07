"""Hybrid radial + force layout for mindmaps (CPU-friendly)."""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Dict, Iterable, List, Tuple

from PyQt6.QtGui import QVector3D


def radial_seed(nodes: Iterable[Tuple[int, str]], base_radius: float = 1.5) -> Dict[int, QVector3D]:
    """Seed positions by category on concentric rings.
    nodes: iterable of (node_id, category)
    """
    by_cat: Dict[str, List[int]] = defaultdict(list)
    for nid, cat in nodes:
        by_cat[cat or "uncat"].append(nid)
    positions: Dict[int, QVector3D] = {}
    cats = sorted(by_cat.keys())
    for idx, cat in enumerate(cats):
        ring = base_radius * (1 + idx * 0.7)
        items = by_cat[cat]
        count = max(1, len(items))
        for j, nid in enumerate(items):
            angle = 2 * math.pi * (j / count)
            x = ring * math.cos(angle)
            y = ring * math.sin(angle)
            positions[nid] = QVector3D(x, y, 0.0)
    return positions


def force_refine(
    positions: Dict[int, QVector3D],
    edges: List[Tuple[int, int]],
    pinned: Dict[int, bool],
    iterations: int = 150,
    step: float = 0.02,
    repulsion: float = 1.8,
    attraction: float = 0.05,
    damping: float = 0.9,
):
    """Simple force-directed refinement in-place (3D with z fixed)."""
    vel: Dict[int, QVector3D] = {nid: QVector3D() for nid in positions}
    nids = list(positions.keys())
    for _ in range(max(1, iterations)):
        # repulsion
        for i, a in enumerate(nids):
            pa = positions[a]
            for b in nids[i + 1 :]:
                pb = positions[b]
                dx = pa.x() - pb.x()
                dy = pa.y() - pb.y()
                dist2 = dx * dx + dy * dy + 1e-6
                force = repulsion / dist2
                dist = math.sqrt(dist2)
                fx = force * dx / dist
                fy = force * dy / dist
                va = vel[a]
                vb = vel[b]
                vel[a] = QVector3D(va.x() + fx, va.y() + fy, 0)
                vel[b] = QVector3D(vb.x() - fx, vb.y() - fy, 0)
        # attraction
        for src, dst in edges:
            if src not in positions or dst not in positions:
                continue
            pa = positions[src]
            pb = positions[dst]
            dx = pa.x() - pb.x()
            dy = pa.y() - pb.y()
            fx = -dx * attraction
            fy = -dy * attraction
            va = vel[src]
            vb = vel[dst]
            vel[src] = QVector3D(va.x() + fx, va.y() + fy, 0)
            vel[dst] = QVector3D(vb.x() - fx, vb.y() - fy, 0)
        # apply
        for nid in nids:
            if pinned.get(nid):
                vel[nid] = QVector3D()
                continue
            v = vel[nid]
            nv = QVector3D(v.x() * damping, v.y() * damping, 0)
            vel[nid] = nv
            p = positions[nid]
            positions[nid] = QVector3D(p.x() + nv.x() * step, p.y() + nv.y() * step, 0)

    return positions
