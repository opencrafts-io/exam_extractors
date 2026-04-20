from typing import Any, Dict, List

from openpyxl import load_workbook

from ...base.scraper import BaseTimetableScraper
from ...registry import ScraperRegistry
from ...schemas import CourseEntry
from ...utils.datetime_parser import compute_datetime_str


@ScraperRegistry.register("nursing_exams")
class NursingExamScraper(BaseTimetableScraper):
    """
    Scraper for Daystar University Nursing timetable Format
    """

    @property
    def institution_name(self) -> str:
        return "nursing_exams"

    def extract(self, file) -> List[CourseEntry]:
        """
        Extract timetable data from nursing excel file
        """
        column_headers = [
            "Day",
            "Campus",
            "Coordinator",
            "Courses",
            "Hours",
            "Venue",
            "Invigilators",
            "Courses_Afternoon",
            "Hours_Afternoon",
            "Venue_Afternoon",
            "Invigilators_Afternoon",
        ]

        wb_obj = load_workbook(file)
        sheet = wb_obj.active

        column_data_dict = self._read_columns(sheet, column_headers)
        morning_exams = self._extract_course_info(
            column_data_dict,
            "Courses",
            ["8.30AM-11.30AM", "8.30-11.30AM", "8.30-11.30 AM"],
        )
        afternoon_exams = self._extract_course_info(
            column_data_dict,
            "Courses_Afternoon",
            ["1.30PM-4.30PM", "1.30-4.30PM", "1.30-4.30 PM"],
        )

        courses = morning_exams + afternoon_exams
        return self.normalize_output(courses)

    def _read_columns(
        self, sheet, column_headers: List[str]
    ) -> Dict[str, List[Any]]:
        """
        Read Excel columns and store data in dictionary.
        Handles merged cells by carrying forward the last non-None value
        """
        column_data_dict = {}
        no_carry_headers = {"Courses", "Courses_Afternoon"}

        for i, column in enumerate(
            sheet.iter_cols(values_only=True) if sheet else []
        ):
            if i >= len(column_headers):
                continue

            header = column_headers[i]
            last_value = None
            column_data = []

            for cell in column:
                if cell is not None:
                    last_value = cell
                    column_data.append(cell)
                else:
                    if header in no_carry_headers:
                        column_data.append(None)
                    else:
                        column_data.append(last_value)

            column_data_dict[header] = column_data

        return column_data_dict

    def _extract_course_info(
        self,
        column_data_dict: Dict[str, List[Any]],
        time_key: str,
        time_range: List[str],
    ) -> List[CourseEntry]:
        """
        Extract course information for a specific time slot (morning or afternoon)
        Args:
            column_data_dict: Dict mapping column headers to cell values
            time_key: Keny for the course column (Courses or Courses_Afternoon)
                time_range: Time range strings to exclude
        Return:
            List of CourseEntry objects
        """
        courses = []

        if "Day" not in column_data_dict or time_key not in column_data_dict:
            return courses

        # Skip the very first row if it contains headers
        start_idx = 0
        if column_data_dict["Day"] and str(column_data_dict["Day"][0]).lower() == "day":
            start_idx = 1

        for i in range(start_idx, len(column_data_dict["Day"])):
            raw_course_code = column_data_dict[time_key][i]
            if raw_course_code is None:
                continue

            course_code = str(raw_course_code).strip()
            if not course_code or course_code.lower() == "none":
                continue
            if any(tr.lower() in course_code.lower() for tr in time_range):
                continue

            if course_code.upper() in ["COURSE", "COURSES", "DAY", "CAMPUS"]:
                continue

            day_val = column_data_dict["Day"][i]
            time_val = (
                "8:30AM-11:30AM" if "8.30" in time_range[0] else "1:30PM-4:30PM"
            )
            suffix = "_Afternoon" if "_Afternoon" in time_key else ""

            course_info = CourseEntry(
                course_code=course_code,
                coordinator=column_data_dict.get("Coordinator", [""] * (i + 1))[i]
                or "",
                time=time_val,
                day=day_val or "",
                campus=column_data_dict.get("Campus", [""] * (i + 1))[i] or "",
                hrs=column_data_dict.get(f"Hours{suffix}", [""] * (i + 1))[i]
                or "",
                venue=column_data_dict.get(f"Venue{suffix}", [""] * (i + 1))[i]
                or "",
                invigilator=column_data_dict.get(
                    f"Invigilators{suffix}", [""] * (i + 1)
                )[i]
                or "",
                datetime_str=compute_datetime_str(day_val, time_val),
            )

            courses.append(course_info)
        return courses
