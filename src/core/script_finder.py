"""Module for finding and retrieving movie scripts."""

import logging
import asyncio
from typing import Optional, List
from .scrapers.base import BaseScraper
from .scrapers.imsdb import IMSDBScraper

logger = logging.getLogger(__name__)


class ScriptFinder:
    """Handles retrieving movie scripts from online sources."""

    def __init__(self):
        """Initialize ScriptFinder with available scrapers."""
        self.scrapers: List[BaseScraper] = [
            IMSDBScraper()  # Add more scrapers here as they're implemented
        ]

    async def find_script(self, title: str) -> Optional[str]:
        """Find and return movie script by title.

        Args:
            title: Movie title to search for.

        Returns:
            Formatted script text if found, None otherwise.
        """
        for scraper in self.scrapers:
            try:
                async with scraper:
                    # Search for the script
                    result = await scraper.search_script(title)
                    if result:
                        # Get the full script text
                        script = await scraper.get_script(result["url"])
                        logger.info(f"Found script for '{title}' on {result['source']}")
                        return script
            except Exception as e:
                logger.error(f"Error searching {scraper.__class__.__name__}: {e}")
                continue

        logger.warning(f"No script found for title: {title}")
        return None

    def find_script_sync(self, title: str) -> Optional[str]:
        """Synchronous wrapper for find_script.

        Args:
            title: Movie title to search for.

        Returns:
            Formatted script text if found, None otherwise.
        """
        return asyncio.run(self.find_script(title))
