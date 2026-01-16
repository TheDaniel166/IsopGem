# Cymatics Simulator Guide

The simulator generates standing wave patterns on 2D plates with multiple geometries, real-time 3D visualization, particle physics simulation, and comprehensive export options.

## Quick Start

1. Open **Cymatics → Cymatics Simulator**
2. Select a **Plate Shape** (Rectangular, Circular, or Hexagonal)
3. Adjust mode parameters or enable **Frequency Mode** for Hz-based input
4. Click **Generate** to render or **Animate** for continuous evolution
5. Toggle **3D Surface** to view as a height map
6. Enable **Particles** to see sand-like accumulation at nodal lines
7. **Save Image** or **Export GIF** to capture your patterns

## What You're Seeing

The visualization shows a standing wave field:
- **Bright regions** = high amplitude (antinodes)
- **Dark regions** = low amplitude (nodal lines)

In real cymatics experiments, particles collect at nodal lines where plate displacement is minimal.

---

## Plate Shapes

### Rectangular (Default)
Classic square plate with sine wave modes:
- Pattern: `sin(m·π·x) × sin(n·π·y)`
- Familiar grid-like nodal patterns

### Circular (Chladni)
True Chladni plate using Bessel functions:
- Pattern: `J_m(k·r) × cos(m·θ)` (Bessel functions in polar coordinates)
- Creates realistic circular Chladni figures
- Radial and angular mode combinations

### Hexagonal
Three-fold symmetric plate:
- Superposition of three 60°-rotated sine waves
- Creates intricate snowflake-like patterns
- Beautiful for decorative visualizations

---

## Wave Mode Controls

### Manual Mode Selection
- **Mode M / Mode N**: Primary wave mode indices (1-12)
  - Higher values = more nodal lines and finer structure
  - M controls horizontal complexity, N controls vertical
- **Secondary M / Secondary N**: Optional interference mode
  - Creates additional pattern complexity
- **Mix**: Blend ratio (0.0 = primary only, 1.0 = secondary only)
  - Values 0.1-0.4 add subtle richness

### Frequency Mode (Hz)
Enable **"Use Frequency (Hz)"** to drive modes from a frequency value:
- Range: 20 Hz - 2000 Hz
- Logarithmically maps to mode pairs
- Intuitive for audio-related exploration
- Status bar shows derived modes (e.g., "440 Hz → (3,4)")

---

## Visualization Options

### Color Gradients
Choose from five visualization palettes:
- **Grayscale**: Classic black/white
- **Heat Map**: Black → Purple → Red → Yellow → White
- **Ocean**: Deep blue → Teal → Cyan
- **Plasma**: Purple → Magenta → Orange → Yellow
- **Viridis**: Purple → Teal → Green → Yellow

### 3D Surface View
Toggle **"Show 3D Surface"** to see the pattern as a height map:
- **Left-drag**: Rotate view (orbital camera)
- **Right-drag/Middle-drag**: Pan view
- **Scroll wheel**: Zoom in/out
- Surface color follows selected gradient
- Flat shading with directional lighting

### Particle Simulation
Enable **"Enable Particles"** to simulate sand behavior:
- Particles drift toward nodal lines (amplitude minima)
- **Gold particles**: Settled at nodal lines
- **Gray particles**: Still moving
- Adjust **Count** (100-5000) for density
- Click **Reset Particles** to redistribute
- Statistics overlay shows settled percentage

---

## Other Controls

### Grid Size
Resolution of the simulation (80-420):
- Higher = sharper patterns, slower render
- Recommended: 200+ for detector accuracy

### Damping
Radial attenuation toward edges (0.0-6.0):
- 0.0 = uniform amplitude
- Higher = concentrated central energy
- Creates softer edge effects

---

## Export & Presets

### Save Image
Exports current pattern as PNG, JPEG, or BMP with applied color gradient.

### Export GIF
Creates animated GIF (60 frames, 30fps):
- Captures one full animation cycle
- Requires `imageio` library: `pip install imageio`

### Save/Load Preset
- Save current parameters with name and description
- Load user presets or built-in presets:
  - **Classic Chladni**: Circular plate fundamentals
  - **Hexagonal Harmony**: Symmetric hex patterns
  - **High Frequency**: Complex interference
  - **Ocean Waves**: Soft, flowing pattern

---

## Practical Recipes

| Goal | Settings |
|------|----------|
| Clean symmetry | Rectangular, M=N (e.g., 3,3), Mix ~0.1 |
| True Chladni | Circular, low modes (2,2 or 3,1) |
| Snowflake | Hexagonal, M=4, N=4, Mix ~0.3 |
| Audio-driven | Frequency mode, adjust Hz slider |
| High detail | Grid Size 280+, modes 5-8 |
| Soft glow | Damping 1.0-2.0 |
| Rich interference | Mix 0.3-0.5, offset secondary modes |

---

## Detector Workflow

The Pattern Detector analyzes the most recent simulator output:

1. Generate a still frame (or pause animation)
2. Open **Cymatics → Pattern Detector**
3. Click **Analyze**
4. Adjust **Nodal Threshold** to tune sensitivity
5. View **Edges** or **Nodal Mask** visualizations
6. Check metrics: symmetry, edge density, radial peaks, frequencies

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Pattern looks flat | Increase Grid Size, reduce Damping |
| Too chaotic/noisy | Lower Mix, use lower modes (2-4) |
| Weak detector edges | Use still frame, lower modes |
| Particles not settling | Wait longer, reduce particle count |
| 3D view too slow | Increase internal subsampling (fewer faces) |
| GIF export fails | Install imageio: `pip install imageio` |
