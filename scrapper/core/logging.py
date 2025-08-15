"""
Logging configuration for the application.
"""
import logging
import sys
from typing import Optional

from core.config import settings


def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """Configure application logging."""
    
    log_level = level or settings.LOG_LEVEL
    log_format = format_string or settings.LOG_FORMAT
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(numeric_level)
    logging.getLogger("fastapi").setLevel(numeric_level)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Application logger
    logger = logging.getLogger("ibtikar_chatbot")
    logger.setLevel(numeric_level)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(f"ibtikar_chatbot.{name}")
