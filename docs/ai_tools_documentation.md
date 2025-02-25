# AI Tools Documentation

## Overview
The AI Tools system in IsopGem provides a comprehensive suite of AI-powered features accessible through the AI Tools tab in the ribbon interface. This document details the architecture, components, and functionality of the AI tools system.

## Core Architecture

### 1. AI Manager (`core/ai/base.py`)
Central singleton manager for all AI operations:
- Manages embeddings using BERT (bert-base-multilingual-cased)
  - Multi-language support (English, Hebrew, Greek)
  - Bidirectional context understanding
  - 768-dimensional embeddings
- FAISS index configuration
  - IndexFlatL2 for exact search
  - Optimized for numerical patterns
  - Efficient similarity search
- Coordinates between different AI subsystems:
  - Model Management
  - RAG System
  - Embeddings
  - Conversation Management
  - Connection Mapping
  - Concept Extraction

### 2. Panel Manager (`ui/workspace/panel_manager.py`)
Manages all UI panels with advanced features:
- Panel lifecycle management
- Theme customization (dark, light, blue themes)
- Window management (minimize, maximize, restore)
- Panel positioning and sizing
- Auxiliary window support
- Integration with AI and RAG managers

## UI Components

### AI Tools Tab (`ui/ribbon/ai_tools_tab.py`)
Organized into functional groups:

#### 1. AI Settings
- Model configuration
- System preferences
- Performance settings

#### 2. AI Chat
- Interactive chat interface
- Context-aware responses
- Code assistance
- Feedback collection

#### 3. Document Tools
- Document import with multi-format support
  - PDF (using PyMuPDF)
  - DOCX (using python-docx)
  - TXT (with encoding detection)
- Connection visualization
- Document relationship management

#### 4. Math Tools 
- Mathematical analysis
- Equation processing
- Numerical computations

#### 5. Image Generation
- AI image generation interface
- Image management tools

#### 6. Concept Tools
- Knowledge visualization
- Concept mapping
- Relationship analysis

#### 7. Feedback System
- User feedback collection
- Analytics dashboard
- System improvement metrics

## Technical Implementation

### 1. RAG System
Components:
- Document Memory
  - FAISS vector store with custom index structures
  - Optimized for pattern matching
  - Multi-dimensional similarity search
  - Scalable to millions of vectors
- BERT Processing
  - Multilingual document understanding
  - Context-aware embeddings
  - Cross-language pattern recognition
- RAG Manager
  - Context building
  - Query processing
  - Response generation
  - Pattern matching optimization

### 2. Model Management
Features:
- Multiple model support
- Ollama integration
- Resource optimization
- Model switching

### 3. Feedback System
Architecture:
- Feedback Collector
- Feedback Manager
- Analytics Engine
- API Integration

## Implementation Phases

### Phase 1: Core AI Infrastructure
1. BERT Setup
   - [x] Install transformers (v4.49.0) and FAISS (v1.10.0)
   - [x] Configure bert-base-multilingual-cased with GPU support
   - [x] Set up tokenization with batching and optimization
   - [x] Implement efficient embedding generation

2. FAISS Index Structure
   - [x] Create custom IndexFlatL2
   - [x] Configure for GPU acceleration
   - [x] Set up similarity search
   - [x] Implement vector storage

3. Pattern Recognition System
   - [x] Basic language detection (Hebrew/Greek/English)
   - [x] Basic pattern embedding
   - [x] Pattern-specific tokenization
   - [x] Advanced pattern relationships

### Phase 2: Document Processing
1. Content Processing
   - [x] Text extraction with PyMuPDF
   - [x] Table structure with python-docx
   - [x] RTL text handling
   - [x] OCR with Tesseract

2. Pattern Extraction
   - [x] Basic pattern detection
   - [x] Language correspondences
   - [x] Hierarchical relationships
   - [ ] Symbol mappings

