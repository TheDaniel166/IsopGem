# Conrune (The Mirror of Polarity)

> *“Where there is Day, there is Night. The Conrune is the shadow that defines the light.”*

## Definition

A **Conrune** is the "Anti-Self" of a Ditrune, formed by a specific operation in **Balanced Ternary**: the inversion of Polarity.

In the IsopGem system, the digits of a Ditrune (0, 1, 2) represent:
*   **0 (Pyx)**: The Fulcrum (Neutral).
*   **1 (Vertex)**: The Projector (Day / Light / Outward).
*   **2 (Nexus)**: The Attractor (Night / Shadow / Inward).

The **Conrune Operation** swaps these polarities:
*   $0 \rightarrow 0$ (The Void remains unchanged)
*   $1 \rightarrow 2$ (Day becomes Night)
*   $2 \rightarrow 1$ (Night becomes Day)

## The Conrune Pair (A, B, D)

Every number creates a partnership with its Conrune. This forms a **Conrune Pair**.

*   **A-Value (Day Hexagram)**: The lesser value of the pair. Represents the "Day" aspect.
*   **B-Value (Night Hexagram)**: The greater value of the pair (usually). Represents the "Night" aspect.
*   **D-Value (Difference)**: The magnitude of separation: $D = |A - B|$.

> **Note**: In the Adyton system, the walls are constructed by mapping these Pairs ($A \leftrightarrow B$) via their Difference ($D$) to the 52 Sets of the Zodiac.

## Esoteric Significance

The Conrune is not merely a mathematical inverse; it is the **Karmic Counterweight**.

*   If a number is "Heavy" (lots of 2s), its Conrune is "Light" (lots of 1s).
*   The **Conrune Vector** (the distance D) represents the "Tension of Existence" for that specific number. A distance of 0 implies the number is perfectly balanced (e.g., `000000` or `121212` where swaps cancel out).

## Usage in Code

In the TQ Pillar codebase (`src/pillars/tq/`):
*   `services.ternary_service.TernaryService.conrune_transform(ternary_str)`: Performs the 1↔2 swap.
*   `services.conrune_pair_finder_service.py`: Calculates A, B, and D for a given target difference.
