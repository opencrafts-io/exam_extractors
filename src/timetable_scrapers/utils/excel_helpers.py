from typing import BinaryIO, Union

from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet


FileLike = Union[BinaryIO, str]


def load_excel(file: FileLike, *, data_only: bool = True) -> Workbook:
    return load_workbook(file, data_only=data_only)


def active_sheet(wb: Workbook) -> Worksheet:
    return wb.active

