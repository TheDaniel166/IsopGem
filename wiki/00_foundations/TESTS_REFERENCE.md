---

**File:** `tests/_legacy/test_db_persistence.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Not yet audited.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `pillars.document_manager.models.mindscape.MindNode`
* `pillars.document_manager.services.mindscape_service.MindscapeService`
* `pytest`
* `shared.database.get_db_session`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_search_node_is_in_db()` - *Functional interface.*








---

**File:** `tests/_legacy/test_db_persistence.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `pillars.document_manager.models.mindscape.MindNode`
* `pillars.document_manager.services.mindscape_service.MindscapeService`
* `pytest`
* `shared.database.get_db_session`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_search_node_is_in_db()` - *Functional interface.*


---

**File:** `tests/_legacy/test_graph_persistence.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `json`
* `pillars.document_manager.models.mindscape.MindNode`
* `pillars.document_manager.services.mindscape_service.MindscapeService`
* `pytest`
* `shared.database.get_db_session`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_node_position_persistence()` - *Functional interface.*


---

**File:** `tests/_legacy/test_node_tooltips.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QApplication`
* `pillars.document_manager.ui.mindscape_items.MindscapeNodeItem`
* `pytest`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_node_tooltip()` - *Functional interface.*
**Exposes:** `test_node_tooltip_empty()` - *Functional interface.*


---

**File:** `tests/_legacy/test_search_isolation.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `json`
* `pillars.document_manager.services.mindscape_service.MindscapeService`
* `pytest`
* `shared.database.get_db_session`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_search_node_structure_only()` - *Functional interface.*


---

**File:** `tests/_legacy/test_search_logic.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `json`
* `pillars.document_manager.models.mindscape.MindEdgeType`
* `pillars.document_manager.services.mindscape_service.MindscapeService`
* `pytest`
* `shared.database.get_db_session`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_duplicate_prevention_and_linking()` - *Functional interface.*


---

**File:** `tests/_legacy/test_search_panel.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QApplication`
* `json`
* `pillars.document_manager.services.mindscape_service.MindscapeService`
* `pillars.document_manager.ui.search_results_panel.SearchResultsPanel`
* `pytest`
* `shared.database.get_db_session`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_search_node_metadata()` - *Functional interface.*
**Exposes:** `test_search_panel_population()` - *Functional interface.*
**Exposes:** `test_search_panel_empty()` - *Functional interface.*


---

**File:** `tests/_legacy/test_view_interaction.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.QPoint`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QMouseEvent`
* `PyQt6.QtWidgets.QApplication`
* `pillars.document_manager.ui.mindscape_items.MindscapeNodeItem`
* `pillars.document_manager.ui.mindscape_view.MindscapeView`
* `pytest`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_view_click_propagation()` - *Verify that clicking a node in the view emits node_selected.*


---

**File:** `tests/_legacy/test_wipe.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `pillars.document_manager.models.mindscape.MindEdge`
* `pillars.document_manager.models.mindscape.MindNode`
* `pillars.document_manager.services.mindscape_service.MindscapeService`
* `pytest`
* `shared.database.get_db_session`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_wipe_database()` - *Functional interface.*


---

**File:** `tests/astrology/test_astrology_service.py`

**Role:** `[Scout]`

**Purpose:** Integration coverage for the Astrology pillar's OpenAstro2 wiring.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `datetime.datetime`
* `datetime.timezone`
* `pytest`
* `src.pillars.astrology.models.AstrologyEvent`
* `src.pillars.astrology.models.ChartRequest`
* `src.pillars.astrology.models.GeoLocation`
* `src.pillars.astrology.services.OpenAstroNotAvailableError`
* `src.pillars.astrology.services.OpenAstroService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_openastro_service_generates_chart_payload()` - *Ensure OpenAstro2 can compute a basic natal chart via the service wrapper.*
**Exposes:** `test_default_settings_returns_independent_copy()` - *Functional interface.*


---

**File:** `tests/astrology/test_chart_storage_service.py`

**Role:** `[Scout]`

**Purpose:** Tests for the astrology chart storage service.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `contextlib.contextmanager`
* `datetime.datetime`
* `datetime.timezone`
* `shared.database.Base`
* `sqlalchemy.create_engine`
* `sqlalchemy.orm.sessionmaker`
* `src.pillars.astrology.models.AstrologyEvent`
* `src.pillars.astrology.models.ChartRequest`
* `src.pillars.astrology.models.ChartResult`
* `src.pillars.astrology.models.GeoLocation`
* `src.pillars.astrology.services.chart_storage_service.ChartStorageService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_save_and_load_chart_round_trip()` - *Functional interface.*
**Exposes:** `test_search_filters_by_category()` - *Functional interface.*
**Exposes:** `session_scope()` - *Functional interface.*


---

**File:** `tests/common/test_window_manager.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* `name`
* `parent`

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QWidget`
* `os`
* `pytest`
* `shared.ui.window_manager.WindowManager`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `app()` - *Functional interface.*
**Exposes:** `test_open_and_reuse_single()` - *Functional interface.*
**Exposes:** `test_open_multiple_and_close()` - *Functional interface.*


---

**File:** `tests/conftest.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `pathlib.Path`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `pytest_configure()` - *Ensure `src/` is importable during tests.*


---

**File:** `tests/document/test_document_search.py`

**Role:** `[Scout]`

**Purpose:** Comprehensive unit tests for Document Search functionality.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QApplication`
* `datetime.datetime`
* `os`
* `pathlib.Path`
* `pillars.document_manager.repositories.search_repository.DocumentSearchRepository`
* `pillars.document_manager.ui.rich_text_editor.RichTextEditor`
* `pytest`
* `shutil`
* `tempfile`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `temp_index_dir()` - *Create a temporary directory for the search index.*
**Exposes:** `search_repo()` - *Create a DocumentSearchRepository with a temporary index.*
**Exposes:** `sample_documents()` - *Sample documents for testing.*
**Exposes:** `mock_documents()` - *Convert sample documents to mock Document objects.*
**Exposes:** `test_index_creation()` - *Index directory should be created.*
**Exposes:** `test_schema_fields()` - *Schema should have required fields.*
**Exposes:** `test_empty_index_search()` - *Searching empty index should return empty list.*
**Exposes:** `test_index_single_document()` - *Should index a single document.*
**Exposes:** `test_index_multiple_documents()` - *Should index multiple documents.*
**Exposes:** `test_search_by_title()` - *Should find documents by title.*
**Exposes:** `test_search_by_content()` - *Should find documents by content.*
**Exposes:** `test_search_by_author()` - *Should find documents by author.*
**Exposes:** `test_hit_count_accuracy()` - *Hit count should reflect actual matches in full content.*
**Exposes:** `test_empty_query()` - *Empty query should return empty results.*
**Exposes:** `test_nonexistent_term()` - *Query for nonexistent term should return empty.*
**Exposes:** `test_special_characters()` - *Should handle special characters gracefully.*
**Exposes:** `test_wildcard_search()` - *Wildcard search should work.*
**Exposes:** `test_phrase_search()` - *Phrase search with quotes should work.*
**Exposes:** `test_result_structure()` - *Search results should have consistent structure.*
**Exposes:** `test_id_is_integer()` - *Document ID should be returned as integer.*
**Exposes:** `test_hit_count_is_integer()` - *Hit count should be an integer.*
**Exposes:** `test_many_documents()` - *Should handle indexing many documents.*
**Exposes:** `test_limit_parameter()` - *Limit parameter should restrict result count.*
**Exposes:** `test_document_update_via_reindex()` - *Updated documents should reflect new content via delete + index.*
**Exposes:** `test_document_deletion()` - *Deleted documents should not appear in results.*
**Exposes:** `test_rebuild_index_clears_and_repopulates()` - *Rebuilding index should clear and repopulate with given documents.*
**Exposes:** `qapp()` - *Create QApplication for widget tests.*
**Exposes:** `editor()` - *Create RichTextEditor instance.*
**Exposes:** `test_find_all_matches_count()` - *find_all_matches should count correctly.*
**Exposes:** `test_find_all_matches_positions()` - *Cursor should be at first match after find_all_matches.*
**Exposes:** `test_find_next_increments()` - *find_next should increment match counter.*
**Exposes:** `test_find_next_wraps()` - *find_next should wrap to beginning.*
**Exposes:** `test_find_previous_decrements()` - *find_previous should decrement match counter.*
**Exposes:** `test_find_previous_wraps()` - *find_previous should wrap to end.*
**Exposes:** `test_clear_search_resets_state()` - *clear_search should reset match state.*
**Exposes:** `test_no_matches_returns_zero()` - *find_all_matches should return 0 for no matches.*
**Exposes:** `test_empty_search_term()` - *Empty search term should return 0.*


