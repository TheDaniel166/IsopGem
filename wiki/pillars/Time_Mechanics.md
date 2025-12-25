# Time Mechanics Pillar

**"Time is the canvas upon which the Numbers paint Reality."**

## Architectural Role
The **Time Mechanics** pillar is the **Sovereign Domain of Cycles**. While the Astrology Pillar calculates the positions of the stars, Time Mechanics interprets the **Harmonic Quality** of time itself. It is the home of the Tzolkin, the Calendar conversions, and the synchronization engines.

## The Core Logic (Services)

### **[tzolkin_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/time_mechanics/services/tzolkin_service.py)**
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

### **[time_mechanics_hub.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/time_mechanics/ui/time_mechanics_hub.py)**
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
*   Pending implementation of `TimeRepository` for storing event logs or cycle definitions.
