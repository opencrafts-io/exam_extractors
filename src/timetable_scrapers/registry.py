from typing import Dict, List, Type

from timetable_scrapers.base import scraper

from .base.scraper import BaseTimeTimetableScraper


class ScraperRegistry:
    """
    Registry for managing timetable for ScraperRegistry
    """

    _scrapers: Dict[str, Type[BaseTimeTimetableScraper]] = {}

    @classmethod
    def register(cls, name: str):
        """
        Decorator to register a scraper class.

        Usage:
            @ScraperRegistry.register("nursing_exams")
            class NursingExamScraper(BaseTimeTimetableScraper)
        Args:
            name: identifier for the scraper
        Returns:
            Decorator function that registers the class
        """

        def decorator(
            scraper_class: Type[BaseTimeTimetableScraper],
        ) -> Type[BaseTimeTimetableScraper]:
            """
            Runs at import
            """
            if not issubclass(scraper_class, BaseTimeTimetableScraper):
                raise TypeError(
                    f"Scraper{scraper_class.__name__} must inherit from BaseTimeTimetableScraper"
                )
            if name in cls._scrapers:
                raise ValueError(
                    f"Scraper name '{name} is already registered"
                    f"Existing: {cls._scrapers[name].__name__}, "
                    f"New: {scraper_class.__name__}"
                )
            cls._scrapers[name] = scraper_class
            return scraper_class

        return decorator

    @classmethod
    def list_scrapers(cls) -> List[str]:
        """
        List all registered scraper names.
        """
        return list(cls._scrapers.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """
            Check if a scraper is registered
        Args:
            name: scraper to Check
        Returns:
            True if registered, False if otherwise
        """
        return name in cls._scrapers