---

**File:** `tests/document/test_document_service.py`

**Role:** `[Scout]`

**Purpose:** Tests for DocumentService database operations.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `pathlib.Path`
* `pillars.document_manager.services.document_service.DocumentService`
* `pytest`
* `shared.database.get_db_session`
* `shared.database`
* `sqlalchemy.create_engine`
* `sqlalchemy.orm.close_all_sessions`
* `sqlalchemy.orm.sessionmaker`
* `sys`
* `typing.Any`
* `typing.Dict`
* `typing.Generator`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `isolated_database()` - *Provide an isolated SQLite database for each test run.*
**Exposes:** `in_memory_search_repo()` - *Stub out the Whoosh-backed repository with an in-memory store.*
**Exposes:** `test_import_and_fetch_document()` - *Functional interface.*
**Exposes:** `test_search_documents_returns_matching_rows()` - *Functional interface.*
**Exposes:** `test_update_and_delete_document()` - *Functional interface.*
**Exposes:** `test_batch_update_documents()` - *Functional interface.*
**Exposes:** `test_delete_all_documents_clears_index()` - *Functional interface.*
**Exposes:** `test_rebuild_search_index_repopulates_entries()` - *Functional interface.*
**Exposes:** `index_document()` - *Functional interface.*
**Exposes:** `index_documents()` - *Functional interface.*
**Exposes:** `delete_document()` - *Functional interface.*
**Exposes:** `search()` - *Functional interface.*
**Exposes:** `rebuild_index()` - *Functional interface.*
**Exposes:** `clear_index()` - *Functional interface.*


---

**File:** `tests/document/test_graph_physics.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pillars.document_manager.ui.graph_physics.GraphPhysics`
* `pytest`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_physics_initialization()` - *Functional interface.*
**Exposes:** `test_add_remove_node()` - *Functional interface.*
**Exposes:** `test_repulsion()` - *Two nodes should push each other away.*
**Exposes:** `test_spring_attraction()` - *Connected nodes far apart should pull together.*


---

**File:** `tests/document/test_verse_parser.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `pillars.gematria.utils.numeric_utils.sum_numeric_face_values`
* `pillars.gematria.utils.verse_parser.parse_verses`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_parse_simple_numbered_verses()` - *Functional interface.*
**Exposes:** `test_parse_verse_start_positions()` - *Functional interface.*
**Exposes:** `test_inline_numbers_are_parsed()` - *Functional interface.*
**Exposes:** `test_inline_numbers_without_punctuation()` - *Functional interface.*
**Exposes:** `test_numbers_after_punctuation()` - *Functional interface.*
**Exposes:** `test_mid_body_numbers_not_parsed()` - *Functional interface.*
**Exposes:** `test_inline_parsing_accepts_verse_markers()` - *Functional interface.*
**Exposes:** `test_mid_body_numbers_not_parsed_permissive()` - *Functional interface.*
**Exposes:** `test_numeric_face_sum_helper()` - *Functional interface.*
**Exposes:** `test_parser_reports_marker_spans()` - *Functional interface.*


---

**File:** `tests/gematria/test_calculation_service.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `json`
* `pillars.gematria.models.calculation_record.CalculationRecord`
* `pillars.gematria.services.base_calculator.GematriaCalculator`
* `pillars.gematria.services.calculation_service.CalculationService`
* `pytest`
* `typing.Dict`
* `typing.List`
* `typing.Optional`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `repo_and_service()` - *Functional interface.*
**Exposes:** `test_save_calculation_serializes_breakdown()` - *Functional interface.*
**Exposes:** `test_update_calculation_only_changes_provided_fields()` - *Functional interface.*
**Exposes:** `test_toggle_favorite_flips_state()` - *Functional interface.*
**Exposes:** `test_get_breakdown_from_record_handles_malformed_json()` - *Functional interface.*
**Exposes:** `name()` - *Functional interface.*
**Exposes:** `save()` - *Functional interface.*
**Exposes:** `get_by_id()` - *Functional interface.*
**Exposes:** `delete()` - *Functional interface.*
**Exposes:** `search()` - *Functional interface.*
**Exposes:** `get_all()` - *Functional interface.*
**Exposes:** `get_by_value()` - *Functional interface.*
**Exposes:** `get_favorites()` - *Functional interface.*


---

