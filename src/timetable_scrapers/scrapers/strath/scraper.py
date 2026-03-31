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
        wb_obj = load_workbook(file, data_only=True, read_only=True)
        all_courses = []

        for sheet in wb_obj.worksheets:
            col_map = {
                "date": 0,
                "time": 2,
                "course": 5,
                "group": 6,
                "number": 7,
                "venue": 8,
                "lecturer": 9,
            }

            header_row_idx = -1

            # Try to find header row and detect columns
            for row_idx, row in enumerate(sheet.iter_rows(values_only=True, max_row=10)):
                row_vals = [str(cell).strip().lower() if cell else "" for cell in row]
                if "time" in row_vals and any(word in "".join(row_vals) for word in ["course", "unit", "examination", "subject"]):
                    header_row_idx = row_idx
                    for i, val in enumerate(row_vals):
                        val_str = str(val).lower()
                        if "date" in val_str: col_map["date"] = i
                        elif "time" in val_str: col_map["time"] = i
                        elif any(kw in val_str for kw in ["unit", "course", "examination"]): col_map["course"] = i
                        elif "group" in val_str: col_map["group"] = i
                        elif "no" in val_str or "number" in val_str: col_map["number"] = i
                        elif "venue" in val_str: col_map["venue"] = i
                        elif any(kw in val_str for kw in ["invigilator", "lecturer"]): col_map["lecturer"] = i
                    break

            if header_row_idx == -1:
                # If no header found, skip this sheet (might be instructions or empty)
                continue

            current_date = ""
            current_time = ""
            current_course = ""
            current_group = ""
            current_number = ""
            current_venue = ""
            current_lecturer = ""

            start_row = header_row_idx + 1

            for row_idx, row in enumerate(sheet.iter_rows(values_only=True)):
                if row_idx < start_row:
                    continue

                if not any(row):
                    continue

                def get_val(idx):
                    return str(row[idx]).strip() if idx < len(row) and row[idx] is not None else ""

                date_val = get_val(col_map["date"])
                time_val = get_val(col_map["time"])
                course_val = get_val(col_map["course"])
                group_val = get_val(col_map["group"])
                number_val = get_val(col_map["number"])
                venue_val = get_val(col_map["venue"])
                lecturer_val = get_val(col_map["lecturer"])

                if date_val: current_date = date_val.rstrip(".")
                if time_val: current_time = time_val
                if course_val: current_course = course_val
                if group_val: current_group = group_val
                if number_val: current_number = number_val
                if venue_val: current_venue = venue_val
                if lecturer_val: current_lecturer = lecturer_val

                if current_course and current_group:
                    if course_val or group_val or venue_val or lecturer_val:
                        course_parts = current_course.split(":", 1)
                        course_code = course_parts[0].strip() if course_parts else current_course
                        course_name = course_parts[1].strip() if len(course_parts) > 1 else ""

                        formatted_time = self._format_strath_time(current_time)

                        all_courses.append(CourseEntry(
                            course_code=course_code,
                            course_name=course_name,
                            day=current_date or "Unknown Date",
                            time=formatted_time,
                            venue=current_venue or "TBA",
                            invigilator=current_lecturer,
                            raw_data={
                                "group": current_group,
                                "student_count": current_number,
                                "program": current_group.split()[0] if current_group else "",
                            },
                        ))

        return self.normalize_output(all_courses)

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
