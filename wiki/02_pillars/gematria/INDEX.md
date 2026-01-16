# Gematria Pillar Documentation Index

<!-- Last Verified: 2026-01-16 -->

**"The Universe is written in the Language of Number. We translate the Shadow back into the Light."**

This index provides a comprehensive map of the Gematria Pillar documentation, combining the **Covenant-aligned core documents** with **detailed technical reference materials** in the repowiki style.

---

## Quick Navigation

### Core Documents (Covenant Style)
These are the primary architectural and usage documents following the Diátaxis pattern:

- **[REFERENCE.md](REFERENCE.md)** - Technical anatomy and cipher reference
- **[EXPLANATION.md](EXPLANATION.md)** - Theoretical foundations and architectural philosophy
- **[GUIDES.md](GUIDES.md)** - Practical how-to guides and workflows

---

## Deep Documentation Structure

### Architecture

Comprehensive architectural patterns and design decisions:

- **[strategy_pattern.md](architecture/strategy_pattern.md)** - Calculator Strategy Pattern
  - Abstract base class design
  - Concrete calculator implementations
  - Extension points and lifecycle
  - Performance characteristics
  
- **[data_flow.md](architecture/data_flow.md)** - End-to-End Data Flow
  - Layer architecture
  - Calculation sequence diagrams
  - Persistence and query flows
  - Error propagation
  - State management

### API Reference

Detailed API documentation for each service component:

- **[calculation_service.md](api/calculation_service.md)** - Calculation Service API
  - `save_calculation()` - Persist calculations
  - `update_calculation()` - Update metadata
  - `search()` - Query saved calculations
  - Data model and schemas
  - Usage examples and error handling

- **[text_analysis_service.md](api/text_analysis_service.md)** - Text Analysis Service (Fast Scan)
  - `find_value_matches()` - Substring matching algorithm
  - Sliding window optimization
  - Performance analysis and benchmarks
  - Integration with document analysis

**To Be Added:**
- `smart_filter_service.md` - NLP-based result filtering
- `els_service.md` - Equidistant Letter Sequence detection
- `acrostic_service.md` - Hidden message discovery
- `batch_io_service.md` - Bulk import/export operations
- `repository_api.md` - Database persistence layer
- `calculator_implementations.md` - Individual calculator details

### Features

Feature-specific documentation for major components:

- **[holy_book_teacher.md](features/holy_book_teacher.md)** - Holy Book Teacher Mode
  - Curated verse analysis
  - Rule-based verse selection
  - Teaching annotations system
  - Integration with Document Manager
  - Extension points for custom rules

**To Be Added:**
- `els_search.md` - ELS Grid Search feature
- `batch_calculator.md` - Great Harvest (batch calculation)
- `saved_calculations.md` - Calculation history management
- `text_analysis_window.md` - Exegesis Window (verse analysis)
- `methods_reference.md` - Cipher reference window
- `acrostics_analysis.md` - Acrostic discovery tool
- `chiastic_structures.md` - Chiasmus detection

### UI Components

User interface architecture and implementation:

**To Be Added:**
- `gematria_hub.md` - Main pillar hub interface
- `calculator_window.md` - Interactive calculator window
- `results_display.md` - Results table and breakdown views
- `cipher_selection.md` - Multi-cipher selection dialogs
- `highlighting_system.md` - Text highlighting engine
- `keyboard_shortcuts.md` - Keyboard interaction patterns

---

## Documentation Status

### Complete ✓
- Architecture overview (strategy pattern, data flow)
- Core API reference (calculation service, text analysis)
- Feature documentation (holy book teacher)

### In Progress 🔄
- Additional API references (planned)
- Feature-specific guides (planned)
- UI component details (planned)

### Planned 📋
- Performance profiling guide
- Testing strategy documentation
- Troubleshooting and debugging guide
- Migration guide (for new calculator types)
- Integration patterns with other pillars

---

## Document Types Explained

### Covenant Documents (REFERENCE, EXPLANATION, GUIDES)
**Purpose**: High-level architectural understanding and practical usage
**Audience**: Developers new to the pillar, architectural decision-makers
**Style**: Esoteric, poetic, Covenant-aligned voice
**Length**: Concise (50-150 lines)

### Architecture Documents
**Purpose**: Deep architectural patterns and design rationale
**Audience**: Developers implementing features or refactoring
**Style**: Technical with mystical terminology
**Length**: Comprehensive (200-400 lines)
**Includes**: Mermaid diagrams, sequence flows, class diagrams

