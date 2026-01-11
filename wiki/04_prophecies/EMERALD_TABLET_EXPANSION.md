# The Rite of Expansion: Emerald Tablet Capabilities

**Created:** 2026-01-10
**Status:** Planned
**Priority:** Medium (after Purification)
**Pillar:** Correspondences (Emerald Tablet)

> *"The Grid reflects the Universe. Let us teach it to see more stars."*

---

## Overview

This scroll documents the **feature expansions** planned for the Emerald Tablet (Spreadsheet). Features are organized into three tiers based on implementation complexity and strategic value.

**Prerequisites:** Complete the [Purification Rite](./EMERALD_TABLET_PURIFICATION.md) before beginning expansion work.

---

## Tier 1: Foundation Functions

**Effort:** 2-4 hours total
**Risk:** Low (additive changes only)

### 1.1 Lookup Functions

Essential for any serious spreadsheet work.

| Function | Syntax | Description |
|----------|--------|-------------|
| `VLOOKUP` | `VLOOKUP(value, range, col_index, [exact])` | Vertical lookup |
| `HLOOKUP` | `HLOOKUP(value, range, row_index, [exact])` | Horizontal lookup |
| `INDEX` | `INDEX(range, row, col)` | Return value at position |
| `MATCH` | `MATCH(value, range, [match_type])` | Find position of value |

**Implementation Location:** `src/pillars/correspondences/services/formula_engine.py`

```python
@FormulaRegistry.register(
    "VLOOKUP", 
    "Vertical lookup in first column of range", 
    "VLOOKUP(value, range, col_index, [exact])", 
    "Lookup",
    [
        ArgumentMetadata("lookup_value", "Value to find", "any"),
        ArgumentMetadata("table_array", "Range to search", "range"),
        ArgumentMetadata("col_index", "Column to return (1-based)", "number"),
        ArgumentMetadata("exact_match", "TRUE for exact, FALSE for approximate", "bool", True)
    ]
)
def func_vlookup(engine: FormulaEngine, value, table_range, col_idx, exact=True):
    """
    Search for value in first column of range, return value from specified column.
    """
    if not isinstance(table_range, list) or not table_range:
        return "#VALUE!"
    
    col_idx = int(col_idx)
    if col_idx < 1:
        return "#VALUE!"
    
    # Determine dimensions (assume rectangular range)
    # table_range is flat list from _resolve_range_values
    # We need to know the original dimensions
    # This requires enhancement to range resolution...
    
    # For now, return placeholder
    return "#NOT_IMPL"


@FormulaRegistry.register(
    "INDEX", 
    "Return value at row/column position in range", 
    "INDEX(range, row, [col])", 
    "Lookup",
    [
        ArgumentMetadata("array", "Range", "range"),
        ArgumentMetadata("row_num", "Row number (1-based)", "number"),
        ArgumentMetadata("col_num", "Column number (1-based)", "number", True)
    ]
)
def func_index(engine: FormulaEngine, array, row_num, col_num=1):
    """Return value at specified position in array."""
    if not isinstance(array, list):
        return "#VALUE!"
    
    row_idx = int(row_num) - 1
    col_idx = int(col_num) - 1 if col_num else 0
    
    # Flat list: need dimensions passed or stored
    # Simplified: assume 1D for now
    if row_idx < 0 or row_idx >= len(array):
        return "#REF!"
    
    return array[row_idx]


@FormulaRegistry.register(
    "MATCH", 
    "Find position of value in range", 
    "MATCH(value, range, [match_type])", 
    "Lookup",
    [
        ArgumentMetadata("lookup_value", "Value to find", "any"),
        ArgumentMetadata("lookup_array", "Range to search", "range"),
        ArgumentMetadata("match_type", "1=less than, 0=exact, -1=greater than", "number", True)
    ]
)
def func_match(engine: FormulaEngine, value, array, match_type=1):
    """Find position of value in array."""
    if not isinstance(array, list):
        return "#VALUE!"
    
    match_type = int(match_type) if match_type is not None else 1
    
    for i, item in enumerate(array):
        if match_type == 0:  # Exact match
            if str(item) == str(value):
                return i + 1  # 1-based
        # TODO: Implement approximate matching
    
    return "#N/A"
```

**Note:** Full VLOOKUP/HLOOKUP implementation requires enhancing `_resolve_range_values` to return structured data with dimensions, not just a flat list.

---

### 1.2 Statistical Functions

