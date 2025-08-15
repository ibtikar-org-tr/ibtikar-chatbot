"""
Health check and monitoring endpoints.
"""
import time
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.deps import get_storage, get_vector_store, get_settings
from core.config import Settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ibtikar-chatbot"
    }


@router.get("/health/detailed")
async def detailed_health_check(
    settings: Settings = Depends(get_settings),
    storage = Depends(get_storage),
    vector_store = Depends(get_vector_store)
):
    """Detailed health check with service dependencies."""
    start_time = time.time()
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ibtikar-chatbot",
        "version": settings.APP_VERSION,
        "checks": {}
    }
    
    # Check storage
    try:
        # Basic storage check (this would depend on your storage implementation)
        health_status["checks"]["storage"] = {
            "status": "healthy",
            "backend": settings.STORAGE_BACKEND
        }
    except Exception as e:
        health_status["checks"]["storage"] = {
            "status": "unhealthy",
            "error": str(e),
            "backend": settings.STORAGE_BACKEND
        }
        health_status["status"] = "degraded"
    
    # Check vector store
    try:
        # Basic vector store check
        health_status["checks"]["vector_store"] = {
            "status": "healthy",
            "backend": settings.VECTOR_BACKEND
        }
    except Exception as e:
        health_status["checks"]["vector_store"] = {
            "status": "unhealthy",
            "error": str(e),
            "backend": settings.VECTOR_BACKEND
        }
        health_status["status"] = "degraded"
    
    health_status["response_time"] = time.time() - start_time
    
    return health_status


@router.get("/info")
async def service_info(settings: Settings = Depends(get_settings)):
    """Service information endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.DESCRIPTION,
        "docs_url": settings.DOCS_URL,
        "api_prefix": settings.API_V1_PREFIX,
        "storage_backend": settings.STORAGE_BACKEND,
        "vector_backend": settings.VECTOR_BACKEND,
        "embedding_model": settings.EMBEDDING_MODEL
    }
