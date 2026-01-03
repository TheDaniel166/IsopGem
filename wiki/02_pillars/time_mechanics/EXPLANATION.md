# Time Mechanics Pillar

**"Time is the canvas upon which the Numbers paint Reality."**

## Architectural Role
The **Time Mechanics** pillar is the **Sovereign Domain of Cycles**. While the Astrology Pillar calculates the positions of the stars, Time Mechanics interprets the **Harmonic Quality** of time itself. It is the home of the Tzolkin, the Calendar conversions, and the synchronization engines.

## The Core Logic (Services)

### **tzolkin_service.py** (`src/pillars/time_mechanics/services/tzolkin_service.py`)
*   **Architectural Role**: Sovereign Service (The Timekeeper)
*   **The Purpose**: Manages the 260-day harmonic Tzolkin cycle, converting Gregorian dates to Kins, Tones, and Signs.
*   **Key Logic**:
    *   **The Epoch**: Anchored to Jan 12, 2020 (Kin 1).
    *   **Calculation**: Computes the Kin index (0-259) based on days elapsed since Epoch.
    *   **Ditrune Mapping**: Retrieves the binary/ternary "Ditrune" pattern for the Kin from the harmonic grid.
    *   **Conrune**: Calculates the "Anti-Self" (oppositional force) by inverting the Ditrune (1<->2).
*   **Dependencies**: `time_mechanics/Tzolkin Cycle.csv` (Grid Data).

### **(Pending)**
*   **CalendarService**: Will handle conversion between Gregorian, Julian, Thelemic, and other esoteric calendars.

## The Presentation Layer (UI)

### **time_mechanics_hub.py** (`src/pillars/time_mechanics/ui/time_mechanics_hub.py`)
*   **Architectural Role**: View (The Diplomat)
*   **The Purpose**: The single entry point for the Magus to access temporal tools.
*   **Key Logic**:
    *   Currently serves as a placeholder.
    *   Will eventually launch the `TzolkinCalculatorWindow` and `CalendarConverterWindow`.
*   **Signal Flow**: Emits nothing yet.
*   **Dependencies**: `shared.ui.WindowManager`.

## Data Structures (Models)
*   Pending implementation of `TzolkinDate` and `CalendarEvent`.

## Infrastructure (Repositories)
## The Tzolkin Protocol (The Mercury Harmonics)

> *"A filter for time, tuned to the frequency of 133."*

### Definition
The **Thelemic Tzolkin** is a 260-day harmonic cycle designed to interface with the **Mercury Current** (133). Unlike the traditional Mayan count, which repeats 1-13 in a linear sequence, the IsopGem Tzolkin utilizes a **Trigrammic** structure to map each day to a unique **Ditrune** (6-digit ternary number).

### Mathematical Proofs
*   **The Sum**: The sum of all 260 Hexagrams in the cycle is **82,992**.
*   **The Harmonic**: $82,992 = 624 \times 133$.
*   **Mercury Resonance**:
    *   **Orbit**: 45 Tzolkins = 11,700 days. $11,700 / 133 = 87.969$ days (Mercury's Orbital Period).
    *   **Rotation**: 30 Tzolkins / 133 = $58.646$ days (Mercury's Rotation Period).

### Structure
The cycle is arranged as a **20 × 13 Grid** (260 cells).
*   **Rows**: 20 Zodiacal/Elemental Signs (The lower Trigram).
*   **Columns**: 13 Tones (The upper Trigram).

#### Construction Logic
Each cell is a **Ditrune** formed by combining two **Antigrams** (Trigrams):
1.  **Vertical Axis**: The 20 Signs are derived from the Zodiacal Trigrams, ordered by decreasing difference value (Leo -> Scorpio).
2.  **Horizontal Axis**: The 13 Tones.
3.  **Balance**: The columns are balanced to keep Yang trigrams on one half and Yin on the other.

### Data Source
*   **File**: `Docs/time_mechanics/Tzolkin Cycle.csv`
*   **Format**:
    *   **Lines 1-20**: The Decimal Values of the Ditrunes to be used for calculation.
    *   **Lines 22-41**: The Ternary representations of the same Ditrunes.

### Usage
Currently, this cycle exists as a reference table. Future implementations in the **Astrology Pillar** should utilize this grid to return the "Tzolkin Radical" for any given date, allowing for harmonic analysis alongside the standard planetary positions.
