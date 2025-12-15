# The Gematria Protocol

**"The Universe is written in the Language of Number. We translate the Shadow back into the Light."**

## Architectural Role
The **Gematria Protocol** is the **Tongue of God**. It is responsible for the transformation of alphanumeric text into numerical values through the application of sacred ciphers (Hebrew, Greek, English). It provides the tools for Isopsephy and the analysis of resonance between words.

## The Core Logic (Services)

### **[calculation_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/services/calculation_service.py)**
*   **Architectural Role**: Sovereign Service (The Enumerator)
*   **The Purpose**: Orchestrates the calculation process. It acts as the central dispatch for all cipher operations.
*   **Key Logic**:
    *   `calculate`: Receives text + Cipher ID, instantiates the correct Calculator strategy, and computes the value.
    *   `save_calculation`: Persists significant findings to the `CalculationRepository`.
*   **Dependencies**: `HebrewCalculator`, `GreekCalculator`, `TQCalculator`.

### **[smart_filter_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/services/smart_filter_service.py)**
*   **Architectural Role**: Service (The Sifter)
*   **The Purpose**: Applies Natural Language Processing (NLP) heuristics to filter out "noise" from large result sets effectively.
*   **Key Logic**:
    *   `_is_valid_phrase`: Uses `Spacy` POS tagging. Rejects phrases that lack semantic weight (e.g., "and the", "of a").
    *   **Filtering**: Requires a Noun or a Verb in the phrase to be considered "Significant".

### **[text_analysis_service.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/services/text_analysis_service.py)**
*   **Architectural Role**: Service (The Analyst)
*   **The Purpose**: Scans entire documents to find all phrases that equal a specific Target Value.
*   **Key Logic**:
    *   **Sliding Window**: Iterates through the text with varying window sizes (words) to find all summing combinations. *Complexity Alert: High*.
*   **Dependencies**: `document_service`.

### **[hebrew_calculator.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/services/hebrew_calculator.py)**
*   **Architectural Role**: Service (Strategy)
*   **The Purpose**: Implements the Standard (Mispar Hecht) and other Rabbinical ciphers.
*   **Key Logic**:
    *   `calculate`: Maps Hebrew UTF-8 chars to values (Aleph=1, ... Tav=400).
    *   **Final Forms**: Handles Sofit letters (e.g., Pe Sofit=800).
*   **Base Class**: `[base_calculator.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/services/base_calculator.py)`

### **[greek_calculator.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/services/greek_calculator.py)**
*   **Architectural Role**: Service (Strategy)
*   **The Purpose**: Implements the Greek Isopsephy logic.

### **[tq_calculator.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/services/tq_calculator.py)**
*   **Architectural Role**: Service (Strategy)
*   **The Purpose**: Implements the Trigrammaton Qabalah English Cipher (Base-3 Logic).

## The Presentation Layer (UI)

### **[gematria_hub.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/ui/gematria_hub.py)**
*   **Architectural Role**: View (The Gateway)
*   **The Purpose**: The sovereign entry point for Gematria operations.

### **[gematria_calculator_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/ui/gematria_calculator_window.py)**
*   **Architectural Role**: View (The Gateway)
*   **The Purpose**: The sovereign entry point for Gematria operations.

### **[gematria_calculator_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/ui/gematria_calculator_window.py)**
*   **Architectural Role**: View (The Altar)
*   **The Purpose**: The primary interface for manual entry and instant feedback.
*   **Key Logic**:
    *   **Real-time Calculation**: Updates results as the user types.
    *   **Virtual Keyboard Integration**: Summons `VirtualKeyboard` for non-Latin input.
*   **Signal Flow**:
    *   **Listens to**: `textChanged`
    *   **Emits**: `calculation_saved`

### **[saved_calculations_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/ui/saved_calculations_window.py)**
*   **Architectural Role**: View (The Ledger)
*   **The Purpose**: Allows the Magus to browse, filter, and export previously saved findings.
*   **Key Logic**:
    *   **Filtering**: Filter by Date, Value, or Cipher.
    *   **Drag & Drop**: Can drag a result into the Mindscape.

### **[text_analysis_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/ui/text_analysis_window.py)**
*   **Architectural Role**: View (The Scanner)
*   **The Purpose**: A Multi-Document Interface (MDI) for deep analysis of texts.
*   **Key Logic**:
    *   **MDI Area**: Manages multiple `DocumentTab` instances.
    *   **Global Search**: `SearchPanel` queries across all open documents.
    *   **Highlighting**: Paints the `QTextEdit` background based on match "Heat" (frequency/significance).

### **[batch_calculator_window.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/ui/batch_calculator_window.py)**
*   **Architectural Role**: View (The Mill)
*   **The Purpose**: Processes bulk data (Spreadsheets).
*   **Key Logic**:
    *   `_import_file`: Loads CSV/Excel.
    *   `_process_threading`: Offloads the row-by-row Gematria calculation to a `QThread` to prevent UI freezing.

## Data Structures (Models)

### **[calculation_record.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/models/calculation_record.py)**
*   **Architectural Role**: Domain Model
*   **The Purpose**: The core DTO for a Gematria Result.
*   **Properties**: `text` (str), `value` (int), `cipher` (str), `breakdown` (list).

## Infrastructure

### **[calculation_repository.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/repositories/calculation_repository.py)**
*   **Architectural Role**: Persistence Layer
*   **The Purpose**: High-speed retrieval of past calculations.
*   **Key Logic**: Wraps `Whoosh` for text indexing.
*   **Backing Store**: `[sqlite_calculation_repository.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/repositories/sqlite_calculation_repository.py)`

### **[cipher_repository.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/repositories/cipher_repository.py)**
*   **Architectural Role**: Persistence Layer
*   **The Purpose**: Loads and caches the Cipher definitions.
*   **Key Logic**: returns `[cipher_token.py](file:///home/burkettdaniel927/projects/isopgem/src/pillars/gematria/models/cipher_token.py)` objects.
