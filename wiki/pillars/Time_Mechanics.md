# Time Mechanics Pillar

**"Time is the canvas upon which the Numbers paint Reality."**

## Architectural Role
The **Time Mechanics** pillar is the **Sovereign Domain of Cycles**. While the Astrology Pillar calculates the positions of the stars, Time Mechanics interprets the **Harmonic Quality** of time itself. It is the home of the Tzolkin, the Calendar conversions, and the synchronization engines.

## The Core Logic (Services)

### **(Pending)**
*   **TzolkinService**: Will implement the logic defined in `Tzolkin_Protocol.md`, converting dates to Ditrunes and analyzing harmonic resonance.
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
