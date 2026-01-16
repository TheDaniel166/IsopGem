# Data Flow Architecture: End-to-End Calculation Journey

<!-- Last Verified: 2026-01-16 -->

<cite>
**Referenced Files in This Document**
- [gematria_calculator_window.py](file://src/pillars/gematria/ui/gematria_calculator_window.py)
- [calculation_service.py](file://src/pillars/gematria/services/calculation_service.py)
- [base_calculator.py](file://src/shared/services/gematria/base_calculator.py)
- [calculation_repository.py](file://src/pillars/gematria/repositories/sqlite_calculation_repository.py)
- [database.py](file://src/shared/database.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Layer Architecture](#layer-architecture)
3. [Calculation Flow](#calculation-flow)
4. [Persistence Flow](#persistence-flow)
5. [Query Flow](#query-flow)
6. [Error Propagation](#error-propagation)
7. [State Management](#state-management)

## Introduction

The Gematria Pillar follows a **layered architecture** with clear separation between presentation (UI), business logic (Services), and data access (Repositories). This document traces the complete journey of data from user input through calculation, persistence, and retrieval.

**Architectural Principles:**
- **Unidirectional Flow**: Data flows downward (UI → Service → Repository)
- **Dependency Injection**: Lower layers don't know about upper layers
- **Immutable Calculations**: Once saved, calculation values never change
- **Signal-Based Updates**: UI updates via observer pattern, not polling

## Layer Architecture

```mermaid
graph TD
    subgraph "Presentation Layer"
        A[GematriaCalculatorWindow]
        B[SavedCalculationsWindow]
        C[BatchCalculatorWindow]
    end
    
    subgraph "Service Layer"
        D[CalculationService]
        E[HebrewCalculator]
        F[GreekCalculator]
        G[TextAnalysisService]
    end
    
    subgraph "Repository Layer"
        H[CalculationRepository]
    end
    
    subgraph "Data Layer"
        I[(SQLite Database)]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    D --> F
    D --> G
    D --> H
    H --> I
    
    style A fill:#9f9,stroke:#333
    style B fill:#9f9,stroke:#333
    style C fill:#9f9,stroke:#333
    style D fill:#f96,stroke:#333
    style E fill:#bbf,stroke:#333
    style F fill:#bbf,stroke:#333
    style G fill:#bbf,stroke:#333
    style H fill:#ff9,stroke:#333
    style I fill:#f9f,stroke:#333
```

### Layer Responsibilities

| Layer | Components | Responsibility |
|-------|------------|----------------|
| **Presentation** | PyQt6 Windows | User interaction, input validation, display |
| **Service** | Calculation/Analysis Services | Business logic, orchestration, validation |
| **Strategy** | Calculator implementations | Algorithm implementations |
| **Repository** | Data access objects | CRUD operations, query building |
| **Data** | SQLite database | Persistent storage |

## Calculation Flow

### Simple Calculation Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as GematriaCalculatorWindow
    participant Service as CalculationService
    participant Calc as HebrewCalculator
    participant Repo as CalculationRepository
    participant DB as SQLite Database
    
    User->>UI: Enter text "שלום"
    User->>UI: Select "Hebrew Standard"
    User->>UI: Click Calculate
    
    UI->>UI: Validate input
    UI->>Calc: __init__() - Create calculator
    Calc->>Calc: _initialize_mapping()
    Calc-->>UI: Calculator instance
    
    UI->>Calc: calculate("שלום")
    Calc->>Calc: normalize_text("שלום")
    Calc->>Calc: Sum letter values
    Calc-->>UI: 376
    
    UI->>Calc: get_breakdown("שלום")
    Calc-->>UI: [('ש',300), ('ל',30), ('ו',6), ('ם',40)]
    
    UI->>UI: Display results
    
    Note over User,UI: User decides to save
    
    User->>UI: Click Save (Ctrl+S)
    UI->>UI: Collect metadata (notes, tags)
    
    UI->>Service: save_calculation(<br/>text="שלום", value=376,<br/>calculator=calc, breakdown=...,<br/>notes="Peace", tags=["virtue"])
    
    Service->>Service: Normalize text via calculator
    Service->>Service: Convert breakdown to JSON
    Service->>Service: Create CalculationRecord
    
    Service->>Repo: save(record)
    Repo->>DB: INSERT INTO gematria_calculations
    DB-->>Repo: Row ID + timestamp
    Repo-->>Service: CalculationRecord with ID
    Service-->>UI: Saved record
    
    UI->>UI: Show success message
    UI->>UI: Add to recent calculations list
    UI-->>User: "Calculation saved successfully"
```

### Multi-Calculator Batch Flow

```mermaid
sequenceDiagram
    actor User
    participant UI as BatchCalculatorWindow
    participant Service as CalculationService
    participant Hebrew as HebrewCalculator
    participant Greek as GreekCalculator
    participant TQ as TQCalculator
    
    User->>UI: Enter text "שלום"
    User->>UI: Select [Hebrew, Greek, TQ]
    User->>UI: Click "Calculate All"
    
    par Hebrew Calculation
        UI->>Hebrew: calculate("שלום")
        Hebrew-->>UI: 376
        UI->>Service: save_calculation(..., calc=Hebrew)
    and Greek Calculation
        UI->>Greek: calculate("שלום")
        Greek-->>UI: 0 (no Greek letters)
        Note over UI: Skip saving (value = 0)
    and TQ Calculation
        UI->>TQ: calculate("שלום")
        TQ-->>UI: 0 (no English letters)
        Note over UI: Skip saving (value = 0)
    end
    
    UI->>UI: Display all results in table
    UI-->>User: Show comparison table
```

## Persistence Flow

### Save Operation Detail

**Input Transformation Pipeline:**

```mermaid
flowchart LR
    A[User Input] --> B[UI Validation]
    B --> C[Service Layer]
    C --> D[Data Normalization]
    D --> E[JSON Serialization]
    E --> F[Record Creation]
    F --> G[Repository Save]
    G --> H[Database INSERT]
    H --> I[Return Saved Record]
```

**Breakdown Serialization:**

```python
# Input from calculator
breakdown = [('ש', 300), ('ל', 30), ('ו', 6), ('ם', 40)]

# Service layer transformation
breakdown_data = [
    {"char": char, "value": val} 
    for char, val in breakdown
]

# JSON encoding
breakdown_json = json.dumps(breakdown_data, ensure_ascii=False)
# Result: '[{"char":"ש","value":300},{"char":"ל","value":30},...]'

# Stored in database
record.breakdown = breakdown_json
```

**Text Normalization:**

```python
# Original text (with diacritics)
original = "בְּרֵאשִׁית"

# Normalized text (diacritics removed)
normalized = calculator.normalize_text(original)
# Result: "בראשית"

# Both stored in record
record.text = "בְּרֵאשִׁית"          # For display
record.normalized_text = "בראשית"     # For calculation/search
```

### Update Operation

```mermaid
sequenceDiagram
    participant UI as SavedCalculationsWindow
    participant Service as CalculationService
    participant Repo as CalculationRepository
    participant DB as Database
    
    UI->>UI: User edits notes field
    UI->>UI: User adds tags
    UI->>UI: User sets rating to 5
    
    UI->>Service: update_calculation(<br/>record_id="abc-123",<br/>notes="Updated notes",<br/>tags=["new", "tags"],<br/>user_rating=5)
    
    Service->>Repo: update(record_id, fields)
    Repo->>DB: UPDATE gematria_calculations<br/>SET notes=?, tags=?, user_rating=?,<br/>updated_at=?<br/>WHERE id=?
    DB-->>Repo: Rows affected
    Repo->>DB: SELECT * FROM...<br/>WHERE id=?
    DB-->>Repo: Updated record
    Repo-->>Service: CalculationRecord
    Service-->>UI: Updated record
    
    UI->>UI: Refresh display
```

## Query Flow

### Search by Value

```mermaid
sequenceDiagram
    participant User
    participant UI as SavedCalculationsWindow
    participant Service as CalculationService
    participant Repo as CalculationRepository
    participant DB as Database
    
    User->>UI: Enter value filter "26"
    User->>UI: Select method "Hebrew Standard"
    User->>UI: Click "Search"
    
    UI->>Service: search(filters={<br/>"value": 26,<br/>"method": "Hebrew Standard"})
    
    Service->>Repo: search(filters, order_by="created_at")
    
    Repo->>DB: SELECT * FROM gematria_calculations<br/>WHERE value = 26<br/>AND method = 'Hebrew Standard'<br/>ORDER BY created_at DESC
    
    DB-->>Repo: Result rows
    Repo->>Repo: Deserialize JSON breakdowns
    Repo->>Repo: Create CalculationRecord objects
    Repo-->>Service: List[CalculationRecord]
    Service-->>UI: Search results
    
    UI->>UI: Populate table widget
    UI->>UI: Update result count
    UI-->>User: Display matches
```

### Complex Query Example

**UI Request:**
```python
filters = {
    "value": 888,
    "tags": ["divine_name"],
    "min_rating": 4,
    "is_favorite": True
}
```

**Repository SQL Translation:**
```sql
SELECT * FROM gematria_calculations
WHERE value = 888
  AND tags LIKE '%"divine_name"%'  -- JSON array search
  AND user_rating >= 4
  AND is_favorite = TRUE
ORDER BY created_at DESC
LIMIT 100
```

## Error Propagation

### Error Handling Strategy

```mermaid
graph TD
    A[User Action] --> B{UI Validation}
    B -->|Invalid| C[Show Error Dialog]
    B -->|Valid| D[Call Service Layer]
    D --> E{Service Validation}
    E -->|Invalid| F[Raise ValueError]
    F --> G[UI Catches Exception]
    G --> C
    E -->|Valid| H[Call Repository]
    H --> I{Database Operation}
    I -->|Error| J[Raise KeyError/DBError]
    J --> K[Service Catches Exception]
    K --> L[Log Error]
    L --> M[Return None or Empty List]
    M --> N[UI Handles Gracefully]
    I -->|Success| O[Return Data]
    O --> P[Display Results]
```

### Error Types by Layer

| Layer | Error Type | Example | Handling |
|-------|------------|---------|----------|
| **UI** | ValidationError | Empty text input | Show inline error message |
| **Service** | ValueError | Invalid rating (>5) | Raise exception to UI |
| **Repository** | KeyError | Record not found | Return None |
| **Database** | sqlite3.Error | Connection failure | Log + retry or fail gracefully |

### Example Error Flow

```python
# UI Layer
try:
    value = int(self.value_input.text())
except ValueError:
    QMessageBox.warning(self, "Invalid Input", "Value must be a number")
    return

# Service Layer
if not (0 <= user_rating <= 5):
    raise ValueError("Rating must be between 0 and 5")

# Repository Layer
try:
    record = self.session.query(CalculationEntity).filter_by(id=record_id).first()
except SQLAlchemyError as e:
    logger.error(f"Database query failed: {e}")
    return None
```

## State Management

### Calculator State

**Calculators are stateless:**
```python
calc = HebrewCalculator()  # Create once
value1 = calc.calculate("שלום")  # 376
value2 = calc.calculate("אהבה")  # 13
# No state persists between calls
```

**Benefit**: Thread-safe, reusable, predictable

### UI State

**Window State Management:**

```mermaid
stateDiagram-v2
    [*] --> Empty: Window Opens
    Empty --> Calculating: User Enters Text
    Calculating --> Results: Calculate Clicked
    Results --> Results: Cipher Changed (recalculate)
    Results --> Saved: Save Clicked
    Saved --> Results: Continue Working
    Results --> Empty: Clear Clicked
    Results --> [*]: Window Closed
```

**State Components:**
- Current text input
- Selected calculators
- Calculation results cache
- Recent calculations list
- UI element visibility flags

### Session State

**Saved Calculations Window:**
```python
class SavedCalculationsWindow:
    def __init__(self):
        self.current_filters = {}
        self.current_sort = "created_at"
        self.selected_records = []
        self.page_offset = 0
        self.page_size = 100
```

**State Persistence:**
- Filters persist during session
- Sort order remembered
- Selection preserved on refresh
- Pagination state maintained

---

**See Also:**
- [strategy_pattern.md](strategy_pattern.md) - Calculator architecture
- [calculation_service.md](../api/calculation_service.md) - Service API
- [../ui_components/calculator_window.md](../ui_components/calculator_window.md) - UI layer

**Revision History:**
- 2026-01-16: Initial data flow documentation with sequence diagrams
