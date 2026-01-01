# The Grimoire of the Document Manager

<!-- Last Verified: 2026-01-01 -->

> *"The Word was written, and the Word became Structure."*

The **Document Manager Pillar** is the Library of Thoth. It is not merely a file storage system, but a **Semantic Web** connecting texts, verses, and concepts into a living Mindscape.

---

## I. The Scroll and the Verse (Theory)

We treat documents not as blobs of text, but as structured hierarchies:
1.  **The Document**: The Container (File).
2.  **The Verse**: The Atomic Unit of Meaning (Sentence/Paragraph).
3.  **The MindNode**: The Conceptual Representation (Graph Node).

This allows us to perform **Granular Analysis**—linking a specific gematria value to a specific verse, not just the whole file.

---

## II. The Ingestion Pipeline

When a scroll is brought to the library, it undergoes **Rites of Entry**:

1.  **Parsing**: Text is extracted from PDF, DOCX, or RTF using `DocumentParser`.
2.  **Verse Segmentation**: The text is broken into verses (auto-detected or manual).
3.  **Indexing**: The content is indexed in **Whoosh** for full-text search.
4.  **Graphing**: A `MindNode` is born to represent the document in the Mindscape.

**Service**: `DocumentService`
- `import_document(path)`: The entry point.
- `search_documents(query)`: Invokes the Whoosh index.

---

## III. The Mindscape (Knowledge Graph)

The **Mindscape** is the neural network of the system.
- **MindNode**: Can be a Document, a Concept, an URL, or a Person.
- **MindEdge**: The connection between nodes (Parent/Child or Associative Jump).

**Visualization**: The `GraphView` renders this web, allowing navigation by association rather than directory structure.

---

## IV. The Verse Teacher

The **VerseTeacherService** acts as the scribe.
- It manages logic for identifying what constitutes a "Verse".
- It handles user annotations and "Truth checking" (validation of verse boundaries).

> *"By the Verse, we measure the Word."*
