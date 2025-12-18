# Kamea (The Lattice of Wisdom)

> *“A finite grid containing an infinite truth.”*

## Definition

The **Kamea** (Hebrew for "Amulet" or "Magic Square") is the fundamental interaction grid of the IsopGem system. While traditionally a generic term for planetary squares, here it specifically refers to the **27×27 Ternary Lattice** developed for the TQ Pillar.

## Geometry

*   **Dimensions**: 27 × 27 cells (729 total).
*   **Coordinate System**: Center-zero, ranging from `(-13, +13)` to `(+13, -13)`.
*   **The Singularity**: The center cell `(0,0)` represents the **Void (000000)**.

## The Hexeract (Hypercube)

The 2D Kamea is actually a projection of a **6-Dimensional Ternary Hypercube** (Hexeract).
*   Each of the 729 cells corresponds to a unique **Ditrune** (6-digit ternary number).
*   The lattice organizes these numbers based on their **Hamming Weight** (sum of digits) and their **Projective Distance** from the center.

## The 9 Regions (The Mandalas of Territory)

The Grid is divided into 9 sectors based on the **Central Bigram** (digits 3 & 4). These regions have distinct physical properties:

### 1. The Immutable Region (0)
*   **Archetype**: The Void / Axis Mundi.
*   **Property**: The source of all lineage. `Prime` is at (0,0).
*   **Philosophy**: Unity and Order.

### 2. The Pure Pairs (4 & 8)
*   **Archetype**: Polarity (Yang/Yin).
*   **Property**: Mirrors of each other.
*   **Philosophy**: The Law of Complementarity.

### 3. The Entangled Regions (5 & 7)
*   **Archetype**: Dynamic Balance.
*   **Property**: "Co-parented" temples. Lineages are shared.
*   **Philosophy**: Harmony arising from Tension.

### 4. The Bigrammic Quadset (1, 2, 3, 6)
*   **Archetype**: Emergence.
*   **Property**: A fourfold web where every Temple is a crossroad.
*   **Philosophy**: Creation from complexity.

## Usage in Code

In the TQ Pillar `src/pillars/tq/`:
*   `ui/kamea_grid_window.py`: The visualizer for the 27x27 grid.
*   `services/kamea_grid_service.py`: Logic for mapping coordinates to Ditrunes.
