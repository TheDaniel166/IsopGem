# The Tzolkin Protocol (The Mercury Harmonics)

> *"A filter for time, tuned to the frequency of 133."*

## Definition
The **Thelemic Tzolkin** is a 260-day harmonic cycle designed to interface with the **Mercury Current** (133). Unlike the traditional Mayan count, which repeats 1-13 in a linear sequence, the IsopGem Tzolkin utilizes a **Trigrammic** structure to map each day to a unique **Ditrune** (6-digit ternary number).

## Mathematical Proofs
*   **The Sum**: The sum of all 260 Hexagrams in the cycle is **82,992**.
*   **The Harmonic**: $82,992 = 624 \times 133$.
*   **Mercury Resonance**:
    *   **Orbit**: 45 Tzolkins = 11,700 days. $11,700 / 133 = 87.969$ days (Mercury's Orbital Period).
    *   **Rotation**: 30 Tzolkins / 133 = $58.646$ days (Mercury's Rotation Period).

## Structure
The cycle is arranged as a **20 × 13 Grid** (260 cells).
*   **Rows**: 20 Zodiacal/Elemental Signs (The lower Trigram).
*   **Columns**: 13 Tones (The upper Trigram).

### Construction Logic
Each cell is a **Ditrune** formed by combining two **Antigrams** (Trigrams):
1.  **Vertical Axis**: The 20 Signs are derived from the Zodiacal Trigrams, ordered by decreasing difference value (Leo -> Scorpio).
2.  **Horizontal Axis**: The 13 Tones.
3.  **Balance**: The columns are balanced to keep Yang trigrams on one half and Yin on the other.

## Data Source
*   **File**: `Docs/time_mechanics/Tzolkin Cycle.csv`
*   **Format**:
    *   **Lines 1-20**: The Decimal Values of the Ditrunes to be used for calculation.
    *   **Lines 22-41**: The Ternary representations of the same Ditrunes.

## Usage
Currently, this cycle exists as a reference table. Future implementations in the **Astrology Pillar** should utilize this grid to return the "Tzolkin Radical" for any given date, allowing for harmonic analysis alongside the standard planetary positions.
