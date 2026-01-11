# ADR-011: Unified Geometry Viewer

<!-- Last Verified: 2026-01-10 -->

**Status: Proposed** *(Awaiting Magus Approval)*

**Aligned with:** 
- ADR-010: Canon DSL Adoption
- Hermetic Geometry Canon v1.0
- Visual Liturgy Reference v3.4.0

---

## Context

The Geometry Pillar currently maintains **two separate viewer architectures**:

| Component | 2D (GeometryCalculatorWindow) | 3D (Geometry3DWindow) |
|-----------|-------------------------------|------------------------|
| Location | `ui/calculator/calculator_window.py` | `ui/geometry3d/window3d.py` |
| Data Model | `GeometricShape` | `SolidCalculator` |
| Properties | `ShapeProperty` | `SolidProperty` |
| Rendering | `QGraphicsView` + `QGraphicsScene` | Custom QPainter projection |
| Output | `get_drawing_instructions()` → Dict | `SolidPayload` |
| History | ❌ None | ❌ None |
| Canon Integration | ❌ None | ✓ Vault of Hestia only |
| View Model | `GeometryViewModel` | Direct manipulation |

This dual architecture causes several problems:

1. **Code Duplication** — ~60% of UI logic (property panels, export, snapshots) is duplicated
2. **Inconsistent UX** — Different layouts, controls, and workflows confuse users
3. **No Calculation History** — Users cannot undo, compare, or review past calculations
4. **Fragmented Canon Migration** — Each viewer must be migrated separately
5. **Testing Burden** — Two separate test matrices
6. **Maintenance Cost** — Visual Liturgy changes must be applied twice

The adoption of the **Canon DSL** (ADR-010) provides a natural unifying abstraction: `Declaration` is dimension-agnostic. Forms declare `dimensional_class: int` (2 or 3), enabling a single viewer that adapts its rendering based on content.

---

## Decision

We will build a **Unified Geometry Viewer** that handles both 2D shapes and 3D solids through a single, Canon-compliant architecture.

### Core Principle

**One Window, Adaptive Rendering, Unified History**

```python
# Both 2D and 3D flow through the same path
decl = solver.create_declaration(user_input)
verdict = engine.validate(decl)
result = engine.realize(decl)
payload = result.get_artifact("geometry")

# Viewer adapts based on payload dimension
viewer.set_payload(payload)  # Auto-detects 2D vs 3D
```

### Architectural Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      UnifiedGeometryViewer                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌─────────────────────────────┐  ┌───────────────────┐  │
│  │ Properties   │  │         Viewport            │  │     Console       │  │
│  │ Panel        │  │                             │  │                   │  │
│  │              │  │  ┌───────────────────────┐  │  │ ┌───────────────┐ │  │
│  │ • Title      │  │  │                       │  │  │ │ Tab Bar       │ │  │
│  │ • Inputs     │  │  │   AdaptiveRenderer    │  │  │ │               │ │  │
│  │ • Derived    │  │  │                       │  │  │ │ Display       │ │  │
│  │ • Readonly   │  │  │   dim=2 → 2D Scene    │  │  │ │ View/Camera   │ │  │
│  │              │  │  │   dim=3 → 3D View     │  │  │ │ Output        │ │  │
│  │ ┌──────────┐ │  │  │                       │  │  │ │ History  NEW  │ │  │
│  │ │✓ Canon   │ │  │  └───────────────────────┘  │  │ │ Canon    NEW  │ │  │
│  │ │Badge     │ │  │                             │  │ └───────────────┘ │  │
│  │ │φ = 1.618 │ │  │  ┌───────────────────────┐  │  │                   │  │
│  │ │sig:a3f2  │ │  │  │ Status Bar            │  │  │ History Panel:    │  │
│  │ └──────────┘ │  │  │ ✓ Canon · 24v · φ     │  │  │ ▸ a3f2 current   │  │
│  │              │  │  └───────────────────────┘  │  │   b4c1 10:32      │  │
│  │ [Calculate]  │  │                             │  │   c5d0 10:28      │  │
│  │              │  │  [Axes] [Labels] [Measure]  │  │ [Restore][Compare]│  │
│  └──────────────┘  └─────────────────────────────┘  └───────────────────┘  │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Canon Engine │ Declaration History │ Undo/Redo │ Export (JSON/PNG/PDF)     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### New Data Structures

