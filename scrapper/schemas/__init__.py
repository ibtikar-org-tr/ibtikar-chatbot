"""
Pydantic schemas for API request/response models.
"""
from schemas.api import (
    DocumentBase,
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    ScrapeRequest,
    ScrapeResponse,
    SearchRequest,
    SearchResult,
    SearchResponse,
    ErrorResponse,
)

__all__ = [
    "DocumentBase",
    "DocumentCreate", 
    "DocumentUpdate",
    "DocumentResponse",
    "ScrapeRequest",
    "ScrapeResponse", 
    "SearchRequest",
    "SearchResult",
    "SearchResponse",
    "ErrorResponse",
]
