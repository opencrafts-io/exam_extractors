from __future__ import annotations

from typing import Iterable

from ..schemas import CourseEntry


def is_nonempty_str(value: object) -> bool:
    return isinstance(value, str) and value.strip() != ""


def validate_course_entry(entry: CourseEntry) -> bool:
    return is_nonempty_str(entry.course_code)


def filter_valid_entries(entries: Iterable[CourseEntry]) -> list[CourseEntry]:
    return [e for e in entries if validate_course_entry(e)]

