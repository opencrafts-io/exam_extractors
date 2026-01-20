import re
from typing import List

from openpyxl import load_workbook

from ...base.scraper import BaseTimetableScraper
from ...registry import ScraperRegistry
from ...schemas import CourseEntry


@ScraperRegistry.register("strath")
class StrathScraper(BaseTimetableScraper):
    """
    Scraper for strathmore university Exams
    Handles merged cells by tracking current values across rows.
    """

    @property
    def institution_name(self) -> str:
        return "Strathmore Exam Scrapers"

    def extract(self, file) -> List[CourseEntry]:
        """
        Extract timetable data from Strathmore Excel file.
        """
        wb_obj = load_workbook(file)
        sheet = wb_obj.active

        current_date = ""
        current_time = ""
        current_course = ""
        current_group = ""
        current_number = ""
        current_venue = ""
        current_lecturer = ""

        courses = []

        for row_idx, row in enumerate(
            sheet.iter_rows(values_only=True) if sheet else []
        ):
            if row_idx < 3:
                continue

            date_val = row[0] if len(row) > 0 else None
            time_val = row[2] if len(row) > 2 else None
            course_val = row[4] if len(row) > 4 else None
            group_val = row[6] if len(row) > 6 else None
            number_val = row[7] if len(row) > 7 else None
            venue_val = row[8] if len(row) > 8 else None
            lecturer_val = row[10] if len(row) > 10 else None

            if date_val and str(date_val).strip():
                current_date = str(date_val).strip().rstrip(".")
            if time_val and str(time_val).strip():
                current_time = str(time_val).strip()
            if course_val and str(course_val).strip():
                current_course = str(course_val).strip()
            if group_val and str(group_val).strip():
                current_group = str(group_val).strip()
            if number_val is not None:
                current_number = str(number_val).strip()
            if venue_val and str(venue_val).strip():
                current_venue = str(venue_val).strip()
            if lecturer_val and str(lecturer_val).strip():
                current_lecturer = str(lecturer_val).strip()

            if current_course and current_group and current_venue:
                if (group_val and str(group_val).strip()) or (
                    venue_val and str(venue_val).strip()
                ):
                    course_parts = current_course.split(":", 1)
                    course_code = (
                        course_parts[0].strip()
                        if course_parts
                        else current_course
                    )
                    course_name = (
                        course_parts[1].strip() if len(course_parts) > 1 else ""
                    )

                    formatted_time = self._format_strath_time(current_time)

                    course_info = CourseEntry(
                        course_code=course_code,
                        course_name=course_name,
                        day=current_date,
                        time=formatted_time,
                        venue=current_venue,
                        invigilator=current_lecturer,
                        raw_data={
                            "group": current_group,
                            "student_count": current_number,
                            "program": (
                                current_group.split()[0]
                                if current_group
                                else ""
                            ),
                        },
                    )
                    courses.append(course_info)

        return self.normalize_output(courses)

    def _format_strath_time(self, time: str) -> str:
        """
        Convert time format (8:00-10:00) to (8:00AM-10:00AM).

        Handles edge cases like "11:00AM-14.00"
        """
        if not time or "-" not in time:
            return time

        original_time = str(time).strip()
        clean_time = original_time.upper()
        clean_time = re.sub(r"\s*-\s*", "-", clean_time)

        start_time, end_time = clean_time.split("-", 1)
        start_time = start_time.strip()
        end_time = end_time.strip()

        def convert_to_12hour(time_24, ampm_hint=None):
            """Convert 24-hour time to 12-hour format"""
            if not time_24:
                return time_24

            ampm = ampm_hint
            time_str = time_24

            ampm_match = re.search(r"([AP]M)", time_str)
            if ampm_match:
                ampm = ampm_match.group(1)
                time_str = re.sub(r"[AP]M", "", time_str).strip()

            if ":" in time_str:
                hour, minute = time_str.split(":")
                hour = int(hour)
                minute = int(minute)
            elif "." in time_str:
                hour, minute = time_str.split(".")
                hour = int(hour)
                minute = int(minute)
            elif len(time_str) == 4 and time_str.isdigit():
                hour = int(time_str[:2])
                minute = int(time_str[2:])
            else:
                try:
                    hour = int(time_str)
                    minute = 0
                except ValueError:
                    return time_24

            if not ampm:
                if hour >= 12:
                    ampm = "PM"
                    if hour > 12:
                        hour = hour - 12
                else:
                    ampm = "AM"
                    if hour == 0:
                        hour = 12

            return f"{hour}:{minute:02d}{ampm}"

        start_ampm = None
        end_ampm = None

        start_ampm_match = re.search(r"([AP]M)", start_time)
        if start_ampm_match:
            start_ampm = start_ampm_match.group(1)

        end_ampm_match = re.search(r"([AP]M)", end_time)
        if end_ampm_match:
            end_ampm = end_ampm_match.group(1)

        formatted_start_time = convert_to_12hour(start_time, start_ampm)
        formatted_end_time = convert_to_12hour(end_time, end_ampm or start_ampm)

        return f"{formatted_start_time}-{formatted_end_time}"
