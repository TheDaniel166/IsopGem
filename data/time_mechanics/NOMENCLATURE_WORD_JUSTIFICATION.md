# Nomenclature Word Justification (Tzolkin Structural Tokens)

This document justifies the **wording choices** used in the structural (non–Maya/Aztec) Tzolkin naming system.

The intent here is linguistic/semantic and engineering-oriented: **clarity, consistency, and parseability**.
(Any numerological tuning that may exist elsewhere is explicitly treated as *non-semantic* and optional.)

---

## 1) Design constraints we are satisfying

1. **No imported day-name mythology**
   - We do not use the 20 Maya/Aztec day names.
   - Names must be derivable from *structure* (trigram composition + placement) rather than a cultural calendar label.

2. **Single-string tokens**
   - A cell name must be a single contiguous token suitable for:
     - CSV export,
     - UI labels,
     - deterministic IDs,
     - search and copy/paste.

3. **Composable meaning**
   - Every token is built from a small set of parts with stable semantics:

     $$\text{TOKEN} = \text{RELATION} + \text{CENTRAL\_ARCHETYPE} + \text{ELEMENT\_SUFFIX}$$

4. **Machine-parseable**
   - Fixed prefixes (`HYPO`/`HYPER`, Greek `ΥΠΟ`/`ΥΠΕΡ`) and short suffix sigils (3 letters) minimize ambiguity.

5. **Two parallel representations**
   - **Operator token (ASCII)** for systems/tools that prefer Latin characters.
   - **True token (Greek)** as the canonical, human-facing rendering.

---

## 2) Token anatomy

### 2.1 Relation prefix (placement)

The relation prefix indicates whether the **elemental/polar trigram** is above or below the **central trigram archetype** in the 6-digit ditrune.

- `HYPO` / `ΥΠΟ` — element is **below** (under) the central archetype.
- `HYPER` / `ΥΠΕΡ` — element is **above** (over) the central archetype.

Justification:
- Uses standard Greek-derived prepositions commonly understood in technical English (hypo-/hyper-).
- Encodes the only placement fact we need (upper vs lower) without inventing new terminology.

Sources of truth:
- [Docs/time_mechanics/Nomenclature_Position_Suffixes.csv](Docs/time_mechanics/Nomenclature_Position_Suffixes.csv)

### 2.2 Central archetype (structural identity)

The central archetype names are **project-defined labels** for the 20 non-element/polar trigrams used as the “central” identity.

Justification:
- They function as *semantic handles* for recurring structural patterns.
- English is kept in **PascalCase compound nouns** to avoid spaces and punctuation.
- Greek is kept in **uppercase, no diacritics, no spaces** to remain visually clean and CSV-safe.
- These are not claims of classical attestation; they are **constructed compounds** using familiar morphemes.

Source of truth:
- [Docs/time_mechanics/Nomenclature_Cipher_Archetypes.csv](Docs/time_mechanics/Nomenclature_Cipher_Archetypes.csv)

### 2.3 Element suffix (element/polar identity)

Elemental and polarity trigrams are represented by a compact 3-letter sigil suffix.

Justification:
- Fixed-length suffixes are fast to scan and easy to parse.
- They distinguish **element/polar identity** from the **central archetype** without additional punctuation.
- Greek suffixes are also 3 letters for symmetry and legibility.

Source of truth:
- [Docs/time_mechanics/Nomenclature_Elemental_Trigrams.csv](Docs/time_mechanics/Nomenclature_Elemental_Trigrams.csv)

### 2.4 Non-semantic tags (optional)

Some archetype strings may include a short trailing tag (example: `…ΚΘ`).

Justification:
- Tags are treated as **non-semantic qualifiers** (versioning/disambiguation/check-digit-like markers).
- They are not required for understanding the token’s core meaning.
- Parsers/UX may ignore them unless a workflow explicitly depends on them.

---

## 3) Glossary and intent

### 3.1 Relation prefixes

| Component | Meaning | Rationale |
|---|---|---|
| `HYPO` / `ΥΠΟ` | under/below | standard, compact, placement-precise |
| `HYPER` / `ΥΠΕΡ` | over/above | standard, compact, placement-precise |

### 3.2 Element/polar suffixes

(“Assigned meaning” here means *meaning within this project’s system*.)

| Trigram | Name | Suffix (EN) | Suffix (EL) | Assigned meaning |
|---:|---|---|---|---|
| `001` | Yang | `OMB` | `ΩΜΒ` | ascent / outward impulse |
| `002` | Yin | `KAT` | `ΚΑΤ` | descent / inward return |
| `010` | Fire | `FRO` | `ΦΡΟ` | ignition / catalytic drive |
| `020` | Water | `HYD` | `ΥΔΡ` | flow / dissolution / continuity |
| `100` | Air | `AER` | `ΑΗΡ` | breath / exchange / transmission |
| `200` | EarthElement | `CTH` | `ΧΘΝ` | ground / telluric constraint |

