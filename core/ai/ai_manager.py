"""
Core AI Manager for coordinating AI operations
"""
from typing import List, Dict, Optional, Tuple
import logging
import asyncio
from pathlib import Path

from .bert_manager import BERTManager
from .faiss_manager import FAISSManager

logger = logging.getLogger(__name__)

class AIManager:
    """Singleton manager for AI operations"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.bert = BERTManager()
        self.faiss = FAISSManager()
        self._initialized = True
        
    async def initialize(self, gpu_index: Optional[int] = None):
        """Initialize AI components"""
        try:
            logger.info("Initializing AI Manager")
            
            # Initialize BERT
            await self.bert.initialize()
            
            # Initialize FAISS
            self.faiss.initialize(gpu_index)
            
            logger.info("AI Manager initialization complete")
        except Exception as e:
            logger.error(f"Error initializing AI Manager: {e}")
            raise
            
    async def process_pattern(self, pattern: Dict) -> Dict:
        """Process a pattern for storage or matching"""
        try:
            # Generate embedding
            embedding = await self.bert.get_pattern_embedding(pattern)
            
            # Detect languages
            languages = {}
            for lang, text in pattern.items():
                if lang in ['english', 'hebrew', 'greek'] and text:
                    detected = self.bert.detect_language(text)
                    languages[lang] = detected
                    
            # Add language info to pattern
            pattern['detected_languages'] = languages
            
            return {
                'pattern': pattern,
                'embedding': embedding
            }
        except Exception as e:
            logger.error(f"Error processing pattern: {e}")
            raise
            
    async def add_patterns(self, patterns: List[Dict]):
        """Add patterns to the index"""
        try:
            # Process patterns and get embeddings
            processed = []
            embeddings = []
            
            for pattern in patterns:
                result = await self.process_pattern(pattern)
                processed.append(result['pattern'])
                embeddings.append(result['embedding'])
                
            # Stack embeddings
            stacked_embeddings = torch.stack(embeddings)
            
            # Add to FAISS index
            self.faiss.add_patterns(stacked_embeddings, processed)
            
            logger.info(f"Added {len(patterns)} patterns to index")
        except Exception as e:
            logger.error(f"Error adding patterns: {e}")
            raise
            
    async def search_similar(self, query: Dict, k: int = 5) -> List[Dict]:
        """Search for similar patterns"""
        try:
            # Process query
            result = await self.process_pattern(query)
            
            # Search FAISS index
            matches, distances = self.faiss.search_patterns(result['embedding'], k)
            
            # Add distances to results
            for match, distance in zip(matches, distances):
                match['similarity_score'] = float(1.0 / (1.0 + distance))
                
            return matches
        except Exception as e:
            logger.error(f"Error searching patterns: {e}")
            raise
            
    async def analyze_relationships(self, patterns: List[Dict]) -> Dict:
        """Analyze relationships between patterns"""
        try:
            relationships = {
                'numerical': [],
                'linguistic': [],
                'hierarchical': []
            }
            
            # Analyze numerical relationships
            for i, pattern1 in enumerate(patterns):
                for pattern2 in patterns[i+1:]:
                    if 'value' in pattern1 and 'value' in pattern2:
                        rel = self._analyze_numerical_relationship(
                            pattern1['value'],
                            pattern2['value']
                        )
                        if rel:
                            relationships['numerical'].append(rel)
                            
            # Analyze language mappings
            for pattern in patterns:
                if all(lang in pattern for lang in ['english', 'hebrew', 'greek']):
                    relationships['linguistic'].append({
                        'type': 'trilingual_mapping',
                        'english': pattern['english'],
                        'hebrew': pattern['hebrew'],
                        'greek': pattern['greek']
                    })
                    
            # Analyze hierarchical relationships
            if any('level' in pattern for pattern in patterns):
                hierarchies = self._analyze_hierarchical_relationships(patterns)
                relationships['hierarchical'].extend(hierarchies)
                
            return relationships
        except Exception as e:
            logger.error(f"Error analyzing relationships: {e}")
            raise
            
    def _analyze_numerical_relationship(self, val1: int, val2: int) -> Optional[Dict]:
        """Analyze relationship between two numerical values"""
        try:
            # Check for basic mathematical relationships
            if val2 % val1 == 0:
                return {
                    'type': 'multiple',
                    'value1': val1,
                    'value2': val2,
                    'factor': val2 // val1
                }
            # Add more relationship types as needed
            return None
        except Exception:
            return None
            
    def _analyze_hierarchical_relationships(self, patterns: List[Dict]) -> List[Dict]:
        """Analyze hierarchical relationships in patterns"""
        hierarchies = []
        try:
            # Group by level
            levels = {}
            for pattern in patterns:
                if 'level' in pattern:
                    level = pattern['level']
                    if level not in levels:
                        levels[level] = []
                    levels[level].append(pattern)
                    
            # Analyze level relationships
            sorted_levels = sorted(levels.keys())
            for i in range(len(sorted_levels)-1):
                current_level = sorted_levels[i]
                next_level = sorted_levels[i+1]
                
                hierarchies.append({
                    'type': 'level_transition',
                    'from_level': current_level,
                    'to_level': next_level,
                    'patterns_from': len(levels[current_level]),
                    'patterns_to': len(levels[next_level])
                })
                
        except Exception as e:
            logger.error(f"Error in hierarchical analysis: {e}")
            
        return hierarchies
