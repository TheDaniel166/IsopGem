# The Architect's Catalog
## Index of the Adyton Construction

> *"Here lies the hammer, the chisel, and the stone."*

This document indexes the complete ecosystem of the Adyton Walls: the **Lore** that gives them meaning, the **Data** that defines their structure, and the **Scripts** used to generate and visualize them.

---

## I. The Grimoires (Lore & Theory)

These are the primary texts for the Adept and the Magus.

| Scroll | Description |
|--------|-------------|
| [The Book of 91 Stars](The_Book_of_91_Stars.md) | The complete mythos, greek keys, and forms of every constellation. |
| [The Book of 91 Stars (Codex)](The_Book_of_91_Stars.html) | **[Generated]** The visual HTML artifact with gold-on-black illuminations. |
| [The Atlas of Seeds](The_Atlas_of_Seeds.md) | The deep metaphysics of the 13 Seeds and the Altar of 287 (Empty Net). |
| [The Chamber of the Adepts](The%20Chamber%20of%20the%20Adepts%20and%20the%20Adyton.%20FINAL%20(1).docx.md) | The foundational vision of the Adyton space. |
| [Constellation Shapes](constellation_shapes.json) | The visual definition (ASCII) of the 13 forms. |

---

## II. The Blueprints (Data Sources)

The raw mathematical and structural definitions.

### The Walls
| File | Role |
|------|------|
| `sun_wall.csv` | The 13x8 grid definition for Sol. |
| `mercury_wall.csv` | The 13x8 grid definition for Mercury. |
| `venus_wall.csv` | The 13x8 grid definition for Venus. |
| `luna_wall.csv` | The 13x8 grid definition for Moon. |
| `mars_wall.csv` | The 13x8 grid definition for Mars. |
| `jupiter_wall.csv` | The 13x8 grid definition for Jupiter. |
| `saturn_wall.csv` | The 13x8 grid definition for Saturn. |

### The Analysis
| File | Role |
|------|------|
| `constellation_metrics.csv` | Statistical breakdown of every constellation. |
| `walls_constellations_complete.csv` | Aggregated data of all 91 forms. |
| `wall_seeds_dna.csv` | The genetic code of the seed placements. |
| `dead_zones_values.csv` | The coordinates and values of the "Empty Net" (Altar). |

---

## III. The Tools (Active Scripts)

These scripts are currently used to maintain, visualize, or verify the Adyton.

| Script | Function |
|--------|----------|
| `scripts/scribe_of_stars.py` | **The Illuminator.** Generates the `The_Book_of_91_Stars.html` from the JSON data. Run this after editing Mythos. |
| `scripts/get_constellation_metrics.py` | Calculates size, density, and spread of constellations. |
| `scripts/get_seed_values.py` | Extracts the 13 seed coordinates from the wall files. |
| `scripts/deep_wall_analysis.py` | Performs structural audit of the lattices. |
| `scripts/analyze_conrune_patterns.py` | Investigates the sonic/phonetic relationships. |

---

## IV. The Attic (Generator Scripts)

These scripts were used by the Architect to **create** the current reality. They are preserved for historical provenance and algorithm study (located in `scripts/attic` or root).

### The Genesis Algorithms
*   `generate_planetary_lattices.py`: The original script that grew the MSTs (Minimum Spanning Trees) from the seeds.
*   `generate_organic_constellations.py`: An experimental generator using "organic" growth rules.
*   `generate_annealed_constellations.py`: Used Simulated Annealing to optimize constellation shapes.
*   `reverse_engineer_seeds.py`: The tool used to discover the "Core Seeds" from the finished walls.

### The Visualization Experiments
*   `visualize_seeds_atlas.py`: Generates the ASCII maps for the Atlas of Seeds.
*   `visualize_wall_octets.py`: Visualizes the 8-row structure.
*   `visualize_constellation_preview.py`: Early tool for checking shapes.

---

## V. Modification Rituals

### How to Edit a Mythos
1.  Open `src/pillars/adyton/data/constellation_mythos.json`.
2.  Edit the text.
3.  Run `./.venv/bin/python scripts/scribe_of_stars.py`.
4.  The HTML Codex is updated.

### How to Change a Shape
1.  Open `Docs/adyton_walls/constellation_shapes.json`.
2.  Adjust the ASCII block (`■`). (Note: This is visual only; the *true* definition is in `planetary_lattices.json`).
3.  Run `./.venv/bin/python scripts/scribe_of_stars.py` to see the new SVG.
