"""
Karnak - An AI guide for spiritual wisdom and understanding
Based on the ancient Temple of Karnak in Egypt, a center of knowledge and enlightenment
"""
from typing import List, Dict, Optional
import logging
from pathlib import Path
import os

from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage

logger = logging.getLogger(__name__)

class KarnakChat:
    """Karnak - Your spiritual guide and wisdom keeper"""
    
    def __init__(self, rag_manager):
        self.rag = rag_manager
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Custom prompt template for Karnak's personality
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are Karnak, an AI guide named after the ancient Temple of Karnak in Egypt.
            Speak with wisdom, compassion, and deep understanding of spiritual matters.
            Use the following context to answer the question, but maintain your role as a spiritual guide.
            
            Context: {context}
            
            Question: {question}
            
            Answer as Karnak:"""
        )
        
    async def get_response(self, query: str) -> str:
        """Get a response from Karnak"""
        try:
            # Search for relevant context
            results = await self.rag.search(query, k=3)
            
            # Build context from results
            context = "\n\n".join([
                f"From {r['source']}:\n{r['content']}"
                for r in results
            ])
            
            # Format response based on context
            if not results:
                return ("I apologize, but I don't find any specific wisdom in our texts about that. "
                       "Perhaps you could rephrase your question, or we could explore a related topic?")
            
            # Use the most relevant content to form a response
            response = self._format_response(context, query)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting Karnak's response: {e}")
            return "I apologize, but I am unable to access the wisdom at this moment. Please try again."
            
    def _format_response(self, context: str, query: str) -> str:
        """Format Karnak's response using the context"""
        try:
            # Create a thoughtful response using the context
            # This is where we'd integrate with a language model
            # For now, we'll return a template response
            response = (
                f"Drawing upon the ancient wisdom, I can share this understanding:\n\n"
                f"{context}\n\n"
                f"Is there a specific aspect of this teaching you'd like to explore further?"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting Karnak's response: {e}")
            return "The mysteries are deep, but I cannot properly express them at this moment."
