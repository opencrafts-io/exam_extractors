from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class CourseEntry:
    """
    Standardized course Entry structure returned by all scrapers
    All scrapers should return a list or CourseEntry objects
    """

    course_code: str
    day: str = ""
    time: str = ""
    start_time: str = ""
    end_time: str = ""
    venue: str = ""
    campus: str = ""
    coordinator: str = ""
    hrs: str = ""
    invigilator: str = ""
    datetime_str: Optional[str] = None
    course_name: str = ""
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert CourseEntry to a dictionary
        """
        return {
            "course_code": self.course_code,
            "day": self.day,
            "time": self.time,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "venue": self.venue,
            "campus": self.campus,
            "coordinator": self.coordinator,
            "hrs": self.hrs,
            "invigilator": self.invigilator,
            "datetime_str": self.datetime_str,
            "course_name": self.course_name,
            "raw_data": self.raw_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CourseEntry":
        """
        Create CourseEntry from dictionary.
        Useful for deserialization or testing
        """
        return cls(
            course_code=data.get("course_code", ""),
            day=data.get("day", ""),
            time=data.get("time", ""),
            start_time=data.get("start_time", ""),
            end_time=data.get("end_time", ""),
            venue=data.get("venue", ""),
            campus=data.get("campus", ""),
            coordinator=data.get("coordinator", ""),
            hrs=data.get("hrs", ""),
            invigilator=data.get("invigilator", ""),
            datetime_str=data.get("datetime_str"),
            course_name=data.get("course_name", ""),
            raw_data=data.get("raw_data", {}),
        )
