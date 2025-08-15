"""
Core configuration settings for the Ibtikar Chatbot application.
"""
import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Ibtikar Community RAG Chatbot"
    APP_VERSION: str = "0.1.0"
    DESCRIPTION: str = "Arabic-first RAG chatbot system for university students"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
    # Storage Configuration
    STORAGE_BACKEND: str = Field(default="local", env="STORAGE_BACKEND")
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = Field(default=None, env="AZURE_STORAGE_CONNECTION_STRING")
    AZURE_CONTAINER_NAME: str = Field(default="documents", env="AZURE_CONTAINER_NAME")
    LOCAL_STORAGE_PATH: str = Field(default="./data/storage", env="LOCAL_STORAGE_PATH")
    
    # Vector Store Configuration
    VECTOR_BACKEND: str = Field(default="faiss", env="VECTOR_BACKEND")
    FAISS_INDEX_PATH: str = Field(default="./data/vector_store/faiss_index", env="FAISS_INDEX_PATH")
    UPSTASH_VECTOR_URL: Optional[str] = Field(default=None, env="UPSTASH_VECTOR_URL")
    UPSTASH_VECTOR_TOKEN: Optional[str] = Field(default=None, env="UPSTASH_VECTOR_TOKEN")
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = Field(default="BAAI/bge-m3", env="EMBEDDING_MODEL")
    EMBEDDING_DIMENSION: int = Field(default=1024, env="EMBEDDING_DIMENSION")
    
    # Scraping Configuration
    SCRAPE_BACKEND: str = Field(default="requests", env="SCRAPE_BACKEND")
    MAX_SCRAPE_DEPTH: int = Field(default=3, env="MAX_SCRAPE_DEPTH")
    SCRAPE_DELAY: float = Field(default=1.0, env="SCRAPE_DELAY")
    CHUNK_SIZE: int = Field(default=500, env="CHUNK_SIZE")
    BATCH_SIZE: int = Field(default=10, env="BATCH_SIZE")
    
    # Database Configuration
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    DB_ECHO: bool = Field(default=False, env="DB_ECHO")
    
    # Redis Configuration
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="%(asctime)s [%(levelname)s] %(name)s: %(message)s", env="LOG_FORMAT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
