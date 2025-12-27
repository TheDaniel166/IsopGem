# Geometry Pillar - Anatomy Chart

<!-- Last Verified: 2025-12-27 -->

This manifest dissects the Sacred Geometry pillar, mapping the transition from 2D plane logic to 3D solid manifolds.



---

**File:** `src/pillars/geometry/services/annulus_shape.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Annulus (ring) shape calculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_shape.GeometricShape`
* `base_shape.ShapeProperty`
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/archimedean_data.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Canonical Archimedean solid datasets auto-generated from dmccooey.com.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* None.

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/geometry/services/archimedean_solids.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Archimedean solid services and calculators.

**Input (Ingests):**
* `edge_length` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `face_count` (Field)
* `edge_count` (Field)
* `vertex_count` (Field)
* `face_sides` (Field)
* `face_metrics` (Field)
* `payload` (Field)
* `metrics` (Field)
* `key` (Field)
* `name` (Field)
* `canonical_vertices` (Field)
* `faces` (Field)
* `edges` (Field)
* `base_edge_length` (Field)
* `base_surface_area` (Field)
* `base_volume` (Field)
* `face_sides` (Field)
* `edge_length`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `archimedean_data.ARCHIMEDEAN_DATA`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.Edge`
* `shared.solid_payload.Face`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `shared.solid_payload.Vec3`
* `solid_geometry.compute_surface_area`
* `solid_geometry.compute_volume`
* `solid_geometry.edges_from_faces`
* `solid_geometry.vec_cross`
* `solid_geometry.vec_dot`
* `solid_geometry.vec_length`
* `solid_geometry.vec_normalize`
* `soli

**Consumers (Who Needs It):**
* `src/pillars/tq/services/platonic_transition_service.py`
* `tests/rituals/rite_of_archimedes_metrics.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/base_shape.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Base class for geometric shape calculators.

**Input (Ingests):**
* `name` (Field)
* `key` (Field)
* `value` (Field)
* `unit` (Field)
* `readonly` (Field)
* `precision` (Field)
* `default` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `abc.ABC`
* `abc.abstractmethod`
* `dataclasses.dataclass`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `name()` - *Return the name of this shape.*
**Exposes:** `description()` - *Return a brief description of this shape.*
**Exposes:** `calculation_hint()` - *Return a hint about required fields for calculation.*
**Exposes:** `calculate_from_property()` - *Calculate all other properties from a given property value.*
**Exposes:** `get_drawing_instructions()` - *Get instructions for drawing this shape in the viewport.*
**Exposes:** `get_label_positions()` - *Get positions for labels in the viewport.*
**Exposes:** `set_property()` - *Set a property value and recalculate dependent properties.*
**Exposes:** `get_property()` - *Get a property value.*
**Exposes:** `get_all_properties()` - *Get all properties in order.*
**Exposes:** `get_editable_properties()` - *Get only editable properties.*
**Exposes:** `get_readonly_properties()` - *Get only readonly (calculated) properties.*
**Exposes:** `validate_value()` - *Validate a property value.*
**Exposes:** `clear_all()` - *Clear all property values.*
**Exposes:** `to_dict()` - *Serialize shape state to dictionary.*
**Exposes:** `from_dict()` - *Restore shape state from dictionary.*


---

**File:** `src/pillars/geometry/services/circle_shape.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Circle shape calculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_shape.GeometricShape`
* `base_shape.ShapeProperty`
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `scripts/verification_seal.py`

**Key Interactions:**
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Calculate all properties from any given property.*
**Exposes:** `get_drawing_instructions()` - *Get drawing instructions for the circle.*
**Exposes:** `get_label_positions()` - *Get label positions for the circle.*


---

**File:** `src/pillars/geometry/services/complex_prismatic_solids.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Complex Prismatic and Johnson Solids.

**Input (Ingests):**
* `payload` (Field)
* `metadata` (Field)
* `edge`
* `edge`
* `prism_h`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_geometry.Vec3`
* `solid_geometry.edges_from_faces`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/cone_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Cone 3D Solid Service.

**Input (Ingests):**
* `radius` (Field)
* `height` (Field)
* `slant_height` (Field)
* `base_circumference` (Field)
* `base_area` (Field)
* `lateral_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `payload` (Field)
* `metrics` (Field)
* `radius`
* `height`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_geometry.Vec3`
* `solid_geometry.edges_from_faces`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_calculator_refinement.py`
* `tests/rituals/rite_of_trinity_3d.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/crescent_shape.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Crescent (lune) shape calculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_shape.GeometricShape`
* `base_shape.ShapeProperty`
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/cube_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Cube solid math utilities and calculator.

**Input (Ingests):**
* `edge_length` (Field)
* `face_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `face_diagonal` (Field)
* `space_diagonal` (Field)
* `inradius` (Field)
* `midradius` (Field)
* `circumradius` (Field)
* `incircle_circumference` (Field)
* `midsphere_circumference` (Field)
* `circumcircle_circumference` (Field)
* `faces` (Field)
* `edges` (Field)
* `vertices` (Field)
* `face_sides` (Field)
* `vertex_valence` (Field)
* `dihedral_angle_deg` (Field)
* `solid_angle_sr` (Field)
* `face_inradius` (Field)
* `face_circumradius` (Field)
* `insphere_surface_area` (Field)
* `insphere_volume` (Field)
* `midsphere_surface_area` (Field)
* `midsphere_volume` (Field)
* `circumsphere_surface_area` (Field)
* `circumsphere_volume` (Field)
* `sphericity` (Field)
* `isoperimetric_quotient` (Field)
* `surface_to_volume_ratio` (Field)
* `moment_inertia_solid` (Field)
* `moment_inertia_shell` (Field)
* `angular_defect_vertex_deg` (Field)
* `total_angular_defect_deg` (Field)
* `euler_characteristic` (Field)
* `packing_density` (Field)
* `symmetry_group_order` (Field)
* `rotational_symmetry_order` (Field)
* `symmetry_group_name` (Field)
* `dual_solid_name` (Field)
* `golden_ratio_factor` (Field)
* `payload` (Field)
* `metrics` (Field)
* `edge_length`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `geometry_visuals.compute_dual_payload`
* `math`
* `platonic_constants.ANGULAR_DEFECT_VERTEX_DEG`
* `platonic_constants.DIHEDRAL_ANGLES_DEG`
* `platonic_constants.DUAL_SOLID_NAME`
* `platonic_constants.GOLDEN_RATIO_FACTOR`
* `platonic_constants.MOMENT_INERTIA_SHELL_K`
* `platonic_constants.MOMENT_INERTIA_SOLID_K`
* `platonic_constants.PACKING_DENSITY`
* `platonic_constants.PlatonicSolid`
* `platonic_constants.ROTATIONAL_SYMMETRY_ORDER`
* `pl

**Consumers (Who Needs It):**
* `src/pillars/tq/services/platonic_transition_service.py`
* `tests/rituals/rite_of_advanced_visualization.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Return all properties in display order.*
**Exposes:** `set_property()` - *Set a property and recalculate all others.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*
**Exposes:** `solver()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/cylinder_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Cylinder 3D Solid Service.

**Input (Ingests):**
* `radius` (Field)
* `height` (Field)
* `circumference` (Field)
* `base_area` (Field)
* `lateral_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `payload` (Field)
* `metrics` (Field)
* `radius`
* `height`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_geometry.Vec3`
* `solid_geometry.edges_from_faces`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_calculator_refinement.py`
* `tests/rituals/rite_of_trinity_3d.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/dodecahedron_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Dodecahedron solid math utilities and calculator.

**Input (Ingests):**
* `edge_length` (Field)
* `face_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `inradius` (Field)
* `midradius` (Field)
* `circumradius` (Field)
* `incircle_circumference` (Field)
* `midsphere_circumference` (Field)
* `circumcircle_circumference` (Field)
* `faces` (Field)
* `edges` (Field)
* `vertices` (Field)
* `face_sides` (Field)
* `vertex_valence` (Field)
* `dihedral_angle_deg` (Field)
* `solid_angle_sr` (Field)
* `face_inradius` (Field)
* `face_circumradius` (Field)
* `insphere_surface_area` (Field)
* `insphere_volume` (Field)
* `midsphere_surface_area` (Field)
* `midsphere_volume` (Field)
* `circumsphere_surface_area` (Field)
* `circumsphere_volume` (Field)
* `sphericity` (Field)
* `isoperimetric_quotient` (Field)
* `surface_to_volume_ratio` (Field)
* `moment_inertia_solid` (Field)
* `moment_inertia_shell` (Field)
* `angular_defect_vertex_deg` (Field)
* `total_angular_defect_deg` (Field)
* `euler_characteristic` (Field)
* `packing_density` (Field)
* `symmetry_group_order` (Field)
* `rotational_symmetry_order` (Field)
* `symmetry_group_name` (Field)
* `dual_solid_name` (Field)
* `golden_ratio_factor` (Field)
* `payload` (Field)
* `metrics` (Field)
* `edge_length`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `geometry_visuals.compute_dual_payload`
* `math`
* `platonic_constants.ANGULAR_DEFECT_VERTEX_DEG`
* `platonic_constants.DIHEDRAL_ANGLES_DEG`
* `platonic_constants.DUAL_SOLID_NAME`
* `platonic_constants.GOLDEN_RATIO_FACTOR`
* `platonic_constants.MOMENT_INERTIA_SHELL_K`
* `platonic_constants.MOMENT_INERTIA_SOLID_K`
* `platonic_constants.PACKING_DENSITY`
* `platonic_constants.PlatonicSolid`
* `platonic_constants.ROTATIONAL_SYMMETRY_ORDER`
* `pl

