# The Gematria Protocol

**"The Universe is written in the Language of Number. We translate the Shadow back into the Light."**

## Architectural Role
The **Gematria Protocol** is the **Tongue of God**. It is responsible for the transformation of alphanumeric text into numerical values through the application of sacred ciphers (Hebrew, Greek, English). It provides the tools for Isopsephy and the analysis of resonance between words.

## The Core Logic (Services)

### **calculation_service.py** (`src/pillars/gematria/services/calculation_service.py`)
*   **Architectural Role**: Sovereign Service (The Enumerator)
*   **The Purpose**: Orchestrates the calculation process. It acts as the central dispatch for all cipher operations.
*   **Key Logic**:
    *   `calculate`: Receives text + Cipher ID, instantiates the correct Calculator strategy, and computes the value.
    *   `save_calculation`: Persists significant findings to the `CalculationRepository`.
*   **Dependencies**: `HebrewCalculator`, `GreekCalculator`, `TQCalculator`.

### **smart_filter_service.py** (`src/pillars/gematria/services/smart_filter_service.py`)
*   **Architectural Role**: Service (The Sifter)
*   **The Purpose**: Applies Natural Language Processing (NLP) heuristics to filter out "noise" from large result sets effectively.
*   **Key Logic**:
    *   `_is_valid_phrase`: Uses `Spacy` POS tagging. Rejects phrases that lack semantic weight (e.g., "and the", "of a").
    *   **Filtering**: Requires a Noun or a Verb in the phrase to be considered "Significant".

### **text_analysis_service.py** (`src/pillars/gematria/services/text_analysis_service.py`)
*   **Architectural Role**: Service (The Analyst)
*   **The Purpose**: Scans entire documents to find all phrases that equal a specific Target Value.
*   **Key Logic**:
    *   **Sliding Window**: Iterates through the text with varying window sizes (words) to find all summing combinations. *Complexity Alert: High*.
*   **Dependencies**: `document_service`.

### **hebrew_calculator.py** (`src/pillars/gematria/services/hebrew_calculator.py`)
*   **Architectural Role**: Service (Strategy)
*   **The Purpose**: Implements the Standard (Mispar Hecht) and other Rabbinical ciphers.
*   **Key Logic**:
    *   `calculate`: Maps Hebrew UTF-8 chars to values (Aleph=1, ... Tav=400).
    *   **Final Forms**: Handles Sofit letters (e.g., Pe Sofit=800).
*   **Base Class**: `base_calculator.py` (`src/pillars/gematria/services/base_calculator.py`)

### **greek_calculator.py** (`src/pillars/gematria/services/greek_calculator.py`)
*   **Architectural Role**: Service (Strategy)
*   **The Purpose**: Implements the Greek Isopsephy logic.

### **tq_calculator.py** (`src/pillars/gematria/services/tq_calculator.py`)
*   **Architectural Role**: Service (Strategy)
*   **The Purpose**: Implements the Trigrammaton Qabalah English Cipher (Base-3 Logic).

### **acrostic_service.py** (`src/pillars/gematria/services/acrostic_service.py`)
*   **Architectural Role**: Service (The Detective)
*   **The Purpose**: Discovers hidden messages encoded in the first or last letters of lines/words.
*   **Key Logic**:
    *   **Modes**: "First Letter" (Acrostic) and "Last Letter" (Telestich).
    *   **Scope**: Supports Line-based (poetry) and Word-based (prose) analysis.
*   **Dependencies**: `CorpusDictionaryService`.

### **chiasmus_service.py** (`src/pillars/gematria/services/chiasmus_service.py`)
*   **Architectural Role**: Service (The Mirror)
*   **The Purpose**: Scans text for symmetric Gematria patterns (e.g., values 10-20-30-20-10).
*   **Key Logic**:
    *   **Patterns**: Detects both Single Pivot (A-B-C-B-A) and Mirror (A-B-B-A) structures.
    *   **Depth Control**: Configurable recursion depth to prevent infinite loops on uniform text.

