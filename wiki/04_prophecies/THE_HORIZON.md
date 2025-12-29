<!-- Last Verified: 2025-12-28 -->

# The Horizon — Astrology Pillar Professionalization

This prophecy charts the work required to elevate the Astrology pillar to a professional-grade engine that matches commercial charting suites and research tools.

## The Bar for Professional Grade
- **Astrometric fidelity**: Swiss Ephemeris accuracy (TT vs UT handling, leap seconds), robust timezone resolution, true node vs mean node selection, topocentric and geocentric options, sidereal/ayanamsa selection.
- **Chart breadth**: Natal, transit overlays, synastry/relationship, solar/lunar returns, progressed charts (secondary, solar arc), mundane/event charts, harmonic charts, fixed stars, Arabic Parts/Lots, midpoints.
- **House/angle rigor**: Multiple house systems (Placidus, Whole Sign, Koch, Regiomontanus), accurate ASC/MC computation per latitude limits, vertex/east point, parallels/contra-parallels.
- **Aspect discipline**: Configurable orbs per aspect/body, moieties, applying/separating flags, aspect sets (major, minor, harmonic), parallels/declination aspects.
- **Interpretation depth**: Complete content coverage for planet-sign, planet-house, planet-sign-house triads, aspect text (A→B directional), fixed-star delineations, lot interpretations, transit narratives, progressions/returns narratives.
- **UX and reporting**: SVG/PNG/PDF export, data export (CSV/JSON), printing templates, accessible overlays, responsive redraws, keyboard navigation, snapshot/versioning of charts and interpretations.
- **Observability and tests**: Deterministic tests against ephemeris known-values, regression tests for aspect/house edge cases, logging with structured context, performance envelopes for batch ephemeris generation.

## Current Pillar Snapshot (from the Grimoire)
- **Existing strengths**: OpenAstro2 bridge, natal chart casting, Arabic Parts, aspects engine, fixed stars, harmonic charts, Venus Rose/Neo-Aubrey visualizations, chart storage, interpretation repository hooks ([wiki/02_pillars/astrology/REFERENCE.md](wiki/02_pillars/astrology/REFERENCE.md), [wiki/02_pillars/astrology/EXPLANATION.md](wiki/02_pillars/astrology/EXPLANATION.md)).
- **UI coverage**: Astrology Hub, Natal Chart window (SVG rendering), Planetary Positions, Venus Rose, Neo-Aubrey, Current Transits, transit overlay support noted in guides ([wiki/02_pillars/astrology/GUIDES.md](wiki/02_pillars/astrology/GUIDES.md)).
- **Known omissions (observed)**: No explicit solar/lunar return flows, no synastry/progression UI, limited export/reporting paths, unknown timezone/ayanamsa handling, interpretation content likely incomplete for triads and transits, unknown test coverage for ephemeris accuracy and house edge cases.

## Current Implementation Snapshot (code-grounded)
- **Ephemeris & engines**: Swiss Ephemeris via OpenAstro2 in [src/pillars/astrology/services/openastro_service.py](src/pillars/astrology/services/openastro_service.py); Skyfield-backed ephemeris provider in [src/pillars/astrology/repositories/ephemeris_provider.py](src/pillars/astrology/repositories/ephemeris_provider.py) for planetary longitudes, heliocentric/ecliptic data, and lunar node calculations.
- **Chart types currently wired**: Natal charts through [src/pillars/astrology/ui/natal_chart_window.py](src/pillars/astrology/ui/natal_chart_window.py) with SVG render; current transits and overlays via [src/pillars/astrology/ui/current_transit_window.py](src/pillars/astrology/ui/current_transit_window.py) and [src/pillars/astrology/ui/planetary_positions_window.py](src/pillars/astrology/ui/planetary_positions_window.py); harmonic charts via [src/pillars/astrology/services/harmonics_service.py](src/pillars/astrology/services/harmonics_service.py); Venus Rose and Neo-Aubrey simulations as specialized visual windows.
- **Aspects & lots**: Major/minor/harmonic aspect calculation in [src/pillars/astrology/services/aspects_service.py](src/pillars/astrology/services/aspects_service.py); Arabic Parts with sect-aware reversal in [src/pillars/astrology/services/arabic_parts_service.py](src/pillars/astrology/services/arabic_parts_service.py).
- **Fixed stars & symbols**: Fixed star proximity checks in [src/pillars/astrology/services/fixed_stars_service.py](src/pillars/astrology/services/fixed_stars_service.py); Maat degree symbols lookup in [src/pillars/astrology/services/maat_symbols_service.py](src/pillars/astrology/services/maat_symbols_service.py).
- **Persistence & data**: Chart storage via [src/pillars/astrology/services/chart_storage_service.py](src/pillars/astrology/services/chart_storage_service.py) and [src/pillars/astrology/repositories/chart_repository.py](src/pillars/astrology/repositories/chart_repository.py); domain models in [src/pillars/astrology/models/chart_models.py](src/pillars/astrology/models/chart_models.py) and [src/pillars/astrology/models/chart_record.py](src/pillars/astrology/models/chart_record.py).
- **Interpretation layer**: Interpretation DTOs in [src/pillars/astrology/models/interpretation_models.py](src/pillars/astrology/models/interpretation_models.py) with content lookup in [src/pillars/astrology/repositories/interpretation_repository.py](src/pillars/astrology/repositories/interpretation_repository.py); service wiring in [src/pillars/astrology/services/interpretation_service.py](src/pillars/astrology/services/interpretation_service.py).

