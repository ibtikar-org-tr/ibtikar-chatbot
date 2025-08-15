"""
Core dependencies and dependency injection setup.
"""
from functools import lru_cache
from typing import Generator

from core.config import Settings, settings
from services.storage.local_storage import LocalStorage
from services.storage.cloud_storage import AzureBlobStorage
from services.vector_store.faiss_store import FaissStore
from services.vector_store.vector_store_handler import VectorStoreHandler


@lru_cache()
def get_settings() -> Settings:
    """Get application settings."""
    return settings


def get_storage():
    """Get storage backend based on configuration."""
    if settings.STORAGE_BACKEND == "local":
        return LocalStorage()
    elif settings.STORAGE_BACKEND == "azure":
        return AzureBlobStorage()
    else:
        raise ValueError(f"Unsupported STORAGE_BACKEND: {settings.STORAGE_BACKEND}")


def get_vector_store():
    """Get vector store backend based on configuration."""
    if settings.VECTOR_BACKEND == "faiss":
        return FaissStore()
    else:
        return VectorStoreHandler()
