"""
RAG (Retrieval-Augmented Generation) system for intelligent document processing
"""
from typing import List, Dict, Optional, Any
import logging
from pathlib import Path
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)

class BERTSingleton:
    """Singleton for BERT embeddings"""
    _instance = None
    
    @classmethod
    def get_instance(cls) -> HuggingFaceEmbeddings:
        if cls._instance is None:
            logger.info("Initializing BERT embeddings singleton")
            cls._instance = HuggingFaceEmbeddings(
                model_name="bert-base-multilingual-cased",
                model_kwargs={'device': 'cuda'},
                encode_kwargs={'normalize_embeddings': True, 'device': 'cuda', 'batch_size': 32}
            )
        return cls._instance

class RAGManager:
    """Manages the RAG system for document processing and retrieval"""
    
    def __init__(self, docs_path: Optional[str] = None):
        self.docs_path = docs_path or os.path.join(os.path.expanduser("~"), "IsopGem", "Documents")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        # Use singleton for embeddings
        self.embeddings = BERTSingleton.get_instance()
        self.vector_store = None
        self.document_map = {}  # Maps chunk IDs to source documents
        
    async def process_documents(self) -> bool:
        """Process and index all documents in the docs folder"""
        try:
            logger.info(f"Processing documents from: {self.docs_path}")
            
            if not os.path.exists(self.docs_path):
                logger.error(f"Documents directory not found: {self.docs_path}")
                return False
                
            # Get all text files
            documents = []
            metadata = []
            
            for root, _, files in os.walk(self.docs_path):
                for file in files:
                    if file.endswith('_extracted.txt'):
                        file_path = os.path.join(root, file)
                        display_name = file.replace('_extracted.txt', '')
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            # Split content into chunks
                            chunks = self.text_splitter.split_text(content)
                            
                            # Add each chunk with metadata
                            for i, chunk in enumerate(chunks):
                                chunk_id = f"{display_name}_chunk_{i}"
                                documents.append(chunk)
                                metadata.append({
                                    'source': display_name,
                                    'chunk_id': chunk_id,
                                    'chunk_index': i,
                                    'total_chunks': len(chunks)
                                })
                                self.document_map[chunk_id] = {
                                    'source': display_name,
                                    'content': chunk,
                                    'index': i,
                                    'total': len(chunks)
                                }
                                
                        except Exception as e:
                            logger.error(f"Error processing file {file_path}: {e}")
                            continue
            
            if not documents:
                logger.warning("No documents found to process")
                return False
                
            # Create vector store
            self.vector_store = FAISS.from_texts(
                documents,
                self.embeddings,
                metadatas=metadata
            )
            
            logger.info(f"Successfully processed {len(documents)} chunks from documents")
            return True
            
        except Exception as e:
            logger.error(f"Error processing documents: {e}")
            return False
            
    async def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for relevant document chunks"""
        try:
            if not self.vector_store:
                if not await self.process_documents():
                    raise ValueError("Failed to process documents")
                    
            # Search vector store
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            # Format results
            formatted_results = []
            for doc, score in results:
                chunk_id = doc.metadata['chunk_id']
                chunk_data = self.document_map[chunk_id]
                
                formatted_results.append({
                    'source': chunk_data['source'],
                    'content': chunk_data['content'],
                    'score': float(score),
                    'chunk_index': chunk_data['index'],
                    'total_chunks': chunk_data['total']
                })
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise
            
    def clear(self):
        """Clear the vector store and document map"""
        self.vector_store = None
        self.document_map.clear()
