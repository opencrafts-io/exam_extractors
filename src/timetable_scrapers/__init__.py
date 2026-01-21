from .base.scraper import BaseTimetableScraper
from .registry import ScraperRegistry
from .schemas import CourseEntry

from . import scrapers as _scrapers

__all__ = [
    "ScraperRegistry",
    "CourseEntry",
    "BaseTimetableScraper",
]
