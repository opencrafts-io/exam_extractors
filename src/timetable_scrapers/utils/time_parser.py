from datetime import datetime
from dateutil import parser as date_parser
from dateutil.tz import UTC
from typing import Optional, Tuple
import logging

from ..schemas import CourseEntry

logger = logging.getLogger(__name__)


def parse_exam_datetime(
    day_str: str,
    time_str: str,
    timezone_str: str = "UTC"
) -> str:
    """
    Convert day and time strings to ISO 8601 UTC format.

    Returns:
        ISO 8601 UTC datetime string (e.g., "2026-04-28T08:00:00Z")
        Returns empty string if parsing fails.
    """
    if not day_str or not time_str:
        logger.warning(f"Missing day_str or time_str: day={day_str}, time={time_str}")
        return ""

    try:
       # "WEDN 29/4/26" -> "29/4/26")
        clean_day = str(day_str).upper().strip()
        day_prefixes = ["WEDNESDAY", "THURSDAY", "SATURDAY", "MONDAY", "TUESDAY", "FRIDAY", "SUNDAY",
                        "THURS", "WEDN", "WED", "THU", "MON", "TUE", "FRI", "SAT", "SUN"]
        for prefix in day_prefixes:
            if clean_day.startswith(prefix):
                remaining = clean_day[len(prefix):].strip()
                if not remaining or remaining[0].isdigit() or remaining[0] in " /-":
                    clean_day = remaining
                    break

        day_obj = date_parser.parse(clean_day, dayfirst=True)

        time_str = str(time_str).replace('.', ':').replace(' ', '').upper()

        try:
            time_obj = datetime.strptime(time_str, "%I:%M%p").time()
        except ValueError:
            try:
                time_obj = datetime.strptime(time_str, "%H:%M").time()
            except ValueError:
                time_obj = datetime.strptime(time_str, "%H%M").time()

        dt = datetime.combine(day_obj.date(), time_obj)

        try:
            from dateutil import tz as dateutil_tz
            tz_obj = dateutil_tz.gettz(timezone_str) or UTC
            dt = dt.replace(tzinfo=tz_obj).astimezone(UTC)
        except Exception as e:
            logger.warning(f"Timezone parsing failed for {timezone_str}: {e}")
            dt = dt.replace(tzinfo=UTC)

        # Return ISO 8601 UTC format
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    except Exception as e:
        logger.warning(f"Failed to parse datetime: day={day_str}, time={time_str}: {e}")
        return ""


def calculate_duration(start_iso: str, end_iso: str) -> str:
    """
    Calculate duration between two ISO 8601 timestamps.

    Returns:
        Duration string (e.g., "2 hours") or empty string if invalid.
    """
    try:
        start = datetime.fromisoformat(start_iso.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_iso.replace('Z', '+00:00'))

        total_seconds = (end - start).total_seconds()

        if total_seconds < 0:
            logger.warning(f"end_time before start_time: {start_iso} to {end_iso}")
            return ""

        hours = total_seconds / 3600

        if hours == int(hours):
            return f"{int(hours)} hour{'s' if hours != 1 else ''}"
        else:
            return f"{hours:.1f} hours"

    except Exception as e:
        logger.warning(f"Failed to calculate duration: {e}")
        return ""


def validate_entry(entry: CourseEntry) -> Tuple[bool, str]:
    """
    Validate CourseEntry against Professor API contract.

    Returns:
        (is_valid, error_message)
    """
    if not entry.course_code or not entry.course_code.strip():
        return False, "course_code cannot be empty"

    if not entry.venue or not entry.venue.strip():
        return False, "venue cannot be empty"

    if not entry.start_time:
        return False, "start_time is required"

    if not entry.end_time:
        return False, "end_time is required"
    try:
        start = datetime.fromisoformat(entry.start_time.replace('Z', '+00:00'))
        end = datetime.fromisoformat(entry.end_time.replace('Z', '+00:00'))

        if end <= start:
            return False, "end_time must be after start_time"
    except ValueError:
        return False, "start_time and end_time must be valid ISO 8601 format"

    return True, ""