```python
# Unified payload for any geometry (2D or 3D)
@dataclass(frozen=True)
class GeometryPayload:
    """Unified output from Canon realization."""
    
    dimensional_class: int  # 2 or 3
    
    # 2D data (populated if dim=2)
    drawing_instructions: Optional[DrawingInstructions] = None
    
    # 3D data (populated if dim=3)
    solid_payload: Optional[SolidPayload] = None
    
    # Always present
    metadata: Dict[str, Any] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_2d(self) -> bool:
        return self.dimensional_class == 2
    
    @property
    def is_3d(self) -> bool:
        return self.dimensional_class == 3


# Calculation history entry
@dataclass
class HistoryEntry:
    """Single entry in calculation history."""
    
    declaration: Declaration
    verdict: Verdict
    result: Optional[RealizeResult]
    timestamp: datetime
    signature: str
    
    @property
    def is_valid(self) -> bool:
        return self.verdict.ok
    
    @property
    def short_signature(self) -> str:
        return self.signature[:8]


# History manager
class DeclarationHistory:
    """Manages calculation history with undo/redo."""
    
    def __init__(self, max_entries: int = 50):
        self._entries: List[HistoryEntry] = []
        self._current_index: int = -1
        self._max_entries = max_entries
    
    def push(self, decl: Declaration, verdict: Verdict, 
             result: Optional[RealizeResult]) -> HistoryEntry:
        """Add new entry, truncate future if undone."""
        ...
    
    def undo(self) -> Optional[HistoryEntry]:
        """Move to previous entry."""
        ...
    
    def redo(self) -> Optional[HistoryEntry]:
        """Move to next entry (if undone)."""
        ...
    
    def get_entry(self, signature: str) -> Optional[HistoryEntry]:
        """Retrieve specific entry by signature."""
        ...
    
    def get_timeline(self) -> List[HistoryEntry]:
        """Return all entries, oldest first."""
        ...
    
    def export_session(self) -> Dict:
        """Export full session as JSON-serializable dict."""
        ...
```

### Adaptive Viewport

```python
class AdaptiveViewport(QWidget):
    """Viewport that switches between 2D and 3D rendering."""
    
    payload_changed = pyqtSignal(object)  # GeometryPayload
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._stack = QStackedWidget()
        
        # 2D renderer
        self._scene_2d = GeometryScene()
        self._view_2d = GeometryView(self._scene_2d)
        
        # 3D renderer
        self._view_3d = Geometry3DView()
        
        self._stack.addWidget(self._view_2d)
        self._stack.addWidget(self._view_3d)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._stack)
    
    def set_payload(self, payload: GeometryPayload):
        """Set payload and switch to appropriate renderer."""
        if payload.is_2d:
            self._scene_2d.set_drawing_instructions(payload.drawing_instructions)
            self._stack.setCurrentWidget(self._view_2d)
        else:
            self._view_3d.set_payload(payload.solid_payload)
            self._stack.setCurrentWidget(self._view_3d)
        
        self.payload_changed.emit(payload)
```

### Console Tabs

| Tab | Contents |
|-----|----------|
| **Display** | Axes, labels, themes, measurement colors |
| **View/Camera** | Pan, zoom, rotation (3D only: elevation, azimuth) |
| **Output** | Snapshot, copy measurements, export formats |
| **History** | Timeline list, restore button, compare button, session export |
| **Canon** | Full validation report, findings list, article references, Declaration JSON |

### History Panel Features

1. **Timeline View** — Chronological list of calculations with signatures and timestamps
2. **Current Indicator** — Visual marker (▸) for active declaration
3. **Restore** — Click any entry to restore that calculation
4. **Compare Mode** — Select two entries for side-by-side comparison
5. **Session Export** — Export full history as JSON for reproducibility
6. **Keyboard Shortcuts** — Ctrl+Z (undo), Ctrl+Y (redo), Ctrl+Shift+Z (redo)

### Canon Tab Features

1. **Validation Status** — Large badge with ✓/⚠/✗
2. **Summary Line** — "Passed with 2 warnings" or "Failed: 1 blocking finding"
3. **Findings List** — Full list with severity icons, messages, article refs
4. **Declaration View** — Read-only JSON view of current declaration
5. **Copy Actions** — Copy Declaration JSON, Copy Validation Report
6. **Article Links** — Clickable Canon article references (opens in wiki)

### Unified Solver Interface

