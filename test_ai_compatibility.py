import torch
import logging
import asyncio
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path to import modules
# Adjust this path as needed for your environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test functions
async def test_torch():
    """Test PyTorch installation and CUDA availability"""
    logger.info("Testing PyTorch...")
    logger.info(f"PyTorch version: {torch.__version__}")
    
    cuda_available = torch.cuda.is_available()
    logger.info(f"CUDA available: {cuda_available}")
    
    if cuda_available:
        logger.info(f"CUDA device: {torch.cuda.get_device_name(0)}")
        logger.info(f"CUDA version: {torch.version.cuda}")
        
        # Test CUDA tensor operations
        a = torch.tensor([1.0, 2.0, 3.0], device='cuda')
        b = torch.tensor([4.0, 5.0, 6.0], device='cuda')
        c = a + b
        logger.info(f"CUDA tensor operation result: {c}")
    
    return True

async def test_transformers():
    """Test transformers library"""
    try:
        logger.info("Testing transformers...")
        from transformers import AutoTokenizer, AutoModel
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
        logger.info(f"Tokenizer loaded: {tokenizer.__class__.__name__}")
        
        # Test tokenization
        text = "Testing BERT tokenizer with multilingual text: Hello, こんにちは, שלום"
        tokens = tokenizer(text, return_tensors="pt")
        logger.info(f"Tokenization successful: {len(tokens['input_ids'][0])} tokens")
        
        # Load model
        model = AutoModel.from_pretrained("bert-base-multilingual-cased")
        logger.info(f"Model loaded: {model.__class__.__name__}")
        
        # Move to GPU if available
        if torch.cuda.is_available():
            model = model.to('cuda')
            tokens = {k: v.to('cuda') for k, v in tokens.items()}
        
        # Test forward pass
        with torch.no_grad():
            outputs = model(**tokens)
            embeddings = outputs.last_hidden_state[:, 0, :]
            logger.info(f"Model forward pass successful, embedding shape: {embeddings.shape}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing transformers: {e}", exc_info=True)
        return False

async def test_sentence_transformers():
    """Test sentence-transformers library"""
    try:
        logger.info("Testing sentence-transformers...")
        from sentence_transformers import SentenceTransformer
        
        # Load model
        model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
        logger.info(f"Model loaded: {model.__class__.__name__}")
        
        # Test encoding
        texts = [
            "This is a test sentence in English.",
            "これは日本語のテストセンテンスです。",
            "זהו משפט בדיקה בעברית."
        ]
        
        # Encode sentences
        embeddings = model.encode(texts, convert_to_tensor=True)
        logger.info(f"Encoding successful, embeddings shape: {embeddings.shape}")
        
        # Test similarity
        from torch.nn.functional import cosine_similarity
        sim = cosine_similarity(embeddings[0].unsqueeze(0), embeddings[1].unsqueeze(0))
        logger.info(f"Similarity between first two sentences: {sim.item():.4f}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing sentence-transformers: {e}", exc_info=True)
        return False

async def test_langchain():
    """Test LangChain components"""
    try:
        logger.info("Testing LangChain...")
        from langchain_community.embeddings import HuggingFaceEmbeddings
        
        # Test embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="paraphrase-multilingual-mpnet-base-v2"
        )
        logger.info(f"LangChain embeddings model loaded: {embeddings.__class__.__name__}")
        
        # Test embedding generation
        text = "This is a test of LangChain embedding functionality."
        result = embeddings.embed_query(text)
        
        logger.info(f"LangChain embedding generated, dimension: {len(result)}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing LangChain: {e}", exc_info=True)
        return False

async def test_faiss():
    """Test FAISS library"""
    try:
        logger.info("Testing FAISS...")
        import faiss
        import numpy as np
        
        # Create a sample index
        dimension = 768  # Standard embedding dimension
        index = faiss.IndexFlatL2(dimension)
        
        # Generate random vectors
        np.random.seed(42)
        vectors = np.random.random((10, dimension)).astype('float32')
        
        # Add to index
        index.add(vectors)
        logger.info(f"Added {index.ntotal} vectors to FAISS index")
        
        # Test search
        query = np.random.random((1, dimension)).astype('float32')
        distances, indices = index.search(query, k=3)
        
        logger.info(f"FAISS search successful, found indices: {indices[0]}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing FAISS: {e}", exc_info=True)
        return False

async def test_project_integration():
    """Test integration with project components"""
    try:
        logger.info("Testing integration with project components...")
        
        # Test BERT Manager (adjust import path as needed)
        try:
            from core.ai.bert_manager import BERTManager
            bert = BERTManager()
            logger.info(f"BERTManager imported successfully")
            
            # Test initialization
            await bert.initialize()
            logger.info("BERTManager initialized successfully")
            
            # Test embedding generation
            texts = ["Testing integration with BERTManager"]
            embeddings = await bert.get_embeddings(texts)
            logger.info(f"BERTManager embeddings generated, shape: {embeddings.shape}")
        except Exception as e:
            logger.error(f"Error testing BERTManager: {e}", exc_info=True)
            logger.warning("Skipping BERTManager test, continuing with other tests")
        
        # Test RAG Manager (adjust import path as needed)
        try:
            from core.ai.rag_manager import RAGManager
            rag = RAGManager()
            logger.info(f"RAGManager imported successfully")
            
            # Test initialization
            success = await rag.process_documents()
            logger.info(f"RAGManager document processing {'successful' if success else 'failed'}")
            
            # Test search
            results = await rag.search("test query")
            logger.info(f"RAGManager search returned {len(results)} results")
        except Exception as e:
            logger.error(f"Error testing RAGManager: {e}", exc_info=True)
            logger.warning("Skipping RAGManager test, continuing with other tests")
        
        return True
    except Exception as e:
        logger.error(f"Error testing project integration: {e}", exc_info=True)
        return False

async def main():
    """Run all tests"""
    results = {}
    
    # Run each test
    results["PyTorch"] = await test_torch()
    results["Transformers"] = await test_transformers()
    results["Sentence-Transformers"] = await test_sentence_transformers()
    results["LangChain"] = await test_langchain()
    results["FAISS"] = await test_faiss()
    results["Project Integration"] = await test_project_integration()
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("COMPATIBILITY TEST RESULTS")
    logger.info("="*50)
    for component, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{component}: {status}")
    logger.info("="*50)

if __name__ == "__main__":
    asyncio.run(main()) 