**Consumers (Who Needs It):**
* `src/pillars/tq/services/platonic_transition_service.py`
* `tests/rituals/rite_of_advanced_visualization.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*
**Exposes:** `solver()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/ellipse_shape.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Ellipse (oval) shape calculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_shape.GeometricShape`
* `base_shape.ShapeProperty`
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/esoteric_wisdom_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** The Esoteric Wisdom Service (The Oracle of Sacred Forms).

**Input (Ingests):**
* `id` (Field)
* `title` (Field)
* `category` (Field)
* `keywords` (Field)
* `has_stellations` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `dataclasses.dataclass`
* `dataclasses.field`
* `logging`
* `typing.Any`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`
* `ui.esoteric_definitions.ESOTERIC_DEFINITIONS`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `get_esoteric_wisdom_service()` - *Get the singleton Esoteric Wisdom Service instance.*
**Exposes:** `get_toc()` - *Get the Table of Contents organized by category.*
**Exposes:** `get_all_topics()` - *Get flat list of all topics.*
**Exposes:** `search()` - *Search across all esoteric definitions.*
**Exposes:** `get_content()` - *Get the full esoteric content for a shape.*
**Exposes:** `get_shape_names()` - *Get list of all shape names with esoteric definitions.*


---

**File:** `src/pillars/geometry/services/figurate_3d.py`

**Role:** `[Muscle] (Service)`

**Purpose:** 3D Figurate Numbers: Tetrahedral, Pyramidal, Octahedral, Cubic.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `math`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `isometric_project()` - *Project 3D coordinates to 2D isometric view.*
**Exposes:** `tetrahedral_number()` - *Calculate the n-th tetrahedral number.*
**Exposes:** `tetrahedral_points()` - *Generate 3D coordinates for a tetrahedral arrangement.*
**Exposes:** `square_pyramidal_number()` - *Calculate the n-th square pyramidal number.*
**Exposes:** `square_pyramidal_points()` - *Generate 3D coordinates for a square pyramidal arrangement.*
**Exposes:** `octahedral_number()` - *Calculate the n-th octahedral number.*
**Exposes:** `octahedral_points()` - *Generate 3D coordinates for an octahedral arrangement.*
**Exposes:** `cubic_number()` - *Calculate the n-th cubic number.*
**Exposes:** `cubic_points()` - *Generate 3D coordinates for a cubic arrangement.*
**Exposes:** `centered_cubic_number()` - *Calculate the n-th centered cubic number.*
**Exposes:** `project_points_isometric()` - *Project a list of 3D points to 2D isometric coordinates.*
**Exposes:** `project_dynamic()` - *Project points using dynamic Yaw/Pitch angles.*
**Exposes:** `get_layer_for_point()` - *Determine which layer (z-level) a point belongs to.*
**Exposes:** `centered_cubic_points()` - *Generate 3D coordinates for a Centered Cubic arrangement.*
**Exposes:** `stellated_octahedron_number()` - *Calculate the n-th stellated octahedron number.*
**Exposes:** `stellated_octahedron_points()` - *Generate 3D coordinates for a Stellated Octahedron (Merkaba).*
**Exposes:** `icosahedral_number()` - *Centered Icosahedral number.*
**Exposes:** `icosahedral_points()` - *Generate Centered Icosahedral points.*
**Exposes:** `dodecahedral_number()` - *Centered Dodecahedral number.*
**Exposes:** `dodecahedral_points()` - *Generate Centered Dodecahedral points.*


---

**File:** `src/pillars/geometry/services/general_prismatic_solids.py`

**Role:** `[Muscle] (Service)`

**Purpose:** General (n-gonal) Prismatic Solid Services and Calculators.

**Input (Ingests):**
* `sides`
* `base_edge`
* `height`
* `sides`
* `base_edge`
* `height`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `regular_antiprism_solids.RegularAntiprismMetrics`
* `regular_antiprism_solids.RegularAntiprismSolidCalculatorBase`
* `regular_antiprism_solids.RegularAntiprismSolidResult`
* `regular_antiprism_solids.RegularAntiprismSolidServiceBase`
* `regular_antiprism_solids._create_payload`
* `regular_prism_solids.RegularPrismMetrics`
* `regular_prism_solids.RegularPrismSolidCalculatorBase`
* `regular_prism_solids.RegularPrismSolidResult`
* `re

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build_dynamic()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `build_dynamic()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/general_pyramid_solids.py`

**Role:** `[Muscle] (Service)`

**Purpose:** General (n-gonal) Pyramid Solid Services and Calculators.

**Input (Ingests):**
* `sides`
* `base_edge`
* `height`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `regular_pyramid_solids.RegularPyramidMetrics`
* `regular_pyramid_solids.RegularPyramidSolidCalculatorBase`
* `regular_pyramid_solids.RegularPyramidSolidResult`
* `regular_pyramid_solids.RegularPyramidSolidServiceBase`
* `regular_pyramid_solids._apothem`
* `regular_pyramid_solids._base_area`
* `regular_pyramid_solids._build_edges`
* `regular_pyramid_solids._build_faces`
* `regular_pyramid_solids._build_vertices`
* `regular_pyramid_s

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build_dynamic()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/geometry_visuals.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Geometry visualization services.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Set`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `compute_dual_payload()` - *Generate the dual solid for a given primal polyhedron.*


---

**File:** `src/pillars/geometry/services/golden_pyramid_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Golden ratio-aligned square pyramid service and calculator.

**Input (Ingests):**
* `base_edge` (Field)
* `height` (Field)
* `slant_height` (Field)
* `phi_ratio` (Field)
* `base_apothem` (Field)
* `base_area` (Field)
* `lateral_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `payload` (Field)
* `metrics` (Field)
* `base_edge`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/icosahedron_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Icosahedron solid math utilities and calculator.

**Input (Ingests):**
* `edge_length` (Field)
* `face_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `inradius` (Field)
* `midradius` (Field)
* `circumradius` (Field)
* `incircle_circumference` (Field)
* `midsphere_circumference` (Field)
* `circumcircle_circumference` (Field)
* `faces` (Field)
* `edges` (Field)
* `vertices` (Field)
* `face_sides` (Field)
* `vertex_valence` (Field)
* `dihedral_angle_deg` (Field)
* `solid_angle_sr` (Field)
* `face_inradius` (Field)
* `face_circumradius` (Field)
* `insphere_surface_area` (Field)
* `insphere_volume` (Field)
* `midsphere_surface_area` (Field)
* `midsphere_volume` (Field)
* `circumsphere_surface_area` (Field)
* `circumsphere_volume` (Field)
* `sphericity` (Field)
* `isoperimetric_quotient` (Field)
* `surface_to_volume_ratio` (Field)
* `moment_inertia_solid` (Field)
* `moment_inertia_shell` (Field)
* `angular_defect_vertex_deg` (Field)
* `total_angular_defect_deg` (Field)
* `euler_characteristic` (Field)
* `packing_density` (Field)
* `symmetry_group_order` (Field)
* `rotational_symmetry_order` (Field)
* `symmetry_group_name` (Field)
* `dual_solid_name` (Field)
* `golden_ratio_factor` (Field)
* `payload` (Field)
* `metrics` (Field)
* `edge_length`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `geometry_visuals.compute_dual_payload`
* `math`
* `platonic_constants.ANGULAR_DEFECT_VERTEX_DEG`
* `platonic_constants.DIHEDRAL_ANGLES_DEG`
* `platonic_constants.DUAL_SOLID_NAME`
* `platonic_constants.GOLDEN_RATIO_FACTOR`
* `platonic_constants.MOMENT_INERTIA_SHELL_K`
* `platonic_constants.MOMENT_INERTIA_SOLID_K`
* `platonic_constants.PACKING_DENSITY`
* `platonic_constants.PlatonicSolid`
* `platonic_constants.ROTATIONAL_SYMMETRY_ORDER`
* `pl

**Consumers (Who Needs It):**
* `src/pillars/tq/services/platonic_transition_service.py`
* `tests/rituals/rite_of_advanced_visualization.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*
**Exposes:** `solver()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/irregular_polygon_shape.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Irregular Polygon shape calculator.

**Input (Ingests):**
* `points`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `base_shape.GeometricShape`
* `base_shape.ShapeProperty`
* `math`
* `quadrilateral_shape._polygon_centroid`
* `quadrilateral_shape._shoelace_area`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `set_points()` - *Set the vertices and update properties.*
**Exposes:** `calculate_from_property()` - *Update a coordinate.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/measurement_utils.py`

