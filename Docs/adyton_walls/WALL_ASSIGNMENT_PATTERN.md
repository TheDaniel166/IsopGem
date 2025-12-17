# Adyton Wall Assignment Pattern

## Overview

The Adyton chamber has 7 walls, each assigned to a planet. Each wall is an 8×13 grid of frustums containing decimal values derived from the **Conrune Pair** system.

## Source Files

| File | Purpose |
|------|---------|
| `wall_conrunepair_pattern.csv` | Set numbers for each (row, col) position |
| `zodiacal_heptagon.csv` | A/B values for each Set (1-52) per wall |
| `*_wall.csv` | Actual decimal values displayed on each wall |

## The Conrune Pair System

A **Conrune** is formed by swapping 1↔2 in the ternary representation of a number.
- **A value** = Day Hexagram (lesser value)
- **B value** = Night Hexagram (greater value)
- **D value** = Differential (B - A)

Each Set (1-52) provides an A/B pair for each of the 7 walls via columns A1-A7 and B1-B7.

## Wall Assignment Rules

### Pattern File Structure

The pattern file maps (row, col) → Set number:
```
     1   2   3   4   5   6   7   8   9  10  11  12  13
1   46  47  48  49  50  51  52  40  41  42  43  44  45
2   33  34  35  36  37  38  39  27  28  29  30  31  32
3    7   8   9  10  11  12  13   1   2   3   4   5   6
4   20  21  22  23  24  25  26  14  15  16  17  18  19
5   19  18  17  16  15  14  26  25  24  23  22  21  20
6    6   5   4   3   2   1  13  12  11  10   9   8   7
7   32  31  30  29  28  27  39  38  37  36  35  34  33
8   45  44  43  42  41  40  52  51  50  49  48  47  46
```

### Mirror Symmetry

Each row pair is a mirror of each other:
- Row 1 ↔ Row 8 (reversed)
- Row 2 ↔ Row 7 (reversed)
- Row 3 ↔ Row 6 (reversed)
- Row 4 ↔ Row 5 (reversed)

### A/B Value Assignment (Verified ✓)

Each cell in the wall uses either the **A** (Day/lesser) or **B** (Night/greater) value from its Set:

| Region | Columns | Value Used |
|--------|---------|------------|
| **Left half** | 1-6 | **B** (Night/greater) |
| **Center** | 7 | **A** for rows 1-4, **B** for rows 5-8 |
| **Right half** | 8-13 | **A** (Day/lesser) |

This creates a diagonal pattern where conrune pairs (A and B from the same Set) appear at symmetrical positions on the wall.

## Verification Status

> [!NOTE]
> All 7 walls verified to match the pattern file + zodiacal_heptagon derivation.

- Wall 1 (Sun): ✓ 8/8 rows match
- Wall 2 (Mercury): ✓ 8/8 rows match
- Wall 3 (Luna): ✓ 8/8 rows match
- Wall 4 (Venus): ✓ 8/8 rows match
- Wall 5 (Jupiter): ✓ 8/8 rows match
- Wall 6 (Mars): ✓ 8/8 rows match
- Wall 7 (Saturn): ✓ 8/8 rows match

## Wall Generation Logic

```python
def get_wall_value(wall_num: int, row: int, col: int) -> int:
    set_num = pattern[(row, col)]  # From wall_conrunepair_pattern.csv
    a_val = heptagon[set_num][f"A{wall_num}"]
    b_val = heptagon[set_num][f"B{wall_num}"]
    
    if col <= 6:
        return b_val  # Left half: always B
    elif col == 7:
        return a_val if row <= 4 else b_val  # Center: A top, B bottom
    else:
        return a_val  # Right half: always A
```

## Verification Script

Located at: `Docs/adyton_walls/verify_walls.py`

Run with:
```bash
python Docs/adyton_walls/verify_walls.py
```
