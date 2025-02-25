"""
BERT model management for multilingual text processing
"""
from typing import List, Dict, Optional, Any
import torch
from transformers import BertTokenizer, BertModel
import logging
from pathlib import Path
from ..documents.base import DocumentContent, ExtractedContent
from ..documents.processor import DocumentProcessor
from .rag_manager import BERTSingleton

logger = logging.getLogger(__name__)

class BERTManager:
    """Manages BERT model operations for multilingual text processing"""
    
    def __init__(self):
        """Initialize BERT manager"""
        # Use singleton for embeddings
        self.model = BERTSingleton.get_instance()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = 'bert-base-multilingual-cased'
        self.tokenizer = None
        self.embedding_dim = 768  # BERT base embedding dimension
        self.document_processor = DocumentProcessor()
        self.document_cache: Dict[str, Dict[str, Any]] = {}
        
        if torch.cuda.is_available():
            logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
            torch.cuda.set_per_process_memory_fraction(0.8)  # Use up to 80% of GPU memory
        
    async def initialize(self):
        """Initialize BERT model and tokenizer"""
        try:
            logger.info(f"Initializing BERT model on {self.device}")
            self.tokenizer = BertTokenizer.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()  # Set to evaluation mode
            
            if torch.cuda.is_available():
                # Enable CUDA optimizations
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.enabled = True
                
            logger.info("BERT initialization complete")
        except Exception as e:
            logger.error(f"Error initializing BERT: {e}")
            raise
            
    async def get_embeddings(self, texts: List[str], batch_size: int = 32) -> torch.Tensor:
        """Generate embeddings for a list of texts with batching"""
        if not self.model or not self.tokenizer:
            await self.initialize()
            
        all_embeddings = []
        try:
            with torch.no_grad():
                # Process in batches
                for i in range(0, len(texts), batch_size):
                    batch_texts = texts[i:i + batch_size]
                    
                    # Tokenize and prepare input
                    inputs = self.tokenizer(
                        batch_texts,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=512
                    ).to(self.device)
                    
                    # Get model output
                    outputs = self.model(**inputs)
                    
                    # Use [CLS] token embedding as sequence representation
                    batch_embeddings = outputs.last_hidden_state[:, 0, :]
                    all_embeddings.append(batch_embeddings)
                    
                    # Clear CUDA cache periodically
                    if torch.cuda.is_available() and (i + 1) % (batch_size * 10) == 0:
                        torch.cuda.empty_cache()
                    
            # Concatenate all batches
            return torch.cat(all_embeddings, dim=0)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
            
    def detect_language(self, text: str) -> str:
        """Detect if text contains specific language patterns"""
        try:
            # Check for Hebrew characters
            if any('\u0590' <= c <= '\u05FF' for c in text):
                return 'hebrew'
            # Check for Greek characters
            elif any('\u0370' <= c <= '\u03FF' for c in text):
                return 'greek'
            # Default to English
            return 'english'
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return 'unknown'
            
    async def get_pattern_embedding(self, pattern: Dict) -> torch.Tensor:
        """Generate embedding for a numerical or symbolic pattern"""
        try:
            # Convert pattern to text representation
            pattern_text = self._pattern_to_text(pattern)
            
            # Get embeddings with pattern-specific tokenization
            embeddings = await self.get_embeddings([pattern_text], batch_size=1)
            return embeddings[0]
        except Exception as e:
            logger.error(f"Error generating pattern embedding: {e}")
            raise
            
    def _pattern_to_text(self, pattern: Dict) -> str:
        """Convert a pattern dictionary to text representation"""
        components = []
        
        # Handle numerical patterns
        if 'value' in pattern:
            components.append(f"numerical:{pattern['value']}")
            
        # Handle gematria values
        if 'gematria' in pattern:
            components.append(f"gematria:{pattern['gematria']}")
            
        # Handle symbolic meanings
        if 'symbols' in pattern:
            components.append(f"symbols:{','.join(pattern['symbols'])}")
            
        # Handle relationships
        if 'relationships' in pattern:
            for rel in pattern['relationships']:
                components.append(f"relation:{rel['type']}:{rel['target']}")
                
        return " | ".join(components)

    async def get_pattern_relationships(self, pattern1: Dict, pattern2: Dict) -> Dict[str, float]:
        """Analyze relationships between two patterns"""
        try:
            # Get embeddings for both patterns
            emb1 = await self.get_pattern_embedding(pattern1)
            emb2 = await self.get_pattern_embedding(pattern2)
            
            # Calculate various relationship metrics
            relationships = {
                'similarity': float(torch.cosine_similarity(emb1, emb2, dim=0)),
                'numerical_ratio': self._calculate_numerical_ratio(pattern1, pattern2),
                'symbolic_overlap': self._calculate_symbolic_overlap(pattern1, pattern2),
                'hierarchical_level': self._calculate_hierarchical_level(pattern1, pattern2)
            }
            
            return relationships
        except Exception as e:
            logger.error(f"Error analyzing pattern relationships: {e}")
            raise
            
    def _calculate_numerical_ratio(self, pattern1: Dict, pattern2: Dict) -> float:
        """Calculate numerical relationship between patterns"""
        try:
            val1 = float(pattern1.get('value', pattern1.get('gematria', 1)))
            val2 = float(pattern2.get('value', pattern2.get('gematria', 1)))
            return val1 / val2 if val2 != 0 else 0
        except:
            return 0
            
    def _calculate_symbolic_overlap(self, pattern1: Dict, pattern2: Dict) -> float:
        """Calculate symbolic overlap between patterns"""
        try:
            symbols1 = set(pattern1.get('symbols', []))
            symbols2 = set(pattern2.get('symbols', []))
            
            if not symbols1 or not symbols2:
                return 0
                
            intersection = symbols1.intersection(symbols2)
            union = symbols1.union(symbols2)
            
            return len(intersection) / len(union)
        except:
            return 0
            
    def _calculate_hierarchical_level(self, pattern1: Dict, pattern2: Dict) -> float:
        """Calculate hierarchical relationship between patterns"""
        try:
            level1 = pattern1.get('level', 0)
            level2 = pattern2.get('level', 0)
            
            # Normalize level difference to [-1, 1] range
            max_level_diff = 10  # Assume max level difference
            return (level1 - level2) / max_level_diff
        except:
            return 0

    async def tokenize_pattern(self, pattern: Dict) -> Dict[str, torch.Tensor]:
        """Tokenize a pattern with specialized handling for different components"""
        try:
            # Prepare pattern components
            components = {
                'numerical': self._tokenize_numerical(pattern),
                'symbolic': self._tokenize_symbolic(pattern),
                'relational': self._tokenize_relational(pattern)
            }
            
            # Get embeddings for each component
            for key, text in components.items():
                if text:
                    components[key] = (await self.get_embeddings([text], batch_size=1))[0]
                else:
                    components[key] = torch.zeros(self.embedding_dim, device=self.device)
                    
            return components
        except Exception as e:
            logger.error(f"Error tokenizing pattern: {e}")
            raise
            
    def _tokenize_numerical(self, pattern: Dict) -> str:
        """Tokenize numerical aspects of a pattern"""
        components = []
        
        if 'value' in pattern:
            components.append(f"value:{pattern['value']}")
        if 'gematria' in pattern:
            components.append(f"gematria:{pattern['gematria']}")
            
        return " ".join(components)
        
    def _tokenize_symbolic(self, pattern: Dict) -> str:
        """Tokenize symbolic aspects of a pattern"""
        if 'symbols' in pattern:
            return "symbols:" + ",".join(pattern['symbols'])
        return ""
        
    def _tokenize_relational(self, pattern: Dict) -> str:
        """Tokenize relational aspects of a pattern"""
        if 'relationships' in pattern:
            return " ".join(f"rel:{r['type']}:{r['target']}" for r in pattern['relationships'])
        return ""

    async def analyze_language_correspondences(self, text: str) -> Dict[str, Any]:
        """Analyze language correspondences in text"""
        try:
            # Initialize correspondence analysis
            correspondences = {
                'primary_language': self.detect_language(text),
                'word_mappings': {},
                'semantic_links': {},
                'cross_references': []
            }

            # Split into words while preserving script
            words = self._split_multilingual_text(text)
            
            # Analyze each word
            for word in words:
                lang = self.detect_language(word)
                if lang != 'unknown':
                    # Get word embedding
                    word_embedding = await self.get_embeddings([word], batch_size=1)
                    
                    # Find semantic neighbors in other languages
                    if lang != 'english':
                        correspondences['word_mappings'][word] = await self._find_language_mappings(
                            word, word_embedding[0], source_lang=lang, target_lang='english'
                        )
                    
                    # Store semantic relationships
                    correspondences['semantic_links'][word] = await self._analyze_semantic_links(
                        word, word_embedding[0], lang
                    )

            return correspondences
        except Exception as e:
            logger.error(f"Error analyzing language correspondences: {e}")
            raise

    def _split_multilingual_text(self, text: str) -> List[str]:
        """Split text while preserving language-specific word boundaries"""
        words = []
        current_word = ""
        current_script = None

        for char in text:
            # Detect character script
            if '\u0590' <= char <= '\u05FF':  # Hebrew
                script = 'hebrew'
            elif '\u0370' <= char <= '\u03FF':  # Greek
                script = 'greek'
            elif char.isspace():  # Space
                if current_word:
                    words.append(current_word)
                    current_word = ""
                current_script = None
                continue
            else:  # English/Other
                script = 'english'

            # Handle script changes
            if current_script and script != current_script and current_word:
                words.append(current_word)
                current_word = ""

            current_word += char
            current_script = script

        # Add final word
        if current_word:
            words.append(current_word)

        return words

    async def _find_language_mappings(
        self, 
        word: str, 
        embedding: torch.Tensor, 
        source_lang: str, 
        target_lang: str
    ) -> List[Dict[str, Any]]:
        """Find corresponding words in target language"""
        try:
            # Get semantic neighbors in target language
            neighbors = []
            similarity_threshold = 0.7

            # Compare with known mappings
            if hasattr(self, 'language_mappings'):
                target_words = self.language_mappings.get(target_lang, {})
                for target_word, target_embedding in target_words.items():
                    similarity = float(torch.cosine_similarity(
                        embedding, target_embedding, dim=0
                    ))
                    if similarity > similarity_threshold:
                        neighbors.append({
                            'word': target_word,
                            'similarity': similarity,
                            'language': target_lang
                        })

            # Sort by similarity
            neighbors.sort(key=lambda x: x['similarity'], reverse=True)
            return neighbors[:5]  # Return top 5 matches
        except Exception as e:
            logger.error(f"Error finding language mappings: {e}")
            return []

    async def _analyze_semantic_links(
        self, 
        word: str, 
        embedding: torch.Tensor, 
        language: str
    ) -> Dict[str, Any]:
        """Analyze semantic relationships for a word"""
        try:
            return {
                'root_meaning': await self._extract_root_meaning(word, language),
                'semantic_field': await self._get_semantic_field(embedding),
                'usage_patterns': await self._analyze_usage_patterns(word, language)
            }
        except Exception as e:
            logger.error(f"Error analyzing semantic links: {e}")
            return {}

    async def _extract_root_meaning(self, word: str, language: str) -> str:
        """Extract root meaning of a word based on language"""
        try:
            if language == 'hebrew':
                # Hebrew root analysis (usually 3 letters)
                return self._analyze_hebrew_root(word)
            elif language == 'greek':
                # Greek root analysis
                return self._analyze_greek_root(word)
            return word
        except Exception as e:
            logger.error(f"Error extracting root meaning: {e}")
            return word

    def _analyze_hebrew_root(self, word: str) -> str:
        """Analyze Hebrew word root (usually 3 letters)"""
        # Remove vowel points and other marks
        clean_word = ''.join(c for c in word if '\u0590' <= c <= '\u05FF')
        # Basic 3-letter root extraction (can be enhanced)
        return clean_word[:3] if len(clean_word) >= 3 else clean_word

    def _analyze_greek_root(self, word: str) -> str:
        """Analyze Greek word root"""
        # Remove diacritics and get base form
        clean_word = ''.join(c for c in word if '\u0370' <= c <= '\u03FF')
        return clean_word

    async def _get_semantic_field(self, embedding: torch.Tensor) -> List[str]:
        """Get semantic field based on embedding"""
        try:
            # Find related concepts based on embedding
            semantic_field = []
            if hasattr(self, 'concept_embeddings'):
                for concept, concept_emb in self.concept_embeddings.items():
                    similarity = float(torch.cosine_similarity(
                        embedding, concept_emb, dim=0
                    ))
                    if similarity > 0.6:  # Threshold for semantic relationship
                        semantic_field.append(concept)
            return semantic_field
        except Exception as e:
            logger.error(f"Error getting semantic field: {e}")
            return []

    async def _analyze_usage_patterns(self, word: str, language: str) -> Dict[str, List[str]]:
        """Analyze common usage patterns of the word"""
        try:
            return {
                'common_contexts': [],  # Could be populated from a usage database
                'collocations': [],     # Common word combinations
                'registers': []         # Formal, informal, religious, etc.
            }
        except Exception as e:
            logger.error(f"Error analyzing usage patterns: {e}")
            return {}

    async def analyze_document_correspondences(self, doc_path: Path) -> Dict[str, Any]:
        """Analyze language correspondences in a document"""
        try:
            # Check cache first
            cache_key = str(doc_path)
            if cache_key in self.document_cache:
                logger.info(f"Using cached analysis for {doc_path}")
                return self.document_cache[cache_key]

            # Process document
            content = await self.document_processor.process(
                doc_path,
                extract_tables=True,
                extract_structure=True
            )

            # Initialize analysis
            analysis = {
                'languages': {},
                'correspondences': {},
                'patterns': {},
                'relationships': {}
            }

            # Analyze document structure
            await self._analyze_document_structure(content, analysis)

            # Process text content
            for section in content.sections:
                # Analyze text
                section_analysis = await self.analyze_language_correspondences(section.text)
                
                # Merge section analysis
                self._merge_section_analysis(analysis, section_analysis, section.metadata)

            # Cache results
            self.document_cache[cache_key] = analysis
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing document correspondences: {e}")
            raise

    async def _analyze_document_structure(
        self, 
        content: DocumentContent, 
        analysis: Dict[str, Any]
    ):
        """Analyze document structure for patterns and relationships"""
        try:
            # Analyze hierarchy
            hierarchy = {
                'levels': self._extract_hierarchy_levels(content),
                'relationships': self._extract_structural_relationships(content),
                'patterns': await self._extract_structural_patterns(content)
            }
            
            # Analyze tables
            tables = {
                'structure': self._analyze_table_structure(content),
                'language_mix': self._analyze_table_languages(content),
                'patterns': await self._extract_table_patterns(content)
            }
            
            # Store results
            analysis['structure'] = {
                'hierarchy': hierarchy,
                'tables': tables,
                'metadata': content.metadata
            }
        except Exception as e:
            logger.error(f"Error analyzing document structure: {e}")
            raise

    def _extract_hierarchy_levels(self, content: DocumentContent) -> Dict[str, Any]:
        """Extract hierarchical levels from document"""
        levels = {}
        try:
            for section in content.sections:
                level = section.metadata.get('level', 0)
                if level not in levels:
                    levels[level] = []
                levels[level].append({
                    'id': section.id,
                    'title': section.title,
                    'language': self.detect_language(section.title)
                })
        except Exception as e:
            logger.error(f"Error extracting hierarchy levels: {e}")
        return levels

    def _extract_structural_relationships(
        self, 
        content: DocumentContent
    ) -> List[Dict[str, Any]]:
        """Extract relationships between document sections"""
        relationships = []
        try:
            for section in content.sections:
                # Parent-child relationships
                if section.parent_id:
                    relationships.append({
                        'type': 'parent-child',
                        'source': section.parent_id,
                        'target': section.id
                    })
                
                # Cross-references
                for ref in section.references:
                    relationships.append({
                        'type': 'reference',
                        'source': section.id,
                        'target': ref.target_id,
                        'context': ref.context
                    })
        except Exception as e:
            logger.error(f"Error extracting structural relationships: {e}")
        return relationships

    async def _extract_structural_patterns(
        self, 
        content: DocumentContent
    ) -> List[Dict[str, Any]]:
        """Extract patterns from document structure"""
        patterns = []
        try:
            # Analyze section patterns
            section_embeddings = {}
            for section in content.sections:
                # Get section embedding
                emb = await self.get_embeddings([section.text], batch_size=1)
                section_embeddings[section.id] = emb[0]
                
                # Find similar sections
                for other_id, other_emb in section_embeddings.items():
                    if other_id != section.id:
                        similarity = float(torch.cosine_similarity(
                            emb[0], other_emb, dim=0
                        ))
                        if similarity > 0.8:  # High similarity threshold
                            patterns.append({
                                'type': 'similar_sections',
                                'sections': [section.id, other_id],
                                'similarity': similarity
                            })
        except Exception as e:
            logger.error(f"Error extracting structural patterns: {e}")
        return patterns

    def _analyze_table_structure(self, content: DocumentContent) -> List[Dict[str, Any]]:
        """Analyze structure of tables in document"""
        table_analysis = []
        try:
            for table in content.tables:
                analysis = {
                    'id': table.id,
                    'dimensions': table.dimensions,
                    'header_languages': [
                        self.detect_language(cell.text) 
                        for cell in table.headers
                    ],
                    'rtl_columns': [
                        i for i, col in enumerate(table.columns)
                        if any(self.detect_language(cell.text) == 'hebrew' 
                             for cell in col)
                    ]
                }
                table_analysis.append(analysis)
        except Exception as e:
            logger.error(f"Error analyzing table structure: {e}")
        return table_analysis

    def _analyze_table_languages(self, content: DocumentContent) -> Dict[str, List[int]]:
        """Analyze language distribution in tables"""
        language_distribution = {'hebrew': [], 'greek': [], 'english': []}
        try:
            for table in content.tables:
                for i, col in enumerate(table.columns):
                    # Count languages in column
                    lang_counts = {'hebrew': 0, 'greek': 0, 'english': 0}
                    for cell in col:
                        lang = self.detect_language(cell.text)
                        if lang in lang_counts:
                            lang_counts[lang] += 1
                    
                    # Determine dominant language
                    max_lang = max(lang_counts.items(), key=lambda x: x[1])[0]
                    language_distribution[max_lang].append(i)
        except Exception as e:
            logger.error(f"Error analyzing table languages: {e}")
        return language_distribution

    async def _extract_table_patterns(
        self, 
        content: DocumentContent
    ) -> List[Dict[str, Any]]:
        """Extract patterns from tables"""
        patterns = []
        try:
            for table in content.tables:
                # Analyze column relationships
                col_patterns = await self._analyze_column_patterns(table)
                patterns.extend(col_patterns)
                
                # Analyze cell patterns
                cell_patterns = await self._analyze_cell_patterns(table)
                patterns.extend(cell_patterns)
        except Exception as e:
            logger.error(f"Error extracting table patterns: {e}")
        return patterns

    def _merge_section_analysis(
        self,
        doc_analysis: Dict[str, Any],
        section_analysis: Dict[str, Any],
        metadata: Dict[str, Any]
    ):
        """Merge section analysis into document analysis"""
        try:
            # Update language statistics
            lang = section_analysis['primary_language']
            if lang not in doc_analysis['languages']:
                doc_analysis['languages'][lang] = 0
            doc_analysis['languages'][lang] += 1
            
            # Merge correspondences
            for word, mappings in section_analysis['word_mappings'].items():
                if word not in doc_analysis['correspondences']:
                    doc_analysis['correspondences'][word] = mappings
                else:
                    # Update existing mappings with new information
                    existing = doc_analysis['correspondences'][word]
                    for mapping in mappings:
                        if mapping not in existing:
                            existing.append(mapping)
            
            # Update patterns
            for word, links in section_analysis['semantic_links'].items():
                if word not in doc_analysis['patterns']:
                    doc_analysis['patterns'][word] = links
                else:
                    # Merge semantic information
                    existing = doc_analysis['patterns'][word]
                    for key, value in links.items():
                        if key not in existing:
                            existing[key] = value
                        elif isinstance(value, list):
                            existing[key].extend(value)
        except Exception as e:
            logger.error(f"Error merging section analysis: {e}")
            
    def __del__(self):
        """Cleanup CUDA memory"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
