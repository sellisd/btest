"""Custom exceptions for the btest package."""

class BtestError(Exception):
    """Base exception for all btest errors."""
    pass

class LLMError(BtestError):
    """Raised when there are issues with LLM operations."""
    pass

class ScriptError(BtestError):
    """Base class for script-related errors."""
    pass

class ScriptNotFoundError(ScriptError):
    """Raised when a requested script cannot be found."""
    pass

class ScriptParseError(ScriptError):
    """Raised when a script cannot be parsed correctly."""
    pass

class ConfigurationError(BtestError):
    """Raised when there are configuration issues."""
    pass

class ValidationError(BtestError):
    """Raised when validation fails."""
    pass

class ConversationError(BtestError):
    """Raised when there are issues analyzing conversations."""
    pass

class CharacterError(BtestError):
    """Raised when there are issues with character analysis."""
    pass
