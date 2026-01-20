from datetime import datetime
from typing import Optional


def compute_hours(formatted_time: str) -> str:
    """
    Compute duration of exams in hours from a range string.
    Args:
        formatted_time Time range string (8:00AM-10:00AM)
    Returns:
        Duration in hours (2) "2" if parsing fails.
    """

    if not formatted_time or "-" not in str(formatted_time):
        return "2"

    try:
        start_str, end_str = str(formatted_time).split("-", 1)
        start_str = start_str.strip()
        end_str = end_str.strip()

        def parse_time(s: str) -> Optional[datetime]:
            """Parse time using multiple formats."""
            for fmt in ["%I:%M%p", "%I:%M %p", "%H:%M", "%H.%M"]:
                try:
                    return datetime.strptime(s, fmt)
                except ValueError:
                    continue
            return None

        start_dt = parse_time(start_str)
        end_dt = parse_time(end_str)
        if not start_dt or not end_dt:
            return "2"
        hrs = (end_dt - start_dt).total_seconds() / 3600
        return str(int(hrs)) if hrs.is_integer() else str(hrs)
    except Exception:
        return "2"
