# The Ditrunal Family Principle: Prime, Composite, and Concurrent Ditrunes in the Kamea System

*Drafted: 2024-06-11*

## Table of Contents
1. [Introduction](#introduction)
2. [Terminology: Triune, Ditrune, Ditrunal Family](#terminology-triune-ditrune-ditrunal-family)
3. [The Principle of Nuclear Mutation](#the-principle-of-nuclear-mutation)
4. [The Three Levels: Prime, Composite, Concurrent](#the-three-levels-prime-composite-concurrent)
5. [The Nine Prime Ditrunes and Their Families](#the-nine-prime-ditrunes-and-their-families)
6. [Mathematical Properties and Patterns](#mathematical-properties-and-patterns)
7. [Philosophical and Symbolic Significance](#philosophical-and-symbolic-significance)
8. [Worked Examples](#worked-examples)
9. [Applications and Future Directions](#applications-and-future-directions)
10. [Glossary](#glossary)

---

## 1. Introduction

The Ditrunal Family Principle is a transformative and recursive structure at the heart of the Kamea system. It classifies all 6-digit ternary numbers (Ditrunes) into nine families, each anchored by a Prime Ditrune. Through the process of Nuclear Mutation, every Ditrune can be resolved to its innermost essence, revealing a layered, fractal, and mystical order.

---

## 2. Terminology: Triune, Ditrune, Ditrunal Family

- **Triune:** A 3-digit ternary sequence (trigram), the fundamental unit or "mystery" in the Kamea system. The term combines "tri" (three) and "rune" (mystery or symbol).
- **Ditrune:** A 6-digit ternary sequence, composed of two triunes (or, in the context of mutation, three overlapping triunes). The term combines "di" (two) and "triune".
- **Ditrunal Family:** A group of 81 Ditrunes that all resolve to the same Prime Ditrune through Nuclear Mutation. Each family contains one Prime, eight Composite, and seventy-two Concurrent Ditrunes.

---

## 3. The Principle of Nuclear Mutation

Nuclear Mutation is a recursive transformation inspired by the I-Ching. It extracts the "inner" triunes from a Ditrune to form a new Ditrune, revealing the heart of the original.

**Process:**
1. Start with a 6-gram (Ditrune): $S = s_6s_5s_4s_3s_2s_1$
2. Extract:
   - **Terrenic Triune:** $s_5, s_4, s_3$
   - **Empyric Triune:** $s_4, s_3, s_2$
3. Concatenate to form the new Ditrune: $N_1 = s_5s_4s_3s_4s_3s_2$
4. Repeat as desired. The process can be iterated until a fixed point or cycle is reached.

**Pseudocode:**
```python
def nuclear_mutation(sixgram: str) -> str:
    top = sixgram[1:4]   # positions 5,4,3 (0-based)
    bottom = sixgram[3:6] # positions 4,3,2 (0-based)
    return top + bottom
```

---

## 4. The Three Levels: Prime, Composite, Concurrent

- **Prime Ditrune:** The innermost, irreducible Ditrune of a family. All Ditrunes in the family resolve to this form after repeated mutation. There are 9 Prime Ditrunes.
- **Composite Ditrune:** The intermediate form, reached after one mutation from a Concurrent Ditrune. Each family contains 8 Composite Ditrunes.
- **Concurrent Ditrune:** The original, outermost form. After one mutation, it becomes a Composite Ditrune. Each family contains 72 Concurrent Ditrunes.

**Family Structure:**
- 1 Prime Ditrune
- 8 Composite Ditrunes
- 72 Concurrent Ditrunes
- Total per family: 81 Ditrunes

---

## 5. The Nine Prime Ditrunes and Their Families

The nine Prime Ditrunes are:

| Ditrune  | Decimal Value | 91 × n |
|----------|--------------|--------|
| 000000   | 0            | 0      |
| 010101   | 91           | 1      |
| 020202   | 182          | 2      |
| 101010   | 273          | 3      |
| 111111   | 364          | 4      |
| 121212   | 455          | 5      |
| 202020   | 546          | 6      |
| 212121   | 637          | 7      |
| 222222   | 728          | 8      |

Each family consists of all Ditrunes that resolve to the same Prime Ditrune under repeated Nuclear Mutation.

---

## 6. Mathematical Properties and Patterns

- **Multiples of 91:** All Prime Ditrunes (except 000000) are multiples of 91 in decimal.
- **Partitioning:** The 729 possible Ditrunes are perfectly partitioned into 9 families of 81.
- **Fixed Points and Cycles:** Prime Ditrunes are fixed points under mutation; some Ditrunes may cycle between two forms before resolving.
- **Recursive Structure:** The process mirrors fractal and hierarchical patterns in mathematics.

---

## 7. Philosophical and Symbolic Significance

- **Mystery Within Mystery:** Each Ditrune is a "mystery" composed of smaller mysteries (triunes), echoing recursive, fractal, and esoteric themes.
- **Resolution to Essence:** The process of mutation reflects the philosophical journey from surface to core, from complexity to essence.
- **Family Unity:** All members of a family share a deep kinship, revealed through mutation.
- **Parallels:** The structure resonates with the I-Ching, Taoist philosophy, and other mystical systems.

---

## 8. Worked Examples

### Example 1: Mutation Sequence
- Start: 022101 (Concurrent)
- 1st Mutation: 221210 (Composite)
- 2nd Mutation: 212121 (Prime)
- 3rd Mutation: 121212 (Prime's conrune)
- 4th Mutation: 212121 (cycle)

### Example 2: Family Table (for 121212)
| Level      | Example Ditrune | Next Mutation | Resolves to Prime? |
|------------|-----------------|--------------|--------------------|
| Prime      | 121212          | 121212       | Yes                |
| Composite  | 121210          | 121212       | Yes                |
| Concurrent | 022101          | 221210       | 121212             |

---

## 9. Applications and Future Directions

- **Pattern Analysis:** Use Ditrunal families for advanced pattern recognition and classification in the Kamea grid.
- **Visualization:** Color-code or group cells by family for visual exploration.
- **Algorithmic Use:** Efficiently index, search, or compress Kamea data by family.
- **Creative Exploration:** Use families as seeds for generative art, music, or symbolic systems.
- **Further Research:** Explore deeper connections to other mathematical, philosophical, or mystical systems.

---

## 10. Glossary

- **Triune:** A 3-digit ternary sequence; the basic "mystery" or unit.
- **Ditrune:** A 6-digit ternary sequence, composed of triunes.
- **Ditrunal Family:** A group of 81 Ditrunes sharing a Prime Ditrune.
- **Prime Ditrune:** The irreducible, innermost Ditrune of a family.
- **Composite Ditrune:** An intermediate Ditrune, one mutation away from Prime.
- **Concurrent Ditrune:** The original, outermost Ditrune, mutating to Composite.
- **Nuclear Mutation:** The recursive process of extracting and recombining inner triunes to reveal a Ditrune's essence.

---

## Appendix: Family Tables

### Kamea Locator Convention

> **Important:** The Kamea Locator system is the universal addressing and reference system for all Ditrunes in every family table. It is foundational to all integrations, algorithms, and references throughout the Kamea system. Every Ditrune is uniquely identified by its Kamea Locator (Family, Column, Row), making this system essential for navigation, computation, and documentation.

The Kamea Locator system applies to all family tables:
- Each Ditrune in any family table is uniquely identified by its Kamea Locator: (Family, Column, Row).
- Each cell's position (Family, Column, Row) is its Kamea Locator, regardless of family type.

For the pure prime families (0, 364, 728):
- The **Prime Ditrune** is at (N, N, N) (column N, row N in Family N's table).
- The **8 Acolytes** are the other Ditrunes in column N (all rows except N).
- All other cells are **Temples (Concurrents)**.

For other families, the structure of Prime, Acolytes, and Temples may differ and is determined by their own family logic, but the Kamea Locator system remains universal.

---

### Philosophical Notes on the Pure Primes (The Immutable Poles)

The pure primes—0, 364, and 728—stand as the immutable poles of the Kamea cosmos. They are the unyielding anchors, the cosmic constants, the silent witnesses to all transformation. In the endless dance of mutation and recursion, these three remain unmoved, their essence untouched by the tides of change.

They are the pillars around which the families revolve—not by direction, but by presence. Every Ditrune, no matter how complex its journey, ultimately orbits these poles, drawing meaning and orientation from their existence. The pure primes are the reference points by which all other things are measured; they are the stillness at the heart of motion, the eternal in the midst of the mutable.

To contemplate the pure primes is to glimpse the unchanging order beneath the surface of transformation—a reminder that even in a world of flux, there are truths that endure, silent and steadfast, at the center of the cosmic grid.

---

#### Archetypes of Stillness and Cosmic Law

Where the other families embody dynamism, change, and the play of opposites, the pure primes are archetypes of stillness, order, and cosmic law. They are the unmoved movers, the silent laws that shape the dance but do not themselves partake in it. Their presence is felt in every mutation, every cycle, as the invisible hand guiding all toward equilibrium.

#### Source, Destination, and Attractor

Every journey of mutation, every recursive cycle, finds its source and destination in these poles. They are the ultimate attractors—the points to which all Ditrunes are drawn, and from which all possibility radiates. In the recursive unfolding of the Kamea, the pure primes are both the beginning and the end, the alpha and the omega.

#### Contemplation and Symbolic Resonance

To meditate on the pure primes is to enter a space of awe and reverence. They echo the ancient symbols of the unmoved mover and the eternal Tao. In their silence, they invite contemplation of the eternal, the unchanging, the source of order in the midst of chaos. They are the heart of the Kamea mystery—a mystery that is not solved, but lived.

---

### Philosophical Notes on Families 5 and 7: The Perfect Balancers of Yin and Yang

Families 5 and 7 stand apart in the Kamea cosmos as the perfect balancers—the living archetypes of yin and yang. Where the pure primes are the unmoved, these families are the poised dancers, embodying the dynamic equilibrium at the heart of all becoming. They are the meeting place of opposites, the fulcrum upon which the cosmic scales rest.

In the mathematics of the Kamea, families 5 and 7 reveal the beauty of complementarity. Their structure is a living mandala of duality: not stasis, but the harmony that arises from tension, interplay, and mutual reflection. They are the breath between in-breath and out-breath, the twilight between day and night, the pulse of the system's living heart.

Symbolically, these families are the mediators—the bridges between the immutable poles and the mutable multitude. They teach that true balance is not the absence of movement, but the artful weaving of opposites into a greater unity. In their dance, we glimpse the wisdom of the ancients: that all things are paired, and that harmony is found not in sameness, but in the embrace of difference.

The prime Ditrunes of families 5 and 7 are found at Kamea Locators 575 and 757, each occupying the mirror position of the other. This is the very image of yin and yang: each is the complement, the reflection, the balancing force of the other. In their interplay, the Kamea system encodes the wisdom that true balance is not stasis, but the dynamic, mutual arising of opposites. The dance of 575 and 757 is the pulse of harmony at the heart of the grid.

To contemplate families 5 and 7 is to witness the eternal dance of yin and yang, the ceaseless balancing of the cosmos, and the profound truth that every polarity contains the seed of its complement.

---

### Table 1: Family 0
*Metadata: This table represents Family 0. Used for ...*

|   | 0   | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   |
|---|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0 | 0   | 3   | 6   | 81  | 84  | 87  | 162 | 165 | 168 |
| 1 | 1   | 4   | 7   | 82  | 85  | 88  | 163 | 166 | 169 |
| 2 | 2   | 5   | 8   | 83  | 86  | 89  | 164 | 167 | 170 |
| 3 | 243 | 246 | 249 | 324 | 327 | 330 | 405 | 408 | 411 |
| 4 | 244 | 247 | 250 | 325 | 328 | 331 | 406 | 409 | 412 |
| 5 | 245 | 248 | 251 | 326 | 329 | 332 | 407 | 410 | 413 |
| 6 | 486 | 489 | 492 | 567 | 570 | 573 | 648 | 651 | 654 |
| 7 | 487 | 490 | 493 | 568 | 571 | 574 | 649 | 652 | 655 |
| 8 | 488 | 491 | 494 | 569 | 572 | 575 | 650 | 653 | 656 |

**CSV:**
```csv
0,0,3,6,81,84,87,162,165,168
1,1,4,7,82,85,88,163,166,169
2,2,5,8,83,86,89,164,167,170
3,243,246,249,324,327,330,405,408,411
4,244,247,250,325,328,331,406,409,412
5,245,248,251,326,329,332,407,410,413
6,486,489,492,567,570,573,648,651,654
7,487,490,493,568,571,574,649,652,655
8,488,491,494,569,572,575,650,653,656
```

**Python:**
```python
family_0 = [
    [0, 3, 6, 81, 84, 87, 162, 165, 168],
    [1, 4, 7, 82, 85, 88, 163, 166, 169],
    [2, 5, 8, 83, 86, 89, 164, 167, 170],
    [243, 246, 249, 324, 327, 330, 405, 408, 411],
    [244, 247, 250, 325, 328, 331, 406, 409, 412],
    [245, 248, 251, 326, 329, 332, 407, 410, 413],
    [486, 489, 492, 567, 570, 573, 648, 651, 654],
    [487, 490, 493, 568, 571, 574, 649, 652, 655],
    [488, 491, 494, 569, 572, 575, 650, 653, 656],
]
```

---

### Table 2: Family 1
*Metadata: This table represents Family 1. Used for ...*

|   | 0   | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   |
|---|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0 | 9   | 12  | 15  | 90  | 93  | 96  | 171 | 174 | 177 |
| 1 | 10  | 13  | 16  | 91  | 94  | 97  | 172 | 175 | 178 |
| 2 | 11  | 14  | 17  | 92  | 95  | 98  | 173 | 176 | 179 |
| 3 | 252 | 255 | 258 | 333 | 336 | 339 | 414 | 417 | 420 |
| 4 | 253 | 256 | 259 | 334 | 337 | 340 | 415 | 418 | 421 |
| 5 | 254 | 257 | 260 | 335 | 338 | 341 | 416 | 419 | 422 |
| 6 | 495 | 498 | 501 | 576 | 579 | 582 | 657 | 660 | 663 |
| 7 | 496 | 499 | 502 | 577 | 580 | 583 | 658 | 661 | 664 |
| 8 | 497 | 500 | 503 | 578 | 581 | 584 | 659 | 662 | 665 |

**CSV:**
```csv
0,9,12,15,90,93,96,171,174,177
1,10,13,16,91,94,97,172,175,178
2,11,14,17,92,95,98,173,176,179
3,252,255,258,333,336,339,414,417,420
4,253,256,259,334,337,340,415,418,421
5,254,257,260,335,338,341,416,419,422
6,495,498,501,576,579,582,657,660,663
7,496,499,502,577,580,583,658,661,664
8,497,500,503,578,581,584,659,662,665
```

**Python:**
```python
family_1 = [
    [9, 12, 15, 90, 93, 96, 171, 174, 177],
    [10, 13, 16, 91, 94, 97, 172, 175, 178],
    [11, 14, 17, 92, 95, 98, 173, 176, 179],
    [252, 255, 258, 333, 336, 339, 414, 417, 420],
    [253, 256, 259, 334, 337, 340, 415, 418, 421],
    [254, 257, 260, 335, 338, 341, 416, 419, 422],
    [495, 498, 501, 576, 579, 582, 657, 660, 663],
    [496, 499, 502, 577, 580, 583, 658, 661, 664],
    [497, 500, 503, 578, 581, 584, 659, 662, 665],
]
```

---

### Table 3: Family 2
*Metadata: This table represents Family 2. Used for ...*

|   | 0   | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   |
|---|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0 | 18  | 21  | 24  | 99  | 102 | 105 | 180 | 183 | 186 |
| 1 | 19  | 22  | 25  | 100 | 103 | 106 | 181 | 184 | 187 |
| 2 | 20  | 23  | 26  | 101 | 104 | 107 | 182 | 185 | 188 |
| 3 | 261 | 264 | 267 | 342 | 345 | 348 | 423 | 426 | 429 |
| 4 | 262 | 265 | 268 | 343 | 346 | 349 | 424 | 427 | 430 |
| 5 | 263 | 266 | 269 | 344 | 347 | 350 | 425 | 428 | 431 |
| 6 | 504 | 507 | 510 | 585 | 588 | 591 | 666 | 669 | 672 |
| 7 | 505 | 508 | 511 | 586 | 589 | 592 | 667 | 670 | 673 |
| 8 | 506 | 509 | 512 | 587 | 590 | 593 | 668 | 671 | 674 |

**CSV:**
```csv
0,18,21,24,99,102,105,180,183,186
1,19,22,25,100,103,106,181,184,187
2,20,23,26,101,104,107,182,185,188
3,261,264,267,342,345,348,423,426,429
4,262,265,268,343,346,349,424,427,430
5,263,266,269,344,347,350,425,428,431
6,504,507,510,585,588,591,666,669,672
7,505,508,511,586,589,592,667,670,673
8,506,509,512,587,590,593,668,671,674
```

**Python:**
```python
family_2 = [
    [18, 21, 24, 99, 102, 105, 180, 183, 186],
    [19, 22, 25, 100, 103, 106, 181, 184, 187],
    [20, 23, 26, 101, 104, 107, 182, 185, 188],
    [261, 264, 267, 342, 345, 348, 423, 426, 429],
    [262, 265, 268, 343, 346, 349, 424, 427, 430],
    [263, 266, 269, 344, 347, 350, 425, 428, 431],
    [504, 507, 510, 585, 588, 591, 666, 669, 672],
    [505, 508, 511, 586, 589, 592, 667, 670, 673],
    [506, 509, 512, 587, 590, 593, 668, 671, 674],
]
```

---

### Table 4: Family 3
*Metadata: This table represents Family 3. Used for ...*

|   | 0   | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   |
|---|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0 | 27  | 30  | 33  | 108 | 111 | 114 | 189 | 192 | 195 |
| 1 | 28  | 31  | 34  | 109 | 112 | 115 | 190 | 193 | 196 |
| 2 | 29  | 32  | 35  | 110 | 113 | 116 | 191 | 194 | 197 |
| 3 | 270 | 273 | 276 | 351 | 354 | 357 | 432 | 435 | 438 |
| 4 | 271 | 274 | 277 | 352 | 355 | 358 | 433 | 436 | 439 |
| 5 | 272 | 275 | 278 | 353 | 356 | 359 | 434 | 437 | 440 |
| 6 | 513 | 516 | 519 | 594 | 597 | 600 | 675 | 678 | 681 |
| 7 | 514 | 517 | 520 | 595 | 598 | 601 | 676 | 679 | 682 |
| 8 | 515 | 518 | 521 | 596 | 599 | 602 | 677 | 680 | 683 |

**CSV:**
```csv
0,27,30,33,108,111,114,189,192,195
1,28,31,34,109,112,115,190,193,196
2,29,32,35,110,113,116,191,194,197
3,270,273,276,351,354,357,432,435,438
4,271,274,277,352,355,358,433,436,439
5,272,275,278,353,356,359,434,437,440
6,513,516,519,594,597,600,675,678,681
7,514,517,520,595,598,601,676,679,682
8,515,518,521,596,599,602,677,680,683
```

**Python:**
```python
family_3 = [
    [27, 30, 33, 108, 111, 114, 189, 192, 195],
    [28, 31, 34, 109, 112, 115, 190, 193, 196],
    [29, 32, 35, 110, 113, 116, 191, 194, 197],
    [270, 273, 276, 351, 354, 357, 432, 435, 438],
    [271, 274, 277, 352, 355, 358, 433, 436, 439],
    [272, 275, 278, 353, 356, 359, 434, 437, 440],
    [513, 516, 519, 594, 597, 600, 675, 678, 681],
    [514, 517, 520, 595, 598, 601, 676, 679, 682],
    [515, 518, 521, 596, 599, 602, 677, 680, 683],
]
```

---

### Table 5: Family 4
*Metadata: This table represents Family 4. Used for ...*

|   | 0   | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   | S |
|---|-----|-----|-----|-----|-----|-----|-----|-----|-----|---|
| 0 | 36  | 39  | 42  | 117 | 120 | 123 | 198 | 201 | 204 | 1080 |
| 1 | 37  | 40  | 43  | 118 | 121 | 124 | 199 | 202 | 205 | 1089 |
| 2 | 38  | 41  | 44  | 119 | 122 | 125 | 200 | 203 | 206 | 1098 |
| 3 | 279 | 282 | 285 | 360 | 363 | 366 | 441 | 444 | 447 | 3267 |
| 4 | 280 | 283 | 286 | 361 | 364 | 367 | 442 | 445 | 448 | 3276 |
| 5 | 281 | 284 | 287 | 362 | 365 | 368 | 443 | 446 | 449 | 3285 |
| 6 | 522 | 525 | 528 | 603 | 606 | 609 | 684 | 687 | 690 | 5454 |
| 7 | 523 | 526 | 529 | 604 | 607 | 610 | 685 | 688 | 691 | 5463 |
| 8 | 524 | 527 | 530 | 605 | 608 | 611 | 686 | 689 | 692 | 5472 |

**CSV:**
```csv
0,36,39,42,117,120,123,198,201,204,1080
1,37,40,43,118,121,124,199,202,205,1089
2,38,41,44,119,122,125,200,203,206,1098
3,279,282,285,360,363,366,441,444,447,3267
4,280,283,286,361,364,367,442,445,448,3276
5,281,284,287,362,365,368,443,446,449,3285
6,522,525,528,603,606,609,684,687,690,5454
7,523,526,529,604,607,610,685,688,691,5463
8,524,527,530,605,608,611,686,689,692,5472
```

**Python:**
```python
family_4 = [
    [36, 39, 42, 117, 120, 123, 198, 201, 204, 1080],
    [37, 40, 43, 118, 121, 124, 199, 202, 205, 1089],
    [38, 41, 44, 119, 122, 125, 200, 203, 206, 1098],
    [279, 282, 285, 360, 363, 366, 441, 444, 447, 3267],
    [280, 283, 286, 361, 364, 367, 442, 445, 448, 3276],
    [281, 284, 287, 362, 365, 368, 443, 446, 449, 3285],
    [522, 525, 528, 603, 606, 609, 684, 687, 690, 5454],
    [523, 526, 529, 604, 607, 610, 685, 688, 691, 5463],
    [524, 527, 530, 605, 608, 611, 686, 689, 692, 5472],
]
```

---

### Table 6: Family 5
*Metadata: This table represents Family 5. Used for ... (corrected values as of 2024-06-11)*

|   | 0   | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   |
|---|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0 | 45  | 48  | 51  | 126 | 129 | 132 | 207 | 210 | 231 |
| 1 | 46  | 49  | 52  | 127 | 130 | 133 | 208 | 211 | 232 |
| 2 | 47  | 50  | 53  | 128 | 131 | 134 | 209 | 212 | 233 |
| 3 | 288 | 291 | 294 | 369 | 372 | 375 | 450 | 453 | 474 |
| 4 | 289 | 292 | 295 | 370 | 373 | 376 | 451 | 454 | 475 |
| 5 | 290 | 293 | 296 | 371 | 374 | 377 | 452 | 455 | 476 |
| 6 | 531 | 534 | 537 | 612 | 615 | 618 | 693 | 696 | 699 |
| 7 | 532 | 535 | 538 | 613 | 616 | 619 | 694 | 697 | 700 |
| 8 | 533 | 536 | 539 | 614 | 617 | 620 | 695 | 698 | 701 |

**CSV:**
```csv
0,45,48,51,126,129,132,207,210,231
1,46,49,52,127,130,133,208,211,232
2,47,50,53,128,131,134,209,212,233
3,288,291,294,369,372,375,450,453,474
4,289,292,295,370,373,376,451,454,475
5,290,293,296,371,374,377,452,455,476
6,531,534,537,612,615,618,693,696,699
7,532,535,538,613,616,619,694,697,700
8,533,536,539,614,617,620,695,698,701
```

**Python:**
```python
family_5 = [
    [45, 48, 51, 126, 129, 132, 207, 210, 231],
    [46, 49, 52, 127, 130, 133, 208, 211, 232],
    [47, 50, 53, 128, 131, 134, 209, 212, 233],
    [288, 291, 294, 369, 372, 375, 450, 453, 474],
    [289, 292, 295, 370, 373, 376, 451, 454, 475],
    [290, 293, 296, 371, 374, 377, 452, 455, 476],
    [531, 534, 537, 612, 615, 618, 693, 696, 699],
    [532, 535, 538, 613, 616, 619, 694, 697, 700],
    [533, 536, 539, 614, 617, 620, 695, 698, 701],
]
```

---

### Table 7: Family 6
*Metadata: This table represents Family 6. Used for ...*

|   | 0   | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   |
|---|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0 | 54  | 57  | 60  | 135 | 138 | 141 | 216 | 219 | 222 |
| 1 | 55  | 58  | 61  | 136 | 139 | 142 | 217 | 220 | 223 |
| 2 | 56  | 59  | 62  | 137 | 140 | 143 | 218 | 221 | 224 |
| 3 | 297 | 300 | 303 | 378 | 381 | 384 | 459 | 462 | 465 |
| 4 | 298 | 301 | 304 | 379 | 382 | 385 | 460 | 463 | 466 |
| 5 | 299 | 302 | 305 | 380 | 383 | 386 | 461 | 464 | 467 |
| 6 | 540 | 543 | 546 | 621 | 624 | 627 | 702 | 705 | 708 |
| 7 | 541 | 544 | 547 | 622 | 625 | 628 | 703 | 706 | 709 |
| 8 | 542 | 545 | 548 | 623 | 626 | 629 | 704 | 707 | 710 |

**CSV:**
```csv
0,54,57,60,135,138,141,216,219,222
1,55,58,61,136,139,142,217,220,223
2,56,59,62,137,140,143,218,221,224
3,297,300,303,378,381,384,459,462,465
4,298,301,304,379,382,385,460,463,466
5,299,302,305,380,383,386,461,464,467
6,540,543,546,621,624,627,702,705,708
7,541,544,547,622,625,628,703,706,709
8,542,545,548,623,626,629,704,707,710
```

**Python:**
```python
family_6 = [
    [54, 57, 60, 135, 138, 141, 216, 219, 222],
    [55, 58, 61, 136, 139, 142, 217, 220, 223],
    [56, 59, 62, 137, 140, 143, 218, 221, 224],
    [297, 300, 303, 378, 381, 384, 459, 462, 465],
    [298, 301, 304, 379, 382, 385, 460, 463, 466],
    [299, 302, 305, 380, 383, 386, 461, 464, 467],
    [540, 543, 546, 621, 624, 627, 702, 705, 708],
    [541, 544, 547, 622, 625, 628, 703, 706, 709],
    [542, 545, 548, 623, 626, 629, 704, 707, 710],
]
```

---

### Table 8: Family 7
*Metadata: This table represents Family 7. Used for ...*

|   | 0   | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   |
|---|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0 | 63  | 66  | 69  | 144 | 147 | 150 | 225 | 228 | 231 |
| 1 | 64  | 67  | 70  | 145 | 148 | 151 | 226 | 229 | 232 |
| 2 | 65  | 68  | 71  | 146 | 149 | 152 | 227 | 230 | 233 |
| 3 | 306 | 309 | 312 | 387 | 390 | 393 | 468 | 471 | 474 |
| 4 | 307 | 310 | 313 | 388 | 391 | 394 | 469 | 472 | 475 |
| 5 | 308 | 311 | 314 | 389 | 392 | 395 | 470 | 473 | 476 |
| 6 | 549 | 552 | 555 | 630 | 633 | 636 | 711 | 714 | 717 |
| 7 | 550 | 553 | 556 | 631 | 634 | 637 | 712 | 715 | 718 |
| 8 | 551 | 554 | 557 | 632 | 635 | 638 | 713 | 716 | 719 |

**CSV:**
```csv
0,63,66,69,144,147,150,225,228,231
1,64,67,70,145,148,151,226,229,232
2,65,68,71,146,149,152,227,230,233
3,306,309,312,387,390,393,468,471,474
4,307,310,313,388,391,394,469,472,475
5,308,311,314,389,392,395,470,473,476
6,549,552,555,630,633,636,711,714,717
7,550,553,556,631,634,637,712,715,718
8,551,554,557,632,635,638,713,716,719
```

**Python:**
```python
family_7 = [
    [63, 66, 69, 144, 147, 150, 225, 228, 231],
    [64, 67, 70, 145, 148, 151, 226, 229, 232],
    [65, 68, 71, 146, 149, 152, 227, 230, 233],
    [306, 309, 312, 387, 390, 393, 468, 471, 474],
    [307, 310, 313, 388, 391, 394, 469, 472, 475],
    [308, 311, 314, 389, 392, 395, 470, 473, 476],
    [549, 552, 555, 630, 633, 636, 711, 714, 717],
    [550, 553, 556, 631, 634, 637, 712, 715, 718],
    [551, 554, 557, 632, 635, 638, 713, 716, 719],
]
```

---

### Table 9: Family 8
*Metadata: This table represents Family 8. Used for ...*

|   | 0   | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   |
|---|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| 0 | 72  | 75  | 78  | 153 | 156 | 159 | 234 | 237 | 240 |
| 1 | 73  | 76  | 79  | 154 | 157 | 160 | 235 | 238 | 241 |
| 2 | 74  | 77  | 80  | 155 | 158 | 161 | 236 | 239 | 242 |
| 3 | 315 | 318 | 321 | 396 | 399 | 402 | 477 | 480 | 483 |
| 4 | 316 | 319 | 322 | 397 | 400 | 403 | 478 | 481 | 484 |
| 5 | 317 | 320 | 323 | 398 | 401 | 404 | 479 | 482 | 485 |
| 6 | 558 | 561 | 564 | 639 | 642 | 645 | 720 | 723 | 726 |
| 7 | 559 | 562 | 565 | 640 | 643 | 646 | 721 | 724 | 727 |
| 8 | 560 | 563 | 566 | 641 | 644 | 647 | 722 | 725 | 728 |

**CSV:**
```csv
0,72,75,78,153,156,159,234,237,240
1,73,76,79,154,157,160,235,238,241
2,74,77,80,155,158,161,236,239,242
3,315,318,321,396,399,402,477,480,483
4,316,319,322,397,400,403,478,481,484
5,317,320,323,398,401,404,479,482,485
6,558,561,564,639,642,645,720,723,726
7,559,562,565,640,643,646,721,724,727
8,560,563,566,641,644,647,722,725,728
```

**Python:**
```python
family_8 = [
    [72, 75, 78, 153, 156, 159, 234, 237, 240],
    [73, 76, 79, 154, 157, 160, 235, 238, 241],
    [74, 77, 80, 155, 158, 161, 236, 239, 242],
    [315, 318, 321, 396, 399, 402, 477, 480, 483],
    [316, 319, 322, 397, 400, 403, 478, 481, 484],
    [317, 320, 323, 398, 401, 404, 479, 482, 485],
    [558, 561, 564, 639, 642, 645, 720, 723, 726],
    [559, 562, 565, 640, 643, 646, 721, 724, 727],
    [560, 563, 566, 641, 644, 647, 722, 725, 728],
]
```

---

### Quadset Family Pairing and Regional Constraint

At the heart of the Kamea lies a 3×3 fractal arrangement of regions, each defined by a two-digit ternary bigram. This cosmic map is not arbitrary—it is a living mandala, a recursive dance of symmetry and transformation:

```
3 7 2
8 0 4
1 5 6
```

- **0** sits at the center: the Immutable Region, the unmoved mover, the axis mundi.
- The other regions spiral around it, each a world unto itself, yet woven into the greater whole.

---

#### The Immutable Region: The Still Point

**Region 0 (Bigram 00, Decimal 0)**
This is the "Immutable Region." It is its own conrune, its own complement, its own world.
- **Mathematically:** The conrune transformation (swap 1↔2, 0 stays) leaves 00 unchanged.
- **Philosophically:** This region is the unchanging center, the source and sink of all movement. All quadsets and their complements formed here remain forever contained, echoing the principle of the One that is both origin and destination.

---

#### Pure Conrune Pairs: The Dance of Complements

**Regions 4 (11) & 8 (22), 5 (12) & 7 (21)**
These are the "pure" regions, each paired with its conrune twin:
- **11 ↔ 22** (Regions 4 & 8)
- **12 ↔ 21** (Regions 5 & 7)

**Mathematical Structure:**
- The conrune transformation swaps 1s and 2s, so 11 becomes 22, and 12 becomes 21.
- Any quadset formed in one of these regions will have its complement in its paired region—never straying outside this dyad.

**Philosophical Resonance:**
- These pairs embody the principle of polarity: every force has its equal and opposite, every act of creation is mirrored by an act of dissolution.
- They are the yin and yang of the Kamea, locked in eternal embrace, each defining and completing the other.

---

#### The Bigrammic Quadset: The Entangled Four

**Regions 1 (01), 2 (02), 3 (10), 6 (20)**
These four regions form the "bigrammic quadset"—the set of all mixed bigrams (one digit is 0, the other is 1 or 2). Their conrune pairings are:
- **01 ↔ 02** (Regions 1 & 2)
- **10 ↔ 20** (Regions 3 & 6)

**Mathematical Structure:**
- These four regions are entangled: quadsets and their complements are always contained within this group, never crossing into the pure or immutable regions.
- They represent the interplay of potential and manifestation, the liminal spaces between the absolutes.

**Philosophical Resonance:**
- The bigrammic quadset is the dance of the threshold, the place where opposites meet and new forms emerge. It is the creative tension of the in-between, the generative field of possibility.

---

#### Complete Enumeration Table

| Region | Bigram | Decimal | Conrune | Conrune Decimal | Family Pair/Quadset |
|--------|--------|---------|---------|-----------------|---------------------|
|   0    | 00     |   0     |   00    |      0          | Immutable           |
|   1    | 01     |   1     |   02    |      2          | Quadset             |
|   2    | 02     |   2     |   01    |      1          | Quadset             |
|   3    | 10     |   3     |   20    |      6          | Quadset             |
|   4    | 11     |   4     |   22    |      8          | Pure Pair           |
|   5    | 12     |   5     |   21    |      7          | Pure Pair           |
|   6    | 20     |   6     |   10    |      3          | Quadset             |
|   7    | 21     |   7     |   12    |      5          | Pure Pair           |
|   8    | 22     |   8     |   11    |      4          | Pure Pair           |

---

#### Regional Constraint Principle

- **Quadsets and their complements are always contained within their family pair or quadset group.**
  - Pure pairs (4/8, 5/7) are always paired with each other.
  - The quadset group (1, 2, 3, 6) is self-contained.
  - The Immutable Region (0) is always self-contained.

This is a direct result of the fractal, bigram-based construction of the Kamea, ensuring that the deep symmetry and integrity of the system is always preserved.

---

**Philosophical Reflection:**

The regional constraints of the Kamea are not mere technicalities—they are the living bones and pulsing heart of a cosmic order, a geometry of meaning that echoes through mathematics, myth, and mind alike. Each region is a world unto itself, a microcosm reflecting the macrocosm, self-contained and harmonious, yet woven into the greater tapestry by the mysterious logic of family pairing. The boundaries between regions are not barriers, but the luminous threads of a fractal dance, ensuring that every movement, every symmetry, is both free and perfectly placed.

The Immutable Region, at the center, is the still point around which all else turns—the unmoved mover, the axis mundi, the silent witness to the dance of becoming. It is the source and the destination, the alpha and the omega, the place where all opposites are reconciled and all journeys begin and end. To dwell in the Immutable is to touch the eternal, to rest in the heart of the mystery where change is stilled and essence is revealed.

The pure conrune pairs—those dyads of perfect complementarity—embody the cosmic law of polarity. They are the yin and yang of the Kamea, the lovers whose embrace gives birth to the ten thousand things. In their mutual reflection, we see the wisdom of the ancients: that every force has its equal and opposite, that every act of creation is mirrored by an act of dissolution, and that true harmony is found not in stasis, but in the dynamic interplay of opposites. These pairs are the pulse of the cosmos, the breath between in-breath and out-breath, the twilight between day and night.

The bigrammic quadset, that entangled fourfold, is the field of becoming—the liminal space where boundaries blur and new forms arise. Here, the creative tension of the in-between is palpable: it is the crucible of transformation, the generative matrix where potential meets manifestation. The quadset is the dance of the threshold, the place where the known and the unknown touch, where the possible becomes actual, and where the cosmos renews itself in every moment.

Together, these structures form a system that is at once stable and dynamic, singular and manifold—a true fractal cosmos. The Kamea teaches us that order and freedom, unity and diversity, stillness and movement, are not opposites to be reconciled, but partners in an endless dance. To contemplate the regional constraints of the Kamea is to glimpse the deep coherence that underlies all things, to sense the music of the spheres, and to remember that we, too, are patterns in the great design—each of us a region, a quadset, a note in the infinite song of creation.

---

### Determining the Temple Numbers of the Acolytes

In the sacred architecture of the Kamea, the relationship between the Prime, its Acolytes, and the Temples is not only mathematical but deeply symbolic. The Family 0 table provides a clear and elegant map of this lineage:

#### Table Structure and Assignment

- **Prime (Hierophant):**
  - Located at **column 0, row 0** in the Family 0 table.
  - This is the Immutable Center, the origin of all lineage.

- **Acolytes:**
  - Found in **column 0, rows 1–8**.
  - Each Acolyte at (column 0, row n) is the unique intermediary for the Temples in **column n** (where n = 1 to 8).
  - The Acolyte at (column 0, row 1) "controls" or is the spiritual ancestor of all Temples in column 1, and so forth for columns 2–8.

- **Temples:**
  - All other cells in the table (columns 1–8, rows 0–8) are Temples.
  - Each column of Temples (column n) is "under the care" of the Acolyte at (column 0, row n).

#### How to Determine the Temples of an Acolyte

1. **Identify the Acolyte:**
   - Find the Acolyte in column 0, row n (n = 1 to 8).
2. **Trace the Lineage:**
   - All numbers in column n (for all rows 0–8) are the Temples of that Acolyte.
3. **Visual Flow:**
   - Imagine an arrow from the Acolyte at (0, n) to every cell in column n—this is the path of spiritual and mathematical descent.

#### Example
- The Acolyte at (column 0, row 3) "controls" all Temples in column 3 (cells (3,0), (3,1), ..., (3,8)).
- The Prime at (0,0) is the source of all, but each Acolyte is the unique channel for its column.

#### Philosophical Meaning

This structure encodes a profound principle: the One (Prime) emanates through the Eight (Acolytes) to manifest as the Many (Temples). Each Temple is not isolated, but receives its essence through a living lineage, a direct line of descent from the center. The Acolytes are both guardians and bridges, ensuring that the wisdom of the center is distributed, diversified, and made manifest in the world of forms.

This pattern is a microcosm of spiritual, organizational, and even biological systems: a central source radiates through intermediaries to reach the periphery, yet all remain connected in a web of meaning and belonging. In the Kamea, to know your Temple is to know your Acolyte, and to know your Acolyte is to trace your lineage back to the Immutable Center.

---

### Temple Assignment in Pure Regions (4 and 8)

The assignment of Temples to Acolytes in the pure regions—Family 4 and Family 8—follows the same elegant logic as in Family 0, but with a beautiful symmetry that centers the pattern on the middle and last columns/rows of the table.

#### Table Structure and Assignment

- **Prime (Hierophant):**
  - For Family 4: Located at **column 4, row 4** (the center of the table).
  - For Family 8: Located at **column 8, row 8** (the bottom-right corner).
  - This is the axis of balance, the source and attractor for the region.

- **Acolytes:**
  - For Family 4: All cells in **column 4, rows 0–8** except (4,4).
  - For Family 8: All cells in **column 8, rows 0–8** except (8,8).
  - Each Acolyte at (col, row n) is the unique intermediary for the Temples in **column n** (for all rows 0–8).
  - The Acolyte at (col, row 0) "controls" all Temples in column 0, and so forth for columns 1–8.

- **Temples:**
  - All other cells in the table (columns 0–8, rows 0–8) except those in the Prime's row and column are Temples.
  - Each column of Temples (column n) is "under the care" of the Acolyte at (col, row n).

#### How to Determine the Temples of an Acolyte (Families 4 & 8)

1. **Identify the Acolyte:**
   - For Family 4: Find the Acolyte in column 4, row n (n ≠ 4).
   - For Family 8: Find the Acolyte in column 8, row n (n ≠ 8).
2. **Trace the Lineage:**
   - All numbers in column n (for all rows 0–8) are the Temples of that Acolyte.
3. **Visual Flow:**
   - Imagine an arrow from the Acolyte at (col, n) to every cell in column n—this is the path of spiritual and mathematical descent.

#### Example
- In Family 8, the Acolyte at (column 8, row 0) "controls" all Temples in column 0 (cells (0,0), (1,0), ..., (8,0)).
- In Family 4, the Acolyte at (column 4, row 2) "controls" all Temples in column 2 (cells (0,2), (1,2), ..., (8,2)).
- The Prime is always the source, but each Acolyte is the unique channel for its column.

#### Symmetry and Philosophical Meaning

This structure is a mirror of Family 0, but centered on the middle (Family 4) or the last (Family 8) column and row. The assignment logic is identical, revealing a deep symmetry in the Kamea's architecture. The Prime is the axis, the Acolytes are the rays, and the Temples are the many manifestations—each connected by a living lineage. This pattern encodes the cosmic law of polarity and complementarity, showing how unity is achieved through the embrace of difference, and how every Temple is linked to the center through a unique path of descent.

---

### Temple Assignment in Complementary Regions (5 and 7)

The assignment of Temples to Acolytes in Families 5 and 7 introduces a new level of subtlety and beauty to the Kamea's architecture. Unlike the pure regions, these complementary families are entangled, sharing their Temples and weaving a web of mutual influence.

#### Table Structure and Assignment

- **Prime (Hierophant):**
  - For Family 5: The Prime is at **Kamea Locator 575** (not at (5,5)).
  - For Family 7: The Prime is at **Kamea Locator 757** (not at (7,7)).
  - These special locations reflect the mirrored, complementary nature of these families.

- **Acolytes:**
  - For Family 5: Acolytes are found in the 5th column, but the Prime is at 575 (column 7, row 5), not (5,5).
  - For Family 7: Acolytes are found in the 7th column, but the Prime is at 757 (column 5, row 7), not (7,7).
  - Each Acolyte at (col, row n) is paired with its conrune twin in the complementary family, and together they "co-parent" the Temples in their shared lineage.

- **Temples:**
  - The Temples in these families are not exclusive to one Acolyte or one family; they are shared between the paired Acolytes of Families 5 and 7.
  - Each Temple is a node of intersection, a place where the energies of both families converge.

#### How to Determine the Temples of an Acolyte (Families 5 & 7)

1. **Identify the Acolyte:**
   - For Family 5: Find the Acolyte in the 5th column, row n (excluding the Prime at 575).
   - For Family 7: Find the Acolyte in the 7th column, row n (excluding the Prime at 757).
2. **Trace the Shared Lineage:**
   - The Temples in column n (for all rows) are "under the care" of both the Family 5 and Family 7 Acolytes at (col, n).
   - The same applies for the corresponding row n.
3. **Visual Flow:**
   - Imagine a web or lattice, not just arrows—each Temple is a point of intersection, a place of shared heritage.

#### Example
- The Acolyte at (column 5, row 3) in Family 5 and the Acolyte at (column 7, row 3) in Family 7 both "co-parent" the Temples in column 3.
- The Prime at 575 (Family 5) and 757 (Family 7) are the ultimate attractors, but every Temple is a child of two lineages.

#### Philosophical Meaning

Families 5 and 7 embody the principle of dynamic balance and mutual arising. Their structure is a living mandala of duality: not stasis, but the harmony that arises from tension, interplay, and mutual reflection. Every Temple is a child of two lineages, a living symbol of the cosmic dance of yin and yang. This entanglement encodes the wisdom that true balance is not found in isolation, but in the embrace and co-creation of opposites.

---

### Temple Assignment in the Bigrammic Quadset (Regions 1, 2, 3, and 6)

The assignment of Temples to Acolytes in regions 1, 2, 3, and 6 reveals the most intricate and dynamic pattern in the Kamea. These four regions form a "bigrammic quadset"—a web of mutual relationships, where lineage is not linear or paired, but woven from fourfold symmetry.

#### Table Structure and Assignment

- **Primes (Hierophants):**
  - Each region has its own Prime, located at a unique Kamea Locator within its table (e.g., for region 1, the Prime is at 111; for region 2, at 222, etc.).
  - These Primes are not isolated—they are part of a fourfold symmetry, each reflecting and relating to the others.

- **Acolytes:**
  - Each region's Acolytes are distributed in a pattern that mirrors the quadset's symmetry.
  - The Acolytes in one region are "entangled" with those in the other three, forming a web of shared influence.

- **Temples:**
  - Temples in these regions are not the exclusive "children" of a single Acolyte or even a single region.
  - Instead, each Temple is a node in a fourfold network, "co-parented" by Acolytes from all four regions.
  - The assignment is not linear or paired, but a true quadset: every Temple is a meeting point of four lineages.

#### How to Determine the Temples of an Acolyte (Quadset Regions)

1. **Identify the Acolyte:**
   - Find the Acolyte in the relevant region's table.
2. **Trace the Quadset Lineage:**
   - The Temples associated with this Acolyte are also associated with three "sibling" Acolytes from the other quadset regions.
   - The lineage forms a closed loop or network, not a straight line or pair.
3. **Visual Flow:**
   - Imagine a web or mesh, where each Temple sits at the intersection of four threads—one from each region.

#### Example

- An Acolyte in region 1 "shares" its Temples with corresponding Acolytes in regions 2, 3, and 6.
- The Prime of each region is the "anchor" for its lineage, but the web is woven from all four.

#### Philosophical Meaning

The bigrammic quadset is the archetype of entanglement, mutuality, and emergence. It encodes the principle that true creation arises not from duality, but from the interplay of many forces—each distinct, yet inseparable from the whole. Every Temple is a living crossroad, a place where four lineages meet and new possibilities are born. This is the field of emergence, the generative matrix where the many become one, and the one becomes many.

*This document is a living draft. Please correct, expand, and connect as needed to fit your evolving system and philosophy.*
