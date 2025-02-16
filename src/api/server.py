"""FastAPI server for movie script scraping API."""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from pathlib import Path
import json
import time

from .models import ScriptSearchResult, ScriptResponse, ErrorResponse
from typing import List, Optional
from ..core.scrapers import (
    BaseScraper,
    IMSDBScraper,
    CinemathequeScraper,
    ScrapingError,
)
from ..core.config import cors_config, cache_config

# Setup logging
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Movie Script API",
    description="API for searching and retrieving movie scripts from various sources",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.allow_origins,
    allow_credentials=cors_config.allow_credentials,
    allow_methods=cors_config.allow_methods,
    allow_headers=cors_config.allow_headers,
)

# Initialize scrapers in priority order
SCRAPERS: List[BaseScraper] = [
    IMSDBScraper(),      # Try IMSDB first
    CinemathequeScraper(), # Fall back to Cinematheque
]

def get_cached_script(title: str) -> Optional[ScriptResponse]:
    """Get script from cache if available and not expired."""
    try:
        cache_file = cache_config.directory / f"{title.lower().replace(' ', '_')}.json"
        if not cache_file.exists():
            return None

        with open(cache_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Check if cache is expired
        if time.time() - data["timestamp"] > cache_config.duration:
            return None

        return ScriptResponse(**data["script"])
    except Exception as e:
        logger.warning(f"Cache read error for {title}: {e}")
        return None

def cache_script(title: str, response: ScriptResponse) -> None:
    """Cache script response."""
    try:
        cache_config.directory.mkdir(parents=True, exist_ok=True)
        cache_file = cache_config.directory / f"{title.lower().replace(' ', '_')}.json"

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": time.time(),
                    "script": response.model_dump()
                },
                f,
                ensure_ascii=False,
                indent=2
            )
    except Exception as e:
        logger.warning(f"Cache write error for {title}: {e}")

@app.exception_handler(ScrapingError)
async def scraping_exception_handler(request, exc: ScrapingError):
    """Handle scraping errors."""
    return JSONResponse(
        status_code=503,  # Service Unavailable
        content=ErrorResponse(
            error="Script scraping failed",
            details=str(exc)
        ).model_dump(),
    )

@app.get(
    "/scripts/search",
    response_model=ScriptSearchResult,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def search_script(
    title: str = Query(..., description="Movie title to search for"),
) -> ScriptSearchResult:
    """Search for a movie script."""
    # Try each scraper in order until we find a script
    for scraper in SCRAPERS:
        async with scraper:
            result = await scraper.search_script(title)
            if result:
                return ScriptSearchResult(**result)

    # If no script found in any source
    raise HTTPException(status_code=404, detail=f"No script found for movie: {title}")

@app.get(
    "/scripts/{title}",
    response_model=ScriptResponse,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def get_script(title: str) -> ScriptResponse:
    """Get a movie script by title."""
    # Check cache first
    if cached := get_cached_script(title):
        return cached

    # Try each scraper in order until we find a script
    for scraper in SCRAPERS:
        async with scraper:
            # Search for script
            result = await scraper.search_script(title)
            if not result:
                continue

            try:
                # Fetch full script
                script_text = await scraper.get_script(result["url"])

                response = ScriptResponse(
                    title=result["title"],
                    script=script_text,
                    source=result["source"],
                    url=result["url"],
                )

                # Cache the result
                cache_script(title, response)

                return response
            except ScrapingError:
                # If script fetch fails, try next scraper
                continue

    # If no script found in any source
    raise HTTPException(status_code=404, detail=f"No script found for movie: {title}")

def start_server():
    """Start the FastAPI server using uvicorn."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
