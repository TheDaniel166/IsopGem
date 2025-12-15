# The TQ Engine

**"The World is built on Three. 0, 1, 2. The Void, The Point, The Line."**

## Architectural Role
The **TQ (Trigrammaton Qabalah) Engine** is the **Logic of the Trinity**. It implements the system of base-3 numerology, "Ditrunes" (6-digit ternary strings), and the 27x27x27 "Kamea" Cube. It is the engine of pattern recognition and sonic synthesis.

## The Core Logic (Services)

### **[ternary_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/services/ternary_service.py)**
*   **Architectural Role**: Sovereign Service (The Translator)
*   **The Purpose**: Translates between base-10 integers and base-3 strings.
*   **Key Logic**:
    *   `decimal_to_ternary`: Algorithmic conversion of `int` -> `str` (e.g., `364` -> `111111`) using modulo-3 operations.
    *   **Balanced Ternary**: (Optional/Future) Logic for (-1, 0, 1) representation.

### **[ditrunal_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/services/ditrunal_service.py)**
*   **Architectural Role**: Sovereign Service (The Alchemist)
*   **The Purpose**: Analyzes the internal structure of a Ditrune.
*   **Key Logic**:
    *   `nuclear_mutation`: Recursively strips the "Skin" (Outer characters) and "Body" to reveal the "Core", determining the Ditrune's Family.
    *   `get_conrune_value`: Calculates the polarity flip (1 <-> 2, 0 stays 0) of a string.

### **[kamea_grid_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/services/kamea_grid_service.py)**
*   **Architectural Role**: Service (The Cartographer)
*   **The Purpose**: Manages the 27x27x27 coordinate space of the Kamea.
*   **Key Logic**:
    *   `load_csv`: Ingests the Master csv defining the 19,683 cells.
    *   **Addressing**: Resolves `Region-Area-Cell` logic (e.g., `0-4-0`).

### **[amun_audio_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/services/amun_audio_service.py)**
*   **Architectural Role**: Service (The Synthesizer)
*   **The Purpose**: Converts the mathematical properties of a Ditrune (Bigrams) into Sound.
*   **Key Logic**:
    *   **AM Synthesis**: Uses Amplitude Modulation. Channel bits map to `Carrier Frequency`, `Modulator Rate`, and `Amplitude`.
    *   `_synthesize_data`: Generates Raw PCM (`bytes`) for `.wav` export.

### **[quadset_engine.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/services/quadset_engine.py)**
*   **Architectural Role**: Service (The Pipeline)
*   **The Purpose**: Expands a single number into a **Quadset**.
*   **Key Logic**:
    *   `calculate`: Derives 1. **Original**, 2. **Conrune**, 3. **Reversal**, 4. **Conrune Reversal**.
    *   **Differentials**: Calculates the interstitial gaps between these 4 values.

### **[ternary_transition_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/services/ternary_transition_service.py)**
*   **Architectural Role**: Service (The Animator)
*   **The Purpose**: Calculates the frame-by-frame interpolation between two ternary states.

### **[pattern_analyzer.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/services/pattern_analyzer.py)**
*   **Architectural Role**: Service (The Mathematician)
*   **The Purpose**: Checks Quadsets for heavy mathematical properties.
*   **Key Logic**:
    *   **Tests**: Checks for Palindromes, Primes, Squares, Cubes, and various Fibonacci/Lucas relationships.
    *   **Helper**: `[number_properties.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/services/number_properties.py)`

### **[kamea_symphony_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/services/kamea_symphony_service.py)**
*   **Architectural Role**: Service (The Conductor)
*   **The Purpose**: Orchestrates large-scale audio synthesis for entire Kamea slices.

## The Presentation Layer (UI)

### **[tq_hub.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/ui/tq_hub.py)**
*   **Architectural Role**: View (The Gateway)
*   **The Purpose**: The sovereign entry point for TQ operations.

### **[kamea_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/ui/kamea_window.py)**
*   **Architectural Role**: View (The Cube)
*   **The Purpose**: The visual interface for the 3D Ternary Grid.
*   **Key Logic**:
    *   **View Switching**: Toggles between `KameaGridView` (2D) and `KameaFractalView` (3D).
    *   **Selection**: Propagates cell selection signals to the `NuclearMutationPanel`.

### **[quadset_analysis_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/ui/quadset_analysis_window.py)**
*   **Architectural Role**: View (The Laboratory)
*   **The Purpose**: A tabbed interface for analyzing multiple numbers.
*   **Key Logic**:
    *   **Visualization**: Renders the "Quadset Glyph" (Diamond shape) for each member.

### **[kamea_fractal_view.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/ui/kamea_fractal_view.py)**
*   **Architectural Role**: View (The 3D Engine)
*   **The Purpose**: Native Software 3D Engine for rendering the 27x27x27 Cube.
*   **Key Logic**:
    *   `_project_point`: Custom Perspective Projection Matrix logic.
    *   `tree_paths`: Renders the hierarchical lines connecting Region -> Area -> Cell.

### **[kamea_grid_view.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/ui/kamea_grid_view.py)**
*   **Architectural Role**: View (The 2D Engine)
*   **The Purpose**: Interactive 2D Slice view of the Kamea.

### **[nuclear_mutation_panel.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/ui/nuclear_mutation_panel.py)**
*   **Architectural Role**: View (The Inspector)
*   **The Purpose**: Displays the deep lineage (Core, Body, Skin) of the selected Ditrune.

### **[ternary_converter_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/ui/ternary_converter_window.py)**
*   **Architectural Role**: View (The Calculator)
*   **The Purpose**: Simple utility for Decimal <-> Ternary conversion.
*   **Key Logic**: Also displays `[fractal_network_dialog.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/ui/fractal_network_dialog.py)`.

### **[transitions_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/ui/transitions_window.py)**
*   **Architectural Role**: View (The Animator)
*   **The Purpose**: visualizing the `TernaryTransitionService` logic.

### **[amun_visualizer.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/ui/amun_visualizer.py)**
*   **Architectural Role**: View (The Mandala)
*   **The Purpose**: Real-time visualization for the Amun Sound System.
*   **Key Logic**:
    *   `paintEvent`: Renders nested polygons/stars based on Bigram value.
    *   **Animation**: Pulse (Rhythm) and Rotation (Pitch) driven by `QTimer`.

### **[ternary_sound_widget.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/ui/ternary_sound_widget.py)**
*   **Architectural Role**: View (The Composer)
*   **The Purpose**: An interface for sequencing Ditrunes.
*   **Key Logic**:
    *   `play_sequence`: Iterates through a list of Ditrunes, invoking `AmunAudioService` for each and managing the playback queue.

## Data Structures (Models)

### **[kamea_cell.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/models/kamea_cell.py)**
*   **Architectural Role**: Domain Model
*   **The Purpose**: Represents a single cell in the hypercube.
*   **Properties**: `ternary_value`, `decimal_value`, `bigrams` (Core, Body, Skin), `coordinates`.

### **[amun_sound.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/tq/models/amun_sound.py)**
*   **Architectural Role**: Domain Model
*   **The Purpose**: A calculated acoustic signature.
*   **Logic**: Maps Bigrams (0-8) to the "9-Octave Ladder" frequencies.
