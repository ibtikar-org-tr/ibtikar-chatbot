"""
Vector store index model for tracking vector embeddings.
"""
from sqlalchemy import Column, String, Text, Integer, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class VectorIndex(Base):
    """Vector index model for tracking embeddings."""
    
    __tablename__ = "vector_indices"
    
    # Reference to document
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    
    # Vector information
    vector_id = Column(String(100), nullable=False, unique=True, index=True)
    chunk_index = Column(Integer, default=0)
    chunk_text = Column(Text, nullable=False)
    
    # Vector store information
    vector_store_type = Column(String(50), nullable=False)  # faiss, upstash, etc.
    namespace = Column(String(100))
    
    # Embedding metadata
    embedding_model = Column(String(100))
    embedding_dimension = Column(Integer)
    
    # Search metadata
    similarity_threshold = Column(Float, default=0.7)
    
    # Additional metadata
    metadata = Column(JSON)
    
    # Relationships
    document = relationship("Document", backref="vector_indices")
    
    def __repr__(self):
        return f"<VectorIndex(id={self.id}, vector_id='{self.vector_id}', document_id={self.document_id})>"
