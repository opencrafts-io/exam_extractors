from . import Scrapers
from .base.scraper import BaseTimetableScraper
from .registry import ScraperRegistry
from .schemas import CourseEntry

__all__ = [
    "ScraperRegistry",
    "CourseEntry",
    "BaseTimetableScraper",
]