| Function | Syntax | Description |
|----------|--------|-------------|
| `COUNTA` | `COUNTA(range)` | Count non-empty cells |
| `COUNTIF` | `COUNTIF(range, criteria)` | Count cells matching criteria |
| `SUMIF` | `SUMIF(range, criteria, [sum_range])` | Sum cells matching criteria |
| `AVERAGEIF` | `AVERAGEIF(range, criteria, [avg_range])` | Average cells matching criteria |

```python
@FormulaRegistry.register("COUNTA", "Count non-empty cells", "COUNTA(range)", "Stats", 
    [ArgumentMetadata("range", "Range to count", "range")], is_variadic=True)
def func_counta(engine: FormulaEngine, *args):
    """Count non-empty cells."""
    count = 0
    def check(item):
        nonlocal count
        if isinstance(item, list):
            for i in item:
                check(i)
        elif item is not None and str(item).strip() != "":
            count += 1
    for a in args:
        check(a)
    return count


@FormulaRegistry.register("COUNTIF", "Count cells matching criteria", "COUNTIF(range, criteria)", "Stats",
    [
        ArgumentMetadata("range", "Range to evaluate", "range"),
        ArgumentMetadata("criteria", "Condition (e.g., '>5', 'text')", "str")
    ])
def func_countif(engine: FormulaEngine, array, criteria):
    """Count cells matching criteria."""
    if not isinstance(array, list):
        return 0
    
    criteria_str = str(criteria)
    count = 0
    
    for item in array:
        if _matches_criteria(item, criteria_str):
            count += 1
    
    return count


def _matches_criteria(value, criteria: str) -> bool:
    """Check if value matches criteria string (e.g., '>5', '<=10', 'text')."""
    criteria = criteria.strip()
    
    # Comparison operators
    if criteria.startswith(">="):
        try:
            return float(value) >= float(criteria[2:])
        except (TypeError, ValueError):
            return False
    elif criteria.startswith("<="):
        try:
            return float(value) <= float(criteria[2:])
        except (TypeError, ValueError):
            return False
    elif criteria.startswith("<>"):
        return str(value) != criteria[2:]
    elif criteria.startswith(">"):
        try:
            return float(value) > float(criteria[1:])
        except (TypeError, ValueError):
            return False
    elif criteria.startswith("<"):
        try:
            return float(value) < float(criteria[1:])
        except (TypeError, ValueError):
            return False
    elif criteria.startswith("="):
        return str(value) == criteria[1:]
    else:
        # Exact match (case-insensitive for text)
        return str(value).lower() == criteria.lower()
```

---

### 1.3 Date/Time Functions

| Function | Syntax | Description |
|----------|--------|-------------|
| `NOW` | `NOW()` | Current date and time |
| `TODAY` | `TODAY()` | Current date |
| `YEAR` | `YEAR(date)` | Extract year |
| `MONTH` | `MONTH(date)` | Extract month |
| `DAY` | `DAY(date)` | Extract day |

```python
from datetime import datetime, date

@FormulaRegistry.register("NOW", "Current date and time", "NOW()", "DateTime", [])
def func_now(engine: FormulaEngine):
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@FormulaRegistry.register("TODAY", "Current date", "TODAY()", "DateTime", [])
def func_today(engine: FormulaEngine):
    return date.today().strftime("%Y-%m-%d")

@FormulaRegistry.register("YEAR", "Extract year from date", "YEAR(date)", "DateTime",
    [ArgumentMetadata("date", "Date string", "str")])
def func_year(engine: FormulaEngine, date_val):
    try:
        dt = datetime.fromisoformat(str(date_val)[:10])
        return dt.year
    except (TypeError, ValueError):
        return "#VALUE!"
```

---

### 1.4 Text Functions

| Function | Syntax | Description |
|----------|--------|-------------|
| `REPT` | `REPT(text, times)` | Repeat text |
| `CHAR` | `CHAR(code)` | Character from Unicode |
| `CODE` | `CODE(char)` | Unicode from character |
| `FIND` | `FIND(find_text, within_text, [start])` | Find substring position |
| `SEARCH` | `SEARCH(find_text, within_text, [start])` | Case-insensitive find |

```python
@FormulaRegistry.register("REPT", "Repeat text", "REPT(text, times)", "Text",
    [
        ArgumentMetadata("text", "Text to repeat", "str"),
        ArgumentMetadata("times", "Number of repetitions", "number")
    ])
def func_rept(engine: FormulaEngine, text, times):
    try:
        return str(text) * int(times)
    except (TypeError, ValueError):
        return "#VALUE!"

@FormulaRegistry.register("CHAR", "Character from code", "CHAR(code)", "Text",
    [ArgumentMetadata("code", "Unicode code point", "number")])
def func_char(engine: FormulaEngine, code):
    try:
        return chr(int(code))
    except (TypeError, ValueError):
        return "#VALUE!"

@FormulaRegistry.register("CODE", "Code from character", "CODE(char)", "Text",
    [ArgumentMetadata("char", "Character", "str")])
def func_code(engine: FormulaEngine, char):
    s = str(char)
    return ord(s[0]) if s else "#VALUE!"
```

