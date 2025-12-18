# Adyton (The Inner Chamber)

> *“The sanctuary where the walls speak the language of the stars.”*

## Definition

The **Adyton** is the central geometric chamber of the IsopGem Temple. It creates a structural bridge between **Time** (Astrology) and **Form** (Geometry).

## Structure

*   **Geometry**: A Regular Heptagon (7-sided polygon).
*   **The Walls**: 7 Walls, corresponding to the 7 Visible Planets.
    1.  **Sun**
    2.  **Mercury**
    3.  **Luna (Moon)**
    4.  **Venus**
    5.  **Jupiter**
    6.  **Mars**
    7.  **Saturn**
*   **The Sets**: The structure evolves through **52 Sets** (weeks), meaning the values on the walls shift throughout the year.

## Construction Logic

The walls are built using **Conrune Pairs** derived from the `zodiacal_heptagon.csv` dataset.
*   Each Set (1-52) assigns an **A-Value** (Day) and **B-Value** (Night) to each of the 7 Walls.
*   The values are arranged on the wall in a specific **Mirror Symmetry** pattern (Rows 1-4 mirror 5-8).

## Usage in Code

In the Geometry Pillar `src/pillars/geometry/`:
*   `ui/adyton_window.py`: The visualization tool for the 52 Sets (Pending).
*   `Docs/adyton_walls/`: Contains the pattern data and CSVs.
