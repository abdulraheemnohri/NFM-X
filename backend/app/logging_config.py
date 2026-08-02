"""
NFM-X V4 Logging Configuration
Configures logging to file and console based on settings
"""

import logging
import logging.handlers
import os
from typing import Optional

from backend.app.config import get_config


def setup_logging() -> None:
    """
    Configure logging based on configuration
    Supports both console and file logging
    """
    config = get_config()
    log_config = config.logging
    
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_config.level.upper(), logging.INFO))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    if log_config.console_enabled:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_config.level.upper(), logging.INFO))
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler
    if log_config.file_enabled:
        # Ensure directory exists
        log_dir = os.path.dirname(log_config.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Rotating file handler
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_config.log_file,
            maxBytes=log_config.max_file_size_mb * 1024 * 1024,
            backupCount=log_config.backup_count,
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, log_config.level.upper(), logging.INFO))
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Set levels for specific loggers
    logging.getLogger("uvicorn").setLevel(getattr(logging, log_config.level.upper(), logging.INFO))
    logging.getLogger("uvicorn.access").setLevel(getattr(logging, log_config.level.upper(), logging.INFO))
    logging.getLogger("fastapi").setLevel(getattr(logging, log_config.level.upper(), logging.INFO))
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={log_config.level}, file_enabled={log_config.file_enabled}, console_enabled={log_config.console_enabled}")
    if log_config.file_enabled:
        logger.info(f"Logging to file: {log_config.log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name
    """
    return logging.getLogger(name)


# Initialize logging when module is imported
# Note: This will be called when the application starts
# To use: import backend.app.logging_config at the start of your application