---

## Tier 2: Esoteric Integration

**Effort:** 4-6 hours total
**Risk:** Low-Medium (requires service integration)

### 2.1 Cross-Pillar Formulas

Expose the Temple's esoteric services to the spreadsheet.

| Function | Source | Syntax | Returns |
|----------|--------|--------|---------|
| `TAROT` | OpenOccult | `TAROT(card)` | Card meaning |
| `RUNE` | OpenOccult | `RUNE(name)` | Rune interpretation |
| `CRYSTAL` | OpenOccult | `CRYSTAL(name)` | Crystal properties |
| `BOTANICAL` | OpenOccult | `BOTANICAL(plant)` | Plant magical properties |
| `ETYMOLOGY` | Lexicon | `ETYMOLOGY(word)` | Word origin |
| `STRONGS` | Classical | `STRONGS(number)` | Strong's definition |
| `THEOSOPHICAL` | Glossary | `THEOSOPHICAL(term)` | Theosophical definition |

**Implementation:**

```python
@FormulaRegistry.register(
    "TAROT", 
    "Tarot card interpretation from OpenOccult", 
    "TAROT(card_name)", 
    "Esoteric",
    [ArgumentMetadata("card", "Card name (e.g., 'The Fool', 'Ace of Wands')", "str")]
)
def func_tarot(engine: FormulaEngine, card: str):
    """Retrieve Tarot card meaning."""
    try:
        from shared.services.lexicon.occult_reference_service import OccultReferenceService
        svc = OccultReferenceService()
        refs = svc.lookup_tarot(str(card))
        if refs:
            return refs[0].definition[:200]  # Truncate for cell display
        return "#NOT_FOUND"
    except ImportError:
        return "#SERVICE_UNAVAILABLE"
    except Exception as e:
        return f"#ERR: {str(e)[:20]}"


@FormulaRegistry.register(
    "RUNE", 
    "Elder Futhark rune meaning from OpenOccult", 
    "RUNE(name)", 
    "Esoteric",
    [ArgumentMetadata("name", "Rune name (e.g., 'Fehu', 'Uruz')", "str")]
)
def func_rune(engine: FormulaEngine, name: str):
    """Retrieve rune interpretation."""
    try:
        from shared.services.lexicon.occult_reference_service import OccultReferenceService
        svc = OccultReferenceService()
        refs = svc.lookup_rune(str(name))
        if refs:
            return refs[0].definition[:200]
        return "#NOT_FOUND"
    except ImportError:
        return "#SERVICE_UNAVAILABLE"
    except Exception as e:
        return f"#ERR: {str(e)[:20]}"


@FormulaRegistry.register(
    "CRYSTAL", 
    "Crystal/stone properties from OpenOccult", 
    "CRYSTAL(name)", 
    "Esoteric",
    [ArgumentMetadata("name", "Crystal name (e.g., 'Amethyst', 'Obsidian')", "str")]
)
def func_crystal(engine: FormulaEngine, name: str):
    """Retrieve crystal magical properties."""
    try:
        from shared.services.lexicon.occult_reference_service import OccultReferenceService
        svc = OccultReferenceService()
        refs = svc.lookup_crystal(str(name))
        if refs:
            return refs[0].definition[:200]
        return "#NOT_FOUND"
    except ImportError:
        return "#SERVICE_UNAVAILABLE"
    except Exception as e:
        return f"#ERR: {str(e)[:20]}"


@FormulaRegistry.register(
    "ETYMOLOGY", 
    "Word origin and etymology", 
    "ETYMOLOGY(word)", 
    "Esoteric",
    [ArgumentMetadata("word", "Word to research", "str")]
)
def func_etymology(engine: FormulaEngine, word: str):
    """Retrieve word etymology."""
    try:
        from shared.services.lexicon.etymology_db_service import EtymologyDbService
        svc = EtymologyDbService()
        relations = svc.get_etymology(str(word))
        if relations:
            return relations[0].to_string()[:200]
        return "#NOT_FOUND"
    except ImportError:
        return "#SERVICE_UNAVAILABLE"
    except Exception as e:
        return f"#ERR: {str(e)[:20]}"


@FormulaRegistry.register(
    "THEOSOPHICAL", 
    "Theosophical glossary definition", 
    "THEOSOPHICAL(term)", 
    "Esoteric",
    [ArgumentMetadata("term", "Theosophical term", "str")]
)
def func_theosophical(engine: FormulaEngine, term: str):
    """Retrieve Theosophical glossary entry."""
    try:
        from shared.services.lexicon.theosophical_service import TheosophicalGlossaryService
        svc = TheosophicalGlossaryService()
        entry = svc.lookup(str(term))
        if entry:
            return entry.definition[:200]
        return "#NOT_FOUND"
    except ImportError:
        return "#SERVICE_UNAVAILABLE"
    except Exception as e:
        return f"#ERR: {str(e)[:20]}"
```