3. Vector Generation
   - [x] Optimized BERT embeddings
   - [x] GPU-accelerated processing
   - [x] Batch processing
   - [x] Context preservation

### Phase 3: Search and Analysis
1. Search Implementation
   - [x] GPU-optimized FAISS search
   - [x] Multi-language queries
   - [ ] Pattern-based search
   - [ ] Advanced correspondence search

2. Analysis Tools
   - [x] Basic pattern detection
   - [ ] Language analysis
   - [ ] Numerical patterns
   - [ ] Symbol relationships

3. User Interface
   - [x] Search interface
   - [x] Results display
   - [ ] Karnak chat interface
   - [ ] Pattern visualization

### Phase 4: Karnak Enhancement
1. Natural Language
   - [x] Basic RAG integration
   - [ ] Context-aware responses
   - [ ] Web-enhanced knowledge
   - [ ] Advanced conversation memory

2. Web Integration
   - [ ] Hebrew/Greek term lookup
   - [ ] Basic etymology search
   - [ ] Deep cultural context
   - [ ] Cross-reference system

3. Spiritual Guidance
   - [x] Basic wisdom sharing
   - [ ] Source attribution
   - [ ] Pattern connections
   - [ ] Symbolic relationships

### Phase 5: Advanced Features
1. Pattern Analysis
   - [ ] Deep numerical patterns
   - [ ] Advanced language mappings
   - [ ] Symbolic hierarchies
   - [ ] Cross-system relationships

2. Visualization
   - [ ] Interactive diagrams
   - [ ] Relationship graphs
   - [ ] Pattern maps
   - [ ] Symbol networks

3. Integration
   - [ ] External API connections
   - [ ] Database synchronization
   - [ ] Cloud backup
   - [ ] Multi-user support

## Pattern Matching Specifications

### Numerical Patterns
- Value correspondences
- Mathematical relationships
- Symbolic number meanings
- Numerical hierarchies

### Language Mappings
- English/Hebrew/Greek correspondences
- RTL text handling
- Script detection
- Semantic relationships

### Hierarchical Structures
- Tree-based relationships
- Level-based organization
- Cross-level connections
- Symbolic hierarchies

### Symbol Systems
- Correspondence tables
- Symbol relationships
- Cross-system mappings
- Pattern recognition rules

## State Management

### 1. Persistence
- QSettings for UI preferences
- Custom state management for AI components
- Document state persistence
- Model state management

### 2. Panel State
- Position tracking
- Size management
- Theme preferences
- Layout persistence

## Error Handling

### 1. Logging System
- Detailed debug logging
- Error tracking
- Performance monitoring
- User action logging

### 2. Error Recovery
- Graceful degradation
- State recovery
- User notification
- Automatic retry mechanisms

## Customization

### 1. Theme System
```python
panel_themes = {
    'dark': {
        'background': '#2b2b2b',
        'border': '#333333',
        'text': '#ffffff',
        'button': '#3d3d3d',
        'button_hover': '#4d4d4d'
    },
    'light': {
        'background': '#f0f0f0',
        'border': '#cccccc',
        'text': '#000000',
        'button': '#e0e0e0',
        'button_hover': '#d0d0d0'
    },
    'blue': {
        'background': '#1e2433',
        'border': '#3498db',
        'text': '#ffffff',
        'button': '#2c3e50',
        'button_hover': '#34495e'
    }
}
```

### 2. Panel Customization
- Border color selection
- Font customization
- Background color
- Size constraints
- Position memory

## Best Practices

### 1. Code Organization
- Clear module separation
- Consistent naming
- Documentation standards
- Type hints usage

### 2. Performance
- Async operations for heavy tasks
- Resource cleanup
- Memory management
- Cache utilization

### 3. UI/UX
- Consistent styling
- Responsive design
- User feedback
- Error messaging

### 4. Testing
- Unit test coverage
- Integration testing
- UI testing
- Performance benchmarks