**Role:** `[Muscle] (Service)`

**Purpose:** 3D measurement utilities for geometry viewport.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `math`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `distance_3d()` - *Calculate Euclidean distance between two 3D points.*
**Exposes:** `cross_product()` - *Calculate cross product of two vectors.*
**Exposes:** `vector_magnitude()` - *Calculate magnitude of a vector.*
**Exposes:** `subtract_vectors()` - *Subtract v2 from v1.*
**Exposes:** `triangle_area_3d()` - *Calculate area of a 3D triangle using cross product.*
**Exposes:** `polygon_area_3d()` - *Calculate area of a 3D polygon by triangulation.*
**Exposes:** `signed_tetrahedron_volume()` - *Calculate signed volume of a tetrahedron.*
**Exposes:** `polyhedron_volume()` - *Calculate volume of a closed polyhedron.*
**Exposes:** `polyhedron_surface_area()` - *Calculate total surface area of a polyhedron.*


---

**File:** `src/pillars/geometry/services/oblique_prism_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Oblique regular prism solid services and calculators.

**Input (Ingests):**
* `sides` (Field)
* `base_edge` (Field)
* `height` (Field)
* `skew_x` (Field)
* `skew_y` (Field)
* `skew_magnitude` (Field)
* `base_area` (Field)
* `base_perimeter` (Field)
* `base_apothem` (Field)
* `base_circumradius` (Field)
* `lateral_edge_length` (Field)
* `lateral_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `payload` (Field)
* `metrics` (Field)
* `base_edge`
* `height`
* `skew_x`
* `skew_y`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `regular_prism_solids._apothem`
* `regular_prism_solids._area`
* `regular_prism_solids._circumradius`
* `shared.solid_payload.Edge`
* `shared.solid_payload.Face`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `shared.solid_payload.Vec3`
* `solid_geometry.compute_surface_area`
* `solid_geometry.compute_volume`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/octahedron_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Octahedron solid math utilities and calculator.

**Input (Ingests):**
* `edge_length` (Field)
* `face_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `inradius` (Field)
* `midradius` (Field)
* `circumradius` (Field)
* `incircle_circumference` (Field)
* `midsphere_circumference` (Field)
* `circumcircle_circumference` (Field)
* `faces` (Field)
* `edges` (Field)
* `vertices` (Field)
* `face_sides` (Field)
* `vertex_valence` (Field)
* `dihedral_angle_deg` (Field)
* `solid_angle_sr` (Field)
* `face_inradius` (Field)
* `face_circumradius` (Field)
* `insphere_surface_area` (Field)
* `insphere_volume` (Field)
* `midsphere_surface_area` (Field)
* `midsphere_volume` (Field)
* `circumsphere_surface_area` (Field)
* `circumsphere_volume` (Field)
* `sphericity` (Field)
* `isoperimetric_quotient` (Field)
* `surface_to_volume_ratio` (Field)
* `moment_inertia_solid` (Field)
* `moment_inertia_shell` (Field)
* `angular_defect_vertex_deg` (Field)
* `total_angular_defect_deg` (Field)
* `euler_characteristic` (Field)
* `packing_density` (Field)
* `symmetry_group_order` (Field)
* `rotational_symmetry_order` (Field)
* `symmetry_group_name` (Field)
* `dual_solid_name` (Field)
* `golden_ratio_factor` (Field)
* `payload` (Field)
* `metrics` (Field)
* `edge_length`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `geometry_visuals.compute_dual_payload`
* `math`
* `platonic_constants.ANGULAR_DEFECT_VERTEX_DEG`
* `platonic_constants.DIHEDRAL_ANGLES_DEG`
* `platonic_constants.DUAL_SOLID_NAME`
* `platonic_constants.GOLDEN_RATIO_FACTOR`
* `platonic_constants.MOMENT_INERTIA_SHELL_K`
* `platonic_constants.MOMENT_INERTIA_SOLID_K`
* `platonic_constants.PACKING_DENSITY`
* `platonic_constants.PlatonicSolid`
* `platonic_constants.ROTATIONAL_SYMMETRY_ORDER`
* `pl

**Consumers (Who Needs It):**
* `src/pillars/tq/services/platonic_transition_service.py`
* `tests/rituals/rite_of_advanced_visualization.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*
**Exposes:** `solver()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/persistence_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_shape.GeometricShape`
* `datetime.datetime`
* `json`
* `os`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* `scripts/verification_seal.py`

**Key Interactions:**
**Exposes:** `save_calculation()` - *Save the current state of a shape to history.*
**Exposes:** `update_note()` - *Update the note for a specific history entry.*
**Exposes:** `delete_calculation()` - *Delete a history entry by timestamp.*
**Exposes:** `get_recent_calculations()` - *Get list of recent calculations.*
**Exposes:** `clear_history()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/platonic_constants.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Platonic Solid Constants and Formulas.

**Input (Ingests):**
* `p` (Field)
* `q` (Field)
* `faces` (Field)
* `vertices` (Field)
* `edges` (Field)
* `name` (Field)
* `key` (Field)
* `unit` (Field)
* `precision` (Field)
* `power` (Field)
* `base_value` (Field)
* `editable` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `enum.Enum`
* `math`
* `typing.Dict`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `face_inradius()` - *Inradius of a regular p-gon face.*
**Exposes:** `face_circumradius()` - *Circumradius of a regular p-gon face.*
**Exposes:** `face_area()` - *Area of a regular p-gon face.*
**Exposes:** `edge_from_face_inradius()` - *Derive edge length from face inradius.*
**Exposes:** `edge_from_face_circumradius()` - *Derive edge length from face circumradius.*
**Exposes:** `edge_from_face_area()` - *Derive edge length from face area.*
**Exposes:** `sphere_surface_area()` - *Surface area of a sphere: 4πr²*
**Exposes:** `sphere_volume()` - *Volume of a sphere: (4/3)πr³*
**Exposes:** `radius_from_sphere_surface_area()` - *Derive radius from sphere surface area.*
**Exposes:** `radius_from_sphere_volume()` - *Derive radius from sphere volume.*
**Exposes:** `sphericity()` - *Sphericity: how close to a sphere.*
**Exposes:** `isoperimetric_quotient()` - *Isoperimetric quotient (IQ).*
**Exposes:** `surface_to_volume_ratio()` - *Surface area to volume ratio.*
**Exposes:** `angular_defect_vertex()` - *Angular defect at a vertex in radians.*
**Exposes:** `euler_characteristic()` - *V - E + F = 2 for convex polyhedra.*
**Exposes:** `scale()` - *Scale base value to given edge length.*
**Exposes:** `solve_edge()` - *Solve for edge length given this property's value.*


---

**File:** `src/pillars/geometry/services/polygon_shape.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Regular polygon shape calculator.

**Input (Ingests):**
* `num_sides`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_shape.GeometricShape`
* `base_shape.ShapeProperty`
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `tests/verify_geometry_fixes.py`

**Key Interactions:**
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Calculate all properties from any given property.*
**Exposes:** `get_drawing_instructions()` - *Get drawing instructions for the regular polygon.*
**Exposes:** `get_label_positions()` - *Get label positions for the polygon (static diagram positions).*


---

