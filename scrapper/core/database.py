"""
Database connection and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

from core.config import settings

# Create database engine
engine = None
SessionLocal = None

if settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_pre_ping=True
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import all models to ensure they are registered with SQLAlchemy
from models import Base  # noqa


def get_db() -> Generator:
    """Get database session."""
    if not SessionLocal:
        raise RuntimeError("Database not configured. Set DATABASE_URL in environment.")
    
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    if engine:
        Base.metadata.create_all(bind=engine)
