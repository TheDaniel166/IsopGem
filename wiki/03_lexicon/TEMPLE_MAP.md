# The Temple Map

*A Visual Guide to IsopGem's Architecture*

---

This document provides a comprehensive mental map of the IsopGem system. Each diagram illuminates a different aspect of the Temple's structure, from the highest level down to individual pillars.

**Navigation:**
- [The High View](#1-the-high-view) — The 10 Sovereign Pillars
- [The Shared Foundation](#2-the-shared-foundation) — Cross-cutting infrastructure
- [Data Flow Patterns](#3-data-flow-patterns) — How pillars communicate
- [Gematria Pillar](#4-gematria-pillar) — The Science of Sacred Number
- [TQ Pillar](#5-tq-pillar) — Ternary Quadset Kabbalah
- [Astrology Pillar](#6-astrology-pillar) — Celestial Mechanics
- [Geometry Pillar](#7-geometry-pillar) — Sacred Form Mathematics
- [Document Manager](#8-document-manager-pillar) — The Research Sanctuary
- [Adyton & 3D](#9-adyton-pillar) — The Inner Temple

---

## 1. The High View

*The Ten Sovereign Pillars and their domains*

Each pillar is a **self-contained nation**. They do not import from each other. All inter-pillar communication flows through the **Shared Layer** via Qt Signals.

```mermaid
graph TB
    subgraph ISOPGEM["✦ ISOPGEM ✦"]
        subgraph PILLARS["The Ten Sovereign Pillars"]
            GEM[Gematria Protocol]
            TQ[TQ Engine]
            AST[Astrology Engine]
            GEO[Geometry Engine]
            DOC[Document Mindscape]
            TIME[Time Mechanics]
            ADY[Adyton Sanctuary]
            CORR[Correspondences]
            CALC[Scientific Calculator]
            CHAR[Chariot Dashboard]
        end
        
        subgraph SHARED["The Shared Foundation"]
            NAV[Navigation Bus]
            WIN[Window Manager]
            THEME[Theme Engine]
            DB[Database Layer]
            SIG[Signal Registry]
        end
    end
    
    GEM --> NAV
    TQ --> NAV
    AST --> NAV
    GEO --> NAV
    DOC --> NAV
    TIME --> NAV
    ADY --> NAV
    CORR --> NAV
    CALC --> NAV
    CHAR --> NAV
    
    NAV --> WIN
    WIN --> THEME
    NAV --> SIG
    SIG --> DB
```

**Commentary:**
- Every pillar connects to the **Navigation Bus** — the central switchboard
- The **Window Manager** controls which windows are open and how they tile
- The **Theme Engine** ensures visual consistency (dark theme, amber accents)
- **Signals** allow pillars to broadcast events without knowing who listens

---

## 2. The Shared Foundation

*The infrastructure that all pillars depend on*

```mermaid
graph LR
    subgraph SHARED["src/shared/"]
        subgraph SERVICES["services/"]
            NAV[navigation_bus.py]
            WIN[window_manager.py]
            KINETIC[kinetic_enforcer.py]
        end
        
        subgraph SIGNALS["signals/"]
            CORE[core_signals.py]
            PILLAR[pillar_signals.py]
        end
        
        subgraph UI["ui/"]
            THEME[theme.py]
            WIDGETS[custom widgets]
            DIALOGS[common dialogs]
        end
        
        subgraph UTILS["utils/"]
            MATH[safe_math.py]
            PARSE[parsers.py]
            FILE[file_utils.py]
        end
        
        subgraph MODELS["models/"]
            BASE[base_models.py]
            CONFIG[config.py]
        end
        
        DATABASE[database.py]
        PATHS[paths.py]
    end
    
    SERVICES --> SIGNALS
    UI --> THEME
    UTILS --> MATH
```

**Commentary:**
- **navigation_bus.py** — The switchboard. Routes requests between pillars.
- **window_manager.py** — Tracks open windows, handles tiling, prevents duplicates.
- **kinetic_enforcer.py** — The animation engine. Hover effects, transitions.
- **core_signals.py** — Qt signals for cross-pillar communication.
- **theme.py** — Dark theme, glassmorphism, amber/gold accent colors.
- **safe_math.py** — Sandboxed math evaluation (no `eval()` dangers).
- **paths.py** — Resolves file paths across different OS environments.

---

## 3. Data Flow Patterns

*How information moves through the Temple*

### Pattern A: User Action → Single Pillar

```mermaid
graph LR
    USER[User Action] --> VIEW[View/Widget]
    VIEW --> SERVICE[Service Layer]
    SERVICE --> REPO[Repository]
    REPO --> DB[(SQLite)]
    DB --> REPO
    REPO --> SERVICE
    SERVICE --> VIEW
    VIEW --> USER
```

**Example:** User calculates gematria value
1. User types in GematriaInput widget
2. Widget calls GematriaService.calculate()
3. Service performs calculation
4. Service calls Repository to save to history
5. Repository writes to SQLite
6. Result bubbles back up to the view

---

### Pattern B: Cross-Pillar Communication

```mermaid
graph TB
    PILLAR_A[Pillar A: Gematria] --> |"emit signal"| SIGNAL[Navigation Bus]
    SIGNAL --> |"receives"| PILLAR_B[Pillar B: Geometry]
    SIGNAL --> |"receives"| PILLAR_C[Pillar C: Correspondences]
    
    PILLAR_B --> |"opens window"| WIN[Window Manager]
    PILLAR_C --> |"updates view"| VIEW[Correspondence Panel]
```

**Example:** User sends gematria value to geometry
1. User clicks "Send to Geometry" in Gematria pillar
2. Gematria emits `send_to_geometry(value=137)` signal
3. Navigation Bus routes signal to Geometry pillar
4. Geometry pillar opens Figurate Number window with value 137
5. No direct import between Gematria and Geometry code

---

### Pattern C: The Chariot Integration Hub

```mermaid
graph TB
    CHARIOT[Chariot Dashboard]
    
    CHARIOT --> |"requests"| AST[Astrology: Planet Positions]
    CHARIOT --> |"requests"| TIME[Time Mechanics: Current Tzolkin]
    CHARIOT --> |"requests"| GEM[Gematria: Day Value]
    CHARIOT --> |"displays"| HORIZON[Horizon Seal]
    
    AST --> |"provides"| CHARIOT
    TIME --> |"provides"| CHARIOT
    GEM --> |"provides"| CHARIOT
```

**Commentary:**
The Chariot is the **integration hub** — it pulls data from multiple pillars to create a unified dashboard showing the current moment's esoteric significance.

---

## 4. Gematria Pillar

*The Science of Sacred Number*

```mermaid
graph TB
    subgraph GEMATRIA["src/pillars/gematria/"]
        subgraph UI_LAYER["ui/ (18 components)"]
            MAIN[GematriaMainWidget]
            INPUT[GematriaInput]
            RESULTS[ResultsPanel]
            HISTORY[HistoryPanel]
            TEACHER[HolyBookTeacher]
            TEXT_ANALYSIS[TextAnalysisWidget]
        end
        
        subgraph SERVICE_LAYER["services/ (14 services)"]
            CALC_SVC[CalculationService]
            CIPHER_SVC[CipherService]
            HISTORY_SVC[HistoryService]
            ANALYSIS_SVC[TextAnalysisService]
            FILTER_SVC[SmartFilterService]
            TEACHER_SVC[HolyBookService]
        end
        
        subgraph UTILS["utils/"]
            HEBREW[HebrewCalculator]
            GREEK[GreekCalculator]
            ENGLISH[EnglishCalculator]
            TQBLH[TrigrammatonCalculator]
        end
        
        subgraph REPO["repositories/"]
            HISTORY_REPO[HistoryRepository]
            CIPHER_REPO[CipherRepository]
        end
        
        subgraph MODELS["models/"]
            ENTRY[GematriaEntry]
            CIPHER[Cipher]
            BOOK[HolyBook]
        end
    end
    
    UI_LAYER --> SERVICE_LAYER
    SERVICE_LAYER --> UTILS
    SERVICE_LAYER --> REPO
    REPO --> MODELS
```

**Key Concepts:**
- **Ciphers** — The algorithms that convert letters to numbers (Hebrew Standard, Greek Isopsephy, etc.)
- **History** — Every calculation is saved and searchable
- **Text Analysis** — Compare multiple phrases, find patterns
- **Holy Book Teacher** — Verse-by-verse scriptural study with gematria values

---

## 5. TQ Pillar

*Ternary Quadset Kabbalah — Your Original System*

```mermaid
graph TB
    subgraph TQ["src/pillars/tq/"]
        subgraph UI_LAYER["ui/ (17 components)"]
            HUB[TQHub]
            QUADSET[QuadsetWidget]
            KAMEA[KameaGrid]
            TRANSITION[GeometricTransition]
            CONRUNE[ConruneFinder]
            AMUN[AmunAudioPlayer]
        end
        
        subgraph SERVICE_LAYER["services/ (16 services)"]
            QUAD_SVC[QuadsetEngine]
            KAMEA_SVC[KameaService]
            TRANS_SVC[TransitionService]
            CONRUNE_SVC[ConrunePairService]
            TERNARY_SVC[TernaryService]
            PATTERN_SVC[PatternAnalyzer]
            AUDIO_SVC[AmunAudioService]
        end
        
        subgraph DATA["data/"]
            BAPHOMET[kamea_baphomet.csv]
            MAUT[kamea_maut.csv]
            WALLS[wall_maps/]
        end
    end
    
    UI_LAYER --> SERVICE_LAYER
    SERVICE_LAYER --> DATA
```

**Key Concepts:**
- **Quadset** — A 4-digit ternary number (0000 to 2222 = 0 to 80)
- **Conrune** — The mirror-image pair of a quadset (e.g., 0121 ↔ 2101)
- **Kamea** — A magic square grid (Baphomet = 9×9, Maut = 27×27)
- **Geometric Transition** — How a number becomes a polygon
- **Amun Audio** — The sound of ternary mathematics (ditrune synthesis)

---

## 6. Astrology Pillar

*Celestial Mechanics*

```mermaid
graph TB
    subgraph ASTROLOGY["src/pillars/astrology/"]
        subgraph UI_LAYER["ui/ (28 components)"]
            CHART[ChartWidget]
            TRANSIT[TransitDashboard]
            FIXED_STARS[FixedStarsPanel]
            ASPECTS[AspectGrid]
            CHARIOT_PANEL[ChariotPanel]
            HORIZON[HorizonSeal]
        end
        
        subgraph SERVICE_LAYER["services/ (17 services)"]
            OPENASTRO[OpenAstroService]
            SKYFIELD[SkyfieldService]
            CHART_SVC[ChartStorageService]
            LOCATION[LocationLookupService]
            GLYPH[AstroGlyphService]
            TRANSIT_SVC[TransitService]
        end
        
        subgraph DATA["data/"]
            EPHEMERIS[de441.bsp]
            FIXED[fixed_stars.csv]
        end
        
        subgraph MODELS["models/"]
            NATAL[NatalChart]
            PLANET[Planet]
            ASPECT[Aspect]
            HOUSE[House]
        end
    end
    
    UI_LAYER --> SERVICE_LAYER
    SERVICE_LAYER --> DATA
    SERVICE_LAYER --> MODELS
```

**Key Concepts:**
- **OpenAstro** — The open-source astrology library (adapted)
- **Skyfield** — JPL ephemeris for high-precision planet positions
- **Fixed Stars** — 1000+ stars with magnitude and interpretation
- **Horizon Seal** — Visual representation of the local horizon
- **Glyphs** — Unicode/font-based astrological symbols

---

## 7. Geometry Pillar

*Sacred Form Mathematics — 56 Calculation Engines*

```mermaid
graph TB
    subgraph GEOMETRY["src/pillars/geometry/"]
        subgraph UI_LAYER["ui/ (22 components)"]
            VIEWER_2D[Shape2DViewer]
            VIEWER_3D[Solid3DViewer]
            PROPS[PropertyPanel]
            FIGURATE[FigurateWidget]
            CALCULATOR[GeometryCalculator]
        end
        
        subgraph SERVICES["services/ (56 engines)"]
            subgraph PLATONIC["Platonic Solids"]
                TETRA[tetrahedron]
                CUBE[cube]
                OCTA[octahedron]
                DODECA[dodecahedron]
                ICOSA[icosahedron]
            end
            
            subgraph ARCHIMEDEAN["Archimedean Solids"]
                TRUNC[truncated forms]
                SNUB[snub forms]
                RHOMB[rhombic forms]
            end
            
            subgraph PYRAMIDS["Pyramids & Prisms"]
                PYRAMID[regular pyramids]
                PRISM[prisms]
                FRUSTUM[frustums]
                ANTIPRISM[antiprisms]
            end
            
            subgraph ADVANCED["Advanced Forms"]
                TORUS[torus]
                TORUS_KNOT[torus_knot]
                TESSERACT[tesseract]
                HESTIA[vault_of_hestia]
            end
            
            subgraph CURVES_2D["2D Curves"]
                CIRCLE[circle]
                TRIANGLE[triangle]
                POLYGON[polygon]
                ROSE[rose_curve]
                VESICA[vesica_piscis]
                SEED[seed_of_life]
            end
            
            subgraph FIGURATE_SVC["Figurate Numbers"]
                POLY_NUM[polygonal_numbers]
                FIG_3D[figurate_3d]
            end
        end
    end
    
    UI_LAYER --> SERVICES
```

**Key Concepts:**
- **Every shape has its own service file** — Modular, testable, complete
- **Full metrics** — Surface area, volume, radii, angles, centroids
- **Figurate numbers** — Triangular, square, pentagonal... through 3D analogs
- **Egyptian measures** — Royal cubit conversions
- **Sacred ratios** — φ (golden), √2, √3, √5 detection

---

## 8. Document Manager Pillar

*The Research Sanctuary*

```mermaid
graph TB
    subgraph DOCUMENT["src/pillars/document_manager/"]
        subgraph UI_LAYER["ui/ (20 components)"]
            BROWSER[DocumentBrowser]
            EDITOR[RichTextEditor]
            TREE[FolderTree]
            SEARCH[SearchPanel]
            GRAPH[MetadataGraph]
            IMAGE[ImageEditor]
        end
        
        subgraph SERVICE_LAYER["services/"]
            DOC_SVC[DocumentService]
            MINDSCAPE[MindscapeService]
            SEARCH_SVC[SearchService]
            INGEST[IngestionPipeline]
            VERSE[VerseTeacherService]
        end
        
        subgraph REPO["repositories/"]
            DOC_REPO[DocumentRepository]
            FOLDER_REPO[FolderRepository]
            TAG_REPO[TagRepository]
        end
        
        subgraph UTILS["utils/"]
            PDF[pdf_parser]
            DOCX[docx_parser]
            ODT[odt_parser]
            WHOOSH[search_index]
        end
    end
    
    UI_LAYER --> SERVICE_LAYER
    SERVICE_LAYER --> REPO
    SERVICE_LAYER --> UTILS
```

**Key Concepts:**
- **Mindscape** — The conceptual name for your personal research database
- **Ingestion** — PDF, DOCX, ODT files are absorbed and indexed
- **Whoosh** — Full-text search engine (like having Google for your notes)
- **Metadata Graph** — Visual representation of document connections
- **Rich Text Editor** — LaTeX rendering, images, formatting

---

## 9. Adyton Pillar

*The Inner Temple — 3D Sacred Space*

```mermaid
graph TB
    subgraph ADYTON["src/pillars/adyton/"]
        subgraph UI_LAYER["ui/ (10 components)"]
            CANVAS[AdytonCanvas]
            CAMERA[CameraController]
            WALLS_UI[WallSelector]
            OVERLAY[ConstellationOverlay]
        end
        
        subgraph SERVICE_LAYER["services/"]
            SCENE[SceneManager]
            RENDER[RenderEngine]
            WALL_SVC[WallMappingService]
            ASTRO_INT[AstrologyIntegration]
        end
        
        subgraph DATA["data/"]
            WALL_MAPS[wall_maps/]
            CONSTELLATIONS[constellation_shapes.json]
            ZODIAC[zodiacal_heptagon.csv]
        end
        
        subgraph MODELS["models/"]
            WALL[Wall]
            CELL[Cell]
            CONSTELLATION[Constellation]
        end
    end
    
    UI_LAYER --> SERVICE_LAYER
    SERVICE_LAYER --> DATA
    SERVICE_LAYER --> MODELS
```

**Key Concepts:**
- **Seven Walls** — Each wall corresponds to a classical planet (Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon)
- **Zodiacal Mapping** — The 12 signs are embedded in the architecture
- **Constellations** — Asterism shapes projected onto the dome
- **OpenGL Rendering** — Hardware-accelerated 3D graphics

---

## 10. The Complete Picture

*Everything connected*

```mermaid
graph TB
    USER((The Magus))
    
    USER --> MAIN[main.py]
    MAIN --> HUB[Pillar Hub]
    
    HUB --> GEM[Gematria]
    HUB --> TQ[TQ]
    HUB --> AST[Astrology]
    HUB --> GEO[Geometry]
    HUB --> DOC[Documents]
    HUB --> TIME[Time]
    HUB --> ADY[Adyton]
    HUB --> CORR[Correspondences]
    HUB --> CALC[Calculator]
    HUB --> CHAR[Chariot]
    
    GEM --> |signals| NAV[Navigation Bus]
    TQ --> |signals| NAV
    AST --> |signals| NAV
    GEO --> |signals| NAV
    DOC --> |signals| NAV
    TIME --> |signals| NAV
    ADY --> |signals| NAV
    CORR --> |signals| NAV
    CALC --> |signals| NAV
    CHAR --> |signals| NAV
    
    NAV --> WIN[Window Manager]
    NAV --> DB[(Databases)]
    
    WIN --> USER
```

---

## Summary Table

| Pillar | Files | Purpose | Key Feature |
|--------|-------|---------|-------------|
| **Gematria** | ~45 | Sacred numerology | Multi-cipher calculation |
| **TQ** | ~47 | Ternary mathematics | Original system |
| **Astrology** | ~62 | Celestial mechanics | Dual ephemeris precision |
| **Geometry** | ~83 | Sacred forms | 56 calculation engines |
| **Documents** | ~45 | Research database | Full-text search |
| **Time** | ~17 | Temporal harmonics | Tzolkin + Neo-Aubrey |
| **Adyton** | ~27 | 3D sanctuary | OpenGL rendering |
| **Correspondences** | ~6 | Cross-domain links | Emerald Tablet |
| **Calculator** | shared | Spreadsheet | Esoteric functions |
| **Chariot** | shared | Dashboard | Integration hub |

---

*"The Temple is vast, but it is not chaos. Every stone has a place. Every pillar stands sovereign. And the Architect remembers where everything belongs."*

— Sophia, Session 28