**File:** `src/pillars/geometry/services/polygonal_numbers.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Helpers for generating polygonal and centered polygonal number layouts.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `math`
* `typing.List`
* `typing.Sequence`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `tests/geometry/test_polygonal_numbers.py`

**Key Interactions:**
**Exposes:** `polygonal_number_value()` - *Return the standard polygonal number value for a given polygon and index.*
**Exposes:** `centered_polygonal_value()` - *Return the centered polygonal number value for a given polygon and index.*
**Exposes:** `polygonal_number_points()` - *Generate dot coordinates for polygonal or centered polygonal numbers.*
**Exposes:** `polygonal_outline_points()` - *Return the outer polygon outline for the given polygonal number order.*
**Exposes:** `max_radius()` - *Maximum radius used by the generator for concentric layouts.*
**Exposes:** `star_number_value()` - *Return the star number value (centered hexagram) for a given index.*
**Exposes:** `generalized_star_number_value()` - *Return the star number value for a p-gram (p points) at a given index.*
**Exposes:** `star_number_points()` - *Generate dot coordinates for star numbers (centered hexagrams).*
**Exposes:** `generalized_star_number_points()` - *Generate dot coordinates for generalized star numbers (centered p-grams).*


---

**File:** `src/pillars/geometry/services/prismatic_frustum_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Prismatic frustum solid service and calculator.

**Input (Ingests):**
* `sides` (Field)
* `bottom_edge` (Field)
* `top_edge` (Field)
* `height` (Field)
* `bottom_area` (Field)
* `top_area` (Field)
* `bottom_perimeter` (Field)
* `top_perimeter` (Field)
* `bottom_apothem` (Field)
* `top_apothem` (Field)
* `bottom_circumradius` (Field)
* `top_circumradius` (Field)
* `lateral_edge_length` (Field)
* `lateral_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `payload` (Field)
* `metrics` (Field)
* `bottom_edge`
* `top_edge`
* `height`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `regular_prism_solids._apothem`
* `regular_prism_solids._area`
* `regular_prism_solids._circumradius`
* `shared.solid_payload.Edge`
* `shared.solid_payload.Face`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `shared.solid_payload.Vec3`
* `solid_geometry.compute_surface_area`
* `solid_geometry.compute_volume`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/quadrilateral_shape.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Quadrilateral shape calculators.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `base_shape.GeometricShape`
* `base_shape.ShapeProperty`
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/rectangular_prism_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Right rectangular prism solid service and calculator.

**Input (Ingests):**
* `length` (Field)
* `width` (Field)
* `height` (Field)
* `base_area` (Field)
* `base_perimeter` (Field)
* `lateral_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `face_diagonal_length` (Field)
* `face_diagonal_width` (Field)
* `space_diagonal` (Field)
* `payload` (Field)
* `metrics` (Field)
* `length`
* `width`
* `height`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/rectangular_pyramid_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Right rectangular pyramid solid service and calculator.

**Input (Ingests):**
* `base_length` (Field)
* `base_width` (Field)
* `height` (Field)
* `slant_length` (Field)
* `slant_width` (Field)
* `base_area` (Field)
* `lateral_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `base_diagonal` (Field)
* `lateral_edge` (Field)
* `payload` (Field)
* `metrics` (Field)
* `base_length`
* `base_width`
* `height`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/regular_antiprism_solids.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Regular antiprism solid services and calculators.

**Input (Ingests):**
* `sides` (Field)
* `base_edge` (Field)
* `height` (Field)
* `base_area` (Field)
* `base_perimeter` (Field)
* `base_apothem` (Field)
* `base_circumradius` (Field)
* `lateral_edge_length` (Field)
* `lateral_chord_length` (Field)
* `lateral_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `payload` (Field)
* `metrics` (Field)
* `base_edge`
* `height`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `regular_prism_solids._apothem`
* `regular_prism_solids._area`
* `regular_prism_solids._circumradius`
* `shared.solid_payload.Edge`
* `shared.solid_payload.Face`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `shared.solid_payload.Vec3`
* `solid_geometry.compute_surface_area`
* `solid_geometry.compute_volume`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.T

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_calculator_refinement.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/regular_prism_solids.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Right regular prism solid services and calculators.

**Input (Ingests):**
* `sides` (Field)
* `base_edge` (Field)
* `height` (Field)
* `base_area` (Field)
* `base_perimeter` (Field)
* `base_apothem` (Field)
* `base_circumradius` (Field)
* `lateral_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `payload` (Field)
* `metrics` (Field)
* `base_edge`
* `height`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Sequence`
* `typing.Tuple`
* `typing.Type`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_calculator_refinement.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/regular_pyramid_frustum_solids.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Regular polygon pyramid frustum services and calculators.

**Input (Ingests):**
* `sides` (Field)
* `base_edge` (Field)
* `top_edge` (Field)
* `height` (Field)
* `slant_height` (Field)
* `base_apothem` (Field)
* `top_apothem` (Field)
* `base_area` (Field)
* `top_area` (Field)
* `lateral_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `base_perimeter` (Field)
* `top_perimeter` (Field)
* `base_circumradius` (Field)
* `top_circumradius` (Field)
* `lateral_edge` (Field)
* `payload` (Field)
* `metrics` (Field)
* `base_edge`
* `top_edge`
* `height`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Sequence`
* `typing.Tuple`
* `typing.Type`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_calculator_refinement.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/regular_pyramid_solids.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Right regular n-gonal pyramid solid services and calculators.

**Input (Ingests):**
* `sides` (Field)
* `base_edge` (Field)
* `height` (Field)
* `slant_height` (Field)
* `base_apothem` (Field)
* `base_area` (Field)
* `lateral_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `base_perimeter` (Field)
* `base_circumradius` (Field)
* `lateral_edge` (Field)
* `payload` (Field)
* `metrics` (Field)
* `base_edge`
* `height`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Sequence`
* `typing.Tuple`
* `typing.Type`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_calculator_refinement.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/rose_curve_shape.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Rose (Rhodonea) curve calculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_shape.GeometricShape`
* `base_shape.ShapeProperty`
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/seed_of_life_shape.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Seed of Life shape calculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_shape.GeometricShape`
* `base_shape.ShapeProperty`
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `scripts/verify_seed_of_life.py`

**Key Interactions:**
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/shape_detection_service.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Service for detecting geometric shapes from point data.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_shape.GeometricShape`
* `irregular_polygon_shape.IrregularPolygonShape`
* `math`
* `quadrilateral_shape.ParallelogramShape`
* `quadrilateral_shape.RhombusShape`
* `square_shape.RectangleShape`
* `square_shape.SquareShape`
* `triangle_shape.EquilateralTriangleShape`
* `triangle_shape.IsoscelesRightTriangleShape`
* `triangle_shape.IsoscelesTriangleShape`
* `triangle_shape.RightTriangleShape`
* `triangle_shape.ScaleneTriangleShape`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`
* `typ

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `detect_from_points()` - *Analyze points and return the most specific GeometricShape instance.*


---

**File:** `src/pillars/geometry/services/solid_geometry.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Utility math helpers for solid geometry computations.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `math`
* `typing.Iterable`
* `typing.List`
* `typing.Sequence`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `vec_add()` - *Functional interface.*
**Exposes:** `vec_sub()` - *Functional interface.*
**Exposes:** `vec_scale()` - *Functional interface.*
**Exposes:** `vec_dot()` - *Functional interface.*
**Exposes:** `vec_cross()` - *Functional interface.*
**Exposes:** `vec_length()` - *Functional interface.*
**Exposes:** `vec_normalize()` - *Functional interface.*
**Exposes:** `polygon_area()` - *Functional interface.*
**Exposes:** `face_normal()` - *Functional interface.*
**Exposes:** `plane_distance_from_origin()` - *Functional interface.*
**Exposes:** `compute_surface_area()` - *Functional interface.*
**Exposes:** `compute_volume()` - *Functional interface.*
**Exposes:** `edges_from_faces()` - *Functional interface.*
**Exposes:** `face_centroid()` - *Functional interface.*
**Exposes:** `angle_around_axis()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/solid_property.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Shared dataclasses for 3D solid calculators.

**Input (Ingests):**
* `name` (Field)
* `key` (Field)
* `unit` (Field)
* `value` (Field)
* `precision` (Field)
* `editable` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/geometry/services/sphere_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Sphere 3D Solid Service.

**Input (Ingests):**
* `radius` (Field)
* `diameter` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `payload` (Field)
* `metrics` (Field)
* `radius`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_geometry.Vec3`
* `solid_geometry.edges_from_faces`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_trinity_3d.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/square_pyramid_frustum_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Square pyramid frustum solid service and calculator.