### 3.3 Central archetypes (20)

These names are intended to be:
- descriptive without importing a preexisting mythic day-name set,
- stable as identifiers,
- suggestive enough to support narrative/UI text later.

| Trigram | Stratum | Archetype (EN) | Archetype (EL) | Design intent (plain-language gloss) |
|---:|---|---|---|---|
| `101` | ZODIAC | VernalGate | ΕΑΡΟΠΥΛΗ | “spring threshold / opening” |
| `120` | ZODIAC | EmergentField | ΑΝΑΔΥΠΕΔΙΟ | “something rising into a plane/field” |
| `021` | ZODIAC | TwinCurrent | ΔΙΔΥΜΟΡΡΟΗ | “paired flow / dual stream” |
| `202` | ZODIAC | TidalHearth | ΠΑΛΙΡΡΟΙΕΣΤΙΑ | “rhythmic return anchored at a center” |
| `110` | ZODIAC | SolarCrown | ΗΛΙΟΣΤΕΦΑΝΟΣ | “solar prominence / crowned radiance” |
| `012` | ZODIAC | GranaryKey | ΣΙΤΟΚΛΕΙΣ | “storage, measure, and access” |
| `102` | ZODIAC | BalanceBeam | ΙΣΟΡΡΟΠΟΔΟΚΟΣ | “balance / load distribution” |
| `220` | ZODIAC | DeepCoil | ΒΑΘΥΕΛΙΞΚΘ | “depth, spiral, return through interior” |
| `011` | ZODIAC | ArrowFire | ΤΟΞΟΠΥΡ | “directed ignition / aimed force” |
| `201` | ZODIAC | StoneRoot | ΛΙΘΟΡΙΖΑ | “rooting, anchoring, endurance” |
| `210` | ZODIAC | SkyCircuit | ΟΥΡΑΝΟΚΥΚΛΟΣ | “celestial cycle / aerial loop” |
| `022` | ZODIAC | OceanVeil | ΩΚΕΑΝΟΠΕΠΛΟΣ | “oceanic cover / concealment by vastness” |
| `111` | PLANET | RadiantAxis | ΑΚΤΙΝΟΑΞΩΝ | “ray + axis; orientation by radiance” |
| `222` | PLANET | SilverMirror | ΑΡΓΥΡΟΚΑΤΟΠΤΡΟ | “reflection, reception, lunar mirroring” |
| `121` | PLANET | QuickGlyph | ΤΑΧΥΓΡΑΜΜΑ | “fast sign / quick mark” |
| `122` | PLANET | HarmonicBloom | ΑΡΜΟΝΙΟΑΝΘΟΣ | “patterned opening / harmonic flowering” |
| `221` | PLANET | EdgeForge | ΑΚΡΟΧΑΛΚΕΥΣ | “boundary-work / shaping at the edge” |
| `211` | PLANET | VastLaw | ΜΕΓΑΝΟΜΟΣ | “large rule / expansive order” |
| `112` | PLANET | BoundaryRing | ΟΡΙΟΔΑΚΤΥΛΙΟΣ | “limit-cycle / ring of constraint” |
| `212` | PLANET | WorldSphere | ΚΟΣΜΟΣΦΑΙΡΑ | “world-as-sphere; global enclosure” |

---

## 4) Reading a token (examples)

- Example (Greek true token): `ΥΠΟΟΥΡΑΝΟΚΥΚΛΟΣΦΡΟ`
  - `ΥΠΟ` = element below
  - `ΟΥΡΑΝΟΚΥΚΛΟΣ` = SkyCircuit archetype
  - `ΦΡΟ` = Fire suffix
  - Plain-language: “Fire below SkyCircuit.”

- Example (ASCII operator token): `HYPERWorldSphereCTH`
  - `HYPER` = element above
  - `WorldSphere` = central archetype
  - `CTH` = EarthElement
  - Plain-language: “EarthElement above WorldSphere.”

---

## 5) What this nomenclature is (and is not)

- **Is:** a compositional vocabulary for Tzolkin cells derived from ditrune structure.
- **Is:** stable identifiers suitable for export, indexing, UI, and cross-referencing.
- **Is not:** a claim of historical Greek orthography or a replacement for any traditional calendar.
- **Is not:** dependent on numerology for its semantic interpretation.
