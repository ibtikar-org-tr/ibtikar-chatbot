"""
Document model for storing scraped documents.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, Boolean
from sqlalchemy.sql import func

from models.base import Base


class Document(Base):
    """Document model for storing scraped content."""
    
    __tablename__ = "documents"
    
    # Document content
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String(2000), nullable=False, index=True)
    
    # Metadata
    content_type = Column(String(100))
    language = Column(String(10), default="ar")
    word_count = Column(Integer)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    is_indexed = Column(Boolean, default=False)
    
    # Additional metadata as JSON
    metadata = Column(JSON)
    
    # Timestamps
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    indexed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title[:50]}...', url='{self.url}')>"
