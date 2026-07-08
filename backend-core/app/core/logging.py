import logging
import sys
import os

def setup_logging() -> logging.Logger:
    """Configure structured logging for the application."""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

    # Create logger
    logger = logging.getLogger('bip')
    logger.setLevel(getattr(logging, log_level))

    # Console handler with formatting
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, log_level))

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger

# Module-level logger for use throughout app
logger = setup_logging()