**File:** `tests/gematria/test_sqlite_repository.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `datetime.datetime`
* `pathlib.Path`
* `pillars.gematria.models.calculation_record.CalculationRecord`
* `pillars.gematria.repositories.sqlite_calculation_repository.SQLiteCalculationRepository`
* `pytest`
* `shared.database.Base`
* `sqlalchemy.create_engine`
* `sqlalchemy.orm.sessionmaker`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `sqlite_repo()` - *Functional interface.*
**Exposes:** `build_record()` - *Functional interface.*
**Exposes:** `test_sqlite_repository_save_and_retrieve()` - *Functional interface.*
**Exposes:** `test_sqlite_repository_search_filters()` - *Functional interface.*


---

**File:** `tests/geometry/test_2d_quadrilaterals.py`

**Role:** `[Scout]`

**Purpose:** Unit tests for 2D Quadrilateral shapes.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.quadrilateral_shape.IsoscelesTrapezoidShape`
* `src.pillars.geometry.services.quadrilateral_shape.KiteShape`
* `src.pillars.geometry.services.quadrilateral_shape.ParallelogramShape`
* `src.pillars.geometry.services.quadrilateral_shape.RhombusShape`
* `src.pillars.geometry.services.quadrilateral_shape.TrapezoidShape`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_base_side_angle_calc()` - *Test calculating from base, side, and angle.*
**Exposes:** `test_base_side_height_calc()` - *Test calculating from base, side, and height.*
**Exposes:** `test_invalid_height_greater_than_side()` - *Test that height > side is rejected.*
**Exposes:** `test_side_angle_calc()` - *Test calculating from side and angle.*
**Exposes:** `test_side_diagonals_calc()` - *Test calculating from both diagonals.*
**Exposes:** `test_bases_height_legs_calc()` - *Test calculating from bases, height, and one leg.*
**Exposes:** `test_bases_leg_calc()` - *Test calculating from bases and leg.*
**Exposes:** `test_sides_angle_calc()` - *Test calculating from sides and angle.*


---

**File:** `tests/geometry/test_2d_triangles.py`

**Role:** `[Scout]`

**Purpose:** Unit tests for 2D Triangle shapes.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.triangle_shape.EquilateralTriangleShape`
* `src.pillars.geometry.services.triangle_shape.IsoscelesTriangleShape`
* `src.pillars.geometry.services.triangle_shape.RightTriangleShape`
* `src.pillars.geometry.services.triangle_shape.TriangleSolution`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_base_height_calc()` - *Test calculating from base and height.*
**Exposes:** `test_hypotenuse_base_calc()` - *Test calculating from hypotenuse and base.*
**Exposes:** `test_area_height_calc()` - *Test calculating from area and height.*
**Exposes:** `test_hypotenuse_area_calc()` - *Test calculating from hypotenuse and area (Ambiguous case handling).*
**Exposes:** `test_perimeter_base_calc()` - *Test calculating from perimeter and base.*
**Exposes:** `test_invalid_input()` - *Test that impossible triangles are rejected.*
**Exposes:** `test_side_calc()` - *Functional interface.*
**Exposes:** `test_height_calc()` - *Functional interface.*
**Exposes:** `test_base_height_calc()` - *Functional interface.*
**Exposes:** `test_base_leg_calc()` - *Functional interface.*
**Exposes:** `test_perimeter_base_calc()` - *Functional interface.*
**Exposes:** `test_perimeter_leg_calc()` - *Functional interface.*
**Exposes:** `test_area_base_calc()` - *Functional interface.*
**Exposes:** `test_area_height_calc()` - *Functional interface.*
**Exposes:** `test_area_leg_calc()` - *Functional interface.*


---

**File:** `tests/geometry/test_antiprisms.py`

**Role:** `[Scout]`

**Purpose:** Unit tests for regular antiprism services and calculators.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.HeptagonalAntiprismSolidService`
* `src.pillars.geometry.services.SquareAntiprismSolidCalculator`
* `src.pillars.geometry.services.TriangularAntiprismSolidService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_triangular_antiprism_metrics_and_payload()` - *Functional interface.*
**Exposes:** `test_square_antiprism_calculator_handles_lateral_edge_and_volume()` - *Functional interface.*
**Exposes:** `test_heptagonal_antiprism_payload_counts()` - *Functional interface.*


---

**File:** `tests/geometry/test_archimedean_solids.py`

**Role:** `[Scout]`

**Purpose:** Unit tests for Archimedean solid services and calculators.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `collections.Counter`
* `math`
* `pytest`
* `src.pillars.geometry.services.CuboctahedronSolidCalculator`
* `src.pillars.geometry.services.CuboctahedronSolidService`
* `src.pillars.geometry.services.IcosidodecahedronSolidCalculator`
* `src.pillars.geometry.services.IcosidodecahedronSolidService`
* `src.pillars.geometry.services.RhombicosidodecahedronSolidCalculator`
* `src.pillars.geometry.services.RhombicosidodecahedronSolidService`
* `src.pillars.geometry.services.RhombicuboctahedronSolidCalc

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_archimedean_service_matches_dataset()` - *Functional interface.*
**Exposes:** `test_archimedean_calculator_scaling()` - *Functional interface.*


---

**File:** `tests/geometry/test_general_solids.py`

**Role:** `[Scout]`

**Purpose:** Unit tests for General n-gonal solids.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.general_prismatic_solids.GeneralPrismSolidCalculator`
* `src.pillars.geometry.services.general_prismatic_solids.GeneralPrismSolidService`
* `src.pillars.geometry.services.general_pyramid_solids.GeneralPyramidSolidCalculator`
* `src.pillars.geometry.services.general_pyramid_solids.GeneralPyramidSolidService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_dynamic_build_heptagon()` - *Test building a 7-sided prism.*
**Exposes:** `test_calculator_property_update()` - *Test updating properties in the calculator.*
**Exposes:** `test_dynamic_build_septagon()` - *Test building a 7-sided pyramid.*
**Exposes:** `test_calculator_property_update()` - *Test updating properties in the calculator.*


---

**File:** `tests/geometry/test_platonic_solids.py`

**Role:** `[Scout]`

**Purpose:** Unit tests for additional platonic solid services and calculators.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.CubeSolidCalculator`
* `src.pillars.geometry.services.CubeSolidService`
* `src.pillars.geometry.services.DodecahedronSolidCalculator`
* `src.pillars.geometry.services.DodecahedronSolidService`
* `src.pillars.geometry.services.IcosahedronSolidCalculator`
* `src.pillars.geometry.services.IcosahedronSolidService`
* `src.pillars.geometry.services.OctahedronSolidCalculator`
* `src.pillars.geometry.services.OctahedronSolidService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_cube_metrics_match_closed_form()` - *Functional interface.*
**Exposes:** `test_cube_calculator_from_surface_area()` - *Functional interface.*
**Exposes:** `test_octahedron_metrics_against_formulas()` - *Functional interface.*
**Exposes:** `test_octahedron_calculator_from_volume()` - *Functional interface.*
**Exposes:** `test_dodecahedron_metrics_match_closed_form()` - *Functional interface.*
**Exposes:** `test_dodecahedron_calculator_from_surface_area()` - *Functional interface.*
**Exposes:** `test_icosahedron_metrics_match_closed_form()` - *Functional interface.*
**Exposes:** `test_icosahedron_calculator_from_volume()` - *Functional interface.*


---

**File:** `tests/geometry/test_polygonal_numbers.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pathlib.Path`
* `pillars.geometry.services.polygonal_numbers.centered_polygonal_value`
* `pillars.geometry.services.polygonal_numbers.polygonal_number_points`
* `pillars.geometry.services.polygonal_numbers.polygonal_number_value`
* `pytest`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_polygonal_number_value_matches_point_count()` - *Functional interface.*
**Exposes:** `test_centered_polygonal_value_matches_point_count()` - *Functional interface.*
**Exposes:** `test_points_are_distributed_on_polygon_rings()` - *Functional interface.*


---

**File:** `tests/geometry/test_prism_variants.py`

**Role:** `[Scout]`

**Purpose:** Unit tests covering oblique and truncated prism variants.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.ObliquePrismSolidCalculator`
* `src.pillars.geometry.services.ObliquePrismSolidService`
* `src.pillars.geometry.services.PrismaticFrustumSolidCalculator`
* `src.pillars.geometry.services.PrismaticFrustumSolidService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_oblique_prism_service_metrics_match_geometry_helpers()` - *Functional interface.*
**Exposes:** `test_oblique_prism_calculator_handles_skew_and_volume()` - *Functional interface.*
**Exposes:** `test_prismatic_frustum_service_metrics()` - *Functional interface.*
**Exposes:** `test_prismatic_frustum_calculator_volume_update()` - *Functional interface.*


