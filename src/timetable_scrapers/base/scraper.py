from abc import ABC, abstractmethod
from typing import BinaryIO, List, Union

from ..schemas import CourseEntry
from ..utils.structured_datetime import compute_datetime_str, split_time_range


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
                if not entry.datetime_str and entry.day and entry.time:
                    entry.datetime_str = compute_datetime_str(entry.day, entry.time)

                if entry.time and (not entry.start_time or not entry.end_time):
                    start, end = split_time_range(entry.time)
                    if not entry.start_time:
                        entry.start_time = start
                    if not entry.end_time:
                        entry.end_time = end

                normalized.append(entry)
        return normalized
