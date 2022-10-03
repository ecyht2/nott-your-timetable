#!/usr/bin/env python3
import json
from importlib.resources import files
from .utils import find_current_week_nott


def get_data() -> tuple[dict, dict]:
    """Gets Department and program data from json files.

    Returns
    -------
    tuple[dict, dict]
        The data where the first one is the department data
        and the second one is the program data.
    """
    data_path = files('nott_your_timetable.data')
    with open(data_path.joinpath("dept.json"), "r", encoding="utf-8")\
         as file:
        dept_data: dict = json.load(file)
    with open(data_path.joinpath("program.json"), "r", encoding="utf-8")\
         as file:
        program_data: dict = json.load(file)

    return (dept_data, program_data)


def get_convinience_weeks() -> dict[str, str]:
    output = {
        "All Year": "1-52",
        "Autumn": "4-15",
        "Spring": "22-33",
        "Summer": "38-49",
        "Full Year": "4-15, 22-33",
        "This Week": str(find_current_week_nott())
    }

    return output


def get_convinience_days() -> dict[str, str]:
    output = {
        "Weekdays": "1-5",
        "All Week": "1-7",
        "Weekends": "6-7"
    }

    return output
