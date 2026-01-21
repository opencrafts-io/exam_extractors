from timetable_scrapers.utils.datetime_parser import compute_datetime_str


def test_compute_datetime_str_parses_text_date_and_ampm_time():
    assert (
        compute_datetime_str("Saturday 6th December 2025", "2:00PM-4:00PM")
        == "2025-12-06T14:00:00Z"
    )


def test_compute_datetime_str_parses_ymd_and_24h_time():
    assert (
        compute_datetime_str("2025-12-01 00:00:00", "08:00-10:00")
        == "2025-12-01T08:00:00Z"
    )


def test_compute_datetime_str_parses_hrs_format():
    assert compute_datetime_str("Mon 12/02/26", "0800-1000 HRS") == "2026-02-12T08:00:00Z"

