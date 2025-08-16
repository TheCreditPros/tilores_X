"""
Debug Configuration for Tilores_X
Centralized debug control for the entire application
"""

import os
import logging
from typing import Optional

# Get debug mode from environment variable
DEBUG_MODE = os.getenv("TILORES_DEBUG", "false").lower() in ["true", "1", "yes"]

# Configure logging level based on debug mode
LOG_LEVEL = logging.DEBUG if DEBUG_MODE else logging.INFO

def setup_logging(name: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration for a module
    
    Args:
        name: Module name (uses __name__ if not provided)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or __name__)
    
    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            if DEBUG_MODE else
            '%(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(LOG_LEVEL)
    
    return logger

def debug_print(message: str, emoji: str = "🔍") -> None:
    """
    Print debug message only when DEBUG_MODE is enabled
    
    Args:
        message: Debug message to print
        emoji: Emoji prefix for the message
    """
    if DEBUG_MODE:
        print(f"{emoji} [DEBUG] {message}")

def is_debug_enabled() -> bool:
    """Check if debug mode is enabled"""
    return DEBUG_MODE

# Create default logger for this module
logger = setup_logging(__name__)

# Log initial debug status
if DEBUG_MODE:
    logger.debug("Debug mode is ENABLED")