---

### 2.2 Gematria Heatmap

**Location:** Conditional Formatting extension

Add specialized Gematria-aware conditional formatting rules:

| Rule Type | Description |
|-----------|-------------|
| `GEMATRIA_GRADIENT` | Color gradient based on Gematria value magnitude |
| `GEMATRIA_MATCH` | Highlight cells with matching Gematria value |
| `GEMATRIA_TARGET` | Highlight cells with specific Gematria (e.g., 93, 418) |

**Implementation in `conditional_formatting.py`:**

```python
class GematriaRule(ConditionalRule):
    """Conditional formatting based on Gematria values."""
    
    def __init__(self, rule_type: str, cipher: str = "ENGLISH (TQ)", 
                 target_value: int = None, gradient_max: int = 1000):
        self.cipher = cipher
        self.target_value = target_value
        self.gradient_max = gradient_max
        super().__init__(rule_type, str(target_value), {}, [])
    
    def evaluate(self, value) -> dict:
        """Return style dict based on Gematria evaluation."""
        from pillars.correspondences.services.formula_engine import _CIPHER_REGISTRY
        
        calculator = _CIPHER_REGISTRY.get(self.cipher.upper())
        if not calculator:
            return {}
        
        gem_value = calculator.calculate(str(value))
        
        if self.rule_type == "GEMATRIA_TARGET":
            if gem_value == self.target_value:
                return {"bg": "#FFD700", "fg": "#000000"}  # Gold highlight
        
        elif self.rule_type == "GEMATRIA_GRADIENT":
            # Map value to color intensity
            intensity = min(gem_value / self.gradient_max, 1.0)
            r = int(255 * intensity)
            return {"bg": f"#{r:02x}4040"}
        
        return {}
```

---

### 2.3 Kamea Integration

| Function | Syntax | Description |
|----------|--------|-------------|
| `KAMEA` | `KAMEA(planet, row, col)` | Magic square cell value |
| `KAMEA_SUM` | `KAMEA_SUM(planet)` | Magic constant of square |
| `KAMEA_SIZE` | `KAMEA_SIZE(planet)` | Dimension of square |

```python
# Planetary Kamea definitions
PLANETARY_KAMEA = {
    "SATURN": [[4,9,2],[3,5,7],[8,1,6]],
    "JUPITER": [[4,14,15,1],[9,7,6,12],[5,11,10,8],[16,2,3,13]],
    "MARS": [[11,24,7,20,3],[4,12,25,8,16],[17,5,13,21,9],[10,18,1,14,22],[23,6,19,2,15]],
    # ... etc
}

@FormulaRegistry.register("KAMEA", "Planetary magic square value", "KAMEA(planet, row, col)", "Esoteric",
    [
        ArgumentMetadata("planet", "Planet name", "str"),
        ArgumentMetadata("row", "Row (1-based)", "number"),
        ArgumentMetadata("col", "Column (1-based)", "number")
    ])
def func_kamea(engine: FormulaEngine, planet: str, row, col):
    """Return value from planetary Kamea."""
    kamea = PLANETARY_KAMEA.get(str(planet).upper())
    if not kamea:
        return "#PLANET?"
    
    r, c = int(row) - 1, int(col) - 1
    if 0 <= r < len(kamea) and 0 <= c < len(kamea[0]):
        return kamea[r][c]
    return "#REF!"
```

---

## Tier 3: Structural Enhancements

**Effort:** 6-10 hours total
**Risk:** Medium-High (parser/model changes)

### 3.1 Named Ranges

Allow defining named ranges for cleaner formulas.

**Storage:** Add to scroll JSON:
```json
{
  "scrolls": [...],
  "named_ranges": {
    "Planets": "A1:A10",
    "Values": "B1:B10"
  }
}
```

