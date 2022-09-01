#!/usr/bin/env python3
from xml.etree import ElementTree as ET
from html.parser import HTMLParser
from enum import Enum
from calendar import Calendar
import datetime
from cli import handle_ranges
import csv


# Other Utils
def find_first_day(day: int | str, year: int, month: int,
                   ISO: bool = False) -> int:
    """Finds the first day of week of a given month and year.

    Parameters
    ----------
    day: int | str
        The day of week to find
    year: int
        The year of interest
    month: int
        The month of interest
    ISO: bool
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
        if ISO:
            day -= 1
    elif isinstance(day, str):
        try:
            day_index = DayOfWeek[day.title()].value
        except KeyError:
            raise ValueError("Invalid Day of Week")

    for week in weeks:
        if week[day_index] > 0:
            return week[day_index]


def find_week1() -> datetime.date:
    """Finds week 1 of the academic year."""
    today: datetime.date = datetime.date.today()
    if today.month < 9:
        year: int = today.year - 1
        day: int = find_first_day(0, year, 9)
    else:
        year: int = today.year
        day: int = find_first_day(0, year, 9)

    week1: datetime.date = datetime.date(year, 9, day)
    return week1


# Utils for parsing data
class DayOfWeek(Enum):
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


class ScheduleParser(HTMLParser):
    """HTML Parser used to parse all the tables

    Parameters
    ----------
    days: list[int] = [1, 2, 3, 4, 5, 6, 7]
        A list of days of the week to look for
    """
    def __init__(self, days: list[int] = [i for i in range(1, 8)]):
        super().__init__()

        # Declaring needed variables
        self.day_found: bool = False
        self.table_found: bool = False
        self.table_ended: bool = False
        self.tables: dict[str, str] = {}
        self.current_day: str = ""

        # Populating tables
        days.sort()
        for day in days:
            self.tables[DayOfWeekISO(day).name] = ""

    def handle_data(self, data):
        """Handles data received (text inside tags)."""
        if not self.day_found:
            # Finding the days
            if data in self.tables:
                self.day_found = True
                self.current_day = data
        else:
            if data.strip() != "" and self.table_found:
                self.tables[self.current_day] += data

    def handle_starttag(self, tag, attr):
        """Handles start tags received."""
        if not self.day_found:
            return
        if (tag == "table" or self.table_found):
            self.table_found = True
            self.tables[self.current_day] += f"<{tag}>"

    def handle_endtag(self, tag):
        """Handles end tags received."""
        if not self.day_found:
            return
        if self.table_found:
            self.tables[self.current_day] += f"</{tag}>"
            if tag == "table":
                self.table_found = False
                self.day_found = False


def table_to_dict(table: str | ET.Element, indexs: list[str] = None,
                  verbose: bool = True) -> dict[str, list[str]] | None:
    """Converts a HTML table into a python dict
    Parameters
    ----------
    table: str | xml.etree.ElementTree
        The HTML table to use.
        It can be in the form of a string, ElementTree from xml module.
    indexs: list[str]
        The Index to use for the dict.
        If None is provided, the first row of the table will be used.
    verbose: bool
        Determine to print information messages

    Returns
    -------
    dict[str, list[str]]
        The data of the table.
    None
        If there isn't any data

    TODO
    ----
    Handle Uneven Spaces
    """
    # Getting Element Tree
    if isinstance(table, ET.Element):
        data: ET.Element = table
    else:
        data: ET.Element = ET.fromstring(table)

    # Returning None if there isn't any data in table
    if data.find("tr") is None:
        if verbose:
            print("No Data in table")
        return None

    # Setting indexes/label used for the csv
    indexed = False
    if indexs is None:
        if verbose:
            print("No Indexs Provided, Using first row as index")

        indexs = []
        for col in data.findall("tr")[0].findall("td"):
            indexs.append(col.text)
        indexed = True

    # Setting up output dict
    output = {}
    for i in indexs:
        output[i] = []

    # Getting data from table
    skipped = False
    for row in data.findall("tr"):
        # Skipping first row if used for indexing
        if indexed and not skipped:
            skipped = True
            continue
        # Looping or indexs
        columns = row.findall("td")
        for i, label in enumerate(indexs):
            try:
                output[label].append(columns[i].text)
            except IndexError:
                if verbose:
                    print("Not Enough Data at Row")

    return output


# Utils for exporting
def csv_export(data: dict, weeks: list,
               output: str = "output.csv") -> list[list]:
    """Exports the timetable in a csv format."""
    start_day = find_week1()
    csv_data = []

    # Looping Over all they day of the week
    for day, day_data in data.items():
        date_with_day = start_day +\
            datetime.timedelta(days=DayOfWeek[day].value)
        # Skipping if there is no classes
        if day_data is None:
            continue

        # Looping over all the modules in they day
        for i in range(len(day_data['Module'])):
            module_weeks = day_data['Weeks'][i]
            module = day_data['Module'][i]

            start = day_data['Start'][i].split(":")
            start = datetime.time(hour=int(start[0]), minute=int(start[1]))
            end = day_data['End'][i].split(":")
            end = datetime.time(hour=int(end[0]), minute=int(end[1]))

            for week in handle_ranges(module_weeks):
                if week not in weeks:
                    continue
                date = date_with_day + datetime.timedelta(weeks=week-1)
                csv_data.append([date, start, end, module])

    csv_data.sort()
    csv_data.insert(0, ["Date", "Start", "End", "Module"])

    with open(output, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)
    return csv_data


def notion_export():
    ...


def google_export():
    ...


def microsoft_export():
    ...
