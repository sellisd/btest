"""Base interface for movie script scrapers."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging
import asyncio
from datetime import datetime, timedelta
import aiohttp
from ..exceptions import ScrapingError

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Abstract base class for movie script scrapers."""
    
    def __init__(self, rate_limit: int = 1, timeout: int = 30):
        """Initialize the scraper.
        
        Args:
            rate_limit: Minimum seconds between requests
            timeout: Request timeout in seconds
        """
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.last_request: Optional[datetime] = None
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Context manager entry."""
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._session:
            await self._session.close()
            self._session = None

    async def _wait_for_rate_limit(self) -> None:
        """Wait for rate limit if needed."""
        if self.last_request:
            elapsed = datetime.now() - self.last_request
            if elapsed < timedelta(seconds=self.rate_limit):
                await asyncio.sleep(self.rate_limit - elapsed.total_seconds())
        self.last_request = datetime.now()

    async def _fetch(self, url: str, headers: Optional[Dict[str, str]] = None) -> str:
        """Fetch a URL with rate limiting and retries.
        
        Args:
            url: URL to fetch
            headers: Optional request headers
        
        Returns:
            Response text
            
        Raises:
            ScrapingError: If the request fails after retries
        """
        if not self._session:
            raise ScrapingError("Session not initialized. Use async context manager.")
            
        await self._wait_for_rate_limit()
        
        try:
            async with self._session.get(url, headers=headers, timeout=self.timeout) as response:
                if response.status != 200:
                    raise ScrapingError(f"HTTP {response.status}: {await response.text()}")
                return await response.text()
                
        except asyncio.TimeoutError:
            raise ScrapingError(f"Request timed out after {self.timeout} seconds")
        except aiohttp.ClientError as e:
            raise ScrapingError(f"Request failed: {str(e)}")

    @abstractmethod
    async def search_script(self, title: str) -> Optional[Dict[str, Any]]:
        """Search for a movie script.
        
        Args:
            title: Movie title to search for
            
        Returns:
            Dict containing script info if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_script(self, script_url: str) -> str:
        """Fetch and parse a script from its URL.
        
        Args:
            script_url: URL to fetch script from
            
        Returns:
            Parsed script text
            
        Raises:
            ScrapingError: If script cannot be fetched/parsed
        """
        pass
