import re
from datetime import datetime
from typing import Optional, Tuple


def parse_exam_date(day_str: str) -> Optional[str]:
    """
    Parse a structured date string into YYYY-MM-DD format.

    - "Saturday 6th December 2025" -> "2025-12-06"
    - "2025-12-01" -> "2025-12-01"
    - "Mon 12/02/26" -> "2026-02-12"
    - "12/02/2026" -> "2026-02-12"

    Args:
        day_str: Structured date string
    Returns:
        Date string in YYYY-MM-DD format, or None if parsing fails
    """
    if not day_str:
        return None

    try:
        s = str(day_str).strip()
        if not s:
            return None

        date_match = re.search(
            r"(\d{1,2})(?:st|nd|rd|th)?\s+([a-zA-Z]+)\s+(\d{4})",
            s,
        )
        if date_match:
            day_num, month_name, year = date_match.groups()
            month_map = {
                "january": 1,
                "february": 2,
                "march": 3,
                "april": 4,
                "may": 5,
                "june": 6,
                "july": 7,
                "august": 8,
                "september": 9,
                "october": 10,
                "november": 11,
                "december": 12,
            }
            month = month_map.get(month_name.lower())
            if not month:
                return None
            date_obj = datetime(int(year), month, int(day_num)).date()
            return date_obj.strftime("%Y-%m-%d")

        if re.match(r"^\d{4}-\d{2}-\d{2}", s):
            try:
                date_obj = datetime.strptime(s.split()[0], "%Y-%m-%d").date()
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                return None

        if "/" in s:
            parts = s.split()
            date_part = parts[-1] if parts else s
            day_prefix_match = re.match(
                r"^[A-Z]{3}\s*(\d{1,2}/\d{1,2}/\d{2,4})",
                s,
                re.IGNORECASE,
            )
            if day_prefix_match:
                date_part = day_prefix_match.group(1)

            for fmt in ("%d/%m/%y", "%d/%m/%Y"):
                try:
                    date_obj = datetime.strptime(date_part, fmt).date()
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue

    except Exception:
        pass

    return None


def _parse_one_time(s: str) -> Optional[datetime]:
    """
    Parse a single time string into a datetime object.

    Handles formats like:
    - "8:30AM" -> datetime with time 08:30
    - "14:30" -> datetime with time 14:30
    - "0800" -> datetime with time 08:00
    - "2.30 pm" -> datetime with time 14:30

    Args:
        s: Time string to parse

    Returns:
        datetime object with parsed time, or None if parsing fails
    """
    if not s:
        return None

    try:
        t = re.sub(r"\bHRS?\b", "", str(s), flags=re.IGNORECASE).strip()
        t = t.replace(".", ":")

        if re.fullmatch(r"\d{4}", t):
            try:
                return datetime.strptime(t, "%H%M")
            except ValueError:
                return None

        for fmt in [
            "%I:%M%p",
            "%I:%M %p",
            "%I%p",
            "%H:%M",
            "%H.%M",
            "%H%M",
        ]:
            try:
                return datetime.strptime(t, fmt)
            except ValueError:
                continue
    except Exception:
        pass

    return None


def parse_time_range_24h(time_str: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse a time range string into separate start and end times in 24-hour format.

    Handles formats like:
    - "8:30AM-11:30AM" -> ("08:30", "11:30")
    - "14:00-16:00" -> ("14:00", "16:00")
    - "0800-1000 HRS" -> ("08:00", "10:00")
    - "2.30 pm - 4.30pm" -> ("14:30", "16:30")
    - "8:00AM" -> ("08:00", None) (no end time)

    Args:
        time_str: Free-form time range string from scrapers

    Returns:
        Tuple of (start_time, end_time) as "HH:MM" strings in 24-hour format.
        Returns (None, None) if parsing fails completely.
        Returns (start, None) if only start time can be parsed.
    """
    if not time_str:
        return (None, None)

    try:
        s = str(time_str).strip()
        if not s:
            return (None, None)

        clean_time = re.sub(r"\bHRS?\b", "", s, flags=re.IGNORECASE).strip()
        clean_time = re.sub(r"\s*-\s*", "-", clean_time)

        if "-" not in clean_time:
            dt = _parse_one_time(clean_time)
            if dt:
                return (dt.strftime("%H:%M"), None)
            return (None, None)

        parts = clean_time.split("-", 1)
        start_part = parts[0].strip()
        end_part = parts[1].strip() if len(parts) > 1 else ""

        start_dt = _parse_one_time(start_part)
        end_dt = _parse_one_time(end_part) if end_part else None

        if not end_dt and end_part:
            ampm_match = re.search(r"([AP]M)\b", start_part.upper())
            if ampm_match:
                end_dt = _parse_one_time(end_part + " " + ampm_match.group(1))

        if not start_dt:
            return (None, None)

        start_time = start_dt.strftime("%H:%M")
        end_time = end_dt.strftime("%H:%M") if end_dt else None

        if end_dt is not None and start_dt is not None and end_dt < start_dt:
            return (start_time, None)

        return (start_time, end_time)
    except Exception:
        pass

    return (None, None)
