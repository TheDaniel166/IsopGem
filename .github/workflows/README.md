# GitHub Actions Workflows

## Active Workflows
_(None currently active)_

## Disabled Workflows

### `verify_covenant.yml.disabled`
**Status**: Temporarily disabled (2026-01-16)

**Reason**: Missing required scripts:
- `workflow_scripts/sync_covenant.py`
- `workflow_scripts/verify_sentinel.py`

**To Re-enable**: 
1. Create the missing verification scripts
2. Test locally: `python workflow_scripts/verify_sentinel.py`
3. Rename: `verify_covenant.yml.disabled` → `verify_covenant.yml`

**Purpose**: Verifies covenant file alignment and synchronization on every push to main.

---

*"The Guardian sleeps, but shall awaken when the scripts are forged."*