```python
class GeometrySolver(ABC):
    """Base solver for both 2D shapes and 3D solids."""
    
    @property
    @abstractmethod
    def form_type(self) -> str:
        """Return the Canon form type (e.g., 'Circle', 'VaultOfHestia')."""
        pass
    
    @property
    @abstractmethod
    def dimensional_class(self) -> int:
        """Return 2 for shapes, 3 for solids."""
        pass
    
    @property
    @abstractmethod
    def canonical_parameter(self) -> str:
        """Return the name of the canonical parameter (e.g., 'radius', 'side_length')."""
        pass
    
    @abstractmethod
    def solve(self, known_property: str, value: float) -> float:
        """Convert any property to the canonical parameter."""
        pass
    
    @abstractmethod
    def create_declaration(self, canonical_value: float) -> Declaration:
        """Create a Canon-compliant Declaration."""
        pass
    
    def get_editable_properties(self) -> List[PropertyDefinition]:
        """Return properties the user can edit."""
        pass
    
    def get_derived_properties(self) -> List[PropertyDefinition]:
        """Return properties computed from the canonical parameter."""
        pass
```

---

## Migration Strategy

### Phase A: Foundation (Week 1)

| Task | Description |
|------|-------------|
| Create `GeometryPayload` | Unified payload dataclass |
| Create `HistoryEntry` | History entry dataclass |
| Create `DeclarationHistory` | History manager with undo/redo |
| Create `AdaptiveViewport` | Stacked widget with 2D/3D views |
| Create `GeometrySolver` ABC | Unified solver interface |

### Phase B: Unified Window Shell (Week 2)

| Task | Description |
|------|-------------|
| Create `UnifiedGeometryViewer` | Main window class |
| Implement Properties Panel | Reuse/adapt from existing |
| Implement Console with tabs | Display, View, Output from existing |
| Add History Tab | New — timeline, restore, export |
| Add Canon Tab | New — validation details, JSON view |
| Add status bar | Unified format for 2D/3D |

### Phase C: 3D Migration (Week 3)

| Task | Description |
|------|-------------|
| Adapt `Geometry3DView` | Work in AdaptiveViewport |
| Migrate Vault of Hestia | Already Canon-compliant |
| Create Platonic Solid solvers | Tetrahedron, Cube, Octahedron, etc. |
| Create Platonic Solid realizers | Wrap existing services |
| Update geometry_definitions.py | Point 3D entries to UnifiedViewer |

### Phase D: 2D Migration (Week 4)

| Task | Description |
|------|-------------|
| Adapt `GeometryScene` | Work in AdaptiveViewport |
| Create Circle solver/realizer | Simple starting point |
| Create Polygon solver/realizer | Regular n-gons |
| Create special shape solvers | Golden Rectangle, etc. |
| Update geometry_definitions.py | Point 2D entries to UnifiedViewer |

### Phase E: Polish (Week 5)

| Task | Description |
|------|-------------|
| Compare Mode | Side-by-side declaration comparison |
| Keyboard Shortcuts | Undo/redo bindings |
| Session Persistence | Save/load history |
| Visual Liturgy audit | Full compliance check |
| Documentation | User guide, contributor guide |

---

## Architectural Guarantees

### 1. Single Source of Truth

The `Declaration` stored in history is the **only** authoritative specification. Derived values (vertices, edges, properties) are computed from the declaration, never stored independently.

### 2. History Immutability

Once a `HistoryEntry` is created, it is immutable. Restoring an entry creates a *new* entry (with the same declaration) rather than modifying history.

### 3. Dimension Agnosticism

All shared code (history, Canon integration, export) treats dimension as data. Only the `AdaptiveViewport` and property definitions vary by dimension.

### 4. Backward Compatibility

The legacy `GeometryCalculatorWindow` and `Geometry3DWindow` remain functional during migration. Entries in `geometry_definitions.py` specify which viewer to use via `window_class`.

### 5. Visual Liturgy Compliance

All new components use `COLORS` tokens and archetype patterns. No hardcoded hex values.

### 6. Pillar Sovereignty

The unified viewer lives in `src/pillars/geometry/ui/unified/`. It imports from `shared.ui` and `canon_dsl`, but not from other pillars.

---

## Consequences

### Positive

1. **Code Reduction** — ~50% less UI code to maintain
2. **Consistent UX** — Same workflow for all geometry
3. **Calculation History** — Undo, compare, reproduce
4. **Unified Canon** — Same validation for 2D and 3D
5. **Easier Testing** — One test matrix instead of two
6. **Future Features** — Templates, batch validation, session sharing

### Negative

1. **Migration Effort** — Significant refactoring required
2. **Complexity** — AdaptiveViewport adds indirection
3. **Risk** — Breaking existing functionality during migration
4. **Learning Curve** — Contributors must understand unified architecture

### Neutral

1. **Performance** — Rendering unchanged; history adds minimal overhead
2. **Dependencies** — No new external dependencies
3. **File Count** — Fewer files overall (consolidation)

---

## Alternatives Considered

### Alternative 1: Enhance Existing Viewers Separately

Add history and Canon integration to both viewers independently.

