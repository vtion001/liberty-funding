"""Logging utility"""
import logging
import sys
from pathlib import Path
from config.settings import LOG_LEVEL, LOG_FILE

def setup_logger(name: str = __name__) -> logging.Logger:
    """Setup logger with file and console output"""
    logger = logging.getLogger(name)
    
    # Set level
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")
    console.setFormatter(console_formatter)
    
    # File handler
    Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console)
    logger.addHandler(file_handler)
    
    return logger


# Default logger
logger = setup_logger(__name__)
