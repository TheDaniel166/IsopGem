"""
FAISS index management for pattern matching and similarity search
"""
from typing import List, Dict, Optional, Tuple
import numpy as np
import faiss
import logging
import torch

logger = logging.getLogger(__name__)

class FAISSManager:
    """Manages FAISS indexes for pattern matching and similarity search"""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.index = None
        self.pattern_metadata = []  # Store metadata for indexed patterns
        
    def initialize(self):
        """Initialize FAISS index with optimizations"""
        try:
            logger.info("Initializing FAISS index")
            
            # Create base index - using L2 distance
            quantizer = faiss.IndexFlatL2(self.dimension)
            
            # Use IVF for faster search with slight accuracy trade-off
            # Number of centroids - rule of thumb: sqrt(N) where N is expected dataset size
            # Let's assume around 10k patterns max initially
            n_centroids = 100
            
            # Create IVF index
            self.index = faiss.IndexIVFFlat(quantizer, self.dimension, n_centroids, faiss.METRIC_L2)
            
            # Generate random training data
            np.random.seed(42)  # For reproducibility
            train_data = np.random.random((2000, self.dimension)).astype('float32')
            self.index.train(train_data)
            
            # Set number of probes (more probes = better accuracy but slower)
            self.index.nprobe = 10
            
            logger.info("FAISS initialization complete")
            return True
        except Exception as e:
            logger.error(f"Error initializing FAISS: {e}")
            self.index = None
            return False
            
    def add_patterns(self, embeddings: torch.Tensor, metadata: List[Dict]):
        """Add pattern embeddings to the index"""
        try:
            if self.index is None:
                if not self.initialize():
                    raise ValueError("Failed to initialize FAISS index")
                
            # Convert to numpy and ensure correct shape
            embeddings_np = embeddings.cpu().numpy().astype('float32')
            if len(embeddings_np.shape) == 1:
                embeddings_np = embeddings_np.reshape(1, -1)
                
            # Add to index
            self.index.add(embeddings_np)
            self.pattern_metadata.extend(metadata)
            
            logger.info(f"Added {len(metadata)} patterns to index")
        except Exception as e:
            logger.error(f"Error adding patterns: {e}")
            raise
            
    def search_patterns(self, query_embedding: torch.Tensor, k: int = 5) -> List[Dict]:
        """Search for similar patterns"""
        try:
            if self.index is None:
                raise ValueError("Index not initialized")
                
            # Convert query to numpy and ensure correct shape
            query_np = query_embedding.cpu().numpy().astype('float32')
            if len(query_np.shape) == 1:
                query_np = query_np.reshape(1, -1)
                
            # Search index
            distances, indices = self.index.search(query_np, k)
            
            # Get metadata for results
            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if 0 <= idx < len(self.pattern_metadata):
                    result = self.pattern_metadata[idx].copy()
                    result['score'] = float(dist)  # Add distance score to result
                    results.append(result)
                    
            return results
        except Exception as e:
            logger.error(f"Error searching patterns: {e}")
            raise
            
    def clear_index(self):
        """Clear the FAISS index and metadata"""
        try:
            logger.info("Clearing FAISS index")
            # Reset the index
            self.index = None
            # Clear metadata
            self.pattern_metadata.clear()
            # Reinitialize fresh index
            self.initialize()
            logger.info("FAISS index cleared and reinitialized")
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            raise