**Rejected because:** Doubles maintenance burden, perpetuates inconsistency, violates DRY.

### Alternative 2: 2D-Only Unification

Unify only 2D shapes, leave 3D separate.

**Rejected because:** 3D is where Canon integration already exists. Partial unification provides partial benefit at similar cost.

### Alternative 3: Tabbed Window (2D Tab + 3D Tab)

Single window with tabs switching between completely separate 2D and 3D implementations.

**Rejected because:** Still maintains two codebases internally. History and Canon would still be duplicated.

### Alternative 4: External Viewer Application

Build viewer as separate Electron/web app communicating via IPC.

**Rejected because:** Architectural over-engineering. PyQt6 is sufficient. Adds deployment complexity.

---

## File Structure

```
src/pillars/geometry/ui/unified/
├── __init__.py
├── unified_viewer.py          # UnifiedGeometryViewer main window
├── adaptive_viewport.py       # AdaptiveViewport (2D/3D switch)
├── panels/
│   ├── __init__.py
│   ├── properties_panel.py    # Left panel
│   └── console_panel.py       # Right panel with tabs
├── tabs/
│   ├── __init__.py
│   ├── display_tab.py
│   ├── view_tab.py
│   ├── output_tab.py
│   ├── history_tab.py         # NEW
│   └── canon_tab.py           # NEW
├── history/
│   ├── __init__.py
│   ├── history_entry.py
│   ├── history_manager.py
│   └── history_widget.py
└── payloads/
    ├── __init__.py
    └── geometry_payload.py
```

---

## Implementation Checklist

### Phase A: Foundation

- [ ] Create `src/pillars/geometry/ui/unified/` directory
- [ ] Implement `GeometryPayload` dataclass
- [ ] Implement `HistoryEntry` dataclass
- [ ] Implement `DeclarationHistory` manager
- [ ] Implement `AdaptiveViewport` widget
- [ ] Define `GeometrySolver` ABC in `canon_dsl`
- [ ] Write unit tests for history manager

### Phase B: Unified Window Shell

- [ ] Create `UnifiedGeometryViewer` main window
- [ ] Implement Properties Panel
- [ ] Implement Console Panel with tab bar
- [ ] Implement Display Tab (port from existing)
- [ ] Implement View/Camera Tab (port from existing)
- [ ] Implement Output Tab (port from existing)
- [ ] Implement History Tab (new)
- [ ] Implement Canon Tab (new)
- [ ] Implement status bar
- [ ] Visual Liturgy compliance check

### Phase C: 3D Migration

- [ ] Integrate `Geometry3DView` into AdaptiveViewport
- [ ] Verify Vault of Hestia works in unified viewer
- [ ] Create `TetrahedronSolver` and `TetrahedronRealizer`
- [ ] Create `CubeSolver` and `CubeRealizer`
- [ ] Create `OctahedronSolver` and `OctahedronRealizer`
- [ ] Create `IcosahedronSolver` and `IcosahedronRealizer`
- [ ] Create `DodecahedronSolver` and `DodecahedronRealizer`
- [ ] Update geometry_definitions.py for 3D entries

### Phase D: 2D Migration

- [ ] Integrate `GeometryScene`/`GeometryView` into AdaptiveViewport
- [ ] Create `CircleSolver` and `CircleRealizer`
- [ ] Create `PolygonSolver` and `PolygonRealizer`
- [ ] Create `RectangleSolver` and `RectangleRealizer`
- [ ] Create `GoldenRectangleSolver` and `GoldenRectangleRealizer`
- [ ] Create `TriangleSolver` and `TriangleRealizer`
- [ ] Update geometry_definitions.py for 2D entries

### Phase E: Polish

- [ ] Implement Compare Mode in History Tab
- [ ] Add keyboard shortcuts (Ctrl+Z, Ctrl+Y)
- [ ] Add session save/load
- [ ] Full Visual Liturgy audit
- [ ] Write user documentation
- [ ] Write contributor migration guide
- [ ] Deprecate legacy viewers (add warnings)

---

## References

- [ADR-010: Canon DSL Adoption](./ADR-010_canon_dsl_adoption.md)
- [Hermetic Geometry Canon v1.0](../HERMETIC_GEOMETRY_CANON.md)
- [Visual Liturgy Reference](../../00_foundations/VISUAL_LITURGY_REFERENCE.md)
- [Canon DSL Implementation Spec](../../00_foundations/Canon%20DSL%20Implementation.md)

---

*"The Circle and the Sphere are One; only the Eye that perceives them differs."*

*This ADR proposes the unification of all geometric visualization under a single, Canon-compliant viewer.*
