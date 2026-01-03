# Shared Base - Guides

<!-- Last Verified: 2026-01-03 -->

This folder documents the shared substrate used by all pillars (signals, managers, reusable UI components, and cross-cutting services).

---

## How To Navigate Shared Code

- UI infrastructure: `src/shared/ui/`
- Cross-pillar services: `src/shared/services/`
- Signals / coordination: `src/shared/signals/`

## When To Update These Docs

- If a shared service becomes a dependency of multiple pillars.
- If window lifecycle/navigation patterns change (e.g., NavigationBus, WindowManager).
