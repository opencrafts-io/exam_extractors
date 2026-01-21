from __future__ import annotations

from typing import Any, Mapping

from ..schemas import CourseEntry


def course_entry_from_mapping(
    data: Mapping[str, Any],
    *,
    course_code_key: str = "course_code",
    day_key: str = "day",
    time_key: str = "time",
    venue_key: str = "venue",
    campus_key: str = "campus",
    coordinator_key: str = "coordinator",
    hrs_key: str = "hrs",
    invigilator_key: str = "invigilator",
    datetime_str_key: str = "datetime_str",
    course_name_key: str = "course_name",
    raw_data_key: str = "raw_data",
) -> CourseEntry:
    raw = data.get(raw_data_key)
    raw_dict = raw if isinstance(raw, dict) else {}

    return CourseEntry(
        course_code=str(data.get(course_code_key, "") or ""),
        day=str(data.get(day_key, "") or ""),
        time=str(data.get(time_key, "") or ""),
        venue=str(data.get(venue_key, "") or ""),
        campus=str(data.get(campus_key, "") or ""),
        coordinator=str(data.get(coordinator_key, "") or ""),
        hrs=str(data.get(hrs_key, "") or ""),
        invigilator=str(data.get(invigilator_key, "") or ""),
        datetime_str=data.get(datetime_str_key),
        course_name=str(data.get(course_name_key, "") or ""),
        raw_data=raw_dict,
    )

