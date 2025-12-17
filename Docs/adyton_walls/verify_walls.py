"""
Wall Value Verification Script

Verifies that all wall CSV values match the pattern defined by:
- wall_conrunepair_pattern.csv (Set # positions)
- zodiacal_heptagon.csv (A/B values per Set #)

The Law:
- Rows 5-8 (top half) → A column value
- Rows 1-4 (bottom half) → B column value
- Wall 1 (Sol) → A1, B1
- Wall 2 (Mercury) → A2, B2
- Wall 3 (Luna) → A3, B3
- Wall 4 (Venus) → A4, B4
- Wall 5 (Jupiter) → A5, B5
- Wall 6 (Mars) → A6, B6
- Wall 7 (Saturn) → A7, B7
"""
import csv
from pathlib import Path
from typing import Dict, List, Tuple

DOCS_ROOT = Path(__file__).parent

WALL_FILES = {
    1: "sun_wall.csv",
    2: "mercury_wall.csv",
    3: "luna_wall.csv",
    4: "venus_wall.csv",
    5: "jupiter_wall.csv",
    6: "mars_wall.csv",
    7: "saturn_wall.csv",
}

def load_pattern() -> Dict[Tuple[int, int], int]:
    """Load the pattern file: returns {(row, col): set_number}"""
    pattern = {}
    path = DOCS_ROOT / "wall_conrunepair_pattern.csv"
    with path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)  # Column headers: empty, 1, 3, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13
        col_indices = [int(c) for c in header[1:]]  # Skip first empty cell
        
        for row_data in reader:
            row_num = int(row_data[0])
            for i, set_num in enumerate(row_data[1:]):
                col_num = col_indices[i]
                pattern[(row_num, col_num)] = int(set_num)
    
    return pattern


def load_zodiacal_heptagon() -> Dict[int, Dict[str, int]]:
    """Load zodiacal heptagon: returns {set_num: {A1: val, B1: val, A2: val, ...}}"""
    heptagon = {}
    path = DOCS_ROOT / "zodiacal_heptagon.csv"
    with path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        
        for row_data in reader:
            set_num = int(row_data[0])
            values = {}
            # Columns: Set #, A1, B1, D1, Zod, Deg, A2, B2, D2, ...
            # A1 at index 1, B1 at index 2
            # A2 at index 6, B2 at index 7
            # Pattern: A at 1 + (wall-1)*5, B at 2 + (wall-1)*5
            for wall in range(1, 8):
                a_idx = 1 + (wall - 1) * 5
                b_idx = 2 + (wall - 1) * 5
                try:
                    values[f"A{wall}"] = int(row_data[a_idx])
                    values[f"B{wall}"] = int(row_data[b_idx])
                except (IndexError, ValueError):
                    pass
            heptagon[set_num] = values
    
    return heptagon


def load_wall_csv(wall_num: int) -> List[List[int]]:
    """Load a wall CSV file: returns list of rows (row 0 = top)"""
    path = DOCS_ROOT / WALL_FILES[wall_num]
    rows = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            cells = [int(c.strip()) for c in line.split(",")]
            rows.append(cells)
    return rows


def derive_wall_value(pattern: Dict, heptagon: Dict, wall_num: int, row: int, col: int) -> int:
    """Derive what the value SHOULD be based on pattern + heptagon.
    
    Diagonal Conrune Pair Placement:
    - Top-left quadrant (rows 1-4, cols 1-6): B column (Night/greater)
    - Top-right quadrant (rows 1-4, cols 8-13): A column (Day/lesser)
    - Center column (col 7): A for top (rows 1-4), B for bottom (rows 5-8)
    - Bottom-left quadrant (rows 5-8, cols 1-6): A column (Day/lesser)
    - Bottom-right quadrant (rows 5-8, cols 8-13): B column (Night/greater)
    """
    set_num = pattern.get((row, col))
    if set_num is None:
        return -1
    
    set_data = heptagon.get(set_num)
    if set_data is None:
        return -1
    
    a_val = set_data.get(f"A{wall_num}", -1)
    b_val = set_data.get(f"B{wall_num}", -1)
    
    if a_val == -1 or b_val == -1:
        return -1
    
    # Diagonal placement logic
    is_top_half = row <= 4
    is_left_half = col <= 6
    is_center = col == 7
    
    if is_center:
        # Center column: A for top, B for bottom
        return a_val if is_top_half else b_val
    elif is_top_half:
        # Top half: B for left, A for right
        return b_val if is_left_half else a_val
    else:
        # Bottom half: A for left, B for right
        return a_val if is_left_half else b_val


def verify_all_walls():
    """Run verification on all walls."""
    print("=" * 60)
    print("ADYTON WALL VALUE VERIFICATION")
    print("=" * 60)
    
    pattern = load_pattern()
    heptagon = load_zodiacal_heptagon()
    
    total_errors = 0
    total_checked = 0
    
    for wall_num in range(1, 8):
        wall_name = WALL_FILES[wall_num].replace("_wall.csv", "").upper()
        print(f"\n--- Wall {wall_num}: {wall_name} ---")
        
        wall_data = load_wall_csv(wall_num)
        errors = []
        
        # Wall CSV row 0 = pattern row 1 (top of wall)
        # Wall CSV row 7 = pattern row 8 (bottom of wall)
        for csv_row_idx, row_values in enumerate(wall_data):
            pattern_row = csv_row_idx + 1  # Pattern rows are 1-indexed
            
            for col_idx, actual_value in enumerate(row_values):
                wall_col = col_idx + 1  # 1-indexed columns
                
                expected = derive_wall_value(pattern, heptagon, wall_num, pattern_row, wall_col)
                total_checked += 1
                
                if expected == -1:
                    errors.append(f"  [?] Row {pattern_row}, Col {wall_col}: No pattern data")
                elif actual_value != expected:
                    errors.append(
                        f"  [X] Row {pattern_row}, Col {wall_col}: "
                        f"Expected {expected}, Got {actual_value}"
                    )
                    total_errors += 1
        
        if errors:
            print(f"  ERRORS FOUND: {len(errors)}")
            for e in errors[:10]:  # Show first 10
                print(e)
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")
        else:
            print(f"  ✓ All {len(wall_data) * 13} values correct!")
    
    print("\n" + "=" * 60)
    print(f"SUMMARY: {total_checked} cells checked, {total_errors} errors found")
    print("=" * 60)
    
    return total_errors == 0


if __name__ == "__main__":
    success = verify_all_walls()
    exit(0 if success else 1)