---

**File:** `tests/geometry/test_pyramid_frustums.py`

**Role:** `[Scout]`

**Purpose:** Unit tests for pyramid frustum solid services and calculators.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.HexagonalPyramidFrustumSolidCalculator`
* `src.pillars.geometry.services.HexagonalPyramidFrustumSolidService`
* `src.pillars.geometry.services.PentagonalPyramidFrustumSolidCalculator`
* `src.pillars.geometry.services.PentagonalPyramidFrustumSolidService`
* `src.pillars.geometry.services.SquarePyramidFrustumSolidCalculator`
* `src.pillars.geometry.services.SquarePyramidFrustumSolidService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_square_pyramid_frustum_metrics_are_consistent()` - *Functional interface.*
**Exposes:** `test_square_pyramid_frustum_calculator_accepts_area_and_slant_inputs()` - *Functional interface.*
**Exposes:** `test_pentagonal_pyramid_frustum_metrics_follow_closed_forms()` - *Functional interface.*
**Exposes:** `test_pentagonal_pyramid_frustum_calculator_volume_and_area_inputs()` - *Functional interface.*
**Exposes:** `test_hexagonal_pyramid_frustum_metrics_and_calculator()` - *Functional interface.*
**Exposes:** `n_area()` - *Functional interface.*
**Exposes:** `hex_area()` - *Functional interface.*


---

**File:** `tests/geometry/test_rectangular_prism.py`

**Role:** `[Scout]`

**Purpose:** Unit tests for the rectangular prism solid service and calculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.RectangularPrismSolidCalculator`
* `src.pillars.geometry.services.RectangularPrismSolidService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_rectangular_prism_metrics_match_closed_form()` - *Functional interface.*
**Exposes:** `test_rectangular_prism_calculator_updates_from_volume()` - *Functional interface.*


---

**File:** `tests/geometry/test_regular_prisms.py`

**Role:** `[Scout]`

**Purpose:** Unit tests for regular prism solid services and calculators.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.HeptagonalPrismSolidService`
* `src.pillars.geometry.services.PentagonalPrismSolidCalculator`
* `src.pillars.geometry.services.TriangularPrismSolidService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_triangular_prism_service_generates_expected_metrics()` - *Functional interface.*
**Exposes:** `test_pentagonal_prism_calculator_handles_apothem_and_volume()` - *Functional interface.*
**Exposes:** `test_heptagonal_prism_service_payload_structure()` - *Functional interface.*


---

**File:** `tests/geometry/test_regular_pyramids.py`

**Role:** `[Scout]`

**Purpose:** Unit tests for additional right regular pyramid services and calculators.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.HeptagonalPyramidSolidCalculator`
* `src.pillars.geometry.services.HeptagonalPyramidSolidService`
* `src.pillars.geometry.services.HexagonalPyramidSolidCalculator`
* `src.pillars.geometry.services.PentagonalPyramidSolidCalculator`
* `src.pillars.geometry.services.PentagonalPyramidSolidService`
* `src.pillars.geometry.services.RectangularPyramidSolidCalculator`
* `src.pillars.geometry.services.RectangularPyramidSolidService`
* `src.pillars.geom

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_rectangular_pyramid_metrics_match_formulas()` - *Functional interface.*
**Exposes:** `test_rectangular_pyramid_calculator_handles_slant_and_volume()` - *Functional interface.*
**Exposes:** `test_triangular_pyramid_metrics_match_regular_formulas()` - *Functional interface.*
**Exposes:** `test_triangular_pyramid_calculator_from_base_area_and_volume()` - *Functional interface.*
**Exposes:** `test_pentagonal_pyramid_metrics_track_perimeter()` - *Functional interface.*
**Exposes:** `test_hexagonal_pyramid_calculator_allows_apothem_input()` - *Functional interface.*
**Exposes:** `test_heptagonal_pyramid_metrics_and_calculator()` - *Functional interface.*


---

**File:** `tests/geometry/test_sacred_pyramids.py`

**Role:** `[Scout]`

**Purpose:** Tests for golden and step pyramid services/calculators.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.GoldenPyramidSolidCalculator`
* `src.pillars.geometry.services.GoldenPyramidSolidService`
* `src.pillars.geometry.services.StepPyramidSolidCalculator`
* `src.pillars.geometry.services.StepPyramidSolidService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_golden_pyramid_metrics_follow_phi_ratio()` - *Functional interface.*
**Exposes:** `test_golden_pyramid_calculator_accepts_height_and_volume()` - *Functional interface.*
**Exposes:** `test_step_pyramid_metrics_sum_layer_volumes()` - *Functional interface.*
**Exposes:** `test_step_pyramid_calculator_updates_tiers()` - *Functional interface.*


---

**File:** `tests/geometry/test_square_pyramid.py`

**Role:** `[Scout]`

**Purpose:** Unit tests for the square pyramid solid service and calculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.SquarePyramidSolidCalculator`
* `src.pillars.geometry.services.SquarePyramidSolidService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_square_pyramid_metrics_match_closed_form()` - *Functional interface.*
**Exposes:** `test_square_pyramid_calculator_handles_slant_height_and_volume()` - *Functional interface.*


---

**File:** `tests/geometry/test_square_pyramid_frustum.py`

**Role:** `[Scout]`

**Purpose:** Unit tests for the square pyramid frustum solid service and calculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.SquarePyramidFrustumSolidCalculator`
* `src.pillars.geometry.services.SquarePyramidFrustumSolidService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_square_pyramid_frustum_metrics_are_consistent()` - *Functional interface.*
**Exposes:** `test_square_pyramid_frustum_calculator_accepts_area_and_slant_inputs()` - *Functional interface.*


---

**File:** `tests/geometry/test_tesseract_solid.py`

**Role:** `[Scout]`

**Purpose:** Tests for the tesseract (hypercube) solid service and calculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.TesseractSolidCalculator`
* `src.pillars.geometry.services.TesseractSolidService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_tesseract_counts_and_faces()` - *Functional interface.*
**Exposes:** `test_tesseract_calculator_scaling_volume_and_area()` - *Functional interface.*


---

**File:** `tests/geometry/test_tetrahedron_solid.py`

**Role:** `[Scout]`

**Purpose:** Unit tests for the tetrahedron solid service and calculator.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pytest`
* `src.pillars.geometry.services.tetrahedron_solid.TetrahedronSolidCalculator`
* `src.pillars.geometry.services.tetrahedron_solid.TetrahedronSolidService`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_metrics_match_closed_form()` - *Functional interface.*
**Exposes:** `test_rejects_non_positive_edge_length()` - *Functional interface.*
**Exposes:** `test_calculator_updates_from_surface_area()` - *Functional interface.*
**Exposes:** `test_calculator_updates_from_volume()` - *Functional interface.*
**Exposes:** `test_calculator_rejects_invalid_inputs()` - *Functional interface.*
**Exposes:** `test_calculator_accepts_circumference_inputs()` - *Functional interface.*


---

