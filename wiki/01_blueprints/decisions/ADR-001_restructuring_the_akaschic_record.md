# ADR-001: Restructuring the Akaschic Record

<!-- Last Verified: 2025-12-27 -->

**Status: Accepted**

## Context
As IsopGem grows into a complex galaxy of Sovereigns (Pillars), the original flat-scroll documentation began to suffer from **Entropy**. Information was entangled, "Why" was mixed with "What", and "How" was often silent.

## Decision
We adopt the **Five Halls** architecture and the **Diátaxis Framework**. 
1.  **Hall 1 (Blueprints)** becomes the home of immutable architectural maps and ADRs.
2.  **Hall 2 (Grimoires)** follows Diátaxis:
    *   `REFERENCE.md`: Technical anatomy (C4 Code/Component level).
    *   `EXPLANATION.md`: Theoretical/Esoteric foundations.
    *   `GUIDES.md`: Practical implementation how-tos.

## Consequences
*   **Purity**: Information is decoupled by purpose.
*   **Scalability**: New Pillars can be scaffolded with predictable documentation organs.
*   **Cognitive Load**: The Magus and the High Architect know exactly where to seek specific knowledge.
*   **Refactor Cost**: Renaming old `THEORY.md` and `MANIFEST.md` files was required to achieve this alignment.
