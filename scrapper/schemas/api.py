"""
Pydantic schemas for API request/response models.
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, HttpUrl, validator


class DocumentBase(BaseModel):
    """Base schema for document."""
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    url: str = Field(..., max_length=2000)
    content_type: Optional[str] = None
    language: Optional[str] = "ar"
    metadata: Optional[Dict[str, Any]] = {}


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""
    pass


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    is_processed: Optional[bool] = None
    is_indexed: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(DocumentBase):
    """Schema for document response."""
    id: int
    word_count: Optional[int] = None
    is_processed: bool = False
    is_indexed: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    scraped_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    indexed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ScrapeRequest(BaseModel):
    """Schema for scraping request."""
    url: Optional[HttpUrl] = None
    max_depth: Optional[int] = Field(3, ge=1, le=10)
    max_pages: Optional[int] = Field(100, ge=1, le=1000)
    
    @validator('url', 'max_depth', 'max_pages', pre=True, always=True)
    def validate_at_least_one_input(cls, v, values):
        if not values.get('url'):
            raise ValueError('URL is required for scraping')
        return v


class ScrapeResponse(BaseModel):
    """Schema for scraping response."""
    message: str
    documents_count: int
    urls_scraped: List[str]
    processing_time: Optional[float] = None


class SearchRequest(BaseModel):
    """Schema for search request."""
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: Optional[int] = Field(10, ge=1, le=100)
    similarity_threshold: Optional[float] = Field(0.7, ge=0.0, le=1.0)
    namespace: Optional[str] = None


class SearchResult(BaseModel):
    """Schema for individual search result."""
    document_id: int
    title: str
    content: str
    url: str
    similarity_score: float
    metadata: Optional[Dict[str, Any]] = {}


class SearchResponse(BaseModel):
    """Schema for search response."""
    query: str
    results: List[SearchResult]
    total_results: int
    processing_time: Optional[float] = None


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
