import re
from datetime import datetime
from typing import Optional


def compute_datetime_str(day_str: str, time_str: str) -> Optional[str]:
    """
    Compute datetime_str in ISO format UTC from day and time strings
    Args:
        day_str, time_str
    Returns:
        ISO format datetime string or None if parsing fails
    """
    if not day_str or not time_str:
        return None
    try:
        date_obj = None
        time_obj = None

        day_str = str(day_str).strip()
        time_str = str(time_str).strip()

        clean_time = re.sub(r"\bHRS?\b", "", time_str, flags=re.IGNORECASE).strip()
        start_time_str = clean_time.split("-", 1)[0].strip()

        if re.fullmatch(r"\d{4}", start_time_str):
            time_obj = datetime.strptime(start_time_str, "%H%M").time()
        else:
            start_time_str = start_time_str.replace(".", ":")
            for fmt in [
                "%I:%M%p",
                "%I:%M %p",
                "%I%p",
                "%H:%M",
                "%H.%M",
                "%H%M",
            ]:
                try:
                    time_obj = datetime.strptime(start_time_str, fmt).time()
                    break
                except ValueError:
                    continue

        if not time_obj:
            return None

        date_match = re.search(
            r"(\d{1,2})(?:st|nd|rd|th)?\s+([a-zA-Z]+)\s+(\d{4})",
            day_str,
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
        elif re.match(r"\d{4}-\d{2}-\d{2}", day_str):
            date_obj = datetime.strptime(day_str.split()[0], "%Y-%m-%d").date()
        elif "/" in day_str:
            parts = day_str.split()
            date_part = parts[-1] if parts else day_str
            day_prefix_match = re.match(
                r"^[A-Z]{3}\s*(\d{1,2}/\d{1,2}/\d{2,4})",
                day_str,
                re.IGNORECASE,
            )
            if day_prefix_match:
                date_part = day_prefix_match.group(1)

            for fmt in ("%d/%m/%y", "%d/%m/%Y"):
                try:
                    date_obj = datetime.strptime(date_part, fmt).date()
                    break
                except ValueError:
                    continue

        if not date_obj:
            return None

        dt = datetime.combine(date_obj, time_obj)
        return dt.isoformat() + "Z"
    except Exception:
        pass

    return None
