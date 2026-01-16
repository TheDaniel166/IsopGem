# Adyton Wall Color Assignment Process

This document explains how colors are assigned to each face of a frustum on the Adyton walls.

## Frustum Structure

Each cell on an 8×13 wall grid is a **frustum** — a truncated pyramid with 5 visible faces:

```
         ┌─────────┐ ← Top Face (trigram based)
        /│         │\
       / │ CENTER  │ \  ← Left Face (planet based)
      /  │ (full   │  \    Right Face (zodiac based)
     │   │ hexagram)│   │
     └───┴─────────┴───┘ ← Bottom Face (trigram based)
```

---

## Step 1: Get the Decimal Value

Each frustum position `(row, col)` on a wall has a **decimal value** stored in the wall CSV file.

**Source Files:**
- `sun_wall.csv`, `mercury_wall.csv`, `luna_wall.csv`, `venus_wall.csv`, `jupiter_wall.csv`, `mars_wall.csv`, `saturn_wall.csv`

---

## Step 2: Convert Decimal to 6-Digit Ternary

The decimal value is converted to a **6-digit ternary string** (padded with leading zeros).

**Example:** Decimal `7` → Ternary `000021`

---

## Step 3: Assign Center Color (Baphomet Method)

The **center face** uses the full 6-digit ternary to calculate an RGB color using the **Baphomet Color System**:

| Channel | Digits | Formula |
|---------|--------|---------|
| **Red** | d1 + d6 | `STEP_MAP[d1 + d6]` |
| **Green** | d2 + d5 | `STEP_MAP[d2 + d5]` |
| **Blue** | d3 + d4 | `STEP_MAP[d3 + d4]` |

**STEP_MAP:**
```
"00" → 0,   "01" → 60,  "02" → 97,  "10" → 60,
"11" → 97, "12" → 194, "20" → 97, "21" → 194, "22" → 254
```

**Example:** `000021` → Red=(d1+d6)=0+1=01=60, Green=(d2+d5)=0+2=02=97, Blue=(d3+d4)=0+0=00=0 → RGB(60, 97, 0)

---

## Step 4: Assign Top/Bottom Face Colors (Trigram Method)

Split the 6-digit ternary into two **trigrams**:
- **Top Trigram** = first 3 digits (d1, d2, d3)
- **Bottom Trigram** = last 3 digits (d4, d5, d6)

Convert each trigram to its **decimal value** and look up the color in `trigram_color.csv`:

| Row | Trigram | RGB | Glyph |
|-----|---------|-----|-------|
| Top Face | `000` = 0 | (194,194,194) | ⁝ |
| Bottom Face | `021` = 7 | (254,97,0) | ♊ |

---

## Step 5: Assign Left Face Color (Planet Method)

The **left face** color is based on the **row position** and the **wall's ruling planet**.

**Planet Order (wall index 0-6):**
```
0: Sun, 1: Mercury, 2: Moon, 3: Venus, 4: Jupiter, 5: Mars, 6: Saturn
```

**Planet Color Codes:**
| Planet | Trigram Code |
|--------|--------------|
| Sun | 13 |
| Saturn | 14 |
| Mercury | 16 |
| Venus | 17 |
| Jupiter | 22 |
| Mars | 25 |
| Moon | 26 |

**Row-to-Planet Mapping:**
| Row | Offset | Planet Selection |
|-----|--------|------------------|
| 0 | -3 | 3 walls counterclockwise |
| 1 | -2 | 2 walls counterclockwise |
| 2 | -1 | 1 wall counterclockwise |
| 3-4 | 0 | Ruling planet of this wall |
| 5 | +1 | 1 wall clockwise |
| 6 | +2 | 2 walls clockwise |
| 7 | +3 | 3 walls clockwise |

**Example:** Wall 0 (Sun), Row 6 → offset +2 → planet index (0+2)%7 = 2 = Moon → code 26

---

## Step 6: Assign Right Face Color (Zodiac Method)

The **right face** color is based on the **column position**.

**Zodiac Cycle (repeating for 13 columns):**
```
Col 0: Aries (10), Col 1: Virgo (15), Col 2: Gemini (7), Col 3: Scorpio (20),
Col 4: Leo (12), Col 5: Pisces (5), Col 6: [RULING PLANET], Col 7: Libra (11),
Col 8: Scorpio (24), Col 9: Sagittarius (4), Col 10: Capricorn (19),
Col 11: Aquarius (21), Col 12: Pisces (8)
```

**Center Column (6):** Uses the wall's **ruling planet** color instead of zodiac.

---

## Color Resolution Summary

| Face | Source | Lookup Key |
|------|--------|------------|
| **Center** | BaphometColorService | Full 6-digit ternary |
| **Top** | trigram_color.csv | Top trigram decimal (0-26) |
| **Bottom** | trigram_color.csv | Bottom trigram decimal (0-26) |
| **Left** | trigram_color.csv → planet code | Row position + wall index |
| **Right** | trigram_color.csv → zodiac code | Column position |

---

## Source Files

| File | Purpose |
|------|---------|
| `trigram_color.csv` | Maps trigram decimal (0-26) to RGB + glyph |
| `left_face_planet_map.csv` | Documents row-to-planet offset rules |
| `FrustumColorService` | Python service implementing all color logic |
| `BaphometColorService` | Calculates center color from 6-digit ternary |
