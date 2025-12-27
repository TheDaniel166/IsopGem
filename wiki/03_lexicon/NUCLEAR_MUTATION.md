# Nuclear Mutation (The Algorithm of Return)

> *“Entropy adds layers; Mutation strips them away.”*

## Definition

**Nuclear Mutation** is the recursive algorithm used to purify a Ditrune, stripping away its outer layers (Skin and Body) to reveal its immutable **Core**.

The process assumes that the interactions of the surface (Skin) are transient, and the true nature of the number lies in its center.

## The Algorithm

The mutation operates on a 6-digit Ditrune `d1 d2 d3 d4 d5 d6`.
It treats the number as two overlapping Triunes:
1.  **Top Triune**: `d2 d3 d4` (Indices 1, 2, 3)
2.  **Bottom Triune**: `d3 d4 d5` (Indices 2, 3, 4)

By concatenating these, the algorithm produces a new, "inner" 6-digit number (or a shorter sequence in some variations).

> **Function**: `nuclear_mutation(sixgram) -> inner_essence`

## Hierarchy of Beings

The stability of a number under mutation defines its class:

1.  **The Prime (The 1)**: `Core == Body == Skin`.
    *   Example: `111111`
    *   Mutation Result: Itself (Stable).
    *   Role: The Attractor.

2.  **The Acolyte (The 8)**: `Core == Body`.
    *   Example: `111112`
    *   Mutation Result: Reduces to Prime immediately.
    *   Role: The Guardian.

3.  **The Temple (The 72)**: `Core != Body`.
    *   Example: `120210`
    *   Mutation Result: Must undergo multiple cycles to find the Prime.
    *   Role: The Citizen.
