from datetime import datetime
from typing import List

from openpyxl import load_workbook

from ...base.scraper import BaseTimetableScraper
from ...registry import ScraperRegistry
from ...schemas import CourseEntry


@ScraperRegistry.register("Daystar")
class SchoolExamScraper(BaseTimetableScraper):
    """
    Scraper for Daystar Univesity Exams

    Handles multiple worksheets, each with room information in the first column.
    """

    @property
    def institution_name(self) -> str:
        return "Daystar University"

    def extract(self, file) -> List[CourseEntry]:
        """Extract exam timetable data from school Excel file."""
        wb_obj = load_workbook(filename=file)
        work_sheets = wb_obj.sheetnames

        rooms = {}
        courses = []

        days_of_the_week = [
            "MONDAY",
            "TUESDAY",
            "WEDNESDAY",
            "THURSDAY",
            "FRIDAY",
            "SATURDAY",
        ]

        for sheet in work_sheets:
            work_sheet = wb_obj[sheet]

            for column_one in work_sheet.iter_cols(values_only=True):
                for i, room in enumerate(column_one):
                    if room is None or room == "ROOM":
                        continue
                    rooms[f"{i}"] = room
                break

            data_columns = list(work_sheet.iter_cols(values_only=True))[1:]

            day = ""
            course_time = ""
            course_code = ""
            hours = "2"

            for column in data_columns:
                for idx, value in enumerate(column):
                    if value is None:
                        continue

                    if value == "CHAPEL":
                        continue

                    if isinstance(value, datetime):
                        day = (
                            days_of_the_week[value.weekday()]
                            + " "
                            + str(value.date()).replace("-", "/")
                        )
                    elif (
                        isinstance(value, str)
                        and value.split(" ")[0] in days_of_the_week
                    ):
                        day = value

                    elif (
                        isinstance(value, str)
                        and len(value) > 0
                        and value[0].isdigit()
                    ):
                        course_time = value.strip()
                        if "-" in course_time:
                            start_time = course_time.split("-")[0]
                            end_time = course_time.split("-")[1]
                            hours = self._time_difference(start_time, end_time)
                        else:
                            hours = "2"
                    elif isinstance(value, str):
                        course_code = value
                        hours_str = "2"
                        if hours and len(hours) > 0:
                            hours_str = "2" if hours[0] == "-" else str(hours)
                        courses.append(
                            CourseEntry(
                                course_code=course_code,
                                day=day,
                                time=course_time,
                                venue=rooms.get(f"{idx}", ""),
                                campus="",
                                coordinator="",
                                hrs=hours_str,
                                invigilator="",
                                datetime_str=None,
                            )
                        )

        return self.normalize_output(courses)

    def _time_difference(self, start_time: str, end_time: str) -> str:
        """
        Returns the difference in hrs between two time intervals.
        Defaults to "2" on parsing failure.
        """
        start_time = start_time.strip()
        end_time = end_time.strip()

        formats = ["%I:%M%p", "%H:%M", "%I:%M %p", "%H:%M "]
        start_dt = None
        end_dt = None

        for fmt in formats:
            try:
                start_dt = datetime.strptime(start_time, fmt)
                break
            except ValueError:
                continue

        for fmt in formats:
            try:
                end_dt = datetime.strptime(end_time, fmt)
                break
            except ValueError:
                continue

        if start_dt is None or end_dt is None:
            return "2"

        hrs = (end_dt - start_dt).total_seconds() / 3600
        return str(hrs)
