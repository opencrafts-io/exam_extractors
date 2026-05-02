import pytest
from timetable_scrapers.utils.time_parser import parse_exam_datetime, calculate_duration, validate_entry
from timetable_scrapers.schemas import CourseEntry

def test_parse_exam_datetime():
    # Test EAT to UTC (EAT is UTC+3)
    result = parse_exam_datetime("28/04/2026", "8:30AM", "EAT")
    assert result == "2026-04-28T05:30:00Z"
    
    # Test afternoon
    result = parse_exam_datetime("28/04/2026", "1:30PM", "EAT")
    assert result == "2026-04-28T10:30:00Z"
    
    # Test different format
    result = parse_exam_datetime("2026-05-15", "14:30", "UTC")
    assert result == "2026-05-15T14:30:00Z"

def test_calculate_duration():
    duration = calculate_duration("2026-04-28T08:00:00Z", "2026-04-28T10:00:00Z")
    assert duration == "2 hours"
    
    duration = calculate_duration("2026-04-28T08:00:00Z", "2026-04-28T10:30:00Z")
    assert duration == "2.5 hours"

def test_validate_entry():
    # Valid entry
    entry = CourseEntry(
        course_code="CS101",
        start_time="2026-04-28T08:00:00Z",
        end_time="2026-04-28T10:00:00Z",
        venue="Main Hall"
    )
    is_valid, error = validate_entry(entry)
    assert is_valid
    
    # Missing course_code
    entry.course_code = ""
    is_valid, error = validate_entry(entry)
    assert not is_valid
    assert "course_code" in error
    
    # Invalid time order
    entry.course_code = "CS101"
    entry.start_time = "2026-04-28T10:00:00Z"
    entry.end_time = "2026-04-28T08:00:00Z"
    is_valid, error = validate_entry(entry)
    assert not is_valid
    assert "after" in error
