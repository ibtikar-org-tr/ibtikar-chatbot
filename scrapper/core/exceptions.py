"""
Custom exception classes for the application.
"""
from typing import Any, Dict, Optional


class IbtikarChatbotException(Exception):
    """Base exception class for the application."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ScrapingException(IbtikarChatbotException):
    """Exception raised during web scraping operations."""
    
    def __init__(self, message: str, url: Optional[str] = None, **kwargs):
        self.url = url
        super().__init__(message, error_code="SCRAPING_ERROR", **kwargs)


class StorageException(IbtikarChatbotException):
    """Exception raised during storage operations."""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        self.operation = operation
        super().__init__(message, error_code="STORAGE_ERROR", **kwargs)


class VectorStoreException(IbtikarChatbotException):
    """Exception raised during vector store operations."""
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        self.operation = operation
        super().__init__(message, error_code="VECTOR_STORE_ERROR", **kwargs)


class EmbeddingException(IbtikarChatbotException):
    """Exception raised during embedding operations."""
    
    def __init__(self, message: str, model: Optional[str] = None, **kwargs):
        self.model = model
        super().__init__(message, error_code="EMBEDDING_ERROR", **kwargs)


class DataProcessingException(IbtikarChatbotException):
    """Exception raised during data processing operations."""
    
    def __init__(self, message: str, stage: Optional[str] = None, **kwargs):
        self.stage = stage
        super().__init__(message, error_code="DATA_PROCESSING_ERROR", **kwargs)