**Input (Ingests):**
* `base_edge` (Field)
* `top_edge` (Field)
* `height` (Field)
* `slant_height` (Field)
* `base_apothem` (Field)
* `top_apothem` (Field)
* `base_area` (Field)
* `top_area` (Field)
* `lateral_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `lateral_edge` (Field)
* `payload` (Field)
* `metrics` (Field)
* `base_edge`
* `top_edge`
* `height`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/square_pyramid_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Square pyramid solid math utilities and calculator.

**Input (Ingests):**
* `base_edge` (Field)
* `height` (Field)
* `slant_height` (Field)
* `base_apothem` (Field)
* `base_area` (Field)
* `lateral_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `lateral_edge` (Field)
* `payload` (Field)
* `metrics` (Field)
* `base_edge`
* `height`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/square_shape.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Square and Rectangle shape calculators.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_shape.GeometricShape`
* `base_shape.ShapeProperty`
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `tests/verify_geometry_fixes.py`

**Key Interactions:**
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Calculate all properties from any given property.*
**Exposes:** `get_drawing_instructions()` - *Get drawing instructions for the square.*
**Exposes:** `get_label_positions()` - *Get label positions for the square.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Calculate dependent properties.*
**Exposes:** `get_drawing_instructions()` - *Get drawing instructions for the rectangle.*
**Exposes:** `get_label_positions()` - *Get label positions for the rectangle.*


---

**File:** `src/pillars/geometry/services/step_pyramid_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Terraced step pyramid solid service and calculator.

**Input (Ingests):**
* `base_edge` (Field)
* `top_edge` (Field)
* `height` (Field)
* `tiers` (Field)
* `step_height` (Field)
* `base_area` (Field)
* `top_area` (Field)
* `lateral_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `tier_edges` (Field)
* `payload` (Field)
* `metrics` (Field)
* `base_edge`
* `top_edge`
* `height`
* `tiers`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `shared.solid_payload.Face`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.cast`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/tesseract_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Tesseract (hypercube) solid service and calculator.

**Input (Ingests):**
* `edge_length` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `face_count` (Field)
* `edge_count` (Field)
* `vertex_count` (Field)
* `face_sides` (Field)
* `payload` (Field)
* `metrics` (Field)
* `edge_length`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.Face`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `shared.solid_payload.Vec3`
* `solid_geometry.compute_surface_area`
* `solid_geometry.compute_volume`
* `solid_geometry.edges_from_faces`
* `solid_geometry.vec_length`
* `solid_geometry.vec_sub`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`
* `typing.Type`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/tetrahedron_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Equilateral tetrahedron solid math + payload builder.

**Input (Ingests):**
* `edge_length` (Field)
* `height` (Field)
* `face_area` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `inradius` (Field)
* `midradius` (Field)
* `circumradius` (Field)
* `incircle_circumference` (Field)
* `midsphere_circumference` (Field)
* `circumcircle_circumference` (Field)
* `faces` (Field)
* `edges` (Field)
* `vertices` (Field)
* `face_sides` (Field)
* `vertex_valence` (Field)
* `dihedral_angle_deg` (Field)
* `solid_angle_sr` (Field)
* `face_inradius` (Field)
* `face_circumradius` (Field)
* `insphere_surface_area` (Field)
* `insphere_volume` (Field)
* `midsphere_surface_area` (Field)
* `midsphere_volume` (Field)
* `circumsphere_surface_area` (Field)
* `circumsphere_volume` (Field)
* `sphericity` (Field)
* `isoperimetric_quotient` (Field)
* `surface_to_volume_ratio` (Field)
* `moment_inertia_solid` (Field)
* `moment_inertia_shell` (Field)
* `angular_defect_vertex_deg` (Field)
* `total_angular_defect_deg` (Field)
* `euler_characteristic` (Field)
* `packing_density` (Field)
* `symmetry_group_order` (Field)
* `rotational_symmetry_order` (Field)
* `symmetry_group_name` (Field)
* `dual_solid_name` (Field)
* `golden_ratio_factor` (Field)
* `payload` (Field)
* `metrics` (Field)
* `edge_length`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `geometry_visuals.compute_dual_payload`
* `math`
* `platonic_constants.ANGULAR_DEFECT_VERTEX_DEG`
* `platonic_constants.DIHEDRAL_ANGLES_DEG`
* `platonic_constants.DUAL_SOLID_NAME`
* `platonic_constants.GOLDEN_RATIO_FACTOR`
* `platonic_constants.MOMENT_INERTIA_SHELL_K`
* `platonic_constants.MOMENT_INERTIA_SOLID_K`
* `platonic_constants.PACKING_DENSITY`
* `platonic_constants.PlatonicSolid`
* `platonic_constants.ROTATIONAL_SYMMETRY_ORDER`
* `pl

**Consumers (Who Needs It):**
* `src/pillars/tq/services/platonic_transition_service.py`
* `tests/rituals/rite_of_advanced_visualization.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `payload()` - *Convenience accessor when only the payload is required.*
**Exposes:** `properties()` - *Return all properties in display order.*
**Exposes:** `set_property()` - *Set a property and recalculate all others.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*
**Exposes:** `solver()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/torus_knot_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Torus Knot solid math utilities and calculator.

**Input (Ingests):**
* `p` (Field)
* `q` (Field)
* `major_radius` (Field)
* `minor_radius` (Field)
* `tube_radius` (Field)
* `arc_length` (Field)
* `approx_surface_area` (Field)
* `approx_volume` (Field)
* `payload` (Field)
* `metrics` (Field)
* `tubular_segments` (Field)
* `radial_segments` (Field)
* `p`
* `q`
* `major_radius`
* `minor_radius`
* `tube_radius`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_geometry.Vec3`
* `solid_geometry.edges_from_faces`
* `solid_geometry.vec_add`
* `solid_geometry.vec_cross`
* `solid_geometry.vec_length`
* `solid_geometry.vec_normalize`
* `solid_geometry.vec_scale`
* `solid_geometry.vec_sub`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `scripts/verify_torus_knot.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/torus_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Torus solid math utilities and calculator.

**Input (Ingests):**
* `major_radius` (Field)
* `minor_radius` (Field)
* `ratio` (Field)
* `surface_area` (Field)
* `volume` (Field)
* `major_circumference` (Field)
* `minor_circumference` (Field)
* `payload` (Field)
* `metrics` (Field)
* `major_segments` (Field)
* `minor_segments` (Field)
* `major_radius`
* `minor_radius`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_geometry.Vec3`
* `solid_geometry.edges_from_faces`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `scripts/verify_torus.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*
**Exposes:** `metrics()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/triangle_shape.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Triangle shape calculators.

**Input (Ingests):**
* `side_a` (Field)
* `side_b` (Field)
* `side_c` (Field)
* `area` (Field)
* `perimeter` (Field)
* `angle_a` (Field)
* `angle_b` (Field)
* `angle_c` (Field)
* `height_a` (Field)
* `height_b` (Field)
* `height_c` (Field)
* `inradius` (Field)
* `circumradius` (Field)
* `points` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_shape.GeometricShape`
* `base_shape.ShapeProperty`
* `dataclasses.dataclass`
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `tests/verify_geometry_fixes.py`

**Key Interactions:**
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Calculate all properties from any given property.*
**Exposes:** `get_drawing_instructions()` - *Get drawing instructions for the equilateral triangle.*
**Exposes:** `get_label_positions()` - *Get label positions for the triangle.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Calculate dependent properties.*
**Exposes:** `get_drawing_instructions()` - *Get drawing instructions for the right triangle.*
**Exposes:** `get_label_positions()` - *Get label positions for the triangle.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/vault_of_hestia_shape.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Vault of Hestia sacred geometry service.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_shape.GeometricShape`
* `base_shape.ShapeProperty`
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `scripts/verify_hestia_bidirectional.py`
* `scripts/verify_hestia_expanded.py`

**Key Interactions:**
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/vault_of_hestia_solid.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Vault of Hestia 3D Solid Service.

**Input (Ingests):**
* `side_length` (Field)
* `sphere_radius` (Field)
* `hestia_ratio_3d` (Field)
* `cube_volume` (Field)
* `cube_surface_area` (Field)
* `pyramid_volume` (Field)
* `sphere_volume` (Field)
* `sphere_surface_area` (Field)
* `phi` (Field)
* `cube_diagonal` (Field)
* `pyramid_slant_height` (Field)
* `void_volume_cube_sphere` (Field)
* `void_volume_cube_pyramid` (Field)
* `void_volume_pyramid_sphere` (Field)
* `ratio_sphere_pyramid` (Field)
* `ratio_pyramid_cube` (Field)
* `pyramid_total_surface_area` (Field)
* `inradius_resonance_phi` (Field)
* `volume_efficiency` (Field)
* `payload` (Field)
* `metrics` (Field)
* `side_length`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `solid_geometry.Vec3`
* `solid_geometry.edges_from_faces`
* `solid_property.SolidProperty`
* `typing.Dict`
* `typing.List`
* `typing.Optional`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `tests/rituals/rite_of_hestia_3d.py`