**File:** `tests/manual_metadata_test.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `docx`
* `os`
* `pathlib.Path`
* `pillars.document_manager.utils.parsers.DocumentParser`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `create_dummy_docx()` - *Functional interface.*
**Exposes:** `test_metadata_extraction()` - *Functional interface.*


---

**File:** `tests/mock_metadata_test.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `pathlib.Path`
* `pillars.document_manager.utils.parsers.DocumentParser`
* `sys`
* `unittest.mock.MagicMock`
* `unittest.mock.patch`
* `unittest`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_parse_docx_metadata()` - *Functional interface.*
**Exposes:** `test_parse_pdf_metadata()` - *Functional interface.*


---

**File:** `tests/repro_detached.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.document_manager.services.mindscape_service.mindscape_service_context`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `repro()` - *Functional interface.*


---

**File:** `tests/rite_of_adyton_kamea.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.adyton.services.kamea_loader_service.KameaLoaderService`
* `sys`
* `unittest`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `setUp()` - *Functional interface.*
**Exposes:** `test_grid_size()` - *Functional interface.*
**Exposes:** `test_singularity()` - *Functional interface.*
**Exposes:** `test_octant_logic()` - *Functional interface.*
**Exposes:** `test_tablet_size()` - *Functional interface.*


---

**File:** `tests/rituals/render_chart_preview.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QSize`
* `PyQt6.QtWidgets.QApplication`
* `datetime.datetime`
* `os`
* `pillars.astrology.models.chart_models.HousePosition`
* `pillars.astrology.models.chart_models.PlanetPosition`
* `pillars.astrology.ui.chart_canvas.ChartCanvas`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `render_preview()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_acrostics.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.gematria.services.acrostic_service.AcrosticResult`
* `pillars.gematria.services.acrostic_service.AcrosticService`
* `sys`
* `unittest.mock.MagicMock`
* `unittest`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `setUp()` - *Functional interface.*
**Exposes:** `test_line_acrostic()` - *Test standard first letter acrostic on lines.*
**Exposes:** `test_word_acrostic()` - *Test first letter acrostic on words.*
**Exposes:** `test_telestich()` - *Test last letter telestich.*
**Exposes:** `test_substring_search()` - *Test finding a valid word hidden in a longer acrostic.*


---

**File:** `tests/rituals/rite_of_advanced_visualization.py`

**Role:** `[Scout]`

**Purpose:** Rite of Advanced Visualization.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pillars.geometry.services.cube_solid.CubeSolidService`
* `pillars.geometry.services.dodecahedron_solid.DodecahedronSolidService`
* `pillars.geometry.services.icosahedron_solid.IcosahedronSolidService`
* `pillars.geometry.services.octahedron_solid.OctahedronSolidService`
* `pillars.geometry.services.tetrahedron_solid.TetrahedronSolidService`
* `sys`
* `typing.Tuple`
* `unittest`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_dual_counts()` - *Functional interface.*
**Exposes:** `test_tetrahedron_dual()` - *Functional interface.*
**Exposes:** `test_cube_dual()` - *Functional interface.*
**Exposes:** `test_octahedron_dual()` - *Functional interface.*
**Exposes:** `test_dodecahedron_dual()` - *Functional interface.*
**Exposes:** `test_icosahedron_dual()` - *Functional interface.*
**Exposes:** `test_dual_scale_consistency()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_archimedes_metrics.py`

**Role:** `[Scout]`

**Purpose:** Rite of Archimedes Metrics

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pillars.geometry.services.archimedean_solids.CuboctahedronSolidCalculator`
* `pillars.geometry.services.archimedean_solids.TruncatedTetrahedronSolidCalculator`
* `sys`
* `unittest`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_cuboctahedron_metrics()` - *Verify Cuboctahedron has Square and Triangle metrics.*
**Exposes:** `test_bidirectional_solving()` - *Verify setting derived metrics updates the solid.*
**Exposes:** `test_truncated_tetrahedron()` - *Verify Truncated Tetrahedron (Transitions involved).*


---

**File:** `tests/rituals/rite_of_calculator_refinement.py`

**Role:** `[Scout]`

**Purpose:** Rite of Calculator Refinement

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pillars.geometry.services.cone_solid.ConeSolidCalculator`
* `pillars.geometry.services.cylinder_solid.CylinderSolidCalculator`
* `pillars.geometry.services.regular_antiprism_solids.SquareAntiprismSolidCalculator`
* `pillars.geometry.services.regular_prism_solids.HexagonalPrismSolidCalculator`
* `pillars.geometry.services.regular_pyramid_frustum_solids.HexagonalPyramidFrustumSolidCalculator`
* `pillars.geometry.services.regular_pyramid_solids.HexagonalPyramidSolidCalculator`
* `pillar

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_cylinder_solving()` - *Verify Cylinder bidirectional metrics.*
**Exposes:** `test_cone_solving()` - *Verify Cone bidirectional metrics.*
**Exposes:** `test_pyramid_solving()` - *Verify Pyramid bidirectional metrics (Square Pyramid).*
**Exposes:** `test_prism_solving()` - *Verify Prism bidirectional metrics.*
**Exposes:** `test_antiprism_solving()` - *Verify Antiprism bidirectional metrics.*
**Exposes:** `test_frustum_solving()` - *Verify Frustum bidirectional metrics.*


---

**File:** `tests/rituals/rite_of_canvas.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPointF`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QMouseEvent`
* `PyQt6.QtWidgets.QApplication`
* `logging`
* `pillars.document_manager.ui.canvas.infinite_canvas.InfiniteCanvasView`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `RiteOfCanvas()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_chiasmus.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.gematria.services.chiasmus_service.ChiasmusService`
* `sys`
* `unittest`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `calculate()` - *Functional interface.*
**Exposes:** `setUp()` - *Functional interface.*
**Exposes:** `test_basic_chiasmus()` - *Functional interface.*
**Exposes:** `test_even_chiasmus()` - *Functional interface.*
**Exposes:** `test_depth_limit()` - *Functional interface.*
**Exposes:** `test_gematria_match()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_dynamis.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.time_mechanics.services.tzolkin_service.TzolkinService`
* `sys`
* `traceback`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_dynamis_logic()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_els.py`

**Role:** `[Scout]`

**Purpose:** Rite of ELS - Verification ritual for ELS Bible Code search.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.gematria.services.els_service.ELSSearchService`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_saturn_structure()` - *♄ SATURN: Test grid factor calculation.*
**Exposes:** `test_sun_core_logic()` - *☉ SUN: Test core ELS search algorithm.*
**Exposes:** `test_mars_edge_cases()` - *♂ MARS: Test edge cases and error handling.*
**Exposes:** `test_mercury_text_preparation()` - *☿ MERCURY: Test text stripping and position mapping.*
**Exposes:** `test_venus_matrix_building()` - *♀ VENUS: Test matrix arrangement.*
**Exposes:** `main()` - *Execute the Rite of ELS.*


---

**File:** `tests/rituals/rite_of_floor.py`

**Role:** `[Scout]`