### API Reference Documents
**Purpose**: Exhaustive method documentation and usage patterns
**Audience**: Developers calling APIs, AI assistants
**Style**: Technical reference with examples
**Length**: Detailed (300-600 lines)
**Includes**: Signatures, parameters, return types, examples, error handling

### Feature Documents
**Purpose**: Complete feature specification and usage
**Audience**: Feature developers, QA, technical writers
**Style**: User-journey focused with technical depth
**Length**: Feature-dependent (200-500 lines)
**Includes**: User workflows, integration points, extension patterns

### UI Component Documents
**Purpose**: UI implementation details and interaction patterns
**Audience**: UI developers, UX designers
**Style**: Visual and interaction-focused
**Length**: Component-dependent (150-400 lines)
**Includes**: Screenshots, state diagrams, event flows

---

## Reading Paths

### For New Developers
1. [EXPLANATION.md](EXPLANATION.md) - Understand the "why"
2. [architecture/strategy_pattern.md](architecture/strategy_pattern.md) - Grasp core design
3. [GUIDES.md](GUIDES.md) - Learn basic operations
4. [api/calculation_service.md](api/calculation_service.md) - Deep dive into API

### For Feature Implementation
1. [REFERENCE.md](REFERENCE.md) - Quick component lookup
2. [architecture/data_flow.md](architecture/data_flow.md) - Understand integration
3. Relevant `features/*.md` - See existing patterns
4. Relevant `api/*.md` - API contracts

### For Debugging
1. [architecture/data_flow.md](architecture/data_flow.md) - Trace execution path
2. Relevant `api/*.md` - Check method signatures
3. Error handling sections in API docs

### For AI Assistants
1. [REFERENCE.md](REFERENCE.md) - Component inventory
2. `api/*.md` - Complete API surface
3. `architecture/*.md` - Design constraints
4. `features/*.md` - Integration patterns

---

## Cross-References to Other Pillars

### Document Manager Integration
- Verse storage and retrieval
- Full-text search integration
- Holy Book Teacher data source
- See: `wiki/02_pillars/document_manager/`

### Shared Substrate
- Calculator base classes: `src/shared/services/gematria/`
- Language detection utilities
- Multi-language calculator orchestration
- See: `wiki/02_pillars/shared/`

### Time Mechanics Integration
- Thelemic Calendar gematria analysis
- Date-based verse selection
- See: `wiki/02_pillars/time_mechanics/`

---

## Contributing to This Documentation

### Adding New Documents

**For Architecture Documents:**
1. Follow the template in existing `architecture/*.md` files
2. Include: Introduction, Pattern Overview, Implementation Details, Trade-offs
3. Use Mermaid diagrams for visual clarity
4. Add entry to this index

**For API Documents:**
1. Use the structure from `api/calculation_service.md` as template
2. Include: Class overview, method signatures, examples, error handling
3. Document all public methods
4. Add usage examples for each method

**For Feature Documents:**
1. Follow pattern in `features/holy_book_teacher.md`
2. Include: User workflow, architecture, integration points, examples
3. Add screenshots or UI mockups if available
4. Document extension points

### Maintaining Documentation

- Update "Last Verified" date when reviewing
- Keep examples runnable and tested
- Update cross-references when files move
- Run `verify_manifest.py` after changes
- Follow Covenant naming conventions

### Style Guidelines

**Voice:**
- Architecture docs: Technical with mystical terminology
- API docs: Precise, neutral technical language
- Feature docs: User-journey focused
- Maintain consistency with Covenant glossary

**Formatting:**
- Use `<cite>` blocks for file references
- Include Mermaid diagrams for flows
- Use tables for structured data
- Code examples should be complete and runnable

---

## Covenant Integration

This documentation structure maintains **dual inscription**:

1. **Covenant Core** (`REFERENCE.md`, `EXPLANATION.md`, `GUIDES.md`)
   - Stable, mystical, architectural
   - Updated per Covenant rituals
   - Source of truth for "why" and "what"

2. **Technical Reference** (`api/`, `architecture/`, `features/`)
   - Detailed, exhaustive, LLM-optimized
   - Updated with code changes
   - Source of truth for "how" and implementation details

Both layers are **complementary**, not redundant. The core provides philosophical grounding; the reference tree provides implementation precision.

---

**Last Updated**: 2026-01-16
**Documentation Version**: 1.0.0
**Gematria Pillar Version**: See `CHANGELOG.md`

---

**Navigation:**
- [← Back to Grimoires Index](../README.md)
- [→ Astrology Pillar Documentation](../astrology/INDEX.md)
- [↑ Foundations](../../00_foundations/README.md)