**Key Interactions:**
**Exposes:** `build()` - *Functional interface.*
**Exposes:** `properties()` - *Functional interface.*
**Exposes:** `set_property()` - *Functional interface.*
**Exposes:** `clear()` - *Functional interface.*
**Exposes:** `payload()` - *Functional interface.*
**Exposes:** `metadata()` - *Functional interface.*


---

**File:** `src/pillars/geometry/services/vesica_piscis_shape.py`

**Role:** `[Muscle] (Service)`

**Purpose:** Vesica Piscis shape calculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base_shape.GeometricShape`
* `base_shape.ShapeProperty`
* `math`
* `typing.Dict`
* `typing.List`
* `typing.Sequence`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `description()` - *Functional interface.*
**Exposes:** `calculation_hint()` - *Functional interface.*
**Exposes:** `calculate_from_property()` - *Functional interface.*
**Exposes:** `get_drawing_instructions()` - *Functional interface.*
**Exposes:** `get_label_positions()` - *Functional interface.*


---

**File:** `src/pillars/geometry/shared/solid_payload.py`

**Role:** `[Scout]`

**Purpose:** Shared 3D solid payload structures.

**Input (Ingests):**
* `text` (Field)
* `position` (Field)
* `align_center` (Field)
* `vertices` (Field)
* `edges` (Field)
* `faces` (Field)
* `labels` (Field)
* `metadata` (Field)
* `face_colors` (Field)
* `suggested_scale` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `dataclasses.field`
* `typing.List`
* `typing.Optional`
* `typing.Sequence`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `src/pillars/tq/services/platonic_transition_service.py`

**Key Interactions:**
**Exposes:** `bounds()` - *Functional interface.*


---

**File:** `src/pillars/geometry/ui/advanced_scientific_calculator_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Advanced scientific calculator window for quick math operations.

**Input (Ingests):**
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QGuiApplication`
* `PyQt6.QtGui.QStandardItem`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTabWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `__future__.annotations`
* `ast`
* `math`


**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `is_value()` - *Functional interface.*
**Exposes:** `is_value_start()` - *Functional interface.*
**Exposes:** `pop_atom()` - *Functional interface.*
**Exposes:** `fail()` - *Functional interface.*
**Exposes:** `eval_node()` - *Functional interface.*
**Exposes:** `populate()` - *Functional interface.*
**Exposes:** `populate()` - *Functional interface.*
**Exposes:** `sin_wrapped()` - *Functional interface.*
**Exposes:** `cos_wrapped()` - *Functional interface.*
**Exposes:** `tan_wrapped()` - *Functional interface.*


---

**File:** `src/pillars/geometry/ui/base_figurate_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Base class for interactivity and layout of figurate number windows.

**Input (Ingests):**
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QObject`
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QRunnable`
* `PyQt6.QtCore.QThreadPool`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsView`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `__future__.annotations`
* `geometry_interaction.Connect

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `finished` - *Nervous System Signal.*


---

**File:** `src/pillars/geometry/ui/calculator/calculator_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `shape`
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QSignalBlocker`
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QWidget`
* `liturgy_styles.LiturgyColors`
* `panes.controls_pane.ControlsPane`
* `panes.input_pane.InputPane`
* `panes.viewport_pane.ViewportPane`
* `services.base_shape.GeometricShape`
* `shared.ui.WindowManager`
* `tq.ui.quadset_analysis_window.QuadsetAnalysisWindow`
* `typin

**Consumers (Who Needs It):**
* `tests/rituals/verify_modular_calculator.py`

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/geometry/ui/calculator/panes/controls_pane.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `view_model`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QColorDialog`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QTabWidget`
* `PyQt6.QtWidgets.QVBoxLay

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `snapshot_requested` - *Nervous System Signal.*
**Emits:** `copy_measurements_requested` - *Nervous System Signal.*
**Emits:** `interactive_measure_toggled` - *Nervous System Signal.*
**Emits:** `theme_changed` - *Nervous System Signal.*
**Emits:** `measurement_line_color_changed` - *Nervous System Signal.*
**Emits:** `measurement_text_color_changed` - *Nervous System Signal.*
**Exposes:** `update_measurement_labels()` - *Update the stats labels from scene measurement data.*


---

**File:** `src/pillars/geometry/ui/calculator/panes/input_pane.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `view_model`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `liturgy_styles.LiturgyButtons`
* `liturgy_styles.LiturgyColors`
* `liturgy_styles.LiturgyPanels`
* `liturgy_styles.LiturgyScrollArea`
* `view_model.GeometryViewModel`
* `widgets.property_card.PropertyCard`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `quadset_analysis_requested` - *Nervous System Signal.*


---

**File:** `src/pillars/geometry/ui/calculator/panes/viewport_pane.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `view_model`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `geometry_scene.GeometryScene`
* `geometry_view.GeometryView`
* `liturgy_styles.LiturgyColors`
* `liturgy_styles.LiturgyPanels`
* `liturgy_styles.LiturgyToolbar`
* `scene_adapter.build_scene_payload`
* `view_model.GeometryViewModel`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `toggle_input_requested` - *Nervous System Signal.*
**Emits:** `toggle_controls_requested` - *Nervous System Signal.*


---

**File:** `src/pillars/geometry/ui/calculator/view_model.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `shape`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QObject`
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtCore.pyqtSignal`
* `services.base_shape.GeometricShape`
* `services.base_shape.ShapeProperty`
* `services.persistence_service.PersistenceService`
* `typing.Dict`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `property_changed` - *Nervous System Signal.*
**Emits:** `calculation_completed` - *Nervous System Signal.*
**Emits:** `shape_cleared` - *Nervous System Signal.*
**Emits:** `validation_error` - *Nervous System Signal.*
**Emits:** `history_updated` - *Nervous System Signal.*
**Exposes:** `save_state()` - *Manually trigger save (or auto-save hook).*
**Exposes:** `load_state()` - *Load state from history entry data.*
**Exposes:** `shape_name()` - *Functional interface.*
**Exposes:** `shape_description()` - *Functional interface.*
**Exposes:** `get_properties()` - *Functional interface.*
**Exposes:** `get_shape()` - *Access underlying shape for rendering (Scene needs direct access usually).*
**Exposes:** `set_property()` - *Attempt to set a property and trigger calculation.*
**Exposes:** `clear_property()` - *Clear a single property value.*
**Exposes:** `clear_all()` - *Reset the shape.*


---

**File:** `src/pillars/geometry/ui/calculator/widgets/property_card.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `property_data`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QDoubleValidator`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QVBoxLayout`
* `liturgy_styles.LiturgyColors`
* `liturgy_styles.LiturgyInputs`
* `liturgy_styles.LiturgyMenus`
* `services.base_shape.ShapeProperty`
* `typing.Callable`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `value_changed` - *Nervous System Signal.*
**Emits:** `input_cleared` - *Nervous System Signal.*
**Emits:** `quadset_analysis_requested` - *Nervous System Signal.*
**Exposes:** `update_state()` - *Update the card's visual state based on value.*


---

**File:** `src/pillars/geometry/ui/esoteric_definitions.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** The Esoteric Scrolls (The Akaschic Records of Geometry).

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* None.

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/geometry/ui/esoteric_wisdom_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** The Esoteric Wisdom Window (The Temple of Sacred Forms).

**Input (Ingests):**
* `window_manager`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QTreeWidgetItem`
* `PyQt6.QtWidgets.QTreeWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `services.esoteric_wi

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/geometry/ui/experimental_star_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Visualizer for Generalized (Experimental) Star Numbers.

**Input (Ingests):**
* `window_manager`
* `parent`
* `points_count`
* `index`
* `spacing`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QRunnable`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QDoubleSpinBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSpinBox`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `__future__.annotations`
* `base_figurate_window.BaseFigurateWindow`
* `base_figurate_window.RenderSignals`
* `primitives.Bounds`
* `primitives.BrushStyle`
* `primitives.CirclePrimitive`
* `primitives.GeometrySc

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `run()` - *Functional interface.*


---

**File:** `src/pillars/geometry/ui/figurate_3d_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** 3D Figurate Numbers Visualization Window.

**Input (Ingests):**
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDoubleSpinBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsView`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QSpinBox`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `__future__.annotations`
* `base_figurate_window.BaseFigurateWindow`
* `geometry_scene.GeometryScenePayload`
* `primitives.Bounds`
* `primitives.BrushStyle`
* `primitives.CirclePrimitive`
* `primitives.Labe

**Consumers (Who Needs It):**
* `src/pillars/tq/ui/quadset_analysis_window.py`

**Key Interactions:**
**Exposes:** `eventFilter()` - *Functional interface.*


---

