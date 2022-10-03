#!/usr/bin/env python3
"""Functions to do calendar related calculations."""
from calendar import Calendar
import datetime
from .enums import DayOfWeek


def find_first_day(day: int | str, year: int, month: int,
                   iso: bool = False) -> int:
    """Finds the first day of week of a given month and year.

    Parameters
    ----------
    day: int | str
        The day of week to find
    year: int
        The year of interest
    month: int
        The month of interest
    iso: bool
        Use the ISO the numbering system to use when specifying day of week
        Can be ignored when day is given as a string

    Returns
    -------
    int
        They date of the month in which the first day of week appeared
    """
    cal: Calendar = Calendar()
    weeks = cal.monthdayscalendar(year, month)

    if isinstance(day, int):
        day_index = day
        if iso:
            day -= 1
    elif isinstance(day, str):
        try:
            day_index = DayOfWeek[day.title()].value
        except KeyError as err:
            raise ValueError("Invalid Day of Week") from err

    day_number = 1
    for week in weeks:
        if week[day_index] > 0:
            day_number = week[day_index]
            break

    return day_number


def find_week1() -> datetime.date:
    """Finds week 1 of the academic year.

    Returns
    -------
    datetime.date
        The date of the first week of september.
    """
    today: datetime.date = datetime.date.today()
    if today.month < 9:
        year: int = today.year - 1
        day: int = find_first_day(0, year, 9)
    else:
        year: int = today.year
        day: int = find_first_day(0, year, 9)

    week1: datetime.date = datetime.date(year, 9, day)
    return week1


def find_current_week_nott() -> int:
    """Finds the week number.

    Returns
    -------
    int
        The current week number.
    """
    diff = datetime.date.today() - find_week1()
    return int(diff.days / 7) + 1
