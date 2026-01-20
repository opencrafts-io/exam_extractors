from abc import ABC, abstractmethod
from typing import BinaryIO, List, Union

from ..schemas import CourseEntry


class BaseTimetableScraper(ABC):
    """
    Abstract base class for all timetable scrapers.
    All scrapers must inherit from this class and implement the abstract methods.
    """

    @property
    @abstractmethod
    def institution_name(self) -> str:
        """
        Unique indentifier for the scraper.
        Used for registration in a registry
        """
        pass

    @abstractmethod
    def extract(self, file: Union[BinaryIO, str]) -> List[CourseEntry]:
        """
        Extract timetable data from a file
        Args:
            file: file object or path (preferrably excel)
        Returns:
            List of CourseEntry objects in standardized format
        Raises:
            Exception if file cannot be read or parsed.
        """
        pass

    def validate_entry(self, entry: CourseEntry) -> bool:
        """
        Validate Course entry
        """
        if not entry.course_code or not entry.course_code.strip():
            return False
        return True

    def normalize_output(self, entries: List[CourseEntry]) -> List[CourseEntry]:
        """
        Applies validation and any normalization
        """
        normalized = []
        for entry in entries:
            if self.validate_entry(entry):
                normalized.append(entry)
            return normalized
