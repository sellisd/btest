"""Cinematheque.fr movie script scraper implementation."""

import re
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import BaseScraper, ScrapingError

class CinemathequeScaper(BaseScraper):
    """Scraper for Cinematheque.fr script collection."""

    BASE_URL = "https://www.cinematheque.fr"
    SEARCH_URL = f"{BASE_URL}/rechercher/scenario"

    def __init__(self, rate_limit: int = 2, timeout: int = 30):
        """Initialize Cinematheque scraper with conservative rate limiting."""
        super().__init__(rate_limit=rate_limit, timeout=timeout)

    async def search_script(self, title: str) -> Optional[Dict[str, Any]]:
        """Search for a movie script on Cinematheque.fr.
        
        Args:
            title: Movie title to search for
            
        Returns:
            Dict with script info if found, None otherwise
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; MovieScriptBot/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        try:
            # Search using their internal search
            search_url = f"{self.SEARCH_URL}?q={title.replace(' ', '+')}"
            html = await self._fetch(search_url, headers=headers)
            soup = BeautifulSoup(html, "html.parser")
            
            # Find script entries in search results
            results = soup.select("article.search-result")
            
            if not results:
                return None
                
            # Get the first result with a script
            for result in results:
                # Check if it's a script entry
                if "scénario" not in result.text.lower():
                    continue
                    
                # Get title and link
                title_elem = result.select_one("h3 a")
                if not title_elem:
                    continue
                    
                script_title = title_elem.text.strip()
                script_path = title_elem["href"]
                
                # Convert relative URL to absolute
                script_url = urljoin(self.BASE_URL, script_path)
                
                return {
                    "title": script_title,
                    "url": script_url,
                    "source": "Cinematheque"
                }
            
            return None
            
        except Exception as e:
            raise ScrapingError(f"Failed to search Cinematheque.fr: {str(e)}")

    async def get_script(self, script_url: str) -> str:
        """Fetch and parse a script from Cinematheque.fr.
        
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
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        try:
            # Get the script page
            html = await self._fetch(script_url, headers=headers)
            soup = BeautifulSoup(html, "html.parser")
            
            # Find the script content
            content_div = soup.select_one("div.scenario-content")
            if not content_div:
                raise ScrapingError("Could not find script content")
                
            # Extract text, preserving important formatting
            def extract_text(element) -> str:
                texts = []
                for child in element.children:
                    if child.name == 'br':
                        texts.append('\n')
                    elif child.name == 'p':
                        texts.append(child.get_text(strip=True) + '\n')
                    elif child.string:
                        texts.append(child.string)
                return ''.join(texts)
                
            script_text = extract_text(content_div)
            
            # Clean up the text
            script_text = re.sub(r'\n{3,}', '\n\n', script_text)  # Remove excessive newlines
            script_text = re.sub(r'[ \t]+\n', '\n', script_text)  # Remove trailing whitespace
            
            return script_text.strip()
            
        except Exception as e:
            raise ScrapingError(f"Failed to fetch script from Cinematheque.fr: {str(e)}")

    def __repr__(self) -> str:
        """Return string representation."""
        return f"CinemathequeScaper(rate_limit={self.rate_limit}, timeout={self.timeout})"
