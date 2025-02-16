"""Tests for movie script scrapers."""

import pytest
from typing import AsyncGenerator
import aiohttp
from unittest.mock import Mock

from src.core.scrapers import IMSDBScraper, CinemathequeScaper, ScrapingError

# Sample HTML responses for testing
IMSDB_SEARCH_HTML = """
<html>
<body>
<p><a href="/Movie Scripts/Test Movie Script.html">Test Movie</a></p>
</body>
</html>
"""

IMSDB_SCRIPT_PAGE_HTML = """
<html>
<body>
<table class="script-details">
<tr><td><a href="/scripts/Test-Movie.html">Read Script</a></td></tr>
</table>
</body>
</html>
"""

IMSDB_SCRIPT_HTML = """
<html>
<body>
<pre>
INT. ROOM - DAY

CHARACTER
This is a test script.

CHARACTER 2
This is another line.
</pre>
</body>
</html>
"""

CINEMATHEQUE_SEARCH_HTML = """
<html>
<body>
<article class="search-result">
<h3><a href="/films/test-movie">Test Movie - scénario</a></h3>
</article>
</body>
</html>
"""

CINEMATHEQUE_SCRIPT_HTML = """
<html>
<body>
<div class="scenario-content">
<p>INT. SALLE - JOUR</p>
<p>PERSONNAGE</p>
<p>C'est un script test.</p>
</div>
</body>
</html>
"""


@pytest.fixture
async def imsdb_scraper() -> AsyncGenerator[IMSDBScraper, None]:
    """Fixture for IMSDB scraper with mocked session."""
    scraper = IMSDBScraper()

    # Create mock session
    mock_session = Mock(spec=aiohttp.ClientSession)
    mock_response = Mock()
    mock_response.__aenter__.return_value = mock_response
    mock_session.get.return_value = mock_response

    scraper._session = mock_session
    yield scraper
    await scraper.__aexit__(None, None, None)


@pytest.fixture
async def cinematheque_scraper() -> AsyncGenerator[CinemathequeScaper, None]:
    """Fixture for Cinematheque scraper with mocked session."""
    scraper = CinemathequeScaper()

    # Create mock session
    mock_session = Mock(spec=aiohttp.ClientSession)
    mock_response = Mock()
    mock_response.__aenter__.return_value = mock_response
    mock_session.get.return_value = mock_response

    scraper._session = mock_session
    yield scraper
    await scraper.__aexit__(None, None, None)


@pytest.mark.asyncio
async def test_imsdb_search_script_success(imsdb_scraper):
    """Test successful script search on IMSDB."""
    # Setup mock response
    mock_response = imsdb_scraper._session.get.return_value.__aenter__.return_value
    mock_response.status = 200
    mock_response.text.return_value = IMSDB_SEARCH_HTML

    result = await imsdb_scraper.search_script("Test Movie")

    assert result is not None
    assert result["title"] == "Test Movie"
    assert "Test Movie Script.html" in result["url"]
    assert result["source"] == "IMSDB"


@pytest.mark.asyncio
async def test_imsdb_search_script_not_found(imsdb_scraper):
    """Test script search with no results on IMSDB."""
    # Setup mock response
    mock_response = imsdb_scraper._session.get.return_value.__aenter__.return_value
    mock_response.status = 200
    mock_response.text.return_value = "<html><body></body></html>"

    result = await imsdb_scraper.search_script("Nonexistent Movie")
    assert result is None


@pytest.mark.asyncio
async def test_imsdb_get_script_success(imsdb_scraper):
    """Test successful script retrieval from IMSDB."""
    # Setup mock responses for the two requests
    mock_response = imsdb_scraper._session.get.return_value.__aenter__.return_value
    mock_response.status = 200
    mock_response.text.side_effect = [IMSDB_SCRIPT_PAGE_HTML, IMSDB_SCRIPT_HTML]

    script = await imsdb_scraper.get_script("https://imsdb.com/scripts/Test-Movie.html")

    assert "INT. ROOM - DAY" in script
    assert "This is a test script." in script


@pytest.mark.asyncio
async def test_cinematheque_search_script_success(cinematheque_scraper):
    """Test successful script search on Cinematheque."""
    # Setup mock response
    mock_response = (
        cinematheque_scraper._session.get.return_value.__aenter__.return_value
    )
    mock_response.status = 200
    mock_response.text.return_value = CINEMATHEQUE_SEARCH_HTML

    result = await cinematheque_scraper.search_script("Test Movie")

    assert result is not None
    assert "Test Movie" in result["title"]
    assert "/films/test-movie" in result["url"]
    assert result["source"] == "Cinematheque"


@pytest.mark.asyncio
async def test_cinematheque_get_script_success(cinematheque_scraper):
    """Test successful script retrieval from Cinematheque."""
    # Setup mock response
    mock_response = (
        cinematheque_scraper._session.get.return_value.__aenter__.return_value
    )
    mock_response.status = 200
    mock_response.text.return_value = CINEMATHEQUE_SCRIPT_HTML

    script = await cinematheque_scraper.get_script(
        "https://cinematheque.fr/films/test-movie"
    )

    assert "INT. SALLE - JOUR" in script
    assert "C'est un script test." in script


@pytest.mark.asyncio
async def test_scraper_http_error():
    """Test handling of HTTP errors."""
    scraper = IMSDBScraper()

    # Create mock session that returns a 404
    mock_session = Mock(spec=aiohttp.ClientSession)
    mock_response = Mock()
    mock_response.__aenter__.return_value = mock_response
    mock_response.status = 404
    mock_response.text.return_value = "Not Found"
    mock_session.get.return_value = mock_response

    scraper._session = mock_session

    with pytest.raises(ScrapingError):
        await scraper.get_script("https://example.com/script")
