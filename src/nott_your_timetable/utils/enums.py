#!/usr/bin/env python3
"""Enumerations for nott-your-timetable"""
from enum import Enum


class DayOfWeek(Enum):
    """Enumaration fo Day of Week."""
    # pylint: disable=invalid-name
    Monday = 0
    Mon = 0
    Tuesday = 1
    Tue = 1
    Wednesday = 2
    Wed = 2
    Thursday = 3
    Thu = 3
    Friday = 4
    Fri = 4
    Saturday = 5
    Sat = 5
    Sunday = 6
    Sun = 6


class DayOfWeekISO(Enum):
    """Enumaration fo Day of Week using ISO format."""
    # pylint: disable=invalid-name
    Monday = 1
    Mon = 1
    Tuesday = 2
    Tue = 2
    Wednesday = 3
    Wed = 3
    Thursday = 4
    Thu = 4
    Friday = 5
    Fri = 5
    Saturday = 6
    Sat = 6
    Sunday = 7
    Sun = 7
