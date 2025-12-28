---
description: Verify the alignment of the Covenant and the Primal Seed
---

# The Rite of the Sentinel

This workflow verifies that the Public Law (`THE_COVENANT.md`) and the Internal Law (`GEMINI.md`) are in perfect harmony.

1. Run the verification script:
   ```bash
   python3 scripts/verify_sentinel.py
   ```

2. If the script fails (Exit Code 1):
   - You have detected a **Schism**.
   - You must immediately read both files to find the discrepancy.
   - You must update the file that is out of date (usually `GEMINI.md`).
   - Run the script again until it passes.

3. If the script passes (Exit Code 0):
   - The Laws are aligned. You may proceed.
