# ADR-030: Documentation TODO Filling Guidelines

**Status**: Active  
**Date**: 2026-01-16  
**Context**: We have 215 TODO markers in pillar documentation that need systematic filling with real code details.

---

## The Mission

Fill documentation TODOs by **extracting real information from source code**, not inventing or guessing.

---

## DO ✅

### 1. READ THE ACTUAL SOURCE FILE
```python
# Before filling: wiki/02_pillars/cymatics/features/cymatics_hub.md
# You MUST read: src/pillars/cymatics/ui/cymatics_hub.py
```

### 2. EXTRACT REAL LISTS
**TODO: List key UI elements**
```markdown
✅ GOOD:
- QScrollArea (main container)
- QLabel (title and description)
- QPushButton (tool cards)
- QGridLayout (3-column grid)
- QFrame (tool cards with hover effects)

❌ BAD:
- Various UI widgets
- Interactive elements
- Standard Qt components
```

### 3. FIND ACTUAL SERVICE DEPENDENCIES
**TODO: List services used by this feature**
```markdown
✅ GOOD:
- CymaticsSimulationService (pattern generation)
- CymaticsGradientService (color mapping)
- CymaticsPresetService (save/load)

❌ BAD:
- Multiple backend services
- Various calculation engines
```

### 4. LIST REAL EVENT HANDLERS
**TODO: List key event handlers**
```markdown
✅ GOOD:
- _on_frequency_changed(value: float) - Updates simulation frequency
- _on_shape_selected(index: int) - Changes plate geometry
- _handle_export() - Saves pattern to file

❌ BAD:
- Event handlers for user interactions
- Various callback methods
```

---

## DON'T ❌

### 1. NO HALLUCINATING FEATURES
```markdown
❌ DON'T invent:
"Real-time audio input from microphone"
(if it's not in the code)

✅ DO say:
"Feature not yet implemented"
(if you can't find it)
```

### 2. NO VAGUE PLACEHOLDERS
```markdown
❌ DON'T write:
"This component handles various user interactions"

✅ DO write:
"User clicks generate button → calls _on_generate() → creates SimulationParams → passes to CymaticsSimulationService"
```

### 3. NO GENERIC DESCRIPTIONS
```markdown
❌ DON'T write:
"The system processes the data efficiently"

✅ DO write:
"Uses cached Bessel function zeros via _BESSEL_ZEROS_CACHE dict to avoid repeated scipy calculations"
```

### 4. NO ASSUMPTIONS ABOUT BEHAVIOR
```markdown
❌ DON'T assume:
"Probably validates input before processing"

✅ DO verify:
Read the actual method and report what it does:
"Clamps frequency to range [20.0, 2000.0] via np.clip()"
```

---

## File Path Mappings

### Cymatics Pillar
| Wiki Doc | Source File |
|----------|-------------|
| `wiki/02_pillars/cymatics/features/cymatics_hub.md` | `src/pillars/cymatics/ui/cymatics_hub.py` |
| `wiki/02_pillars/cymatics/features/cymatics_simulator.md` | `src/pillars/cymatics/ui/cymatics_simulator_window.py` |
| `wiki/02_pillars/cymatics/features/cymatics_detector.md` | `src/pillars/cymatics/ui/cymatics_detector_window.py` |
| `wiki/02_pillars/cymatics/ui_components/cymaticshub.md` | `src/pillars/cymatics/ui/cymatics_hub.py` |
| `wiki/02_pillars/cymatics/api/cymatics_simulation_service.md` | `src/pillars/cymatics/services/cymatics_simulation_service.py` |

### Correspondences Pillar
| Wiki Doc | Source File |
|----------|-------------|
| `wiki/02_pillars/correspondences/features/spreadsheet.md` | `src/pillars/correspondences/ui/spreadsheet_window.py` |
| `wiki/02_pillars/correspondences/features/formula_bar.md` | `src/pillars/correspondences/ui/formula_bar_widget.py` |
| `wiki/02_pillars/correspondences/api/formula_engine.md` | `src/pillars/correspondences/services/formula_engine.py` |

### TQ Lexicon Pillar
| Wiki Doc | Source File |
|----------|-------------|
| `wiki/02_pillars/tq_lexicon/features/unified_lexicon.md` | `src/pillars/tq_lexicon/ui/unified_lexicon_window.py` |
| `wiki/02_pillars/tq_lexicon/features/lexicon_manager.md` | `src/pillars/tq_lexicon/ui/lexicon_manager_window.py` |

---

## Specific TODO Types

### Type 1: List Key UI Elements
**Pattern to extract:**
```python
# Look for: Q{WidgetName}( in the source
QLabel(...)         → QLabel
QPushButton(...)    → QPushButton  
QTableWidget(...)   → QTableWidget
```

