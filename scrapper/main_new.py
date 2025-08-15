"""
FastAPI Main Application

This is the main entry point for the Ibtikar Community RAG Chatbot API.
Refactored for better structure and maintainability.
"""
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import settings
from core.logging import setup_logging, get_logger
from core.exceptions import IbtikarChatbotException
from endpoints import scraping, search, health

# Set event loop policy on Windows to avoid NotImplementedError with subprocess
if sys.platform.startswith("win"):
    policy = asyncio.WindowsProactorEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    logger = get_logger("startup")
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Storage backend: {settings.STORAGE_BACKEND}")
    logger.info(f"Vector backend: {settings.VECTOR_BACKEND}")
    logger.info(f"Embedding model: {settings.EMBEDDING_MODEL}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.APP_VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(IbtikarChatbotException)
async def ibtikar_exception_handler(request: Request, exc: IbtikarChatbotException):
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=400,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger = get_logger("exception")
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_ERROR",
            "message": "An internal error occurred"
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - Welcome message"""
    return {
        "message": "مرحباً بكم في نظام الدردشة الذكي لمجتمع إبتكار",
        "welcome": "Welcome to Ibtikar Community RAG Chatbot",
        "status": "active",
        "version": settings.APP_VERSION,
        "docs_url": settings.DOCS_URL,
        "api_prefix": settings.API_V1_PREFIX
    }


# Include API routers
app.include_router(
    health.router,
    prefix=settings.API_V1_PREFIX,
    tags=["health"]
)

app.include_router(
    scraping.router,
    prefix=settings.API_V1_PREFIX,
    tags=["scraping"]
)

app.include_router(
    search.router,
    prefix=settings.API_V1_PREFIX,
    tags=["search"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
