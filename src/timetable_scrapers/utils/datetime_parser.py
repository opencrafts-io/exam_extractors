from typing import Optional
from .structured_datetime import compute_datetime_str as _compute_datetime_str


def compute_datetime_str(day_str: str, time_str: str) -> Optional[str]:
    """
    Compute datetime_str in ISO format UTC from day and time strings
    Args:
        day_str, time_str
    Returns:
        ISO format datetime string or None if parsing fails
    """
    return _compute_datetime_str(day_str, time_str)