**Purpose:** RITE OF THE FLOOR

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `os`
* `pillars.adyton.constants.KATALYSIS_SIDE_LENGTH`
* `pillars.adyton.constants.PERIMETER_SIDE_LENGTH`
* `pillars.adyton.constants.VOWEL_RING_COLORS`
* `pillars.adyton.models.floor.FloorGeometry`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `break_seal_floor()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_font_manager.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QApplication`
* `importlib.util`
* `os`
* `shared.ui.font_loader`
* `sys`
* `unittest.mock.MagicMock`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `import_font_manager_window()` - *Functional interface.*
**Exposes:** `rite_of_font_manager()` - *Rite of Verification for the Font Manager Utility.*


---

**File:** `tests/rituals/rite_of_gematria_transitions.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `src.pillars.gematria.ui.gematria_calculator_window.GematriaCalculatorWindow`
* `sys`
* `unittest.mock.MagicMock`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_presence()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_genesis_verification.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QApplication`
* `main.IsopGemMainWindow`
* `os`
* `pillars.time_mechanics.ui.TimeMechanicsHub`
* `shared.database.init_db`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `rite_of_saturn()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_hestia_3d.py`

**Role:** `[Scout]`

**Purpose:** Rite of Hestia 3D Verification.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `pathlib.Path`
* `pillars.geometry.services.vault_of_hestia_solid.VaultOfHestiaSolidCalculator`
* `pillars.geometry.services.vault_of_hestia_solid.VaultOfHestiaSolidService`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_hestia_3d()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_hyperphysics.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QColor`
* `PyQt6.QtWidgets.QApplication`
* `os`
* `pillars.time_mechanics.ui.dynamis_window.PillarGauge`
* `pillars.time_mechanics.ui.dynamis_window.TrigramItem`
* `pillars.time_mechanics.ui.dynamis_window.TzolkinDynamisWindow`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `rite_of_hyperphysics()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_interpretation.py`

**Role:** `[Scout]`

**Purpose:** Rite of Interpretation: Verification of the Chart Interpretation Service.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `datetime.datetime`
* `os`
* `pathlib.Path`
* `pillars.astrology.models.chart_models.AstrologyEvent`
* `pillars.astrology.models.chart_models.ChartResult`
* `pillars.astrology.models.chart_models.GeoLocation`
* `pillars.astrology.models.chart_models.HousePosition`
* `pillars.astrology.models.chart_models.PlanetPosition`
* `pillars.astrology.repositories.interpretation_repository.InterpretationRepository`
* `pillars.astrology.services.interpretation_service.InterpretationService`
* `sys`
* `uni

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_combinatorial_interpretation()` - *Functional interface.*
**Exposes:** `test_fallback_logic()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_keyboard_styling.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QPoint`
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QFontDatabase`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QPushButton`
* `os`
* `shared.ui.font_loader`
* `shared.ui.virtual_keyboard.VirtualKeyboard`
* `sys`
* `traceback`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `rite_of_keyboard_styling()` - *Rite of Verification for the Virtual Keyboard Refactoring.*


---

**File:** `tests/rituals/rite_of_mindscape_tree.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.document_manager.services.mindscape_service.MindEdgeType`
* `pillars.document_manager.services.mindscape_service.MindscapeService`
* `shared.database.Base`
* `shared.database.get_db_session`
* `sqlalchemy.create_engine`
* `sqlalchemy.orm.sessionmaker`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `rite_of_mindscape_tree()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_notebooks.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `pillars.document_manager.services.notebook_service.NotebookService`
* `shared.database.get_db_session`
* `sqlalchemy.orm.Session`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `RiteOfNotebooks()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_prisms_expanded.py`

**Role:** `[Scout]`

**Purpose:** Verification Ritual for Expanded Prisms and Antiprisms.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `os`
* `pillars.geometry.services.GeneralAntiprismSolidCalculator`
* `pillars.geometry.services.GeneralPrismSolidCalculator`
* `pillars.geometry.services.GyroelongatedSquarePrismSolidService`
* `pillars.geometry.services.SnubAntiprismSolidService`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_general_prism()` - *Functional interface.*
**Exposes:** `test_general_antiprism()` - *Functional interface.*
**Exposes:** `test_snub_antiprism()` - *Functional interface.*
**Exposes:** `test_gyro_prism()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_quadset.py`

**Role:** `[Scout]`

**Purpose:** Deep Rite of the Seven Seals - Comprehensive Verification Script

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.tq.services.number_properties.NumberPropertiesService`
* `pillars.tq.services.quadset_engine.QuadsetEngine`
* `sys`
* `time`
* `traceback`
* `typing.Any`
* `typing.List`
* `typing.Tuple`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_section()` - *Print section header.*
**Exposes:** `test_result()` - *Print test result.*
**Exposes:** `run_tests()` - *Run list of tests, return (passed, total).*
**Exposes:** `test_saturn()` - *Functional interface.*
**Exposes:** `test_jupiter()` - *Functional interface.*
**Exposes:** `test_mars()` - *Functional interface.*
**Exposes:** `test_sun()` - *Functional interface.*
**Exposes:** `test_venus()` - *Functional interface.*
**Exposes:** `test_mercury()` - *Functional interface.*
**Exposes:** `test_moon()` - *Functional interface.*
**Exposes:** `main()` - *Functional interface.*
**Exposes:** `test_happy_exhaustive()` - *Functional interface.*
**Exposes:** `test_sad_exhaustive()` - *Functional interface.*
**Exposes:** `test_primes()` - *Functional interface.*
**Exposes:** `test_composites()` - *Functional interface.*
**Exposes:** `test_triangular()` - *Functional interface.*
**Exposes:** `test_squares()` - *Functional interface.*
**Exposes:** `test_cubes()` - *Functional interface.*
**Exposes:** `test_fibonacci()` - *Functional interface.*
**Exposes:** `test_tetrahedral()` - *Functional interface.*
**Exposes:** `test_cubic()` - *Functional interface.*
**Exposes:** `test_keys()` - *Functional interface.*
**Exposes:** `test_types()` - *Functional interface.*
**Exposes:** `test_quadset_symmetry()` - *Functional interface.*
**Exposes:** `test_quadset_diffs()` - *Functional interface.*
**Exposes:** `test_chain_iteration_consistency()` - *Functional interface.*
**Exposes:** `test_none_props()` - *Functional interface.*
**Exposes:** `test_none_happy()` - *Functional interface.*
**Exposes:** `test_string_props()` - *Functional interface.*
**Exposes:** `test_float_props()` - *Functional interface.*
**Exposes:** `test_stateless()` - *Functional interface.*
**Exposes:** `test_deterministic_chain()` - *Functional interface.*
**Exposes:** `test_no_side_effects()` - *Functional interface.*
**Exposes:** `test_engine_stateless()` - *Functional interface.*
**Exposes:** `test_fn()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_ribbon.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QAction`
* `PyQt6.QtGui.QIcon`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QMainWindow`
* `os`
* `pillars.document_manager.ui.ribbon_widget.RibbonWidget`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `rite_of_ribbon()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_scaling.py`

**Role:** `[Scout]`

