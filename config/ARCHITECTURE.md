# IsopGem Architecture

This document describes the domain-pillar architecture of the IsopGem application.

## Five Main Pillars

### 1. Gematria
Hebrew, Greek, and English numerical analysis tools
- **Status**: Active
- **Components**: Hebrew calculator (implemented)

### 2. Geometry
Sacred geometry visualization and calculation tools
- **Status**: Planned
- **Components**: TBD

### 3. Document Manager
Analysis and organization of texts and documents
- **Status**: Planned
- **Components**: TBD

### 4. Astrology
Cosmic calendar and zodiacal mappings
- **Status**: Planned
- **Components**: TBD

### 5. TQ (Trigrammaton QBLH)
Integration and pattern analysis
- **Status**: Planned
- **Components**: TBD

## Component Architecture

Each pillar follows a consistent structure:

```
pillar/
├── ui/              # PyQt6-based interface components
├── services/        # Business logic and core functionality
├── models/          # Data structures and type definitions
├── repositories/    # Data access and persistence
└── utils/           # Helper functions and utilities
```

## Shared Components

The `shared/` directory contains components used across multiple pillars:
- `shared/ui/` - Common UI widgets and dialogs
- `shared/models/` - Shared data models
- `shared/utils/` - General utility functions
