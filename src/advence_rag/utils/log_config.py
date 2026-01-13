"""Logging configuration."""

import logging
import sys
from typing import Literal
from pythonjsonlogger import jsonlogger

def setup_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO",
) -> logging.Logger:
    """Set up logging configuration with JSON formatting.
    
    Args:
        level: Log level string
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("advence_rag")
    logger.setLevel(getattr(logging, level))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level))
        
        # JSON Formatter
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(trace_id)s %(span_id)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            json_ensure_ascii=False
        )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Silence noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    return logger
