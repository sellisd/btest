"""Core functionality for the Bechdel test analyzer."""

import logging
from .config import llm_config, log_config
from .exceptions import (
    BtestError,
    LLMError,
    ConfigurationError,
    ScrapingError,
    ConversationError,
)
from .logger import setup_logger
from .text_processor import TextProcessor
from .character import Character, CharacterClassifier
from .conversation import ConversationAnalyzer
from .analyzer import BechdelAnalyzer

# Initialize package logging
logger = setup_logger("btest.core")
logger.debug("Initializing btest.core package")

# Export public classes
__all__ = [
    "TextProcessor",
    "Character",
    "CharacterClassifier",
    "ConversationAnalyzer",
    "BechdelAnalyzer",
    "BtestError",
    "LLMError",
    "ConfigurationError",
    "ScrapingError",
    "ConversationError",
]

# Log configuration on import
logger.info(f"Using LLM model: {llm_config.model}")
if llm_config.host:
    logger.info(f"Using custom Ollama host: {llm_config.host}")
logger.debug(f"Log level set to: {log_config.level}")
