# ValidationError API Reference

<!-- Last Verified: 2026-01-16 -->

<cite>
**Referenced Files in This Document**
- [src/pillars/correspondences/services/spreadsheet_validator.py](file://src/pillars/correspondences/services/spreadsheet_validator.py)
- [logging](file://logging)
- [typing](file://typing)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Class Overview](#class-overview)
3. [Core Methods](#core-methods)
4. [Usage Examples](#usage-examples)
5. [Error Handling](#error-handling)
6. [Dependencies](#dependencies)
7. [Performance Considerations](#performance-considerations)

## Introduction

Raised when spreadsheet data fails validation.

**Architectural Role**: [Documentation needed: Define role (Service/Model/View/Repository)]
- **Layer**: [Documentation needed: Which architectural layer]
- **Responsibilities**: - Validate and sanitize spreadsheet data
- **Dependencies**: logging, typing
- **Consumers**: Unknown

## Class Overview

```python
class ValidationError(Exception):
    """Raised when spreadsheet data fails validation."""
```

[Documentation needed: Add class diagram showing relationships]

## Core Methods

## Usage Examples

```python
from pillars.correspondences.services import SpreadsheetValidator

# Create instance
instance = SpreadsheetValidator()

# Use methods
# instance.some_method()
```

## Error Handling

[Documentation needed: Document error types and handling strategies]

## Dependencies

```mermaid
graph LR
    ValidationError --> logging
 --> typing
```

## Performance Considerations

[Documentation needed: Add complexity analysis and optimization notes]

---

**See Also:**
- [../REFERENCE.md](../REFERENCE.md) - Pillar reference
- [Documentation needed: Add related documentation links]

**Revision History:**
- 2026-01-16: Initial auto-generated documentation
