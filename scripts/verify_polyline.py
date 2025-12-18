import sys
import os
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'src'))

from pillars.geometry.ui.scene_adapter import build_scene_payload
from pillars.geometry.ui.primitives import PolygonPrimitive, BrushStyle

# Test Polyline
instructions = {
    "type": "composite",
    "primitives": [
        {
            "shape": "polyline",
            "points": [(0, 0), (10, 0), (10, 10)],
            "pen": {"color": (255, 0, 0, 255), "width": 2.0},
            "closed": False
        }
    ]
}

payload = build_scene_payload(instructions, [])
if not payload.primitives:
    print("FAILED: No primitives returned for polyline.")
    sys.exit(1)

prim = payload.primitives[0]
if not isinstance(prim, PolygonPrimitive):
    print(f"FAILED: Expected PolygonPrimitive, got {type(prim)}")
    sys.exit(1)

if prim.closed:
    print("FAILED: Polyline should be open (closed=False).")
    sys.exit(1)

if prim.brush.enabled:
    print("FAILED: Polyline brush should be disabled by default.")
    sys.exit(1)

print("SUCCESS: Polyline parsed correctly.")
