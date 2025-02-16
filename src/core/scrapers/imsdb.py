"""IMSDB movie script scraper implementation."""

import re
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import quote  # Add this import at the top
from .base import BaseScraper, ScrapingError


class IMSDBScraper(BaseScraper):
    """Scraper for the Internet Movie Script Database (IMSDB)."""

    BASE_URL = "https://imsdb.com"
    SEARCH_URL = f"{BASE_URL}/search.php"

    def __init__(self, rate_limit: int = 2, timeout: int = 30):
        """Initialize IMSDB scraper with conservative rate limiting."""
        super().__init__(rate_limit=rate_limit, timeout=timeout)

    async def search_script(self, title: str) -> Optional[Dict[str, Any]]:
        """Search for a movie script on IMSDB."""
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; MovieScriptBot/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        try:
            # Search for the script
            html = await self._fetch(
                f"{self.SEARCH_URL}?query={title.replace(' ', '+')}", headers=headers
            )
            soup = BeautifulSoup(html, "html.parser")

            # Find script links in search results
            results = soup.select("p a[href*='/Movie Scripts/']")

            if not results:
                return None

            # Get the first result (most relevant match)
            script_link = results[0]
            script_title = script_link.text.strip()

            # Convert movie title to script URL format
            # Example: "The Matrix" -> "Matrix,-The.html"
            formatted_title = script_title.strip()
            if formatted_title.lower().startswith("the "):
                formatted_title = f"{formatted_title[4:]},-The"
            formatted_title = formatted_title.replace(" ", "-")

            # Construct direct script URL
            script_path = f"/scripts/{formatted_title}.html"
            script_url = f"{self.BASE_URL}{quote(script_path)}"

            return {"title": script_title, "url": script_url, "source": "IMSDB"}

        except Exception as e:
            raise ScrapingError(f"Failed to search IMSDB: {str(e)}")

    async def get_script(self, script_url: str) -> str:
        """Fetch and parse a script from IMSDB.

        Args:
            script_url: Script page URL

        Returns:
            Parsed script text

        Raises:
            ScrapingError: If script cannot be fetched/parsed
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; MovieScriptBot/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        try:
            # First get the script viewer page
            html = await self._fetch(script_url, headers=headers)
            soup = BeautifulSoup(html, "html.parser")
            # Find the pre-formatted script text
            script_pre = soup.find("pre")

            if not script_pre:
                raise ScrapingError("Could not find script content")

            script_text = script_pre.get_text(strip=True)

            # Basic cleaning
            script_text = re.sub(
                r"\n{3,}", "\n\n", script_text
            )  # Remove excessive newlines
            script_text = re.sub(
                r"[ \t]+\n", "\n", script_text
            )  # Remove trailing whitespace

            return script_text

        except Exception as e:
            raise ScrapingError(f"Failed to fetch script from IMSDB: {str(e)}")

    def __repr__(self) -> str:
        """Return string representation."""
        return f"IMSDBScraper(rate_limit={self.rate_limit}, timeout={self.timeout})"