**Output format:**
```markdown
**Key UI Elements:**
- QLabel - Title and description text
- QPushButton - Action buttons (Generate, Export, etc.)
- QTableWidget - Data grid (if present)
```

### Type 2: List Services Used
**Pattern to extract:**
```python
# Look for: self._something = SomethingService()
self._simulator = CymaticsSimulationService()
self._gradient = CymaticsGradientService()
```

**Output format:**
```markdown
**Services:**
- CymaticsSimulationService - Generates standing wave patterns
- CymaticsGradientService - Applies color gradients to visualizations
```

### Type 3: Describe User Interactions
**Pattern to extract:**
```python
# Look for button connections and event handlers
button.clicked.connect(self._on_generate)
slider.valueChanged.connect(self._on_frequency_changed)
```

**Output format:**
```markdown
**User Interactions:**
1. Adjust frequency slider → Updates label and regenerates pattern in real-time
2. Click "Export" button → Opens file dialog and saves PNG/GIF
3. Select plate shape dropdown → Switches between rectangular/circular modes
```

### Type 4: List Event Handlers
**Pattern to extract:**
```python
# Look for methods starting with _on_ or _handle_
def _on_frequency_changed(self, value: float):
def _handle_export(self):
```

**Output format:**
```markdown
**Event Handlers:**
- `_on_frequency_changed(value: float)` - Updates simulation when slider moves
- `_handle_export()` - Exports current pattern to file
```

---

## Quality Checklist

Before submitting filled documentation, verify:

- [ ] I read the actual source file mentioned in the file path mapping
- [ ] Every item in my lists exists in the source code
- [ ] I copied actual class/method names (not paraphrased)
- [ ] I included brief descriptions based on docstrings or behavior
- [ ] I did NOT invent features that aren't implemented
- [ ] I used actual parameter names and types from the code
- [ ] I checked that file paths in examples match reality

---

## Examples of Each Difficulty Level

### EASY_EXTRACTION (68 tasks) - Perfect for Free Models

**Example Task:**
> In `wiki/02_pillars/cymatics/ui_components/cymaticshub.md`  
> Replace: `**TODO**: List key UI elements`

**What to do:**
1. Read `src/pillars/cymatics/ui/cymatics_hub.py`
2. Search for `Q[A-Z]\w+\(` pattern (Qt widgets)
3. List what you find with 1-line descriptions

**Expected output:**
```markdown
**Key UI Elements:**
- QScrollArea - Scrollable container for hub content
- QLabel - Displays "Cymatics" title and description
- QPushButton - Tool card buttons (Simulator, Detector, Help)
- QGridLayout - 3-column grid layout for tool cards
- QFrame - Individual tool card containers with hover styling
```

---

### MEDIUM_ANALYSIS (54 tasks) - Good for GPT-3.5

**Example Task:**
> In `wiki/02_pillars/cymatics/features/cymatics_simulator.md`  
> Replace: `**TODO**: Describe how users interact`

**What to do:**
1. Read the UI file to understand the interface
2. Find signal connections (`.connect()` calls)
3. Trace what happens when user acts

**Expected output:**
```markdown
**User Interactions:**
1. **Adjust frequency slider** (20-2000 Hz) → Calls `_on_frequency_changed()` → Updates label → Auto-regenerates pattern if auto-refresh enabled
2. **Select plate shape** → Calls `_on_shape_changed()` → Resets particle simulation → Regenerates pattern with new boundary conditions
3. **Click "Generate"** → Calls `_on_generate()` → Creates `SimulationParams` → Passes to `CymaticsSimulationService.simulate()` → Updates viewport
4. **Toggle 3D view** → Switches between 2D canvas and 3D OpenGL surface view
5. **Export pattern** → Opens file dialog → Saves as PNG/GIF via `CymaticsExportService`
```

---

## When You're Unsure

**If source file doesn't exist:**
```markdown
**TODO**: [Source file not found: src/pillars/{pillar}/ui/{file}.py]
```

**If feature isn't implemented:**
```markdown
**TODO**: [Feature not yet implemented - no corresponding code found]
```

**If you can't understand the code:**
```markdown
**TODO**: [Complex implementation - requires architectural review]
```

---

## Success Metrics

Good fill = **Someone reading the doc can understand the feature WITHOUT reading the code**

Bad fill = Generic descriptions that could apply to any feature

**Remember:** It's better to say "not found" than to invent!

---

**Last Updated**: 2026-01-16  
**Applies To**: All TODO markers in wiki/02_pillars/{cymatics,correspondences,tq_lexicon}  
**Review Status**: Ready for use with free models
