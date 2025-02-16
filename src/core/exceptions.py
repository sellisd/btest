"""Custom exceptions for the application."""


class BtestError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str):
        """Initialize BtestError.

        Args:
            message: Error message explaining what went wrong
        """
        self.message = message
        super().__init__(self.message)


class LLMError(BtestError):
    """Exception raised when LLM operations fail."""

    pass


class ConfigurationError(BtestError):
    """Exception raised when configuration is invalid."""

    pass


class ScrapingError(BtestError):
    """Exception raised when script scraping fails."""

    pass


class ConversationError(BtestError):
    """Exception raised when conversation processing fails."""

    pass
