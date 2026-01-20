import re
from datetime import datetime
from typing import Any, List, Optional

from openpyxl import load_workbook

from ...base.scraper import BaseTimetableScraper
from ...registry import ScraperRegistry
from ...schemas import CourseEntry
from ...utils.datetime_parser import compute_datetime_str
from ...utils.time_formatter import compute_hours


@ScraperRegistry.register("kca")
class KCAScraper(BaseTimetableScraper):
    """
    Scraper for KCA University exam timetable format.

    This scraper uses header detection to find columns dynamically,
    making it more flexible than fixed-column scrapers.
    """

    @property
    def institution_name(self) -> str:
        return "kca"

    def extract(self, file) -> List[CourseEntry]:
        """Extract exam timetable data from KCA Excel file."""
        wb_obj = load_workbook(file, data_only=True)

        key_map = {
            "DATE": "DATE",
            "TIME": "TIME",
            "VENUE": "ROOM|VENUE",
            "UNIT_CODE": "UNIT_CODE|UNIT CODE",
            "CAMPUS": "CAMPUS",
            "COORDINATOR": "INVIGILATOR OF THE DAY",
            "INVIGILATOR": "INVIGILATORS|PRINCIPAL INVIGILATORS|INVIGILATOR",
        }
        unit_code_pattern = re.compile(r"^[A-Z]{2,4}\s*\d{3,4}")

        all_courses: List[CourseEntry] = []

        for sheet_name in wb_obj.sheetnames:
            sheet = wb_obj[sheet_name]

            header_row: Optional[List[str]] = None
            header_idx = 0

            for row_idx, row in enumerate(
                sheet.iter_rows(values_only=True) if sheet else [], start=1
            ):
                if any(
                    "UNIT CODE" in str(cell).upper() for cell in row if cell
                ):
                    header_row = [
                        str(cell) if cell is not None else "" for cell in row
                    ]
                    header_idx = row_idx
                    break

            if not header_row:
                continue

            norm_headers = {
                self._normalize_header(h): idx
                for idx, h in enumerate(header_row)
                if h
            }

            courses: List[CourseEntry] = []
            current_entry: Optional[CourseEntry] = None

            for row_idx, row in enumerate(
                (
                    sheet.iter_rows(min_row=header_idx + 1, values_only=True)
                    if sheet
                    else []
                ),
                start=header_idx + 1,
            ):
                row = [cell if cell is not None else "" for cell in row]

                unit_code = ""
                for pattern in key_map["UNIT_CODE"].split("|"):
                    norm_pattern = self._normalize_header(pattern)
                    if norm_pattern in norm_headers:
                        unit_code = str(row[norm_headers[norm_pattern]]).strip()
                        break

                norm_uc = unit_code.upper().replace(" ", "").replace("_", "")
                if (
                    not unit_code
                    or norm_uc
                    in {
                        "UNITCODE",
                        "UNIT",
                        "TIME",
                        "DATE",
                        "DAY",
                        "VENUE",
                        "ROOM",
                        "EXAMINATION",
                    }
                    or not unit_code_pattern.search(unit_code.upper())
                ):
                    continue

                if current_entry:
                    courses.append(current_entry)

                current_entry = CourseEntry(
                    course_code=unit_code,
                    day="",
                    time="",
                    venue="",
                    campus="",
                    coordinator="",
                    hrs="",
                    invigilator="",
                    datetime_str=None,
                )

                for out_key, patterns in key_map.items():
                    for pattern in patterns.split("|"):
                        norm_pattern = self._normalize_header(pattern)
                        if norm_pattern in norm_headers:
                            val = row[norm_headers[norm_pattern]]
                            if out_key == "DATE":
                                val = self._convert_date(val)
                                current_entry.day = str(val).strip()
                            elif out_key == "TIME":
                                raw_time = str(val)
                                formatted = self._format_time(raw_time)
                                current_entry.time = formatted
                                current_entry.hrs = compute_hours(formatted)
                            elif out_key == "VENUE":
                                current_entry.venue = str(val).strip()
                            elif out_key == "CAMPUS":
                                current_entry.campus = str(val).strip()
                            elif out_key == "COORDINATOR":
                                current_entry.coordinator = str(val).strip()
                            elif out_key == "INVIGILATOR":
                                current_entry.invigilator = str(val).strip()
                            break

                current_entry.datetime_str = compute_datetime_str(
                    current_entry.day, current_entry.time
                )

            if current_entry:
                courses.append(current_entry)

            all_courses.extend(courses)

        return self.normalize_output(all_courses)

    def _format_time(self, time_str: str) -> str:
        """
        Standardizes various time formats to (8:00AM-10:00AM).

        Handles: "8:00AM-10:00AM", "0800-1000 HRS", "2.30 pm - 4.30pm", "11:00AM-14.00"
        """
        if not time_str:
            return ""

        original_time = str(time_str).strip()
        clean_time = original_time.upper()

        clean_time = re.sub(r"(HR|HRS)", "", clean_time).strip()
        clean_time = re.sub(r"\s*-\s*", "-", clean_time)
        clean_time = re.sub(r"\s+", " ", clean_time)

        def to_12hour(hour_min, ampm=None):
            """Convert hour:minute to 12-hour format"""
            try:
                if ":" in hour_min:
                    hour, minute = map(int, hour_min.split(":"))
                else:
                    hour = int(hour_min)
                    minute = 0

                if ampm is None:
                    if hour >= 12:
                        ampm = "PM"
                        if hour > 12:
                            hour = hour - 12
                        elif hour == 12:
                            pass
                    else:
                        ampm = "AM"
                        if hour == 0:
                            hour = 12

                return f"{hour}:{minute:02d}{ampm}"
            except (ValueError, AttributeError):
                return hour_min

        start_time_str = None
        end_time_str = None
        start_ampm = None
        end_ampm = None

        if "-" in clean_time:
            parts = clean_time.split("-", 1)
            start_part = parts[0].strip()
            end_part = parts[1].strip()

            start_ampm_match = re.search(r"([AP]M)", start_part)
            if start_ampm_match:
                start_ampm = start_ampm_match.group(1)
                start_part = re.sub(r"[AP]M", "", start_part).strip()

            end_ampm_match = re.search(r"([AP]M)", end_part)
            if end_ampm_match:
                end_ampm = end_ampm_match.group(1)
                end_part = re.sub(r"[AP]M", "", end_part).strip()

            start_time_str = start_part
            end_time_str = end_part

            if not start_time_str or not end_time_str:
                return original_time

            start_time_str = start_time_str.replace(".", ":")
            end_time_str = end_time_str.replace(".", ":")

            if (
                ":" not in start_time_str
                and len(start_time_str) == 4
                and start_time_str.isdigit()
            ):
                start_time_str = f"{start_time_str[:2]}:{start_time_str[2:]}"
            elif ":" not in start_time_str:
                start_time_str = f"{start_time_str}:00"

            if ":" not in end_time_str:
                if len(end_time_str) == 4 and end_time_str.isdigit():
                    end_time_str = f"{end_time_str[:2]}:{end_time_str[2:]}"
                elif (
                    "." in end_time_str
                    or end_time_str.replace(".", "").isdigit()
                ):
                    end_time_str = end_time_str.replace(".", ":")
                    if ":" not in end_time_str:
                        end_time_str = f"{end_time_str}:00"
                else:
                    end_time_str = f"{end_time_str}:00"

            formatted_start = to_12hour(start_time_str, start_ampm)
            formatted_end = to_12hour(end_time_str, end_ampm or start_ampm)

            return f"{formatted_start}-{formatted_end}"

        return original_time

    def _convert_date(self, date_val: Any) -> str:
        """
        Convert Excel serial or string to readable date.
        From (Monday, 1st January 2025) to (2025-01-01)
        """
        if isinstance(date_val, (int, float)):
            try:
                return datetime.fromordinal(
                    datetime(1900, 1, 1).toordinal() + int(date_val) - 2
                ).strftime("%Y-%m-%d")
            except ValueError:
                return str(date_val)
        return str(date_val).strip()

    def _normalize_header(self, header_str: str) -> str:
        """Normalize header string for matching (uppercase, remove special chars)"""
        if not header_str:
            return ""
        normalized = str(header_str).upper().strip()
        normalized = re.sub(r"[^\w\s]", "", normalized)
        normalized = re.sub(r"\s+", "_", normalized)
        return normalized