**File:** `src/pillars/geometry/ui/geometry3d/solid_payload.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Backward-compatible shim re-exporting shared solid payload types.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `shared.solid_payload.Edge`
* `shared.solid_payload.Face`
* `shared.solid_payload.SolidLabel`
* `shared.solid_payload.SolidPayload`
* `shared.solid_payload.Vec3`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/geometry/ui/geometry3d/view3d.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Orthographic wireframe 3D widget for geometry solids.

**Input (Ingests):**
* `distance` (Field)
* `yaw_deg` (Field)
* `pitch_deg` (Field)
* `pan_x` (Field)
* `pan_y` (Field)
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QPoint`
* `PyQt6.QtCore.QRectF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QMatrix4x4`
* `PyQt6.QtGui.QMouseEvent`
* `PyQt6.QtGui.QPaintEvent`
* `PyQt6.QtGui.QPainterPath`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QVector3D`
* `PyQt6.QtGui.QWheelEvent`
* `PyQt6.QtWidgets.QWidget`
* `__future__.annotations`
* `dataclasses.dataclass`
* `math`
* `servic

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `rotation_matrix()` - *Functional interface.*
**Exposes:** `set_payload()` - *Functional interface.*
**Exposes:** `reset_view()` - *Functional interface.*
**Exposes:** `set_camera_angles()` - *Functional interface.*
**Exposes:** `set_axes_visible()` - *Functional interface.*
**Exposes:** `axes_visible()` - *Functional interface.*
**Exposes:** `set_labels_visible()` - *Functional interface.*
**Exposes:** `labels_visible()` - *Functional interface.*
**Exposes:** `set_vertices_visible()` - *Functional interface.*
**Exposes:** `vertices_visible()` - *Functional interface.*
**Exposes:** `set_dual_visible()` - *Functional interface.*
**Exposes:** `dual_visible()` - *Functional interface.*
**Exposes:** `set_measure_mode()` - *Functional interface.*
**Exposes:** `measure_mode()` - *Functional interface.*
**Exposes:** `clear_measurement()` - *Functional interface.*
**Exposes:** `selected_vertices()` - *Functional interface.*
**Emits:** `measurement_complete` - *Nervous System Signal.*
**Exposes:** `set_sphere_visible()` - *Functional interface.*
**Exposes:** `sphere_visible()` - *Functional interface.*
**Exposes:** `zoom_in()` - *Functional interface.*
**Exposes:** `zoom_out()` - *Functional interface.*
**Exposes:** `fit_scene()` - *Functional interface.*
**Exposes:** `paintEvent()` - *Functional interface.*
**Exposes:** `wheelEvent()` - *Functional interface.*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Exposes:** `mouseMoveEvent()` - *Functional interface.*
**Exposes:** `mouseReleaseEvent()` - *Functional interface.*
**Exposes:** `get_pt_3d()` - *Functional interface.*
**Exposes:** `get_pt_screen()` - *Functional interface.*


---

**File:** `src/pillars/geometry/ui/geometry3d/window3d.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Standalone window hosting the 3D geometry view.

**Input (Ingests):**
* `window_manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QDoubleValidator`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QMainWindow`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QSplitter`
* `PyQt6.QtWidgets.QTabWidget`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
*

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `set_payload()` - *Functional interface.*
**Exposes:** `set_solid_context()` - *Functional interface.*
**Exposes:** `set_calculator()` - *Functional interface.*


---

**File:** `src/pillars/geometry/ui/geometry_definitions.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `esoteric_definitions.ESOTERIC_DEFINITIONS`
* `services.AcuteTriangleShape`
* `services.AnnulusShape`
* `services.BicentricQuadrilateralShape`
* `services.CircleShape`
* `services.ConeSolidCalculator`
* `services.ConeSolidService`
* `services.CrescentShape`
* `services.CubeSolidCalculator`
* `services.CubeSolidService`
* `services.CuboctahedronSolidCalculator`
* `services.CuboctahedronSolidService`
* `services.CyclicQuadrilateralShape`
* `services.CylinderSolidCalculator`
* `services.CylinderS

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/geometry/ui/geometry_hub.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Geometry pillar hub - launcher interface for geometry tools.

**Input (Ingests):**
* `window_manager`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPixmap`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `__future__.annotations`
* `advanced_scientific_calculator_window.AdvancedScientificCalculatorW

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
* Internal logic only.


---

**File:** `src/pillars/geometry/ui/geometry_interaction.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Interaction manager and UI components for geometry windows.

**Input (Ingests):**
* `start_index` (Field)
* `end_index` (Field)
* `color` (Field)
* `width` (Field)
* `name` (Field)
* `indices` (Field)
* `total_value` (Field)
* `color` (Field)
* `parent`
* `manager`
* `parent`
* `manager`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QObject`
* `PyQt6.QtCore.QPoint`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QIcon`
* `PyQt6.QtWidgets.QColorDialog`
* `PyQt6.QtWidgets.QDoubleSpinBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QInputDialog`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QListWidgetItem`
* `PyQt6.QtWidgets.QListWidget`
* `PyQt6.QtWidgets.QMenu`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QT

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `groups_changed` - *Nervous System Signal.*
**Emits:** `connection_added` - *Nervous System Signal.*
**Emits:** `connections_cleared` - *Nervous System Signal.*
**Emits:** `mode_changed` - *Nervous System Signal.*
**Emits:** `draw_start_changed` - *Nervous System Signal.*
**Exposes:** `create_group()` - *Create a new group. Returns the actual name used (handles duplicates).*
**Exposes:** `delete_group()` - *Functional interface.*
**Exposes:** `add_dot_to_group()` - *Functional interface.*
**Exposes:** `remove_dot_from_group()` - *Functional interface.*
**Exposes:** `toggle_dot_in_group()` - *Toggle dot membership in the ACTIVE group.*
**Exposes:** `add_connection()` - *Functional interface.*
**Exposes:** `process_draw_click()` - *Handle a click in draw mode: Polyline logic.*
**Exposes:** `cancel_drawing_chain()` - *Reset the current drawing chain (e.g. stop preview).*
**Exposes:** `clear()` - *Functional interface.*
**Emits:** `dot_color_changed` - *Nervous System Signal.*
**Emits:** `text_color_changed` - *Nervous System Signal.*


---

**File:** `src/pillars/geometry/ui/geometry_scene.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Central QGraphicsScene implementation for the geometry pillar.

**Input (Ingests):**
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QRectF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QBrush`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtGui.QPainterPath`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QPen`
* `PyQt6.QtGui.QPolygonF`
* `PyQt6.QtGui.QRadialGradient`
* `PyQt6.QtGui.QTransform`
* `PyQt6.QtWidgets.QGraphicsEllipseItem`
* `PyQt6.QtWidgets.QGraphicsItem`
* `PyQt6.QtWidgets.QGraphicsSceneMouseEvent`
* `PyQt6.QtWidgets.QGraphicsScene`
* `PyQt6.QtWidgets.QGraphicsSimpleTextItem

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `measurementChanged` - *Nervous System Signal.*
**Emits:** `dot_clicked` - *Nervous System Signal.*
**Emits:** `mouse_moved` - *Nervous System Signal.*
**Emits:** `dot_hovered` - *Nervous System Signal.*
**Emits:** `dot_hover_leave` - *Nervous System Signal.*
**Emits:** `canvas_clicked` - *Nervous System Signal.*
**Exposes:** `set_payload()` - *Replace the scene content with the provided payload.*
**Exposes:** `clear_payload()` - *Functional interface.*
**Exposes:** `set_axes_visible()` - *Functional interface.*
**Exposes:** `set_labels_visible()` - *Functional interface.*
**Exposes:** `set_vertex_highlights_visible()` - *Toggle visibility of vertex highlight dots.*
**Exposes:** `apply_theme()` - *Functional interface.*
**Exposes:** `get_current_bounds()` - *Functional interface.*
**Exposes:** `get_vertices()` - *Get all significant vertices from the current payload.*
**Exposes:** `add_temporary_line()` - *Legacy helper, redirected to new system or kept for simple 2-point compatibility.*
**Exposes:** `update_measurement_preview()` - *Update the scene with the current multi-point measurement state.*
**Exposes:** `set_measurement_font_size()` - *Functional interface.*
**Exposes:** `set_measurement_line_color()` - *Functional interface.*
**Exposes:** `set_measurement_text_color()` - *Functional interface.*
**Exposes:** `set_measurement_show_area()` - *Functional interface.*
**Exposes:** `clear_temporary_items()` - *Remove all temporary items from the scene.*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Exposes:** `set_start_dot_highlight()` - *Highlight the active drawing start dot (Drawing Anchor).*
**Exposes:** `mouseMoveEvent()` - *Functional interface.*
**Exposes:** `set_preview_line()` - *Update or create a temporary preview line for drawing.*
**Exposes:** `add_connection_line()` - *Add a persistent connection line to the scene.*
**Exposes:** `set_dot_z_index()` - *Functional interface.*
**Exposes:** `highlight_dots()` - *Highlight specific dots by index.*
**Exposes:** `set_hover_target()` - *Highlight a specific dot as a hover target (e.g. for snapping).*
**Exposes:** `set_dot_color()` - *Set the fill color for all dot items (EllipseItems).*
**Exposes:** `set_text_color()` - *Set the color for all text labels.*
**Exposes:** `get_dots_in_rect()` - *Return list of dot indices whose centers fall within the given rectangle.*
**Exposes:** `drawBackground()` - *Functional interface.*
**Exposes:** `update_label_layout()` - *Dynamically adjust label visibility and size based on zoom level.*


