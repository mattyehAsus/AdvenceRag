from advence_rag.utils.log_config import setup_logging
import logging
import pytest

def test_setup_logging_returns_logger():
    """Test that setup_logging returns a Logger instance."""
    logger = setup_logging()
    assert isinstance(logger, logging.Logger)
    assert logger.name == "advence_rag"

def test_setup_logging_level():
    """Test that setup_logging correctly sets the log level."""
    logger = setup_logging(level="DEBUG")
    assert logger.level == logging.DEBUG
    
    logger = setup_logging(level="ERROR")
    assert logger.level == logging.ERROR

def test_setup_logging_singleton_handlers():
    """Test that multiple calls to setup_logging don't duplicate handlers."""
    logger = setup_logging()
    initial_handler_count = len(logger.handlers)
    
    logger = setup_logging()
    assert len(logger.handlers) == initial_handler_count
