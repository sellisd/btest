"""Module for centralized configuration management."""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class LLMConfig:
    """Configuration for LLM integration."""
    
    model: str = "llama2"
    host: Optional[str] = None
    timeout: int = 30
    cache_size: int = 128

    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """Create config from environment variables."""
        return cls(
            model=os.getenv("OLLAMA_MODEL", "llama2"),
            host=os.getenv("OLLAMA_HOST"),
            timeout=int(os.getenv("OLLAMA_TIMEOUT", "30")),
            cache_size=int(os.getenv("OLLAMA_CACHE_SIZE", "128")),
        )

@dataclass
class LogConfig:
    """Configuration for logging."""
    
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def from_env(cls) -> 'LogConfig':
        """Create config from environment variables."""
        return cls(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv(
                "LOG_FORMAT",
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ),
        )

# Global configuration instances
llm_config = LLMConfig.from_env()
log_config = LogConfig.from_env()