## Gap Analysis — Required Upgrades
- **Timekeeping & ephemeris**: Enforce TT/UT conversions, leap seconds, delta-T sourcing; allow true/mean node toggle; implement sidereal with selectable ayanamsa; add topocentric option and atmospheric refraction handling for angles.
- **Timezone & geocoding**: Integrate robust timezone resolver (e.g., tzdb via geo lookup) with historical DST; validate location input paths and caching.
- **Chart families**: Add solar/lunar return generation, secondary progressions (Naibod), solar arc directions, synastry/bi-wheel overlays, composite charts, mundane/event charts, midpoints grid.
- **House/angle systems**: Expand house systems; add latitude guardrails for Placidus/Koch near polar latitudes; compute vertex/east point; ensure MC/ASC correctness across coordinate modes.
- **Aspect engine**: Configurable orbs per planet/aspect; moieties; parallels/contra-parallels; minor/harmonic aspect sets toggleable; applying/separating accuracy using velocities.
- **Fixed stars & lots**: Expand star catalog with magnitudes and mythic notes; add parans; extend Arabic Parts catalog and validation; add orbs and day/night reversals with tests.
- **Interpretation corpus**: Fill triads (planet-sign-house), aspects directional text, transits to natal, progressions/returns narratives, star and lot delineations; surface weights and source metadata.
- **Data & persistence**: Versioned chart records, delta history, tagging/search facets, export/import flows (JSON/CSV), cached ephemeris slices for batch runs.
- **UX/reporting**: PDF/PNG export of charts and reports; printable layouts; keyboard shortcuts; accessibility labeling; responsive redraw on setting changes; status/toast feedback for failures.
- **Performance & offline**: Benchmarks for batch ephemeris generation (Jupiter trial); optional offline mode with cached ephemeris; background threading for heavy calculations (avoid main-thread freezes).
- **Observability & safety**: Structured logging (pillar=astrology, chart_type, calculation_mode), slow-op warnings, graceful fallbacks when ephemeris/geo lookup fails.
- **Verification**: Golden-value tests for planetary positions (sample dates), house cusp validations, aspect matrix checks, lots reversal tests, fixed-star proximity tests, performance thresholds, UI smoke tests headless where possible.

## Phased Roadmap
- **Phase 1 — Astrometric Integrity**: Harden ephemeris/timezone handling; add true/mean node toggle, sidereal/ayanamsa selection, topocentric option; create golden-value tests for planetary positions and house cusps.
- **Phase 2 — Chart Breadth & Engines**: Implement solar/lunar returns, progressions (secondary, solar arc), synastry/bi-wheel, composite charts, expanded house systems, aspect engine upgrades (orbs/moieties/parallels).
- **Phase 3 — Interpretation & Reporting**: Complete interpretation corpus (triads, aspects, transits, progressions, stars, lots), add report generation (PDF/PNG), export/import, versioned chart storage with tags.
- **Phase 4 — UX, Performance, Observability**: Responsive redraws, keyboard/accessibility, structured logging, slow-op alerts, background workers for heavy ops, caching/offline mode, regression suite for UI flows and performance.

## Verification Plan (Seals Focus)
- **Saturn**: Static analysis for sovereignty and import purity; type coverage across services and repositories.
- **Jupiter**: Benchmarks for batch ephemeris generation and chart rendering; guardrail thresholds.
- **Mars**: Fuzzed inputs for dates/locations/timezones; invalid coordinates; missing ephemeris files; ensure graceful errors.
- **Sun/Venus**: Golden-value correctness for planetary positions, houses, aspects, lots; DTO shape consistency for chart and interpretation outputs.
- **Mercury**: Structured logging coverage for every service entry/exit; signal/slot emissions for UI updates.
- **Moon**: Persistence round-trips for chart storage, versioning, and imports/exports.
