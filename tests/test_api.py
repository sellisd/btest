"""Tests for the script API endpoints."""

import pytest
from fastapi.testclient import TestClient
import json
from pathlib import Path
from unittest.mock import patch, Mock
import tempfile
import shutil

from src.api.server import app, CACHE_DIR
from src.api.models import ScriptResponse
from src.core.scrapers import ScrapingError

# Create test client
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup and teardown for each test."""
    # Create temporary cache directory
    temp_cache_dir = tempfile.mkdtemp()
    original_cache_dir = CACHE_DIR
    
    # Override cache directory
    global CACHE_DIR
    CACHE_DIR = Path(temp_cache_dir)
    
    yield
    
    # Cleanup
    shutil.rmtree(temp_cache_dir)
    CACHE_DIR = original_cache_dir

def test_search_script_success():
    """Test successful script search."""
    with patch('src.api.server.SCRAPERS') as mock_scrapers:
        # Mock first scraper to return a result
        mock_scraper = mock_scrapers[0]
        mock_scraper.search_script.return_value = {
            "title": "Test Movie",
            "url": "https://example.com/script",
            "source": "IMSDB"
        }
        
        response = client.get("/scripts/search?title=Test+Movie")
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Test Movie"
        assert data["source"] == "IMSDB"

def test_search_script_not_found():
    """Test script search with no results."""
    with patch('src.api.server.SCRAPERS') as mock_scrapers:
        # Make all scrapers return None
        for scraper in mock_scrapers:
            scraper.search_script.return_value = None
        
        response = client.get("/scripts/search?title=Nonexistent+Movie")
        assert response.status_code == 404
        
        data = response.json()
        assert "No script found" in data["detail"]

def test_get_script_success():
    """Test successful script retrieval."""
    with patch('src.api.server.SCRAPERS') as mock_scrapers:
        # Mock first scraper
        mock_scraper = mock_scrapers[0]
        mock_scraper.search_script.return_value = {
            "title": "Test Movie",
            "url": "https://example.com/script",
            "source": "IMSDB"
        }
        mock_scraper.get_script.return_value = "Test script content"
        
        response = client.get("/scripts/Test%20Movie")
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Test Movie"
        assert data["script"] == "Test script content"
        assert data["source"] == "IMSDB"

def test_get_script_from_cache():
    """Test retrieving script from cache."""
    # Create cached script
    cache_file = CACHE_DIR / "test_movie.json"
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    script_data = {
        "timestamp": 9999999999,  # Future timestamp to prevent expiration
        "script": {
            "title": "Test Movie",
            "script": "Cached script content",
            "source": "IMSDB",
            "url": "https://example.com/script"
        }
    }
    
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(script_data, f)
    
    with patch('src.api.server.SCRAPERS') as mock_scrapers:
        # Scraper should not be called
        response = client.get("/scripts/Test%20Movie")
        assert response.status_code == 200
        
        data = response.json()
        assert data["script"] == "Cached script content"
        
        # Verify scrapers were not called
        for scraper in mock_scrapers:
            scraper.search_script.assert_not_called()

def test_get_script_scraping_error():
    """Test handling of scraping errors."""
    with patch('src.api.server.SCRAPERS') as mock_scrapers:
        # Make first scraper raise error
        mock_scraper = mock_scrapers[0]
        mock_scraper.search_script.side_effect = ScrapingError("Test error")
        
        response = client.get("/scripts/Test%20Movie")
        assert response.status_code == 503
        
        data = response.json()
        assert data["error"] == "Script scraping failed"
        assert "Test error" in data["details"]

def test_fallback_between_scrapers():
    """Test fallback to second scraper when first fails."""
    with patch('src.api.server.SCRAPERS') as mock_scrapers:
        # Make first scraper return None
        mock_scrapers[0].search_script.return_value = None
        
        # Make second scraper succeed
        mock_scrapers[1].search_script.return_value = {
            "title": "Test Movie",
            "url": "https://example.com/script",
            "source": "Cinematheque"
        }
        mock_scrapers[1].get_script.return_value = "Test script content"
        
        response = client.get("/scripts/Test%20Movie")
        assert response.status_code == 200
        
        data = response.json()
        assert data["source"] == "Cinematheque"
        assert data["script"] == "Test script content"