**Parser Enhancement:**
```python
def atom(self):
    # ... existing code ...
    elif token.type == TokenType.ID:
        name = token.value
        self.eat(TokenType.ID)
        
        # Check for named range BEFORE function call
        if hasattr(self.engine, 'named_ranges'):
            range_str = self.engine.named_ranges.get(name.upper())
            if range_str:
                # Parse and resolve the range
                return self.engine._resolve_named_range(range_str)
        
        # ... existing function call logic ...
```

---

### 3.2 Cross-Sheet References

Enable referencing cells in other sheets.

**Syntax:** `=Sheet2!A1` or `='Sheet Name'!A1:B10`

**Parser Enhancement:**
- Detect `!` token after ID
- Resolve sheet by name from parent model list
- Delegate evaluation to target model

```python
# In Parser.atom(), after ID token:
if self.current_token.type == TokenType.OP and self.current_token.value == '!':
    sheet_name = name
    self.eat(TokenType.OP)  # !
    
    # Next should be cell reference
    cell_ref = self.current_token.value
    self.eat(TokenType.ID)
    
    return self.engine._resolve_cross_sheet_ref(sheet_name, cell_ref)
```

---

### 3.3 Number Formatting

Display formatted numbers without changing underlying data.

**Storage:** Add `format_type` to cell styles:
```python
_styles[(row, col)] = {
    "bg": "#ffffff",
    "format": "currency"  # or "percent", "date", "scientific"
}
```

**Display Logic in `data()` method:**
```python
if role == Qt.ItemDataRole.DisplayRole:
    value = self.evaluate_cell(row, col)
    style = self._styles.get((row, col), {})
    format_type = style.get("format")
    
    if format_type == "currency":
        try:
            return f"${float(value):,.2f}"
        except:
            pass
    elif format_type == "percent":
        try:
            return f"{float(value) * 100:.1f}%"
        except:
            pass
    
    return value
```

---

### 3.4 Format Painter

**UI Addition:** Toolbar button to copy formatting.

**State Machine:**
1. Click "Format Painter" → enters copy mode
2. Click source cell → captures style
3. Click/drag target cells → applies style
4. Exit mode

**Implementation in `style_handler.py`:**
```python
class StyleHandler:
    def __init__(self, window):
        self.window = window
        self._format_painter_active = False
        self._copied_style = None
    
    def activate_format_painter(self):
        self._format_painter_active = True
        self.window.view.setCursor(Qt.CursorShape.CrossCursor)
    
    def on_cell_click_for_format(self, index):
        if not self._format_painter_active:
            return False
        
        if self._copied_style is None:
            # First click: copy
            self._copied_style = self.window.model._styles.get(
                (index.row(), index.column()), {}
            ).copy()
        else:
            # Subsequent clicks: paste
            self._apply_style_to_selection(self._copied_style)
            self._format_painter_active = False
            self._copied_style = None
            self.window.view.setCursor(Qt.CursorShape.ArrowCursor)
        
        return True
```

---

## Implementation Priority

| Phase | Features | Est. Time | Value |
|-------|----------|-----------|-------|
| **Expansion 1** | COUNTA, COUNTIF, SUMIF, NOW, TODAY | 2 hours | High |
| **Expansion 2** | TAROT, RUNE, CRYSTAL, ETYMOLOGY | 3 hours | **Unique** |
| **Expansion 3** | INDEX, MATCH (simplified) | 2 hours | High |
| **Expansion 4** | Number Formatting | 2 hours | Medium |
| **Expansion 5** | Gematria Heatmap | 3 hours | **Unique** |
| **Expansion 6** | Named Ranges | 4 hours | Medium |
| **Expansion 7** | Cross-Sheet References | 4 hours | Medium |
| **Expansion 8** | VLOOKUP, HLOOKUP (full) | 4 hours | High |

---

## Verification Requirements

Each expansion phase should include:

1. **Unit tests** for new functions
2. **Formula Wizard** metadata registration
3. **Documentation** in `wiki/02_pillars/emerald_tablet/GUIDES.md`
4. **Verification script** entry in `verification_seal.py`

---

## Dependencies

- **Expansion 2 (Esoteric Functions)** requires `OccultReferenceService` data files in `data/openoccult/`
- **Expansion 5 (Gematria Heatmap)** requires existing Gematria calculators
- **Expansion 6-7 (Named Ranges, Cross-Sheet)** requires parser modifications

---

## Post-Expansion

After completing these expansions, the Emerald Tablet will support:
- Standard spreadsheet workflows (lookup, statistics, dates)
- **Unique esoteric research** (Tarot, Runes, Etymology, Gematria visualization)
- Professional formatting and organization
- Cross-referencing across sheets

The Grid shall truly reflect the Universe.
