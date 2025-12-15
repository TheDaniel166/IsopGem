# The Astrology Engine

**"As Above, So Below. The stars do not compel, but they incline."**

## Architectural Role
The **Astrology Engine** is the **Keeper of Time**. Its sovereign duty is to calculate the precise positions of the celestial bodies and interpret their geometric relationships. It serves as the bridge between the physical sky (Ephemeris) and the symbolic meaning (Zodiac).

## The Core Logic (Services)

### **[openastro_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/astrology/services/openastro_service.py)**
*   **Architectural Role**: Sovereign Service (The Bridge)
*   **The Purpose**: It is the Diplomat to the external world. It integrates the `OpenAstro2` library into our Temple, translating our internal requests into the language of the Swisseph/PyEphem kernels.
*   **Key Logic**:
    *   `_extract_planet_positions`: Validates the `Swisseph` availability, calculates the Julian Day, and extracts the geocentric/heliocentric longitudes/latitudes for the Seven Wanderers (Sun through Saturn).
*   **Signal Flow**:
    *   **Listens to**: `request_chart_calculation` (Method call)
    *   **Emits**: `ChartData` (Dict)
*   **Dependencies**: `OpenAstro2`, `swisseph`, `pyephem`.

### **[chart_storage_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/astrology/services/chart_storage_service.py)**
*   **Architectural Role**: Handmaiden Utility (The Archivist)
*   **The Purpose**: Persists the frozen moments of time (Natal Charts) into the database. It ensures that a "Birth" is never forgotten.
*   **Key Logic**:
    *   `save_chart`: Orchestrates the transaction.
    *   `_extract_house_system`: Parses the raw input definition to determine the Placidus/Whole Sign house system configuration.
*   **Signal Flow**: None (Synchronous).
*   **Dependencies**: `shared.database.SessionLocal`, `ChartRepository`.

### **[location_lookup.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/astrology/services/location_lookup.py)**
*   **Architectural Role**: Handmaiden Utility (The Navigator)
*   **The Purpose**: Resolves human-readable strings (e.g., "Athens, Greece") into terrestrial coordinates (Latitude/Longitude).
*   **Key Logic**:
    *   `search`: Queries the internal or external geocoding database. Calculates time zone offsets based on longitude and date.
*   **Signal Flow**: None.
*   **Dependencies**: `geopy` (implied/optional).

## The Presentation Layer (UI)

### **[astrology_hub.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/astrology/ui/astrology_hub.py)**
*   **Architectural Role**: View (The Gateway)
*   **The Purpose**: The single entry point for the Magus to access the Star Tools.
*   **Key Logic**:
    *   `launch_natal`: Summons the `NatalChartWindow`.
    *   `launch_ephemeris`: Summons the `PlanetaryPositionsWindow`.
*   **Signal Flow**: Emits nothing; calls `WindowManager.open_window`.
*   **Dependencies**: `shared.ui.WindowManager`.

### **[natal_chart_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/astrology/ui/natal_chart_window.py)**
*   **Architectural Role**: View (The Mirror)
*   **The Purpose**: An interactive interface for casting charts.
*   **Key Logic**:
    *   `_load_chart`: Orchestrates the "Configuration" vs "Revelation" tab state.
    *   **Visualization**: Renders the SVG output from OpenAstro into a `QWebEngineView` or `QSvgWidget`.
*   **Signal Flow**:
    *   **Emits**: `chart_saved`, `calculation_requested`.
*   **Dependencies**: `OpenAstroService`, `ChartStorageService`.

### **[planetary_positions_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/astrology/ui/planetary_positions_window.py)**
*   **Architectural Role**: View (The Ephemeris)
*   **The Purpose**: A raw data viewer that displays the exact zodiacal degrees of the planets.
*   **Key Logic**:
    *   `_generate_ephemeris`: Loop over a date range, calling calculation service for each day, and populating the `QTableWidget`.
*   **Dependencies**: `utils.conversions.to_zodiacal_string`.

### **[venus_rose_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/astrology/ui/venus_rose_window.py)**
*   **Architectural Role**: View (The Dance)
*   **The Purpose**: A generative art visualization demonstrating the 13:8 orbital resonance between Earth and Venus.
*   **Key Logic**:
    *   **Orbital Simulation**: Simulates Earth (T=1.0) and Venus (T=0.615) orbits.
    *   **The Trace**: Draws the line between them at every tick to reveal the Pentagram.
    *   **Drift Calculation**: "Real Physics" mode applies the 1.5° drift per 8-year cycle.
*   **Signal Flow**: Internal animation loop (`QTimer`).

### **[neo_aubrey_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/astrology/ui/neo_aubrey_window.py)**
*   **Architectural Role**: View (The Neolithic Computer)
*   **The Purpose**: Simulates the Aubrey Holes at Stonehenge for Eclipse prediction.
*   **Key Logic**:
    *   **Saros Ring**: 223 items tracking the 18-year cycle.
    *   **Aubrey Ring**: 56 holes tracking the Lunar Nodes.
*   **Dependencies**: `QGraphicsScene`.

### **[current_transit_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/astrology/ui/current_transit_window.py)**
*   **Architectural Role**: View (The Watcher)
*   **The Purpose**: Displays the current real-time position of the planets (The "Now").
*   **Key Logic**:
    *   **Auto-Update**: Refreshes calculation every minute to track the Ascendant's movement.


## Data Structures (Models)

### **[chart_record.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/astrology/models/chart_record.py)**
*   **Architectural Role**: Domain Model (The Entity)
*   **The Purpose**: The SQLAlchemy definition of a Chart.
*   **Key Logic**: Maps python attributes to the `charts` table.

## Infrastructure (Repositories)

### **[chart_repository.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/astrology/repositories/chart_repository.py)**
*   **Architectural Role**: Persistence Layer
*   **The Purpose**: Handles the raw SQL interactions for Charts.
*   **Key Logic**:
    *   `search`: Advanced heuristic search by Name, Date, or Location.
