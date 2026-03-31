from typing import Any, Dict, Iterable, List, Optional, Tuple

from .schemas import CourseEntry
from .utils.structured_datetime import parse_exam_date, parse_time_range_24h


ALLOWED_ITEM_KEYS = {
    "course_code",
    "course_name",
    "exam_date",
    "start_time",
    "end_time",
    "day",
    "time",
    "venue",
    "campus",
    "coordinator",
    "hrs",
    "invigilator",
    "location",
    "room",
    "building",
    "exam_type",
    "instructions",
    "raw_data",
}

INSTITUTION_ID_MAP: Dict[str, str] = {
    "kca": "123",
    "strath": "5461",
    "nursing_exams": "5426",
    "school_exams": "5426",
}


def _clean_str(v: Any) -> Optional[str]:
    """
    Clean and normalize a string value.

    Args:
        v: Value to clean

    Returns:
        Trimmed string if non-empty, None otherwise
    """
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


def course_entry_to_professor_item(
    entry: CourseEntry,
    *,
    exam_date: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convert a CourseEntry to a contract-compliant Professor.

    This function:
    - Only includes contract-allowed keys
    - Trims strings and omits empty values

    Args:
        entry: CourseEntry object to convert
        exam_date: Optional exam date in YYYY-MM-DD format
        start_time: Optional start time in HH:MM format (24h)
        end_time: Optional end time in HH:MM format (24h)

    Returns:
        Dictionary compliant with Professor contract item schema

    Raises:
        ValueError: If course_code is missing or empty after trimming
    """
    course_code = _clean_str(entry.course_code)
    if not course_code:
        raise ValueError("course_code is required and cannot be empty")

    raw_data: Dict[str, Any] = dict(entry.raw_data or {})

    if entry.datetime_str:
        raw_data.setdefault("datetime_str", entry.datetime_str)

    item: Dict[str, Any] = {"course_code": course_code}

    for field_name in (
        "course_name",
        "day",
        "time",
        "venue",
        "campus",
        "coordinator",
        "hrs",
        "invigilator",
        "location",
        "room",
        "building",
        "exam_type",
        "instructions",
    ):
        if hasattr(entry, field_name):
            v = _clean_str(getattr(entry, field_name))
            if v is not None:
                item[field_name] = v

    if exam_date is not None:
        item["exam_date"] = exam_date

    if start_time is not None:
        item["start_time"] = start_time

    if end_time is not None:
        if start_time is not None:
            try:
                from datetime import datetime
                start_dt = datetime.strptime(start_time, "%H:%M")
                end_dt = datetime.strptime(end_time, "%H:%M")
                if end_dt > start_dt:
                    item["end_time"] = end_time
            except (ValueError, TypeError):
                item["end_time"] = end_time
        else:
            item["end_time"] = end_time

    if raw_data:
        item["raw_data"] = raw_data

    return {k: item[k] for k in item.keys() if k in ALLOWED_ITEM_KEYS}


def get_institution_id(scraper_name: str) -> str:
    """
    Map a scraper registry name to a stable institution ID.

    Args:
        scraper_name: Name from ScraperRegistry (e.g., "nursing_exams", "kca")

    Returns:
        Stable institution ID for Professor API (e.g., "nursing", "kca")

    Raises:
        ValueError: If scraper_name is not in the mapping
    """
    institution_id = INSTITUTION_ID_MAP.get(scraper_name)
    if institution_id is None:
        available = ", ".join(sorted(INSTITUTION_ID_MAP.keys()))
        raise ValueError(
            f"Unknown scraper name: '{scraper_name}'. "
            f"Available scrapers: {available}"
        )
    return institution_id


def build_ingest_payload(
    *,
    institution_id: str,
    semester_id: Optional[int],
    entries: Iterable[CourseEntry],
    chunk_size: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Build Professor API ingest payload(s) from CourseEntry objects.

    Args:
        institution_id: Stable institution identifier (use get_institution_id())
        semester_id: Optional semester ID (integer or None)
        entries: Iterable of CourseEntry objects
        chunk_size: Optional chunk size. If None, returns single payload.
                   If set, chunks items into batches of this size.

    Returns:
        List of payload dictionaries. Each payload has structure:
        {
            "institution_id": str,
            "semester_id": int | None,
            "items": [...]
        }
        Returns single-item list if chunk_size is None.

    Raises:
        ValueError: If institution_id is empty or entries contain invalid data
    """
    inst = str(institution_id).strip()
    if not inst:
        raise ValueError("institution_id is required and cannot be empty")

    items: List[Dict[str, Any]] = []
    seen: Dict[Tuple[str, Optional[int], str], int] = {}

    for entry in entries:
        if not entry.course_code or not entry.course_code.strip():
            continue

        exam_date = parse_exam_date(entry.day)
        start_time, end_time = parse_time_range_24h(entry.time)

        try:
            item = course_entry_to_professor_item(
                entry,
                exam_date=exam_date,
                start_time=start_time,
                end_time=end_time,
            )

            key = (inst, semester_id, item["course_code"])
            if key in seen:
                items[seen[key]] = item
            else:
                seen[key] = len(items)
                items.append(item)
        except ValueError:
            continue

    if not items:
        return []

    if chunk_size is None or chunk_size <= 0:
        payload = {"institution_id": inst, "items": items}
        if semester_id is not None:
            payload["semester_id"] = int(semester_id)
        return [payload]

    payloads: List[Dict[str, Any]] = []
    for i in range(0, len(items), chunk_size):
        chunk = items[i : i + chunk_size]
        payload = {"institution_id": inst, "items": chunk}
        if semester_id is not None:
            payload["semester_id"] = int(semester_id)
        payloads.append(payload)

    return payloads
