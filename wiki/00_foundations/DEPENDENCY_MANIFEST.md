# Dependency Manifest: The Pillars of Support

<!-- Last Verified: 2025-12-27 -->

**"No Temple stands alone; it is supported by the Giants who came before."**

This manifest explains the specific architectural purpose (*The Why*) for every external library integrated into the IsopGem ecosystem. We do not use "convenience" libraries; we use "Foundational" tools.

---

## 1. The Core Infrastructure (The Triad of Power)

### **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/)**
*   **Role**: [Skin/System] - The Manifestation Framework.
*   **The Why**: Provides the cross-platform GUI engine, the **Visual Liturgy** styling system (QSS), and the **Signal/Slot** nervous system that allows our Sovereign Pillars to communicate without Entanglement.

### **[Whoosh](https://whoosh.readthedocs.io/en/latest/)**
*   **Role**: [Memory] - The Akaschic Eye.
*   **The Why**: A pure-Python full-text search engine. It allows the Document Manager to index tens of thousands of manuscripts and perform near-instant keyword searching without the overhead of an external server like Elasticsearch.

### **[SQLAlchemy](https://www.sqlalchemy.org/)**
*   **Role**: [Bone] - The Divine Memory.
*   **The Why**: The industry-standard ORM. It ensures our Python objects (Documents, Calculations, Conversations) are mapped cleanly to the SQLite database. It prevents us from writing raw, fragile SQL strings.

---

## 2. The Astrology Stack (The Chronos Sphere)

### **[pyswisseph](https://pypi.org/project/pyswisseph/) & [openastro2](https://github.com/dimmastro/openastro2)**
*   **Role**: [Muscle] - The Planetary Core.
*   **The Why**: High-precision bindings for the **Swiss Ephemeris**. This is the gold standard for astronomical calculations (132,000-year range). Essential for the Astrology Pillar's chart generation.

### **[Skyfield](https://rhodesmill.org/skyfield/) & [Ephem](https://rhodesmill.org/pyephem/)**
*   **Role**: [Muscle] - The Celestial Verifiers.
*   **The Why**: Secondary engines used to cross-verify the Swiss Ephemeris and provide specialized calculations (e.g., satellite movements, precise eclipse timings) that openastro2 might lack.

---

## 3. The Scribe's Tools (Document Ingestion)

### **[Mammoth](https://pypi.org/project/mammoth/) / [python-docx](https://python-docx.readthedocs.io/)**
*   **Role**: [Translator] - Docx Ingestion.
*   **The Why**: Mammoth is used for clean HTML conversion (preserving semantic structure), while `python-docx` allows for granular manipulation of word documents.

### **[PyMuPDF](https://pymupdf.readthedocs.io/) / [pypdf](https://pypi.org/project/pypdf/)**
*   **Role**: [Translator] - PDF Ingestion.
*   **The Why**: PyMuPDF is selected for its high-speed text extraction and rendering capabilities, while `pypdf` serves as a lightweight alternative for metadata operations.

---

## 4. The Computational Logic (Numerical Harmonics)

### **[NumPy](https://numpy.org/) & [Pandas](https://pandas.pydata.org/)**
*   **Role**: [Muscle] - Heavy Calculation Engines.
*   **The Why**: Used for the **TQ Engine** and large-scale **Gematria** analysis. They allow us to process vectors of numbers with C-like performance, which is vital for detecting patterns in massive textual datasets.

### **[SciPy](https://scipy.org/)**
*   **Role**: [Judge] - Statistical Verification.
*   **The Why**: Provides the complex statistical tests used in the **Rite of the Seal** to verify that detected "patterns" are mathematically significant and not just Pareidolia (random noise).

---

## 5. Linguistic & Esoteric Foundation

### **[Ety](https://pypi.org/project/ety/)**
*   **Role**: [Linguist] - The Etymological Lens.
*   **The Why**: Powers the word-origin features in the Document Manager, allowing the Magus to trace the history of a word across languages.

### **[PyEnchant](https://pyenchant.github.io/pyenchant/)**
*   **Role**: [Editor] - Linguistic Purity.
*   **The Why**: The underlying engine for our spell-checker, supporting custom esoteric dictionaries.

---

## 6. Visualization & Form

### **[Pillow](https://python-pillow.org/)**
*   **Role**: [Skin] - Image Processing.
*   **The Why**: Manages document thumbnails and image assets within the Rich Text Editor.

### **[SVGWrite](https://pypi.org/project/svgwrite/)**
*   **Role**: [Artist] - Vector Manifestation.
*   **The Why**: Renders the crisp, scalable vector charts for Astrology and Geometry.

### **[QtAwesome](https://pypi.org/project/QtAwesome/)**
*   **Role**: [Skin] - Iconography.
*   **The Why**: Enables the use of FontAwesome and other icon fonts within PyQt6, ensuring consistent, scalable, and theme-aware iconography across the entire Visual Liturgy without managing hundreds of pixel-based image files.
