"""Module for centralized configuration management."""

import os
from dataclasses import dataclass, field
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class ConfigError(Exception):
    """Base exception for configuration errors."""

    pass


class LLMConfigModel(BaseModel):
    """Pydantic model for LLM configuration validation."""

    model: str = Field(default="llama2", min_length=1)
    host: Optional[str] = Field(default="http://localhost:11434")
    timeout: int = Field(default=30, ge=1)
    cache_size: int = Field(default=128, ge=1)

    @field_validator("host")
    def validate_host(cls, v):
        """Validate host URL format."""
        if v and not (v.startswith("http://") or v.startswith("https://")):
            return f"http://{v}"
        return v


class CORSConfigModel(BaseModel):
    """Pydantic model for CORS configuration validation."""

    allow_origins: List[str] = Field(default=["*"])
    allow_credentials: bool = Field(default=True)
    allow_methods: List[str] = Field(default=["*"])
    allow_headers: List[str] = Field(default=["*"])

    @field_validator("allow_origins")
    def validate_origins(cls, v):
        """Validate origins list."""
        if "*" in v and len(v) > 1:
            raise ValueError('Cannot mix "*" with other origins')
        return v


@dataclass
class LLMConfig:
    """Configuration for LLM integration."""

    model: str = field(default="llama2")
    host: Optional[str] = field(default="http://localhost:11434")
    timeout: int = field(default=30)
    cache_size: int = field(default=128)

    @classmethod
    def from_env(cls) -> "LLMConfig":
        """Create config from environment variables."""
        try:
            # Get raw values from environment
            model = os.getenv("OLLAMA_MODEL", "llama2")
            host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            timeout_str = os.getenv("OLLAMA_TIMEOUT", "30")
            cache_size_str = os.getenv("OLLAMA_CACHE_SIZE", "128")

            # Validate using pydantic model
            config_model = LLMConfigModel(
                model=model,
                host=host,
                timeout=int(timeout_str),
                cache_size=int(cache_size_str),
            )

            return cls(
                model=config_model.model,
                host=config_model.host,
                timeout=config_model.timeout,
                cache_size=config_model.cache_size,
            )
        except ValueError as e:
            raise ConfigError(f"Invalid LLM configuration: {str(e)}")


@dataclass
class LogConfig:
    """Configuration for logging."""

    level: str = field(default="INFO")
    format: str = field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    @classmethod
    def from_env(cls) -> "LogConfig":
        """Create config from environment variables."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        level = os.getenv("LOG_LEVEL", "INFO").upper()

        if level not in valid_levels:
            raise ConfigError(
                f"Invalid log level: {level}. Must be one of {valid_levels}"
            )

        return cls(
            level=level,
            format=os.getenv(
                "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ),
        )


@dataclass
class CORSConfig:
    """Configuration for CORS settings."""

    allow_origins: List[str] = field(default_factory=lambda: ["*"])
    allow_credentials: bool = field(default=True)
    allow_methods: List[str] = field(default_factory=lambda: ["*"])
    allow_headers: List[str] = field(default_factory=lambda: ["*"])

    @classmethod
    def from_env(cls) -> "CORSConfig":
        """Create config from environment variables."""
        try:
            # Parse origins from comma-separated string
            origins_str = os.getenv("CORS_ALLOW_ORIGINS", "*")
            origins = [o.strip() for o in origins_str.split(",")]

            # Parse methods and headers if specified
            methods_str = os.getenv("CORS_ALLOW_METHODS", "*")
            methods = [m.strip() for m in methods_str.split(",")]

            headers_str = os.getenv("CORS_ALLOW_HEADERS", "*")
            headers = [h.strip() for h in headers_str.split(",")]

            # Parse credentials bool
            credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

            # Validate using pydantic model
            config_model = CORSConfigModel(
                allow_origins=origins,
                allow_credentials=credentials,
                allow_methods=methods,
                allow_headers=headers,
            )

            return cls(
                allow_origins=config_model.allow_origins,
                allow_credentials=config_model.allow_credentials,
                allow_methods=config_model.allow_methods,
                allow_headers=config_model.allow_headers,
            )
        except ValueError as e:
            raise ConfigError(f"Invalid CORS configuration: {str(e)}")


# Global configuration instances
try:
    llm_config = LLMConfig.from_env()
    log_config = LogConfig.from_env()
    cors_config = CORSConfig.from_env()
except ConfigError as e:
    import sys

    print(f"Configuration error: {e}", file=sys.stderr)
    sys.exit(1)
