"""Tests for custom exceptions."""

import unittest
from src.core.exceptions import (
    BtestError,
    LLMError,
    ScriptError,
    ScriptNotFoundError,
    ScriptParseError,
    ConfigurationError,
    ValidationError,
    ConversationError,
    CharacterError,
)


class TestExceptions(unittest.TestCase):
    """Test custom exceptions."""

    def test_exception_hierarchy(self):
        """Test exception inheritance hierarchy."""
        # All custom exceptions should inherit from BtestError
        self.assertTrue(issubclass(LLMError, BtestError))
        self.assertTrue(issubclass(ScriptError, BtestError))
        self.assertTrue(issubclass(ConfigurationError, BtestError))
        self.assertTrue(issubclass(ValidationError, BtestError))
        self.assertTrue(issubclass(ConversationError, BtestError))
        self.assertTrue(issubclass(CharacterError, BtestError))

        # Script-specific errors should inherit from ScriptError
        self.assertTrue(issubclass(ScriptNotFoundError, ScriptError))
        self.assertTrue(issubclass(ScriptParseError, ScriptError))

        # All should ultimately inherit from Exception
        self.assertTrue(issubclass(BtestError, Exception))

    def test_error_messages(self):
        """Test error message handling."""
        msg = "Test error message"

        # Test each exception type
        self.assertEqual(str(BtestError(msg)), msg)
        self.assertEqual(str(LLMError(msg)), msg)
        self.assertEqual(str(ScriptError(msg)), msg)
        self.assertEqual(str(ScriptNotFoundError(msg)), msg)
        self.assertEqual(str(ScriptParseError(msg)), msg)
        self.assertEqual(str(ConfigurationError(msg)), msg)
        self.assertEqual(str(ValidationError(msg)), msg)
        self.assertEqual(str(ConversationError(msg)), msg)
        self.assertEqual(str(CharacterError(msg)), msg)

    def test_exception_chaining(self):
        """Test exception chaining."""

        def raise_chained():
            try:
                raise ValueError("Original error")
            except ValueError as original:
                raise LLMError("Chained error") from original

        with self.assertRaises(LLMError) as context:
            raise_chained()

        self.assertEqual(str(context.exception), "Chained error")
        self.assertIsInstance(context.exception.__cause__, ValueError)
        self.assertEqual(str(context.exception.__cause__), "Original error")

    def test_error_usage(self):
        """Test practical usage of exceptions."""

        def raise_script_error():
            raise ScriptNotFoundError("Script not found")

        def raise_llm_error():
            try:
                raise ConnectionError("Connection failed")
            except ConnectionError as e:
                raise LLMError("LLM operation failed") from e

        # Test script error
        with self.assertRaises(ScriptNotFoundError) as context:
            raise_script_error()
        self.assertEqual(str(context.exception), "Script not found")

        # Test LLM error with chaining
        with self.assertRaises(LLMError) as context:
            raise_llm_error()
        self.assertEqual(str(context.exception), "LLM operation failed")
        self.assertIsInstance(context.exception.__cause__, ConnectionError)