**Purpose:** RITE OF SCALING

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `os`
* `pillars.adyton.constants.KATALYSIS_SIDE_LENGTH`
* `pillars.adyton.constants.PERIMETER_SIDE_LENGTH`
* `pillars.adyton.constants.Z_BIT_INCHES`
* `pillars.adyton.models.prism.SevenSidedPrism`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `break_seal_scaling()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_search.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.gematria.models.CalculationRecord`
* `pillars.gematria.repositories.sqlite_calculation_repository.SQLiteCalculationRepository`
* `shared.database.SessionLocal`
* `shared.database.init_db`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `run_rite()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_special_chars.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QApplication`
* `importlib.util`
* `os`
* `sys`
* `traceback`
* `unittest.mock.MagicMock`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `import_dialog()` - *Functional interface.*
**Exposes:** `rite_of_special_chars()` - *Rite of Verification for the Special Characters Dialog.*


---

**File:** `tests/rituals/rite_of_trinity_3d.py`

**Role:** `[Scout]`

**Purpose:** Verification Ritual for the Foundational Trinity (Sphere, Cylinder, Cone).

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `os`
* `pillars.geometry.services.cone_solid.ConeSolidCalculator`
* `pillars.geometry.services.cylinder_solid.CylinderSolidCalculator`
* `pillars.geometry.services.sphere_solid.SphereSolidCalculator`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_sphere()` - *Functional interface.*
**Exposes:** `test_cylinder()` - *Functional interface.*
**Exposes:** `test_cone()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_tzolkin.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `datetime.date`
* `datetime.timedelta`
* `os`
* `pillars.time_mechanics.services.tzolkin_service.TzolkinService`
* `sys`
* `traceback`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_tzolkin_logic()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_tzolkin_grid.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `datetime.date`
* `datetime.timedelta`
* `os`
* `pillars.time_mechanics.services.tzolkin_service.TzolkinService`
* `sys`
* `traceback`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_grid_logic()` - *Functional interface.*


---

**File:** `tests/rituals/rite_of_word_acrostics.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.gematria.services.acrostic_service.AcrosticService`
* `sys`
* `unittest.mock.MagicMock`
* `unittest`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `setUp()` - *Functional interface.*
**Exposes:** `test_mid_stream_word_acrostic()` - *Test finding an acrostic hidden in the middle of a stream of words.*


---

**File:** `tests/rituals/verify_advanced_tab.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QApplication`
* `os`
* `src.pillars.astrology.ui.natal_chart_window.NatalChartWindow`
* `sys`
* `unittest`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `setUpClass()` - *Functional interface.*
**Exposes:** `test_advanced_tab_structure()` - *Functional interface.*


---

**File:** `tests/rituals/verify_arabic_parts.py`

**Role:** `[Scout]`

**Purpose:** Verify Arabic Parts service works correctly.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.astrology.services.arabic_parts_service.ArabicPartsService`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `main()` - *Functional interface.*


---

**File:** `tests/rituals/verify_aspects.py`

**Role:** `[Scout]`

**Purpose:** Verify Aspects service works correctly.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.astrology.services.aspects_service.AspectsService`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `main()` - *Functional interface.*


---

**File:** `tests/rituals/verify_calculator_ui.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QApplication`
* `os`
* `pillars.geometry.services.CircleShape`
* `pillars.geometry.services.GeometricShape`
* `pillars.geometry.ui.geometry_calculator_window.GeometryCalculatorWindow`
* `sys`
* `traceback`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_ui()` - *Functional interface.*


---

**File:** `tests/rituals/verify_fixed_stars.py`

**Role:** `[Scout]`

**Purpose:** Verify Fixed Stars service works correctly.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `datetime.datetime`
* `datetime.timezone`
* `os`
* `pillars.astrology.services.fixed_stars_service.FixedStarsService`
* `swisseph`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `main()` - *Functional interface.*


---

**File:** `tests/rituals/verify_harmonics.py`

**Role:** `[Scout]`

**Purpose:** Verify Harmonics service works correctly.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.astrology.services.harmonics_service.HarmonicsService`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `main()` - *Functional interface.*


---

**File:** `tests/rituals/verify_midpoints.py`

**Role:** `[Scout]`

**Purpose:** Verify Midpoints service works correctly.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.astrology.services.midpoints_service.MidpointsService`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `main()` - *Functional interface.*


---

**File:** `tests/rituals/verify_modular_calculator.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QApplication`
* `os`
* `pillars.geometry.services.CircleShape`
* `pillars.geometry.ui.calculator.calculator_window.GeometryCalculatorWindow`
* `sys`
* `traceback`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_modular_ui()` - *Functional interface.*


---

**File:** `tests/test_amun_audio.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.tq.services.amun_audio_service.AmunAudioService`
* `sys`
* `unittest`
* `wave`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_wave_generation()` - *Test that generate_wave_file creates a valid WAV file.*
**Exposes:** `test_silence()` - *Test 0 frequency generates silence.*


---

**File:** `tests/test_amun_sound.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `pathlib.Path`
* `pillars.tq.models.amun_sound.AmunSoundCalculator`
* `sys`
* `unittest`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `setUp()` - *Functional interface.*
**Exposes:** `test_zero_ditrune()` - *Test Value 0 (000000) -> Reversed 000000*
**Exposes:** `test_one_ditrune()` - *Test Value 1 (000001) -> Reversed 100000*
**Exposes:** `test_octave_shift_cosmic()` - *Test Value forcing Radiance Plane (Bigram 8 in Ch1)*
**Exposes:** `test_three_ditrune()` - *Test Value 3 (000010) -> Reversed 010000*


---

**File:** `tests/test_calculator_persistence.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `pathlib.Path`
* `src.shared.utils.calculator_persistence.CalculatorState`
* `src.shared.utils.calculator_persistence.load_state`
* `src.shared.utils.calculator_persistence.save_state`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_load_missing_returns_default()` - *Functional interface.*
**Exposes:** `test_save_then_load_round_trip()` - *Functional interface.*
**Exposes:** `test_load_corrupt_json_falls_back()` - *Functional interface.*
**Exposes:** `test_history_is_capped()` - *Functional interface.*


---

**File:** `tests/test_correspondences_cycles.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QApplication`
* `pillars.correspondences.ui.spreadsheet_view.SpreadsheetModel`
* `pytest`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `qapp()` - *Functional interface.*
**Exposes:** `build_model()` - *Functional interface.*
**Exposes:** `test_self_reference_reports_cycle()` - *Functional interface.*
**Exposes:** `test_two_cell_cycle_reports_cycle_both_cells()` - *Functional interface.*
**Exposes:** `test_non_cycle_evaluates_value()` - *Functional interface.*
**Exposes:** `test_range_reference_with_self_cycle()` - *Functional interface.*


---

**File:** `tests/test_egyptian_measures.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `importlib.util`
* `pathlib.Path`
* `pytest`
* `src.shared.utils.measure_conversion.convert_between_units`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `load_calc_module()` - *Functional interface.*
**Exposes:** `test_egyptian_length_derivations_are_consistent()` - *Functional interface.*
**Exposes:** `test_egyptian_kite_is_tenth_deben()` - *Functional interface.*
**Exposes:** `test_egyptian_hinu_is_tenth_hekat()` - *Functional interface.*
**Exposes:** `test_convert_1_cubit_to_palms()` - *Functional interface.*


---

