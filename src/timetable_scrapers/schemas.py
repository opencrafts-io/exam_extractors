from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class CourseEntry:
    """
    Standardized course Entry structure returned by all scrapers
    All scrapers should return a list or CourseEntry objects
    """

    course_code: str
    start_time: str  # ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ
    end_time: str  # ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ
    venue: str
    coordinator: str = ""
    hrs: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "course_code": self.course_code,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "venue": self.venue,
            "coordinator": self.coordinator,
            "hrs": self.hrs,
            "raw_data": self.raw_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CourseEntry":
        """Create from dictionary."""
        return cls(
            course_code=data.get("course_code", ""),
            start_time=data.get("start_time", ""),
            end_time=data.get("end_time", ""),
            venue=data.get("venue", ""),
            coordinator=data.get("coordinator", ""),
            hrs=data.get("hrs", ""),
            raw_data=data.get("raw_data", {}),
        )
