# Enochian Name Generation Rules (Neo-Enochian)

## Overview
The "Angelic Names" of the Enochian system are not arbitrary; they are **Geometrical Derivations** from the Watchtower Grids. By tracing specific vectors (lines, spirals, crosses) across the grid, we extract strings of letters that form the names of Servient Angels, Kerubim, Seniors, and Kings.

In **IsopGem**, we apply these ancient algorithms to the **Kamea of Maut**, mapping our Ternary Grid to the Enochian Letter Cipher.

## 1. The Letter Mapping (The Cipher)
To convert a Kamea Cell (Ditrune/Decimal) into a Letter, we use the **Gematria Cipher** (`src/pillars/tq/data/cipher_correspondence.csv`).

**Formula:**
> `Letter = Cipher(Decimal_Value % 27)`

The 27-Letter Cipher:
| Val | Let | Val | Let | Val | Let |
|---|---|---|---|---|---|
| 0 | **I** | 9 | **T** | 18 | **Y** |
| 1 | **L** | 10 | **O** | 19 | **Z** |
| 2 | **C** | 11 | **G** | 20 | **B** |
| 3 | **H** | 12 | **F** | 21 | **M** |
| 4 | **P** | 13 | **E** | 22 | **V** |
| 5 | **A** | 14 | **R** | 23 | **D** |
| 6 | **X** | 15 | **S** | 24 | **N** |
| 7 | **J** | 16 | **Q** | 25 | **U** |
| 8 | **W** | 17 | **K** | 26 | **(Null)**|

## 2. The Kerubic Angels (The 4-Fold Name)
In each Sub-Quadrant (Lesser Angle), there is a **Cross**. The row *above* the horizontal beam contains 4 Letters.
*   **Source**: The 4 cells forming the "Top Row" of the sub-quadrant (excluding the central column).
*   **Permutation**: These 4 letters (e.g., `R Z L A`) are permuted to form 4 Angelic Names:
    1.  **R Z L A**
    2.  **Z L A R**
    3.  **L A R Z**
    4.  **A R Z L**
*   **Function**: These govern the specific sub-element (e.g., "Air of Earth").

## 3. The Ruling Archangels (The Prefix)
To command the Kerubic Angels, one must invoke the Archangel.
*   **Formula**: `Union_Letter + Kerubic_Name`
*   **Source**: The **Tablet of Union** (Spirit Tablet) provides the prefix.
    *   **Air**: `E` (from `EXARP`)
    *   **Water**: `H` (from `HCOMA`)
    *   **Earth**: `N` (from `NANTA`)
    *   **Fire**: `B` (from `BITOM`)
*   **Example**: `E` + `RZLA` = **ERZLA** (Archangel of Air-Earth Subquadrant).

## 4. The Planetary Seniors (The Cross)
The 6 Seniors (Planetary Rulers) are drawn from the **Central Cross** of the Watchtower.
*   **Extraction**: Reading from the Center outward along the 4 arms of the cross.
*   **Attribution**: Associated with the 7 Planets (excluding one, usually dependent on the tablet, or splitting the Moon/Saturn).

## 5. The Great Kings (The Spiral)
The Three Holy Names of God and the Great King are derived from the **Central Line** (Linea Spiritus) and a **Spiral**.
*   **Bataivah** (Air King): Derived from a spiral around the center.
*   **IsopGem Algorithm**: We shall implement a "Spiral Reader" that starts at the Tablet Center and uncoils to generate the King's Name.

## Implementation Plan
1.  **Cipher Service**: Map `WatchtowerView` cells to Letters.
2.  **Selection Tool**: When a user selects a region (e.g., a "Cross"), auto-generate the names.
3.  **Name Browser**: A dedicated UI to list the names derived from the current Watchtower State (since names change as cells mutate!).
