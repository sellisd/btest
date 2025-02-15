"""Tests for configuration management."""

import os
from unittest import TestCase, mock

from src.core.config import LLMConfig, LogConfig

class TestLLMConfig(TestCase):
    """Test LLM configuration."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = LLMConfig()
        self.assertEqual(config.model, "llama2")
        self.assertIsNone(config.host)
        self.assertEqual(config.timeout, 30)
        self.assertEqual(config.cache_size, 128)
    
    def test_from_env(self):
        """Test configuration from environment variables."""
        env_vars = {
            "OLLAMA_MODEL": "mistral",
            "OLLAMA_HOST": "localhost:11434",
            "OLLAMA_TIMEOUT": "60",
            "OLLAMA_CACHE_SIZE": "256"
        }
        
        with mock.patch.dict(os.environ, env_vars):
            config = LLMConfig.from_env()
            self.assertEqual(config.model, "mistral")
            self.assertEqual(config.host, "localhost:11434")
            self.assertEqual(config.timeout, 60)
            self.assertEqual(config.cache_size, 256)

class TestLogConfig(TestCase):
    """Test logging configuration."""
    
    def test_default_values(self):
        """Test default logging configuration."""
        config = LogConfig()
        self.assertEqual(config.level, "INFO")
        self.assertEqual(
            config.format,
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    def test_from_env(self):
        """Test logging configuration from environment variables."""
        env_vars = {
            "LOG_LEVEL": "DEBUG",
            "LOG_FORMAT": "%(levelname)s: %(message)s"
        }
        
        with mock.patch.dict(os.environ, env_vars):
            config = LogConfig.from_env()
            self.assertEqual(config.level, "DEBUG")
            self.assertEqual(config.format, "%(levelname)s: %(message)s")