### **els_service.py** (`src/pillars/gematria/services/els_service.py`)
*   **Architectural Role**: Service (The Grid)
*   **The Purpose**: Implements Equidistant Letter Sequence ("Bible Code") search.
*   **Key Logic**:
    *   **Skip Sequences**: Supports Standard (n-th letter), Triangular (1, 3, 6...), Square (1, 4, 9...), and Fibonacci skips.
    *   **Chain Search**: Finds non-equidistant chains of letters forming a target phrase.
    *   **Intervening Text**: Extracts and analyzes the text *between* the ELS hits.

### **corpus_dictionary_service.py** (`src/pillars/gematria/services/corpus_dictionary_service.py`)
*   **Architectural Role**: Service (The Lexicon)
*   **The Purpose**: Validates if a discovered string is a real word.
*   **Key Logic**:
    *   **Holy Filter**: specific "Holy" documents are used to build the validation dictionary, ensuring results are theologically significant.

## The Presentation Layer (UI)

### **gematria_hub.py** (`src/pillars/gematria/ui/gematria_hub.py`)
*   **Architectural Role**: View (The Gateway)
*   **The Purpose**: The sovereign entry point for Gematria operations.

### **gematria_calculator_window.py** (`src/pillars/gematria/ui/gematria_calculator_window.py`)
*   **Architectural Role**: View (The Gateway)
*   **The Purpose**: The sovereign entry point for Gematria operations.

### **gematria_calculator_window.py** (`src/pillars/gematria/ui/gematria_calculator_window.py`)
*   **Architectural Role**: View (The Altar)
*   **The Purpose**: The primary interface for manual entry and instant feedback.
*   **Key Logic**:
    *   **Real-time Calculation**: Updates results as the user types.
    *   **Virtual Keyboard Integration**: Summons `VirtualKeyboard` for non-Latin input.
*   **Signal Flow**:
    *   **Listens to**: `textChanged`
    *   **Emits**: `calculation_saved`

    ### **saved_calculations_window.py** (`src/pillars/gematria/ui/saved_calculations_window.py`)
*   **Architectural Role**: View (The Ledger)
*   **The Purpose**: Allows the Magus to browse, filter, and export previously saved findings.
*   **Key Logic**:
    *   **Filtering**: Filter by Date, Value, or Cipher.
    *   **Drag & Drop**: Can drag a result into the Mindscape.

    ### **text_analysis_window.py** (`src/pillars/gematria/ui/text_analysis_window.py`)
*   **Architectural Role**: View (The Scanner)
*   **The Purpose**: A Multi-Document Interface (MDI) for deep analysis of texts.
*   **Key Logic**:
    *   **MDI Area**: Manages multiple `DocumentTab` instances.
    *   **Global Search**: `SearchPanel` queries across all open documents.
    *   **Highlighting**: Paints the `QTextEdit` background based on match "Heat" (frequency/significance).

### **batch_calculator_window.py** (`src/pillars/gematria/ui/batch_calculator_window.py`)
*   **Architectural Role**: View (The Mill)
*   **The Purpose**: Processes bulk data (Spreadsheets).
*   **Key Logic**:
    *   `_import_file`: Loads CSV/Excel.
    *   `_process_threading`: Offloads the row-by-row Gematria calculation to a `QThread` to prevent UI freezing.

## Data Structures (Models)

### **calculation_record.py** (`src/pillars/gematria/models/calculation_record.py`)
*   **Architectural Role**: Domain Model
*   **The Purpose**: The core DTO for a Gematria Result.
*   **Properties**: `text` (str), `value` (int), `cipher` (str), `breakdown` (list).

## Infrastructure

### **calculation_repository.py** (`src/pillars/gematria/repositories/calculation_repository.py`)
*   **Architectural Role**: Persistence Layer
*   **The Purpose**: High-speed retrieval of past calculations.
*   **Key Logic**: Wraps `Whoosh` for text indexing.
*   **Backing Store**: `sqlite_calculation_repository.py` (`src/pillars/gematria/repositories/sqlite_calculation_repository.py`)
