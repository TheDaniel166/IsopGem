# Archimedean Solids Plan

Initial delivery scope focuses on two high-value Archimedean solids that give good coverage of mixed face structures:

1. **Cuboctahedron** – edge-transitive solid with 8 triangular faces and 6 squares (total 12 vertices). Symmetric coordinate set available using permutations of `(±1, ±1, 0)`.
2. **Truncated Tetrahedron** – smallest truncated form with 4 hexagons and 4 triangles (total 12 vertices) demonstrating non-equal face types and two edge classes.

## Implementation Approach
- Create a shared `archimedean_solids.py` service module that houses:
  - Canonical vertex/face definitions for supported solids (normalized to convenient coordinates).
  - Utility builder that scales canonical vertices to a requested `edge_length` by measuring the baseline edge distance and applying a uniform scale factor.
  - Metadata computation using existing helpers (`compute_surface_area`, `compute_volume`, `edges_from_faces`).
  - Calculator classes exposing editable `edge_length` plus derived metrics (surface area, volume, face counts).
- Add targeted PyQt6 hub wiring so the existing Archimedean category cards switch from "Coming soon" to actual `solid_viewer` launches for the implemented solids.
- Provide pytest coverage verifying vertex/edge/face counts, scaling accuracy, and calculator bidirectional behavior.

## Follow-up Expansion
Once the first two solids are stable, extend the same pattern to: truncated cube/oct, cuboctahedron variants (snub, rhombicuboctahedron), etc. The shared module can accumulate canonical datasets for each additional solid without changing UI plumbing.
