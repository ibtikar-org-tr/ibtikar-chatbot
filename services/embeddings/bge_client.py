import numpy as np
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import os 
import logging

load_dotenv()

logger = logging.getLogger(__name__)


try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class BGEEmbeddingClient:
    """Client for BGE (BAAI General Embedding) model embeddings"""
    
    def __init__(self, model_name: str = None):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise Exception(
                "sentence-transformers library not installed. Install with: pip install sentence-transformers",
                error_code="MISSING_DEPENDENCY"
            )
        
        self.model_name = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-large-en-v1.5")
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            
            # Map model name to actual Hugging Face model ID
            model_mapping = {
                "bge-large-en-v1.5": "BAAI/bge-large-en-v1.5",
                "bge-base-en-v1.5": "BAAI/bge-base-en-v1.5",
                "bge-small-en-v1.5": "BAAI/bge-small-en-v1.5"
            }
            
            model_id = model_mapping.get(self.model_name, self.model_name)
            
            self.model = SentenceTransformer(model_id)
            logger.info("Embedding model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load embedding model {self.model_name}: {str(e)}")
            raise Exception(
                f"Failed to initialize embedding model: {str(e)}",
                error_code="MODEL_INIT_ERROR"
            )
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for a single text"""
        return self.embed_texts([text])[0]
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not self.model:
            raise Exception(
                "Embedding model not initialized",
                error_code="MODEL_NOT_INITIALIZED"
            )
        
        if not texts:
            return []
        
        try:
            # Clean and prepare texts
            cleaned_texts = []
            for text in texts:
                if not text or not text.strip():
                    cleaned_texts.append("")
                else:
                    # For BGE models, add query prefix for better retrieval
                    if not text.startswith("Represent this sentence for searching relevant passages:"):
                        cleaned_text = f"Represent this sentence for searching relevant passages: {text.strip()}"
                    else:
                        cleaned_text = text.strip()
                    cleaned_texts.append(cleaned_text)
            
            # Generate embeddings
            embeddings = self.model.encode(
                cleaned_texts,
                normalize_embeddings=True,  # Normalize for dot product similarity
                show_progress_bar=False
            )
            
            # Convert to list format
            if len(embeddings.shape) == 1:
                embeddings = embeddings.reshape(1, -1)
            
            return embeddings.tolist()
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {str(e)}")
            raise Exception(
                f"Embedding generation failed: {str(e)}",
                error_code="EMBEDDING_ERROR"
            )
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embeddings for a search query (with special handling)"""
        if not query or not query.strip():
            return [0.0] * self.get_embedding_dimension()
        
        # For queries, use a specific prefix for BGE models
        query_text = f"Represent this sentence for searching relevant passages: {query.strip()}"
        return self.embed_text(query_text)
    
    def embed_document(self, document: str) -> List[float]:
        """Generate embeddings for a document (for indexing)"""
        if not document or not document.strip():
            return [0.0] * self.get_embedding_dimension()
        
        # For documents, no special prefix needed
        return self.embed_text(document.strip())
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model"""
        if not self.model:
            # BGE-large-en-v1.5 produces 1024-dimensional embeddings
            return 1024
        
        return self.model.get_sentence_embedding_dimension()
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute dot product similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Compute dot product (assuming normalized embeddings)
            similarity = np.dot(vec1, vec2)
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to compute similarity: {str(e)}")
            return 0.0
    
    def is_available(self) -> bool:
        """Check if the embedding service is available"""
        return SENTENCE_TRANSFORMERS_AVAILABLE and self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model"""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.get_embedding_dimension(),
            "available": self.is_available(),
            "library": "sentence-transformers" if SENTENCE_TRANSFORMERS_AVAILABLE else None
        }


# Global embedding client instance
_embedding_client: Optional[BGEEmbeddingClient] = None


def get_embedding_client() -> BGEEmbeddingClient:
    """Get or create the global embedding client"""
    global _embedding_client
    
    if _embedding_client is None:
        _embedding_client = BGEEmbeddingClient()
    
    return _embedding_client


def embed_text(text: str) -> List[float]:
    """Convenience function to embed a single text"""
    client = get_embedding_client()
    return client.embed_text(text)


def embed_query(query: str) -> List[float]:
    """Convenience function to embed a query"""
    client = get_embedding_client()
    return client.embed_query(query)


def embed_document(document: str) -> List[float]:
    """Convenience function to embed a document"""
    client = get_embedding_client()
    return client.embed_document(document)