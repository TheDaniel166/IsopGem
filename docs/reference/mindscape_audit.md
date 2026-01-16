# Mindscape Pillar Audit (Dec 2025) — Updated after fixes

## Scope
- Pillar: Document Manager / Mindscape (models, service, UI, physics, scripts)
- Goals: Identify entropy, architectural fractures, and missing safeguards; propose purification steps aligned with Sophia's Covenant.

## Current Status (Post-fix)
- Verification: `tests/verify_mindscape_service.py` passes.
- Home/root, context menu, and duplicate `get_edge` issues are resolved.
- Structured document links added via `mind_nodes.document_id`; migration applied (`src/scripts/migrate_mindscape_schema.py`).
- Imports and search now run in background `QRunnable` workers with signal callbacks; drag-save persists asynchronously.
- Physics gains adaptive repulsion + soft bounds; additive loads preserve springs.
- Destructive scripts require `--force`.

## Remaining Risks / Follow-ups
- Local graph fetch is still synchronous on the UI thread; large graphs may still hitch during `load_graph` (mitigate with worker + staged render if usage grows).
- Result objects/logging are basic; consider structured Result/Failure types for UI-safe messaging and richer Chronicle entries.
- No dedicated index on `document_id` yet beyond column definition; if dataset grows, add explicit index/pragma checks.
- Search/import workers use bare `QRunnable`; a common worker base with signals would reduce duplication and improve cancellation/error routing.

## Updated Recommendations
1) Wrap `get_local_graph` fetch in a worker when node degree exceeds a threshold to fully free the Wheel on large Plexes.
2) Introduce a small Result DTO for service mutators (success/err, message) and surface Chronicle logs in UI toasts for failures.
3) Add an explicit index for `mind_nodes.document_id` and confirm SQLite JSON1 availability during startup, logging fallbacks.
4) Extract a reusable signal-emitting worker base for imports/search to unify completion/error handling and enable cancellation if needed.
