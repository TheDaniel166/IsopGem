---
description: Automated Pylance type error analysis and fixes
---

# The Rite of Pylance Satisfaction

This workflow provides automated tools to analyze and fix Pylance type errors.

## Phase 1: Diagnosis

Analyze type errors for a specific pillar or the entire codebase:

```bash
# Analyze a specific pillar
python3 scripts/covenant_scripts/satisfy_pylance.py --pillar adyton --threshold 20

# Analyze entire src/
python3 scripts/covenant_scripts/satisfy_pylance.py --threshold 30

# Analyze with lower threshold (more files shown)
python3 scripts/covenant_scripts/satisfy_pylance.py --pillar gematria --threshold 5
```

**Output**: Error statistics, file rankings, and fixable error counts.

## Phase 2: Automated Fixes (Dry Run)

Preview what fixes would be applied:

```bash
# Preview fixes for a pillar (both strategies)
python3 scripts/covenant_scripts/apply_type_fixes.py --pillar adyton --strategy both --min-errors 20

# Preview only type: ignore comments
python3 scripts/covenant_scripts/apply_type_fixes.py --pillar gematria --strategy ignore --min-errors 30

# Preview only unused variable fixes
python3 scripts/covenant_scripts/apply_type_fixes.py --pillar astrology --strategy unused --min-errors 10
```

**Strategies**:
- `ignore`: Add `# type: ignore[rule]` to high-noise lines (3+ errors)
- `unused`: Prefix unused variables with `_`
- `annotate`: Add basic `-> None` annotations to void methods
- `both`: Apply all strategies

## Phase 3: Apply Fixes

**⚠️ CAUTION**: Review the dry run output first, then commit changes:

```bash
# Apply fixes to a high-error pillar
python3 scripts/covenant_scripts/apply_type_fixes.py --pillar adyton --strategy both --min-errors 50 --commit

# Apply only ignore directives (safest)
python3 scripts/covenant_scripts/apply_type_fixes.py --pillar geometry --strategy ignore --min-errors 30 --commit
```

## Phase 4: Verify Reduction

Re-run the diagnostic to see the improvement:

```bash
# Check error count after fixes
python3 scripts/covenant_scripts/satisfy_pylance.py --pillar adyton --threshold 10
```

## Strategy Recommendations

1. **Start with high-error files** (`--min-errors 50+`) to get maximum impact
2. **Use `--strategy ignore` first** - it's the safest and most effective
3. **Review diffs** before committing to ensure no logic changes
4. **Target one pillar at a time** to make reviews manageable
5. **Run tests** after applying fixes to ensure no regressions

## Pillar Priority (by typical error count)

Based on initial scans:
1. `adyton` - 655 errors (many in `wall_designer.py`)
2. `geometry` - High due to OpenGL/3D code
3. `gematria` - Moderate
4. `astrology` - Moderate
5. `time_mechanics` - Lower
6. `tq` (Thelemic Qabalah) - Lower

## Alternative: Relax Strictness

If automated fixes aren't suitable, consider relaxing Pylance settings in `pyrightconfig.json`:

```json
{
  "typeCheckingMode": "basic",  // Instead of "strict"
  "reportUnknownMemberType": "none",
  "reportUnknownVariableType": "warning"
}
```

This is less ideal but may be pragmatic for UI-heavy code.