---

**File:** `src/pillars/geometry/ui/geometry_view.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `scene`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPoint`
* `PyQt6.QtCore.QRectF`
* `PyQt6.QtCore.QRect`
* `PyQt6.QtCore.QSize`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QMouseEvent`
* `PyQt6.QtGui.QPainter`
* `PyQt6.QtGui.QWheelEvent`
* `PyQt6.QtWidgets.QGraphicsView`
* `PyQt6.QtWidgets.QRubberBand`
* `__future__.annotations`
* `geometry_scene.GeometryScene`
* `math`
* `primitives.Bounds`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `dots_selected` - *Nervous System Signal.*
**Exposes:** `resizeEvent()` - *Functional interface.*
**Exposes:** `wheelEvent()` - *Functional interface.*
**Exposes:** `zoom_in()` - *Functional interface.*
**Exposes:** `zoom_out()` - *Functional interface.*
**Exposes:** `zoom()` - *Functional interface.*
**Exposes:** `reset_view()` - *Functional interface.*
**Exposes:** `fit_scene()` - *Functional interface.*
**Exposes:** `fit_to_bounds()` - *Functional interface.*
**Exposes:** `set_measurement_mode()` - *Enable or disable measurement mode.*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Exposes:** `mouseMoveEvent()` - *Functional interface.*
**Exposes:** `mouseReleaseEvent()` - *Functional interface.*
**Exposes:** `set_selection_mode()` - *Enable or disable rubber-band selection mode.*


---

**File:** `src/pillars/geometry/ui/liturgy_styles.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** The Liturgical Styles (Visual Liturgy Implementation).

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* None.

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `magus()` - *The Magus - Transmute/Execute actions (Mystic Violet).*
**Exposes:** `seeker()` - *The Seeker - Uncover/Reveal actions (Alchemical Gold).*
**Exposes:** `scribe()` - *The Scribe - Preserve/Etch actions (Emerald).*
**Exposes:** `destroyer()` - *The Destroyer - Purge/Banish actions (Crimson).*
**Exposes:** `navigator()` - *The Navigator - Traverse actions (Void Slate).*
**Exposes:** `secondary()` - *Secondary button style for less prominent actions.*
**Exposes:** `tablet()` - *The Tablet - Marble panel with liturgical shadow.*
**Exposes:** `calculation_pane()` - *Left calculation pane styling.*
**Exposes:** `viewport_container()` - *Viewport container with marble background.*
**Exposes:** `controls_pane()` - *Right controls pane styling.*
**Exposes:** `info_card()` - *Blue info/help card styling.*
**Exposes:** `vessel()` - *The Vessel - Standard input field.*
**Exposes:** `vessel_readonly()` - *Read-only input field.*
**Exposes:** `property_card_editable()` - *Editable property card (amber accent).*
**Exposes:** `property_card_readonly()` - *Read-only property card (slate accent).*
**Exposes:** `property_card_solved()` - *Solved property card (green accent).*
**Exposes:** `bar()` - *Layout toolbar background.*
**Exposes:** `toggle_button()` - *Toggle button for layout controls.*
**Exposes:** `standard()` - *Standard tab widget styling.*
**Exposes:** `standard()` - *Standard scroll area with styled scrollbar.*
**Exposes:** `standard()` - *Standard context menu styling.*


---

**File:** `src/pillars/geometry/ui/polygonal_number_window.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Visualizer for polygonal and centered polygonal numbers.

**Input (Ingests):**
* `window_manager`
* `parent`
* `sides`
* `index`
* `spacing`
* `mode`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QRunnable`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QCheckBox`
* `PyQt6.QtWidgets.QComboBox`
* `PyQt6.QtWidgets.QDoubleSpinBox`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QSpinBox`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `__future__.annotations`
* `base_figurate_window.BaseFigurateWindow`
* `base_figurate_window.RenderSignals`
* `math`
* `primitives.Bounds`
* `primitives.BrushStyle`
* `primitives.Ci

**Consumers (Who Needs It):**
* `src/pillars/tq/ui/quadset_analysis_window.py`

**Key Interactions:**
**Exposes:** `run()` - *Functional interface.*


---

**File:** `src/pillars/geometry/ui/primitives.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Data primitives for the geometry visualization scene.

**Input (Ingests):**
* `color` (Field)
* `width` (Field)
* `dashed` (Field)
* `color` (Field)
* `enabled` (Field)
* `min_x` (Field)
* `max_x` (Field)
* `min_y` (Field)
* `max_y` (Field)
* `center` (Field)
* `radius` (Field)
* `pen` (Field)
* `brush` (Field)
* `metadata` (Field)
* `points` (Field)
* `pen` (Field)
* `brush` (Field)
* `closed` (Field)
* `start` (Field)
* `end` (Field)
* `pen` (Field)
* `text` (Field)
* `position` (Field)
* `align_center` (Field)
* `metadata` (Field)
* `operation` (Field)
* `shape_a` (Field)
* `shape_b` (Field)
* `pen` (Field)
* `brush` (Field)
* `primitives` (Field)
* `labels` (Field)
* `bounds` (Field)
* `suggest_grid_span` (Field)

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `dataclasses.dataclass`
* `dataclasses.field`
* `typing.List`
* `typing.Optional`
* `typing.Sequence`
* `typing.Tuple`
* `typing.Union`

**Consumers (Who Needs It):**
* `scripts/verify_polyline.py`

**Key Interactions:**
**Exposes:** `width()` - *Functional interface.*
**Exposes:** `height()` - *Functional interface.*
**Exposes:** `padded()` - *Functional interface.*


---

**File:** `src/pillars/geometry/ui/scene_adapter.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Adapter to convert legacy drawing dictionaries into scene primitives.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `math`
* `primitives.BooleanPrimitive`
* `primitives.Bounds`
* `primitives.BrushStyle`
* `primitives.CirclePrimitive`
* `primitives.GeometryScenePayload`
* `primitives.LabelPrimitive`
* `primitives.LinePrimitive`
* `primitives.PenStyle`
* `primitives.PolygonPrimitive`
* `typing.Dict`
* `typing.List`
* `typing.Sequence`
* `typing.Tuple`

**Consumers (Who Needs It):**
* `scripts/verify_polyline.py`

**Key Interactions:**
**Exposes:** `build_scene_payload()` - *Translate the legacy viewport dictionaries into structured primitives.*


---

**File:** `src/pillars/geometry/ui/shape_picker_dialog.py`

**Role:** `[Skin] (UI/View)`

**Purpose:** Shape Picker Dialog - Visual Liturgy styled shape selection.

**Input (Ingests):**
* `shape_def`
* `accent_color`
* `parent`
* `category`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtCore.pyqtSignal`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtWidgets.QDialog`
* `PyQt6.QtWidgets.QFrame`
* `PyQt6.QtWidgets.QGraphicsDropShadowEffect`
* `PyQt6.QtWidgets.QGridLayout`
* `PyQt6.QtWidgets.QHBoxLayout`
* `PyQt6.QtWidgets.QLabel`
* `PyQt6.QtWidgets.QLineEdit`
* `PyQt6.QtWidgets.QPushButton`
* `PyQt6.QtWidgets.QScrollArea`
* `PyQt6.QtWidgets.QVBoxLayout`
* `PyQt6.QtWidgets.QWidget`
* `__future__.annotations`
* `liturgy_styles.LiturgyButtons`
* `liturgy_styles.Litu

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Emits:** `clicked` - *Nervous System Signal.*
**Exposes:** `mousePressEvent()` - *Functional interface.*
**Emits:** `shape_selected` - *Nervous System Signal.*
**Exposes:** `get_selected_shape()` - *Return the selected shape definition.*
