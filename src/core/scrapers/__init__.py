"""Movie script scrapers package."""

from .base import BaseScraper, ScrapingError
from .imsdb import IMSDBScraper
from .cinematheque import CinemathequeScraper

__all__ = ["BaseScraper", "IMSDBScraper", "CinemathequeScraper", "ScrapingError"]
