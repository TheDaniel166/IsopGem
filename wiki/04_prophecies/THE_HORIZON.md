<!-- Last Verified: 2025-12-30 -->

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

### Timekeeping & Ephemeris
- [ ] Enforce TT/UT conversions, leap seconds, delta-T sourcing
- [ ] Allow true/mean node toggle
- [ ] Implement sidereal with selectable ayanamsa
- [ ] Add topocentric option and atmospheric refraction handling for angles

### Timezone & Geocoding
- [x] Integrate robust timezone resolver (`location_lookup.py`)
- [ ] Validate location input paths and caching
- [ ] Historical DST handling

### Chart Families
- [x] Synastry/bi-wheel overlays (`synastry_service.py`, `synastry_window.py`)
- [x] Solar/lunar return generation (`returns_service.py`, `returns_window.py`)
- [x] Secondary progressions (`progressions_service.py`, `progressions_window.py`)
- [x] Midpoints grid (`midpoints_service.py`, `midpoints_dial.py`)
- [ ] Solar arc directions
- [ ] Composite charts (stub exists: `composite_chart_window.py`)
- [ ] Mundane/event charts

### House/Angle Systems
- [ ] Expand house systems (Koch, Regiomontanus, etc.)
- [ ] Add latitude guardrails for Placidus/Koch near polar latitudes
- [ ] Compute vertex/east point
- [ ] Ensure MC/ASC correctness across coordinate modes

### Aspect Engine
- [x] Basic major/minor aspect calculation (`aspects_service.py`)
- [ ] Configurable orbs per planet/aspect
- [ ] Moieties
- [ ] Parallels/contra-parallels
- [ ] Applying/separating accuracy using velocities

### Fixed Stars & Lots
- [x] Fixed star proximity checks (`fixed_stars_service.py`)
- [x] Arabic Parts with sect-aware reversal (`arabic_parts_service.py`)
- [ ] Expand star catalog with magnitudes and mythic notes
- [ ] Add parans
- [ ] Extend Arabic Parts catalog and validation

### Interpretation Corpus
- [x] Planet-sign interpretations (partial)
- [x] Planet-house interpretations (partial)
- [ ] Complete triads (planet-sign-house)
- [ ] Aspects directional text
- [ ] Transits to natal narratives
- [ ] Progressions/returns narratives
- [ ] Star and lot delineations
- [ ] Surface weights and source metadata

### Data & Persistence
- [x] Chart storage (`chart_storage_service.py`, `chart_repository.py`)
- [ ] Versioned chart records, delta history
- [ ] Tagging/search facets
- [ ] Export/import flows (JSON/CSV)
- [ ] Cached ephemeris slices for batch runs

### UX/Reporting
- [x] Report service exists (`report_service.py`)
- [ ] PDF/PNG export of charts and reports
- [ ] Printable layouts
- [ ] Keyboard shortcuts
- [ ] Accessibility labeling
- [ ] Responsive redraw on setting changes
- [ ] Status/toast feedback for failures

### Performance & Offline
- [ ] Benchmarks for batch ephemeris generation (Jupiter trial)
- [ ] Optional offline mode with cached ephemeris
- [ ] Background threading for heavy calculations

### Observability & Safety
- [ ] Structured logging (pillar=astrology, chart_type, calculation_mode)
- [ ] Slow-op warnings
- [ ] Graceful fallbacks when ephemeris/geo lookup fails

### Verification
- [ ] Golden-value tests for planetary positions (sample dates)
- [ ] House cusp validations
- [ ] Aspect matrix checks
- [ ] Lots reversal tests
- [ ] Fixed-star proximity tests
- [ ] Performance thresholds
- [ ] UI smoke tests headless where possible

## Phased Roadmap

### Phase 1 — Astrometric Integrity
- [ ] Harden ephemeris/timezone handling
- [ ] Add true/mean node toggle
- [ ] Sidereal/ayanamsa selection
- [ ] Topocentric option
- [ ] Create golden-value tests for planetary positions and house cusps

### Phase 2 — Chart Breadth & Engines (Mostly Complete)
- [x] Solar/lunar returns (`returns_service.py`, `returns_window.py`)
- [x] Secondary progressions (`progressions_service.py`, `progressions_window.py`)
- [x] Synastry/bi-wheel (`synastry_service.py`, `synastry_window.py`)
- [x] Midpoints grid (`midpoints_service.py`, `midpoints_dial.py`)
- [ ] Solar arc directions
- [ ] Composite charts (stub exists)
- [ ] Expanded house systems
- [ ] Aspect engine upgrades (orbs/moieties/parallels)

### Phase 3 — Interpretation & Reporting (Partial)
- [x] Interpretation service and repository exist
- [x] Report service exists (`report_service.py`)
- [ ] Complete interpretation corpus (triads, aspects, transits, progressions, stars, lots)
- [ ] Add report generation (PDF/PNG)
- [ ] Export/import
- [ ] Versioned chart storage with tags

### Phase 4 — UX, Performance, Observability
- [ ] Responsive redraws
- [ ] Keyboard/accessibility
- [ ] Structured logging
- [ ] Slow-op alerts
- [ ] Background workers for heavy ops
- [ ] Caching/offline mode
- [ ] Regression suite for UI flows and performance

## Verification Plan (Seals Focus)
- **Saturn**: Static analysis for sovereignty and import purity; type coverage across services and repositories.
- **Jupiter**: Benchmarks for batch ephemeris generation and chart rendering; guardrail thresholds.
- **Mars**: Fuzzed inputs for dates/locations/timezones; invalid coordinates; missing ephemeris files; ensure graceful errors.
- **Sun/Venus**: Golden-value correctness for planetary positions, houses, aspects, lots; DTO shape consistency for chart and interpretation outputs.
- **Mercury**: Structured logging coverage for every service entry/exit; signal/slot emissions for UI updates.
- **Moon**: Persistence round-trips for chart storage, versioning, and imports/exports.

---

## Future Vision: The Cross-Pillar Interpretation Engine

> *"The whole is greater than the sum of its parts."* — Aristotle

This is the unique offering that no other astrological software can provide: **IsopGem contains multiple esoteric systems** (Gematria, Geometry, Astrology, TQ) that can be *synthesized* into a unified interpretation.

### The Concept

Instead of isolated astrological text, the interpretation engine would weave across pillars:

1. **The Degree as Number**: A planet's degree position has a numerical value. That value has Gematric correspondences (Hebrew letters, Tarot trumps, Kabbalistic paths). Sun at 15° Aries isn't just "mid-Aries"—it's a *Vav degree*, with all the Tiphareth/Lovers resonance that implies.

2. **Aspect Geometry as Sacred Form**: Grand Trines, T-Squares, and Yods are not just aspect patterns—they are *geometric forms*. The Geometry pillar can render them, name their proportions, link them to Platonic solids and sacred ratios.

3. **The Name as Lens**: The user's name (processed via Gematria) produces a numerical signature. The chart is interpreted *through* that signature—two people with the same Sun sign receive different interpretations based on their names.

4. **TQ Integration**: The Quadset of the birth date provides a hidden numerical fingerprint beneath the astrological one. Transits can be interpreted as TQ pattern activations.

### Architectural Implications

- **Shared interpretation service** that queries multiple pillar repositories
- **Correspondence tables** linking degrees ↔ numbers ↔ letters ↔ trumps
- **Dynamic composition** rather than static text storage
- **User profile integration** for personalized synthesis

### Priority: Future (Post-Phase 4)

This feature depends on the maturity of all four pillars. It represents the *culmination* of IsopGem's vision: not four separate tools, but one unified Temple of correspondences.

