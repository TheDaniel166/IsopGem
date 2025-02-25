"""
AI Test Panel implementation
"""
from PyQt6.QtWidgets import (QTextEdit, QPushButton, QVBoxLayout, 
                           QHBoxLayout, QLabel, QSpinBox, QComboBox, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal
import torch
import numpy as np
import logging
from typing import List, Dict
from pathlib import Path
from qasync import asyncSlot
import os

from ..base import BasePanel
from ....ai.bert_manager import BERTManager
from ....ai.faiss_manager import FAISSManager
from ....ai.rag_manager import RAGManager

from ....base.config import ConfigManager

logger = logging.getLogger(__name__)

class AITestPanel(BasePanel):
    """Panel for testing AI components"""
    
    test_completed = pyqtSignal(str)  # Test results
    
    def __init__(self, parent=None):
        super().__init__(parent, title="AI Test")
        self.bert = BERTManager()
        self.faiss = FAISSManager()
        self.rag = RAGManager()
        # Use the Documents folder in IsopGem
        self.doc_path = os.path.join(os.path.expanduser("~"), "IsopGem", "Documents")
        logger.info(f"Documents path: {self.doc_path}")
        
    def setup_ui(self):
        """Set up the test panel UI"""
        # Test Configuration
        config_layout = QHBoxLayout()
        
        # Number of test patterns
        pattern_layout = QVBoxLayout()
        pattern_layout.addWidget(QLabel("Test Patterns:"))
        self.pattern_count = QSpinBox(self)
        self.pattern_count.setRange(1, 1000)
        self.pattern_count.setValue(100)
        pattern_layout.addWidget(self.pattern_count)
        config_layout.addLayout(pattern_layout)
        
        # Pattern type
        type_layout = QVBoxLayout()
        type_layout.addWidget(QLabel("Pattern Type:"))
        self.pattern_type = QComboBox(self)
        self.pattern_type.addItems(["Numerical", "Text", "Mixed"])
        type_layout.addWidget(self.pattern_type)
        config_layout.addLayout(type_layout)
        
        # Search input
        search_layout = QVBoxLayout()
        search_layout.addWidget(QLabel("Search Query:"))
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter search text...")
        search_layout.addWidget(self.search_input)
        config_layout.addLayout(search_layout)
        
        # Add to main layout
        self.content_layout.addLayout(config_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("Generate Patterns", self)
        self.generate_btn.clicked.connect(self._on_generate_clicked)
        button_layout.addWidget(self.generate_btn)
        
        self.search_btn = QPushButton("Search", self)
        self.search_btn.clicked.connect(self._on_search_clicked)
        button_layout.addWidget(self.search_btn)
        
        self.clear_btn = QPushButton("Clear", self)
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        button_layout.addWidget(self.clear_btn)
        
        self.content_layout.addLayout(button_layout)
        
        # Status area
        self.status = QTextEdit(self)
        self.status.setReadOnly(True)
        self.status.setStyleSheet("QTextEdit { background-color: #1e1e1e; color: #ffffff; }")
        self.content_layout.addWidget(self.status)
        
    @asyncSlot()
    async def _on_generate_clicked(self):
        """Handle generate button click"""
        self.generate_btn.setEnabled(False)
        try:
            await self._generate_patterns()
        finally:
            self.generate_btn.setEnabled(True)
        
    async def _generate_patterns(self):
        """Generate and index test patterns"""
        try:
            self.status.append("Generating patterns...")
            
            # Get pattern count and type
            count = self.pattern_count.value()
            pattern_type = self.pattern_type.currentText()
            
            # Generate patterns
            if pattern_type == "Mixed":
                patterns = self._generate_mixed_patterns(count)
            elif pattern_type == "Numerical":
                patterns = self._generate_numerical_patterns(count)
            else:
                patterns = self._generate_text_patterns(count)
            
            # Convert patterns to text
            texts = [self._pattern_to_text(p) for p in patterns]
            
            # Initialize AI components if needed
            await self.bert.initialize()
            self.faiss.initialize()
            
            # Get embeddings and add to index
            embeddings = await self.bert.get_embeddings(texts)
            self.faiss.add_patterns(embeddings, patterns)  # Fixed method name
            
            self.status.append(f"Generated and indexed {count} patterns")
            self.test_completed.emit("Pattern generation complete")
            
        except Exception as e:
            logger.error(f"Error generating patterns: {e}")
            self.status.append(f"Error: {str(e)}")
            self.test_completed.emit(f"Error: {str(e)}")
            
    def _generate_numerical_patterns(self, count: int) -> List[Dict]:
        """Generate numerical test patterns"""
        return [{"value": np.random.randint(1, 1000)} for _ in range(count)]
        
    def _generate_text_patterns(self, count: int) -> List[Dict]:
        """Generate text test patterns"""
        return [{"text": f"test_pattern_{i}"} for i in range(count)]
        
    def _generate_mixed_patterns(self, count: int) -> List[Dict]:
        """Generate mixed test patterns"""
        return [{
            "value": np.random.randint(1, 1000),
            "text": f"test_pattern_{i}"
        } for i in range(count)]
        
    def _pattern_to_text(self, pattern: Dict) -> str:
        """Convert pattern to text representation"""
        if "text" in pattern and "value" in pattern:
            return f"{pattern['text']} ({pattern['value']})"
        elif "text" in pattern:
            return pattern["text"]
        else:
            return str(pattern["value"])
            
    async def index_documents(self):
        """Index all documents in the docs folder"""
        try:
            self.status.append("Indexing documents...")
            logger.info(f"Looking for documents in: {self.doc_path}")
            
            # Initialize AI components first
            await self.bert.initialize()
            self.faiss.initialize()
            
            # Get all text files
            docs = []
            if os.path.exists(self.doc_path):
                for root, _, files in os.walk(self.doc_path):
                    for file in files:
                        if file.endswith('_extracted.txt'):
                            file_path = os.path.join(root, file)
                            logger.info(f"Found document: {file_path}")
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    # Remove the _extracted.txt suffix for display
                                    display_name = file.replace('_extracted.txt', '')
                                    docs.append({
                                        'text': content,
                                        'file': display_name
                                    })
                            except Exception as e:
                                logger.error(f"Error reading file {file_path}: {e}")
            else:
                logger.error(f"Documents directory not found: {self.doc_path}")
                self.status.append("Error: Documents directory not found")
                return False
            
            if not docs:
                self.status.append("No documents found to index")
                return False
                
            # Get embeddings and index
            texts = [doc['text'] for doc in docs]
            embeddings = await self.bert.get_embeddings(texts)
            self.faiss.add_patterns(embeddings, docs)
            
            self.status.append(f"Indexed {len(docs)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            self.status.append(f"Error: {str(e)}")
            return False

    @asyncSlot()
    async def _on_search_clicked(self):
        """Handle search button click"""
        try:
            query = self.search_input.text().strip()
            if not query:
                self.status.append("Please enter a search query")
                return
                
            self.status.append(f"Searching for: {query}")
            self.search_btn.setEnabled(False)
            
            # Search using RAG
            results = await self.rag.search(query)
            
            # Display results
            self.status.append("\nSearch Results:")
            if not results:
                self.status.append("No matching documents found")
            else:
                for i, result in enumerate(results):
                    self.status.append(f"{i+1}. File: {result['source']}")
                    self.status.append(f"   Score: {result['score']:.4f}")
                    self.status.append(f"   Section: {result['chunk_index'] + 1} of {result['total_chunks']}")
                    self.status.append(f"   Content: {result['content']}\n")
                
            self.search_btn.setEnabled(True)
            self.test_completed.emit("Search completed successfully")
            
        except Exception as e:
            logger.error(f"Error searching: {e}")
            self.status.append(f"Error: {str(e)}")
            self.search_btn.setEnabled(True)
            self.test_completed.emit(f"Error: {str(e)}")
            
    @asyncSlot()
    async def _on_clear_clicked(self):
        """Handle clear button click"""
        try:
            self.status.clear()
            self.rag.clear()
            self.status.append("Cleared search index")
            self.test_completed.emit("Index cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
            self.status.append(f"Error: {str(e)}")
            self.test_completed.emit(f"Error: {str(e)}")

    def get_preferred_area(self):
        """Get preferred dock area"""
        return Qt.DockWidgetArea.RightDockWidgetArea