**File:** `tests/test_measure_conversion.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `math`
* `pytest`
* `src.shared.utils.measure_conversion.convert_between_units`
* `src.shared.utils.measure_conversion.parse_measure_value`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_parse_measure_value_plain_float()` - *Functional interface.*
**Exposes:** `test_parse_measure_value_commas()` - *Functional interface.*
**Exposes:** `test_parse_measure_value_fraction()` - *Functional interface.*
**Exposes:** `test_parse_measure_value_invalid()` - *Functional interface.*
**Exposes:** `test_convert_between_units_length_round_trip()` - *Functional interface.*
**Exposes:** `test_convert_between_units_mass()` - *Functional interface.*
**Exposes:** `test_convert_between_units_uses_string_factor()` - *Functional interface.*
**Exposes:** `test_convert_between_units_rejects_invalid_unit()` - *Functional interface.*


---

**File:** `tests/test_qurl_parsing.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QUrl`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_url_parsing()` - *Functional interface.*


---

**File:** `tests/test_safe_math_eval.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `importlib.util`
* `math`
* `pathlib.Path`
* `pytest`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `load_safe_math_eval()` - *Functional interface.*
**Exposes:** `smart_backspace()` - *Functional interface.*
**Exposes:** `safe_eval()` - *Functional interface.*
**Exposes:** `test_basic_math()` - *Functional interface.*
**Exposes:** `test_trig_and_constants()` - *Functional interface.*
**Exposes:** `test_unit_suffixes_deg_rad()` - *Functional interface.*
**Exposes:** `test_deg_rad_helpers()` - *Functional interface.*
**Exposes:** `test_ans_constant_usage()` - *Functional interface.*
**Exposes:** `test_implicit_multiplication()` - *Functional interface.*
**Exposes:** `test_postfix_factorial_and_whitespace()` - *Functional interface.*
**Exposes:** `test_factorial_ui_style_postfix()` - *Functional interface.*
**Exposes:** `test_more_functions_allowlist()` - *Functional interface.*
**Exposes:** `test_smart_backspace()` - *Functional interface.*
**Exposes:** `test_rejects_unsafe_constructs()` - *Functional interface.*
**Exposes:** `test_domain_errors_become_valueerror()` - *Functional interface.*


---

**File:** `tests/test_time_units.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `__future__.annotations`
* `importlib.util`
* `pathlib.Path`
* `pytest`
* `src.shared.utils.measure_conversion.convert_between_units`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `load_calc_module()` - *Functional interface.*
**Exposes:** `test_time_units_include_basic_si()` - *Functional interface.*
**Exposes:** `test_convert_seconds_to_minutes()` - *Functional interface.*
**Exposes:** `test_convert_days_to_hours()` - *Functional interface.*
**Exposes:** `test_julian_year_seconds_is_exact_by_definition()` - *Functional interface.*


---

**File:** `tests/verification/verify_alignment_mutex.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QActionGroup`
* `PyQt6.QtWidgets.QApplication`
* `pillars.document_manager.ui.rich_text_editor.RichTextEditor`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_alignment_mutex()` - *Functional interface.*


---

**File:** `tests/verification/verify_clear_highlight.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtGui.QColor`
* `PyQt6.QtWidgets.QApplication`
* `pillars.document_manager.ui.rich_text_editor.RichTextEditor`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_clear_highlight()` - *Functional interface.*


---

**File:** `tests/verification/verify_headings.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtGui.QFont`
* `PyQt6.QtGui.QTextCharFormat`
* `PyQt6.QtWidgets.QApplication`
* `pillars.document_manager.ui.rich_text_editor.RichTextEditor`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_semantic_headings()` - *Functional interface.*


---

**File:** `tests/verification/verify_headings_gui.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtGui.QFont`
* `PyQt6.QtWidgets.QApplication`
* `pillars.document_manager.ui.rich_text_editor.RichTextEditor`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `run_test()` - *Functional interface.*
**Exposes:** `step1()` - *Functional interface.*
**Exposes:** `step2()` - *Functional interface.*
**Exposes:** `step3()` - *Functional interface.*
**Exposes:** `step4()` - *Functional interface.*


---

**File:** `tests/verification/verify_lists.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.QTimer`
* `PyQt6.QtWidgets.QApplication`
* `pillars.document_manager.ui.rich_text_editor.RichTextEditor`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `run_test()` - *Functional interface.*
**Exposes:** `step1()` - *Functional interface.*
**Exposes:** `step2()` - *Functional interface.*
**Exposes:** `step3()` - *Functional interface.*
**Exposes:** `step4()` - *Functional interface.*


---

**File:** `tests/verification/verify_pdf_export.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtPrintSupport.QPrinter`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QTextEdit`
* `os`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_pdf_export()` - *Functional interface.*


---

**File:** `tests/verification/verify_ribbon.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtWidgets.QApplication`
* `pillars.document_manager.ui.ribbon_widget.RibbonWidget`
* `pillars.document_manager.ui.rich_text_editor.RichTextEditor`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_ribbon()` - *Functional interface.*


---

**File:** `tests/verify_database_manager.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pathlib.Path`
* `pillars.document_manager.models.document.DocumentImage`
* `pillars.document_manager.services.document_service.DocumentService`
* `shared.database.get_db_session`
* `sys`
* `traceback`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_database_manager()` - *Functional interface.*


---

**File:** `tests/verify_fixes.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `PyQt6.QtCore.Qt`
* `PyQt6.QtWidgets.QApplication`
* `PyQt6.QtWidgets.QTextEdit`
* `os`
* `pathlib.Path`
* `pillars.document_manager.ui.rich_text_editor.RichTextEditor`
* `pillars.document_manager.utils.parsers.DocumentParser`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_editor_ltr()` - *Functional interface.*
**Exposes:** `verify_parser_integrity()` - *Functional interface.*


---

**File:** `tests/verify_geometry_fixes.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `math`
* `os`
* `pillars.geometry.services.polygon_shape.RegularPolygonShape`
* `pillars.geometry.services.square_shape.RectangleShape`
* `pillars.geometry.services.triangle_shape.RightTriangleShape`
* `sys`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_polygon_drawing_scaling()` - *Functional interface.*
**Exposes:** `test_rectangle_solving()` - *Functional interface.*
**Exposes:** `test_right_triangle_solving()` - *Functional interface.*


---

**File:** `tests/verify_image_utils.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `base64`
* `os`
* `pillars.document_manager.utils.image_utils.extract_images_from_html`
* `pillars.document_manager.utils.image_utils.restore_images_in_html`
* `sys`
* `unittest.mock.MagicMock`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_image_utils()` - *Functional interface.*


---

**File:** `tests/verify_list_parsing.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.document_manager.utils.parsers.DocumentParser`
* `sys`
* `unittest.mock.MagicMock`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `test_list_detection()` - *Functional interface.*


---

**File:** `tests/verify_mindscape_service.py`

**Role:** `[Scout]`

**Purpose:** Soul not yet specified.

**Input (Ingests):**
* Pure data structure or utility module.

**Output (Emits):**
* Data primitives or DTOs.

**Dependencies (It Needs):**
* `os`
* `pillars.document_manager.services.mindscape_service.mindscape_service_context`
* `sys`
* `traceback`

**Consumers (Who Needs It):**
* None detected.

**Key Interactions:**
**Exposes:** `verify_service()` - *Functional interface.*
